"""
Pre-Game Prediction Interface
Uses the self-learning model for predictions before games are played
This is separate from the post-game win probability analysis
"""

import json
import requests
import os
import numpy as np
from nhl_api_client import NHLAPIClient
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from correlation_model import CorrelationModel
from lineup_service import LineupService
from pdf_report_generator import PostGameReportGenerator
from advanced_metrics_analyzer import AdvancedMetricsAnalyzer
from schedule_analyzer import ScheduleAnalyzer
from datetime import datetime, timedelta
from typing import Optional
import pytz
import logging

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class PredictionInterface:
    def __init__(self):
        """Initialize the prediction interface"""
        self.api = NHLAPIClient()
        self.learning_model = ImprovedSelfLearningModelV2()
        self.corr_model = CorrelationModel()
        self.lineup_service = LineupService()
        self.report_generator = PostGameReportGenerator()
        try:
            self.schedule_analyzer = ScheduleAnalyzer()
        except Exception as e:
            print(f"Warning: Could not initialize ScheduleAnalyzer: {e}")
            self.schedule_analyzer = None
    
    def check_and_add_missing_games(self):
        """Check for missing games from recent days and add them to the model"""
        print("🔍 Checking for missing games...")
        
        # Get the last 7 days
        central_tz = pytz.timezone('US/Central')
        central_now = datetime.now(central_tz)
        
        # Load existing predictions to see what we have
        predictions_store = self.learning_model.model_data.get('predictions', [])
        prediction_index = {}
        for idx, pred in enumerate(predictions_store):
            gid = str(pred.get('game_id') or '')
            if gid:
                prediction_index[gid] = idx
        
        games_added = 0
        games_updated = 0
        stale_updates = 0
        
        # Check each of the last 7 days
        for days_back in range(1, 8):
            check_date = (central_now - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # Get games from this date
            schedule = self.api.get_game_schedule(check_date)
            if not schedule or 'gameWeek' not in schedule:
                continue
            
            for day in schedule['gameWeek']:
                if day.get('date') == check_date and 'games' in day:
                    for game in day['games']:
                        game_id = str(game.get('id'))
                        away_team = game.get('awayTeam', {}).get('abbrev', 'UNK')
                        home_team = game.get('homeTeam', {}).get('abbrev', 'UNK')
                        game_state = game.get('gameState', 'UNKNOWN')
                        
                        # If we already have this game, update results if needed
                        if game_id in prediction_index:
                            existing_prediction = predictions_store[prediction_index[game_id]]
                            if existing_prediction.get('actual_winner'):
                                continue
                            
                            if game_state not in ['FINAL', 'OFF']:
                                continue
                            
                            try:
                                game_data = self.api.get_comprehensive_game_data(game_id)
                                if not game_data or 'boxscore' not in game_data:
                                    continue
                                away_goals = int(game_data['boxscore']['awayTeam'].get('score', 0))
                                home_goals = int(game_data['boxscore']['homeTeam'].get('score', 0))
                            except Exception as e:
                                print(f"  ❌ Error updating {away_team} @ {home_team}: {e}")
                                continue
                            
                            if away_goals == home_goals:
                                # Ignore ties/invalid data
                                continue
                            
                            if self._update_prediction_result_entry(
                                existing_prediction, away_team, home_team, away_goals, home_goals
                            ):
                                games_updated += 1
                                winner_label = away_team if away_goals > home_goals else home_team
                                print(f"  🔁 Updated result for {away_team} @ {home_team}: {winner_label} won")
                            continue
                        
                        # Only process completed games
                        if game_state in ['FINAL', 'OFF']:
                            try:
                                # Get comprehensive game data
                                game_data = self.api.get_comprehensive_game_data(game_id)
                                if not game_data:
                                    continue
                                
                                # Get team IDs for metrics calculation
                                away_team_data = game_data.get('boxscore', {}).get('awayTeam', {})
                                home_team_data = game_data.get('boxscore', {}).get('homeTeam', {})
                                away_team_id = away_team_data.get('id')
                                home_team_id = home_team_data.get('id')
                                
                                if not away_team_id or not home_team_id:
                                    continue
                                
                                # Determine actual winner
                                away_goals = game_data['boxscore']['awayTeam'].get('score', 0)
                                home_goals = game_data['boxscore']['homeTeam'].get('score', 0)
                                
                                actual_winner = None
                                if away_goals > home_goals:
                                    actual_winner = "away"
                                elif home_goals > away_goals:
                                    actual_winner = "home"
                                
                                if actual_winner:
                                    away_shots = game_data['boxscore']['awayTeam'].get('sog', 0)
                                    home_shots = game_data['boxscore']['homeTeam'].get('sog', 0)
                                    try:
                                        away_rest = self.learning_model._calculate_rest_days_advantage(away_team, 'away', check_date)
                                        home_rest = self.learning_model._calculate_rest_days_advantage(home_team, 'home', check_date)
                                    except Exception:
                                        away_rest = home_rest = 0.0
                                    context_bucket = self.learning_model.determine_context_bucket(away_rest, home_rest)
                                    away_b2b = away_rest <= -0.5
                                    home_b2b = home_rest <= -0.5
                                    # Use the actual model to make a prediction for this game
                                    try:
                                        model_prediction = self.learning_model.ensemble_predict(away_team, home_team)
                                        raw_away_prob = model_prediction.get('away_prob', 0.5)
                                        raw_home_prob = model_prediction.get('home_prob', 0.5)
                                        predicted_away_prob = self.learning_model.apply_calibration(raw_away_prob, context_bucket)
                                        predicted_home_prob = 1.0 - predicted_away_prob
                                        prediction_confidence = max(predicted_away_prob, predicted_home_prob)
                                        ensemble_away_prob = raw_away_prob
                                        ensemble_home_prob = raw_home_prob
                                    except Exception as e:
                                        print(f"    ⚠️  Could not get model prediction: {e}")
                                        # Fallback to shot-based prediction
                                        away_shots = game_data['boxscore']['awayTeam'].get('sog', 0)
                                        home_shots = game_data['boxscore']['homeTeam'].get('sog', 0)
                                        total_shots = away_shots + home_shots
                                        if total_shots > 0:
                                            raw_away_prob = away_shots / total_shots
                                            raw_home_prob = home_shots / total_shots
                                        else:
                                            raw_away_prob = 0.5
                                            raw_home_prob = 0.5
                                        predicted_away_prob = self.learning_model.apply_calibration(raw_away_prob, context_bucket)
                                        predicted_home_prob = 1.0 - predicted_away_prob
                                        prediction_confidence = max(predicted_away_prob, predicted_home_prob)
                                        ensemble_away_prob = raw_away_prob
                                        ensemble_home_prob = raw_home_prob
                                    
                                    # Extract comprehensive metrics (matching recalculate_advanced_metrics.py)
                                    metrics_used = {
                                        "away_shots": away_shots,
                                        "home_shots": home_shots,
                                        "away_rest": away_rest,
                                        "home_rest": home_rest,
                                        "context_bucket": context_bucket,
                                        "away_back_to_back": away_b2b,
                                        "home_back_to_back": home_b2b
                                    }
                                    
                                    # Calculate xG and HDC
                                    try:
                                        if 'play_by_play' in game_data:
                                            away_xg, home_xg = self.report_generator._calculate_xg_from_plays(game_data)
                                            away_hdc, home_hdc = self.report_generator._calculate_hdc_from_plays(game_data)
                                            metrics_used["away_xg"] = away_xg
                                            metrics_used["home_xg"] = home_xg
                                            metrics_used["away_hdc"] = away_hdc
                                            metrics_used["home_hdc"] = home_hdc
                                        else:
                                            metrics_used["away_xg"] = 0.0
                                            metrics_used["home_xg"] = 0.0
                                            metrics_used["away_hdc"] = 0
                                            metrics_used["home_hdc"] = 0
                                    except Exception as e:
                                        print(f"    ⚠️  Error calculating xG/HDC: {e}")
                                        metrics_used["away_xg"] = 0.0
                                        metrics_used["home_xg"] = 0.0
                                        metrics_used["away_hdc"] = 0
                                        metrics_used["home_hdc"] = 0
                                    
                                    # Calculate zone metrics (needed for both game-level and period-level)
                                    away_zone_metrics = {}
                                    home_zone_metrics = {}
                                    try:
                                        away_zone_metrics = self.report_generator._calculate_zone_metrics(game_data, away_team_id, 'away')
                                        home_zone_metrics = self.report_generator._calculate_zone_metrics(game_data, home_team_id, 'home')
                                        
                                        metrics_used['away_nzt'] = sum(away_zone_metrics.get('nz_turnovers', [0, 0, 0]))
                                        metrics_used['away_nztsa'] = sum(away_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0]))
                                        metrics_used['away_ozs'] = sum(away_zone_metrics.get('oz_originating_shots', [0, 0, 0]))
                                        metrics_used['away_nzs'] = sum(away_zone_metrics.get('nz_originating_shots', [0, 0, 0]))
                                        metrics_used['away_dzs'] = sum(away_zone_metrics.get('dz_originating_shots', [0, 0, 0]))
                                        metrics_used['away_fc'] = sum(away_zone_metrics.get('fc_cycle_sog', [0, 0, 0]))
                                        metrics_used['away_rush'] = sum(away_zone_metrics.get('rush_sog', [0, 0, 0]))
                                        
                                        metrics_used['home_nzt'] = sum(home_zone_metrics.get('nz_turnovers', [0, 0, 0]))
                                        metrics_used['home_nztsa'] = sum(home_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0]))
                                        metrics_used['home_ozs'] = sum(home_zone_metrics.get('oz_originating_shots', [0, 0, 0]))
                                        metrics_used['home_nzs'] = sum(home_zone_metrics.get('nz_originating_shots', [0, 0, 0]))
                                        metrics_used['home_dzs'] = sum(home_zone_metrics.get('dz_originating_shots', [0, 0, 0]))
                                        metrics_used['home_fc'] = sum(home_zone_metrics.get('fc_cycle_sog', [0, 0, 0]))
                                        metrics_used['home_rush'] = sum(home_zone_metrics.get('rush_sog', [0, 0, 0]))
                                    except Exception as e:
                                        print(f"    ⚠️  Error calculating zone metrics: {e}")
                                        for key in ['away_nzt', 'away_nztsa', 'away_ozs', 'away_nzs', 'away_dzs', 'away_fc', 'away_rush',
                                                   'home_nzt', 'home_nztsa', 'home_ozs', 'home_nzs', 'home_dzs', 'home_fc', 'home_rush']:
                                            metrics_used[key] = 0
                                    
                                    # Calculate movement metrics
                                    try:
                                        if 'play_by_play' in game_data:
                                            analyzer = AdvancedMetricsAnalyzer(game_data.get('play_by_play', {}))
                                            
                                            away_movement = analyzer.calculate_pre_shot_movement_metrics(away_team_id)
                                            home_movement = analyzer.calculate_pre_shot_movement_metrics(home_team_id)
                                            
                                            metrics_used['away_lateral'] = away_movement['lateral_movement'].get('avg_delta_y', 0.0)
                                            metrics_used['away_longitudinal'] = away_movement['longitudinal_movement'].get('avg_delta_x', 0.0)
                                            
                                            metrics_used['home_lateral'] = home_movement['lateral_movement'].get('avg_delta_y', 0.0)
                                            metrics_used['home_longitudinal'] = home_movement['longitudinal_movement'].get('avg_delta_x', 0.0)
                                        else:
                                            metrics_used['away_lateral'] = 0.0
                                            metrics_used['away_longitudinal'] = 0.0
                                            metrics_used['home_lateral'] = 0.0
                                            metrics_used['home_longitudinal'] = 0.0
                                    except Exception as e:
                                        print(f"    ⚠️  Error calculating movement metrics: {e}")
                                        for key in ['away_lateral', 'away_longitudinal', 'home_lateral', 'home_longitudinal']:
                                            metrics_used[key] = 0.0
                                    
                                    # Calculate period stats for detailed breakdowns
                                    try:
                                        away_period_stats = self.report_generator._calculate_real_period_stats(game_data, away_team_id, 'away')
                                        home_period_stats = self.report_generator._calculate_real_period_stats(game_data, home_team_id, 'home')
                                        
                                        # Power play details
                                        metrics_used['away_pp_goals'] = sum(away_period_stats.get('pp_goals', [0, 0, 0]))
                                        metrics_used['away_pp_attempts'] = sum(away_period_stats.get('pp_attempts', [0, 0, 0]))
                                        metrics_used['home_pp_goals'] = sum(home_period_stats.get('pp_goals', [0, 0, 0]))
                                        metrics_used['home_pp_attempts'] = sum(home_period_stats.get('pp_attempts', [0, 0, 0]))
                                        
                                        # Faceoff details
                                        metrics_used['away_faceoff_wins'] = sum(away_period_stats.get('faceoff_wins', [0, 0, 0]))
                                        metrics_used['away_faceoff_total'] = sum(away_period_stats.get('faceoff_total', [0, 0, 0]))
                                        metrics_used['home_faceoff_wins'] = sum(home_period_stats.get('faceoff_wins', [0, 0, 0]))
                                        metrics_used['home_faceoff_total'] = sum(home_period_stats.get('faceoff_total', [0, 0, 0]))
                                        
                                        # Period-by-period metrics (store as arrays [p1, p2, p3])
                                        metrics_used['away_period_shots'] = away_period_stats.get('shots', [0, 0, 0])
                                        metrics_used['away_period_corsi_pct'] = away_period_stats.get('corsi_pct', [50.0, 50.0, 50.0])
                                        metrics_used['away_period_pp_goals'] = away_period_stats.get('pp_goals', [0, 0, 0])
                                        metrics_used['away_period_pp_attempts'] = away_period_stats.get('pp_attempts', [0, 0, 0])
                                        metrics_used['away_period_pim'] = away_period_stats.get('pim', [0, 0, 0])
                                        metrics_used['away_period_hits'] = away_period_stats.get('hits', [0, 0, 0])
                                        metrics_used['away_period_fo_pct'] = away_period_stats.get('fo_pct', [50.0, 50.0, 50.0])
                                        metrics_used['away_period_blocks'] = away_period_stats.get('bs', [0, 0, 0])
                                        metrics_used['away_period_giveaways'] = away_period_stats.get('gv', [0, 0, 0])
                                        metrics_used['away_period_takeaways'] = away_period_stats.get('tk', [0, 0, 0])
                                        
                                        metrics_used['home_period_shots'] = home_period_stats.get('shots', [0, 0, 0])
                                        metrics_used['home_period_corsi_pct'] = home_period_stats.get('corsi_pct', [50.0, 50.0, 50.0])
                                        metrics_used['home_period_pp_goals'] = home_period_stats.get('pp_goals', [0, 0, 0])
                                        metrics_used['home_period_pp_attempts'] = home_period_stats.get('pp_attempts', [0, 0, 0])
                                        metrics_used['home_period_pim'] = home_period_stats.get('pim', [0, 0, 0])
                                        metrics_used['home_period_hits'] = home_period_stats.get('hits', [0, 0, 0])
                                        metrics_used['home_period_fo_pct'] = home_period_stats.get('fo_pct', [50.0, 50.0, 50.0])
                                        metrics_used['home_period_blocks'] = home_period_stats.get('bs', [0, 0, 0])
                                        metrics_used['home_period_giveaways'] = home_period_stats.get('gv', [0, 0, 0])
                                        metrics_used['home_period_takeaways'] = home_period_stats.get('tk', [0, 0, 0])
                                        
                                        # Period GS and xG
                                        period_gs_xg_away = self.report_generator._calculate_period_metrics(game_data, away_team_id, 'away')
                                        period_gs_xg_home = self.report_generator._calculate_period_metrics(game_data, home_team_id, 'home')
                                        
                                        if period_gs_xg_away:
                                            metrics_used['away_period_gs'] = period_gs_xg_away[0]
                                            metrics_used['away_period_xg'] = period_gs_xg_away[1]
                                        else:
                                            metrics_used['away_period_gs'] = [0.0, 0.0, 0.0]
                                            metrics_used['away_period_xg'] = [0.0, 0.0, 0.0]
                                        
                                        if period_gs_xg_home:
                                            metrics_used['home_period_gs'] = period_gs_xg_home[0]
                                            metrics_used['home_period_xg'] = period_gs_xg_home[1]
                                        else:
                                            metrics_used['home_period_gs'] = [0.0, 0.0, 0.0]
                                            metrics_used['home_period_xg'] = [0.0, 0.0, 0.0]
                                        
                                        # Period zone metrics
                                        metrics_used['away_period_nzt'] = away_zone_metrics.get('nz_turnovers', [0, 0, 0])
                                        metrics_used['away_period_nztsa'] = away_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0])
                                        metrics_used['away_period_ozs'] = away_zone_metrics.get('oz_originating_shots', [0, 0, 0])
                                        metrics_used['away_period_nzs'] = away_zone_metrics.get('nz_originating_shots', [0, 0, 0])
                                        metrics_used['away_period_dzs'] = away_zone_metrics.get('dz_originating_shots', [0, 0, 0])
                                        metrics_used['away_period_fc'] = away_zone_metrics.get('fc_cycle_sog', [0, 0, 0])
                                        metrics_used['away_period_rush'] = away_zone_metrics.get('rush_sog', [0, 0, 0])
                                        
                                        metrics_used['home_period_nzt'] = home_zone_metrics.get('nz_turnovers', [0, 0, 0])
                                        metrics_used['home_period_nztsa'] = home_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0])
                                        metrics_used['home_period_ozs'] = home_zone_metrics.get('oz_originating_shots', [0, 0, 0])
                                        metrics_used['home_period_nzs'] = home_zone_metrics.get('nz_originating_shots', [0, 0, 0])
                                        metrics_used['home_period_dzs'] = home_zone_metrics.get('dz_originating_shots', [0, 0, 0])
                                        metrics_used['home_period_fc'] = home_zone_metrics.get('fc_cycle_sog', [0, 0, 0])
                                        metrics_used['home_period_rush'] = home_zone_metrics.get('rush_sog', [0, 0, 0])
                                        
                                        # Calculate averages for game-level metrics
                                        metrics_used['away_corsi_pct'] = sum(away_period_stats.get('corsi_pct', [50.0, 50.0, 50.0])) / 3.0
                                        metrics_used['home_corsi_pct'] = sum(home_period_stats.get('corsi_pct', [50.0, 50.0, 50.0])) / 3.0
                                        
                                        pp_goals_away = metrics_used['away_pp_goals']
                                        pp_attempts_away = metrics_used['away_pp_attempts']
                                        metrics_used['away_power_play_pct'] = (pp_goals_away / pp_attempts_away * 100) if pp_attempts_away > 0 else 0.0
                                        
                                        pp_goals_home = metrics_used['home_pp_goals']
                                        pp_attempts_home = metrics_used['home_pp_attempts']
                                        metrics_used['home_power_play_pct'] = (pp_goals_home / pp_attempts_home * 100) if pp_attempts_home > 0 else 0.0
                                        
                                        fo_wins_away = metrics_used['away_faceoff_wins']
                                        fo_total_away = metrics_used['away_faceoff_total']
                                        metrics_used['away_faceoff_pct'] = (fo_wins_away / fo_total_away * 100) if fo_total_away > 0 else 50.0
                                        
                                        fo_wins_home = metrics_used['home_faceoff_wins']
                                        fo_total_home = metrics_used['home_faceoff_total']
                                        metrics_used['home_faceoff_pct'] = (fo_wins_home / fo_total_home * 100) if fo_total_home > 0 else 50.0
                                        
                                        # Physical play metrics
                                        metrics_used['away_hits'] = sum(away_period_stats.get('hits', [0, 0, 0]))
                                        metrics_used['home_hits'] = sum(home_period_stats.get('hits', [0, 0, 0]))
                                        metrics_used['away_blocked_shots'] = sum(away_period_stats.get('bs', [0, 0, 0]))
                                        metrics_used['home_blocked_shots'] = sum(home_period_stats.get('bs', [0, 0, 0]))
                                        metrics_used['away_giveaways'] = sum(away_period_stats.get('gv', [0, 0, 0]))
                                        metrics_used['home_giveaways'] = sum(home_period_stats.get('gv', [0, 0, 0]))
                                        metrics_used['away_takeaways'] = sum(away_period_stats.get('tk', [0, 0, 0]))
                                        metrics_used['home_takeaways'] = sum(home_period_stats.get('tk', [0, 0, 0]))
                                        metrics_used['away_penalty_minutes'] = sum(away_period_stats.get('pim', [0, 0, 0]))
                                        metrics_used['home_penalty_minutes'] = sum(home_period_stats.get('pim', [0, 0, 0]))
                                        
                                        # Game Score
                                        if period_gs_xg_away:
                                            metrics_used['away_gs'] = sum(period_gs_xg_away[0])
                                        else:
                                            metrics_used['away_gs'] = 0.0
                                        
                                        if period_gs_xg_home:
                                            metrics_used['home_gs'] = sum(period_gs_xg_home[0])
                                        else:
                                            metrics_used['home_gs'] = 0.0
                                    except Exception as e:
                                        print(f"    ⚠️  Error calculating period stats: {e}")
                                        # Set defaults
                                        default_period = [0, 0, 0]
                                        default_period_pct = [50.0, 50.0, 50.0]
                                        for key in ['away_pp_goals', 'away_pp_attempts', 'home_pp_goals', 'home_pp_attempts',
                                                   'away_faceoff_wins', 'away_faceoff_total', 'home_faceoff_wins', 'home_faceoff_total',
                                                   'away_hits', 'home_hits', 'away_blocked_shots', 'home_blocked_shots',
                                                   'away_giveaways', 'home_giveaways', 'away_takeaways', 'home_takeaways',
                                                   'away_penalty_minutes', 'home_penalty_minutes']:
                                            metrics_used[key] = 0
                                        for key in ['away_corsi_pct', 'home_corsi_pct', 'away_power_play_pct', 'home_power_play_pct',
                                                   'away_faceoff_pct', 'home_faceoff_pct', 'away_gs', 'home_gs']:
                                            metrics_used[key] = 0.0 if 'gs' in key else 50.0
                                        for key in ['away_period_shots', 'away_period_pp_goals', 'away_period_pp_attempts',
                                                   'away_period_pim', 'away_period_hits', 'away_period_blocks',
                                                   'away_period_giveaways', 'away_period_takeaways',
                                                   'home_period_shots', 'home_period_pp_goals', 'home_period_pp_attempts',
                                                   'home_period_pim', 'home_period_hits', 'home_period_blocks',
                                                   'home_period_giveaways', 'home_period_takeaways']:
                                            metrics_used[key] = default_period.copy()
                                        for key in ['away_period_corsi_pct', 'away_period_fo_pct',
                                                   'home_period_corsi_pct', 'home_period_fo_pct']:
                                            metrics_used[key] = default_period_pct.copy()
                                        for key in ['away_period_gs', 'away_period_xg', 'home_period_gs', 'home_period_xg']:
                                            metrics_used[key] = [0.0, 0.0, 0.0]
                                        for key in ['away_period_nzt', 'away_period_nztsa', 'away_period_ozs', 'away_period_nzs',
                                                   'away_period_dzs', 'away_period_fc', 'away_period_rush',
                                                   'home_period_nzt', 'home_period_nztsa', 'home_period_ozs', 'home_period_nzs',
                                                   'home_period_dzs', 'home_period_fc', 'home_period_rush']:
                                            metrics_used[key] = default_period.copy()
                                    
                                    # Calculate clutch metrics
                                    try:
                                        # Goals by period
                                        away_period_goals, _, _ = self.report_generator._calculate_goals_by_period(game_data, away_team_id)
                                        home_period_goals, _, _ = self.report_generator._calculate_goals_by_period(game_data, home_team_id)
                                        
                                        metrics_used['away_third_period_goals'] = away_period_goals[2] if len(away_period_goals) > 2 else 0
                                        metrics_used['home_third_period_goals'] = home_period_goals[2] if len(home_period_goals) > 2 else 0
                                        
                                        # One-goal game
                                        goal_diff = abs(away_goals - home_goals)
                                        metrics_used['away_one_goal_game'] = (goal_diff == 1)
                                        metrics_used['home_one_goal_game'] = (goal_diff == 1)
                                        
                                        # Who scored first
                                        first_goal_scorer = None
                                        if 'play_by_play' in game_data and 'plays' in game_data['play_by_play']:
                                            for play in game_data['play_by_play']['plays']:
                                                if play.get('typeDescKey') == 'goal':
                                                    details = play.get('details', {})
                                                    first_goal_scorer = details.get('eventOwnerTeamId')
                                                    break
                                        
                                        metrics_used['away_scored_first'] = (first_goal_scorer == away_team_id)
                                        metrics_used['home_scored_first'] = (first_goal_scorer == home_team_id)
                                        metrics_used['away_opponent_scored_first'] = (first_goal_scorer == home_team_id)
                                        metrics_used['home_opponent_scored_first'] = (first_goal_scorer == away_team_id)
                                    except Exception as e:
                                        print(f"    ⚠️  Error calculating clutch metrics: {e}")
                                        for key in ['away_third_period_goals', 'home_third_period_goals',
                                                   'away_one_goal_game', 'home_one_goal_game',
                                                   'away_scored_first', 'home_scored_first',
                                                   'away_opponent_scored_first', 'home_opponent_scored_first']:
                                            metrics_used[key] = False if 'game' in key or 'scored' in key else 0
                                    
                                    correlation_away_prob = None
                                    correlation_home_prob = None
                                    try:
                                        corr_prediction = self.corr_model.predict_from_metrics(metrics_used)
                                        correlation_away_prob = corr_prediction.get('away_prob')
                                        correlation_home_prob = corr_prediction.get('home_prob')
                                    except Exception:
                                        pass
                                    corr_disagreement = 0.0
                                    if correlation_away_prob is not None:
                                        if correlation_home_prob is not None:
                                            corr_disagreement = abs(float(correlation_away_prob) - float(correlation_home_prob))
                                        elif ensemble_away_prob is not None:
                                            corr_disagreement = abs(float(correlation_away_prob) - float(ensemble_away_prob))
                                    metrics_used["corr_disagreement"] = corr_disagreement
                                    flip_rate = 0.0
                                    try:
                                        flip_rate = self.learning_model._estimate_monte_carlo_signal(
                                            {
                                                "metrics_used": metrics_used,
                                                "predicted_winner": "away" if raw_away_prob >= raw_home_prob else "home",
                                                "raw_away_prob": raw_away_prob,
                                                "raw_home_prob": raw_home_prob
                                            },
                                            iterations=40
                                        )
                                    except Exception:
                                        flip_rate = 0.0
                                    metrics_used["monte_carlo_flip_rate"] = flip_rate
                                    upset_probability = self.learning_model.predict_upset_probability(
                                        [prediction_confidence, abs(raw_away_prob - raw_home_prob), corr_disagreement, flip_rate]
                                    )
                                    
                                    # Add to model
                                    self.learning_model.add_prediction(
                                        game_id=game_id,
                                        date=check_date,
                                        away_team=away_team,
                                        home_team=home_team,
                                        predicted_away_prob=predicted_away_prob,
                                        predicted_home_prob=predicted_home_prob,
                                        metrics_used=metrics_used,
                                        actual_winner=actual_winner,
                                        actual_away_score=away_goals,
                                        actual_home_score=home_goals,
                                        prediction_confidence=prediction_confidence,
                                        raw_away_prob=raw_away_prob,
                                        raw_home_prob=raw_home_prob,
                                        calibrated_away_prob=predicted_away_prob,
                                        calibrated_home_prob=predicted_home_prob,
                                        correlation_away_prob=correlation_away_prob,
                                        correlation_home_prob=correlation_home_prob,
                                        ensemble_away_prob=ensemble_away_prob,
                                        ensemble_home_prob=ensemble_home_prob
                                    )
                                    
                                    games_added += 1
                                    print(f"  ✅ Added missing game: {away_team} @ {home_team} ({actual_winner} won)")
                                    
                            except Exception as e:
                                print(f"  ❌ Error processing {away_team} @ {home_team}: {e}")
        
        if games_added > 0:
            print(f"🎉 Added {games_added} missing games to model")
        else:
            print("✅ No missing games found")
        
        # Fallback: scan stored predictions for stale entries without results
        stale_updates += self._repair_stale_predictions(predictions_store)
        
        total_updates = games_updated + stale_updates
        if total_updates > 0:
            self.learning_model.save_model_data()
            print(f"🔁 Updated results for {total_updates} previously tracked game(s)")
        
        return games_added + total_updates

    @staticmethod
    def _normalize_probability_value(value):
        if isinstance(value, (int, float)):
            val = float(value)
            if val > 1.0:
                val = val / 100.0
            return max(0.0, min(1.0, val))
        return None
    
    def _update_prediction_result_entry(self, prediction, away_team, home_team, away_goals, home_goals):
        if prediction is None:
            return False
        
        if away_goals == home_goals:
            return False
        
        actual_winner = "away" if away_goals > home_goals else "home"
        prediction['actual_winner'] = actual_winner
        prediction['actual_winner_side'] = actual_winner
        prediction['actual_winner_team'] = away_team if actual_winner == "away" else home_team
        prediction['actual_away_score'] = away_goals
        prediction['actual_home_score'] = home_goals
        prediction['result_updated_at'] = datetime.now().isoformat()
        
        away_prob = self._normalize_probability_value(prediction.get('predicted_away_win_prob'))
        home_prob = self._normalize_probability_value(prediction.get('predicted_home_win_prob'))
        if away_prob is not None and home_prob is not None:
            prediction['prediction_accuracy'] = away_prob if actual_winner == "away" else home_prob
        
        return True

    def _repair_stale_predictions(self, predictions_store):
        """Backfill results for older predictions still missing outcomes."""
        updates = 0
        central_tz = pytz.timezone('US/Central')
        central_now = datetime.now(central_tz).date()
        
        for pred in predictions_store:
            if pred.get('actual_winner'):
                continue
            game_id = str(pred.get('game_id') or '')
            if not game_id:
                continue
            pred_date_str = pred.get('date')
            try:
                pred_date = datetime.strptime(pred_date_str, '%Y-%m-%d').date() if pred_date_str else None
            except Exception:
                pred_date = None
            # Skip very recent predictions (probably future games)
            if pred_date and (central_now - pred_date).days < 1:
                continue
            
            try:
                game_data = self.api.get_comprehensive_game_data(game_id)
            except Exception as exc:
                print(f"  ⚠️  Unable to fetch stale game {game_id}: {exc}")
                continue
            
            if not game_data or 'boxscore' not in game_data:
                continue
            game_state = game_data.get('gameState') or game_data.get('gameStateId') or ''
            if game_state not in ['FINAL', 'OFF', '5', 'FINAL_OT', 'FINAL_SO']:
                continue
            
            away_team = pred.get('away_team')
            home_team = pred.get('home_team')
            try:
                away_goals = int(game_data['boxscore']['awayTeam'].get('score', 0))
                home_goals = int(game_data['boxscore']['homeTeam'].get('score', 0))
            except Exception:
                continue
            if away_goals == home_goals:
                continue
            
            if self._update_prediction_result_entry(pred, away_team, home_team, away_goals, home_goals):
                updates += 1
                winner_label = away_team if away_goals > home_goals else home_team
                print(f"  🔁 Backfilled stale result for {away_team} @ {home_team}: {winner_label} won")
        
        return updates
    
    def _compute_model_performance_fallback(self):
        """Compute performance from saved predictions if in-memory stats are empty."""
        try:
            with open('win_probability_predictions_v2.json', 'r') as f:
                data = json.load(f)
            predictions = data.get('predictions', [])
            total = 0
            correct = 0
            # Compute across all available finalized games
            for p in predictions:
                actual = p.get('actual_winner')
                # Derive predicted winner from probabilities
                away_prob = p.get('predicted_away_win_prob')
                home_prob = p.get('predicted_home_win_prob')
                predicted = None
                if isinstance(away_prob, (int, float)) and isinstance(home_prob, (int, float)):
                    predicted = 'away' if away_prob > home_prob else 'home'

                # Normalize actual winner to 'home'/'away' if it's a team abbrev
                if actual and actual not in ('home', 'away'):
                    away_team = p.get('away_team')
                    home_team = p.get('home_team')
                    if actual == away_team:
                        actual_side = 'away'
                    elif actual == home_team:
                        actual_side = 'home'
                    else:
                        actual_side = None
                else:
                    actual_side = actual

                if actual_side and predicted:
                    total += 1
                    if actual_side == predicted:
                        correct += 1
            if total > 0:
                acc = correct / total
                return {
                    'total_games': total,
                    'correct_predictions': correct,
                    'accuracy': acc,
                    'recent_accuracy': acc
                }
        except Exception:
            pass
        # If nothing found, return zeros (caller may decide what to display)
        return {
            'total_games': 0,
            'correct_predictions': 0,
            'accuracy': 0.0,
            'recent_accuracy': 0.0
        }
        
    def _calculate_win_probability(self, home_lambda, away_lambda):
        """
        Calculate the probability of Home Win, Away Win, and Tie
        using the Poisson distribution for independent events.
        """
        import math
        
        # Max reasonable goals to check (Poisson prob approaches 0)
        max_goals = 15
        
        prob_home_win = 0.0
        prob_away_win = 0.0
        prob_tie = 0.0
        
        for h in range(max_goals + 1):
            for a in range(max_goals + 1):
                p_h = (math.exp(-home_lambda) * home_lambda**h) / math.factorial(h)
                p_a = (math.exp(-away_lambda) * away_lambda**a) / math.factorial(a)
                p_matrix = p_h * p_a
                
                if h > a:
                    prob_home_win += p_matrix
                elif a > h:
                    prob_away_win += p_matrix
                else:
                    prob_tie += p_matrix
                    
        return prob_home_win, prob_away_win, prob_tie

    def get_daily_predictions(self):
        """
        Generate predictions for all games scheduled for the current date.
        Retains the exact score prediction logic but adds Conf/Vol context.
        """
        try:
            # Get today's games
            schedule = self.api.get_game_schedule()
            if not schedule or 'gameWeek' not in schedule:
                print("No schedule data found")
                return []
                
            today_games = []
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            for day in schedule['gameWeek']:
                if day['date'] == today_str:
                    today_games = day.get('games', [])
                    break
            
            if not today_games:
                print(f"No games found for {today_str}")
                return []
                
            predictions = []
            
            for game in today_games:
                try:
                    # Basic Info
                    game_id = game.get('id')
                    home_data = game.get('homeTeam', {})
                    away_data = game.get('awayTeam', {})
                    home_team = home_data.get('abbrev')
                    away_team = away_data.get('abbrev')
                    start_time = game.get('startTimeUTC')
                    
                    if not home_team or not away_team:
                        continue
                        
                    # Get Team Stats (Season)
                    home_perf = self.learning_model.get_team_performance(home_team, venue="home")
                    away_perf = self.learning_model.get_team_performance(away_team, venue="away")

                    # --- ADVANCED ACCURACY LOGIC: FATIGUE & RECENCY ---
                    
                    # 1. Schedule Fatigue (Back-to-Back)
                    # If played yesterday -> 5% Offense Penalty, 5% Defense Penalty (allow more)
                    h_fatigue = False
                    a_fatigue = False
                    if self.schedule_analyzer:
                        h_fatigue = self.schedule_analyzer.played_yesterday(home_team, today_str)
                        a_fatigue = self.schedule_analyzer.played_yesterday(away_team, today_str)
                    
                    fatigue_factor = 0.95 

                    # 2. Recency Bias (Last 10 Games)
                    # Blend: 60% Season / 40% L10
                    recency_weight = 0.40
                    season_weight = 0.60
                    
                    h_recent_xg = 3.0
                    h_recent_goals = 3.0
                    h_recent_xg_ag = 3.0
                    h_recent_g_ag = 3.0
                    
                    a_recent_xg = 3.0
                    a_recent_goals = 3.0
                    a_recent_xg_ag = 3.0
                    a_recent_g_ag = 3.0

                    if self.schedule_analyzer:
                        # Home Recent
                        h_games = self.schedule_analyzer.get_recent_games(home_team, today_str, n=10)
                        if h_games:
                             # Calculate averages
                            tot_g = 0; tot_ga = 0
                            for g in h_games:
                                is_home = (g.get('homeTeam', {}).get('abbrev') == home_team)
                                if is_home:
                                    tot_g += g.get('homeTeam', {}).get('score', 0)
                                    tot_ga += g.get('awayTeam', {}).get('score', 0)
                                else:
                                    tot_g += g.get('awayTeam', {}).get('score', 0)
                                    tot_ga += g.get('homeTeam', {}).get('score', 0)
                            h_recent_goals = tot_g / len(h_games)
                            h_recent_g_ag = tot_ga / len(h_games)
                            # Approximation: Use Goals as proxy for xG in recent data if raw xG not avail
                            h_recent_xg = h_recent_goals 
                            h_recent_xg_ag = h_recent_g_ag

                        # Away Recent
                        a_games = self.schedule_analyzer.get_recent_games(away_team, today_str, n=10)
                        if a_games:
                            tot_g = 0; tot_ga = 0
                            for g in a_games:
                                is_home = (g.get('homeTeam', {}).get('abbrev') == away_team)
                                if is_home:
                                    tot_g += g.get('homeTeam', {}).get('score', 0)
                                    tot_ga += g.get('awayTeam', {}).get('score', 0)
                                else:
                                    tot_g += g.get('awayTeam', {}).get('score', 0)
                                    tot_ga += g.get('homeTeam', {}).get('score', 0)
                            a_recent_goals = tot_g / len(a_games)
                            a_recent_g_ag = tot_ga / len(a_games)
                            a_recent_xg = a_recent_goals
                            a_recent_xg_ag = a_recent_g_ag

                    # --- BLENDED METRICS ---
                    
                    # Home Offense
                    h_xg_season = float(home_perf.get("xg_avg", 3.0))
                    h_goals_season = float(home_perf.get("goals_avg", 3.0))
                    h_xg_blend = (h_xg_season * season_weight) + (h_recent_xg * recency_weight)
                    h_goals_blend = (h_goals_season * season_weight) + (h_recent_goals * recency_weight)
                    
                    # Home Defense
                    h_xg_ag_season = float(home_perf.get("xg_against_avg", 3.0))
                    h_g_ag_season = float(home_perf.get("goals_against_avg", 3.0))
                    h_xg_ag_blend = (h_xg_ag_season * season_weight) + (h_recent_xg_ag * recency_weight)
                    h_g_ag_blend = (h_g_ag_season * season_weight) + (h_recent_g_ag * recency_weight)

                    # Away Offense
                    a_xg_season = float(away_perf.get("xg_avg", 3.0))
                    a_goals_season = float(away_perf.get("goals_avg", 3.0))
                    a_xg_blend = (a_xg_season * season_weight) + (a_recent_xg * recency_weight)
                    a_goals_blend = (a_goals_season * season_weight) + (a_recent_goals * recency_weight)

                    # Away Defense
                    a_xg_ag_season = float(away_perf.get("xg_against_avg", 3.0))
                    a_g_ag_season = float(away_perf.get("goals_against_avg", 3.0))
                    a_xg_ag_blend = (a_xg_ag_season * season_weight) + (a_recent_xg_ag * recency_weight)
                    a_g_ag_blend = (a_g_ag_season * season_weight) + (a_recent_g_ag * recency_weight)


                    # --- 5-FACTOR ADVANCED MODEL (OPTIMIZED) ---
                    # W_XG=0.53, W_OFF_H=0.58, W_OFF_A=0.65, W_POSS=0.026, W_ST=0.017, W_LUCK=0.002
                    
                    # 1. Base Offense
                    h_base = (h_xg_blend * 0.53) + (h_goals_blend * 0.47)
                    a_base = (a_xg_blend * 0.53) + (a_goals_blend * 0.47)
                    
                    # 2. Base Defense 
                    h_def_base = (h_xg_ag_blend * 0.53) + (h_g_ag_blend * 0.47)
                    a_def_base = (a_xg_ag_blend * 0.53) + (a_g_ag_blend * 0.47)

                    # Apply Fatigue Penalties
                    if h_fatigue:
                        h_base *= fatigue_factor # Offense suffers
                        h_def_base *= (2 - fatigue_factor) # Defense gets worse (1.05 multiplier approx)
                    
                    if a_fatigue:
                        a_base *= fatigue_factor
                        a_def_base *= (2 - fatigue_factor)

                    # 3. Possession Adjustment
                    h_corsi = float(home_perf.get("corsi_avg", 50.0))
                    a_corsi = float(away_perf.get("corsi_avg", 50.0))
                    h_poss_adj = (h_corsi - 50.0) * 0.026 
                    a_poss_adj = (a_corsi - 50.0) * 0.026

                    # 4. Special Teams Matchup
                    h_pp = float(home_perf.get("power_play_avg", 20.0))
                    a_pk = float(away_perf.get("penalty_kill_avg", 80.0))
                    h_st_adj = ((h_pp - 20.0) + (80.0 - a_pk)) * 0.017
                    
                    a_pp = float(away_perf.get("power_play_avg", 20.0))
                    h_pk = float(home_perf.get("penalty_kill_avg", 80.0))
                    a_st_adj = ((a_pp - 20.0) + (80.0 - h_pk)) * 0.017

                    # 5. Luck Adjustment
                    h_pdo = float(home_perf.get("pdo_avg", 100.0))
                    a_pdo = float(away_perf.get("pdo_avg", 100.0))
                    h_luck_adj = (100.0 - h_pdo) * 0.002
                    a_luck_adj = (100.0 - a_pdo) * 0.002

                    # Final Lambda
                    home_exp_raw = (h_base * 0.58) + (a_def_base * 0.42) 
                    home_exp = home_exp_raw + h_poss_adj + h_st_adj + h_luck_adj + 0.02
                    
                    away_exp_raw = (a_base * 0.65) + (h_def_base * 0.35)
                    away_exp = away_exp_raw + a_poss_adj + a_st_adj + a_luck_adj

                    home_exp = max(1.0, min(6.5, home_exp))
                    away_exp = max(1.0, min(6.5, away_exp))
                    
                    # Log inputs for debugging variety
                    print(f"   [Debug] xG inputs: {away_team} {away_exp:.2f} @ {home_team} {home_exp:.2f}")

                    # Predict Score
                    home_goals, away_goals = self.learning_model.predict_score_distribution(home_exp, away_exp)
                    
                    # Calculate Win Prob & Volatility
                    p_home, p_away, p_tie = self._calculate_win_probability(home_exp, away_exp)
                    
                    if home_goals > away_goals:
                        confidence = p_home + (p_tie / 2)
                        winner = home_team
                    else:
                        confidence = p_away + (p_tie / 2)
                        winner = away_team
                        
                    # Handle Ties (e.g. 2-2, 3-3) by assigning OT winner
                    # This ensures "Final Score" validity (no ties) and variety (3-2 OT, 4-3 OT)
                    if home_goals == away_goals:
                        # Give the win to the team with higher probability
                        if p_home >= p_away:
                            home_goals += 1
                            winner = home_team
                            confidence = p_home + (p_tie / 2)
                        else:
                            away_goals += 1
                            winner = away_team
                            confidence = p_away + (p_tie / 2)
                    elif abs(home_goals - away_goals) == 1 and (confidence * 100) <= 60.0:
                         # Close game (e.g. 3-2) with low confidence -> Likely went to OT
                         pass
                        
                    confidence_pct = min(99.9, max(50.1, confidence * 100))
                    
                    # Determine Volatility
                    total_exp = home_exp + away_exp
                    if total_exp < 5.5:
                        volatility = "Low"
                    elif total_exp > 6.5:
                        volatility = "High"
                    else:
                        volatility = "Medium"

                    # Determine Upset Risk
                    upset_prob = 100.0 - confidence_pct
                    if upset_prob > 40.0:
                        upset_risk = "High"
                    elif upset_prob > 25.0:
                        upset_risk = "Medium"
                    else:
                        upset_risk = "Low"
                    
                except Exception as e:
                    # logger hasn't been defined here, using print
                    print(f"Error determining prediction for {home_team} vs {away_team}: {e}")
                    home_goals = 3
                    away_goals = 2
                    confidence_pct = 50.0
                    volatility = "Medium"
                    upset_risk = "Medium"
                    upset_prob = 50.0
                    winner = home_team
                
                # Add Fatigue tag to reasoning if applicable
                reasoning_str = f"Model favors {winner} ({confidence_pct:.1f}%) in {volatility}-volatility matchup. Upset Risk: {upset_risk} ({upset_prob:.1f}%)."
                if h_fatigue:
                    reasoning_str += f" ALERT: {home_team} is fatigued (Back-to-Back)."
                if a_fatigue:
                    reasoning_str += f" ALERT: {away_team} is fatigued (Back-to-Back)."

                predictions.append({
                    'game_id': game_id,
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': home_goals,
                    'away_score': away_goals,
                    'confidence': confidence_pct,
                    'volatility': volatility,
                    'upset_risk': upset_risk,
                    'upset_prob': upset_prob,
                    'start_time': start_time,
                    'reasoning': reasoning_str
                })
            
            return predictions
        except Exception as e:
            print(f"Error in get_daily_predictions: {e}")
            return []
        
    def get_todays_predictions(self):
        """Get predictions for today's games using the self-learning model"""
        print('🏒 NHL GAME PREDICTIONS (Self-Learning Model) 🏒')
        print('=' * 60)
        central_tz = pytz.timezone('US/Central')
        now_ct = datetime.now(central_tz)
        print(f'📅 Date (CT): {now_ct.strftime("%Y-%m-%d")}')
        
        # Check for missing games first
        missing_games = self.check_and_add_missing_games()
        if missing_games > 0:
            print(f"📈 Model updated with {missing_games} missing games")
            # Recalculate model performance after adding missing games
            try:
                self.learning_model.recalculate_performance_from_scratch()
            except Exception as e:
                print(f"⚠️  Warning: Could not recalculate performance: {e}")
        
        # Show model architecture
        print(f'🎯 Prediction Model: 70% Correlation-Weighted + 30% Ensemble')
        completed_count = len([p for p in self.learning_model.model_data.get("predictions", []) if p.get("actual_winner")])
        print(f'   (Correlation model uses re-fitted weights from {completed_count} completed games)')
        print()
        
        # Define today's window in Central Time and convert to UTC bounds
        start_of_day_ct = now_ct.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day_ct = start_of_day_ct + timedelta(days=1)
        start_utc = start_of_day_ct.astimezone(pytz.utc)
        end_utc = end_of_day_ct.astimezone(pytz.utc)

        # Fetch schedule for the week (API returns a gameWeek)
        schedule_data = self.api.get_game_schedule(now_ct.strftime('%Y-%m-%d'))
        
        # Get ONLY today's games using the day bucket matching Central date
        games = []
        today_ct_str = now_ct.strftime('%Y-%m-%d')
        for day_data in schedule_data.get('gameWeek', []):
            if not isinstance(day_data, dict):
                continue
            if day_data.get('date') == today_ct_str and 'games' in day_data:
                games.extend(day_data['games'])
        
        # Helper to parse ISO8601 UTC timestamps
        def parse_utc(ts: str):
            try:
                # Ensure timezone-aware
                return datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(pytz.utc)
            except Exception:
                return None

        # Filter for games starting within today's Central day, using UTC bounds (extra safety)
        today_games = []
        for game in games:
            ts = game.get('startTimeUTC')
            dt_utc = parse_utc(ts) if isinstance(ts, str) else None
            if not dt_utc:
                continue
            if start_utc <= dt_utc < end_utc and game.get('gameState') in ['PRE', 'FUT']:
                today_games.append(game)
        
        print(f'🔍 Found {len(today_games)} games today')
        print()
        
        # Generate predictions using the self-learning model
        predictions = []
        for i, game in enumerate(today_games):
            away_team = game.get('awayTeam', {}).get('abbrev', 'UNK')
            home_team = game.get('homeTeam', {}).get('abbrev', 'UNK')
            game_time = game.get('startTimeUTC', 'UNK')
            # Convert to Central for display if possible
            try:
                dt_utc = parse_utc(game_time)
                game_time_ct = dt_utc.astimezone(central_tz).strftime('%Y-%m-%d %I:%M %p CT') if dt_utc else game_time
            except Exception:
                game_time_ct = game_time
            
            print(f'{i+1}. {away_team} @ {home_team}')
            print(f'   🕐 Time: {game_time_ct}')
            
            # Get prediction using self-learning model (pass game_id for lineup confirmation)
            game_id = str(game.get('id'))
            prediction = self.predict_game(away_team, home_team, game_id=game_id)
            
            away_prob = prediction["away_prob"]
            home_prob = prediction["home_prob"]
            print(f'   🎯 Prediction: {away_team} {away_prob*100:.1f}% | {home_team} {home_prob*100:.1f}%')
            
            # Determine favorite
            if away_prob > home_prob:
                favorite = away_team
            else:
                favorite = home_team
            confidence = max(away_prob, home_prob) * 100.0
            flip_rate = float(prediction.get("monte_carlo_flip_rate", 0.0) or 0.0)
            upset = float(prediction.get("upset_probability", 0.0) or 0.0) * 100.0

            # Flip-rate band label
            if flip_rate < 0.20:
                flip_label = "LOW"
            elif flip_rate < 0.40:
                flip_label = "MED"
            else:
                flip_label = "HIGH"

            # Likeliest score using ADVANCED team + venue + situational data
            try:
                home_perf = self.learning_model.get_team_performance(home_team, venue="home")
                away_perf = self.learning_model.get_team_performance(away_team, venue="away")
                
                # --- START WITH VENUE-SPECIFIC SEASON STATS (most reliable) ---
                today_str = datetime.now().strftime('%Y-%m-%d')
                
                # 1. Schedule Fatigue (Back-to-Back) - lighter penalty
                h_fatigue = False
                a_fatigue = False
                if self.schedule_analyzer:
                    try:
                        h_fatigue = self.schedule_analyzer.played_yesterday(home_team, today_str)
                        a_fatigue = self.schedule_analyzer.played_yesterday(away_team, today_str)
                    except Exception:
                        pass  # Schedule analyzer may not work in all environments
                
                fatigue_factor = 0.97  # 3% penalty (was 5%)
                
                # 2. Use venue-specific season stats as PRIMARY source (80%)
                # Only blend in recent form if available (20%)
                recency_weight = 0.20  # Reduced from 0.40
                season_weight = 0.80   # Increased from 0.60
                
                # Get season stats from venue-specific performance
                h_xg_season = float(home_perf.get("xg_avg", 3.0))
                h_goals_season = float(home_perf.get("goals_avg", 3.0))
                h_xg_ag_season = float(home_perf.get("xg_against_avg", 3.0))
                h_g_ag_season = float(home_perf.get("goals_against_avg", 3.0))
                
                a_xg_season = float(away_perf.get("xg_avg", 3.0))
                a_goals_season = float(away_perf.get("goals_avg", 3.0))
                a_xg_ag_season = float(away_perf.get("xg_against_avg", 3.0))
                a_g_ag_season = float(away_perf.get("goals_against_avg", 3.0))
                
                # Get recent form (last 5 games) directly from stats
                h_recent_form = self.learning_model._calculate_recent_form_from_stats(home_team.upper(), "home", n=5)
                a_recent_form = self.learning_model._calculate_recent_form_from_stats(away_team.upper(), "away", n=5)
                
                # Use recent form if available, otherwise use season stats
                h_recent_xg = h_recent_form.get('xg_avg', h_xg_season)
                h_recent_goals = h_recent_form.get('goals_avg', h_goals_season)
                h_recent_xg_ag = h_recent_form.get('xg_against_avg', h_xg_ag_season)
                h_recent_g_ag = h_recent_form.get('goals_against_avg', h_g_ag_season)
                
                a_recent_xg = a_recent_form.get('xg_avg', a_xg_season)
                a_recent_goals = a_recent_form.get('goals_avg', a_goals_season)
                a_recent_xg_ag = a_recent_form.get('xg_against_avg', a_xg_ag_season)
                a_recent_g_ag = a_recent_form.get('goals_against_avg', a_g_ag_season)
                
                # --- EMPIRICALLY-DRIVEN MODEL (Based on Correlation Analysis) ---
                # Correlation analysis revealed what ACTUALLY predicts goals:
                # 1. PDO (luck/sh%/sv%): r=0.655 (STRONG)
                # 2. Power Play %: r=0.498 (MODERATE)  
                # 3. xG: r=0.107 (VERY WEAK - surprisingly!)
                
                # Get all metrics
                h_goals = float(home_perf.get("goals_avg", 3.0))
                h_pdo = float(home_perf.get("pdo_avg", 100.0))
                h_pp = float(home_perf.get("power_play_avg", 20.0))
                h_xg = float(home_perf.get("xg_avg", 3.0))
                h_ga = float(home_perf.get("goals_against_avg", 3.0))
                h_xga = float(home_perf.get("xg_against_avg", 3.0))
                
                a_goals = float(away_perf.get("goals_avg", 3.0))
                a_pdo = float(away_perf.get("pdo_avg", 100.0))
                a_pp = float(away_perf.get("power_play_avg", 20.0))
                a_xg = float(away_perf.get("xg_avg", 3.0))
                a_ga = float(away_perf.get("goals_against_avg", 3.0))
                a_xga = float(away_perf.get("xg_against_avg", 3.0))
                
                # Check OT/SO tendency (teams that play close games)
                h_ot_tendency = False
                a_ot_tendency = False
                
                # Calculate if this is an OT/SO likely team
                # Teams with avg goal diff < 1.5 push games to OT often
                try:
                    h_team_stats = self.learning_model.team_stats.get(home_team.upper(), {}).get("home", {})
                    if h_team_stats and 'goals' in h_team_stats and 'opp_goals' in h_team_stats:
                        h_goals_arr = h_team_stats['goals']
                        h_ga_arr = h_team_stats['opp_goals']
                        if len(h_goals_arr) == len(h_ga_arr) and len(h_goals_arr) > 0:
                            import numpy as np
                            h_avg_diff = np.mean([abs(g - ga) for g, ga in zip(h_goals_arr, h_ga_arr)])
                            h_close_pct = sum(1 for g, ga in zip(h_goals_arr, h_ga_arr) if abs(g - ga) <= 1) / len(h_goals_arr)
                            h_ot_tendency = h_close_pct > 0.60
                            
                    a_team_stats = self.learning_model.team_stats.get(away_team.upper(), {}).get("away", {})
                    if a_team_stats and 'goals' in a_team_stats and 'opp_goals' in a_team_stats:
                        a_goals_arr = a_team_stats['goals']
                        a_ga_arr = a_team_stats['opp_goals']
                        if len(a_goals_arr) == len(a_ga_arr) and len(a_goals_arr) > 0:
                            import numpy as np
                            a_avg_diff = np.mean([abs(g - ga) for g, ga in zip(a_goals_arr, a_ga_arr)])
                            a_close_pct = sum(1 for g, ga in zip(a_goals_arr, a_ga_arr) if abs(g - ga) <= 1) / len(a_goals_arr)
                            a_ot_tendency = a_close_pct > 0.60
                except:
                    pass
                
                # Blend in recent form (light touch)
                h_recent_form = self.learning_model._calculate_recent_form_from_stats(home_team.upper(), "home", n=5)
                a_recent_form = self.learning_model._calculate_recent_form_from_stats(away_team.upper(), "away", n=5)
                
                if h_recent_form:
                    h_goals = (h_goals * 0.90) + (h_recent_form.get('goals_avg', h_goals) * 0.10)
                if a_recent_form:
                    a_goals = (a_goals * 0.90) + (a_recent_form.get('goals_avg', a_goals) * 0.10)
                
                # Fatigue
                if h_fatigue:
                    h_goals *= 0.95
                    h_pdo *= 0.98
                if a_fatigue:
                    a_goals *= 0.95
                    a_pdo *= 0.98
                
                # --- EMPIRICAL FORMULA (weights from correlation analysis) ---
                # PDO: 36.2% weight (strongest predictor)
                # PP%: 27.5% weight (2nd strongest)
                # xG: 10% weight (surprisingly weak - use as sanity check)
                # Goals: 26.3% weight (actual results matter)
                
                # PDO adjustment (100 = league average, >100 = lucky/good, <100 = unlucky/bad)
                h_pdo_factor = ((h_pdo - 100.0) / 100.0) * 1.5  # ±1.5 goals for +/-10 PDO
                a_pdo_factor = ((a_pdo - 100.0) / 100.0) * 1.5
                
                # Power Play impact (20% is league average)
                h_pp_factor = (h_pp - 20.0) * 0.03  # ±0.3 goals for ±10% PP
                a_pp_factor = (a_pp - 20.0) * 0.03
                
                # Base prediction (goals scored + PDO effect + PP effect + small xG check)
                home_exp = (h_goals * 0.40) + h_pdo_factor + h_pp_factor + (h_xg * 0.15) + 0.20  # home ice
                away_exp = (a_goals * 0.40) + a_pdo_factor + a_pp_factor + (a_xg * 0.15)
                
                # Defensive adjustment (opponent weakness)
                home_exp += (a_ga * 0.25)
                away_exp += (h_ga * 0.25)
                
                # Bounds
                home_exp = max(1.5, min(6.5, home_exp))
                away_exp = max(1.5, min(6.5, away_exp))

                logger.info(f"5-Factor Model (Optimized) {home_team} vs {away_team}:")
            # Predict exact score using Poisson Distribution
                home_goals, away_goals = self.learning_model.predict_score_distribution(home_exp, away_exp)
                
                # Calculate Win Probability (Confidence)
                p_home, p_away, p_tie = self._calculate_win_probability(home_exp, away_exp)
                
                # Determine Confidence Level
                if home_goals > away_goals:
                    confidence = p_home + (p_tie / 2) # Give tie probability split
                    win_prob = p_home
                else:
                    confidence = p_away + (p_tie / 2)
                    win_prob = p_away
                    
                confidence_pct = min(99.9, max(50.1, confidence * 100))
                
                # Determine Volatility (risk of high variance)
                # Volatility is function of Total Expected Goals (Lambda sum)
                total_exp = home_exp + away_exp
                if total_exp < 5.5:
                    volatility = "Low" # Defensive battle, predictable
                elif total_exp > 6.5:
                    volatility = "High" # Shootout, high variance
                else:
                    volatility = "Medium"
                
            except Exception as e:
                logger.error(f"Error determining prediction for {home_team} vs {away_team}: {e}")
                home_goals = 3
                away_goals = 2
                confidence_pct = 50.0
                volatility = "Medium"

            # Calculate likeliest exact score using Poisson distribution
            # This finds the scoreline (e.g. 4-2) with the highest mathematical probability
            try:
                home_goals, away_goals = self.learning_model.predict_score_distribution(home_exp, away_exp)
            except Exception:
                # Fallback if model method fails
                home_goals = int(round(home_exp))
                away_goals = int(round(away_exp))
            
            # Verify favorite wins in the scoreline if probability > 60% (margin of safety)
            # Poisson often predicts 2-2 or 3-3 even if one team is favored.
            # If the favorite has a strong probability, we ensure they have at least +1 goal.
            fav_prob = home_prob if favorite == home_team else away_prob
            fav_prob_pct = fav_prob * 100.0
            
            if fav_prob_pct > 60.0:
                if favorite == home_team and home_goals <= away_goals:
                     # Force home win
                     if home_goals == away_goals:
                         home_goals += 1
                     else:
                         home_goals, away_goals = away_goals, home_goals
                     
                     
                     # If score is now too low compared to expectation, bump up
                     # Only if significant difference (> 0.5 goals) to avoid gratuitous bumps
                     if home_goals < (home_exp - 0.5):
                         home_goals += 1
                         
                elif favorite == away_team and away_goals <= home_goals:
                     # Force away win
                     if away_goals == home_goals:
                         away_goals += 1
                     else:
                         home_goals, away_goals = away_goals, home_goals
                         
                     # If score is now too low compared to expectation, bump up
                     if away_goals < (away_exp - 0.5):
                         away_goals += 1

            # Handle Ties (e.g. 2-2, 3-3) by assigning OT winner
            if home_goals == away_goals:
                ot_tag = "(OT/SO)"
                # Give the win to the team with higher probability
                if fav_prob_pct > 50.0:
                    if favorite == home_team:
                        home_goals += 1
                    else:
                        away_goals += 1
                else:
                    # Pure coin flip scenarios (rare), give to home team as edge
                    home_goals += 1
            elif abs(home_goals - away_goals) == 1 and fav_prob_pct <= 60.0:
                 # Close game (e.g. 3-2) with low confidence -> Likely went to OT
                 ot_tag = "(OT/SO)"
            elif (h_ot_tendency or a_ot_tendency) and abs(home_goals - away_goals) <= 1:
                 # Team has empirical tendency to play close games (>60%)
                 ot_tag = "(OT/SO)"
            else:
                 ot_tag = ""
                 
            # Identify the score winner for display
            if home_goals > away_goals:
                score_winner = home_team
            else:
                score_winner = away_team

            # Ensure we display "Winner High-Low"
            likely_score = f"{score_winner} {max(home_goals, away_goals)}–{min(home_goals, away_goals)} {ot_tag}"

            print(f'   ⭐ Favorite: {favorite} (confidence {confidence_pct:.1f}%)')
            print(f'   🌪️ Volatility (flip-rate): {flip_label} ({flip_rate*100:.1f}%)')
            print(f'   ⚡ Upset risk: {upset:.1f}%')
            print(f'   📐 Likeliest score: {likely_score}')
            print()
            
            predictions.append({
                'game_id': game.get('id'),
                'away_team': away_team,
                'home_team': home_team,
                'predicted_away_win_prob': away_prob,  # Already decimal
                'predicted_home_win_prob': home_prob,  # Already decimal
                'prediction_confidence': max(away_prob, home_prob),
                'raw_away_prob': prediction.get("raw_away_prob"),
                'raw_home_prob': prediction.get("raw_home_prob"),
                'correlation_away_prob': prediction.get("correlation_away_prob"),
                'correlation_home_prob': prediction.get("correlation_home_prob"),
                'ensemble_away_prob': prediction.get("ensemble_away_prob"),
                'ensemble_home_prob': prediction.get("ensemble_home_prob"),
                'corr_disagreement': prediction.get("corr_disagreement"),
                'monte_carlo_flip_rate': prediction.get("monte_carlo_flip_rate"),
                'upset_probability': prediction.get("upset_probability"),
                'context_bucket': prediction.get("context_bucket"),
                'away_back_to_back': prediction.get("away_back_to_back"),
                'home_back_to_back': prediction.get("home_back_to_back"),
                'away_rest': prediction.get("away_rest"),
                'home_rest': prediction.get("home_rest"),
                'favorite': favorite,
                'spread': abs(away_prob - home_prob)
            })

        # Save predictions to model for future learning
        for pred in predictions:
            try:
                # Include situational features at prediction time
                game_date = datetime.now().strftime('%Y-%m-%d')
                # --- Situational / context features for this prediction ---
                # Rest days and back-to-back flags
                try:
                    away_rest = self.learning_model._calculate_rest_days_advantage(
                        pred['away_team'], 'away', game_date
                    )
                    home_rest = self.learning_model._calculate_rest_days_advantage(
                        pred['home_team'], 'home', game_date
                    )
                except Exception:
                    away_rest = 0.0
                    home_rest = 0.0

                # Derive consistent context bucket + B2B flags from rest advantage
                context_bucket = self.learning_model.determine_context_bucket(away_rest, home_rest)
                away_back_to_back = away_rest <= -0.5
                home_back_to_back = home_rest <= -0.5

                # Goalie performance signal (may be 0.0 if we don't have data yet)
                try:
                    away_goalie_perf = self.learning_model._goalie_performance_for_game(
                        pred['away_team'], 'away', game_date
                    )
                    home_goalie_perf = self.learning_model._goalie_performance_for_game(
                        pred['home_team'], 'home', game_date
                    )
                except Exception:
                    away_goalie_perf = 0.0
                    home_goalie_perf = 0.0
                try:
                    away_sos = self.learning_model._calculate_sos(pred['away_team'], 'away')
                    home_sos = self.learning_model._calculate_sos(pred['home_team'], 'home')
                except Exception:
                    away_sos = 0.0
                    home_sos = 0.0
                try:
                    away_venue_win_pct = self.learning_model._calculate_venue_win_percentage(pred['away_team'], 'away')
                    home_venue_win_pct = self.learning_model._calculate_venue_win_percentage(pred['home_team'], 'home')
                except Exception:
                    away_venue_win_pct = 0.5
                    home_venue_win_pct = 0.5

                # Store all situational context in metrics_used so nothing silently
                # drops on the floor in the training data.
                metrics_used = {
                    "away_rest": away_rest,
                    "home_rest": home_rest,
                    "context_bucket": context_bucket,
                    "away_back_to_back": away_back_to_back,
                    "home_back_to_back": home_back_to_back,
                    "away_goalie_perf": away_goalie_perf,
                    "home_goalie_perf": home_goalie_perf,
                    "away_sos": away_sos,
                    "home_sos": home_sos,
                    "away_venue_win_pct": away_venue_win_pct,
                    "home_venue_win_pct": home_venue_win_pct,
                    "corr_disagreement": pred.get('corr_disagreement'),
                    "monte_carlo_flip_rate": pred.get('monte_carlo_flip_rate'),
                }
                self.learning_model.add_prediction(
                    game_id=pred.get('game_id', ''),
                    date=game_date,
                    away_team=pred['away_team'],
                    home_team=pred['home_team'],
                    predicted_away_prob=pred['predicted_away_win_prob'],
                    predicted_home_prob=pred['predicted_home_win_prob'],
                    metrics_used=metrics_used,  # Store situational context
                    actual_winner=None,  # Will be updated when game completes
                    prediction_confidence=pred.get('prediction_confidence'),
                    raw_away_prob=pred.get('raw_away_prob'),
                    raw_home_prob=pred.get('raw_home_prob'),
                    calibrated_away_prob=pred.get('predicted_away_win_prob'),
                    calibrated_home_prob=pred.get('predicted_home_win_prob'),
                    correlation_away_prob=pred.get('correlation_away_prob'),
                    correlation_home_prob=pred.get('correlation_home_prob'),
                    ensemble_away_prob=pred.get('ensemble_away_prob'),
                    ensemble_home_prob=pred.get('ensemble_home_prob')
                )
            except Exception as e:
                print(f"⚠️  Error saving prediction: {e}")

        # Run daily learning update (only learn from completed games, not future predictions)
        try:
            self.learning_model.run_daily_update()
        except Exception as e:
            print(f"⚠️  Error updating learning model: {e}")

        return predictions
    
    def predict_game(self, away_team, home_team, game_id: Optional[str] = None):
        """Predict a single game using correlation model (primary) with ensemble as fallback.
        
        Args:
            away_team: Away team abbreviation
            home_team: Home team abbreviation
            game_id: Optional game ID for lineup confirmation
        """
        # Build situational metrics for correlation model & learning model pre-game
        today_str = datetime.now().strftime('%Y-%m-%d')
        try:
            away_rest = self.learning_model._calculate_rest_days_advantage(away_team, 'away', today_str)
            home_rest = self.learning_model._calculate_rest_days_advantage(home_team, 'home', today_str)
        except Exception:
            away_rest = home_rest = 0.0
        context_bucket = self.learning_model.determine_context_bucket(away_rest, home_rest)
        away_b2b = away_rest <= -0.5
        home_b2b = home_rest <= -0.5
        
        # First-goal profile features (pre-game, by venue)
        away_fg = self.learning_model.get_first_goal_profile(away_team, venue="away")
        home_fg = self.learning_model.get_first_goal_profile(home_team, venue="home")
        
        # Check for confirmed goalies first, fallback to prediction
        away_goalie_confirmed = None
        home_goalie_confirmed = None
        if game_id:
            away_goalie_confirmed = self.lineup_service.get_confirmed_goalie(away_team, game_id, today_str)
            home_goalie_confirmed = self.lineup_service.get_confirmed_goalie(home_team, game_id, today_str)
        
        try:
            # If confirmed goalies available, use those for GSAX calculation
            # Otherwise use predicted starter GSAX
            away_goalie_perf = self.learning_model._goalie_performance_for_game(
                away_team, 'away', today_str, confirmed_goalie=away_goalie_confirmed
            )
            home_goalie_perf = self.learning_model._goalie_performance_for_game(
                home_team, 'home', today_str, confirmed_goalie=home_goalie_confirmed
            )
        except Exception:
            away_goalie_perf = home_goalie_perf = 0.0
        
        # Calculate goalie matchup quality and special teams matchup
        try:
            goalie_matchup_quality = self.learning_model._calculate_goalie_matchup_quality(
                away_team, home_team, today_str,
                away_goalie_confirmed=away_goalie_confirmed,
                home_goalie_confirmed=home_goalie_confirmed
            )
            special_teams_matchup = self.learning_model._calculate_special_teams_matchup(away_team, home_team)
        except Exception:
            goalie_matchup_quality = 0.0
            special_teams_matchup = 0.0
        try:
            away_sos = self.learning_model._calculate_sos(away_team, 'away')
            home_sos = self.learning_model._calculate_sos(home_team, 'home')
        except Exception:
            away_sos = home_sos = 0.5
        # Team venue performance proxies
        away_perf = self.learning_model.get_team_performance(away_team, 'away')
        home_perf = self.learning_model.get_team_performance(home_team, 'home')
        # Get recent form (last 5-10 games windowed)
        away_recent_form = away_perf.get('recent_form', 0.5)
        home_recent_form = home_perf.get('recent_form', 0.5)
        
        # --- Simple lineup / team-strength scaffolding ---
        # Placeholder for future enhancement: use LineupService and player-level
        # metrics to estimate how close each team is to full strength.
        # For now, we assume full-strength (1.0) so the feature is wired but neutral.
        away_lineup_strength = 1.0
        home_lineup_strength = 1.0
        
        # Get venue-specific win percentages (full season)
        try:
            away_venue_win_pct = self.learning_model._calculate_venue_win_percentage(away_team, 'away')
            home_venue_win_pct = self.learning_model._calculate_venue_win_percentage(home_team, 'home')
        except Exception:
            away_venue_win_pct = 0.5
            home_venue_win_pct = 0.5
        
        metrics = {
            'away_gs': away_perf.get('gs_avg', 0.0), 'home_gs': home_perf.get('gs_avg', 0.0),
            'away_power_play_pct': away_perf.get('power_play_avg', 0.0), 'home_power_play_pct': home_perf.get('power_play_avg', 0.0),
            'away_blocked_shots': away_perf.get('blocked_shots_avg', 0.0), 'home_blocked_shots': home_perf.get('blocked_shots_avg', 0.0),
            'away_corsi_pct': away_perf.get('corsi_avg', 50.0), 'home_corsi_pct': home_perf.get('corsi_avg', 50.0),
            'away_hits': away_perf.get('hits_avg', 0.0), 'home_hits': home_perf.get('hits_avg', 0.0),
            'away_rest': away_rest, 'home_rest': home_rest,
            'away_hdc': away_perf.get('hdc_avg', 0.0), 'home_hdc': home_perf.get('hdc_avg', 0.0),
            'away_shots': away_perf.get('shots_avg', 30.0), 'home_shots': home_perf.get('shots_avg', 30.0),
            'away_giveaways': away_perf.get('giveaways_avg', 0.0), 'home_giveaways': home_perf.get('giveaways_avg', 0.0),
            'away_sos': away_sos, 'home_sos': home_sos,
            'away_takeaways': away_perf.get('takeaways_avg', 0.0), 'home_takeaways': home_perf.get('takeaways_avg', 0.0),
            'away_xg': away_perf.get('xg_avg', 0.0), 'home_xg': home_perf.get('xg_avg', 0.0),
            'away_penalty_minutes': away_perf.get('penalty_minutes_avg', 0.0), 'home_penalty_minutes': home_perf.get('penalty_minutes_avg', 0.0),
            'away_faceoff_pct': away_perf.get('faceoff_avg', 50.0), 'home_faceoff_pct': home_perf.get('faceoff_avg', 50.0),
            'away_goalie_perf': away_goalie_perf, 'home_goalie_perf': home_goalie_perf,
            'goalie_matchup_quality': goalie_matchup_quality,  # Goalie matchup advantage
            'special_teams_matchup': special_teams_matchup,  # Special teams matchup advantage
            'recent_form_diff': away_recent_form - home_recent_form,  # Add recent form difference
            'away_venue_win_pct': away_venue_win_pct, 'home_venue_win_pct': home_venue_win_pct,  # Venue-specific win rates
            'context_bucket': context_bucket,
            'away_back_to_back': away_b2b,
            'home_back_to_back': home_b2b,
            # First-goal likelihood & impact (team/venue specific)
            'away_prob_score_first': away_fg['scored_first_rate'],
            'home_prob_score_first': home_fg['scored_first_rate'],
            'away_first_goal_win_uplift': away_fg['first_goal_uplift'],
            'home_first_goal_win_uplift': home_fg['first_goal_uplift'],
            # Lineup/team-strength scaffolding (currently neutral = 1.0)
            'away_lineup_strength': away_lineup_strength,
            'home_lineup_strength': home_lineup_strength,
        }
        corr = self.corr_model.predict_from_metrics(metrics)
        ens = self.learning_model.ensemble_predict(away_team, home_team, game_date=today_str)
        # Blend: correlation model + ensemble.
        # Fresh full-history backtest over all completed games shows the
        # best overall accuracy and Brier using the ensemble alone, so we
        # default to 0% correlation / 100% ensemble for live predictions.
        corr_weight = 0.0
        ens_weight = 1.0 - corr_weight
        if corr and all(k in corr for k in ('away_prob','home_prob')):
            away_blend_raw = corr_weight * corr['away_prob'] + ens_weight * ens.get('away_prob', 0.5)
            home_blend_raw = 1.0 - away_blend_raw
            away_calibrated = self.learning_model.apply_calibration(away_blend_raw, context_bucket)
            home_calibrated = 1.0 - away_calibrated
            corr_disagreement = abs(corr['away_prob'] - ens.get('away_prob', away_blend_raw))
            flip_rate = self.learning_model._estimate_monte_carlo_signal(
                {
                    "metrics_used": metrics,
                    "predicted_winner": "away" if away_blend_raw >= home_blend_raw else "home",
                    "raw_away_prob": away_blend_raw,
                    "raw_home_prob": home_blend_raw
                },
                iterations=40
            )
            upset_probability = self.learning_model.predict_upset_probability(
                [max(away_calibrated, home_calibrated), abs(away_blend_raw - home_blend_raw), corr_disagreement, flip_rate]
            )

            # Variance-aware adjustment: shrink extreme probabilities toward 0.5
            # when Monte Carlo flip_rate is high. This dampens fragile edges.
            shrink_strength = 0.7  # how strongly flip_rate impacts shrink
            shrink = max(0.0, min(1.0, 1.0 - shrink_strength * float(flip_rate)))
            away_adj = 0.5 + (away_calibrated - 0.5) * shrink
            home_adj = 1.0 - away_adj

            # Team bias corrections (per team, per venue)
            home_bias = self.learning_model.get_team_bias(home_team, venue="home")
            away_bias = self.learning_model.get_team_bias(away_team, venue="away")
            away_final = away_adj + away_bias
            home_final = home_adj + home_bias
            total_final = away_final + home_final
            if total_final > 0:
                away_final /= total_final
                home_final /= total_final
            else:
                away_final = home_final = 0.5

            metrics["corr_disagreement"] = corr_disagreement
            metrics["monte_carlo_flip_rate"] = flip_rate
            return {
                'away_prob': away_final,
                'home_prob': home_final,
                'prediction_confidence': max(away_final, home_final),
                'raw_away_prob': away_blend_raw,
                'raw_home_prob': home_blend_raw,
                'correlation_away_prob': corr['away_prob'],
                'correlation_home_prob': corr['home_prob'],
                'ensemble_away_prob': ens.get('away_prob', 0.5),
                'ensemble_home_prob': ens.get('home_prob', 0.5),
                'calibration_applied': True,
                'corr_disagreement': corr_disagreement,
                'monte_carlo_flip_rate': flip_rate,
                'upset_probability': upset_probability,
                'context_bucket': context_bucket,
                'away_back_to_back': away_b2b,
                'home_back_to_back': home_b2b,
                'away_rest': away_rest,
                'home_rest': home_rest,
                'goalie_matchup_quality': goalie_matchup_quality,
                'special_teams_matchup': special_teams_matchup,
                'away_goalie_perf': away_goalie_perf,
                'home_goalie_perf': home_goalie_perf
            }
        # Fallback to ensemble if correlation fails
        fallback_away = ens['away_prob']
        fallback_home = ens['home_prob']
        away_calibrated = self.learning_model.apply_calibration(fallback_away, context_bucket)
        home_calibrated = 1.0 - away_calibrated
        corr_disagreement = 0.0
        flip_rate = self.learning_model._estimate_monte_carlo_signal(
            {
                "metrics_used": metrics,
                "predicted_winner": "away" if fallback_away >= fallback_home else "home",
                "raw_away_prob": fallback_away,
                "raw_home_prob": fallback_home
            },
            iterations=40
        )
        upset_probability = self.learning_model.predict_upset_probability(
            [max(away_calibrated, home_calibrated), abs(fallback_away - fallback_home), corr_disagreement, flip_rate]
        )

        # Variance-aware adjustment for fallback as well
        shrink_strength = 0.7
        shrink = max(0.0, min(1.0, 1.0 - shrink_strength * float(flip_rate)))
        away_adj = 0.5 + (away_calibrated - 0.5) * shrink
        home_adj = 1.0 - away_adj

        # Apply team bias corrections
        home_bias = self.learning_model.get_team_bias(home_team, venue="home")
        away_bias = self.learning_model.get_team_bias(away_team, venue="away")
        away_final = away_adj + away_bias
        home_final = home_adj + home_bias
        total_final = away_final + home_final
        if total_final > 0:
            away_final /= total_final
            home_final /= total_final
        else:
            away_final = home_final = 0.5
        metrics["corr_disagreement"] = corr_disagreement
        metrics["monte_carlo_flip_rate"] = flip_rate
        return {
            'away_prob': away_final,
            'home_prob': home_final,
            'prediction_confidence': max(away_final, home_final),
            'raw_away_prob': fallback_away,
            'raw_home_prob': fallback_home,
            'correlation_away_prob': None,
            'correlation_home_prob': None,
            'ensemble_away_prob': fallback_away,
            'ensemble_home_prob': fallback_home,
            'calibration_applied': True,
            'corr_disagreement': corr_disagreement,
            'monte_carlo_flip_rate': flip_rate,
            'upset_probability': upset_probability,
            'context_bucket': context_bucket,
            'away_back_to_back': away_b2b,
            'home_back_to_back': home_b2b,
            'away_rest': away_rest,
            'home_rest': home_rest,
            'goalie_matchup_quality': goalie_matchup_quality,
            'special_teams_matchup': special_teams_matchup,
            'away_goalie_perf': away_goalie_perf,
            'home_goalie_perf': home_goalie_perf
        }
    
    def get_team_performance_data(self):
        """Get current team performance data (this would be updated regularly)"""
        # This is where you'd get the most recent team performance data
        # For now, using static data - in production this would be updated from recent games
        return {
            'TOR': {'xg_avg': 3.2, 'hdc_avg': 2, 'shots_avg': 32, 'gs_avg': 15.2},
            'SEA': {'xg_avg': 2.8, 'hdc_avg': 1.5, 'shots_avg': 28, 'gs_avg': 12.8},
            'NYR': {'xg_avg': 3.1, 'hdc_avg': 2.2, 'shots_avg': 30, 'gs_avg': 14.9},
            'MTL': {'xg_avg': 2.9, 'hdc_avg': 1.8, 'shots_avg': 29, 'gs_avg': 13.7},
            'MIN': {'xg_avg': 2.7, 'hdc_avg': 1.6, 'shots_avg': 27, 'gs_avg': 13.1},
            'PHI': {'xg_avg': 2.6, 'hdc_avg': 1.4, 'shots_avg': 26, 'gs_avg': 12.4},
            'TBL': {'xg_avg': 3.0, 'hdc_avg': 2.0, 'shots_avg': 31, 'gs_avg': 15.8},
            'CBJ': {'xg_avg': 2.4, 'hdc_avg': 1.2, 'shots_avg': 24, 'gs_avg': 11.2},
            'DAL': {'xg_avg': 3.3, 'hdc_avg': 2.3, 'shots_avg': 33, 'gs_avg': 16.1},
            'STL': {'xg_avg': 2.8, 'hdc_avg': 1.7, 'shots_avg': 28, 'gs_avg': 13.4},
            'NSH': {'xg_avg': 2.9, 'hdc_avg': 1.9, 'shots_avg': 29, 'gs_avg': 13.9},
            'WPG': {'xg_avg': 3.1, 'hdc_avg': 2.1, 'shots_avg': 31, 'gs_avg': 15.0},
            'BOS': {'xg_avg': 2.5, 'hdc_avg': 1.3, 'shots_avg': 25, 'gs_avg': 12.1},
            'COL': {'xg_avg': 3.4, 'hdc_avg': 2.4, 'shots_avg': 34, 'gs_avg': 16.5},
            'CAR': {'xg_avg': 3.2, 'hdc_avg': 2.2, 'shots_avg': 32, 'gs_avg': 15.3},
            'LAK': {'xg_avg': 2.7, 'hdc_avg': 1.6, 'shots_avg': 27, 'gs_avg': 13.0},
            'CGY': {'xg_avg': 2.8, 'hdc_avg': 1.7, 'shots_avg': 28, 'gs_avg': 13.5},
            'VGK': {'xg_avg': 3.0, 'hdc_avg': 2.0, 'shots_avg': 30, 'gs_avg': 14.7},
            'PIT': {'xg_avg': 2.9, 'hdc_avg': 1.8, 'shots_avg': 29, 'gs_avg': 13.8},
            'SJS': {'xg_avg': 2.2, 'hdc_avg': 1.0, 'shots_avg': 22, 'gs_avg': 10.5}
        }
    
    def send_discord_notification(self, predictions):
        """Send Discord notification with today's predictions"""
        # Discord webhook URL must come from environment/secret
        webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        
        if not webhook_url:
            print("❌ Discord webhook URL not configured")
            return False
        
        # Format predictions for Discord
        prediction_text = "🏒 **DAILY NHL PREDICTIONS** 🏒\n\n"
        
        for i, pred in enumerate(predictions, 1):
            away_team = pred['away_team']
            home_team = pred['home_team']
            away_prob = pred['predicted_away_win_prob'] * 100
            home_prob = pred['predicted_home_win_prob'] * 100
            favorite = pred['favorite']
            
            # Calculate confidence (max probability)
            confidence = max(away_prob, home_prob)
            
            # Get volatility (Monte Carlo flip-rate)
            flip_rate = pred.get('monte_carlo_flip_rate', 0.0)
            try:
                flip_val = float(flip_rate) if flip_rate is not None else 0.0
            except (TypeError, ValueError):
                flip_val = 0.0
            
            # Volatility label
            if flip_val < 0.20:
                volatility_label = "LOW"
            elif flip_val < 0.40:
                volatility_label = "MED"
            else:
                volatility_label = "HIGH"
            
            # Get upset probability
            upset_prob = pred.get('upset_probability', 0.0)
            try:
                upset_val = float(upset_prob) if upset_prob is not None else 0.0
            except (TypeError, ValueError):
                upset_val = 0.0
            
            # Calculate likeliest score using team performance data
            # Use both offensive capability (goals scored) and defensive capability (goals allowed)
            try:
                home_perf = self.learning_model.get_team_performance(home_team, venue="home")
                away_perf = self.learning_model.get_team_performance(away_team, venue="away")
                
                # Get goals scored averages
                home_gf = float(home_perf.get("goals_avg", 3.0)) if home_perf else 3.0
                away_gf = float(away_perf.get("goals_avg", 3.0)) if away_perf else 3.0
                
                # Calculate goals_against from team_stats
                # Derive from historical game results if goals_against array isn't populated
                def get_goals_against_avg(team_key, venue, team_goals_avg=3.0):
                    """Get goals allowed average, deriving from historical games if needed"""
                    if team_key not in self.learning_model.team_stats:
                        # Use inverse relationship: teams that score more tend to allow more
                        return max(2.5, min(3.5, team_goals_avg * 0.95))
                    
                    venue_data = self.learning_model.team_stats[team_key].get(venue, {})
                    
                    # First try: use goals_against array if populated
                    ga_list = venue_data.get('goals_against', [])
                    if ga_list and len(ga_list) > 0:
                        valid_values = [float(x) for x in ga_list if x is not None and not (isinstance(x, float) and np.isnan(x))]
                        if valid_values:
                            return float(np.mean(valid_values))
                    
                    # Second try: derive from opponent goals in historical games
                    opp_goals_list = venue_data.get('opp_goals', [])
                    if opp_goals_list and len(opp_goals_list) > 0:
                        valid_values = [float(x) for x in opp_goals_list if x is not None and not (isinstance(x, float) and np.isnan(x))]
                        if valid_values:
                            return float(np.mean(valid_values))
                    
                    # Third try: derive from historical predictions file
                    try:
                        predictions_file = os.path.join(os.path.dirname(__file__), 'win_probability_predictions_v2.json')
                        if os.path.exists(predictions_file):
                            with open(predictions_file, 'r') as f:
                                all_predictions = json.load(f)
                            
                            # Find games where this team played at this venue
                            ga_values = []
                            for pred in all_predictions:
                                if venue == "home" and pred.get('home_team') == team_key:
                                    away_score = pred.get('metrics_used', {}).get('away_score')
                                    if away_score is not None:
                                        ga_values.append(float(away_score))
                                elif venue == "away" and pred.get('away_team') == team_key:
                                    home_score = pred.get('metrics_used', {}).get('home_score')
                                    if home_score is not None:
                                        ga_values.append(float(home_score))
                            
                            if ga_values and len(ga_values) >= 3:  # Need at least 3 games
                                return float(np.mean(ga_values))
                    except Exception:
                        pass
                    
                    # Fourth try: use team-specific estimate based on goals scored
                    # Teams that score more tend to play more open games (allow more)
                    # But cap it between 2.5 and 3.5 for realism
                    estimated_ga = team_goals_avg * 0.95  # Slight inverse correlation
                    return max(2.5, min(3.5, estimated_ga))
                
                home_team_key = home_team.upper()
                away_team_key = away_team.upper()
                
                # Get goals allowed averages (pass goals_avg for better fallback)
                home_ga = get_goals_against_avg(home_team_key, "home", home_gf)
                away_ga = get_goals_against_avg(away_team_key, "away", away_gf)
                
                # Predicted score = weighted average:
                # 60% team's offensive capability, 40% opponent's defensive weakness
                # This gives more weight to what the team actually scores
                home_g = (home_gf * 0.6) + (away_ga * 0.4)
                away_g = (away_gf * 0.6) + (home_ga * 0.4)
                    
            except Exception as e:
                # Fallback: use just goals scored if calculation fails
                try:
                    home_perf = self.learning_model.get_team_performance(home_team, venue="home")
                    away_perf = self.learning_model.get_team_performance(away_team, venue="away")
                    home_g = float(home_perf.get("goals_avg", 3.0)) if home_perf else 3.0
                    away_g = float(away_perf.get("goals_avg", 3.0)) if away_perf else 3.0
                except Exception:
                    home_g = away_g = 3.0
            
            # More nuanced rounding: round to nearest integer, but preserve differences
            # Use floor/ceiling logic to avoid always getting same scores
            def smart_round(val):
                """Round with preference for common hockey scores (2-5 range)"""
                if val < 1.5:
                    return 1
                elif val < 2.5:
                    return 2
                elif val < 3.5:
                    return 3
                elif val < 4.5:
                    return 4
                elif val < 5.5:
                    return 5
                else:
                    return int(round(val))
            
            home_goals = smart_round(home_g)
            away_goals = smart_round(away_g)
            
            # Ensure favorite wins (if prediction says they should)
            fav_prob = home_prob if favorite == home_team else away_prob
            if fav_prob > 50.0:  # Only if favorite has >50% chance
                if home_goals == away_goals:
                    # Nudge favorite to win by one
                    if favorite == home_team:
                        home_goals = away_goals + 1
                    else:
                        away_goals = home_goals + 1
                elif favorite == home_team and home_goals < away_goals:
                    # Favorite should win, swap if needed
                    home_goals, away_goals = away_goals, home_goals
                elif favorite != home_team and away_goals < home_goals:
                    # Favorite should win, swap if needed
                    home_goals, away_goals = away_goals, home_goals
            
            # Determine if OT/SO is likely based on closeness
            fav_prob = home_prob if favorite == home_team else away_prob
            if abs(home_goals - away_goals) == 1 and 50.0 <= fav_prob <= 58.0:
                ot_so_str = "(OT/SO likely)"
            else:
                ot_so_str = "(regulation)"
            
            # Format score with favorite first
            if favorite == home_team:
                likely_score = f"{home_team} {home_goals}–{away_goals} {away_team} {ot_so_str}"
            else:
                likely_score = f"{away_team} {away_goals}–{home_goals} {home_team} {ot_so_str}"
            
            # Retrieve enhanced metrics if available (calculated in get_daily_predictions)
            upset_str = pred.get('upset_risk', 'Low')
            upset_p = pred.get('upset_prob', 0.0)
            reasoning = pred.get('reasoning', '')
            
            prediction_text += f"{away_team} @ {home_team}\n\n"
            prediction_text += f"🎯 {away_team} {away_prob:.1f}% | {home_team} {home_prob:.1f}%\n"
            prediction_text += f"⭐ Favorite: {favorite} (confidence {confidence:.1f}%)\n"
            prediction_text += f"🌪️ Volatility: {volatility_label}\n"
            prediction_text += f"⚡ Upset Risk: {upset_str} ({upset_p:.1f}%)\n"
            prediction_text += f"📐 Likeliest score: {likely_score}\n"
            if reasoning:
                prediction_text += f"📝 Analysis: {reasoning}\n"
            prediction_text += "\n"
        
        # Ensure model performance is up-to-date (recalculate from scratch for accuracy)
        try:
            self.learning_model.recalculate_performance_from_scratch()
        except Exception:
            pass
        
        # Get current model performance
        perf = self.learning_model.get_model_performance()
        if not perf or perf.get('total_games', 0) == 0:
            perf = self._compute_model_performance_fallback()
        
        # Get actual model performance from the learning model
        actual_total_games = perf.get('total_games', 0)
        actual_accuracy = perf.get('accuracy', 0.0)
        recent_accuracy = perf.get('recent_accuracy', actual_accuracy)
        
        prediction_text += f"📊 **Model Performance:**\n"
        prediction_text += f"• Total Games: {actual_total_games}\n"
        prediction_text += f"• Accuracy: {actual_accuracy:.1%}\n"
        prediction_text += f"• Recent Accuracy: {recent_accuracy:.1%}\n\n"
        prediction_text += f"🤖 *Powered by Self-Learning AI Model*"
        
        # Discord webhook payload
        payload = {
            "content": prediction_text,
            "username": "NHL Predictions Bot",
            "embeds": [
                {
                    "title": "🏒 Daily NHL Predictions",
                    "description": f"Predictions for {len(predictions)} games today",
                    "color": 3447003,  # Blue color
                    "fields": [
                        {
                            "name": "📅 Date",
                            "value": datetime.now().strftime('%Y-%m-%d'),
                            "inline": True
                        },
                        {
                            "name": "🎮 Games",
                            "value": str(len(predictions)),
                            "inline": True
                        },
                        {
                            "name": "📊 Model Accuracy",
                            "value": f"{actual_accuracy:.1%}",
                            "inline": True
                        }
                    ],
                    "footer": {
                        "text": "Self-Learning AI Model • Updated Daily"
                    }
                }
            ]
        }
        
        try:
            print("📤 Sending Discord notification...")
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 204:
                print("✅ Discord notification sent successfully!")
                return True
            else:
                print(f"❌ Discord notification failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Discord notification: {e}")
            return False
    
    def show_model_performance(self):
        """Show current model performance"""
        # Recalculate to ensure fresh data
        try:
            self.learning_model.recalculate_performance_from_scratch()
        except Exception:
            pass
        
        perf = self.learning_model.get_model_performance()
        if not perf or perf.get('total_games', 0) == 0:
            perf = self._compute_model_performance_fallback()
        print(f"\n📊 MODEL PERFORMANCE:")
        print(f"  Total Games: {perf['total_games']}")
        print(f"  Accuracy: {perf['accuracy']:.3f}")
        print(f"  Recent Accuracy: {perf['recent_accuracy']:.3f}")
        
        # Show model analysis
        analysis = self.learning_model.analyze_model_performance()
        if analysis.get('team_accuracy'):
            print(f"\n📈 TOP TEAM ACCURACY:")
            sorted_teams = sorted(analysis['team_accuracy'].items(), key=lambda x: x[1], reverse=True)
            for team, acc in sorted_teams[:5]:
                print(f"  {team}: {acc:.3f}")


def main():
    """Main function to run predictions"""
    predictor = PredictionInterface()
    
    # Get today's predictions
    predictions = predictor.get_todays_predictions()
    
    # Show model performance
    predictor.show_model_performance()
    
    # Send Discord notification if there are predictions
    if predictions:
        print(f"\n📤 Sending Discord notification...")
        success = predictor.send_discord_notification(predictions)
        if success:
            print("✅ Discord notification sent successfully!")
        else:
            print("❌ Discord notification failed")
    else:
        print("\nℹ️  No games today - skipping Discord notification")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  Total games predicted: {len(predictions)}")
    print(f"  Model uses self-learning weights")
    print(f"  Separate from post-game win probability analysis")


if __name__ == "__main__":
    main()
