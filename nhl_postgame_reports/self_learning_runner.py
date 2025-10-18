"""
Self-Learning Model Runner
Runs alongside the existing post-game reports without affecting them
"""

import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from nhl_api_client import NHLAPIClient
from self_learning_model import SelfLearningWinProbabilityModel


class SelfLearningRunner:
    """Runner for the self-learning win probability model"""
    
    def __init__(self):
        self.client = NHLAPIClient()
        self.model = SelfLearningWinProbabilityModel()
    
    def process_todays_games(self):
        """Process today's games to make predictions"""
        print("🧠 SELF-LEARNING MODEL - PROCESSING TODAY'S GAMES")
        print("=" * 60)
        
        # Get today's games
        central_tz = timezone(timedelta(hours=-6))
        central_now = datetime.now(central_tz)
        today_str = central_now.strftime('%Y-%m-%d')
        
        print(f"📅 Processing games from: {today_str}")
        
        try:
            schedule = self.client.get_game_schedule(today_str)
            if not schedule or 'gameWeek' not in schedule:
                print("No games found for today")
                return
            
            games = []
            for day in schedule['gameWeek']:
                if day.get('date') == today_str and 'games' in day:
                    games.extend(day['games'])
            
            print(f"🔍 Found {len(games)} games today")
            
            # Process each game
            for game in games:
                game_id = str(game.get('id'))
                game_state = game.get('gameState', 'UNKNOWN')
                away_team = game.get('awayTeam', {}).get('abbrev', 'UNK')
                home_team = game.get('homeTeam', {}).get('abbrev', 'UNK')
                
                print(f"   {away_team} @ {home_team}: {game_state}")
                
                # Only make predictions for completed games
                if game_state == 'OFF':
                    # Check if we already have a prediction for this game
                    existing_prediction = None
                    for pred in self.model.predictions:
                        if pred.game_id == game_id:
                            existing_prediction = pred
                            break
                    
                    if existing_prediction:
                        print(f"     ✅ Already have prediction for {away_team} @ {home_team}")
                        continue
                    
                    # Get game data and make prediction
                    try:
                        game_data = {
                            'boxscore': self.client.get_game_boxscore(game_id),
                            'play_by_play': self.client.get_play_by_play(game_id)
                        }
                        
                        # Record prediction
                        prediction = self.model.record_prediction(game_data, game_id)
                        
                        if prediction:
                            print(f"     📊 New prediction recorded for {away_team} @ {home_team}")
                        
                    except Exception as e:
                        print(f"     ❌ Error processing {away_team} @ {home_team}: {e}")
            
            # Save predictions
            self.model.save_predictions()
            
        except Exception as e:
            print(f"❌ Error processing today's games: {e}")
    
    def run_full_update(self):
        """Run full update: process today's games and update outcomes"""
        print("🧠 SELF-LEARNING WIN PROBABILITY MODEL - FULL UPDATE")
        print("=" * 60)
        
        # Process today's games for new predictions
        self.process_todays_games()
        
        # Process completed games to update outcomes
        self.model.process_completed_games()
        
        # Retrain model
        self.model.retrain_model()
        
        # Show stats
        stats = self.model.get_model_stats()
        print(f"\n📊 Model Statistics:")
        print(f"   - Total predictions: {stats['total_predictions']}")
        print(f"   - Completed predictions: {stats['completed_predictions']}")
        print(f"   - Average accuracy: {stats['average_accuracy']:.3f}")
        
        print("\n✅ Full update completed!")


if __name__ == "__main__":
    runner = SelfLearningRunner()
    runner.run_full_update()
