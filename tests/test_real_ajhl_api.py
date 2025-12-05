#!/usr/bin/env python3
"""
Test script for the AJHL Real Team & League API
Tests the API using actual Hudl Instat data structure
"""

import requests
import json
import time
from datetime import datetime

# API configuration
API_BASE_URL = "http://localhost:8004"
API_KEY = "test_key_123"  # Replace with actual API key

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
            print(f"Response keys: {list(result.keys())}")
            
            # Print specific data based on endpoint
            if "teams" in endpoint:
                if "teams" in result:
                    print(f"Total teams: {result.get('total_teams', 0)}")
                    print(f"Teams with CSV data: {result.get('teams_with_csv_data', 0)}")
                    print(f"Data source: {result.get('data_source', 'Unknown')}")
            elif "metrics" in endpoint:
                print(f"Team: {result.get('team', {}).get('team_name', 'Unknown')}")
                print(f"Data source: {result.get('data_source', 'Unknown')}")
                if 'metrics' in result:
                    metrics = result['metrics']
                    print(f"Key metrics: {list(metrics.keys())}")
            elif "league" in endpoint:
                if "rankings" in result:
                    print(f"Rankings available: {list(result['rankings'].keys())}")
                if "league_totals" in result:
                    totals = result["league_totals"]
                    print(f"League totals: {list(totals.keys())}")
            
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

def test_health_check():
    """Test the health check endpoint"""
    print("\n🏥 Testing Health Check...")
    result = test_api_endpoint("/health")
    
    if result:
        print(f"Status: {result.get('status', 'Unknown')}")
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        print(f"CSV data available: {result.get('csv_data_available', False)}")
        print(f"Teams with data: {result.get('teams_with_data', 0)}")
    
    return result is not None

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🏠 Testing Root Endpoint...")
    result = test_api_endpoint("/")
    
    if result:
        print(f"Message: {result.get('message', 'Unknown')}")
        print(f"Version: {result.get('version', 'Unknown')}")
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        print(f"Features: {len(result.get('features', []))} features available")
        print(f"Hudl tabs: {len(result.get('hudl_tabs_processed', []))} tabs")
    
    return result is not None

def test_teams_endpoint():
    """Test the teams endpoint"""
    print("\n🏒 Testing Teams Endpoint...")
    result = test_api_endpoint("/teams")
    
    if result and result.get('success'):
        teams = result.get('teams', [])
        print(f"Total teams: {len(teams)}")
        
        # Show first few teams
        for i, team in enumerate(teams[:3]):
            print(f"  {i+1}. {team.get('team_name', 'Unknown')} - {team.get('data_source', 'Unknown')}")
        
        if len(teams) > 3:
            print(f"  ... and {len(teams) - 3} more teams")
    
    return result is not None

def test_team_details(team_id: str = "21479"):
    """Test team details endpoint"""
    print(f"\n🏒 Testing Team Details for {team_id}...")
    result = test_api_endpoint(f"/teams/{team_id}")
    
    if result and result.get('success'):
        team = result.get('team', {})
        print(f"Team: {team.get('team_name', 'Unknown')}")
        print(f"City: {team.get('city', 'Unknown')}")
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        
        csv_summary = result.get('csv_data_summary', {})
        if csv_summary:
            print(f"Tabs available: {csv_summary.get('tabs_available', [])}")
            print(f"Last updated: {csv_summary.get('last_updated', 'Unknown')}")
    else:
        print(f"❌ No data available for team {team_id}")
    
    return result is not None

def test_team_metrics(team_id: str = "21479"):
    """Test team metrics endpoint"""
    print(f"\n📊 Testing Team Metrics for {team_id}...")
    result = test_api_endpoint(f"/teams/{team_id}/metrics")
    
    if result and result.get('success'):
        team = result.get('team', {})
        print(f"Team: {team.get('team_name', 'Unknown')}")
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        
        # Show available metrics
        metrics = result.get('metrics', {})
        if metrics:
            print(f"Skaters metrics: {list(metrics.keys())}")
            print(f"  Total skaters: {metrics.get('total_skaters', 0)}")
            print(f"  Total goals: {metrics.get('total_goals', 0)}")
            print(f"  Total points: {metrics.get('total_points', 0)}")
        
        goalies_metrics = result.get('goalies_metrics', {})
        if goalies_metrics:
            print(f"Goalies metrics: {list(goalies_metrics.keys())}")
            print(f"  Total goalies: {goalies_metrics.get('total_goalies', 0)}")
            print(f"  Save percentage: {goalies_metrics.get('save_percentage', 0)}%")
        
        games_metrics = result.get('games_metrics', {})
        if games_metrics:
            print(f"Games metrics: {list(games_metrics.keys())}")
            print(f"  Total games: {games_metrics.get('total_games', 0)}")
            print(f"  Win percentage: {games_metrics.get('win_percentage', 0)}%")
    else:
        print(f"❌ No metrics available for team {team_id}")
    
    return result is not None

def test_league_stats():
    """Test league stats endpoint"""
    print("\n🏆 Testing League Stats...")
    result = test_api_endpoint("/league/stats")
    
    if result and result.get('success'):
        league_data = result.get('league_data', {})
        print(f"League: {league_data.get('league', 'Unknown')}")
        print(f"Data source: {league_data.get('data_source', 'Unknown')}")
        
        league_totals = league_data.get('league_totals', {})
        if league_totals:
            print(f"Total teams: {league_totals.get('total_teams', 0)}")
            print(f"Total goals: {league_totals.get('total_goals', 0)}")
            print(f"Total games: {league_totals.get('total_games', 0)}")
        
        rankings = league_data.get('rankings', {})
        if rankings:
            print(f"Rankings available: {list(rankings.keys())}")
            
            # Show top 3 teams by points
            by_points = rankings.get('by_points', [])
            if by_points:
                print("Top 3 teams by points:")
                for i, team in enumerate(by_points[:3]):
                    print(f"  {i+1}. {team.get('team', 'Unknown')} - {team.get('points', 0)} points")
    
    return result is not None

def test_league_rankings():
    """Test league rankings endpoint"""
    print("\n🏆 Testing League Rankings...")
    result = test_api_endpoint("/league/rankings")
    
    if result and result.get('success'):
        rankings = result.get('rankings', {})
        league_totals = result.get('league_totals', {})
        
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        print(f"Last updated: {result.get('last_updated', 'Unknown')}")
        
        if league_totals:
            print(f"League totals: {list(league_totals.keys())}")
        
        if rankings:
            print(f"Rankings available: {list(rankings.keys())}")
            
            # Show top teams in each category
            for category, teams in rankings.items():
                if teams:
                    print(f"\nTop 3 teams by {category}:")
                    for i, team in enumerate(teams[:3]):
                        team_name = team.get('team', 'Unknown')
                        if category == 'by_points':
                            points = team.get('points', 0)
                            print(f"  {i+1}. {team_name} - {points} points")
                        elif category == 'by_goals_for':
                            goals = team.get('goals', 0)
                            print(f"  {i+1}. {team_name} - {goals} goals")
                        elif category == 'by_goals_against':
                            goals_against = team.get('goals_against', 0)
                            print(f"  {i+1}. {team_name} - {goals_against} goals against")
                        elif category == 'by_win_percentage':
                            win_pct = team.get('win_percentage', 0)
                            print(f"  {i+1}. {team_name} - {win_pct}%")
    
    return result is not None

def test_refresh_data():
    """Test the refresh data endpoint"""
    print("\n🔄 Testing Data Refresh...")
    result = test_api_endpoint("/refresh", method="POST")
    
    if result and result.get('success'):
        print(f"Message: {result.get('message', 'Unknown')}")
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        print(f"Teams processed: {result.get('teams_processed', 0)}")
        print(f"Successful teams: {result.get('successful_teams', 0)}")
        print(f"CSV files downloaded: {result.get('csv_files_downloaded', 0)}")
    else:
        print(f"❌ Refresh failed: {result.get('error', 'Unknown error') if result else 'No response'}")
    
    return result is not None

def main():
    """Run all API tests"""
    print("🧪 AJHL Real Team & League API Test Suite")
    print("=" * 60)
    print(f"Testing API at: {API_BASE_URL}")
    print(f"API Key: {API_KEY}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test results
    test_results = []
    
    # Run tests
    test_results.append(("Health Check", test_health_check()))
    test_results.append(("Root Endpoint", test_root_endpoint()))
    test_results.append(("Teams Endpoint", test_teams_endpoint()))
    test_results.append(("Team Details (21479)", test_team_details("21479")))
    test_results.append(("Team Metrics (21479)", test_team_metrics("21479")))
    test_results.append(("League Stats", test_league_stats()))
    test_results.append(("League Rankings", test_league_rankings()))
    
    # Optional: Test refresh (commented out to avoid actual data download)
    # test_results.append(("Data Refresh", test_refresh_data()))
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 Test Results Summary")
    print(f"{'='*60}")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API server and data availability.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
