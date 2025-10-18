#!/usr/bin/env python3
"""
Test script for AJHL Teams by Name API
Tests all team name lookups and search functionality
"""

import requests
import json
import time
from datetime import datetime

# API configuration
API_BASE_URL = "http://localhost:8005"
API_KEY = "test_key_123"

def test_api_endpoint(endpoint: str, method: str = "GET", data: dict = None):
    """Test an API endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"\n{'='*60}")
        print(f"Testing: {method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def test_all_teams():
    """Test getting all teams"""
    print("🏒 Testing All Teams...")
    result = test_api_endpoint("/teams")
    if result and result.get('success'):
        teams = result.get('teams', [])
        print(f"Total teams: {result.get('total_teams', 0)}")
        print(f"Teams with data: {result.get('teams_with_data', 0)}")
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        
        print(f"\nAll AJHL Teams:")
        for i, team in enumerate(teams, 1):
            print(f"  {i:2d}. {team.get('team_name', 'Unknown')} ({team.get('team_id', 'Unknown')})")
    return result

def test_team_by_name(team_name: str):
    """Test getting a team by exact name"""
    print(f"\n🏒 Testing Team by Name: '{team_name}'...")
    result = test_api_endpoint(f"/teams/name/{team_name}")
    if result and result.get('success'):
        team = result.get('team', {})
        print(f"Team: {team.get('team_name', 'Unknown')}")
        print(f"City: {team.get('city', 'Unknown')}, {team.get('province', 'Unknown')}")
        print(f"Team ID: {team.get('team_id', 'Unknown')}")
        print(f"Hudl Team ID: {team.get('hudl_team_id', 'Unknown')}")
        print(f"Active: {team.get('is_active', False)}")
        
        hudl_integration = result.get('hudl_integration', {})
        if hudl_integration:
            print(f"Data Source: {hudl_integration.get('real_data_source', 'Unknown')}")
            print(f"Tabs Available: {', '.join(hudl_integration.get('tabs_available', []))}")
    else:
        print(f"❌ Team '{team_name}' not found")
    return result

def test_team_metrics_by_name(team_name: str):
    """Test getting team metrics by name"""
    print(f"\n📊 Testing Team Metrics by Name: '{team_name}'...")
    result = test_api_endpoint(f"/teams/name/{team_name}/metrics")
    if result:
        if result.get('success'):
            print(f"✅ Metrics available for {team_name}")
            # Would show metrics here if data was available
        else:
            print(f"ℹ️  {result.get('message', 'No message')}")
            print(f"Data Source: {result.get('data_source', 'Unknown')}")
            
            next_steps = result.get('next_steps', [])
            if next_steps:
                print(f"Next Steps:")
                for i, step in enumerate(next_steps, 1):
                    print(f"  {i}. {step}")
    return result

def test_search_teams(search_term: str):
    """Test searching teams by partial name"""
    print(f"\n🔍 Testing Team Search: '{search_term}'...")
    result = test_api_endpoint(f"/teams/search/{search_term}")
    if result and result.get('success'):
        teams = result.get('teams', [])
        print(f"Search term: '{result.get('search_term', 'Unknown')}'")
        print(f"Total matches: {result.get('total_matches', 0)}")
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        
        if teams:
            print(f"\nMatching teams:")
            for i, team in enumerate(teams, 1):
                print(f"  {i}. {team.get('team_name', 'Unknown')} ({team.get('team_id', 'Unknown')})")
        else:
            print(f"No teams found matching '{search_term}'")
    else:
        print(f"❌ Search failed for '{search_term}'")
    return result

def test_league_stats():
    """Test league statistics"""
    print("\n🏆 Testing League Stats...")
    result = test_api_endpoint("/league/stats")
    if result and result.get('success'):
        league_data = result.get('league_data', {})
        print(f"League: {league_data.get('league', 'Unknown')}")
        print(f"Data Source: {league_data.get('data_source', 'Unknown')}")
        
        totals = league_data.get('league_totals', {})
        if totals:
            print(f"Total Teams: {totals.get('total_teams', 0)}")
            print(f"Total Goals: {totals.get('total_goals', 0)}")
            print(f"Total Games: {totals.get('total_games', 0)}")
    return result

def main():
    """Run all team name tests"""
    print("🧪 AJHL Teams by Name API Test Suite")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"API Key: {API_KEY}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if API is running
    print("🔍 Checking if API is running...")
    health = test_api_endpoint("/health")
    if not health:
        print("❌ API is not running or not accessible")
        print("Please start the API server first:")
        print("  python ajhl_direct_site_api.py")
        return
    
    print("✅ API is running!")
    print()
    
    # Test all teams
    all_teams_result = test_all_teams()
    
    # Test specific teams by name
    test_teams = [
        "Lloydminster Bobcats",
        "Brooks Bandits", 
        "Okotoks Oilers",
        "Calgary Canucks",
        "Camrose Kodiaks"
    ]
    
    print(f"\n🏒 Testing Specific Teams by Name...")
    for team_name in test_teams:
        test_team_by_name(team_name)
        test_team_metrics_by_name(team_name)
    
    # Test team search functionality
    print(f"\n🔍 Testing Team Search Functionality...")
    search_terms = [
        "Bobcats",
        "Bandits",
        "Oilers", 
        "Canucks",
        "Kodiaks",
        "Eagles",
        "Dragons",
        "Storm",
        "Grizzlys",
        "Crusaders",
        "Saints",
        "Wolverines"
    ]
    
    for search_term in search_terms:
        test_search_teams(search_term)
    
    # Test league stats
    test_league_stats()
    
    print(f"\n🎉 All team name tests completed!")
    print(f"Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
