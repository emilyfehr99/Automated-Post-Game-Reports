#!/usr/bin/env python3
"""
Reprocess all NHL games with real metrics extracted from game data
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from nhl_api_client import NHLAPIClient
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from pdf_report_generator import PostGameReportGenerator
import numpy as np

def extract_real_metrics(game_data, away_team_id, home_team_id):
    """Extract real metrics from game data"""
    try:
        # Initialize the report generator to use its metric extraction methods
        generator = PostGameReportGenerator()
        
        # Extract advanced metrics
        away_xg, home_xg = generator._calculate_xg_from_plays(game_data)
        away_hdc, home_hdc = generator._calculate_hdc_from_plays(game_data)
        away_gs, home_gs = generator._calculate_game_scores(game_data)
        
        # Get period stats for additional metrics
        away_period_stats = generator._calculate_real_period_stats(game_data, away_team_id, 'away')
        home_period_stats = generator._calculate_real_period_stats(game_data, home_team_id, 'home')
        
        # Extract basic metrics from boxscore
        boxscore = game_data.get('boxscore', {})
        away_team_data = boxscore.get('awayTeam', {})
        home_team_data = boxscore.get('homeTeam', {})
        
        # Calculate averages for period-based stats
        away_corsi_pct = np.mean(away_period_stats.get('corsi_pct', [50.0]))
        home_corsi_pct = np.mean(home_period_stats.get('corsi_pct', [50.0]))
        
        away_pp_goals = np.mean(away_period_stats.get('pp_goals', [0]))
        away_pp_attempts = np.mean(away_period_stats.get('pp_attempts', [1]))
        home_pp_goals = np.mean(home_period_stats.get('pp_goals', [0]))
        home_pp_attempts = np.mean(home_period_stats.get('pp_attempts', [1]))
        
        away_pp_pct = (away_pp_goals / max(1, away_pp_attempts)) * 100
        home_pp_pct = (home_pp_goals / max(1, home_pp_attempts)) * 100
        
        away_fo_pct = np.mean(away_period_stats.get('fo_pct', [50.0]))
        home_fo_pct = np.mean(home_period_stats.get('fo_pct', [50.0]))
        
        metrics = {
            "away_xg": away_xg,
            "home_xg": home_xg,
            "away_hdc": away_hdc,
            "home_hdc": home_hdc,
            "away_shots": away_team_data.get('sog', 0),
            "home_shots": home_team_data.get('sog', 0),
            "away_gs": away_gs,
            "home_gs": home_gs,
            "away_corsi_pct": away_corsi_pct,
            "home_corsi_pct": home_corsi_pct,
            "away_power_play_pct": away_pp_pct,
            "home_power_play_pct": home_pp_pct,
            "away_faceoff_pct": away_fo_pct,
            "home_faceoff_pct": home_fo_pct,
            "away_hits": np.mean(away_period_stats.get('hits', [0])),
            "home_hits": np.mean(home_period_stats.get('hits', [0])),
            "away_blocked_shots": np.mean(away_period_stats.get('bs', [0])),
            "home_blocked_shots": np.mean(home_period_stats.get('bs', [0])),
            "away_giveaways": np.mean(away_period_stats.get('gv', [0])),
            "home_giveaways": np.mean(home_period_stats.get('gv', [0])),
            "away_takeaways": np.mean(away_period_stats.get('tk', [0])),
            "home_takeaways": np.mean(home_period_stats.get('tk', [0])),
            "away_penalty_minutes": np.mean(away_period_stats.get('pim', [0])),
            "home_penalty_minutes": np.mean(home_period_stats.get('pim', [0]))
        }
        
        return metrics
        
    except Exception as e:
        print(f"   ⚠️  Error extracting metrics: {e}")
        return None

def reprocess_all_games():
    """Reprocess all games with real metrics"""
    print("🏒 REPROCESSING ALL GAMES WITH REAL METRICS 🏒")
    print("=" * 60)
    
    # Load existing predictions
    predictions_file = Path('win_probability_predictions_v2.json')
    if not predictions_file.exists():
        print("❌ No predictions file found!")
        return
    
    with open(predictions_file, 'r') as f:
        pred_data = json.load(f)
    
    predictions = pred_data.get('predictions', [])
    print(f"📊 Found {len(predictions)} games to reprocess")
    
    # Initialize API client
    api_client = NHLAPIClient()
    
    # Initialize learning model
    learning_model = ImprovedSelfLearningModelV2()
    
    updated_count = 0
    failed_count = 0
    
    for i, pred in enumerate(predictions):
        game_id = pred.get('game_id')
        away_team = pred.get('away_team')
        home_team = pred.get('home_team')
        
        print(f"\\n🎯 Processing {i+1}/{len(predictions)}: {away_team} @ {home_team} ({game_id})")
        
        try:
            # Get comprehensive game data
            game_data = api_client.get_comprehensive_game_data(game_id)
            
            if game_data is None:
                print(f"   ❌ Could not fetch game data")
                failed_count += 1
                continue
            
            # Get team IDs for metric extraction
            away_team_id = game_data['boxscore']['awayTeam']['id']
            home_team_id = game_data['boxscore']['homeTeam']['id']
            
            # Extract real metrics
            real_metrics = extract_real_metrics(game_data, away_team_id, home_team_id)
            
            if real_metrics is None:
                print(f"   ❌ Could not extract metrics")
                failed_count += 1
                continue
            
            # Update the prediction with real metrics
            pred['metrics_used'] = real_metrics
            
            # Recalculate prediction accuracy
            actual_winner = pred.get('actual_winner')
            if actual_winner and pred.get('predicted_away_win_prob') and pred.get('predicted_home_win_prob'):
                predicted_winner = away_team if pred['predicted_away_win_prob'] > pred['predicted_home_win_prob'] else home_team
                pred['prediction_accuracy'] = 1.0 if predicted_winner == actual_winner else 0.0
            
            # Update timestamp
            pred['timestamp'] = datetime.now().isoformat()
            
            updated_count += 1
            
            # Show some sample metrics
            print(f"   ✅ Updated with real metrics:")
            print(f"      xG: {away_team} {real_metrics['away_xg']:.2f} vs {home_team} {real_metrics['home_xg']:.2f}")
            print(f"      HDC: {away_team} {real_metrics['away_hdc']} vs {home_team} {real_metrics['home_hdc']}")
            print(f"      Shots: {away_team} {real_metrics['away_shots']} vs {home_team} {real_metrics['home_shots']}")
            
        except Exception as e:
            print(f"   ❌ Error processing {game_id}: {e}")
            failed_count += 1
            continue
    
    # Save updated predictions
    with open(predictions_file, 'w') as f:
        json.dump(pred_data, f, indent=2)
    
    print(f"\\n📊 REPROCESSING SUMMARY:")
    print(f"   ✅ Successfully updated: {updated_count} games")
    print(f"   ❌ Failed to update: {failed_count} games")
    print(f"   📊 Total games: {len(predictions)}")
    
    # Recalculate accuracy
    correct_predictions = sum(1 for p in predictions if p.get('prediction_accuracy') == 1.0)
    total_predictions = len(predictions)
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
    
    print(f"\\n🎯 UPDATED ACCURACY:")
    print(f"   Correct predictions: {correct_predictions}/{total_predictions}")
    print(f"   Accuracy: {accuracy:.1%}")
    
    return updated_count, failed_count

def main():
    updated, failed = reprocess_all_games()
    
    if updated > 0:
        print(f"\\n🎉 SUCCESS!")
        print(f"   Reprocessed {updated} games with real metrics")
        print(f"   Model now uses legitimate data instead of defaults")
    else:
        print(f"\\n❌ FAILED!")
        print(f"   Could not reprocess any games")

if __name__ == "__main__":
    main()
