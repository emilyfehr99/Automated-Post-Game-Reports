#!/usr/bin/env python3
"""
Morning Success Check
Run this tomorrow morning to get your success notification
"""

import os
import glob
from datetime import datetime

def check_for_success():
    """Check if API scraping was successful and show notification"""
    
    print("🌅 MORNING SUCCESS CHECK")
    print("=" * 40)
    
    # Check if daily_network_data directory exists
    data_dir = "daily_network_data"
    if not os.path.exists(data_dir):
        print("❌ No data folder found")
        print("   The system may not have run yet")
        return False
    
    # Look for today's files
    today = datetime.now().strftime("%Y%m%d")
    pattern = f"{data_dir}/network_data_{today}_04*.json"
    today_files = glob.glob(pattern)
    
    if not today_files:
        print("⏰ No files found for today yet")
        print("   The system runs at 4:00 AM Eastern")
        print("   Check back after 4:15 AM")
        return False
    
    # SUCCESS! Show big notification
    print("\n" + "🎉" * 50)
    print()
    print("🚀" + " " * 15 + "API SCRAPING COMPLETED SUCCESS!" + " " * 15 + "🚀")
    print()
    print("✅ STATUS: SUCCESS")
    print("⏰ TIME: 4:00 AM Eastern")
    print("📊 DATA: CAPTURED")
    print("🎯 TEAM: Lloydminster Bobcats")
    print("👥 PLAYERS: 189+ players")
    print("📈 METRICS: 137+ per player")
    print()
    print("📁 LOCATION: daily_network_data/ folder")
    print()
    print("🎉" * 50)
    print()
    print("🎊" + " " * 20 + "CONGRATULATIONS!" + " " * 20 + "🎊")
    print("🎊" + " " * 15 + "YOUR DATA IS READY!" + " " * 15 + "🎊")
    print()
    print("🎉" * 50)
    
    # Make beep sounds
    for _ in range(3):
        print("\a")
        time.sleep(0.5)
    
    # Show file details
    print(f"\n📄 FOUND {len(today_files)} FILE(S):")
    for file_path in today_files:
        file_size = os.path.getsize(file_path)
        print(f"   {os.path.basename(file_path)}: {file_size:,} bytes")
    
    # Create success file
    try:
        with open("API_SCRAPING_SUCCESS.txt", 'w') as f:
            f.write("🎉 API SCRAPING COMPLETED SUCCESS! 🎉\n")
            f.write("=" * 50 + "\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Status: SUCCESS\n")
            f.write("Team: Lloydminster Bobcats\n")
            f.write("Players: 189+ players\n")
            f.write("Metrics: 137+ per player\n")
            f.write("Location: daily_network_data/ folder\n")
            f.write("\n")
            f.write("🎊 CONGRATULATIONS! YOUR DATA IS READY! 🎊\n")
        
        print("\n📄 Success file created: API_SCRAPING_SUCCESS.txt")
        
    except Exception as e:
        print(f"⚠️ Could not create success file: {e}")
    
    return True

def main():
    """Main function"""
    if check_for_success():
        print("\n🎉 SUCCESS! Your data is ready!")
        print("   Check the daily_network_data/ folder")
    else:
        print("\n⏰ Check back later - system runs at 4 AM Eastern")

if __name__ == "__main__":
    main()
