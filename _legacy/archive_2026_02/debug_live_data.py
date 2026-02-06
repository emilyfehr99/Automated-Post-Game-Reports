
import requests
import json
import datetime

# Use production backend since that's what the Vercel app uses
BACKEND_URL = "https://nhl-analytics-api.onrender.com"

def get_live_game_id():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    url = f"https://api-web.nhle.com/v1/schedule/{today}"
    try:
        print(f"Fetching schedule for {today}...")
        resp = requests.get(url)
        data = resp.json()
        if 'gameWeek' in data and len(data['gameWeek']) > 0:
            games = data['gameWeek'][0]['games']
            for game in games:
                state = game.get('gameState')
                print(f"Game: {game['awayTeam']['abbrev']} vs {game['homeTeam']['abbrev']} (State: {state}, ID: {game['id']})")
                if state in ['LIVE', 'CRIT']:
                    return game['id']
                # If no live game, return a FINAL one to test structure
                if state in ['FINAL', 'OFF']:
                     # prefer live, but verify final too
                     pass
            
            # Return first game if no live ones, just to check
            return games[0]['id'] if games else None
    except Exception as e:
        print(f"Error fetching schedule: {e}")
    return None

def check_live_game_data(game_id):
    if not game_id:
        print("No game ID found.")
        return

    url = f"{BACKEND_URL}/api/live-game/{game_id}"
    print(f"Checking {url}...")
    try:
        resp = requests.get(url)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print("Keys:", list(data.keys()))
            print(f"away_prob: {data.get('away_prob')}")
            print(f"home_prob: {data.get('home_prob')}")
            print(f"Type of away_prob: {type(data.get('away_prob'))}")
        else:
            print("Response:", resp.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    gid = get_live_game_id()
    if gid:
        check_live_game_data(gid)
    else:
        print("No games found.")
