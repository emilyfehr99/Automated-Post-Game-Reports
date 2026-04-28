import json
from pathlib import Path

def backfill_playoff_schedule():
    path = Path('data/season_2025_2026_schedule.json')
    if not path.exists():
        return
    
    with open(path, 'r') as f:
        games = json.load(f)
    
    # 2026-04-26 Playoff Games (Round 1, Game 4)
    playoff_games = [
        {
            "id": 2025030124,
            "gameDate": "2026-04-26",
            "startTimeUTC": "2026-04-26T23:00:00Z",
            "gameType": 3,
            "awayTeam": {"abbrev": "BUF"},
            "homeTeam": {"abbrev": "BOS"},
            "gameState": "FUT",
            "seriesStatus": {"topSeedWins": 3, "bottomSeedWins": 0, "topSeedTeamAbbrev": "BOS"}
        },
        {
            "id": 2025030144,
            "gameDate": "2026-04-26",
            "startTimeUTC": "2026-04-26T23:30:00Z",
            "gameType": 3,
            "awayTeam": {"abbrev": "TBL"},
            "homeTeam": {"abbrev": "MTL"},
            "gameState": "FUT",
            "seriesStatus": {"topSeedWins": 2, "bottomSeedWins": 1, "topSeedTeamAbbrev": "TBL"}
        },
        {
            "id": 2025030164,
            "gameDate": "2026-04-27T02:00:00Z", # Late night 
            "gameDate_actual": "2026-04-26",
            "startTimeUTC": "2026-04-27T02:00:00Z",
            "gameType": 3,
            "awayTeam": {"abbrev": "COL"},
            "homeTeam": {"abbrev": "LAK"},
            "gameState": "FUT",
            "seriesStatus": {"topSeedWins": 3, "bottomSeedWins": 0, "topSeedTeamAbbrev": "COL"}
        },
        {
            "id": 2025030184,
            "gameDate": "2026-04-27T02:30:00Z",
            "gameDate_actual": "2026-04-26",
            "startTimeUTC": "2026-04-27T02:30:00Z",
            "gameType": 3,
            "awayTeam": {"abbrev": "EDM"},
            "homeTeam": {"abbrev": "ANA"},
            "gameState": "FUT",
            "seriesStatus": {"topSeedWins": 2, "bottomSeedWins": 1, "topSeedTeamAbbrev": "EDM"}
        }
    ]
    
    # Hack for timezone: standard schedule uses gameDate
    for g in playoff_games:
        if "gameDate_actual" in g:
            g["gameDate"] = g["gameDate_actual"]
    
    games.extend(playoff_games)
    
    with open(path, 'w') as f:
        json.dump(games, f, indent=2)
    print(f"✅ Appended {len(playoff_games)} Playoff games to schedule")

if __name__ == "__main__":
    backfill_playoff_schedule()
