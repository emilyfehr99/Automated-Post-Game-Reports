import requests
import json
import time
import os
import sys
from pathlib import Path

# Add core path to sys.path
sys.path.append(os.getcwd())

from team_advanced_metrics_builder import TeamAdvancedMetricsBuilder

BASE_URL = "https://api-web.nhle.com/v1"

def get_season_game_ids(year_start):
    """Fetch all regular season game IDs for a given season start year (e.g., 2023)"""
    game_ids = []
    # Simplified month range for regular season
    months = [10, 11, 12, 1, 2, 3, 4]
    
    for month in months:
        year = year_start if month >= 10 else year_start + 1
        date_str = f"{year}-{month:02d}-01"
        try:
            r = requests.get(f"{BASE_URL}/schedule/{date_str}")
            if r.status_code == 200:
                data = r.json()
                for day in data.get('gameWeek', []):
                    for game in day.get('games', []):
                        if game.get('gameType') == 2: # Regular Season
                            game_ids.append(str(game['id']))
            time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching {date_str}: {e}")
            continue
            
    return list(set(game_ids))

def run_historical_reconstruction():
    builder = TeamAdvancedMetricsBuilder()
    
    # Process a sample from 2023-24 to identify "Playoff Success DNA"
    print("🔭 Identifying 2023-24 (Season ID 20232024) Regular Season samples...")
    games_23 = get_season_game_ids(2023)
    print(f"📊 Found {len(games_23)} games. Starting high-fidelity PBP reconstruction for Audit Sample...")
    
    # We'll take a significant sample of 150 games to run the correlation test
    sample_games = sorted(games_23)[:150]
    
    # Inject IDs into builder's process
    for gid in sample_games:
        if gid not in builder.processed_games:
            try:
                builder.process_game(gid)
                # Print progress every 25
                if len(builder.processed_games) % 25 == 0:
                    print(f"  Processed {len(builder.processed_games)} games...")
            except Exception as e:
                print(f"  Error on {gid}: {e}")

    builder.save()
    print("\n✅ Reconstruction of Audit Sample Complete.")

if __name__ == "__main__":
    run_historical_reconstruction()
