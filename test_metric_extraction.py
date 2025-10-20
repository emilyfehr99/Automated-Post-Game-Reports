#!/usr/bin/env python3
"""
Test script to debug metric extraction from game data
"""

import json
from pdf_report_generator import PostGameReportGenerator
from github_actions_runner import GitHubActionsRunner

def test_metric_extraction():
    print('🔍 TESTING METRIC EXTRACTION')
    print('=' * 40)
    
    # Initialize components
    generator = PostGameReportGenerator()
    runner = GitHubActionsRunner()
    
    # Load a recent game from the predictions
    with open('win_probability_predictions_v2.json', 'r') as f:
        data = json.load(f)
    
    # Get a recent prediction with actual winner
    recent_prediction = None
    for pred in reversed(data['predictions']):
        if pred.get('actual_winner') and pred.get('game_id'):
            recent_prediction = pred
            break
    
    if not recent_prediction:
        print('❌ No recent prediction with game_id found')
        return
    
    print(f'\\n📊 Testing with game: {recent_prediction["away_team"]} @ {recent_prediction["home_team"]}')
    print(f'Game ID: {recent_prediction["game_id"]}')
    print(f'Date: {recent_prediction["date"]}')
    
    # Try to get game data
    try:
        from nhl_api_client import NHLAPIClient
        api = NHLAPIClient()
        game_data = api.get_game_center(recent_prediction["game_id"])
        
        if not game_data:
            print('❌ Could not fetch game data')
            return
        
        print('✅ Game data fetched successfully')
        
        # Test metric extraction
        print('\\n🔧 Testing metric extraction...')
        
        try:
            away_period_stats = generator._calculate_real_period_stats(
                game_data, 
                game_data['boxscore']['awayTeam']['id'], 
                'away'
            )
            home_period_stats = generator._calculate_real_period_stats(
                game_data, 
                game_data['boxscore']['homeTeam']['id'], 
                'home'
            )
            
            print('✅ Period stats calculated successfully')
            print(f'\\nAway team period stats:')
            for key, value in away_period_stats.items():
                print(f'  {key}: {value}')
            
            print(f'\\nHome team period stats:')
            for key, value in home_period_stats.items():
                print(f'  {key}: {value}')
            
            # Test the full learning process
            print('\\n🎯 Testing full learning process...')
            runner.learn_from_game(
                game_data, 
                recent_prediction["game_id"], 
                recent_prediction["away_team"], 
                recent_prediction["home_team"]
            )
            print('✅ Learning process completed')
            
        except Exception as e:
            print(f'❌ Error in metric extraction: {e}')
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f'❌ Error fetching game data: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_metric_extraction()
