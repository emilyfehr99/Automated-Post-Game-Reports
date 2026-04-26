import json
import os
from datetime import datetime, timedelta

def analyze_predictions(days=5):
    prediction_file = '/Users/emilyfehr8/CascadeProjects/automated-post-game-reports/data/win_probability_predictions_v2.json'
    
    if not os.path.exists(prediction_file):
        print(f"Error: {prediction_file} not found")
        return

    with open(prediction_file, 'r') as f:
        data = json.load(f)
    
    predictions = data.get('predictions', [])
    
    # Target dates: last 5 days from April 26 (inclusive or exclusive? let's say up to yesterday)
    # 21, 22, 23, 24, 25
    target_dates = ['2026-04-21', '2026-04-22', '2026-04-23', '2026-04-24', '2026-04-25']
    
    recent_predictions = [p for p in predictions if p.get('date') in target_dates]
    
    if not recent_predictions:
        print("No predictions found for the last 5 days.")
        # Let's print the last few dates available
        all_dates = sorted(list(set(p.get('date') for p in predictions if p.get('date'))))
        print(f"Last available dates in predictions: {all_dates[-10:]}")
        return

    print(f"Found {len(recent_predictions)} predictions for dates: {target_dates}")
    
    # We'll need to fetch outcomes. Since I don't have a reliable local outcome file for these dates,
    # I'll output the game IDs and teams so I can look them up or try to fetch them.
    for p in recent_predictions:
        print(f"Date: {p['date']}, ID: {p['game_id']}, {p['away_team']} @ {p['home_team']}, Predicted: {p['predicted_winner']} ({p.get('away_win_prob',0):.1%} vs {p.get('home_win_prob',0):.1%})")

if __name__ == "__main__":
    analyze_predictions()
