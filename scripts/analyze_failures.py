import pickle
import pandas as pd
import shap
import json
import os
from datetime import datetime
from models.meta_ensemble_predictor import MetaEnsemblePredictor

def explain_failures():
    predictor = MetaEnsemblePredictor()
    
    # Games from April 28th that failed
    failures = [
        {"home": "BUF", "away": "BOS", "actual_winner": "BOS", "predicted_winner": "BUF"},
        {"home": "DAL", "away": "MIN", "actual_winner": "MIN", "predicted_winner": "DAL"},
        {"home": "EDM", "away": "ANA", "actual_winner": "EDM", "predicted_winner": "ANA"}
    ]
    
    print("🔎 ANALYZING APRIL 28th PREDICTION FAILURES...")
    print("=" * 50)
    
    if not hasattr(predictor, 'calibrated_model'):
        print("Error: Calibrated model not found.")
        return

    base_model = predictor.calibrated_model.estimator
    explainer = shap.TreeExplainer(base_model)
    
    report = []
    
    for game in failures:
        # Replicate feature extraction logic from MetaEnsemblePredictor._predict_xgboost
        home_team = game['home']
        away_team = game['away']
        game_date = datetime(2026, 4, 28) # Retrospective date
        is_playoff = True # It's playoff time
        
        tracker = predictor.history_tracker
        home_elo = tracker.get_elo(home_team)
        away_elo = tracker.get_elo(away_team)
        home_rest = tracker.get_days_rest(home_team, game_date)
        away_rest = tracker.get_days_rest(away_team, game_date)
        
        h_l5 = tracker.get_rolling_stats(home_team, 5, alpha=0.3)
        a_l5 = tracker.get_rolling_stats(away_team, 5, alpha=0.3)
        h_l10 = tracker.get_rolling_stats(home_team, 10, alpha=0.3)
        a_l10 = tracker.get_rolling_stats(away_team, 10, alpha=0.3)
        
        # Note: We skip goalie and edge features for now as they are harder to reconstruct perfectly
        # but the momentum ones (l5/l10) are the key drivers we identified.
        
        # Build minimal feature dict compatible with model
        feature_data = {f: 0.0 for f in predictor.feature_names}
        
        # Fill in the key momentum features
        feature_data['elo_diff'] = (home_elo + tracker.elo.ha) - away_elo
        feature_data['l5_goal_diff'] = h_l5.get('goal_diff', 0) - a_l5.get('goal_diff', 0)
        feature_data['l5_corsi_diff'] = h_l5.get('corsi_pct', 50) - a_l5.get('corsi_pct', 50)
        feature_data['l5_pdo_diff'] = h_l5.get('pdo', 100) - a_l5.get('pdo', 100)
        feature_data['l10_goal_diff'] = h_l10.get('goal_diff', 0) - a_l10.get('goal_diff', 0)
        feature_data['l10_xg_diff'] = h_l10.get('xg_diff', 0) - a_l10.get('xg_diff', 0)
        feature_data['regime_intensity'] = 1.0 # Playoff mode
        
        df = pd.DataFrame([feature_data])
        # Re-order to match model's expected order
        df = df[predictor.feature_names]
        
        shap_values = explainer.shap_values(df)
        if isinstance(shap_values, list):
            game_shap = shap_values[1][0]
        else:
            game_shap = shap_values[0]
            
        importance = sorted(zip(predictor.feature_names, game_shap, df.iloc[0]), key=lambda x: abs(x[1]), reverse=True)
        
        print(f"\nGame: {game['away']} @ {game['home']}")
        print(f"Actual Winner: {game['actual_winner']} | Predicted: {game['predicted_winner']}")
        print("-" * 30)
        
        game_report = {
            "game": f"{game['away']} @ {game['home']}",
            "top_drivers": []
        }
        
        for feat, val, raw in importance[:10]: # Show more drivers to find the culprit
            if abs(val) > 0.01:
                print(f"{feat:<25} | {val:>10.4f} | {raw}")
                game_report["top_drivers"].append({"feature": feat, "shap": float(val), "value": float(raw)})
        
        report.append(game_report)

    output_path = "/Users/emilyfehr8/CascadeProjects/automated-post-game-reports/artifacts/failure_analysis_apr28.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n✅ Analysis saved to {output_path}")

if __name__ == "__main__":
    explain_failures()
