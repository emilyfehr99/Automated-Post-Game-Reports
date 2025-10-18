#!/usr/bin/env python3
"""
Simple Fast API - Works with any player name
Get results in under a minute
"""

import requests
import json
import random

def get_player_stats_fast(player_name):
    """Get player stats quickly - works with any player name"""
    
    print(f"🏒 Getting {player_name} stats...")
    print("=" * 50)
    
    try:
        # Encode player name for URL
        encoded_name = player_name.replace(" ", "%20")
        
        # Make API request
        response = requests.get(f"http://localhost:8000/players/{encoded_name}")
        
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
            print(f"❌ {player_name} not found in API")
            print("🔄 Auto-generating stats for this player...")
            
            # Auto-generate stats for any player
            generate_player_stats(player_name)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔄 Auto-generating stats for this player...")
        generate_player_stats(player_name)

def generate_player_stats(player_name):
    """Generate realistic stats for any player"""
    
    # NHL teams and positions
    teams = ["ANA", "ARI", "BOS", "BUF", "CGY", "CAR", "CHI", "COL", "CBJ", "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NSH", "NJD", "NYI", "NYR", "OTT", "PHI", "PIT", "SJS", "SEA", "STL", "TBL", "TOR", "VAN", "VGK", "WSH", "WPG"]
    positions = ["C", "LW", "RW", "D", "G"]
    
    # Pick random team and position
    team = random.choice(teams)
    position = random.choice(positions)
    
    print(f"Name: {player_name}")
    print(f"Team: {team}")
    print(f"Position: {position}")
    print(f"5v5 Time on Ice: {round(random.uniform(100, 200), 1)} minutes")
    print()
    
    if position == "G":
        print("🏒 GOALIE STATS:")
        print(f"  Save Percentage: {round(random.uniform(0.900, 0.930), 3)}")
        print(f"  Goals Against Average: {round(random.uniform(2.0, 3.5), 2)}")
        print(f"  Wins: {random.randint(10, 45)}")
        print(f"  Shutouts: {random.randint(0, 8)}")
    else:
        # Generate realistic stats
        if position == "D":
            shots_per_60 = round(random.uniform(0.1, 0.8), 2)
            assists_per_60 = round(random.uniform(0.2, 0.9), 2)
            zone_entries = round(random.uniform(0.3, 0.8), 2)
            retrievals = round(random.uniform(2.5, 4.5), 2)
        else:
            shots_per_60 = round(random.uniform(0.5, 1.8), 2)
            assists_per_60 = round(random.uniform(0.4, 1.2), 2)
            zone_entries = round(random.uniform(0.8, 1.8), 2)
            retrievals = round(random.uniform(1.5, 3.0), 2)
        
        print("📊 GENERAL OFFENSE:")
        print(f"  Shots/60: {shots_per_60}")
        print(f"  Shot Assists/60: {assists_per_60}")
        print(f"  Total Shot Contributions/60: {round(shots_per_60 + assists_per_60, 2)}")
        print(f"  Chances/60: {round(shots_per_60 * random.uniform(0.7, 1.3), 2)}")
        print(f"  Chance Assists/60: {round(assists_per_60 * random.uniform(0.8, 1.4), 2)}")
        print()
        
        print(" PASSING:")
        print(f"  High Danger Assists/60: {round(assists_per_60 * random.uniform(0.8, 1.2), 2)}")
        print()
        
        print("🏃 ZONE ENTRIES:")
        print(f"  Zone Entries/60: {zone_entries}")
        print(f"  Controlled Entry %: {round(random.uniform(0.25, 0.65), 2):.1%}")
        print(f"  Controlled Entry with Chance %: {round(random.uniform(0.15, 0.35), 2):.1%}")
        print()
        
        print("🛡️  DEFENSIVE ZONE PLAY:")
        print(f"  DZ Puck Touches/60: {round(retrievals * random.uniform(0.8, 1.2), 2)}")
        print(f"  Retrievals/60: {retrievals}")
        print(f"  Successful Retrieval %: {round(random.uniform(0.55, 0.85), 2):.1%}")
        print(f"  Exits/60: {round(random.uniform(0.1, 0.4), 2)}")
        print(f"  Botched Retrievals/60: {round(random.uniform(-4.0, -1.5), 2)}")
    
    print(f"\n✅ {player_name} stats generated successfully!")
    print("🤖 These are realistic but auto-generated stats")

def main():
    """Main function"""
    
    print("🏒 SIMPLE FAST API")
    print("=" * 50)
    
    # 🎯 ENTER ANY PLAYER NAME HERE!
    player_name = input("Enter player name: ")  # <-- Type any player name you want!
    
    # Get player stats quickly
    get_player_stats_fast(player_name)

if __name__ == "__main__":
    main()
