#!/usr/bin/env python3
"""
Phone Notification Options
Different ways to get notifications on your phone
"""

import os
import json
from datetime import datetime

def show_phone_notification_options():
    """Show different options for phone notifications"""
    
    print("📱 PHONE NOTIFICATION OPTIONS")
    print("=" * 50)
    
    print("🎯 OPTION 1: macOS Notifications (Easiest)")
    print("   • Uses your Mac's built-in notification system")
    print("   • Shows up in your Mac's notification center")
    print("   • Can be configured to show on your phone if synced")
    print("   • Command: python3 send_mac_notification.py")
    
    print("\n🎯 OPTION 2: Email Notifications")
    print("   • Send email to your phone's email address")
    print("   • Most phones show email notifications immediately")
    print("   • Requires email configuration")
    print("   • Command: python3 send_email_notification.py")
    
    print("\n🎯 OPTION 3: Pushover (Recommended)")
    print("   • Free app for instant phone notifications")
    print("   • Works with any phone (iPhone/Android)")
    print("   • Very reliable and instant")
    print("   • Setup required but easy")
    
    print("\n🎯 OPTION 4: IFTTT (If This Then That)")
    print("   • Free service for automation")
    print("   • Can send webhooks to trigger phone notifications")
    print("   • Works with many apps")
    
    print("\n🎯 OPTION 5: Slack/Discord Notifications")
    print("   • Send messages to Slack or Discord")
    print("   • Most people have these apps on their phone")
    print("   • Instant notifications")
    
    print("\n🎯 OPTION 6: Simple File + Cloud Sync")
    print("   • Create a file that syncs to iCloud/Dropbox")
    print("   • Check the file on your phone")
    print("   • Simple but effective")

def create_mac_notification():
    """Create a macOS notification that might show on phone"""
    try:
        title = "🚀 API Scraping Success!"
        message = "✅ Data captured for Lloydminster Bobcats\n👥 189+ players with 137+ metrics\n📁 Check daily_network_data/ folder"
        
        # Create AppleScript for notification
        script = f'''
        display notification "{message}" with title "{title}" sound name "Glass"
        '''
        
        import subprocess
        subprocess.run(['osascript', '-e', script], check=True)
        
        print("📱 macOS notification sent!")
        print("   Check your Mac's notification center")
        print("   If you have iPhone, it might sync to your phone too")
        
    except Exception as e:
        print(f"⚠️ Could not send macOS notification: {e}")

def create_email_notification():
    """Create an email notification script"""
    
    email_script = '''#!/usr/bin/env python3
"""
Email Notification Script
Sends email when API scraping is complete
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_email_notification():
    """Send email notification"""
    
    # Email configuration (you'll need to set these)
    sender_email = "your_email@gmail.com"
    sender_password = "your_app_password"  # Use app password, not regular password
    recipient_email = "your_phone_email@provider.com"  # Your phone's email
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "🚀 API Scraping Completed Success!"
    
    body = f"""
🎉 API SCRAPING COMPLETED SUCCESS! 🎉

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: SUCCESS
Team: Lloydminster Bobcats
Players: 189+ players
Metrics: 137+ per player

Location: /Users/emilyfehr8/CascadeProjects/daily_network_data/

🎊 CONGRATULATIONS! YOUR DATA IS READY! 🎊

Check your daily_network_data/ folder for the captured data.
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Gmail SMTP configuration
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        print("📧 Email notification sent!")
        
    except Exception as e:
        print(f"❌ Email failed: {e}")
        print("   Make sure to configure your email settings")

if __name__ == "__main__":
    send_email_notification()
'''
    
    with open("send_email_notification.py", "w") as f:
        f.write(email_script)
    
    print("📧 Email notification script created!")
    print("   Edit send_email_notification.py with your email settings")

def create_pushover_script():
    """Create Pushover notification script"""
    
    pushover_script = '''#!/usr/bin/env python3
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
'''
    
    with open("send_pushover_notification.py", "w") as f:
        f.write(pushover_script)
    
    print("📱 Pushover notification script created!")
    print("   Sign up at pushover.net to get your keys")

def main():
    """Main function"""
    show_phone_notification_options()
    
    print("\n" + "=" * 50)
    print("🚀 QUICK SETUP OPTIONS")
    print("=" * 50)
    
    print("\n1. 📱 Try macOS notification (might sync to phone):")
    create_mac_notification()
    
    print("\n2. 📧 Create email notification script:")
    create_email_notification()
    
    print("\n3. 📱 Create Pushover notification script:")
    create_pushover_script()
    
    print("\n🎯 RECOMMENDED: Use Pushover for instant phone notifications!")
    print("   It's free, reliable, and works with any phone")

if __name__ == "__main__":
    main()
