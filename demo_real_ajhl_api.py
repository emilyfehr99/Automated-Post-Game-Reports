#!/usr/bin/env python3
"""
Demo script for the AJHL Real Team & League API
Shows how to use the API with real Hudl Instat data
"""

import requests
import json
from datetime import datetime

# API configuration
API_BASE_URL = "http://localhost:8004"
API_KEY = "test_key_123"  # Replace with your actual API key

def make_api_request(endpoint: str, method: str = "GET"):
    """Make an API request with proper headers"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def demo_health_check():
    """Demo the health check endpoint"""
    print("🏥 Health Check Demo")
    print("-" * 40)
    
    result = make_api_request("/health")
    if result:
        print(f"Status: {result.get('status', 'Unknown')}")
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        print(f"CSV data available: {result.get('csv_data_available', False)}")
        print(f"Teams with data: {result.get('teams_with_data', 0)}")
        print(f"Cache age: {result.get('cache_age_seconds', 0)} seconds")
    else:
        print("❌ Health check failed")
    
    print()

def demo_teams_overview():
    """Demo the teams overview"""
    print("🏒 Teams Overview Demo")
    print("-" * 40)
    
    result = make_api_request("/teams")
    if result and result.get('success'):
        teams = result.get('teams', [])
        print(f"Total teams: {result.get('total_teams', 0)}")
        print(f"Teams with CSV data: {result.get('teams_with_csv_data', 0)}")
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        
        print("\nTeams with data:")
        for team in teams:
            if team.get('has_csv_data'):
                print(f"  ✅ {team.get('team_name', 'Unknown')} ({team.get('team_id', 'Unknown')})")
            else:
                print(f"  ❌ {team.get('team_name', 'Unknown')} ({team.get('team_id', 'Unknown')}) - No data")
    else:
        print("❌ Failed to get teams data")
    
    print()

def demo_team_details(team_id: str = "21479"):
    """Demo team details for a specific team"""
    print(f"🏒 Team Details Demo - Team {team_id}")
    print("-" * 40)
    
    result = make_api_request(f"/teams/{team_id}")
    if result and result.get('success'):
        team = result.get('team', {})
        print(f"Team: {team.get('team_name', 'Unknown')}")
        print(f"City: {team.get('city', 'Unknown')}, {team.get('province', 'Unknown')}")
        print(f"League: {team.get('league', 'Unknown')}")
        print(f"Hudl Team ID: {team.get('hudl_team_id', 'Unknown')}")
        print(f"Active: {team.get('is_active', False)}")
        
        csv_summary = result.get('csv_data_summary', {})
        if csv_summary:
            print(f"\nData Summary:")
            print(f"  Tabs available: {', '.join(csv_summary.get('tabs_available', []))}")
            print(f"  Last updated: {csv_summary.get('last_updated', 'Unknown')}")
            print(f"  Total tabs with data: {csv_summary.get('total_tabs_with_data', 0)}")
        
        print(f"\nData source: {result.get('data_source', 'Unknown')}")
    else:
        print(f"❌ No data available for team {team_id}")
        if result:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    print()

def demo_team_metrics(team_id: str = "21479"):
    """Demo team metrics for a specific team"""
    print(f"📊 Team Metrics Demo - Team {team_id}")
    print("-" * 40)
    
    result = make_api_request(f"/teams/{team_id}/metrics")
    if result and result.get('success'):
        team = result.get('team', {})
        print(f"Team: {team.get('team_name', 'Unknown')}")
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        print(f"Last updated: {result.get('last_updated', 'Unknown')}")
        
        # Skaters metrics
        metrics = result.get('metrics', {})
        if metrics:
            print(f"\n📈 Skaters Metrics:")
            print(f"  Total skaters: {metrics.get('total_skaters', 0)}")
            print(f"  Forwards: {metrics.get('forwards', 0)}")
            print(f"  Defensemen: {metrics.get('defensemen', 0)}")
            print(f"  Total goals: {metrics.get('total_goals', 0)}")
            print(f"  Total assists: {metrics.get('total_assists', 0)}")
            print(f"  Total points: {metrics.get('total_points', 0)}")
            print(f"  Average +/-: {metrics.get('avg_plus_minus', 0)}")
            print(f"  Shot percentage: {metrics.get('shot_percentage', 0)}%")
            print(f"  Faceoff percentage: {metrics.get('faceoff_percentage', 0)}%")
        
        # Goalies metrics
        goalies_metrics = result.get('goalies_metrics', {})
        if goalies_metrics:
            print(f"\n🥅 Goalies Metrics:")
            print(f"  Total goalies: {goalies_metrics.get('total_goalies', 0)}")
            print(f"  Save percentage: {goalies_metrics.get('save_percentage', 0)}%")
            print(f"  Goals against average: {goalies_metrics.get('goals_against_average', 0)}")
            print(f"  Total wins: {goalies_metrics.get('total_wins', 0)}")
            print(f"  Total losses: {goalies_metrics.get('total_losses', 0)}")
            print(f"  Shutouts: {goalies_metrics.get('total_shutouts', 0)}")
        
        # Games metrics
        games_metrics = result.get('games_metrics', {})
        if games_metrics:
            print(f"\n🏆 Games Metrics:")
            print(f"  Total games: {games_metrics.get('total_games', 0)}")
            print(f"  Wins: {games_metrics.get('wins', 0)}")
            print(f"  Losses: {games_metrics.get('losses', 0)}")
            print(f"  OT Losses: {games_metrics.get('ot_losses', 0)}")
            print(f"  Win percentage: {games_metrics.get('win_percentage', 0)}%")
            print(f"  Points: {games_metrics.get('points', 0)}")
            print(f"  Goal differential: {games_metrics.get('goal_differential', 0)}")
        
        # Faceoffs metrics
        faceoffs_metrics = result.get('faceoffs_metrics', {})
        if faceoffs_metrics:
            print(f"\n🎯 Faceoffs Metrics:")
            print(f"  Total faceoffs: {faceoffs_metrics.get('total_faceoffs', 0)}")
            print(f"  Faceoffs won: {faceoffs_metrics.get('faceoffs_won', 0)}")
            print(f"  Faceoffs lost: {faceoffs_metrics.get('faceoffs_lost', 0)}")
            print(f"  Faceoff percentage: {faceoffs_metrics.get('faceoff_percentage', 0)}%")
    else:
        print(f"❌ No metrics available for team {team_id}")
        if result:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    print()

def demo_league_rankings():
    """Demo league rankings"""
    print("🏆 League Rankings Demo")
    print("-" * 40)
    
    result = make_api_request("/league/rankings")
    if result and result.get('success'):
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        print(f"Last updated: {result.get('last_updated', 'Unknown')}")
        
        rankings = result.get('rankings', {})
        league_totals = result.get('league_totals', {})
        
        if league_totals:
            print(f"\n📊 League Totals:")
            print(f"  Total teams: {league_totals.get('total_teams', 0)}")
            print(f"  Total goals: {league_totals.get('total_goals', 0)}")
            print(f"  Total games: {league_totals.get('total_games', 0)}")
            print(f"  Average goals per team: {league_totals.get('avg_goals_per_team', 0)}")
            print(f"  Average games per team: {league_totals.get('avg_games_per_team', 0)}")
        
        if rankings:
            # Points standings
            by_points = rankings.get('by_points', [])
            if by_points:
                print(f"\n🥇 Points Standings (Top 5):")
                for i, team in enumerate(by_points[:5]):
                    print(f"  {i+1}. {team.get('team', 'Unknown')} - {team.get('points', 0)} points ({team.get('wins', 0)}W-{team.get('losses', 0)}L)")
            
            # Goals for
            by_goals_for = rankings.get('by_goals_for', [])
            if by_goals_for:
                print(f"\n⚽ Most Goals For (Top 5):")
                for i, team in enumerate(by_goals_for[:5]):
                    print(f"  {i+1}. {team.get('team', 'Unknown')} - {team.get('goals', 0)} goals")
            
            # Goals against
            by_goals_against = rankings.get('by_goals_against', [])
            if by_goals_against:
                print(f"\n🛡️  Fewest Goals Against (Top 5):")
                for i, team in enumerate(by_goals_against[:5]):
                    print(f"  {i+1}. {team.get('team', 'Unknown')} - {team.get('goals_against', 0)} goals against")
            
            # Win percentage
            by_win_percentage = rankings.get('by_win_percentage', [])
            if by_win_percentage:
                print(f"\n📈 Best Win Percentage (Top 5):")
                for i, team in enumerate(by_win_percentage[:5]):
                    print(f"  {i+1}. {team.get('team', 'Unknown')} - {team.get('win_percentage', 0)}%")
    else:
        print("❌ Failed to get league rankings")
        if result:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    print()

def demo_data_refresh():
    """Demo data refresh (optional - commented out to avoid actual download)"""
    print("🔄 Data Refresh Demo (Simulated)")
    print("-" * 40)
    print("Note: This would normally download fresh data from Hudl Instat")
    print("Skipping actual refresh to avoid data download...")
    
    # Uncomment the following lines to actually refresh data:
    # result = make_api_request("/refresh", method="POST")
    # if result and result.get('success'):
    #     print(f"Message: {result.get('message', 'Unknown')}")
    #     print(f"Teams processed: {result.get('teams_processed', 0)}")
    #     print(f"Successful teams: {result.get('successful_teams', 0)}")
    #     print(f"CSV files downloaded: {result.get('csv_files_downloaded', 0)}")
    # else:
    #     print("❌ Refresh failed")
    
    print()

def main():
    """Run the demo"""
    print("🎯 AJHL Real Team & League API Demo")
    print("=" * 50)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"API Key: {API_KEY}")
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if API is running
    print("🔍 Checking if API is running...")
    health_result = make_api_request("/health")
    if not health_result:
        print("❌ API is not running or not accessible")
        print("Please start the API server first:")
        print("  python ajhl_real_team_league_api.py")
        return
    
    print("✅ API is running!")
    print()
    
    # Run demos
    demo_health_check()
    demo_teams_overview()
    demo_team_details("21479")  # Lloydminster Bobcats
    demo_team_metrics("21479")
    demo_league_rankings()
    demo_data_refresh()
    
    print("🎉 Demo completed!")
    print(f"Demo finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
