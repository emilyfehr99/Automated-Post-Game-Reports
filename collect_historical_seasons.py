#!/usr/bin/env python3
"""
Collect Historical NHL Seasons (2023-2024, 2024-2025)
Extracts all regular season games and aggregates team stats
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator


def daterange(start_date: datetime, end_date: datetime):
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)


def is_regular_season(game: dict) -> bool:
    gt = game.get('gameType')
    if isinstance(gt, str):
        return gt.upper().startswith('R')
    if isinstance(gt, int):
        return gt == 2
    return True


def collect_season_data(season_name: str, start_date: datetime, end_date: datetime):
    """Collect all games for a season and aggregate team stats"""
    api = NHLAPIClient()
    gen = PostGameReportGenerator()
    
    seen_game_ids = set()
    sums = defaultdict(lambda: defaultdict(float))
    counts = defaultdict(int)
    
    print(f"🔍 Collecting {season_name} season data...")
    print(f"   Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    for day in daterange(start_date, end_date):
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
                
                game_data = {
                    'game_center': data.get('boxscore'),
                    'boxscore': data.get('boxscore'),
                    'play_by_play': data.get('play_by_play'),
                }
                
                box = data.get('boxscore') or {}
                away = box.get('awayTeam', {})
                home = box.get('homeTeam', {})
                away_abbrev = away.get('abbrev')
                home_abbrev = home.get('abbrev')
                
                if not away_abbrev or not home_abbrev:
                    continue
                
                try:
                    # Extract metrics
                    away_xg, home_xg = gen._calculate_xg_from_plays(game_data)
                    away_hdc, home_hdc = gen._calculate_hdc_from_plays(game_data)
                    away_gs, home_gs = gen._calculate_game_scores(game_data)
                    
                except Exception as e:
                    print(f"   ⚠️  Skipping game {game_id}: {e}")
                    continue
                
                # Aggregate metrics for each team
                for team_abbrev, xg, hdc, gs in [
                    (away_abbrev, away_xg, away_hdc, away_gs),
                    (home_abbrev, home_xg, home_hdc, home_gs),
                ]:
                    sums[team_abbrev]['xg'] += float(xg or 0.0)
                    sums[team_abbrev]['hdc'] += float(hdc or 0.0)
                    sums[team_abbrev]['gs'] += float(gs or 0.0)
                    counts[team_abbrev] += 1
                
                seen_game_ids.add(game_id)
                if len(seen_game_ids) % 50 == 0:
                    print(f"   📊 Processed {len(seen_game_ids)} games...")
    
    # Build output
    output = {
        'season': season_name,
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
    
    # Save season data
    filename = f'season_{season_name.replace("-", "_")}_team_stats.json'
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ {season_name} complete: {len(seen_game_ids)} games")
    print(f"   Saved: {filename}")
    return output


def main():
    """Collect historical seasons"""
    print("🏒 NHL HISTORICAL SEASON DATA COLLECTION")
    print("=" * 60)
    
    # Define seasons
    seasons = [
        {
            'name': '2023-2024',
            'start': datetime(2023, 10, 10),  # Approximate start
            'end': datetime(2024, 4, 18)      # Approximate end
        },
        {
            'name': '2024-2025', 
            'start': datetime(2024, 10, 4),   # Approximate start
            'end': datetime(2025, 4, 16)      # Approximate end
        }
    ]
    
    all_seasons = {}
    
    for season in seasons:
        try:
            data = collect_season_data(
                season['name'],
                season['start'], 
                season['end']
            )
            all_seasons[season['name']] = data
        except Exception as e:
            print(f"❌ Error collecting {season['name']}: {e}")
    
    # Create combined historical data
    combined = {
        'seasons': all_seasons,
        'generated_at': datetime.utcnow().isoformat(),
        'total_games': sum(s['total_games'] for s in all_seasons.values())
    }
    
    with open('historical_seasons_team_stats.json', 'w') as f:
        json.dump(combined, f, indent=2)
    
    print(f"\n🎯 HISTORICAL COLLECTION COMPLETE")
    print(f"   Total games across all seasons: {combined['total_games']}")
    print(f"   Saved: historical_seasons_team_stats.json")


if __name__ == '__main__':
    main()