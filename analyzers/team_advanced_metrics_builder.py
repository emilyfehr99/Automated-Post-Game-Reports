#!/usr/bin/env python3
"""
Team Advanced Metrics Builder
Extracts custom PBP-based metrics for teams across the season:
  - Rebound Generation (Offensive)
  - Rush Chances & Capitalization
  - Defensive Zone Giveaways ("Pizzas") & High-Danger Turnovers
  - Slot Shot Block Rate
  - Goalie GSAX (utilizing ImprovedXGModel)

Processes all completed games from prediction history and saves
structured data to team_advanced_metrics.json.
"""

import json
import time
import math
import os
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from nhl_api_client import NHLAPIClient
from improved_xg_model import ImprovedXGModel

# ─── Ice Geometry Constants ───
SLOT_X_THRESHOLD = 69     # Inside ~20ft of goal line
SLOT_Y_THRESHOLD = 22     # Within ~22ft of center (slot width)
HIGH_DANGER_DIST = 25     # Within 25ft of net = high-danger
CREASE_DIST = 10          # Within 10ft = crease area

REBOUND_WINDOW_SEC = 3.0  # Consecutive shots within 3s = rebound
RUSH_WINDOW_SEC = 6.0     # Shot within 6s of possession change = rush chance


class TeamAdvancedMetricsBuilder:
    """Extracts and aggregates custom advanced team metrics from PBP data."""
    
    def __init__(self):
        self.api = NHLAPIClient()
        self.xg_model = ImprovedXGModel()
        self.team_stats = defaultdict(lambda: {
            'team': '',
            'games': 0,
            
            # Rebounds Generated (Offense)
            'rebound_shots_generated': 0,
            'rapid_rebound_shots': 0,      # < 2.0s
            'rebound_goals_generated': 0,
            'total_offensive_shots': 0,
            
            # Rush & Transition (Offense)
            'rush_shots_for': 0,
            'rush_goals_for': 0,
            'ex_to_en_times': [],         # List of transition speeds (D-Exit -> O-Entry)
            'en_to_s_times': [],          # List of persistence times (O-Entry -> Shot)
            
            # Tactical Sequence Buckets
            'quick_strike_shots': 0,      # < 10s possession
            'mid_range_buildup_shots': 0, # 10-30s possession
            'extended_buildup_shots': 0,  # > 30s possession
            
            # Turnovers (Defense/Puck Management)
            'dzone_giveaways': 0,
            'hd_giveaways': 0,      # Giveaways in high-danger slot
            'total_giveaways': 0,
            
            # Shot Blocking (Defense)
            'shots_blocked_in_slot': 0,
            'total_blocks': 0,
            
            # Faceoffs (Tactical Core)
            'ozone_faceoff_wins': 0,
            'ozone_faceoff_total': 0,
            
            'game_log': [],
        })
        
        # Track Goalie-Specific GSAX (xG - Total Goals)
        self.goalie_stats = defaultdict(lambda: {
            'name': '',
            'team': '',
            'games': 0,
            'xg_faced': 0.0,
            'goals_against': 0,
            'shots_on_goal': 0,
        })
        
        self.processed_games = set()
        self.output_path = Path('data/team_advanced_metrics.json')
        self._load_existing()
    
    def set_output_path(self, path: str):
        """Allow custom output path for historical reconstructions."""
        self.output_path = Path(path)
        self.processed_games = set()
        self.team_stats.clear()
        self.goalie_stats.clear()
        self._load_existing()
    
    def _load_existing(self):
        if self.output_path.exists():
            try:
                with open(self.output_path) as f:
                    data = json.load(f)
                
                self.processed_games = set(data.get('processed_games', []))
                for abbrev, stats in data.get('teams', {}).items():
                    base = self.team_stats[abbrev]
                    base.update(stats)
                    self.team_stats[abbrev] = base
                
                # Load goalie stats if they exist
                for gid, stats in data.get('goalies', {}).items():
                    self.goalie_stats[int(gid)].update(stats)
                
                print(f"📂 Loaded existing advanced stats: {len(self.team_stats)} teams, "
                      f"{len(self.goalie_stats)} goalies, {len(self.processed_games)} games processed")
            except Exception as e:
                print(f"⚠️ Error loading existing stats: {e}. Starting fresh.")
                  
    def _shot_distance(self, x: float, y: float, defending_right: bool) -> float:
        """Calculate distance from event to the net."""
        goal_x = 89.0 if defending_right else -89.0
        return math.sqrt((x - goal_x) ** 2 + y ** 2)
    
    def _is_high_danger(self, x: float, y: float, defending_right: bool) -> bool:
        return self._shot_distance(x, y, defending_right) <= HIGH_DANGER_DIST

    def _is_slot(self, x: float, y: float, defending_right: bool) -> bool:
        in_x = (x >= SLOT_X_THRESHOLD) if defending_right else (x <= -SLOT_X_THRESHOLD)
        in_y = abs(y) <= SLOT_Y_THRESHOLD
        return in_x and in_y

    def _get_time_secs(self, time_str: str, period: int) -> int:
        m, s = map(int, time_str.split(':'))
        return (period - 1) * 1200 + m * 60 + s

    def process_game(self, game_id: str):
        """Process a single game's play-by-play for advanced metrics."""
        game_id = str(game_id)
        if game_id in self.processed_games:
            return
            
        pbp = self.api.get_play_by_play(game_id)
        if not pbp:
            return
            
        plays = pbp.get('plays', [])
        if not plays:
            return
            
        away_team_id = pbp.get('awayTeam', {}).get('id')
        home_team_id = pbp.get('homeTeam', {}).get('id')
        away_abbrev = pbp.get('awayTeam', {}).get('abbrev', '???')
        home_abbrev = pbp.get('homeTeam', {}).get('abbrev', '???')
        
        # Init base stats
        self.team_stats[away_abbrev]['team'] = away_abbrev
        self.team_stats[home_abbrev]['team'] = home_abbrev
        
        # High-Fidelity State Trackers
        last_shot_time = {away_abbrev: -999, home_abbrev: -999}
        possession_start = {away_abbrev: 0, home_abbrev: 0}
        last_dz_exit = {away_abbrev: 0, home_abbrev: 0}
        last_oz_entry = {away_abbrev: 0, home_abbrev: 0}
        current_zone = {away_abbrev: 'N', home_abbrev: 'N'}
        
        # Game State for xG Model
        score = {away_team_id: 0, home_team_id: 0}
        strength = '5v5'
        previous_events = []
        
        # Goalie Mapping
        goalie_names = {}
        for spot in pbp.get('rosterSpots', []):
            if spot.get('positionCode') == 'G':
                goalie_names[spot['playerId']] = f"{spot['firstName']['default']} {spot['lastName']['default']}"

        # Team game log trackers
        game_data = {
            away_abbrev: {'reb_gen': 0, 'rapid_reb': 0, 'reb_goals': 0, 'rush_for': 0, 'rush_goals': 0, 
                          'dz_give': 0, 'hd_give': 0, 'tot_give': 0, 'slot_blk': 0, 'tot_blk': 0, 'shots': 0,
                          'ex_to_en': [], 'en_to_s': [], 'quick': 0, 'mid': 0, 'ext': 0,
                          'oz_fo_win': 0, 'oz_fo_tot': 0},
            home_abbrev: {'reb_gen': 0, 'rapid_reb': 0, 'reb_goals': 0, 'rush_for': 0, 'rush_goals': 0, 
                          'dz_give': 0, 'hd_give': 0, 'tot_give': 0, 'slot_blk': 0, 'tot_blk': 0, 'shots': 0,
                          'ex_to_en': [], 'en_to_s': [], 'quick': 0, 'mid': 0, 'ext': 0,
                          'oz_fo_win': 0, 'oz_fo_tot': 0},
        }
        
        # Track goalies who played in this game
        game_goalies = set()
        
        for play in plays:
            event_type = play.get('typeDescKey', '')
            details = play.get('details', {})
            event_team_id = details.get('eventOwnerTeamId')
            
            if not event_team_id:
                if event_type == 'faceoff':
                    event_team_id = details.get('winningPlayerTeamId')
                else:
                    previous_events.append(play)
                    continue
            
            team_abbrev = away_abbrev if event_team_id == away_team_id else home_abbrev
            opp_abbrev = home_abbrev if team_abbrev == away_abbrev else away_abbrev
            
            x = details.get('xCoord', 0) or 0
            y = details.get('yCoord', 0) or 0
            time_str = play.get('timeInPeriod', '00:00')
            period = play.get('periodDescriptor', {}).get('number', 1)
            time_secs = self._get_time_secs(time_str, period)
            zone = details.get('zoneCode', '')
            
            home_defending = play.get('homeTeamDefendingSide', 'right')
            if team_abbrev == home_abbrev:
                defending_right = (home_defending == 'right')
                attacking_right = not defending_right
            else:
                defending_right = (home_defending != 'right')
                attacking_right = not defending_right
                
            is_goal = (event_type == 'goal')

            # 🚀 ZONE LOGIC (EXtoEN, ENtoS)
            if zone and zone != current_zone[team_abbrev]:
                prev_z = current_zone[team_abbrev]
                current_zone[team_abbrev] = zone
                
                # Exit Defense
                if prev_z == 'D' and zone in ('N', 'O'):
                    last_dz_exit[team_abbrev] = time_secs
                    # Reset Oz entry as we are leaving D
                    last_oz_entry[team_abbrev] = 0
                
                # Enter Offense
                elif zone == 'O':
                    last_oz_entry[team_abbrev] = time_secs
                    if last_dz_exit[team_abbrev] > 0:
                        game_data[team_abbrev]['ex_to_en'].append(time_secs - last_dz_exit[team_abbrev])
                
                # Exit Offense
                elif prev_z == 'O' and zone in ('N', 'D'):
                    last_oz_entry[team_abbrev] = 0

            # Possession updates
            if event_type == 'faceoff':
                possession_start[team_abbrev] = time_secs
                if zone == 'O':
                    game_data[team_abbrev]['oz_fo_tot'] += 1
                    game_data[team_abbrev]['oz_fo_win'] += 1
                    game_data[opp_abbrev]['oz_fo_tot'] += 1
            elif event_type == 'takeaway':
                possession_start[team_abbrev] = time_secs
            elif event_type == 'giveaway':
                possession_start[opp_abbrev] = time_secs
                game_data[team_abbrev]['tot_give'] += 1
                if zone == 'D':
                    game_data[team_abbrev]['dz_give'] += 1
                    if self._is_high_danger(x, y, defending_right):
                        game_data[team_abbrev]['hd_give'] += 1

            elif event_type == 'blocked-shot':
                game_data[team_abbrev]['tot_blk'] += 1
                if self._is_slot(x, y, defending_right):
                    game_data[team_abbrev]['slot_blk'] += 1

            elif event_type in ('shot-on-goal', 'goal', 'missed-shot'):
                if event_type in ('shot-on-goal', 'goal'):
                    game_data[team_abbrev]['shots'] += 1
                
                # REB: Rebound tracking
                if team_abbrev in last_shot_time:
                    delta = time_secs - last_shot_time[team_abbrev]
                    if 0 < delta <= REBOUND_WINDOW_SEC:
                        if event_type != 'missed-shot':
                            game_data[team_abbrev]['reb_gen'] += 1
                            if delta <= 2.0: game_data[team_abbrev]['rapid_reb'] += 1
                            if is_goal: game_data[team_abbrev]['reb_goals'] += 1
                last_shot_time[team_abbrev] = time_secs
                
                # 🎯 Tactical Sequence Buckets (ENtoS)
                if possession_start[team_abbrev] > 0:
                    poss_dur = time_secs - possession_start[team_abbrev]
                    if poss_dur <= 10: game_data[team_abbrev]['quick'] += 1
                    elif poss_dur <= 30: game_data[team_abbrev]['mid'] += 1
                    else: game_data[team_abbrev]['ext'] += 1
                    
                if last_oz_entry[team_abbrev] > 0:
                    game_data[team_abbrev]['en_to_s'].append(time_secs - last_oz_entry[team_abbrev])
                
                # 🧤 GOALIE GSAX (xG - Total Goals)
                if event_type in ('shot-on-goal', 'goal'):
                    goalie_id = details.get('goalieInNetId')
                    if goalie_id:
                        game_goalies.add(goalie_id)
                        shot_data = {
                            'x_coord': x,
                            'y_coord': y,
                            'shot_type': details.get('shotType', 'wrist'),
                            'event_type': event_type,
                            'time_in_period': time_str,
                            'period': period,
                            'strength_state': strength,
                            'score_differential': score[event_team_id] - score[home_team_id if event_team_id == away_team_id else away_team_id],
                            'team_id': event_team_id
                        }
                        xg = self.xg_model.calculate_xg(shot_data, previous_events)
                        gs = self.goalie_stats[goalie_id]
                        if not gs['name']:
                            gs['name'] = goalie_names.get(goalie_id, f"Goalie {goalie_id}")
                            gs['team'] = opp_abbrev
                        
                        gs['xg_faced'] += xg
                        gs['shots_on_goal'] += 1
                        if is_goal:
                            gs['goals_against'] += 1
                            score[event_team_id] += 1
            
            # Maintain rolling window for xG context
            previous_events.append(play)
            if len(previous_events) > 10:
                previous_events.pop(0)

        # Update goalie game counts
        for gid in game_goalies:
            self.goalie_stats[gid]['games'] += 1

        # Aggregate Team Data
        for abbrev in [away_abbrev, home_abbrev]:
            ts = self.team_stats[abbrev]
            gd = game_data[abbrev]
            ts['games'] += 1
            ts['rebound_shots_generated'] += gd['reb_gen']
            ts['rapid_rebound_shots'] += gd['rapid_reb']
            ts['rebound_goals_generated'] += gd['reb_goals']
            ts['total_offensive_shots'] += gd['shots']
            ts['quick_strike_shots'] += gd['quick']
            ts['mid_range_buildup_shots'] += gd['mid']
            ts['extended_buildup_shots'] += gd['ext']
            ts['dzone_giveaways'] += gd['dz_give']
            ts['hd_giveaways'] += gd['hd_give']
            ts['total_giveaways'] += gd['tot_give']
            ts['shots_blocked_in_slot'] += gd['slot_blk']
            ts['total_blocks'] += gd['tot_blk']
            ts['ozone_faceoff_wins'] += gd['oz_fo_win']
            ts['ozone_faceoff_total'] += gd['oz_fo_tot']
            ts['ex_to_en_times'].extend(gd['ex_to_en'])
            ts['en_to_s_times'].extend(gd['en_to_s'])
            
            ts['game_log'].append({
                'game_id': game_id,
                'rapid_rebonds': gd['rapid_reb'],
                'quick_strikes': gd['quick'],
                'dzone_giveaways': gd['dz_give'],
            })
            
        self.processed_games.add(game_id)
        
    def save(self):
        """Save aggregated metrics to a JSON file."""
        team_summaries = {}
        for abbrev, stats in self.team_stats.items():
            if stats['games'] == 0: continue
            
            summary = stats.copy()
            shots = max(1, stats['total_offensive_shots'])
            games = max(1, stats['games'])

            summary['rebound_gen_rate'] = round(stats['rebound_shots_generated'] / shots, 3)
            summary['rapid_reb_rate'] = round(stats['rapid_rebound_shots'] / shots, 3)
            summary['quick_strike_rate'] = round(stats['quick_strike_shots'] / shots, 3)
            summary['extended_buildup_rate'] = round(stats['extended_buildup_shots'] / shots, 3)
            
            summary['avg_ex_to_en'] = round(sum(stats['ex_to_en_times']) / len(stats['ex_to_en_times']), 2) if stats['ex_to_en_times'] else 0
            summary['avg_en_to_s'] = round(sum(stats['en_to_s_times']) / len(stats['en_to_s_times']), 2) if stats['en_to_s_times'] else 0
            
            summary['pizzas_per_game'] = round(stats['total_giveaways'] / games, 2)
            summary['hd_pizzas_per_game'] = round(stats['hd_giveaways'] / games, 2)
            summary['slot_block_rate'] = round(stats['shots_blocked_in_slot'] / stats['total_blocks'], 3) if stats['total_blocks'] > 0 else 0
            summary['ozone_faceoff_pct'] = round(stats['ozone_faceoff_wins'] / stats['ozone_faceoff_total'], 3) if stats['ozone_faceoff_total'] > 0 else 0.5
            
            del summary['ex_to_en_times']
            del summary['en_to_s_times']
            team_summaries[abbrev] = summary

        goalie_summaries = {}
        for gid, gs in self.goalie_stats.items():
            if gs['shots_on_goal'] < 10: continue
            
            summ = gs.copy()
            summ['gsax'] = round(gs.get('xg_faced', 0) - gs.get('goals_against', 0), 2)
            team_games = team_summaries.get(gs.get('team', ''), {}).get('games', 1)
            summ['gsax_per_game'] = round(summ['gsax'] / team_games, 3)
            goalie_summaries[str(gid)] = summ

        output = {
            'updated_at': time.strftime("%Y-%m-%dT%H:%M:%S"),
            'processed_games': list(self.processed_games),
            'teams': team_summaries,
            'goalies': goalie_summaries
        }
        
        Path('data').mkdir(exist_ok=True)
        with open(self.output_path, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"💾 Saved advanced stats for {len(team_summaries)} teams and {len(goalie_summaries)} goalies")

    def run_backfill(self, game_ids: List[str], batch_size: int = 50):
        new_games = [gid for gid in game_ids if str(gid) not in self.processed_games]
        print(f"🏒 Backfilling Team & Goalie ADV Stats: {len(new_games)} games")
        
        for i, gid in enumerate(new_games):
            try:
                self.process_game(gid)
                if (i + 1) % batch_size == 0 or (i + 1) == len(new_games):
                    self.save()
                    print(f"  ✅ {i+1}/{len(new_games)} processed")
            except Exception as e:
                print(f"  ⚠️ Error on game {gid}: {e}")
                
    def rebuild_season(self, count=923):
        """Full high-fidelity re-audit of the season history"""
        # Scrape or load game IDs from the prediction history
        p = Path('data/win_probability_predictions_v2.json')
        if p.exists():
            with open(p) as f:
                data = json.load(f)
            # Take the most recent 'count' games that have an actual winner (completed)
            game_ids = [str(pr.get('game_id')) for pr in data.get('predictions', []) 
                       if pr.get('actual_winner')]
            # Sort by game ID to ensure consistent backfill
            self.run_backfill(sorted(game_ids)[-count:])
        else:
            print("❌ No prediction history found for rebuild")

    def run_refresher(self):
        self.rebuild_season(100) # Quick refresh of last 100 games

if __name__ == "__main__":
    # Force a full clean rebuild if requested or if logic changed
    stale = 'data/team_advanced_metrics.json'
    if os.path.exists(stale):
        os.remove(stale)
        print(f"🗑️ Cleared stale metrics for full xG rebuild")

    builder = TeamAdvancedMetricsBuilder()
    builder.run_refresher()
