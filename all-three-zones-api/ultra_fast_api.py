#!/usr/bin/env python3
"""
Ultra Fast API - Pre-loaded Data
Instant results, no waiting
"""

import requests
import json
import time

def get_player_stats_ultra_fast(player_name):
    """Get player stats instantly from pre-loaded data"""
    
    print(f"🏒 Getting {player_name} stats...")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Encode player name for URL
        encoded_name = player_name.replace(" ", "%20")
        
        # Make API request with timeout
        response = requests.get(f"http://localhost:8000/players/{encoded_name}", timeout=10)
        
        end_time = time.time()
        print(f"⏱️  API Response Time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            player_data = response.json()
            
            print(f"Name: {player_data['name']}")
            print(f"Team: {player_data['team']}")
            print(f"Position: {player_data['position']}")
            print(f"5v5 Time on Ice: {player_data['5v5_toi']} minutes")
            print()

            # Check if it's a goalie
            if player_data['position'] == "G":
                goalie_stats = player_data['stats']['goalie_stats']
                print("🏒 GOALIE STATS:")
                print(f"  Save Percentage: {goalie_stats['save_percentage']:.3f}")
                print(f"  Goals Against Average: {goalie_stats['goals_against_average']}")
                print(f"  Wins: {goalie_stats['wins']}")
                print(f"  Shutouts: {goalie_stats['shutouts']}")
                return

            # General Offense
            offense = player_data['stats']['general_offense']
            print("📊 GENERAL OFFENSE:")
            print(f"  Shots/60: {offense['shots_per_60']}")
            print(f"  Shot Assists/60: {offense['shot_assists_per_60']}")
            print(f"  Total Shot Contributions/60: {offense['total_shot_contributions_per_60']}")
            print(f"  Chances/60: {offense['chances_per_60']}")
            print(f"  Chance Assists/60: {offense['chance_assists_per_60']}")
            print()

            # Passing
            passing = player_data['stats']['passing']
            print(" PASSING:")
            print(f"  High Danger Assists/60: {passing['high_danger_assists_per_60']}")
            print()

            # Zone Entries
            zone_entries = player_data['stats']['zone_entries']
            print("🏃 ZONE ENTRIES:")
            print(f"  Zone Entries/60: {zone_entries['zone_entries_per_60']}")
            print(f"  Controlled Entry %: {zone_entries['controlled_entry_percent']:.1%}")
            print(f"  Controlled Entry with Chance %: {zone_entries['controlled_entry_with_chance_percent']:.1%}")
            print()

            # DZ Retrievals & Exits
            defense = player_data['stats']['dz_retrievals_exits']
            print("🛡️  DEFENSIVE ZONE PLAY:")
            print(f"  DZ Puck Touches/60: {defense['dz_puck_touches_per_60']}")
            print(f"  Retrievals/60: {defense['retrievals_per_60']}")
            print(f"  Successful Retrieval %: {defense['successful_retrieval_percent']:.1%}")
            print(f"  Exits/60: {defense['exits_per_60']}")
            print(f"  Botched Retrievals/60: {defense['botched_retrievals_per_60']}")

            print(f"\n✅ {player_name} data retrieved successfully!")
            print(" This is a REAL All Three Zones player!")
            
        else:
            print(f"❌ {player_name} not found in API (Status: {response.status_code})")
            print("📋 Try one of these players:")
            print("   - Connor McDavid")
            print("   - Sidney Crosby") 
            print("   - Alex Ovechkin")
            print("   - Dylan Strome")
            print("   - Neal Pionk")
            
    except requests.exceptions.Timeout:
        print("⏰ API request timed out - server is too slow")
        print("💡 Try restarting the API server")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the API server is running")

def test_api_speed():
    """Test the API speed with multiple players"""
    
    test_players = ["Connor McDavid", "Sidney Crosby", "Alex Ovechkin"]
    
    print("🏒 TESTING API SPEED")
    print("=" * 50)
    
    for player in test_players:
        print(f"\n🔍 Testing: {player}")
        start_time = time.time()
        
        try:
            encoded_name = player.replace(" ", "%20")
            response = requests.get(f"http://localhost:8000/players/{encoded_name}", timeout=5)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                print(f"✅ Found in {response_time:.2f} seconds")
            else:
                print(f"❌ Not found in {response_time:.2f} seconds")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🏆 Speed test complete!")

def main():
    """Main function"""
    
    print("🏒 ULTRA FAST API")
    print("=" * 50)
    
    # 🎯 ENTER ANY PLAYER NAME HERE!
    player_name = "Neal Pionk"  # <-- Change this to any player you want!
    
    # Get player stats quickly
    get_player_stats_ultra_fast(player_name)

if __name__ == "__main__":
    main()























