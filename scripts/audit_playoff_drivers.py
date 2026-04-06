import json
import numpy as np
from pathlib import Path

def run_audit():
    # Load Playoff Outcomes (Success Rank: 0-4)
    # R1 Out = 0, R2 Out = 1, CF Out = 2, Final Out = 3, Champ = 4
    playoff_outcomes = {
        "2023_2024": {
            "NYR": 2, "CAR": 1, "NYI": 0, "WSH": 0, "FLA": 4, "BOS": 1, "TBL": 0, "TOR": 0,
            "DAL": 2, "WPG": 0, "COL": 1, "NSH": 0, "VAN": 1, "EDM": 3, "LAK": 0, "VGK": 0
        },
        "2022_2023": {
            "BOS": 0, "TOR": 1, "TBL": 0, "FLA": 3, "CAR": 2, "NJD": 1, "NYR": 0, "NYI": 0,
            "COL": 0, "DAL": 2, "MIN": 0, "SEA": 1, "VGK": 4, "EDM": 1, "LAK": 0, "WPG": 0
        }
    }
    
    # Load Advanced Metrics
    metrics_path = Path('data/team_advanced_metrics.json')
    if not metrics_path.exists():
        print("❌ Advanced metrics file not found.")
        return
        
    with open(metrics_path) as f:
        metrics_data = json.load(f)
        
    teams_stats = metrics_data.get('teams', {})
    
    # Metrics to test
    feature_list = [
        'rebound_gen_rate', 'rush_rate', 'rush_capitalization', 
        'pizzas_per_game', 'hd_pizzas_per_game', 'slot_blocks_per_game'
    ]
    
    audit_results = {}
    
    for feature in feature_list:
        x = []
        y = []
        
        # We aggregate for 2023-24 (our recently reconstructed sample)
        for team, rank in playoff_outcomes["2023_2024"].items():
            if team in teams_stats:
                val = teams_stats[team].get(feature, 0)
                x.append(val)
                y.append(rank)
        
        if len(x) > 5:
            correlation = np.corrcoef(x, y)[0, 1]
            audit_results[feature] = correlation

    # Sort results by absolute correlation
    sorted_audit = sorted(audit_results.items(), key=lambda x: abs(x[1]), reverse=True)
    
    print("📊 PLAYOFF SUCCESS CORRELATION AUDIT")
    print("=" * 60)
    print(f"{'Metric':<25} | {'Correlation (Success Rank)':<25}")
    print("-" * 60)
    for metric, corr in sorted_audit:
        print(f"{metric:<25} | {corr:>25.4f}")
    
    print("\n💡 AUDIT INSIGHTS")
    top_metric = sorted_audit[0][0]
    direction = "Strong correlation" if sorted_audit[0][1] > 0 else "Inverse correlation"
    print(f"- {top_metric} identified as the #1 driver of playoff success ({direction}).")
    
    # Suggest weights for PlayoffModel
    weights = {m: round(abs(c), 2) for m, c in audit_results.items() if abs(c) > 0.1}
    print(f"- Recommended Playoff Weights: {json.dumps(weights, indent=2)}")

if __name__ == "__main__":
    run_audit()
