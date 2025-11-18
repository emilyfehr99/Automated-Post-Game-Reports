#!/usr/bin/env python3
"""
Live Stats Extractor - Extract HDC and shots data from live NHL games
Uses the same logic as the post-game report generator
"""

import requests
from typing import Dict, Tuple

class LiveStatsExtractor:
    def __init__(self):
        self.base_url = "https://api-web.nhle.com/v1"
    
    def get_live_stats(self, game_id: str) -> Dict:
        """Get live HDC and shots data for a game"""
        try:
            # Get play-by-play data
            response = requests.get(f'{self.base_url}/gamecenter/{game_id}/play-by-play')
            if response.status_code != 200:
                return None
                
            data = response.json()
            
            # Get team IDs
            away_team_id = data.get('awayTeam', {}).get('id')
            home_team_id = data.get('homeTeam', {}).get('id')
            away_team_abbrev = data.get('awayTeam', {}).get('abbrev')
            home_team_abbrev = data.get('homeTeam', {}).get('abbrev')
            
            if not all([away_team_id, home_team_id, away_team_abbrev, home_team_abbrev]):
                return None
            
            # Calculate HDC and shots from plays
            away_hdc, home_hdc = self._calculate_hdc_from_plays(data, away_team_id, home_team_id)
            away_shots, home_shots = self._calculate_shots_from_plays(data, away_team_id, home_team_id)
            
            return {
                'away_team': away_team_abbrev,
                'home_team': home_team_abbrev,
                'away_hdc': away_hdc,
                'home_hdc': home_hdc,
                'away_shots': away_shots,
                'home_shots': home_shots,
                'away_score': data.get('awayTeam', {}).get('score', 0),
                'home_score': data.get('homeTeam', {}).get('score', 0)
            }
            
        except Exception as e:
            print(f"Error getting live stats: {e}")
            return None
    
    def _calculate_hdc_from_plays(self, data: Dict, away_team_id: int, home_team_id: int) -> Tuple[int, int]:
        """Calculate high danger chances from play-by-play data (same logic as post-game reports)"""
        try:
            away_hdc = 0
            home_hdc = 0
            
            if 'plays' in data:
                for play in data['plays']:
                    if play.get('typeDescKey') in ['shot-on-goal', 'goal']:
                        team_id = play.get('details', {}).get('eventOwnerTeamId')
                        if team_id == away_team_id or team_id == home_team_id:
                            # Check if it's a high danger chance (close to net)
                            details = play.get('details', {})
                            x_coord = details.get('xCoord', 0)
                            y_coord = details.get('yCoord', 0)
                            
                            # High danger area: close to net and in front (same logic as post-game reports)
                            if x_coord > 50 and abs(y_coord) < 20:  # In front of net, close
                                if team_id == away_team_id:
                                    away_hdc += 1
                                else:
                                    home_hdc += 1
            
            return away_hdc, home_hdc
            
        except Exception as e:
            print(f"Error calculating HDC from plays: {e}")
            return 0, 0
    
    def _calculate_shots_from_plays(self, data: Dict, away_team_id: int, home_team_id: int) -> Tuple[int, int]:
        """Calculate total shots from play-by-play data"""
        try:
            away_shots = 0
            home_shots = 0
            
            if 'plays' in data:
                for play in data['plays']:
                    if play.get('typeDescKey') in ['shot-on-goal', 'goal']:
                        team_id = play.get('details', {}).get('eventOwnerTeamId')
                        if team_id == away_team_id:
                            away_shots += 1
                        elif team_id == home_team_id:
                            home_shots += 1
            
            return away_shots, home_shots
            
        except Exception as e:
            print(f"Error calculating shots from plays: {e}")
            return 0, 0

def main():
    """Test the live stats extractor"""
    extractor = LiveStatsExtractor()
    
    # Test with the current VAN @ WSH game
    game_id = "2025020089"
    stats = extractor.get_live_stats(game_id)
    
    if stats:
        print("🏒 Live Game Stats")
        print("="*40)
        print(f"Game: {stats['away_team']} @ {stats['home_team']}")
        print(f"Score: {stats['away_team']} {stats['away_score']} - {stats['home_score']} {stats['home_team']}")
        print(f"HDC: {stats['away_team']} {stats['away_hdc']} - {stats['home_hdc']} {stats['home_team']}")
        print(f"Shots: {stats['away_team']} {stats['away_shots']} - {stats['home_shots']} {stats['home_team']}")
    else:
        print("❌ Could not get live stats")

if __name__ == "__main__":
    main()
