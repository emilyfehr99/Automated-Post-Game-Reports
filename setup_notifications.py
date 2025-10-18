#!/usr/bin/env python3
"""
AJHL Notification Setup
Interactive setup for notification channels
"""

import json
import os
import getpass
from pathlib import Path

def setup_email_notifications():
    """Setup email notification configuration"""
    print("\n📧 Email Notification Setup")
    print("=" * 30)
    
    enabled = input("Enable email notifications? (y/n): ").lower().startswith('y')
    
    if not enabled:
        return {"enabled": False}
    
    smtp_server = input("SMTP Server (default: smtp.gmail.com): ").strip() or "smtp.gmail.com"
    smtp_port = input("SMTP Port (default: 587): ").strip() or "587"
    username = input("Email username: ").strip()
    password = getpass.getpass("Email password (or app password): ")
    
    print("\nEnter recipient email addresses (one per line, empty line to finish):")
    recipients = []
    while True:
        email = input("Recipient: ").strip()
        if not email:
            break
        recipients.append(email)
    
    return {
        "enabled": True,
        "smtp_server": smtp_server,
        "smtp_port": int(smtp_port),
        "username": username,
        "password": password,
        "recipients": recipients
    }

def setup_sms_notifications():
    """Setup SMS notification configuration"""
    print("\n📱 SMS Notification Setup")
    print("=" * 30)
    
    enabled = input("Enable SMS notifications? (y/n): ").lower().startswith('y')
    
    if not enabled:
        return {"enabled": False}
    
    print("\nSMS Providers:")
    print("1. Twilio (recommended)")
    print("2. SendGrid")
    
    provider_choice = input("Choose provider (1-2): ").strip()
    
    if provider_choice == "1":
        provider = "twilio"
        account_sid = input("Twilio Account SID: ").strip()
        auth_token = getpass.getpass("Twilio Auth Token: ")
        from_number = input("Twilio Phone Number (e.g., +1234567890): ").strip()
    else:
        provider = "sendgrid"
        account_sid = input("SendGrid API Key: ").strip()
        auth_token = ""
        from_number = input("From Phone Number: ").strip()
    
    print("\nEnter recipient phone numbers (one per line, empty line to finish):")
    recipients = []
    while True:
        phone = input("Phone number (e.g., +1234567890): ").strip()
        if not phone:
            break
        recipients.append(phone)
    
    return {
        "enabled": True,
        "provider": provider,
        "account_sid": account_sid,
        "auth_token": auth_token,
        "from_number": from_number,
        "recipients": recipients
    }

def setup_push_notifications():
    """Setup push notification configuration"""
    print("\n🔔 Push Notification Setup")
    print("=" * 30)
    
    enabled = input("Enable push notifications? (y/n): ").lower().startswith('y')
    
    if not enabled:
        return {"enabled": False}
    
    print("\nPush Services:")
    print("1. Pushover (recommended)")
    print("2. Pushbullet")
    
    service_choice = input("Choose service (1-2): ").strip()
    
    if service_choice == "1":
        service = "pushover"
        print("\nTo get Pushover credentials:")
        print("1. Go to https://pushover.net/")
        print("2. Create an account and get your User Key")
        print("3. Create an application and get the API Token")
        
        api_key = input("Pushover API Token: ").strip()
        user_key = input("Pushover User Key: ").strip()
        device = input("Device name (optional): ").strip() or ""
    else:
        service = "pushbullet"
        print("\nTo get Pushbullet credentials:")
        print("1. Go to https://www.pushbullet.com/")
        print("2. Go to Settings > Access Tokens")
        print("3. Create a new access token")
        
        api_key = input("Pushbullet Access Token: ").strip()
        user_key = ""
        device = ""
    
    return {
        "enabled": True,
        "service": service,
        "api_key": api_key,
        "user_key": user_key,
        "device": device
    }

def setup_discord_notifications():
    """Setup Discord notification configuration"""
    print("\n💬 Discord Notification Setup")
    print("=" * 30)
    
    enabled = input("Enable Discord notifications? (y/n): ").lower().startswith('y')
    
    if not enabled:
        return {"enabled": False}
    
    print("\nTo get Discord webhook URL:")
    print("1. Go to your Discord server")
    print("2. Right-click on the channel where you want notifications")
    print("3. Select 'Edit Channel' > 'Integrations' > 'Webhooks'")
    print("4. Click 'Create Webhook' and copy the URL")
    
    webhook_url = input("Discord Webhook URL: ").strip()
    
    return {
        "enabled": True,
        "webhook_url": webhook_url
    }

def setup_slack_notifications():
    """Setup Slack notification configuration"""
    print("\n💬 Slack Notification Setup")
    print("=" * 30)
    
    enabled = input("Enable Slack notifications? (y/n): ").lower().startswith('y')
    
    if not enabled:
        return {"enabled": False}
    
    print("\nTo get Slack webhook URL:")
    print("1. Go to https://api.slack.com/apps")
    print("2. Create a new app or select existing one")
    print("3. Go to 'Incoming Webhooks' and activate them")
    print("4. Add a webhook to your desired channel")
    print("5. Copy the webhook URL")
    
    webhook_url = input("Slack Webhook URL: ").strip()
    
    return {
        "enabled": True,
        "webhook_url": webhook_url
    }

def main():
    """Main setup function"""
    print("🏒 AJHL Notification System Setup")
    print("=" * 40)
    print("This will help you configure notification channels for when new game data becomes available.")
    
    config = {
        "email": setup_email_notifications(),
        "sms": setup_sms_notifications(),
        "push": setup_push_notifications(),
        "discord": setup_discord_notifications(),
        "slack": setup_slack_notifications(),
        "check_interval_minutes": 30,
        "team_name": "Lloydminster Bobcats",
        "team_id": "21479"
    }
    
    # Ask about check interval
    print("\n⏰ Monitoring Configuration")
    print("=" * 30)
    interval = input("How often should we check for new data? (minutes, default: 30): ").strip()
    if interval.isdigit():
        config["check_interval_minutes"] = int(interval)
    
    # Save configuration
    config_file = "notification_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to {config_file}")
    
    # Show summary
    print("\n📊 Configuration Summary:")
    print("=" * 30)
    
    enabled_channels = []
    if config['email']['enabled']:
        enabled_channels.append(f"📧 Email ({len(config['email']['recipients'])} recipients)")
    if config['sms']['enabled']:
        enabled_channels.append(f"📱 SMS ({len(config['sms']['recipients'])} recipients)")
    if config['push']['enabled']:
        enabled_channels.append(f"🔔 Push ({config['push']['service']})")
    if config['discord']['enabled']:
        enabled_channels.append("💬 Discord")
    if config['slack']['enabled']:
        enabled_channels.append("💬 Slack")
    
    if enabled_channels:
        print("Enabled notification channels:")
        for channel in enabled_channels:
            print(f"  ✅ {channel}")
    else:
        print("❌ No notification channels enabled")
    
    print(f"\n⏰ Check interval: {config['check_interval_minutes']} minutes")
    print(f"🏒 Team: {config['team_name']} (ID: {config['team_id']})")
    
    print("\n🚀 Next steps:")
    print("1. Test your notifications: python ajhl_notification_system.py --test")
    print("2. Start monitoring: python ajhl_notification_system.py --start")
    print("3. Check once: python ajhl_notification_system.py --check")

if __name__ == "__main__":
    main()
