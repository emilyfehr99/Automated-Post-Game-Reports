#!/usr/bin/env python3
"""
Comprehensive Python Client for All Three Zones API
Demonstrates how to access all players quickly for Python work
"""

import requests
import json
from typing import Dict, List, Any

class ComprehensiveAllThreeZonesClient:
    """Comprehensive client for All Three Zones API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            response = requests.get(f"{self.base_url}/stats")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting database stats: {e}")
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
    
    def search_players(self, query: str) -> List[Dict[str, Any]]:
        """Search for players"""
        try:
            response = requests.get(f"{self.base_url}/search", params={"query": query})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error searching players: {e}")
            return []
    
    def get_player(self, player_name: str) -> Dict[str, Any]:
        """Get specific player"""
        try:
            response = requests.get(f"{self.base_url}/players/{player_name}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting player {player_name}: {e}")
            return {}
    
    def get_players_by_position(self, position: str) -> List[Dict[str, Any]]:
        """Get players by position (C, LW, RW, D, G)"""
        try:
            response = requests.get(f"{self.base_url}/players/position/{position}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting players by position: {e}")
            return []
    
    def get_players_by_team(self, team: str) -> List[Dict[str, Any]]:
        """Get players by team"""
        try:
            response = requests.get(f"{self.base_url}/players/team/{team}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting players by team: {e}")
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

def analyze_player_stats(player: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a player's statistics"""
    if "stats" not in player:
        return {}
    
    stats = player["stats"]
    analysis = {
        "name": player["name"],
        "team": player["team"],
        "position": player["position"],
        "analysis": {}
    }
    
    # Analyze general offense
    if "general_offense" in stats:
        offense = stats["general_offense"]
        analysis["analysis"]["offense_rating"] = offense.get("total_shot_contributions_per_60", 0)
        analysis["analysis"]["shot_efficiency"] = offense.get("shots_per_60", 0)
        analysis["analysis"]["playmaking"] = offense.get("shot_assists_per_60", 0)
    
    # Analyze passing
    if "passing" in stats:
        passing = stats["passing"]
        analysis["analysis"]["high_danger_playmaking"] = passing.get("high_danger_assists_per_60", 0)
    
    # Analyze zone entries
    if "zone_entries" in stats:
        entries = stats["zone_entries"]
        analysis["analysis"]["zone_entry_rate"] = entries.get("zone_entries_per_60", 0)
        analysis["analysis"]["controlled_entry_percent"] = entries.get("controlled_entry_percent", 0)
    
    # Analyze defensive zone play
    if "dz_retrievals_exits" in stats:
        defense = stats["dz_retrievals_exits"]
        analysis["analysis"]["retrieval_success_rate"] = defense.get("successful_retrieval_percent", 0)
        analysis["analysis"]["exit_rate"] = defense.get("exits_per_60", 0)
    
    return analysis

def find_top_players_by_stat(players: List[Dict[str, Any]], stat_path: str, top_n: int = 10) -> List[Dict[str, Any]]:
    """Find top players by a specific statistic"""
    def get_stat_value(player, path):
        """Get nested stat value"""
        keys = path.split('.')
        value = player
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return 0
        return value if isinstance(value, (int, float)) else 0
    
    # Add stat value to each player
    for player in players:
        player['_temp_stat'] = get_stat_value(player, stat_path)
    
    # Sort by stat value
    sorted_players = sorted(players, key=lambda x: x['_temp_stat'], reverse=True)
    
    # Return top N players
    top_players = sorted_players[:top_n]
    
    # Clean up temporary stat
    for player in top_players:
        del player['_temp_stat']
    
    return top_players

def main():
    """Main function to demonstrate comprehensive API usage"""
    print("🏒 Comprehensive All Three Zones API Client")
    print("=" * 60)
    
    # Initialize client
    client = ComprehensiveAllThreeZonesClient()
    
    # Get database stats
    print("📊 Database Statistics:")
    stats = client.get_database_stats()
    if stats:
        print(f"  Total Players: {stats['total_players']}")
        print(f"  Total Teams: {stats['total_teams']}")
        print(f"  Forwards: {stats['forwards']}")
        print(f"  Defensemen: {stats['defensemen']}")
        print(f"  Goalies: {stats['goalies']}")
    
    # Get all players
    print("\n👥 Getting all players...")
    all_players = client.get_all_players()
    print(f"✅ Retrieved {len(all_players)} players")
    
    # Find top players by different stats
    print("\n🏆 Top 5 Players by Total Shot Contributions:")
    top_shot_contributors = find_top_players_by_stat(all_players, "stats.general_offense.total_shot_contributions_per_60", 5)
    for i, player in enumerate(top_shot_contributors, 1):
        stat = player["stats"]["general_offense"]["total_shot_contributions_per_60"]
        print(f"  {i}. {player['name']} ({player['team']}) - {stat}")
    
    print("\n🎯 Top 5 Players by High Danger Assists:")
    top_assisters = find_top_players_by_stat(all_players, "stats.passing.high_danger_assists_per_60", 5)
    for i, player in enumerate(top_assisters, 1):
        stat = player["stats"]["passing"]["high_danger_assists_per_60"]
        print(f"  {i}. {player['name']} ({player['team']}) - {stat}")
    
    print("\n🛡️  Top 5 Defensemen by Retrieval Success Rate:")
    defensemen = client.get_players_by_position("D")
    top_retrievers = find_top_players_by_stat(defensemen, "stats.dz_retrievals_exits.successful_retrieval_percent", 5)
    for i, player in enumerate(top_retrievers, 1):
        stat = player["stats"]["dz_retrievals_exits"]["successful_retrieval_percent"]
        print(f"  {i}. {player['name']} ({player['team']}) - {stat:.1%}")
    
    # Search for specific players
    print("\n🔍 Searching for specific players:")
    search_terms = ["Crosby", "McDavid", "Samberg", "Makar", "Matthews"]
    for term in search_terms:
        results = client.search_players(term)
        if results:
            print(f"  '{term}': Found {len(results)} players")
            for player in results[:2]:  # Show first 2
                print(f"    - {player['name']} ({player['team']})")
        else:
            print(f"  '{term}': No results")
    
    # Get team rosters
    print("\n🏆 Team Rosters (showing first 3 teams):")
    teams = client.get_teams()
    for i, (team, players) in enumerate(teams.items()):
        if i >= 3:  # Only show first 3 teams
            break
        print(f"  {team}: {len(players)} players")
        for player in players[:3]:  # Show first 3 players per team
            print(f"    - {player['name']} ({player['position']})")
    
    print("\n🎉 Comprehensive API demonstration completed!")
    print("\nYou now have access to 550+ players with complete statistics!")
    print("Perfect for Python data analysis and research!")

if __name__ == "__main__":
    main() 