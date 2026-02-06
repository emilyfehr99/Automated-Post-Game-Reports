#!/usr/bin/env python3
"""
Correlation analysis of POSTGAME metrics - using actual game stats from completed games
to determine which metrics best predict win outcomes.
"""
import json
import numpy as np
import pandas as pd
from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator
from pathlib import Path
from datetime import datetime, timedelta
import pytz

def analyze_postgame_metrics(max_games=500):
    """Analyze correlation of actual postgame metrics with game outcomes"""
    api = NHLAPIClient()
    generator = PostGameReportGenerator()
    
    # Get completed games from predictions file
    predictions_file = Path('win_probability_predictions_v2.json')
    if predictions_file.exists():
        with open(predictions_file, 'r') as f:
            data = json.load(f)
        predictions = [p for p in data.get('predictions', []) if p.get('actual_winner')]
    else:
        predictions = []
    
    print(f"Found {len(predictions)} completed games in predictions file")
    
    components_data = []
    games_processed = 0
    games_failed = 0
    
    # Process games (limit to avoid too long runtime)
    for pred in predictions[:max_games]:
        game_id = pred.get('game_id')
        if not game_id:
            continue
        
        try:
            # Get comprehensive game data
            game_data = api.get_comprehensive_game_data(str(game_id))
            if not game_data or 'boxscore' not in game_data:
                games_failed += 1
                continue
            
            boxscore = game_data['boxscore']
            away_team = boxscore.get('awayTeam', {})
            home_team = boxscore.get('homeTeam', {})
            
            away_team_id = away_team.get('id')
            home_team_id = home_team.get('id')
            away_goals = away_team.get('score', 0)
            home_goals = home_team.get('score', 0)
            
            # Determine outcome: 1 if away wins, 0 if home wins
            if away_goals > home_goals:
                outcome = 1  # Away won
            elif home_goals > away_goals:
                outcome = 0  # Home won
            else:
                continue  # Skip ties (shouldn't happen but just in case)
            
            # Extract actual game metrics
            # Calculate xG, HDC, Game Score from play-by-play
            away_xg, home_xg = generator._calculate_xg_from_plays(game_data)
            away_hdc, home_hdc = generator._calculate_hdc_from_plays(game_data)
            away_gs, home_gs = generator._calculate_game_scores(game_data)
            
            # Get period stats for additional metrics
            away_period_stats = generator._calculate_real_period_stats(game_data, away_team_id, 'away')
            home_period_stats = generator._calculate_real_period_stats(game_data, home_team_id, 'home')
            
            # Extract basic metrics from boxscore
            away_sog = away_team.get('sog', 0)
            home_sog = home_team.get('sog', 0)
            
            # Calculate Corsi (shot attempts) - shots + blocked shots + missed shots
            # We'll approximate from available data
            away_corsi_pct = np.mean(away_period_stats.get('corsi_pct', [50.0])) if away_period_stats.get('corsi_pct') else 50.0
            home_corsi_pct = np.mean(home_period_stats.get('corsi_pct', [50.0])) if home_period_stats.get('corsi_pct') else 50.0
            
            # Power play percentage
            away_pp_goals = sum(away_period_stats.get('pp_goals', [0]))
            away_pp_attempts = sum(away_period_stats.get('pp_attempts', [0]))
            home_pp_goals = sum(home_period_stats.get('pp_goals', [0]))
            home_pp_attempts = sum(home_period_stats.get('pp_attempts', [0]))
            
            away_pp_pct = (away_pp_goals / max(1, away_pp_attempts)) * 100 if away_pp_attempts > 0 else 0.0
            home_pp_pct = (home_pp_goals / max(1, home_pp_attempts)) * 100 if home_pp_attempts > 0 else 0.0
            
            # Faceoff percentage
            away_faceoff_wins = sum(away_period_stats.get('faceoff_wins', [0]))
            away_faceoff_total = sum(away_period_stats.get('faceoff_total', [0]))
            home_faceoff_wins = sum(home_period_stats.get('faceoff_wins', [0]))
            home_faceoff_total = sum(home_period_stats.get('faceoff_total', [0]))
            
            away_faceoff_pct = (away_faceoff_wins / max(1, away_faceoff_total)) * 100 if away_faceoff_total > 0 else 50.0
            home_faceoff_pct = (home_faceoff_wins / max(1, home_faceoff_total)) * 100 if home_faceoff_total > 0 else 50.0
            
            # Other metrics from boxscore/period stats
            away_hits = sum(away_period_stats.get('hits', [0]))
            home_hits = sum(home_period_stats.get('hits', [0]))
            
            away_blocked_shots = sum(away_period_stats.get('blocked_shots', [0]))
            home_blocked_shots = sum(home_period_stats.get('blocked_shots', [0]))
            
            away_pim = sum(away_period_stats.get('pim', [0]))
            home_pim = sum(home_period_stats.get('pim', [0]))
            
            # Try to get giveaways/takeaways from boxscore
            away_giveaways = away_team.get('giveaways', 0)
            home_giveaways = home_team.get('giveaways', 0)
            away_takeaways = away_team.get('takeaways', 0)
            home_takeaways = home_team.get('takeaways', 0)
            
            # If not in team data, try to calculate from player stats
            if away_giveaways == 0 or home_giveaways == 0:
                try:
                    away_team_stats = generator._calculate_team_stats_from_players(boxscore, 'away')
                    home_team_stats = generator._calculate_team_stats_from_players(boxscore, 'home')
                    away_giveaways = away_team_stats.get('giveaways', 0)
                    home_giveaways = home_team_stats.get('giveaways', 0)
                    away_takeaways = away_team_stats.get('takeaways', 0)
                    home_takeaways = home_team_stats.get('takeaways', 0)
                except:
                    pass
            
            # Build difference row (away - home)
            row = {
                'outcome': outcome,
                'gs_diff': away_gs - home_gs,
                'xg_diff': away_xg - home_xg,
                'hdc_diff': away_hdc - home_hdc,
                'shots_diff': away_sog - home_sog,
                'corsi_diff': away_corsi_pct - home_corsi_pct,
                'power_play_diff': away_pp_pct - home_pp_pct,
                'faceoff_diff': away_faceoff_pct - home_faceoff_pct,
                'hits_diff': away_hits - home_hits,
                'blocked_shots_diff': away_blocked_shots - home_blocked_shots,
                'takeaways_diff': away_takeaways - home_takeaways,
                'giveaways_diff': away_giveaways - home_giveaways,
                'pim_diff': away_pim - home_pim,
            }
            
            components_data.append(row)
            games_processed += 1
            
        except Exception as e:
            games_failed += 1
            if games_processed % 50 == 0:
                print(f"Processed {games_processed} games, {games_failed} failed...")
            continue
    
    print(f"\nSuccessfully processed {games_processed} games")
    if games_failed > 0:
        print(f"Failed to process {games_failed} games")
    
    if not components_data:
        print("No valid postgame metric data extracted")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(components_data)
    
    # Calculate correlations with outcome
    correlations = {}
    for col in df.columns:
        if col != 'outcome':
            # Check for variance
            if df[col].std() > 1e-6:
                corr = df[col].corr(df['outcome'])
                if not np.isnan(corr):
                    correlations[col] = corr
    
    # Sort by absolute correlation
    sorted_corrs = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
    
    print("\n" + "="*70)
    print("POSTGAME CORRELATION ANALYSIS: Actual Game Metrics vs Win Outcomes")
    print("="*70)
    print(f"\nSample size: {len(df)} games")
    print(f"\nMetric correlations (sorted by absolute value):")
    print(f"{'Metric':<25s} {'Correlation':>12s} {'Direction':>10s} {'Magnitude'}")
    print("-" * 70)
    
    for metric, corr in sorted_corrs:
        abs_corr = abs(corr)
        direction = "↑ Away Win" if corr > 0 else "↓ Home Win"
        bar = "█" * int(abs_corr * 30)
        print(f"{metric:<25s} {corr:11.4f}  {direction:<10s} {bar}")
    
    # Additional analysis: mean differences by outcome
    print("\n" + "="*70)
    print("MEAN METRIC VALUES: Away Wins vs Home Wins")
    print("="*70)
    
    away_wins = df[df['outcome'] == 1]
    home_wins = df[df['outcome'] == 0]
    
    print(f"\nAway wins: {len(away_wins)} games")
    print(f"Home wins: {len(home_wins)} games\n")
    print(f"{'Metric':<25s} {'Away Wins':>12s} {'Home Wins':>12s} {'Difference':>12s}")
    print("-" * 70)
    
    for metric, _ in sorted_corrs:
        away_mean = away_wins[metric].mean()
        home_mean = home_wins[metric].mean()
        diff = away_mean - home_mean
        print(f"{metric:<25s} {away_mean:12.3f} {home_mean:12.3f} {diff:12.3f}")
    
    # Print top predictors
    print("\n" + "="*70)
    print("TOP 5 STRONGEST PREDICTORS (by absolute correlation):")
    print("="*70)
    for i, (metric, corr) in enumerate(sorted_corrs[:5], 1):
        print(f"{i}. {metric}: {corr:.4f}")
    
    return sorted_corrs, df

if __name__ == '__main__':
    analyze_postgame_metrics()

