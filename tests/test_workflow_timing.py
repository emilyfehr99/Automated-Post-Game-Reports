"""
Test script to verify workflow timing logic
"""

import pytz
from datetime import datetime

def test_daily_predictions_timing():
    """Test daily predictions workflow timing"""
    print("🕐 DAILY PREDICTIONS WORKFLOW TIMING TEST")
    print("=" * 50)
    
    ct = pytz.timezone('US/Central')
    now_ct = datetime.now(ct)
    
    print(f"Current Central Time: {now_ct.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Hour: {now_ct.hour}, Minute: {now_ct.minute}")
    
    # Check if within 6:00-6:29 AM window
    is_within_window = (now_ct.hour == 6 and now_ct.minute < 30)
    
    print(f"\\n📋 DAILY PREDICTIONS LOGIC:")
    print(f"Should run between 6:00-6:29 AM CT")
    print(f"Current time: {now_ct.hour:02d}:{now_ct.minute:02d}")
    print(f"Within window: {is_within_window}")
    
    if is_within_window:
        print("✅ SHOULD RUN - within 6:00-6:29 AM window")
    else:
        print("❌ SHOULD NOT RUN - outside 6:00-6:29 AM window")
        print("   (This explains why it failed with exit code 78)")

def test_auto_post_timing():
    """Test auto post reports workflow timing"""
    print("\\n🕐 AUTO POST REPORTS WORKFLOW TIMING TEST")
    print("=" * 50)
    
    ct = pytz.timezone('US/Central')
    now_ct = datetime.now(ct)
    
    print(f"Current Central Time: {now_ct.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Hour: {now_ct.hour}, Day of week: {now_ct.weekday() + 1}")
    
    # Check skip logic
    is_weekday = now_ct.weekday() + 1 <= 5  # Monday=1, Friday=5
    is_skip_hours = 2 <= now_ct.hour < 15   # 2am to 3pm
    should_skip = is_weekday and is_skip_hours
    
    print(f"\\n📋 AUTO POST REPORTS LOGIC:")
    print(f"Skip if weekday (1-5) AND between 2am-3pm")
    print(f"Is weekday: {is_weekday}")
    print(f"Is skip hours (2am-3pm): {is_skip_hours}")
    print(f"Should skip: {should_skip}")
    
    if should_skip:
        print("⏸️  SHOULD SKIP - weekday off-hours")
    else:
        print("✅ SHOULD RUN - outside skip window")

def main():
    """Main test function"""
    test_daily_predictions_timing()
    test_auto_post_timing()
    
    print("\\n🎯 SUMMARY:")
    print("Daily predictions failed because it ran at 7:17 AM CT")
    print("(outside the 6:00-6:29 AM window)")
    print("Auto post reports should skip at 7:17 AM CT on weekdays")
    print("(within the 2am-3pm skip window)")

if __name__ == "__main__":
    main()
