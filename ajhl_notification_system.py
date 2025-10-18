#!/usr/bin/env python3
"""
AJHL Notification System
Sends notifications when new game data becomes available for Lloydminster Bobcats
"""

import json
import time
import logging
import smtplib
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import schedule
import threading
from ajhl_team_config import DATA_DIRECTORIES
from ajhl_complete_opponent_system import AJHLCompleteOpponentSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AJHLNotificationSystem:
    """Notification system for AJHL game data availability"""
    
    def __init__(self, config_file: str = "notification_config.json"):
        """Initialize the notification system"""
        self.config_file = config_file
        self.config = self._load_config()
        self.last_check_time = None
        self.last_game_data = None
        self.notification_history = []
        
        # Load notification history
        self._load_notification_history()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load notification configuration"""
        default_config = {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "recipients": []
            },
            "sms": {
                "enabled": False,
                "provider": "twilio",  # twilio, sendgrid, etc.
                "account_sid": "",
                "auth_token": "",
                "from_number": "",
                "recipients": []
            },
            "push": {
                "enabled": False,
                "service": "pushover",  # pushover, pushbullet, etc.
                "api_key": "",
                "user_key": "",
                "device": ""
            },
            "discord": {
                "enabled": False,
                "webhook_url": ""
            },
            "slack": {
                "enabled": False,
                "webhook_url": ""
            },
            "check_interval_minutes": 30,
            "team_name": "Lloydminster Bobcats",
            "team_id": "21479"
        }
        
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                # Create default config file
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"📄 Created default notification config: {self.config_file}")
                return default_config
        except Exception as e:
            logger.error(f"❌ Error loading config: {e}")
            return default_config
    
    def _load_notification_history(self):
        """Load notification history to avoid duplicates"""
        history_file = Path(DATA_DIRECTORIES['base_path']) / 'logs' / 'notification_history.json'
        try:
            if history_file.exists():
                with open(history_file, 'r') as f:
                    self.notification_history = json.load(f)
            else:
                self.notification_history = []
        except Exception as e:
            logger.warning(f"⚠️  Error loading notification history: {e}")
            self.notification_history = []
    
    def _save_notification_history(self):
        """Save notification history"""
        history_file = Path(DATA_DIRECTORIES['base_path']) / 'logs' / 'notification_history.json'
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(history_file, 'w') as f:
                json.dump(self.notification_history, f, indent=2)
        except Exception as e:
            logger.warning(f"⚠️  Error saving notification history: {e}")
    
    def check_for_new_game_data(self) -> Dict[str, Any]:
        """Check if new game data is available"""
        logger.info("🔍 Checking for new game data...")
        
        try:
            # Initialize the opponent system to check for data
            from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
            system = AJHLCompleteOpponentSystem(HUDL_USERNAME, HUDL_PASSWORD)
            
            # Get current game data status
            current_data = self._get_current_game_data_status()
            
            # Compare with last known data
            if self.last_game_data is None:
                self.last_game_data = current_data
                logger.info("📊 Initial game data snapshot taken")
                return {"status": "initial", "message": "Initial data snapshot taken"}
            
            # Check for changes
            new_games = self._find_new_games(current_data, self.last_game_data)
            
            if new_games:
                logger.info(f"🎉 Found {len(new_games)} new games with data!")
                
                # Send notifications
                notification_results = self._send_notifications(new_games)
                
                # Update last known data
                self.last_game_data = current_data
                
                # Save notification to history
                notification_record = {
                    "timestamp": datetime.now().isoformat(),
                    "new_games": new_games,
                    "notification_results": notification_results
                }
                self.notification_history.append(notification_record)
                self._save_notification_history()
                
                return {
                    "status": "new_data",
                    "new_games": new_games,
                    "notification_results": notification_results
                }
            else:
                logger.info("📊 No new game data found")
                return {"status": "no_new_data", "message": "No new games with data found"}
                
        except Exception as e:
            logger.error(f"❌ Error checking for new game data: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_current_game_data_status(self) -> Dict[str, Any]:
        """Get current status of game data"""
        try:
            # Check Lloydminster Bobcats data directory
            team_dir = Path(DATA_DIRECTORIES['base_path']) / 'opponent_data' / 'lloydminster_bobcats'
            
            if not team_dir.exists():
                return {"games": [], "last_updated": None}
            
            # Look for recent game files
            game_files = []
            for file_path in team_dir.rglob("*.json"):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    game_files.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "modified_time": file_time.isoformat(),
                        "size": file_path.stat().st_size
                    })
            
            # Sort by modification time
            game_files.sort(key=lambda x: x['modified_time'], reverse=True)
            
            return {
                "games": game_files,
                "last_updated": game_files[0]['modified_time'] if game_files else None,
                "total_files": len(game_files)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting current game data status: {e}")
            return {"games": [], "last_updated": None, "error": str(e)}
    
    def _find_new_games(self, current_data: Dict, last_data: Dict) -> List[Dict[str, Any]]:
        """Find new games by comparing current and last known data"""
        if not last_data or not last_data.get('games'):
            return []
        
        current_files = {f['filename']: f for f in current_data.get('games', [])}
        last_files = {f['filename']: f for f in last_data.get('games', [])}
        
        new_games = []
        
        # Find files that are new or have been updated
        for filename, file_info in current_files.items():
            if filename not in last_files:
                # New file
                new_games.append({
                    "type": "new_file",
                    "filename": filename,
                    "modified_time": file_info['modified_time'],
                    "size": file_info['size']
                })
            else:
                # Check if file was modified
                last_file_info = last_files[filename]
                if file_info['modified_time'] != last_file_info['modified_time']:
                    new_games.append({
                        "type": "updated_file",
                        "filename": filename,
                        "modified_time": file_info['modified_time'],
                        "size": file_info['size'],
                        "previous_time": last_file_info['modified_time']
                    })
        
        return new_games
    
    def _send_notifications(self, new_games: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send notifications through all enabled channels"""
        results = {
            "email": {"sent": 0, "failed": 0, "errors": []},
            "sms": {"sent": 0, "failed": 0, "errors": []},
            "push": {"sent": 0, "failed": 0, "errors": []},
            "discord": {"sent": 0, "failed": 0, "errors": []},
            "slack": {"sent": 0, "failed": 0, "errors": []}
        }
        
        # Prepare notification message
        message = self._prepare_notification_message(new_games)
        
        # Send email notifications
        if self.config['email']['enabled']:
            results['email'] = self._send_email_notification(message, new_games)
        
        # Send SMS notifications
        if self.config['sms']['enabled']:
            results['sms'] = self._send_sms_notification(message)
        
        # Send push notifications
        if self.config['push']['enabled']:
            results['push'] = self._send_push_notification(message)
        
        # Send Discord notifications
        if self.config['discord']['enabled']:
            results['discord'] = self._send_discord_notification(message)
        
        # Send Slack notifications
        if self.config['slack']['enabled']:
            results['slack'] = self._send_slack_notification(message)
        
        return results
    
    def _prepare_notification_message(self, new_games: List[Dict[str, Any]]) -> str:
        """Prepare notification message"""
        team_name = self.config['team_name']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"🏒 {team_name} - New Game Data Available!\n\n"
        message += f"📅 Time: {timestamp}\n"
        message += f"📊 New/Updated Files: {len(new_games)}\n\n"
        
        for i, game in enumerate(new_games, 1):
            message += f"{i}. {game['filename']}\n"
            message += f"   📁 Type: {game['type']}\n"
            message += f"   ⏰ Updated: {game['modified_time']}\n"
            message += f"   📏 Size: {game['size']} bytes\n\n"
        
        message += "🔗 Check your data directory for the latest files!"
        
        return message
    
    def _send_email_notification(self, message: str, new_games: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send email notification"""
        try:
            email_config = self.config['email']
            
            # Create message
            msg = MimeMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(email_config['recipients'])
            msg['Subject'] = f"🏒 {self.config['team_name']} - New Game Data Available"
            
            # Add body
            msg.attach(MimeText(message, 'plain'))
            
            # Connect to server and send
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            
            text = msg.as_string()
            server.sendmail(email_config['username'], email_config['recipients'], text)
            server.quit()
            
            logger.info(f"✅ Email notification sent to {len(email_config['recipients'])} recipients")
            return {"sent": len(email_config['recipients']), "failed": 0, "errors": []}
            
        except Exception as e:
            logger.error(f"❌ Email notification failed: {e}")
            return {"sent": 0, "failed": 1, "errors": [str(e)]}
    
    def _send_sms_notification(self, message: str) -> Dict[str, Any]:
        """Send SMS notification via Twilio"""
        try:
            sms_config = self.config['sms']
            
            if sms_config['provider'] == 'twilio':
                from twilio.rest import Client
                
                client = Client(sms_config['account_sid'], sms_config['auth_token'])
                
                sent = 0
                failed = 0
                errors = []
                
                for recipient in sms_config['recipients']:
                    try:
                        message_obj = client.messages.create(
                            body=message,
                            from_=sms_config['from_number'],
                            to=recipient
                        )
                        sent += 1
                        logger.info(f"✅ SMS sent to {recipient}")
                    except Exception as e:
                        failed += 1
                        errors.append(f"Failed to send to {recipient}: {str(e)}")
                
                return {"sent": sent, "failed": failed, "errors": errors}
            else:
                return {"sent": 0, "failed": 1, "errors": ["Unsupported SMS provider"]}
                
        except Exception as e:
            logger.error(f"❌ SMS notification failed: {e}")
            return {"sent": 0, "failed": 1, "errors": [str(e)]}
    
    def _send_push_notification(self, message: str) -> Dict[str, Any]:
        """Send push notification via Pushover"""
        try:
            push_config = self.config['push']
            
            if push_config['service'] == 'pushover':
                url = "https://api.pushover.net/1/messages.json"
                
                data = {
                    "token": push_config['api_key'],
                    "user": push_config['user_key'],
                    "message": message,
                    "title": f"🏒 {self.config['team_name']} Game Data"
                }
                
                if push_config.get('device'):
                    data['device'] = push_config['device']
                
                response = requests.post(url, data=data)
                
                if response.status_code == 200:
                    logger.info("✅ Push notification sent")
                    return {"sent": 1, "failed": 0, "errors": []}
                else:
                    logger.error(f"❌ Push notification failed: {response.text}")
                    return {"sent": 0, "failed": 1, "errors": [response.text]}
            else:
                return {"sent": 0, "failed": 1, "errors": ["Unsupported push service"]}
                
        except Exception as e:
            logger.error(f"❌ Push notification failed: {e}")
            return {"sent": 0, "failed": 1, "errors": [str(e)]}
    
    def _send_discord_notification(self, message: str) -> Dict[str, Any]:
        """Send Discord notification via webhook"""
        try:
            discord_config = self.config['discord']
            
            webhook_url = discord_config['webhook_url']
            
            # Discord message format
            discord_message = {
                "content": f"🏒 **{self.config['team_name']} - New Game Data Available!**",
                "embeds": [{
                    "title": "New Game Data Detected",
                    "description": message,
                    "color": 0x00ff00,  # Green color
                    "timestamp": datetime.now().isoformat(),
                    "footer": {
                        "text": "AJHL Data Collection System"
                    }
                }]
            }
            
            response = requests.post(webhook_url, json=discord_message)
            
            if response.status_code == 204:
                logger.info("✅ Discord notification sent")
                return {"sent": 1, "failed": 0, "errors": []}
            else:
                logger.error(f"❌ Discord notification failed: {response.text}")
                return {"sent": 0, "failed": 1, "errors": [response.text]}
                
        except Exception as e:
            logger.error(f"❌ Discord notification failed: {e}")
            return {"sent": 0, "failed": 1, "errors": [str(e)]}
    
    def _send_slack_notification(self, message: str) -> Dict[str, Any]:
        """Send Slack notification via webhook"""
        try:
            slack_config = self.config['slack']
            
            webhook_url = slack_config['webhook_url']
            
            # Slack message format
            slack_message = {
                "text": f"🏒 *{self.config['team_name']} - New Game Data Available!*",
                "attachments": [{
                    "color": "good",
                    "text": message,
                    "footer": "AJHL Data Collection System",
                    "ts": int(datetime.now().timestamp())
                }]
            }
            
            response = requests.post(webhook_url, json=slack_message)
            
            if response.status_code == 200:
                logger.info("✅ Slack notification sent")
                return {"sent": 1, "failed": 0, "errors": []}
            else:
                logger.error(f"❌ Slack notification failed: {response.text}")
                return {"sent": 0, "failed": 1, "errors": [response.text]}
                
        except Exception as e:
            logger.error(f"❌ Slack notification failed: {e}")
            return {"sent": 0, "failed": 1, "errors": [str(e)]}
    
    def start_monitoring(self):
        """Start continuous monitoring for new game data"""
        logger.info("🚀 Starting AJHL notification monitoring...")
        
        # Schedule regular checks
        interval = self.config['check_interval_minutes']
        schedule.every(interval).minutes.do(self.check_for_new_game_data)
        
        logger.info(f"⏰ Monitoring started - checking every {interval} minutes")
        logger.info("📱 Notifications enabled for:")
        
        if self.config['email']['enabled']:
            logger.info(f"  📧 Email: {len(self.config['email']['recipients'])} recipients")
        if self.config['sms']['enabled']:
            logger.info(f"  📱 SMS: {len(self.config['sms']['recipients'])} recipients")
        if self.config['push']['enabled']:
            logger.info(f"  🔔 Push: {self.config['push']['service']}")
        if self.config['discord']['enabled']:
            logger.info(f"  💬 Discord: Webhook configured")
        if self.config['slack']['enabled']:
            logger.info(f"  💬 Slack: Webhook configured")
        
        # Run initial check
        self.check_for_new_game_data()
        
        # Start monitoring loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
    
    def test_notifications(self):
        """Test all configured notification channels"""
        logger.info("🧪 Testing notification channels...")
        
        test_games = [{
            "type": "test",
            "filename": "test_game_data.json",
            "modified_time": datetime.now().isoformat(),
            "size": 1024
        }]
        
        results = self._send_notifications(test_games)
        
        print("📊 Notification Test Results:")
        for channel, result in results.items():
            if self.config[channel]['enabled']:
                status = "✅" if result['sent'] > 0 else "❌"
                print(f"  {status} {channel.title()}: {result['sent']} sent, {result['failed']} failed")
                if result['errors']:
                    for error in result['errors']:
                        print(f"    Error: {error}")
    
    def get_notification_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get notification history for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_notifications = []
        for notification in self.notification_history:
            notification_time = datetime.fromisoformat(notification['timestamp'])
            if notification_time >= cutoff_date:
                recent_notifications.append(notification)
        
        return recent_notifications

def main():
    """Main function for notification system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AJHL Notification System')
    parser.add_argument('--start', action='store_true', help='Start monitoring for new game data')
    parser.add_argument('--check', action='store_true', help='Check once for new game data')
    parser.add_argument('--test', action='store_true', help='Test notification channels')
    parser.add_argument('--history', action='store_true', help='Show notification history')
    parser.add_argument('--config', action='store_true', help='Show current configuration')
    
    args = parser.parse_args()
    
    notification_system = AJHLNotificationSystem()
    
    if args.start:
        print("🚀 Starting AJHL notification monitoring...")
        notification_system.start_monitoring()
    
    elif args.check:
        print("🔍 Checking for new game data...")
        result = notification_system.check_for_new_game_data()
        print(f"Status: {result['status']}")
        if 'new_games' in result:
            print(f"New games found: {len(result['new_games'])}")
    
    elif args.test:
        print("🧪 Testing notification channels...")
        notification_system.test_notifications()
    
    elif args.history:
        print("📊 Notification History (Last 7 days):")
        history = notification_system.get_notification_history(7)
        for notification in history:
            print(f"  {notification['timestamp']}: {len(notification['new_games'])} new games")
    
    elif args.config:
        print("⚙️ Current Configuration:")
        print(json.dumps(notification_system.config, indent=2))
    
    else:
        print("🏒 AJHL Notification System")
        print("=" * 40)
        print("Available commands:")
        print("  --start    Start monitoring for new game data")
        print("  --check    Check once for new game data")
        print("  --test     Test notification channels")
        print("  --history  Show notification history")
        print("  --config   Show current configuration")
        print("\n📝 First, edit notification_config.json to configure your notification channels")

if __name__ == "__main__":
    main()

