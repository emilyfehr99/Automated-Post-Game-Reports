#!/usr/bin/env python3
"""
Verify NHL Player ID to Name Mappings
This script verifies that our player ID mappings are accurate
"""

import requests
import json
import time

def verify_player_mapping(player_id, expected_name):
    """Verify a single player ID mapping"""
    try:
        # Try the official NHL API
        url = f"https://statsapi.web.nhl.com/api/v1/people/{player_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'people' in data and len(data['people']) > 0:
                player = data['people'][0]
                actual_name = player.get('fullName', 'Unknown')
                first_name = player.get('firstName', 'Unknown')
                last_name = player.get('lastName', 'Unknown')
                
                print(f"✅ ID {player_id}: {actual_name} (Expected: {expected_name})")
                if actual_name.lower() == expected_name.lower():
                    return True
                else:
                    print(f"   ❌ MISMATCH: Expected '{expected_name}', got '{actual_name}'")
                    return False
            else:
                print(f"❌ ID {player_id}: No player data found")
                return False
        else:
            print(f"❌ ID {player_id}: API error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ID {player_id}: Error - {e}")
        return False

def main():
    """Verify all our player mappings"""
    print("🏒 VERIFYING NHL PLAYER ID MAPPINGS 🏒")
    print("=" * 50)
    
    # Our current mappings to verify
    player_mappings = {
        8478402: "Connor McDavid",
        8477493: "Ryan McLeod", 
        8475218: "Ryan Nugent-Hopkins",
        8470621: "Zach Hyman",
        8473419: "Evan Bouchard",
        8475169: "Darnell Nurse",
        8475683: "Stuart Skinner",
        8477409: "Cody Ceci",
        8478859: "Warren Foegele",
        8477934: "Leon Draisaitl",
        8477406: "Sam Bennett",
        8477953: "Sam Reinhart",
        8477933: "Jonathan Huberdeau",
        8477935: "Matthew Tkachuk",
        8479314: "Brandon Montour",
    }
    
    correct_count = 0
    total_count = len(player_mappings)
    
    for player_id, expected_name in player_mappings.items():
        if verify_player_mapping(player_id, expected_name):
            correct_count += 1
        time.sleep(0.5)  # Be nice to the API
    
    print("\n" + "=" * 50)
    print(f"📊 VERIFICATION RESULTS: {correct_count}/{total_count} correct")
    
    if correct_count == total_count:
        print("🎉 ALL MAPPINGS ARE ACCURATE!")
    else:
        print("⚠️  SOME MAPPINGS NEED CORRECTION")

if __name__ == "__main__":
    main()
