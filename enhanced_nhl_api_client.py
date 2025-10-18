#!/usr/bin/env python3
"""
Enhanced NHL API Client - 2025 Edition
Comprehensive client for all NHL API endpoints with advanced features
"""

import requests
import json
import time
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional, Any

class EnhancedNHLAPIClient:
    def __init__(self):
        """Initialize the enhanced NHL API client with all 2025 endpoints"""
        # Base URLs for different API versions
        self.web_api_base = "https://api-web.nhle.com/v1"
        self.stats_api_base = "https://api.nhle.com/stats/rest"
        self.legacy_api_base = "https://statsapi.web.nhl.com/api/v1"
        
        # Session setup with proper headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
        
        # Team mappings
        self.team_abbrevs = {
            'FLA': 13, 'EDM': 22, 'BOS': 6, 'TOR': 10, 'MTL': 8, 'OTT': 9,
            'BUF': 7, 'DET': 17, 'TBL': 14, 'CAR': 12, 'WSH': 15, 'PIT': 5,
            'NYR': 3, 'NYI': 2, 'NJD': 1, 'PHI': 4, 'CBJ': 29, 'NSH': 18,
            'STL': 19, 'MIN': 30, 'WPG': 52, 'COL': 21, 'ARI': 53, 'VGK': 54,
            'SJS': 28, 'LAK': 26, 'ANA': 24, 'CGY': 20, 'VAN': 23, 'SEA': 55,
            'CHI': 16, 'DAL': 25
        }
        
        # Reverse mapping
        self.team_ids = {v: k for k, v in self.team_abbrevs.items()}
    
    def _rate_limit(self):
        """Implement rate limiting to avoid API throttling"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make a rate-limited request to the NHL API"""
        self._rate_limit()
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"Resource not found: {url}")
                return None
            elif response.status_code == 307:
                print(f"Redirect detected: {url}")
                return None
            else:
                print(f"API request failed with status {response.status_code}: {url}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
    
    # ==================== TEAM INFORMATION ====================
    
    def get_all_teams(self, season: str = "20242025") -> Optional[Dict]:
        """Get all NHL teams for a specific season"""
        url = f"{self.legacy_api_base}/teams"
        params = {"season": season}
        return self._make_request(url, params)
    
    def get_team_info(self, team_id: int, season: str = "20242025") -> Optional[Dict]:
        """Get detailed team information including roster"""
        # Try the web API first (more reliable)
        team_abbrev = self.get_team_abbrev_from_id(team_id)
        if team_abbrev:
            roster_data = self.get_team_roster(team_abbrev, season)
            if roster_data:
                return {
                    'teams': [{
                        'id': team_id,
                        'abbreviation': team_abbrev,
                        'name': self.get_team_name_from_abbrev(team_abbrev),
                        'roster': roster_data
                    }]
                }
        
        # Fallback to legacy API
        url = f"{self.legacy_api_base}/teams/{team_id}"
        params = {
            "expand": "team.roster",
            "season": season
        }
        return self._make_request(url, params)
    
    def get_team_roster(self, team_code: str, season: str = "20242025") -> Optional[Dict]:
        """Get team roster using team code (e.g., 'EDM' for Edmonton)"""
        url = f"{self.web_api_base}/roster/{team_code.upper()}/{season}"
        return self._make_request(url)
    
    # ==================== PLAYER INFORMATION ====================
    
    def get_player_profile(self, player_id: int) -> Optional[Dict]:
        """Get player profile information"""
        url = f"{self.web_api_base}/player/{player_id}/landing"
        return self._make_request(url)
    
    def get_player_game_log(self, player_id: int, season: str = "20242025", game_type: int = 2) -> Optional[Dict]:
        """Get player's game-by-game stats for a season
        game_type: 2=regular season, 3=playoffs, 1=preseason, 4=All-Star
        """
        url = f"{self.web_api_base}/player/{player_id}/game-log/{season}/{game_type}"
        return self._make_request(url)
    
    def get_skater_stats(self, season: str = "20242025", limit: int = 50, sort_by: str = "points") -> Optional[Dict]:
        """Get skater statistics with customizable filters"""
        url = f"{self.stats_api_base}/en/skater/summary"
        params = {
            "limit": limit,
            "start": 0,
            "sort": sort_by,
            "cayenneExp": f"seasonId={season}"
        }
        return self._make_request(url, params)
    
    def get_goalie_stats(self, season: str = "20242025", limit: int = 50, sort_by: str = "wins") -> Optional[Dict]:
        """Get goalie statistics with customizable filters"""
        url = f"{self.stats_api_base}/en/goalie/summary"
        params = {
            "limit": limit,
            "start": 0,
            "sort": sort_by,
            "cayenneExp": f"seasonId={season}"
        }
        return self._make_request(url, params)
    
    # ==================== GAME AND SCHEDULE INFORMATION ====================
    
    def get_schedule(self, date: str = None) -> Optional[Dict]:
        """Get game schedule for a specific date (YYYYMMDD format)"""
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        url = f"{self.web_api_base}/schedule/{date}"
        return self._make_request(url)
    
    def get_game_center(self, game_id: str) -> Optional[Dict]:
        """Get comprehensive game center data"""
        url = f"{self.web_api_base}/gamecenter/{game_id}/feed/live"
        return self._make_request(url)
    
    def get_game_boxscore(self, game_id: str) -> Optional[Dict]:
        """Get game boxscore data"""
        url = f"{self.web_api_base}/gamecenter/{game_id}/boxscore"
        return self._make_request(url)
    
    def get_play_by_play(self, game_id: str) -> Optional[Dict]:
        """Get detailed play-by-play data with coordinates and events"""
        url = f"{self.web_api_base}/gamecenter/{game_id}/play-by-play"
        return self._make_request(url)
    
    # ==================== STANDINGS AND LEADERS ====================
    
    def get_standings(self, date: str = None) -> Optional[Dict]:
        """Get NHL standings as of a specific date"""
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        url = f"{self.web_api_base}/standings/{date}"
        return self._make_request(url)
    
    def get_skater_leaders(self, season: str = "20242025", game_type: int = 2, 
                          category: str = "points", limit: int = 10) -> Optional[Dict]:
        """Get skater statistical leaders"""
        url = f"{self.web_api_base}/skater-stats-leaders/{season}/{game_type}"
        params = {
            "categories": category,
            "limit": limit
        }
        return self._make_request(url, params)
    
    def get_goalie_leaders(self, season: str = "20242025", game_type: int = 2,
                          category: str = "wins", limit: int = 10) -> Optional[Dict]:
        """Get goalie statistical leaders"""
        url = f"{self.web_api_base}/goalie-stats-leaders/{season}/{game_type}"
        params = {
            "categories": category,
            "limit": limit
        }
        return self._make_request(url, params)
    
    # ==================== DRAFT AND PROSPECTS ====================
    
    def get_draft_info(self, season: str = "20242025") -> Optional[Dict]:
        """Get draft information for a specific season"""
        url = f"{self.stats_api_base}/en/draft"
        params = {"cayenneExp": f"seasonId={season}"}
        return self._make_request(url, params)
    
    def get_prospects(self) -> Optional[Dict]:
        """Get prospect information"""
        url = f"{self.stats_api_base}/en/prospect"
        return self._make_request(url)
    
    # ==================== MISCELLANEOUS ====================
    
    def get_awards(self) -> Optional[Dict]:
        """Get NHL awards information"""
        url = f"{self.web_api_base}/awards"
        return self._make_request(url)
    
    def get_countries(self) -> Optional[Dict]:
        """Get country codes for player nationalities"""
        url = f"{self.stats_api_base}/en/country"
        return self._make_request(url)
    
    # ==================== ADVANCED ANALYTICS ====================
    
    def get_advanced_skater_stats(self, season: str = "20242025", game_type: int = 2) -> Optional[Dict]:
        """Get advanced skater statistics (EDGE stats)"""
        url = f"{self.stats_api_base}/en/skater/summary"
        params = {
            "cayenneExp": f"seasonId={season} and gameTypeId={game_type}",
            "limit": 100
        }
        return self._make_request(url, params)
    
    def get_advanced_goalie_stats(self, season: str = "20242025", game_type: int = 2) -> Optional[Dict]:
        """Get advanced goalie statistics"""
        url = f"{self.stats_api_base}/en/goalie/summary"
        params = {
            "cayenneExp": f"seasonId={season} and gameTypeId={game_type}",
            "limit": 50
        }
        return self._make_request(url, params)
    
    # ==================== GAME ANALYSIS HELPERS ====================
    
    def find_recent_game(self, team1_abbrev: str, team2_abbrev: str, days_back: int = 30) -> Optional[str]:
        """Find the most recent game between two teams"""
        team1_id = self.team_abbrevs.get(team1_abbrev.upper())
        team2_id = self.team_abbrevs.get(team2_abbrev.upper())
        
        if not team1_id or not team2_id:
            print(f"Team abbreviation not found: {team1_abbrev} or {team2_abbrev}")
            return None
        
        # Search through recent dates
        for i in range(days_back):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y%m%d")
            
            schedule = self.get_schedule(date_str)
            if schedule and 'gameWeek' in schedule:
                for day in schedule['gameWeek']:
                    for game in day.get('games', []):
                        away_id = game.get('awayTeam', {}).get('id')
                        home_id = game.get('homeTeam', {}).get('id')
                        
                        if ((away_id == team1_id and home_id == team2_id) or 
                            (away_id == team2_id and home_id == team1_id)):
                            return str(game['id'])
        
        return None
    
    def get_comprehensive_game_data(self, game_id: str) -> Dict:
        """Get all available data for a specific game"""
        print(f"Fetching comprehensive data for game {game_id}...")
        
        data = {
            'game_center': self.get_game_center(game_id),
            'boxscore': self.get_game_boxscore(game_id),
            'play_by_play': self.get_play_by_play(game_id)
        }
        
        # Add standings context
        try:
            game_center = data['game_center']
            if game_center and 'game' in game_center:
                game_date = game_center['game']['gameDate']
                # Convert to YYYYMMDD format for standings
                date_obj = datetime.strptime(game_date, "%Y-%m-%d")
                standings_date = date_obj.strftime("%Y%m%d")
                data['standings'] = self.get_standings(standings_date)
        except Exception as e:
            print(f"Could not fetch standings: {e}")
            data['standings'] = None
        
        return data
    
    def get_player_comparison_data(self, player_ids: List[int], season: str = "20242025") -> Dict:
        """Get comparison data for multiple players"""
        comparison_data = {}
        
        for player_id in player_ids:
            print(f"Fetching data for player {player_id}...")
            comparison_data[player_id] = {
                'profile': self.get_player_profile(player_id),
                'game_log': self.get_player_game_log(player_id, season),
                'season_stats': None  # Will be filled from league stats
            }
        
        return comparison_data
    
    def get_team_context(self, team_abbrev: str, season: str = "20242025") -> Dict:
        """Get comprehensive team context including roster, stats, and standings"""
        team_id = self.team_abbrevs.get(team_abbrev.upper())
        if not team_id:
            return {}
        
        print(f"Fetching team context for {team_abbrev}...")
        
        return {
            'team_info': self.get_team_info(team_id, season),
            'roster': self.get_team_roster(team_abbrev, season),
            'standings': self.get_standings(),
            'recent_games': self._get_recent_team_games(team_abbrev, days_back=10)
        }
    
    def _get_recent_team_games(self, team_abbrev: str, days_back: int = 10) -> List[Dict]:
        """Get recent games for a team"""
        team_id = self.team_abbrevs.get(team_abbrev.upper())
        if not team_id:
            return []
        
        recent_games = []
        
        for i in range(days_back):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y%m%d")
            
            schedule = self.get_schedule(date_str)
            if schedule and 'gameWeek' in schedule:
                for day in schedule['gameWeek']:
                    for game in day.get('games', []):
                        away_id = game.get('awayTeam', {}).get('id')
                        home_id = game.get('homeTeam', {}).get('id')
                        
                        if away_id == team_id or home_id == team_id:
                            recent_games.append(game)
        
        return recent_games
    
    # ==================== UTILITY METHODS ====================
    
    def get_current_season(self) -> str:
        """Get the current NHL season in YYYY YYYY format"""
        now = datetime.now()
        if now.month >= 10:  # Season starts in October
            return f"{now.year}{now.year + 1}"
        else:
            return f"{now.year - 1}{now.year}"
    
    def format_game_id(self, date: str, game_number: int = 1) -> str:
        """Format a game ID from date and game number
        date: YYYYMMDD format
        game_number: 1-999
        """
        return f"{date}{game_number:03d}"
    
    def parse_game_id(self, game_id: str) -> Dict:
        """Parse a game ID to extract date and game number"""
        if len(game_id) != 11:
            return {}
        
        date_str = game_id[:8]
        game_num = int(game_id[8:])
        
        try:
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            return {
                'date': date_obj,
                'date_str': date_str,
                'game_number': game_num,
                'season': self.get_season_from_date(date_obj)
            }
        except ValueError:
            return {}
    
    def get_season_from_date(self, date: datetime) -> str:
        """Get the NHL season from a date"""
        if date.month >= 10:  # Season starts in October
            return f"{date.year}{date.year + 1}"
        else:
            return f"{date.year - 1}{date.year}"
    
    def validate_team_abbrev(self, abbrev: str) -> bool:
        """Validate if a team abbreviation exists"""
        return abbrev.upper() in self.team_abbrevs
    
    def get_team_name_from_abbrev(self, abbrev: str) -> str:
        """Get full team name from abbreviation"""
        # Simple mapping to avoid recursion
        team_names = {
            'EDM': 'Edmonton Oilers', 'FLA': 'Florida Panthers', 'BOS': 'Boston Bruins',
            'TOR': 'Toronto Maple Leafs', 'MTL': 'Montreal Canadiens', 'OTT': 'Ottawa Senators',
            'BUF': 'Buffalo Sabres', 'DET': 'Detroit Red Wings', 'TBL': 'Tampa Bay Lightning',
            'CAR': 'Carolina Hurricanes', 'WSH': 'Washington Capitals', 'PIT': 'Pittsburgh Penguins',
            'NYR': 'New York Rangers', 'NYI': 'New York Islanders', 'NJD': 'New Jersey Devils',
            'PHI': 'Philadelphia Flyers', 'CBJ': 'Columbus Blue Jackets', 'NSH': 'Nashville Predators',
            'STL': 'St. Louis Blues', 'MIN': 'Minnesota Wild', 'WPG': 'Winnipeg Jets',
            'COL': 'Colorado Avalanche', 'ARI': 'Arizona Coyotes', 'VGK': 'Vegas Golden Knights',
            'SJS': 'San Jose Sharks', 'LAK': 'Los Angeles Kings', 'ANA': 'Anaheim Ducks',
            'CGY': 'Calgary Flames', 'VAN': 'Vancouver Canucks', 'SEA': 'Seattle Kraken',
            'CHI': 'Chicago Blackhawks', 'DAL': 'Dallas Stars'
        }
        return team_names.get(abbrev.upper(), abbrev.upper())
    
    def get_team_abbrev_from_id(self, team_id: int) -> str:
        """Get team abbreviation from team ID"""
        return self.team_ids.get(team_id, f"UNK{team_id}")


# Example usage and testing
if __name__ == "__main__":
    # Initialize the enhanced client
    client = EnhancedNHLAPIClient()
    
    print("🏒 Enhanced NHL API Client - 2025 Edition 🏒")
    print("=" * 50)
    
    # Test basic functionality
    print("Testing API connectivity...")
    
    # Test standings
    standings = client.get_standings()
    if standings:
        print("✅ Standings API working")
    else:
        print("❌ Standings API failed")
    
    # Test schedule
    schedule = client.get_schedule()
    if schedule:
        print("✅ Schedule API working")
    else:
        print("❌ Schedule API failed")
    
    # Test team info
    team_info = client.get_team_info(22)  # Edmonton Oilers
    if team_info:
        print("✅ Team info API working")
    else:
        print("❌ Team info API failed")
    
    # Test player stats
    skater_stats = client.get_skater_stats(limit=5)
    if skater_stats:
        print("✅ Skater stats API working")
    else:
        print("❌ Skater stats API failed")
    
    print("\n🎯 Enhanced NHL API Client ready for advanced reports!")
