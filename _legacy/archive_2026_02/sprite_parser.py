"""
NHL Sprite Data Parser
Extracts shot release points from frame-by-frame tracking data
"""

import requests
import json

def get_sprite_data(game_id, event_id):
    """Fetch sprite tracking data for a specific event"""
    try:
        if not game_id or str(game_id).lower() == 'none' or str(game_id).strip() == '':
            print(f"DEBUG: Invalid game_id '{game_id}', skipping sprite fetch.")
            return None
            
        year = str(game_id)[:4]
        next_year = str(int(year) + 1)
        season = f"{year}{next_year}"
    except:
        season = "20252026"

    sprite_url = f'https://wsr.nhle.com/sprites/{season}/{game_id}/ev{event_id}.json'
    print(f"DEBUG: Fetching sprite from {sprite_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.nhl.com/',
        'Origin': 'https://www.nhl.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Connection': 'keep-alive'
    }
    
    try:
        response = requests.get(sprite_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error fetching sprite: {e}")
        return None

def extract_release_point(sprite_data):
    """Extract puck release point from sprite frames"""
    
    if not sprite_data or len(sprite_data) < 2:
        return None
    
    # Look for puck (id: 1) across frames
    puck_positions = []
    
    for frame in sprite_data:
        on_ice = frame.get('onIce', {})
        
        # Find puck (id 1 or empty sweater number)
        for player_id, player_data in on_ice.items():
            if (player_data.get('id') == 1 or 
                player_data.get('sweaterNumber') == '' or
                player_data.get('playerId') == ''):
                
                puck_positions.append({
                    'timestamp': frame.get('timeStamp'),
                    'x': player_data.get('x'),
                    'y': player_data.get('y')
                })
                break
    
    if puck_positions:
        # Release point = first puck position
        release = puck_positions[0]
        # Goal point = last puck position
        goal = puck_positions[-1]
        
        return {
            'release_point': {'x': release['x'], 'y': release['y']},
            'goal_point': {'x': goal['x'], 'y': goal['y']},
            'num_frames': len(puck_positions),
            'duration_ms': puck_positions[-1]['timestamp'] - puck_positions[0]['timestamp']
        }
    
    return None

def analyze_goal(game_id, event_id):
    """Full analysis of a goal with sprite data"""
    
    print(f"🎯 Analyzing Event {event_id} from Game {game_id}...")
    
    sprite_data = get_sprite_data(game_id, event_id)
    
    if not sprite_data:
        print("❌ Could not fetch sprite data")
        return None
    
    release_data = extract_release_point(sprite_data)
    
    if release_data:
        print(f"✅ Release Point: ({release_data['release_point']['x']:.1f}, {release_data['release_point']['y']:.1f})")
        print(f"🥅 Goal Point: ({release_data['goal_point']['x']:.1f}, {release_data['goal_point']['y']:.1f})")
        print(f"📊 Tracked {release_data['num_frames']} frames over {release_data['duration_ms']}ms")
        
        return release_data
    else:
        print("⚠️  Could not extract release point")
        return None


if __name__ == "__main__":
    # Test with the example from the screenshot
    analyze_goal('2025020536', '139')
