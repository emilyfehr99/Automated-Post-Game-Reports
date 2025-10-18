#!/usr/bin/env python3
"""
Get Correct ESPN IDs - Find the correct ESPN team IDs for NHL teams
"""

import requests
import os

def get_correct_espn_team_ids():
    """Get correct ESPN team IDs by testing known team names"""
    
    # Let's try different approaches to find the correct team IDs
    # ESPN might use different ID schemes
    
    # Approach 1: Try team names in URLs
    team_names = [
        'edmonton-oilers',
        'vancouver-canucks', 
        'vegas-golden-knights',
        'washington-capitals',
        'edmonton',
        'vancouver',
        'vegas',
        'washington'
    ]
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    print("🔍 Trying team names in ESPN URLs...")
    print("=" * 50)
    
    for team_name in team_names:
        url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{team_name}.png"
        try:
            response = session.get(url, timeout=5)
            if response.status_code == 200 and len(response.content) > 1000:
                print(f"✅ {team_name}: Working ({len(response.content)} bytes)")
                # Save it to see what it is
                filename = f"test_{team_name.replace('-', '_')}.png"
                with open(filename, 'wb') as f:
                    f.write(response.content)
            else:
                print(f"❌ {team_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {team_name}: Error - {e}")
    
    # Approach 2: Try some common team ID patterns
    print("\n🔍 Trying common team ID patterns...")
    print("=" * 50)
    
    # Common patterns that might work
    test_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    
    for team_id in test_ids:
        url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{team_id}.png"
        try:
            response = session.get(url, timeout=3)
            if response.status_code == 200 and len(response.content) > 1000:
                print(f"✅ ID {team_id}: Working ({len(response.content)} bytes)")
                # Save a few to identify them
                if team_id in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                    filename = f"test_id_{team_id}.png"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
        except Exception as e:
            pass  # Skip errors for speed

if __name__ == "__main__":
    get_correct_espn_team_ids()
