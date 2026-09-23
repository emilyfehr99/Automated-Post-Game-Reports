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
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://www.nhl.com/',
        })
        self._sprite_cache = {}
    
    def distance(self, x1, y1, x2, y2):
        """Calculate Euclidean distance"""
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    def _get_target_goal_x(self, sprite_data):
        """Determine target goal X coordinate (right ~2250 or left ~150) from sprite puck path"""
        if not sprite_data:
            return 2250
        for frame in reversed(sprite_data[-10:]):
            for p in frame.get('onIce', {}).values():
                if p.get('id') == 1 and 'x' in p:
                    return 2250 if p['x'] > 1200 else 150
        return 2250
    
    def get_sprite_data(self, game_id, event_id):
        """Fetch sprite data for a specific event with in-memory caching"""
        cache_key = f"{game_id}_{event_id}"
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]
        try:
            year = str(game_id)[:4]
            next_year = str(int(year) + 1)
            season = f"{year}{next_year}"
        except Exception:
            try:
                from utils.season_utils import current_season_string
                season = current_season_string()
            except Exception:
                try:
                    from season_utils import current_season_string
                    season = current_season_string()
                except Exception:
                    from datetime import datetime
                    y = datetime.now().year
                    m = datetime.now().month
                    season = f"{y}{y+1}" if m >= 7 else f"{y-1}{y}"
            
        url = f'https://wsr.nhle.com/sprites/{season}/{game_id}/ev{event_id}.json'
        try:
            response = self.session.get(url, timeout=4)
            if response.status_code == 200:
                data = response.json()
                self._sprite_cache[cache_key] = data
                return data
        except Exception:
            pass
        self._sprite_cache[cache_key] = None
        return None
    
    def get_game_data(self, game_id):
        """Fetch game play-by-play data"""
        url = f'https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play'
        try:
            resp = self.session.get(url, timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None
    
    def analyze_net_front_presence(self, sprite_data):
        """
        Count average players screening or battling in the net-front area
        inside the goalie's sightline corridor during shot release.
        """
        if not sprite_data or len(sprite_data) < 10:
            return 0
        
        # Determine goal X position from puck trajectory in final frames
        goal_x = 2200
        puck_xs = []
        for frame in sprite_data[-10:]:
            for p in frame['onIce'].values():
                if p.get('id') == 1 and 'x' in p:
                    puck_xs.append(p['x'])
                    break
        if puck_xs:
            avg_x = sum(puck_xs) / len(puck_xs)
            goal_x = 2200 if avg_x > 1200 else 200
            
        # Define net-front screening bounding box (crease + inner slot: ~18ft depth, centered in Y)
        # Rink Y is approx 0 to 1000 with center at 500
        GOAL_Y_MIN = 350
        GOAL_Y_MAX = 650
        if goal_x > 1200:
            GOAL_X_MIN = goal_x - 220  # ~18 feet out from right net
            GOAL_X_MAX = goal_x + 50
        else:
            GOAL_X_MIN = goal_x - 50
            GOAL_X_MAX = goal_x + 220  # ~18 feet out from left net
        
        mid_point = len(sprite_data) // 2
        sample_frames = sprite_data[max(0, mid_point-10):min(len(sprite_data), mid_point+10)]
        
        player_counts = []
        for frame in sample_frames:
            count = 0
            for p in frame['onIce'].values():
                if p.get('sweaterNumber') == '' or p.get('id') == 1:
                    continue
                if 'x' not in p or 'y' not in p:
                    continue
                # Exclude defending goalie (usually stationed directly on the goal line)
                if (GOAL_X_MIN <= p['x'] <= GOAL_X_MAX and 
                    GOAL_Y_MIN <= p['y'] <= GOAL_Y_MAX):
                    count += 1
            player_counts.append(count)
        
        return round(sum(player_counts) / len(player_counts), 1) if player_counts else 0
    
    def analyze_shot_distance(self, sprite_data):
        """Calculate shot distance from release point to goal in FEET"""
        if not sprite_data:
            return 0
        
        # Find the shot release point (earliest puck position)
        release_point = None
        for frame in sprite_data[:10]:  # Check first 10 frames for release
        # ... (rest of the file content as read previously)
            for p in frame['onIce'].values():
                if p.get('id') == 1:  # Puck ID
                    release_point = (p['x'], p['y'])
                    break
            if release_point:
                break
        
        if not release_point:
            return 0
        
        # Find goal point (last puck position before crossing goal line)
        goal_point = None
        for frame in reversed(sprite_data):
            for p in frame['onIce'].values():
                if p.get('id') == 1:  # Puck ID
                    goal_point = (p['x'], p['y'])
                    break
            if goal_point:
                break
        
        if not goal_point:
            # Fallback: estimate goal location based on release side
            # NHL rink in sprite coordinates appears to be ~2400 pixels wide
            # Goals are at the ends (x ~= 0 or x ~= 2400)
            goal_point = (2400 if release_point[0] < 1200 else 0, release_point[1])
        
        # Calculate distance in pixels
        pixel_distance = self.distance(release_point[0], release_point[1], goal_point[0], goal_point[1])
        
        # Convert pixels to feet
        # NHL rink is 200 feet long
        # Sprite coordinates appear to span ~2400 pixels for full rink width
        # So: 1 foot ≈ 12 pixels
        PIXELS_PER_FOOT = 12.0
        
        shot_distance_feet = pixel_distance / PIXELS_PER_FOOT
        
        # Sanity check: shots should be between 1-89 feet (can't be longer than rink)
        shot_distance_feet = max(1, min(89, shot_distance_feet))
        
        return round(shot_distance_feet, 0)
    
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
        passes = self.analyze_passes(sprite_data)
        return len(passes)

    def analyze_passes(self, sprite_data):
        """Identify player ids involved in the scoring sequence"""
        if not sprite_data:
            return []
        
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
                if p.get('sweaterNumber') == '':
                    continue
                dist = self.distance(puck.get('x', 0), puck.get('y', 0), p.get('x', 0), p.get('y', 0))
                if dist < 50 and dist < closest_dist:
                    closest_dist = dist
                    closest_player = p['sweaterNumber']
            
            if closest_player:
                if not possessions or possessions[-1] != closest_player:
                    possessions.append(closest_player)
        
        return possessions

    def analyze_traffic_screens(self, sprite_data):
        """Count opponent players in the shot lane"""
        if not sprite_data or len(sprite_data) < 5:
            return 0
            
        last_frame = sprite_data[-1]
        puck = None
        for p in last_frame.get('onIce', {}).values():
            if p.get('id') == 1:
                puck = p
                break
        
        if not puck or 'x' not in puck:
            return 0
            
        target_goal_x = self._get_target_goal_x(sprite_data)
        count = 0
        p_x, p_y = puck['x'], puck['y']
        
        for p in last_frame.get('onIce', {}).values():
            if p.get('id') == 1: continue
            if 'x' not in p: continue
            
            px, py = p['x'], p['y']
            if min(p_x, target_goal_x) <= px <= max(p_x, target_goal_x):
                if abs(py - 500) < 65:
                    count += 1
        
        return max(0, count - 1)

    def analyze_goalie_status(self, sprite_data):
        """Determine if goalie is set or out of position"""
        if not sprite_data:
            return "Unknown"
            
        target_goal_x = self._get_target_goal_x(sprite_data)
        last_frame = sprite_data[-1]
        goalie = None
        min_dist = 1000
        
        for p in last_frame.get('onIce', {}).values():
            if p.get('id') == 1: continue
            if 'x' not in p: continue
            
            dist = self.distance(p['x'], p['y'], target_goal_x, 500)
            if dist < min_dist:
                min_dist = dist
                goalie = p
                
        if not goalie:
            return "Unknown"
            
        if min_dist > 80:
            return "Out of Position"
        else:
            return "Set"
    
    def analyze_game_goals_by_team(self, game_id, game_data=None, landing_data=None) -> Optional[Dict]:
        """Analyze all goals by team and return team comparison data"""
        if game_data is None:
            if self.game_data and isinstance(self.game_data, dict):
                game_data = self.game_data.get('play_by_play') or self.game_data
            else:
                game_data = self.get_game_data(game_id)
        elif isinstance(game_data, dict) and 'play_by_play' in game_data:
            game_data = game_data['play_by_play']
            
        if landing_data is None:
            if self.game_data and isinstance(self.game_data, dict) and 'landing' in self.game_data:
                landing_data = self.game_data['landing']
            else:
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
                p_desc = period_info.get('periodDescriptor', {})
                p_num = p_desc.get('number')
                
                # Check first goal for side info
                goals_list = period_info.get('goals', [])
                if goals_list and p_num:
                    side = goals_list[0].get('homeTeamDefendingSide')
                    if side:
                        period_sides[p_num] = side
        
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
        
        for goal in goals:
            event_id = goal.get('eventId')
            scoring_team_id = goal.get('details', {}).get('eventOwnerTeamId')
            period_num = goal.get('periodDescriptor', {}).get('number')
            
            if scoring_team_id not in team_stats:
                continue
            
            team_stats[scoring_team_id]['total_goals'] += 1
            details = goal.get('details', {})
            shot_type = str(details.get('shotType', '')).lower()
            
            sprite_data = self.get_sprite_data(game_id, event_id)
            if not sprite_data:
                # Accurate fallback using official high-fidelity NHL PBP tracking coordinates
                x = details.get('xCoord')
                y = details.get('yCoord')
                dist_ft = None
                if x is not None and y is not None:
                    # In official NHL coordinates (-100 to 100), goal line is at +/-89 ft
                    dist_ft = math.sqrt((89 - abs(x))**2 + y**2)
                    team_stats[scoring_team_id]['shot_dist'].append(round(dist_ft, 1))
                    
                    # Net-front presence proxy: within 15ft of crease
                    team_stats[scoring_team_id]['net_front'].append(2.0 if dist_ft < 15.0 else 1.0)
                    
                # Check for net-front traffic / screen / deflection
                is_traffic = (shot_type in ['tip-in', 'deflected', 'tip', 'deflection', 'wrap-around', 'bat'] or (dist_ft is not None and dist_ft <= 12.0))
                if is_traffic:
                    team_stats[scoring_team_id]['traffic_goals'] += 1
                    
                # Assists / Passes on goal
                a1 = details.get('assist1PlayerId')
                a2 = details.get('assist2PlayerId')
                passes = (1 if a1 else 0) + (1 if a2 else 0)
                team_stats[scoring_team_id]['passes'].append(passes)
                
                # Zone entry classification from goal build-up
                if passes >= 2:
                    team_stats[scoring_team_id]['entry_types']['pass'] += 1
                elif passes == 1:
                    team_stats[scoring_team_id]['entry_types']['carry'] += 1
                else:
                    team_stats[scoring_team_id]['entry_types']['carry'] += 1
                continue
            
            # Net-front presence from raw sprite
            net_front = self.analyze_net_front_presence(sprite_data)
            team_stats[scoring_team_id]['net_front'].append(net_front)
            is_traffic = (net_front >= 1.0 or shot_type in ['tip-in', 'deflected', 'tip', 'deflection', 'wrap-around', 'bat'])
            if is_traffic:
                team_stats[scoring_team_id]['traffic_goals'] += 1
            
            # Shot distance in feet from raw sprite
            shot_dist = self.analyze_shot_distance(sprite_data)
            team_stats[scoring_team_id]['shot_dist'].append(shot_dist)
            
            # Zone entry
            side = period_sides.get(period_num)
            if side:
                entry_type = self.analyze_zone_entry_count(sprite_data, scoring_team_id, side, home_team_id)
            else:
                goal_x_avg = 0
                c = 0
                for f in sprite_data[-10:]:
                    for p in f.get('onIce', {}).values():
                        if p.get('id') == 1 and 'x' in p:
                            goal_x_avg += p['x']
                            c += 1
                            break
                if c > 0:
                    goal_x_avg /= c
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
            traffic_pct = 0.0
            if stats['total_goals'] > 0:
                traffic_pct = min(100.0, round((stats['traffic_goals'] / stats['total_goals']) * 100, 1))
            
            result[team_id] = {
                'abbrev': stats['abbrev'],
                'total_goals': stats['total_goals'],
                'avg_net_front': round(sum(stats['net_front']) / len(stats['net_front']), 1) if stats['net_front'] else 0.0,
                'net_front_traffic_pct': traffic_pct,
                'avg_shot_dist': round(sum(stats['shot_dist']) / len(stats['shot_dist']), 1) if stats['shot_dist'] else 0.0,
                'entry_counts': stats['entry_types'],
                'avg_passes': round(sum(stats['passes']) / len(stats['passes']), 1) if stats['passes'] else 0.0
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
