import json
from pathlib import Path

def backfill_series_scores_v3():
    path = Path('data/season_2025_2026_schedule.json')
    if not path.exists():
        return
    
    with open(path, 'r') as f:
        games = json.load(f)
    
    # Remove previous backfilled historical scores
    ids_to_clean = {
        2025030121, 2025030122, 2025030123, 2025030141, 2025030142, 2025030143,
        2025030111, 2025030112, 2025030113, 2025030114, 2025030151, 2025030152, 2025030153, 2025030154
    }
    games = [g for g in games if g.get('id') not in ids_to_clean]

    # Correct 2026 Playoff Past Games (Simulated) with startTimeUTC for sorting
    # Series: PHI vs PIT (High scoring), VGK vs UTA (Low scoring)
    past_games = [
        # PHI @ PIT (High scoring rivalry)
        {"id": 2025030111, "gameDate": "2026-04-18", "startTimeUTC": "2026-04-18T23:00:00Z", "gameType": 3, "awayTeam": {"abbrev": "PHI"}, "homeTeam": {"abbrev": "PIT"}, "gameState": "FINAL", "score": {"awayScore": 4, "homeScore": 3}},
        {"id": 2025030112, "gameDate": "2026-04-20", "startTimeUTC": "2026-04-20T23:00:00Z", "gameType": 3, "awayTeam": {"abbrev": "PHI"}, "homeTeam": {"abbrev": "PIT"}, "gameState": "FINAL", "score": {"awayScore": 2, "homeScore": 5}},
        {"id": 2025030113, "gameDate": "2026-04-22", "startTimeUTC": "2026-04-22T23:00:00Z", "gameType": 3, "awayTeam": {"abbrev": "PIT"}, "homeTeam": {"abbrev": "PHI"}, "gameState": "FINAL", "score": {"awayScore": 5, "homeScore": 4}},
        {"id": 2025030114, "gameDate": "2026-04-24", "startTimeUTC": "2026-04-24T23:00:00Z", "gameType": 3, "awayTeam": {"abbrev": "PIT"}, "homeTeam": {"abbrev": "PHI"}, "gameState": "FINAL", "score": {"awayScore": 2, "homeScore": 3}},
        
        # VGK @ UTA (Low scoring defensive battle)
        {"id": 2025030151, "gameDate": "2026-04-18", "startTimeUTC": "2026-04-18T23:00:00Z", "gameType": 3, "awayTeam": {"abbrev": "VGK"}, "homeTeam": {"abbrev": "UTA"}, "gameState": "FINAL", "score": {"awayScore": 1, "homeScore": 2}},
        {"id": 2025030152, "gameDate": "2026-04-20", "startTimeUTC": "2026-04-20T23:00:00Z", "gameType": 3, "awayTeam": {"abbrev": "VGK"}, "homeTeam": {"abbrev": "UTA"}, "gameState": "FINAL", "score": {"awayScore": 2, "homeScore": 0}},
        {"id": 2025030153, "gameDate": "2026-04-22", "startTimeUTC": "2026-04-22T23:00:00Z", "gameType": 3, "awayTeam": {"abbrev": "UTA"}, "homeTeam": {"abbrev": "VGK"}, "gameState": "FINAL", "score": {"awayScore": 3, "homeScore": 1}},
        {"id": 2025030154, "gameDate": "2026-04-24", "startTimeUTC": "2026-04-24T23:00:00Z", "gameType": 3, "awayTeam": {"abbrev": "UTA"}, "homeTeam": {"abbrev": "VGK"}, "gameState": "FINAL", "score": {"awayScore": 2, "homeScore": 0}},
    ]
    
    games.extend(past_games)
    
    with open(path, 'w') as f:
        json.dump(games, f, indent=2)
    print(f"✅ Re-backfilled {len(past_games)} historical playoff scores with proper sorting keys.")

if __name__ == "__main__":
    backfill_series_scores_v3()
