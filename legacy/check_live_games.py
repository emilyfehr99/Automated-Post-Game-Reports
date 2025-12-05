#!/usr/bin/env python3
"""
Check for live NHL games and make predictions
"""

import json
import requests
from datetime import datetime
import pytz
from pathlib import Path
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from nhl_api_client import NHLAPIClient

def check_live_games():
    """Check for live games and make predictions"""
    print("🏒 CHECKING FOR LIVE NHL GAMES")
    print("=" * 50)
    
    try:
        # Initialize components
        api = NHLAPIClient()
        model = ImprovedSelfLearningModelV2()
        ct_tz = pytz.timezone('US/Central')
        
        # Get today's games
        today = datetime.now(ct_tz).strftime('%Y-%m-%d')
        print(f"📅 Checking games for: {today}")
        
        schedule = api.get_game_schedule(today)
        if not schedule:
            print("❌ No games found for today")
            return
            
        print(f"📊 Found {len(schedule)} games scheduled")
        
        # Check for live games
        live_games = []
        for game in schedule:
            game_status = game.get('status', {}).get('detailedState', '')
            if game_status in ['In Progress', 'In Progress - Critical']:
                live_games.append(game)
                
        if not live_games:
            print("⏰ No live games currently")
            return
            
        print(f"🔥 Found {len(live_games)} live games!")
        print()
        
        # Process each live game
        for i, game in enumerate(live_games, 1):
            game_id = game.get('id')
            away_team = game.get('teams', {}).get('away', {}).get('team', {}).get('abbreviation', '')
            home_team = game.get('teams', {}).get('home', {}).get('team', {}).get('abbreviation', '')
            
            print(f"🏒 LIVE GAME #{i}: {away_team} @ {home_team}")
            print(f"🆔 Game ID: {game_id}")
            
            # Get current game state
            try:
                game_data = api.get_comprehensive_game_data(game_id)
                if not game_data:
                    print("❌ Could not get game data")
                    continue
                    
                # Extract current state
                boxscore = game_data.get('game_center', {}).get('boxscore', {})
                teams = boxscore.get('teams', {})
                
                away_team_data = teams.get('away', {})
                home_team_data = teams.get('home', {})
                
                # Get current score
                away_score = away_team_data.get('teamStats', {}).get('teamSkaterStats', {}).get('goals', 0)
                home_score = home_team_data.get('teamStats', {}).get('teamSkaterStats', {}).get('goals', 0)
                
                # Get period info
                period_info = boxscore.get('periodInfo', {})
                current_period = period_info.get('currentPeriod', 1)
                time_remaining = period_info.get('timeRemaining', '20:00')
                
                print(f"📊 Current Score: {away_team} {away_score} - {home_score} {home_team}")
                print(f"⏰ Period {current_period} - {time_remaining} remaining")
                
                # Make live prediction
                try:
                    # Get team performance
                    away_perf = model.get_team_performance(away_team, 'away')
                    home_perf = model.get_team_performance(home_team, 'home')
                    
                    # Calculate score differential impact
                    score_diff = away_score - home_score
                    score_impact = score_diff * 0.1  # Each goal = 10% shift
                    
                    # Get base prediction
                    base_prediction = model.ensemble_predict(away_team, home_team)
                    away_prob = base_prediction['away_prob']
                    home_prob = base_prediction['home_prob']
                    
                    # Adjust for current score
                    away_prob += score_impact
                    home_prob -= score_impact
                    
                    # Normalize
                    total = away_prob + home_prob
                    away_prob = max(0.01, min(0.99, away_prob / total))
                    home_prob = max(0.01, min(0.99, home_prob / total))
                    
                    # Calculate confidence
                    confidence = 0.5 + (current_period - 1) * 0.1
                    confidence = min(0.95, confidence)
                    
                    # Determine favorite
                    if away_prob > home_prob:
                        favorite = f"{away_team} (+{(away_prob - home_prob) * 100:.1f}%)"
                    else:
                        favorite = f"{home_team} (+{(home_prob - away_prob) * 100:.1f}%)"
                    
                    print(f"🎯 LIVE PREDICTION:")
                    print(f"   {away_team}: {away_prob * 100:.1f}%")
                    print(f"   {home_team}: {home_prob * 100:.1f}%")
                    print(f"   ⭐ Favorite: {favorite}")
                    print(f"📈 Confidence: {confidence * 100:.1f}%")
                    
                    if score_diff != 0:
                        print(f"📊 Score Impact: {score_impact * 100:+.1f}%")
                    
                except Exception as e:
                    print(f"❌ Error making prediction: {e}")
                    
            except Exception as e:
                print(f"❌ Error getting game state: {e}")
                
            print()
            
    except Exception as e:
        print(f"❌ Error checking live games: {e}")

if __name__ == "__main__":
    check_live_games()
