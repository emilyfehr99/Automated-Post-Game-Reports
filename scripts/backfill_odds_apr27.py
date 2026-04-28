import json
import time

def backfill_odds_apr27():
    odds = {
        "NYR_vs_CAR": {
            "away_prob": 0.435, "home_prob": 0.565,
            "away_american": 130, "home_american": -155,
            "timestamp": time.time(), "provider": "Manual"
        },
        "FLA_vs_TOR": {
            "away_prob": 0.545, "home_prob": 0.455,
            "away_american": -120, "home_american": 100,
            "timestamp": time.time(), "provider": "Manual"
        },
        "VGK_vs_DAL": {
            "away_prob": 0.444, "home_prob": 0.556,
            "away_american": 125, "home_american": -145,
            "timestamp": time.time(), "provider": "Manual"
        },
        "WPG_vs_VAN": {
            "away_prob": 0.476, "home_prob": 0.524,
            "away_american": 110, "home_american": -130,
            "timestamp": time.time(), "provider": "Manual"
        }
    }
    
    with open('data/vegas_odds.json', 'w') as f:
        json.dump(odds, f, indent=2)
    print("✅ Backfilled Vegas odds for April 27 playoff games.")

if __name__ == "__main__":
    backfill_odds_apr27()
