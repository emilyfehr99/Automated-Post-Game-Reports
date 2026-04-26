
import sys
import os
sys.path.append('models')
sys.path.append('utils')

from daily_prediction_notifier import DailyPredictionNotifier
from meta_ensemble_predictor import MetaEnsemblePredictor

def test_playoff_logic():
    notifier = DailyPredictionNotifier()
    
    # Mock some data
    game = {
        'away_team': 'CAR',
        'home_team': 'OTT',
        'away_goalie': 'Andersen',
        'home_goalie': 'Forsberg'
    }
    
    # Mock schedule_map to indicate playoff
    # In a real run, this is populated from the NHL API
    notifier.schedule_map = {
        'CAR@OTT': {
            'id': 2025030133,
            'gameType': 3,
            'series_status': 'Series tied 2-2'
        }
    }
    
    print("Testing prediction for playoff game (Series tied 2-2)...")
    pred = notifier.meta_ensemble.predict(
        game['away_team'],
        game['home_team'],
        is_playoff=True,
        series_status='Series tied 2-2'
    )
    
    print(f"Predicted Winner: {pred['predicted_winner']}")
    print(f"Probabilities: CAR {pred['away_prob']:.1f}% / OTT {pred['home_prob']:.1f}%")
    print(f"Confidence Tier: {pred['confidence_tier']}")
    
    # Check if desperation was used (we'd need to look at internal model state or debug logs)
    # But if it didn't crash, that's a good sign.

if __name__ == "__main__":
    test_playoff_logic()
