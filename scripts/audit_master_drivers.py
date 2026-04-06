import json
import numpy as np
from pathlib import Path

def run_master_audit():
    # 5-Year Cup Winners and Finalists (Success Rank 0-4)
    # 4=Champion, 3=Finalist, 2=Conf Final, 1=Round 2, 0=Round 1
    master_outcomes = {
        "20232024": {"FLA": 4, "EDM": 3, "NYR": 2, "DAL": 2, "VAN": 1, "CAR": 1, "BOS": 1, "COL": 1, "WPG": 0, "NSH": 0, "VGK": 0, "LAK": 0, "TOR": 0, "TBL": 0, "NYI": 0, "WSH": 0},
        "20222023": {"VGK": 4, "FLA": 3, "CAR": 2, "DAL": 2, "SEA": 1, "NJD": 1, "TOR": 1, "EDM": 1, "BOS": 0, "COL": 0, "NYR": 0, "MIN": 0, "TBL": 0, "LAK": 0, "NYI": 0, "WPG": 0},
        "20212022": {"COL": 4, "TBL": 3, "NYR": 2, "EDM": 2, "FLA": 1, "CAR": 1, "STL": 1, "CGY": 1, "MIN": 0, "TOR": 0, "BOS": 0, "WSH": 0, "PIT": 0, "NSH": 0, "DAL": 0, "LAK": 0},
        "20202021": {"TBL": 4, "MTL": 3, "NYI": 2, "VGK": 2, "CAR": 1, "COL": 1, "BOS": 1, "WPG": 1, "PIT": 0, "WSH": 0, "FLA": 0, "NSH": 0, "MIN": 0, "EDM": 0, "TOR": 0, "STL": 0},
        "20192020": {"TBL": 4, "DAL": 3, "NYI": 2, "VGK": 2, "PHI": 1, "COL": 1, "VAN": 1, "BOS": 1, "WSH": 0, "STL": 0, "CAR": 0, "ARI": 0, "MTL": 0, "CHI": 0, "CBJ": 0, "CGY": 0}
    }
    
    metrics_path = Path('data/historical_master_metrics.json')
    if not metrics_path.exists():
        print("❌ Master metrics not found.")
        return
        
    with open(metrics_path) as f:
        metrics_data = json.load(f)
    
    teams_stats = metrics_data.get('teams', {})
    
    # Audit across all 5 years
    feature_list = [
        'rebound_gen_rate', 'rush_rate', 'rush_capitalization', 
        'pizzas_per_game', 'hd_pizzas_per_game', 'slot_blocks_per_game'
    ]
    
    master_results = {}
    for feature in feature_list:
        x, y = [], []
        for season_id, outcomes in master_outcomes.items():
            for team, rank in outcomes.items():
                if team in teams_stats:
                    x.append(teams_stats[team].get(feature, 0))
                    y.append(rank)
        
        if len(x) > 10:
            correlation = np.corrcoef(x, y)[0, 1]
            master_results[feature] = correlation

    # Sort results to identify the 'Championship Profile'
    sorted_master = sorted(master_results.items(), key=lambda x: abs(x[1]), reverse=True)
    
    print("🏆 THE STANLEY CUP 'CHAMPIONSHIP DNA' AUDIT (2020-2025)")
    print("=" * 60)
    print(f"{'Universal Success Driver':<25} | {'5-Year Correlation':<20}")
    print("-" * 60)
    for metric, corr in sorted_master:
        print(f"{metric:<25} | {corr:>20.4f}")
    
    weights = {m: round(abs(c), 2) for m, c in master_results.items() if abs(c) > 0.05}
    print(f"\n✅ Definitive Championship Weights: {json.dumps(weights, indent=2)}")
    
if __name__ == "__main__":
    run_master_audit()
