#!/usr/bin/env python3
"""
Test Discord Webhook - Find Your Channel
This will help you find where the Discord notifications are being sent
"""

import requests
import json
from datetime import datetime

def test_discord_webhook():
    """Test Discord webhook and help you find the channel"""
    
    print("🔍 DISCORD WEBHOOK TEST")
    print("=" * 50)
    
    # Your Discord webhook URL
    webhook_url = "https://discord.com/api/webhooks/1417616260958785667/2QvzAvVoVnU3gY-_xYwTWwMsiBM4osXmI9n46n40wA5ZIVJEUyxGB-FxZ_Zx_DMF1EaT"
    
    print("📋 WEBHOOK INFORMATION:")
    print(f"   • Server ID: 1417616184475390034")
    print(f"   • Webhook ID: 1417616260958785667")
    print(f"   • This webhook sends to a specific channel in your Discord server")
    print()
    
    # Test message with clear instructions
    message = f"""🔔 **DISCORD NOTIFICATION TEST** 🔔

**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a test message from your NHL Predictions system!

**If you can see this message:**
✅ Discord notifications are working!
✅ You found the right channel!

**If you can't see this message:**
❌ Check other channels in your Discord server
❌ Look for a channel named 'nhl-predictions' or similar
❌ Check if you have notifications disabled

**Next Steps:**
1. Look for this message in your Discord server
2. If you find it, the daily predictions will work!
3. If you don't find it, we need to create a new webhook"""

    payload = {
        "content": message,
        "username": "NHL Predictions Bot",
        "embeds": [
            {
                "title": "🧪 Discord Test Message",
                "description": "Testing if you can see Discord notifications",
                "color": 16776960,  # Yellow
                "fields": [
                    {
                        "name": "Status",
                        "value": "✅ Working!",
                        "inline": True
                    },
                    {
                        "name": "Time",
                        "value": datetime.now().strftime('%H:%M:%S'),
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "NHL Predictions System"
                }
            }
        ]
    }
    
    try:
        print("📤 Sending test message to Discord...")
        response = requests.post(webhook_url, json=payload)
        
        if response.status_code == 204:
            print("✅ Test message sent successfully!")
            print()
            print("🔍 WHERE TO LOOK:")
            print("   1. Open your Discord app")
            print("   2. Go to your server (ID: 1417616184475390034)")
            print("   3. Look for a channel with the test message")
            print("   4. Check if you get a phone notification")
            print()
            print("📱 NOTIFICATION TIPS:")
            print("   • Make sure Discord notifications are enabled on your phone")
            print("   • Check your phone's notification settings for Discord")
            print("   • The message should appear in the channel where the webhook was created")
            
        else:
            print(f"❌ Test message failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error sending test message: {e}")

if __name__ == "__main__":
    test_discord_webhook()
