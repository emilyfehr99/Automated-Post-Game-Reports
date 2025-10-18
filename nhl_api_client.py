import requests
import json
from datetime import datetime, timedelta
import pandas as pd

class NHLAPIClient:
    def __init__(self):
        self.base_url = "https://api-web.nhle.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_team_info(self, team_id):
        """Get team information by team ID"""
        url = f"{self.base_url}/teams/{team_id}"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_team_roster(self, team_id):
        """Get team roster by team ID"""
        url = f"{self.base_url}/teams/{team_id}/roster"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_game_schedule(self, date=None):
        """Get game schedule for a specific date"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        url = f"{self.base_url}/schedule/{date}"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_game_center(self, game_id):
        """Get detailed game information"""
        url = f"{self.base_url}/gamecenter/{game_id}/feed/live"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_game_boxscore(self, game_id):
        """Get game boxscore"""
        url = f"{self.base_url}/gamecenter/{game_id}/boxscore"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_player_stats(self, player_id):
        """Get player statistics"""
        url = f"{self.base_url}/players/{player_id}/stats"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def find_recent_game(self, team1_abbrev, team2_abbrev, days_back=30):
        """Find the most recent game between two teams"""
        # Get team IDs from abbreviations
        team_ids = {
            'FLA': 13, 'EDM': 22, 'BOS': 6, 'TOR': 10, 'MTL': 8, 'OTT': 9,
            'BUF': 7, 'DET': 17, 'TBL': 14, 'CAR': 12, 'WSH': 15, 'PIT': 5,
            'NYR': 3, 'NYI': 2, 'NJD': 1, 'PHI': 4, 'CBJ': 29, 'NSH': 18,
            'STL': 19, 'MIN': 30, 'WPG': 52, 'COL': 21, 'ARI': 53, 'VGK': 54,
            'SJS': 28, 'LAK': 26, 'ANA': 24, 'CGY': 20, 'VAN': 23, 'SEA': 55,
            'CHI': 16, 'DAL': 25
        }
        
        team1_id = team_ids.get(team1_abbrev.upper())
        team2_id = team_ids.get(team2_abbrev.upper())
        
        if not team1_id or not team2_id:
            raise ValueError(f"Team abbreviation not found: {team1_abbrev} or {team2_id}")
        
        # Search through recent dates for the game
        for i in range(days_back):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            schedule = self.get_game_schedule(date_str)
            if schedule and 'gameWeek' in schedule:
                for day in schedule['gameWeek']:
                    for game in day.get('games', []):
                        if (game.get('awayTeam', {}).get('id') == team1_id and 
                            game.get('homeTeam', {}).get('id') == team2_id) or \
                           (game.get('awayTeam', {}).get('id') == team2_id and 
                            game.get('homeTeam', {}).get('id') == team1_id):
                            return game['id']
        
        return None
    
    def get_stanley_cup_finals_game(self):
        """Get the most recent Stanley Cup Finals game between FLA and EDM"""
        # For Stanley Cup Finals, we'll look for recent games between these teams
        # Since this is a specific request, we'll search for recent matchups
        return self.find_recent_game('FLA', 'EDM', days_back=60)
    
    def get_comprehensive_game_data(self, game_id):
        """Get comprehensive game data including boxscore and play-by-play"""
        game_center = self.get_game_center(game_id)
        boxscore = self.get_game_boxscore(game_id)
        
        return {
            'game_center': game_center,
            'boxscore': boxscore
        }
