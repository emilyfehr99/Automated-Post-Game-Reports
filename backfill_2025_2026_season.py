#!/usr/bin/env python3
"""
Backfill 2025-2026 Regular Season Metrics

Collects all regular-season games from the start of 2025-2026, dedupes by gameId,
extracts real metrics (xG, HDC, Game Score, period stats) using PostGameReportGenerator
without generating or posting reports, and aggregates per-team sums/averages.

Output: season_2025_2026_team_stats.json
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict

from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator


def daterange(start_date: datetime, end_date: datetime):
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)


def is_regular_season(game: dict) -> bool:
    # NHL API sometimes uses numeric codes; fall back to safe checks
    gt = game.get('gameType')
    if isinstance(gt, str):
        return gt.upper().startswith('R')
    if isinstance(gt, int):
        # 2 is typically regular season in NHL stats APIs
        return gt == 2
    # If unknown, include but can be filtered later if needed
    return True


def main():
    api = NHLAPIClient()
    gen = PostGameReportGenerator()

    # Define season window (adjust if NHL official start date differs)
    season_start = datetime(2025, 10, 1)
    season_end = datetime.now()

    seen_game_ids = set()

    # Aggregates per team
    # sums[team_abbrev]['xg'|'hdc'|'gs'|...] = float
    sums = defaultdict(lambda: defaultdict(float))
    counts = defaultdict(int)

    # Iterate dates, collect game IDs once
    for day in daterange(season_start, season_end):
        schedule = api.get_game_schedule(day.strftime('%Y-%m-%d'))
        if not schedule or 'gameWeek' not in schedule:
            continue
        for bucket in schedule['gameWeek']:
            for game in bucket.get('games', []):
                if not is_regular_season(game):
                    continue
                game_id = game.get('id')
                if not game_id or game_id in seen_game_ids:
                    continue

                # Fetch comprehensive data
                data = api.get_comprehensive_game_data(game_id)
                if not data:
                    continue

                # Compose game_data structure expected by generator methods
                game_data = {
                    'game_center': data.get('boxscore'),  # for team abbrevs we use boxscore
                    'boxscore': data.get('boxscore'),
                    'play_by_play': data.get('play_by_play'),
                }

                box = data.get('boxscore') or {}
                away = box.get('awayTeam', {})
                home = box.get('homeTeam', {})
                away_abbrev = away.get('abbrev')
                home_abbrev = home.get('abbrev')
                away_id = away.get('id')
                home_id = home.get('id')
                if not away_abbrev or not home_abbrev:
                    continue

                try:
                    # Extract metrics via generator helpers
                    away_xg, home_xg = gen._calculate_xg_from_plays(game_data)
                    away_hdc, home_hdc = gen._calculate_hdc_from_plays(game_data)
                    away_gs, home_gs = gen._calculate_game_scores(game_data)

                    # Optional period-level enrichment (not aggregated directly here)
                    # gen._calculate_real_period_stats(game_data, away_id, 'away')
                    # gen._calculate_real_period_stats(game_data, home_id, 'home')

                except Exception:
                    # Skip games that fail metric extraction
                    continue

                # Attribute metrics to each team; count game once per team (no duplicate games)
                for team_abbrev, xg, hdc, gs in (
                    (away_abbrev, away_xg, away_hdc, away_gs),
                    (home_abbrev, home_xg, home_hdc, home_gs),
                ):
                    sums[team_abbrev]['xg'] += float(xg or 0.0)
                    sums[team_abbrev]['hdc'] += float(hdc or 0.0)
                    sums[team_abbrev]['gs'] += float(gs or 0.0)
                    counts[team_abbrev] += 1

                seen_game_ids.add(game_id)

    # Build output with averages
    output = {
        'season': '2025-2026',
        'generated_at': datetime.utcnow().isoformat(),
        'total_games': len(seen_game_ids),
        'teams': {}
    }

    for team, c in counts.items():
        s = sums[team]
        output['teams'][team] = {
            'games_played': c,
            'xg_sum': s.get('xg', 0.0),
            'hdc_sum': s.get('hdc', 0.0),
            'gs_sum': s.get('gs', 0.0),
            'xg_avg': (s.get('xg', 0.0) / c) if c else 0.0,
            'hdc_avg': (s.get('hdc', 0.0) / c) if c else 0.0,
            'gs_avg': (s.get('gs', 0.0) / c) if c else 0.0,
        }

    with open('season_2025_2026_team_stats.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✅ Backfill complete. Games processed: {len(seen_game_ids)}")
    print("Saved: season_2025_2026_team_stats.json")


if __name__ == '__main__':
    main()


