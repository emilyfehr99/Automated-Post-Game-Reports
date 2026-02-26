#!/usr/bin/env python3
"""
Goalie Stats Builder
Extracts comprehensive goalie metrics from NHL play-by-play data:
  - Save % (overall, EV, PP/PK)
  - High-danger save % (shots from slot/crease)
  - Off-wing save % (shots to glove vs blocker side)
  - Rebound control (% of shots that generate rebounds)
  - Cross-ice save %
  - Shot type breakdown (wrist, slap, snap, backhand, etc.)
  - GSAX (Goals Saved Above Expected)
  - Recent form (last 5/10 games weighted)

Processes all completed games from prediction history and saves
structured goalie stats to goalie_stats.json.
"""

import json
import time
import math
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from nhl_api_client import NHLAPIClient


# ─── Ice Geometry Constants ───
# NHL rink: 200ft x 85ft, center ice at (0,0)
# Positive x = right side of rink (from broadcast view)
# Goal lines at x = ±89
SLOT_X_THRESHOLD = 69     # Inside ~20ft of goal line
SLOT_Y_THRESHOLD = 22     # Within ~22ft of center (slot width)
HIGH_DANGER_DIST = 25     # Within 25ft of net = high-danger
CREASE_DIST = 10          # Within 10ft = crease area
REBOUND_WINDOW_SEC = 3    # Consecutive shots within 3s = rebound

# xG lookup by distance + shot type (simplified model)
XG_BASE = {
    'wrist': 0.065,
    'snap': 0.075,
    'slap': 0.055,
    'backhand': 0.085,
    'tip-in': 0.120,
    'wrap-around': 0.050,
    'deflected': 0.090,
    '': 0.060,
}


class GoalieStatsBuilder:
    """Extracts and aggregates goalie stats from PBP data."""
    
    def __init__(self):
        self.api = NHLAPIClient()
        self.goalie_cache = {}      # goalie_id -> catches hand
        self.goalie_names = {}      # goalie_id -> full name
        self.goalie_stats = defaultdict(lambda: {
            'name': '',
            'team': '',
            'catches': '',
            'games': 0,
            'wins': 0,
            'losses': 0,
            'ot_losses': 0,
            
            # Save counts
            'shots_against': 0,
            'goals_against': 0,
            'saves': 0,
            
            # Situation splits
            'ev_shots': 0, 'ev_goals': 0,
            'pp_shots': 0, 'pp_goals': 0,   # Opponent on PP (goalie PK)
            'pk_shots': 0, 'pk_goals': 0,   # Team on PP (goalie PP)
            
            # Shot type breakdown
            'wrist_shots': 0, 'wrist_goals': 0,
            'snap_shots': 0, 'snap_goals': 0,
            'slap_shots': 0, 'slap_goals': 0,
            'backhand_shots': 0, 'backhand_goals': 0,
            'tipin_shots': 0, 'tipin_goals': 0,
            'wraparound_shots': 0, 'wraparound_goals': 0,
            
            # Location-based
            'high_danger_shots': 0, 'high_danger_goals': 0,
            'slot_shots': 0, 'slot_goals': 0,
            'perimeter_shots': 0, 'perimeter_goals': 0,
            
            # Shot Angle (Center vs Acute)
            'center_angle_shots': 0, 'center_angle_goals': 0,
            'acute_angle_shots': 0, 'acute_angle_goals': 0,
            
            # Off-wing (shots to blocker side vs glove side)
            'glove_shots': 0, 'glove_goals': 0,
            'blocker_shots': 0, 'blocker_goals': 0,
            
            # Home vs Away Split
            'home_shots': 0, 'home_goals': 0,
            'away_shots': 0, 'away_goals': 0,
            
            # Head-to-Head tracking (opponent_abbrev -> {shots, goals})
            'opponent_stats': {},
            
            # Rebound control
            'rebound_shots': 0,      # Shots that generated a rebound
            'total_shot_sequences': 0,  # Total unique shot sequences
            
            # xG tracking
            'xg_against': 0.0,       # Sum of xG on all shots
            
            # Per-game records for recent form
            'game_log': [],
        })
        
        # Track which games we've already processed
        self.processed_games = set()
        self._load_existing()
    
    def _load_existing(self):
        """Load previously computed stats."""
        path = Path('data/goalie_stats.json')
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            
            # Restore processed games
            self.processed_games = set(data.get('processed_games', []))
            
            # Restore goalie stats
            for gid, stats in data.get('goalies', {}).items():
                self.goalie_stats[gid] = stats
                self.goalie_names[gid] = stats.get('name', '')
            
            print(f"📂 Loaded existing stats: {len(self.goalie_stats)} goalies, "
                  f"{len(self.processed_games)} games processed")
    
    def _get_goalie_catches(self, goalie_id: str) -> str:
        """Get goalie's catching hand (L or R)."""
        if goalie_id in self.goalie_cache:
            return self.goalie_cache[goalie_id]
        
        try:
            r = self.api.session.get(
                f'https://api-web.nhle.com/v1/player/{goalie_id}/landing'
            )
            if r.status_code == 200:
                data = r.json()
                catches = data.get('shootsCatches', 'L')
                name = f"{data.get('firstName', {}).get('default', '')} {data.get('lastName', {}).get('default', '')}".strip()
                self.goalie_cache[goalie_id] = catches
                self.goalie_names[goalie_id] = name
                return catches
        except:
            pass
        
        self.goalie_cache[goalie_id] = 'L'  # Default
        return 'L'
    
    def _shot_distance(self, x: float, y: float, defending_right: bool) -> float:
        """Calculate distance from shot to net."""
        goal_x = 89.0 if defending_right else -89.0
        return math.sqrt((x - goal_x) ** 2 + y ** 2)
    
    def _is_high_danger(self, x: float, y: float, defending_right: bool) -> bool:
        """Is this shot from a high-danger area?"""
        return self._shot_distance(x, y, defending_right) <= HIGH_DANGER_DIST
    
    def _is_slot(self, x: float, y: float, defending_right: bool) -> bool:
        """Is this shot from the slot?"""
        goal_x = 89.0 if defending_right else -89.0
        return (abs(x - goal_x) <= (89 - SLOT_X_THRESHOLD) and 
                abs(y) <= SLOT_Y_THRESHOLD)

    def _get_shot_angle(self, x: float, y: float, defending_right: bool) -> float:
        """Calculate the absolute angle of the shot relative to the center of the net.
        0 degrees = straight down the middle.
        90 degrees = straight from the side boards at the goal line.
        """
        goal_x = 89.0 if defending_right else -89.0
        dx = abs(x - goal_x)
        dy = abs(y)
        if dx == 0:
            return 90.0 if dy > 0 else 0.0
        
        # Angle in degrees
        angle = math.degrees(math.atan(dy / dx))
        return angle
    
    def _is_glove_side(self, x: float, y: float, defending_right: bool, 
                       catches: str) -> bool:
        """Determine if shot went to goalie's glove side.
        
        For a goalie facing the shooter:
        - If defending right end (goal at x=89): shooter at lower x
          - Catches L: glove is on goalie's left = positive y from shooter perspective
          - Catches R: glove is on goalie's right = negative y
        """
        if defending_right:
            # Goalie faces left (toward center)
            return (y > 0) == (catches == 'L')
        else:
            # Goalie faces right
            return (y < 0) == (catches == 'L')
    
    def _calc_xg(self, shot_type: str, distance: float, is_hd: bool) -> float:
        """Calculate expected goals for a shot."""
        base = XG_BASE.get(shot_type, 0.060)
        
        # Distance decay
        dist_factor = max(0.2, 1.0 - (distance / 80.0))
        
        # High-danger boost
        hd_factor = 1.5 if is_hd else 1.0
        
        return min(0.5, base * dist_factor * hd_factor)
    
    def _parse_situation(self, sit_code: str, goalie_team_is_home: bool) -> str:
        """Parse situation code to determine EV/PP/PK.
        
        Code format: away_skaters / away_goalies / home_skaters / home_goalies
        e.g. '1551' = away 5 skaters + 1 goalie, home 5 skaters + 1 goalie
        """
        if not sit_code or len(sit_code) != 4:
            return 'ev'
        
        try:
            away_sk = int(sit_code[0])
            home_sk = int(sit_code[2])
        except:
            return 'ev'
        
        if goalie_team_is_home:
            team_sk, opp_sk = home_sk, away_sk
        else:
            team_sk, opp_sk = away_sk, home_sk
        
        if opp_sk > team_sk:
            return 'pp_against'  # Opponent on PP, goalie's team PK
        elif team_sk > opp_sk:
            return 'pk_for'      # Team on PP
        return 'ev'
    
    def process_game(self, game_id: str):
        """Process a single game's PBP for goalie stats."""
        game_id = str(game_id)
        if game_id in self.processed_games:
            return
        
        pbp = self.api.get_play_by_play(game_id)
        if not pbp:
            return
        
        plays = pbp.get('plays', [])
        if not plays:
            return
        
        # Get team IDs
        away_team_id = pbp.get('awayTeam', {}).get('id')
        home_team_id = pbp.get('homeTeam', {}).get('id')
        away_abbrev = pbp.get('awayTeam', {}).get('abbrev', '???')
        home_abbrev = pbp.get('homeTeam', {}).get('abbrev', '???')
        
        # Track goalies seen in this game and their per-game stats
        game_goalies = defaultdict(lambda: {
            'shots': 0, 'goals': 0, 'xg': 0.0, 
            'hd_shots': 0, 'hd_goals': 0,
            'rebound_shots': 0, 'total_sequences': 0,
        })
        
        # Track last shot time per goalie for rebound detection
        last_shot_time = {}
        
        # Process all shot events
        for i, play in enumerate(plays):
            event_type = play.get('typeDescKey', '')
            if event_type not in ('shot-on-goal', 'goal'):
                continue
            
            details = play.get('details', {})
            goalie_id = str(details.get('goalieInNetId', ''))
            if not goalie_id or goalie_id == 'None':
                continue  # Empty net
            
            x = details.get('xCoord', 0) or 0
            y = details.get('yCoord', 0) or 0
            shot_type = details.get('shotType', '')
            sit_code = play.get('situationCode', '')
            time_str = play.get('timeInPeriod', '00:00')
            period = play.get('periodDescriptor', {}).get('number', 1)
            
            # Determine which end the goalie's team defends
            home_defending = play.get('homeTeamDefendingSide', 'right')
            event_team_id = details.get('eventOwnerTeamId')
            
            # If the shooting team is the away team, the shot is toward the home end
            # homeTeamDefendingSide tells us which side home defends
            if event_team_id == away_team_id:
                # Away team shooting → toward home goal
                goalie_team = home_abbrev
                defending_right = (home_defending == 'right')
                goalie_is_home = True
            else:
                # Home team shooting → toward away goal
                goalie_team = away_abbrev
                defending_right = (home_defending != 'right')
                goalie_is_home = False
            
            is_goal = (event_type == 'goal')
            
            # Get goalie's catches hand
            catches = self._get_goalie_catches(goalie_id)
            goalie_name = self.goalie_names.get(goalie_id, f'Unknown ({goalie_id})')
            
            # Initialize goalie if needed
            gs = self.goalie_stats[goalie_id]
            if not gs['name']:
                gs['name'] = goalie_name
                gs['team'] = goalie_team
                gs['catches'] = catches
            
            # Distance and zone calculations
            dist = self._shot_distance(x, y, defending_right)
            is_hd = self._is_high_danger(x, y, defending_right)
            is_slot = self._is_slot(x, y, defending_right)
            is_glove = self._is_glove_side(x, y, defending_right, catches)
            xg = self._calc_xg(shot_type, dist, is_hd)
            situation = self._parse_situation(sit_code, goalie_is_home)
            
            # Rebound detection: shot within REBOUND_WINDOW_SEC of previous shot on same goalie
            try:
                parts = time_str.split(':')
                time_secs = int(parts[0]) * 60 + int(parts[1]) + (period - 1) * 1200
            except:
                time_secs = 0
            
            is_rebound = False
            if goalie_id in last_shot_time:
                prev_time = last_shot_time[goalie_id]
                if 0 < (time_secs - prev_time) <= REBOUND_WINDOW_SEC:
                    is_rebound = True
            last_shot_time[goalie_id] = time_secs
            
            # ─── Accumulate stats ───
            gs['shots_against'] += 1
            gs['xg_against'] += xg
            if is_goal:
                gs['goals_against'] += 1
            else:
                gs['saves'] += 1
            
            # Situation
            if situation == 'ev':
                gs['ev_shots'] += 1
                gs['ev_goals'] += (1 if is_goal else 0)
            elif situation == 'pp_against':
                gs['pp_shots'] += 1
                gs['pp_goals'] += (1 if is_goal else 0)
            elif situation == 'pk_for':
                gs['pk_shots'] += 1
                gs['pk_goals'] += (1 if is_goal else 0)
            
            # Shot type
            type_key = shot_type.replace('-', '')
            for st, prefix in [('wrist', 'wrist'), ('snap', 'snap'), ('slap', 'slap'),
                               ('backhand', 'backhand'), ('tipin', 'tipin'), 
                               ('wraparound', 'wraparound')]:
                if type_key == st:
                    gs[f'{prefix}_shots'] += 1
                    gs[f'{prefix}_goals'] += (1 if is_goal else 0)
            
            # Location
            if is_hd:
                gs['high_danger_shots'] += 1
                gs['high_danger_goals'] += (1 if is_goal else 0)
            if is_slot:
                gs['slot_shots'] += 1
                gs['slot_goals'] += (1 if is_goal else 0)
            else:
                gs['perimeter_shots'] += 1
                gs['perimeter_goals'] += (1 if is_goal else 0)
                
            # Angle
            angle = self._get_shot_angle(x, y, defending_right)
            if angle <= 35.0:  # Center shots (relatively straight on)
                gs['center_angle_shots'] += 1
                gs['center_angle_goals'] += (1 if is_goal else 0)
            else:              # Acute angles (from the sides)
                gs['acute_angle_shots'] += 1
                gs['acute_angle_goals'] += (1 if is_goal else 0)
            
            # Glove/blocker
            if is_glove:
                gs['glove_shots'] += 1
                gs['glove_goals'] += (1 if is_goal else 0)
            else:
                gs['blocker_shots'] += 1
                gs['blocker_goals'] += (1 if is_goal else 0)
                
            # Venue (Home vs Away performance)
            if goalie_is_home:
                gs['home_shots'] += 1
                gs['home_goals'] += (1 if is_goal else 0)
            else:
                gs['away_shots'] += 1
                gs['away_goals'] += (1 if is_goal else 0)
                
            # Head-to-Head
            opponent = away_abbrev if goalie_is_home else home_abbrev
            if opponent not in gs['opponent_stats']:
                gs['opponent_stats'][opponent] = {'shots': 0, 'goals': 0}
            gs['opponent_stats'][opponent]['shots'] += 1
            gs['opponent_stats'][opponent]['goals'] += (1 if is_goal else 0)
            
            # Rebounds
            if is_rebound:
                gs['rebound_shots'] += 1
            gs['total_shot_sequences'] += 1
            
            # Per-game tracking
            game_goalies[goalie_id]['shots'] += 1
            game_goalies[goalie_id]['goals'] += (1 if is_goal else 0)
            game_goalies[goalie_id]['xg'] += xg
            game_goalies[goalie_id]['hd_shots'] += (1 if is_hd else 0)
            game_goalies[goalie_id]['hd_goals'] += (1 if is_goal and is_hd else 0)
            if is_rebound:
                game_goalies[goalie_id]['rebound_shots'] += 1
            game_goalies[goalie_id]['total_sequences'] += 1
        
        # Determine game result + add to game logs
        away_score = 0
        home_score = 0
        for play in plays:
            if play.get('typeDescKey') == 'goal':
                d = play.get('details', {})
                if d.get('eventOwnerTeamId') == away_team_id:
                    away_score = d.get('awayScore', away_score)
                else:
                    home_score = d.get('homeScore', home_score)
        
        for gid, gstats in game_goalies.items():
            if gstats['shots'] == 0:
                continue
            
            gs = self.goalie_stats[gid]
            gs['games'] += 1
            
            # Determine W/L/OTL
            is_home = (gs['team'] == home_abbrev)
            team_score = home_score if is_home else away_score
            opp_score = away_score if is_home else home_score
            
            if team_score > opp_score:
                gs['wins'] += 1
                decision = 'W'
            else:
                gs['losses'] += 1
                decision = 'L'
            
            sv_pct = (gstats['shots'] - gstats['goals']) / gstats['shots'] if gstats['shots'] > 0 else 0
            gsax = gstats['xg'] - gstats['goals']
            
            gs['game_log'].append({
                'game_id': game_id,
                'date': pbp.get('gameDate', ''),
                'opponent': home_abbrev if not is_home else away_abbrev,
                'shots': gstats['shots'],
                'goals': gstats['goals'],
                'saves': gstats['shots'] - gstats['goals'],
                'sv_pct': round(sv_pct, 3),
                'xg': round(gstats['xg'], 2),
                'gsax': round(gsax, 2),
                'hd_shots': gstats['hd_shots'],
                'hd_goals': gstats['hd_goals'],
                'rebound_rate': round(gstats['rebound_shots'] / max(1, gstats['total_sequences']), 3),
                'decision': decision,
            })
            
            # Keep only last 30 games in log
            if len(gs['game_log']) > 30:
                gs['game_log'] = gs['game_log'][-30:]
        
        self.processed_games.add(game_id)
    
    def save(self):
        """Save goalie stats to JSON."""
        output = {
            'updated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'processed_games': list(self.processed_games),
            'total_goalies': len(self.goalie_stats),
            'goalies': {},
        }
        
        for gid, gs in self.goalie_stats.items():
            if gs['games'] == 0:
                continue
            
            # Calculate derived metrics
            sa = gs['shots_against']
            ga = gs['goals_against']
            
            derived = {
                'sv_pct': round((sa - ga) / sa, 4) if sa > 0 else 0,
                'gaa': round(ga / max(1, gs['games']), 2),
                'gsax_total': round(gs['xg_against'] - ga, 2),
                'gsax_per_game': round((gs['xg_against'] - ga) / max(1, gs['games']), 3),
                
                # EV splits
                'ev_sv_pct': round((gs['ev_shots'] - gs['ev_goals']) / gs['ev_shots'], 4) if gs['ev_shots'] > 0 else 0,
                'pp_sv_pct': round((gs['pp_shots'] - gs['pp_goals']) / gs['pp_shots'], 4) if gs['pp_shots'] > 0 else 0,
                
                # High-danger & Angles
                'hd_sv_pct': round((gs['high_danger_shots'] - gs['high_danger_goals']) / gs['high_danger_shots'], 4) if gs['high_danger_shots'] > 0 else 0,
                'slot_sv_pct': round((gs['slot_shots'] - gs['slot_goals']) / gs['slot_shots'], 4) if gs['slot_shots'] > 0 else 0,
                'center_angle_sv_pct': round((gs['center_angle_shots'] - gs['center_angle_goals']) / gs['center_angle_shots'], 4) if gs['center_angle_shots'] > 0 else 0,
                'acute_angle_sv_pct': round((gs['acute_angle_shots'] - gs['acute_angle_goals']) / gs['acute_angle_shots'], 4) if gs['acute_angle_shots'] > 0 else 0,
                
                # Shot Types
                'slap_sv_pct': round((gs['slap_shots'] - gs['slap_goals']) / gs['slap_shots'], 4) if gs['slap_shots'] > 0 else 0,
                'wrist_sv_pct': round((gs['wrist_shots'] - gs['wrist_goals']) / gs['wrist_shots'], 4) if gs['wrist_shots'] > 0 else 0,
                'backhand_sv_pct': round((gs['backhand_shots'] - gs['backhand_goals']) / gs['backhand_shots'], 4) if gs['backhand_shots'] > 0 else 0,
                
                # Venue
                'home_sv_pct': round((gs['home_shots'] - gs['home_goals']) / gs['home_shots'], 4) if gs['home_shots'] > 0 else 0,
                'away_sv_pct': round((gs['away_shots'] - gs['away_goals']) / gs['away_shots'], 4) if gs['away_shots'] > 0 else 0,
                
                # Glove/Blocker
                'glove_sv_pct': round((gs['glove_shots'] - gs['glove_goals']) / gs['glove_shots'], 4) if gs['glove_shots'] > 0 else 0,
                'blocker_sv_pct': round((gs['blocker_shots'] - gs['blocker_goals']) / gs['blocker_shots'], 4) if gs['blocker_shots'] > 0 else 0,
                
                # Rebound control
                'rebound_rate': round(gs['rebound_shots'] / max(1, gs['total_shot_sequences']), 4),
                
                # Recent form (last 5 games)
                'recent_5_sv_pct': 0, 'recent_5_gsax': 0,
                'recent_10_sv_pct': 0, 'recent_10_gsax': 0,
            }
            
            # Recent form
            log = gs.get('game_log', [])
            for n, label in [(5, 'recent_5'), (10, 'recent_10')]:
                recent = log[-n:] if len(log) >= n else log
                if recent:
                    total_shots = sum(g['shots'] for g in recent)
                    total_goals = sum(g['goals'] for g in recent)
                    total_gsax = sum(g['gsax'] for g in recent)
                    derived[f'{label}_sv_pct'] = round((total_shots - total_goals) / total_shots, 4) if total_shots > 0 else 0
                    derived[f'{label}_gsax'] = round(total_gsax, 2)
            
            output['goalies'][gid] = {**gs, **derived}
        
        Path('data').mkdir(exist_ok=True)
        with open('data/goalie_stats.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"💾 Saved {len(output['goalies'])} goalies to data/goalie_stats.json")
    
    def run_backfill(self, game_ids: List[str], batch_size: int = 10):
        """Process a batch of games with rate limiting."""
        total = len(game_ids)
        new_games = [gid for gid in game_ids if str(gid) not in self.processed_games]
        print(f"\n🏒 Backfilling goalie stats: {len(new_games)} new games "
              f"(of {total} total, {len(self.processed_games)} already done)")
        
        for i, gid in enumerate(new_games):
            try:
                self.process_game(gid)
                if (i + 1) % batch_size == 0:
                    self.save()  # Checkpoint
                    pct = (i + 1) / len(new_games) * 100
                    print(f"  ✅ {i+1}/{len(new_games)} ({pct:.0f}%) — "
                          f"{len(self.goalie_stats)} goalies tracked")
                    time.sleep(0.5)  # Rate limit
            except Exception as e:
                print(f"  ⚠️  Error on game {gid}: {e}")
                continue
        
        self.save()
        
        # Print summary
        self._print_summary()
    def _print_summary(self):
        """Print top goalies summary."""
        print("\n📊 TOP GOALIES (min 10 GP)")
        print("=" * 80)
        
        qualified = [(gid, gs) for gid, gs in self.goalie_stats.items() 
                     if gs['games'] >= 10]
        
        # Sort by GSAX per game
        qualified.sort(key=lambda x: (x[1].get('xg_against', 0) - x[1]['goals_against']) / max(1, x[1]['games']), reverse=True)
        
        print(f"{'Goalie':<22} {'GP':>3} {'SV%':>6} {'GAA':>5} {'GSAX':>6} "
              f"{'HDSV%':>6} {'GlvSV%':>7} {'BlkSV%':>7} {'REB%':>5}")
        print("-" * 80)
        
        for gid, gs in qualified[:15]:
            sa = gs['shots_against']
            ga = gs['goals_against']
            sv_pct = (sa - ga) / sa if sa > 0 else 0
            gaa = ga / max(1, gs['games'])
            gsax = gs.get('xg_against', 0) - ga
            hd_sv = (gs['high_danger_shots'] - gs['high_danger_goals']) / gs['high_danger_shots'] if gs['high_danger_shots'] > 0 else 0
            glv_sv = (gs['glove_shots'] - gs['glove_goals']) / gs['glove_shots'] if gs['glove_shots'] > 0 else 0
            blk_sv = (gs['blocker_shots'] - gs['blocker_goals']) / gs['blocker_shots'] if gs['blocker_shots'] > 0 else 0
            reb = gs['rebound_shots'] / max(1, gs['total_shot_sequences'])
            
            print(f"{gs['name']:<22} {gs['games']:>3} {sv_pct:>6.3f} {gaa:>5.2f} "
                  f"{gsax:>+6.1f} {hd_sv:>6.3f} {glv_sv:>7.3f} {blk_sv:>7.3f} {reb:>5.3f}")

    def run_refresher(self):
        """Main entry point to refresh goalie stats from prediction history."""
        # Load game IDs from prediction history
        for p in [Path('data/win_probability_predictions_v2.json'),
                  Path('win_probability_predictions_v2.json')]:
            if p.exists():
                with open(p) as f:
                    pred_data = json.load(f)
                game_ids = [str(pr.get('game_id')) for pr in pred_data.get('predictions', [])
                           if pr.get('actual_winner')]
                
                print(f"📋 Found {len(game_ids)} completed games to process")
                self.run_backfill(game_ids)
                return
        
        print("❌ No prediction history found")

if __name__ == "__main__":
    builder = GoalieStatsBuilder()
    builder.run_refresher()
