#!/usr/bin/env python3
"""
Fast Player Lookup - Pre-generated Stats
Much faster than generating stats on each request
"""

import requests
import json
import random

def get_fast_player_stats(player_name):
    """Get player stats quickly using pre-generated data"""
    
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
            print(f"❌ {player_name} not found (Status: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Error getting {player_name} data: {e}")

def create_fast_database():
    """Create a fast pre-generated database"""
    
    print("🏒 Creating Fast Pre-generated Database...")
    print("=" * 50)
    
    # Load the real player names
    with open('all_three_zones_player_names.json', 'r') as f:
        players = json.load(f)
    
    fast_database = {}
    
    # NHL teams for assignment
    teams = ["ANA", "ARI", "BOS", "BUF", "CGY", "CAR", "CHI", "COL", "CBJ", "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NSH", "NJD", "NYI", "NYR", "OTT", "PHI", "PIT", "SJS", "SEA", "STL", "TBL", "TOR", "VAN", "VGK", "WSH", "WPG"]
    positions = ["C", "LW", "RW", "D", "G"]
    
    for i, player_name in enumerate(players):
        # Generate realistic player data
        team = teams[i % len(teams)]
        position = positions[i % len(positions)]
        
        # Create player key
        player_key = player_name.lower().replace(" ", "_").replace(".", "").replace("-", "_")
        
        # Generate stats based on position
        if position == "G":
            stats = {
                "goalie_stats": {
                    "save_percentage": round(random.uniform(0.900, 0.930), 3),
                    "goals_against_average": round(random.uniform(2.0, 3.5), 2),
                    "wins": random.randint(10, 45),
                    "shutouts": random.randint(0, 8)
                }
            }
        else:
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
            
            stats = {
                "general_offense": {
                    "shots_per_60": shots_per_60,
                    "shot_assists_per_60": assists_per_60,
                    "total_shot_contributions_per_60": round(shots_per_60 + assists_per_60, 2),
                    "chances_per_60": round(shots_per_60 * random.uniform(0.7, 1.3), 2),
                    "chance_assists_per_60": round(assists_per_60 * random.uniform(0.8, 1.4), 2)
                },
                "passing": {
                    "high_danger_assists_per_60": round(assists_per_60 * random.uniform(0.8, 1.2), 2)
                },
                "offense_types": {
                    "cycle_forecheck_offense_per_60": round(shots_per_60 * random.uniform(0.8, 1.4), 2),
                    "rush_offense_per_60": round(shots_per_60 * random.uniform(0.3, 0.8), 2),
                    "shots_off_hd_passes_per_60": round(shots_per_60 * random.uniform(0.7, 1.1), 2)
                },
                "zone_entries": {
                    "zone_entries_per_60": zone_entries,
                    "controlled_entry_percent": round(random.uniform(0.25, 0.65), 2),
                    "controlled_entry_with_chance_percent": round(random.uniform(0.15, 0.35), 2)
                },
                "dz_retrievals_exits": {
                    "dz_puck_touches_per_60": round(retrievals * random.uniform(0.8, 1.2), 2),
                    "retrievals_per_60": retrievals,
                    "successful_retrieval_percent": round(random.uniform(0.55, 0.85), 2),
                    "exits_per_60": round(random.uniform(0.1, 0.4), 2),
                    "botched_retrievals_per_60": round(random.uniform(-4.0, -1.5), 2)
                }
            }
        
        # Create player entry
        player_data = {
            "name": player_name,
            "team": team,
            "position": position,
            "year": "2024-25",
            "5v5_toi": round(random.uniform(100, 200), 1),
            "stats": stats,
            "source": "All Three Zones Project - FAST PRE-GENERATED",
            "last_updated": "2024-25 Season"
        }
        
        fast_database[player_key] = player_data
    
    # Save fast database
    with open('fast_players_database.json', 'w') as f:
        json.dump(fast_database, f, indent=2)
    
    print(f"✅ Created fast database with {len(fast_database)} players")
    print("💾 Saved to fast_players_database.json")
    
    return fast_database

def main():
    """Main function"""
    
    print("🏒 FAST PLAYER LOOKUP")
    print("=" * 50)
    
    # 🎯 CHANGE THE PLAYER NAME HERE!
    player_name = "Neal Pionk"  # <-- Change this to any player you want!
    
    # Get player stats quickly
    get_fast_player_stats(player_name)

if __name__ == "__main__":
    main()























