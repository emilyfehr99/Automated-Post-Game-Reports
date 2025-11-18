#!/usr/bin/env python3
"""
Playoff Prediction Model
Uses daily scraped data and full prediction model to calculate playoff probabilities
Simulates remaining games using actual schedule and comprehensive metrics
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pytz
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from nhl_api_client import NHLAPIClient
from correlation_model import CorrelationModel
from lineup_service import LineupService

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

class PlayoffPredictionModel:
    def __init__(self):
        """Initialize the playoff prediction model"""
        self.model = ImprovedSelfLearningModelV2()
        # Don't use deterministic mode - we need randomness for simulations
        self.model.deterministic = False
        self.api = NHLAPIClient()
        self.corr_model = CorrelationModel()
        self.lineup_service = LineupService()
        
        # Load team stats
        self.team_stats_file = Path("season_2025_2026_team_stats.json")
        self.team_stats = self.load_team_stats()
        
        # Cache for remaining schedule
        self._remaining_schedule_cache = None
        self._schedule_cache_date = None
    
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
    
    def get_remaining_schedule(self) -> List[Dict]:
        """
        Get all remaining games in the season from NHL API
        Returns list of games with away_team, home_team, and date
        """
        # Cache schedule for today
        today = datetime.now(pytz.timezone('US/Central')).strftime('%Y-%m-%d')
        if self._remaining_schedule_cache and self._schedule_cache_date == today:
            return self._remaining_schedule_cache
        
        remaining_games = []
        today_dt = datetime.now(pytz.timezone('US/Central'))
        
        # Get schedule for next 90 days (covers rest of season, reduced for performance)
        for days_ahead in range(90):
            date = today_dt + timedelta(days=days_ahead)
            date_str = date.strftime('%Y-%m-%d')
            
            try:
                schedule = self.api.get_game_schedule(date_str)
                if schedule and 'gameWeek' in schedule:
                    for day in schedule.get('gameWeek', []):
                        if day.get('date') != date_str:
                            continue
                        for game in day.get('games', []):
                            game_state = game.get('gameState', '')
                            # Only include future games (PREVIEW or not started)
                            if game_state in ['PREVIEW', 'LIVE', 'CRIT']:
                                away_team_obj = game.get('awayTeam', {})
                                home_team_obj = game.get('homeTeam', {})
                                
                                # Handle team abbrev - could be dict or string
                                away_abbrev = away_team_obj.get('abbrev', {})
                                if isinstance(away_abbrev, dict):
                                    away_abbrev = away_abbrev.get('default', '')
                                
                                home_abbrev = home_team_obj.get('abbrev', {})
                                if isinstance(home_abbrev, dict):
                                    home_abbrev = home_abbrev.get('default', '')
                                
                                if away_abbrev and home_abbrev:
                                    remaining_games.append({
                                        'away_team': away_abbrev,
                                        'home_team': home_abbrev,
                                        'date': date_str,
                                        'game_id': game.get('id')
                                    })
            except Exception as e:
                print(f"Error fetching schedule for {date_str}: {e}")
                continue
        
        self._remaining_schedule_cache = remaining_games
        self._schedule_cache_date = today
        return remaining_games
    
    def predict_game_outcome(self, away_team: str, home_team: str, game_date: str, game_id: Optional[str] = None) -> Dict:
        """
        Predict a single game using the full prediction model
        Returns dict with 'away_prob', 'home_prob', and 'predicted_winner'
        """
        try:
            # Use the same prediction logic as run_predictions_for_date
            from run_predictions_for_date import predict_game_for_date
            
            prediction = predict_game_for_date(
                self.model,
                self.corr_model,
                away_team,
                home_team,
                game_date,
                game_id=game_id,
                lineup_service=self.lineup_service
            )
            
            if prediction:
                away_prob = prediction.get('away_prob', 0.5)
                home_prob = prediction.get('home_prob', 0.5)
                
                # Normalize to 0-1 range (predict_game_for_date returns 0-1, but ensemble_predict might return 0-100)
                if away_prob > 1.0:
                    away_prob = away_prob / 100.0
                if home_prob > 1.0:
                    home_prob = home_prob / 100.0
                
                # Ensure they sum to 1.0
                total = away_prob + home_prob
                if total > 0:
                    away_prob = away_prob / total
                    home_prob = home_prob / total
                else:
                    away_prob = 0.5
                    home_prob = 0.5
                
                # Calculate confidence based on how far from 50/50
                # Confidence = distance from 0.5, scaled to 0-1, then to percentage
                max_prob = max(away_prob, home_prob)
                confidence = abs(max_prob - 0.5) * 2  # 0 to 1 scale
                confidence_pct = confidence * 100  # Convert to percentage
                
                predicted_winner = home_team if home_prob > away_prob else away_team
                
                return {
                    'away_prob': away_prob,
                    'home_prob': home_prob,
                    'predicted_winner': predicted_winner,
                    'confidence': confidence_pct
                }
        except Exception as e:
            print(f"Error predicting {away_team} @ {home_team}: {e}")
        
        # Fallback to 50/50 if prediction fails
        return {
            'away_prob': 0.5,
            'home_prob': 0.5,
            'predicted_winner': home_team  # Default to home team
        }
    
    def simulate_game(self, away_team: str, home_team: str, away_prob: float, home_prob: float) -> Tuple[str, int, int]:
        """
        Simulate a single game outcome with proper randomness
        Returns (winner, points_for_away, points_for_home)
        Points: 2 for win, 1 for OT loss, 0 for regulation loss
        """
        # Use random seed per simulation to ensure variance
        rand = random.random()
        
        # Normalize probabilities (handle both 0-1 and 0-100 formats)
        # If probabilities are > 1, they're in percentage format
        if away_prob > 1.0 or home_prob > 1.0:
            away_prob = away_prob / 100.0
            home_prob = home_prob / 100.0
        
        total_prob = away_prob + home_prob
        if total_prob > 0:
            away_prob_norm = away_prob / total_prob
            home_prob_norm = home_prob / total_prob
        else:
            away_prob_norm = 0.5
            home_prob_norm = 0.5
        
        # Add some variance to prevent deterministic outcomes
        # Even strong favorites can lose sometimes
        variance = 0.05  # 5% chance of upset regardless of prediction
        if random.random() < variance:
            # Upset: flip the probabilities
            away_prob_norm, home_prob_norm = home_prob_norm, away_prob_norm
        
        # Determine winner (with OT probability ~20% of games)
        if rand < away_prob_norm:
            # Away team wins
            # 20% chance of OT win
            if random.random() < 0.2:
                return (away_team, 2, 1)  # Away wins in OT, home gets 1 point
            else:
                return (away_team, 2, 0)  # Away wins in regulation
        else:
            # Home team wins
            if random.random() < 0.2:
                return (home_team, 1, 2)  # Home wins in OT, away gets 1 point
            else:
                return (home_team, 0, 2)  # Home wins in regulation
    
    def calculate_playoff_probabilities(self, num_simulations: int = 1000) -> Dict:
        """
        Calculate playoff probabilities by simulating remaining games using full prediction model
        Uses actual schedule, head-to-head records, goalie performance, and all advanced metrics
        
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
            # Handle teamAbbrev - could be dict or string
            team_abbrev_obj = team_data.get('teamAbbrev', {})
            if isinstance(team_abbrev_obj, dict):
                team_abbrev = team_abbrev_obj.get('default', '')
            else:
                team_abbrev = str(team_abbrev_obj) if team_abbrev_obj else ''
            
            if not team_abbrev:
                continue
            
            wins = team_data.get('wins', 0)
            ot_losses = team_data.get('otLosses', 0)
            losses = team_data.get('losses', 0)
            points = wins * 2 + ot_losses  # NHL point system: 2 for win, 1 for OT loss
            
            # Determine conference - could be dict or string
            conference_obj = team_data.get('conferenceName', {})
            if isinstance(conference_obj, dict):
                conference = conference_obj.get('default', '')
            else:
                conference = str(conference_obj) if conference_obj else ''
            
            # Determine division - could be dict or string
            division_obj = team_data.get('divisionName', {})
            if isinstance(division_obj, dict):
                division = division_obj.get('default', '')
            else:
                division = str(division_obj) if division_obj else ''
            
            team_records[team_abbrev] = {
                'wins': wins,
                'losses': losses,
                'ot_losses': ot_losses,
                'points': points,
                'games_played': wins + losses + ot_losses,
                'conference': conference,
                'division': division
            }
        
        # Get remaining schedule
        remaining_games = self.get_remaining_schedule()
        print(f"Found {len(remaining_games)} remaining games in schedule")
        
        if not remaining_games or len(remaining_games) < 10:
            print("WARNING: Very few remaining games found. This may cause inaccurate probabilities.")
            # If we have very few games, the current standings will dominate
            # This is expected if we're late in the season
        
        # Pre-predict all remaining games (cache predictions)
        # Limit to reasonable number for performance
        max_games_to_predict = 500  # Cap at 500 games to avoid timeout
        games_to_predict = remaining_games[:max_games_to_predict]
        
        print(f"Predicting {len(games_to_predict)} remaining games (out of {len(remaining_games)} total)...")
        game_predictions = {}
        sample_predictions = []  # For debugging
        
        for i, game in enumerate(games_to_predict):
            away = game['away_team']
            home = game['home_team']
            if away == 'OPP' or home == 'OPP':
                continue  # Skip placeholder games
            
            game_key = f"{away}@{home}_{game['date']}"
            if game_key not in game_predictions:
                try:
                    pred = self.predict_game_outcome(away, home, game['date'], game.get('game_id'))
                    game_predictions[game_key] = pred
                    
                    # Collect sample predictions for debugging
                    if len(sample_predictions) < 5:
                        sample_predictions.append(f"{away}@{home}: away={pred['away_prob']:.3f}, home={pred['home_prob']:.3f}")
                except Exception as e:
                    print(f"Error predicting {away} @ {home}: {e}")
                    import traceback
                    traceback.print_exc()
                    # Use fallback prediction
                    game_predictions[game_key] = {'away_prob': 0.5, 'home_prob': 0.5}
            
            # Progress indicator
            if (i + 1) % 50 == 0:
                print(f"  Predicted {i + 1}/{len(games_to_predict)} games...")
        
        print(f"Cached {len(game_predictions)} game predictions")
        if sample_predictions:
            print(f"Sample predictions: {', '.join(sample_predictions)}")
        
        # Verify predictions are varying (not all 50/50)
        if len(game_predictions) > 0:
            probs = [p['away_prob'] for p in game_predictions.values()]
            avg_prob = sum(probs) / len(probs)
            min_prob = min(probs)
            max_prob = max(probs)
            print(f"Prediction variance: avg={avg_prob:.3f}, min={min_prob:.3f}, max={max_prob:.3f}")
            if max_prob - min_prob < 0.1:
                print("WARNING: Predictions have very low variance! They may not be working correctly.")
        
        # Simulate remaining season
        playoff_counts = {team: 0 for team in team_records.keys()}
        
        print(f"Running {num_simulations} simulations...")
        print(f"Using {len(game_predictions)} cached predictions for {len(games_to_predict)} games")
        
        for sim in range(num_simulations):
            if (sim + 1) % 200 == 0:
                print(f"  Completed {sim + 1}/{num_simulations} simulations...")
            # Start with current points
            sim_points = {team: record['points'] for team, record in team_records.items()}
            
            # Simulate each remaining game (only use games we predicted)
            games_simulated = 0
            for game in games_to_predict:
                away = game['away_team']
                home = game['home_team']
                
                if away == 'OPP' or home == 'OPP' or away not in sim_points or home not in sim_points:
                    continue
                
                game_key = f"{away}@{home}_{game['date']}"
                pred = game_predictions.get(game_key)
                
                if pred and 'away_prob' in pred and 'home_prob' in pred:
                    winner, away_pts, home_pts = self.simulate_game(
                        away, home, pred['away_prob'], pred['home_prob']
                    )
                    sim_points[away] += away_pts
                    sim_points[home] += home_pts
                    games_simulated += 1
            
            # Debug: show sample simulation results for first sim
            if sim == 0 and games_simulated > 0:
                sample_teams = list(sim_points.items())[:5]
                print(f"Sample simulation results (first sim): {sample_teams}")
            
            # Determine playoff teams (top 8 in each conference)
            eastern_teams = [(team, sim_points[team]) for team, data in team_records.items() 
                            if data['conference'] in ['Eastern', 'EASTERN'] and team in sim_points]
            western_teams = [(team, sim_points[team]) for team, data in team_records.items() 
                            if data['conference'] in ['Western', 'WESTERN'] and team in sim_points]
            
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
        remaining_game_counts = {}
        for game in games_to_predict:
            away = game['away_team']
            home = game['home_team']
            if away != 'OPP' and home != 'OPP':
                remaining_game_counts[away] = remaining_game_counts.get(away, 0) + 1
                remaining_game_counts[home] = remaining_game_counts.get(home, 0) + 1
        
        # Debug: show playoff counts
        print(f"\nPlayoff counts (sample):")
        sample_counts = sorted(playoff_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for team, count in sample_counts:
            print(f"  {team}: {count}/{num_simulations} ({count/num_simulations*100:.1f}%)")
        
        for team, count in playoff_counts.items():
            prob = count / num_simulations
            record = team_records.get(team, {})
            playoff_probs[team] = {
                'playoff_probability': prob,
                'current_points': record.get('points', 0),
                'games_played': record.get('games_played', 0),
                'remaining_games': remaining_game_counts.get(team, 0),
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

