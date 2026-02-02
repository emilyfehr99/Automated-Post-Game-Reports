#!/ env python3
import json
import urllib.request
from datetime import datetime, timedelta

def get_date_str(delta=0):
    # NHL API expects dates in YYYY-MM-DD
    # We check today and yesterday to be safe
    return (datetime.now() - timedelta(days=delta)).strftime("%Y-%m-%d")

def check_games():
    # Load processed games
    processed_games = set()
    try:
        with open('processed_games.json', 'r') as f:
            data = json.load(f)
            processed_games = set(str(g) for g in data.get('games', []))
    except Exception as e:
        print(f"Note: Could not load processed_games.json (normal for first run): {e}")

    dates_to_check = [get_date_str(0), get_date_str(1)]
    found_reason_to_run = False
    
    print(f"Checking games for {dates_to_check}...")
    
    for date_str in dates_to_check:
        url = f"https://api-web.nhle.com/v1/schedule/{date_str}"
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                if 'gameWeek' in data:
                    for day in data['gameWeek']:
                        if day.get('date') == date_str:
                            games = day.get('games', [])
                            for game in games:
                                game_id = str(game.get('id'))
                                state = game.get('gameState')
                                
                                # Priority 1: LIVE games (worth monitoring)
                                if state in ['LIVE', 'CRIT']:
                                    print(f"Found LIVE game {game_id}")
                                    return True
                                
                                # Priority 2: FINAL games that haven't been processed
                                if state in ['FINAL', 'OFF'] and game_id not in processed_games:
                                    print(f"Found UNPROCESSED completed game {game_id}")
                                    return True
        except Exception as e:
            print(f"Error checking {date_str}: {e}")
            
    return found_reason_to_run

if __name__ == "__main__":
    if check_games():
        print("YES")
        exit(0) # Exit with 0 to indicate we should run
    else:
        print("NO")
        exit(1) # Exit with non-zero to indicate we should skip
