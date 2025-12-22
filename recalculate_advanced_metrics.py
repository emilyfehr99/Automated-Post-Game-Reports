#!/usr/bin/env python3
"""
Recalculate advanced metrics (lateral, longitudinal, nzt, nztsa, etc.) 
from play-by-play data for all completed games
"""
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from pdf_report_generator import PostGameReportGenerator
from advanced_metrics_analyzer import AdvancedMetricsAnalyzer
from experimental_metrics_analyzer import ExperimentalMetricsAnalyzer
from sprite_goal_analyzer import SpriteGoalAnalyzer
from nhl_api_client import NHLAPIClient
import json

def recalculate_advanced_metrics():
    """Recalculate all advanced metrics from game data"""
    print("🔄 RECALCULATING ADVANCED METRICS")
    print("=" * 60)
    
    model = ImprovedSelfLearningModelV2()
    generator = PostGameReportGenerator()
    api = NHLAPIClient()
    
    preds = model.model_data.get('predictions', [])
    completed = [p for p in preds if p.get('actual_winner')]
    
    print(f"Found {len(completed)} completed games to total")
    
    updated = 0
    failed = 0
    skipped = 0
    
    for i, pred in enumerate(completed):
        game_id = str(pred.get('game_id', ''))
        if not game_id:
            failed += 1
            continue
            
        # Resume capability: Check if game already has advanced metrics
        metrics = pred.get('metrics_used', {})
        if 'away_rebounds' in metrics and metrics.get('away_rebounds') is not None:
            skipped += 1
            if skipped % 50 == 0:
                print(f"  ⏭️  Skipped {skipped} already processed games...")
            continue
        
        print(f"  🔄 Processing game {game_id} ({i+1}/{len(completed)})...")
        
        try:
            # Get comprehensive game data
            game_data = api.get_comprehensive_game_data(game_id)
            if not game_data or 'play_by_play' not in game_data:
                failed += 1
                continue
            
            away_team = pred.get('away_team', '').upper()
            home_team = pred.get('home_team', '').upper()
            
            # Get team IDs from boxscore
            boxscore = game_data.get('boxscore', {})
            away_team_data = boxscore.get('awayTeam', {})
            home_team_data = boxscore.get('homeTeam', {})
            away_team_id = away_team_data.get('id')
            home_team_id = home_team_data.get('id')
            
            if not away_team_id or not home_team_id:
                failed += 1
                continue
            
            metrics = pred.get('metrics_used', {}).copy()
            
            # Calculate zone metrics
            try:
                away_zone_metrics = generator._calculate_zone_metrics(game_data, away_team_id, 'away')
                home_zone_metrics = generator._calculate_zone_metrics(game_data, home_team_id, 'home')
                
                # Sum across periods
                metrics['away_nzt'] = sum(away_zone_metrics.get('nz_turnovers', [0, 0, 0]))
                metrics['away_nztsa'] = sum(away_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0]))
                metrics['away_ozs'] = sum(away_zone_metrics.get('oz_originating_shots', [0, 0, 0]))
                metrics['away_nzs'] = sum(away_zone_metrics.get('nz_originating_shots', [0, 0, 0]))
                metrics['away_dzs'] = sum(away_zone_metrics.get('dz_originating_shots', [0, 0, 0]))
                metrics['away_fc'] = sum(away_zone_metrics.get('fc_cycle_sog', [0, 0, 0]))
                metrics['away_rush'] = sum(away_zone_metrics.get('rush_sog', [0, 0, 0]))
                
                metrics['home_nzt'] = sum(home_zone_metrics.get('nz_turnovers', [0, 0, 0]))
                metrics['home_nztsa'] = sum(home_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0]))
                metrics['home_ozs'] = sum(home_zone_metrics.get('oz_originating_shots', [0, 0, 0]))
                metrics['home_nzs'] = sum(home_zone_metrics.get('nz_originating_shots', [0, 0, 0]))
                metrics['home_dzs'] = sum(home_zone_metrics.get('dz_originating_shots', [0, 0, 0]))
                metrics['home_fc'] = sum(home_zone_metrics.get('fc_cycle_sog', [0, 0, 0]))
                metrics['home_rush'] = sum(home_zone_metrics.get('rush_sog', [0, 0, 0]))
            except Exception as e:
                print(f"  ⚠️  Zone metrics error for {game_id}: {e}")
                # Set defaults
                for key in ['away_nzt', 'away_nztsa', 'away_ozs', 'away_nzs', 'away_dzs', 'away_fc', 'away_rush',
                           'home_nzt', 'home_nztsa', 'home_ozs', 'home_nzs', 'home_dzs', 'home_fc', 'home_rush']:
                    metrics[key] = 0
            
            # Calculate movement metrics
            try:
                analyzer = AdvancedMetricsAnalyzer(game_data.get('play_by_play', {}))
                
                away_movement = analyzer.calculate_pre_shot_movement_metrics(away_team_id)
                home_movement = analyzer.calculate_pre_shot_movement_metrics(home_team_id)
                
                metrics['away_lateral'] = away_movement['lateral_movement'].get('avg_delta_y', 0.0)
                metrics['away_longitudinal'] = away_movement['longitudinal_movement'].get('avg_delta_x', 0.0)
                
                metrics['home_lateral'] = home_movement['lateral_movement'].get('avg_delta_y', 0.0)
                metrics['home_longitudinal'] = home_movement['longitudinal_movement'].get('avg_delta_x', 0.0)
            except Exception as e:
                print(f"  ⚠️  Movement metrics error for {game_id}: {e}")
                # Set defaults
                for key in ['away_lateral', 'away_longitudinal', 'home_lateral', 'home_longitudinal']:
                    metrics[key] = 0.0
            
            # Calculate period stats for detailed breakdowns
            try:
                away_period_stats = generator._calculate_real_period_stats(game_data, away_team_id, 'away')
                home_period_stats = generator._calculate_real_period_stats(game_data, home_team_id, 'home')
                
                # Power play details
                metrics['away_pp_goals'] = sum(away_period_stats.get('pp_goals', [0, 0, 0]))
                metrics['away_pp_attempts'] = sum(away_period_stats.get('pp_attempts', [0, 0, 0]))
                metrics['home_pp_goals'] = sum(home_period_stats.get('pp_goals', [0, 0, 0]))
                metrics['home_pp_attempts'] = sum(home_period_stats.get('pp_attempts', [0, 0, 0]))
                
                # Faceoff details
                metrics['away_faceoff_wins'] = sum(away_period_stats.get('faceoff_wins', [0, 0, 0]))
                metrics['away_faceoff_total'] = sum(away_period_stats.get('faceoff_total', [0, 0, 0]))
                metrics['home_faceoff_wins'] = sum(home_period_stats.get('faceoff_wins', [0, 0, 0]))
                metrics['home_faceoff_total'] = sum(home_period_stats.get('faceoff_total', [0, 0, 0]))
                
                # Period-by-period metrics (store as arrays [p1, p2, p3])
                metrics['away_period_shots'] = away_period_stats.get('shots', [0, 0, 0])
                metrics['away_period_corsi_pct'] = away_period_stats.get('corsi_pct', [50.0, 50.0, 50.0])
                metrics['away_period_pp_goals'] = away_period_stats.get('pp_goals', [0, 0, 0])
                metrics['away_period_pp_attempts'] = away_period_stats.get('pp_attempts', [0, 0, 0])
                metrics['away_period_pim'] = away_period_stats.get('pim', [0, 0, 0])
                metrics['away_period_hits'] = away_period_stats.get('hits', [0, 0, 0])
                metrics['away_period_fo_pct'] = away_period_stats.get('fo_pct', [50.0, 50.0, 50.0])
                metrics['away_period_blocks'] = away_period_stats.get('bs', [0, 0, 0])
                metrics['away_period_giveaways'] = away_period_stats.get('gv', [0, 0, 0])
                metrics['away_period_takeaways'] = away_period_stats.get('tk', [0, 0, 0])
                
                metrics['home_period_shots'] = home_period_stats.get('shots', [0, 0, 0])
                metrics['home_period_corsi_pct'] = home_period_stats.get('corsi_pct', [50.0, 50.0, 50.0])
                metrics['home_period_pp_goals'] = home_period_stats.get('pp_goals', [0, 0, 0])
                metrics['home_period_pp_attempts'] = home_period_stats.get('pp_attempts', [0, 0, 0])
                metrics['home_period_pim'] = home_period_stats.get('pim', [0, 0, 0])
                metrics['home_period_hits'] = home_period_stats.get('hits', [0, 0, 0])
                metrics['home_period_fo_pct'] = home_period_stats.get('fo_pct', [50.0, 50.0, 50.0])
                metrics['home_period_blocks'] = home_period_stats.get('bs', [0, 0, 0])
                metrics['home_period_giveaways'] = home_period_stats.get('gv', [0, 0, 0])
                metrics['home_period_takeaways'] = home_period_stats.get('tk', [0, 0, 0])
                
                # Period GS and xG
                period_gs_xg_away = generator._calculate_period_metrics(game_data, away_team_id, 'away')
                period_gs_xg_home = generator._calculate_period_metrics(game_data, home_team_id, 'home')
                
                if period_gs_xg_away:
                    metrics['away_period_gs'] = period_gs_xg_away[0]  # [p1_gs, p2_gs, p3_gs]
                    metrics['away_period_xg'] = period_gs_xg_away[1]  # [p1_xg, p2_xg, p3_xg]
                else:
                    metrics['away_period_gs'] = [0.0, 0.0, 0.0]
                    metrics['away_period_xg'] = [0.0, 0.0, 0.0]
                
                if period_gs_xg_home:
                    metrics['home_period_gs'] = period_gs_xg_home[0]
                    metrics['home_period_xg'] = period_gs_xg_home[1]
                else:
                    metrics['home_period_gs'] = [0.0, 0.0, 0.0]
                    metrics['home_period_xg'] = [0.0, 0.0, 0.0]
                
                # Period zone metrics
                metrics['away_period_nzt'] = away_zone_metrics.get('nz_turnovers', [0, 0, 0])
                metrics['away_period_nztsa'] = away_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0])
                metrics['away_period_ozs'] = away_zone_metrics.get('oz_originating_shots', [0, 0, 0])
                metrics['away_period_nzs'] = away_zone_metrics.get('nz_originating_shots', [0, 0, 0])
                metrics['away_period_dzs'] = away_zone_metrics.get('dz_originating_shots', [0, 0, 0])
                metrics['away_period_fc'] = away_zone_metrics.get('fc_cycle_sog', [0, 0, 0])
                metrics['away_period_rush'] = away_zone_metrics.get('rush_sog', [0, 0, 0])
                
                metrics['home_period_nzt'] = home_zone_metrics.get('nz_turnovers', [0, 0, 0])
                metrics['home_period_nztsa'] = home_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0])
                metrics['home_period_ozs'] = home_zone_metrics.get('oz_originating_shots', [0, 0, 0])
                metrics['home_period_nzs'] = home_zone_metrics.get('nz_originating_shots', [0, 0, 0])
                metrics['home_period_dzs'] = home_zone_metrics.get('dz_originating_shots', [0, 0, 0])
                metrics['home_period_fc'] = home_zone_metrics.get('fc_cycle_sog', [0, 0, 0])
                metrics['home_period_rush'] = home_zone_metrics.get('rush_sog', [0, 0, 0])
                
            except Exception as e:
                print(f"  ⚠️  Period stats error for {game_id}: {e}")
                # Set defaults for period metrics
                default_period = [0, 0, 0]
                default_period_pct = [50.0, 50.0, 50.0]
                for key in ['away_pp_goals', 'away_pp_attempts', 'home_pp_goals', 'home_pp_attempts',
                           'away_faceoff_wins', 'away_faceoff_total', 'home_faceoff_wins', 'home_faceoff_total']:
                    metrics[key] = 0
                for key in ['away_period_shots', 'away_period_pp_goals', 'away_period_pp_attempts',
                           'away_period_pim', 'away_period_hits', 'away_period_blocks',
                           'away_period_giveaways', 'away_period_takeaways',
                           'home_period_shots', 'home_period_pp_goals', 'home_period_pp_attempts',
                           'home_period_pim', 'home_period_hits', 'home_period_blocks',
                           'home_period_giveaways', 'home_period_takeaways']:
                    metrics[key] = default_period.copy()
                for key in ['away_period_corsi_pct', 'away_period_fo_pct',
                           'home_period_corsi_pct', 'home_period_fo_pct']:
                    metrics[key] = default_period_pct.copy()
                for key in ['away_period_gs', 'away_period_xg', 'home_period_gs', 'home_period_xg']:
                    metrics[key] = [0.0, 0.0, 0.0]
                for key in ['away_period_nzt', 'away_period_nztsa', 'away_period_ozs', 'away_period_nzs',
                           'away_period_dzs', 'away_period_fc', 'away_period_rush',
                           'home_period_nzt', 'home_period_nztsa', 'home_period_ozs', 'home_period_nzs',
                           'home_period_dzs', 'home_period_fc', 'home_period_rush']:
                    metrics[key] = default_period.copy()
            
            # Calculate clutch metrics
            try:
                # Get scores from prediction
                away_score = pred.get('actual_away_score', 0) or 0
                home_score = pred.get('actual_home_score', 0) or 0
                
                # Goals by period
                away_period_goals, _, _ = generator._calculate_goals_by_period(game_data, away_team_id)
                home_period_goals, _, _ = generator._calculate_goals_by_period(game_data, home_team_id)
                
                metrics['away_third_period_goals'] = away_period_goals[2] if len(away_period_goals) > 2 else 0
                metrics['home_third_period_goals'] = home_period_goals[2] if len(home_period_goals) > 2 else 0
                
                # One-goal game
                goal_diff = abs(away_score - home_score)
                metrics['away_one_goal_game'] = (goal_diff == 1)
                metrics['home_one_goal_game'] = (goal_diff == 1)
                
                # Who scored first
                first_goal_scorer = None
                if 'play_by_play' in game_data and 'plays' in game_data['play_by_play']:
                    for play in game_data['play_by_play']['plays']:
                        if play.get('typeDescKey') == 'goal':
                            details = play.get('details', {})
                            first_goal_scorer = details.get('eventOwnerTeamId')
                            break
                
                metrics['away_scored_first'] = (first_goal_scorer == away_team_id)
                metrics['home_scored_first'] = (first_goal_scorer == home_team_id)
                metrics['away_opponent_scored_first'] = (first_goal_scorer == home_team_id)
                metrics['home_opponent_scored_first'] = (first_goal_scorer == away_team_id)
                
                # NEW: High-signal advanced metrics
                pbp = game_data.get('play_by_play', {})
                exp_analyzer = ExperimentalMetricsAnalyzer(pbp, game_id=game_id)
                exp_results = exp_analyzer.calculate_all_experimental_metrics()
                
                away_exp = exp_results.get(away_team_id, {})
                home_exp = exp_results.get(home_team_id, {})
                
                metrics['away_rebounds'] = away_exp.get('rebound_count', 0)
                metrics['home_rebounds'] = home_exp.get('rebound_count', 0)
                metrics['away_rush_shots'] = away_exp.get('rush_shots', 0)
                metrics['home_rush_shots'] = home_exp.get('rush_shots', 0)
                metrics['away_cycle_shots'] = away_exp.get('cycle_shots', 0)
                metrics['home_cycle_shots'] = home_exp.get('cycle_shots', 0)
                metrics['away_forecheck_turnovers'] = away_exp.get('forecheck_turnovers', 0)
                metrics['home_forecheck_turnovers'] = home_exp.get('forecheck_turnovers', 0)
                metrics['away_passes_per_goal'] = away_exp.get('passes_per_goal', 0.0)
                metrics['home_passes_per_goal'] = home_exp.get('passes_per_goal', 0.0)
                
                # Sprite Goal analysis
                sprite_analyzer = SpriteGoalAnalyzer(game_data)
                sprite_results = sprite_analyzer.analyze_goals()
                
                away_sprite = sprite_results.get('away', {})
                home_sprite = sprite_results.get('home', {})
                
                metrics['away_net_front_traffic_pct'] = away_sprite.get('net_front_traffic_pct', 0.0)
                metrics['home_net_front_traffic_pct'] = home_sprite.get('net_front_traffic_pct', 0.0)
                metrics['away_avg_goal_distance'] = away_sprite.get('avg_goal_distance', 0.0)
                metrics['home_avg_goal_distance'] = home_sprite.get('avg_goal_distance', 0.0)
                
                away_entries = away_sprite.get('entry_type_share', {})
                home_entries = home_sprite.get('entry_type_share', {})
                metrics['away_zone_entry_carry_pct'] = away_entries.get('carry', 0.0)
                metrics['home_zone_entry_carry_pct'] = home_entries.get('carry', 0.0)
                metrics['away_zone_entry_pass_pct'] = away_entries.get('pass', 0.0)
                metrics['home_zone_entry_pass_pct'] = home_entries.get('pass', 0.0)
                
                away_mv = away_sprite.get('movement_metrics', {})
                home_mv = home_sprite.get('movement_metrics', {})
                metrics['away_east_west_play'] = away_mv.get('east_west', 0.0)
                metrics['home_east_west_play'] = home_mv.get('east_west', 0.0)
                metrics['away_north_south_play'] = away_mv.get('north_south', 0.0)
                metrics['home_north_south_play'] = home_mv.get('north_south', 0.0)
                
            except Exception as e:
                print(f"  ⚠️  Clutch/Advanced metrics error for {game_id}: {e}")
                # Set defaults for new metrics if they fail
                for k in ['rebounds', 'rush_shots', 'cycle_shots', 'forecheck_turnovers', 'passes_per_goal',
                         'net_front_traffic_pct', 'avg_goal_distance', 'zone_entry_carry_pct', 'zone_entry_pass_pct',
                         'east_west_play', 'north_south_play']:
                    metrics[f'away_{k}'] = 0.0
                    metrics[f'home_{k}'] = 0.0
                
                for key in ['away_third_period_goals', 'home_third_period_goals',
                           'away_one_goal_game', 'home_one_goal_game',
                           'away_scored_first', 'home_scored_first',
                           'away_opponent_scored_first', 'home_opponent_scored_first']:
                    metrics[key] = False if 'game' in key or 'scored' in key else 0
            
            # Update prediction with new metrics
            pred['metrics_used'] = metrics
            updated += 1
            
            if updated % 25 == 0:
                print(f"  ✅ Updated {updated}/{len(completed)} games...")
                
        except Exception as e:
            failed += 1
            if failed <= 5:
                print(f"  ❌ Error processing {game_id}: {e}")
            continue
    
    # Save updated predictions
    model.save_model_data()
    
    print("\n✅ Metrics recalculation complete!")
    print(f"   Updated: {updated} games")
    print(f"   Skipped: {skipped} games")
    print(f"   Failed:  {failed} games")
    
    # Rebuild team_stats with new metrics
    print(f"\n🔄 Rebuilding team_stats with new metrics...")
    model.team_stats = {}
    model.team_stats = model.load_team_stats()
    
    for i, pred in enumerate(completed):
        try:
            model.update_team_stats(pred)
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(completed)} games...")
        except Exception as e:
            if i < 3:
                print(f"  Error: {e}")
    
    model.save_model_data()
    model.save_team_stats()
    
    print(f"\n✅ Team stats rebuilt with advanced metrics!")
    
    # Show sample
    sample_team = 'CAR'
    if sample_team in model.team_stats:
        venue_data = model.team_stats[sample_team]['home']
        print(f"\n  Sample ({sample_team} home):")
        print(f"    Games: {len(venue_data.get('games', []))}")
        print(f"    Lateral: {len(venue_data.get('lateral', []))} values")
        print(f"    NZT: {len(venue_data.get('nzt', []))} values")
        if venue_data.get('lateral'):
            print(f"    Sample lateral: {venue_data['lateral'][:3]}")
        if venue_data.get('nzt'):
            print(f"    Sample nzt: {venue_data['nzt'][:3]}")
    
    return updated

if __name__ == "__main__":
    recalculate_advanced_metrics()

