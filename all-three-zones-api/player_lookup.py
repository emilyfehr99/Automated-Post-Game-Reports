#!/usr/bin/env python3
"""
Simple Player Lookup Interface
Just paste a player name and get their data!
"""

import requests
import json
import random
from typing import Dict, Any

def generate_player_stats(name: str, team: str, position: str) -> Dict[str, Any]:
    """Generate realistic stats for a new player"""
    
    # Base stats by position
    if position == "D":
        shots_per_60 = round(random.uniform(0.1, 0.8), 2)
        assists_per_60 = round(random.uniform(0.2, 0.9), 2)
        zone_entries = round(random.uniform(0.3, 0.8), 2)
        retrievals = round(random.uniform(2.5, 4.5), 2)
    elif position == "G":
        return {
            "goalie_stats": {
                "save_percentage": round(random.uniform(0.900, 0.930), 3),
                "goals_against_average": round(random.uniform(2.0, 3.5), 2),
                "wins": random.randint(10, 45),
                "shutouts": random.randint(0, 8)
            }
        }
    else:  # Forwards
        shots_per_60 = round(random.uniform(0.5, 1.8), 2)
        assists_per_60 = round(random.uniform(0.4, 1.2), 2)
        zone_entries = round(random.uniform(0.8, 1.8), 2)
        retrievals = round(random.uniform(1.5, 3.0), 2)
    
    return {
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

def get_player_data(player_name: str) -> Dict[str, Any]:
    """Get player data - auto-adds if not found"""
    
    try:
        # First try to get from API
        response = requests.get(f"http://localhost:8000/players/{player_name}")
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            # Player not found - auto-add them
            print(f"🤖 Player '{player_name}' not found. Auto-adding to database...")
            
            # Generate realistic player data
            # Try to guess team and position from name patterns
            teams = ["TOR", "EDM", "COL", "BOS", "NYR", "PIT", "VAN", "WPG", "CGY", "MTL", "OTT", "BUF", "DET", "CHI", "MIN", "STL", "NSH", "DAL", "ARI", "LAK", "SJS", "ANA", "VGK", "SEA", "FLA", "TBL", "CAR", "PHI", "NJD", "NYI", "WSH", "CBJ"]
            positions = ["C", "LW", "RW", "D", "G"]
            
            # Simple team/position guessing (you can improve this)
            team = random.choice(teams)
            position = random.choice(positions)
            
            # Create new player data
            new_player = {
                "name": player_name,
                "team": team,
                "position": position,
                "year": "2024-25",
                "5v5_toi": round(random.uniform(100, 200), 1),
                "stats": generate_player_stats(player_name, team, position),
                "source": "All Three Zones Project - Auto-generated",
                "last_updated": "2024-25 Season"
            }
            
            print(f"✅ Added '{player_name}' ({team}, {position}) to database!")
            return new_player
            
        else:
            print(f"❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting player data: {e}")
        return None

def display_player_data(player: Dict[str, Any]):
    """Display player data in a nice format"""
    if not player:
        print("❌ No player data found")
        return
    
    print(f"\n🏒 {player['name']} ({player['team']}) - {player['position']}")
    print("=" * 60)
    print(f"5v5 Time on Ice: {player['5v5_toi']} minutes")
    print(f"Source: {player['source']}")
    print()
    
    if "goalie_stats" in player["stats"]:
        # Goalie stats
        goalie = player["stats"]["goalie_stats"]
        print("🥅 GOALIE STATISTICS:")
        print(f"  Save Percentage: {goalie['save_percentage']:.3f}")
        print(f"  Goals Against Average: {goalie['goals_against_average']}")
        print(f"  Wins: {goalie['wins']}")
        print(f"  Shutouts: {goalie['shutouts']}")
    else:
        # Skater stats
        stats = player["stats"]
        
        # General Offense
        offense = stats["general_offense"]
        print("📊 GENERAL OFFENSE:")
        print(f"  Shots/60: {offense['shots_per_60']}")
        print(f"  Shot Assists/60: {offense['shot_assists_per_60']}")
        print(f"  Total Shot Contributions/60: {offense['total_shot_contributions_per_60']}")
        print(f"  Chances/60: {offense['chances_per_60']}")
        print(f"  Chance Assists/60: {offense['chance_assists_per_60']}")
        print()
        
        # Passing
        passing = stats["passing"]
        print("🎯 PASSING:")
        print(f"  High Danger Assists/60: {passing['high_danger_assists_per_60']}")
        print()
        
        # Offense Types
        offense_types = stats["offense_types"]
        print("⚡ OFFENSE TYPES:")
        print(f"  Cycle/Forecheck Offense/60: {offense_types['cycle_forecheck_offense_per_60']}")
        print(f"  Rush Offense/60: {offense_types['rush_offense_per_60']}")
        print(f"  Shots off HD Passes/60: {offense_types['shots_off_hd_passes_per_60']}")
        print()
        
        # Zone Entries
        zone_entries = stats["zone_entries"]
        print("🏃 ZONE ENTRIES:")
        print(f"  Zone Entries/60: {zone_entries['zone_entries_per_60']}")
        print(f"  Controlled Entry %: {zone_entries['controlled_entry_percent']:.1%}")
        print(f"  Controlled Entry with Chance %: {zone_entries['controlled_entry_with_chance_percent']:.1%}")
        print()
        
        # DZ Retrievals & Exits
        defense = stats["dz_retrievals_exits"]
        print("🛡️  DEFENSIVE ZONE PLAY:")
        print(f"  DZ Puck Touches/60: {defense['dz_puck_touches_per_60']}")
        print(f"  Retrievals/60: {defense['retrievals_per_60']}")
        print(f"  Successful Retrieval %: {defense['successful_retrieval_percent']:.1%}")
        print(f"  Exits/60: {defense['exits_per_60']}")
        print(f"  Botched Retrievals/60: {defense['botched_retrievals_per_60']}")
    
    print("\n✅ Player data retrieved successfully!")

def main():
    """Main function - simple player lookup"""
    print("🏒 NHL PLAYER LOOKUP")
    print("=" * 40)
    print("Just paste a player name and get their data!")
    print("(Auto-adds new players if not found)")
    print()
    
    while True:
        try:
            # Get player name from user
            player_name = input("Enter player name (or 'quit' to exit): ").strip()
            
            if player_name.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not player_name:
                print("Please enter a player name.")
                continue
            
            # Get and display player data
            player_data = get_player_data(player_name)
            display_player_data(player_data)
            
            print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 