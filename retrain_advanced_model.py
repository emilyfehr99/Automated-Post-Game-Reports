"""
Retrain the advanced metrics model with all historical games
"""

import json
from datetime import datetime
from advanced_metrics_model import AdvancedMetricsModel
from nhl_api_client import NHLAPIClient

def retrain_advanced_model():
    """Retrain the advanced model with all historical games"""
    
    print("🚀 RETRAINING ADVANCED METRICS MODEL")
    print("=" * 60)
    
    # Initialize models
    advanced_model = AdvancedMetricsModel()
    client = NHLAPIClient()
    
    # Load existing predictions to get game list
    with open('win_probability_predictions_v2.json', 'r') as f:
        predictions_data = json.load(f)
    
    all_predictions = predictions_data.get('predictions', [])
    
    print(f"📊 Found {len(all_predictions)} games to retrain")
    
    successful_games = 0
    failed_games = 0
    
    # Process each game
    for i, pred in enumerate(all_predictions):
        game_id = pred.get('game_id')
        date = pred.get('date')
        away_team = pred.get('away_team')
        home_team = pred.get('home_team')
        actual_winner = pred.get('actual_winner')
        
        print(f"\n🎯 Processing {i+1}/{len(all_predictions)}: {away_team} @ {home_team} ({date})")
        
        try:
            # Get game data
            game_data = client.get_comprehensive_game_data(game_id)
            
            if game_data:
                # Add to advanced model
                prediction = advanced_model.add_game_data(
                    game_id=game_id,
                    date=date,
                    away_team=away_team,
                    home_team=home_team,
                    game_data=game_data,
                    actual_winner=actual_winner
                )
                
                if prediction:
                    successful_games += 1
                    print(f"   ✅ Advanced prediction: {away_team} {prediction['away_prob']:.1f}% vs {home_team} {prediction['home_prob']:.1f}%")
                    print(f"   🏆 Actual winner: {actual_winner}")
                    
                    # Check if prediction was correct
                    predicted_winner = prediction['predicted_winner']
                    is_correct = (predicted_winner == actual_winner)
                    print(f"   {'✅ Correct' if is_correct else '❌ Incorrect'}")
                    
                    # Show advanced metrics
                    away_perf = prediction['away_performance']
                    home_perf = prediction['home_performance']
                    print(f"   📊 TBL: Pressure={away_perf['pressure_avg']:.1f}, Possession={away_perf['possession_avg']:.1f}")
                    print(f"   📊 DET: Pressure={home_perf['pressure_avg']:.1f}, Possession={home_perf['possession_avg']:.1f}")
                else:
                    failed_games += 1
                    print(f"   ❌ Failed to make prediction")
            else:
                failed_games += 1
                print(f"   ❌ Could not fetch game data")
                
        except Exception as e:
            failed_games += 1
            print(f"   ❌ Error: {e}")
    
    # Get final performance
    performance = advanced_model.get_model_performance()
    
    print(f"\n📊 RETRAINING SUMMARY:")
    print(f"   ✅ Successfully processed: {successful_games} games")
    print(f"   ❌ Failed to process: {failed_games} games")
    print(f"   📈 Total games: {len(all_predictions)}")
    
    print(f"\n🎯 ADVANCED MODEL PERFORMANCE:")
    print(f"   Correct predictions: {performance['correct_predictions']}/{performance['total_games']}")
    print(f"   Accuracy: {performance['accuracy']:.1f}%")
    
    print(f"\n🚀 ADVANCED METRICS MODEL COMPLETE!")
    print(f"   This model uses sophisticated metrics instead of simple weights:")
    print(f"   • Sustained Pressure (zone control)")
    print(f"   • Possession Control (pass success)")
    print(f"   • Momentum (period-by-period performance)")
    print(f"   • Territorial Control (offensive zone time)")
    print(f"   • Traditional metrics (xG, HDC, etc.)")

if __name__ == "__main__":
    retrain_advanced_model()
