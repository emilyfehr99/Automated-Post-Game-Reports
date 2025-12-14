#!/usr/bin/env python3
"""
Generate real team stats JSON from actual NHL game data
Uses the same calculation logic as team_report_generator.py
"""

import json
import requests
from nhl_api_client import NHLAPIClient
from advanced_metrics_analyzer import AdvancedMetricsAnalyzer
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
        
        # Movement metrics (using AdvancedMetricsAnalyzer)
        lat = 0.0
        long_movement = 0.0
        
        try:
            # We need valid PBP data for this
            if 'play_by_play' in game_data:
                analyzer = AdvancedMetricsAnalyzer(game_data.get('play_by_play', {}))
                movement_metrics = analyzer.calculate_pre_shot_movement_metrics(team_id)
                lat = movement_metrics['lateral_movement'].get('avg_delta_y', 0.0)
                long_movement = movement_metrics['longitudinal_movement'].get('avg_delta_x', 0.0)
                print(f"    Calculated movement: LAT={lat:.2f}, LONG={long_movement:.2f}")
        except Exception as e:
            print(f"    Error calculating movement metrics: {e}")
        
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
            'lat': round(lat, 2),
            'long_movement': round(long_movement, 2),
            'hdc': team_hdc,
            'hdca': opp_hdc,
            'opp_xg': round(opp_xg, 2),  # ← NEW: Opponent xG (xG allowed)
            'period_dzs': round(total_dzs, 2)
        }
    
    def generate_all_team_stats(self):
        """Generate stats for all teams"""
        print("Fetching standings to get all teams...")
        try:
            response = requests.get("https://api-web.nhle.com/v1/standings/now")
            data = response.json()
            standings = data.get('standings', [])
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return
        
        teams_data = {}
        
        for team in standings:
            abbrev = team['teamAbbrev']['default']
            name = team['teamName']['default']
            
            print(f"\n{'='*60}")
            print(f"Processing {name} ({abbrev})...")
            print(f"{'='*60}")
            
            # Get all games for this team using parent class method
            team_games = self.get_team_games(abbrev)
            print(f"Found {len(team_games)} games")
            
            if not team_games:
                print(f"  No games found for {abbrev}, skipping...")
                continue
            
            # Separate home and away games
            home_games = [g for g in team_games if g['was_home']]
            away_games = [g for g in team_games if not g['was_home']]
            
            print(f"  Home games: {len(home_games)}, Away games: {len(away_games)}")
            
            # Process home games
            home_stats = {
                'gs': [], 'xg': [], 'corsi_pct': [], 'fenwick_pct': [], 'pdo': [],
                'ozs': [], 'nzs': [], 'dzs': [], 'goals': [], 'opp_goals': [], 'shots': [],
                'hits': [], 'blocked_shots': [], 'giveaways': [], 'takeaways': [],
                'penalty_minutes': [], 'power_play_pct': [], 'penalty_kill_pct': [],
                'faceoff_pct': [], 'nzt': [], 'nztsa': [], 'fc': [], 'rush': [],
                'lat': [], 'long_movement': [], 'hdc': [], 'hdca': [], 'opp_xg': [], 'period_dzs': [],
                'games': []
            }
            
            for i, game_info in enumerate(home_games):
                game_id = game_info.get('game_id')
                if not game_id:
                    continue
                
                print(f"  Processing home game {i+1}/{len(home_games)}: {game_info.get('date')} (ID: {game_id})...", end=' ', flush=True)
                
                try:
                    game_data = self.api.get_comprehensive_game_data(str(game_id))
                    if not game_data:
                        print("No data")
                        continue
                    
                    boxscore = game_data.get('boxscore', {})
                    home_team_data = boxscore.get('homeTeam', {})
                    team_id = home_team_data.get('id')
                    
                    if not team_id:
                        print("No team ID")
                        continue
                    
                    metrics = self.calculate_game_metrics(game_data, team_id, is_home=True)
                    if metrics:
                        # DEBUG: Print first game's metrics to verify opponent fields exist
                        if i == 0:
                            print(f"\n  DEBUG - Metrics keys: {list(metrics.keys())}")
                            print(f"  DEBUG - opp_goals: {metrics.get('opp_goals', 'MISSING')}")
                            print(f"  DEBUG - opp_xg: {metrics.get('opp_xg', 'MISSING')}\n")
                        
                        for key in home_stats.keys():
                            if key != 'games':
                                home_stats[key].append(metrics.get(key, 0))
                        home_stats['games'].append(i)
                        print(f"✓ GS={metrics['gs']:.1f}, xG={metrics['xg']:.2f}")
                    else:
                        print("Failed to calculate metrics")
                except Exception as e:
                    print(f"Error: {e}")
            
            # Process away games
            away_stats = {
                'gs': [], 'xg': [], 'corsi_pct': [], 'fenwick_pct': [], 'pdo': [],
                'ozs': [], 'nzs': [], 'dzs': [], 'goals': [], 'opp_goals': [], 'shots': [],
                'hits': [], 'blocked_shots': [], 'giveaways': [], 'takeaways': [],
                'penalty_minutes': [], 'power_play_pct': [], 'penalty_kill_pct': [],
                'faceoff_pct': [], 'nzt': [], 'nztsa': [], 'fc': [], 'rush': [],
                'lat': [], 'long_movement': [], 'hdc': [], 'hdca': [], 'opp_xg': [], 'period_dzs': [],
                'games': []
            }
            
            for i, game_info in enumerate(away_games):
                game_id = game_info.get('game_id')
                if not game_id:
                    continue
                
                print(f"  Processing away game {i+1}/{len(away_games)}: {game_info.get('date')} (ID: {game_id})...", end=' ', flush=True)
                
                try:
                    game_data = self.api.get_comprehensive_game_data(str(game_id))
                    if not game_data:
                        print("No data")
                        continue
                    
                    boxscore = game_data.get('boxscore', {})
                    away_team_data = boxscore.get('awayTeam', {})
                    team_id = away_team_data.get('id')
                    
                    if not team_id:
                        print("No team ID")
                        continue
                    
                    metrics = self.calculate_game_metrics(game_data, team_id, is_home=False)
                    if metrics:
                        for key in away_stats.keys():
                            if key != 'games':
                                away_stats[key].append(metrics.get(key, 0))
                        away_stats['games'].append(i)
                        print(f"✓ GS={metrics['gs']:.1f}, xG={metrics['xg']:.2f}")
                    else:
                        print("Failed to calculate metrics")
                except Exception as e:
                    print(f"Error: {e}")
            
            teams_data[abbrev] = {
                'home': home_stats,
                'away': away_stats
            }
            
            # DEBUG: Check if opponent fields exist in arrays
            print(f"  DEBUG - home_stats keys: {list(home_stats.keys())}")
            print(f"  DEBUG - home opp_goals array length: {len(home_stats.get('opp_goals', []))}")
            print(f"  DEBUG - home opp_xg array length: {len(home_stats.get('opp_xg', []))}")
            
            print(f"\n✓ Completed {abbrev}: {len(home_stats['gs'])} home games, {len(away_stats['gs'])} away games")
        
        output = {"teams": teams_data}
        
        # DEBUG: Print what's actually about to be written
        if teams_data:
            first_team = list(teams_data.keys())[0]
            print(f"\n\n=== FINAL DEBUG BEFORE JSON WRITE ===")
            print(f"First team: {first_team}")
            print(f"Home keys: {list(teams_data[first_team]['home'].keys())}")
            print(f"Has opp_goals? {'opp_goals' in teams_data[first_team]['home']}")
            print(f"Has opp_xg? {'opp_xg' in teams_data[first_team]['home']}")
            if 'opp_goals' in teams_data[first_team]['home']:
                print(f"opp_goals length: {len(teams_data[first_team]['home']['opp_goals'])}")
            if 'opp_xg' in teams_data[first_team]['home']:
                print(f"opp_xg length: {len(teams_data[first_team]['home']['opp_xg'])}")
            print(f"=====================================\n")
        
        # Ensure the 'data' directory exists
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(self.output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✓ Generated {self.output_file} with real calculated data!")
        print(f"{'='*60}")

if __name__ == "__main__":
    generator = RealTeamStatsGenerator()
    generator.generate_all_team_stats()
