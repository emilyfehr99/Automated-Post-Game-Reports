import json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict

def normalize_side(val, home_team, away_team):
    """Normalize a value (team name, 'home', 'away') to 'home' or 'away'"""
    if not val:
        return None
    val = str(val).lower()
    if val == 'home':
        return 'home'
    if val == 'away':
        return 'away'
    if val == str(home_team).lower():
        return 'home'
    if val == str(away_team).lower():
        return 'away'
    return None

def analyze_weaknesses():
    print("📊 ANALYZING MODEL WEAKNESSES (ROBUST MODE)")
    print("=" * 60)
    
    file_path = Path('data/win_probability_predictions_v2.json')
    if not file_path.exists():
        file_path = Path('win_probability_predictions_v2.json')
        
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    raw_predictions = data.get('predictions', [])
    valid_predictions = []
    
    # Pre-process and normalize
    for p in raw_predictions:
        home_team = p.get('home_team')
        away_team = p.get('away_team')
        
        # Determine predicted side
        pred_val = p.get('predicted_winner')
        pred_side = normalize_side(pred_val, home_team, away_team)
        
        # If ambiguous, use probabilities
        if not pred_side:
            p_home = p.get('predicted_home_win_prob', 0)
            p_away = p.get('predicted_away_win_prob', 0)
            if p_home > p_away:
                pred_side = 'home'
            else:
                pred_side = 'away'
                
        # Determine actual side
        actual_val = p.get('actual_winner')
        actual_side = normalize_side(actual_val, home_team, away_team)
        
        if actual_side and pred_side:
            is_correct = (actual_side == pred_side)
            valid_predictions.append({
                'home_team': home_team,
                'away_team': away_team,
                'pred_side': pred_side,
                'actual_side': actual_side,
                'is_correct': is_correct,
                'confidence': p.get('prediction_confidence', 0.5) * 100,
                'date': p.get('date')
            })
            
    print(f"Total Validated Predictions: {len(valid_predictions)}")
    
    if not valid_predictions:
        print("❌ No valid predictions found after normalization.")
        return

    # Overall Accuracy
    total_correct = sum(1 for p in valid_predictions if p['is_correct'])
    print(f"Overall Accuracy: {total_correct/len(valid_predictions):.1%} ({total_correct}/{len(valid_predictions)})")
    
    # 1. Accuracy by Confidence Bucket
    print("\n1. Accuracy by Confidence:")
    bins = [(50, 55), (55, 60), (60, 65), (65, 100)]
    for low, high in bins:
        subset = [p for p in valid_predictions if low <= p['confidence'] < high]
        if not subset:
            print(f"   {low}-{high}% Conf: N/A (0 games)")
            continue
        correct = sum(1 for p in subset if p['is_correct'])
        acc = correct / len(subset)
        print(f"   {low}-{high}% Conf: {acc:.1%} accuracy ({len(subset)} games)")
        
    # 2. Accuracy by Team (Top 5 Worst)
    print("\n2. Worst Performing Teams (min 10 games involving team):")
    team_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
    
    for p in valid_predictions:
        for team in [p['home_team'], p['away_team']]:
            team_stats[team]['total'] += 1
            if p['is_correct']:
                team_stats[team]['correct'] += 1
                
    team_accs = []
    for team, stats in team_stats.items():
        if stats['total'] >= 10:
            team_accs.append((team, stats['correct'] / stats['total'], stats['total']))
            
    team_accs.sort(key=lambda x: x[1])
    
    for team, acc, total in team_accs[:5]:
        print(f"   {team}: {acc:.1%} ({total} games)")
        
    # 3. Home vs Away Bias
    print("\n3. Venue Bias:")
    pred_home = sum(1 for p in valid_predictions if p['pred_side'] == 'home')
    actual_home = sum(1 for p in valid_predictions if p['actual_side'] == 'home')
    
    print(f"   Predicted Home Win Rate: {pred_home/len(valid_predictions):.1%}")
    print(f"   Actual Home Win Rate:    {actual_home/len(valid_predictions):.1%}")
    
    # 4. Calibration Check
    avg_conf = np.mean([p['confidence'] for p in valid_predictions])
    actual_acc = total_correct / len(valid_predictions) * 100
    
    print(f"\n4. Calibration:")
    print(f"   Avg Confidence: {avg_conf:.1f}%")
    print(f"   Actual Accuracy: {actual_acc:.1f}%")
    diff = avg_conf - actual_acc
    if diff > 2:
        print(f"   ⚠️  Overconfident by {diff:.1f} points")
    elif diff < -2:
        print(f"   ⚠️  Underconfident by {abs(diff):.1f} points")
    else:
        print("   ✅ Well calibrated")

if __name__ == "__main__":
    analyze_weaknesses()
