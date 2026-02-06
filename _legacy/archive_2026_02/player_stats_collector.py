#!/usr/bin/env python3
"""
Player Stats Collector
Fetches and processes individual player statistics from NHL API
"""
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class PlayerStatsCollector:
    def __init__(self):
        self.base_url = "https://api-web.nhle.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.player_cache = {}
    
    def get_player_stats(self, player_id: int, season: str = "20252026") -> Optional[Dict]:
        """Get comprehensive player statistics"""
        try:
            # Check cache first
            cache_key = f"{player_id}_{season}"
            if cache_key in self.player_cache:
                return self.player_cache[cache_key]
            
            url = f"{self.base_url}/player/{player_id}/landing"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant stats
            stats = self._extract_player_stats(data, season)
            
            # Cache the result
            self.player_cache[cache_key] = stats
            
            return stats
            
        except Exception as e:
            print(f"Error fetching stats for player {player_id}: {e}")
            return None
    
    def _extract_player_stats(self, data: Dict, season: str) -> Dict:
        """Extract and calculate relevant player statistics"""
        stats = {
            'player_id': data.get('playerId'),
            'name': data.get('firstName', {}).get('default', '') + ' ' + data.get('lastName', {}).get('default', ''),
            'position': data.get('position'),
            'team_abbr': data.get('currentTeamAbbrev'),
        }
        
        # Get season stats
        season_stats = data.get('featuredStats', {}).get('regularSeason', {}).get('subSeason', {})
        
        if season_stats:
            games_played = season_stats.get('gamesPlayed', 0)
            goals = season_stats.get('goals', 0)
            assists = season_stats.get('assists', 0)
            points = season_stats.get('points', 0)
            shots = season_stats.get('shots', 0)
            toi_per_game = season_stats.get('avgToi', '00:00')
            
            # Calculate per-game rates
            stats['games_played'] = games_played
            stats['goals_per_game'] = goals / games_played if games_played > 0 else 0
            stats['assists_per_game'] = assists / games_played if games_played > 0 else 0
            stats['points_per_game'] = points / games_played if games_played > 0 else 0
            stats['shots_per_game'] = shots / games_played if games_played > 0 else 0
            
            # Calculate shooting percentage
            stats['shooting_pct'] = (goals / shots * 100) if shots > 0 else 0
            
            # Parse TOI
            stats['toi_per_game'] = self._parse_toi(toi_per_game)
            
            # Calculate per-60 metrics
            toi_minutes = stats['toi_per_game']
            if toi_minutes > 0 and games_played > 0:
                total_toi_minutes = games_played * toi_minutes
                stats['goals_per_60'] = (goals / total_toi_minutes) * 60
                stats['points_per_60'] = (points / total_toi_minutes) * 60
                stats['shots_per_60'] = (shots / total_toi_minutes) * 60
            else:
                stats['goals_per_60'] = 0
                stats['points_per_60'] = 0
                stats['shots_per_60'] = 0
        
        # Get recent form (last 5 games)
        stats['recent_form'] = self._calculate_recent_form(data)
        
        return stats
    
    def _parse_toi(self, toi_str: str) -> float:
        """Parse time on ice string (MM:SS) to minutes"""
        try:
            if ':' in toi_str:
                parts = toi_str.split(':')
                return int(parts[0]) + int(parts[1]) / 60
            return 0
        except:
            return 0
    
    def _calculate_recent_form(self, data: Dict) -> Dict:
        """Calculate recent performance (last 5 games)"""
        # This would ideally fetch game log data
        # For now, return placeholder
        return {
            'last_5_ppg': 0.0,
            'last_5_shots_pg': 0.0,
            'trending': 'neutral'
        }
    
    def get_team_roster_stats(self, team_abbr: str) -> List[Dict]:
        """Get stats for all players on a team"""
        try:
            url = f"{self.base_url}/roster/{team_abbr}/current"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            roster_data = response.json()
            
            all_stats = []
            
            # Process forwards
            for position in ['forwards', 'defensemen', 'goalies']:
                players = roster_data.get(position, [])
                for player in players:
                    player_id = player.get('id')
                    if player_id:
                        stats = self.get_player_stats(player_id)
                        if stats:
                            all_stats.append(stats)
            
            return all_stats
            
        except Exception as e:
            print(f"Error fetching roster stats for {team_abbr}: {e}")
            return []
    
    def calculate_lineup_xg(self, lineup: List[int]) -> float:
        """Calculate expected goals for a lineup based on player stats"""
        total_xg = 0.0
        
        for player_id in lineup:
            stats = self.get_player_stats(player_id)
            if stats and stats.get('position') != 'G':  # Exclude goalies
                # Simple xG approximation: goals_per_60 * expected_ice_time
                goals_per_60 = stats.get('goals_per_60', 0)
                toi = stats.get('toi_per_game', 0)
                
                # Weight by ice time (normalize to 60 minutes)
                contribution = goals_per_60 * (toi / 60)
                total_xg += contribution
        
        return total_xg
    
    def save_roster_stats(self, team_abbr: str, filename: str = None):
        """Save team roster stats to JSON file"""
        if filename is None:
            filename = f"data/player_stats_{team_abbr}_{datetime.now().strftime('%Y%m%d')}.json"
        
        stats = self.get_team_roster_stats(team_abbr)
        
        with open(filename, 'w') as f:
            json.dump({
                'team': team_abbr,
                'date': datetime.now().isoformat(),
                'players': stats
            }, f, indent=2)
        
        print(f"Saved {len(stats)} player stats to {filename}")
        return filename

if __name__ == "__main__":
    collector = PlayerStatsCollector()
    
    # Test with a few teams
    print("🏒 NHL Player Stats Collector")
    print("=" * 50)
    
    test_teams = ['TBL', 'STL', 'TOR']
    
    for team in test_teams:
        print(f"\n📊 Fetching stats for {team}...")
        stats = collector.get_team_roster_stats(team)
        
        if stats:
            print(f"   Found {len(stats)} players")
            
            # Show top 3 scorers
            scorers = sorted(stats, key=lambda x: x.get('points_per_game', 0), reverse=True)[:3]
            print(f"   Top scorers:")
            for player in scorers:
                print(f"      {player['name']}: {player.get('points_per_game', 0):.2f} PPG, {player.get('goals_per_60', 0):.2f} G/60")
