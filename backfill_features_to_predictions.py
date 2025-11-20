#!/usr/bin/env python3
"""
Backfill goalie matchup and special teams matchup features into historical predictions
so the correlation model can learn optimal weights from them.
"""

import json
from pathlib import Path
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from prediction_interface import PredictionInterface

def backfill_features_to_predictions():
    """Add goalie matchup and special teams matchup to historical predictions"""
    
    model = ImprovedSelfLearningModelV2()
    interface = PredictionInterface()
    
    predictions_file = Path("win_probability_predictions_v2.json")
    with open(predictions_file, 'r') as f:
        data = json.load(f)
    
    predictions = data.get('predictions', [])
    updated = 0
    
    print(f"Processing {len(predictions)} predictions...")
    
    for i, pred in enumerate(predictions):
        if not pred.get('actual_winner'):
            continue
        
        metrics = pred.get('metrics_used', {})
        if not metrics:
            continue
        
        away_team = pred.get('away_team')
        home_team = pred.get('home_team')
        game_date = pred.get('date')
        
        if not away_team or not home_team or not game_date:
            continue
        
        # Check if features already exist
        if 'goalie_matchup_quality' in metrics and 'special_teams_matchup' in metrics:
            if metrics.get('goalie_matchup_quality') is not None and metrics.get('special_teams_matchup') is not None:
                continue  # Already has features
        
        try:
            # Calculate goalie matchup quality
            goalie_matchup = model._calculate_goalie_matchup_quality(
                away_team, home_team, game_date
            )
            
            # Calculate special teams matchup
            special_teams = model._calculate_special_teams_matchup(away_team, home_team)
            
            # Add to metrics
            metrics['goalie_matchup_quality'] = goalie_matchup
            metrics['special_teams_matchup'] = special_teams
            
            pred['metrics_used'] = metrics
            updated += 1
            
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(predictions)} predictions...")
                
        except Exception as e:
            print(f"  Error processing {away_team} @ {home_team} on {game_date}: {e}")
            continue
    
    if updated > 0:
        print(f"\n✅ Updated {updated} predictions with new features")
        data['predictions'] = predictions
        with open(predictions_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"✅ Saved updated predictions to {predictions_file}")
    else:
        print("\nℹ️  No predictions needed updating")
    
    return updated

if __name__ == "__main__":
    backfill_features_to_predictions()

