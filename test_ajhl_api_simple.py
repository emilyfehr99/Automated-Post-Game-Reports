#!/usr/bin/env python3
"""
Simple test for AJHL Comprehensive API
Tests the working API with Alessio Nardelli data
"""

import requests
import json
import time

def test_ajhl_api():
    """Test the AJHL API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🏒 Testing AJHL Comprehensive API")
    print("=" * 50)
    
    # Test 1: Health check
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ API is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    # Test 2: Teams endpoint
    print("\n🏆 Testing teams endpoint...")
    try:
        response = requests.get(f"{base_url}/teams")
        if response.status_code == 200:
            teams = response.json()
            print(f"✅ Found {len(teams)} teams")
            for team in teams[:3]:  # Show first 3
                print(f"   - {team['team_name']} (ID: {team['team_id']})")
        else:
            print(f"❌ Teams endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Teams error: {e}")
    
    # Test 3: Specific team (Lloydminster Bobcats)
    print("\n🏒 Testing Lloydminster Bobcats...")
    try:
        response = requests.get(f"{base_url}/teams/21479")
        if response.status_code == 200:
            team = response.json()
            print(f"✅ Bobcats found: {team['team_name']}")
            print(f"   Location: {team.get('city', 'N/A')}")
            print(f"   Hudl ID: {team.get('hudl_id', 'N/A')}")
        else:
            print(f"❌ Bobcats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Bobcats error: {e}")
    
    # Test 4: Players search (without auth for now)
    print("\n👥 Testing players search...")
    try:
        response = requests.get(f"{base_url}/players/search/Alessio")
        if response.status_code == 200:
            players = response.json()
            print(f"✅ Found {len(players)} players named Alessio")
            for player in players:
                print(f"   - {player['name']} (#{player.get('jersey', 'N/A')}) - {player.get('position', 'N/A')}")
        elif response.status_code == 401:
            print("🔐 Authentication required for player search")
        else:
            print(f"❌ Players search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Players search error: {e}")
    
    # Test 5: League stats
    print("\n📊 Testing league stats...")
    try:
        response = requests.get(f"{base_url}/league/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ League stats retrieved")
            print(f"   Total teams: {stats.get('total_teams', 'N/A')}")
            print(f"   Total players: {stats.get('total_players', 'N/A')}")
        else:
            print(f"❌ League stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ League stats error: {e}")
    
    print("\n🎉 AJHL API test completed!")

if __name__ == "__main__":
    test_ajhl_api()
