#!/usr/bin/env python3
"""
A/B Testing Framework for NHL Prediction Model
Allows testing different model configurations and comparing their performance
"""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from correlation_model import CorrelationModel
from prediction_interface import PredictionInterface


class ABTestFramework:
    """Framework for A/B testing different model configurations"""
    
    def __init__(self, predictions_file: str = "win_probability_predictions_v2.json"):
        self.predictions_file = Path(predictions_file)
        self.test_results_file = Path("ab_test_results.json")
        self.test_results = self._load_test_results()
    
    def _load_test_results(self) -> Dict:
        """Load existing test results"""
        if self.test_results_file.exists():
            try:
                with open(self.test_results_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"tests": []}
    
    def _save_test_results(self):
        """Save test results to file"""
        try:
            with open(self.test_results_file, 'w') as f:
                json.dump(self.test_results, f, indent=2)
        except Exception:
            pass
    
    def create_test_variant(self, variant_name: str, config: Dict) -> Dict:
        """Create a test variant configuration
        
        Args:
            variant_name: Name for this variant (e.g., 'baseline', 'with_goalie_matchup')
            config: Configuration dictionary with model parameters
                   Example: {
                       'correlation_weight': 0.7,
                       'ensemble_weight': 0.3,
                       'use_goalie_matchup': True,
                       'use_special_teams': True,
                       'calibration_enabled': True,
                       'context_aware_calibration': True
                   }
        """
        variant = {
            'name': variant_name,
            'config': config,
            'created_at': datetime.now().isoformat(),
            'predictions': [],
            'performance': {
                'total_games': 0,
                'correct_predictions': 0,
                'accuracy': 0.0,
                'brier_score': 0.0,
                'log_loss': 0.0,
                'recent_accuracy': 0.0
            }
        }
        return variant
    
    def run_ab_test(self, variant_a: Dict, variant_b: Dict, 
                    window: int = 60, test_name: Optional[str] = None) -> Dict:
        """Run A/B test comparing two variants on recent games
        
        Args:
            variant_a: First variant configuration
            variant_b: Second variant configuration
            window: Number of recent games to test on
            test_name: Optional name for this test run
        """
        if test_name is None:
            test_name = f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🧪 Running A/B Test: {test_name}")
        print(f"   Variant A: {variant_a['name']}")
        print(f"   Variant B: {variant_b['name']}")
        print(f"   Window: {window} games")
        
        # Load predictions with actual results
        try:
            with open(self.predictions_file, 'r') as f:
                data = json.load(f)
            all_predictions = [p for p in data.get('predictions', []) if p.get('actual_winner')]
        except Exception as e:
            print(f"❌ Error loading predictions: {e}")
            return None
        
        if len(all_predictions) < window:
            print(f"⚠️  Not enough games for {window}-game test. Found {len(all_predictions)}.")
            return None
        
        test_predictions = all_predictions[-window:]
        
        # Run predictions for both variants
        results_a = self._evaluate_variant(variant_a, test_predictions)
        results_b = self._evaluate_variant(variant_b, test_predictions)
        
        # Compare results
        comparison = self._compare_results(results_a, results_b)
        
        test_result = {
            'test_name': test_name,
            'timestamp': datetime.now().isoformat(),
            'window_size': window,
            'variant_a': {
                'name': variant_a['name'],
                'config': variant_a['config'],
                'results': results_a
            },
            'variant_b': {
                'name': variant_b['name'],
                'config': variant_b['config'],
                'results': results_b
            },
            'comparison': comparison
        }
        
        # Save test result
        self.test_results['tests'].append(test_result)
        self._save_test_results()
        
        # Print summary
        self._print_test_summary(test_result)
        
        return test_result
    
    def _evaluate_variant(self, variant: Dict, test_predictions: List[Dict]) -> Dict:
        """Evaluate a variant on test predictions"""
        config = variant['config']
        
        # Create model instances with variant configuration
        model = ImprovedSelfLearningModelV2()
        corr_model = CorrelationModel()
        
        # Apply configuration
        # Note: Some configs may require model modifications
        # For now, we'll use the existing models and adjust prediction logic
        
        correct = 0
        total = len(test_predictions)
        brier_sum = 0.0
        log_loss_sum = 0.0
        log_loss_count = 0
        
        for pred in test_predictions:
            away_team = pred.get('away_team')
            home_team = pred.get('home_team')
            game_date = pred.get('date')
            actual_winner = pred.get('actual_winner')
            
            if not away_team or not home_team:
                continue
            
            # Get prediction using variant configuration
            try:
                prediction = self._predict_with_variant(
                    model, corr_model, away_team, home_team, game_date, config
                )
                
                away_prob = prediction.get('away_prob', 0.5)
                home_prob = prediction.get('home_prob', 0.5)
                
                # Determine predicted winner
                predicted_side = 'away' if away_prob > home_prob else 'home'
                
                # Normalize actual winner
                actual_side = self._normalize_winner(actual_winner, away_team, home_team)
                
                if actual_side and predicted_side == actual_side:
                    correct += 1
                
                # Brier Score
                if actual_side == 'away':
                    brier_sum += (away_prob - 1.0)**2
                elif actual_side == 'home':
                    brier_sum += (away_prob - 0.0)**2
                
                # Log Loss
                if away_prob > 0 and away_prob < 1:
                    if actual_side == 'away':
                        log_loss_sum += -math.log(away_prob)
                    elif actual_side == 'home':
                        log_loss_sum += -math.log(1.0 - away_prob)
                    log_loss_count += 1
                    
            except Exception as e:
                print(f"⚠️  Error predicting {away_team} @ {home_team}: {e}")
                continue
        
        accuracy = correct / total if total > 0 else 0.0
        brier_score = brier_sum / total if total > 0 else 0.0
        log_loss = log_loss_sum / log_loss_count if log_loss_count > 0 else 0.0
        
        return {
            'total_games': total,
            'correct_predictions': correct,
            'accuracy': accuracy,
            'brier_score': brier_score,
            'log_loss': log_loss
        }
    
    def _predict_with_variant(self, model: ImprovedSelfLearningModelV2, 
                              corr_model: CorrelationModel,
                              away_team: str, home_team: str, 
                              game_date: Optional[str],
                              config: Dict) -> Dict:
        """Make prediction using variant configuration"""
        from prediction_interface import PredictionInterface
        
        # Use prediction interface to get metrics
        interface = PredictionInterface()
        
        # Build metrics (same as prediction_interface.predict_game)
        today_str = game_date or datetime.now().strftime('%Y-%m-%d')
        try:
            away_rest = model._calculate_rest_days_advantage(away_team, 'away', today_str)
            home_rest = model._calculate_rest_days_advantage(home_team, 'home', today_str)
        except Exception:
            away_rest = home_rest = 0.0
        
        context_bucket = model.determine_context_bucket(away_rest, home_rest)
        
        try:
            away_goalie_perf = model._goalie_performance_for_game(away_team, 'away', today_str)
            home_goalie_perf = model._goalie_performance_for_game(home_team, 'home', today_str)
        except Exception:
            away_goalie_perf = home_goalie_perf = 0.0
        
        # Calculate new features if enabled
        goalie_matchup_quality = 0.0
        special_teams_matchup = 0.0
        
        if config.get('use_goalie_matchup', False):
            try:
                goalie_matchup_quality = model._calculate_goalie_matchup_quality(
                    away_team, home_team, today_str
                )
            except Exception:
                pass
        
        if config.get('use_special_teams', False):
            try:
                special_teams_matchup = model._calculate_special_teams_matchup(away_team, home_team)
            except Exception:
                pass
        
        away_perf = model.get_team_performance(away_team, 'away')
        home_perf = model.get_team_performance(home_team, 'home')
        
        metrics = {
            'away_gs': away_perf.get('gs_avg', 0.0), 'home_gs': home_perf.get('gs_avg', 0.0),
            'away_power_play_pct': away_perf.get('power_play_avg', 0.0),
            'home_power_play_pct': home_perf.get('power_play_avg', 0.0),
            'away_corsi_pct': away_perf.get('corsi_avg', 50.0),
            'home_corsi_pct': home_perf.get('corsi_avg', 50.0),
            'away_rest': away_rest, 'home_rest': home_rest,
            'away_goalie_perf': away_goalie_perf, 'home_goalie_perf': home_goalie_perf,
            'goalie_matchup_quality': goalie_matchup_quality,
            'special_teams_matchup': special_teams_matchup,
        }
        
        # Get predictions
        corr_pred = corr_model.predict_from_metrics(metrics)
        ens_pred = model.ensemble_predict(away_team, home_team, game_date=today_str)
        
        # Blend based on config
        corr_weight = config.get('correlation_weight', 0.7)
        ens_weight = config.get('ensemble_weight', 0.3)
        
        if corr_pred and all(k in corr_pred for k in ('away_prob', 'home_prob')):
            away_blend = corr_weight * corr_pred['away_prob'] + ens_weight * ens_pred.get('away_prob', 0.5)
            home_blend = 1.0 - away_blend
        else:
            away_blend = ens_pred.get('away_prob', 0.5)
            home_blend = ens_pred.get('home_prob', 0.5)
        
        # Apply calibration if enabled
        if config.get('calibration_enabled', True):
            if config.get('context_aware_calibration', True):
                away_calibrated = model.apply_calibration(away_blend, context_bucket)
            else:
                away_calibrated = model.apply_calibration(away_blend, None)
            home_calibrated = 1.0 - away_calibrated
        else:
            away_calibrated = away_blend
            home_calibrated = home_blend
        
        return {
            'away_prob': away_calibrated,
            'home_prob': home_calibrated
        }
    
    def _normalize_winner(self, winner: Optional[str], away_team: str, home_team: str) -> Optional[str]:
        """Normalize winner to 'away' or 'home'"""
        if not winner:
            return None
        if winner in ('away', 'home'):
            return winner
        if winner.upper() == away_team.upper():
            return 'away'
        if winner.upper() == home_team.upper():
            return 'home'
        return None
    
    def _compare_results(self, results_a: Dict, results_b: Dict) -> Dict:
        """Compare results from two variants"""
        acc_diff = results_a['accuracy'] - results_b['accuracy']
        brier_diff = results_a['brier_score'] - results_b['brier_score']
        log_loss_diff = results_a['log_loss'] - results_b['log_loss']
        
        # Determine winner
        winner = None
        if abs(acc_diff) > 0.01:  # Significant difference threshold
            if acc_diff > 0:
                winner = 'variant_a'
            else:
                winner = 'variant_b'
        
        return {
            'accuracy_difference': acc_diff,
            'brier_difference': brier_diff,
            'log_loss_difference': log_loss_diff,
            'winner': winner,
            'significant_difference': abs(acc_diff) > 0.01
        }
    
    def _print_test_summary(self, test_result: Dict):
        """Print summary of test results"""
        print(f"\n📊 A/B Test Results: {test_result['test_name']}")
        print("=" * 60)
        
        var_a = test_result['variant_a']
        var_b = test_result['variant_b']
        comp = test_result['comparison']
        
        print(f"\nVariant A ({var_a['name']}):")
        print(f"  Accuracy: {var_a['results']['accuracy']:.3f}")
        print(f"  Brier Score: {var_a['results']['brier_score']:.3f}")
        print(f"  Log Loss: {var_a['results']['log_loss']:.3f}")
        
        print(f"\nVariant B ({var_b['name']}):")
        print(f"  Accuracy: {var_b['results']['accuracy']:.3f}")
        print(f"  Brier Score: {var_b['results']['brier_score']:.3f}")
        print(f"  Log Loss: {var_b['results']['log_loss']:.3f}")
        
        print(f"\nComparison:")
        print(f"  Accuracy Difference: {comp['accuracy_difference']:+.3f}")
        print(f"  Brier Difference: {comp['brier_difference']:+.3f}")
        print(f"  Log Loss Difference: {comp['log_loss_difference']:+.3f}")
        
        if comp['winner']:
            winner_name = var_a['name'] if comp['winner'] == 'variant_a' else var_b['name']
            print(f"\n🏆 Winner: {winner_name} ({comp['winner']})")
        else:
            print(f"\n🤝 No significant difference")
    
    def list_tests(self) -> List[Dict]:
        """List all previous test results"""
        return self.test_results.get('tests', [])
    
    def get_test_summary(self, test_name: str) -> Optional[Dict]:
        """Get summary of a specific test"""
        for test in self.test_results.get('tests', []):
            if test.get('test_name') == test_name:
                return test
        return None


def main():
    """Example A/B test"""
    framework = ABTestFramework()
    
    # Create baseline variant (current model)
    baseline = framework.create_test_variant('baseline', {
        'correlation_weight': 0.7,
        'ensemble_weight': 0.3,
        'use_goalie_matchup': False,
        'use_special_teams': False,
        'calibration_enabled': True,
        'context_aware_calibration': True
    })
    
    # Create variant with new features
    with_features = framework.create_test_variant('with_new_features', {
        'correlation_weight': 0.7,
        'ensemble_weight': 0.3,
        'use_goalie_matchup': True,
        'use_special_teams': True,
        'calibration_enabled': True,
        'context_aware_calibration': True
    })
    
    # Run A/B test
    result = framework.run_ab_test(baseline, with_features, window=60)
    
    if result:
        print(f"\n✅ Test completed and saved")
        print(f"   Results saved to: ab_test_results.json")


if __name__ == "__main__":
    main()

