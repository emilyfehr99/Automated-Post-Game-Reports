#!/usr/bin/env python3
"""
Backfill Advanced Metrics
Populates Phase 18 and momentum signals for recent games in the event store.
"""
import json
import logging
from pathlib import Path
from nhl_api_client import NHLAPIClient
from analyzers.advanced_metrics_analyzer import AdvancedMetricsAnalyzer
from utils.event_store import append_outcome_event, load_latest_by_game_id, OUTCOME_EVENTS_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backfill():
    client = NHLAPIClient()
    outcomes = load_latest_by_game_id(OUTCOME_EVENTS_PATH)
    
    # Get last 150 games to ensure rolling L20 is healthy
    sorted_gids = sorted(outcomes.keys(), reverse=True)[:150]
    
    logger.info(f"Backfilling {len(sorted_gids)} games...")
    
    for gid in sorted_gids:
        pred = outcomes[gid]
        if pred.get('home_royal_road') is not None:
            # Already backfilled
            continue
            
        logger.info(f"Processing game {gid}...")
        try:
            game_data = client.get_comprehensive_game_data(str(gid))
            if not game_data or 'play_by_play' not in game_data:
                continue
                
            boxscore = game_data.get('boxscore', {})
            h_id = boxscore.get('homeTeam', {}).get('id')
            a_id = boxscore.get('awayTeam', {}).get('id')
            
            analyzer = AdvancedMetricsAnalyzer(game_data['play_by_play'])
            report = analyzer.generate_comprehensive_report(a_id, h_id)
            h_rep = report.get('home_team', {})
            a_rep = report.get('away_team', {})
            
            mom = analyzer.calculate_momentum_metrics(a_id, h_id)
            
            full_metrics = {
                'home_royal_road': h_rep.get('pre_shot_movement', {}).get('royal_road_proxy', {}).get('attempts', 0),
                'away_royal_road': a_rep.get('pre_shot_movement', {}).get('royal_road_proxy', {}).get('attempts', 0),
                'home_lateral': h_rep.get('pre_shot_movement', {}).get('lateral_movement', {}).get('avg_delta_y', 0),
                'away_lateral': a_rep.get('pre_shot_movement', {}).get('lateral_movement', {}).get('avg_delta_y', 0),
                'home_nzt_possession': h_rep.get('nzt_stats', {}).get('nzt_possession_pct', 50.0),
                'away_nzt_possession': a_rep.get('nzt_stats', {}).get('nzt_possession_pct', 50.0),
                'home_rush_sv_pct': h_rep.get('rush_stats', {}).get('rush_save_pct', 90.0),
                'away_rush_sv_pct': a_rep.get('rush_stats', {}).get('rush_save_pct', 90.0),
                'home_ca_shots': h_rep.get('nzt_stats', {}).get('counter_attack_shots', 0),
                'away_ca_shots': a_rep.get('nzt_stats', {}).get('counter_attack_shots', 0),
                'p1_xg_home': mom.get('p1_xg', {}).get('home', 0.8),
                'p1_xg_away': mom.get('p1_xg', {}).get('away', 0.8),
                'p2_xg_home': mom.get('p2_xg', {}).get('home', 0.8),
                'p2_xg_away': mom.get('p2_xg', {}).get('away', 0.8),
                'p3_xg_home': mom.get('p3_xg', {}).get('home', 0.8),
                'p3_xg_away': mom.get('p3_xg', {}).get('away', 0.8),
                'lead_after_p2': mom.get('lead_after_p2', 0)
            }
            
            # Re-append with new fields (event store handles duplicates by keeping latest)
            append_outcome_event(
                game_id=str(gid),
                date=pred.get('date'),
                away_team=pred.get('away_team'),
                home_team=pred.get('home_team'),
                actual_away_score=pred.get('actual_away_score'),
                actual_home_score=pred.get('actual_home_score'),
                actual_winner=pred.get('actual_winner'),
                lead_after_p1=pred.get('lead_after_p1', 0),
                **full_metrics
            )
            
        except Exception as e:
            logger.error(f"Error backfilling {gid}: {e}")

if __name__ == "__main__":
    backfill()
