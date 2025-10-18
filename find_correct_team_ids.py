#!/usr/bin/env python3
"""
Find Correct Team IDs - Test different ESPN team IDs to find the right ones
"""

import requests
import os

def test_team_ids():
    """Test different team IDs to find the correct ones"""
    
    # Let's test a range of team IDs to find Edmonton and Vancouver
    test_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    print("🔍 Testing ESPN team IDs to find Edmonton and Vancouver...")
    print("=" * 60)
    
    working_ids = []
    
    for team_id in test_ids:
        url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{team_id}.png"
        try:
            response = session.get(url, timeout=5)
            if response.status_code == 200 and len(response.content) > 1000:
                working_ids.append(team_id)
                print(f"✅ Team ID {team_id}: Working ({len(response.content)} bytes)")
            else:
                print(f"❌ Team ID {team_id}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Team ID {team_id}: Error - {e}")
    
    print(f"\n📊 Found {len(working_ids)} working team IDs: {working_ids}")
    
    # Now let's download a few and see what they look like
    print("\n🖼️ Downloading sample logos to identify teams...")
    
    for team_id in working_ids[:10]:  # Test first 10 working IDs
        url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{team_id}.png"
        try:
            response = session.get(url, timeout=5)
            if response.status_code == 200:
                filename = f"test_logo_{team_id}.png"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"  Downloaded {filename} ({len(response.content)} bytes)")
        except Exception as e:
            print(f"  Failed to download team ID {team_id}: {e}")

if __name__ == "__main__":
    test_team_ids()
