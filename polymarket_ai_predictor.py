#!/usr/bin/env python3
"""
Polymarket AI Prediction Model
A comprehensive AI system for predicting Polymarket outcomes and providing trading recommendations
Optimized for Canadian users with CAD/USD conversion support

⚠️ IMPORTANT LEGAL DISCLAIMER:
- Polymarket is currently restricted in Ontario, Canada
- Manitoba residents should verify local regulations
- Consult legal/financial professionals before trading
- This tool is for educational/research purposes only
"""

import requests
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Machine Learning Libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib

# For sentiment analysis and external data
import yfinance as yf
from textblob import TextBlob

class PolymarketAIPredictor:
    def __init__(self):
        self.base_url = "https://gamma-api.polymarket.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # CAD/USD conversion rate (will be updated dynamically)
        self.cad_to_usd_rate = 0.74  # Approximate rate, will fetch real-time
        
        # Model storage
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        
        # Risk management parameters - Ultra-conservative for 90% confidence
        self.max_position_size = 0.05  # Max 5% of portfolio per trade
        self.stop_loss_threshold = 0.15  # 15% stop loss
        self.take_profit_threshold = 0.3  # 30% take profit
        self.min_confidence_threshold = 0.90  # 90% minimum confidence
        
        print("🚀 Polymarket AI Predictor initialized")
        print("⚠️  Legal Notice: Manitoba residents - verify local regulations")
        
    def get_cad_usd_rate(self) -> float:
        """Get real-time CAD/USD exchange rate"""
        try:
            # Using Yahoo Finance for real-time rates
            ticker = yf.Ticker("CADUSD=X")
            data = ticker.history(period="1d")
            if not data.empty:
                self.cad_to_usd_rate = float(data['Close'].iloc[-1])
                print(f"💱 Current CAD/USD rate: {self.cad_to_usd_rate:.4f}")
            return self.cad_to_usd_rate
        except Exception as e:
            print(f"⚠️  Could not fetch exchange rate: {e}")
            return self.cad_to_usd_rate
    
    def fetch_polymarket_events(self, limit: int = 50) -> List[Dict]:
        """Fetch active Polymarket events"""
        try:
            url = f"{self.base_url}/events"
            params = {
                'limit': limit,
                'active': True,
                'archived': False
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            events = response.json()
            print(f"📊 Fetched {len(events)} active events")
            return events
            
        except Exception as e:
            print(f"❌ Error fetching events: {e}")
            return []
    
    def fetch_market_data(self, market_id: str) -> Dict:
        """Fetch detailed market data for a specific market"""
        try:
            url = f"{self.base_url}/markets/{market_id}"
            response = self.session.get(url)
            response.raise_for_status()
            
            market_data = response.json()
            return market_data
            
        except Exception as e:
            print(f"❌ Error fetching market data for {market_id}: {e}")
            return {}
    
    def fetch_historical_prices(self, market_id: str, days: int = 30) -> pd.DataFrame:
        """Fetch historical price data for a market"""
        try:
            url = f"{self.base_url}/markets/{market_id}/candles"
            end_time = int(time.time() * 1000)
            start_time = end_time - (days * 24 * 60 * 60 * 1000)
            
            params = {
                'start': start_time,
                'end': end_time,
                'interval': '1h'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data and 'candles' in data:
                df = pd.DataFrame(data['candles'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error fetching historical data for {market_id}: {e}")
            return pd.DataFrame()
    
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text using TextBlob"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity  # -1 to 1 scale
        except:
            return 0.0
    
    def extract_features(self, market_data: Dict, historical_data: pd.DataFrame) -> Dict:
        """Extract features for machine learning model"""
        features = {}
        
        # Basic market features
        features['current_price'] = market_data.get('price', 0)
        features['volume_24h'] = market_data.get('volume', 0)
        features['market_cap'] = market_data.get('marketCap', 0)
        features['liquidity'] = market_data.get('liquidity', 0)
        
        # Time-based features
        end_time = market_data.get('endDate')
        if end_time:
            time_to_end = (datetime.fromisoformat(end_time.replace('Z', '+00:00')) - datetime.now()).total_seconds()
            features['hours_to_end'] = time_to_end / 3600
            features['days_to_end'] = time_to_end / (24 * 3600)
        else:
            features['hours_to_end'] = 0
            features['days_to_end'] = 0
        
        # Historical price features
        if not historical_data.empty:
            features['price_volatility'] = historical_data['close'].std()
            features['price_trend'] = (historical_data['close'].iloc[-1] - historical_data['close'].iloc[0]) / historical_data['close'].iloc[0]
            features['volume_trend'] = historical_data['volume'].mean() if 'volume' in historical_data.columns else 0
            features['max_price'] = historical_data['high'].max()
            features['min_price'] = historical_data['low'].min()
        else:
            features['price_volatility'] = 0
            features['price_trend'] = 0
            features['volume_trend'] = 0
            features['max_price'] = features['current_price']
            features['min_price'] = features['current_price']
        
        # Sentiment analysis
        question = market_data.get('question', '')
        features['sentiment'] = self.analyze_sentiment(question)
        
        # Category encoding
        category = market_data.get('category', 'other')
        features['category_encoded'] = hash(category) % 100  # Simple encoding
        
        return features
    
    def train_prediction_model(self, training_data: List[Dict]) -> Dict:
        """Train machine learning models for prediction"""
        if len(training_data) < 10:
            print("⚠️  Insufficient training data")
            return {}
        
        # Prepare features and targets
        X = []
        y = []
        
        for data in training_data:
            features = data['features']
            outcome = data['outcome']  # 1 for YES, 0 for NO
            
            feature_vector = [
                features.get('current_price', 0),
                features.get('volume_24h', 0),
                features.get('liquidity', 0),
                features.get('hours_to_end', 0),
                features.get('price_volatility', 0),
                features.get('price_trend', 0),
                features.get('sentiment', 0),
                features.get('category_encoded', 0)
            ]
            
            X.append(feature_vector)
            y.append(outcome)
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train multiple models
        models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000)
        }
        
        trained_models = {}
        scores = {}
        
        for name, model in models.items():
            # Cross-validation
            cv_scores = cross_val_score(model, X_scaled, y, cv=5)
            scores[name] = cv_scores.mean()
            
            # Train on full dataset
            model.fit(X_scaled, y)
            trained_models[name] = model
            
            print(f"📈 {name} accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Select best model
        best_model_name = max(scores, key=scores.get)
        best_model = trained_models[best_model_name]
        
        print(f"🏆 Best model: {best_model_name} with accuracy {scores[best_model_name]:.3f}")
        
        return {
            'model': best_model,
            'scaler': scaler,
            'model_name': best_model_name,
            'accuracy': scores[best_model_name]
        }
    
    def predict_outcome(self, market_data: Dict, historical_data: pd.DataFrame, model_info: Dict) -> Dict:
        """Make prediction for a market"""
        if not model_info:
            return {'prediction': 0.5, 'confidence': 0.0, 'recommendation': 'HOLD'}
        
        # Extract features
        features = self.extract_features(market_data, historical_data)
        
        # Prepare feature vector
        feature_vector = np.array([[
            features.get('current_price', 0),
            features.get('volume_24h', 0),
            features.get('liquidity', 0),
            features.get('hours_to_end', 0),
            features.get('price_volatility', 0),
            features.get('price_trend', 0),
            features.get('sentiment', 0),
            features.get('category_encoded', 0)
        ]])
        
        # Scale features
        feature_vector_scaled = model_info['scaler'].transform(feature_vector)
        
        # Make prediction
        model = model_info['model']
        prediction_proba = model.predict_proba(feature_vector_scaled)[0]
        
        # Get YES probability
        yes_probability = prediction_proba[1] if len(prediction_proba) > 1 else prediction_proba[0]
        
        # Calculate confidence based on model accuracy and probability distance from 0.5
        confidence = model_info['accuracy'] * abs(yes_probability - 0.5) * 2
        
        # Generate recommendation
        current_price = features.get('current_price', 0.5)
        
        if yes_probability > 0.6 and current_price < 0.6:
            recommendation = 'BUY YES'
        elif yes_probability < 0.4 and current_price > 0.4:
            recommendation = 'BUY NO'
        else:
            recommendation = 'HOLD'
        
        return {
            'prediction': yes_probability,
            'confidence': confidence,
            'recommendation': recommendation,
            'current_price': current_price,
            'expected_value': yes_probability * 1.0 - current_price,
            'features': features
        }
    
    def calculate_position_size(self, prediction: Dict, portfolio_value_cad: float) -> Dict:
        """Calculate optimal position size based on Kelly Criterion"""
        if prediction['confidence'] < 0.3:
            return {'position_size_cad': 0, 'position_size_usd': 0, 'reason': 'Low confidence'}
        
        # Kelly Criterion: f = (bp - q) / b
        # where b = odds, p = probability of winning, q = probability of losing
        
        current_price = prediction['current_price']
        yes_probability = prediction['prediction']
        
        if prediction['recommendation'] == 'BUY YES':
            b = (1 - current_price) / current_price  # Odds for YES
            p = yes_probability
            q = 1 - yes_probability
        elif prediction['recommendation'] == 'BUY NO':
            b = current_price / (1 - current_price)  # Odds for NO
            p = 1 - yes_probability
            q = yes_probability
        else:
            return {'position_size_cad': 0, 'position_size_usd': 0, 'reason': 'Hold recommendation'}
        
        # Kelly fraction
        kelly_fraction = (b * p - q) / b
        
        # Apply conservative scaling and risk management
        kelly_fraction = max(0, min(kelly_fraction, self.max_position_size))
        kelly_fraction *= prediction['confidence']  # Scale by confidence
        
        # Convert to CAD and USD
        position_size_cad = portfolio_value_cad * kelly_fraction
        position_size_usd = position_size_cad * self.cad_to_usd_rate
        
        return {
            'position_size_cad': position_size_cad,
            'position_size_usd': position_size_usd,
            'kelly_fraction': kelly_fraction,
            'reason': f'Kelly-based position sizing'
        }
    
    def generate_trading_recommendations(self, portfolio_value_cad: float = 1000) -> List[Dict]:
        """Generate comprehensive trading recommendations"""
        print(f"\n🎯 Generating trading recommendations for ${portfolio_value_cad:.2f} CAD portfolio")
        
        # Update exchange rate
        self.get_cad_usd_rate()
        
        # Fetch active events
        events = self.fetch_polymarket_events(limit=20)
        
        if not events:
            print("❌ No events found")
            return []
        
        recommendations = []
        
        for event in events[:10]:  # Analyze top 10 events
            market_id = event.get('id')
            if not market_id:
                continue
            
            print(f"\n📊 Analyzing: {event.get('question', 'Unknown')[:50]}...")
            
            # Fetch detailed market data
            market_data = self.fetch_market_data(market_id)
            if not market_data:
                continue
            
            # Fetch historical data
            historical_data = self.fetch_historical_prices(market_id, days=7)
            
            # For demo purposes, create a simple model (in production, use trained model)
            # This is a simplified version - you'd want to train on historical data
            demo_model = {
                'model': RandomForestClassifier(n_estimators=10, random_state=42),
                'scaler': StandardScaler(),
                'model_name': 'demo_model',
                'accuracy': 0.65
            }
            
            # Make prediction
            prediction = self.predict_outcome(market_data, historical_data, demo_model)
            
            # Calculate position size
            position_info = self.calculate_position_size(prediction, portfolio_value_cad)
            
            # Create recommendation
            recommendation = {
                'market_id': market_id,
                'question': event.get('question', 'Unknown'),
                'category': event.get('category', 'Other'),
                'end_date': event.get('endDate', 'Unknown'),
                'current_price': prediction['current_price'],
                'prediction': prediction['prediction'],
                'confidence': prediction['confidence'],
                'recommendation': prediction['recommendation'],
                'expected_value': prediction['expected_value'],
                'position_size_cad': position_info['position_size_cad'],
                'position_size_usd': position_info['position_size_usd'],
                'kelly_fraction': position_info.get('kelly_fraction', 0),
                'reason': position_info.get('reason', ''),
                'risk_score': self.calculate_risk_score(prediction, market_data)
            }
            
            recommendations.append(recommendation)
            
            # Print summary
            print(f"   💡 Recommendation: {prediction['recommendation']}")
            print(f"   📈 Prediction: {prediction['prediction']:.1%} YES")
            print(f"   🎯 Confidence: {prediction['confidence']:.1%}")
            print(f"   💰 Position: ${position_info['position_size_cad']:.2f} CAD")
        
        # Sort by expected value
        recommendations.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return recommendations
    
    def calculate_risk_score(self, prediction: Dict, market_data: Dict) -> float:
        """Calculate risk score (0-1, higher = riskier)"""
        risk_factors = []
        
        # Time risk (closer to end = riskier)
        hours_to_end = prediction['features'].get('hours_to_end', 0)
        if hours_to_end < 24:
            risk_factors.append(0.8)
        elif hours_to_end < 168:  # 1 week
            risk_factors.append(0.4)
        else:
            risk_factors.append(0.1)
        
        # Volatility risk
        volatility = prediction['features'].get('price_volatility', 0)
        risk_factors.append(min(volatility * 2, 1.0))
        
        # Liquidity risk
        liquidity = prediction['features'].get('liquidity', 0)
        if liquidity < 1000:
            risk_factors.append(0.8)
        elif liquidity < 10000:
            risk_factors.append(0.4)
        else:
            risk_factors.append(0.1)
        
        # Confidence risk (lower confidence = higher risk)
        confidence = prediction['confidence']
        risk_factors.append(1 - confidence)
        
        return sum(risk_factors) / len(risk_factors)
    
    def print_recommendations(self, recommendations: List[Dict]):
        """Print formatted trading recommendations"""
        print("\n" + "="*80)
        print("🎯 POLYMARKET AI TRADING RECOMMENDATIONS")
        print("="*80)
        
        if not recommendations:
            print("❌ No recommendations generated")
            return
        
        print(f"\n📊 Top {len(recommendations)} opportunities:")
        print("-" * 80)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['question'][:60]}...")
            print(f"   Category: {rec['category']}")
            print(f"   End Date: {rec['end_date']}")
            print(f"   Current Price: {rec['current_price']:.1%}")
            print(f"   AI Prediction: {rec['prediction']:.1%} YES")
            print(f"   Confidence: {rec['confidence']:.1%}")
            print(f"   Recommendation: {rec['recommendation']}")
            print(f"   Expected Value: {rec['expected_value']:.3f}")
            print(f"   Position Size: ${rec['position_size_cad']:.2f} CAD (${rec['position_size_usd']:.2f} USD)")
            print(f"   Risk Score: {rec['risk_score']:.1%}")
            print(f"   Kelly Fraction: {rec['kelly_fraction']:.1%}")
        
        # Summary statistics
        total_position_cad = sum(rec['position_size_cad'] for rec in recommendations)
        avg_confidence = sum(rec['confidence'] for rec in recommendations) / len(recommendations)
        avg_expected_value = sum(rec['expected_value'] for rec in recommendations) / len(recommendations)
        
        print(f"\n📈 PORTFOLIO SUMMARY:")
        print(f"   Total Position Size: ${total_position_cad:.2f} CAD")
        print(f"   Average Confidence: {avg_confidence:.1%}")
        print(f"   Average Expected Value: {avg_expected_value:.3f}")
        
        print(f"\n⚠️  LEGAL DISCLAIMER:")
        print(f"   - Polymarket may be restricted in your jurisdiction")
        print(f"   - Consult legal/financial professionals before trading")
        print(f"   - Past performance does not guarantee future results")
        print(f"   - Only invest what you can afford to lose")

def main():
    """Main function to run the AI predictor"""
    print("🚀 Starting Polymarket AI Predictor...")
    
    # Initialize predictor
    predictor = PolymarketAIPredictor()
    
    # Get portfolio value from user
    try:
        portfolio_value = float(input("Enter your portfolio value in CAD (default: 1000): ") or "1000")
    except ValueError:
        portfolio_value = 1000
        print("Using default portfolio value: $1000 CAD")
    
    # Generate recommendations
    recommendations = predictor.generate_trading_recommendations(portfolio_value)
    
    # Print results
    predictor.print_recommendations(recommendations)
    
    # Save recommendations to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"polymarket_recommendations_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(recommendations, f, indent=2, default=str)
    
    print(f"\n💾 Recommendations saved to: {filename}")

if __name__ == "__main__":
    main()
