# AJHL Notification System

A comprehensive notification system that alerts you when new game data becomes available for the Lloydminster Bobcats and their upcoming opponents.

## 🚀 Quick Start

1. **Install requirements:**
   ```bash
   pip install -r ajhl_requirements.txt
   ```

2. **Configure credentials:**
   Edit `hudl_credentials.py` with your Hudl Instat credentials

3. **Setup notifications:**
   ```bash
   python setup_notifications.py
   ```

4. **Start the system:**
   ```bash
   python start_ajhl_system.py
   ```

## 📱 Notification Channels

### Email Notifications
- **Gmail**: Use your Gmail account with an app password
- **Other SMTP**: Configure any SMTP server
- **Multiple recipients**: Send to multiple email addresses

### SMS Notifications
- **Twilio** (recommended): Professional SMS service
- **SendGrid**: Alternative SMS provider
- **Multiple recipients**: Send to multiple phone numbers

### Push Notifications
- **Pushover**: Cross-platform push notifications
- **Pushbullet**: Alternative push service
- **Mobile & Desktop**: Works on all devices

### Team Communication
- **Discord**: Webhook integration for team channels
- **Slack**: Webhook integration for team workspaces

## ⚙️ Configuration

The system uses `notification_config.json` for configuration:

```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your_email@gmail.com",
    "password": "your_app_password",
    "recipients": ["coach@team.com", "analyst@team.com"]
  },
  "sms": {
    "enabled": true,
    "provider": "twilio",
    "account_sid": "your_twilio_sid",
    "auth_token": "your_twilio_token",
    "from_number": "+1234567890",
    "recipients": ["+1234567890", "+0987654321"]
  },
  "push": {
    "enabled": true,
    "service": "pushover",
    "api_key": "your_pushover_token",
    "user_key": "your_pushover_user_key"
  },
  "discord": {
    "enabled": true,
    "webhook_url": "https://discord.com/api/webhooks/..."
  },
  "slack": {
    "enabled": true,
    "webhook_url": "https://hooks.slack.com/services/..."
  },
  "check_interval_minutes": 30,
  "team_name": "Lloydminster Bobcats",
  "team_id": "21479"
}
```

## 🔧 Setup Instructions

### Email Setup (Gmail)
1. Enable 2-factor authentication on your Gmail account
2. Generate an app password: Google Account → Security → App passwords
3. Use your Gmail address and the app password

### SMS Setup (Twilio)
1. Sign up at [twilio.com](https://twilio.com)
2. Get your Account SID and Auth Token from the console
3. Purchase a phone number for sending SMS
4. Add recipient phone numbers in E.164 format (+1234567890)

### Push Notifications (Pushover)
1. Sign up at [pushover.net](https://pushover.net)
2. Create an application to get your API token
3. Get your user key from your account page
4. Install the Pushover app on your devices

### Discord Setup
1. Go to your Discord server
2. Right-click the channel → Edit Channel → Integrations → Webhooks
3. Create a new webhook and copy the URL

### Slack Setup
1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Create a new app or select existing one
3. Go to Incoming Webhooks and activate them
4. Add a webhook to your desired channel

## 🎯 Usage Examples

### Run Full Analysis with Notifications
```bash
python ajhl_complete_system_with_notifications.py --full
```

### Start Continuous Monitoring
```bash
python ajhl_complete_system_with_notifications.py --monitor
```

### Test Notifications
```bash
python ajhl_complete_system_with_notifications.py --test
```

### Check System Status
```bash
python ajhl_complete_system_with_notifications.py --status
```

## 📊 Monitoring Features

### Automatic Detection
- Monitors data directories for new files
- Detects file modifications and updates
- Compares timestamps to identify new data

### Smart Notifications
- Avoids duplicate notifications
- Tracks notification history
- Provides detailed file information

### System Health
- Monitors system status
- Tracks notification success rates
- Logs all activities

## 🔍 Notification Examples

### Email Notification
```
🏒 Lloydminster Bobcats - New Game Data Available!

📅 Time: 2024-01-15 14:30:00
📊 New/Updated Files: 3

1. game_20240115_vs_bandits.json
   📁 Type: new_file
   ⏰ Updated: 2024-01-15T14:25:00
   📏 Size: 15420 bytes

2. skaters_data_20240115.json
   📁 Type: updated_file
   ⏰ Updated: 2024-01-15T14:28:00
   📏 Size: 8920 bytes

🔗 Check your data directory for the latest files!
```

### SMS Notification
```
🏒 Lloydminster Bobcats - New Game Data Available! 3 new/updated files detected. Check your data directory!
```

### Discord/Slack Notification
Rich embeds with color coding and detailed information about new data files.

## 📁 File Structure

```
ajhl_data/
├── opponent_data/
│   ├── lloydminster_bobcats/
│   │   ├── game_data_*.json
│   │   └── skaters_data_*.json
│   ├── upcoming_opponents/
│   └── reports/
├── logs/
│   ├── notification_history.json
│   └── system_logs.log
└── reports/
    ├── dashboards/
    └── summaries/
```

## 🛠️ Troubleshooting

### Common Issues

**Notifications not sending:**
- Check credentials and configuration
- Verify internet connection
- Check service-specific requirements (app passwords, API keys)

**No new data detected:**
- Verify data collection is working
- Check file permissions
- Ensure data files are being created

**System not starting:**
- Check Python dependencies
- Verify credentials file exists
- Check file permissions

### Debug Mode
Enable debug logging by modifying the logging level in the scripts:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Channels
```bash
# Test email only
python ajhl_notification_system.py --test

# Test specific notification
python -c "
from ajhl_notification_system import AJHLNotificationSystem
ns = AJHLNotificationSystem()
ns.test_notifications()
"
```

## 📈 Advanced Features

### Custom Check Intervals
Modify `check_interval_minutes` in the config to change how often the system checks for new data.

### Multiple Teams
The system can be configured to monitor multiple teams by modifying the team configuration.

### Integration with Other Systems
The notification system can be integrated with other analytics tools and databases.

## 🔒 Security Notes

- Store credentials securely
- Use app passwords instead of main passwords
- Regularly rotate API keys
- Monitor notification logs for suspicious activity

## 📞 Support

For issues or questions:
1. Check the logs in `ajhl_data/logs/`
2. Run the test command to verify configuration
3. Check the system status for health information

## 🎉 Success!

Once configured, you'll receive notifications whenever new game data becomes available, keeping you up-to-date with the latest analytics for the Lloydminster Bobcats and their opponents!
