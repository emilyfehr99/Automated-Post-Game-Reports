import requests
import json
import os
from datetime import datetime, timedelta

def get_actual_results(date_str):
    url = f"https://api-web.nhle.com/v1/score/{date_str}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def analyze_last_5_days():
    prediction_file = '/Users/emilyfehr8/CascadeProjects/automated-post-game-reports/data/win_probability_predictions_v2.json'
    with open(prediction_file, 'r') as f:
        data = json.load(f)
    predictions = data.get('predictions', [])

    today = datetime(2026, 4, 26)
    results_summary = []

    for i in range(1, 7): # Last 6 days to be safe
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        print(f"\nAnalyzing {date_str}...")
        
        # Get actual results for this date
        actual_data = get_actual_results(date_str)
        if not actual_data:
            print(f"  Could not fetch actual results for {date_str}")
            continue
            
        actual_games = {}
        for g in actual_data.get('games', []):
            gid = g.get('id')
            state = g.get('gameState')
            if state in ['OFF', 'FINAL']:
                away_score = g.get('awayTeam', {}).get('score', 0)
                home_score = g.get('homeTeam', {}).get('score', 0)
                winner = g.get('awayTeam', {}).get('abbrev') if away_score > home_score else g.get('homeTeam', {}).get('abbrev')
                actual_games[gid] = {
                    'winner': winner,
                    'score': f"{g.get('awayTeam', {}).get('abbrev')} {away_score} - {home_score} {g.get('homeTeam', {}).get('abbrev')}"
                }

        # Get predictions for this date
        day_preds = [p for p in predictions if p.get('date') == date_str]
        
        if not day_preds:
            print(f"  No predictions found for {date_str}")
            continue

        correct = 0
        total = 0
        for p in day_preds:
            gid = p.get('game_id')
            if gid in actual_games:
                total += 1
                pred_winner = p.get('predicted_winner')
                actual_winner = actual_games[gid]['winner']
                is_correct = pred_winner == actual_winner
                if is_correct:
                    correct += 1
                
                status = "✅ CORRECT" if is_correct else "❌ WRONG"
                print(f"  Game {gid}: {p['away_team']} @ {p['home_team']} -> Predicted {pred_winner}, Actual {actual_winner} ({actual_games[gid]['score']}) {status}")
            else:
                # Check if it happened on a different day or if it's still LIVE/PRE
                print(f"  Game {gid}: {p['away_team']} @ {p['home_team']} -> Prediction found, but game not finished or not on this day's schedule.")

        if total > 0:
            print(f"  Summary for {date_str}: {correct}/{total} ({correct/total:.1%})")
            results_summary.append({'date': date_str, 'correct': correct, 'total': total})
        else:
            print(f"  No completed games found for {date_str} predictions.")

    print("\n--- FINAL OVERALL SUMMARY ---")
    grand_correct = sum(r['correct'] for r in results_summary)
    grand_total = sum(r['total'] for r in results_summary)
    if grand_total > 0:
        print(f"Overall Accuracy: {grand_correct}/{grand_total} ({grand_correct/grand_total:.1%})")
    else:
        print("No matches found to analyze.")

if __name__ == "__main__":
    analyze_last_5_days()
