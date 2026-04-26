import sys, os
from pathlib import Path
_module_dirs = ['models', 'analyzers', 'scrapers', 'utils']
_base_dir = Path(__file__).resolve().parent.parent
for _d in _module_dirs:
    _p = _base_dir / _d
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from score_prediction_model import ScorePredictionModel

def audit_prediction():
    model = ScorePredictionModel()
    
    # Test a high-stakes playoff game (e.g. COL @ LAK)
    game = {'away': 'COL', 'home': 'LAK', 'is_playoff': True}
    
    print(f"\n🔬 PHASE 25 ACCURACY AUDIT: {game['away']} @ {game['home']}")
    print("=" * 60)
    
    res = model.predict_score(
        game['away'], game['home'],
        is_playoff=game['is_playoff']
    )
    
    print(f"📊 Predicted Score: {game['away']} {res['away_score']} - {game['home']} {res['home_score']}")
    print(f"📈 Expected xG:    {res['away_xg']} - {res['home_xg']}")
    print(f"⭐ Confidence:     {res['confidence']:.1%}")
    
    print("\n🧠 FEATURE ATTRIBUTION (What drove this accuracy?)")
    print("-" * 60)
    for attr in res.get('attribution', []):
        print(f" ✅ {attr}")
    
    print("\n📝 ACCURACY ANALYSIS:")
    print(f"  - The model identified {len(res.get('attribution', 0))} specific signals for this game.")
    if 'Playoff Tight Checking (-6% Scoring)' in res['attribution']:
        print("  - Playoff-specific 'checking' logic was applied to lower the score expectation.")
    if 'Star Power Boost (+10% GS)' in res['attribution']:
        print("  - Elite individual talent weights were increased due to playoff environment.")

if __name__ == "__main__":
    audit_prediction()
