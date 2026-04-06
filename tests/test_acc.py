import json
from collections import defaultdict

with open('data/win_probability_predictions_v2.json', 'r') as f:
    data = json.load(f)

predictions = data.get('predictions', [])
completed = [p for p in predictions if p.get('actual_winner') and p.get('actual_winner') not in ('', None)]

by_month = defaultdict(list)
for p in completed:
    date = p.get('date', 'Unknown')
    month = date[:7] if len(date) >= 7 else "Unknown"
    
    ap = p.get("predicted_away_win_prob") or p.get("away_win_prob", 0)
    hp = p.get("predicted_home_win_prob") or p.get("home_win_prob", 0)
    
    if ap > 1.0 or hp > 1.0:
        ap /= 100.0
        hp /= 100.0
        
    away_team = p.get("away_team")
    home_team = p.get("home_team")
    
    actual_winner = p.get("actual_winner")
    actual_side = "away" if actual_winner == away_team or actual_winner == "away" else "home"
    
    predicted_side = p.get("predicted_winner")
    if predicted_side == away_team: predicted_side = "away"
    elif predicted_side == home_team: predicted_side = "home"
    
    if predicted_side not in ("away", "home"):
        predicted_side = "away" if ap >= hp else "home"
        
    by_month[month].append(actual_side == predicted_side)

print("Accuracy by month:")
for month in sorted(by_month.keys()):
    correct = sum(by_month[month])
    total = len(by_month[month])
    print(f"  {month}: {correct}/{total} = {correct/total:.1%}")
    
total_correct = sum(sum(v) for v in by_month.values())
total_games = sum(len(v) for v in by_month.values())
print(f"\nTotal: {total_correct}/{total_games} = {total_correct/total_games:.1%}")
