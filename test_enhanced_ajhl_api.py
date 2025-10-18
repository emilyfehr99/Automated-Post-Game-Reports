#!/usr/bin/env python3
"""
Test script for enhanced AJHL API endpoints
"""

import requests
import json
from datetime import datetime

def test_enhanced_ajhl_api():
    """Test the enhanced AJHL API endpoints"""
    base_url = "http://localhost:8001"
    
    print("🏒 TESTING ENHANCED AJHL API 🏒")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("\n1. ROOT ENDPOINT")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Version: {data.get('version')}")
            print(f"   Available endpoints: {len(data.get('endpoints', {}))}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Enhanced team endpoint
    print("\n2. ENHANCED TEAM ENDPOINT (Lloydminster Bobcats)")
    print("-" * 50)
    try:
        response = requests.get(f"{base_url}/teams/21479", 
                              headers={"Authorization": "Bearer demo_key"})
        if response.status_code == 200:
            data = response.json()
            team = data.get("team", {})
            metrics = data.get("team_metrics", {})
            print(f"✅ Team: {team.get('team_name')}")
            print(f"   Total Points: {metrics.get('total_points')}")
            print(f"   Total Goals: {metrics.get('total_goals')}")
            print(f"   Faceoff %: {metrics.get('faceoff_percentage')}%")
            print(f"   Roster: {metrics.get('total_players')} players")
            
            # Check performance analysis
            perf = data.get("performance_analysis", {})
            top_scorers = perf.get("top_scorers", [])
            if top_scorers:
                print(f"   Top Scorer: {top_scorers[0].get('name')} ({top_scorers[0].get('points')} pts)")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Enhanced league stats
    print("\n3. ENHANCED LEAGUE STATS")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/league/stats", 
                              headers={"Authorization": "Bearer demo_key"})
        if response.status_code == 200:
            data = response.json()
            overview = data.get("overview", {})
            totals = data.get("league_totals", {})
            averages = data.get("league_averages", {})
            
            print(f"✅ Total Teams: {overview.get('total_teams')}")
            print(f"   Total Players: {overview.get('total_players')}")
            print(f"   League Goals: {totals.get('total_goals')}")
            print(f"   League Points: {totals.get('total_points')}")
            print(f"   Avg Goals/Team: {averages.get('avg_goals_per_team')}")
            
            # Check team rankings
            rankings = data.get("team_rankings", {})
            if rankings.get("by_points"):
                top_team = rankings["by_points"][0]
                print(f"   Top Team by Points: {top_team.get('team_name')} ({top_team.get('total_points')} pts)")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Team comparison
    print("\n4. TEAM COMPARISON")
    print("-" * 25)
    try:
        response = requests.get(f"{base_url}/teams/compare/21479/21480", 
                              headers={"Authorization": "Bearer demo_key"})
        if response.status_code == 200:
            data = response.json()
            comparison = data.get("comparison", {})
            team1 = comparison.get("team1", {})
            team2 = comparison.get("team2", {})
            h2h = comparison.get("head_to_head", {})
            
            print(f"✅ {team1.get('team_name')} vs {team2.get('team_name')}")
            print(f"   Points: {team1.get('metrics', {}).get('total_points')} vs {team2.get('metrics', {}).get('total_points')}")
            print(f"   Goals: {team1.get('metrics', {}).get('total_goals')} vs {team2.get('metrics', {}).get('total_goals')}")
            print(f"   Faceoff %: {team1.get('metrics', {}).get('faceoff_percentage')}% vs {team2.get('metrics', {}).get('faceoff_percentage')}%")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Health check
    print("\n5. HEALTH CHECK")
    print("-" * 20)
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"   Cached Teams: {data.get('cached_teams')}")
            print(f"   Cached Players: {data.get('cached_players')}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏒 ENHANCED AJHL API TEST COMPLETE 🏒")

if __name__ == "__main__":
    test_enhanced_ajhl_api()
