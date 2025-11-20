"""
Simple Phone Notification System
Uses multiple services to ensure you get notifications
"""

import requests
import json
from datetime import datetime

def send_notification_via_ntfy():
    """Send notification via ntfy.sh (free, no signup required)"""
    try:
        # Get today's predictions
        with open('daily_predictions_20251018.txt', 'r') as f:
            predictions = f.read()
        
        # Send to ntfy.sh (free push notification service)
        message = f"Today's NHL Predictions\n\n{predictions[:500]}..."
        response = requests.post(
            'https://ntfy.sh/nhl-predictions-emily',
            data=message.encode('utf-8'),
            headers={
                'Title': 'NHL Predictions Ready!',
                'Priority': 'high',
                'Tags': 'hockey,ice_hockey'
            }
        )
        
        if response.status_code == 200:
            print("✅ Notification sent via ntfy.sh!")
            print("📱 Check your phone - you should get a push notification!")
            print("🔗 Or visit: https://ntfy.sh/nhl-predictions-emily")
            return True
        else:
            print(f"❌ ntfy.sh failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error with ntfy.sh: {e}")
        return False

def send_notification_via_pushover():
    """Send notification via Pushover (requires free account)"""
    try:
        # You would need to sign up at pushover.net and get tokens
        print("ℹ️  Pushover requires signup at pushover.net")
        return False
    except Exception as e:
        print(f"❌ Error with Pushover: {e}")
        return False

def send_notification_via_telegram():
    """Send notification via Telegram (requires bot setup)"""
    try:
        print("ℹ️  Telegram requires bot setup")
        return False
    except Exception as e:
        print(f"❌ Error with Telegram: {e}")
        return False

def main():
    """Send notification using the best available method"""
    print("📱 SENDING PHONE NOTIFICATION")
    print("=" * 40)
    
    # Try ntfy.sh first (easiest, no signup)
    if send_notification_via_ntfy():
        print("\n🎉 SUCCESS!")
        print("You should have received a push notification on your phone!")
        print("\n📱 To get notifications on your phone:")
        print("1. Install ntfy app from App Store/Google Play")
        print("2. Subscribe to: nhl-predictions-emily")
        print("3. You'll get push notifications for all NHL predictions!")
    else:
        print("\n❌ ntfy.sh failed, trying alternatives...")
        
        # Try other methods
        if send_notification_via_pushover():
            print("✅ Pushover notification sent!")
        elif send_notification_via_telegram():
            print("✅ Telegram notification sent!")
        else:
            print("❌ All notification methods failed")
            print("\n🔧 Manual setup required:")
            print("1. Sign up for a free push notification service")
            print("2. Add credentials to GitHub secrets")
            print("3. Update the workflow")

if __name__ == "__main__":
    main()
