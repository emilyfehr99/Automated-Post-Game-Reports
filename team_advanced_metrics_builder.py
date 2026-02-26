#!/usr/bin/env python3
"""
Team Advanced Metrics Builder
Extracts custom PBP-based metrics for teams across the season:
  - Rebound Generation (Offensive)
  - Rush Chances & Capitalization
  - Defensive Zone Giveaways ("Pizzas") & High-Danger Turnovers
  - Slot Shot Block Rate

Processes all completed games from prediction history and saves
structured team stats to team_advanced_metrics.json.
"""

import json
import time
import math
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from nhl_api_client import NHLAPIClient

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
        self.team_stats = defaultdict(lambda: {
            'team': '',
            'games': 0,
            
            # Rebounds Generated (Offense)
            'rebound_shots_generated': 0,
            'rebound_goals_generated': 0,
            'total_offensive_shots': 0,
            
            # Rush Chances (Offense)
            'rush_shots_for': 0,
            'rush_goals_for': 0,
            
            # Turnovers (Defense/Puck Management)
            'dzone_giveaways': 0,
            'hd_giveaways': 0,      # Giveaways in high-danger slot
            'total_giveaways': 0,
            
            # Shot Blocking (Defense)
            'shots_blocked_in_slot': 0,
            'total_blocks': 0,
            
            # Opponent metrics (to calculate rates like block % or rush defense)
            'opp_rush_shots': 0,
            'opp_rush_goals': 0,
            'opp_rebound_shots': 0,
            
            'game_log': [],
        })
        
        self.processed_games = set()
        self._load_existing()
    
    def _load_existing(self):
        path = Path('data/team_advanced_metrics.json')
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            
            self.processed_games = set(data.get('processed_games', []))
            for abbrev, stats in data.get('teams', {}).items():
                self.team_stats[abbrev] = stats
            
            print(f"📂 Loaded existing advanced stats: {len(self.team_stats)} teams, "
                  f"{len(self.processed_games)} games processed")
                  
    def _shot_distance(self, x: float, y: float, defending_right: bool) -> float:
        """Calculate distance from event to the net."""
        goal_x = 89.0 if defending_right else -89.0
        return math.sqrt((x - goal_x) ** 2 + y ** 2)
    
    def _is_high_danger(self, x: float, y: float, defending_right: bool) -> bool:
        return self._shot_distance(x, y, defending_right) <= HIGH_DANGER_DIST
    
    def _is_slot(self, x: float, y: float, defending_right: bool) -> bool:
        goal_x = 89.0 if defending_right else -89.0
        return (abs(x - goal_x) <= (89 - SLOT_X_THRESHOLD) and 
                abs(y) <= SLOT_Y_THRESHOLD)

    def _get_time_secs(self, time_str: str, period: int) -> int:
        try:
            parts = time_str.split(':')
            return int(parts[0]) * 60 + int(parts[1]) + (period - 1) * 1200
        except:
            return 0

    def process_game(self, game_id: str):
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
        
        # Game-level trackers
        game_data = {
            away_abbrev: {'reb_gen': 0, 'reb_goals': 0, 'rush_for': 0, 'rush_goals': 0, 
                          'dz_give': 0, 'hd_give': 0, 'tot_give': 0, 'slot_blk': 0, 'tot_blk': 0, 'shots': 0},
            home_abbrev: {'reb_gen': 0, 'reb_goals': 0, 'rush_for': 0, 'rush_goals': 0, 
                          'dz_give': 0, 'hd_give': 0, 'tot_give': 0, 'slot_blk': 0, 'tot_blk': 0, 'shots': 0},
        }

        # Possession tracking for rush definition
        # Track the last time a team gained possession (takeaway, won faceoff, opp giveaway)
        last_possession_change_time = {away_abbrev: 0, home_abbrev: 0}
        
        # Track last shot for rebounds
        last_shot_time = {away_abbrev: -999, home_abbrev: -999}
        
        for play in plays:
            event_type = play.get('typeDescKey', '')
            details = play.get('details', {})
            event_team_id = details.get('eventOwnerTeamId')
            
            if not event_team_id:
                if event_type == 'faceoff':
                    event_team_id = details.get('winningPlayerTeamId')
                else:
                    continue
            
            team_abbrev = away_abbrev if event_team_id == away_team_id else home_abbrev
            opp_abbrev = home_abbrev if team_abbrev == away_abbrev else away_abbrev
            
            x = details.get('xCoord', 0) or 0
            y = details.get('yCoord', 0) or 0
            time_str = play.get('timeInPeriod', '00:00')
            period = play.get('periodDescriptor', {}).get('number', 1)
            time_secs = self._get_time_secs(time_str, period)
            
            home_defending = play.get('homeTeamDefendingSide', 'right')
            # If home defends right, their net is at x=89, away net is at x=-89
            # If team_abbrev is home, they defend right -> goal is x=89.
            # If team_abbrev is away, they defend left -> goal is x=-89.
            if team_abbrev == home_abbrev:
                defending_right = (home_defending == 'right')
                # Home is defending `defending_right`, attacking the opposite
                attacking_right = not defending_right
            else:
                defending_right = (home_defending != 'right')
                attacking_right = not defending_right
                
            is_goal = (event_type == 'goal')

            # Possession updates
            if event_type in ('takeaway', 'faceoff'):
                last_possession_change_time[team_abbrev] = time_secs
            elif event_type == 'giveaway':
                last_possession_change_time[opp_abbrev] = time_secs
                game_data[team_abbrev]['tot_give'] += 1
                zone = details.get('zoneCode', '')
                if zone == 'D':
                    game_data[team_abbrev]['dz_give'] += 1
                    if self._is_high_danger(x, y, defending_right):
                        game_data[team_abbrev]['hd_give'] += 1

            elif event_type == 'blocked-shot':
                # The team blocking the shot is the eventOwnerTeamId
                game_data[team_abbrev]['tot_blk'] += 1
                # Event coords are where the block happened (in their defending zone)
                if self._is_slot(x, y, defending_right):
                    game_data[team_abbrev]['slot_blk'] += 1

            elif event_type in ('shot-on-goal', 'goal', 'missed-shot'):
                if event_type in ('shot-on-goal', 'goal'):
                    game_data[team_abbrev]['shots'] += 1
                
                # Rebound logic
                if team_abbrev in last_shot_time:
                    prev_time = last_shot_time[team_abbrev]
                    if 0 < (time_secs - prev_time) <= REBOUND_WINDOW_SEC:
                        if event_type != 'missed-shot':
                            game_data[team_abbrev]['reb_gen'] += 1
                            if is_goal:
                                game_data[team_abbrev]['reb_goals'] += 1
                
                last_shot_time[team_abbrev] = time_secs
                
                # Rush logic
                pos_time = last_possession_change_time.get(team_abbrev, 0)
                if pos_time > 0 and 0 < (time_secs - pos_time) <= RUSH_WINDOW_SEC:
                    if event_type != 'missed-shot':
                        game_data[team_abbrev]['rush_for'] += 1
                        if is_goal:
                            game_data[team_abbrev]['rush_goals'] += 1

        # Aggregate 
        for abbrev in [away_abbrev, home_abbrev]:
            opp = home_abbrev if abbrev == away_abbrev else away_abbrev
            
            ts = self.team_stats[abbrev]
            ts['games'] += 1
            ts['rebound_shots_generated'] += game_data[abbrev]['reb_gen']
            ts['rebound_goals_generated'] += game_data[abbrev]['reb_goals']
            ts['total_offensive_shots'] += game_data[abbrev]['shots']
            ts['rush_shots_for'] += game_data[abbrev]['rush_for']
            ts['rush_goals_for'] += game_data[abbrev]['rush_goals']
            ts['dzone_giveaways'] += game_data[abbrev]['dz_give']
            ts['hd_giveaways'] += game_data[abbrev]['hd_give']
            ts['total_giveaways'] += game_data[abbrev]['tot_give']
            ts['shots_blocked_in_slot'] += game_data[abbrev]['slot_blk']
            ts['total_blocks'] += game_data[abbrev]['tot_blk']
            
            ts['opp_rush_shots'] += game_data[opp]['rush_for']
            ts['opp_rush_goals'] += game_data[opp]['rush_goals']
            ts['opp_rebound_shots'] += game_data[opp]['reb_gen']
            
            ts['game_log'].append({
                'game_id': game_id,
                'rush_shots': game_data[abbrev]['rush_for'],
                'rush_goals': game_data[abbrev]['rush_goals'],
                'dzone_giveaways': game_data[abbrev]['dz_give'],
                'hd_giveaways': game_data[abbrev]['hd_give'],
            })
            
        self.processed_games.add(game_id)
        
    def save(self):
        output = {
            'updated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'processed_games': list(self.processed_games),
            'teams': {},
        }
        
        for k, v in self.team_stats.items():
            if v['games'] == 0: continue
            
            # Compute rates
            shots = max(1, v['total_offensive_shots'])
            games = max(1, v['games'])
            
            v['rebound_gen_rate'] = round(v['rebound_shots_generated'] / shots, 3)
            v['rush_rate'] = round(v['rush_shots_for'] / shots, 3)
            v['rush_capitalization'] = round(v['rush_goals_for'] / max(1, v['rush_shots_for']), 3)
            
            v['pizzas_per_game'] = round(v['dzone_giveaways'] / games, 2)
            v['hd_pizzas_per_game'] = round(v['hd_giveaways'] / games, 2)
            v['slot_blocks_per_game'] = round(v['shots_blocked_in_slot'] / games, 2)
            
            output['teams'][k] = v
            
        Path('data').mkdir(exist_ok=True)
        with open('data/team_advanced_metrics.json', 'w') as f:
            json.dump(output, f, indent=2)
            
        print(f"💾 Saved advanced stats for {len(output['teams'])} teams")
        
    def run_backfill(self, game_ids: List[str], batch_size: int = 20):
        new_games = [gid for gid in game_ids if str(gid) not in self.processed_games]
        print(f"🏒 Backfilling Team ADV Stats: {len(new_games)} new games")
        
        for i, gid in enumerate(new_games):
            try:
                self.process_game(gid)
                if (i + 1) % batch_size == 0 or (i + 1) == len(new_games):
                    self.save()
                    print(f"  ✅ {i+1}/{len(new_games)} processed")
                    time.sleep(0.3)
            except Exception as e:
                print(f"  ⚠️  Error on game {gid}: {e}")
                
        print("\n📊 TEAM ADVANCED METRICS SUMMARY")
        print("=" * 80)
        
        teams = [v for v in self.team_stats.values() if v['games'] > 10]
        teams.sort(key=lambda x: x['rebound_gen_rate'], reverse=True)
        
        print(f"{'Team':<5} {'GP':>3} | {'RebGen%':>8} | {'Rush/Gm':>8} | {'Pizzas/Gm':>10}")
        print("-" * 50)
        for t in teams[:10]:
            print(f"{t['team']:<5} {t['games']:>3} | {t['rebound_gen_rate']:>8.1%} | "
                  f"{t['rush_shots_for']/t['games']:>8.1f} | {t['pizzas_per_game']:>10.1f}")


    def run_refresher(self):
        """Main entry point to refresh team stats from prediction history."""
        for p in [Path('data/win_probability_predictions_v2.json'),
                  Path('win_probability_predictions_v2.json')]:
            if p.exists():
                with open(p) as f:
                    pred_data = json.load(f)
                game_ids = [str(pr.get('game_id')) for pr in pred_data.get('predictions', []) 
                           if pr.get('actual_winner')]
                
                print(f"📋 Found {len(game_ids)} completed games to process for Team ADV Stats")
                self.run_backfill(game_ids)
                return
        
        print("❌ No prediction history found")


if __name__ == "__main__":
    builder = TeamAdvancedMetricsBuilder()
    builder.run_refresher()
