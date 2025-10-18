#!/usr/bin/env python3
"""
Example client for All Three Zones API
"""

import requests
import json
import time
from typing import Dict, List, Any

class AllThreeZonesClient:
    """Client for interacting with the All Three Zones API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the API is running"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_all_players(self) -> List[Dict[str, Any]]:
        """Get all players"""
        try:
            response = self.session.get(f"{self.base_url}/players")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get players: {e}")
            return []
    
    def get_player(self, player_name: str) -> Dict[str, Any]:
        """Get a specific player"""
        try:
            response = self.session.get(f"{self.base_url}/players/{player_name}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get player {player_name}: {e}")
            return {}
    
    def search_players(self, query: str) -> List[Dict[str, Any]]:
        """Search for players"""
        try:
            response = self.session.get(f"{self.base_url}/search", params={"query": query})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to search players: {e}")
            return []
    
    def get_team(self, team_name: str) -> Dict[str, Any]:
        """Get team data"""
        try:
            response = self.session.get(f"{self.base_url}/teams/{team_name}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get team {team_name}: {e}")
            return {}
    
    def get_players_by_team(self, team_name: str) -> List[Dict[str, Any]]:
        """Get players filtered by team"""
        try:
            response = self.session.get(f"{self.base_url}/players", params={"team": team_name})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get players for team {team_name}: {e}")
            return []

def print_player_info(player: Dict[str, Any]):
    """Print player information in a formatted way"""
    print(f"\n{'='*50}")
    print(f"Player: {player.get('name', 'Unknown')}")
    print(f"Team: {player.get('team', 'Unknown')}")
    print(f"Position: {player.get('position', 'Unknown')}")
    print(f"Games Played: {player.get('games_played', 0)}")
    
    stats = player.get('stats', {})
    if stats:
        print("\nStatistics:")
        for stat_name, stat_value in stats.items():
            print(f"  {stat_name}: {stat_value}")
    print(f"{'='*50}")

def print_team_info(team: Dict[str, Any]):
    """Print team information in a formatted way"""
    print(f"\n{'='*50}")
    print(f"Team: {team.get('team_name', 'Unknown')}")
    
    stats = team.get('stats', {})
    if stats:
        print("\nTeam Statistics:")
        for stat_name, stat_value in stats.items():
            print(f"  {stat_name}: {stat_value}")
    print(f"{'='*50}")

def main():
    """Example usage of the All Three Zones API client"""
    print("All Three Zones API Client Example")
    print("="*50)
    
    # Initialize client
    client = AllThreeZonesClient()
    
    # Check if API is running
    print("\n1. Checking API health...")
    health = client.health_check()
    print(f"Health status: {health}")
    
    if health.get('status') != 'healthy':
        print("❌ API is not running. Please start the API server first.")
        print("Run: python run.py")
        return
    
    print("✅ API is running!")
    
    # Example 1: Get all players
    print("\n2. Getting all players...")
    players = client.get_all_players()
    print(f"Found {len(players)} players")
    
    if players:
        # Show first few players
        for i, player in enumerate(players[:3]):
            print(f"\nPlayer {i+1}:")
            print(f"  Name: {player.get('name', 'Unknown')}")
            print(f"  Team: {player.get('team', 'Unknown')}")
    
    # Example 2: Search for a specific player
    print("\n3. Searching for players...")
    search_results = client.search_players("McDavid")
    print(f"Found {len(search_results)} players matching 'McDavid'")
    
    for player in search_results:
        print_player_info(player)
    
    # Example 3: Get team data
    print("\n4. Getting team data...")
    team_data = client.get_team("Oilers")
    if team_data:
        print_team_info(team_data)
    else:
        print("No team data found")
    
    # Example 4: Get players by team
    print("\n5. Getting players by team...")
    team_players = client.get_players_by_team("Oilers")
    print(f"Found {len(team_players)} players for Oilers")
    
    for player in team_players[:3]:  # Show first 3 players
        print(f"  - {player.get('name', 'Unknown')} ({player.get('position', 'Unknown')})")
    
    print("\n" + "="*50)
    print("Example completed!")
    print("\nTo use this client in your own code:")
    print("1. Start the API server: python run.py")
    print("2. Import and use the AllThreeZonesClient class")
    print("3. Call the methods to get data")

if __name__ == "__main__":
    main() 