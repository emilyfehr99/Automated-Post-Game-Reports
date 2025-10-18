#!/usr/bin/env python3
"""
Debug script to check NHL API logo formats
"""

import requests
import json

def debug_nhl_logos(game_id):
    """Debug NHL API logo formats"""
    print(f"Debugging NHL API logos for game {game_id}...")
    
    play_by_play_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    
    try:
        response = requests.get(play_by_play_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Data fetched successfully")
            
            # Check team logos
            away_team = data.get('awayTeam', {})
            home_team = data.get('homeTeam', {})
            
            print(f"\nAway Team ({away_team.get('abbrev', 'Unknown')}):")
            print(f"  Logo URL: {away_team.get('logo', 'No logo')}")
            print(f"  Dark Logo URL: {away_team.get('darkLogo', 'No dark logo')}")
            
            print(f"\nHome Team ({home_team.get('abbrev', 'Unknown')}):")
            print(f"  Logo URL: {home_team.get('logo', 'No logo')}")
            print(f"  Dark Logo URL: {home_team.get('darkLogo', 'No dark logo')}")
            
            # Check player headshots
            if 'rosterSpots' in data:
                roster_spots = data['rosterSpots']
                print(f"\nPlayer headshots (first 5 players):")
                for i, spot in enumerate(roster_spots[:5]):
                    player_name = f"{spot.get('firstName', {}).get('default', '')} {spot.get('lastName', {}).get('default', '')}"
                    headshot_url = spot.get('headshot', '')
                    print(f"  {i+1}. {player_name}: {headshot_url}")
            
            # Test downloading a logo
            if away_team.get('logo'):
                print(f"\nTesting logo download for {away_team.get('abbrev')}...")
                logo_response = requests.get(away_team.get('logo'), timeout=10)
                print(f"  Status: {logo_response.status_code}")
                print(f"  Content-Type: {logo_response.headers.get('content-type', 'Unknown')}")
                print(f"  Content-Length: {logo_response.headers.get('content-length', 'Unknown')}")
                
                if logo_response.status_code == 200:
                    # Check first few bytes to identify format
                    content = logo_response.content[:20]
                    print(f"  First 20 bytes: {content}")
                    
                    # Check if it's SVG
                    if content.startswith(b'<svg') or b'<svg' in content:
                        print("  Format: SVG")
                    elif content.startswith(b'\x89PNG'):
                        print("  Format: PNG")
                    elif content.startswith(b'\xff\xd8\xff'):
                        print("  Format: JPEG")
                    else:
                        print(f"  Format: Unknown (starts with: {content[:10]})")
            
            return data
        else:
            print(f"❌ API returned {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    game_id = "2024030242"
    debug_nhl_logos(game_id)
