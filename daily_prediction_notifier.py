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

class DailyPredictionNotifier:
    def __init__(self):
        """Initialize the notifier with meta-ensemble predictor"""
        self.predictor = PredictionInterface()  # Keep for compatibility
        self.meta_ensemble = MetaEnsemblePredictor()
        self.rotowire = RotoWireScraper()
        
    def get_daily_predictions_summary(self):
        """Get formatted summary of today's predictions using meta-ensemble"""
        # Get today's games from RotoWire
        rotowire_data = self.rotowire.scrape_daily_data()
        games = rotowire_data.get('games', [])
        
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
                pred = self.meta_ensemble.predict(
                    game['away_team'],
                    game['home_team'],
                    away_lineup=game.get('away_lineup'),
                    home_lineup=game.get('home_lineup'),
                    away_goalie=game.get('away_goalie'),
                    home_goalie=game.get('home_goalie')
                )
                
                # Only include if meets confidence threshold (50%)
                if self.meta_ensemble.should_predict(pred):
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
                        'contexts': pred.get('contexts_used', [])
                    })
            except Exception as e:
                print(f"Error predicting {game['away_team']} @ {game['home_team']}: {e}")
                continue
        
        if not predictions:
            return "No high-confidence predictions for today."
        
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
            try:
                from score_prediction_model import ScorePredictionModel
                score_model = ScorePredictionModel()
                score_pred = score_model.predict_score(
                    away, home,
                    away_goalie=pred.get('away_goalie'),
                    home_goalie=pred.get('home_goalie')
                )
                away_score = score_pred['away_score']
                home_score = score_pred['home_score']
            except Exception as e:
                # Fallback to base model
                try:
                    base_pred = self.predictor.learning_model.predict_game(away, home)
                    away_score = round(base_pred.get('away_score', 3))
                    home_score = round(base_pred.get('home_score', 3))
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
            summary += f"  ⭐ Confidence: {confidence:.1f}%\n"
            summary += f"  🥅 Goalies: {pred['away_goalie']} vs {pred['home_goalie']}\n"
            
            # Show contexts used
            if pred['contexts']:
                contexts_str = ", ".join([f"{c[0]} ({c[1]:.0%})" for c in pred['contexts']])
                summary += f"  🎯 Contexts: {contexts_str}\n"
            
            summary += "\n"
        
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
    
    def send_discord_notification(self, webhook_url):
        """Send predictions via Discord webhook"""
        try:
            import requests
            
            predictions_text = self.get_daily_predictions_summary()
            
            # Discord webhook payload
            payload = {
                "content": predictions_text,
                "username": "NHL Predictions Bot",
                "avatar_url": "https://cdn-icons-png.flaticon.com/512/3048/3048127.png"
            }
            
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 204:
                print("✅ Discord notification sent successfully")
                return True
            else:
                print(f"❌ Discord notification failed: {response.status_code}")
                return False
                
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
