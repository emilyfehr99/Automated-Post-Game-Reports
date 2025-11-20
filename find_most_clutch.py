#!/usr/bin/env python3
"""Find the most clutch team"""

from team_report_generator import TeamReportGenerator

gen = TeamReportGenerator()

print("Calculating league-wide clutch rankings...")
rankings = gen.get_league_clutch_rankings()

if not rankings:
    print("Could not calculate rankings")
    exit(1)

# Sort by rank (1 is best)
sorted_rankings = sorted(rankings.items(), key=lambda x: x[1])

print(f"\n✅ Calculated rankings for {len(rankings)} teams\n")
print("="*60)
print("🏆 MOST CLUTCH TEAM:")
print("="*60)
most_clutch = sorted_rankings[0]
print(f"Team: {most_clutch[0]}")
print(f"Rank: {most_clutch[1]}st (out of {len(rankings)} teams)")
print()

print("Top 5 Most Clutch Teams:")
print("-"*60)
for i, (abbrev, rank) in enumerate(sorted_rankings[:5], 1):
    print(f"{i}. {abbrev} - Rank #{rank}")

