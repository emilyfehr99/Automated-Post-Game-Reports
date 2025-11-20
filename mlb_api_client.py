#!/usr/bin/env python3
"""
MLB API Client
Fetches player and team data from the official MLB API
"""

import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import time

class MLBAPIClient:
    def __init__(self):
        self.base_url = "https://statsapi.mlb.com/api/v1"
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
    
    def get_player_info(self, player_id):
        """Get player information by player ID"""
        url = f"{self.base_url}/people/{player_id}"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_player_stats(self, player_id, season=2024, stat_type="hitting"):
        """Get player statistics for a specific season"""
        url = f"{self.base_url}/people/{player_id}/stats"
        params = {
            'stats': stat_type,
            'season': season,
            'group': 'hitting' if stat_type == 'hitting' else 'pitching'
        }
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_player_game_log(self, player_id, season=2024):
        """Get player's game log for a season"""
        url = f"{self.base_url}/people/{player_id}/stats"
        params = {
            'stats': 'gameLog',
            'season': season
        }
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_team_roster(self, team_id, season=2024):
        """Get team roster for a specific season"""
        url = f"{self.base_url}/teams/{team_id}/roster"
        params = {'season': season}
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_schedule(self, team_id, start_date=None, end_date=None):
        """Get team schedule for date range"""
        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if end_date is None:
            end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        url = f"{self.base_url}/schedule"
        params = {
            'sportId': 1,  # MLB
            'teamId': team_id,
            'startDate': start_date,
            'endDate': end_date
        }
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_game_data(self, game_id):
        """Get detailed game data"""
        url = f"{self.base_url}/game/{game_id}/boxscore"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_play_by_play(self, game_id):
        """Get play-by-play data for a game"""
        url = f"{self.base_url}/game/{game_id}/playByPlay"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def search_player(self, name):
        """Search for a player by name"""
        url = f"{self.base_url}/people/search"
        params = {'names': name}
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_team_ids(self):
        """Get all MLB team IDs and names"""
        teams = {
            'LAD': 119,  # Los Angeles Dodgers
            'TOR': 141,  # Toronto Blue Jays
            'NYY': 147,  # New York Yankees
            'BOS': 111,  # Boston Red Sox
            'TB': 139,    # Tampa Bay Rays
            'BAL': 110,   # Baltimore Orioles
            'HOU': 117,   # Houston Astros
            'TEX': 142,   # Texas Rangers
            'SEA': 136,   # Seattle Mariners
            'LAA': 108,   # Los Angeles Angels
            'OAK': 133,   # Oakland Athletics
            'ATL': 144,   # Atlanta Braves
            'PHI': 143,   # Philadelphia Phillies
            'NYM': 121,   # New York Mets
            'MIA': 146,   # Miami Marlins
            'WSH': 120,   # Washington Nationals
            'CHC': 112,   # Chicago Cubs
            'MIL': 158,   # Milwaukee Brewers
            'STL': 138,   # St. Louis Cardinals
            'PIT': 134,   # Pittsburgh Pirates
            'CIN': 113,   # Cincinnati Reds
            'CLE': 114,   # Cleveland Guardians
            'DET': 116,   # Detroit Tigers
            'KC': 118,    # Kansas City Royals
            'MIN': 142,   # Minnesota Twins
            'CWS': 145,   # Chicago White Sox
            'SF': 137,    # San Francisco Giants
            'SD': 135,    # San Diego Padres
            'COL': 115,   # Colorado Rockies
            'ARI': 109    # Arizona Diamondbacks
        }
        return teams
    
    def get_comprehensive_player_data(self, player_id, season=2024):
        """Get comprehensive player data including stats and game log"""
        player_info = self.get_player_info(player_id)
        hitting_stats = self.get_player_stats(player_id, season, "hitting")
        pitching_stats = self.get_player_stats(player_id, season, "pitching")
        game_log = self.get_player_game_log(player_id, season)
        
        return {
            'player_info': player_info,
            'hitting_stats': hitting_stats,
            'pitching_stats': pitching_stats,
            'game_log': game_log
        }
    
    def find_player_by_name(self, name):
        """Find player ID by name"""
        search_results = self.search_player(name)
        if search_results and 'people' in search_results:
            for person in search_results['people']:
                if person.get('fullName', '').lower() == name.lower():
                    return person.get('id')
        return None
