#!/usr/bin/env python3
"""
Script to populate team stats from existing predictions
"""

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
import json

def populate_team_stats():
    print('🔄 POPULATING TEAM STATS FROM EXISTING PREDICTIONS')
    print('=' * 60)
    
    # Initialize model
    model = ImprovedSelfLearningModelV2()
    
    # Get all predictions with actual winners
    predictions_with_winners = [p for p in model.model_data["predictions"] if p.get("actual_winner")]
    
    print(f'Found {len(predictions_with_winners)} predictions with actual winners')
    
    # Process each prediction to update team stats
    for i, prediction in enumerate(predictions_with_winners):
        print(f'Processing {i+1}/{len(predictions_with_winners)}: {prediction["away_team"]} @ {prediction["home_team"]}')
        
        # Update team stats for this prediction
        model.update_team_stats(prediction)
    
    # Save the updated model data
    model.save_model_data()
    
    print(f'\\n✅ Team stats populated!')
    print(f'Teams with data: {len(model.team_stats)}')
    
    # Show some examples
    if len(model.team_stats) > 0:
        print('\\nSample team data:')
        for team in list(model.team_stats.keys())[:5]:
            home_games = len(model.team_stats[team].get('home', {}).get('games', []))
            away_games = len(model.team_stats[team].get('away', {}).get('games', []))
            print(f'  {team}: {home_games} home, {away_games} away games')

if __name__ == "__main__":
    populate_team_stats()
