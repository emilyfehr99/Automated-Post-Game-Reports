"""
Advanced NHL Metrics Analyzer
Creates custom hockey analytics from play-by-play data
"""

import json
import csv
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

class AdvancedMetricsAnalyzer:
    def __init__(self, play_by_play_data: dict):
        self.plays = play_by_play_data.get('plays', [])
        self.roster_map = self._create_roster_map(play_by_play_data)
        
    def _create_roster_map(self, play_by_play_data: dict) -> dict:
        """Create a mapping of player IDs to player info"""
        roster_map = {}
        if 'rosterSpots' in play_by_play_data:
            for player in play_by_play_data['rosterSpots']:
                player_id = player['playerId']
                roster_map[player_id] = {
                    'firstName': player['firstName']['default'],
                    'lastName': player['lastName']['default'],
                    'sweaterNumber': player['sweaterNumber'],
                    'positionCode': player['positionCode'],
                    'teamId': player['teamId']
                }
        return roster_map
    
    def get_available_metrics(self) -> dict:
        """Get all available metrics from the play-by-play data"""
        metrics = {
            'event_types': defaultdict(int),
            'spatial_data': set(),
            'player_actions': defaultdict(int),
            'zone_activities': defaultdict(int),
            'shot_types': set(),
            'penalty_types': set()
        }
        
        for play in self.plays:
            event_type = play.get('typeDescKey', '')
            details = play.get('details', {})
            
            # Count event types
            metrics['event_types'][event_type] += 1
            
            # Collect spatial data
            if 'xCoord' in details and 'yCoord' in details:
                metrics['spatial_data'].add('coordinates')
            if 'zoneCode' in details:
                metrics['zone_activities'][details['zoneCode']] += 1
                
            # Collect player actions
            for key in details.keys():
                if 'PlayerId' in key:
                    metrics['player_actions'][key] += 1
                    
            # Collect shot types
            if 'shotType' in details:
                metrics['shot_types'].add(details['shotType'])
                
            # Collect penalty types
            if 'descKey' in details and event_type == 'penalty':
                metrics['penalty_types'].add(details['descKey'])
        
        return metrics
    
    
    def calculate_shot_quality_metrics(self, team_id: int) -> dict:
        """Calculate advanced shot quality metrics"""
        shot_quality = {
            'total_shots': 0,
            'shots_on_goal': 0,
            'missed_shots': 0,
            'blocked_shots': 0,
            'shot_types': defaultdict(int),
            'shot_locations': defaultdict(int),
            'high_danger_shots': 0,
            'shooting_percentage': 0,
            'expected_goals': 0
        }
        
        for play in self.plays:
            details = play.get('details', {})
            event_type = play.get('typeDescKey', '')
            event_team = details.get('eventOwnerTeamId')
            
            if event_team != team_id:
                continue
                
            if event_type in ['shot-on-goal', 'missed-shot', 'blocked-shot']:
                shot_quality['total_shots'] += 1
                
                if event_type == 'shot-on-goal':
                    shot_quality['shots_on_goal'] += 1
                elif event_type == 'missed-shot':
                    shot_quality['missed_shots'] += 1
                elif event_type == 'blocked-shot':
                    shot_quality['blocked_shots'] += 1
                
                # Shot type analysis
                shot_type = details.get('shotType', 'unknown')
                shot_quality['shot_types'][shot_type] += 1
                
                # Location analysis
                x_coord = details.get('xCoord', 0)
                y_coord = details.get('yCoord', 0)
                zone = details.get('zoneCode', '')
                
                # High danger area (close to net, in front)
                if zone == 'O' and x_coord > 50 and abs(y_coord) < 20:
                    shot_quality['high_danger_shots'] += 1
                
                # Zone analysis
                shot_quality['shot_locations'][zone] += 1
        
        # Calculate shooting percentage
        if shot_quality['total_shots'] > 0:
            shot_quality['shooting_percentage'] = shot_quality['shots_on_goal'] / shot_quality['total_shots']
        
        # Calculate expected goals using advanced model
        shot_quality['expected_goals'] = self._calculate_expected_goals(team_id)
        
        return shot_quality
    
    def _calculate_expected_goals(self, team_id: int) -> float:
        """Calculate expected goals using distance, angle, shot type, and zone-based model"""
        total_xG = 0.0
        
        for play in self.plays:
            details = play.get('details', {})
            event_type = play.get('typeDescKey', '')
            event_team = details.get('eventOwnerTeamId')
            
            if event_team != team_id:
                continue
                
            if event_type in ['shot-on-goal', 'missed-shot', 'blocked-shot']:
                x_coord = details.get('xCoord', 0)
                y_coord = details.get('yCoord', 0)
                zone = details.get('zoneCode', '')
                shot_type = details.get('shotType', 'unknown')
                
                # Calculate expected goal value for this shot
                xG = self._calculate_single_shot_xG(x_coord, y_coord, zone, shot_type, event_type)
                total_xG += xG
        
        return round(total_xG, 2)
    
    def _calculate_single_shot_xG(self, x_coord: float, y_coord: float, zone: str, shot_type: str, event_type: str) -> float:
        """Calculate expected goal value for a single shot based on NHL analytics model"""
        
        # Base expected goal value
        base_xG = 0.0
        
        # Distance calculation (from goal line at x=89)
        distance_from_goal = ((89 - x_coord) ** 2 + (y_coord) ** 2) ** 0.5
        
        # Angle calculation (angle from goal posts)
        # Goal posts are at y = ±3 (assuming 6-foot goal width)
        angle_to_goal = self._calculate_shot_angle(x_coord, y_coord)
        
        # Zone-based adjustments
        zone_multiplier = self._get_zone_multiplier(zone, x_coord, y_coord)
        
        # Shot type adjustments
        shot_type_multiplier = self._get_shot_type_multiplier(shot_type)
        
        # Event type adjustments (shots on goal vs missed/blocked)
        event_multiplier = self._get_event_type_multiplier(event_type)
        
        # Core distance-based model (NHL standard curve)
        if distance_from_goal <= 10:
            base_xG = 0.25  # Very close to net
        elif distance_from_goal <= 20:
            base_xG = 0.15  # Close range
        elif distance_from_goal <= 35:
            base_xG = 0.08  # Medium range
        elif distance_from_goal <= 50:
            base_xG = 0.04  # Long range
        else:
            base_xG = 0.02  # Very long range
        
        # Apply angle adjustment (shots from wider angles have lower xG)
        if angle_to_goal > 45:
            angle_multiplier = 0.3  # Very wide angle
        elif angle_to_goal > 30:
            angle_multiplier = 0.5  # Wide angle
        elif angle_to_goal > 15:
            angle_multiplier = 0.8  # Moderate angle
        else:
            angle_multiplier = 1.0  # Good angle
        
        # Calculate final expected goal value
        final_xG = base_xG * zone_multiplier * shot_type_multiplier * event_multiplier * angle_multiplier
        
        # Cap at reasonable maximum
        return min(final_xG, 0.95)
    
    def _calculate_shot_angle(self, x_coord: float, y_coord: float) -> float:
        """Calculate the angle of the shot relative to the goal"""
        import math
        
        # Goal center is at (89, 0), goal posts at (89, ±3)
        distance_to_center = ((89 - x_coord) ** 2 + (y_coord) ** 2) ** 0.5
        
        if distance_to_center == 0:
            return 0
        
        # Calculate angle using law of cosines
        # Distance from shot to left post
        dist_to_left = ((89 - x_coord) ** 2 + (y_coord - 3) ** 2) ** 0.5
        # Distance from shot to right post  
        dist_to_right = ((89 - x_coord) ** 2 + (y_coord + 3) ** 2) ** 0.5
        
        # Goal width
        goal_width = 6
        
        # Use law of cosines to find angle
        if dist_to_left > 0 and dist_to_right > 0:
            cos_angle = (dist_to_left ** 2 + dist_to_right ** 2 - goal_width ** 2) / (2 * dist_to_left * dist_to_right)
            cos_angle = max(-1, min(1, cos_angle))  # Clamp to valid range
            angle = math.acos(cos_angle)
            return math.degrees(angle)
        
        return 45  # Default angle if calculation fails
    
    def _get_zone_multiplier(self, zone: str, x_coord: float, y_coord: float) -> float:
        """Get zone-based expected goal multiplier"""
        
        # High danger area (slot, crease area)
        if zone == 'O' and x_coord > 75 and abs(y_coord) < 15:
            return 1.5
        
        # Medium danger area (offensive zone, good position)
        elif zone == 'O' and x_coord > 60 and abs(y_coord) < 25:
            return 1.2
        
        # Low danger area (point shots, wide angles)
        elif zone == 'O':
            return 0.8
        
        # Neutral zone shots (rare but possible)
        elif zone == 'N':
            return 0.3
        
        # Defensive zone shots (very rare)
        elif zone == 'D':
            return 0.1
        
        return 1.0  # Default
    
    def _get_shot_type_multiplier(self, shot_type: str) -> float:
        """Get shot type-based expected goal multiplier"""
        
        shot_type = shot_type.lower()
        
        # High-danger shot types
        if shot_type in ['tip-in', 'deflection', 'backhand']:
            return 1.3
        elif shot_type in ['wrist', 'snap']:
            return 1.0
        elif shot_type in ['slap', 'slapshot']:
            return 0.9
        elif shot_type in ['wrap-around', 'wrap']:
            return 1.1
        elif shot_type in ['one-timer', 'onetime']:
            return 1.2
        
        return 1.0  # Default for unknown types
    
    def _get_event_type_multiplier(self, event_type: str) -> float:
        """Get event type-based expected goal multiplier"""
        
        if event_type == 'shot-on-goal':
            return 1.0  # Full value for shots on goal
        elif event_type == 'missed-shot':
            return 0.7  # Reduced value for missed shots
        elif event_type == 'blocked-shot':
            return 0.5  # Lower value for blocked shots
        
        return 1.0  # Default
    
    def calculate_pressure_metrics(self, team_id: int) -> dict:
        """Calculate offensive pressure metrics"""
        pressure = {
            'sustained_pressure_sequences': 0,
            'quick_strike_opportunities': 0,
            'zone_time': defaultdict(int),
            'shot_attempts_per_sequence': [],
            'pressure_players': defaultdict(int)
        }
        
        current_sequence = []
        sequence_start_time = None
        
        for play in self.plays:
            details = play.get('details', {})
            event_type = play.get('typeDescKey', '')
            event_team = details.get('eventOwnerTeamId')
            time_in_period = play.get('timeInPeriod', '00:00')
            
            # Convert time to seconds for analysis
            try:
                minutes, seconds = time_in_period.split(':')
                time_seconds = int(minutes) * 60 + int(seconds)
            except:
                time_seconds = 0
            
            if event_team == team_id:
                if not current_sequence:
                    sequence_start_time = time_seconds
                    current_sequence = []
                
                current_sequence.append({
                    'event_type': event_type,
                    'time': time_seconds,
                    'zone': details.get('zoneCode', ''),
                    'player_id': details.get('playerId') or details.get('shootingPlayerId')
                })
                
                # Track zone time
                zone = details.get('zoneCode', '')
                if zone:
                    pressure['zone_time'][zone] += 1
                    
            else:
                # End of possession sequence
                if current_sequence and sequence_start_time:
                    sequence_duration = time_seconds - sequence_start_time
                    shot_attempts = len([e for e in current_sequence if 'shot' in e['event_type']])
                    
                    pressure['shot_attempts_per_sequence'].append(shot_attempts)
                    
                    if sequence_duration > 30:  # Sustained pressure
                        pressure['sustained_pressure_sequences'] += 1
                    elif shot_attempts > 0:  # Quick strike
                        pressure['quick_strike_opportunities'] += 1
                    
                    # Track players involved in pressure
                    for event in current_sequence:
                        if event['player_id']:
                            pressure['pressure_players'][event['player_id']] += 1
                
                current_sequence = []
                sequence_start_time = None
        
        return pressure
    
    def calculate_cross_ice_pass_metrics(self, team_id: int) -> dict:
        """Calculate cross-ice pass success rate metrics"""
        cross_ice = {
            'total_cross_ice_attempts': 0,
            'successful_cross_ice_passes': 0,
            'cross_ice_success_rate': 0,
            'cross_ice_by_zone': defaultdict(lambda: {'attempts': 0, 'successful': 0}),
            'cross_ice_by_player': defaultdict(lambda: {'attempts': 0, 'successful': 0}),
            'cross_ice_distance_analysis': {
                'short_passes': {'attempts': 0, 'successful': 0},  # < 20 feet
                'medium_passes': {'attempts': 0, 'successful': 0}, # 20-40 feet
                'long_passes': {'attempts': 0, 'successful': 0}    # > 40 feet
            }
        }
        
        for i, play in enumerate(self.plays):
            details = play.get('details', {})
            event_type = play.get('typeDescKey', '')
            event_team = details.get('eventOwnerTeamId')
            
            if event_team != team_id or event_type != 'giveaway':
                continue
                
            # Look for cross-ice passes (giveaways that might be cross-ice attempts)
            # We need to analyze the next few events to see if it was a successful pass
            x_coord = details.get('xCoord', 0)
            y_coord = details.get('yCoord', 0)
            zone = details.get('zoneCode', '')
            player_id = details.get('playerId')
            
            # Check if this giveaway was actually a cross-ice pass attempt
            if self._is_cross_ice_pass_attempt(play, i):
                cross_ice['total_cross_ice_attempts'] += 1
                cross_ice['cross_ice_by_zone'][zone]['attempts'] += 1
                
                if player_id:
                    cross_ice['cross_ice_by_player'][player_id]['attempts'] += 1
                
                # Calculate pass distance
                pass_distance = self._calculate_pass_distance(play, i)
                if pass_distance < 20:
                    cross_ice['cross_ice_distance_analysis']['short_passes']['attempts'] += 1
                elif pass_distance <= 40:
                    cross_ice['cross_ice_distance_analysis']['medium_passes']['attempts'] += 1
                else:
                    cross_ice['cross_ice_distance_analysis']['long_passes']['attempts'] += 1
                
                # Check if the pass was successful (no immediate turnover)
                if self._was_cross_ice_pass_successful(play, i):
                    cross_ice['successful_cross_ice_passes'] += 1
                    cross_ice['cross_ice_by_zone'][zone]['successful'] += 1
                    
                    if player_id:
                        cross_ice['cross_ice_by_player'][player_id]['successful'] += 1
                    
                    # Update distance success
                    if pass_distance < 20:
                        cross_ice['cross_ice_distance_analysis']['short_passes']['successful'] += 1
                    elif pass_distance <= 40:
                        cross_ice['cross_ice_distance_analysis']['medium_passes']['successful'] += 1
                    else:
                        cross_ice['cross_ice_distance_analysis']['long_passes']['successful'] += 1
        
        # Calculate success rates
        if cross_ice['total_cross_ice_attempts'] > 0:
            cross_ice['cross_ice_success_rate'] = cross_ice['successful_cross_ice_passes'] / cross_ice['total_cross_ice_attempts']
        
        # Calculate zone success rates
        for zone in cross_ice['cross_ice_by_zone']:
            attempts = cross_ice['cross_ice_by_zone'][zone]['attempts']
            successful = cross_ice['cross_ice_by_zone'][zone]['successful']
            if attempts > 0:
                cross_ice['cross_ice_by_zone'][zone]['success_rate'] = successful / attempts
        
        # Calculate player success rates
        for player_id in cross_ice['cross_ice_by_player']:
            attempts = cross_ice['cross_ice_by_player'][player_id]['attempts']
            successful = cross_ice['cross_ice_by_player'][player_id]['successful']
            if attempts > 0:
                cross_ice['cross_ice_by_player'][player_id]['success_rate'] = successful / attempts
        
        # Calculate distance success rates
        for distance_type in cross_ice['cross_ice_distance_analysis']:
            attempts = cross_ice['cross_ice_distance_analysis'][distance_type]['attempts']
            successful = cross_ice['cross_ice_distance_analysis'][distance_type]['successful']
            if attempts > 0:
                cross_ice['cross_ice_distance_analysis'][distance_type]['success_rate'] = successful / attempts
        
        return cross_ice
    
    def _is_cross_ice_pass_attempt(self, play: dict, play_index: int) -> bool:
        """Determine if a giveaway was actually a cross-ice pass attempt"""
        details = play.get('details', {})
        
        # Look for giveaway events that might be cross-ice passes
        if play.get('typeDescKey') == 'giveaway':
            # Check if there's a teammate nearby who might have received the pass
            x_coord = details.get('xCoord', 0)
            y_coord = details.get('yCoord', 0)
            
            # Look at next few plays to see if there's a teammate in the area
            for j in range(play_index + 1, min(play_index + 5, len(self.plays))):
                next_play = self.plays[j]
                next_details = next_play.get('details', {})
                next_team = next_details.get('eventOwnerTeamId')
                
                # If next event is by same team, might be a successful cross-ice pass
                if next_team == details.get('eventOwnerTeamId'):
                    next_x = next_details.get('xCoord', 0)
                    next_y = next_details.get('yCoord', 0)
                    
                    # Check if it's a significant lateral movement (cross-ice)
                    lateral_distance = abs(next_y - y_coord)
                    if lateral_distance > 15:  # Significant lateral movement
                        return True
        
        return False
    
    def _calculate_pass_distance(self, play: dict, play_index: int) -> float:
        """Calculate the distance of a cross-ice pass"""
        details = play.get('details', {})
        x_coord = details.get('xCoord', 0)
        y_coord = details.get('yCoord', 0)
        
        # Find the receiving player in subsequent plays
        for j in range(play_index + 1, min(play_index + 5, len(self.plays))):
            next_play = self.plays[j]
            next_details = next_play.get('details', {})
            next_team = next_details.get('eventOwnerTeamId')
            
            if next_team == details.get('eventOwnerTeamId'):
                next_x = next_details.get('xCoord', 0)
                next_y = next_details.get('yCoord', 0)
                
                # Calculate Euclidean distance
                distance = ((next_x - x_coord) ** 2 + (next_y - y_coord) ** 2) ** 0.5
                return distance
        
        return 0
    
    def _was_cross_ice_pass_successful(self, play: dict, play_index: int) -> bool:
        """Determine if a cross-ice pass was successful"""
        details = play.get('details', {})
        team_id = details.get('eventOwnerTeamId')
        
        # Look at next few plays to see if team maintains possession
        for j in range(play_index + 1, min(play_index + 3, len(self.plays))):
            next_play = self.plays[j]
            next_details = next_play.get('details', {})
            next_team = next_details.get('eventOwnerTeamId')
            
            # If next event is by same team, pass was successful
            if next_team == team_id:
                return True
            # If next event is by opponent, pass was unsuccessful
            elif next_team != team_id:
                return False
        
        # If we can't determine, assume unsuccessful
        return False

    def calculate_defensive_metrics(self, team_id: int) -> dict:
        """Calculate defensive metrics"""
        defense = {
            'blocked_shots': 0,
            'takeaways': 0,
            'hits': 0,
            'defensive_zone_clears': 0,
            'penalty_kill_efficiency': 0,
            'shot_attempts_against': 0,
            'high_danger_chances_against': 0,
            'defensive_players': defaultdict(int)
        }
        
        penalty_situations = []
        current_penalty = None
        
        for play in self.plays:
            details = play.get('details', {})
            event_type = play.get('typeDescKey', '')
            event_team = details.get('eventOwnerTeamId')
            zone = details.get('zoneCode', '')
            
            # Track penalty situations
            if event_type == 'penalty':
                if event_team != team_id:  # Opponent penalty
                    current_penalty = {
                        'start_time': play.get('timeInPeriod', '00:00'),
                        'duration': details.get('duration', 0)
                    }
                else:  # Our penalty
                    penalty_situations.append({
                        'start_time': play.get('timeInPeriod', '00:00'),
                        'duration': details.get('duration', 0)
                    })
            
            # Count defensive actions
            if event_team == team_id:
                if event_type == 'blocked-shot':
                    defense['blocked_shots'] += 1
                    player_id = details.get('blockingPlayerId')
                    if player_id:
                        defense['defensive_players'][player_id] += 1
                        
                elif event_type == 'takeaway':
                    defense['takeaways'] += 1
                    player_id = details.get('playerId')
                    if player_id:
                        defense['defensive_players'][player_id] += 1
                        
                elif event_type == 'hit':
                    defense['hits'] += 1
                    player_id = details.get('hittingPlayerId')
                    if player_id:
                        defense['defensive_players'][player_id] += 1
                        
                elif event_type == 'giveaway' and zone == 'D':
                    defense['defensive_zone_clears'] += 1
            
            # Track shots against
            elif event_type in ['shot-on-goal', 'missed-shot']:
                defense['shot_attempts_against'] += 1
                
                # High danger chances
                x_coord = details.get('xCoord', 0)
                if zone == 'O' and x_coord > 50 and abs(details.get('yCoord', 0)) < 20:
                    defense['high_danger_chances_against'] += 1
        
        return defense
    
    def generate_comprehensive_report(self, away_team_id: int, home_team_id: int) -> dict:
        """Generate a comprehensive advanced metrics report"""
        report = {
            'away_team': {
                'team_id': away_team_id,
                'shot_quality': self.calculate_shot_quality_metrics(away_team_id),
                'pressure': self.calculate_pressure_metrics(away_team_id),
                'defense': self.calculate_defensive_metrics(away_team_id),
                'cross_ice_passes': self.calculate_cross_ice_pass_metrics(away_team_id)
            },
            'home_team': {
                'team_id': home_team_id,
                'shot_quality': self.calculate_shot_quality_metrics(home_team_id),
                'pressure': self.calculate_pressure_metrics(home_team_id),
                'defense': self.calculate_defensive_metrics(home_team_id),
                'cross_ice_passes': self.calculate_cross_ice_pass_metrics(home_team_id)
            },
            'available_metrics': self.get_available_metrics()
        }
        
        return report

def analyze_game_metrics(game_id: str) -> dict:
    """Analyze advanced metrics for a specific game"""
    import requests
    
    # Fetch play-by-play data
    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"error": "Could not fetch game data"}
    
    play_by_play_data = response.json()
    
    # Get team IDs from boxscore
    boxscore_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"
    boxscore_response = requests.get(boxscore_url)
    
    if boxscore_response.status_code != 200:
        return {"error": "Could not fetch boxscore data"}
    
    boxscore_data = boxscore_response.json()
    away_team_id = boxscore_data['awayTeam']['id']
    home_team_id = boxscore_data['homeTeam']['id']
    
    # Create analyzer and generate report
    analyzer = AdvancedMetricsAnalyzer(play_by_play_data)
    return analyzer.generate_comprehensive_report(away_team_id, home_team_id)

if __name__ == "__main__":
    # Test with current game
    game_id = "2024020088"
    metrics = analyze_game_metrics(game_id)
    
    print("🏒 ADVANCED NHL METRICS ANALYSIS 🏒")
    print("=" * 50)
    
    if "error" in metrics:
        print(f"Error: {metrics['error']}")
    else:
        print(f"Game ID: {game_id}")
        print(f"Available Event Types: {list(metrics['available_metrics']['event_types'].keys())}")
        print(f"Shot Types: {list(metrics['available_metrics']['shot_types'])}")
        print(f"Zone Activities: {dict(metrics['available_metrics']['zone_activities'])}")
        
        print("\n📊 CUSTOM METRICS SUMMARY:")
        print(f"Away Team High Danger Shots: {metrics['away_team']['shot_quality']['high_danger_shots']}")
        print(f"Away Team Sustained Pressure: {metrics['away_team']['pressure']['sustained_pressure_sequences']}")
        print(f"Away Team Blocked Shots: {metrics['away_team']['defense']['blocked_shots']}")
        print(f"Away Team Cross-Ice Pass Success: {metrics['away_team']['cross_ice_passes']['cross_ice_success_rate']:.2%} ({metrics['away_team']['cross_ice_passes']['successful_cross_ice_passes']}/{metrics['away_team']['cross_ice_passes']['total_cross_ice_attempts']})")
        
        print(f"\nHome Team High Danger Shots: {metrics['home_team']['shot_quality']['high_danger_shots']}")
        print(f"Home Team Sustained Pressure: {metrics['home_team']['pressure']['sustained_pressure_sequences']}")
        print(f"Home Team Blocked Shots: {metrics['home_team']['defense']['blocked_shots']}")
        print(f"Home Team Cross-Ice Pass Success: {metrics['home_team']['cross_ice_passes']['cross_ice_success_rate']:.2%} ({metrics['home_team']['cross_ice_passes']['successful_cross_ice_passes']}/{metrics['home_team']['cross_ice_passes']['total_cross_ice_attempts']})")

def export_game_data_to_csv(game_id: str, output_dir: str = None) -> str:
    """Export comprehensive game data to CSV files for Excel analysis"""
    if output_dir is None:
        output_dir = f"game_data_{game_id}"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Fetch game data
    import requests
    
    # Get play-by-play data
    pbp_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    pbp_response = requests.get(pbp_url)
    
    if pbp_response.status_code != 200:
        return f"Error: Could not fetch play-by-play data for game {game_id}"
    
    play_by_play_data = pbp_response.json()
    
    # Get boxscore data
    boxscore_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"
    boxscore_response = requests.get(boxscore_url)
    
    if boxscore_response.status_code != 200:
        return f"Error: Could not fetch boxscore data for game {game_id}"
    
    boxscore_data = boxscore_response.json()
    
    # Get game center data (optional)
    gamecenter_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/feed/live"
    gamecenter_response = requests.get(gamecenter_url)
    gamecenter_data = {}
    
    if gamecenter_response.status_code == 200:
        gamecenter_data = gamecenter_response.json()
    
    # 1. Export Raw Play-by-Play Data (exactly as provided by NHL API)
    pbp_filename = os.path.join(output_dir, f"play_by_play_{game_id}.csv")
    with open(pbp_filename, 'w', newline='', encoding='utf-8') as csvfile:
        if play_by_play_data.get('plays'):
            # Get all possible fieldnames from the API data
            all_fieldnames = set()
            for play in play_by_play_data['plays']:
                # Add top-level fields
                for key in play.keys():
                    all_fieldnames.add(key)
                # Add details fields with 'details_' prefix
                details = play.get('details', {})
                for key in details.keys():
                    all_fieldnames.add(f'details_{key}')
                # Add period descriptor fields
                period_desc = play.get('periodDescriptor', {})
                for key in period_desc.keys():
                    all_fieldnames.add(f'periodDescriptor_{key}')
                # Add description fields
                description = play.get('description', {})
                for key in description.keys():
                    all_fieldnames.add(f'description_{key}')
            
            # Sort fieldnames for consistent output
            fieldnames = sorted(list(all_fieldnames))
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for play in play_by_play_data['plays']:
                row = {}
                
                # Add top-level fields
                for key, value in play.items():
                    if isinstance(value, dict):
                        # Skip nested dicts - we'll handle them separately
                        continue
                    row[key] = value
                
                # Add details fields with prefix
                details = play.get('details', {})
                for key, value in details.items():
                    row[f'details_{key}'] = value
                
                # Add period descriptor fields with prefix
                period_desc = play.get('periodDescriptor', {})
                for key, value in period_desc.items():
                    row[f'periodDescriptor_{key}'] = value
                
                # Add description fields with prefix
                description = play.get('description', {})
                for key, value in description.items():
                    row[f'description_{key}'] = value
                
                writer.writerow(row)
    
    # 2. Export Player Statistics
    player_filename = os.path.join(output_dir, f"player_stats_{game_id}.csv")
    with open(player_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'team', 'player_id', 'jersey_number', 'name', 'position', 'toi', 
            'goals', 'assists', 'points', 'plus_minus', 'pim', 'shots', 
            'hits', 'blocks', 'giveaways', 'takeaways', 'faceoffs_won', 'faceoffs_lost'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Away team players
        away_team = boxscore_data.get('awayTeam', {})
        for player in away_team.get('players', []):
            stats = player.get('stats', {})
            row = {
                'team': 'Away',
                'player_id': player.get('playerId', ''),
                'jersey_number': player.get('sweaterNumber', ''),
                'name': f"{player.get('firstName', {}).get('default', '')} {player.get('lastName', {}).get('default', '')}",
                'position': player.get('positionCode', ''),
                'toi': stats.get('timeOnIce', ''),
                'goals': stats.get('goals', 0),
                'assists': stats.get('assists', 0),
                'points': stats.get('goals', 0) + stats.get('assists', 0),
                'plus_minus': stats.get('plusMinus', 0),
                'pim': stats.get('pim', 0),
                'shots': stats.get('shots', 0),
                'hits': stats.get('hits', 0),
                'blocks': stats.get('blockedShots', 0),
                'giveaways': stats.get('giveaways', 0),
                'takeaways': stats.get('takeaways', 0),
                'faceoffs_won': stats.get('faceoffWins', 0),
                'faceoffs_lost': stats.get('faceoffLosses', 0)
            }
            writer.writerow(row)
        
        # Home team players
        home_team = boxscore_data.get('homeTeam', {})
        for player in home_team.get('players', []):
            stats = player.get('stats', {})
            row = {
                'team': 'Home',
                'player_id': player.get('playerId', ''),
                'jersey_number': player.get('sweaterNumber', ''),
                'name': f"{player.get('firstName', {}).get('default', '')} {player.get('lastName', {}).get('default', '')}",
                'position': player.get('positionCode', ''),
                'toi': stats.get('timeOnIce', ''),
                'goals': stats.get('goals', 0),
                'assists': stats.get('assists', 0),
                'points': stats.get('goals', 0) + stats.get('assists', 0),
                'plus_minus': stats.get('plusMinus', 0),
                'pim': stats.get('pim', 0),
                'shots': stats.get('shots', 0),
                'hits': stats.get('hits', 0),
                'blocks': stats.get('blockedShots', 0),
                'giveaways': stats.get('giveaways', 0),
                'takeaways': stats.get('takeaways', 0),
                'faceoffs_won': stats.get('faceoffWins', 0),
                'faceoffs_lost': stats.get('faceoffLosses', 0)
            }
            writer.writerow(row)
    
    # 3. Export Team Statistics
    team_filename = os.path.join(output_dir, f"team_stats_{game_id}.csv")
    with open(team_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'team', 'goals', 'shots', 'power_play_conversion', 'penalty_minutes',
            'hits', 'faceoff_wins', 'blocked_shots', 'giveaways', 'takeaways'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Away team
        away_stats = {
            'team': away_team.get('abbrev', 'Away'),
            'goals': away_team.get('score', 0),
            'shots': away_team.get('sog', 0),
            'power_play_conversion': away_team.get('powerPlayConversion', ''),
            'penalty_minutes': away_team.get('penaltyMinutes', 0),
            'hits': away_team.get('hits', 0),
            'faceoff_wins': away_team.get('faceoffWins', 0),
            'blocked_shots': away_team.get('blockedShots', 0),
            'giveaways': away_team.get('giveaways', 0),
            'takeaways': away_team.get('takeaways', 0)
        }
        writer.writerow(away_stats)
        
        # Home team
        home_stats = {
            'team': home_team.get('abbrev', 'Home'),
            'goals': home_team.get('score', 0),
            'shots': home_team.get('sog', 0),
            'power_play_conversion': home_team.get('powerPlayConversion', ''),
            'penalty_minutes': home_team.get('penaltyMinutes', 0),
            'hits': home_team.get('hits', 0),
            'faceoff_wins': home_team.get('faceoffWins', 0),
            'blocked_shots': home_team.get('blockedShots', 0),
            'giveaways': home_team.get('giveaways', 0),
            'takeaways': home_team.get('takeaways', 0)
        }
        writer.writerow(home_stats)
    
    # 4. Export Advanced Metrics
    analyzer = AdvancedMetricsAnalyzer(play_by_play_data)
    away_team_id = boxscore_data['awayTeam']['id']
    home_team_id = boxscore_data['homeTeam']['id']
    metrics = analyzer.generate_comprehensive_report(away_team_id, home_team_id)
    
    advanced_filename = os.path.join(output_dir, f"advanced_metrics_{game_id}.csv")
    with open(advanced_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'team', 'metric_category', 'metric_name', 'value'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Export metrics for both teams
        for team_name, team_data in [('Away', metrics['away_team']), ('Home', metrics['home_team'])]:
            # Shot Quality Metrics
            shot_quality = team_data['shot_quality']
            for metric, value in shot_quality.items():
                if isinstance(value, (int, float)):
                    writer.writerow({
                        'team': team_name,
                        'metric_category': 'Shot Quality',
                        'metric_name': metric,
                        'value': value
                    })
            
            # Pressure Metrics
            pressure = team_data['pressure']
            for metric, value in pressure.items():
                if isinstance(value, (int, float)):
                    writer.writerow({
                        'team': team_name,
                        'metric_category': 'Pressure',
                        'metric_name': metric,
                        'value': value
                    })
            
            # Defense Metrics
            defense = team_data['defense']
            for metric, value in defense.items():
                if isinstance(value, (int, float)):
                    writer.writerow({
                        'team': team_name,
                        'metric_category': 'Defense',
                        'metric_name': metric,
                        'value': value
                    })
            
            # Cross-Ice Pass Metrics
            cross_ice = team_data['cross_ice_passes']
            for metric, value in cross_ice.items():
                if isinstance(value, (int, float)):
                    writer.writerow({
                        'team': team_name,
                        'metric_category': 'Cross-Ice Passes',
                        'metric_name': metric,
                        'value': value
                    })
    
    return f"Game data exported to {output_dir}/ with {len([f for f in os.listdir(output_dir) if f.endswith('.csv')])} CSV files"
