#!/usr/bin/env python3
"""
Debug script to examine the details structure of play-by-play data
"""

import requests
import json

def debug_play_details(game_id):
    """Debug the details structure of plays"""
    print(f"Debugging play details for game {game_id}...")
    
    play_by_play_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    
    try:
        response = requests.get(play_by_play_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            plays = data['plays']
            
            print(f"Examining {len(plays)} plays for details structure...")
            
            # Look for plays with details
            plays_with_details = [play for play in plays if 'details' in play]
            print(f"Plays with details: {len(plays_with_details)}")
            
            # Examine different types of plays
            play_types = {}
            for play in plays:
                play_type = play.get('typeDescKey', 'unknown')
                if play_type not in play_types:
                    play_types[play_type] = []
                play_types[play_type].append(play)
            
            print(f"\nPlay types found: {list(play_types.keys())}")
            
            # Look at specific play types
            interesting_types = ['goal', 'shot-on-goal', 'missed-shot', 'hit', 'faceoff', 'penalty']
            
            for play_type in interesting_types:
                if play_type in play_types:
                    print(f"\n=== {play_type.upper()} ===")
                    sample_play = play_types[play_type][0]
                    print(f"Keys: {list(sample_play.keys())}")
                    
                    if 'details' in sample_play:
                        details = sample_play['details']
                        print(f"Details keys: {list(details.keys())}")
                        
                        # Look for player information in details
                        if 'players' in details:
                            players = details['players']
                            print(f"Players in details: {len(players)}")
                            for i, player in enumerate(players[:2]):
                                print(f"  Player {i+1}: {player}")
                        else:
                            print("No players in details")
                        
                        # Look for other interesting fields
                        for key in ['xCoord', 'yCoord', 'shotType', 'penaltyMinutes']:
                            if key in details:
                                print(f"  {key}: {details[key]}")
                    else:
                        print("No details found")
            
            # Look for plays with coordinates
            plays_with_coords = []
            for play in plays:
                if 'details' in play:
                    details = play['details']
                    if 'xCoord' in details or 'yCoord' in details:
                        plays_with_coords.append(play)
            
            print(f"\nPlays with coordinates: {len(plays_with_coords)}")
            if plays_with_coords:
                sample_shot = plays_with_coords[0]
                print(f"Sample shot play: {sample_shot}")
            
            return data
        else:
            print(f"❌ API returned {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    game_id = "2024030242"
    debug_play_details(game_id)
