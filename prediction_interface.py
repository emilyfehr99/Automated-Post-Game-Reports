"""
Pre-Game Prediction Interface
Uses the self-learning model for predictions before games are played
This is separate from the post-game win probability analysis
"""

import json
import requests
import os
from nhl_api_client import NHLAPIClient
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from correlation_model import CorrelationModel
from datetime import datetime, timedelta
import pytz

class PredictionInterface:
    def __init__(self):
        """Initialize the prediction interface"""
        self.api = NHLAPIClient()
        self.learning_model = ImprovedSelfLearningModelV2()
        self.corr_model = CorrelationModel()
    
    def check_and_add_missing_games(self):
        """Check for missing games from recent days and add them to the model"""
        print("🔍 Checking for missing games...")
        
        # Get the last 7 days
        central_tz = pytz.timezone('US/Central')
        central_now = datetime.now(central_tz)
        
        # Load existing predictions to see what we have
        try:
            with open('win_probability_predictions_v2.json', 'r') as f:
                data = json.load(f)
            existing_predictions = data.get('predictions', [])
            existing_game_ids = set(pred.get('game_id') for pred in existing_predictions)
        except:
            existing_game_ids = set()
        
        games_added = 0
        
        # Check each of the last 7 days
        for days_back in range(1, 8):
            check_date = (central_now - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # Get games from this date
            schedule = self.api.get_game_schedule(check_date)
            if not schedule or 'gameWeek' not in schedule:
                continue
            
            for day in schedule['gameWeek']:
                if day.get('date') == check_date and 'games' in day:
                    for game in day['games']:
                        game_id = str(game.get('id'))
                        away_team = game.get('awayTeam', {}).get('abbrev', 'UNK')
                        home_team = game.get('homeTeam', {}).get('abbrev', 'UNK')
                        game_state = game.get('gameState', 'UNKNOWN')
                        
                        # Check if we already have this game
                        if game_id in existing_game_ids:
                            continue
                        
                        # Only process completed games
                        if game_state in ['FINAL', 'OFF']:
                            try:
                                # Get comprehensive game data
                                game_data = self.api.get_comprehensive_game_data(game_id)
                                if not game_data:
                                    continue
                                
                                # Determine actual winner
                                away_goals = game_data['boxscore']['awayTeam'].get('score', 0)
                                home_goals = game_data['boxscore']['homeTeam'].get('score', 0)
                                
                                actual_winner = None
                                if away_goals > home_goals:
                                    actual_winner = "away"
                                elif home_goals > away_goals:
                                    actual_winner = "home"
                                
                                if actual_winner:
                                    # Use the actual model to make a prediction for this game
                                    try:
                                        model_prediction = self.learning_model.ensemble_predict(away_team, home_team)
                                        predicted_away_prob = model_prediction.get('away_prob', 0.5)
                                        predicted_home_prob = model_prediction.get('home_prob', 0.5)
                                    except Exception as e:
                                        print(f"    ⚠️  Could not get model prediction: {e}")
                                        # Fallback to shot-based prediction
                                        away_shots = game_data['boxscore']['awayTeam'].get('sog', 0)
                                        home_shots = game_data['boxscore']['homeTeam'].get('sog', 0)
                                        total_shots = away_shots + home_shots
                                        if total_shots > 0:
                                            predicted_away_prob = away_shots / total_shots
                                            predicted_home_prob = home_shots / total_shots
                                        else:
                                            predicted_away_prob = 0.5
                                            predicted_home_prob = 0.5
                                    
                                    # Create metrics used (simplified)
                                    metrics_used = {
                                        "away_xg": 0.0, "home_xg": 0.0,
                                        "away_hdc": 0, "home_hdc": 0,
                                        "away_shots": away_shots,
                                        "home_shots": home_shots,
                                        "away_gs": 0.0, "home_gs": 0.0,
                                        "away_corsi_pct": 50.0, "home_corsi_pct": 50.0,
                                        "away_power_play_pct": 0.0, "home_power_play_pct": 0.0,
                                        "away_faceoff_pct": 50.0, "home_faceoff_pct": 50.0,
                                        "away_hits": 0, "home_hits": 0,
                                        "away_blocked_shots": 0, "home_blocked_shots": 0,
                                        "away_giveaways": 0, "home_giveaways": 0,
                                        "away_takeaways": 0, "home_takeaways": 0,
                                        "away_penalty_minutes": 0, "home_penalty_minutes": 0
                                    }
                                    
                                    # Add to model
                                    self.learning_model.add_prediction(
                                        game_id=game_id,
                                        date=check_date,
                                        away_team=away_team,
                                        home_team=home_team,
                                        predicted_away_prob=predicted_away_prob,
                                        predicted_home_prob=predicted_home_prob,
                                        metrics_used=metrics_used,
                                        actual_winner=actual_winner,
                                        actual_away_score=away_goals,
                                        actual_home_score=home_goals
                                    )
                                    
                                    games_added += 1
                                    print(f"  ✅ Added missing game: {away_team} @ {home_team} ({actual_winner} won)")
                                    
                            except Exception as e:
                                print(f"  ❌ Error processing {away_team} @ {home_team}: {e}")
        
        if games_added > 0:
            print(f"🎉 Added {games_added} missing games to model")
        else:
            print("✅ No missing games found")
        
        return games_added
    
    def _compute_model_performance_fallback(self):
        """Compute performance from saved predictions if in-memory stats are empty."""
        try:
            with open('win_probability_predictions_v2.json', 'r') as f:
                data = json.load(f)
            predictions = data.get('predictions', [])
            total = 0
            correct = 0
            # Compute across all available finalized games
            for p in predictions:
                actual = p.get('actual_winner')
                # Derive predicted winner from probabilities
                away_prob = p.get('predicted_away_win_prob')
                home_prob = p.get('predicted_home_win_prob')
                predicted = None
                if isinstance(away_prob, (int, float)) and isinstance(home_prob, (int, float)):
                    predicted = 'away' if away_prob > home_prob else 'home'

                # Normalize actual winner to 'home'/'away' if it's a team abbrev
                if actual and actual not in ('home', 'away'):
                    away_team = p.get('away_team')
                    home_team = p.get('home_team')
                    if actual == away_team:
                        actual_side = 'away'
                    elif actual == home_team:
                        actual_side = 'home'
                    else:
                        actual_side = None
                else:
                    actual_side = actual

                if actual_side and predicted:
                    total += 1
                    if actual_side == predicted:
                        correct += 1
            if total > 0:
                acc = correct / total
                return {
                    'total_games': total,
                    'correct_predictions': correct,
                    'accuracy': acc,
                    'recent_accuracy': acc
                }
        except Exception:
            pass
        # If nothing found, return zeros (caller may decide what to display)
        return {
            'total_games': 0,
            'correct_predictions': 0,
            'accuracy': 0.0,
            'recent_accuracy': 0.0
        }
        
    def get_todays_predictions(self):
        """Get predictions for today's games using the self-learning model"""
        print('🏒 NHL GAME PREDICTIONS (Self-Learning Model) 🏒')
        print('=' * 60)
        central_tz = pytz.timezone('US/Central')
        now_ct = datetime.now(central_tz)
        print(f'📅 Date (CT): {now_ct.strftime("%Y-%m-%d")}')
        
        # Check for missing games first
        missing_games = self.check_and_add_missing_games()
        if missing_games > 0:
            print(f"📈 Model updated with {missing_games} missing games")
        
        # Get current model weights
        weights = self.learning_model.get_current_weights()
        print(f'🎯 Model Weights: xG={weights["xg_weight"]}, HDC={weights["hdc_weight"]}, Shots={weights["shots_weight"]}, GS={weights["game_score_weight"]}')
        print()
        
        # Define today's window in Central Time and convert to UTC bounds
        start_of_day_ct = now_ct.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day_ct = start_of_day_ct + timedelta(days=1)
        start_utc = start_of_day_ct.astimezone(pytz.utc)
        end_utc = end_of_day_ct.astimezone(pytz.utc)

        # Fetch schedule for the week (API returns a gameWeek)
        schedule_data = self.api.get_game_schedule(now_ct.strftime('%Y-%m-%d'))
        
        # Get ONLY today's games using the day bucket matching Central date
        games = []
        today_ct_str = now_ct.strftime('%Y-%m-%d')
        for day_data in schedule_data.get('gameWeek', []):
            if not isinstance(day_data, dict):
                continue
            if day_data.get('date') == today_ct_str and 'games' in day_data:
                games.extend(day_data['games'])
        
        # Helper to parse ISO8601 UTC timestamps
        def parse_utc(ts: str):
            try:
                # Ensure timezone-aware
                return datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(pytz.utc)
            except Exception:
                return None

        # Filter for games starting within today's Central day, using UTC bounds (extra safety)
        today_games = []
        for game in games:
            ts = game.get('startTimeUTC')
            dt_utc = parse_utc(ts) if isinstance(ts, str) else None
            if not dt_utc:
                continue
            if start_utc <= dt_utc < end_utc and game.get('gameState') in ['PRE', 'FUT']:
                today_games.append(game)
        
        print(f'🔍 Found {len(today_games)} games today')
        print()
        
        # Generate predictions using the self-learning model
        predictions = []
        for i, game in enumerate(today_games):
            away_team = game.get('awayTeam', {}).get('abbrev', 'UNK')
            home_team = game.get('homeTeam', {}).get('abbrev', 'UNK')
            game_time = game.get('startTimeUTC', 'UNK')
            # Convert to Central for display if possible
            try:
                dt_utc = parse_utc(game_time)
                game_time_ct = dt_utc.astimezone(central_tz).strftime('%Y-%m-%d %I:%M %p CT') if dt_utc else game_time
            except Exception:
                game_time_ct = game_time
            
            print(f'{i+1}. {away_team} @ {home_team}')
            print(f'   🕐 Time: {game_time_ct}')
            
            # Get prediction using self-learning model
            prediction = self.predict_game(away_team, home_team)
            
            print(f'   🎯 Prediction: {away_team} {prediction["away_prob"]*100:.1f}% | {home_team} {prediction["home_prob"]*100:.1f}%')
            
            # Determine favorite
            if prediction["away_prob"] > prediction["home_prob"]:
                favorite = away_team
                spread = prediction["away_prob"] - prediction["home_prob"]
            else:
                favorite = home_team
                spread = prediction["home_prob"] - prediction["away_prob"]
            
            print(f'   ⭐ Favorite: {favorite} (+{spread*100:.1f}%)')
            print(f'   📊 Confidence: {max(prediction["away_prob"], prediction["home_prob"])*100:.1f}%')
            print()
            
            predictions.append({
                'game_id': game.get('id'),
                'away_team': away_team,
                'home_team': home_team,
                'predicted_away_win_prob': prediction["away_prob"],  # Already decimal
                'predicted_home_win_prob': prediction["home_prob"],  # Already decimal
                'favorite': favorite,
                'spread': spread
            })

        # Save predictions to model for future learning
        for pred in predictions:
            try:
                # Include situational features at prediction time
                game_date = datetime.now().strftime('%Y-%m-%d')
                try:
                    away_rest = self.learning_model._calculate_rest_days_advantage(pred['away_team'], 'away', game_date)
                    home_rest = self.learning_model._calculate_rest_days_advantage(pred['home_team'], 'home', game_date)
                except Exception:
                    away_rest = 0.0
                    home_rest = 0.0
                try:
                    away_goalie_perf = self.learning_model._goalie_performance_for_game(pred['away_team'], 'away', game_date)
                    home_goalie_perf = self.learning_model._goalie_performance_for_game(pred['home_team'], 'home', game_date)
                except Exception:
                    away_goalie_perf = 0.0
                    home_goalie_perf = 0.0
                try:
                    away_sos = self.learning_model._calculate_sos(pred['away_team'], 'away')
                    home_sos = self.learning_model._calculate_sos(pred['home_team'], 'home')
                except Exception:
                    away_sos = 0.0
                    home_sos = 0.0

                metrics_used = {
                    "away_rest": away_rest,
                    "home_rest": home_rest,
                    "away_goalie_perf": away_goalie_perf,
                    "home_goalie_perf": home_goalie_perf,
                    "away_sos": away_sos,
                    "home_sos": home_sos,
                }
                self.learning_model.add_prediction(
                    game_id=pred.get('game_id', ''),
                    date=game_date,
                    away_team=pred['away_team'],
                    home_team=pred['home_team'],
                    predicted_away_prob=pred['predicted_away_win_prob'],
                    predicted_home_prob=pred['predicted_home_win_prob'],
                    metrics_used=metrics_used,  # Store situational context
                    actual_winner=None  # Will be updated when game completes
                )
            except Exception as e:
                print(f"⚠️  Error saving prediction: {e}")

        # Run daily learning update (only learn from completed games, not future predictions)
        try:
            self.learning_model.run_daily_update()
        except Exception as e:
            print(f"⚠️  Error updating learning model: {e}")

        return predictions
    
    def predict_game(self, away_team, home_team):
        """Predict a single game using correlation model (primary) with ensemble as fallback."""
        # Build situational metrics for correlation model pre-game
        today_str = datetime.now().strftime('%Y-%m-%d')
        try:
            away_rest = self.learning_model._calculate_rest_days_advantage(away_team, 'away', today_str)
            home_rest = self.learning_model._calculate_rest_days_advantage(home_team, 'home', today_str)
        except Exception:
            away_rest = home_rest = 0.0
        try:
            away_goalie_perf = self.learning_model._goalie_performance_for_game(away_team, 'away', today_str)
            home_goalie_perf = self.learning_model._goalie_performance_for_game(home_team, 'home', today_str)
        except Exception:
            away_goalie_perf = home_goalie_perf = 0.0
        try:
            away_sos = self.learning_model._calculate_sos(away_team, 'away')
            home_sos = self.learning_model._calculate_sos(home_team, 'home')
        except Exception:
            away_sos = home_sos = 0.5
        # Team venue performance proxies
        away_perf = self.learning_model.get_team_performance(away_team, 'away')
        home_perf = self.learning_model.get_team_performance(home_team, 'home')
        metrics = {
            'away_gs': away_perf.get('gs_avg', 0.0), 'home_gs': home_perf.get('gs_avg', 0.0),
            'away_power_play_pct': away_perf.get('power_play_avg', 0.0), 'home_power_play_pct': home_perf.get('power_play_avg', 0.0),
            'away_blocked_shots': away_perf.get('blocked_shots_avg', 0.0), 'home_blocked_shots': home_perf.get('blocked_shots_avg', 0.0),
            'away_corsi_pct': away_perf.get('corsi_avg', 50.0), 'home_corsi_pct': home_perf.get('corsi_avg', 50.0),
            'away_hits': away_perf.get('hits_avg', 0.0), 'home_hits': home_perf.get('hits_avg', 0.0),
            'away_rest': away_rest, 'home_rest': home_rest,
            'away_hdc': away_perf.get('hdc_avg', 0.0), 'home_hdc': home_perf.get('hdc_avg', 0.0),
            'away_shots': away_perf.get('shots_avg', 30.0), 'home_shots': home_perf.get('shots_avg', 30.0),
            'away_giveaways': away_perf.get('giveaways_avg', 0.0), 'home_giveaways': home_perf.get('giveaways_avg', 0.0),
            'away_sos': away_sos, 'home_sos': home_sos,
            'away_takeaways': away_perf.get('takeaways_avg', 0.0), 'home_takeaways': home_perf.get('takeaways_avg', 0.0),
            'away_xg': away_perf.get('xg_avg', 0.0), 'home_xg': home_perf.get('xg_avg', 0.0),
            'away_penalty_minutes': away_perf.get('penalty_minutes_avg', 0.0), 'home_penalty_minutes': home_perf.get('penalty_minutes_avg', 0.0),
            'away_faceoff_pct': away_perf.get('faceoff_avg', 50.0), 'home_faceoff_pct': home_perf.get('faceoff_avg', 50.0),
        }
        corr = self.corr_model.predict_from_metrics(metrics)
        ens = self.learning_model.ensemble_predict(away_team, home_team, game_date=today_str)
        # 70/30 blend: correlation model (70%) + ensemble (30%)
        if corr and all(k in corr for k in ('away_prob','home_prob')):
            away_blend = 0.7 * corr['away_prob'] + 0.3 * ens.get('away_prob', 0.5)
            home_blend = 1.0 - away_blend
            return {
                'away_prob': away_blend,
                'home_prob': home_blend,
                'prediction_confidence': max(away_blend, home_blend)
            }
        # Fallback to ensemble if correlation fails
        return {
            'away_prob': ens['away_prob'],
            'home_prob': ens['home_prob'],
            'prediction_confidence': ens['prediction_confidence']
        }
    
    def get_team_performance_data(self):
        """Get current team performance data (this would be updated regularly)"""
        # This is where you'd get the most recent team performance data
        # For now, using static data - in production this would be updated from recent games
        return {
            'TOR': {'xg_avg': 3.2, 'hdc_avg': 2, 'shots_avg': 32, 'gs_avg': 15.2},
            'SEA': {'xg_avg': 2.8, 'hdc_avg': 1.5, 'shots_avg': 28, 'gs_avg': 12.8},
            'NYR': {'xg_avg': 3.1, 'hdc_avg': 2.2, 'shots_avg': 30, 'gs_avg': 14.9},
            'MTL': {'xg_avg': 2.9, 'hdc_avg': 1.8, 'shots_avg': 29, 'gs_avg': 13.7},
            'MIN': {'xg_avg': 2.7, 'hdc_avg': 1.6, 'shots_avg': 27, 'gs_avg': 13.1},
            'PHI': {'xg_avg': 2.6, 'hdc_avg': 1.4, 'shots_avg': 26, 'gs_avg': 12.4},
            'TBL': {'xg_avg': 3.0, 'hdc_avg': 2.0, 'shots_avg': 31, 'gs_avg': 15.8},
            'CBJ': {'xg_avg': 2.4, 'hdc_avg': 1.2, 'shots_avg': 24, 'gs_avg': 11.2},
            'DAL': {'xg_avg': 3.3, 'hdc_avg': 2.3, 'shots_avg': 33, 'gs_avg': 16.1},
            'STL': {'xg_avg': 2.8, 'hdc_avg': 1.7, 'shots_avg': 28, 'gs_avg': 13.4},
            'NSH': {'xg_avg': 2.9, 'hdc_avg': 1.9, 'shots_avg': 29, 'gs_avg': 13.9},
            'WPG': {'xg_avg': 3.1, 'hdc_avg': 2.1, 'shots_avg': 31, 'gs_avg': 15.0},
            'BOS': {'xg_avg': 2.5, 'hdc_avg': 1.3, 'shots_avg': 25, 'gs_avg': 12.1},
            'COL': {'xg_avg': 3.4, 'hdc_avg': 2.4, 'shots_avg': 34, 'gs_avg': 16.5},
            'CAR': {'xg_avg': 3.2, 'hdc_avg': 2.2, 'shots_avg': 32, 'gs_avg': 15.3},
            'LAK': {'xg_avg': 2.7, 'hdc_avg': 1.6, 'shots_avg': 27, 'gs_avg': 13.0},
            'CGY': {'xg_avg': 2.8, 'hdc_avg': 1.7, 'shots_avg': 28, 'gs_avg': 13.5},
            'VGK': {'xg_avg': 3.0, 'hdc_avg': 2.0, 'shots_avg': 30, 'gs_avg': 14.7},
            'PIT': {'xg_avg': 2.9, 'hdc_avg': 1.8, 'shots_avg': 29, 'gs_avg': 13.8},
            'SJS': {'xg_avg': 2.2, 'hdc_avg': 1.0, 'shots_avg': 22, 'gs_avg': 10.5}
        }
    
    def send_discord_notification(self, predictions):
        """Send Discord notification with today's predictions"""
        # Discord webhook URL must come from environment/secret
        webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        
        if not webhook_url:
            print("❌ Discord webhook URL not configured")
            return False
        
        # Format predictions for Discord
        prediction_text = "🏒 **DAILY NHL PREDICTIONS** 🏒\n\n"
        
        for i, pred in enumerate(predictions, 1):
            away_team = pred['away_team']
            home_team = pred['home_team']
            away_prob = pred['predicted_away_win_prob'] * 100
            home_prob = pred['predicted_home_win_prob'] * 100
            favorite = pred['favorite']
            spread = pred['spread']
            
            prediction_text += f"**{i}. {away_team} @ {home_team}**\n"
            prediction_text += f"🎯 {away_team} {away_prob:.1f}% | {home_team} {home_prob:.1f}%\n"
            prediction_text += f"⭐ Favorite: {favorite} (+{spread:.1f}%)\n\n"
        
        # Get current model performance for recent accuracy
        perf = self.learning_model.get_model_performance()
        if not perf or perf.get('total_games', 0) == 0:
            perf = self._compute_model_performance_fallback()
        
        # Get actual model performance from the learning model
        actual_total_games = perf.get('total_games', 0)
        actual_accuracy = perf.get('accuracy', 0.0)
        recent_accuracy = perf.get('recent_accuracy', actual_accuracy)
        
        prediction_text += f"📊 **Model Performance:**\n"
        prediction_text += f"• Total Games: {actual_total_games}\n"
        prediction_text += f"• Accuracy: {actual_accuracy:.1%}\n"
        prediction_text += f"• Recent Accuracy: {recent_accuracy:.1%}\n\n"
        prediction_text += f"🤖 *Powered by Self-Learning AI Model*"
        
        # Discord webhook payload
        payload = {
            "content": prediction_text,
            "username": "NHL Predictions Bot",
            "embeds": [
                {
                    "title": "🏒 Daily NHL Predictions",
                    "description": f"Predictions for {len(predictions)} games today",
                    "color": 3447003,  # Blue color
                    "fields": [
                        {
                            "name": "📅 Date",
                            "value": datetime.now().strftime('%Y-%m-%d'),
                            "inline": True
                        },
                        {
                            "name": "🎮 Games",
                            "value": str(len(predictions)),
                            "inline": True
                        },
                        {
                            "name": "📊 Model Accuracy",
                            "value": f"{actual_accuracy:.1%}",
                            "inline": True
                        }
                    ],
                    "footer": {
                        "text": "Self-Learning AI Model • Updated Daily"
                    }
                }
            ]
        }
        
        try:
            print("📤 Sending Discord notification...")
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 204:
                print("✅ Discord notification sent successfully!")
                return True
            else:
                print(f"❌ Discord notification failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Discord notification: {e}")
            return False

    def show_model_performance(self):
        """Show current model performance"""
        perf = self.learning_model.get_model_performance()
        if not perf or perf.get('total_games', 0) == 0:
            perf = self._compute_model_performance_fallback()
        print(f"\n📊 MODEL PERFORMANCE:")
        print(f"  Total Games: {perf['total_games']}")
        print(f"  Accuracy: {perf['accuracy']:.3f}")
        print(f"  Recent Accuracy: {perf['recent_accuracy']:.3f}")
        
        # Show model analysis
        analysis = self.learning_model.analyze_model_performance()
        if analysis.get('team_accuracy'):
            print(f"\n📈 TOP TEAM ACCURACY:")
            sorted_teams = sorted(analysis['team_accuracy'].items(), key=lambda x: x[1], reverse=True)
            for team, acc in sorted_teams[:5]:
                print(f"  {team}: {acc:.3f}")


def main():
    """Main function to run predictions"""
    predictor = PredictionInterface()
    
    # Get today's predictions
    predictions = predictor.get_todays_predictions()
    
    # Show model performance
    predictor.show_model_performance()
    
    # Send Discord notification if there are predictions
    if predictions:
        print(f"\n📤 Sending Discord notification...")
        success = predictor.send_discord_notification(predictions)
        if success:
            print("✅ Discord notification sent successfully!")
        else:
            print("❌ Discord notification failed")
    else:
        print("\nℹ️  No games today - skipping Discord notification")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  Total games predicted: {len(predictions)}")
    print(f"  Model uses self-learning weights")
    print(f"  Separate from post-game win probability analysis")


if __name__ == "__main__":
    main()
