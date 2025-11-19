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

# Don't set global random seed - we need variance in simulations
# Each simulation will use different random values

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
        Predict a single game using DATA-DRIVEN approach:
        - 70% Team Strength (comprehensive metrics)
        - 20% Recent Form
        - 10% Base prediction model (includes standings context)
        Returns dict with 'away_prob', 'home_prob', and 'predicted_winner'
        """
        try:
            # 1. CALCULATE TEAM STRENGTH (70% weight) - PRIMARY FACTOR
            away_strength_data = self.calculate_comprehensive_team_strength(away_team)
            home_strength_data = self.calculate_comprehensive_team_strength(home_team)
            
            away_strength = away_strength_data['strength_score']
            home_strength = home_strength_data['strength_score']
            
            # Convert strength difference to probability
            # Strength difference: -1 to +1, where positive = away team stronger
            strength_diff = away_strength - home_strength
            
            # Convert strength difference to base probabilities
            # Use sigmoid-like function: strength_diff of +0.3 = ~65% away win
            strength_base_away = 0.5 + (strength_diff * 0.4)  # Max swing of ±0.4 from 50%
            strength_base_home = 1.0 - strength_base_away
            
            # 2. GET RECENT FORM (20% weight) - SECONDARY FACTOR
            away_form = self.get_recent_team_form(away_team, num_games=15)
            home_form = self.get_recent_team_form(home_team, num_games=15)
            
            form_diff = away_form['form_score'] - home_form['form_score']
            
            # Form adjustment: max ±0.15 swing (15%)
            form_adjustment = form_diff * 0.15
            
            # 3. GET BASE PREDICTION (10% weight) - MINIMAL FACTOR (includes standings context)
            try:
                from run_predictions_for_date import predict_game_for_date
                base_prediction = predict_game_for_date(
                self.model,
                self.corr_model,
                away_team,
                home_team,
                game_date,
                game_id=game_id,
                lineup_service=self.lineup_service
            )
            
                if base_prediction:
                    base_away_prob = base_prediction.get('away_prob', 0.5)
                    base_home_prob = base_prediction.get('home_prob', 0.5)
                    
                    # Normalize to 0-1 range
                    if base_away_prob > 1.0:
                        base_away_prob = base_away_prob / 100.0
                    if base_home_prob > 1.0:
                        base_home_prob = base_home_prob / 100.0
                    
                    total_base = base_away_prob + base_home_prob
                    if total_base > 0:
                        base_away_prob = base_away_prob / total_base
                        base_home_prob = base_home_prob / total_base
                else:
                        base_away_prob = 0.5
                        base_home_prob = 0.5
                else:
                    base_away_prob = 0.5
                    base_home_prob = 0.5
            except Exception as e:
                print(f"Warning: Base prediction failed, using 50/50: {e}")
                base_away_prob = 0.5
                base_home_prob = 0.5
            
            # 4. COMBINE ALL FACTORS (70% strength + 20% form + 10% base)
            # Start with strength-based prediction
            away_prob_combined = strength_base_away
            
            # Add form adjustment (20% weight)
            away_prob_combined = away_prob_combined + form_adjustment
            
            # Blend with base prediction (10% weight)
            away_prob_final = away_prob_combined * 0.90 + base_away_prob * 0.10
            home_prob_final = 1.0 - away_prob_final
                
                # Normalize to ensure they sum to 1.0
            total_final = away_prob_final + home_prob_final
            if total_final > 0:
                away_prob_final = away_prob_final / total_final
                home_prob_final = home_prob_final / total_final
                else:
                    away_prob_final = 0.5
                    home_prob_final = 0.5
                
            # Clamp to valid range (5%-95% to prevent extremes)
            away_prob_final = max(0.05, min(0.95, away_prob_final))
            home_prob_final = max(0.05, min(0.95, home_prob_final))
                
                # Renormalize after clamping
                total_final = away_prob_final + home_prob_final
                if total_final > 0:
                    away_prob_final = away_prob_final / total_final
                    home_prob_final = home_prob_final / total_final
                
                # Calculate confidence based on how far from 50/50
                max_prob = max(away_prob_final, home_prob_final)
                confidence = abs(max_prob - 0.5) * 2  # 0 to 1 scale
                confidence_pct = confidence * 100  # Convert to percentage
                
                predicted_winner = home_team if home_prob_final > away_prob_final else away_team
                
                return {
                    'away_prob': away_prob_final,
                    'home_prob': home_prob_final,
                    'predicted_winner': predicted_winner,
                    'confidence': confidence_pct,
                'away_strength': away_strength,
                'home_strength': home_strength,
                'strength_diff': strength_diff,
                    'form_adjustment': form_adjustment,
                    'away_form_score': away_form['form_score'],
                'home_form_score': home_form['form_score'],
                'base_away_prob': base_away_prob,
                'base_home_prob': base_home_prob
                }
        except Exception as e:
            print(f"Error predicting {away_team} @ {home_team}: {e}")
            import traceback
            traceback.print_exc()
        
        # Fallback to 50/50 if prediction fails
        return {
            'away_prob': 0.5,
            'home_prob': 0.5,
            'predicted_winner': home_team
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
        
        # Add more variance to prevent deterministic outcomes
        # Even strong favorites can lose sometimes - increase variance for more realistic simulations
        variance = 0.12  # 12% chance of upset regardless of prediction (increased from 5%)
        if random.random() < variance:
            # Upset: flip the probabilities
            away_prob_norm, home_prob_norm = home_prob_norm, away_prob_norm
        
        # Add additional randomness based on probability spread
        # If probabilities are very lopsided, add more variance
        prob_spread = abs(away_prob_norm - home_prob_norm)
        if prob_spread > 0.3:  # If one team is heavily favored
            # Add extra variance (5-15% chance of additional upset)
            extra_variance = 0.05 + (prob_spread - 0.3) * 0.2
            if random.random() < extra_variance:
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
        
        # Calculate season progress to cap probabilities appropriately
        # NHL teams play 82 games per season
        NHL_GAMES_PER_SEASON = 82
        avg_games_played = sum(record['games_played'] for record in team_records.values()) / len(team_records) if team_records else 0
        season_progress = avg_games_played / NHL_GAMES_PER_SEASON  # 0.0 to 1.0
        
        print(f"\nSeason progress: {avg_games_played:.1f} games played ({(season_progress*100):.1f}% of season)")
        
        # Calculate max probability cap based on season progress
        # Early season (< 20 games): max 60%
        # Mid season (20-50 games): max 80%
        # Late season (50-70 games): max 95%
        # Very late season (> 70 games): max 99%
        if avg_games_played < 20:
            max_probability_cap = 0.60
            print(f"Early season detected - capping probabilities at {max_probability_cap*100:.0f}%")
        elif avg_games_played < 50:
            max_probability_cap = 0.80
            print(f"Mid season detected - capping probabilities at {max_probability_cap*100:.0f}%")
        elif avg_games_played < 70:
            max_probability_cap = 0.95
            print(f"Late season detected - capping probabilities at {max_probability_cap*100:.0f}%")
        else:
            max_probability_cap = 0.99
            print(f"Very late season detected - capping probabilities at {max_probability_cap*100:.0f}%")
        
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
                    if len(sample_predictions) < 10:
                        conf = pred.get('confidence', 0.0)
                        sample_predictions.append(f"{away}@{home}: away={pred['away_prob']:.3f}, home={pred['home_prob']:.3f}, conf={conf:.1f}%")
                except Exception as e:
                    print(f"Error predicting {away} @ {home}: {e}")
                    import traceback
                    traceback.print_exc()
                    # Use fallback prediction
                    game_predictions[game_key] = {'away_prob': 0.5, 'home_prob': 0.5, 'confidence': 0.0}
            
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
            
            # Set a different random seed for each simulation to ensure variance
            # Use simulation number as seed so each sim is different but reproducible
            random.seed(sim * 1000 + int(datetime.now().timestamp()) % 10000)
            np.random.seed(sim * 1000 + int(datetime.now().timestamp()) % 10000)
            
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
        
        # Get recent form for all teams to adjust probabilities
        print("\nCalculating recent form for all teams...")
        team_forms = {}
        for team in team_records.keys():
            form = self.get_recent_team_form(team, num_games=10)
            team_forms[team] = form
            if form['recent_games'] > 0:
                print(f"  {team}: {form['recent_wins']}/{form['recent_games']} wins ({form['win_pct']*100:.1f}%), form_score={form['form_score']:.3f}")
        
        # Debug: show playoff counts before form adjustment
        print(f"\nPlayoff counts (before form adjustment):")
        sample_counts = sorted(playoff_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for team, count in sample_counts:
            print(f"  {team}: {count}/{num_simulations} ({count/num_simulations*100:.1f}%)")
        
        # Calculate team strength for all teams (PRIMARY FACTOR - 70% weight)
        print("\nCalculating comprehensive team strength for all teams...")
        team_strengths = {}
        for team in team_records.keys():
            strength_data = self.calculate_comprehensive_team_strength(team)
            team_strengths[team] = strength_data
            if strength_data['games_played'] > 0:
                print(f"  {team}: strength={strength_data['strength_score']:.3f} (off={strength_data['offensive_strength']:.3f}, def={strength_data['defensive_strength']:.3f}, adv={strength_data['advanced_strength']:.3f}), games={strength_data['games_played']}")
        
        # Calculate strength-based probabilities (before simulations)
        # Teams with higher strength should have higher playoff probability
        # This is the PRIMARY factor (70% weight)
        strength_probs = {}
        if team_strengths:
            # Normalize strength scores to probabilities
            # Use percentile ranking: top teams get higher probabilities
            strength_scores = [(team, data['strength_score']) for team, data in team_strengths.items()]
            strength_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Convert strength ranking to base probability
            # Top 8 teams in each conference get higher probabilities
            for i, (team, strength) in enumerate(strength_scores):
                # Rank-based probability (top teams get higher prob)
                # But also factor in actual strength score
                rank_prob = max(0.05, min(0.95, 0.95 - (i * 0.02)))  # Top team: 95%, decreases by 2% per rank
                strength_prob = 0.3 + (strength * 0.4)  # Strength contributes 30-70% range
                
                # Blend rank and strength (60% strength, 40% rank)
                strength_probs[team] = strength_prob * 0.6 + rank_prob * 0.4
        
        # Apply recent form adjustments to probabilities (SECONDARY FACTOR - 20% weight)
        # Teams with better recent form get a boost, teams with worse form get a penalty
        num_remaining_games_total = len(games_to_predict)
        remaining_games_factor = min(1.0, num_remaining_games_total / 200.0)  # Scale based on games left
        
        # Form adjustment strength: 20% weight
        form_adjustment_strength = 0.20 * remaining_games_factor
        
        print(f"\nApplying form adjustments (strength: {form_adjustment_strength*100:.1f}%, remaining games factor: {remaining_games_factor:.2f})")
        
        for team, count in playoff_counts.items():
            # BASE PROBABILITY from simulations (includes standings as starting point)
            base_prob = count / num_simulations
            
            # Get team strength probability (PRIMARY FACTOR - 70% weight)
            strength_prob = strength_probs.get(team, 0.5)
            
            # Get recent form (SECONDARY FACTOR - 20% weight)
            form = team_forms.get(team, {'form_score': 0.5})
            remaining_games = remaining_game_counts.get(team, 0)
            
            # Calculate form adjustment: form_score of 0.5 = no change, >0.5 = boost, <0.5 = penalty
            form_adjustment = (form['form_score'] - 0.5) * 2  # -1 to +1
            
            # Apply form adjustment (20% weight)
            remaining_games_weight = min(1.0, remaining_games / 20.0)  # Max weight at 20+ games
            effective_form_adjustment = form_adjustment * form_adjustment_strength * (0.5 + 0.5 * remaining_games_weight)
            
            # COMBINE: 70% strength + 20% form + 10% simulation base (which includes standings)
            # The simulation base already includes standings influence, so we're reducing it to 10%
            adjusted_prob = (
                strength_prob * 0.70 +  # PRIMARY: Team strength (data-driven)
                (base_prob + effective_form_adjustment) * 0.20 +  # SECONDARY: Form-adjusted simulation
                base_prob * 0.10  # MINIMAL: Standings influence (through simulation base)
            )
            
            # Add additional uncertainty based on remaining games
            # More games remaining = more uncertainty = probabilities spread out more
            if remaining_games > 10:
                # For teams with many games left, add more variance
                uncertainty_factor = min(0.15, remaining_games / 100.0)
                # Pull probabilities toward 50% slightly (adds uncertainty)
                if base_prob > 0.7:
                    adjusted_prob = adjusted_prob * (1.0 - uncertainty_factor) + 0.5 * uncertainty_factor
                elif base_prob < 0.3:
                    adjusted_prob = adjusted_prob * (1.0 - uncertainty_factor) + 0.5 * uncertainty_factor
            
            # Apply season-based probability cap
            # Early in season, no team should be at 100%
            adjusted_prob = min(adjusted_prob, max_probability_cap)
            
            # Additional early-season adjustments
            if season_progress < 0.25:  # First quarter of season (< 20 games)
                # Pull all probabilities toward 50% more aggressively
                uncertainty_pull = 0.20  # 20% pull toward 50%
                adjusted_prob = adjusted_prob * (1.0 - uncertainty_pull) + 0.5 * uncertainty_pull
                # Cap even lower for early season
                adjusted_prob = min(adjusted_prob, 0.65)
            elif season_progress < 0.50:  # First half of season (< 41 games)
                # Moderate pull toward 50%
                uncertainty_pull = 0.10  # 10% pull toward 50%
                adjusted_prob = adjusted_prob * (1.0 - uncertainty_pull) + 0.5 * uncertainty_pull
            
            # Additional adjustment: if base prob is 100%, force it down based on form and remaining games
            if base_prob >= 0.99 and remaining_games > 5:
                # Even teams at 100% should have some uncertainty if they have games left
                # Pull them down based on form and remaining games
                uncertainty_reduction = min(0.25, remaining_games / 40.0)  # Up to 25% reduction
                if form['form_score'] < 0.5:  # Poor recent form
                    uncertainty_reduction += 0.10  # Additional 10% reduction for poor form
                adjusted_prob = max(0.65, min(adjusted_prob, base_prob - uncertainty_reduction))
            
            # Similar adjustment for teams at 0% - give them hope if they have games left
            if base_prob <= 0.01 and remaining_games > 10:
                uncertainty_boost = min(0.20, remaining_games / 60.0)  # Up to 20% boost
                if form['form_score'] > 0.6:  # Good recent form
                    uncertainty_boost += 0.10  # Additional 10% boost for good form
                adjusted_prob = min(0.35, max(adjusted_prob, base_prob + uncertainty_boost))
            
            # Final clamp to valid range [0, 1]
            adjusted_prob = max(0.0, min(1.0, adjusted_prob))
            
            record = team_records.get(team, {})
            playoff_probs[team] = {
                'playoff_probability': adjusted_prob,
                'current_points': record.get('points', 0),
                'games_played': record.get('games_played', 0),
                'remaining_games': remaining_game_counts.get(team, 0),
                'conference': record.get('conference', ''),
                'wins': record.get('wins', 0),
                'losses': record.get('losses', 0),
                'ot_losses': record.get('ot_losses', 0),
                'recent_form': {
                    'form_score': form['form_score'],
                    'recent_wins': form['recent_wins'],
                    'recent_games': form['recent_games'],
                    'win_pct': form.get('win_pct', 0.0)
                },
                'base_probability': base_prob,
                'strength_probability': strength_prob,
                'form_adjustment': effective_form_adjustment
            }
        
        # Debug: show adjusted probabilities
        print(f"\nFinal playoff probabilities (data-driven):")
        sample_probs = sorted(playoff_probs.items(), key=lambda x: x[1]['playoff_probability'], reverse=True)[:10]
        for team, data in sample_probs:
            base = data['base_probability']
            strength = data.get('strength_probability', 0.5)
            form_adj = data['form_adjustment']
            adjusted = data['playoff_probability']
            print(f"  {team}: sim={base*100:.1f}%, strength={strength*100:.1f}%, form={form_adj*100:+.1f}% -> final={adjusted*100:.1f}%")
        
        return playoff_probs
    
    def get_recent_team_form(self, team_abbrev: str, num_games: int = 10) -> Dict:
        """
        Get recent team form from completed games using NHL API
        Returns recent performance metrics to adjust playoff probabilities
        """
        try:
            import requests
            # Get team's recent games from NHL API
            # First, get team ID from abbreviation
            team_id_map = self._get_team_id_map()
            team_id = team_id_map.get(team_abbrev.upper())
            
            if not team_id:
                return {'form_score': 0.5, 'recent_wins': 0, 'recent_games': 0, 'xg_trend': 0.0}
            
            # Get recent completed games for this team
            recent_games = []
            today = datetime.now(pytz.timezone('US/Central'))
            
            # Look back 30 days to find recent games
            for days_back in range(30):
                date = today - timedelta(days=days_back)
                date_str = date.strftime('%Y-%m-%d')
                
                try:
                    schedule = self.api.get_game_schedule(date_str)
                    if schedule and 'gameWeek' in schedule:
                        for day in schedule.get('gameWeek', []):
                            if day.get('date') != date_str:
                                continue
                            for game in day.get('games', []):
                                game_state = game.get('gameState', '')
                                # Only completed games
                                if game_state not in ['OFF', 'FINAL']:
                                    continue
                                
                                away_team_obj = game.get('awayTeam', {})
                                home_team_obj = game.get('homeTeam', {})
                                
                                away_id = away_team_obj.get('id') if isinstance(away_team_obj, dict) else None
                                home_id = home_team_obj.get('id') if isinstance(home_team_obj, dict) else None
                                
                                # Check if this team played in this game
                                if away_id == team_id or home_id == team_id:
                                    # Get game result
                                    away_score = away_team_obj.get('score', 0) if isinstance(away_team_obj, dict) else 0
                                    home_score = home_team_obj.get('score', 0) if isinstance(home_team_obj, dict) else 0
                                    
                                    # Determine if team won
                                    team_won = (away_id == team_id and away_score > home_score) or \
                                              (home_id == team_id and home_score > away_score)
                                    
                                    recent_games.append({
                                        'date': date_str,
                                        'won': team_won,
                                        'team_score': away_score if away_id == team_id else home_score,
                                        'opp_score': home_score if away_id == team_id else away_score,
                                        'was_home': home_id == team_id
                                    })
                                    
                                    if len(recent_games) >= num_games:
                                        break
                except Exception as e:
                    continue
                
                if len(recent_games) >= num_games:
                    break
            
            if len(recent_games) == 0:
                return {'form_score': 0.5, 'recent_wins': 0, 'recent_games': 0, 'xg_trend': 0.0}
            
            # Calculate recent form metrics
            recent_wins = sum(1 for g in recent_games if g['won'])
            win_pct = recent_wins / len(recent_games)
            
            # Get xG trends from team stats if available
            xg_trend = 0.0
            if self.team_stats and 'teams' in self.team_stats:
                team_data = self.team_stats['teams'].get(team_abbrev.upper(), {})
                if team_data:
                    # Compare recent xG to season average
                    recent_xg = team_data.get('xg_avg', 0)
                    # NHL average is around 2.8, so normalize
                    xg_trend = (recent_xg - 2.8) / 1.0  # Normalize around league average
            
            # Calculate form score (0-1 scale, 0.5 = average)
            # Win percentage contributes 70%, xG trend contributes 30%
            form_score = (win_pct * 0.7) + (0.5 + min(0.2, max(-0.2, xg_trend * 0.1)) * 0.3)
            form_score = max(0.0, min(1.0, form_score))
            
            return {
                'form_score': form_score,
                'recent_wins': recent_wins,
                'recent_games': len(recent_games),
                'win_pct': win_pct,
                'xg_trend': xg_trend
            }
        except Exception as e:
            print(f"Error getting recent form for {team_abbrev}: {e}")
            return {'form_score': 0.5, 'recent_wins': 0, 'recent_games': 0, 'xg_trend': 0.0}
    
    def _get_team_id_map(self) -> Dict[str, int]:
        """Get mapping of team abbreviations to team IDs"""
        try:
            import requests
            url = 'https://api-web.nhle.com/v1/standings/now'
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                data = response.json()
                team_map = {}
                for team_data in data.get('standings', []):
                    team_abbrev_obj = team_data.get('teamAbbrev', {})
                    if isinstance(team_abbrev_obj, dict):
                        team_abbrev = team_abbrev_obj.get('default', '')
                    else:
                        team_abbrev = str(team_abbrev_obj) if team_abbrev_obj else ''
                    
                    team_id = team_data.get('teamId')
                    if team_abbrev and team_id:
                        team_map[team_abbrev.upper()] = team_id
                return team_map
        except Exception as e:
            print(f"Error getting team ID map: {e}")
        return {}
    
    def calculate_comprehensive_team_strength(self, team_abbrev: str) -> Dict:
        """
        Calculate comprehensive team strength using ALL metrics from team stats
        Returns strength score (0-1) and component breakdowns
        Primary factor for playoff probabilities (70% weight)
        """
        team_abbrev_upper = team_abbrev.upper()
        
        # Try to get team stats from the model's team_stats
        team_data = None
        if hasattr(self.model, 'team_stats') and self.model.team_stats:
            team_data = self.model.team_stats.get(team_abbrev_upper, {})
        
        # If not found, try loading from file
        if not team_data:
            try:
                if self.team_stats_file.exists():
                    with open(self.team_stats_file, 'r') as f:
                        file_stats = json.load(f)
                        team_data = file_stats.get('teams', {}).get(team_abbrev_upper, {})
            except:
                pass
        
        # If still not found, return default
        if not team_data:
            return {
                'strength_score': 0.5,
                'offensive_strength': 0.5,
                'defensive_strength': 0.5,
                'advanced_strength': 0.5,
                'games_played': 0
            }
        
        # Aggregate home and away data
        home_data = team_data.get('home', {}) if isinstance(team_data, dict) else {}
        away_data = team_data.get('away', {}) if isinstance(team_data, dict) else {}
        
        # Combine home and away metrics (weighted average)
        def safe_avg(values):
            """Calculate average, handling empty lists and None values"""
            valid = [v for v in values if v is not None and isinstance(v, (int, float))]
            return sum(valid) / len(valid) if valid else 0.0
        
        def safe_sum(values):
            """Calculate sum, handling empty lists and None values"""
            valid = [v for v in values if v is not None and isinstance(v, (int, float))]
            return sum(valid) if valid else 0.0
        
        # Get games played
        home_games = len(home_data.get('games', [])) if isinstance(home_data, dict) else 0
        away_games = len(away_data.get('games', [])) if isinstance(away_data, dict) else 0
        total_games = home_games + away_games
        
        if total_games < 5:
            return {
                'strength_score': 0.5,
                'offensive_strength': 0.5,
                'defensive_strength': 0.5,
                'advanced_strength': 0.5,
                'games_played': total_games
            }
        
        # OFFENSIVE METRICS (normalized to 0-1)
        # xG for
        home_xg_for = safe_avg(home_data.get('xG_for', []) or home_data.get('xg', []))
        away_xg_for = safe_avg(away_data.get('xG_for', []) or away_data.get('xg', []))
        xg_for = (home_xg_for * home_games + away_xg_for * away_games) / total_games if total_games > 0 else 0.0
        xg_for_norm = max(0, min(1, (xg_for - 2.0) / 2.0))  # NHL range: 2.0-4.0
        
        # Goals for
        home_goals_for = safe_avg(home_data.get('goals_for', []) or home_data.get('goals', []))
        away_goals_for = safe_avg(away_data.get('goals_for', []) or away_data.get('goals', []))
        goals_for = (home_goals_for * home_games + away_goals_for * away_games) / total_games if total_games > 0 else 0.0
        goals_for_norm = max(0, min(1, (goals_for - 2.0) / 2.0))  # NHL range: 2.0-4.0
        
        # HDC for
        home_hdc_for = safe_avg(home_data.get('hdc_for', []) or home_data.get('hdc', []))
        away_hdc_for = safe_avg(away_data.get('hdc_for', []) or away_data.get('hdc', []))
        hdc_for = (home_hdc_for * home_games + away_hdc_for * away_games) / total_games if total_games > 0 else 0.0
        hdc_for_norm = max(0, min(1, (hdc_for - 5.0) / 10.0))  # NHL range: 5-15
        
        # Shots for
        home_shots_for = safe_avg(home_data.get('shots_for', []) or home_data.get('shots', []))
        away_shots_for = safe_avg(away_data.get('shots_for', []) or away_data.get('shots', []))
        shots_for = (home_shots_for * home_games + away_shots_for * away_games) / total_games if total_games > 0 else 0.0
        shots_for_norm = max(0, min(1, (shots_for - 25.0) / 15.0))  # NHL range: 25-40
        
        # Offensive zone shots (OZS)
        home_ozs = safe_sum(home_data.get('ozs', []))
        away_ozs = safe_sum(away_data.get('ozs', []))
        ozs_total = home_ozs + away_ozs
        ozs_per_game = ozs_total / total_games if total_games > 0 else 0.0
        ozs_norm = max(0, min(1, (ozs_per_game - 5.0) / 10.0))  # NHL range: 5-15 per game
        
        # Rush shots
        home_rush = safe_sum(home_data.get('rush', []))
        away_rush = safe_sum(away_data.get('rush', []))
        rush_total = home_rush + away_rush
        rush_per_game = rush_total / total_games if total_games > 0 else 0.0
        rush_norm = max(0, min(1, (rush_per_game - 3.0) / 7.0))  # NHL range: 3-10 per game
        
        # Offensive strength (weighted average)
        offensive_strength = (
            xg_for_norm * 0.30 +
            goals_for_norm * 0.20 +
            hdc_for_norm * 0.20 +
            shots_for_norm * 0.15 +
            ozs_norm * 0.10 +
            rush_norm * 0.05
        )
        
        # DEFENSIVE METRICS (normalized to 0-1, inverted so higher = better defense)
        # xG against (lower is better)
        home_xg_against = safe_avg(home_data.get('xG_against', []) or home_data.get('opp_xg', []))
        away_xg_against = safe_avg(away_data.get('xG_against', []) or away_data.get('opp_xg', []))
        xg_against = (home_xg_against * home_games + away_xg_against * away_games) / total_games if total_games > 0 else 3.0
        xg_against_norm = max(0, min(1, 1.0 - (xg_against - 2.0) / 2.0))  # Inverted: lower xG against = better
        
        # Goals against (lower is better)
        home_goals_against = safe_avg(home_data.get('goals_against', []) or home_data.get('opp_goals', []))
        away_goals_against = safe_avg(away_data.get('goals_against', []) or away_data.get('opp_goals', []))
        goals_against = (home_goals_against * home_games + away_goals_against * away_games) / total_games if total_games > 0 else 3.0
        goals_against_norm = max(0, min(1, 1.0 - (goals_against - 2.0) / 2.0))  # Inverted
        
        # HDC against (lower is better)
        home_hdc_against = safe_avg(home_data.get('hdc_against', []))
        away_hdc_against = safe_avg(away_data.get('hdc_against', []))
        hdc_against = (home_hdc_against * home_games + away_hdc_against * away_games) / total_games if total_games > 0 else 10.0
        hdc_against_norm = max(0, min(1, 1.0 - (hdc_against - 5.0) / 10.0))  # Inverted
        
        # Shots against (lower is better)
        home_shots_against = safe_avg(home_data.get('shots_against', []))
        away_shots_against = safe_avg(away_data.get('shots_against', []))
        shots_against = (home_shots_against * home_games + away_shots_against * away_games) / total_games if total_games > 0 else 30.0
        shots_against_norm = max(0, min(1, 1.0 - (shots_against - 25.0) / 15.0))  # Inverted
        
        # Defensive zone shots (DZS) - lower is better
        home_dzs = safe_sum(home_data.get('dzs', []))
        away_dzs = safe_sum(away_data.get('dzs', []))
        dzs_total = home_dzs + away_dzs
        dzs_per_game = dzs_total / total_games if total_games > 0 else 10.0
        dzs_norm = max(0, min(1, 1.0 - (dzs_per_game - 5.0) / 10.0))  # Inverted
        
        # Defensive strength (weighted average)
        defensive_strength = (
            xg_against_norm * 0.30 +
            goals_against_norm * 0.25 +
            hdc_against_norm * 0.20 +
            shots_against_norm * 0.15 +
            dzs_norm * 0.10
        )
        
        # ADVANCED METRICS
        # Game Score
        home_gs = safe_avg(home_data.get('gs', []))
        away_gs = safe_avg(away_data.get('gs', []))
        gs_avg = (home_gs * home_games + away_gs * away_games) / total_games if total_games > 0 else 4.0
        gs_norm = max(0, min(1, (gs_avg - 3.0) / 2.0))  # NHL range: 3.0-5.0
        
        # Corsi %
        home_corsi = safe_avg(home_data.get('corsi_pct', []))
        away_corsi = safe_avg(away_data.get('corsi_pct', []))
        corsi_avg = (home_corsi * home_games + away_corsi * away_games) / total_games if total_games > 0 else 50.0
        corsi_norm = max(0, min(1, (corsi_avg - 40.0) / 20.0))  # NHL range: 40-60%
        
        # Power Play %
        home_pp = safe_avg(home_data.get('power_play_pct', []) or home_data.get('pp_pct', []))
        away_pp = safe_avg(away_data.get('power_play_pct', []) or away_data.get('pp_pct', []))
        pp_avg = (home_pp * home_games + away_pp * away_games) / total_games if total_games > 0 else 20.0
        pp_norm = max(0, min(1, (pp_avg - 15.0) / 15.0))  # NHL range: 15-30%
        
        # Faceoff %
        home_fo = safe_avg(home_data.get('faceoff_pct', []) or home_data.get('fo_pct', []))
        away_fo = safe_avg(away_data.get('faceoff_pct', []) or away_data.get('fo_pct', []))
        fo_avg = (home_fo * home_games + away_fo * away_games) / total_games if total_games > 0 else 50.0
        fo_norm = max(0, min(1, (fo_avg - 45.0) / 10.0))  # NHL range: 45-55%
        
        # Neutral zone turnovers (NZT) - more is better (indicates good forechecking)
        home_nzt = safe_sum(home_data.get('nzt', []))
        away_nzt = safe_sum(away_data.get('nzt', []))
        nzt_total = home_nzt + away_nzt
        nzt_per_game = nzt_total / total_games if total_games > 0 else 5.0
        nzt_norm = max(0, min(1, (nzt_per_game - 3.0) / 7.0))  # NHL range: 3-10 per game
        
        # Movement metrics
        home_lateral = safe_avg(home_data.get('lateral', []))
        away_lateral = safe_avg(away_data.get('lateral', []))
        lateral_avg = (home_lateral * home_games + away_lateral * away_games) / total_games if total_games > 0 else 0.0
        lateral_norm = max(0, min(1, (abs(lateral_avg) + 5.0) / 10.0))  # Normalize around 0
        
        home_longitudinal = safe_avg(home_data.get('longitudinal', []))
        away_longitudinal = safe_avg(away_data.get('longitudinal', []))
        longitudinal_avg = (home_longitudinal * home_games + away_longitudinal * away_games) / total_games if total_games > 0 else 0.0
        longitudinal_norm = max(0, min(1, (abs(longitudinal_avg) + 10.0) / 20.0))  # Normalize around 0
        
        # Clutch score
        home_clutch = safe_avg(home_data.get('clutch_score', []))
        away_clutch = safe_avg(away_data.get('clutch_score', []))
        clutch_avg = (home_clutch * home_games + away_clutch * away_games) / total_games if total_games > 0 else 0.5
        clutch_norm = max(0, min(1, clutch_avg))  # Already 0-1 scale
        
        # Advanced strength (weighted average)
        advanced_strength = (
            gs_norm * 0.25 +
            corsi_norm * 0.20 +
            pp_norm * 0.15 +
            fo_norm * 0.10 +
            nzt_norm * 0.10 +
            lateral_norm * 0.05 +
            longitudinal_norm * 0.05 +
            clutch_norm * 0.10
        )
        
        # OVERALL STRENGTH SCORE (weighted combination)
        # Offensive: 35%, Defensive: 35%, Advanced: 30%
        strength_score = (
            offensive_strength * 0.35 +
            defensive_strength * 0.35 +
            advanced_strength * 0.30
        )
        
        return {
            'strength_score': max(0.0, min(1.0, strength_score)),
            'offensive_strength': max(0.0, min(1.0, offensive_strength)),
            'defensive_strength': max(0.0, min(1.0, defensive_strength)),
            'advanced_strength': max(0.0, min(1.0, advanced_strength)),
            'games_played': total_games,
            'components': {
                'xg_for': xg_for_norm,
                'goals_for': goals_for_norm,
                'hdc_for': hdc_for_norm,
                'xg_against': xg_against_norm,
                'goals_against': goals_against_norm,
                'hdc_against': hdc_against_norm,
                'gs': gs_norm,
                'corsi': corsi_norm,
                'pp': pp_norm
            }
        }
    
    def _estimate_team_strength(self, team_abbrev: str) -> float:
        """Legacy method - now uses comprehensive strength calculation"""
        strength_data = self.calculate_comprehensive_team_strength(team_abbrev)
        return strength_data['strength_score']

