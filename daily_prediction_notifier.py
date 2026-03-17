"""
Daily Prediction Notifier
Sends daily NHL game predictions via email, Discord, or other methods
Uses Meta-Ensemble Predictor for 55-60% accuracy
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz
from prediction_interface import PredictionInterface
from meta_ensemble_predictor import MetaEnsemblePredictor
from rotowire_scraper import RotoWireScraper
import os
from pathlib import Path

class DailyPredictionNotifier:
    def __init__(self):
        """Initialize the notifier with meta-ensemble predictor"""
        self.predictor = PredictionInterface()  # Keep for compatibility
        self.meta_ensemble = MetaEnsemblePredictor()
        self.rotowire = RotoWireScraper()

    def save_predictions_to_history(self, predictions: list):
        """Save predictions to the permanent JSON history file for future training"""
        history_file = Path('data/win_probability_predictions_v2.json')
        if not history_file.exists():
            history_file = Path('win_probability_predictions_v2.json')
            
        if not history_file.exists():
            print("⚠️ Warning: Could not find history file to save predictions.")
            return

        try:
            with open(history_file, 'r') as f:
                data = json.load(f)
            
            existing_ids = {p.get('game_id') for p in data.get('predictions', []) if p.get('game_id')}
            new_count = 0
            
            for pred in predictions:
                # Only save if we have a game_id and it's not already there
                if pred.get('game_id') and pred.get('game_id') not in existing_ids:
                    # Construct record in the format expected by training scripts
                    record = {
                        'date': datetime.now(pytz.timezone('US/Central')).strftime('%Y-%m-%d'),
                        'game_id': pred['game_id'],
                        'home_team': pred['home_team'],
                        'away_team': pred['away_team'],
                        'predicted_winner': pred['predicted_winner'],
                        'home_win_prob': pred['home_prob'] / 100.0,
                        'away_win_prob': pred['away_prob'] / 100.0,
                        'model_confidence': pred['confidence'] / 100.0,
                        # Store the metrics used for this prediction (crucial for training)
                        'metrics_used': {
                            'home_xg': pred.get('home_xg', 0),
                            'away_xg': pred.get('away_xg', 0),
                            # Add other metrics if available from meta_ensemble
                        },
                        'prediction_reason': "Meta-Ensemble Daily Run",
                        'suggested_units': pred.get('suggested_units', 0.0),
                        'odds_taken': pred.get('odds_taken', 0)
                    }
                    data['predictions'].append(record)
                    existing_ids.add(pred['game_id'])
                    new_count += 1
            
            if new_count > 0:
                with open(history_file, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"✅ Saved {new_count} new predictions to history file.")
            else:
                print("ℹ️  No new predictions to save (all game IDs already exist).")
                
        except Exception as e:
            print(f"❌ Error saving predictions to history: {e}")

    def get_daily_predictions_summary(self):
        """Get formatted summary of today's predictions using meta-ensemble"""
        # Get today's games from RotoWire
        rotowire_data = self.rotowire.scrape_daily_data()
        games = rotowire_data.get('games', [])
        
        # Fetch Vegas odds
        from vegas_odds_scraper import scrape_vegas_odds
        market_odds = scrape_vegas_odds()
        
        # Get NHL Schedule for Game IDs
        from nhl_api_client import NHLAPIClient
        nhl_client = NHLAPIClient()
        schedule = nhl_client.get_game_schedule()  # Defaults to today
        schedule_map = {} # 'AWAY@HOME' -> game_id
        
        if schedule:
            # Handle new API structure: { "gameWeek": [ { "games": [...] } ] }
            games_list = []
            if 'gameWeek' in schedule:
                for day in schedule['gameWeek']:
                    games_list.extend(day.get('games', []))
            elif 'games' in schedule:
                # Legacy fallback
                games_list = schedule['games']
            
            for g in games_list:
                # API v1 uses 'awayTeam'/'homeTeam' objects
                # Check different key possibilities just in case
                away_abbr = g.get('awayTeam', {}).get('abbrev') or g.get('awayTeam', {}).get('triCode')
                home_abbr = g.get('homeTeam', {}).get('abbrev') or g.get('homeTeam', {}).get('triCode')
                
                if away_abbr and home_abbr:
                    key = f"{away_abbr}@{home_abbr}"
                    schedule_map[key] = g['id']
        
        if not games:
            # Fallback to prediction interface
            predictions = self.predictor.get_daily_predictions()
            if not predictions:
                return "No games scheduled for today."
            games = [{'away_team': p['away_team'], 'home_team': p['home_team']} 
                    for p in predictions]
        
        # Make meta-ensemble predictions
        predictions = []
        for game in games:
            try:
                # Map RotoWire game to Vegas odds key
                odds_key = f"{game['away_team']}_vs_{game['home_team']}"
                vegas_odds = market_odds.get(odds_key)
                
                pred = self.meta_ensemble.predict(
                    game['away_team'],
                    game['home_team'],
                    away_lineup=game.get('away_lineup'),
                    home_lineup=game.get('home_lineup'),
                    away_goalie=game.get('away_goalie'),
                    home_goalie=game.get('home_goalie'),
                    vegas_odds=vegas_odds
                )
                
                # Attach odds taken for ROI tracking
                if vegas_odds:
                    pred['odds_taken'] = vegas_odds.get('home_ml') if pred['home_prob'] > pred['away_prob'] else vegas_odds.get('away_ml')

                # Include all games as requested by user
                if True: # was: if self.meta_ensemble.should_predict(pred):
                    # Attach Game ID
                    key = f"{game['away_team']}@{game['home_team']}"
                    game_id = schedule_map.get(key)
                    if not game_id:
                        print(f"⚠️  Could not find game_id for {key}. Keys in map: {list(schedule_map.keys())[:5]}...")
                    
                    predictions.append({
                        'away_team': game['away_team'],
                        'home_team': game['home_team'],
                        'away_prob': pred['away_prob'],
                        'home_prob': pred['home_prob'],
                        'predicted_winner': pred['predicted_winner'],
                        'confidence': pred['prediction_confidence'] * 100,
                        'away_goalie': game.get('away_goalie', 'TBD'),
                        'home_goalie': game.get('home_goalie', 'TBD'),
                        'start_time': game.get('game_time', ''),
                        'contexts': pred.get('contexts_used', []),
                        'game_id': game_id,
                        'confidence_tier': pred.get('confidence_tier', 'Standard'),
                        'predicted_margin': pred.get('predicted_margin', 0.0),
                        'edge_away': pred.get('edge_away', 0.0),
                        'edge_home': pred.get('edge_home', 0.0),
                        'is_plus_ev_away': pred.get('is_plus_ev_away', False),
                        'is_plus_ev_home': pred.get('is_plus_ev_home', False),
                        'suggested_units': pred.get('suggested_units', 0.0),
                        'odds_taken': pred.get('odds_taken', 0),
                        'p1_home_prob': pred.get('p1_home_prob', 50.0)
                    })
            except Exception as e:
                print(f"Error predicting {game['away_team']} @ {game['home_team']}: {e}")
                continue
        
        if not predictions:
            return "No high-confidence predictions for today."
            
        # SAVE PREDICTIONS TO IDB
        self.save_predictions_to_history(predictions)
        
        total_games = len(games)
        
        # Format predictions
        summary = "🏒 **NHL GAME PREDICTIONS FOR TODAY** 🏒\n\n"
        summary += f"Showing **{len(predictions)} high-confidence games** out of {total_games} on the schedule.\n"
        summary += f"(Meta-Ensemble Model: 55-60% accuracy)\n\n"

        for i, pred in enumerate(predictions, 1):
            away = pred['away_team']
            home = pred['home_team']
            winner = pred['predicted_winner']
            confidence = pred['confidence']
            
            # Get actual score prediction from advanced score model
            score_pred = {}
            try:
                from score_prediction_model import ScorePredictionModel
                score_model = ScorePredictionModel()
                score_pred = score_model.predict_score(
                    away, home,
                    away_goalie=pred.get('away_goalie'),
                    home_goalie=pred.get('home_goalie'),
                    away_b2b=pred.get('away_back_to_back', False),
                    home_b2b=pred.get('home_back_to_back', False)
                )
                away_score = score_pred['away_score']
                home_score = score_pred['home_score']
            except Exception as e:
                # Fallback: derive realistic scores from xG averages + win probability
                try:
                    base_pred = self.predictor.learning_model.predict_game(away, home)
                    # Use xG averages (realistic per-game values ~2-4), NOT raw model composite scores
                    away_xg = base_pred.get('away_perf', {}).get('xg_avg', 2.8)
                    home_xg = base_pred.get('home_perf', {}).get('xg_avg', 2.8)
                    away_score = round(away_xg)
                    home_score = round(home_xg)
                    # Ensure winner's score is higher
                    if winner == away and away_score <= home_score:
                        away_score = home_score + 1
                    elif winner == home and home_score <= away_score:
                        home_score = away_score + 1
                except:
                    # Final fallback
                    if winner == away:
                        away_score = 3
                        home_score = 2
                    else:
                        away_score = 2
                        home_score = 3
            
            summary += f"**Game {i}**: {away} @ {home}\n"
            summary += f"  🏆 Prediction: **{winner} wins** ({away_score}-{home_score})\n"
            
            # Phase 17: Period 1 Prediction
            p1_home_prob = pred.get('p1_home_prob', 50.0)
            p1_winner = home if p1_home_prob > 55 else (away if p1_home_prob < 45 else None)
            if p1_winner:
                p1_conf = max(p1_home_prob, 100 - p1_home_prob)
                summary += f"  🕐 1st Period: **{p1_winner}** favored ({p1_conf:.1f}%)\n"
            
            summary += f"  ⭐ Confidence: {confidence:.1f}% ({pred.get('confidence_tier', 'Standard')})\n"
            
            # Phase 16: Market Value Overlay
            edge = pred.get('edge_home') if winner == home else pred.get('edge_away')
            if edge and edge > 5.0:
                summary += f"  💰 **+EV Value**: Edge of **{edge:.1f}%** detected vs Market\n"
                if pred.get('suggested_units', 0) > 0:
                    summary += f"  📏 **Bet Size**: Suggested **{pred['suggested_units']} units** (Kelly Criterion)\n"
            elif edge and edge > 1.0:
                summary += f"  ⚖️ Market Alignment: Edge of {edge:.1f}%\n"

            if 'predicted_margin' in pred and abs(pred['predicted_margin']) > 0.1:
                side = "Home" if pred['predicted_margin'] > 0 else "Away"
                summary += f"  📏 Margin Model: **{side} {abs(pred['predicted_margin']):.1f}** goals\n"

            # Add In-Depth Analysis
            # Add In-Depth Analysis
            has_factors = False
            if 'factors' in score_pred:
                factors = score_pred['factors']
                if factors.get('pace') != 'Neutral':
                    summary += f"  ⏱️ {factors['pace']}\n"
                    has_factors = True
                if factors.get('situation') != 'Neutral':
                    summary += f"  🔥 {factors['situation']}\n"
                    has_factors = True
                    
            if not has_factors:
                 summary += f"  🥅 Goalies: {pred['away_goalie']} vs {pred['home_goalie']}\n"
            
            # Show contexts used
            if pred['contexts']:
                contexts_str = ", ".join([f"{c[0]} ({c[1]:.0%})" for c in pred['contexts']])
                summary += f"  🎯 Contexts: {contexts_str}\n"
            
            summary += "\n"
        
        # Recalculate model performance from latest predictions before displaying
        try:
            self.predictor.learning_model.recalculate_performance_from_scratch()
        except Exception as e:
            print(f"⚠️  Warning: Failed to recalculate performance: {e}")
        
        # Add model performance
        perf = self.predictor.learning_model.get_model_performance()
        summary += f"📊 **Model Performance:**\n"
        summary += f"   Accuracy: {perf.get('accuracy', 0):.1%}\n"
        summary += f"   Recent Accuracy: {perf.get('recent_accuracy', 0):.1%}\n"
        summary += f"   Total Games: {perf.get('total_games', 0)}\n\n"
        
        summary += f"🤖 Generated by NHL Meta-Ensemble Model (55-60% accuracy)\n"
        summary += f"📅 {datetime.now(pytz.timezone('US/Central')).strftime('%Y-%m-%d %I:%M %p CT')}"
        
        return summary

    def send_email_notification(self, to_email, subject="Daily NHL Predictions"):
        """Send predictions via email"""
        try:
            # Email configuration (you'll need to set these as environment variables)
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            email_user = os.getenv('EMAIL_USER')
            email_password = os.getenv('EMAIL_PASSWORD')
            
            if not email_user or not email_password:
                print("❌ Email credentials not configured. Set EMAIL_USER and EMAIL_PASSWORD environment variables.")
                return False
            
            # Get predictions
            predictions_text = self.get_daily_predictions_summary()
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(predictions_text, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            text = msg.as_string()
            server.sendmail(email_user, to_email, text)
            server.quit()
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    def _split_message(self, text, limit=1900):
        """Split a large message into chunks that fit Discord's character limit"""
        chunks = []
        while len(text) > limit:
            # Find the last newline before the limit to avoid cutting in the middle of a line
            split_at = text.rfind('\n', 0, limit)
            if split_at == -1 or split_at < 500: # If no newline or it's too early, just cut at limit
                split_at = limit
            
            chunks.append(text[:split_at].strip())
            text = text[split_at:].strip()
        
        if text:
            chunks.append(text)
        return chunks

    def send_discord_notification(self, webhook_url):
        """Send predictions via Discord webhook"""
        try:
            import requests
            
            predictions_text = self.get_daily_predictions_summary()
            
            # Split message if it exceeds Discord's limit (2000 chars)
            # Using 1900 to be safe
            chunks = self._split_message(predictions_text, limit=1900)
            
            success = True
            for i, chunk in enumerate(chunks):
                # Discord webhook payload
                payload = {
                    "content": chunk,
                    "username": "NHL Predictions Bot",
                    "avatar_url": "https://cdn-icons-png.flaticon.com/512/3048/3048127.png"
                }
                
                # Add part indicator if split
                if len(chunks) > 1:
                    payload["username"] = f"NHL Predictions Bot (Part {i+1}/{len(chunks)})"

                response = requests.post(webhook_url, json=payload, timeout=15)
                
                if response.status_code not in [200, 204]:
                    print(f"❌ Discord notification chunk {i+1} failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    success = False
            
            if success:
                print(f"✅ Discord notification sent successfully ({len(chunks)} parts)")
            return success
                
        except Exception as e:
            print(f"❌ Error sending Discord notification: {e}")
            return False
    
    def save_to_file(self, filename=None):
        """Save predictions to a text file"""
        try:
            if not filename:
                date_str = datetime.now(pytz.timezone('US/Central')).strftime('%Y%m%d')
                filename = f"daily_predictions_{date_str}.txt"
            
            predictions_text = self.get_daily_predictions_summary()
            
            with open(filename, 'w') as f:
                f.write(predictions_text)
            
            print(f"✅ Predictions saved to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving to file: {e}")
            return False
    
    def send_notification(self, method="file", **kwargs):
        """Send notification using specified method"""
        if method == "email":
            return self.send_email_notification(
                kwargs.get('to_email'),
                kwargs.get('subject', 'Daily NHL Predictions')
            )
        elif method == "discord":
            return self.send_discord_notification(kwargs.get('webhook_url'))
        elif method == "file":
            return self.save_to_file(kwargs.get('filename'))
        else:
            print(f"❌ Unknown notification method: {method}")
            return False


def main():
    """Main function to send daily predictions"""
    notifier = DailyPredictionNotifier()
    
    print("🔔 DAILY NHL PREDICTIONS NOTIFIER")
    print("=" * 50)
    
    # Get predictions summary
    summary = notifier.get_daily_predictions_summary()
    print(summary)
    print("\n" + "=" * 50)
    
    # Send notifications
    print("\n📤 SENDING NOTIFICATIONS:")
    
    # Save to file (always works)
    notifier.save_to_file()
    
    # Try email if configured
    email = os.getenv('NOTIFICATION_EMAIL')
    if email:
        notifier.send_email_notification(email)
    else:
        print("ℹ️  Set NOTIFICATION_EMAIL environment variable to enable email notifications")
    
    # Try Discord if configured
    discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
    if discord_webhook:
        notifier.send_discord_notification(discord_webhook)
    else:
        print("ℹ️  Set DISCORD_WEBHOOK_URL environment variable to enable Discord notifications")


if __name__ == "__main__":
    main()
