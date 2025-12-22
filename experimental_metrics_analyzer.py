"""
Experimental NHL Metrics Analyzer
Calculates new, advanced metrics for verification.
"""

import json
from collections import defaultdict
from typing import Dict, List, Optional

class ExperimentalMetricsAnalyzer:
    def __init__(self, play_by_play_data: dict, sprite_data: Optional[dict] = None):
        self.plays = play_by_play_data.get('plays', [])
        self.sprite_data = sprite_data
        self._sprite_cache = {} # Cache to avoid redundant requests
        import time
        self._last_request_time = 0
        
    def calculate_experimental_report(self, away_team_id: int, home_team_id: int) -> dict:
        """Generate a report containing only experimental metrics"""
        return {
            'away_team': self._calculate_team_experimental(away_team_id),
            'home_team': self._calculate_team_experimental(home_team_id),
            'game_id': self._get_game_id()
        }
        
    def _calculate_team_experimental(self, team_id: int) -> dict:
        """Calculate metrics for a specific team"""
        metrics = {
            'rebounds': self._calculate_rebounds(team_id),
            'cycle_shots': self._calculate_cycle_shots(team_id),
            'forecheck_turnovers': self._calculate_forecheck_turnovers(team_id),
            'nz_success_rate': self._calculate_nz_success_rate(team_id),
            'east_west_passing_volume': self._calculate_passing_depth(team_id),
            'possession_efficiency': self._calculate_possession_efficiency(team_id)
        }
        
        # Always calculate spatial metrics
        metrics.update(self._calculate_spatial_metrics(team_id))
        metrics['entry_gap'] = self._calculate_entry_gap(team_id)
            
        return metrics

    def _calculate_rebounds(self, team_id: int) -> int:
        """Count shots taken as rebounds (within 3s of previous shot, no stoppage)"""
        rebound_count = 0
        last_shot_time = -999
        last_period = -1
        
        for play in self.plays:
            event_type = play.get('typeDescKey', '')
            details = play.get('details', {})
            event_team = details.get('eventOwnerTeamId')
            period = play.get('periodDescriptor', {}).get('number', 1)
            time_str = play.get('timeInPeriod', '00:00')
            current_time = self._time_to_seconds(time_str)
            
            # Reset on stoppage/faceoff (not a rebound if play stopped)
            if event_type in ['stoppage', 'faceoff', 'period-start']:
                last_shot_time = -999
                continue
                
            if event_type in ['shot-on-goal', 'missed-shot', 'blocked-shot', 'goal'] and event_team == team_id:
                if period == last_period and (current_time - last_shot_time) <= 3 and last_shot_time != -999:
                    rebound_count += 1
                
                # Update last shot (any team's shot could lead to a rebound for team_id if possession changes, 
                # but usually we mean team_id's own follow-up)
                # Here we track team_id's own follow-ups to stay conservative.
                last_shot_time = current_time
                last_period = period
                
        return rebound_count

    def _calculate_cycle_shots(self, team_id: int) -> int:
        """Count shots occurring after >10s of continuous OZ possession"""
        cycle_shots = 0
        oz_entry_time = None
        current_oz_team = None
        
        for play in self.plays:
            details = play.get('details', {})
            zone = details.get('zoneCode', '')
            event_team = details.get('eventOwnerTeamId')
            event_type = play.get('typeDescKey', '')
            time_str = play.get('timeInPeriod', '00:00')
            current_time = self._time_to_seconds(time_str)
            
            # Track OZ possession
            if zone == 'O':
                if current_oz_team != event_team:
                    current_oz_team = event_team
                    oz_entry_time = current_time
                
                # Check for shot during cycle
                if event_type in ['shot-on-goal', 'missed-shot', 'blocked-shot', 'goal'] and event_team == team_id:
                    if oz_entry_time and (current_time - oz_entry_time) >= 10:
                        cycle_shots += 1
            else:
                # Puck left 'O' zone or neutral zone event
                oz_entry_time = None
                current_oz_team = None
                
            # Possession change in O-zone (e.g. giveaway/takeaway)
            if event_type in ['giveaway', 'takeaway'] and zone == 'O':
                # If team_id loses puck, cycle resets
                if event_type == 'giveaway' and event_team == team_id:
                    oz_entry_time = None
                elif event_type == 'takeaway' and event_team != team_id:
                    oz_entry_time = None
                    
        return cycle_shots

    def _calculate_forecheck_turnovers(self, team_id: int) -> int:
        """Count takeaways in the Offensive Zone"""
        fcto = 0
        for play in self.plays:
            event_type = play.get('typeDescKey', '')
            details = play.get('details', {})
            zone = details.get('zoneCode', '')
            event_team = details.get('eventOwnerTeamId')
            
            if event_type == 'takeaway' and zone == 'O' and event_team == team_id:
                fcto += 1
        return fcto

    def _calculate_nz_success_rate(self, team_id: int) -> dict:
        """Calculate % of NZ entries that lead to a shot"""
        entries = 0
        successful_entries = 0
        
        # This is complex: need to find entries, then look ahead for shots
        for i, play in enumerate(self.plays):
            details = play.get('details', {})
            event_type = play.get('typeDescKey', '')
            zone = details.get('zoneCode', '')
            event_team = details.get('eventOwnerTeamId')
            
            # Simple entry proxy: Team has event in NZ, followed by event in OZ
            if zone == 'N' and event_team == team_id:
                # Look ahead for entry
                for j in range(i + 1, min(i + 10, len(self.plays))):
                    next_play = self.plays[j]
                    next_details = next_play.get('details', {})
                    next_zone = next_details.get('zoneCode', '')
                    next_team = next_details.get('eventOwnerTeamId')
                    
                    if next_team != team_id: break # Change of possession
                    
                    if next_zone == 'O':
                        entries += 1
                        # Found entry, now look for shot within 8s of entry
                        entry_time = self._time_to_seconds(next_play.get('timeInPeriod', '00:00'))
                        shot_found = False
                        for k in range(j, min(j + 15, len(self.plays))):
                            shot_play = self.plays[k]
                            shot_time = self._time_to_seconds(shot_play.get('timeInPeriod', '00:00'))
                            if (shot_time - entry_time) > 8: break
                            if shot_play.get('details', {}).get('eventOwnerTeamId') != team_id: break
                            
                            if shot_play.get('typeDescKey') in ['shot-on-goal', 'missed-shot', 'blocked-shot', 'goal']:
                                shot_found = True
                                break
                        if shot_found:
                            successful_entries += 1
                        break
                        
        return {
            'entries': entries,
            'successful': successful_entries,
            'rate': (successful_entries / entries) if entries > 0 else 0
        }

    def _calculate_spatial_metrics(self, team_id: int) -> dict:
        """Calculate Slot Penetration and Net-Front Traffic Efficienty"""
        slot_penetrations = 0
        net_front_traffic_events = 0
        total_traffic_sum = 0
        
        # 1. Slot Penetration Loop (PBP-based for volume)
        # Perimeter: abs(y) > 22 or x < 55
        # Slot: abs(y) <= 22 and x >= 55
        for i, play in enumerate(self.plays):
            details = play.get('details', {})
            event_team = details.get('eventOwnerTeamId')
            if event_team != team_id: continue
            
            x = details.get('xCoord', 0)
            y = details.get('yCoord', 0)
            
            # Check if this is a "Penetration" (prev play was outside, current is inside slot)
            if abs(y) <= 22 and abs(x) >= 55: # In Slot
                # Find previous event by same team in same sequence
                for j in range(i - 1, max(0, i - 5), -1):
                    prev_play = self.plays[j]
                    prev_details = prev_play.get('details', {})
                    if prev_details.get('eventOwnerTeamId') != team_id: break # Change of pos
                    
                    prev_x = prev_details.get('xCoord', 0)
                    prev_y = prev_details.get('yCoord', 0)
                    
                    # If prev was outside slot (either wider or further back)
                    if abs(prev_y) > 22 or abs(prev_x) < 55:
                        slot_penetrations += 1
                        break
        
        # 2. Net-Front Traffic (Screening Efficiency on Goals)
        # Measures % of goals scored with a teammate screening the goalie
        # PBP Proxy: Goals with shot types indicating traffic (tip-in, deflected, wrap-around)
        traffic_goals = 0
        total_goals = 0
        
        for play in self.plays:
            if play.get('typeDescKey') != 'goal':
                continue
                
            details = play.get('details', {})
            event_team = details.get('eventOwnerTeamId')
            
            if event_team != team_id:
                continue
            
            total_goals += 1
            shot_type = details.get('shotType', '').lower()
            
            # Shot types that indicate net-front traffic/screening
            if shot_type in ['tip-in', 'deflected', 'wrap-around', 'bat']:
                traffic_goals += 1
        
        traffic_rate = (traffic_goals / max(1, total_goals))
                        
        return {
            'slot_penetration': slot_penetrations,
            'net_front_efficiency': f"{traffic_rate:.1%}"
        }

    def _calculate_possession_efficiency(self, team_id: int) -> str:
        """Goals + Shots per 60 seconds of OZ time"""
        total_shots = 0
        total_oz_seconds = 0
        
        oz_start_time = None
        for play in self.plays:
            details = play.get('details', {})
            zone = details.get('zoneCode', '')
            event_team = details.get('eventOwnerTeamId')
            event_type = play.get('typeDescKey', '')
            time_str = play.get('timeInPeriod', '00:00')
            current_time = self._time_to_seconds(time_str)
            
            if zone == 'O' and event_team == team_id:
                if oz_start_time is None:
                    oz_start_time = current_time
                if event_type in ['shot-on-goal', 'missed-shot', 'blocked-shot', 'goal']:
                    total_shots += 1
            else:
                if oz_start_time is not None:
                    total_oz_seconds += (current_time - oz_start_time)
                    oz_start_time = None
        
        if total_oz_seconds > 0:
            efficiency = total_shots / (total_oz_seconds / 60.0)
            return f"{efficiency:.1f}"
        return "0.0"

    def _calculate_entry_gap(self, team_id: int) -> str:
        """Average distance to nearest defender at zone entry (first frame of goal Sprite data)"""
        total_gap = 0
        gap_counts = 0
        
        game_id = self._get_game_id()
        
        # Only analyze goals since Sprite data is only available for goals
        # Use FIRST frame to capture entry moment, not final goal moment
        for play in self.plays:
            if play.get('typeDescKey') != 'goal':
                continue
                
            details = play.get('details', {})
            if details.get('eventOwnerTeamId') != team_id:
                continue
                
            event_id = play.get('eventId')
            if not event_id:
                continue
                
            sprite = self._get_sprite_with_throttling(game_id, event_id)
            if sprite and len(sprite) > 0:
                # Use FIRST frame (index 0) to capture entry, not final goal moment
                first_frame = sprite[0]
                on_ice = first_frame.get('onIce', {})
                
                # Find puck carrier (usually ID '1' or player with puck)
                carrier_pos = None
                
                for p_id, p_data in on_ice.items():
                    if p_data.get('id') == 1 or p_id == '1':
                        carrier_pos = (p_data.get('x', 0), p_data.get('y', 0))
                        break
                
                if not carrier_pos:
                    continue
                    
                cx, cy = carrier_pos
                min_def_dist = 999
                
                # Find closest other player (proxy for nearest defender)
                for p_id, p_data in on_ice.items():
                    if p_data.get('id') == 1 or p_id == '1':
                        continue  # Skip the puck carrier
                    
                    dx, dy = p_data.get('x', 0), p_data.get('y', 0)
                    dist = ((cx-dx)**2 + (cy-dy)**2)**0.5
                    
                    if dist < min_def_dist:
                        min_def_dist = dist
                
                if min_def_dist < 50:  # Reasonable gap range
                    total_gap += min_def_dist
                    gap_counts += 1
        
        if gap_counts > 0:
            return f"{total_gap/gap_counts:.1f} ft"
        return "None"


    def _calculate_passing_depth(self, team_id: int) -> float:
        """Calculate cumulative lateral (y-delta) distance of successful passes in OZ"""
        total_depth = 0
        
        for i, play in enumerate(self.plays):
            details = play.get('details', {})
            event_type = play.get('typeDescKey', '')
            zone = details.get('zoneCode', '')
            event_team = details.get('eventOwnerTeamId')
            
            # Simple pass logic: If current event and next event are same team in same zone
            if event_team == team_id and zone == 'O':
                # Look at next play
                if i + 1 < len(self.plays):
                    next_play = self.plays[i+1]
                    next_details = next_play.get('details', {})
                    next_team = next_details.get('eventOwnerTeamId')
                    next_zone = next_details.get('zoneCode', '')
                    
                    if next_team == team_id and next_zone == 'O':
                        y1 = details.get('yCoord', 0)
                        y2 = next_details.get('yCoord', 0)
                        total_depth += abs(y2 - y1)
        
        return round(total_depth, 1)

    def _time_to_seconds(self, time_str: str) -> int:
        try:
            parts = time_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])
        except:
            return 0
            
    def _get_sprite_with_throttling(self, game_id, event_id):
        """Fetch sprite data with a small delay to avoid 403 blocks"""
        if event_id in self._sprite_cache:
            return self._sprite_cache[event_id]
            
        import time
        now = time.time()
        # Ensure at least 0.5s between requests
        if now - self._last_request_time < 0.5:
            time.sleep(0.5 - (now - self._last_request_time))
            
        from sprite_parser import get_sprite_data
        data = get_sprite_data(game_id, event_id)
        self._last_request_time = time.time()
        self._sprite_cache[event_id] = data
        return data

    def _get_game_id(self) -> str:
        # We'll need to store or pass the game_id
        return getattr(self, 'game_id', "2024020088") # Default fallback

