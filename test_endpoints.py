#!/usr/bin/env python3
import requests
import json

def test_nhl_endpoints():
    base_url = "https://api-web.nhle.com/v1"
    
    print("🔍 NHL API ENDPOINT EXPLORATION 🔍")
    print("=" * 50)
    
    # Test 1: Team Information
    print("\n1. TEAM INFORMATION (Florida Panthers)")
    print("-" * 40)
    url = f"{base_url}/teams/13"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Team: {data.get('name', 'N/A')}")
        print(f"   Abbreviation: {data.get('abbrev', 'N/A')}")
        print(f"   Conference: {data.get('conferenceName', 'N/A')}")
        print(f"   Division: {data.get('divisionName', 'N/A')}")
        print(f"   Available fields: {list(data.keys())}")
        
        # Show venue info if available
        if 'venue' in data:
            print(f"   Venue: {data['venue'].get('default', 'N/A')}")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    # Test 2: Team Roster
    print("\n2. TEAM ROSTER (Florida Panthers)")
    print("-" * 40)
    url = f"{base_url}/teams/13/roster"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Roster retrieved successfully")
        print(f"   Forwards: {len(data.get('forwards', []))}")
        print(f"   Defensemen: {len(data.get('defensemen', []))}")
        print(f"   Goalies: {len(data.get('goalies', []))}")
        print(f"   Available fields: {list(data.keys())}")
        
        # Show sample player data
        if data.get('forwards'):
            player = data['forwards'][0]
            print(f"   Sample forward: {player.get('name', 'N/A')}")
            print(f"     Position: {player.get('position', 'N/A')}")
            print(f"     Available fields: {list(player.keys())}")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    # Test 3: Team Statistics
    print("\n3. TEAM STATISTICS (Florida Panthers)")
    print("-" * 40)
    url = f"{base_url}/teams/13/stats"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Stats retrieved successfully")
        print(f"   Available fields: {list(data.keys())}")
        if 'stats' in data:
            print(f"   Stats fields: {list(data['stats'].keys())}")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    # Test 4: Schedule
    print("\n4. DAILY SCHEDULE")
    print("-" * 40)
    url = f"{base_url}/schedule/2024-08-18"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Schedule retrieved successfully")
        print(f"   Available fields: {list(data.keys())}")
        if 'gameWeek' in data:
            total_games = sum(len(day.get('games', [])) for day in data['gameWeek'])
            print(f"   Total games today: {total_games}")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    # Test 5: League Standings
    print("\n5. LEAGUE STANDINGS")
    print("-" * 40)
    url = f"{base_url}/standings/now"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Standings retrieved successfully")
        print(f"   Available fields: {list(data.keys())}")
        if 'standings' in data:
            print(f"   Standings entries: {len(data['standings'])}")
    else:
        print(f"❌ Failed: {response.status_code}")

if __name__ == "__main__":
    test_nhl_endpoints()
