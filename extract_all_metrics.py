#!/usr/bin/env python3
"""
Extract comprehensive metrics for all 84 historical games using NHL schedule endpoint
and post-game report generator
"""

import json
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from pdf_report_generator import PostGameReportGenerator
from nhl_api_client import NHLAPIClient

def extract_all_metrics():
    print('🎯 EXTRACTING COMPREHENSIVE METRICS FOR ALL 84 GAMES')
    print('=' * 60)
    
    # Initialize components
    model = ImprovedSelfLearningModelV2()
    generator = PostGameReportGenerator()
    api = NHLAPIClient()
    
    # Get all predictions with actual winners
    predictions_with_winners = [p for p in model.model_data["predictions"] if p.get("actual_winner")]
    
    print(f'Found {len(predictions_with_winners)} predictions to process')
    
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
            # Get game data from NHL API
            game_data = api.get_game_center(game_id)
            if not game_data:
                print(f'❌ Could not fetch game data for {game_id}')
                failed_extractions += 1
                continue
            
            print(f'✅ Fetched game data for {game_id}')
            
            # Use the post-game report generator to extract ALL metrics
            # This is the key insight - the report generator already has all the logic!
            
            # Extract comprehensive metrics using the same methods as the report generator
            away_xg, home_xg = generator._calculate_xg_from_plays(game_data)
            away_hdc, home_hdc = generator._calculate_hdc_from_plays(game_data)
            away_gs, home_gs = generator._calculate_game_scores(game_data)
            
            # Get period stats (this gives us Corsi, PP%, Faceoff%, etc.)
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
            
            # Create comprehensive metrics dictionary
            comprehensive_metrics = {
                # Basic metrics
                "away_xg": away_xg, "home_xg": home_xg,
                "away_hdc": away_hdc, "home_hdc": home_hdc,
                "away_gs": away_gs, "home_gs": home_gs,
                "away_shots": game_data['boxscore']['awayTeam'].get('sog', 0),
                "home_shots": game_data['boxscore']['homeTeam'].get('sog', 0),
                
                # Advanced metrics from period stats
                "away_corsi_pct": sum(away_period_stats.get('corsi_pct', [50.0])) / len(away_period_stats.get('corsi_pct', [50.0])),
                "home_corsi_pct": sum(home_period_stats.get('corsi_pct', [50.0])) / len(home_period_stats.get('corsi_pct', [50.0])),
                
                # Power play percentage
                "away_power_play_pct": sum(away_period_stats.get('pp_goals', [0])) / max(1, sum(away_period_stats.get('pp_attempts', [1]))) * 100,
                "home_power_play_pct": sum(home_period_stats.get('pp_goals', [0])) / max(1, sum(home_period_stats.get('pp_attempts', [1]))) * 100,
                
                # Faceoff percentage
                "away_faceoff_pct": sum(away_period_stats.get('fo_pct', [50.0])) / len(away_period_stats.get('fo_pct', [50.0])),
                "home_faceoff_pct": sum(home_period_stats.get('fo_pct', [50.0])) / len(home_period_stats.get('fo_pct', [50.0])),
                
                # Physical play metrics
                "away_hits": sum(away_period_stats.get('hits', [0])),
                "home_hits": sum(home_period_stats.get('hits', [0])),
                "away_blocked_shots": sum(away_period_stats.get('bs', [0])),
                "home_blocked_shots": sum(home_period_stats.get('bs', [0])),
                
                # Turnover metrics
                "away_giveaways": sum(away_period_stats.get('gv', [0])),
                "home_giveaways": sum(home_period_stats.get('gv', [0])),
                "away_takeaways": sum(away_period_stats.get('tk', [0])),
                "home_takeaways": sum(home_period_stats.get('tk', [0])),
                
                # Penalty metrics
                "away_penalty_minutes": sum(away_period_stats.get('pim', [0])),
                "home_penalty_minutes": sum(home_period_stats.get('pim', [0]))
            }
            
            # Update the prediction with real metrics
            prediction["metrics_used"] = comprehensive_metrics
            
            # Update team stats with real metrics
            model.update_team_stats(prediction)
            
            successful_extractions += 1
            print(f'✅ Extracted comprehensive metrics:')
            print(f'   xG: {away_xg:.2f} vs {home_xg:.2f}')
            print(f'   HDC: {away_hdc} vs {home_hdc}')
            print(f'   Shots: {comprehensive_metrics["away_shots"]} vs {comprehensive_metrics["home_shots"]}')
            print(f'   Corsi%: {comprehensive_metrics["away_corsi_pct"]:.1f}% vs {comprehensive_metrics["home_corsi_pct"]:.1f}%')
            
        except Exception as e:
            print(f'❌ Error processing {game_id}: {e}')
            import traceback
            traceback.print_exc()
            failed_extractions += 1
            continue
    
    # Save the updated model
    model.save_model_data()
    
    print(f'\\n🎯 METRIC EXTRACTION COMPLETE!')
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
                print(f'  Corsi%: {venue_data.get("corsi_pct", [])[:5]}...')
    
    return successful_extractions > 0

if __name__ == "__main__":
    extract_all_metrics()
