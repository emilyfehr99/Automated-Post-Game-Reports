#!/usr/bin/env python3
"""
Pushover Notification Script
Sends push notification to your phone via Pushover
"""

import requests
import json
from datetime import datetime

def send_pushover_notification():
    """Send Pushover notification"""
    
    # Pushover configuration (you'll need to get these from pushover.net)
    user_key = "your_user_key_here"
    api_token = "your_api_token_here"
    
    message = f"""🚀 API Scraping Completed Success!

✅ Status: SUCCESS
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Team: Lloydminster Bobcats
👥 Players: 189+ players
📈 Metrics: 137+ per player

📁 Location: daily_network_data/ folder

🎊 CONGRATULATIONS! YOUR DATA IS READY! 🎊"""
    
    data = {
        "token": api_token,
        "user": user_key,
        "message": message,
        "title": "API Scraping Success!",
        "sound": "pushover"
    }
    
    try:
        response = requests.post("https://api.pushover.net/1/messages.json", data=data)
        
        if response.status_code == 200:
            print("📱 Pushover notification sent!")
            print("   Check your phone for the notification")
        else:
            print(f"❌ Pushover failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Pushover error: {e}")
        print("   Make sure to configure your Pushover settings")

if __name__ == "__main__":
    send_pushover_notification()
