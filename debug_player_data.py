#!/usr/bin/env python3
"""
Debug script to examine the actual structure of play-by-play data
"""

import requests
import json

def debug_play_by_play_data(game_id):
    """Debug the structure of play-by-play data"""
    print(f"Debugging play-by-play data for game {game_id}...")
    
    play_by_play_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    
    try:
        response = requests.get(play_by_play_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Data fetched successfully")
            
            # Print top-level keys
            print(f"\nTop-level keys: {list(data.keys())}")
            
            # Examine plays structure
            if 'plays' in data:
                plays = data['plays']
                print(f"\nNumber of plays: {len(plays)}")
                
                # Look at first few plays
                print("\nFirst 3 plays structure:")
                for i, play in enumerate(plays[:3]):
                    print(f"\nPlay {i+1}:")
                    print(f"  Keys: {list(play.keys())}")
                    print(f"  Type: {play.get('typeDescKey', 'unknown')}")
                    print(f"  Period: {play.get('periodNumber', 'unknown')}")
                    
                    # Look for player information
                    if 'players' in play:
                        players = play['players']
                        print(f"  Players: {len(players)}")
                        for j, player in enumerate(players[:2]):  # First 2 players
                            print(f"    Player {j+1}: {player}")
                    else:
                        print("  No players key found")
                    
                    # Look for shot information
                    if 'xCoord' in play or 'yCoord' in play:
                        print(f"  Shot location: x={play.get('xCoord', 'N/A')}, y={play.get('yCoord', 'N/A')}")
                    
                    if 'shotType' in play:
                        print(f"  Shot type: {play.get('shotType', 'N/A')}")
            
            # Look for team information
            if 'awayTeam' in data:
                print(f"\nAway team: {data['awayTeam']}")
            if 'homeTeam' in data:
                print(f"Home team: {data['homeTeam']}")
            
            # Look for game information
            if 'game' in data:
                print(f"\nGame info: {data['game']}")
            
            return data
        else:
            print(f"❌ API returned {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    game_id = "2024030242"
    debug_play_by_play_data(game_id)
