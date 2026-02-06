#!/usr/bin/env python3
"""
Backfill situational metrics (rest, goalie_perf, SOS) into stored predictions.
Uses NHL schedule API to get actual game dates for accurate rest calculation.
"""
import json
from pathlib import Path
from typing import Dict, Set, List, Tuple
from datetime import datetime, timedelta

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from nhl_api_client import NHLAPIClient


PREDICTIONS_FILE = Path('win_probability_predictions_v2.json')


def compute_situational(model: ImprovedSelfLearningModelV2, away: str, home: str, date: str,
                        prev_game_date_by_team: Dict[str, str],
                        sos_index_by_team_date: Dict[str, float]) -> Dict[str, float]:
    # Defaults
    away_rest = home_rest = 0.0
    away_goalie_perf = home_goalie_perf = 0.0
    away_sos = home_sos = 0.0

    # Rest: compute from actual schedule dates (real days between games)
    try:
        def rest_days(team: str) -> float:
            prev = prev_game_date_by_team.get(f"{team}|{date}")
            if not prev:
                return 0.0  # First game of season or unknown
            try:
                d0 = datetime.strptime(prev, '%Y-%m-%d')
                d1 = datetime.strptime(date, '%Y-%m-%d')
                days = (d1 - d0).days
                if days <= 1:
                    return -0.3  # B2B disadvantage
                elif days == 2:
                    return 0.1   # 2 days rest advantage
                elif days >= 3:
                    return 0.2   # 3+ days rest advantage
                else:
                    return 0.0
            except Exception:
                return 0.0
        away_rest = rest_days(away)
        home_rest = rest_days(home)
    except Exception:
        pass
    try:
        away_goalie_perf = model._goalie_performance_for_game(away, 'away', date)
        home_goalie_perf = model._goalie_performance_for_game(home, 'home', date)
    except Exception:
        pass
    # SOS: use precomputed rolling index from opponents' actual win% to date
    away_sos = float(sos_index_by_team_date.get(f"{away}|{date}", 0.5))
    home_sos = float(sos_index_by_team_date.get(f"{home}|{date}", 0.5))

    return {
        'away_rest': float(away_rest or 0.0),
        'home_rest': float(home_rest or 0.0),
        'away_goalie_perf': float(away_goalie_perf or 0.0),
        'home_goalie_perf': float(home_goalie_perf or 0.0),
        'away_sos': float(away_sos or 0.0),
        'home_sos': float(home_sos or 0.0),
    }


def main():
    if not PREDICTIONS_FILE.exists():
        print('No predictions file found')
        return

    with open(PREDICTIONS_FILE, 'r') as f:
        data = json.load(f)

    preds = data.get('predictions', [])
    if not preds:
        print('No predictions to backfill')
        return

    model = ImprovedSelfLearningModelV2()
    api = NHLAPIClient()
    
    # Get all unique dates from predictions
    all_dates = sorted(set(p.get('date') for p in preds if p.get('date')))
    if not all_dates:
        print('No dates found in predictions')
        return
    
    print(f'Fetching NHL schedule for {len(all_dates)} dates...')
    
    # Build complete game timeline from NHL schedule API
    schedule_games_by_team: Dict[str, List[Tuple[str, str]]] = {}  # team -> [(date, opponent)]
    schedule_dates_by_team: Dict[str, List[str]] = {}  # team -> [sorted dates]
    
    for date_str in all_dates:
        try:
            schedule = api.get_game_schedule(date_str)
            if not schedule or 'gameWeek' not in schedule:
                continue
            for day in schedule.get('gameWeek', []):
                if day.get('date') != date_str:
                    continue
                for game in day.get('games', []):
                    away = (game.get('awayTeam', {}).get('abbrev') or '').upper()
                    home = (game.get('homeTeam', {}).get('abbrev') or '').upper()
                    if away and home:
                        schedule_games_by_team.setdefault(away, []).append((date_str, home))
                        schedule_games_by_team.setdefault(home, []).append((date_str, away))
                        schedule_dates_by_team.setdefault(away, []).append(date_str)
                        schedule_dates_by_team.setdefault(home, []).append(date_str)
        except Exception as e:
            print(f'  Warning: Could not fetch schedule for {date_str}: {e}')
    
    # Sort dates per team
    for team in schedule_dates_by_team:
        schedule_dates_by_team[team] = sorted(set(schedule_dates_by_team[team]))
    
    # Map team|date -> previous schedule date
    prev_game_date_by_team: Dict[str, str] = {}
    for team, dates in schedule_dates_by_team.items():
        for i, d in enumerate(dates):
            if i == 0:
                continue
            prev_game_date_by_team[f"{team}|{d}"] = dates[i-1]
    
    # Build win/loss records from stored predictions for SOS calculation
    results_by_team: Dict[str, List[Tuple[str, int]]] = {}  # team -> [(date, win)]
    for p in preds:
        date = p.get('date')
        away = (p.get('away_team') or '').upper()
        home = (p.get('home_team') or '').upper()
        actual = p.get('actual_winner')
        if not date or not away or not home or not actual:
            continue
        # Normalize actual winner
        actual_side = 'away' if actual in (away, 'away') else 'home' if actual in (home, 'home') else None
        if not actual_side:
            continue
        # Record outcomes
        for team, side in ((away, 'away'), (home, 'home')):
            win = 1 if actual_side == side else 0
            results_by_team.setdefault(team, []).append((date, win))
    
    # Compute rolling opponent win% index per team per date (SOS)
    sos_index_by_team_date: Dict[str, float] = {}
    for team, games in schedule_games_by_team.items():
        games_sorted = sorted(games, key=lambda x: x[0])
        for game_date, opponent in games_sorted:
            # Get opponent's win% prior to this date
            opp_results = sorted(results_by_team.get(opponent, []), key=lambda x: x[0])
            prior_wins = [w for (od, w) in opp_results if od < game_date]
            if prior_wins:
                # Use last 5 games
                sos = sum(prior_wins[-5:]) / min(5, len(prior_wins))
            else:
                sos = 0.5  # Default neutral
            sos_index_by_team_date[f"{team}|{game_date}"] = sos
    updated = 0

    for p in preds:
        away = (p.get('away_team') or '').upper()
        home = (p.get('home_team') or '').upper()
        date = p.get('date')
        if not away or not home or not date:
            continue
        metrics = p.get('metrics_used') or {}
        # Always recompute to fix previously neutral values
        situ = compute_situational(model, away, home, date, prev_game_date_by_team, sos_index_by_team_date)
        metrics.update(situ)
        p['metrics_used'] = metrics
        updated += 1

    if updated:
        with open(PREDICTIONS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f'✅ Backfilled situational metrics for {updated} predictions')
    else:
        print('Nothing to update (all predictions already have situational metrics)')


if __name__ == '__main__':
    main()


