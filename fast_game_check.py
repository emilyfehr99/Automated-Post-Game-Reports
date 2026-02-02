#!/usr/bin/env python3
import json
import urllib.request
from datetime import datetime, timedelta, timezone

def get_date_str(delta=0):
    # NHL API expects dates in YYYY-MM-DD
    # Use UTC to match API expectations and avoid local time confusion
    return (datetime.now(timezone.utc) - timedelta(days=delta)).strftime("%Y-%m-%d")

def check_games():
    # Load processed games
    processed_games = set()
    try:
        with open('processed_games.json', 'r') as f:
            data = json.load(f)
            processed_games = set(str(g) for g in data.get('games', []))
    except Exception as e:
        print(f"Note: Could not load processed_games.json: {e}")

    now_utc = datetime.now(timezone.utc)
    # Check today and yesterday
    dates_to_check = [get_date_str(0), get_date_str(1)]
    found_reason_to_run = False
    
    print(f"Checking games for {dates_to_check}... (Current UTC: {now_utc})")
    
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
                                start_time_str = game.get('startTimeUTC')
                                
                                try:
                                    start_dt = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                                except (ValueError, TypeError):
                                    start_dt = None

                                # 1. LIVE games - Definitely run
                                if state in ['LIVE', 'CRIT']:
                                    print(f"Found LIVE game {game_id} ({game.get('awayTeam', {}).get('abbrev')} @ {game.get('homeTeam', {}).get('abbrev')})")
                                    return True
                                
                                # 2. Completed games - Run if not processed and NOT STALE (> 24h old)
                                if state in ['FINAL', 'OFF'] and game_id not in processed_games:
                                    if start_dt and (now_utc - start_dt) > timedelta(hours=24):
                                        print(f"Skipping STALE unprocessed game {game_id} (started > 24h ago)")
                                        continue
                                    print(f"Found UNPROCESSED completed game {game_id}")
                                    return True
                                
                                # 3. Future games - Run only if starting SOON (< 2 hours)
                                if state in ['FUT', 'PRE'] and start_dt:
                                    if (start_dt - now_utc) < timedelta(hours=2):
                                        print(f"Found UPCOMING game {game_id} starting within 2 hours")
                                        return True

        except Exception as e:
            print(f"Error checking {date_str}: {e}")
            
    return found_reason_to_run

if __name__ == "__main__":
    if check_games():
        print("YES")
        exit(0)
    else:
        print("NO")
        exit(1)
