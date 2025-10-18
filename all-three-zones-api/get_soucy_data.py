#!/usr/bin/env python3
"""
Quick script to get Carson Soucy data
"""

import requests
import json

def get_soucy_data():
    """Get Carson Soucy's complete statistics"""
    
    # Method 1: Direct player lookup
    try:
        response = requests.get("http://localhost:8000/players/Carson%20Soucy")
        if response.status_code == 200:
            soucy = response.json()
            print("🏒 CARSON SOUCY DATA")
            print("=" * 50)
            print(f"Name: {soucy['name']}")
            print(f"Team: {soucy['team']}")
            print(f"Position: {soucy['position']}")
            print(f"5v5 Time on Ice: {soucy['5v5_toi']} minutes")
            print()
            
            # General Offense
            offense = soucy['stats']['general_offense']
            print("📊 GENERAL OFFENSE:")
            print(f"  Shots/60: {offense['shots_per_60']}")
            print(f"  Shot Assists/60: {offense['shot_assists_per_60']}")
            print(f"  Total Shot Contributions/60: {offense['total_shot_contributions_per_60']}")
            print(f"  Chances/60: {offense['chances_per_60']}")
            print(f"  Chance Assists/60: {offense['chance_assists_per_60']}")
            print()
            
            # Passing
            passing = soucy['stats']['passing']
            print("🎯 PASSING:")
            print(f"  High Danger Assists/60: {passing['high_danger_assists_per_60']}")
            print()
            
            # Offense Types
            offense_types = soucy['stats']['offense_types']
            print("⚡ OFFENSE TYPES:")
            print(f"  Cycle/Forecheck Offense/60: {offense_types['cycle_forecheck_offense_per_60']}")
            print(f"  Rush Offense/60: {offense_types['rush_offense_per_60']}")
            print(f"  Shots off HD Passes/60: {offense_types['shots_off_hd_passes_per_60']}")
            print()
            
            # Zone Entries
            zone_entries = soucy['stats']['zone_entries']
            print("🏃 ZONE ENTRIES:")
            print(f"  Zone Entries/60: {zone_entries['zone_entries_per_60']}")
            print(f"  Controlled Entry %: {zone_entries['controlled_entry_percent']:.1%}")
            print(f"  Controlled Entry with Chance %: {zone_entries['controlled_entry_with_chance_percent']:.1%}")
            print()
            
            # DZ Retrievals & Exits
            defense = soucy['stats']['dz_retrievals_exits']
            print("🛡️  DEFENSIVE ZONE PLAY:")
            print(f"  DZ Puck Touches/60: {defense['dz_puck_touches_per_60']}")
            print(f"  Retrievals/60: {defense['retrievals_per_60']}")
            print(f"  Successful Retrieval %: {defense['successful_retrieval_percent']:.1%}")
            print(f"  Exits/60: {defense['exits_per_60']}")
            print(f"  Botched Retrievals/60: {defense['botched_retrievals_per_60']}")
            print()
            
            print("✅ Carson Soucy data retrieved successfully!")
            return soucy
            
        else:
            print(f"❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting Carson Soucy data: {e}")
        return None

def get_soucy_json():
    """Get Carson Soucy data as JSON"""
    try:
        response = requests.get("http://localhost:8000/players/Carson%20Soucy")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

if __name__ == "__main__":
    get_soucy_data() 