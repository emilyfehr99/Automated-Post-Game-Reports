"""
Sprite Goal Analyzer - Team Comparison Version
Analyzes sprite data for both teams and provides comparative statistics
"""

import requests
import math
from typing import Dict, Optional

class SpriteGoalAnalyzer:
    """Analyzes all goals in a game using sprite tracking data - team comparison"""
    
    def __init__(self, game_data=None):
        self.game_data = game_data
        self.GOAL_X = 2250
        self.GOAL_Y = 500
        self.BLUE_LINE_X = 700
    
    def distance(self, x1, y1, x2, y2):
        """Calculate Euclidean distance"""
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    def get_sprite_data(self, game_id, event_id):
        """Fetch sprite data for a specific event"""
        try:
            year = str(game_id)[:4]
            next_year = str(int(year) + 1)
            season = f"{year}{next_year}"
        except:
            season = "20252026"
            
        url = f'https://wsr.nhle.com/sprites/{season}/{game_id}/ev{event_id}.json'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://www.nhl.com/',
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def get_game_data(self, game_id):
        """Fetch game play-by-play data"""
        url = f'https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play'
        try:
            return requests.get(url, timeout=5).json()
        except:
            return None
    
    def analyze_net_front_presence(self, sprite_data):
        """Count average players in net-front area"""
        if not sprite_data or len(sprite_data) < 10:
            return 0
        
        GOAL_X_MIN = 2000
        GOAL_X_MAX = 2300
        GOAL_Y_MIN = 350
        GOAL_Y_MAX = 650
        
        mid_point = len(sprite_data) // 2
        sample_frames = sprite_data[max(0, mid_point-10):min(len(sprite_data), mid_point+10)]
        
        player_counts = []
        for frame in sample_frames:
            count = 0
            for p in frame['onIce'].values():
                if p.get('sweaterNumber') == '':
                    continue
                if (GOAL_X_MIN <= p['x'] <= GOAL_X_MAX and 
                    GOAL_Y_MIN <= p['y'] <= GOAL_Y_MAX):
                    count += 1
            player_counts.append(count)
        
        return round(sum(player_counts) / len(player_counts), 1) if player_counts else 0
    
    def analyze_shot_distance(self, sprite_data):
        """Calculate shot distance from release point to goal"""
        if not sprite_data:
            return 0
        
        # Find the shot release point (earliest puck position)
        release_point = None
        for frame in sprite_data[:10]:  # Check first 10 frames for release
            for p in frame['onIce'].values():
                if p.get('id') == 1:  # Puck ID
                    release_point = (p['x'], p['y'])
                    break
            if release_point:
                break
        
        if not release_point:
            return 0
        
        # Goal is always at x = ±89 (89 feet from center), y = 0 (center of goal)
        # Determine which goal based on x position of shot
        # If shot from left side (negative x), goal is at right (positive x = 89)
        # If shot from right side (positive x), goal is at left (negative x = -89)
        goal_x = 89 if release_point[0] < 0 else -89
        goal_y = 0
        
        # Calculate distance from release point to goal
        shot_distance = self.distance(release_point[0], release_point[1], goal_x, goal_y)
        
        return round(shot_distance, 0)
    
    def get_game_landing(self, game_id):
        """Fetch game landing data for detailed period info"""
        url = f'https://api-web.nhle.com/v1/gamecenter/{game_id}/landing'
        try:
            return requests.get(url, timeout=5).json()
        except:
            return None
            
    def analyze_zone_entry_count(self, sprite_data, scoring_team_id, period_defending_side, home_team_id):
        """
        Determine zone entry type:
        - CARRY: Player possesses puck cross offensive blue line
        - PASS: Puck crosses line independently, then received by teammate
        - DUMP: Puck crosses line independently, not received immediately
        """
        if not sprite_data or len(sprite_data) < 10:
            return None
            
        # Determine Attack Direction
        # period_defending_side is for HOME team (e.g. 'left' or 'right')
        # If Home Defends Left -> Home Zone < 1200. Home Attacks Right (> 1200).
        # If Home Defends Right -> Home Zone > 1200. Home Attacks Left (< 1200).
        
        # Coordinate Logic:
        # Standard Rink: 0 (Left) to 2400 (Right). Center 1200.
        # Defending Left: Zone is 0-900?
        # Defending Right: Zone is 1500-2400?
        
        is_home_scoring = (scoring_team_id == home_team_id)
        
        home_defends_right = (period_defending_side == 'right') # implies > 1200
        
        if is_home_scoring:
            # Home is Attacking.
            # If Home Defends Right -> Home Attacks Left (< 1200)
            # If Home Defends Left -> Home Attacks Right (> 1200)
            attacking_right = not home_defends_right
        else:
            # Away is Attacking.
            # If Home Defends Right -> Away Attacks Right (> 1200) (Towards Home Zone)
            # If Home Defends Left -> Away Attacks Left (< 1200)
            attacking_right = home_defends_right
            
        # Set Offensive Blue Line
        # If Attacking Right: Cross 1500 (Increasing X)
        # If Attacking Left: Cross 900 (Decreasing X)
        blue_line_x = 1500 if attacking_right else 900
        
        # Helper to return WHO has possession
        def get_possessor(frame, dist_threshold=80):
            for p in frame['onIce'].values():
                if p.get('sweaterNumber') == '' or p.get('teamId') != scoring_team_id:
                    continue
                # Find puck
                puck = None
                for px in frame['onIce'].values():
                    if px.get('id')==1: puck=px; break
                if not puck: return None
                
                dist = self.distance(puck['x'], puck['y'], p['x'], p['y'])
                if dist < dist_threshold: return p.get('id') # ROI or ID
            return None

        # Check if START is already inside
        # Attacking Right: Inside if X > 1500
        # Attacking Left: Inside if X < 900
        start_inside = False
        first_frame = sprite_data[0]
        # Find puck in first frame
        puck_start_x = None
        for p in first_frame['onIce'].values():
            if p.get('id') == 1: puck_start_x = p['x']; break
            
        if puck_start_x is not None:
            if attacking_right and puck_start_x >= blue_line_x:
                start_inside = True
            elif not attacking_right and puck_start_x <= blue_line_x:
                start_inside = True
                
        if start_inside:
            # Fallback handling for clips starting inside zone
            initial_possessor_id = get_possessor(first_frame, 80)
            
            if initial_possessor_id:
                # Check for transfer (Pass)
                possible_pass = False
                for i in range(1, min(40, len(sprite_data))):
                    curr_pid = get_possessor(sprite_data[i], 100) # Slightly broader for receipt
                    if curr_pid and curr_pid != initial_possessor_id:
                        return 'pass' # Transferred to teammate
                return 'carry' # Kept it (or lost it later, but initially carried)
            else:
                # Look for first receipt (Dump -> Pass/Possession)
                for i in range(1, min(40, len(sprite_data))):
                    if get_possessor(sprite_data[i], 100):
                        return 'pass' # Received loose puck
                return 'dump'
        
        # Standard Crossing Logic
        puck_positions = []
        for i, frame in enumerate(sprite_data):
            for p in frame['onIce'].values():
                if p.get('id') == 1:
                    puck_positions.append({'frame': i, 'x': p['x'], 'y': p['y']})
                    break
                    
        for i in range(1, len(puck_positions)):
            prev_x = puck_positions[i-1]['x']
            curr_x = puck_positions[i]['x']
            
            # Check for Offensive Crossing
            crossing_detected = False
            if attacking_right:
                if prev_x < blue_line_x and curr_x >= blue_line_x:
                    crossing_detected = True
            else:
                if prev_x > blue_line_x and curr_x <= blue_line_x:
                    crossing_detected = True
            
            if crossing_detected:
                entry_frame_idx = puck_positions[i]['frame']
                entry_frame = sprite_data[entry_frame_idx]
                
                # Check possession AT the line (CARRY)
                # Relaxed threshold (80 units ~ 6-7 feet) per user feedback
                puck_pos = (curr_x, puck_positions[i]['y'])
                
                closest_dist_at_line = float('inf')
                for p in entry_frame['onIce'].values():
                    if p.get('sweaterNumber') == '' or p.get('teamId') != scoring_team_id:
                        continue
                    dist = self.distance(puck_pos[0], puck_pos[1], p['x'], p['y'])
                    if dist < closest_dist_at_line:
                        closest_dist_at_line = dist
                
                if closest_dist_at_line < 80: 
                    return 'carry'
                
                # If not possessed at line, check next 40 frames (approx 1.2s) for PASS receipt
                for f_offset in range(1, 41):
                    if entry_frame_idx + f_offset >= len(sprite_data):
                        break
                    
                    future_frame = sprite_data[entry_frame_idx + f_offset]
                    fut_puck = None
                    for p in future_frame['onIce'].values():
                        if p.get('id') == 1:
                            fut_puck = p
                            break
                    
                    if not fut_puck: continue
                    
                    for p in future_frame['onIce'].values():
                        if p.get('sweaterNumber') == '' or p.get('teamId') != scoring_team_id:
                            continue
                        dist = self.distance(fut_puck['x'], fut_puck['y'], p['x'], p['y'])
                        if dist < 100: # Received!
                            return 'pass'
                
                return 'dump'
        
        return None
    
    def analyze_pass_count(self, sprite_data, scoring_team_id):
        """Count number of passes in sequence"""
        if not sprite_data:
            return 0
        
        possessions = []
        for frame in sprite_data[::5]:
            puck = None
            for p in frame['onIce'].values():
                if p.get('id') == 1:
                    puck = p
                    break
            
            if not puck:
                continue
            
            closest_dist = float('inf')
            closest_player = None
            
            for p in frame['onIce'].values():
                if p.get('sweaterNumber') == '' or p.get('teamId') != scoring_team_id:
                    continue
                dist = self.distance(puck['x'], puck['y'], p['x'], p['y'])
                if dist < 50 and dist < closest_dist:
                    closest_dist = dist
                    closest_player = p['sweaterNumber']
            
            if closest_player:
                possessions.append(closest_player)
        
        passes = 0
        for i in range(1, len(possessions)):
            if possessions[i] != possessions[i-1]:
                passes += 1
        
        return passes
    
    def analyze_game_goals_by_team(self, game_id) -> Optional[Dict]:
        """Analyze all goals by team and return team comparison data"""
        game_data = self.get_game_data(game_id)
        landing_data = self.get_game_landing(game_id)
        
        if not game_data:
            return None
        
        # Get team info
        away_team_id = game_data.get('awayTeam', {}).get('id')
        home_team_id = game_data.get('homeTeam', {}).get('id')
        away_abbrev = game_data.get('awayTeam', {}).get('abbrev', 'AWAY')
        home_abbrev = game_data.get('homeTeam', {}).get('abbrev', 'HOME')
        
        if not away_team_id or not home_team_id:
            return None
            
        # Build Map of Period -> Home Defending Side
        period_sides = {}
        if landing_data and 'summary' in landing_data and 'scoring' in landing_data['summary']:
            for period_info in landing_data['summary']['scoring']:
                # The period info usually contains a list of goals
                # We need the period number
                p_desc = period_info.get('periodDescriptor', {})
                p_num = p_desc.get('number')
                
                # Check first goal for side info
                goals_list = period_info.get('goals', [])
                if goals_list and p_num:
                    side = goals_list[0].get('homeTeamDefendingSide')
                    if side:
                        period_sides[p_num] = side
                        
        # Fallback sides if not found (standard rotation)
        # Period 1: usually 'right' or 'left' but switch in 2.
        # If we didn't find specific API info, let's default to inference inside the function
        # Or simplistic: 1=right, 2=left, 3=right (often home defends right first? not guaranteed!)
        # Actually, let's rely on goal heuristic if side is missing (pass None)
        
        goals = [p for p in game_data.get('plays', []) if p.get('typeDescKey') == 'goal']
        
        if not goals:
            return None
        
        # Initialize team stats
        team_stats = {
            away_team_id: {
                'abbrev': away_abbrev,
                'net_front': [],
                'shot_dist': [],
                'entry_types': {'carry': 0, 'pass': 0, 'dump': 0},
                'total_entries': 0,
                'passes': [],
                'traffic_goals': 0,  # Goals with screening
                'total_goals': 0  # Total goals
            },
            home_team_id: {
                'abbrev': home_abbrev,
                'net_front': [],
                'shot_dist': [],
                'entry_types': {'carry': 0, 'pass': 0, 'dump': 0},
                'total_entries': 0,
                'passes': [],
                'traffic_goals': 0,  # Goals with screening
                'total_goals': 0  # Total goals
            }
        }
        
        # Fetch PBP data to calculate Net-Front Traffic %
        pbp_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
        pbp_response = requests.get(pbp_url)
        if pbp_response.status_code == 200:
            pbp_data = pbp_response.json()
            plays = pbp_data.get('plays', [])
            
            # Calculate traffic goals for each team
            for play in plays:
                if play.get('typeDescKey') != 'goal':
                    continue
                details = play.get('details', {})
                event_team = details.get('eventOwnerTeamId')
                
                if event_team in team_stats:
                    team_stats[event_team]['total_goals'] += 1
                    shot_type = details.get('shotType', '').lower()
                    # Shot types indicating net-front traffic
                    if shot_type in ['tip-in', 'deflected', 'wrap-around', 'bat']:
                        team_stats[event_team]['traffic_goals'] += 1
        
        for goal in goals:
            event_id = goal.get('eventId')
            scoring_team_id = goal.get('details', {}).get('eventOwnerTeamId')
            period_num = goal.get('periodDescriptor', {}).get('number')
            
            if scoring_team_id not in team_stats:
                continue
            
            sprite_data = self.get_sprite_data(game_id, event_id)
            if not sprite_data:
                continue
            
            # Net-front presence
            net_front = self.analyze_net_front_presence(sprite_data)
            team_stats[scoring_team_id]['net_front'].append(net_front)
            
            # Shot distance
            shot_dist = self.analyze_shot_distance(sprite_data)
            team_stats[scoring_team_id]['shot_dist'].append(shot_dist)
            
            # Zone entry
            # Get side for this period
            side = period_sides.get(period_num)
            # If side is missing, we could try to infer it here or handle in func
            # For robustness: if side is None, func will fail? 
            # Let's ensure logic works or defaults.
            # But the user specifically asked for API info. I implemented finding it.
            # If side is None, we default to the heuristic I removed?
            # I should keep the heuristic as fallback inside analyze_zone_entry_count?
            # No, I removed it. I will restore heuristic if side is None.
            
            if side:
                entry_type = self.analyze_zone_entry_count(sprite_data, scoring_team_id, side, home_team_id)
            else:
                # Fallback: Infer from goal location (pass fake side based on inference)
                # Infer side from goal
                goal_x_avg = 0
                c = 0
                for f in sprite_data[-10:]:
                    for p in f['onIce'].values():
                        if p.get('id')==1: goal_x_avg+=p['x']; c+=1; break
                if c>0:
                    goal_x_avg/=c
                    # If goal > 1200, Defending Side = Right
                    # If goal < 1200, Defending Side = Left
                    inferred_side = 'right' if goal_x_avg > 1200 else 'left'
                    entry_type = self.analyze_zone_entry_count(sprite_data, scoring_team_id, inferred_side, home_team_id)
                else:
                    entry_type = None

            if entry_type:
                team_stats[scoring_team_id]['entry_types'][entry_type] += 1
            
            # Passes
            pass_count = self.analyze_pass_count(sprite_data, scoring_team_id)
            team_stats[scoring_team_id]['passes'].append(pass_count)
        
        # Calculate averages
        result = {}
        for team_id, stats in team_stats.items():
            # Calculate Net-Front Traffic %
            traffic_pct = 0
            if stats['total_goals'] > 0:
                traffic_pct = round((stats['traffic_goals'] / stats['total_goals']) * 100, 1)
            
            result[team_id] = {
                'abbrev': stats['abbrev'],
                'avg_net_front': round(sum(stats['net_front']) / len(stats['net_front']), 1) if stats['net_front'] else 0,
                'net_front_traffic_pct': traffic_pct,  # New screening efficiency metric
                # Convert units to feet (approx 12 units = 1 foot)
                'avg_shot_dist': round((sum(stats['shot_dist']) / len(stats['shot_dist'])) / 12, 0) if stats['shot_dist'] else 0,
                'entry_counts': stats['entry_types'], # Return raw counts for visualization
                'avg_passes': round(sum(stats['passes']) / len(stats['passes']), 1) if stats['passes'] else 0
            }
        
        return {
            'away_team_id': away_team_id,
            'home_team_id': home_team_id,
            'stats': result
        }

    def analyze_goals(self) -> Dict:
        """Helper for the model pipeline to get structured sprite metrics"""
        if not self.game_data:
            return {}
            
        game_id = self.game_data.get('id')
        if not game_id:
            return {}
            
        result = self.analyze_game_goals_by_team(game_id)
        if not result:
            return {}
            
        away_id = result['away_team_id']
        home_id = result['home_team_id']
        
        away_stats = result['stats'].get(away_id, {})
        home_stats = result['stats'].get(home_id, {})
        
        # Calculate movement metrics (Proxy from passes and net front)
        # In a real scenario, we'd have more granular movement, but this fits the schema
        return {
            'away': {
                'net_front_traffic_pct': away_stats.get('net_front_traffic_pct', 0.0),
                'avg_goal_distance': away_stats.get('avg_shot_dist', 0.0),
                'entry_type_share': {
                    'carry': away_stats.get('entry_counts', {}).get('carry', 0),
                    'pass': away_stats.get('entry_counts', {}).get('pass', 0),
                    'dump': away_stats.get('entry_counts', {}).get('dump', 0)
                },
                'movement_metrics': {
                    'east_west': away_stats.get('avg_passes', 0.0) * 1.5, # Multiplier for volume
                    'north_south': 100 - (away_stats.get('avg_passes', 0.0) * 1.5)
                }
            },
            'home': {
                'net_front_traffic_pct': home_stats.get('net_front_traffic_pct', 0.0),
                'avg_goal_distance': home_stats.get('avg_shot_dist', 0.0),
                'entry_type_share': {
                    'carry': home_stats.get('entry_counts', {}).get('carry', 0),
                    'pass': home_stats.get('entry_counts', {}).get('pass', 0),
                    'dump': home_stats.get('entry_counts', {}).get('dump', 0)
                },
                'movement_metrics': {
                    'east_west': home_stats.get('avg_passes', 0.0) * 1.5,
                    'north_south': 100 - (home_stats.get('avg_passes', 0.0) * 1.5)
                }
            }
        }


if __name__ == "__main__":
    analyzer = SpriteGoalAnalyzer()
    result = analyzer.analyze_game_goals_by_team('2025020536')
    
    if result:
        print("Team Comparison:")
        for team_id, stats in result['stats'].items():
            print(f"\n{stats['abbrev']}:")
            print(f"  Avg Net-Front: {stats['avg_net_front']} players")
            print(f"  Net-Front Traffic %: {stats['net_front_traffic_pct']}%")
            print(f"  Avg Shot Dist: {stats['avg_shot_dist']} units")
            print(f"  Zone Entries: {stats['entry_counts']}")
            print(f"  Avg Passes: {stats['avg_passes']}")
    else:
        print("No data available")
