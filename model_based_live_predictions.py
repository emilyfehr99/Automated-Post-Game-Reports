#!/usr/bin/env python3
"""
Model-Based Live In-Game NHL Predictions
Uses the trained model's advanced metrics (xG, HDC, GS) for live predictions
"""

import json
import requests
import time
from datetime import datetime, timedelta
import pytz
from pathlib import Path
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from nhl_api_client import NHLAPIClient

class ModelBasedLivePredictor:
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
        """Get live game data with basic stats"""
        try:
            game_data = self.api.get_comprehensive_game_data(game_id)
            if not game_data:
                return None
                
            # Extract live game state
            boxscore = game_data.get('game_center', {}).get('boxscore', {})
            
            # Get team data
            away_team = boxscore.get('awayTeam', {})
            home_team = boxscore.get('homeTeam', {})
            
            # Basic stats
            away_score = away_team.get('score', 0)
            home_score = home_team.get('score', 0)
            away_shots = away_team.get('sog', 0)
            home_shots = home_team.get('sog', 0)
            
            # Period and time info
            period_info = boxscore.get('periodDescriptor', {})
            current_period = period_info.get('number', 1)
            clock = boxscore.get('clock', {})
            time_remaining = clock.get('timeRemaining', '20:00')
            
            return {
                'away_team': away_team.get('abbrev', ''),
                'home_team': home_team.get('abbrev', ''),
                'away_score': away_score,
                'home_score': home_score,
                'current_period': current_period,
                'time_remaining': time_remaining,
                'away_shots': away_shots,
                'home_shots': home_shots,
                'game_state': boxscore.get('gameState', ''),
                'game_id': game_id
            }
        except Exception as e:
            print(f"❌ Error getting live game data for {game_id}: {e}")
            return None
    
    def get_model_advanced_metrics(self, away_team, home_team):
        """Get advanced metrics from the trained model"""
        try:
            # Get team performance data from model
            away_perf = self.model.get_team_performance(away_team, 'away')
            home_perf = self.model.get_team_performance(home_team, 'home')
            
            return {
                'away': {
                    'xg': away_perf.get('xg_avg', 0.0),
                    'hdc': away_perf.get('hdc_avg', 0.0),
                    'gs': away_perf.get('gs_avg', 0.0),
                    'corsi': away_perf.get('corsi_avg', 50.0),
                    'power_play': away_perf.get('power_play_avg', 0.0),
                    'faceoff': away_perf.get('faceoff_avg', 50.0),
                    'games_played': away_perf.get('games_played', 0),
                    'confidence': away_perf.get('confidence', 0.5)
                },
                'home': {
                    'xg': home_perf.get('xg_avg', 0.0),
                    'hdc': home_perf.get('hdc_avg', 0.0),
                    'gs': home_perf.get('gs_avg', 0.0),
                    'corsi': home_perf.get('corsi_avg', 50.0),
                    'power_play': home_perf.get('power_play_avg', 0.0),
                    'faceoff': home_perf.get('faceoff_avg', 50.0),
                    'games_played': home_perf.get('games_played', 0),
                    'confidence': home_perf.get('confidence', 0.5)
                }
            }
        except Exception as e:
            print(f"❌ Error getting model advanced metrics: {e}")
            return {
                'away': {'xg': 0.0, 'hdc': 0.0, 'gs': 0.0, 'corsi': 50.0, 'power_play': 0.0, 'faceoff': 50.0, 'games_played': 0, 'confidence': 0.5},
                'home': {'xg': 0.0, 'hdc': 0.0, 'gs': 0.0, 'corsi': 50.0, 'power_play': 0.0, 'faceoff': 50.0, 'games_played': 0, 'confidence': 0.5}
            }
    
    def calculate_live_momentum(self, live_metrics, model_metrics):
        """Calculate momentum using live game state and model metrics"""
        try:
            away_score = live_metrics['away_score']
            home_score = live_metrics['home_score']
            current_period = live_metrics['current_period']
            time_remaining = live_metrics['time_remaining']
            away_shots = live_metrics['away_shots']
            home_shots = live_metrics['home_shots']
            
            # Score differential impact (strongest factor)
            score_diff = away_score - home_score
            period_multiplier = 0.1 + (current_period - 1) * 0.05
            score_impact = score_diff * period_multiplier
            
            # Shot differential impact
            shot_diff = (away_shots - home_shots) * 0.02
            
            # Model-based advanced metrics impact
            away_adv = model_metrics['away']
            home_adv = model_metrics['home']
            
            # xG differential (from model)
            xg_diff = (away_adv['xg'] - home_adv['xg']) * 0.1
            
            # HDC differential (from model)
            hdc_diff = (away_adv['hdc'] - home_adv['hdc']) * 0.05
            
            # Game Score differential (from model)
            gs_diff = (away_adv['gs'] - home_adv['gs']) * 0.05
            
            # Corsi differential (from model)
            corsi_diff = (away_adv['corsi'] - home_adv['corsi']) * 0.01
            
            # Time pressure
            try:
                time_parts = time_remaining.split(':')
                minutes = int(time_parts[0])
                seconds = int(time_parts[1])
                total_seconds = minutes * 60 + seconds
                time_pressure = max(0, (1200 - total_seconds) / 1200)
            except:
                time_pressure = 0.5
            
            # Calculate total momentum
            total_momentum = score_impact + shot_diff + xg_diff + hdc_diff + gs_diff + corsi_diff
            
            return {
                'score_impact': score_impact,
                'shot_impact': shot_diff,
                'xg_impact': xg_diff,
                'hdc_impact': hdc_diff,
                'gs_impact': gs_diff,
                'corsi_impact': corsi_diff,
                'time_pressure': time_pressure,
                'total_momentum': total_momentum,
                'model_metrics': {
                    'away_xg': away_adv['xg'],
                    'home_xg': home_adv['xg'],
                    'away_hdc': away_adv['hdc'],
                    'home_hdc': home_adv['hdc'],
                    'away_gs': away_adv['gs'],
                    'home_gs': home_adv['gs'],
                    'away_corsi': away_adv['corsi'],
                    'home_corsi': home_adv['corsi'],
                    'away_confidence': away_adv['confidence'],
                    'home_confidence': home_adv['confidence']
                }
            }
        except Exception as e:
            print(f"❌ Error calculating live momentum: {e}")
            return {
                'score_impact': 0,
                'shot_impact': 0,
                'xg_impact': 0,
                'hdc_impact': 0,
                'gs_impact': 0,
                'corsi_impact': 0,
                'time_pressure': 0.5,
                'total_momentum': 0,
                'model_metrics': {}
            }
    
    def predict_live_game(self, live_metrics):
        """Make live in-game prediction using model advanced metrics"""
        try:
            away_team = live_metrics['away_team']
            home_team = live_metrics['home_team']
            
            # Get advanced metrics from trained model
            model_metrics = self.get_model_advanced_metrics(away_team, home_team)
            
            # Get base prediction from model
            base_prediction = self.model.ensemble_predict(away_team, home_team)
            away_prob = base_prediction['away_prob']
            home_prob = base_prediction['home_prob']
            
            # Calculate live momentum factors
            momentum = self.calculate_live_momentum(live_metrics, model_metrics)
            
            # Apply live adjustments
            away_prob += momentum['total_momentum']
            home_prob -= momentum['total_momentum']
            
            # Apply time pressure
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
            
            # Calculate confidence based on game state and model confidence
            base_confidence = 0.5 + (live_metrics['current_period'] - 1) * 0.1
            model_confidence = (model_metrics['away']['confidence'] + model_metrics['home']['confidence']) / 2
            confidence = min(0.95, (base_confidence + model_confidence) / 2)
            
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
        model_metrics = momentum.get('model_metrics', {})
        
        # Determine favorite
        if away_prob > home_prob:
            favorite = f"{away_team} (+{(away_prob - home_prob) * 100:.1f}%)"
        else:
            favorite = f"{home_team} (+{(home_prob - away_prob) * 100:.1f}%)"
        
        return f"""
🏒 MODEL-BASED LIVE IN-GAME PREDICTION
{'=' * 60}
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
   xG Impact: {momentum['xg_impact'] * 100:+.1f}%
   HDC Impact: {momentum['hdc_impact'] * 100:+.1f}%
   GS Impact: {momentum['gs_impact'] * 100:+.1f}%
   Corsi Impact: {momentum['corsi_impact'] * 100:+.1f}%

📊 MODEL ADVANCED METRICS:
   xG: {away_team} {model_metrics.get('away_xg', 0):.2f} - {model_metrics.get('home_xg', 0):.2f} {home_team}
   HDC: {away_team} {model_metrics.get('away_hdc', 0):.1f} - {model_metrics.get('home_hdc', 0):.1f} {home_team}
   GS: {away_team} {model_metrics.get('away_gs', 0):.1f} - {model_metrics.get('home_gs', 0):.1f} {home_team}
   Corsi%: {away_team} {model_metrics.get('away_corsi', 0):.1f}% - {model_metrics.get('home_corsi', 0):.1f}% {home_team}

📈 Confidence: {confidence * 100:.1f}%
🔄 Updated: {datetime.now(self.ct_tz).strftime('%H:%M:%S CT')}
"""
    
    def run_live_predictions(self, update_interval=30):
        """Run model-based live in-game predictions with automatic updates"""
        print("🏒 MODEL-BASED LIVE IN-GAME NHL PREDICTIONS")
        print("=" * 70)
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
    predictor = ModelBasedLivePredictor()
    
    print("🏒 MODEL-BASED LIVE IN-GAME NHL PREDICTIONS")
    print("=" * 70)
    print("Using trained model's advanced metrics (xG, HDC, GS)...")
    print()
    
    # Run live predictions with 30-second updates
    predictor.run_live_predictions(30)

if __name__ == "__main__":
    main()
