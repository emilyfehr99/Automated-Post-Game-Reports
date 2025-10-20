#!/usr/bin/env python3
"""
Script to fix team metrics by reprocessing historical games
"""

import json
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from pdf_report_generator import PostGameReportGenerator
from nhl_api_client import NHLAPIClient

def fix_team_metrics():
    print('🔧 FIXING TEAM METRICS BY REPROCESSING HISTORICAL GAMES')
    print('=' * 60)
    
    # Initialize components
    model = ImprovedSelfLearningModelV2()
    generator = PostGameReportGenerator()
    api = NHLAPIClient()
    
    # Get all predictions with actual winners
    predictions_with_winners = [p for p in model.model_data["predictions"] if p.get("actual_winner")]
    
    print(f'Found {len(predictions_with_winners)} predictions to reprocess')
    
    successful_extractions = 0
    failed_extractions = 0
    
    # Process each prediction
    for i, prediction in enumerate(predictions_with_winners):
        game_id = prediction.get("game_id")
        if not game_id:
            print(f'⚠️  Skipping {i+1}/{len(predictions_with_winners)}: No game_id')
            continue
        
        print(f'\\nProcessing {i+1}/{len(predictions_with_winners)}: {prediction["away_team"]} @ {prediction["home_team"]} (ID: {game_id})')
        
        try:
            # Get game data
            game_data = api.get_game_center(game_id)
            if not game_data:
                print(f'❌ Could not fetch game data for {game_id}')
                failed_extractions += 1
                continue
            
            # Extract comprehensive metrics
            away_xg, home_xg = generator._calculate_xg_from_plays(game_data)
            away_hdc, home_hdc = generator._calculate_hdc_from_plays(game_data)
            away_gs, home_gs = generator._calculate_game_scores(game_data)
            
            # Get period stats
            away_period_stats = generator._calculate_real_period_stats(
                game_data, 
                game_data['boxscore']['awayTeam']['id'], 
                'away'
            )
            home_period_stats = generator._calculate_real_period_stats(
                game_data, 
                game_data['boxscore']['homeTeam']['id'], 
                'home'
            )
            
            # Create comprehensive metrics
            comprehensive_metrics = {
                "away_xg": away_xg, "home_xg": home_xg,
                "away_hdc": away_hdc, "home_hdc": home_hdc,
                "away_gs": away_gs, "home_gs": home_gs,
                "away_shots": game_data['boxscore']['awayTeam'].get('sog', 0),
                "home_shots": game_data['boxscore']['homeTeam'].get('sog', 0),
                "away_corsi_pct": sum(away_period_stats.get('corsi_pct', [50.0])) / len(away_period_stats.get('corsi_pct', [50.0])),
                "home_corsi_pct": sum(home_period_stats.get('corsi_pct', [50.0])) / len(home_period_stats.get('corsi_pct', [50.0])),
                "away_power_play_pct": sum(away_period_stats.get('pp_goals', [0])) / max(1, sum(away_period_stats.get('pp_attempts', [1]))) * 100,
                "home_power_play_pct": sum(home_period_stats.get('pp_goals', [0])) / max(1, sum(home_period_stats.get('pp_attempts', [1]))) * 100,
                "away_faceoff_pct": sum(away_period_stats.get('fo_pct', [50.0])) / len(away_period_stats.get('fo_pct', [50.0])),
                "home_faceoff_pct": sum(home_period_stats.get('fo_pct', [50.0])) / len(home_period_stats.get('fo_pct', [50.0])),
                "away_hits": sum(away_period_stats.get('hits', [0])),
                "home_hits": sum(home_period_stats.get('hits', [0])),
                "away_blocked_shots": sum(away_period_stats.get('bs', [0])),
                "home_blocked_shots": sum(home_period_stats.get('bs', [0])),
                "away_giveaways": sum(away_period_stats.get('gv', [0])),
                "home_giveaways": sum(home_period_stats.get('gv', [0])),
                "away_takeaways": sum(away_period_stats.get('tk', [0])),
                "home_takeaways": sum(home_period_stats.get('tk', [0])),
                "away_penalty_minutes": sum(away_period_stats.get('pim', [0])),
                "home_penalty_minutes": sum(home_period_stats.get('pim', [0]))
            }
            
            # Update the prediction with real metrics
            prediction["metrics_used"] = comprehensive_metrics
            
            # Update team stats with real metrics
            model.update_team_stats(prediction)
            
            successful_extractions += 1
            print(f'✅ Successfully extracted metrics: xG({away_xg:.2f}/{home_xg:.2f}), HDC({away_hdc}/{home_hdc}), Shots({comprehensive_metrics["away_shots"]}/{comprehensive_metrics["home_shots"]})')
            
        except Exception as e:
            print(f'❌ Error processing {game_id}: {e}')
            failed_extractions += 1
            continue
    
    # Save the updated model
    model.save_model_data()
    
    print(f'\\n🎯 REPROCESSING COMPLETE!')
    print(f'✅ Successful extractions: {successful_extractions}')
    print(f'❌ Failed extractions: {failed_extractions}')
    print(f'📊 Success rate: {successful_extractions/(successful_extractions+failed_extractions)*100:.1f}%')
    
    # Show sample of updated team stats
    if successful_extractions > 0:
        print(f'\\n📈 SAMPLE UPDATED TEAM STATS:')
        sample_team = list(model.team_stats.keys())[0]
        team_data = model.team_stats[sample_team]
        
        for venue in ['home', 'away']:
            if venue in team_data:
                venue_data = team_data[venue]
                print(f'\\n{sample_team} {venue}:')
                print(f'  Games: {len(venue_data.get("games", []))}')
                print(f'  Goals: {venue_data.get("goals", [])[:5]}...')
                print(f'  xG: {venue_data.get("xg", [])[:5]}...')
                print(f'  HDC: {venue_data.get("hdc", [])[:5]}...')
                print(f'  Shots: {venue_data.get("shots", [])[:5]}...')

if __name__ == "__main__":
    fix_team_metrics()
