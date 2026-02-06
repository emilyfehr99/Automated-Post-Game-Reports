"""
Correlation Analysis: What Actually Predicts Goals?

Analyzes all available metrics to determine which ones have the strongest
correlation with actual goals scored, so we can build a data-driven model
instead of making assumptions.
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats

def load_team_stats():
    """Load the team stats JSON file"""
    stats_file = Path("data/season_2025_2026_team_stats.json")
    with open(stats_file, 'r') as f:
        data = json.load(f)
    return data['teams']

def calculate_correlations_for_team(team_name, team_data, venue):
    """Calculate correlation between each metric and goals scored"""
    venue_data = team_data.get(venue, {})
    
    if not venue_data or 'goals' not in venue_data:
        return None
    
    goals = np.array(venue_data['goals'])
    
    if len(goals) < 3:  # Need at least 3 games
        return None
    
    correlations = {}
    
    # Metrics to analyze
    metrics = {
        'xg': 'Expected Goals',
        'shots': 'Shots on Goal',
        'hdc': 'High Danger Chances',
        'corsi_pct': 'Corsi %',
        'fenwick_pct': 'Fenwick %',
        'pdo': 'PDO (Luck)',
        'ozs': 'Offensive Zone Starts',
        'power_play_pct': 'Power Play %',
        'faceoff_pct': 'Faceoff %',
        'takeaways': 'Takeaways',
        'giveaways': 'Giveaways',
        'hits': 'Hits',
        'blocked_shots': 'Blocked Shots',
        'fc': 'Forecheck',
        'rush': 'Rush Attempts',
    }
    
    for metric_key, metric_name in metrics.items():
        if metric_key in venue_data:
            metric_values = np.array(venue_data[metric_key])
            
            # Make sure arrays are same length
            min_len = min(len(goals), len(metric_values))
            if min_len < 3:
                continue
                
            goals_trimmed = goals[:min_len]
            metric_trimmed = metric_values[:min_len]
            
            try:
                # Calculate Pearson correlation
                correlation, p_value = stats.pearsonr(goals_trimmed, metric_trimmed)
                
                if not np.isnan(correlation):
                    correlations[metric_key] = {
                        'name': metric_name,
                        'correlation': correlation,
                        'p_value': p_value,
                        'significant': p_value < 0.05
                    }
            except:
                pass
    
    return correlations

def analyze_overtime_shootout_tendency(team_data, venue):
    """Analyze how often team's games go to OT/SO"""
    venue_data = team_data.get(venue, {})
    
    if not venue_data or 'goals' not in venue_data:
        return None
    
    goals_for = np.array(venue_data['goals'])
    goals_against = np.array(venue_data.get('opp_goals', []))
    
    if len(goals_for) != len(goals_against) or len(goals_for) < 3:
        return None
    
    # Games decided by 1 goal are likely OT/SO
    goal_diff = np.abs(goals_for - goals_against)
    one_goal_games = np.sum(goal_diff <= 1)
    total_games = len(goals_for)
    
    close_game_pct = (one_goal_games / total_games) * 100
    
    # Average goal differential (margin of victory/defeat)
    avg_goal_diff = np.mean(goal_diff)
    
    return {
        'close_games_pct': close_game_pct,
        'avg_goal_diff': avg_goal_diff,
        'ot_so_tendency': 'High' if close_game_pct > 60 else 'Medium' if close_game_pct > 40 else 'Low'
    }

def main():
    teams = load_team_stats()
    
    print("=" * 80)
    print("CORRELATION ANALYSIS: WHAT PREDICTS GOALS?")
    print("=" * 80)
    print()
    
    all_correlations = {}
    
    # Analyze each team at home and away
    for team_code, team_data in teams.items():
        for venue in ['home', 'away']:
            key = f"{team_code}_{venue}"
            correlations = calculate_correlations_for_team(team_code, team_data, venue)
            
            if correlations:
                all_correlations[key] = correlations
    
    # Aggregate correlations across all teams
    print("\n📊 AGGREGATE CORRELATIONS (All Teams, All Venues)")
    print("-" * 80)
    
    metric_correlations = {}
    
    for team_key, team_corrs in all_correlations.items():
        for metric_key, data in team_corrs.items():
            if metric_key not in metric_correlations:
                metric_correlations[metric_key] = {
                    'name': data['name'],
                    'correlations': [],
                    'p_values': []
                }
            metric_correlations[metric_key]['correlations'].append(data['correlation'])
            metric_correlations[metric_key]['p_values'].append(data['p_value'])
    
    # Calculate average correlation for each metric
    metric_summary = []
    for metric_key, data in metric_correlations.items():
        avg_corr = np.mean(data['correlations'])
        median_corr = np.median(data['correlations'])
        avg_p = np.mean(data['p_values'])
        
        metric_summary.append({
            'metric': metric_key,
            'name': data['name'],
            'avg_correlation': avg_corr,
            'median_correlation': median_corr,
            'avg_p_value': avg_p,
            'sample_size': len(data['correlations'])
        })
    
    # Sort by average correlation (descending)
    metric_summary.sort(key=lambda x: abs(x['avg_correlation']), reverse=True)
    
    print(f"{'Metric':<25} {'Avg Corr':<12} {'Median':<12} {'P-Value':<12} {'Strength'}")
    print("-" * 80)
    
    for item in metric_summary:
        strength = "STRONG" if abs(item['avg_correlation']) > 0.6 else \
                   "MODERATE" if abs(item['avg_correlation']) > 0.4 else \
                   "WEAK" if abs(item['avg_correlation']) > 0.2 else "VERY WEAK"
        
        print(f"{item['name']:<25} {item['avg_correlation']:>10.3f}  {item['median_correlation']:>10.3f}  "
              f"{item['avg_p_value']:>10.3f}  {strength}")
    
    print("\n" + "=" * 80)
    print("📈 RECOMMENDED MODEL WEIGHTS")
    print("=" * 80)
    
    # Suggest weights based on correlations
    total_corr = sum(abs(item['avg_correlation']) for item in metric_summary[:5])
    
    print("\nTop 5 Predictors of Goals (normalized weights):")
    for item in metric_summary[:5]:
        weight = abs(item['avg_correlation']) / total_corr
        print(f"  {item['name']:<25} {weight*100:>6.1f}%  (r={item['avg_correlation']:.3f})")
    
    # Analyze OT/SO tendencies
    print("\n" + "=" * 80)
    print("🎯 OVERTIME/SHOOTOUT TENDENCY ANALYSIS")
    print("=" * 80)
    print()
    
    ot_tendencies = []
    
    for team_code, team_data in teams.items():
        for venue in ['home', 'away']:
            ot_data = analyze_overtime_shootout_tendency(team_data, venue)
            if ot_data:
                ot_tendencies.append({
                    'team': f"{team_code} ({venue})",
                    **ot_data
                })
    
    # Sort by close game percentage
    ot_tendencies.sort(key=lambda x: x['close_games_pct'], reverse=True)
    
    print(f"{'Team':<15} {'Close Games %':<15} {'Avg Goal Diff':<15} {'OT/SO Tendency'}")
    print("-" * 80)
    
    for item in ot_tendencies[:10]:  # Top 10
        print(f"{item['team']:<15} {item['close_games_pct']:>13.1f}%  {item['avg_goal_diff']:>13.2f}  "
              f"{item['ot_so_tendency']:>15}")
    
    print("\n💡 INSIGHT: Teams with >60% close games are highly likely to push to OT/SO")
    print("           Consider flagging predictions as '(OT/SO)' for these teams\n")

if __name__ == "__main__":
    main()
