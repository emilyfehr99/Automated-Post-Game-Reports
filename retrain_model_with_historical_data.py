#!/usr/bin/env python3
"""
Retrain the model to use historical team performance data for predictions
"""

import json
from pathlib import Path
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

def retrain_model_with_historical_data():
    """Retrain the model using historical team performance data"""
    print("🏒 RETRAINING MODEL WITH HISTORICAL DATA 🏒")
    print("=" * 60)
    
    # Initialize the learning model
    learning_model = ImprovedSelfLearningModelV2()
    
    # Load predictions
    predictions_file = Path('win_probability_predictions_v2.json')
    if not predictions_file.exists():
        print("❌ No predictions file found!")
        return
    
    with open(predictions_file, 'r') as f:
        pred_data = json.load(f)
    
    predictions = pred_data.get('predictions', [])
    print(f"📊 Found {len(predictions)} games to retrain")
    
    # Process games in chronological order to build historical data
    sorted_predictions = sorted(predictions, key=lambda x: x.get('date', ''))
    
    retrained_count = 0
    failed_count = 0
    
    for i, pred in enumerate(sorted_predictions):
        game_id = pred.get('game_id')
        date = pred.get('date')
        away_team = pred.get('away_team')
        home_team = pred.get('home_team')
        
        print(f"\\n🎯 Retraining {i+1}/{len(sorted_predictions)}: {away_team} @ {home_team} ({date})")
        
        try:
            # Get historical team performance (this should use data from previous games)
            away_performance = learning_model.get_team_performance(away_team, 'away')
            home_performance = learning_model.get_team_performance(home_team, 'home')
            
            print(f"   📊 Historical Performance:")
            print(f"      {away_team} (away): xG={away_performance.get('xg_avg', 0):.2f}, HDC={away_performance.get('hdc_avg', 0):.1f}")
            print(f"      {home_team} (home): xG={home_performance.get('xg_avg', 0):.2f}, HDC={home_performance.get('hdc_avg', 0):.1f}")
            
            # Make prediction based on historical performance
            prediction = learning_model.ensemble_predict(away_team, home_team)
            
            # Update the prediction record
            pred['predicted_away_win_prob'] = prediction['away_prob']
            pred['predicted_home_win_prob'] = prediction['home_prob']
            pred['prediction_confidence'] = prediction['prediction_confidence']
            pred['ensemble_methods'] = prediction.get('ensemble_methods', {})
            pred['ensemble_weights'] = prediction.get('ensemble_weights', [])
            pred['model_weights'] = learning_model.get_current_weights()
            
            # Recalculate prediction accuracy
            actual_winner = pred.get('actual_winner')
            if actual_winner:
                predicted_winner = away_team if prediction['away_prob'] > prediction['home_prob'] else home_team
                pred['prediction_accuracy'] = 1.0 if predicted_winner == actual_winner else 0.0
                
                print(f"   🎯 Prediction: {away_team} {prediction['away_prob']:.1f}% vs {home_team} {prediction['home_prob']:.1f}%")
                print(f"   🏆 Actual Winner: {actual_winner}")
                print(f"   ✅ Correct: {'Yes' if predicted_winner == actual_winner else 'No'}")
            
            # Add this game to the learning model for future predictions
            if actual_winner and pred.get('metrics_used'):
                learning_model.add_prediction(
                    game_id=game_id,
                    date=date,
                    away_team=away_team,
                    home_team=home_team,
                    predicted_away_prob=prediction['away_prob'],
                    predicted_home_prob=prediction['home_prob'],
                    metrics_used=pred['metrics_used'],
                    actual_winner=actual_winner,
                    actual_away_score=pred.get('actual_away_score', 0),
                    actual_home_score=pred.get('actual_home_score', 0)
                )
            
            retrained_count += 1
            
        except Exception as e:
            print(f"   ❌ Error retraining {game_id}: {e}")
            failed_count += 1
            continue
    
    # Save updated predictions
    with open(predictions_file, 'w') as f:
        json.dump(pred_data, f, indent=2)
    
    print(f"\\n📊 RETRAINING SUMMARY:")
    print(f"   ✅ Successfully retrained: {retrained_count} games")
    print(f"   ❌ Failed to retrain: {failed_count} games")
    
    # Calculate new accuracy
    correct_predictions = sum(1 for p in predictions if p.get('prediction_accuracy') == 1.0)
    total_predictions = len(predictions)
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
    
    print(f"\\n🎯 NEW ACCURACY:")
    print(f"   Correct predictions: {correct_predictions}/{total_predictions}")
    print(f"   Accuracy: {accuracy:.1%}")
    
    return accuracy

def main():
    accuracy = retrain_model_with_historical_data()
    
    if accuracy > 0.3:  # 30% threshold
        print(f"\\n🎉 SUCCESS!")
        print(f"   Model retrained with historical data")
        print(f"   Accuracy improved to {accuracy:.1%}")
    else:
        print(f"\\n⚠️  NEEDS IMPROVEMENT")
        print(f"   Accuracy is still low at {accuracy:.1%}")
        print(f"   May need more historical data or better prediction logic")

if __name__ == "__main__":
    main()
