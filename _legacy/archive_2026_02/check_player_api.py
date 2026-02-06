#!/usr/bin/env python3
"""
Test script to check what fields are actually being returned by the live API
"""
import requests
import json

print("Testing Player Stats API Response...")
print("=" * 80)

url = "https://nhl-analytics-api.onrender.com/api/player-stats?season=2025&type=regular&situation=all"

try:
    response = requests.get(url, timeout=30)
    print(f"Status: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        
        if data and len(data) > 0:
            # Get first player
            first_player = data[0]
            
            print(f"Sample Player: {first_player.get('name', 'Unknown')}")
            print(f"Team: {first_player.get('team', 'Unknown')}")
            print(f"Total fields returned: {len(first_player.keys())}\n")
            
            print("All field names:")
            print("-" * 80)
            for i, field in enumerate(sorted(first_player.keys()), 1):
                value = first_player[field]
                print(f"{i:3}. {field:40} = {value}")
            
            print("\n" + "=" * 80)
            print("Checking specific fields the frontend expects:")
            print("-" * 80)
            
            expected_fields = [
                'points_per_game', 'hits', 'hits_per_game', 'blocks', 
                'pim', 'takeaways', 'giveaways', 'fo_pct'
            ]
            
            for field in expected_fields:
                value = first_player.get(field, 'FIELD NOT FOUND')
                print(f"{field:25} = {value}")
                
        else:
            print("No player data returned!")
    else:
        print(f"Error: {response.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")
