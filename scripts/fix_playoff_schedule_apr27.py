import json
from pathlib import Path

def fix_playoff_schedule_apr27():
    path = Path('data/season_2025_2026_schedule.json')
    if not path.exists():
        return
    
    with open(path, 'r') as f:
        games = json.load(f)
    
    # Remove the incorrect 2026-04-27 games (NYR, FLA, DAL, VAN)
    # They have specific IDs I used: 2025030115, 2025030135, 2025030155, 2025030175
    incorrect_ids = {2025030115, 2025030135, 2025030155, 2025030175}
    games = [g for g in games if g.get('id') not in incorrect_ids]
    
    # Correct 2026-04-27 Playoff Games (Game 5)
    # Series: PHI vs PIT, VGK vs UTA
    correct_games = [
        {
            "id": 2025030115, # Use a different ID range if needed, but these are fine for mock
            "gameDate": "2026-04-27",
            "startTimeUTC": "2026-04-27T23:00:00Z",
            "gameType": 3,
            "awayTeam": {"abbrev": "PHI"},
            "homeTeam": {"abbrev": "PIT"},
            "gameState": "FUT",
            "seriesStatus": {"topSeedWins": 2, "bottomSeedWins": 2, "topSeedTeamAbbrev": "PIT"}
        },
        {
            "id": 2025030155,
            "gameDate": "2026-04-27",
            "startTimeUTC": "2026-04-28T02:00:00Z",
            "gameType": 3,
            "awayTeam": {"abbrev": "VGK"},
            "homeTeam": {"abbrev": "UTA"},
            "gameState": "FUT",
            "seriesStatus": {"topSeedWins": 3, "bottomSeedWins": 1, "topSeedTeamAbbrev": "VGK"}
        }
    ]
    
    games.extend(correct_games)
    
    with open(path, 'w') as f:
        json.dump(games, f, indent=2)
    print(f"✅ Replaced incorrect games with PHI@PIT and VGK@UTA for April 27")

if __name__ == "__main__":
    fix_playoff_schedule_apr27()
