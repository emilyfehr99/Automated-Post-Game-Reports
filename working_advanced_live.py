#!/usr/bin/env python3
"""
Working Advanced Live In-Game NHL Predictions
Uses available advanced metrics from the NHL API
"""

import json
import requests
import time
from datetime import datetime, timedelta
import pytz
from pathlib import Path
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from nhl_api_client import NHLAPIClient

class WorkingAdvancedLivePredictor:
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
        """Get comprehensive live game data using available metrics"""
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
            
            # Get player stats for advanced metrics
            player_stats = boxscore.get('playerByGameStats', [])
            
            # Calculate advanced metrics from available data
            advanced_metrics = self.calculate_available_advanced_metrics(
                player_stats, away_team.get('abbrev', ''), home_team.get('abbrev', '')
            )
            
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
    
    def calculate_available_advanced_metrics(self, player_stats, away_team, home_team):
        """Calculate advanced metrics from available player stats"""
        try:
            # Initialize metrics
            away_metrics = {
                'xg': 0.0,
                'hdc': 0,
                'gs': 0.0,
                'corsi': 0,
                'fenwick': 0,
                'scf': 0,
                'hdcf': 0,
                'rush_chances': 0,
                'sustained_pressure': 0,
                'zone_time': 0,
                'hits': 0,
                'blocks': 0,
                'takeaways': 0,
                'giveaways': 0,
                'faceoff_wins': 0,
                'faceoff_losses': 0
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
                'zone_time': 0,
                'hits': 0,
                'blocks': 0,
                'takeaways': 0,
                'giveaways': 0,
                'faceoff_wins': 0,
                'faceoff_losses': 0
            }
            
            # Process player stats
            for player in player_stats:
                if 'teamAbbrev' not in player:
                    continue
                    
                team_abbrev = player['teamAbbrev']
                is_away = team_abbrev == away_team
                is_home = team_abbrev == home_team
                
                if not (is_away or is_home):
                    continue
                
                metrics = away_metrics if is_away else home_metrics
                
                # Extract available stats
                stats = player.get('stats', {})
                
                # Shots and goals
                goals = stats.get('goals', 0)
                shots = stats.get('shots', 0)
                missed_shots = stats.get('missedShots', 0)
                blocked_shots = stats.get('blockedShots', 0)
                
                # Calculate Corsi and Fenwick
                corsi = shots + missed_shots + blocked_shots
                fenwick = shots + missed_shots
                
                metrics['corsi'] += corsi
                metrics['fenwick'] += fenwick
                
                # Calculate Game Score
                gs = goals * 1.0  # Goals
                gs += shots * 0.5  # Shots on goal
                gs += missed_shots * 0.3  # Missed shots
                gs += blocked_shots * 0.2  # Blocked shots
                
                # Other stats
                hits = stats.get('hits', 0)
                blocks = stats.get('blockedShots', 0)
                takeaways = stats.get('takeaways', 0)
                giveaways = stats.get('giveaways', 0)
                faceoff_wins = stats.get('faceoffWins', 0)
                faceoff_losses = stats.get('faceoffLosses', 0)
                
                metrics['gs'] += gs
                metrics['hits'] += hits
                metrics['blocks'] += blocks
                metrics['takeaways'] += takeaways
                metrics['giveaways'] += giveaways
                metrics['faceoff_wins'] += faceoff_wins
                metrics['faceoff_losses'] += faceoff_losses
                
                # Estimate xG based on shots (simplified)
                estimated_xg = shots * 0.15  # Rough estimate
                metrics['xg'] += estimated_xg
                
                # Estimate HDC based on goals and shots
                if goals > 0:
                    metrics['hdc'] += goals
                    metrics['hdcf'] += goals
                
                # Estimate scoring chances
                if shots > 0:
                    metrics['scf'] += shots
            
            return {
                'away': away_metrics,
                'home': home_metrics
            }
            
        except Exception as e:
            print(f"❌ Error calculating available advanced metrics: {e}")
            return self.get_default_advanced_metrics()
    
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
                'zone_time': 0,
                'hits': 0,
                'blocks': 0,
                'takeaways': 0,
                'giveaways': 0,
                'faceoff_wins': 0,
                'faceoff_losses': 0
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
                'zone_time': 0,
                'hits': 0,
                'blocks': 0,
                'takeaways': 0,
                'giveaways': 0,
                'faceoff_wins': 0,
                'faceoff_losses': 0
            }
        }
    
    def calculate_advanced_momentum(self, live_metrics):
        """Calculate momentum using available advanced metrics"""
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
            
            # xG differential impact
            xg_diff = (away_adv['xg'] - home_adv['xg']) * 0.3
            
            # High danger chances impact
            hdc_diff = (away_adv['hdc'] - home_adv['hdc']) * 0.05
            
            # Game Score impact
            gs_diff = (away_adv['gs'] - home_adv['gs']) * 0.1
            
            # Corsi impact
            corsi_diff = (away_adv['corsi'] - home_adv['corsi']) * 0.01
            
            # Scoring chances impact
            scf_diff = (away_adv['scf'] - home_adv['scf']) * 0.03
            
            # Faceoff dominance
            away_faceoff_pct = away_adv['faceoff_wins'] / max(away_adv['faceoff_wins'] + away_adv['faceoff_losses'], 1)
            home_faceoff_pct = home_adv['faceoff_wins'] / max(home_adv['faceoff_wins'] + home_adv['faceoff_losses'], 1)
            faceoff_diff = (away_faceoff_pct - home_faceoff_pct) * 0.02
            
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
            total_momentum = score_impact + xg_diff + hdc_diff + gs_diff + corsi_diff + scf_diff + faceoff_diff
            
            return {
                'score_impact': score_impact,
                'xg_impact': xg_diff,
                'hdc_impact': hdc_diff,
                'gs_impact': gs_diff,
                'corsi_impact': corsi_diff,
                'scf_impact': scf_diff,
                'faceoff_impact': faceoff_diff,
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
                    'home_corsi': home_adv['corsi'],
                    'away_faceoff_pct': away_faceoff_pct,
                    'home_faceoff_pct': home_faceoff_pct
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
                'faceoff_impact': 0,
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
   Faceoff Impact: {momentum['faceoff_impact'] * 100:+.1f}%

📊 ADVANCED METRICS:
   xG: {away_team} {advanced.get('away_xg', 0):.2f} - {advanced.get('home_xg', 0):.2f} {home_team}
   HDC: {away_team} {advanced.get('away_hdc', 0)} - {advanced.get('home_hdc', 0)} {home_team}
   GS: {away_team} {advanced.get('away_gs', 0):.1f} - {advanced.get('home_gs', 0):.1f} {home_team}
   Corsi: {away_team} {advanced.get('away_corsi', 0)} - {advanced.get('home_corsi', 0)} {home_team}
   Faceoff%: {away_team} {advanced.get('away_faceoff_pct', 0)*100:.1f}% - {advanced.get('home_faceoff_pct', 0)*100:.1f}% {home_team}

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
    predictor = WorkingAdvancedLivePredictor()
    
    print("🏒 ADVANCED LIVE IN-GAME NHL PREDICTIONS")
    print("=" * 70)
    print("Starting advanced live predictions with GS, xG, HDC...")
    print()
    
    # Run live predictions with 30-second updates
    predictor.run_live_predictions(30)

if __name__ == "__main__":
    main()
