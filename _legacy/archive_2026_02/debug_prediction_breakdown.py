#!/usr/bin/env python3
"""
Debug script to show exact prediction breakdown for a specific game.
"""
from prediction_interface import PredictionInterface
from correlation_model import CorrelationModel
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from datetime import datetime

def breakdown_prediction(away_team: str, home_team: str, game_id: str = None):
    """Break down a prediction into all components."""
    interface = PredictionInterface()
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n{'='*80}")
    print(f"PREDICTION BREAKDOWN: {away_team} @ {home_team}")
    print(f"{'='*80}\n")
    
    # Build metrics exactly as predict_game does
    try:
        away_rest = interface.learning_model._calculate_rest_days_advantage(away_team, 'away', today_str)
        home_rest = interface.learning_model._calculate_rest_days_advantage(home_team, 'home', today_str)
    except Exception as e:
        print(f"⚠️  Error calculating rest: {e}")
        away_rest = home_rest = 0.0
    
    # Check for confirmed goalies
    away_goalie_confirmed = None
    home_goalie_confirmed = None
    if game_id:
        away_goalie_confirmed = interface.lineup_service.get_confirmed_goalie(away_team, game_id, today_str)
        home_goalie_confirmed = interface.lineup_service.get_confirmed_goalie(home_team, game_id, today_str)
    
    try:
        away_goalie_perf = interface.learning_model._goalie_performance_for_game(
            away_team, 'away', today_str, confirmed_goalie=away_goalie_confirmed
        )
        home_goalie_perf = interface.learning_model._goalie_performance_for_game(
            home_team, 'home', today_str, confirmed_goalie=home_goalie_confirmed
        )
    except Exception as e:
        print(f"⚠️  Error calculating goalie perf: {e}")
        away_goalie_perf = home_goalie_perf = 0.0
    
    try:
        away_sos = interface.learning_model._calculate_sos(away_team, 'away')
        home_sos = interface.learning_model._calculate_sos(home_team, 'home')
    except Exception as e:
        print(f"⚠️  Error calculating SOS: {e}")
        away_sos = home_sos = 0.5
    
    # Team venue performance
    away_perf = interface.learning_model.get_team_performance(away_team, 'away')
    home_perf = interface.learning_model.get_team_performance(home_team, 'home')
    
    away_recent_form = away_perf.get('recent_form', 0.5)
    home_recent_form = home_perf.get('recent_form', 0.5)
    
    print(f"📍 VENUE CONTEXT:")
    print(f"   {away_team} (away) | {home_team} (home)")
    print()
    
    # Show team metrics
    print(f"📊 TEAM METRICS (venue-specific):")
    print(f"\n   {away_team} (Away):")
    for key in ['xg_avg', 'hdc_avg', 'shots_avg', 'gs_avg', 'corsi_avg', 'faceoff_avg', 
                'power_play_avg', 'hits_avg', 'blocked_shots_avg', 'takeaways_avg']:
        val = away_perf.get(key, 0.0)
        print(f"      {key:20s}: {val:8.3f}")
    print(f"      {'recent_form':20s}: {away_recent_form:8.3f}")
    
    print(f"\n   {home_team} (Home):")
    for key in ['xg_avg', 'hdc_avg', 'shots_avg', 'gs_avg', 'corsi_avg', 'faceoff_avg',
                'power_play_avg', 'hits_avg', 'blocked_shots_avg', 'takeaways_avg']:
        val = home_perf.get(key, 0.0)
        print(f"      {key:20s}: {val:8.3f}")
    print(f"      {'recent_form':20s}: {home_recent_form:8.3f}")
    print()
    
    # Build metrics dict
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
    }
    
    # Get venue win percentages
    try:
        away_venue_win_pct = interface.learning_model._calculate_venue_win_percentage(away_team, 'away')
        home_venue_win_pct = interface.learning_model._calculate_venue_win_percentage(home_team, 'home')
    except Exception:
        away_venue_win_pct = 0.5
        home_venue_win_pct = 0.5
    
    metrics['away_venue_win_pct'] = away_venue_win_pct
    metrics['home_venue_win_pct'] = home_venue_win_pct
    
    print(f"🎯 SITUATIONAL FACTORS:")
    print(f"   Rest Days:  {away_team}={away_rest:+.4f} | {home_team}={home_rest:+.4f} | Diff={away_rest - home_rest:+.4f}")
    print(f"   Goalie GSAX: {away_team}={away_goalie_perf:+.4f} | {home_team}={home_goalie_perf:+.4f} | Diff={away_goalie_perf - home_goalie_perf:+.4f}")
    if away_goalie_confirmed or home_goalie_confirmed:
        print(f"   Confirmed Goalies: {away_team}={away_goalie_confirmed or 'predicted'} | {home_team}={home_goalie_confirmed or 'predicted'}")
    print(f"   SOS:        {away_team}={away_sos:.4f} | {home_team}={home_sos:.4f} | Diff={away_sos - home_sos:+.4f}")
    print(f"   Recent Form: {away_team}={away_recent_form:.4f} | {home_team}={home_recent_form:.4f} | Diff={away_recent_form - home_recent_form:+.4f}")
    print(f"   Venue Win %: {away_team} away={away_venue_win_pct:.4f} | {home_team} home={home_venue_win_pct:.4f} | Diff={away_venue_win_pct - home_venue_win_pct:+.4f}")
    print()
    
    # Correlation model breakdown
    print(f"🔍 CORRELATION MODEL BREAKDOWN (70% weight):")
    corr_model = interface.corr_model
    feats = corr_model._feature_row_from_metrics(metrics)
    
    # Show feature differences
    print(f"\n   Feature Differences (away - home):")
    diff_features = [
        ('gs_diff', 'Game Score'),
        ('xg_diff', 'Expected Goals'),
        ('hdc_diff', 'High Danger Chances'),
        ('corsi_diff', 'Corsi %'),
        ('power_play_diff', 'Power Play %'),
        ('faceoff_diff', 'Faceoff %'),
        ('shots_diff', 'Shots'),
        ('hits_diff', 'Hits'),
        ('blocked_shots_diff', 'Blocked Shots'),
        ('takeaways_diff', 'Takeaways'),
        ('giveaways_diff', 'Giveaways'),
        ('pim_diff', 'Penalty Minutes'),
        ('rest_diff', 'Rest Days'),
        ('goalie_perf_diff', 'Goalie GSAX'),
        ('sos_diff', 'Strength of Schedule'),
        ('recent_form_diff', 'Recent Form'),
        ('venue_win_pct_diff', 'Venue Win %'),
    ]
    
    for feat_key, feat_name in diff_features:
        val = feats.get(feat_key, 0.0)
        weight = corr_model.weights.get(feat_key, 0.0)
        # Apply scaling
        scaled_val = val
        if feat_key in ('power_play_diff', 'corsi_diff', 'faceoff_diff'):
            scaled_val = val / 10.0
        if feat_key == 'gs_diff':
            scaled_val = val * 0.5
        contribution = weight * scaled_val
        print(f"      {feat_name:25s}: {val:8.3f} × {weight:7.4f} = {contribution:8.4f}")
    
    # Calculate correlation score
    corr_score = corr_model._score(feats)
    corr_pred = corr_model.predict_from_metrics(metrics)
    
    venue_diff = feats.get('venue_win_pct_diff', 0.0)
    venue_contribution = 0.5 * venue_diff if venue_diff != 0.0 else 0.0
    print(f"\n   Venue Win % Contribution: {venue_contribution:+.4f} (0.5 × {venue_diff:+.4f})")
    print(f"   Raw Correlation Score: {corr_score:.4f}")
    print(f"   {away_team} (away) probability: {corr_pred['away_prob']:.4f} ({corr_pred['away_prob']*100:.2f}%)")
    print(f"   {home_team} (home) probability: {corr_pred['home_prob']:.4f} ({corr_pred['home_prob']*100:.2f}%)")
    print()
    
    # Ensemble model
    print(f"📈 ENSEMBLE MODEL BREAKDOWN (30% weight):")
    ens_pred = interface.learning_model.ensemble_predict(away_team, home_team, game_date=today_str)
    print(f"   {away_team} (away) probability: {ens_pred['away_prob']:.4f} ({ens_pred['away_prob']*100:.2f}%)")
    print(f"   {home_team} (home) probability: {ens_pred['home_prob']:.4f} ({ens_pred['home_prob']*100:.2f}%)")
    print()
    
    # Final blend
    away_blend = 0.7 * corr_pred['away_prob'] + 0.3 * ens_pred.get('away_prob', 0.5)
    home_blend = 1.0 - away_blend
    
    print(f"⚖️  FINAL PREDICTION (70/30 Blend):")
    print(f"   {away_team} (away): {away_blend:.4f} ({away_blend*100:.2f}%)")
    print(f"      = 0.7 × {corr_pred['away_prob']:.4f} + 0.3 × {ens_pred.get('away_prob', 0.5):.4f}")
    print(f"   {home_team} (home): {home_blend:.4f} ({home_blend*100:.2f}%)")
    print(f"      = 0.7 × {corr_pred['home_prob']:.4f} + 0.3 × {ens_pred.get('home_prob', 0.5):.4f}")
    print()
    
    favorite = home_team if home_blend > away_blend else away_team
    margin = abs(home_blend - away_blend) * 100
    print(f"⭐ FAVORITE: {favorite} (+{margin:.2f}%)")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 3:
        away = sys.argv[1].upper()
        home = sys.argv[2].upper()
        game_id = sys.argv[3] if len(sys.argv) > 3 else None
        breakdown_prediction(away, home, game_id)
    else:
        print("Usage: python debug_prediction_breakdown.py AWAY_TEAM HOME_TEAM [game_id]")
        print("\nExample: python debug_prediction_breakdown.py WSH BUF")
        # Default to WSH @ BUF
        breakdown_prediction('WSH', 'BUF')

