#!/usr/bin/env python3
"""
Update Game Outcomes
-------------------
This script checks for past predictions that don't have an outcome (actual_winner)
and queries the NHL API to see if the game has been played. If so, it updates
the prediction record with the final score and winner.

This ensures the model performance metrics (accuracy, etc.) remain up-to-date.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
try:
    from utils.nhl_api_client import NHLAPIClient
except ImportError:
    from nhl_api_client import NHLAPIClient
try:
    from utils.timing import timed
except Exception:
    from timing import timed
try:
    from utils.event_store import append_outcome_event
except Exception:
    try:
        from event_store import append_outcome_event
    except Exception:
        append_outcome_event = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_game_outcomes():
    """Update valid predictions with actual game outcomes"""
    with timed("update_game_outcomes total"):
        # Canonical: use append-only event logs
        try:
            from utils.event_store import load_latest_by_game_id, PREDICTION_EVENTS_PATH, OUTCOME_EVENTS_PATH
        except Exception:
            load_latest_by_game_id = None
            PREDICTION_EVENTS_PATH = None
            OUTCOME_EVENTS_PATH = None

        predictions: list = []
        if load_latest_by_game_id is not None and PREDICTION_EVENTS_PATH is not None:
            preds_by_gid = load_latest_by_game_id(PREDICTION_EVENTS_PATH)
            outs_by_gid = load_latest_by_game_id(OUTCOME_EVENTS_PATH) if OUTCOME_EVENTS_PATH is not None else {}
            for gid, p in preds_by_gid.items():
                # Mark outcomes if already present
                if outs_by_gid.get(gid, {}).get("actual_winner"):
                    continue
                predictions.append(p)
            logger.info(f"Checking for game updates via events log ({len(predictions)} pending games)...")
        else:
            # Legacy fallback
            predictions_file = Path('data/win_probability_predictions_v2.json')
            if not predictions_file.exists():
                predictions_file = Path('win_probability_predictions_v2.json')
            if not predictions_file.exists():
                logger.error("Predictions file not found (events log missing too)")
                print("OUTCOMES_UPDATED=0")
                return 0
            logger.info(f"Checking for game updates in {predictions_file}...")
            with open(predictions_file, 'r') as f:
                data = json.load(f)
            predictions = data.get('predictions', [])

        updated_count = 0
        client = NHLAPIClient()

        # Identify games that need updates (past date, no actual_winner)
        today = datetime.now().strftime('%Y-%m-%d')
        
        pending_games = []
        for pred in predictions:
            if pred.get('actual_winner'):
                continue
            g_date = pred.get('date')
            g_id = pred.get('game_id')
            if not g_date or not g_id or g_date > today:
                continue
            pending_games.append(pred)

        if not pending_games:
            logger.info("No pending games needing outcome checks.")
            print("OUTCOMES_UPDATED=0")
            return 0

        logger.info(f"Checking {len(pending_games)} pending games across dates...")

        # 1. High-Speed Batch Schedule Lookup (1 call covers entire weeks of games)
        dates_to_query = sorted(list(set(p.get('date') for p in pending_games if p.get('date'))))
        schedule_games_map = {}
        
        from concurrent.futures import ThreadPoolExecutor
        
        def fetch_date_schedule(dt):
            try:
                url = f"https://api-web.nhle.com/v1/schedule/{dt}"
                resp = client.session.get(url, timeout=6)
                if resp.status_code == 200:
                    d = resp.json()
                    return [g for day in d.get('gameWeek', []) for g in day.get('games', [])]
            except Exception as e:
                logger.debug(f"Error fetching batch schedule for {dt}: {e}")
            return []

        with ThreadPoolExecutor(max_workers=min(8, len(dates_to_query) or 1)) as executor:
            schedule_results = executor.map(fetch_date_schedule, dates_to_query)
            for g_list in schedule_results:
                for g in g_list:
                    if g.get('id'):
                        schedule_games_map[str(g['id'])] = g

        # 2. Parallel Processing of Completed Games
        def process_completed_game(pred):
            game_id = str(pred.get('game_id'))
            game_date = pred.get('date')
            sched_info = schedule_games_map.get(game_id)
            
            # Fast check from schedule payload
            game_state = sched_info.get('gameState', 'Unknown') if sched_info else 'Unknown'
            away_score = sched_info.get('awayTeam', {}).get('score') if sched_info else None
            home_score = sched_info.get('homeTeam', {}).get('score') if sched_info else None
            
            is_complete = game_state in ['FINAL', 'OFF', 'OFFICIAL'] or (game_date < today and away_score is not None and home_score is not None)
            
            if not is_complete:
                return None

            try:
                game_data = client.get_comprehensive_game_data(game_id)
                if not game_data:
                    return None
                    
                boxscore = game_data.get('boxscore', {})
                if not boxscore:
                    return None
                    
                away_score = boxscore.get('awayTeam', {}).get('score', away_score)
                home_score = boxscore.get('homeTeam', {}).get('score', home_score)
                
                if away_score is None or home_score is None:
                    return None

                actual_winner = pred.get('away_team') if away_score > home_score else (pred.get('home_team') if home_score > away_score else 'TIE')
                
                full_metrics = {}
                try:
                    home_team_box = boxscore.get('homeTeam', {})
                    away_team_box = boxscore.get('awayTeam', {})
                    full_metrics['home_goals'] = home_score
                    full_metrics['away_goals'] = away_score
                    full_metrics['home_shots'] = home_team_box.get('sog', 0)
                    full_metrics['away_shots'] = away_team_box.get('sog', 0)
                    
                    if 'play_by_play' in game_data:
                        from analyzers.advanced_metrics_analyzer import AdvancedMetricsAnalyzer
                        analyzer = AdvancedMetricsAnalyzer(game_data['play_by_play'])
                        h_id = home_team_box.get('id')
                        a_id = away_team_box.get('id')
                        report = analyzer.generate_comprehensive_report(a_id, h_id)
                        h_rep = report.get('home_team', {})
                        a_rep = report.get('away_team', {})
                        
                        full_metrics['home_xg'] = h_rep.get('expected_goals', home_score)
                        full_metrics['away_xg'] = a_rep.get('expected_goals', away_score)
                        full_metrics['home_corsi_pct'] = h_rep.get('possession', {}).get('corsi_pct', 50.0)
                        full_metrics['away_corsi_pct'] = a_rep.get('possession', {}).get('corsi_pct', 50.0)
                        full_metrics['home_hdsv_pct'] = h_rep.get('goaltending', {}).get('high_danger_save_pct', 0.8)
                        full_metrics['away_hdsv_pct'] = a_rep.get('goaltending', {}).get('high_danger_save_pct', 0.8)
                        full_metrics['home_pressure'] = h_rep.get('offensive_pressure', {}).get('pressure_score', 2.0)
                        full_metrics['away_pressure'] = a_rep.get('offensive_pressure', {}).get('pressure_score', 2.0)
                        
                        mom = analyzer.calculate_momentum_metrics(a_id, h_id)
                        full_metrics['p1_xg_home'] = mom.get('p1_xg', {}).get('home', 0.8)
                        full_metrics['p1_xg_away'] = mom.get('p1_xg', {}).get('away', 0.8)
                        full_metrics['p2_xg_home'] = mom.get('p2_xg', {}).get('home', 0.8)
                        full_metrics['p2_xg_away'] = mom.get('p2_xg', {}).get('away', 0.8)
                        full_metrics['p3_xg_home'] = mom.get('p3_xg', {}).get('home', 0.8)
                        full_metrics['p3_xg_away'] = mom.get('p3_xg', {}).get('away', 0.8)
                        full_metrics['lead_after_p2'] = mom.get('lead_after_p2', 0)
                except Exception as e:
                    logger.debug(f"Metrics extraction note: {e}")

                lead_after_p1 = 0
                try:
                    landing_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/landing"
                    landing_resp = client.session.get(landing_url, timeout=6)
                    if landing_resp.status_code == 200:
                        landing_data = landing_resp.json()
                        p1_away = 0
                        p1_home = 0
                        away_abbr = pred.get('away_team')
                        home_abbr = pred.get('home_team')
                        scoring = landing_data.get('summary', {}).get('scoring', [])
                        for period_data in scoring:
                            if period_data.get('periodDescriptor', {}).get('number') == 1:
                                for goal in period_data.get('goals', []):
                                    goal_team = goal.get('teamAbbrev', {}).get('default')
                                    if goal_team == away_abbr: p1_away += 1
                                    elif goal_team == home_abbr: p1_home += 1
                        if p1_home > p1_away: lead_after_p1 = 1
                        elif p1_away > p1_home: lead_after_p1 = -1
                except Exception:
                    pass

                return {
                    'game_id': game_id,
                    'game_date': game_date,
                    'away_team': pred.get('away_team'),
                    'home_team': pred.get('home_team'),
                    'away_score': away_score,
                    'home_score': home_score,
                    'actual_winner': actual_winner,
                    'lead_after_p1': lead_after_p1,
                    'full_metrics': full_metrics
                }
            except Exception as e:
                logger.debug(f"Error processing outcome for game {game_id}: {e}")
                return None

        with ThreadPoolExecutor(max_workers=min(12, len(pending_games) or 1)) as executor:
            processed_results = list(executor.map(process_completed_game, pending_games))

        for res in processed_results:
            if not res:
                continue
            updated_count += 1
            logger.info(f"✅ Updated: {res['away_team']} {res['away_score']}-{res['home_score']} {res['home_team']} (Winner: {res['actual_winner']})")
            
            if append_outcome_event is not None:
                try:
                    append_outcome_event(
                        game_id=str(res['game_id']),
                        date=res['game_date'],
                        away_team=res['away_team'],
                        home_team=res['home_team'],
                        actual_away_score=int(res['away_score']) if res['away_score'] is not None else None,
                        actual_home_score=int(res['home_score']) if res['home_score'] is not None else None,
                        actual_winner=res['actual_winner'],
                        lead_after_p1=res['lead_after_p1'],
                        **res['full_metrics']
                    )
                except Exception as e:
                    logger.warning(f"Could not append outcome event: {e}")
            
        if updated_count > 0:
            # Regenerate derived JSON view for legacy readers/dashboard
            with timed("rebuild predictions JSON view"):
                try:
                    from utils.build_predictions_history_view import write_view
                    write_view()
                except Exception:
                    try:
                        from build_predictions_history_view import write_view
                        write_view()
                    except Exception as e:
                        logger.warning(f"Could not regenerate JSON history view: {e}")
        else:
            logger.info("No completed games found needing updates.")

        # Machine-readable output for CI/workflows
        print(f"OUTCOMES_UPDATED={updated_count}")
        return int(updated_count)

if __name__ == "__main__":
    # Always exit 0 so the workflow can decide whether to retrain.
    update_game_outcomes()
