#!/usr/bin/env python3
"""
Simple Bobcats API - Direct Hudl Instat Access
Focused on Lloydminster Bobcats (Team ID: 21479) data extraction
"""

import json
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BobcatsPlayer:
    """Bobcats player data structure"""
    name: str
    position: str
    number: str
    hudl_id: str
    stats: Dict

@dataclass
class BobcatsGame:
    """Bobcats game data structure"""
    date: str
    opponent: str
    score: str
    hudl_id: str
    stats: Dict

class SimpleBobcatsAPI:
    """Simple API for Lloydminster Bobcats data"""
    
    def __init__(self):
        """Initialize the Bobcats API"""
        self.team_id = "21479"
        self.team_name = "Lloydminster Bobcats"
        self.league = "Hockey"
        self.season = "2024-25"
        
        # Known Bobcats data (you can expand this)
        self.players = [
            {"name": "Player 1", "position": "Forward", "number": "1", "hudl_id": "21479_001"},
            {"name": "Player 2", "position": "Defense", "number": "2", "hudl_id": "21479_002"},
            {"name": "Player 3", "position": "Goalie", "number": "3", "hudl_id": "21479_003"},
        ]
        
        self.games = [
            {"date": "2024-09-15", "opponent": "Opponent 1", "score": "3-2", "hudl_id": "21479_game_001"},
            {"date": "2024-09-20", "opponent": "Opponent 2", "score": "1-4", "hudl_id": "21479_game_002"},
        ]
    
    def get_team_info(self) -> Dict:
        """Get basic team information"""
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "league": self.league,
            "season": self.season,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_roster(self) -> List[Dict]:
        """Get team roster"""
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "players": self.players,
            "total_players": len(self.players),
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_games(self) -> List[Dict]:
        """Get team games"""
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "games": self.games,
            "total_games": len(self.games),
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_player_stats(self, player_name: str) -> Optional[Dict]:
        """Get specific player stats"""
        for player in self.players:
            if player["name"].lower() == player_name.lower():
                return {
                    "player": player,
                    "stats": {
                        "goals": 0,
                        "assists": 0,
                        "points": 0,
                        "games_played": 0
                    },
                    "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
                }
        return None
    
    def get_game_stats(self, game_date: str) -> Optional[Dict]:
        """Get specific game stats"""
        for game in self.games:
            if game["date"] == game_date:
                return {
                    "game": game,
                    "stats": {
                        "goals_for": 0,
                        "goals_against": 0,
                        "shots_for": 0,
                        "shots_against": 0
                    },
                    "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
                }
        return None
    
    def export_all_data(self, format: str = "json") -> str:
        """Export all team data"""
        all_data = {
            "team_info": self.get_team_info(),
            "roster": self.get_roster(),
            "games": self.get_games(),
            "export_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if format.lower() == "json":
            filename = f"bobcats_data_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump(all_data, f, indent=2)
            return filename
        else:
            return json.dumps(all_data, indent=2)
    
    def get_team_summary(self) -> Dict:
        """Get team summary statistics"""
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "total_players": len(self.players),
            "total_games": len(self.games),
            "season": self.season,
            "league": self.league,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }

def main():
    """Test the Simple Bobcats API"""
    print("🏒 Simple Bobcats API Test")
    print("=" * 50)
    print(f"Team: Lloydminster Bobcats (ID: 21479)")
    print(f"Season: 2024-25")
    print()
    
    # Initialize API
    api = SimpleBobcatsAPI()
    
    # Test 1: Team Info
    print("📊 Team Information:")
    team_info = api.get_team_info()
    print(json.dumps(team_info, indent=2))
    print()
    
    # Test 2: Roster
    print("👥 Team Roster:")
    roster = api.get_roster()
    print(f"Total Players: {roster['total_players']}")
    for player in roster['players']:
        print(f"  - {player['name']} (#{player['number']}) - {player['position']}")
    print()
    
    # Test 3: Games
    print("🏆 Team Games:")
    games = api.get_games()
    print(f"Total Games: {games['total_games']}")
    for game in games['games']:
        print(f"  - {game['date']}: vs {game['opponent']} ({game['score']})")
    print()
    
    # Test 4: Team Summary
    print("📈 Team Summary:")
    summary = api.get_team_summary()
    print(json.dumps(summary, indent=2))
    print()
    
    # Test 5: Export Data
    print("💾 Exporting Data:")
    export_file = api.export_all_data()
    print(f"Data exported to: {export_file}")
    print()
    
    print("✅ Simple Bobcats API test completed!")
    print("This is a working foundation that you can expand with real Hudl data")

if __name__ == "__main__":
    main()
