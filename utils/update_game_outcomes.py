#!/usr/bin/env python3
"""
Update Game Outcomes
-------------------
Checks past predictions missing actual_winner and fills them from the NHL API.
Optimized for CI: schedule prefilter → parallel comprehensive fetches (cached) →
metrics extraction without duplicate landing calls.
"""

import json
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None

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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _today_ct() -> str:
    if ZoneInfo is not None:
        return datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d")
    return datetime.now().strftime("%Y-%m-%d")


def _lead_after_p1_from_landing(landing, away_abbr, home_abbr) -> int:
    if not landing:
        return 0
    try:
        p1_away = p1_home = 0
        scoring = (landing.get("summary") or {}).get("scoring") or []
        for period_data in scoring:
            if (period_data.get("periodDescriptor") or {}).get("number") != 1:
                continue
            for goal in period_data.get("goals") or []:
                goal_team = (goal.get("teamAbbrev") or {}).get("default")
                if goal_team == away_abbr:
                    p1_away += 1
                elif goal_team == home_abbr:
                    p1_home += 1
        if p1_home > p1_away:
            return 1
        if p1_away > p1_home:
            return -1
    except Exception:
        return 0
    return 0


try:
    from utils.game_id_resolve import is_valid_nhl_game_id as _valid_nhl_game_id
    from utils.game_id_resolve import resolve_game_id, prefetch_schedules
except Exception:
    from game_id_resolve import is_valid_nhl_game_id as _valid_nhl_game_id
    from game_id_resolve import resolve_game_id, prefetch_schedules


def _sync_outcomes_from_prediction_records(preds_by_gid, outs_by_gid) -> int:
    """Backfill outcome events when prediction rows already have winners.

    Historically ~900+ games had actual_winner on the prediction record but
    never landed in outcome_events.jsonl, forcing daily re-scans.
    """
    if append_outcome_event is None:
        return 0
    synced = 0
    for gid, p in preds_by_gid.items():
        if outs_by_gid.get(gid, {}).get("actual_winner"):
            continue
        winner = p.get("actual_winner")
        if not winner:
            continue
        if not _valid_nhl_game_id(gid):
            continue
        try:
            append_outcome_event(
                game_id=str(gid),
                date=p.get("date"),
                away_team=p.get("away_team"),
                home_team=p.get("home_team"),
                actual_away_score=p.get("actual_away_score"),
                actual_home_score=p.get("actual_home_score"),
                actual_winner=winner,
                lead_after_p1=p.get("lead_after_p1"),
                synced_from_prediction=True,
            )
            outs_by_gid[str(gid)] = {"actual_winner": winner}
            synced += 1
        except Exception as e:
            logger.debug("Could not sync outcome for %s: %s", gid, e)
    if synced:
        logger.info("⚡ Synced %s outcome events from prediction records (no API)", synced)
    return synced


def update_game_outcomes():
    """Update valid predictions with actual game outcomes"""
    with timed("update_game_outcomes total"):
        try:
            from utils.event_store import load_latest_by_game_id, PREDICTION_EVENTS_PATH, OUTCOME_EVENTS_PATH
        except Exception:
            load_latest_by_game_id = None
            PREDICTION_EVENTS_PATH = None
            OUTCOME_EVENTS_PATH = None

        predictions = []
        synced_count = 0
        if load_latest_by_game_id is not None and PREDICTION_EVENTS_PATH is not None:
            preds_by_gid = load_latest_by_game_id(PREDICTION_EVENTS_PATH)
            outs_by_gid = (
                load_latest_by_game_id(OUTCOME_EVENTS_PATH) if OUTCOME_EVENTS_PATH is not None else {}
            )
            synced_count = _sync_outcomes_from_prediction_records(preds_by_gid, outs_by_gid)
            for gid, p in preds_by_gid.items():
                if outs_by_gid.get(gid, {}).get("actual_winner"):
                    continue
                if p.get("actual_winner"):
                    continue
                predictions.append(p)
            logger.info("Checking for game updates via events log (%s truly pending)...", len(predictions))
        else:
            predictions_file = Path("data/win_probability_predictions_v2.json")
            if not predictions_file.exists():
                predictions_file = Path("win_probability_predictions_v2.json")
            if not predictions_file.exists():
                logger.error("Predictions file not found (events log missing too)")
                print("OUTCOMES_UPDATED=0")
                return 0
            logger.info("Checking for game updates in %s...", predictions_file)
            with open(predictions_file, "r") as f:
                data = json.load(f)
            predictions = data.get("predictions", [])

        # synced_count is local backfill only — must NOT trigger model retrain in CI.
        api_updated_count = 0
        client = NHLAPIClient(timeout=8, pool_size=32)
        today = _today_ct()
        skip_path = Path("data/outcome_skip_game_ids.json")
        skip_ids = set()
        if skip_path.exists():
            try:
                skip_ids = set(json.loads(skip_path.read_text()).get("game_ids") or [])
            except Exception:
                skip_ids = set()

        # Resolve synthetic matchup keys → official NHL ids before fetching.
        sched_cache = prefetch_schedules(
            [p.get("date") for p in predictions if p.get("date") and not p.get("actual_winner")]
        )
        pending_games = []
        for pred in predictions:
            if pred.get("actual_winner"):
                continue
            g_date = pred.get("date")
            g_id = pred.get("game_id")
            if not g_date or not g_id or g_date > today:
                continue
            if str(g_id) in skip_ids and _valid_nhl_game_id(g_id):
                continue
            if not _valid_nhl_game_id(g_id):
                resolved = resolve_game_id(
                    game_id=g_id,
                    away_team=pred.get("away_team"),
                    home_team=pred.get("home_team"),
                    date=g_date,
                    schedule_cache=sched_cache,
                    session=client.session,
                )
                if not resolved:
                    continue
                pred = dict(pred)
                pred["game_id"] = resolved
                g_id = resolved
            pending_games.append(pred)

        if not pending_games:
            logger.info("No pending games needing outcome checks.")
            print("OUTCOMES_UPDATED=0")
            return 0

        logger.info("Checking %s pending games across dates...", len(pending_games))

        dates_to_query = sorted({p.get("date") for p in pending_games if p.get("date")})
        schedule_games_map = {}

        def fetch_date_schedule(dt):
            try:
                url = f"https://api-web.nhle.com/v1/schedule/{dt}"
                resp = client.session.get(url, timeout=6)
                if resp.status_code == 200:
                    d = resp.json()
                    return [g for day in d.get("gameWeek", []) for g in day.get("games", [])]
            except Exception as e:
                logger.debug("Error fetching batch schedule for %s: %s", dt, e)
            return []

        with ThreadPoolExecutor(max_workers=min(12, len(dates_to_query) or 1)) as executor:
            for g_list in executor.map(fetch_date_schedule, dates_to_query):
                for g in g_list:
                    if g.get("id"):
                        schedule_games_map[str(g["id"])] = g

        # Only spend API budget on games the schedule says are done.
        completed_pending = []
        abandoned = 0
        for pred in pending_games:
            game_id = str(pred.get("game_id"))
            game_date = pred.get("date")
            sched_info = schedule_games_map.get(game_id)
            game_state = (sched_info or {}).get("gameState", "Unknown")
            away_score = ((sched_info or {}).get("awayTeam") or {}).get("score")
            home_score = ((sched_info or {}).get("homeTeam") or {}).get("score")
            is_complete = game_state in ("FINAL", "OFF", "OFFICIAL") or (
                game_date < today and away_score is not None and home_score is not None
            )
            if is_complete:
                completed_pending.append(pred)
                continue
            # Only abandon IDs that are invalid forever (not found on that date's slate).
            if game_date and game_date < today and sched_info is None:
                skip_ids.add(game_id)
                abandoned += 1
        if abandoned:
            logger.info("⚡ Abandoned %s IDs with no schedule row on their date", abandoned)

        # Persist skip list for permanently unresolvable / abandoned IDs.
        if skip_ids:
            try:
                skip_path.parent.mkdir(parents=True, exist_ok=True)
                skip_path.write_text(json.dumps({"game_ids": sorted(skip_ids)}, indent=2))
            except Exception:
                pass

        if not completed_pending:
            if synced_count > 0:
                with timed("rebuild predictions JSON view after sync"):
                    try:
                        from utils.build_predictions_history_view import write_view
                        write_view()
                    except Exception:
                        try:
                            from build_predictions_history_view import write_view
                            write_view()
                        except Exception as e:
                            logger.warning("Could not regenerate JSON history view: %s", e)
            else:
                logger.info("No completed games found needing updates.")
            # Retrain trigger uses API updates only.
            print(f"OUTCOMES_SYNCED={synced_count}")
            print(f"OUTCOMES_UPDATED={api_updated_count}")
            return int(api_updated_count)

        logger.info("Fetching details for %s completed games...", len(completed_pending))
        # Warm shared disk/memory cache in one parallel wave.
        client.prefetch_games([p.get("game_id") for p in completed_pending], max_workers=16)

        def process_completed_game(pred):
            game_id = str(pred.get("game_id"))
            game_date = pred.get("date")
            try:
                game_data = client.get_comprehensive_game_data(
                    game_id, include_right_rail=False, use_cache=True
                )
                if not game_data:
                    return None

                boxscore = game_data.get("boxscore") or {}
                away_score = (boxscore.get("awayTeam") or {}).get("score")
                home_score = (boxscore.get("homeTeam") or {}).get("score")
                if away_score is None or home_score is None:
                    sched = schedule_games_map.get(game_id) or {}
                    away_score = (sched.get("awayTeam") or {}).get("score")
                    home_score = (sched.get("homeTeam") or {}).get("score")
                if away_score is None or home_score is None:
                    return None

                actual_winner = (
                    pred.get("away_team")
                    if away_score > home_score
                    else (pred.get("home_team") if home_score > away_score else "TIE")
                )

                full_metrics = {
                    "home_goals": home_score,
                    "away_goals": away_score,
                    "home_shots": (boxscore.get("homeTeam") or {}).get("sog", 0),
                    "away_shots": (boxscore.get("awayTeam") or {}).get("sog", 0),
                }

                pbp = game_data.get("play_by_play")
                if pbp:
                    try:
                        from analyzers.advanced_metrics_analyzer import AdvancedMetricsAnalyzer

                        analyzer = AdvancedMetricsAnalyzer(pbp)
                        h_id = (boxscore.get("homeTeam") or {}).get("id")
                        a_id = (boxscore.get("awayTeam") or {}).get("id")
                        report = analyzer.generate_comprehensive_report(a_id, h_id)
                        h_rep = report.get("home_team", {})
                        a_rep = report.get("away_team", {})
                        full_metrics["home_xg"] = h_rep.get("expected_goals", home_score)
                        full_metrics["away_xg"] = a_rep.get("expected_goals", away_score)
                        full_metrics["home_corsi_pct"] = h_rep.get("possession", {}).get("corsi_pct", 50.0)
                        full_metrics["away_corsi_pct"] = a_rep.get("possession", {}).get("corsi_pct", 50.0)
                        full_metrics["home_hdsv_pct"] = h_rep.get("goaltending", {}).get(
                            "high_danger_save_pct", 0.8
                        )
                        full_metrics["away_hdsv_pct"] = a_rep.get("goaltending", {}).get(
                            "high_danger_save_pct", 0.8
                        )
                        full_metrics["home_pressure"] = h_rep.get("offensive_pressure", {}).get(
                            "pressure_score", 2.0
                        )
                        full_metrics["away_pressure"] = a_rep.get("offensive_pressure", {}).get(
                            "pressure_score", 2.0
                        )
                        mom = analyzer.calculate_momentum_metrics(a_id, h_id)
                        full_metrics["p1_xg_home"] = mom.get("p1_xg", {}).get("home", 0.8)
                        full_metrics["p1_xg_away"] = mom.get("p1_xg", {}).get("away", 0.8)
                        full_metrics["p2_xg_home"] = mom.get("p2_xg", {}).get("home", 0.8)
                        full_metrics["p2_xg_away"] = mom.get("p2_xg", {}).get("away", 0.8)
                        full_metrics["p3_xg_home"] = mom.get("p3_xg", {}).get("home", 0.8)
                        full_metrics["p3_xg_away"] = mom.get("p3_xg", {}).get("away", 0.8)
                        full_metrics["lead_after_p2"] = mom.get("lead_after_p2", 0)
                    except Exception as e:
                        logger.debug("Metrics extraction note: %s", e)

                lead_after_p1 = _lead_after_p1_from_landing(
                    game_data.get("landing"), pred.get("away_team"), pred.get("home_team")
                )

                return {
                    "game_id": game_id,
                    "game_date": game_date,
                    "away_team": pred.get("away_team"),
                    "home_team": pred.get("home_team"),
                    "away_score": away_score,
                    "home_score": home_score,
                    "actual_winner": actual_winner,
                    "lead_after_p1": lead_after_p1,
                    "full_metrics": full_metrics,
                }
            except Exception as e:
                logger.debug("Error processing outcome for game %s: %s", game_id, e)
                return None

        with ThreadPoolExecutor(max_workers=min(16, len(completed_pending) or 1)) as executor:
            processed_results = list(executor.map(process_completed_game, completed_pending))

        for res in processed_results:
            if not res:
                continue
            api_updated_count += 1
            logger.info(
                "✅ Updated: %s %s-%s %s (Winner: %s)",
                res["away_team"],
                res["away_score"],
                res["home_score"],
                res["home_team"],
                res["actual_winner"],
            )
            if append_outcome_event is not None:
                try:
                    append_outcome_event(
                        game_id=str(res["game_id"]),
                        date=res["game_date"],
                        away_team=res["away_team"],
                        home_team=res["home_team"],
                        actual_away_score=int(res["away_score"]) if res["away_score"] is not None else None,
                        actual_home_score=int(res["home_score"]) if res["home_score"] is not None else None,
                        actual_winner=res["actual_winner"],
                        lead_after_p1=res["lead_after_p1"],
                        **res["full_metrics"],
                    )
                except Exception as e:
                    logger.warning("Could not append outcome event: %s", e)

        if api_updated_count > 0 or synced_count > 0:
            with timed("rebuild predictions JSON view"):
                try:
                    from utils.build_predictions_history_view import write_view

                    write_view()
                except Exception:
                    try:
                        from build_predictions_history_view import write_view

                        write_view()
                    except Exception as e:
                        logger.warning("Could not regenerate JSON history view: %s", e)
        else:
            logger.info("No completed games found needing updates.")

        print(f"OUTCOMES_SYNCED={synced_count}")
        print(f"OUTCOMES_UPDATED={api_updated_count}")
        return int(api_updated_count)


if __name__ == "__main__":
    update_game_outcomes()
