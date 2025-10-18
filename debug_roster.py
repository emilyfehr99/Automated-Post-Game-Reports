#!/usr/bin/env python3
"""
Debug script to examine the roster structure and player name resolution
"""

import requests
import json

def debug_roster_structure(game_id):
    """Debug the roster structure to understand player name resolution"""
    print(f"Debugging roster structure for game {game_id}...")
    
    play_by_play_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    
    try:
        response = requests.get(play_by_play_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Data fetched successfully")
            
            # Check if rosterSpots exists
            if 'rosterSpots' in data:
                roster_spots = data['rosterSpots']
                print(f"\nRoster spots found: {len(roster_spots)}")
                
                # Look at first few roster spots
                print("\nFirst 5 roster spots:")
                for i, spot in enumerate(roster_spots[:5]):
                    print(f"  Spot {i+1}: {spot}")
                
                # Create player ID to name mapping
                player_mapping = {}
                for spot in roster_spots:
                    player_id = spot.get('playerId')
                    player_name = spot.get('playerName')
                    if player_id and player_name:
                        player_mapping[player_id] = player_name
                
                print(f"\nPlayer mapping created: {len(player_mapping)} players")
                print("Sample mappings:")
                for i, (player_id, name) in enumerate(list(player_mapping.items())[:5]):
                    print(f"  {player_id}: {name}")
                
                return player_mapping
            else:
                print("❌ No rosterSpots found in data")
                return None
        else:
            print(f"❌ API returned {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    game_id = "2024030242"
    player_mapping = debug_roster_structure(game_id)
