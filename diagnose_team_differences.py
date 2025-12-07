import sys
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

# Check if team stats actually show variety
model = ImprovedSelfLearningModelV2()

teams = ['VGK', 'NJD', 'BUF', 'WPG', 'SJS', 'DAL', 'UTA', 'VAN', 'WSH', 'ANA']

print("🔍 ANALYZING TEAM STAT VARIETY")
print("=" * 80)

for team in teams:
    perf = model.get_team_performance(team, venue="home")
    
    xg = perf.get('xg_avg', 0)
    xga = perf.get('xg_against_avg', 0)
    goals = perf.get('goals_avg', 0)
    ga = perf.get('goals_against_avg', 0)
    
    print(f"\n{team}:")
    print(f"  Offense: {xg:.2f} xG/game, {goals:.2f} G/game")
    print(f"  Defense: {xga:.2f} xGA/game, {ga:.2f} GA/game")
    
    # Classify
    if xg > 3.5:
        offense_rating = "STRONG"
    elif xg < 2.5:
        offense_rating = "WEAK"
    else:
        offense_rating = "AVERAGE"
    
    if xga < 2.5:
        defense_rating = "STRONG"
    elif xga > 3.5:
        defense_rating = "WEAK"  
    else:
        defense_rating = "AVERAGE"
    
    print(f"  → {offense_rating} Offense, {defense_rating} Defense")

print("\n" + "=" * 80)
print("\n💡 IDEAL MATCHUP PREDICTIONS:")
print("  Strong Off vs Weak Def → HIGH scoring (5-4, 6-5)")
print("  Weak Off vs Strong Def → LOW scoring (1-0, 2-1)")
print("  Average vs Average → MEDIUM scoring (3-2, 4-3)")
