#!/usr/bin/env python3
"""
Quick test for Dylan Samberg data
"""

import requests

# Test Dylan Samberg search
response = requests.get('http://localhost:8000/search?query=Dylan%20Samberg')
data = response.json()

if data:
    player = data[0]
    print(f"🏒 {player['name']} ({player['team']}) - {player['position']}")
    print("=" * 50)
    print(f"5v5 Time on Ice: {player['5v5_toi']} minutes")
    print(f"Shots/60: {player['stats']['general_offense']['shots_per_60']}")
    print(f"Shot Assists/60: {player['stats']['general_offense']['shot_assists_per_60']}")
    print(f"High Danger Assists/60: {player['stats']['passing']['high_danger_assists_per_60']}")
    print(f"Zone Entries/60: {player['stats']['zone_entries']['zone_entries_per_60']}")
    print(f"Controlled Entry %: {player['stats']['zone_entries']['controlled_entry_percent']:.1%}")
    print(f"Successful Retrieval %: {player['stats']['dz_retrievals_exits']['successful_retrieval_percent']:.1%}")
    print(f"Exits/60: {player['stats']['dz_retrievals_exits']['exits_per_60']}")
    print("\n✅ Dylan Samberg data retrieved successfully!")
else:
    print("❌ No data found for Dylan Samberg") 