import requests
import json
import os
from datetime import datetime, timedelta

def get_scores_for_date(date_str):
    url = f"https://api-web.nhle.com/v1/score/{date_str}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def analyze_last_5_days_calendar():
    prediction_file = '/Users/emilyfehr8/CascadeProjects/automated-post-game-reports/data/win_probability_predictions_v2.json'
    with open(prediction_file, 'r') as f:
        data = json.load(f)
    predictions = data.get('predictions', [])

    today = datetime(2026, 4, 26)
    
    # We want to check games that happened on April 21, 22, 23, 24, 25
    calendar_dates = [ (today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 6) ]
    calendar_dates.reverse() # 21 to 25

    print(f"Analyzing calendar dates: {calendar_dates}")
    
    daily_results = {}

    for date_str in calendar_dates:
        print(f"\nChecking games on {date_str}...")
        scores = get_scores_for_date(date_str)
        if not scores:
            print(f"  Failed to fetch scores for {date_str}")
            continue
            
        daily_results[date_str] = []
        for game in scores.get('games', []):
            gid = game.get('id')
            state = game.get('gameState')
            if state not in ['OFF', 'FINAL']:
                print(f"  Game {gid} ({game['awayTeam']['abbrev']} @ {game['homeTeam']['abbrev']}) is {state}, skipping.")
                continue
                
            away_team = game['awayTeam']['abbrev']
            home_team = game['homeTeam']['abbrev']
            away_score = game['awayTeam']['score']
            home_score = game['homeTeam']['score']
            winner = away_team if away_score > home_score else home_team
            
            # Find the most recent prediction for this game ID
            # (Sometimes there are multiple runs, we take the one recorded last before the game)
            game_preds = [p for p in predictions if p.get('game_id') == gid]
            if not game_preds:
                # Try finding by teams if ID doesn't match for some reason
                game_preds = [p for p in predictions if p.get('away_team') == away_team and p.get('home_team') == home_team]
            
            if game_preds:
                # Take the last one in the list (assuming chronological)
                pred = game_preds[-1]
                pred_winner = pred.get('predicted_winner')
                is_correct = pred_winner == winner
                status = "✅ CORRECT" if is_correct else "❌ WRONG"
                
                print(f"  Game {gid}: {away_team} {away_score} - {home_score} {home_team} | Predicted: {pred_winner} | {status}")
                daily_results[date_str].append(is_correct)
            else:
                print(f"  Game {gid}: {away_team} {away_score} - {home_score} {home_team} | No prediction found.")

    print("\n--- FINAL SUMMARY ---")
    grand_correct = 0
    grand_total = 0
    for date_str in calendar_dates:
        results = daily_results.get(date_str, [])
        if results:
            correct = sum(1 for r in results if r)
            total = len(results)
            print(f"{date_str}: {correct}/{total} ({correct/total:.1%})")
            grand_correct += correct
            grand_total += total
        else:
            print(f"{date_str}: No games with predictions found.")
            
    if grand_total > 0:
        print(f"\nOverall Accuracy (Last 5 Days): {grand_correct}/{grand_total} ({grand_correct/grand_total:.1%})")
    else:
        print("\nNo data found to summarize.")

if __name__ == "__main__":
    analyze_last_5_days_calendar()
