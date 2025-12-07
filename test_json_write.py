#!/usr/bin/env python3
"""Quick test to verify opponent stats are written to JSON"""

from generate_real_team_stats import RealTeamStatsGenerator
import json

# Create generator
gen = RealTeamStatsGenerator()

# Get one game
print("Fetching test game data...")
game_data = gen.api.get_comprehensive_game_data('2025020300')

# Calculate metrics (COL home game)
print("Calculating metrics...")
metrics = gen.calculate_game_metrics(game_data, team_id=21, is_home=True)

print(f"\n✓ Metrics generated with {len(metrics)} fields")
print(f"  Keys: {list(metrics.keys())}")
print(f"  opp_goals: {metrics.get('opp_goals', 'MISSING')}")
print(f"  opp_xg: {metrics.get('opp_xg', 'MISSING')}")

# Manually create the arrays as the generat or does
home_stats = {
    'gs': [], 'xg': [], 'opp_goals': [], 'opp_xg': [], 'goals': []
}

# Append metrics
for key in home_stats.keys():
    home_stats[key].append(metrics.get(key, 0))

print(f"\n✓ Arrays populated:")
print(f"  xg: {home_stats['xg']}")
print(f"  opp_goals: {home_stats['opp_goals']}")
print(f"  opp_xg: {home_stats['opp_xg']}")

# Write to test file
test_data = {"teams": {"COL": {"home": home_stats}}}
with open('/tmp/test_stats.json', 'w') as f:
    json.dump(test_data, f, indent=2)

# Read back and verify
with open('/tmp/test_stats.json') as f:
    loaded = json.load(f)

print(f"\n✓ File written and read back:")
print(f"  Keys in file: {list(loaded['teams']['COL']['home'].keys())}")
print(f"  opp_goals in file? {' opp_goals' in loaded['teams']['COL']['home']}")
print(f"  opp_xg in file? {'opp_xg' in loaded['teams']['COL']['home']}")
print(f"  opp_goals value: {loaded['teams']['COL']['home'].get('opp_goals')}")
print(f"  opp_xg value: {loaded['teams']['COL']['home'].get('opp_xg')}")
