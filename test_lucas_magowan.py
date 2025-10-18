#!/usr/bin/env python3
"""
Test Lucas Magowan specifically
"""

import requests
import json
import time

def test_lucas_magowan():
    """Test specifically for Lucas Magowan"""
    base_url = "http://localhost:8000"
    
    print("🏒 Testing for Lucas Magowan specifically")
    print("=" * 50)
    
    # Test 1: Health Check
    print("🔍 1. API Health Check:")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API Status: {health['status']}")
            print(f"   Hudl Scraper: {health['hudl_scraper']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    print()
    
    # Test 2: Search for Lucas Magowan
    print("🔍 2. Searching for Lucas Magowan:")
    try:
        response = requests.get(f"{base_url}/players/search/Lucas", timeout=30)
        if response.status_code == 200:
            search_data = response.json()
            print(f"✅ Search completed")
            print(f"   Total players found: {search_data['total_players']}")
            
            if search_data['total_players'] > 0:
                print("   Players found:")
                for player in search_data['players']:
                    print(f"     - {player.get('name', 'Unknown')} (#{player.get('jersey', 'N/A')}) - {player.get('position', 'Unknown')} - {player.get('team_name', 'Unknown')}")
            else:
                print("   ⚠️ No players found")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Search error: {e}")
    print()
    
    # Test 3: Search for Magowan
    print("🔍 3. Searching for 'Magowan':")
    try:
        response = requests.get(f"{base_url}/players/search/Magowan", timeout=30)
        if response.status_code == 200:
            search_data = response.json()
            print(f"✅ Search completed")
            print(f"   Total players found: {search_data['total_players']}")
            
            if search_data['total_players'] > 0:
                print("   Players found:")
                for player in search_data['players']:
                    print(f"     - {player.get('name', 'Unknown')} (#{player.get('jersey', 'N/A')}) - {player.get('position', 'Unknown')} - {player.get('team_name', 'Unknown')}")
            else:
                print("   ⚠️ No players found")
        else:
            print(f"❌ Search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search error: {e}")
    print()
    
    # Test 4: Check Lloydminster Bobcats players
    print("🏒 4. Checking Lloydminster Bobcats players:")
    try:
        response = requests.get(f"{base_url}/teams/21479/players", timeout=30)
        if response.status_code == 200:
            players_data = response.json()
            print(f"✅ Team: {players_data['team_name']}")
            print(f"   Total Players: {players_data['total_players']}")
            
            if players_data['total_players'] > 0:
                print("   Players found:")
                for player in players_data['players'][:10]:  # Show first 10
                    print(f"     - {player.get('name', 'Unknown')} (#{player.get('jersey', 'N/A')}) - {player.get('position', 'Unknown')}")
            else:
                print("   ⚠️ No players found")
        else:
            print(f"❌ Team players failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Team players error: {e}")
    print()
    
    print("🎯 Lucas Magowan Test Results:")
    print("✅ API is running")
    print("⚠️ Player data may still be loading or require authentication")

if __name__ == "__main__":
    test_lucas_magowan()
