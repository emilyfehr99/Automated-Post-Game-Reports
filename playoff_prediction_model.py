#!/usr/bin/env python3
"""
Playoff Prediction Model
Uses daily scraped data to calculate playoff probabilities
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

class PlayoffPredictionModel:
    def __init__(self):
        """Initialize the playoff prediction model"""
        self.model = ImprovedSelfLearningModelV2()
        self.model.deterministic = True
        
        # Load team stats
        self.team_stats_file = Path("season_2025_2026_team_stats.json")
        self.team_stats = self.load_team_stats()
    
    def load_team_stats(self) -> Dict:
        """Load current season team statistics"""
        try:
            if self.team_stats_file.exists():
                with open(self.team_stats_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading team stats: {e}")
        return {}
    
    def get_current_standings(self) -> Dict:
        """Get current NHL standings from API"""
        try:
            import requests
            url = 'https://api-web.nhle.com/v1/standings/now'
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error getting standings: {e}")
        return {}
    
    def calculate_playoff_probabilities(self, num_simulations: int = 10000) -> Dict:
        """
        Calculate playoff probabilities for each team by simulating remaining games
        
        Returns:
            Dict with team abbreviations as keys and playoff probability as values
        """
        # Get current standings
        standings_data = self.get_current_standings()
        if not standings_data or 'standings' not in standings_data:
            return {}
        
        # Build current records
        team_records = {}
        
        for team_data in standings_data.get('standings', []):
            team_abbrev = team_data.get('teamAbbrev', {}).get('default', '')
            if not team_abbrev:
                continue
            
            wins = team_data.get('wins', 0)
            ot_losses = team_data.get('otLosses', 0)
            losses = team_data.get('losses', 0)
            points = wins * 2 + ot_losses  # NHL point system: 2 for win, 1 for OT loss
            
            # Determine conference
            conference = team_data.get('conferenceName', {}).get('default', '')
            division = team_data.get('divisionName', {}).get('default', '')
            
            team_records[team_abbrev] = {
                'wins': wins,
                'losses': losses,
                'ot_losses': ot_losses,
                'points': points,
                'games_played': wins + losses + ot_losses,
                'conference': conference,
                'division': division
            }
        
        # Get remaining schedule (82 total games in season)
        remaining_games = {}
        for team_abbrev, record in team_records.items():
            games_played = record['games_played']
            remaining_games[team_abbrev] = max(0, 82 - games_played)
        
        # Simulate remaining season
        playoff_counts = {team: 0 for team in team_records.keys()}
        
        for sim in range(num_simulations):
            # Create simulated final standings
            sim_records = {}
            for team_abbrev, record in team_records.items():
                sim_points = record['points']
                remaining = remaining_games[team_abbrev]
                
                # Simulate remaining games based on team strength
                team_strength = self._estimate_team_strength(team_abbrev)
                
                # Estimate points from remaining games
                # Average NHL team gets ~0.55 points per game
                # Adjust based on team strength
                expected_points_per_game = 0.55 + (team_strength - 0.5) * 0.3
                sim_points += remaining * expected_points_per_game * 2  # Convert to points
                
                sim_records[team_abbrev] = {
                    'points': sim_points,
                    'conference': record['conference']
                }
            
            # Determine playoff teams (top 8 in each conference)
            eastern_teams = [(team, data['points']) for team, data in sim_records.items() 
                            if data['conference'] in ['Eastern', 'EASTERN']]
            western_teams = [(team, data['points']) for team, data in sim_records.items() 
                            if data['conference'] in ['Western', 'WESTERN']]
            
            # Sort by points (descending)
            eastern_teams.sort(key=lambda x: x[1], reverse=True)
            western_teams.sort(key=lambda x: x[1], reverse=True)
            
            # Count playoff teams
            for team, _ in eastern_teams[:8]:
                playoff_counts[team] += 1
            for team, _ in western_teams[:8]:
                playoff_counts[team] += 1
        
        # Calculate probabilities
        playoff_probs = {}
        for team, count in playoff_counts.items():
            prob = count / num_simulations
            record = team_records.get(team, {})
            playoff_probs[team] = {
                'playoff_probability': prob,
                'current_points': record.get('points', 0),
                'games_played': record.get('games_played', 0),
                'remaining_games': remaining_games.get(team, 0),
                'conference': record.get('conference', ''),
                'wins': record.get('wins', 0),
                'losses': record.get('losses', 0),
                'ot_losses': record.get('ot_losses', 0)
            }
        
        return playoff_probs
    
    def _estimate_team_strength(self, team_abbrev: str) -> float:
        """Estimate team strength (0-1 scale) based on current stats"""
        if not self.team_stats or 'teams' not in self.team_stats:
            return 0.5  # Average
        
        team_data = self.team_stats['teams'].get(team_abbrev, {})
        if not team_data or team_data.get('games_played', 0) < 10:
            return 0.5
        
        # Normalize metrics to 0-1 scale
        xg_avg = team_data.get('xg_avg', 0)
        gs_avg = team_data.get('gs_avg', 0)
        
        # NHL average is around 2.8-3.0 xG per game
        # Scale to 0-1 (assuming range of 2.0-4.0)
        xg_normalized = max(0, min(1, (xg_avg - 2.0) / 2.0))
        
        # Game score average (typically 3.5-5.0)
        gs_normalized = max(0, min(1, (gs_avg - 3.0) / 2.0))
        
        # Weighted average
        strength = (xg_normalized * 0.6 + gs_normalized * 0.4)
        
        return max(0.0, min(1.0, strength))

