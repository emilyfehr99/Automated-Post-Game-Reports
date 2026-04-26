
import sys
import os
sys.path.append('models')
from playoff_predictor import PlayoffSeriesPredictor

PLAYOFF_TEAMS = [
  "ANA", "BOS", "BUF", "CAR", "COL", "DAL", "EDM", "LAK", 
  "MIN", "MTL", "OTT", "PHI", "PIT", "TBL", "UTA", "VGK"
]

def run_filtered_audit():
    predictor = PlayoffSeriesPredictor()
    rankings = predictor.predict_cup_winner()
    
    filtered = [r for r in rankings if r['team'] in PLAYOFF_TEAMS]
    
    print("\n🏆 CORRECTED 2026 STANLEY CUP DNA AUDIT (PLAYOFF TEAMS ONLY)")
    print("="*60)
    for i, r in enumerate(filtered[:10], 1):
        star = "⭐ " if i == 1 else "   "
        print(f"{star}{i:<2}. {r['team']:<5} | DNA Alignment: {r['dna_alignment']:>8.4f}")

if __name__ == "__main__":
    run_filtered_audit()
