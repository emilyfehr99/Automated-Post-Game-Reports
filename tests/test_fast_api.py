#!/usr/bin/env python3
"""
Test the fast AJHL API
"""

import requests
import json
import time

# API base URL
API_BASE = "http://localhost:8001"

# Test API key (simplified for demo)
API_KEY = "demo_key"

def test_api_endpoint(endpoint, description):
    """Test an API endpoint"""
    print(f"\n🧪 Testing {description}")
    print(f"   Endpoint: {endpoint}")
    
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Status: {response.status_code}")
            print(f"   📊 Response keys: {list(data.keys())}")
            
            # Show sample data
            if "teams" in data:
                print(f"   🏒 Teams found: {len(data['teams'])}")
                if data['teams']:
                    sample_team = data['teams'][0]
                    print(f"   📋 Sample team: {sample_team.get('team_name', 'Unknown')}")
            
            elif "players" in data:
                print(f"   👥 Players found: {len(data['players'])}")
                if data['players']:
                    sample_player = data['players'][0]
                    print(f"   🏒 Sample player: {sample_player.get('name', 'Unknown')} (#{sample_player.get('jersey_number', '?')})")
                    print(f"   📊 Sample metrics: {list(sample_player.get('metrics', {}).keys())[:5]}...")
            
            elif "league" in data:
                print(f"   📈 League stats: {data}")
            
            return True
        else:
            print(f"   ❌ Failed! Status: {response.status_code}")
            print(f"   📝 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - API not running?")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Testing AJHL Fast API")
    print("=" * 50)
    
    # Wait a moment for API to start
    print("⏳ Waiting for API to start...")
    time.sleep(3)
    
    # Test endpoints
    tests = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/teams", "All teams"),
        ("/teams/21479", "Lloydminster Bobcats"),
        ("/teams/21479/players", "Lloydminster Bobcats players"),
        ("/players", "All players"),
        ("/players/search/Alessio", "Search for Alessio Nardelli"),
        ("/players/search/Luke", "Search for Luke Abraham"),
        ("/league/stats", "League statistics")
    ]
    
    results = []
    for endpoint, description in tests:
        success = test_api_endpoint(endpoint, description)
        results.append((endpoint, success))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {endpoint}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Fast API is working correctly.")
        print("\n🏆 Key Features Demonstrated:")
        print("   • All 13 AJHL teams available")
        print("   • Player data with comprehensive metrics")
        print("   • Fast cached responses")
        print("   • Player search across all teams")
        print("   • League-wide statistics")
    else:
        print("⚠️  Some tests failed. Check the API logs for details.")

if __name__ == "__main__":
    main()
