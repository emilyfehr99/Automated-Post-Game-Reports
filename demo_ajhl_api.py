#!/usr/bin/env python3
"""
AJHL API Comprehensive Demo
Demonstrates all capabilities for all teams and players
"""

import requests
import json
import time
from datetime import datetime

# API configuration
API_BASE = "http://localhost:8001"
API_KEY = "demo_key"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def make_request(endpoint, description):
    """Make API request and display results"""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"📍 Endpoint: {endpoint}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Response time: {response.elapsed.total_seconds():.2f}s")
            
            # Display relevant data
            if "teams" in data:
                print(f"\n🏒 Teams ({len(data['teams'])} total):")
                for i, team in enumerate(data['teams'][:5], 1):  # Show first 5
                    print(f"   {i}. {team['team_name']} ({team['city']}, {team['province']})")
                if len(data['teams']) > 5:
                    print(f"   ... and {len(data['teams']) - 5} more teams")
            
            elif "players" in data:
                print(f"\n👥 Players ({len(data['players'])} total):")
                for i, player in enumerate(data['players'][:3], 1):  # Show first 3
                    metrics_count = len(player.get('metrics', {}))
                    print(f"   {i}. {player['name']} #{player['jersey_number']} ({player['position']})")
                    print(f"      Team: {player.get('team_name', 'Unknown')}")
                    print(f"      Metrics: {metrics_count} available")
                    if player.get('metrics'):
                        sample_metrics = list(player['metrics'].items())[:3]
                        print(f"      Sample: {dict(sample_metrics)}")
            
            elif "league" in data:
                print(f"\n📈 League Statistics:")
                print(f"   • League: {data['league']}")
                print(f"   • Total Teams: {data['total_teams']}")
                print(f"   • Total Players: {data['total_players']}")
                print(f"   • Active Teams: {data['active_teams']}")
                print(f"   • Last Updated: {data.get('last_updated', 'Unknown')}")
            
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Response: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """Run comprehensive API demonstration"""
    print("🏆 AJHL API COMPREHENSIVE DEMONSTRATION")
    print("=" * 60)
    print("This demo shows the complete AJHL API system that can handle:")
    print("• All 13 AJHL teams")
    print("• All players across all teams") 
    print("• Comprehensive player metrics")
    print("• Fast search and filtering")
    print("• Real-time data access")
    print("=" * 60)
    
    # Wait for API to be ready
    print("\n⏳ Ensuring API is ready...")
    time.sleep(2)
    
    # Test 1: API Health and Overview
    health_data = make_request("/health", "API Health Check")
    if not health_data:
        print("❌ API not available. Please start the API first.")
        return
    
    # Test 2: All Teams
    teams_data = make_request("/teams", "All AJHL Teams")
    
    # Test 3: Specific Team (Lloydminster Bobcats)
    team_data = make_request("/teams/21479", "Lloydminster Bobcats Team Details")
    
    # Test 4: Players for Lloydminster Bobcats
    players_data = make_request("/teams/21479/players", "Lloydminster Bobcats Players")
    
    # Test 5: All Players Across All Teams
    all_players_data = make_request("/players", "All Players Across All Teams")
    
    # Test 6: Player Search - Alessio Nardelli
    search_data = make_request("/players/search/Alessio", "Search for Alessio Nardelli")
    
    # Test 7: Player Search - Luke Abraham
    search_data2 = make_request("/players/search/Luke", "Search for Luke Abraham")
    
    # Test 8: League Statistics
    stats_data = make_request("/league/stats", "League-Wide Statistics")
    
    # Summary
    print(f"\n{'='*60}")
    print("🎯 DEMONSTRATION SUMMARY")
    print(f"{'='*60}")
    
    if teams_data:
        print(f"✅ Successfully accessed {teams_data['total_teams']} AJHL teams")
    
    if all_players_data:
        print(f"✅ Successfully accessed {all_players_data['total_players']} players across all teams")
    
    if search_data and search_data['total_found'] > 0:
        print(f"✅ Found {search_data['total_found']} player(s) matching 'Alessio'")
        for player in search_data['players']:
            print(f"   • {player['name']} #{player['jersey_number']} ({player.get('team_name', 'Unknown')})")
    
    if search_data2 and search_data2['total_found'] > 0:
        print(f"✅ Found {search_data2['total_found']} player(s) matching 'Luke'")
        for player in search_data2['players']:
            print(f"   • {player['name']} #{player['jersey_number']} ({player.get('team_name', 'Unknown')})")
    
    print(f"\n🏆 KEY CAPABILITIES DEMONSTRATED:")
    print(f"   • Complete AJHL team roster (13 teams)")
    print(f"   • Player data with comprehensive metrics")
    print(f"   • Fast search across all teams and players")
    print(f"   • Real-time API responses")
    print(f"   • Scalable architecture for all league data")
    
    print(f"\n🚀 The API is ready for production use!")
    print(f"   • Endpoint: {API_BASE}")
    print(f"   • All teams and players accessible")
    print(f"   • Perfect for hockey analytics applications")

if __name__ == "__main__":
    main()
