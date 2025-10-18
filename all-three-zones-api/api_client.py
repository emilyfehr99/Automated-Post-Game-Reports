#!/usr/bin/env python3
"""
Simple API Client for All Three Zones API
Demonstrates how to use the API to get player data
"""

import requests
import json
from typing import Dict, List, Any

class AllThreeZonesClient:
    """Client for All Three Zones API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def search_players(self, query: str) -> List[Dict[str, Any]]:
        """Search for players by query"""
        try:
            response = requests.get(f"{self.base_url}/search", params={"query": query})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error searching players: {e}")
            return []
    
    def get_player(self, player_name: str) -> Dict[str, Any]:
        """Get specific player data"""
        try:
            response = requests.get(f"{self.base_url}/players/{player_name}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting player {player_name}: {e}")
            return {}
    
    def get_all_players(self) -> List[Dict[str, Any]]:
        """Get all players"""
        try:
            response = requests.get(f"{self.base_url}/players")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting all players: {e}")
            return []
    
    def get_teams(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all teams and their players"""
        try:
            response = requests.get(f"{self.base_url}/teams")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting teams: {e}")
            return {}
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False

def print_player_stats(player: Dict[str, Any]):
    """Pretty print player statistics"""
    print(f"\n🏒 {player['name']} ({player['team']}) - {player['position']}")
    print("=" * 60)
    
    if '5v5_toi' in player:
        print(f"5v5 Time on Ice: {player['5v5_toi']} minutes")
    
    stats = player.get('stats', {})
    
    # General Offense
    if 'general_offense' in stats:
        print("\n📊 General Offense (per 60 minutes):")
        for stat, value in stats['general_offense'].items():
            print(f"  {stat.replace('_', ' ').title()}: {value}")
    
    # Passing
    if 'passing' in stats:
        print("\n🎯 Passing:")
        for stat, value in stats['passing'].items():
            print(f"  {stat.replace('_', ' ').title()}: {value}")
    
    # Offense Types
    if 'offense_types' in stats:
        print("\n⚡ Offense Types (per 60 minutes):")
        for stat, value in stats['offense_types'].items():
            print(f"  {stat.replace('_', ' ').title()}: {value}")
    
    # Zone Entries
    if 'zone_entries' in stats:
        print("\n🚪 Zone Entries:")
        for stat, value in stats['zone_entries'].items():
            if 'percent' in stat:
                print(f"  {stat.replace('_', ' ').title()}: {value:.1%}")
            else:
                print(f"  {stat.replace('_', ' ').title()}: {value}")
    
    # DZ Retrievals & Exits
    if 'dz_retrievals_exits' in stats:
        print("\n🔄 DZ Retrievals & Exits:")
        for stat, value in stats['dz_retrievals_exits'].items():
            if 'percent' in stat:
                print(f"  {stat.replace('_', ' ').title()}: {value:.1%}")
            else:
                print(f"  {stat.replace('_', ' ').title()}: {value}")

def main():
    """Main function to demonstrate API usage"""
    print("🏒 All Three Zones API Client")
    print("=" * 50)
    
    # Initialize client
    client = AllThreeZonesClient()
    
    # Check if API is running
    if not client.health_check():
        print("❌ API is not running. Please start the API first:")
        print("   python3 main.py")
        return
    
    print("✅ API is running!")
    
    # Search for Sidney Crosby
    print("\n🔍 Searching for Sidney Crosby...")
    crosby_results = client.search_players("Sidney Crosby")
    
    if crosby_results:
        print(f"✅ Found {len(crosby_results)} result(s)")
        print_player_stats(crosby_results[0])
    else:
        print("❌ No results found")
    
    # Get all players
    print("\n📋 Getting all players...")
    all_players = client.get_all_players()
    print(f"✅ Found {len(all_players)} players:")
    
    for player in all_players:
        print(f"  - {player['name']} ({player['team']})")
    
    # Get teams
    print("\n🏆 Getting teams...")
    teams = client.get_teams()
    print(f"✅ Found {len(teams)} teams:")
    
    for team, players in teams.items():
        print(f"  {team}: {len(players)} player(s)")
        for player in players:
            print(f"    - {player['name']}")
    
    # Search for other players
    print("\n🔍 Searching for Connor McDavid...")
    mcdavid_results = client.search_players("McDavid")
    
    if mcdavid_results:
        print(f"✅ Found {len(mcdavid_results)} result(s)")
        print_player_stats(mcdavid_results[0])
    
    print("\n🎉 API demonstration completed!")
    print("\nYou can now use the API without opening the website!")

if __name__ == "__main__":
    main() 