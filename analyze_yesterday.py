
import json
import os
from datetime import datetime
import numpy as np

def analyze_performance(target_date="2025-12-09"):
    file_path = '/Users/emilyfehr8/CascadeProjects/automated-post-game-reports/data/win_probability_predictions_v2.json'
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("Error decoding JSON")
        return

    predictions = data.get("predictions", [])
    
    # Filter for target date
    # The date format in predictions might vary, let's inspect one if possible or assume YYYY-MM-DD
    # Based on previous code view, it seems to use ISO format or simple date string.
    # We will look for the date in the 'date' field.
    
    games = [p for p in predictions if p.get("date") == target_date]
    
    if not games:
        print(f"No games found for date: {target_date}")
        # Let's print the last 5 dates found to help debug
        dates = sorted(list(set(p.get("date") for p in predictions)))[-5:]
        print(f"Most recent dates in file: {dates}")
        return

    print(f"📊 Analysis for {target_date} ({len(games)} games)\n")
    
    correct_winners = 0
    correct_score_winner = 0
    exact_scores = 0
    close_scores = 0 # Within 1 goal for both teams
    
    for g in games:
        home = g.get('home_team')
        away = g.get('away_team')
        
        # Predicted
        pred_home_score = g.get('home_goals', 0) # Use the Poisson calculated integer score
        pred_away_score = g.get('away_goals', 0)
        
        pred_winner = home if g.get('predicted_home_win_prob', 0) > g.get('predicted_away_win_prob', 0) else away
        confidence = max(g.get('predicted_home_win_prob', 0), g.get('predicted_away_win_prob', 0)) * 100
        
        # Actual
        actual_home = g.get('actual_home_score')
        actual_away = g.get('actual_away_score')
        actual_winner = g.get('actual_winner') # This might be 'home' or 'away' or team name. 
        # The model code normalizes this, let's assume it's stored as 'home'/'away' or team abbrev.
        # Let's look at the structure from previous steps: "actual_winner": "home" or "away" usually.
        
        # If actual data is missing
        if actual_home is None:
            print(f"⏳ {away} @ {home}: Validation Pending (Score not updated)")
            continue
            
        # Normalize actual winner to team name
        if actual_winner == 'home':
            winner_name = home
        elif actual_winner == 'away':
            winner_name = away
        else:
            winner_name = actual_winner # might be already team name
            
        is_correct = (pred_winner == winner_name)
        if is_correct:
            correct_winners += 1
            
        # Score check
        pred_str = f"{pred_away_score}-{pred_home_score}" # Convention: Away-Home or just check values
        actual_str = f"{actual_away}-{actual_home}"
        
        # Exact score match?
        is_exact = (pred_home_score == actual_home and pred_away_score == actual_away)
        if is_exact:
            exact_scores += 1
            
        # Close score? (Within 1 goal error for each team)
        if abs(pred_home_score - actual_home) <= 1 and abs(pred_away_score - actual_away) <= 1:
            close_scores += 1
            
        icon = "✅" if is_correct else "❌"
        
        print(f"{icon} {away} @ {home}")
        print(f"   Pred: {away} {pred_away_score}-{pred_home_score} {home} (Winner: {pred_winner} {confidence:.1f}%)")
        print(f"   Real: {away} {actual_away}-{actual_home} {home}")
        
        # Score diff analysis
        err_h = actual_home - pred_home_score
        err_a = actual_away - pred_away_score
        print(f"   Error: Home {err_h:+d}, Away {err_a:+d}")
        print("-" * 40)

    print(f"\n📈 Summary for {target_date}:")
    print(f"Winner Accuracy: {correct_winners}/{len(games)} ({correct_winners/len(games)*100:.1f}%)")
    print(f"Exact Scores: {exact_scores}")
    print(f"Close Scores (±1): {close_scores}")

if __name__ == "__main__":
    analyze_performance()
