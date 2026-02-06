
import sys
import os
from datetime import datetime

# Adjust path to import the model
sys.path.append('/Users/emilyfehr8/CascadeProjects/automated-post-game-reports')

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2, DEFAULT_SCORE_WEIGHTS

def test_score_learning():
    print("🧪 Testing Self-Learning Score Model...")
    
    # Initialize model
    model = ImprovedSelfLearningModelV2()
    
    # Define a mock prediction history
    # Scenario: High PDO teams are scoring MORE than we predicted.
    # This means we are UNDER-valuing PDO.
    # Expectation: pdo_weight should INCREASE.
    
    # Setup:
    # Home Team: PDO=105 (+5 above norm). Normalized Feature = 5.0.
    # Prediction: 2 goals.
    # Actual: 5 goals.
    # Error: +3 goals.
    
    mock_prediction = {
        'game_id': 'test_game_1',
        'home_team': 'TEST_H',
        'away_team': 'TEST_A',
        'predicted_home_score': 2,
        'predicted_away_score': 2,
        'actual_home_score': 5,
        'actual_away_score': 2,
        'metrics_used': {
            'home_goals_season': 3.0,
            'home_xg_season': 3.0,
            'home_pdo_season': 5.0,   # High PDO (+5)
            'home_pp_season': 0.0,
            'home_recent_goals': 3.0,
            
            'away_goals_season': 3.0,
            'away_xg_season': 3.0,
            'away_pdo_season': 0.0,
            'away_pp_season': 0.0,
            'away_recent_goals': 3.0
        }
    }
    
    # Replicate this for 10 games to get a strong signal
    recent_predictions = [mock_prediction] * 10
    
    # Calculate updates
    print("📊 Calculating weight updates based on +3 error for high PDO team...")
    updates = model._calculate_score_weight_updates(recent_predictions)
    
    print("\nWeight Updates:")
    for k, v in updates.items():
        print(f"  {k}: {v:.5f}")
        
    # Validation
    # pdo_weight update should be: Rate(0.01) * Error(+3) * Feature(5.0/10.0 = 0.5) = +0.015 approx
    assert updates['pdo_weight'] > 0, "❌ PDO weight should increase!"
    print("\n✅ PASSED: PDO weight increased as expected.")
    
    # Test Reverse: Over-prediction
    # If we predicted 5, outcome was 2 (Error -3).
    # Then pdo_weight should DECREASE because high pdo didn't help.
    
    mock_prediction_reverse = mock_prediction.copy()
    mock_prediction_reverse['predicted_home_score'] = 5
    mock_prediction_reverse['actual_home_score'] = 2
    
    print("\n📊 Calculating weight updates based on -3 error (Over-prediction)...")
    updates_rev = model._calculate_score_weight_updates([mock_prediction_reverse] * 10)
    
    for k, v in updates_rev.items():
        print(f"  {k}: {v:.5f}")
        
    assert updates_rev['pdo_weight'] < 0, "❌ PDO weight should decrease!"
    print("\n✅ PASSED: PDO weight decreased as expected.")
    
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    test_score_learning()
