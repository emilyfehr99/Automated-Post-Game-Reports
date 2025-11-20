#!/usr/bin/env python3
"""
Complete team metrics extraction - ensure every team has comprehensive metrics
for every single game they've played this season
"""

import json
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from pdf_report_generator import PostGameReportGenerator
from nhl_api_client import NHLAPIClient

def complete_team_metrics():
    print('🎯 COMPLETE TEAM METRICS EXTRACTION')
    print('=' * 50)
    print('Ensuring every team has comprehensive metrics for every game')
    
    # Initialize components
    model = ImprovedSelfLearningModelV2()
    generator = PostGameReportGenerator()
    api = NHLAPIClient()
    
    # Get all predictions with actual winners
    predictions_with_winners = [p for p in model.model_data["predictions"] if p.get("actual_winner")]
    
    print(f'Found {len(predictions_with_winners)} predictions to process')
    
    # Clear existing team stats to start fresh
    model.team_stats = {}
    
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
            
            # Extract comprehensive metrics using the post-game report generator
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
            
            # Update team stats with real metrics (this will now be clean data)
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
    
    print(f'\\n🎯 COMPLETE METRICS EXTRACTION FINISHED!')
    print(f'✅ Successful extractions: {successful_extractions}')
    print(f'❌ Failed extractions: {failed_extractions}')
    print(f'📊 Success rate: {successful_extractions/(successful_extractions+failed_extractions)*100:.1f}%')
    
    # Verify the results
    print(f'\\n🔍 VERIFICATION:')
    verify_complete_metrics(model)
    
    return successful_extractions > 0

def verify_complete_metrics(model):
    """Verify that every team has complete metrics for every game"""
    print('Checking team metrics completeness...')
    
    teams_with_complete_data = 0
    teams_with_incomplete_data = 0
    
    for team in sorted(model.team_stats.keys()):
        team_data = model.team_stats[team]
        team_complete = True
        
        for venue in ['home', 'away']:
            if venue in team_data:
                venue_data = team_data[venue]
                games = len(venue_data.get('games', []))
                
                if games == 0:
                    continue
                
                # Check if all metrics have real data (no zeros)
                xg_data = venue_data.get('xg', [])
                hdc_data = venue_data.get('hdc', [])
                shots_data = venue_data.get('shots', [])
                
                # Count real vs default values
                real_xg = [x for x in xg_data if x > 0]
                real_hdc = [h for h in hdc_data if h > 0]
                real_shots = [s for s in shots_data if s > 0]
                
                if len(real_xg) != games or len(real_hdc) != games or len(real_shots) != games:
                    team_complete = False
                    print(f'❌ {team} {venue}: {len(real_xg)}/{games} xG, {len(real_hdc)}/{games} HDC, {len(real_shots)}/{games} shots')
        
        if team_complete:
            teams_with_complete_data += 1
        else:
            teams_with_incomplete_data += 1
    
    print(f'\\n📊 VERIFICATION RESULTS:')
    print(f'Teams with complete metrics: {teams_with_complete_data}')
    print(f'Teams with incomplete metrics: {teams_with_incomplete_data}')
    print(f'Total teams: {len(model.team_stats)}')
    
    if teams_with_incomplete_data == 0:
        print('🎉 SUCCESS: All teams have complete metrics for all games!')
    else:
        print('⚠️  Some teams still have incomplete metrics')

if __name__ == "__main__":
    complete_team_metrics()
