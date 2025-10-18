#!/usr/bin/env python3
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
