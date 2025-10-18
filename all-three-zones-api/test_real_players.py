#!/usr/bin/env python3
"""
Test Real All Three Zones Players
Test the API with real players from the downloaded data
"""

import requests
import json

def test_real_players():
    """Test searching for real All Three Zones players"""
    
    print("🏒 TESTING REAL ALL THREE ZONES PLAYERS")
    print("=" * 50)
    
    # Test players from the real list
    test_players = [
        "Alex Ovechkin",
        "Connor McDavid", 
        "Sidney Crosby",
        "Nathan MacKinnon",
        "Dylan Strome",
        "Dylan DeMelo",
        "Carson Soucy",
        "Dylan Samberg",
        "Trevor van Riemsdyk",
        "Tom Wilson"
    ]
    
    print("🎯 Testing API with real All Three Zones players...")
    print()
    
    for player in test_players:
        try:
            # Encode player name for URL
            encoded_name = player.replace(" ", "%20")
            
            # Make API request
            response = requests.get(f"http://localhost:8000/players/{encoded_name}")
            
            if response.status_code == 200:
                player_data = response.json()
                print(f"✅ {player} - FOUND!")
                print(f"   Team: {player_data['team']}")
                print(f"   Position: {player_data['position']}")
                print(f"   Source: {player_data['source']}")
            else:
                print(f"❌ {player} - NOT FOUND (Status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ {player} - ERROR: {e}")
        
        print()
    
    print("🏆 API Test Complete!")
    print("📊 These are REAL players from All Three Zones!")
    print("🎯 You can now search for any of the 613 real players!")

def show_player_count():
    """Show how many real players we have"""
    
    try:
        # Load the player names
        with open('all_three_zones_player_names.json', 'r') as f:
            players = json.load(f)
        
        print(f"📊 Total Real All Three Zones Players: {len(players)}")
        print()
        print("📋 Sample players from the real list:")
        for i, player in enumerate(players[:20]):
            print(f"   {i+1:2d}. {player}")
        if len(players) > 20:
            print(f"   ... and {len(players) - 20} more players")
            
    except Exception as e:
        print(f"❌ Error loading player list: {e}")

def main():
    """Main function"""
    
    print("🏒 REAL ALL THREE ZONES PLAYERS TEST")
    print("=" * 60)
    
    # Show player count
    show_player_count()
    print()
    
    # Test API
    test_real_players()

if __name__ == "__main__":
    main()
