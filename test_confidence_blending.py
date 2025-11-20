#!/usr/bin/env python3
"""
Test confidence-based dynamic blending - use more correlation model when confident,
more ensemble when uncertain
"""

import json
from pathlib import Path
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from correlation_model import CorrelationModel

def test_confidence_blending(window: int = 60):
    """Test confidence-based dynamic blending"""
    
    model = ImprovedSelfLearningModelV2()
    corr_model = CorrelationModel()
    
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
            
            corr_pred = corr_model.predict_from_metrics(metrics)
            ens_pred = model.ensemble_predict(away_team, home_team, game_date=today_str)
            
            if corr_pred and all(k in corr_pred for k in ('away_prob', 'home_prob')):
                # Calculate confidence from correlation model
                corr_confidence = abs(corr_pred['away_prob'] - 0.5) * 2  # 0 to 1
                
                # Dynamic blend: higher confidence = more correlation model
                # Range: 0.6-0.8 correlation weight based on confidence
                base_corr_weight = 0.7
                confidence_boost = corr_confidence * 0.1  # Up to 0.1 boost
                corr_weight = base_corr_weight + confidence_boost
                corr_weight = min(0.8, max(0.6, corr_weight))  # Clamp to 0.6-0.8
                ens_weight = 1.0 - corr_weight
                
                away_blend = corr_weight * corr_pred['away_prob'] + ens_weight * ens_pred.get('away_prob', 0.5)
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
        'accuracy': accuracy,
        'brier_score': brier_score,
        'total': total,
        'correct': correct
    }

if __name__ == "__main__":
    result = test_confidence_blending()
    if result:
        print(f"Confidence-Based Dynamic Blending:")
        print(f"  Accuracy: {result['accuracy']:.3f} ({result['correct']}/{result['total']})")
        print(f"  Brier Score: {result['brier_score']:.3f}")

