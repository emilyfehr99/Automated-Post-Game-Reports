#!/usr/bin/env python3
"""
Per-game goalie analytics for postgame reports.

GSAx and context save rates come from real NHL PBP + ImprovedXGModel.
Sv/SA prefers official boxscore. Missing coordinates are never invented.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Optional

try:
    from utils.nhl_api_client import NHLAPIClient
except ImportError:
    from nhl_api_client import NHLAPIClient

try:
    from models.improved_xg_model import ImprovedXGModel
except ImportError:
    try:
        from improved_xg_model import ImprovedXGModel
    except ImportError:
        ImprovedXGModel = None


def _time_to_seconds(time_str: str) -> float:
    try:
        if time_str and ':' in str(time_str):
            parts = str(time_str).split(':')
            return int(parts[0]) * 60 + int(parts[1])
        return 0.0
    except (ValueError, IndexError, TypeError):
        return 0.0


class GoalieAnalyticsAnalyzer:
    """Analyze goalie performance for a single NHL game."""

    def __init__(self, game_id, game_data: Optional[dict] = None):
        self.game_id = game_id
        self.game_data = game_data
        self.api = NHLAPIClient()
        self.xg_model = ImprovedXGModel() if ImprovedXGModel else None

    def _ensure_game_data(self) -> Optional[dict]:
        if isinstance(self.game_data, dict) and (
            self.game_data.get('play_by_play') or self.game_data.get('boxscore')
        ):
            return self.game_data
        data = self.api.get_comprehensive_game_data(self.game_id)
        self.game_data = data
        return data

    def _shot_xg(self, details: dict, event_type: str, play: dict, previous_events: list) -> float:
        if not self.xg_model:
            return 0.0
        if details.get('xCoord') is None or details.get('yCoord') is None:
            return 0.0
        sit = play.get('situationCode') or '1551'
        try:
            strength = f"{int(sit[1])}v{int(sit[2])}" if len(sit) >= 4 else '5v5'
        except (ValueError, IndexError, TypeError):
            strength = '5v5'
        shot_data = {
            'x_coord': details.get('xCoord', 0),
            'y_coord': details.get('yCoord', 0),
            'shot_type': (details.get('shotType') or 'wrist').lower(),
            'event_type': event_type,
            'time_in_period': play.get('timeInPeriod', '00:00'),
            'period': (play.get('periodDescriptor') or {}).get('number', 1),
            'strength_state': strength,
            'score_differential': 0,
            'team_id': details.get('eventOwnerTeamId', 0),
        }
        try:
            return float(self.xg_model.calculate_xg(shot_data, previous_events) or 0.0)
        except Exception:
            return 0.0

    def _classify_context(self, plays: list, idx: int, details: dict, shooting_team_id) -> dict:
        flags = {'royal_road': False, 'carry_entry': False, 'pass_entry': False}
        x = details.get('xCoord')
        y = details.get('yCoord')
        if x is None or y is None:
            return flags

        zone = details.get('zoneCode', '')
        current_time = _time_to_seconds(plays[idx].get('timeInPeriod', '00:00'))
        period = (plays[idx].get('periodDescriptor') or {}).get('number')

        for j in range(idx - 1, max(-1, idx - 20), -1):
            prev = plays[j]
            if (prev.get('periodDescriptor') or {}).get('number') != period:
                break
            prev_details = prev.get('details') or {}
            prev_team = prev_details.get('eventOwnerTeamId')
            prev_time = _time_to_seconds(prev.get('timeInPeriod', '00:00'))
            if current_time - prev_time > 5:
                break
            if prev_team != shooting_team_id:
                continue

            prev_x = prev_details.get('xCoord')
            prev_y = prev_details.get('yCoord')
            prev_zone = prev_details.get('zoneCode', '')
            prev_type = prev.get('typeDescKey', '')
            if prev_x is None or prev_y is None:
                continue
            try:
                dy = abs(float(y) - float(prev_y))
                dx = abs(float(x) - float(prev_x))
            except (TypeError, ValueError):
                continue

            if zone == 'O' and dy >= 18.0:
                flags['royal_road'] = True
                flags['pass_entry'] = True
            if prev_type == 'pass' and dy >= 12.0:
                flags['pass_entry'] = True
                if dy >= 18.0:
                    flags['royal_road'] = True
            if zone == 'O' and prev_zone in ('N', 'D') and dx >= 20.0 and dy < 22.0:
                flags['carry_entry'] = True

        return flags

    def _boxscore_goalies(self, game_data: dict) -> Dict[int, dict]:
        out = {}
        box = game_data.get('boxscore') or {}
        pbg = box.get('playerByGameStats') or {}
        for side in ('awayTeam', 'homeTeam'):
            for g in (pbg.get(side) or {}).get('goalies') or []:
                gid = g.get('playerId')
                if not gid:
                    continue
                sa = int(g.get('shotsAgainst') or 0)
                ga = int(g.get('goalsAgainst') or 0)
                out[int(gid)] = {
                    'shotsAgainst': sa,
                    'goalsAgainst': ga,
                    'saves': int(g.get('saves') or max(0, sa - ga)),
                    'toi': g.get('toi') or '',
                }
        return out

    def analyze_goalies(self) -> Dict[int, dict]:
        game_data = self._ensure_game_data()
        if not game_data:
            return {}

        plays = ((game_data.get('play_by_play') or {}).get('plays')) or []
        box_goalies = self._boxscore_goalies(game_data)

        stats = defaultdict(lambda: {
            'pbp_shots': 0,
            'pbp_goals': 0,
            'modeled_shots': 0,
            'modeled_goals': 0,
            'xG': 0.0,
            'RoyalRoad_Shots': 0,
            'RoyalRoad_Goals': 0,
            'CarryEntry_Shots': 0,
            'CarryEntry_Goals': 0,
            'PassEntry_Shots': 0,
            'PassEntry_Goals': 0,
        })

        for i, play in enumerate(plays):
            event_type = play.get('typeDescKey', '')
            if event_type not in ('shot-on-goal', 'goal'):
                continue
            details = play.get('details') or {}
            goalie_id = details.get('goalieInNetId')
            if not goalie_id:
                continue
            goalie_id = int(goalie_id)
            is_goal = event_type == 'goal'
            s = stats[goalie_id]
            s['pbp_shots'] += 1
            if is_goal:
                s['pbp_goals'] += 1

            prev = plays[max(0, i - 10):i]
            has_coords = details.get('xCoord') is not None and details.get('yCoord') is not None
            if has_coords:
                xg = self._shot_xg(details, event_type, play, prev)
                s['xG'] += xg
                s['modeled_shots'] += 1
                if is_goal:
                    s['modeled_goals'] += 1

                ctx = self._classify_context(plays, i, details, details.get('eventOwnerTeamId'))
                if ctx['royal_road']:
                    s['RoyalRoad_Shots'] += 1
                    if is_goal:
                        s['RoyalRoad_Goals'] += 1
                if ctx['carry_entry']:
                    s['CarryEntry_Shots'] += 1
                    if is_goal:
                        s['CarryEntry_Goals'] += 1
                if ctx['pass_entry']:
                    s['PassEntry_Shots'] += 1
                    if is_goal:
                        s['PassEntry_Goals'] += 1

        result = {}
        goalie_ids = set(stats.keys()) | set(box_goalies.keys())
        for gid in goalie_ids:
            s = stats[gid]
            box = box_goalies.get(gid) or {}
            # Official Sv/SA from boxscore when available
            if box.get('shotsAgainst', 0) > 0:
                shots = box['shotsAgainst']
                goals = box['goalsAgainst']
            elif s['pbp_shots'] > 0:
                shots = s['pbp_shots']
                goals = s['pbp_goals']
            else:
                continue  # DNP / no shots — omit from results

            # GSAx only from located PBP shots (xG - goals on those same events)
            if s['modeled_shots'] > 0:
                gsax = round(s['xG'] - s['modeled_goals'], 3)
            else:
                gsax = None

            def _svpct(n_shots, n_goals):
                return ((n_shots - n_goals) / n_shots) if n_shots > 0 else 0.0

            result[gid] = {
                'shots': shots,
                'goals': goals,
                'xG': float(s['xG'] or 0.0),
                'GSAx': gsax,
                'RoyalRoad_Shots': s['RoyalRoad_Shots'],
                'RoyalRoad_Goals': s['RoyalRoad_Goals'],
                'RoyalRoad_SvPct': _svpct(s['RoyalRoad_Shots'], s['RoyalRoad_Goals']),
                'CarryEntry_Shots': s['CarryEntry_Shots'],
                'CarryEntry_Goals': s['CarryEntry_Goals'],
                'CarryEntry_SvPct': _svpct(s['CarryEntry_Shots'], s['CarryEntry_Goals']),
                'PassEntry_Shots': s['PassEntry_Shots'],
                'PassEntry_Goals': s['PassEntry_Goals'],
                'PassEntry_SvPct': _svpct(s['PassEntry_Shots'], s['PassEntry_Goals']),
            }

        return result
