#!/usr/bin/env python3
"""
Analyze longitudinal and lateral movement combinations for winners vs losers
from postgame advanced metrics data
"""
import json
import pandas as pd
from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator
from advanced_metrics_analyzer import AdvancedMetricsAnalyzer
from pathlib import Path
from collections import defaultdict

def analyze_movement_combinations(max_games=500):
    """Analyze movement pattern combinations for winners vs losers"""
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
    
    winner_combos = defaultdict(int)
    loser_combos = defaultdict(int)
    all_data = []
    
    games_processed = 0
    games_failed = 0
    
    # Process games
    for pred in predictions[:max_games]:
        game_id = pred.get('game_id')
        if not game_id:
            continue
        
        try:
            # Get comprehensive game data
            game_data = api.get_comprehensive_game_data(str(game_id))
            if not game_data or 'boxscore' not in game_data or 'play_by_play' not in game_data:
                games_failed += 1
                continue
            
            boxscore = game_data['boxscore']
            away_team = boxscore.get('awayTeam', {})
            home_team = boxscore.get('homeTeam', {})
            
            away_team_id = away_team.get('id')
            home_team_id = home_team.get('id')
            away_goals = away_team.get('score', 0)
            home_goals = home_team.get('score', 0)
            
            # Determine winner
            if away_goals > home_goals:
                winner = 'away'
                loser = 'home'
            elif home_goals > away_goals:
                winner = 'home'
                loser = 'away'
            else:
                continue  # Skip ties
            
            # Calculate movement metrics using AdvancedMetricsAnalyzer
            analyzer = AdvancedMetricsAnalyzer(game_data.get('play_by_play', {}))
            
            away_movement = analyzer.calculate_pre_shot_movement_metrics(away_team_id)
            home_movement = analyzer.calculate_pre_shot_movement_metrics(home_team_id)
            
            # Get average movement values
            away_lateral = away_movement['lateral_movement'].get('avg_delta_y', 0.0)
            away_longitudinal = away_movement['longitudinal_movement'].get('avg_delta_x', 0.0)
            home_lateral = home_movement['lateral_movement'].get('avg_delta_y', 0.0)
            home_longitudinal = home_movement['longitudinal_movement'].get('avg_delta_x', 0.0)
            
            # Classify movement into categories using the same logic as the report
            def classify_lateral(avg_feet):
                if avg_feet == 0:
                    return "Stationary"
                elif avg_feet < 10:
                    return "Minor side-to-side"
                elif avg_feet < 20:
                    return "Cross-ice movement"
                elif avg_feet < 35:
                    return "Wide-lane movement"
                else:
                    return "Full-width movement"
            
            def classify_longitudinal(avg_feet):
                if avg_feet == 0:
                    return "Stationary"
                elif avg_feet < 15:
                    return "Close-range setup"
                elif avg_feet < 30:
                    return "Mid-range buildup"
                elif avg_feet < 50:
                    return "Extended buildup"
                else:
                    return "Long-range rush"
            
            # Classify both teams
            away_lateral_cat = classify_lateral(away_lateral)
            away_longitudinal_cat = classify_longitudinal(away_longitudinal)
            home_lateral_cat = classify_lateral(home_lateral)
            home_longitudinal_cat = classify_longitudinal(home_longitudinal)
            
            # Create combo strings
            if winner == 'away':
                winner_combo = f"Lat: {away_lateral_cat} | Long: {away_longitudinal_cat}"
                loser_combo = f"Lat: {home_lateral_cat} | Long: {home_longitudinal_cat}"
            else:
                winner_combo = f"Lat: {home_lateral_cat} | Long: {home_longitudinal_cat}"
                loser_combo = f"Lat: {away_lateral_cat} | Long: {away_longitudinal_cat}"
            
            winner_combos[winner_combo] += 1
            loser_combos[loser_combo] += 1
            
            # Store detailed data
            all_data.append({
                'game_id': game_id,
                'winner': winner,
                'away_lateral': away_lateral,
                'away_longitudinal': away_longitudinal,
                'home_lateral': home_lateral,
                'home_longitudinal': home_longitudinal,
                'away_lateral_cat': away_lateral_cat,
                'away_longitudinal_cat': away_longitudinal_cat,
                'home_lateral_cat': home_lateral_cat,
                'home_longitudinal_cat': home_longitudinal_cat,
                'winner_combo': winner_combo,
                'loser_combo': loser_combo
            })
            
            games_processed += 1
            
            if games_processed % 50 == 0:
                print(f"Processed {games_processed} games...")
                
        except Exception as e:
            games_failed += 1
            if games_failed <= 5:  # Only print first few errors
                print(f"Error processing game {game_id}: {e}")
            continue
    
    print(f"\n✅ Successfully processed {games_processed} games")
    if games_failed > 0:
        print(f"⚠️  Failed to process {games_failed} games")
    
    if not all_data:
        print("No valid movement data extracted")
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(all_data)
    
    # Print top combinations for winners
    print("\n" + "="*80)
    print("TOP MOVEMENT COMBINATIONS FOR WINNERS")
    print("="*80)
    winner_sorted = sorted(winner_combos.items(), key=lambda x: x[1], reverse=True)
    print(f"\n{'Combination':<70s} {'Count':>8s} {'%':>8s}")
    print("-" * 80)
    total_winners = sum(winner_combos.values())
    for combo, count in winner_sorted[:15]:
        pct = (count / total_winners) * 100 if total_winners > 0 else 0
        print(f"{combo:<70s} {count:>8d} {pct:>7.1f}%")
    
    # Print top combinations for losers
    print("\n" + "="*80)
    print("TOP MOVEMENT COMBINATIONS FOR LOSERS")
    print("="*80)
    loser_sorted = sorted(loser_combos.items(), key=lambda x: x[1], reverse=True)
    print(f"\n{'Combination':<70s} {'Count':>8s} {'%':>8s}")
    print("-" * 80)
    total_losers = sum(loser_combos.values())
    for combo, count in loser_sorted[:15]:
        pct = (count / total_losers) * 100 if total_losers > 0 else 0
        print(f"{combo:<70s} {count:>8d} {pct:>7.1f}%")
    
    # Compare individual categories
    print("\n" + "="*80)
    print("LATERAL MOVEMENT: WINNERS VS LOSERS")
    print("="*80)
    
    winner_lateral = []
    loser_lateral = []
    winner_longitudinal = []
    loser_longitudinal = []
    
    for row in all_data:
        if row['winner'] == 'away':
            winner_lateral.append(row['away_lateral_cat'])
            winner_longitudinal.append(row['away_longitudinal_cat'])
            loser_lateral.append(row['home_lateral_cat'])
            loser_longitudinal.append(row['home_longitudinal_cat'])
        else:
            winner_lateral.append(row['home_lateral_cat'])
            winner_longitudinal.append(row['home_longitudinal_cat'])
            loser_lateral.append(row['away_lateral_cat'])
            loser_longitudinal.append(row['away_longitudinal_cat'])
    
    from collections import Counter
    winner_lateral_counts = Counter(winner_lateral)
    loser_lateral_counts = Counter(loser_lateral)
    
    print(f"\n{'Category':<30s} {'Winners':>12s} {'Losers':>12s} {'Difference':>12s}")
    print("-" * 80)
    all_cats = set(winner_lateral_counts.keys()) | set(loser_lateral_counts.keys())
    for cat in sorted(all_cats):
        w_count = winner_lateral_counts.get(cat, 0)
        l_count = loser_lateral_counts.get(cat, 0)
        diff = w_count - l_count
        print(f"{cat:<30s} {w_count:>12d} {l_count:>12d} {diff:>12d}")
    
    print("\n" + "="*80)
    print("LONGITUDINAL MOVEMENT: WINNERS VS LOSERS")
    print("="*80)
    
    winner_long_counts = Counter(winner_longitudinal)
    loser_long_counts = Counter(loser_longitudinal)
    
    print(f"\n{'Category':<30s} {'Winners':>12s} {'Losers':>12s} {'Difference':>12s}")
    print("-" * 80)
    all_cats = set(winner_long_counts.keys()) | set(loser_long_counts.keys())
    for cat in sorted(all_cats):
        w_count = winner_long_counts.get(cat, 0)
        l_count = loser_long_counts.get(cat, 0)
        diff = w_count - l_count
        print(f"{cat:<30s} {w_count:>12d} {l_count:>12d} {diff:>12d}")
    
    # Find most predictive combinations (biggest difference)
    print("\n" + "="*80)
    print("MOST PREDICTIVE COMBINATIONS (Biggest Winner - Loser Difference)")
    print("="*80)
    
    combo_diffs = {}
    all_combos = set(winner_combos.keys()) | set(loser_combos.keys())
    for combo in all_combos:
        w_count = winner_combos.get(combo, 0)
        l_count = loser_combos.get(combo, 0)
        diff = w_count - l_count
        total = w_count + l_count
        if total > 5:  # Only show combos that appear at least 5 times
            combo_diffs[combo] = {
                'winner_count': w_count,
                'loser_count': l_count,
                'diff': diff,
                'total': total,
                'win_rate': (w_count / total * 100) if total > 0 else 0
            }
    
    sorted_diffs = sorted(combo_diffs.items(), key=lambda x: x[1]['diff'], reverse=True)
    
    print(f"\n{'Combination':<70s} {'W':>4s} {'L':>4s} {'Diff':>6s} {'Win%':>7s}")
    print("-" * 80)
    for combo, stats in sorted_diffs[:20]:
        print(f"{combo:<70s} {stats['winner_count']:>4d} {stats['loser_count']:>4d} {stats['diff']:>6d} {stats['win_rate']:>6.1f}%")
    
    return df, winner_combos, loser_combos

if __name__ == '__main__':
    analyze_movement_combinations()

