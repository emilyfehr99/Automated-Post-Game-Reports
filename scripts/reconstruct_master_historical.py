import requests
import json
import time
import os
import sys
from pathlib import Path

# Add core path
sys.path.append(os.getcwd())
from team_advanced_metrics_builder import TeamAdvancedMetricsBuilder

BASE_URL = "https://api-web.nhle.com/v1"
SEASONS = [2019, 2020, 2021, 2022, 2023, 2024]

def get_season_game_ids(year_start):
    """Fetch all regular season (Type 2) game IDs for a season."""
    game_ids = []
    if year_start == 2020:
        months = [1, 2, 3, 4, 5]
    else:
        months = [10, 11, 12, 1, 2, 3, 4]
    for month in months:
        year = year_start if month >= 10 else year_start + 1
        date_str = f"{year}-{month:02d}-01"
        try:
            r = requests.get(f"{BASE_URL}/schedule/{date_str}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                for day in data.get('gameWeek', []):
                    for game in day.get('games', []):
                        if game.get('gameType') == 2:
                            game_ids.append(str(game['id']))
            time.sleep(0.05)
        except:
            continue
    return list(set(game_ids))

def run_master_reconstruction():
    builder = TeamAdvancedMetricsBuilder()
    # Use the new setter
    builder.set_output_path('data/historical_master_metrics.json')
    
    all_game_ids = []
    for s in SEASONS:
        gids = get_season_game_ids(s)
        all_game_ids.extend(gids)
    
    import random
    random.shuffle(all_game_ids)
    # 300 game multi-season sample across 5 years
    sample_ids = all_game_ids[:300]
    
    print(f"🧩 Processing 300-game Multi-Season 'DNA sample' for {SEASONS} era...")
    for i, gid in enumerate(sample_ids):
        try:
            builder.process_game(gid)
        except Exception:
            continue
    builder.save()
    print("\n✅ Master DNA Database Created: data/historical_master_metrics.json")

if __name__ == "__main__":
    run_master_reconstruction()
