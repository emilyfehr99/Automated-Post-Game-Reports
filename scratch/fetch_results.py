import requests
import json

game_ids = [2025030144, 2025030164, 2025030185, 2025030124, 2025030174, 2025030186]
results = {}

for gid in game_ids:
    url = f"https://api-web.nhle.com/v1/gamecenter/{gid}/boxscore"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            away_score = data.get('awayTeam', {}).get('score', 0)
            home_score = data.get('homeTeam', {}).get('score', 0)
            away_team = data.get('awayTeam', {}).get('abbrev')
            home_team = data.get('homeTeam', {}).get('abbrev')
            winner = away_team if away_score > home_score else home_team
            results[str(gid)] = {
                'away_team': away_team,
                'home_team': home_team,
                'away_score': away_score,
                'home_score': home_score,
                'winner': winner
            }
        else:
            print(f"Failed to fetch {gid}: {response.status_code}")
    except Exception as e:
        print(f"Error fetching {gid}: {e}")

print(json.dumps(results, indent=2))
