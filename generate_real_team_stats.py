#!/usr/bin/env python3
"""
Generate real team stats JSON from actual NHL game data
Uses the same calculation logic as team_report_generator.py
"""

import json
import requests
from pathlib import Path
from nhl_api_client import NHLAPIClient
from advanced_metrics_analyzer import AdvancedMetricsAnalyzer
from experimental_metrics_analyzer import ExperimentalMetricsAnalyzer
from sprite_goal_analyzer import SpriteGoalAnalyzer
from goalie_stats_builder import GoalieStatsBuilder
from team_advanced_metrics_builder import TeamAdvancedMetricsBuilder
from collections import defaultdict
from datetime import datetime
import numpy as np
import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from team_report_generator import TeamReportGenerator

class RealTeamStatsGenerator(TeamReportGenerator):
    """Generate real team stats using TeamReportGenerator's calculation methods"""
    
    def __init__(self):
        super().__init__()
        # Use absolute path for robustness
        script_dir = Path(__file__).parent.absolute()
        self.output_file = script_dir / "data" / "season_2025_2026_team_stats.json"

    
    def calculate_game_metrics(self, game_data, team_id, is_home):
        """Calculate all metrics for a single game"""
        venue_key = 'home' if is_home else 'away'
        
        boxscore = game_data.get('boxscore', {})
        if not boxscore:
            return None
        
        home_team_data = boxscore.get('homeTeam', {})
        away_team_data = boxscore.get('awayTeam', {})
        
        if is_home:
            team_data = home_team_data
            opponent_data = away_team_data
        else:
            team_data = away_team_data
            opponent_data = home_team_data
        
        # Basic stats
        goals_for = team_data.get('score', 0)
        goals_against = opponent_data.get('score', 0)
        shots_for = team_data.get('sog', 0)
        shots_against = opponent_data.get('sog', 0)
        
        # Calculate period stats using parent class methods
        period_stats = self._calculate_real_period_stats(game_data, team_id, venue_key)
        period_gs_xg = self._calculate_period_metrics(game_data, team_id, venue_key)
        zone_metrics = self._calculate_zone_metrics(game_data, team_id, venue_key)
        
        if not period_stats:
            return None
        
        # Aggregate period stats
        total_shots = sum(period_stats['shots'])
        avg_corsi = np.mean(period_stats['corsi_pct']) if period_stats['corsi_pct'] else 50.0
        total_pim = sum(period_stats['pim'])
        total_hits = sum(period_stats['hits'])
        avg_fo_pct = np.mean(period_stats['fo_pct']) if period_stats['fo_pct'] else 50.0
        total_blocks = sum(period_stats['bs'])
        total_giveaways = sum(period_stats['gv'])
        total_takeaways = sum(period_stats['tk'])
        
        # Power play
        total_pp_goals = sum(period_stats['pp_goals'])
        total_pp_attempts = sum(period_stats['pp_attempts'])
        pp_pct = (total_pp_goals / total_pp_attempts * 100) if total_pp_attempts > 0 else 0.0
        
        # Penalty kill (simplified - would need opponent PP data)
        pk_pct = 100.0 - pp_pct if pp_pct > 0 else 80.0
        
        # Game Score
        if period_gs_xg:
            gs_periods, xg_periods = period_gs_xg
            total_gs = sum(gs_periods)
            total_xg = sum(xg_periods)
        else:
            total_gs = 0.0
            total_xg = 0.0
        
        # Zone metrics
        total_nzt = sum(zone_metrics.get('nz_turnovers', [0]))
        total_nztsa = sum(zone_metrics.get('nz_turnovers_to_shots', [0]))
        total_ozs = sum(zone_metrics.get('oz_originating_shots', [0]))
        total_nzs = sum(zone_metrics.get('nz_originating_shots', [0]))
        total_dzs = sum(zone_metrics.get('dz_originating_shots', [0]))
        total_fc = sum(zone_metrics.get('fc_cycle_sog', [0]))
        total_rush = sum(zone_metrics.get('rush_sog', [0]))
        
        # Advanced metrics
        away_xg, home_xg = self._calculate_xg_from_plays(game_data)
        away_hdc, home_hdc = self._calculate_hdc_from_plays(game_data)
        
        # Extract team values based on venue
        if is_home:
            team_xg = home_xg
            opp_xg = away_xg
            team_hdc = home_hdc
            opp_hdc = away_hdc
        else:
            team_xg = away_xg
            opp_xg = home_xg
            team_hdc = away_hdc
            opp_hdc = home_hdc
        
        # Corsi and Fenwick
        corsi_for = sum(period_stats['shots'])  # Simplified
        fenwick_pct = avg_corsi  # Simplified
        
        # PDO (simplified)
        sv_pct = (1 - (goals_against / shots_against)) * 100 if shots_against > 0 else 92.0
        sh_pct = (goals_for / shots_for * 100) if shots_for > 0 else 10.0
        pdo = sv_pct + sh_pct
        
        
        # Get pre-shot movement from advanced metrics analyzer
        lat = "No data"
        long_movement = "No data"
        
        try:
            from advanced_metrics_analyzer import AdvancedMetricsAnalyzer
            analyzer = AdvancedMetricsAnalyzer(game_data.get('play_by_play', {}))
            metrics_report = analyzer.generate_comprehensive_report(away_team_data.get('id'), home_team_data.get('id'))
            
            if is_home:
                pre_shot_data = metrics_report.get('home_team', {}).get('pre_shot_movement', {})
            else:
                pre_shot_data = metrics_report.get('away_team', {}).get('pre_shot_movement', {})
            
            # Extract numeric values
            lat_feet = pre_shot_data.get('lateral_movement', {}).get('avg_delta_y', 0.0)
            long_feet = pre_shot_data.get('longitudinal_movement', {}).get('avg_delta_x', 0.0)
            
            # Convert to text descriptions (same as PDF reports)
            lat = self._classify_lateral_movement(lat_feet)
            long_movement = self._classify_longitudinal_movement(long_feet)
        except Exception as e:
            print(f"    Warning: Could not calculate movement metrics: {e}")
        
        # High-signal experimental metrics
        rebounds = 0
        rush_shots = 0
        cycle_shots = 0
        forecheck_turnovers = 0
        passes_per_goal = 0.0
        avg_goal_distance = 0.0
        east_west_play = 0.0
        north_south_play = 0.0
        
        # Sprite/Dynamic metrics
        net_front_traffic_pct = 0.0
        carry_pct = 0.0
        pass_pct = 0.0
        
        try:
            if 'play_by_play' in game_data:
                pbp = game_data['play_by_play']
                # Pass game_id (as string) to ensure sprite lookups work
                game_id = game_data.get('game_center', {}).get('id')
                if not game_id:
                     # Fallback to checking boxscore or other fields if needed
                     game_id = game_data.get('boxscore', {}).get('id')
                
                game_id_str = str(game_id) if game_id else ''
                exp_analyzer = ExperimentalMetricsAnalyzer(pbp, game_id=game_id_str)
                exp_results = exp_analyzer.calculate_all_experimental_metrics()
                
                # Fetch team-specific metrics
                team_metrics = exp_results.get(team_id, {})
                rebounds = team_metrics.get('rebound_count', 0)
                rush_shots = team_metrics.get('rush_shots', 0)
                cycle_shots = team_metrics.get('cycle_shots', 0)
                forecheck_turnovers = team_metrics.get('forecheck_turnovers', 0)
                passes_per_goal = team_metrics.get('passes_per_goal', 0.0)
                
                # Sprite Goal analysis
                sprite_analyzer = SpriteGoalAnalyzer(game_data)
                sprite_results = sprite_analyzer.analyze_goals()
                
                # Extract venue-specific sprite stats
                venue_sprite = sprite_results.get('away' if venue_key == 'away' else 'home', {})
                net_front_traffic_pct = venue_sprite.get('net_front_traffic_pct', 0.0)
                avg_goal_distance = venue_sprite.get('avg_goal_distance', 0.0)
                
                entry_share = venue_sprite.get('entry_type_share', {})
                carry_pct = entry_share.get('carry', 0.0)
                pass_pct = entry_share.get('pass', 0.0)
                
                # Movement re-mapping
                movement = venue_sprite.get('movement_metrics', {})
                east_west_play = movement.get('east_west', 0.0)
                north_south_play = movement.get('north_south', 0.0)
        except Exception as e:
            print(f"    Error calculating high-signal metrics: {e}")
            
        return {
            'gs': round(total_gs, 2),
            'xg': round(total_xg, 2),
            'corsi_pct': round(avg_corsi, 2),
            'fenwick_pct': round(fenwick_pct, 2),
            'pdo': round(pdo, 2),
            'ozs': round(total_ozs, 2),
            'nzs': round(total_nzs, 2),
            'dzs': round(total_dzs, 2),
            'goals': goals_for,
            'opp_goals': goals_against,  # ← NEW: Opponent goals (goals allowed)
            'shots': shots_for,
            'hits': total_hits,
            'blocked_shots': total_blocks,
            'giveaways': total_giveaways,
            'takeaways': total_takeaways,
            'penalty_minutes': total_pim,
            'power_play_pct': round(pp_pct, 2),
            'penalty_kill_pct': round(pk_pct, 2),
            'faceoff_pct': round(avg_fo_pct, 2),
            'nzt': round(total_nzt, 2),
            'nztsa': round(total_nztsa, 2),
            'fc': round(total_fc, 2),
            'rush': round(total_rush, 2),
            'lat': lat,  # Text description
            'long_movement': long_movement,  # Text description
            'hdc': team_hdc,
            'hdca': opp_hdc,
            'opp_xg': round(opp_xg, 2),  # ← NEW: Opponent xG (xG allowed)
            'period_dzs': round(total_dzs, 2),
            # New Advanced Metrics
            'rebounds': rebounds,
            'rush_shots': rush_shots,
            'cycle_shots': cycle_shots,
            'forecheck_turnovers': forecheck_turnovers,
            'net_front_traffic_pct': round(net_front_traffic_pct, 2),
            'passes_per_goal': round(passes_per_goal, 2),
            'avg_goal_distance': round(avg_goal_distance, 2),
            'east_west_play': round(east_west_play, 2),
            'north_south_play': round(north_south_play, 2),
            'zone_entry_carry_pct': round(carry_pct, 2),
            'zone_entry_pass_pct': round(pass_pct, 2)
        }
    
    def generate_all_team_stats(self):
        """Generate stats for all teams incrementally"""
        print("Fetching standings to get all teams...")
        try:
            # Use the API client's session to ensure proper headers (User-Agent) are sent
            response = self.api.session.get("https://api-web.nhle.com/v1/standings/now")
            if response.status_code != 200:
                print(f"Error fetching standings: Status {response.status_code}")
                return
            data = response.json()
            standings = data.get('standings', [])
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return
        
        # Load existing data to enable incremental updates
        existing_data = {}
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r') as f:
                    file_content = json.load(f)
                    existing_data = file_content.get('teams', {})
                print(f"✅ Loaded existing stats for {len(existing_data)} teams")
            except Exception as e:
                print(f"⚠️ Could not load existing stats: {e}. Starting fresh.")
                
        teams_data = existing_data
        
        for team in standings:
            abbrev = team['teamAbbrev']['default']
            name = team['teamName']['default']
            
            print(f"\n{'='*60}")
            print(f"Processing {name} ({abbrev})...")
            print(f"{'='*60}")
            
            # Get all games for this team using parent class method
            team_games = self.get_team_games(abbrev)
            print(f"Found {len(team_games)} total games in history")
            
            if not team_games:
                print(f"  No games found for {abbrev}, skipping...")
                continue
            
            # Separate home and away games
            home_games = [g for g in team_games if g['was_home']]
            away_games = [g for g in team_games if not g['was_home']]
            
            # Initialize team stats structure if not present
            if abbrev not in teams_data:
                teams_data[abbrev] = {
                    'home': {
                        'gs': [], 'xg': [], 'corsi_pct': [], 'fenwick_pct': [], 'pdo': [],
                        'ozs': [], 'nzs': [], 'dzs': [], 'goals': [], 'opp_goals': [], 'shots': [],
                        'hits': [], 'blocked_shots': [], 'giveaways': [], 'takeaways': [],
                        'penalty_minutes': [], 'power_play_pct': [], 'penalty_kill_pct': [],
                        'faceoff_pct': [], 'nzt': [], 'nztsa': [], 'fc': [], 'rush': [],
                        'lat': [], 'long_movement': [], 'hdc': [], 'hdca': [], 'opp_xg': [], 'period_dzs': [],
                        'rebounds': [], 'rush_shots': [], 'cycle_shots': [], 'forecheck_turnovers': [],
                        'net_front_traffic_pct': [], 'passes_per_goal': [], 'avg_goal_distance': [],
                        'east_west_play': [], 'north_south_play': [],
                        'zone_entry_carry_pct': [], 'zone_entry_pass_pct': [],
                        'games': []
                    },
                    'away': {
                        'gs': [], 'xg': [], 'corsi_pct': [], 'fenwick_pct': [], 'pdo': [],
                        'ozs': [], 'nzs': [], 'dzs': [], 'goals': [], 'opp_goals': [], 'shots': [],
                        'hits': [], 'blocked_shots': [], 'giveaways': [], 'takeaways': [],
                        'penalty_minutes': [], 'power_play_pct': [], 'penalty_kill_pct': [],
                        'faceoff_pct': [], 'nzt': [], 'nztsa': [], 'fc': [], 'rush': [],
                        'lat': [], 'long_movement': [], 'hdc': [], 'hdca': [], 'opp_xg': [], 'period_dzs': [],
                        'rebounds': [], 'rush_shots': [], 'cycle_shots': [], 'forecheck_turnovers': [],
                        'net_front_traffic_pct': [], 'passes_per_goal': [], 'avg_goal_distance': [],
                        'east_west_play': [], 'north_south_play': [],
                        'zone_entry_carry_pct': [], 'zone_entry_pass_pct': [],
                        'games': []
                    }
                }
            
            # INCREMENTAL UPDATE LOGIC
            # Check how many games we have already processed
            processed_home = len(teams_data[abbrev]['home'].get('gs', []))
            processed_away = len(teams_data[abbrev]['away'].get('gs', []))
            
            # Identify new games (by skipping the first N games)
            # Assumption: team_games is sorted by date (guaranteed by get_team_games)
            new_home_games = home_games[processed_home:]
            new_away_games = away_games[processed_away:]
            
            print(f"  Home games: {processed_home} processed, {len(new_home_games)} new")
            print(f"  Away games: {processed_away} processed, {len(new_away_games)} new")
            
            # Process new home games
            home_stats = teams_data[abbrev]['home']
            for i, game_info in enumerate(new_home_games):
                # Calculate true index (for logging)
                idx = processed_home + i
                game_id = game_info.get('game_id')
                if not game_id:
                    continue
                
                print(f"  Processing NEW home game {i+1}/{len(new_home_games)}: {game_info.get('date')} (ID: {game_id})...", end=' ', flush=True)
                
                try:
                    import signal
                    
                    # Set 30-second timeout for API call
                    def timeout_handler(signum, frame):
                        raise TimeoutError("API call timed out")
                    
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(30)  # 30 second timeout
                    
                    try:
                        game_data = self.api.get_comprehensive_game_data(str(game_id))
                    finally:
                        signal.alarm(0)  # Cancel alarm
                    
                    if not game_data:
                        print("No data - skipping")
                        continue
                    
                    boxscore = game_data.get('boxscore', {})
                    home_team_data = boxscore.get('homeTeam', {})
                    team_id = home_team_data.get('id')
                    
                    metrics = self.calculate_game_metrics(game_data, team_id, is_home=True)
                    if metrics:
                        # Append metrics to existing lists
                        for key in home_stats.keys():
                            if key != 'games' and key in metrics:
                                home_stats[key].append(metrics.get(key, 0))
                        
                        # Use game_id instead of index for robustness
                        home_stats['games'].append(game_id)
                        print(f"✓ GS={metrics['gs']:.1f}, xG={metrics['xg']:.2f}")
                    else:
                        print("Failed to calculate metrics - skipping")
                except TimeoutError as e:
                    print(f"Timeout - skipping: {e}")
                except KeyboardInterrupt:
                    raise  # Allow user to stop
                except Exception as e:
                    print(f"Error (skipping): {e}")
            
            # Process new away games
            away_stats = teams_data[abbrev]['away']
            for i, game_info in enumerate(new_away_games):
                idx = processed_away + i
                game_id = game_info.get('game_id')
                
                print(f"  Processing NEW away game {i+1}/{len(new_away_games)}: {game_info.get('date')} (ID: {game_id})...", end=' ', flush=True)
                
                try:
                    import signal
                    
                    def timeout_handler(signum, frame):
                        raise TimeoutError("API call timed out")
                    
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(30)
                    
                    try:
                        game_data = self.api.get_comprehensive_game_data(str(game_id))
                    finally:
                        signal.alarm(0)
                    
                    if not game_data:
                        print("No data - skipping")
                        continue
                    
                    boxscore = game_data.get('boxscore', {})
                    away_team_data = boxscore.get('awayTeam', {})
                    team_id = away_team_data.get('id')
                    
                    metrics = self.calculate_game_metrics(game_data, team_id, is_home=False)
                    if metrics:
                        for key in away_stats.keys():
                            if key != 'games' and key in metrics:
                                away_stats[key].append(metrics.get(key, 0))
                        
                        away_stats['games'].append(game_id)
                        print(f"✓ GS={metrics['gs']:.1f}, xG={metrics['xg']:.2f}")
                    else:
                        print("Failed to calculate metrics - skipping")
                except TimeoutError as e:
                    print(f"Timeout - skipping: {e}")
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"Error (skipping): {e}")
            
            # Incremental Save
            try:
                output_dir = os.path.dirname(self.output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                output = {"teams": teams_data}
                with open(self.output_file, 'w') as f:
                    json.dump(output, f, indent=2)
                if len(new_home_games) > 0 or len(new_away_games) > 0:
                    print(f"  (Saved updates to {self.output_file})")
            except Exception as e:
                print(f"  Warning: Failed to save progress: {e}")
        
        # Final Save
        output = {"teams": teams_data}
        with open(self.output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✓ Stats generation complete. {self.output_file}")
        
        # Also refresh advanced goalie and team metrics
        print(f"\n{'='*60}")
        print("🔄 Refreshing advanced goalie and team metrics...")
        try:
            # Refresh Goalie Stats
            gb = GoalieStatsBuilder()
            # Reuse the already processed games if possible, but for simplicity, 
            # we can just run the builder's logic.
            # GoalieStatsBuilder.save() handles the final calculations.
            # We don't need to re-process everything if github_actions_runner does it per-game,
            # but for a full regeneration, we should ensure the summary is up to date.
            gb.save() 
            
            # Refresh Team Advanced Metrics
            tb = TeamAdvancedMetricsBuilder()
            tb.save()
            print("✅ Advanced metrics summaries refreshed successfully")
        except Exception as e:
            print(f"⚠️ Failed to refresh advanced metrics: {e}")
            
        print(f"{'='*60}")

if __name__ == "__main__":
    generator = RealTeamStatsGenerator()
    generator.generate_all_team_stats()
