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
from pathlib import Path
from datetime import datetime
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

        for pred in predictions:
            # Skip if already has an outcome (checking actual_winner explicitly)
            if pred.get('actual_winner'):
                continue
            
            game_date = pred.get('date')
            game_id = pred.get('game_id')

            if not game_date or not game_id:
                continue

            # Only check if game date is in the past or today
            if game_date > today:
                continue

            logger.info(
                f"Checking status for game {game_id} ({pred.get('away_team')} @ {pred.get('home_team')}) on {game_date}..."
            )

            try:
                # We can use the cached schedule fetching from client if available,
                # or just fetch the game data directly since we have the ID
                game_data = client.get_comprehensive_game_data(str(game_id))

                if not game_data:
                    logger.warning(f"Could not fetch data for game {game_id}")
                    continue

                game_state = 'Unknown'

                # Check game state from various possible locations in response
                if 'game_center' in game_data and game_data['game_center']:
                    game_state = game_data['game_center'].get('gameState', 'Unknown')
                elif 'boxscore' in game_data and game_data['boxscore']:
                    # Boxscore often doesn't have explicit state, but if it has scores and periods, it might be done
                    # Usually we rely on game_center for state
                    pass

                # If we used the schedule endpoint (not used here directly), we'd have explicit state
                # Let's try to determine winner from scores if available
                boxscore = game_data.get('boxscore', {})

                if boxscore:
                    away_score = boxscore.get('awayTeam', {}).get('score')
                    home_score = boxscore.get('homeTeam', {}).get('score')

                    # Check if game is final (approximate check if state missing)
                    is_complete = False
                    if game_state in ['FINAL', 'OFF', 'OFFICIAL']:
                        is_complete = True
                    elif game_date < today and away_score is not None and home_score is not None:
                        # If it's a past date and we have scores, assume complete
                        is_complete = True

                    if is_complete and away_score is not None and home_score is not None:
                        actual_winner = None
                        if away_score > home_score:
                            actual_winner = pred.get('away_team')  # Use tracked abbrev to match
                        elif home_score > away_score:
                            actual_winner = pred.get('home_team')
                        else:
                            actual_winner = 'TIE'  # Rare/Impossible in regular season usually

                        # NEW: Track Period 1 Leader (Phase 20)
                        lead_after_p1 = 0  # 0=Tie, 1=Home, -1=Away
                        try:
                            # Landing endpoint has period-by-period scoring summary
                            landing_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/landing"
                            landing_resp = client.session.get(landing_url, timeout=10)
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
                                            if goal_team == away_abbr:
                                                p1_away += 1
                                            elif goal_team == home_abbr:
                                                p1_home += 1

                                if p1_home > p1_away:
                                    lead_after_p1 = 1
                                elif p1_away > p1_home:
                                    lead_after_p1 = -1

                                # Store lead_after_p1 in metrics_used for training parity
                                if 'metrics_used' not in pred:
                                    pred['metrics_used'] = {}
                                pred['metrics_used']['lead_after_p1'] = lead_after_p1
                                logger.info(
                                    f"   P1 Score: {away_abbr} {p1_away} - {p1_home} {home_abbr} (Lead: {lead_after_p1})"
                                )
                        except Exception as e:
                            logger.warning(f"   Could not determine P1 lead for {game_id}: {e}")

                        updated_count += 1
                        logger.info(
                            f"✅ Updated: {pred['away_team']} {away_score}-{home_score} {pred['home_team']} (Winner: {actual_winner})"
                        )

                        # Append outcome event for deterministic retraining (append-only).
                        if append_outcome_event is not None:
                            try:
                                append_outcome_event(
                                    game_id=str(game_id),
                                    date=game_date,
                                    away_team=pred.get("away_team"),
                                    home_team=pred.get("home_team"),
                                    actual_away_score=int(away_score) if away_score is not None else None,
                                    actual_home_score=int(home_score) if home_score is not None else None,
                                    actual_winner=actual_winner,
                                    lead_after_p1=lead_after_p1,
                                )
                            except Exception as e:
                                logger.warning(f"Could not append outcome event: {e}")

            except Exception as e:
                logger.error(f"Error checking game {game_id}: {e}")
                continue
            
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
