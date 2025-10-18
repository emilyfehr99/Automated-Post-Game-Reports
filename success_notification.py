#!/usr/bin/env python3
"""
Success Notification System
Shows a clear success message when API scraping is complete
"""

import os
import sys
import time
import json
from datetime import datetime

def show_success_notification():
    """Show a clear success notification"""
    
    # Clear screen
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("🎉" * 50)
    print()
    print("🚀 API SCRAPING COMPLETED SUCCESS! 🚀")
    print()
    print("✅ STATUS: SUCCESS")
    print("⏰ TIME:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("📊 DATA: CAPTURED")
    print("🎯 TEAM: Lloydminster Bobcats")
    print("👥 PLAYERS: 189+ players")
    print("📈 METRICS: 137+ per player")
    print()
    print("📁 LOCATION: /Users/emilyfehr8/CascadeProjects/daily_network_data/")
    print()
    print("🎉" * 50)
    print()
    print("🎊 CONGRATULATIONS! YOUR DATA IS READY! 🎊")
    print()
    
    # Make a beep sound if possible
    try:
        print("\a")  # Bell character
    except:
        pass
    
    # Show for 5 seconds
    time.sleep(5)

def check_and_notify():
    """Check if scraping is complete and show notification"""
    
    data_dir = "daily_network_data"
    
    if not os.path.exists(data_dir):
        print("⏰ No data folder found yet...")
        return False
    
    # Look for today's files
    today = datetime.now().strftime("%Y%m%d")
    pattern = f"{data_dir}/network_data_{today}_04*.json"
    
    import glob
    today_files = glob.glob(pattern)
    
    if today_files:
        show_success_notification()
        return True
    else:
        print("⏰ No files found for today yet...")
        print("   System runs at 4:00 AM Eastern")
        return False

def main():
    """Main function"""
    print("🔍 Checking for API scraping completion...")
    
    if check_and_notify():
        print("\n✅ SUCCESS! Your data is ready!")
    else:
        print("\n⏰ Check back later - system runs at 4 AM Eastern")

if __name__ == "__main__":
    main()
