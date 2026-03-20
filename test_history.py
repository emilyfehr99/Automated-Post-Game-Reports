import json

def get_acc(completed_list):
    total = len(completed_list)
    correct = 0
    for p in completed_list:
        actual_winner = p.get('actual_winner')
        pred_winner = p.get('predicted_winner')
        
        # Simple match for actual vs pred 
        # Note: improved_self_learning_model normalizes this, but assuming pred_winner and actual_winner match for simplicity
        is_away = actual_winner == p.get('away_team')
        is_home = actual_winner == p.get('home_team')
        actual_side = "away" if is_away else ("home" if is_home else actual_winner)
        
        pred_side = pred_winner
        if pred_side == p.get('away_team'): pred_side = "away"
        if pred_side == p.get('home_team'): pred_side = "home"
        
        ap = p.get("predicted_away_win_prob") or p.get("away_win_prob", 0)
        hp = p.get("predicted_home_win_prob") or p.get("home_win_prob", 0)
        
        if pred_side not in ("away", "home"):
            pred_side = "away" if ap >= hp else "home"
            
        if actual_side and pred_side == actual_side:
            correct += 1
    return total, correct, correct/total if total > 0 else 0

d = json.load(open('data/win_probability_predictions_v2.json'))
completed = [p for p in d['predictions'] if p.get('actual_winner')]

for i in range(1, 6):
    cutoff = len(completed) - i*5
    past_completed = completed[:cutoff]
    t, c, a = get_acc(past_completed)
    
    # Check recent accuracy format
    recent = past_completed[-30:] if len(past_completed) > 30 else past_completed
    rt, rc, ra = get_acc(recent)
    
    print(f"Games -{i*5:02d}: Total={t}, Acc={a*100:.2f}%, Recent Acc={ra*100:.2f}% (Recent Correct: {rc}/{rt})")
