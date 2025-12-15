
import requests
import json
import datetime

BASE_URL = "http://localhost:5002"

def check_predictions():
    print(f"Checking {BASE_URL}/api/predictions/today...")
    try:
        response = requests.get(f"{BASE_URL}/api/predictions/today")
        if response.status_code == 200:
            preds = response.json()
            print(f"Found {len(preds)} predictions.")
            if len(preds) > 0:
                print("Sample prediction:", json.dumps(preds[0], indent=2))
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Connection error: {e}")

def check_live_game(game_id):
    print(f"Checking {BASE_URL}/api/live-game/{game_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/live-game/{game_id}")
        if response.status_code == 200:
            data = response.json()
            print("Live game data keys:", data.keys())
            if 'away_prob' in data:
                print(f"Away Prob: {data['away_prob']}, Home Prob: {data['home_prob']}")
            else:
                print("WARNING: away_prob/home_prob missing from live game data!")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    check_predictions()
    # Need a game ID - usually we'd get this from the schedule or predictions
