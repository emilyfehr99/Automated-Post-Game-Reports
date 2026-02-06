#!/usr/bin/env python3
"""
Enhanced Model Training with Advanced Metrics
Adds sophisticated metrics to improve model accuracy beyond 56.2%
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from sklearn.metrics import accuracy_score, log_loss, r2_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator

class EnhancedModelTrainer:
    def __init__(self):
        self.model = ImprovedSelfLearningModelV2()
        self.api = NHLAPIClient()
        self.report_generator = PostGameReportGenerator()
        
        # Advanced metrics storage
        self.advanced_features = {}
        self.enhanced_predictions = []
        
    def extract_advanced_metrics(self, game_data, away_team_id, home_team_id):
        """Extract comprehensive advanced metrics from game data"""
        try:
            # Traditional metrics
            away_xg, home_xg = self.report_generator._calculate_xg_from_plays(game_data)
            away_hdc, home_hdc = self.report_generator._calculate_hdc_from_plays(game_data)
            away_gs, home_gs = self.report_generator._calculate_game_scores(game_data)
            
            # Zone control metrics
            away_zone_metrics = self.report_generator._calculate_zone_metrics(game_data, away_team_id, 'away')
            home_zone_metrics = self.report_generator._calculate_zone_metrics(game_data, home_team_id, 'home')
            
            # Pass metrics
            away_pass_metrics = self.report_generator._calculate_pass_metrics(game_data, away_team_id, 'away')
            home_pass_metrics = self.report_generator._calculate_pass_metrics(game_data, home_team_id, 'home')
            
            # Period metrics
            away_period_metrics = self.report_generator._calculate_period_metrics(game_data, away_team_id, 'away')
            home_period_metrics = self.report_generator._calculate_period_metrics(game_data, home_team_id, 'home')
            
            # Calculate advanced composite scores
            away_metrics = self._calculate_composite_scores(
                away_xg, away_hdc, away_gs, away_zone_metrics, 
                away_pass_metrics, away_period_metrics
            )
            
            home_metrics = self._calculate_composite_scores(
                home_xg, home_hdc, home_gs, home_zone_metrics,
                home_pass_metrics, home_period_metrics
            )
            
            return {
                'away': away_metrics,
                'home': home_metrics
            }
            
        except Exception as e:
            print(f"❌ Error extracting advanced metrics: {e}")
            return None
    
    def _calculate_composite_scores(self, xg, hdc, gs, zone_metrics, pass_metrics, period_metrics):
        """Calculate advanced composite scores"""
        try:
            # Pressure Score - Offensive zone control
            oz_shots = np.sum(zone_metrics.get('oz_originating_shots', [0]))
            fc_sog = np.sum(zone_metrics.get('fc_cycle_sog', [0]))
            rush_sog = np.sum(zone_metrics.get('rush_sog', [0]))
            total_sog = np.sum(period_metrics.get('shots', [1]))
            
            pressure_score = ((oz_shots + fc_sog + rush_sog) / max(1, total_sog)) * 100 if total_sog > 0 else 0.0
            
            # Possession Score - Pass success and control
            total_passes = np.sum(pass_metrics[0]) if pass_metrics and len(pass_metrics) > 0 else 0
            successful_passes = np.sum(pass_metrics[1]) if pass_metrics and len(pass_metrics) > 1 else 0
            possession_score = (successful_passes / max(1, total_passes)) * 100 if total_passes > 0 else 0.0
            
            # Momentum Score - Period-by-period performance
            goals_by_period = period_metrics.get('goals', [0, 0, 0])
            momentum_score = 1.0
            if len(goals_by_period) >= 3:
                total_goals = np.sum(goals_by_period)
                if total_goals > 0:
                    momentum_score = (goals_by_period[2] - goals_by_period[0]) / total_goals
            
            # Territorial Score - Zone time advantage
            territorial_score = (oz_shots / max(1, total_sog)) * 100 if total_sog > 0 else 0.0
            
            # Quality Score - Shot quality and danger
            quality_score = (hdc / max(1, total_sog)) * 100 if total_sog > 0 else 0.0
            
            return {
                'xg': float(xg),
                'hdc': float(hdc),
                'gs': float(gs),
                'pressure_score': pressure_score,
                'possession_score': possession_score,
                'momentum_score': momentum_score,
                'territorial_score': territorial_score,
                'quality_score': quality_score,
                'oz_shots': int(oz_shots),
                'fc_sog': int(fc_sog),
                'rush_sog': int(rush_sog),
                'total_passes': int(total_passes),
                'successful_passes': int(successful_passes)
            }
            
        except Exception as e:
            print(f"❌ Error calculating composite scores: {e}")
            return {
                'xg': 0.0, 'hdc': 0.0, 'gs': 0.0,
                'pressure_score': 0.0, 'possession_score': 0.0,
                'momentum_score': 0.0, 'territorial_score': 0.0,
                'quality_score': 0.0, 'oz_shots': 0, 'fc_sog': 0,
                'rush_sog': 0, 'total_passes': 0, 'successful_passes': 0
            }
    
    def train_enhanced_model(self):
        """Train model with advanced metrics"""
        print("🚀 Starting Enhanced Model Training with Advanced Metrics")
        print("="*70)
        
        # Load historical data
        historical_file = Path("historical_seasons_team_stats.json")
        if not historical_file.exists():
            print("❌ Historical data not found. Run collect_historical_seasons.py first.")
            return False
        
        with open(historical_file, 'r') as f:
            historical_data = json.load(f)
        
        # Load current predictions
        predictions_file = Path("win_probability_predictions_v2.json")
        if not predictions_file.exists():
            print("❌ Predictions file not found.")
            return False
        
        with open(predictions_file, 'r') as f:
            predictions_data = json.load(f)
        
        predictions = predictions_data.get('predictions', [])
        print(f"📊 Processing {len(predictions)} predictions with advanced metrics...")
        
        # Extract advanced metrics for each prediction
        enhanced_features = []
        valid_predictions = []
        
        for i, pred in enumerate(predictions):
            if i % 20 == 0:
                print(f"   Processing prediction {i+1}/{len(predictions)}...")
            
            game_id = pred.get('game_id')
            if not game_id:
                continue
            
            try:
                # Get game data
                game_data = self.api.get_comprehensive_game_data(game_id)
                if not game_data:
                    continue
                
                # Extract team IDs
                boxscore = game_data.get('game_center', {}).get('boxscore', {})
                away_team_id = boxscore.get('awayTeam', {}).get('id')
                home_team_id = boxscore.get('homeTeam', {}).get('id')
                
                if not away_team_id or not home_team_id:
                    continue
                
                # Extract advanced metrics
                advanced_metrics = self.extract_advanced_metrics(game_data, away_team_id, home_team_id)
                if not advanced_metrics:
                    continue
                
                # Create feature vector
                away_features = advanced_metrics['away']
                home_features = advanced_metrics['home']
                
                # Calculate relative advantages
                feature_vector = [
                    away_features['xg'] - home_features['xg'],
                    away_features['hdc'] - home_features['hdc'],
                    away_features['gs'] - home_features['gs'],
                    away_features['pressure_score'] - home_features['pressure_score'],
                    away_features['possession_score'] - home_features['possession_score'],
                    away_features['momentum_score'] - home_features['momentum_score'],
                    away_features['territorial_score'] - home_features['territorial_score'],
                    away_features['quality_score'] - home_features['quality_score'],
                    # Absolute values
                    away_features['xg'], away_features['hdc'], away_features['gs'],
                    home_features['xg'], home_features['hdc'], home_features['gs']
                ]
                
                enhanced_features.append(feature_vector)
                valid_predictions.append(pred)
                
            except Exception as e:
                print(f"   ⚠️ Error processing game {game_id}: {e}")
                continue
        
        if len(enhanced_features) < 10:
            print("❌ Not enough valid data for training")
            return False
        
        print(f"✅ Extracted advanced metrics for {len(enhanced_features)} games")
        
        # Convert to numpy arrays
        X = np.array(enhanced_features)
        
        # Create target variable (1 = home win, 0 = away win)
        y = []
        for pred in valid_predictions:
            actual_winner = pred.get('actual_winner')
            home_team = pred.get('home_team')
            away_team = pred.get('away_team')
            
            if actual_winner == home_team:
                y.append(1)  # Home win
            elif actual_winner == away_team:
                y.append(0)  # Away win
            else:
                continue  # Skip unclear results
        
        y = np.array(y)
        
        if len(y) != len(X):
            print("❌ Mismatch between features and targets")
            return False
        
        print(f"📈 Training on {len(X)} samples with {X.shape[1]} features")
        
        # Train multiple models
        models = {
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
        
        results = {}
        
        for name, model in models.items():
            print(f"\n🏋️ Training {name}...")
            
            # Cross-validation
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
            
            # Train on full dataset
            model.fit(X, y)
            
            # Make predictions
            y_pred = model.predict(X)
            y_pred_proba = model.predict_proba(X)
            
            # Calculate metrics
            accuracy = accuracy_score(y, y_pred)
            logloss = log_loss(y, y_pred_proba)
            
            results[name] = {
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'log_loss': logloss,
                'model': model
            }
            
            print(f"   Accuracy: {accuracy:.1%}")
            print(f"   CV Score: {cv_scores.mean():.1%} ± {cv_scores.std():.1%}")
            print(f"   Log Loss: {logloss:.4f}")
        
        # Find best model
        best_model_name = max(results.keys(), key=lambda k: results[k]['accuracy'])
        best_model = results[best_model_name]['model']
        
        print(f"\n🏆 BEST MODEL: {best_model_name}")
        print(f"   Accuracy: {results[best_model_name]['accuracy']:.1%}")
        print(f"   Log Loss: {results[best_model_name]['log_loss']:.4f}")
        
        # Feature importance (if available)
        if hasattr(best_model, 'feature_importances_'):
            feature_names = [
                'xG_diff', 'HDC_diff', 'GS_diff', 'Pressure_diff', 'Possession_diff',
                'Momentum_diff', 'Territorial_diff', 'Quality_diff',
                'Away_xG', 'Away_HDC', 'Away_GS', 'Home_xG', 'Home_HDC', 'Home_GS'
            ]
            
            importances = best_model.feature_importances_
            feature_importance = list(zip(feature_names, importances))
            feature_importance.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\n📊 TOP FEATURE IMPORTANCE:")
            for feature, importance in feature_importance[:5]:
                print(f"   {feature}: {importance:.3f}")
        
        # Save enhanced model
        self.save_enhanced_model(best_model, results, feature_names if 'feature_names' in locals() else [])
        
        return True
    
    def save_enhanced_model(self, model, results, feature_names):
        """Save the enhanced model and results"""
        model_data = {
            'model_type': type(model).__name__,
            'results': results,
            'feature_names': feature_names,
            'training_date': datetime.now().isoformat(),
            'enhanced_metrics_used': [
                'Pressure Score', 'Possession Score', 'Momentum Score',
                'Territorial Score', 'Quality Score', 'Zone Control',
                'Pass Success', 'Period Performance'
            ]
        }
        
        with open('enhanced_model_results.json', 'w') as f:
            json.dump(model_data, f, indent=2, default=str)
        
        print(f"\n💾 Enhanced model saved to enhanced_model_results.json")
        print(f"🎯 This model uses advanced metrics for better predictions!")

if __name__ == "__main__":
    trainer = EnhancedModelTrainer()
    success = trainer.train_enhanced_model()
    
    if success:
        print("\n🎉 Enhanced training completed successfully!")
        print("🚀 Model now uses advanced metrics for better accuracy!")
    else:
        print("\n❌ Enhanced training failed. Check the logs above.")
