#!/usr/bin/env python3
"""
Test Players Endpoint
Shows what the players endpoint would return
"""

import json
from datetime import datetime
from ajhl_team_config import get_active_teams

def test_players_endpoint():
    """Test what the players endpoint would return"""
    print("🏒 Testing Players Endpoint")
    print("=" * 40)
    
    # Mock player data (what would come from Hudl Instat)
    mock_players = [
        {
            "player_id": "player_001",
            "team_id": "lloydminster_bobcats",
            "name": "John Smith",
            "position": "F",
            "stats": {
                "goals": 15,
                "assists": 20,
                "points": 35,
                "games_played": 25,
                "plus_minus": 8,
                "penalty_minutes": 12,
                "shots_on_goal": 45,
                "shooting_percentage": 33.3
            },
            "last_updated": "2024-01-15T10:30:00Z"
        },
        {
            "player_id": "player_002", 
            "team_id": "lloydminster_bobcats",
            "name": "Mike Johnson",
            "position": "D",
            "stats": {
                "goals": 3,
                "assists": 18,
                "points": 21,
                "games_played": 25,
                "plus_minus": 12,
                "penalty_minutes": 8,
                "shots_on_goal": 15,
                "shooting_percentage": 20.0
            },
            "last_updated": "2024-01-15T10:30:00Z"
        },
        {
            "player_id": "player_003",
            "team_id": "lloydminster_bobcats", 
            "name": "Alex Wilson",
            "position": "G",
            "stats": {
                "games_played": 20,
                "wins": 12,
                "losses": 6,
                "overtime_losses": 2,
                "goals_against_average": 2.45,
                "save_percentage": 0.915,
                "shutouts": 3,
                "saves": 450
            },
            "last_updated": "2024-01-15T10:30:00Z"
        },
        {
            "player_id": "player_004",
            "team_id": "brooks_bandits",
            "name": "Ryan Brown",
            "position": "F", 
            "stats": {
                "goals": 22,
                "assists": 15,
                "points": 37,
                "games_played": 24,
                "plus_minus": 15,
                "penalty_minutes": 20,
                "shots_on_goal": 68,
                "shooting_percentage": 32.4
            },
            "last_updated": "2024-01-15T10:30:00Z"
        }
    ]
    
    print(f"Found {len(mock_players)} players:")
    print()
    
    # Show players by position
    forwards = [p for p in mock_players if p["position"] == "F"]
    defensemen = [p for p in mock_players if p["position"] == "D"] 
    goalies = [p for p in mock_players if p["position"] == "G"]
    
    print("📊 Players by Position:")
    print(f"  Forwards: {len(forwards)}")
    print(f"  Defensemen: {len(defensemen)}")
    print(f"  Goalies: {len(goalies)}")
    print()
    
    # Show sample players
    print("👥 Sample Players:")
    for i, player in enumerate(mock_players[:3]):
        print(f"{i+1}. {player['name']} ({player['position']}) - {player['team_id']}")
        print(f"   Goals: {player['stats'].get('goals', 'N/A')}")
        print(f"   Assists: {player['stats'].get('assists', 'N/A')}")
        print(f"   Points: {player['stats'].get('points', 'N/A')}")
        print()
    
    # Show JSON format
    print("📄 JSON Response Format:")
    print("=" * 40)
    print(json.dumps(mock_players[:2], indent=2))
    
    print()
    print("🔍 Available Endpoints:")
    print("-" * 40)
    print("GET /players - Get all players")
    print("GET /players?team_id=lloydminster_bobcats - Get team players")
    print("GET /players?position=F - Get forwards only")
    print("GET /players?team_id=lloydminster_bobcats&position=G - Get team goalies")
    print()
    
    print("📱 Example Usage:")
    print("-" * 40)
    print("# Get all players")
    print("curl http://localhost:8000/players")
    print()
    print("# Get Lloydminster Bobcats players")
    print("curl 'http://localhost:8000/players?team_id=lloydminster_bobcats'")
    print()
    print("# Get only forwards")
    print("curl 'http://localhost:8000/players?position=F'")
    print()
    print("# Get team goalies")
    print("curl 'http://localhost:8000/players?team_id=lloydminster_bobcats&position=G'")
    print()
    
    print("🐍 Python Example:")
    print("-" * 40)
    print("import requests")
    print()
    print("# Get all players")
    print("response = requests.get('http://localhost:8000/players')")
    print("players = response.json()")
    print()
    print("# Get team players")
    print("response = requests.get('http://localhost:8000/players', params={'team_id': 'lloydminster_bobcats'})")
    print("team_players = response.json()")
    print()
    print("# Get forwards only")
    print("response = requests.get('http://localhost:8000/players', params={'position': 'F'})")
    print("forwards = response.json()")
    print()
    
    print("✅ This is exactly what the players API would return!")

if __name__ == "__main__":
    test_players_endpoint()
