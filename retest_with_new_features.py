#!/usr/bin/env python3
"""
Re-test accuracy by re-predicting historical games with new features enabled
"""

import json
from pathlib import Path
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from prediction_interface import PredictionInterface
from correlation_model import CorrelationModel

def retest_with_new_features(window=60):
    """Re-predict historical games with new features and compare accuracy"""
    
    # Load historical predictions
    predictions_file = Path("win_probability_predictions_v2.json")
    with open(predictions_file, 'r') as f:
        data = json.load(f)
    
    # Get completed games
    all_predictions = [p for p in data.get('predictions', []) if p.get('actual_winner')]
    if len(all_predictions) < window:
        print(f"Not enough games. Found {len(all_predictions)}, need {window}")
        return
    
    test_predictions = all_predictions[-window:]
    
    # Initialize models
    model = ImprovedSelfLearningModelV2()
    corr_model = CorrelationModel()
    interface = PredictionInterface()
    
    # Re-predict with new features
    correct = 0
    total = 0
    brier_sum = 0.0
    log_loss_sum = 0.0
    log_loss_count = 0
    
    print(f"Re-predicting {len(test_predictions)} games with new features...")
    
    for i, pred in enumerate(test_predictions):
        away_team = pred.get('away_team')
        home_team = pred.get('home_team')
        game_date = pred.get('date')
        actual_winner = pred.get('actual_winner')
        
        if not away_team or not home_team or not actual_winner:
            continue
        
        try:
            # Make new prediction with features
            new_pred = interface.predict_game(away_team, home_team, game_id=None)
            
            away_prob = new_pred.get('away_prob', 0.5)
            home_prob = new_pred.get('home_prob', 0.5)
            
            # Check if features were calculated
            if i == 0:  # Print first prediction details
                print(f"\nFirst prediction ({away_team} @ {home_team}):")
                print(f"  Goalie matchup quality: {new_pred.get('goalie_matchup_quality', 'N/A')}")
                print(f"  Special teams matchup: {new_pred.get('special_teams_matchup', 'N/A')}")
            
            # Determine predicted winner
            predicted_side = 'away' if away_prob > home_prob else 'home'
            
            # Normalize actual winner (handle both team abbrev and 'away'/'home')
            if actual_winner in ('away', 'home'):
                actual_side = actual_winner
            elif actual_winner and isinstance(actual_winner, str):
                if actual_winner.upper() == away_team.upper():
                    actual_side = 'away'
                elif actual_winner.upper() == home_team.upper():
                    actual_side = 'home'
                else:
                    actual_side = None
            else:
                actual_side = None
            
            if actual_side:
                total += 1
                if predicted_side == actual_side:
                    correct += 1
                
                # Brier Score
                if actual_side == 'away':
                    brier_sum += (away_prob - 1.0)**2
                else:
                    brier_sum += (away_prob - 0.0)**2
                
                # Log Loss
                if away_prob > 0 and away_prob < 1:
                    if actual_side == 'away':
                        log_loss_sum += -np.log(away_prob)
                    else:
                        log_loss_sum += -np.log(1.0 - away_prob)
                    log_loss_count += 1
                    
        except Exception as e:
            print(f"Error predicting {away_team} @ {home_team}: {e}")
            continue
    
    accuracy = correct / total if total > 0 else 0.0
    brier_score = brier_sum / total if total > 0 else 0.0
    log_loss = log_loss_sum / log_loss_count if log_loss_count > 0 else 0.0
    
    print(f"\n{'='*60}")
    print(f"Re-test Results (with new features):")
    print(f"  Sample Size: {total}")
    print(f"  Accuracy: {accuracy:.3f} ({correct}/{total})")
    print(f"  Brier Score: {brier_score:.3f}")
    print(f"  Log Loss: {log_loss:.3f}")
    print(f"{'='*60}")
    
    return {
        'accuracy': accuracy,
        'brier_score': brier_score,
        'log_loss': log_loss,
        'total': total,
        'correct': correct
    }

if __name__ == "__main__":
    import numpy as np
    retest_with_new_features()

