#!/usr/bin/env python3
"""
Test script for Lloydminster Bobcats with Direct Site API
Tests the API using SQL database and direct site data
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

def test_lloydminster_bobcats():
    """Test specifically with Lloydminster Bobcats (team_id: 21479)"""
    print("🏒 Testing Lloydminster Bobcats (Team ID: 21479)")
    print("=" * 60)
    
    # Test health check
    print("\n🏥 Health Check...")
    health = test_api_endpoint("/health")
    if health:
        print(f"Status: {health.get('status', 'Unknown')}")
        print(f"Database available: {health.get('database_available', False)}")
        print(f"Teams in DB: {health.get('teams_in_db', 0)}")
        print(f"Players in DB: {health.get('players_in_db', 0)}")
    
    # Test teams endpoint
    print("\n🏒 All Teams...")
    teams = test_api_endpoint("/teams")
    if teams and teams.get('success'):
        print(f"Total teams: {teams.get('total_teams', 0)}")
        print(f"Teams with data: {teams.get('teams_with_data', 0)}")
        
        # Find Bobcats
        bobcats = None
        for team in teams.get('teams', []):
            if team.get('team_id') == '21479':
                bobcats = team
                break
        
        if bobcats:
            print(f"\n✅ Found Lloydminster Bobcats:")
            print(f"  Team ID: {bobcats.get('team_id')}")
            print(f"  Team Name: {bobcats.get('team_name')}")
            print(f"  City: {bobcats.get('city')}, {bobcats.get('province')}")
            print(f"  Hudl Team ID: {bobcats.get('hudl_team_id')}")
            print(f"  Has Data: {bobcats.get('has_data', False)}")
            print(f"  Data Source: {bobcats.get('data_source', 'Unknown')}")
    
    # Test team details
    print("\n🏒 Bobcats Team Details...")
    details = test_api_endpoint("/teams/21479")
    if details and details.get('success'):
        team = details.get('team', {})
        print(f"Team: {team.get('team_name', 'Unknown')}")
        print(f"City: {team.get('city', 'Unknown')}, {team.get('province', 'Unknown')}")
        print(f"League: {team.get('league', 'Unknown')}")
        print(f"Hudl Team ID: {team.get('hudl_team_id', 'Unknown')}")
        print(f"Active: {team.get('is_active', False)}")
        
        hudl_integration = details.get('hudl_integration', {})
        if hudl_integration:
            print(f"\nHudl Integration:")
            print(f"  Data Source: {hudl_integration.get('real_data_source', 'Unknown')}")
            print(f"  Tabs Available: {', '.join(hudl_integration.get('tabs_available', []))}")
            print(f"  API Endpoints: {', '.join(hudl_integration.get('api_endpoints_used', []))}")
    
    # Test team metrics
    print("\n📊 Bobcats Team Metrics...")
    metrics = test_api_endpoint("/teams/21479/metrics")
    if metrics and metrics.get('success'):
        team = metrics.get('team', {})
        print(f"Team: {team.get('team_name', 'Unknown')}")
        print(f"Data Source: {metrics.get('data_source', 'Unknown')}")
        print(f"Last Updated: {metrics.get('last_updated', 'Unknown')}")
        
        # Skaters metrics
        skaters = metrics.get('metrics', {})
        if skaters:
            print(f"\n📈 Skaters Metrics:")
            print(f"  Total Skaters: {skaters.get('total_skaters', 0)}")
            print(f"  Forwards: {skaters.get('forwards', 0)}")
            print(f"  Defensemen: {skaters.get('defensemen', 0)}")
            print(f"  Total Goals: {skaters.get('total_goals', 0)}")
            print(f"  Total Assists: {skaters.get('total_assists', 0)}")
            print(f"  Total Points: {skaters.get('total_points', 0)}")
            print(f"  Average +/-: {skaters.get('avg_plus_minus', 0)}")
            print(f"  Shot Percentage: {skaters.get('shot_percentage', 0)}%")
            print(f"  Faceoff Percentage: {skaters.get('faceoff_percentage', 0)}%")
            print(f"  Total Hits: {skaters.get('total_hits', 0)}")
            print(f"  Total Blocks: {skaters.get('total_blocks', 0)}")
            print(f"  Total Takeaways: {skaters.get('total_takeaways', 0)}")
            print(f"  Total Giveaways: {skaters.get('total_giveaways', 0)}")
            print(f"  Total PIM: {skaters.get('total_penalty_minutes', 0)}")
        
        # Goalies metrics
        goalies = metrics.get('goalies_metrics', {})
        if goalies:
            print(f"\n🥅 Goalies Metrics:")
            print(f"  Total Goalies: {goalies.get('total_goalies', 0)}")
            print(f"  Save Percentage: {goalies.get('save_percentage', 0)}%")
            print(f"  Goals Against Average: {goalies.get('goals_against_average', 0)}")
            print(f"  Total Wins: {goalies.get('total_wins', 0)}")
            print(f"  Total Losses: {goalies.get('total_losses', 0)}")
            print(f"  OT Losses: {goalies.get('total_ot_losses', 0)}")
            print(f"  Shutouts: {goalies.get('total_shutouts', 0)}")
        
        # Games metrics
        games = metrics.get('games_metrics', {})
        if games:
            print(f"\n🏆 Games Metrics:")
            print(f"  Total Games: {games.get('total_games', 0)}")
            print(f"  Wins: {games.get('wins', 0)}")
            print(f"  Losses: {games.get('losses', 0)}")
            print(f"  OT Losses: {games.get('ot_losses', 0)}")
            print(f"  Win Percentage: {games.get('win_percentage', 0)}%")
            print(f"  Points: {games.get('points', 0)}")
            print(f"  Goals For: {games.get('total_goals_for', 0)}")
            print(f"  Goals Against: {games.get('total_goals_against', 0)}")
            print(f"  Goal Differential: {games.get('goal_differential', 0)}")
    
    # Test league stats
    print("\n🏆 League Stats...")
    league_stats = test_api_endpoint("/league/stats")
    if league_stats and league_stats.get('success'):
        league_data = league_stats.get('league_data', {})
        print(f"League: {league_data.get('league', 'Unknown')}")
        print(f"Data Source: {league_data.get('data_source', 'Unknown')}")
        
        totals = league_data.get('league_totals', {})
        if totals:
            print(f"\nLeague Totals:")
            print(f"  Total Teams: {totals.get('total_teams', 0)}")
            print(f"  Total Goals: {totals.get('total_goals', 0)}")
            print(f"  Total Games: {totals.get('total_games', 0)}")
            print(f"  Avg Goals per Team: {totals.get('avg_goals_per_team', 0)}")
            print(f"  Avg Games per Team: {totals.get('avg_games_per_team', 0)}")
    
    # Test league rankings
    print("\n🏆 League Rankings...")
    rankings = test_api_endpoint("/league/rankings")
    if rankings and rankings.get('success'):
        print(f"Data Source: {rankings.get('data_source', 'Unknown')}")
        print(f"Last Updated: {rankings.get('last_updated', 'Unknown')}")
        
        rankings_data = rankings.get('rankings', {})
        if rankings_data:
            # Points standings
            by_points = rankings_data.get('by_points', [])
            if by_points:
                print(f"\n🥇 Points Standings:")
                for i, team in enumerate(by_points[:5]):
                    print(f"  {i+1}. {team.get('team', 'Unknown')} - {team.get('points', 0)} points ({team.get('wins', 0)}W-{team.get('losses', 0)}L)")
            
            # Goals for
            by_goals_for = rankings_data.get('by_goals_for', [])
            if by_goals_for:
                print(f"\n⚽ Most Goals For:")
                for i, team in enumerate(by_goals_for[:5]):
                    print(f"  {i+1}. {team.get('team', 'Unknown')} - {team.get('goals', 0)} goals")

def main():
    """Run the Bobcats test"""
    print("🧪 Lloydminster Bobcats Direct Site API Test")
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
    
    # Run Bobcats-specific tests
    test_lloydminster_bobcats()
    
    print("\n🎉 Bobcats test completed!")
    print(f"Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
