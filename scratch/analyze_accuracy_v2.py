import requests
import json
import os
from datetime import datetime, timedelta

def get_game_result(game_id):
    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            state = data.get('gameState')
            if state in ['OFF', 'FINAL']:
                away_score = data.get('awayTeam', {}).get('score', 0)
                home_score = data.get('homeTeam', {}).get('score', 0)
                away_abbrev = data.get('awayTeam', {}).get('abbrev')
                home_abbrev = data.get('homeTeam', {}).get('abbrev')
                winner = away_abbrev if away_score > home_score else home_abbrev
                return {
                    'winner': winner,
                    'score': f"{away_abbrev} {away_score} - {home_score} {home_abbrev}",
                    'date': data.get('gameDate')
                }
    except:
        pass
    return None

def analyze_recent_predictions():
    prediction_file = '/Users/emilyfehr8/CascadeProjects/automated-post-game-reports/data/win_probability_predictions_v2.json'
    with open(prediction_file, 'r') as f:
        data = json.load(f)
    predictions = data.get('predictions', [])

    # Get predictions made/for the last 10 days to be thorough
    target_dates = [ (datetime(2026, 4, 26) - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10) ]
    
    recent_predictions = [p for p in predictions if p.get('date') in target_dates]
    
    print(f"Analyzing {len(recent_predictions)} recent predictions...")
    
    results = []
    for p in recent_predictions:
        gid = p.get('game_id')
        print(f"Checking Game {gid}: {p['away_team']} @ {p['home_team']} (Pred Date: {p['date']})...")
        res = get_game_result(gid)
        if res:
            pred_winner = p.get('predicted_winner')
            actual_winner = res['winner']
            is_correct = pred_winner == actual_winner
            status = "✅ CORRECT" if is_correct else "❌ WRONG"
            print(f"  Result: {res['score']} on {res['date']}. Predicted {pred_winner} -> {status}")
            results.append({
                'game_id': gid,
                'correct': is_correct,
                'teams': f"{p['away_team']} @ {p['home_team']}",
                'prediction': pred_winner,
                'actual': actual_winner,
                'score': res['score'],
                'date': res['date']
            })
        else:
            print(f"  Game not finished yet or ID invalid.")

    print("\n--- SUMMARY ---")
    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    if total_count > 0:
        print(f"Accuracy: {correct_count}/{total_count} ({correct_count/total_count:.1%})")
        
        # Breakdown by date
        by_date = {}
        for r in results:
            d = r['date']
            if d not in by_date: by_date[d] = {'c': 0, 't': 0}
            by_date[d]['t'] += 1
            if r['correct']: by_date[d]['c'] += 1
            
        print("\nBreakdown by Actual Game Date:")
        for d in sorted(by_date.keys()):
            print(f"  {d}: {by_date[d]['c']}/{by_date[d]['t']} ({by_date[d]['c']/by_date[d]['t']:.1%})")
    else:
        print("No completed games found in recent predictions.")

if __name__ == "__main__":
    analyze_recent_predictions()
