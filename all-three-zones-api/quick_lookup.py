#!/usr/bin/env python3
"""
Quick Player Lookup - One-liner style
Just paste a player name and get instant data!
"""

import requests
import sys

def quick_lookup(player_name):
    """Quick lookup for a player"""
    try:
        # Try to get from API
        response = requests.get(f"http://localhost:8000/players/{player_name}")
        
        if response.status_code == 200:
            player = response.json()
            print(f"🏒 {player['name']} ({player['team']}) - {player['position']}")
            print(f"Shots/60: {player['stats']['general_offense']['shots_per_60']}")
            print(f"Retrievals/60: {player['stats']['dz_retrievals_exits']['retrievals_per_60']}")
            print(f"Successful Retrieval %: {player['stats']['dz_retrievals_exits']['successful_retrieval_percent']:.1%}")
            return player
        else:
            print(f"❌ Player '{player_name}' not found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        player_name = " ".join(sys.argv[1:])
        quick_lookup(player_name)
    else:
        print("Usage: python3 quick_lookup.py 'Player Name'")
        print("Example: python3 quick_lookup.py 'Carson Soucy'") 