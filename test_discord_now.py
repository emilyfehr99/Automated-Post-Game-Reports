#!/usr/bin/env python3
"""
Test Discord Notification Right Now
Quick test to see if Discord notifications work
"""

import requests
import json
from datetime import datetime

def test_discord_notification():
    """Test Discord notification with a simple message"""
    
    print("📱 TESTING DISCORD NOTIFICATION")
    print("=" * 40)
    
    # Your Discord webhook URL
    webhook_url = "https://discord.com/api/webhooks/1417616260958785667/2QvzAvVoVnU3gY-_xYwTWwMsiBM4osXmI9n46n40wA5ZIVJEUyxGB-FxZ_Zx_DMF1EaT"
    
    # Webhook URL is already configured!
    
    # Simple test message
    message = f"""🧪 **TEST MESSAGE** 🧪

This is a test from your API scraping system!

⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 **Team:** Lloydminster Bobcats
👥 **Players:** 189+ players
📈 **Metrics:** 137+ per player

If you see this message, Discord notifications are working! 🎉"""
    
    # Discord webhook payload
    payload = {
        "content": message,
        "username": "Instat API Notification",
        "embeds": [
            {
                "title": "🧪 Test Notification",
                "description": "Testing Discord notifications for API scraping",
                "color": 16776960,  # Yellow color
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
                    "text": "API Scraping Test"
                }
            }
        ]
    }
    
    try:
        print("📤 Sending test message to Discord...")
        response = requests.post(webhook_url, json=payload)
        
        if response.status_code == 204:
            print("✅ Discord test message sent!")
            print("   Check your Discord channel and phone!")
            print("   You should get a push notification!")
        else:
            print(f"❌ Discord failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Discord error: {e}")
        print("   Make sure your webhook URL is correct")

def main():
    """Main function"""
    test_discord_notification()
    
    print("\n🎯 NEXT STEPS:")
    print("   1. If test worked: Great! You're all set!")
    print("   2. If test failed: Check your webhook URL")
    print("   3. Once working: Add to your daily 4 AM system")

if __name__ == "__main__":
    main()
