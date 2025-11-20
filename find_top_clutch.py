#!/usr/bin/env python3
"""Quick find top clutch team based on report clutch indicator"""

from team_report_generator import TeamReportGenerator
import requests

gen = TeamReportGenerator()

# Get all teams
url = 'https://api-web.nhle.com/v1/standings/now'
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
standings_data = response.json()

teams = []
for team in standings_data.get('standings', []):
    abbrev = team.get('teamAbbrev', {}).get('default', '')
    if abbrev:
        games = gen.get_team_games(abbrev)
        if games:
            stats = gen.aggregate_team_stats(abbrev, games)
            third_period_goals = stats['clutch']['third_period_goals']
            one_goal_games = stats['clutch']['one_goal_games']
            one_goal_wins = stats['clutch']['one_goal_wins']
            one_goal_win_pct = (one_goal_wins / one_goal_games * 100) if one_goal_games > 0 else 0.0
            # Clutch score from report (same formula as in create_clutch_performance_box)
            clutch_score = (third_period_goals * 2) + (one_goal_win_pct * 0.5)
            teams.append((abbrev, clutch_score, third_period_goals, one_goal_win_pct))

# Sort by clutch score
teams.sort(key=lambda x: x[1], reverse=True)

print("\n🏆 TOP CLUTCH TEAM:", teams[0][0])
print(f"Clutch Score: {teams[0][1]:.2f}")
print(f"3rd Period Goals: {teams[0][2]}")
print(f"One-Goal Win %: {teams[0][3]:.1f}%")
print(f"\nTop 5:")
for i, (abbrev, score, goals, win_pct) in enumerate(teams[:5], 1):
    print(f"{i}. {abbrev}: {score:.2f} (3P Goals: {goals}, 1-Goal Win%: {win_pct:.1f}%)")

