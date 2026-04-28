import json
from pathlib import Path

def backfill_playoff_schedule_apr27():
    path = Path('data/season_2025_2026_schedule.json')
    if not path.exists():
        return
    
    with open(path, 'r') as f:
        games = json.load(f)
    
    # 2026-04-27 Playoff Games (Round 1, Game 5)
    playoff_games = [
        {
            "id": 2025030115,
            "gameDate": "2026-04-27",
            "startTimeUTC": "2026-04-27T23:00:00Z",
            "gameType": 3,
            "awayTeam": {"abbrev": "NYR"},
            "homeTeam": {"abbrev": "CAR"},
            "gameState": "FUT",
            "seriesStatus": {"topSeedWins": 2, "bottomSeedWins": 2, "topSeedTeamAbbrev": "CAR"}
        },
        {
            "id": 2025030135,
            "gameDate": "2026-04-27",
            "startTimeUTC": "2026-04-27T23:30:00Z",
            "gameType": 3,
            "awayTeam": {"abbrev": "FLA"},
            "homeTeam": {"abbrev": "TOR"},
            "gameState": "FUT",
            "seriesStatus": {"topSeedWins": 3, "bottomSeedWins": 1, "topSeedTeamAbbrev": "FLA"}
        },
        {
            "id": 2025030155,
            "gameDate": "2026-04-28T02:00:00Z",
            "gameDate_actual": "2026-04-27",
            "startTimeUTC": "2026-04-28T02:00:00Z",
            "gameType": 3,
            "awayTeam": {"abbrev": "VGK"},
            "homeTeam": {"abbrev": "DAL"},
            "gameState": "FUT",
            "seriesStatus": {"topSeedWins": 1, "bottomSeedWins": 3, "topSeedTeamAbbrev": "DAL"}
        },
        {
            "id": 2025030175,
            "gameDate": "2026-04-28T02:30:00Z",
            "gameDate_actual": "2026-04-27",
            "startTimeUTC": "2026-04-28T02:30:00Z",
            "gameType": 3,
            "awayTeam": {"abbrev": "WPG"},
            "homeTeam": {"abbrev": "VAN"},
            "gameState": "FUT",
            "seriesStatus": {"topSeedWins": 2, "bottomSeedWins": 2, "topSeedTeamAbbrev": "VAN"}
        }
    ]
    
    for g in playoff_games:
        if "gameDate_actual" in g:
            g["gameDate"] = g["gameDate_actual"]
    
    games.extend(playoff_games)
    
    with open(path, 'w') as f:
        json.dump(games, f, indent=2)
    print(f"✅ Appended {len(playoff_games)} Playoff games for April 27 to schedule")

if __name__ == "__main__":
    backfill_playoff_schedule_apr27()
