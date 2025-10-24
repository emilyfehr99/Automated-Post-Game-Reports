#!/usr/bin/env python3
"""
Advanced Live In-Game NHL Predictions
Uses advanced metrics like GS, xG, HDC, and other sophisticated stats
"""

import json
import requests
import time
from datetime import datetime, timedelta
import pytz
from pathlib import Path
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from nhl_api_client import NHLAPIClient

class AdvancedLivePredictor:
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
    
    def get_advanced_live_metrics(self, game_id):
        """Get comprehensive live game data including advanced metrics"""
        try:
            game_data = self.api.get_comprehensive_game_data(game_id)
            if not game_data:
                return None
                
            # Extract live game state
            boxscore = game_data.get('game_center', {}).get('boxscore', {})
            play_by_play = game_data.get('game_center', {}).get('play_by_play', {})
            
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
            
            # Calculate advanced metrics from play-by-play data
            advanced_metrics = self.calculate_advanced_metrics(play_by_play, away_team.get('abbrev', ''), home_team.get('abbrev', ''))
            
            live_metrics = {
                'away_team': away_team.get('abbrev', ''),
                'home_team': home_team.get('abbrev', ''),
                'away_score': away_score,
                'home_score': home_score,
                'current_period': current_period,
                'time_remaining': time_remaining,
                'away_shots': away_shots,
                'home_shots': home_shots,
                'game_state': boxscore.get('gameState', ''),
                'game_id': game_id,
                'advanced_metrics': advanced_metrics
            }
            
            return live_metrics
        except Exception as e:
            print(f"❌ Error getting advanced live metrics for {game_id}: {e}")
            return None
    
    def calculate_advanced_metrics(self, play_by_play, away_team, home_team):
        """Calculate advanced metrics from play-by-play data"""
        try:
            if not play_by_play or 'plays' not in play_by_play:
                return self.get_default_advanced_metrics()
            
            plays = play_by_play.get('plays', [])
            
            # Initialize metrics
            away_metrics = {
                'xg': 0.0,
                'hdc': 0,
                'gs': 0.0,
                'corsi': 0,
                'fenwick': 0,
                'scf': 0,  # Scoring Chances For
                'hdcf': 0,  # High Danger Chances For
                'rush_chances': 0,
                'sustained_pressure': 0,
                'zone_time': 0
            }
            
            home_metrics = {
                'xg': 0.0,
                'hdc': 0,
                'gs': 0.0,
                'corsi': 0,
                'fenwick': 0,
                'scf': 0,
                'hdcf': 0,
                'rush_chances': 0,
                'sustained_pressure': 0,
                'zone_time': 0
            }
            
            # Process each play
            for play in plays:
                if 'details' not in play:
                    continue
                    
                details = play['details']
                event_type = details.get('eventTypeId', '')
                
                # Determine team
                team_abbrev = details.get('eventOwnerTeamId', '')
                is_away = team_abbrev == away_team
                is_home = team_abbrev == home_team
                
                if not (is_away or is_home):
                    continue
                
                metrics = away_metrics if is_away else home_metrics
                
                # Calculate xG for shots
                if event_type == 'SHOT':
                    xg = self.calculate_shot_xg(details)
                    metrics['xg'] += xg
                    metrics['corsi'] += 1
                    metrics['fenwick'] += 1
                    
                    # High danger chances
                    if self.is_high_danger_chance(details):
                        metrics['hdc'] += 1
                        metrics['hdcf'] += 1
                    
                    # Scoring chances
                    if self.is_scoring_chance(details):
                        metrics['scf'] += 1
                
                # Corsi events
                elif event_type in ['MISSED_SHOT', 'BLOCKED_SHOT']:
                    metrics['corsi'] += 1
                    if event_type == 'MISSED_SHOT':
                        metrics['fenwick'] += 1
                
                # Rush chances
                elif event_type == 'RUSH':
                    metrics['rush_chances'] += 1
                
                # Calculate Game Score components
                if event_type == 'GOAL':
                    metrics['gs'] += 1.0  # Goal
                elif event_type == 'SHOT':
                    metrics['gs'] += 0.5  # Shot on goal
                elif event_type == 'HIT':
                    metrics['gs'] += 0.1  # Hit
                elif event_type == 'BLOCK':
                    metrics['gs'] += 0.2  # Blocked shot
                elif event_type == 'TAKEAWAY':
                    metrics['gs'] += 0.3  # Takeaway
                elif event_type == 'GIVEAWAY':
                    metrics['gs'] -= 0.3  # Giveaway
                elif event_type == 'PENALTY':
                    metrics['gs'] -= 0.2  # Penalty
            
            return {
                'away': away_metrics,
                'home': home_metrics
            }
            
        except Exception as e:
            print(f"❌ Error calculating advanced metrics: {e}")
            return self.get_default_advanced_metrics()
    
    def calculate_shot_xg(self, shot_details):
        """Calculate expected goals for a shot"""
        try:
            # Get shot coordinates
            coordinates = shot_details.get('coordinates', {})
            x = coordinates.get('x', 0)
            y = coordinates.get('y', 0)
            
            # Calculate distance from goal
            distance = ((x - 89) ** 2 + y ** 2) ** 0.5
            
            # Calculate angle
            angle = abs(y) / max(distance, 1)
            
            # Basic xG calculation (simplified)
            if distance < 20:
                xg = 0.3
            elif distance < 40:
                xg = 0.15
            elif distance < 60:
                xg = 0.05
            else:
                xg = 0.01
            
            # Adjust for angle
            if angle > 0.5:  # Wide angle
                xg *= 0.5
            
            return min(xg, 0.95)  # Cap at 95%
        except:
            return 0.1  # Default xG
    
    def is_high_danger_chance(self, shot_details):
        """Determine if shot is high danger"""
        try:
            coordinates = shot_details.get('coordinates', {})
            x = coordinates.get('x', 0)
            y = coordinates.get('y', 0)
            
            # High danger area: close to goal and in front
            return x > 70 and abs(y) < 20
        except:
            return False
    
    def is_scoring_chance(self, shot_details):
        """Determine if shot is a scoring chance"""
        try:
            coordinates = shot_details.get('coordinates', {})
            x = coordinates.get('x', 0)
            y = coordinates.get('y', 0)
            
            # Scoring chance area: in offensive zone
            return x > 60 and abs(y) < 30
        except:
            return False
    
    def get_default_advanced_metrics(self):
        """Return default advanced metrics when data is unavailable"""
        return {
            'away': {
                'xg': 0.0,
                'hdc': 0,
                'gs': 0.0,
                'corsi': 0,
                'fenwick': 0,
                'scf': 0,
                'hdcf': 0,
                'rush_chances': 0,
                'sustained_pressure': 0,
                'zone_time': 0
            },
            'home': {
                'xg': 0.0,
                'hdc': 0,
                'gs': 0.0,
                'corsi': 0,
                'fenwick': 0,
                'scf': 0,
                'hdcf': 0,
                'rush_chances': 0,
                'sustained_pressure': 0,
                'zone_time': 0
            }
        }
    
    def calculate_advanced_momentum(self, live_metrics):
        """Calculate momentum using advanced metrics"""
        try:
            away_score = live_metrics['away_score']
            home_score = live_metrics['home_score']
            current_period = live_metrics['current_period']
            time_remaining = live_metrics['time_remaining']
            
            advanced = live_metrics['advanced_metrics']
            away_adv = advanced['away']
            home_adv = advanced['home']
            
            # Score differential impact
            score_diff = away_score - home_score
            period_multiplier = 0.1 + (current_period - 1) * 0.05
            score_impact = score_diff * period_multiplier
            
            # xG differential impact (most important)
            xg_diff = (away_adv['xg'] - home_adv['xg']) * 0.3  # 30% per xG difference
            
            # High danger chances impact
            hdc_diff = (away_adv['hdc'] - home_adv['hdc']) * 0.05  # 5% per HDC difference
            
            # Game Score impact
            gs_diff = (away_adv['gs'] - home_adv['gs']) * 0.1  # 10% per GS difference
            
            # Corsi impact
            corsi_diff = (away_adv['corsi'] - home_adv['corsi']) * 0.01  # 1% per Corsi difference
            
            # Scoring chances impact
            scf_diff = (away_adv['scf'] - home_adv['scf']) * 0.03  # 3% per SCF difference
            
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
            total_momentum = score_impact + xg_diff + hdc_diff + gs_diff + corsi_diff + scf_diff
            
            return {
                'score_impact': score_impact,
                'xg_impact': xg_diff,
                'hdc_impact': hdc_diff,
                'gs_impact': gs_diff,
                'corsi_impact': corsi_diff,
                'scf_impact': scf_diff,
                'time_pressure': time_pressure,
                'total_momentum': total_momentum,
                'advanced_metrics': {
                    'away_xg': away_adv['xg'],
                    'home_xg': home_adv['xg'],
                    'away_hdc': away_adv['hdc'],
                    'home_hdc': home_adv['hdc'],
                    'away_gs': away_adv['gs'],
                    'home_gs': home_adv['gs'],
                    'away_corsi': away_adv['corsi'],
                    'home_corsi': home_adv['corsi']
                }
            }
        except Exception as e:
            print(f"❌ Error calculating advanced momentum: {e}")
            return {
                'score_impact': 0,
                'xg_impact': 0,
                'hdc_impact': 0,
                'gs_impact': 0,
                'corsi_impact': 0,
                'scf_impact': 0,
                'time_pressure': 0.5,
                'total_momentum': 0,
                'advanced_metrics': {}
            }
    
    def predict_live_game(self, live_metrics):
        """Make live in-game prediction using advanced metrics"""
        try:
            away_team = live_metrics['away_team']
            home_team = live_metrics['home_team']
            
            # Get base prediction from historical data
            base_prediction = self.model.ensemble_predict(away_team, home_team)
            away_prob = base_prediction['away_prob']
            home_prob = base_prediction['home_prob']
            
            # Calculate advanced momentum factors
            momentum = self.calculate_advanced_momentum(live_metrics)
            
            # Apply advanced adjustments
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
        advanced = momentum.get('advanced_metrics', {})
        
        # Determine favorite
        if away_prob > home_prob:
            favorite = f"{away_team} (+{(away_prob - home_prob) * 100:.1f}%)"
        else:
            favorite = f"{home_team} (+{(home_prob - away_prob) * 100:.1f}%)"
        
        return f"""
🏒 ADVANCED LIVE IN-GAME PREDICTION
{'=' * 60}
📊 {away_team} @ {home_team}
🎯 LIVE SCORE: {away_team} {away_score} - {home_score} {home_team}
⏰ Period {current_period} - {time_remaining} remaining

🎯 LIVE PREDICTION:
   {away_team}: {away_prob * 100:.1f}%
   {home_team}: {home_prob * 100:.1f}%
   ⭐ Favorite: {favorite}

📈 ADVANCED MOMENTUM:
   Score Impact: {momentum['score_impact'] * 100:+.1f}%
   xG Impact: {momentum['xg_impact'] * 100:+.1f}%
   HDC Impact: {momentum['hdc_impact'] * 100:+.1f}%
   GS Impact: {momentum['gs_impact'] * 100:+.1f}%
   Corsi Impact: {momentum['corsi_impact'] * 100:+.1f}%
   SCF Impact: {momentum['scf_impact'] * 100:+.1f}%

📊 ADVANCED METRICS:
   xG: {away_team} {advanced.get('away_xg', 0):.2f} - {advanced.get('home_xg', 0):.2f} {home_team}
   HDC: {away_team} {advanced.get('away_hdc', 0)} - {advanced.get('home_hdc', 0)} {home_team}
   GS: {away_team} {advanced.get('away_gs', 0):.1f} - {advanced.get('home_gs', 0):.1f} {home_team}
   Corsi: {away_team} {advanced.get('away_corsi', 0)} - {advanced.get('home_corsi', 0)} {home_team}

📈 Confidence: {confidence * 100:.1f}%
🔄 Updated: {datetime.now(self.ct_tz).strftime('%H:%M:%S CT')}
"""
    
    def run_live_predictions(self, update_interval=30):
        """Run advanced live in-game predictions with automatic updates"""
        print("🏒 ADVANCED LIVE IN-GAME NHL PREDICTIONS")
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
                        live_metrics = self.get_advanced_live_metrics(game_id)
                        
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
    predictor = AdvancedLivePredictor()
    
    print("🏒 ADVANCED LIVE IN-GAME NHL PREDICTIONS")
    print("=" * 70)
    print("Starting advanced live predictions with GS, xG, HDC...")
    print()
    
    # Run live predictions with 30-second updates
    predictor.run_live_predictions(30)

if __name__ == "__main__":
    main()
