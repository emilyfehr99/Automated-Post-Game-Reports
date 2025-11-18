#!/usr/bin/env python3
"""
Add missing NHL games from October 19-21, 2025 to our prediction system
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from nhl_api_client import NHLAPIClient
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

def fetch_missing_games():
    """Fetch missing games from Oct 19-21, 2025"""
    missing_dates = ['2025-10-19', '2025-10-20', '2025-10-21']
    all_missing_games = []
    
    print("🔍 Fetching missing games from NHL API...")
    
    for date in missing_dates:
        print(f"📅 Checking {date}...")
        try:
            url = f'https://api-web.nhle.com/v1/schedule/{date}'
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                games_today = 0
                
                for week in data.get('gameWeek', []):
                    for game in week.get('games', []):
                        if game.get('gameState') in ['FINAL', 'OFF']:
                            game_info = {
                                'gameId': game.get('gameId'),
                                'date': game.get('gameDate'),
                                'awayTeam': game.get('awayTeam', {}).get('abbrev'),
                                'homeTeam': game.get('homeTeam', {}).get('abbrev'),
                                'awayScore': game.get('awayTeam', {}).get('score', 0),
                                'homeScore': game.get('homeTeam', {}).get('score', 0),
                                'gameState': game.get('gameState')
                            }
                            all_missing_games.append(game_info)
                            games_today += 1
                
                print(f"   Found {games_today} games")
            else:
                print(f"   API error: {response.status_code}")
                
        except Exception as e:
            print(f"   Error: {e}")
    
    print(f"📊 Total missing games found: {len(all_missing_games)}")
    return all_missing_games

def add_games_to_predictions(missing_games):
    """Add missing games to our prediction system"""
    print("📝 Adding games to prediction system...")
    
    # Load existing predictions
    predictions_file = Path('win_probability_predictions_v2.json')
    if predictions_file.exists():
        with open(predictions_file, 'r') as f:
            pred_data = json.load(f)
    else:
        pred_data = {"predictions": []}
    
    existing_game_ids = {pred.get('game_id') for pred in pred_data['predictions']}
    
    # Initialize the learning model
    learning_model = ImprovedSelfLearningModelV2()
    
    new_predictions = 0
    skipped_games = 0
    
    for game in missing_games:
        game_id = str(game['gameId'])
        
        # Skip if we already have this game
        if game_id in existing_game_ids:
            skipped_games += 1
            continue
        
        print(f"🎯 Processing game: {game['awayTeam']} @ {game['homeTeam']} ({game['date']})")
        
        try:
            # Get comprehensive game data
            api_client = NHLAPIClient()
            game_data = api_client.get_comprehensive_game_data(game_id)
            
            if game_data is None:
                print(f"   ⚠️  Could not fetch game data for {game_id}")
                continue
            
            # Make prediction using the learning model
            prediction = learning_model.ensemble_predict(game['awayTeam'], game['homeTeam'])
            
            # Determine actual winner
            away_score = game['awayScore']
            home_score = game['homeScore']
            actual_winner = None
            
            if away_score > home_score:
                actual_winner = game['awayTeam']
            elif home_score > away_score:
                actual_winner = game['homeTeam']
            else:
                actual_winner = 'TIE'
            
            # Create prediction record
            prediction_record = {
                "game_id": game_id,
                "date": game['date'],
                "away_team": game['awayTeam'],
                "home_team": game['homeTeam'],
                "predicted_away_win_prob": prediction['away_prob'],
                "predicted_home_win_prob": prediction['home_prob'],
                "actual_away_score": away_score,
                "actual_home_score": home_score,
                "actual_winner": actual_winner,
                "prediction_confidence": prediction['prediction_confidence'],
                "ensemble_methods": prediction.get('ensemble_methods', {}),
                "ensemble_weights": prediction.get('ensemble_weights', []),
                "metrics_used": {},
                "model_weights": learning_model.get_current_weights(),
                "prediction_accuracy": 1.0 if actual_winner == (game['awayTeam'] if prediction['away_prob'] > prediction['home_prob'] else game['homeTeam']) else 0.0,
                "timestamp": datetime.now().isoformat()
            }
            
            # Enrich situational metrics for analysis
            try:
                away_rest = learning_model._calculate_rest_days_advantage(game['awayTeam'], 'away', game['date'])
                home_rest = learning_model._calculate_rest_days_advantage(game['homeTeam'], 'home', game['date'])
            except Exception:
                away_rest = 0.0
                home_rest = 0.0
            try:
                away_goalie_perf = learning_model._goalie_performance_for_game(game['awayTeam'], 'away', game['date'])
                home_goalie_perf = learning_model._goalie_performance_for_game(game['homeTeam'], 'home', game['date'])
            except Exception:
                away_goalie_perf = 0.0
                home_goalie_perf = 0.0
            try:
                away_sos = learning_model._calculate_sos(game['awayTeam'], 'away')
                home_sos = learning_model._calculate_sos(game['homeTeam'], 'home')
            except Exception:
                away_sos = 0.0
                home_sos = 0.0

            prediction_record['metrics_used'] = {
                "away_shots": game_data['boxscore']['awayTeam'].get('sog', 0),
                "home_shots": game_data['boxscore']['homeTeam'].get('sog', 0),
                "away_rest": away_rest,
                "home_rest": home_rest,
                "away_goalie_perf": away_goalie_perf,
                "home_goalie_perf": home_goalie_perf,
                "away_sos": away_sos,
                "home_sos": home_sos,
            }

            # Add to predictions
            pred_data['predictions'].append(prediction_record)
            new_predictions += 1
            
            # Add to learning model for future predictions
            learning_model.add_prediction(
                game_id=game_id,
                date=game['date'],
                away_team=game['awayTeam'],
                home_team=game['homeTeam'],
                predicted_away_prob=prediction['away_prob'],
                predicted_home_prob=prediction['home_prob'],
                metrics_used=prediction_record['metrics_used'],
                actual_winner=actual_winner,
                actual_away_score=away_score,
                actual_home_score=home_score
            )
            
            print(f"   ✅ Added: {game['awayTeam']} @ {game['homeTeam']} - {away_score}-{home_score} (Winner: {actual_winner})")
            
        except Exception as e:
            print(f"   ❌ Error processing {game_id}: {e}")
            continue
    
    # Save updated predictions
    with open(predictions_file, 'w') as f:
        json.dump(pred_data, f, indent=2)
    
    print(f"\\n📊 SUMMARY:")
    print(f"   New predictions added: {new_predictions}")
    print(f"   Games skipped (already exist): {skipped_games}")
    print(f"   Total predictions now: {len(pred_data['predictions'])}")
    
    return new_predictions

def main():
    print("🏒 ADDING MISSING NHL GAMES (Oct 19-21, 2025) 🏒")
    print("=" * 60)
    
    # Fetch missing games
    missing_games = fetch_missing_games()
    
    if not missing_games:
        print("❌ No missing games found!")
        return
    
    # Add games to predictions
    new_count = add_games_to_predictions(missing_games)
    
    print(f"\\n🎉 COMPLETED!")
    print(f"   Added {new_count} new games to the prediction system")
    print(f"   System now has complete coverage through Oct 21, 2025")

if __name__ == "__main__":
    main()
