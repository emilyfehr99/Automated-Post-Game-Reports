import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.meta_ensemble_predictor import MetaEnsemblePredictor
from models.score_prediction_model import ScorePredictionModel

def test_attribution():
    predictor = MetaEnsemblePredictor()
    score_model = ScorePredictionModel()
    
    # Mock a playoff game with series status
    away, home = "TOR", "BOS"
    series_status = "BOS leads 3-1"
    
    print(f"Testing attribution for {away} @ {home} ({series_status})")
    
    for i in range(10):
        # Predict using score model
        # The pseudo-random seed in _map_scoreline_nb uses away, home, away_mu, home_mu, confidence, is_playoff. 
        # To test variance, we need to artificially inject some noise or use different confidence.
        # Wait, the pseudo-random seed is DETERMINISTIC based on input. 
        # For a single game, it will always return the same score! This is intended!
        # Let's test with slightly different xG (simulating different games or slightly different inputs over days)
        
        # We will manually call _map_scoreline_nb to test the distribution
        score_res = score_model.predict_score(away, home, is_playoff=True, series_status=series_status)
        
        away_xg = score_res['away_expected']
        home_xg = score_res['home_expected']
        
        a, h = score_model._map_scoreline_nb(
            away=away, home=home,
            away_mu=away_xg + (i * 0.05), home_mu=home_xg,
            winner_side="home"
        )
        print(f"Iter {i} (Away xG {away_xg + i*0.05:.2f}): Score {a}-{h}")


if __name__ == "__main__":
    test_attribution()
