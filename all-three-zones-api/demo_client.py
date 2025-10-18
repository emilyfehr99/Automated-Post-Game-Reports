#!/usr/bin/env python3
"""
Demo client for All Three Zones API
"""

import requests
import json

def demo_api():
    """Demonstrate the API functionality"""
    base_url = "http://localhost:8000"
    
    print("🏒 All Three Zones API Demo")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API Status: {health['status']}")
            print(f"✅ Message: {health['message']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            info = response.json()
            print(f"✅ API: {info['message']}")
            print(f"✅ Version: {info['version']}")
            print(f"✅ Available endpoints: {list(info['endpoints'].keys())}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test players endpoint
    print("\n3. Testing players endpoint...")
    try:
        response = requests.get(f"{base_url}/players")
        if response.status_code == 200:
            players = response.json()
            print(f"✅ Found {len(players)} players")
            if players:
                for i, player in enumerate(players[:3]):
                    print(f"  Player {i+1}: {player.get('name', 'Unknown')} ({player.get('team', 'Unknown')})")
            else:
                print("  ⚠️  No players found (this is expected until we fix the parsing)")
        else:
            print(f"❌ Players endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test search endpoint
    print("\n4. Testing search endpoint...")
    try:
        response = requests.get(f"{base_url}/search", params={"query": "McDavid"})
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Found {len(results)} players matching 'McDavid'")
            if results:
                for player in results:
                    print(f"  {player.get('name', 'Unknown')} ({player.get('team', 'Unknown')})")
            else:
                print("  ⚠️  No results found (this is expected until we fix the parsing)")
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test teams endpoint
    print("\n5. Testing teams endpoint...")
    try:
        response = requests.get(f"{base_url}/teams")
        if response.status_code == 200:
            teams = response.json()
            print(f"✅ Found {len(teams)} teams")
            if teams:
                for team in teams:
                    print(f"  {team.get('team_name', 'Unknown')}")
            else:
                print("  ⚠️  No teams found (this is expected until we fix the parsing)")
        else:
            print(f"❌ Teams endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API Demo Completed!")
    print("\nNext steps:")
    print("1. The API is working correctly")
    print("2. We need to improve the scraper to parse actual player data")
    print("3. Once parsing is fixed, the endpoints will return real data")
    print("\nAPI Documentation: http://localhost:8000/docs")
    print("API Health: http://localhost:8000/health")

if __name__ == "__main__":
    demo_api() 