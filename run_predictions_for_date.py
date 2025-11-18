#!/usr/bin/env python3
"""
Generate pre-game predictions for a given date as-if it's the morning of that date.
Uses the 70/30 blend (correlation model + ensemble) and situational features at that date.
"""
from __future__ import annotations
from datetime import datetime, timedelta
import pytz
from typing import Dict, Optional

from nhl_api_client import NHLAPIClient
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from correlation_model import CorrelationModel
from lineup_service import LineupService


def predict_game_for_date(model: ImprovedSelfLearningModelV2, corr: CorrelationModel,
                          away_team: str, home_team: str, game_date: str, 
                          game_id: Optional[str] = None, lineup_service: Optional[LineupService] = None) -> Dict[str, float]:
    # Build situational metrics for that date
    try:
        away_rest = model._calculate_rest_days_advantage(away_team, 'away', game_date)
        home_rest = model._calculate_rest_days_advantage(home_team, 'home', game_date)
    except Exception:
        away_rest = home_rest = 0.0
    
    # Check for confirmed goalies if lineup service and game_id provided
    away_goalie_confirmed = None
    home_goalie_confirmed = None
    if lineup_service and game_id:
        away_goalie_confirmed = lineup_service.get_confirmed_goalie(away_team, game_id, game_date)
        home_goalie_confirmed = lineup_service.get_confirmed_goalie(home_team, game_id, game_date)
    
    try:
        away_goalie_perf = model._goalie_performance_for_game(away_team, 'away', game_date, confirmed_goalie=away_goalie_confirmed)
        home_goalie_perf = model._goalie_performance_for_game(home_team, 'home', game_date, confirmed_goalie=home_goalie_confirmed)
    except Exception:
        away_goalie_perf = home_goalie_perf = 0.0
    try:
        away_sos = model._calculate_sos(away_team, 'away')
        home_sos = model._calculate_sos(home_team, 'home')
    except Exception:
        away_sos = home_sos = 0.5

    away_perf = model.get_team_performance(away_team, 'away')
    home_perf = model.get_team_performance(home_team, 'home')
    away_recent_form = away_perf.get('recent_form', 0.5)
    home_recent_form = home_perf.get('recent_form', 0.5)
    
    # Debug: Check if we have actual team data
    away_games = away_perf.get('games_played', 0)
    home_games = home_perf.get('games_played', 0)
    if away_games == 0 or home_games == 0:
        print(f"WARNING: Missing team data - {away_team}: {away_games} games, {home_team}: {home_games} games")
    
    # Get venue-specific win percentages (full season)
    try:
        away_venue_win_pct = model._calculate_venue_win_percentage(away_team, 'away')
        home_venue_win_pct = model._calculate_venue_win_percentage(home_team, 'home')
    except Exception:
        away_venue_win_pct = 0.5
        home_venue_win_pct = 0.5
    
    metrics = {
        'away_gs': away_perf.get('gs_avg', 0.0), 'home_gs': home_perf.get('gs_avg', 0.0),
        'away_power_play_pct': away_perf.get('power_play_avg', 0.0), 'home_power_play_pct': home_perf.get('power_play_avg', 0.0),
        'away_blocked_shots': away_perf.get('blocked_shots_avg', 0.0), 'home_blocked_shots': home_perf.get('blocked_shots_avg', 0.0),
        'away_corsi_pct': away_perf.get('corsi_avg', 50.0), 'home_corsi_pct': home_perf.get('corsi_avg', 50.0),
        'away_hits': away_perf.get('hits_avg', 0.0), 'home_hits': home_perf.get('hits_avg', 0.0),
        'away_rest': away_rest, 'home_rest': home_rest,
        'away_hdc': away_perf.get('hdc_avg', 0.0), 'home_hdc': home_perf.get('hdc_avg', 0.0),
        'away_shots': away_perf.get('shots_avg', 30.0), 'home_shots': home_perf.get('shots_avg', 30.0),
        'away_giveaways': away_perf.get('giveaways_avg', 0.0), 'home_giveaways': home_perf.get('giveaways_avg', 0.0),
        'away_sos': away_sos, 'home_sos': home_sos,
        'away_takeaways': away_perf.get('takeaways_avg', 0.0), 'home_takeaways': home_perf.get('takeaways_avg', 0.0),
        'away_xg': away_perf.get('xg_avg', 0.0), 'home_xg': home_perf.get('xg_avg', 0.0),
        'away_penalty_minutes': away_perf.get('penalty_minutes_avg', 0.0), 'home_penalty_minutes': home_perf.get('penalty_minutes_avg', 0.0),
        'away_faceoff_pct': away_perf.get('faceoff_avg', 50.0), 'home_faceoff_pct': home_perf.get('faceoff_avg', 50.0),
        'away_goalie_perf': away_goalie_perf, 'home_goalie_perf': home_goalie_perf,
        'recent_form_diff': away_recent_form - home_recent_form,
        'away_venue_win_pct': away_venue_win_pct, 'home_venue_win_pct': home_venue_win_pct,  # Venue-specific win rates
    }

    corr_pred = corr.predict_from_metrics(metrics)
    ens_pred = model.ensemble_predict(away_team, home_team, game_date=game_date)

    # Ensure probabilities are in 0-1 range
    corr_away = corr_pred.get('away_prob', 0.5)
    corr_home = corr_pred.get('home_prob', 0.5)
    if corr_away > 1.0:
        corr_away = corr_away / 100.0
    if corr_home > 1.0:
        corr_home = corr_home / 100.0
    
    ens_away = ens_pred.get('away_prob', 0.5)
    ens_home = ens_pred.get('home_prob', 0.5)
    if ens_away > 1.0:
        ens_away = ens_away / 100.0
    if ens_home > 1.0:
        ens_home = ens_home / 100.0
    
    # Normalize to sum to 1.0
    corr_total = corr_away + corr_home
    if corr_total > 0:
        corr_away = corr_away / corr_total
        corr_home = corr_home / corr_total
    
    ens_total = ens_away + ens_home
    if ens_total > 0:
        ens_away = ens_away / ens_total
        ens_home = ens_home / ens_total

    away_blend = 0.7 * corr_away + 0.3 * ens_away
    home_blend = 1.0 - away_blend
    
    # Calculate confidence from both models
    corr_confidence = abs(corr_away - 0.5) * 2  # Distance from 0.5, scaled
    ens_confidence = ens_pred.get('prediction_confidence', 0.5) if 'prediction_confidence' in ens_pred else abs(ens_away - 0.5) * 2
    if ens_confidence > 1.0:
        ens_confidence = ens_confidence / 100.0
    blended_confidence = 0.7 * corr_confidence + 0.3 * ens_confidence
    
    return {
        'away_prob': away_blend,
        'home_prob': home_blend,
        'confidence': blended_confidence * 100  # Convert to percentage
    }


def main(target_date: str | None = None):
    api = NHLAPIClient()
    ct = pytz.timezone('US/Central')
    now_ct = datetime.now(ct)
    if not target_date:
        target_date = (now_ct - timedelta(days=1)).strftime('%Y-%m-%d')  # yesterday by default

    schedule = api.get_game_schedule(target_date)
    if not schedule or 'gameWeek' not in schedule:
        print(f'No schedule for {target_date}')
        return

    model = ImprovedSelfLearningModelV2()
    model.deterministic = True
    corr = CorrelationModel()
    lineup = LineupService()

    print(f'Predictions for {target_date} (pre-game):')
    for day in schedule.get('gameWeek', []):
        if day.get('date') != target_date:
            continue
        for g in day.get('games', []):
            away = (g.get('awayTeam', {}) or {}).get('abbrev')
            home = (g.get('homeTeam', {}) or {}).get('abbrev')
            game_id = str(g.get('id'))
            if not away or not home:
                continue
            res = predict_game_for_date(model, corr, away, home, target_date, game_id=game_id, lineup_service=lineup)
            ap = res['away_prob'] * 100
            hp = res['home_prob'] * 100
            fav = home if hp > ap else away
            spread = abs(hp - ap)
            print(f"{away} @ {home}: {ap:.1f}% | {hp:.1f}%  Favorite: {fav} (+{spread:.1f}%)")


if __name__ == '__main__':
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)


