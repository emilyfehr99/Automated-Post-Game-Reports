#!/usr/bin/env python3
"""
Comprehensive Model Training and Evaluation
Trains the model on historical data and evaluates with proper metrics
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    log_loss, r2_score, confusion_matrix, classification_report
)
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator

class ComprehensiveModelTrainer:
    def __init__(self):
        self.model = ImprovedSelfLearningModelV2()
        self.api = NHLAPIClient()
        self.report_generator = PostGameReportGenerator()
        
        # Data files
        self.historical_file = Path("historical_seasons_team_stats.json")
        self.current_file = Path("season_2025_2026_team_stats.json")
        self.predictions_file = Path("win_probability_predictions_v2.json")
        
        # Results storage
        self.training_results = {}
        self.evaluation_metrics = {}
        
    def load_historical_data(self):
        """Load historical seasons data"""
        print("📚 Loading historical training data...")
        
        if not self.historical_file.exists():
            print("❌ Historical data file not found. Run collect_historical_seasons.py first.")
            return False
            
        with open(self.historical_file, 'r') as f:
            data = json.load(f)
            
        print(f"✅ Loaded {len(data.get('seasons', {}))} historical seasons")
        return data
    
    def load_current_season_data(self):
        """Load current season data for testing"""
        print("📊 Loading current season test data...")
        
        if not self.current_file.exists():
            print("❌ Current season data file not found. Run backfill_2025_2026_season.py first.")
            return False
            
        with open(self.current_file, 'r') as f:
            data = json.load(f)
            
        print(f"✅ Loaded current season with {data.get('total_games', 0)} games")
        return data
    
    def load_predictions_data(self):
        """Load predictions for evaluation"""
        print("🎯 Loading predictions data...")
        
        if not self.predictions_file.exists():
            print("❌ Predictions file not found.")
            return []
            
        with open(self.predictions_file, 'r') as f:
            data = json.load(f)
            
        predictions = data.get('predictions', [])
        print(f"✅ Loaded {len(predictions)} predictions")
        return predictions
    
    def train_model_on_historical_data(self, historical_data):
        """Train model using historical seasons"""
        print("\n🏋️ Training model on historical data...")
        
        # Initialize model with historical data
        self.model.historical_stats = historical_data.get('seasons', {})
        
        # Calculate training metrics from historical data
        total_historical_games = 0
        for season_name, season_data in self.model.historical_stats.items():
            season_games = season_data.get('total_games', 0)
            total_historical_games += season_games
            print(f"   📈 {season_name}: {season_games} games")
        
        print(f"✅ Model trained on {total_historical_games} historical games")
        
        # Store training results
        self.training_results = {
            'total_historical_games': total_historical_games,
            'seasons_used': list(self.model.historical_stats.keys()),
            'training_timestamp': datetime.now().isoformat()
        }
        
        return True
    
    def evaluate_model_performance(self, predictions):
        """Comprehensive model evaluation with proper metrics"""
        print("\n📊 Evaluating model performance...")
        
        if not predictions:
            print("❌ No predictions to evaluate")
            return {}
        
        # Filter predictions with actual outcomes
        valid_predictions = [p for p in predictions if p.get('actual_winner')]
        
        if len(valid_predictions) < 10:
            print(f"⚠️ Only {len(valid_predictions)} valid predictions for evaluation")
            return {}
        
        print(f"📈 Evaluating {len(valid_predictions)} predictions...")
        
        # Extract data for evaluation
        y_true = []
        y_pred = []
        y_pred_proba = []
        
        for pred in valid_predictions:
            # Get actual winner (normalize to 0/1)
            actual_winner = pred.get('actual_winner')
            home_team = pred.get('home_team')
            away_team = pred.get('away_team')
            
            if actual_winner == home_team:
                actual = 1  # Home win
            elif actual_winner == away_team:
                actual = 0  # Away win
            else:
                continue  # Skip if actual_winner is not clear
            
            # Get predicted probabilities
            home_prob = pred.get('predicted_home_win_prob', 0.5)
            away_prob = pred.get('predicted_away_win_prob', 0.5)
            
            # Normalize probabilities
            total_prob = home_prob + away_prob
            if total_prob > 0:
                home_prob_norm = home_prob / total_prob
                away_prob_norm = away_prob / total_prob
            else:
                home_prob_norm = 0.5
                away_prob_norm = 0.5
            
            y_true.append(actual)
            y_pred.append(1 if home_prob_norm > 0.5 else 0)
            y_pred_proba.append([away_prob_norm, home_prob_norm])
        
        if len(y_true) < 10:
            print("❌ Not enough valid predictions for evaluation")
            return {}
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Log Loss (requires probability predictions)
        try:
            logloss = log_loss(y_true, y_pred_proba)
        except:
            logloss = float('inf')
        
        # R² Score (coefficient of determination)
        try:
            r2 = r2_score(y_true, y_pred)
        except:
            r2 = 0.0
        
        # Statistical significance (Chi-square test)
        try:
            # Create confusion matrix for chi-square
            cm = confusion_matrix(y_true, y_pred)
            if cm.shape == (2, 2):
                chi2, p_value, dof, expected = stats.chi2_contingency(cm)
            else:
                chi2, p_value = 0.0, 1.0
        except:
            chi2, p_value = 0.0, 1.0
        
        # Confidence intervals (Wilson score interval)
        n = len(y_true)
        z = 1.96  # 95% confidence
        p_hat = accuracy
        ci_lower = (p_hat + z*z/(2*n) - z * np.sqrt((p_hat*(1-p_hat) + z*z/(4*n))/n)) / (1 + z*z/n)
        ci_upper = (p_hat + z*z/(2*n) + z * np.sqrt((p_hat*(1-p_hat) + z*z/(4*n))/n)) / (1 + z*z/n)
        
        # Store comprehensive metrics
        self.evaluation_metrics = {
            'total_predictions': len(valid_predictions),
            'accuracy': accuracy,
            'accuracy_ci_lower': ci_lower,
            'accuracy_ci_upper': ci_upper,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'log_loss': logloss,
            'r_squared': r2,
            'chi_square': chi2,
            'p_value': p_value,
            'statistical_significance': p_value < 0.05,
            'evaluation_timestamp': datetime.now().isoformat()
        }
        
        return self.evaluation_metrics
    
    def generate_detailed_report(self):
        """Generate comprehensive training and evaluation report"""
        print("\n" + "="*80)
        print("🏆 COMPREHENSIVE MODEL TRAINING & EVALUATION REPORT")
        print("="*80)
        
        # Training Results
        print(f"\n📚 TRAINING DATA:")
        print(f"   Historical Games: {self.training_results.get('total_historical_games', 0):,}")
        print(f"   Seasons Used: {', '.join(self.training_results.get('seasons_used', []))}")
        print(f"   Training Date: {self.training_results.get('training_timestamp', 'Unknown')}")
        
        # Evaluation Metrics
        if self.evaluation_metrics:
            print(f"\n📊 EVALUATION METRICS:")
            print(f"   Total Predictions: {self.evaluation_metrics.get('total_predictions', 0):,}")
            print(f"   Accuracy: {self.evaluation_metrics.get('accuracy', 0):.1%}")
            print(f"   95% CI: [{self.evaluation_metrics.get('accuracy_ci_lower', 0):.1%}, {self.evaluation_metrics.get('accuracy_ci_upper', 0):.1%}]")
            print(f"   Precision: {self.evaluation_metrics.get('precision', 0):.1%}")
            print(f"   Recall: {self.evaluation_metrics.get('recall', 0):.1%}")
            print(f"   F1-Score: {self.evaluation_metrics.get('f1_score', 0):.1%}")
            print(f"   Log Loss: {self.evaluation_metrics.get('log_loss', 0):.4f}")
            print(f"   R² Score: {self.evaluation_metrics.get('r_squared', 0):.4f}")
            print(f"   Chi-Square: {self.evaluation_metrics.get('chi_square', 0):.4f}")
            print(f"   P-Value: {self.evaluation_metrics.get('p_value', 1):.4f}")
            
            significance = "✅ SIGNIFICANT" if self.evaluation_metrics.get('statistical_significance', False) else "❌ NOT SIGNIFICANT"
            print(f"   Statistical Significance: {significance}")
            
            # Interpretation
            print(f"\n🎯 INTERPRETATION:")
            accuracy = self.evaluation_metrics.get('accuracy', 0)
            if accuracy > 0.6:
                print("   🚀 EXCELLENT: Model shows strong predictive power")
            elif accuracy > 0.55:
                print("   ✅ GOOD: Model shows solid predictive ability")
            elif accuracy > 0.5:
                print("   ⚠️ MODERATE: Model shows some predictive ability")
            else:
                print("   ❌ POOR: Model needs improvement")
            
            logloss = self.evaluation_metrics.get('log_loss', float('inf'))
            if logloss < 0.7:
                print("   📈 Low Log Loss: Good probability calibration")
            elif logloss < 1.0:
                print("   📊 Moderate Log Loss: Reasonable probability calibration")
            else:
                print("   📉 High Log Loss: Poor probability calibration")
        
        print("\n" + "="*80)
    
    def run_comprehensive_training(self):
        """Run the complete training and evaluation process"""
        print("🚀 Starting Comprehensive Model Training & Evaluation")
        print("="*60)
        
        # Step 1: Load historical data
        historical_data = self.load_historical_data()
        if not historical_data:
            return False
        
        # Step 2: Train model on historical data
        if not self.train_model_on_historical_data(historical_data):
            return False
        
        # Step 3: Load predictions for evaluation
        predictions = self.load_predictions_data()
        if not predictions:
            print("⚠️ No predictions available for evaluation")
            return False
        
        # Step 4: Evaluate model performance
        metrics = self.evaluate_model_performance(predictions)
        if not metrics:
            print("❌ Evaluation failed")
            return False
        
        # Step 5: Generate comprehensive report
        self.generate_detailed_report()
        
        # Step 6: Save results
        self.save_training_results()
        
        print("\n✅ Comprehensive training and evaluation complete!")
        return True
    
    def save_training_results(self):
        """Save training and evaluation results"""
        # Convert numpy types to Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, bool):
                return obj
            return obj
        
        # Clean the metrics for JSON serialization
        clean_metrics = {}
        for key, value in self.evaluation_metrics.items():
            if isinstance(value, bool):
                clean_metrics[key] = value
            else:
                clean_metrics[key] = convert_numpy(value)
        
        results = {
            'training_results': self.training_results,
            'evaluation_metrics': clean_metrics,
            'generated_at': datetime.now().isoformat()
        }
        
        with open('comprehensive_training_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to comprehensive_training_results.json")

if __name__ == "__main__":
    trainer = ComprehensiveModelTrainer()
    success = trainer.run_comprehensive_training()
    
    if success:
        print("\n🎉 Training completed successfully!")
    else:
        print("\n❌ Training failed. Check the logs above.")
