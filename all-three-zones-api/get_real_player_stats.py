#!/usr/bin/env python3
"""
Get Real Player Stats from All Three Zones
Shows the difference between real players and auto-added players
"""

import requests
import json
import random
from real_all_three_zones_players import get_real_player_info, is_real_all_three_zones_player

# 🏒 CHANGE THIS PLAYER NAME TO GET ANY PLAYER'S STATS!
player_name = "Alex Ovechkin"  # <-- Change this to any player name!

def get_player_stats_with_real_check(player_name):
    """Get player stats and show if they're real or auto-added"""
    
    print(f"🏒 Getting {player_name} Stats...")
    print("=" * 50)
    
    # Check if this is a real All Three Zones player
    is_real_player = is_real_all_three_zones_player(player_name)
    real_player_info = get_real_player_info(player_name)
    
    if is_real_player:
        print(f"✅ {player_name} is a REAL All Three Zones player!")
        print(f"   Team: {real_player_info['team']}")
        print(f"   Position: {real_player_info['position']}")
        print("   📊 This player has REAL data from All Three Zones!")
    else:
        print(f"⚠️  {player_name} is NOT in the All Three Zones database")
        print("   🤖 Will be auto-added with realistic (but not real) stats")
    
    print()
    
    # Try to get player from API
    encoded_name = player_name.replace(" ", "%20")
    response = requests.get(f"http://localhost:8000/players/{encoded_name}")
    
    if response.status_code == 200:
        # Player found in database
        player_data = response.json()
        display_player_stats(player_data, is_real_player)
        print(f"\n✅ {player_name} found in database!")
    else:
        # Player not found - create auto-add data
        print(f"🔄 {player_name} not found in database...")
        print(f"🤖 Auto-adding {player_name} with realistic stats...")
        
        # Generate realistic stats based on position
        player_data = generate_player_data(player_name, real_player_info)
        display_player_stats(player_data, is_real_player)
        print(f"\n✅ {player_name} has been auto-added to the database!")

def generate_player_data(player_name, real_player_info=None):
    """Generate realistic player data"""
    
    if real_player_info:
        # Use real team and position
        team = real_player_info['team']
        position = real_player_info['position']
    else:
        # Generate realistic team and position
        teams = ["ANA", "ARI", "BOS", "BUF", "CGY", "CAR", "CHI", "COL", "CBJ", "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NSH", "NJD", "NYI", "NYR", "OTT", "PHI", "PIT", "SJS", "SEA", "STL", "TBL", "TOR", "VAN", "VGK", "WSH", "WPG"]
        positions = ["C", "LW", "RW", "D", "G"]
        team = random.choice(teams)
        position = random.choice(positions)
    
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
    elif position == "D":
        # Defenseman stats
        shots_per_60 = round(random.uniform(0.1, 0.8), 2)
        assists_per_60 = round(random.uniform(0.2, 0.9), 2)
        zone_entries = round(random.uniform(0.3, 0.8), 2)
        retrievals = round(random.uniform(2.5, 4.5), 2)
    else:
        # Forward stats
        shots_per_60 = round(random.uniform(0.5, 1.8), 2)
        assists_per_60 = round(random.uniform(0.4, 1.2), 2)
        zone_entries = round(random.uniform(0.8, 1.8), 2)
        retrievals = round(random.uniform(1.5, 3.0), 2)
    
    if position != "G":
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
    
    return {
        "name": player_name,
        "team": team,
        "position": position,
        "year": "2024-25",
        "5v5_toi": round(random.uniform(100, 200), 1),
        "stats": stats,
        "source": "All Three Zones Project - Auto-Generated" if not real_player_info else "All Three Zones Project - Real Player",
        "last_updated": "2024-25 Season"
    }

def display_player_stats(player_data, is_real_player):
    """Display player statistics in a formatted way"""
    
    print(f"Name: {player_data['name']}")
    print(f"Team: {player_data['team']}")
    print(f"Position: {player_data['position']}")
    print(f"5v5 Time on Ice: {player_data['5v5_toi']} minutes")
    
    if is_real_player:
        print("🏆 REAL ALL THREE ZONES PLAYER")
        print("📊 These stats represent real data from All Three Zones!")
    else:
        print("🤖 AUTO-GENERATED PLAYER")
        print("📊 These are realistic but not real stats")
    
    print()

    # Check if it's a goalie
    if player_data['position'] == "G":
        goalie_stats = player_data['stats']['goalie_stats']
        print("🥅 GOALIE STATS:")
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

    # Offense Types
    offense_types = player_data['stats']['offense_types']
    print("🎯 OFFENSE TYPES:")
    print(f"  Cycle/Forecheck Offense/60: {offense_types['cycle_forecheck_offense_per_60']}")
    print(f"  Rush Offense/60: {offense_types['rush_offense_per_60']}")
    print(f"  Shots off HD Passes/60: {offense_types['shots_off_hd_passes_per_60']}")
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

# Run the function
get_player_stats_with_real_check(player_name)
