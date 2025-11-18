#!/usr/bin/env python3
"""
Live In-Game NHL Predictions
Makes real-time predictions during active games using current game state
"""

import json
import requests
import time
from datetime import datetime, timedelta
import pytz
from pathlib import Path
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from nhl_api_client import NHLAPIClient

class LiveGamePredictor:
    def __init__(self):
        self.api = NHLAPIClient()
        self.model = ImprovedSelfLearningModelV2()
        self.ct_tz = pytz.timezone('US/Central')
        
    def get_live_games(self):
        """Get all currently active NHL games"""
        try:
            # Get today's games
            today = datetime.now(self.ct_tz).strftime('%Y-%m-%d')
            schedule = self.api.get_game_schedule(today)
            
            live_games = []
            for game in schedule:
                game_status = game.get('status', {}).get('detailedState', '')
                if game_status in ['In Progress', 'In Progress - Critical']:
                    live_games.append(game)
                    
            return live_games
        except Exception as e:
            print(f"❌ Error getting live games: {e}")
            return []
    
    def get_game_state(self, game_id):
        """Get current game state including score, period, time remaining"""
        try:
            game_data = self.api.get_comprehensive_game_data(game_id)
            if not game_data:
                return None
                
            # Extract current game state
            boxscore = game_data.get('game_center', {}).get('boxscore', {})
            teams = boxscore.get('teams', {})
            
            away_team = teams.get('away', {})
            home_team = teams.get('home', {})
            
            # Get current score
            away_score = away_team.get('teamStats', {}).get('teamSkaterStats', {}).get('goals', 0)
            home_score = home_team.get('teamStats', {}).get('teamSkaterStats', {}).get('goals', 0)
            
            # Get period info
            period_info = boxscore.get('periodInfo', {})
            current_period = period_info.get('currentPeriod', 1)
            time_remaining = period_info.get('timeRemaining', '20:00')
            
            return {
                'away_team': away_team.get('team', {}).get('abbreviation', ''),
                'home_team': home_team.get('team', {}).get('abbreviation', ''),
                'away_score': away_score,
                'home_score': home_score,
                'current_period': current_period,
                'time_remaining': time_remaining,
                'game_id': game_id
            }
        except Exception as e:
            print(f"❌ Error getting game state for {game_id}: {e}")
            return None
    
    def predict_live_game(self, game_state):
        """Make live prediction for a game in progress"""
        try:
            away_team = game_state['away_team']
            home_team = game_state['home_team']
            away_score = game_state['away_score']
            home_score = game_state['home_score']
            current_period = game_state['current_period']
            time_remaining = game_state['time_remaining']
            
            # Get team performance data
            away_perf = self.model.get_team_performance(away_team, 'away')
            home_perf = self.model.get_team_performance(home_team, 'home')
            
            # Calculate score differential impact
            score_diff = away_score - home_score
            score_impact = score_diff * 0.1  # Each goal difference = 10% probability shift
            
            # Calculate period impact (later periods = more certain)
            period_impact = (current_period - 1) * 0.05  # Each period = 5% more certainty
            
            # Get base prediction
            base_prediction = self.model.ensemble_predict(away_team, home_team)
            away_prob = base_prediction['away_prob']
            home_prob = base_prediction['home_prob']
            
            # Adjust for current score
            away_prob += score_impact
            home_prob -= score_impact
            
            # Adjust for period (later periods = more certain)
            if current_period > 1:
                if away_score > home_score:
                    away_prob += period_impact
                    home_prob -= period_impact
                elif home_score > away_score:
                    home_prob += period_impact
                    away_prob -= period_impact
            
            # Normalize probabilities
            total = away_prob + home_prob
            away_prob = max(0.01, min(0.99, away_prob / total))
            home_prob = max(0.01, min(0.99, home_prob / total))
            
            # Calculate confidence based on game state
            confidence = 0.5 + (current_period - 1) * 0.1  # More confident in later periods
            confidence = min(0.95, confidence)
            
            return {
                'away_team': away_team,
                'home_team': home_team,
                'away_score': away_score,
                'home_score': home_score,
                'current_period': current_period,
                'time_remaining': time_remaining,
                'away_prob': away_prob,
                'home_prob': home_prob,
                'confidence': confidence,
                'score_impact': score_impact,
                'period_impact': period_impact
            }
            
        except Exception as e:
            print(f"❌ Error making live prediction: {e}")
            return None
    
    def format_live_prediction(self, prediction):
        """Format live prediction for display"""
        if not prediction:
            return "❌ Could not generate prediction"
            
        away_team = prediction['away_team']
        home_team = prediction['home_team']
        away_score = prediction['away_score']
        home_score = prediction['home_score']
        current_period = prediction['current_period']
        time_remaining = prediction['time_remaining']
        away_prob = prediction['away_prob']
        home_prob = prediction['home_prob']
        confidence = prediction['confidence']
        
        # Determine favorite
        if away_prob > home_prob:
            favorite = f"{away_team} (+{(away_prob - home_prob) * 100:.1f}%)"
        else:
            favorite = f"{home_team} (+{(home_prob - away_prob) * 100:.1f}%)"
        
        return f"""
🏒 LIVE GAME PREDICTION
{'=' * 50}
📊 {away_team} @ {home_team}
🎯 Score: {away_team} {away_score} - {home_score} {home_team}
⏰ Period {current_period} - {time_remaining} remaining

🎯 Live Prediction:
   {away_team}: {away_prob * 100:.1f}%
   {home_team}: {home_prob * 100:.1f}%
   ⭐ Favorite: {favorite}

📈 Confidence: {confidence * 100:.1f}%
🔄 Updated: {datetime.now(self.ct_tz).strftime('%H:%M:%S CT')}
"""
    
    def run_live_predictions(self, update_interval=30):
        """Run live predictions with automatic updates"""
        print("🏒 LIVE NHL GAME PREDICTIONS")
        print("=" * 50)
        print(f"🔄 Update interval: {update_interval} seconds")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                live_games = self.get_live_games()
                
                if not live_games:
                    print(f"⏰ {datetime.now(self.ct_tz).strftime('%H:%M:%S CT')} - No live games")
                else:
                    print(f"⏰ {datetime.now(self.ct_tz).strftime('%H:%M:%S CT')} - {len(live_games)} live games")
                    print()
                    
                    for game in live_games:
                        game_id = game.get('id')
                        game_state = self.get_game_state(game_id)
                        
                        if game_state:
                            prediction = self.predict_live_game(game_state)
                            if prediction:
                                print(self.format_live_prediction(prediction))
                                print()
                
                print(f"⏳ Waiting {update_interval} seconds for next update...")
                time.sleep(update_interval)
                print()
                
        except KeyboardInterrupt:
            print("\n🛑 Live predictions stopped")
        except Exception as e:
            print(f"\n❌ Error in live predictions: {e}")

def main():
    predictor = LiveGamePredictor()
    
    print("🏒 LIVE NHL GAME PREDICTIONS")
    print("=" * 50)
    print("1. Get current live games")
    print("2. Run continuous live predictions")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        live_games = predictor.get_live_games()
        if live_games:
            print(f"\n📊 Found {len(live_games)} live games:")
            for game in live_games:
                game_id = game.get('id')
                game_state = predictor.get_game_state(game_id)
                if game_state:
                    prediction = predictor.predict_live_game(game_state)
                    if prediction:
                        print(predictor.format_live_prediction(prediction))
        else:
            print("\n⏰ No live games currently")
            
    elif choice == "2":
        interval = input("Update interval in seconds (default 30): ").strip()
        try:
            interval = int(interval) if interval else 30
        except ValueError:
            interval = 30
        predictor.run_live_predictions(interval)
        
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
