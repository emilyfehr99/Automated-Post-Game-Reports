import json
import time

def fix_odds_apr27():
    odds = {
        "PHI_vs_PIT": {
            "away_prob": 0.447, "home_prob": 0.553,
            "away_american": 114, "home_american": -136,
            "timestamp": time.time(), "provider": "ActionNetwork"
        },
        "VGK_vs_UTA": {
            "away_prob": 0.511, "home_prob": 0.489,
            "away_american": -115, "home_american": -105,
            "timestamp": time.time(), "provider": "ActionNetwork"
        }
    }
    
    with open('data/vegas_odds.json', 'w') as f:
        json.dump(odds, f, indent=2)
    print("✅ Fixed Vegas odds for PHI@PIT and VGK@UTA.")

if __name__ == "__main__":
    fix_odds_apr27()
