import json

with open("data/win_probability_predictions_v2.json", "r") as f:
    data = json.load(f)

predictions = data.get("predictions", [])
completed = [p for p in predictions if p.get("actual_winner") and p.get("actual_winner") not in ("", None)]

recent_games = [p for p in completed if abs(p.get("predicted_away_win_prob", 0) - p.get("predicted_home_win_prob", 0)) >= 0.01]
recent = recent_games[-30:] if len(recent_games) > 30 else recent_games

correct = 0
for pred in recent:
    away_prob = pred.get("predicted_away_win_prob", 0)
    home_prob = pred.get("predicted_home_win_prob", 0)
    away_team = pred.get("away_team")
    home_team = pred.get("home_team")
    actual_winner = pred.get("actual_winner")
    
    # Simple normalization without the model function
    actual_side = "away" if actual_winner == away_team else "home"
    predicted_side = "away" if away_prob >= home_prob else "home"
    
    if actual_side == predicted_side:
        correct += 1
        print(f"✅ {pred.get('date')} {away_team} @ {home_team} | Pred: {predicted_side} | Act: {actual_side}")
    else:
        print(f"❌ {pred.get('date')} {away_team} @ {home_team} | Pred: {predicted_side} | Act: {actual_side}")

print(f"\nRecent correct: {correct}/{len(recent)} = {correct/len(recent) if recent else 0:.3f}")
