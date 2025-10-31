#!/usr/bin/env python3
"""
Correlation analysis of prediction model components to identify biggest win predictors
"""
import json
import numpy as np
import pandas as pd
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from pathlib import Path

def analyze_components():
    """Analyze correlation of all prediction components with actual game outcomes"""
    model = ImprovedSelfLearningModelV2()
    
    # Get all completed predictions
    predictions = [p for p in model.model_data.get('predictions', []) if p.get('actual_winner')]
    
    if not predictions:
        print("No completed predictions found")
        return
    
    print(f"Analyzing {len(predictions)} completed games...")
    
    # Extract component data
    components_data = []
    
    for pred in predictions:
        away_team = pred.get('away_team', '').upper()
        home_team = pred.get('home_team', '').upper()
        date = pred.get('date')
        actual_winner = pred.get('actual_winner')
        
        # Determine actual outcome: 1 if away wins, 0 if home wins
        if actual_winner == away_team or actual_winner == 'away':
            outcome = 1  # Away won
        elif actual_winner == home_team or actual_winner == 'home':
            outcome = 0  # Home won
        else:
            continue
        
        try:
            # Use stored metrics if available, otherwise compute
            metrics = pred.get('metrics_used', {})
            
            # Extract from stored metrics (away - home differences)
            row = {
                'outcome': outcome,
                'xg_diff': metrics.get('away_xg', 0) - metrics.get('home_xg', 0),
                'hdc_diff': metrics.get('away_hdc', 0) - metrics.get('home_hdc', 0),
                'corsi_diff': metrics.get('away_corsi_pct', 50) - metrics.get('home_corsi_pct', 50),
                'shots_diff': metrics.get('away_shots', 0) - metrics.get('home_shots', 0),
                'gs_diff': metrics.get('away_gs', 0) - metrics.get('home_gs', 0),
                'power_play_diff': metrics.get('away_power_play_pct', 0) - metrics.get('home_power_play_pct', 0),
                'faceoff_diff': metrics.get('away_faceoff_pct', 50) - metrics.get('home_faceoff_pct', 50),
                'hits_diff': metrics.get('away_hits', 0) - metrics.get('home_hits', 0),
                'blocked_shots_diff': metrics.get('away_blocked_shots', 0) - metrics.get('home_blocked_shots', 0),
                'takeaways_diff': metrics.get('away_takeaways', 0) - metrics.get('home_takeaways', 0),
                'giveaways_diff': metrics.get('away_giveaways', 0) - metrics.get('home_giveaways', 0),
                'pim_diff': metrics.get('away_penalty_minutes', 0) - metrics.get('home_penalty_minutes', 0),
            }
            
            # Use stored situational factors if available (from backfill), otherwise compute
            stored_rest = metrics.get('away_rest') is not None and metrics.get('home_rest') is not None
            stored_goalie = metrics.get('away_goalie_perf') is not None and metrics.get('home_goalie_perf') is not None
            stored_sos = metrics.get('away_sos') is not None and metrics.get('home_sos') is not None
            
            if stored_rest:
                row['rest_diff'] = metrics.get('away_rest', 0.0) - metrics.get('home_rest', 0.0)
            else:
                try:
                    away_rest = model._calculate_rest_days_advantage(away_team, 'away', date)
                    home_rest = model._calculate_rest_days_advantage(home_team, 'home', date)
                    row['rest_diff'] = away_rest - home_rest
                except Exception as e:
                    row['rest_diff'] = 0.0
            
            if stored_goalie:
                row['goalie_diff'] = metrics.get('away_goalie_perf', 0.0) - metrics.get('home_goalie_perf', 0.0)
            else:
                try:
                    away_goalie = model._goalie_performance_for_game(away_team, 'away', date)
                    home_goalie = model._goalie_performance_for_game(home_team, 'home', date)
                    row['goalie_diff'] = away_goalie - home_goalie
                except Exception as e:
                    row['goalie_diff'] = 0.0
            
            if stored_sos:
                row['sos_diff'] = metrics.get('away_sos', 0.0) - metrics.get('home_sos', 0.0)
            else:
                try:
                    away_sos = model._calculate_sos(away_team, 'away')
                    home_sos = model._calculate_sos(home_team, 'home')
                    row['sos_diff'] = away_sos - home_sos
                except Exception as e:
                    row['sos_diff'] = 0.0
            
            # Get team performance for recent form
            try:
                away_perf = model.get_team_performance(away_team, 'away')
                home_perf = model.get_team_performance(home_team, 'home')
                row['recent_form_diff'] = away_perf.get('recent_form', 0.5) - home_perf.get('recent_form', 0.5)
            except:
                row['recent_form_diff'] = 0.0
            
            components_data.append(row)
        except Exception as e:
            continue
    
    if not components_data:
        print("No valid component data extracted")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(components_data)
    
    # Calculate correlations with outcome
    correlations = {}
    for col in df.columns:
        if col != 'outcome':
            # Skip columns with all zeros or constant values (but include rest/goalie/sos even if low variance)
            if df[col].std() > 1e-6 or col in ['rest_diff', 'goalie_diff', 'sos_diff', 'recent_form_diff']:
                corr = df[col].corr(df['outcome'])
                if not np.isnan(corr):
                    correlations[col] = corr
    
    # Debug: show variance for situational factors
    print("\nSituational factor variance:")
    for factor in ['rest_diff', 'goalie_diff', 'sos_diff', 'recent_form_diff']:
        if factor in df.columns:
            std_val = df[factor].std()
            mean_val = df[factor].mean()
            print(f"  {factor}: mean={mean_val:.4f}, std={std_val:.4f}")
    
    # Sort by absolute correlation
    sorted_corrs = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
    
    print("\n" + "="*70)
    print("CORRELATION ANALYSIS: Prediction Components vs Win Outcomes")
    print("="*70)
    print(f"\nSample size: {len(df)} games")
    print(f"\nComponent correlations (sorted by absolute value):")
    print(f"{'Component':<25s} {'Correlation':>12s} {'Direction':>10s} {'Magnitude'}")
    print("-" * 70)
    
    for component, corr in sorted_corrs:
        abs_corr = abs(corr)
        direction = "↑ Away Win" if corr > 0 else "↓ Home Win"
        bar = "█" * int(abs_corr * 30)
        print(f"{component:<25s} {corr:11.4f}  {direction:<10s} {bar}")
    
    # Additional analysis: mean differences by outcome
    print("\n" + "="*70)
    print("MEAN COMPONENT VALUES: Away Wins vs Home Wins")
    print("="*70)
    
    away_wins = df[df['outcome'] == 1]
    home_wins = df[df['outcome'] == 0]
    
    print(f"\nAway wins: {len(away_wins)} games")
    print(f"Home wins: {len(home_wins)} games\n")
    print(f"{'Component':<25s} {'Away Wins':>12s} {'Home Wins':>12s} {'Difference':>12s}")
    print("-" * 70)
    
    for col in sorted_corrs:
        component = col[0]
        if component != 'outcome':
            away_mean = away_wins[component].mean()
            home_mean = home_wins[component].mean()
            diff = away_mean - home_mean
            print(f"{component:<25s} {away_mean:12.3f} {home_mean:12.3f} {diff:12.3f}")
    
    return sorted_corrs

if __name__ == '__main__':
    analyze_components()

