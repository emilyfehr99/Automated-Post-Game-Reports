"""
Setup Daily NHL Prediction Notifications
Helps configure email and Discord notifications
"""

import os
import json
from pathlib import Path

def setup_email_notifications():
    """Setup email notifications"""
    print("📧 EMAIL NOTIFICATION SETUP")
    print("=" * 40)
    
    email = input("Enter your email address: ").strip()
    if not email:
        print("❌ Email address required")
        return False
    
    print("\nFor Gmail:")
    print("1. Enable 2-factor authentication")
    print("2. Generate an App Password:")
    print("   - Go to Google Account settings")
    print("   - Security → 2-Step Verification → App passwords")
    print("   - Generate password for 'Mail'")
    
    app_password = input("\nEnter your Gmail App Password: ").strip()
    if not app_password:
        print("❌ App password required")
        return False
    
    print(f"\n✅ Email configured for: {email}")
    print("\nTo set up in GitHub Actions:")
    print("1. Go to your repository settings")
    print("2. Go to Secrets and variables → Actions")
    print("3. Add these secrets:")
    print(f"   - NOTIFICATION_EMAIL: {email}")
    print(f"   - EMAIL_USER: {email}")
    print(f"   - EMAIL_PASSWORD: {app_password}")
    
    return True

def setup_discord_notifications():
    """Setup Discord notifications"""
    print("\n💬 DISCORD NOTIFICATION SETUP")
    print("=" * 40)
    
    print("To set up Discord notifications:")
    print("1. Go to your Discord server")
    print("2. Go to Server Settings → Integrations → Webhooks")
    print("3. Click 'New Webhook'")
    print("4. Choose a channel (e.g., #nhl-predictions)")
    print("5. Copy the webhook URL")
    
    webhook_url = input("\nEnter Discord webhook URL (or press Enter to skip): ").strip()
    if not webhook_url:
        print("ℹ️  Discord notifications skipped")
        return False
    
    print(f"\n✅ Discord webhook configured")
    print("\nTo set up in GitHub Actions:")
    print("1. Go to your repository settings")
    print("2. Go to Secrets and variables → Actions")
    print("3. Add this secret:")
    print(f"   - DISCORD_WEBHOOK_URL: {webhook_url}")
    
    return True

def test_notifications():
    """Test the notification setup"""
    print("\n🧪 TESTING NOTIFICATIONS")
    print("=" * 40)
    
    try:
        from daily_prediction_notifier import DailyPredictionNotifier
        notifier = DailyPredictionNotifier()
        
        # Test file output
        print("Testing file output...")
        if notifier.save_to_file("test_predictions.txt"):
            print("✅ File output works")
        
        # Test email if configured
        email = os.getenv('NOTIFICATION_EMAIL')
        if email:
            print(f"Testing email to {email}...")
            if notifier.send_email_notification(email, "Test NHL Predictions"):
                print("✅ Email works")
            else:
                print("❌ Email failed")
        else:
            print("ℹ️  Email not configured (set NOTIFICATION_EMAIL)")
        
        # Test Discord if configured
        discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        if discord_webhook:
            print("Testing Discord webhook...")
            if notifier.send_discord_notification(discord_webhook):
                print("✅ Discord works")
            else:
                print("❌ Discord failed")
        else:
            print("ℹ️  Discord not configured (set DISCORD_WEBHOOK_URL)")
            
    except Exception as e:
        print(f"❌ Error testing notifications: {e}")

def main():
    """Main setup function"""
    print("🔔 DAILY NHL PREDICTIONS NOTIFICATION SETUP")
    print("=" * 50)
    print("This will help you set up daily notifications for NHL game predictions.")
    print("You can receive predictions via email, Discord, or both.")
    print()
    
    # Setup email
    setup_email = input("Do you want to set up email notifications? (y/n): ").lower().strip()
    if setup_email == 'y':
        setup_email_notifications()
    
    # Setup Discord
    setup_discord = input("\nDo you want to set up Discord notifications? (y/n): ").lower().strip()
    if setup_discord == 'y':
        setup_discord_notifications()
    
    print("\n" + "=" * 50)
    print("🎯 NEXT STEPS:")
    print("1. Add the secrets to your GitHub repository")
    print("2. The daily workflow will run at 8:00 AM Central Time")
    print("3. You'll receive predictions every morning")
    print("4. You can also run manually: python3 daily_prediction_notifier.py")
    
    # Test if environment variables are set
    if os.getenv('NOTIFICATION_EMAIL') or os.getenv('DISCORD_WEBHOOK_URL'):
        test_setup = input("\nDo you want to test the notifications now? (y/n): ").lower().strip()
        if test_setup == 'y':
            test_notifications()

if __name__ == "__main__":
    main()
