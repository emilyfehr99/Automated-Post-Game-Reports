import json

def _normalize_outcome_side(outcome, away_team, home_team):
    if not outcome: return None
    out_lower = outcome.lower()
    if out_lower in ("away", "home"): return out_lower
    if away_team and out_lower == away_team.lower(): return "away"
    if home_team and out_lower == home_team.lower(): return "home"
    return outcome

d = json.load(open('data/win_probability_predictions_v2.json'))
predictions = d.get('predictions', [])

completed = []
for p in predictions:
    actual_winner = p.get("actual_winner")
    if actual_winner and actual_winner not in ("", None):
        completed.append(p)

total_games = len(completed)
correct_predictions = 0

for pred in completed:
    away_prob = pred.get("predicted_away_win_prob") or pred.get("away_win_prob", 0)
    home_prob = pred.get("predicted_home_win_prob") or pred.get("home_win_prob", 0)
    if away_prob > 1.0 or home_prob > 1.0:
        away_prob /= 100.0
        home_prob /= 100.0

    away_team = pred.get("away_team")
    home_team = pred.get("home_team")
    actual_side = _normalize_outcome_side(pred.get("actual_winner"), away_team, home_team)
    predicted_side = pred.get("predicted_winner")
    if predicted_side not in ("away", "home"):
        predicted_side = "away" if away_prob >= home_prob else "home"
    if actual_side and predicted_side == actual_side:
        correct_predictions += 1

accuracy = correct_predictions / total_games if total_games > 0 else 0.0

recent_games = []
for p in completed:
    ap = p.get("predicted_away_win_prob") or p.get("away_win_prob", 0)
    hp = p.get("predicted_home_win_prob") or p.get("home_win_prob", 0)
    if ap > 1.0 or hp > 1.0:
        ap /= 100.0
        hp /= 100.0
    if abs(ap - hp) >= 0.01:
        recent_games.append(p)
recent_games = recent_games[-30:] if len(recent_games) > 30 else recent_games

recent_correct = 0
for pred in recent_games:
    away_prob = pred.get("predicted_away_win_prob") or pred.get("away_win_prob", 0)
    home_prob = pred.get("predicted_home_win_prob") or pred.get("home_win_prob", 0)
    if away_prob > 1.0 or home_prob > 1.0:
        away_prob /= 100.0
        home_prob /= 100.0
    away_team = pred.get("away_team")
    home_team = pred.get("home_team")
    actual_side = _normalize_outcome_side(pred.get("actual_winner"), away_team, home_team)
    predicted_side = pred.get("predicted_winner")
    if predicted_side not in ("away", "home"):
        predicted_side = "away" if away_prob >= home_prob else "home"
    if actual_side and predicted_side == actual_side:
        recent_correct += 1

recent_accuracy = recent_correct / len(recent_games) if len(recent_games) >= 3 else accuracy

print(f"Total: {total_games}, Correct: {correct_predictions}, Accuracy: {accuracy}")
print(f"Recent Total: {len(recent_games)}, Recent Correct: {recent_correct}, Recent Accuracy: {recent_accuracy}")
