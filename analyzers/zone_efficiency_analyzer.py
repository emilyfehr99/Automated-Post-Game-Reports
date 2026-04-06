#!/usr/bin/env python3
"""
Zone Transition Efficiency Analyzer
Focuses on two key metrics:
1. Entries Leading to Shots - Offensive zone entry efficiency
2. Exits Leading to Entries - Breakout success rate
"""

from nhl_api_client import NHLAPIClient
from typing import Dict, List
from datetime import datetime
import json


class ZoneTransitionEfficiencyAnalyzer:
    """Analyze zone transition efficiency with available data"""
    
    def __init__(self):
        self.api = NHLAPIClient()
    
    def time_to_seconds(self, time_str: str) -> int:
        """Convert MM:SS to total seconds"""
        if not time_str:
            return 0
        try:
            parts = time_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])
        except:
            return 0
    
    def analyze_game(self, game_id: str) -> Dict:
        """Analyze zone transition efficiency"""
        
        pbp = self.api.get_play_by_play(game_id)
        if not pbp:
            return {}
        
        plays = pbp.get('plays', [])
        
        # Get team IDs
        away_team_id, home_team_id = self._get_team_ids(plays)
        
        # Initialize tracking
        stats = {
            away_team_id: {
                'entries_to_shots': [],
                'exits_to_entries': [],
                'total_entries': 0,
                'total_exits': 0,
                'total_shots': 0
            },
            home_team_id: {
                'entries_to_shots': [],
                'exits_to_entries': [],
                'total_entries': 0,
                'total_exits': 0,
                'total_shots': 0
            }
        }
        
        # Track recent entries and exits for each team
        recent_entries = {away_team_id: [], home_team_id: []}
        recent_exits = {away_team_id: [], home_team_id: []}
        matched_entries = {away_team_id: set(), home_team_id: set()}  # Track which entries already matched to shots
        
        prev_play = None
        
        for play in plays:
            details = play.get('details', {})
            zone = details.get('zoneCode')
            team = details.get('eventOwnerTeamId')
            event = play.get('typeDescKey')
            period = play.get('periodDescriptor', {}).get('number')
            time_in_period = play.get('timeInPeriod')
            
            if not team or not zone:
                prev_play = play
                continue
            
            # NHL API zoneCode is relative to the event owner:
            # 'D' = Defensive, 'N' = Neutral, 'O' = Offensive
            team_defensive_zone = 'D'
            team_offensive_zone = 'O'
            
            # Detect EXITS (leaving defensive zone)
            if prev_play:
                prev_zone = prev_play.get('details', {}).get('zoneCode')
                prev_team = prev_play.get('details', {}).get('eventOwnerTeamId')
                
                if (prev_zone == team_defensive_zone and 
                    zone in ['N', team_offensive_zone] and 
                    team == prev_team):
                    
                    exit_event = {
                        'period': period,
                        'time': time_in_period,
                        'time_seconds': self.time_to_seconds(time_in_period),
                        'event': event
                    }
                    recent_exits[team].append(exit_event)
                    stats[team]['total_exits'] += 1
                    
                    # Keep only last 5 exits
                    if len(recent_exits[team]) > 5:
                        recent_exits[team].pop(0)
                
                # Detect ENTRIES (entering offensive zone)
                if (prev_zone in [team_defensive_zone, 'N'] and 
                    zone == team_offensive_zone and 
                    team == prev_team):
                    
                    entry_event = {
                        'period': period,
                        'time': time_in_period,
                        'time_seconds': self.time_to_seconds(time_in_period),
                        'event': event,
                        'id': f"{period}_{time_in_period}"  # Unique ID for tracking
                    }
                    recent_entries[team].append(entry_event)
                    stats[team]['total_entries'] += 1
                    
                    # Check if this entry followed an exit (successful breakout)
                    # D→O transitions are simultaneous exit+entry (instant breakout)
                    if prev_zone == team_defensive_zone:
                        # Direct D→O = successful breakout in one move
                        stats[team]['exits_to_entries'].append({
                            'exit_time': time_in_period,
                            'entry_time': time_in_period,
                            'period': period,
                            'time_diff': 0,
                            'type': 'direct'
                        })
                    else:
                        # N→O entry, check for recent exit (within 15 seconds)
                        for exit_ev in recent_exits[team]:
                            if (exit_ev['period'] == period and
                                0 < (entry_event['time_seconds'] - exit_ev['time_seconds']) <= 15):
                                stats[team]['exits_to_entries'].append({
                                    'exit_time': exit_ev['time'],
                                    'entry_time': entry_event['time'],
                                    'period': period,
                                    'time_diff': entry_event['time_seconds'] - exit_ev['time_seconds'],
                                    'type': 'sequence'
                                })
                                break
                    
                    # Keep only last 5 entries
                    if len(recent_entries[team]) > 5:
                        recent_entries[team].pop(0)
            
            # Detect SHOTS following entries
            # Note: for blocked-shot, the eventOwnerTeamId is the team that BLOCKED the shot.
            # We want to attribute the shot to the shooter (the other team).
            shot_team = team
            if event == 'blocked-shot':
                shot_team = home_team_id if team == away_team_id else away_team_id
                
            if event in ['shot-on-goal', 'missed-shot', 'blocked-shot', 'goal']:
                stats[shot_team]['total_shots'] += 1
                
                # Find the MOST RECENT entry (within 15 seconds) that hasn't been matched yet
                matched_entry = None
                for entry_ev in reversed(recent_entries[shot_team]):  # Check most recent first
                    entry_id = entry_ev['id']
                    if (entry_id not in matched_entries[shot_team] and
                        entry_ev['period'] == period and
                        0 <= (self.time_to_seconds(time_in_period) - entry_ev['time_seconds']) <= 15):
                        matched_entry = entry_ev
                        matched_entries[shot_team].add(entry_id)  # Mark as matched
                        break
                
                if matched_entry:
                    stats[shot_team]['entries_to_shots'].append({
                        'entry_time': matched_entry['time'],
                        'shot_time': time_in_period,
                        'shot_type': event,
                        'period': period,
                        'time_diff': self.time_to_seconds(time_in_period) - matched_entry['time_seconds']
                    })
            
            prev_play = play
        
        return {
            'game_id': game_id,
            'away_team_id': away_team_id,
            'home_team_id': home_team_id,
            'stats': stats
        }
    
    def analyze_by_period(self, game_id: str) -> Dict:
        """Analyze zone efficiency by period for report integration
        
        Returns:
            Dict with period-by-period stats for both teams
        """
        pbp = self.api.get_play_by_play(game_id)
        if not pbp:
            return {}
        
        plays = pbp.get('plays', [])
        away_team_id, home_team_id = self._get_team_ids(plays)
        
        # Initialize period stats
        period_stats = {
            away_team_id: {},
            home_team_id: {}
        }
        
        # Process each period separately
        max_period = max([p.get('periodDescriptor', {}).get('number', 1) for p in plays if p.get('periodDescriptor')])
        
        for period_num in range(1, max_period + 1):
            period_plays = [p for p in plays if p.get('periodDescriptor', {}).get('number') == period_num]
            
            # Track for this period
            period_entries = {away_team_id: 0, home_team_id: 0}
            period_exits = {away_team_id: 0, home_team_id: 0}
            period_entries_to_shots = {away_team_id: 0, home_team_id: 0}
            period_exits_to_entries = {away_team_id: 0, home_team_id: 0}
            
            recent_entries = {away_team_id: [], home_team_id: []}
            recent_exits = {away_team_id: [], home_team_id: []}
            matched_entries = {away_team_id: set(), home_team_id: set()}
            
            prev_play = None
            
            for play in period_plays:
                details = play.get('details', {})
                zone = details.get('zoneCode')
                team = details.get('eventOwnerTeamId')
                event = play.get('typeDescKey')
                time_in_period = play.get('timeInPeriod')
                
                if not team or not zone:
                    prev_play = play
                    continue
                
                team_defensive_zone = 'D'
                team_offensive_zone = 'O'
                
                if prev_play:
                    prev_zone = prev_play.get('details', {}).get('zoneCode')
                    prev_team = prev_play.get('details', {}).get('eventOwnerTeamId')
                    
                    # Detect exits
                    if (prev_zone == team_defensive_zone and 
                        zone in ['N', team_offensive_zone] and 
                        team == prev_team):
                        
                        exit_event = {
                            'time': time_in_period,
                            'time_seconds': self.time_to_seconds(time_in_period)
                        }
                        recent_exits[team].append(exit_event)
                        period_exits[team] += 1
                    
                    # Detect entries
                    if (prev_zone in [team_defensive_zone, 'N'] and 
                        zone == team_offensive_zone and 
                        team == prev_team):
                        
                        entry_event = {
                            'time': time_in_period,
                            'time_seconds': self.time_to_seconds(time_in_period),
                            'id': f"{period_num}_{time_in_period}"
                        }
                        recent_entries[team].append(entry_event)
                        period_entries[team] += 1
                        
                        # Check for successful breakout
                        if prev_zone == team_defensive_zone:
                            period_exits_to_entries[team] += 1
                        else:
                            for exit_ev in recent_exits[team]:
                                if 0 < (entry_event['time_seconds'] - exit_ev['time_seconds']) <= 15:
                                    period_exits_to_entries[team] += 1
                                    break
                
                # Detect shots following entries
                shot_team = team
                if event == 'blocked-shot':
                    shot_team = away_team_id if team == home_team_id else home_team_id

                if event in ['shot-on-goal', 'missed-shot', 'blocked-shot', 'goal']:
                    matched_entry = None
                    for entry_ev in reversed(recent_entries[shot_team]):
                        entry_id = entry_ev['id']
                        if (entry_id not in matched_entries[shot_team] and
                            0 <= (self.time_to_seconds(time_in_period) - entry_ev['time_seconds']) <= 15):
                            matched_entry = entry_ev
                            matched_entries[shot_team].add(entry_id)
                            break
                    
                    if matched_entry:
                        period_entries_to_shots[shot_team] += 1
                
                prev_play = play
            
            # Calculate percentages for this period
            for team_id in [away_team_id, home_team_id]:
                entry_eff = (period_entries_to_shots[team_id] / period_entries[team_id] * 100) if period_entries[team_id] > 0 else 0
                breakout_success = (period_exits_to_entries[team_id] / period_exits[team_id] * 100) if period_exits[team_id] > 0 else 0
                
                period_stats[team_id][period_num] = {
                    'entries': period_entries[team_id],
                    'exits': period_exits[team_id],
                    'entries_to_shots': period_entries_to_shots[team_id],
                    'exits_to_entries': period_exits_to_entries[team_id],
                    'entry_efficiency': round(entry_eff, 1),
                    'breakout_success': round(breakout_success, 1)
                }
        
        return {
            'game_id': game_id,
            'away_team_id': away_team_id,
            'home_team_id': home_team_id,
            'period_stats': period_stats
        }
    
    def _get_team_ids(self, plays: List[Dict]) -> tuple:
        """Extract team IDs"""
        away_id = None
        home_id = None
        
        for play in plays:
            team = play.get('details', {}).get('eventOwnerTeamId')
            if team:
                if away_id is None:
                    away_id = team
                elif team != away_id:
                    home_id = team
                    break
        
        return away_id, home_id
    
    def generate_report(self, game_id: str, output_path: str = None):
        """Generate focused efficiency report"""
        result = self.analyze_game(game_id)
        
        if not result:
            return "No data available", None
        
        away_id = result['away_team_id']
        home_id = result['home_team_id']
        away_stats = result['stats'][away_id]
        home_stats = result['stats'][home_id]
        
        # Save JSON
        if output_path is None:
            output_path = f"/Users/emilyfehr8/Desktop/zone_efficiency_{game_id}.json"
        
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Generate summary
        summary = []
        summary.append("═" * 70)
        summary.append("ZONE TRANSITION EFFICIENCY ANALYSIS")
        summary.append(f"Game: {game_id} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        summary.append("═" * 70)
        summary.append("")
        summary.append("📊 KEY METRICS:")
        summary.append("  1. Entries → Shots: Offensive zone entry efficiency")
        summary.append("  2. Exits → Entries: Breakout success rate")
        summary.append("")
        summary.append("─" * 70)
        summary.append("")
        
        # Away team
        summary.append(f"AWAY TEAM (ID: {away_id}):")
        summary.append(f"  Total Entries: {away_stats['total_entries']}")
        summary.append(f"  Entries → Shots: {len(away_stats['entries_to_shots'])}")
        if away_stats['total_entries'] > 0:
            pct = (len(away_stats['entries_to_shots']) / away_stats['total_entries']) * 100
            summary.append(f"  Entry Efficiency: {pct:.1f}%")
        summary.append("")
        summary.append(f"  Total Exits: {away_stats['total_exits']}")
        summary.append(f"  Exits → Entries: {len(away_stats['exits_to_entries'])}")
        if away_stats['total_exits'] > 0:
            pct = (len(away_stats['exits_to_entries']) / away_stats['total_exits']) * 100
            summary.append(f"  Breakout Success: {pct:.1f}%")
        summary.append("")
        
        # Home team
        summary.append(f"HOME TEAM (ID: {home_id}):")
        summary.append(f"  Total Entries: {home_stats['total_entries']}")
        summary.append(f"  Entries → Shots: {len(home_stats['entries_to_shots'])}")
        if home_stats['total_entries'] > 0:
            pct = (len(home_stats['entries_to_shots']) / home_stats['total_entries']) * 100
            summary.append(f"  Entry Efficiency: {pct:.1f}%")
        summary.append("")
        summary.append(f"  Total Exits: {home_stats['total_exits']}")
        summary.append(f"  Exits → Entries: {len(home_stats['exits_to_entries'])}")
        if home_stats['total_exits'] > 0:
            pct = (len(home_stats['exits_to_entries']) / home_stats['total_exits']) * 100
            summary.append(f"  Breakout Success: {pct:.1f}%")
        summary.append("")
        summary.append("═" * 70)
        
        return "\n".join(summary), output_path


if __name__ == "__main__":
    import sys
    
    game_id = sys.argv[1] if len(sys.argv) > 1 else '2025020497'
    
    analyzer = ZoneTransitionEfficiencyAnalyzer()
    
    print(f"\nAnalyzing zone transition efficiency for game {game_id}...\n")
    
    summary, path = analyzer.generate_report(game_id)
    print(summary)
    print(f"\n✅ Report saved to: {path}")
