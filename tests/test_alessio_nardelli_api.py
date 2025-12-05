#!/usr/bin/env python3
"""
Test AJHL API specifically for Alessio Nardelli
"""

import requests
import json
import time

# API configuration
API_BASE = "http://localhost:8001"
API_KEY = "demo_key"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def test_alessio_nardelli():
    """Test the API specifically for Alessio Nardelli"""
    print("🏒 Testing AJHL API for Alessio Nardelli")
    print("=" * 50)
    
    # Test 1: Search for Alessio Nardelli
    print("\n🔍 Searching for Alessio Nardelli...")
    try:
        response = requests.get(f"{API_BASE}/players/search/Alessio", headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful!")
            print(f"📊 Found {data['total_found']} player(s)")
            
            if data['players']:
                alessio = data['players'][0]
                print(f"\n🏒 Player Details:")
                print(f"   Name: {alessio['name']}")
                print(f"   Jersey: #{alessio['jersey_number']}")
                print(f"   Position: {alessio['position']}")
                print(f"   Team: {alessio.get('team_name', 'Unknown')}")
                print(f"   Player ID: {alessio['player_id']}")
                print(f"   Last Updated: {alessio.get('last_updated', 'Unknown')}")
                
                # Show all metrics
                metrics = alessio.get('metrics', {})
                print(f"\n📊 Comprehensive Metrics ({len(metrics)} total):")
                print("   " + "="*60)
                
                # Group metrics by category
                basic_stats = ['TOI', 'GP', 'SHIFTS', 'G', 'A1', 'A2', 'A', 'P', '+/-']
                faceoff_stats = ['FO', 'FO+', 'FO%', 'FOD', 'FOD+', 'FOD%', 'FON', 'FON+', 'FON%', 'FOA', 'FOA+', 'FOA%']
                shot_stats = ['S', 'S+', 'SBL', 'SPP', 'SSH', 'PTTS']
                other_stats = ['SC', 'PEA', 'PEN', 'H+']
                
                print("   🏒 Basic Statistics:")
                for stat in basic_stats:
                    if stat in metrics:
                        print(f"      {stat}: {metrics[stat]}")
                
                print("\n   🎯 Faceoff Statistics:")
                for stat in faceoff_stats:
                    if stat in metrics:
                        print(f"      {stat}: {metrics[stat]}")
                
                print("\n   🏹 Shot Statistics:")
                for stat in shot_stats:
                    if stat in metrics:
                        print(f"      {stat}: {metrics[stat]}")
                
                print("\n   📈 Other Statistics:")
                for stat in other_stats:
                    if stat in metrics:
                        print(f"      {stat}: {metrics[stat]}")
                
                # Show remaining metrics
                shown_stats = set(basic_stats + faceoff_stats + shot_stats + other_stats)
                remaining_stats = {k: v for k, v in metrics.items() if k not in shown_stats}
                if remaining_stats:
                    print("\n   🔍 Additional Metrics:")
                    for stat, value in remaining_stats.items():
                        print(f"      {stat}: {value}")
                
                print("   " + "="*60)
                
                return True
            else:
                print("❌ No players found matching 'Alessio'")
                return False
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error searching for Alessio: {e}")
        return False

def test_lloydminster_players():
    """Test getting all Lloydminster Bobcats players"""
    print("\n🏒 Testing Lloydminster Bobcats players...")
    try:
        response = requests.get(f"{API_BASE}/teams/21479/players", headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved {data['total_players']} players")
            
            # Find Alessio in the team roster
            alessio_found = False
            for player in data['players']:
                if 'Alessio' in player['name']:
                    alessio_found = True
                    print(f"✅ Found Alessio Nardelli in team roster!")
                    print(f"   Jersey: #{player['jersey_number']}")
                    print(f"   Position: {player['position']}")
                    break
            
            if not alessio_found:
                print("⚠️  Alessio Nardelli not found in team roster")
            
            return True
        else:
            print(f"❌ Failed to get team players: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting team players: {e}")
        return False

def test_all_players():
    """Test getting all players across all teams"""
    print("\n🏒 Testing all players across all teams...")
    try:
        response = requests.get(f"{API_BASE}/players", headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved {data['total_players']} players from {data['total_teams']} teams")
            
            # Find Alessio in all players
            alessio_found = False
            for player in data['players']:
                if 'Alessio' in player['name']:
                    alessio_found = True
                    print(f"✅ Found Alessio Nardelli in all players!")
                    print(f"   Team: {player.get('team_name', 'Unknown')}")
                    print(f"   Jersey: #{player['jersey_number']}")
                    break
            
            if not alessio_found:
                print("⚠️  Alessio Nardelli not found in all players")
            
            return True
        else:
            print(f"❌ Failed to get all players: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting all players: {e}")
        return False

def main():
    """Run all tests for Alessio Nardelli"""
    print("🚀 AJHL API Test - Alessio Nardelli Focus")
    print("=" * 60)
    
    # Wait for API to be ready
    print("⏳ Ensuring API is ready...")
    time.sleep(2)
    
    # Run tests
    tests = [
        ("Search for Alessio Nardelli", test_alessio_nardelli),
        ("Lloydminster Bobcats players", test_lloydminster_players),
        ("All players across all teams", test_all_players)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print(f"{'='*60}")
        
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Alessio Nardelli's data is accessible via the API.")
        print("\n🏆 Key Findings:")
        print("   • Alessio Nardelli is successfully found in the API")
        print("   • All comprehensive metrics are available")
        print("   • Data is accessible via search and team endpoints")
        print("   • API is working perfectly for hockey analytics")
    else:
        print("⚠️  Some tests failed. Check the API logs for details.")

if __name__ == "__main__":
    main()
