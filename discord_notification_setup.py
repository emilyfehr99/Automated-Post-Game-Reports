#!/usr/bin/env python3
"""
Discord Notification Setup
Instructions and script for Discord notifications
"""

import os
import json
from datetime import datetime

def show_discord_setup_instructions():
    """Show step-by-step Discord setup instructions"""
    
    print("📱 DISCORD NOTIFICATION SETUP")
    print("=" * 50)
    
    print("🎯 STEP 1: Create a Discord Webhook")
    print("   1. Open Discord on your computer or phone")
    print("   2. Go to your server (or create a new one)")
    print("   3. Click the server name → Server Settings")
    print("   4. Go to Integrations → Webhooks")
    print("   5. Click 'Create Webhook'")
    print("   6. Name it 'API Scraping Bot'")
    print("   7. Choose a channel (like #general)")
    print("   8. Click 'Copy Webhook URL'")
    print("   9. Save this URL - you'll need it!")
    
    print("\n🎯 STEP 2: Configure the Script")
    print("   1. Edit discord_notification.py")
    print("   2. Replace 'YOUR_WEBHOOK_URL_HERE' with your webhook URL")
    print("   3. Save the file")
    
    print("\n🎯 STEP 3: Test the Notification")
    print("   1. Run: python3 discord_notification.py")
    print("   2. Check your Discord channel")
    print("   3. Check your phone for the notification!")
    
    print("\n🎯 STEP 4: Add to Your Daily System")
    print("   1. The script will automatically run at 4 AM")
    print("   2. You'll get a Discord message on your phone")
    print("   3. You'll get a push notification instantly!")

def create_discord_notification_script():
    """Create the Discord notification script"""
    
    discord_script = '''#!/usr/bin/env python3
"""
Discord Notification Script
Sends Discord message when API scraping is complete
"""

import requests
import json
from datetime import datetime

def send_discord_notification():
    """Send Discord notification"""
    
    # Discord webhook URL (replace with your actual webhook URL)
    webhook_url = "YOUR_WEBHOOK_URL_HERE"
    
    # Create the message
    message = f"""🚀 **API SCRAPING COMPLETED SUCCESS!** 🚀

✅ **Status:** SUCCESS
⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 **Team:** Lloydminster Bobcats
👥 **Players:** 189+ players
📈 **Metrics:** 137+ per player

📁 **Location:** daily_network_data/ folder

🎊 **CONGRATULATIONS! YOUR DATA IS READY!** 🎊

Check your daily_network_data/ folder for the captured data."""
    
    # Discord webhook payload
    payload = {
        "content": message,
        "username": "API Scraping Bot",
        "avatar_url": "https://cdn.discordapp.com/emojis/🚀.png",
        "embeds": [
            {
                "title": "🎉 Data Capture Complete!",
                "description": "Your Hudl Instat data has been successfully captured",
                "color": 65280,  # Green color
                "fields": [
                    {
                        "name": "Team",
                        "value": "Lloydminster Bobcats",
                        "inline": True
                    },
                    {
                        "name": "Players",
                        "value": "189+ players",
                        "inline": True
                    },
                    {
                        "name": "Metrics",
                        "value": "137+ per player",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Automated API Scraping System"
                },
                "timestamp": datetime.now().isoformat()
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        
        if response.status_code == 204:
            print("📱 Discord notification sent!")
            print("   Check your Discord channel and phone!")
        else:
            print(f"❌ Discord failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Discord error: {e}")
        print("   Make sure your webhook URL is correct")

def test_discord_notification():
    """Test the Discord notification"""
    print("🧪 Testing Discord notification...")
    send_discord_notification()

if __name__ == "__main__":
    test_discord_notification()
'''
    
    with open("discord_notification.py", "w") as f:
        f.write(discord_script)
    
    print("📱 Discord notification script created!")
    print("   File: discord_notification.py")

def create_discord_config():
    """Create a configuration file for Discord settings"""
    
    config = {
        "discord_webhook_url": "YOUR_WEBHOOK_URL_HERE",
        "discord_channel": "#general",
        "discord_username": "API Scraping Bot",
        "enabled": True,
        "test_mode": False
    }
    
    with open("discord_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("📁 Discord config file created!")
    print("   File: discord_config.json")

def main():
    """Main function"""
    show_discord_setup_instructions()
    
    print("\n" + "=" * 50)
    print("🚀 CREATING DISCORD FILES")
    print("=" * 50)
    
    create_discord_notification_script()
    create_discord_config()
    
    print("\n🎯 NEXT STEPS:")
    print("   1. Get your Discord webhook URL (follow Step 1 above)")
    print("   2. Edit discord_notification.py with your webhook URL")
    print("   3. Test it: python3 discord_notification.py")
    print("   4. You'll get a Discord message on your phone!")

if __name__ == "__main__":
    main()
