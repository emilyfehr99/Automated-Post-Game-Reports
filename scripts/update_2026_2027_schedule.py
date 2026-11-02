#!/usr/bin/env python3
"""
Fetch and update the complete, official 2026-2027 NHL Schedule
Directly from official NHL API club-schedule-season endpoints.
"""

import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

TEAMS = [
    "ANA", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL",
    "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NJD",
    "NSH", "NYI", "NYR", "OTT", "PHI", "PIT", "SEA", "SJS",
    "STL", "TBL", "TOR", "UTA", "VAN", "VGK", "WPG", "WSH"
]

def fetch_team_schedule(team: str):
    url = f"https://api-web.nhle.com/v1/club-schedule-season/{team}/20262027"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("games", [])
    except Exception as e:
        print(f"Error fetching schedule for {team}: {e}")
        return []

def main():
    print(f"Fetching official 2026-2027 schedule for {len(TEAMS)} teams...")
    all_games_map = {}
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_team_schedule, t): t for t in TEAMS}
        for future in as_completed(futures):
            team = futures[future]
            games = future.result()
            print(f"  {team}: {len(games)} games fetched")
            for g in games:
                gid = g.get("id")
                if gid:
                    all_games_map[gid] = g

    full_schedule = list(all_games_map.values())
    full_schedule.sort(key=lambda g: (g.get("gameDate", ""), g.get("startTimeUTC", ""), g.get("id", 0)))
    print(f"\nTotal unique 2026-2027 games compiled: {len(full_schedule)}")
    
    dates = [g.get("gameDate") for g in full_schedule if g.get("gameDate")]
    if dates:
        print(f"Date range: {min(dates)} to {max(dates)}")

    out_path = Path("data/season_2026_2027_schedule.json")
    with open(out_path, "w") as f:
        json.dump(full_schedule, f, indent=2)
    print(f"Successfully saved to {out_path}!")

if __name__ == "__main__":
    main()
