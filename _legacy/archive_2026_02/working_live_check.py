#!/usr/bin/env python3
"""
Working Live NHL Game Checker
"""

from nhl_api_client import NHLAPIClient
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from datetime import datetime
import pytz

def check_live_games():
    """Check for live games and make predictions"""
    print("🏒 LIVE NHL GAME CHECKER")
    print("=" * 40)
    
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
            
        # Extract games from the correct structure
        games = []
        if 'gameWeek' in schedule and len(schedule['gameWeek']) > 0:
            for day in schedule['gameWeek']:
                if 'games' in day:
                    games.extend(day['games'])
        
        print(f"📊 Found {len(games)} games scheduled")
        
        # Check for live games
        live_games = []
        for game in games:
            game_state = game.get('gameState', '')
            if game_state in ['LIVE', 'CRIT']:
                live_games.append(game)
                
        if not live_games:
            print("⏰ No live games currently")
            print("\n📋 All games today:")
            for game in games:
                away_team = game.get('awayTeam', {}).get('abbrev', '?')
                home_team = game.get('homeTeam', {}).get('abbrev', '?')
                game_state = game.get('gameState', '?')
                start_time = game.get('startTimeUTC', '?')
                print(f"  🏒 {away_team} @ {home_team} - {game_state}")
            return
            
        print(f"🔥 Found {len(live_games)} live games!")
        print()
        
        # Process each live game
        for i, game in enumerate(live_games, 1):
            game_id = game.get('id')
            away_team = game.get('awayTeam', {}).get('abbrev', '')
            home_team = game.get('homeTeam', {}).get('abbrev', '')
            game_state = game.get('gameState', '')
            
            print(f"🏒 LIVE GAME #{i}: {away_team} @ {home_team}")
            print(f"🆔 Game ID: {game_id}")
            print(f"📊 Status: {game_state}")
            
            # Make live prediction
            try:
                # Get team performance
                away_perf = model.get_team_performance(away_team, 'away')
                home_perf = model.get_team_performance(home_team, 'home')
                
                # Get base prediction
                base_prediction = model.ensemble_predict(away_team, home_team)
                away_prob = base_prediction['away_prob']
                home_prob = base_prediction['home_prob']
                
                # Determine favorite
                if away_prob > home_prob:
                    favorite = f"{away_team} (+{(away_prob - home_prob) * 100:.1f}%)"
                else:
                    favorite = f"{home_team} (+{(home_prob - away_prob) * 100:.1f}%)"
                
                print(f"🎯 LIVE PREDICTION:")
                print(f"   {away_team}: {away_prob * 100:.1f}%")
                print(f"   {home_team}: {home_prob * 100:.1f}%")
                print(f"   ⭐ Favorite: {favorite}")
                
            except Exception as e:
                print(f"❌ Error making prediction: {e}")
                
            print()
            
    except Exception as e:
        print(f"❌ Error checking live games: {e}")

if __name__ == "__main__":
    check_live_games()
