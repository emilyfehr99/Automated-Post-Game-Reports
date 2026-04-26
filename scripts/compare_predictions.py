import sys, os
from pathlib import Path
_module_dirs = ['models', 'analyzers', 'scrapers', 'utils']
_base_dir = Path(__file__).resolve().parent.parent
for _d in _module_dirs:
    _p = _base_dir / _d
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from playoff_predictor import PlayoffSeriesPredictor
import json

def run_comparison():
    predictor = PlayoffSeriesPredictor()
    
    games = [
        ('BUF', 'BOS'), # Away, Home
        ('TBL', 'MTL'),
        ('COL', 'LAK'),
        ('EDM', 'ANA')
    ]
    
    print("\n🏆 DAILY PREDICTION COMPARISON (PHASE 21 vs BASELINE)")
    print("="*65)
    print(f"{'Matchup':<15} | {'Baseline':<10} | {'New Model':<10} | {'Shift'}")
    print("-" * 65)
    
    # Baseline probabilities from earlier run (recorded at 11:25 UTC)
    baselines = {
        'BUF_BOS': 0.2885,
        'TBL_MTL': 0.7157,
        'COL_LAK': 0.7325,
        'EDM_ANA': 0.6063
    }
    
    for away, home in games:
        key = f"{away}_{home}"
        res = predictor.simulate_series(away, home, simulations=5000)
        new_prob = res['away_series_win_prob']
        base_prob = baselines.get(key, 0.0)
        shift = new_prob - base_prob
        
        arrow = "↑" if shift > 0 else "↓"
        print(f"{away} @ {home:<8} | {base_prob:>10.1%} | {new_prob:>10.1%} | {arrow} {abs(shift):.1%}")

if __name__ == "__main__":
    run_comparison()
