"""
Daily Prediction Notifier
Sends daily NHL game predictions via email, Discord, or other methods
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz
from prediction_interface import PredictionInterface
import os

class DailyPredictionNotifier:
    def __init__(self):
        """Initialize the notifier"""
        self.predictor = PredictionInterface()
        
    def get_daily_predictions_summary(self):
        """Get formatted summary of today's predictions"""
        predictions = self.predictor.get_todays_predictions()
        
        if not predictions:
            return "No games scheduled for today."

        total_games = len(predictions)

        # ---- High-confidence filter for notifications ----
        # Use overall confidence and Monte Carlo flip rate to focus Discord/email
        # on the most stable edges. We still keep all games available via the API.
        GREEN_CONF_MIN = 0.58     # at least 58% win prob on favorite
        GREEN_FLIP_MAX = 0.40     # avoid very volatile (high flip-rate) games

        green_zone = []
        for pred in predictions:
            confidence = float(pred.get('prediction_confidence', max(
                pred.get('predicted_away_win_prob', 0.5),
                pred.get('predicted_home_win_prob', 0.5),
            )))
            flip_rate = pred.get('monte_carlo_flip_rate')
            try:
                flip_rate = float(flip_rate) if flip_rate is not None else 0.0
            except (TypeError, ValueError):
                flip_rate = 0.0

            if confidence >= GREEN_CONF_MIN and flip_rate <= GREEN_FLIP_MAX:
                green_zone.append(pred)

        # If filter is too strict and yields nothing, fall back to all games
        filtered = green_zone if green_zone else predictions
        
        # Format predictions as bullet points (row 3, row 4, ...)
        summary = "🏒 **NHL GAME PREDICTIONS FOR TODAY** 🏒\n\n"
        if green_zone:
            summary += f"Showing **{len(filtered)} high-confidence games** out of {total_games} on the schedule.\n"
            summary += f"(Filters: confidence ≥ {GREEN_CONF_MIN*100:.0f}%, volatility (flip-rate) ≤ {int(GREEN_FLIP_MAX*100)}%)\n\n"

        for i, pred in enumerate(filtered, 1):
            away_team = pred['away_team']
            home_team = pred['home_team']
            away_prob = pred['predicted_away_win_prob'] * 100  # Convert to percentage
            home_prob = pred['predicted_home_win_prob'] * 100  # Convert to percentage
            favorite = pred['favorite']
            confidence = float(pred.get('prediction_confidence', max(
                pred.get('predicted_away_win_prob', 0.5),
                pred.get('predicted_home_win_prob', 0.5),
            ))) * 100.0
            flip_rate = pred.get('monte_carlo_flip_rate') or 0.0
            upset = float(pred.get('upset_probability', 0.0) or 0.0) * 100.0

            # Flip-rate bands for readability
            try:
                flip_val = float(flip_rate)
            except (TypeError, ValueError):
                flip_val = 0.0
            if flip_val < 0.20:
                flip_label = "LOW"
            elif flip_val < 0.40:
                flip_label = "MED"
            else:
                flip_label = "HIGH"

            # Likeliest score using season/team and home/away goal averages
            try:
                home_perf = self.predictor.learning_model.get_team_performance(home_team, venue="home")
                away_perf = self.predictor.learning_model.get_team_performance(away_team, venue="away")
                home_g = float(home_perf.get("goals_avg", 3.0)) if home_perf else 3.0
                away_g = float(away_perf.get("goals_avg", 3.0)) if away_perf else 3.0
            except Exception:
                home_g = away_g = 3.0

            # Round to a plausible hockey scoreline near the season averages
            home_goals = int(round(home_g))
            away_goals = int(round(away_g))
            if home_goals == away_goals:
                # Nudge favorite to win by one
                if favorite == home_team:
                    home_goals = away_goals + 1
                else:
                    away_goals = home_goals + 1

            # Decide if OT/SO is likely based on closeness of win probability
            fav_prob = pred['predicted_home_win_prob'] if favorite == home_team else pred['predicted_away_win_prob']
            fav_prob_pct = fav_prob * 100.0
            if abs(home_goals - away_goals) == 1 and 50.0 <= fav_prob_pct <= 58.0:
                ot_tag = "(OT/SO likely)"
            else:
                ot_tag = "(regulation)"
            likely_score = f"{favorite} {max(home_goals, away_goals)}–{min(home_goals, away_goals)} {ot_tag}"

            summary += f"- **Row {i}**: {away_team} @ {home_team}\n"
            summary += f"  - 🎯 {away_team} {away_prob:.1f}% | {home_team} {home_prob:.1f}%\n"
            summary += f"  - ⭐ Favorite: {favorite} (confidence {confidence:.1f}%)\n"
            summary += f"  - 🌪️ Volatility (flip-rate): {flip_label} ({flip_val*100:.1f}%)\n"
            summary += f"  - ⚡ Upset risk: {upset:.1f}%\n"
            summary += f"  - 📐 Likeliest score: {likely_score}\n"
        
        # Add model performance
        perf = self.predictor.learning_model.get_model_performance()
        summary += f"📊 **Model Performance:**\n"
        summary += f"   Accuracy: {perf['accuracy']:.1%}\n"
        summary += f"   Recent Accuracy: {perf['recent_accuracy']:.1%}\n"
        summary += f"   Total Games: {perf['total_games']}\n\n"
        
        summary += f"🤖 Generated by NHL Self-Learning Model\n"
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
