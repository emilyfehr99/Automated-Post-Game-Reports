#!/usr/bin/env python3
"""
Test different hardcoded weights for goalie matchup and special teams to optimize accuracy
"""

import json
from pathlib import Path
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from prediction_interface import PredictionInterface
from correlation_model import CorrelationModel
import copy

def test_feature_weights(goalie_weight: float, special_teams_weight: float, window: int = 60):
    """Test specific feature weights"""
    
    model = ImprovedSelfLearningModelV2()
    corr_model = CorrelationModel()
    
    # Create a modified correlation model with custom weights
    class CustomCorrelationModel(CorrelationModel):
        def _score(self, feats):
            s = self.bias
            for k, w in self.weights.items():
                v = feats.get(k, 0.0)
                if k in ('power_play_diff','corsi_diff','faceoff_diff'):
                    v = v / 10.0
                if k == 'gs_diff':
                    v = v * 0.5
                s += w * v
            
            venue_win_pct_diff = feats.get('venue_win_pct_diff', 0.0)
            if venue_win_pct_diff != 0.0:
                s += 0.5 * venue_win_pct_diff
            
            recent_form_diff = feats.get('recent_form_diff', 0.0)
            if recent_form_diff != 0.0:
                s += 0.2 * recent_form_diff
            
            # Custom weights for new features
            goalie_matchup = feats.get('goalie_matchup_quality', 0.0)
            if goalie_matchup != 0.0:
                s += goalie_weight * goalie_matchup
            
            special_teams = feats.get('special_teams_matchup', 0.0)
            if special_teams != 0.0:
                s += special_teams_weight * special_teams
            
            return s
    
    custom_corr = CustomCorrelationModel()
    interface = PredictionInterface()
    
    # Load predictions
    predictions_file = Path("win_probability_predictions_v2.json")
    with open(predictions_file, 'r') as f:
        data = json.load(f)
    
    all_predictions = [p for p in data.get('predictions', []) if p.get('actual_winner')]
    if len(all_predictions) < window:
        return None
    
    test_predictions = all_predictions[-window:]
    
    correct = 0
    total = 0
    brier_sum = 0.0
    
    for pred in test_predictions:
        away_team = pred.get('away_team')
        home_team = pred.get('home_team')
        game_date = pred.get('date')
        actual_winner = pred.get('actual_winner')
        
        if not away_team or not home_team or not actual_winner:
            continue
        
        try:
            today_str = game_date or '2025-01-15'
            
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
            
            goalie_matchup_quality = model._calculate_goalie_matchup_quality(away_team, home_team, today_str)
            special_teams_matchup = model._calculate_special_teams_matchup(away_team, home_team)
            
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
            
            corr_pred = custom_corr.predict_from_metrics(metrics)
            ens_pred = model.ensemble_predict(away_team, home_team, game_date=today_str)
            
            # 70/30 blend
            if corr_pred and all(k in corr_pred for k in ('away_prob', 'home_prob')):
                away_blend = 0.7 * corr_pred['away_prob'] + 0.3 * ens_pred.get('away_prob', 0.5)
            else:
                away_blend = ens_pred.get('away_prob', 0.5)
            
            away_calibrated = model.apply_calibration(away_blend, context_bucket)
            home_calibrated = 1.0 - away_calibrated
            
            predicted_side = 'away' if away_calibrated > home_calibrated else 'home'
            
            if actual_winner in ('away', away_team):
                actual_side = 'away'
            elif actual_winner in ('home', home_team):
                actual_side = 'home'
            else:
                actual_side = None
            
            if actual_side:
                total += 1
                if predicted_side == actual_side:
                    correct += 1
                
                if actual_side == 'away':
                    brier_sum += (away_calibrated - 1.0)**2
                else:
                    brier_sum += (away_calibrated - 0.0)**2
                    
        except Exception:
            continue
    
    if total == 0:
        return None
    
    accuracy = correct / total
    brier_score = brier_sum / total
    
    return {
        'goalie_weight': goalie_weight,
        'special_teams_weight': special_teams_weight,
        'accuracy': accuracy,
        'brier_score': brier_score,
        'total': total,
        'correct': correct
    }

def main():
    """Test different feature weight combinations"""
    print("🔍 Testing different feature weights...\n")
    
    # Test combinations
    weight_combinations = [
        (0.1, 0.05),   # Low weights
        (0.2, 0.1),    # Medium-low
        (0.3, 0.15),   # Current
        (0.4, 0.2),    # Medium-high
        (0.5, 0.25),   # High
        (0.6, 0.3),    # Very high
        (0.3, 0.05),   # High goalie, low special teams
        (0.5, 0.1),    # Very high goalie, low special teams
        (0.1, 0.3),    # Low goalie, high special teams
    ]
    
    results = []
    for goalie_w, st_w in weight_combinations:
        result = test_feature_weights(goalie_w, st_w)
        if result:
            results.append(result)
            print(f"Goalie: {goalie_w:.2f}, Special Teams: {st_w:.2f} -> "
                  f"Accuracy: {result['accuracy']:.3f}, Brier: {result['brier_score']:.3f}")
    
    if results:
        best = max(results, key=lambda x: x['accuracy'])
        print(f"\n🏆 Best Feature Weights:")
        print(f"   Goalie Matchup: {best['goalie_weight']:.2f}")
        print(f"   Special Teams: {best['special_teams_weight']:.2f}")
        print(f"   Accuracy: {best['accuracy']:.3f} ({best['correct']}/{best['total']})")
        print(f"   Brier Score: {best['brier_score']:.3f}")
        
        return best
    return None

if __name__ == "__main__":
    main()

