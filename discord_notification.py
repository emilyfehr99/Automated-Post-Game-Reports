#!/usr/bin/env python3
"""
Discord Notification Script
Sends Discord message when API scraping is complete
"""

import requests
import json
from datetime import datetime

def send_discord_notification(title="🚀 API SCRAPING COMPLETED SUCCESS! 🚀", message="✅ **Status:** SUCCESS"):
    """Send Discord notification"""
    
    # Discord webhook URL (replace with your actual webhook URL)
    webhook_url = "https://discord.com/api/webhooks/1417616260958785667/2QvzAvVoVnU3gY-_xYwTWwMsiBM4osXmI9n46n40wA5ZIVJEUyxGB-FxZ_Zx_DMF1EaT"
    
    # Create the message
    full_message = f"""**{title}**

{message}
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
        "username": "Instat API Notification",
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
