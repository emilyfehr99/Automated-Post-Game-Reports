#!/usr/bin/env python3
"""
AJHL System Startup Script
Easy way to start the complete AJHL data collection and notification system
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    print("🔍 Checking requirements...")
    
    try:
        import selenium
        import requests
        import schedule
        print("✅ Core requirements found")
        return True
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        print("📦 Installing requirements...")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "ajhl_requirements.txt"], check=True)
            print("✅ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements")
            return False

def check_credentials():
    """Check if credentials file exists"""
    print("🔐 Checking credentials...")
    
    if not Path("hudl_credentials.py").exists():
        print("❌ hudl_credentials.py not found")
        print("📝 Creating template credentials file...")
        
        template = '''# Hudl Instat Credentials
# Replace with your actual credentials

HUDL_USERNAME = "your_username_here"
HUDL_PASSWORD = "your_password_here"
'''
        
        with open("hudl_credentials.py", "w") as f:
            f.write(template)
        
        print("📄 Created hudl_credentials.py template")
        print("⚠️  Please edit hudl_credentials.py with your actual credentials")
        return False
    else:
        print("✅ Credentials file found")
        return True

def check_notification_config():
    """Check if notification config exists"""
    print("🔔 Checking notification configuration...")
    
    if not Path("notification_config.json").exists():
        print("❌ notification_config.json not found")
        print("📝 Run setup to configure notifications: python setup_notifications.py")
        return False
    else:
        print("✅ Notification configuration found")
        return True

def show_menu():
    """Show main menu"""
    print("\n🏒 AJHL Data Collection & Notification System")
    print("=" * 50)
    print("1. Setup notification channels")
    print("2. Run full analysis with notifications")
    print("3. Start continuous monitoring")
    print("4. Test notification system")
    print("5. Generate dashboard")
    print("6. Show system status")
    print("7. Download Lloydminster data only")
    print("8. Get upcoming opponents list")
    print("9. Exit")
    print("=" * 50)

def main():
    """Main startup function"""
    print("🚀 Starting AJHL System...")
    
    # Check requirements
    if not check_requirements():
        print("❌ System check failed. Please install requirements manually.")
        return
    
    # Check credentials
    if not check_credentials():
        print("❌ Please configure credentials and run again.")
        return
    
    # Check notification config
    notification_configured = check_notification_config()
    
    while True:
        show_menu()
        
        try:
            choice = input("\nSelect an option (1-9): ").strip()
            
            if choice == "1":
                print("\n⚙️ Setting up notification channels...")
                subprocess.run([sys.executable, "setup_notifications.py"])
                notification_configured = True
            
            elif choice == "2":
                if not notification_configured:
                    print("❌ Please setup notifications first (option 1)")
                    continue
                print("\n🏒 Running full analysis with notifications...")
                subprocess.run([sys.executable, "ajhl_complete_system_with_notifications.py", "--full"])
            
            elif choice == "3":
                if not notification_configured:
                    print("❌ Please setup notifications first (option 1)")
                    continue
                print("\n🚀 Starting continuous monitoring...")
                print("Press Ctrl+C to stop monitoring")
                try:
                    subprocess.run([sys.executable, "ajhl_complete_system_with_notifications.py", "--monitor"])
                except KeyboardInterrupt:
                    print("\n🛑 Monitoring stopped")
            
            elif choice == "4":
                if not notification_configured:
                    print("❌ Please setup notifications first (option 1)")
                    continue
                print("\n🧪 Testing notification system...")
                subprocess.run([sys.executable, "ajhl_complete_system_with_notifications.py", "--test"])
            
            elif choice == "5":
                print("\n📊 Generating dashboard...")
                subprocess.run([sys.executable, "ajhl_complete_system_with_notifications.py", "--dashboard"])
            
            elif choice == "6":
                print("\n📊 System Status:")
                subprocess.run([sys.executable, "ajhl_complete_system_with_notifications.py", "--status"])
            
            elif choice == "7":
                print("\n📥 Downloading Lloydminster data...")
                subprocess.run([sys.executable, "ajhl_complete_opponent_system.py", "--lloydminster"])
            
            elif choice == "8":
                print("\n📅 Getting upcoming opponents...")
                subprocess.run([sys.executable, "ajhl_complete_opponent_system.py", "--opponents"])
            
            elif choice == "9":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid option. Please select 1-9.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
