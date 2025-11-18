#!/usr/bin/env python3
"""
True Live In-Game NHL Predictions
Uses real-time game data, scores, and metrics to make predictions that change as the game progresses
"""

import json
import requests
import time
from datetime import datetime, timedelta
import pytz
from pathlib import Path
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from nhl_api_client import NHLAPIClient

class LiveInGamePredictor:
    def __init__(self):
        self.api = NHLAPIClient()
        self.model = ImprovedSelfLearningModelV2()
        self.ct_tz = pytz.timezone('US/Central')
        
    def get_live_games(self):
        """Get all currently active NHL games"""
        try:
            today = datetime.now(self.ct_tz).strftime('%Y-%m-%d')
            schedule = self.api.get_game_schedule(today)
            
            if not schedule or 'gameWeek' not in schedule:
                return []
                
            games = []
            for day in schedule['gameWeek']:
                if 'games' in day:
                    games.extend(day['games'])
            
            live_games = []
            for game in games:
                game_state = game.get('gameState', '')
                if game_state in ['LIVE', 'CRIT']:
                    live_games.append(game)
                    
            return live_games
        except Exception as e:
            print(f"❌ Error getting live games: {e}")
            return []
    
    def get_live_game_data(self, game_id):
        """Get comprehensive live game data including scores, metrics, and game state"""
        try:
            game_data = self.api.get_comprehensive_game_data(game_id)
            if not game_data:
                return None
                
            # Extract live game state
            boxscore = game_data.get('game_center', {}).get('boxscore', {})
            teams = boxscore.get('teams', {})
            
            away_team = teams.get('away', {})
            home_team = teams.get('home', {})
            
            # Get current score
            away_score = away_team.get('teamStats', {}).get('teamSkaterStats', {}).get('goals', 0)
            home_score = home_team.get('teamStats', {}).get('teamSkaterStats', {}).get('goals', 0)
            
            # Get period and time info
            period_info = boxscore.get('periodInfo', {})
            current_period = period_info.get('currentPeriod', 1)
            time_remaining = period_info.get('timeRemaining', '20:00')
            
            # Get live game metrics
            away_stats = away_team.get('teamStats', {}).get('teamSkaterStats', {})
            home_stats = home_team.get('teamStats', {}).get('teamSkaterStats', {})
            
            live_metrics = {
                'away_team': away_team.get('team', {}).get('abbreviation', ''),
                'home_team': home_team.get('team', {}).get('abbreviation', ''),
                'away_score': away_score,
                'home_score': home_score,
                'current_period': current_period,
                'time_remaining': time_remaining,
                'away_shots': away_stats.get('shots', 0),
                'home_shots': home_stats.get('shots', 0),
                'away_hits': away_stats.get('hits', 0),
                'home_hits': home_stats.get('hits', 0),
                'away_pim': away_stats.get('pim', 0),
                'home_pim': home_stats.get('pim', 0),
                'away_faceoff_wins': away_stats.get('faceOffWins', 0),
                'home_faceoff_wins': home_stats.get('faceOffWins', 0),
                'away_power_play_goals': away_stats.get('powerPlayGoals', 0),
                'home_power_play_goals': home_stats.get('powerPlayGoals', 0),
                'away_power_play_opportunities': away_stats.get('powerPlayOpportunities', 0),
                'home_power_play_opportunities': home_stats.get('powerPlayOpportunities', 0),
                'game_id': game_id
            }
            
            return live_metrics
        except Exception as e:
            print(f"❌ Error getting live game data for {game_id}: {e}")
            return None
    
    def calculate_live_momentum(self, live_metrics):
        """Calculate momentum factors based on live game data"""
        try:
            away_score = live_metrics['away_score']
            home_score = live_metrics['home_score']
            current_period = live_metrics['current_period']
            time_remaining = live_metrics['time_remaining']
            
            # Score differential impact (stronger in later periods)
            score_diff = away_score - home_score
            period_multiplier = 0.1 + (current_period - 1) * 0.05  # More impact in later periods
            score_impact = score_diff * period_multiplier
            
            # Time pressure (less time = more impact)
            try:
                time_parts = time_remaining.split(':')
                minutes = int(time_parts[0])
                seconds = int(time_parts[1])
                total_seconds = minutes * 60 + seconds
                time_pressure = max(0, (1200 - total_seconds) / 1200)  # 0-1 scale
            except:
                time_pressure = 0.5  # Default if time parsing fails
            
            # Shot differential impact
            away_shots = live_metrics['away_shots']
            home_shots = live_metrics['home_shots']
            shot_diff = (away_shots - home_shots) * 0.02  # 2% per shot difference
            
            # Power play impact
            away_pp_goals = live_metrics['away_power_play_goals']
            home_pp_goals = live_metrics['home_power_play_goals']
            pp_impact = (away_pp_goals - home_pp_goals) * 0.05  # 5% per PP goal
            
            # Faceoff dominance
            away_faceoffs = live_metrics['away_faceoff_wins']
            home_faceoffs = live_metrics['home_faceoff_wins']
            total_faceoffs = away_faceoffs + home_faceoffs
            if total_faceoffs > 0:
                faceoff_impact = ((away_faceoffs - home_faceoffs) / total_faceoffs) * 0.03
            else:
                faceoff_impact = 0
            
            return {
                'score_impact': score_impact,
                'time_pressure': time_pressure,
                'shot_impact': shot_diff,
                'pp_impact': pp_impact,
                'faceoff_impact': faceoff_impact,
                'total_momentum': score_impact + shot_diff + pp_impact + faceoff_impact
            }
        except Exception as e:
            print(f"❌ Error calculating momentum: {e}")
            return {
                'score_impact': 0,
                'time_pressure': 0.5,
                'shot_impact': 0,
                'pp_impact': 0,
                'faceoff_impact': 0,
                'total_momentum': 0
            }
    
    def predict_live_game(self, live_metrics):
        """Make live in-game prediction using real-time data"""
        try:
            away_team = live_metrics['away_team']
            home_team = live_metrics['home_team']
            
            # Get base prediction from historical data
            base_prediction = self.model.ensemble_predict(away_team, home_team)
            away_prob = base_prediction['away_prob']
            home_prob = base_prediction['home_prob']
            
            # Calculate live momentum factors
            momentum = self.calculate_live_momentum(live_metrics)
            
            # Apply live adjustments
            away_prob += momentum['total_momentum']
            home_prob -= momentum['total_momentum']
            
            # Apply time pressure (later periods = more certain)
            time_pressure = momentum['time_pressure']
            if live_metrics['away_score'] > live_metrics['home_score']:
                away_prob += time_pressure * 0.1
                home_prob -= time_pressure * 0.1
            elif live_metrics['home_score'] > live_metrics['away_score']:
                home_prob += time_pressure * 0.1
                away_prob -= time_pressure * 0.1
            
            # Normalize probabilities
            total = away_prob + home_prob
            away_prob = max(0.01, min(0.99, away_prob / total))
            home_prob = max(0.01, min(0.99, home_prob / total))
            
            # Calculate confidence based on game state
            confidence = 0.5 + (live_metrics['current_period'] - 1) * 0.1
            confidence = min(0.95, confidence)
            
            return {
                'away_team': away_team,
                'home_team': home_team,
                'away_score': live_metrics['away_score'],
                'home_score': live_metrics['home_score'],
                'current_period': live_metrics['current_period'],
                'time_remaining': live_metrics['time_remaining'],
                'away_prob': away_prob,
                'home_prob': home_prob,
                'confidence': confidence,
                'momentum': momentum,
                'live_metrics': live_metrics
            }
            
        except Exception as e:
            print(f"❌ Error making live prediction: {e}")
            return None
    
    def format_live_prediction(self, prediction):
        """Format live in-game prediction for display"""
        if not prediction:
            return "❌ Could not generate live prediction"
            
        away_team = prediction['away_team']
        home_team = prediction['home_team']
        away_score = prediction['away_score']
        home_score = prediction['home_score']
        current_period = prediction['current_period']
        time_remaining = prediction['time_remaining']
        away_prob = prediction['away_prob']
        home_prob = prediction['home_prob']
        confidence = prediction['confidence']
        momentum = prediction['momentum']
        
        # Determine favorite
        if away_prob > home_prob:
            favorite = f"{away_team} (+{(away_prob - home_prob) * 100:.1f}%)"
        else:
            favorite = f"{home_team} (+{(home_prob - away_prob) * 100:.1f}%)"
        
        return f"""
🏒 LIVE IN-GAME PREDICTION
{'=' * 50}
📊 {away_team} @ {home_team}
🎯 LIVE SCORE: {away_team} {away_score} - {home_score} {home_team}
⏰ Period {current_period} - {time_remaining} remaining

🎯 LIVE PREDICTION:
   {away_team}: {away_prob * 100:.1f}%
   {home_team}: {home_prob * 100:.1f}%
   ⭐ Favorite: {favorite}

📈 LIVE MOMENTUM:
   Score Impact: {momentum['score_impact'] * 100:+.1f}%
   Shot Impact: {momentum['shot_impact'] * 100:+.1f}%
   PP Impact: {momentum['pp_impact'] * 100:+.1f}%
   Faceoff Impact: {momentum['faceoff_impact'] * 100:+.1f}%

📊 LIVE METRICS:
   Shots: {away_team} {prediction['live_metrics']['away_shots']} - {prediction['live_metrics']['home_shots']} {home_team}
   Hits: {away_team} {prediction['live_metrics']['away_hits']} - {prediction['live_metrics']['home_hits']} {home_team}
   PIM: {away_team} {prediction['live_metrics']['away_pim']} - {prediction['live_metrics']['home_pim']} {home_team}

📈 Confidence: {confidence * 100:.1f}%
🔄 Updated: {datetime.now(self.ct_tz).strftime('%H:%M:%S CT')}
"""
    
    def run_live_predictions(self, update_interval=30):
        """Run live in-game predictions with automatic updates"""
        print("🏒 LIVE IN-GAME NHL PREDICTIONS")
        print("=" * 60)
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
                        live_metrics = self.get_live_game_data(game_id)
                        
                        if live_metrics:
                            prediction = self.predict_live_game(live_metrics)
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
    predictor = LiveInGamePredictor()
    
    print("🏒 LIVE IN-GAME NHL PREDICTIONS")
    print("=" * 60)
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
                live_metrics = predictor.get_live_game_data(game_id)
                if live_metrics:
                    prediction = predictor.predict_live_game(live_metrics)
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
