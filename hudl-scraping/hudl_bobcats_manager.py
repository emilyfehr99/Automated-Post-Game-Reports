#!/usr/bin/env python3
"""
Hudl Bobcats Team Manager
Specialized manager for the Bobcats team (ID: 21479) with Hudl identifiers
"""

import json
import time
import logging
from typing import Dict, List, Optional
from hudl_multi_user_manager import HudlMultiUserManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HudlBobcatsManager:
    """Specialized manager for the Bobcats team"""
    
    def __init__(self, username: str, password: str):
        """Initialize the Bobcats manager"""
        self.team_id = "21479"  # Bobcats team ID
        self.team_name = "Bobcats"
        self.manager = HudlMultiUserManager(username, password)
        
        # Hudl identifier mappings (these will be populated from the API)
        self.player_identifiers = {}
        self.league_identifiers = {}
        self.game_identifiers = {}
        
    def get_team_roster(self, user_id: str) -> Dict:
        """Get the complete Bobcats roster with Hudl identifiers"""
        try:
            players = self.manager.get_team_players(user_id, self.team_id)
            
            # Process players to extract Hudl identifiers
            roster_data = {
                "team_id": self.team_id,
                "team_name": self.team_name,
                "players": [],
                "total_players": len(players),
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            for player in players:
                if "error" not in player:
                    # Extract Hudl player identifier if available
                    player_data = {
                        "name": player.get("name", "Unknown"),
                        "position": player.get("position", "Unknown"),
                        "number": player.get("number", "Unknown"),
                        "hudl_player_id": self._extract_hudl_id(player),
                        "raw_data": player
                    }
                    roster_data["players"].append(player_data)
            
            # Store player identifiers for future use
            self.player_identifiers = {
                player["hudl_player_id"]: player["name"] 
                for player in roster_data["players"] 
                if player["hudl_player_id"]
            }
            
            return roster_data
            
        except Exception as e:
            logger.error(f"❌ Error getting roster: {e}")
            return {"error": str(e), "team_id": self.team_id}
    
    def get_team_games(self, user_id: str) -> Dict:
        """Get Bobcats games with Hudl identifiers"""
        try:
            games = self.manager.get_team_games(user_id, self.team_id)
            
            games_data = {
                "team_id": self.team_id,
                "team_name": self.team_name,
                "games": [],
                "total_games": len(games),
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            for game in games:
                if "error" not in game:
                    game_data = {
                        "date": game.get("date", "Unknown"),
                        "opponent": game.get("opponent", "Unknown"),
                        "score": game.get("score", "Unknown"),
                        "hudl_game_id": self._extract_hudl_id(game),
                        "raw_data": game
                    }
                    games_data["games"].append(game_data)
            
            # Store game identifiers
            self.game_identifiers = {
                game["hudl_game_id"]: f"{game['date']} vs {game['opponent']}"
                for game in games_data["games"]
                if game["hudl_game_id"]
            }
            
            return games_data
            
        except Exception as e:
            logger.error(f"❌ Error getting games: {e}")
            return {"error": str(e), "team_id": self.team_id}
    
    def get_team_info(self, user_id: str) -> Dict:
        """Get comprehensive Bobcats team information"""
        try:
            team_info = self.manager.get_team_info(user_id, self.team_id)
            
            # Add Bobcats-specific information
            bobcats_info = {
                "team_id": self.team_id,
                "team_name": self.team_name,
                "hudl_team_id": self.team_id,
                "league": "Hockey",
                "season": "2024-25",
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "raw_data": team_info
            }
            
            return bobcats_info
            
        except Exception as e:
            logger.error(f"❌ Error getting team info: {e}")
            return {"error": str(e), "team_id": self.team_id}
    
    def get_player_by_hudl_id(self, user_id: str, hudl_player_id: str) -> Optional[Dict]:
        """Get specific player by Hudl identifier"""
        roster = self.get_team_roster(user_id)
        
        for player in roster.get("players", []):
            if player.get("hudl_player_id") == hudl_player_id:
                return player
        
        return None
    
    def get_game_by_hudl_id(self, user_id: str, hudl_game_id: str) -> Optional[Dict]:
        """Get specific game by Hudl identifier"""
        games = self.get_team_games(user_id)
        
        for game in games.get("games", []):
            if game.get("hudl_game_id") == hudl_game_id:
                return game
        
        return None
    
    def get_team_analytics(self, user_id: str) -> Dict:
        """Get team analytics and statistics"""
        try:
            # This would need to be implemented based on what data is available
            # from the Hudl Instat platform
            analytics = {
                "team_id": self.team_id,
                "team_name": self.team_name,
                "analytics_available": False,
                "note": "Analytics extraction needs to be implemented based on Hudl data structure",
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error getting analytics: {e}")
            return {"error": str(e), "team_id": self.team_id}
    
    def _extract_hudl_id(self, data: Dict) -> Optional[str]:
        """Extract Hudl identifier from data object"""
        # Look for common Hudl ID patterns
        id_fields = ["id", "hudl_id", "player_id", "game_id", "team_id", "identifier"]
        
        for field in id_fields:
            if field in data and data[field]:
                return str(data[field])
        
        # Look in raw_data if available
        if "raw_data" in data:
            for field in id_fields:
                if field in data["raw_data"] and data["raw_data"][field]:
                    return str(data["raw_data"][field])
        
        return None
    
    def export_team_data(self, user_id: str, format: str = "json") -> str:
        """Export complete team data"""
        try:
            team_data = {
                "team_info": self.get_team_info(user_id),
                "roster": self.get_team_roster(user_id),
                "games": self.get_team_games(user_id),
                "analytics": self.get_team_analytics(user_id),
                "export_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if format.lower() == "json":
                filename = f"bobcats_data_{int(time.time())}.json"
                with open(filename, 'w') as f:
                    json.dump(team_data, f, indent=2)
                return filename
            else:
                return json.dumps(team_data, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error exporting data: {e}")
            return f"Error: {e}"
    
    def get_session_status(self) -> Dict:
        """Get current session status"""
        return self.manager.get_session_status()
    
    def close_all_sessions(self):
        """Close all active sessions"""
        self.manager.close_all_sessions()

def main():
    """Example usage of the Bobcats manager"""
    print("🏒 Hudl Bobcats Team Manager")
    print("=" * 50)
    print(f"Team ID: 21479")
    print(f"Team Name: Bobcats")
    
    # Initialize the manager
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        bobcats = HudlBobcatsManager(HUDL_USERNAME, HUDL_PASSWORD)
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
        return
    
    # Example: Get team information
    print(f"\n📊 Getting Bobcats team information...")
    team_info = bobcats.get_team_info("emily")
    print(f"Team Info: {json.dumps(team_info, indent=2)}")
    
    # Example: Get roster
    print(f"\n👥 Getting Bobcats roster...")
    roster = bobcats.get_team_roster("emily")
    print(f"Roster: {len(roster.get('players', []))} players found")
    
    # Show Hudl identifiers found
    if roster.get("players"):
        print(f"\n🆔 Hudl Player Identifiers found:")
        for player in roster["players"][:5]:  # Show first 5
            if player.get("hudl_player_id"):
                print(f"  - {player['name']}: {player['hudl_player_id']}")
    
    # Example: Get games
    print(f"\n🏆 Getting Bobcats games...")
    games = bobcats.get_team_games("emily")
    print(f"Games: {len(games.get('games', []))} games found")
    
    # Show Hudl identifiers found
    if games.get("games"):
        print(f"\n🆔 Hudl Game Identifiers found:")
        for game in games["games"][:3]:  # Show first 3
            if game.get("hudl_game_id"):
                print(f"  - {game['date']} vs {game['opponent']}: {game['hudl_game_id']}")
    
    # Export data
    print(f"\n💾 Exporting team data...")
    export_file = bobcats.export_team_data("emily")
    print(f"Data exported to: {export_file}")
    
    # Show session status
    print(f"\n📊 Session Status:")
    status = bobcats.get_session_status()
    print(json.dumps(status, indent=2))
    
    # Clean up
    bobcats.close_all_sessions()
    print("\n✅ All sessions closed")

if __name__ == "__main__":
    main()
