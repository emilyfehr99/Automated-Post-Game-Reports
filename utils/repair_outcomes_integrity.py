#!/usr/bin/env python3
"""
Full integrity repair for prediction/outcome history.

Fixes:
- actual_winner stored as "home"/"away" → team abbrev
- synthetic IDs (AWAY@HOME_YYYY-MM-DD) → official NHL game IDs
- wrong-season numeric IDs (e.g. 202502… for 2026-10 games)
- score / winner mismatches vs NHL schedule/boxscore
- missing lead_after_p1, shots, goalie IDs on completed games
- duplicate matchup rows (keeps official id; mirrors outcome onto stale ids)

Rebuilds data/win_probability_predictions_v2.json at the end.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
for _d in ("utils", "models", "analyzers", "scrapers"):
    _p = str(_ROOT / _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None

from utils.event_store import (
    OUTCOME_EVENTS_PATH,
    PREDICTION_EVENTS_PATH,
    append_outcome_event,
    append_prediction_event,
    load_latest_by_game_id,
)
from utils.game_id_resolve import (
    is_valid_nhl_game_id,
    prefetch_schedules,
    resolve_game_id,
)
from utils.nhl_api_client import NHLAPIClient
from utils.update_game_outcomes import _lead_after_p1_from_landing


SKIP_PATH = Path("data/outcome_skip_game_ids.json")


def _today_ct() -> str:
    if ZoneInfo is not None:
        return datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d")
    return datetime.now().strftime("%Y-%m-%d")


def normalize_winner(
    winner: Any,
    away_team: Optional[str],
    home_team: Optional[str],
    away_score: Any = None,
    home_score: Any = None,
) -> Optional[str]:
    if winner is None:
        return None
    w = str(winner).strip()
    if not w:
        return None
    low = w.lower()
    away = (away_team or "").upper() or None
    home = (home_team or "").upper() or None
    if low == "home" and home:
        return home
    if low == "away" and away:
        return away
    if w.upper() in {away, home, "TIE"}:
        return w.upper() if w.upper() != "TIE" else "TIE"
    # Prefer score-derived winner when label is garbage
    try:
        if away_score is not None and home_score is not None and away and home:
            a, h = int(away_score), int(home_score)
            if a > h:
                return away
            if h > a:
                return home
            return "TIE"
    except Exception:
        pass
    return w


def _winner_from_scores(away: str, home: str, away_score: int, home_score: int) -> str:
    if away_score > home_score:
        return away
    if home_score > away_score:
        return home
    return "TIE"


def _goalie_id_from_box(box: dict, side: str) -> Optional[str]:
    """Best-effort starting/primary goalie playerId from boxscore."""
    try:
        team = (box.get(side) or {})
        gid = team.get("goalieInNetId") or team.get("goalieId")
        if gid:
            return str(gid)
        pbg = ((box.get("playerByGameStats") or {}).get(side) or {}).get("goalies") or []
        if not pbg:
            return None
        # Prefer goalie with most TOI / shots against
        def _key(g):
            toi = str(g.get("toi") or "0:00")
            try:
                m, s = toi.split(":")
                seconds = int(m) * 60 + int(s)
            except Exception:
                seconds = 0
            return (seconds, int(g.get("shotsAgainst") or 0), int(g.get("saves") or 0))

        best = max(pbg, key=_key)
        pid = best.get("playerId") or best.get("id")
        return str(pid) if pid else None
    except Exception:
        return None


def _needs_outcome_refresh(o: Dict[str, Any], today: str) -> bool:
    if not o:
        return True
    date = o.get("date") or ""
    if date >= today:
        return False
    winner = str(o.get("actual_winner") or "")
    if winner.lower() in ("home", "away", ""):
        return True
    if o.get("actual_away_score") is None or o.get("actual_home_score") is None:
        return True
    if o.get("lead_after_p1") is None:
        return True
    if o.get("home_shots") is None or o.get("away_shots") is None:
        return True
    if not o.get("home_goalie") or not o.get("away_goalie"):
        return True
    if str(o.get("home_goalie")) in ("Unknown", "None", "0") or str(o.get("away_goalie")) in (
        "Unknown",
        "None",
        "0",
    ):
        return True
    return False


def _boxscore_identity(client: NHLAPIClient, game_id: str) -> Optional[Dict[str, Any]]:
    """Return canonical date/teams/scores from NHL boxscore, or None."""
    try:
        data = client.get_comprehensive_game_data(game_id, include_right_rail=False, use_cache=True)
    except Exception:
        return None
    box = (data or {}).get("boxscore") or {}
    away = ((box.get("awayTeam") or {}).get("abbrev") or "").upper()
    home = ((box.get("homeTeam") or {}).get("abbrev") or "").upper()
    if not away or not home:
        return None
    away_score = (box.get("awayTeam") or {}).get("score")
    home_score = (box.get("homeTeam") or {}).get("score")
    date = (box.get("gameDate") or "")[:10] or None
    if not date:
        # fallback from startTimeUTC
        stu = box.get("startTimeUTC") or ""
        date = stu[:10] if stu else None
    return {
        "date": date,
        "away_team": away,
        "home_team": home,
        "away_score": away_score,
        "home_score": home_score,
        "game_state": box.get("gameState"),
        "box": box,
        "landing": (data or {}).get("landing") or {},
        "data": data,
    }


def repair_outcomes_integrity(*, max_workers: int = 16) -> Dict[str, int]:
    today = _today_ct()
    client = NHLAPIClient(timeout=8, pool_size=32)
    preds = load_latest_by_game_id(PREDICTION_EVENTS_PATH)
    outs = load_latest_by_game_id(OUTCOME_EVENTS_PATH)

    stats = {
        "ids_rewritten": 0,
        "winners_normalized": 0,
        "outcomes_refreshed": 0,
        "outcomes_mirrored": 0,
        "score_mismatches_fixed": 0,
        "still_past_missing": 0,
        "live_or_future": 0,
        "unresolved": 0,
    }

    # --- 1) Resolve every prediction to an official id ---
    dates = [p.get("date") for p in preds.values() if p.get("date")]
    # Also include nearby days for wrong-date rows
    print(f"🗺️  Prefetching schedules for {len(set(dates))} dates...")
    schedule_cache = prefetch_schedules(dates)

    resolved_map: Dict[str, str] = {}  # old_gid -> official
    unresolved: List[str] = []
    for gid, p in preds.items():
        rid = resolve_game_id(
            game_id=gid,
            away_team=p.get("away_team"),
            home_team=p.get("home_team"),
            date=p.get("date"),
            schedule_cache=schedule_cache,
            session=client.session,
            verify_matchup=True,
        )
        if rid:
            resolved_map[str(gid)] = str(rid)
        else:
            unresolved.append(str(gid))
    stats["unresolved"] = len(unresolved)
    print(f"✅ Resolved {len(resolved_map)} / {len(preds)} prediction IDs")
    if unresolved:
        print(f"⚠️  Unresolved: {len(unresolved)}")
        for u in unresolved[:15]:
            p = preds[u]
            print(f"   • {p.get('date')} {p.get('away_team')}@{p.get('home_team')} id={u}")

    # --- 2) Rewrite predictions under official IDs when stale/synthetic/wrong ---
    for old, rid in resolved_map.items():
        if old == rid and is_valid_nhl_game_id(old):
            continue
        src = preds.get(old) or {}
        # Prefer existing official prediction if richer
        existing = preds.get(rid) or {}
        if existing.get("predicted_winner") or existing.get("predicted_home_win_prob") is not None:
            # Still ensure we have a pointer rewrite for audit, but skip duplicate payload
            if not existing.get("away_team"):
                pass
            else:
                continue
        event = {
            "date": src.get("date"),
            "game_id": int(rid) if str(rid).isdigit() else rid,
            "home_team": src.get("home_team"),
            "away_team": src.get("away_team"),
            "predicted_winner": src.get("predicted_winner"),
            "predicted_home_win_prob": src.get("predicted_home_win_prob") or src.get("home_win_prob"),
            "predicted_away_win_prob": src.get("predicted_away_win_prob") or src.get("away_win_prob"),
            "model_confidence": src.get("model_confidence"),
            "metrics_used": src.get("metrics_used") or {},
            "extra_metadata": {
                "rewritten_from_game_id": old,
                "integrity_repair": True,
            },
        }
        # Carry score predictions if present
        for k in (
            "predicted_home_goals",
            "predicted_away_goals",
            "predicted_total_goals",
            "home_win_prob",
            "away_win_prob",
            "prediction_reason",
            "suggested_units",
            "odds_taken",
            "away_back_to_back",
            "home_back_to_back",
            "away_rest_value",
            "home_rest_value",
            "ensemble_mode",
            "ensemble_weights",
        ):
            if src.get(k) is not None:
                event[k] = src.get(k)
        append_prediction_event(event)
        preds[rid] = event
        stats["ids_rewritten"] += 1
    print(f"📝 Prediction IDs rewritten: {stats['ids_rewritten']}")

    # --- 2b) Verify suspicious numeric IDs against NHL boxscore ---
    # Full scan only when not FAST_CI; in CI, check ids that fail schedule matchup
    # or have season-prefix/date disagreement.
    stats["matchup_corrections"] = 0
    import os

    fast = os.environ.get("FAST_CI", "").lower() in ("1", "true", "yes")
    numeric_ids = []
    for gid, p in preds.items():
        if not is_valid_nhl_game_id(gid):
            continue
        date = p.get("date") or ""
        if date > today:
            continue
        if not fast:
            numeric_ids.append(str(gid))
            continue
        day_games = schedule_cache.get(date) or []
        on_slate = any(str(g.get("id")) == str(gid) for g in day_games)
        try:
            season_prefix = int(str(gid)[:4])
            year = int(date[:4])
            month = int(date[5:7])
            expected_season = year if month >= 8 else year - 1
            season_mismatch = season_prefix != expected_season and str(gid)[4:6] not in ("03", "04")
        except Exception:
            season_mismatch = False
        if (not on_slate) or season_mismatch:
            numeric_ids.append(str(gid))
    print(f"🔎 Verifying {len(numeric_ids)} numeric IDs against NHL boxscores (fast={fast})...")
    client.prefetch_games(numeric_ids, max_workers=max_workers)
    for gid in numeric_ids:
        p = preds.get(gid) or {}
        ident = _boxscore_identity(client, gid)
        if not ident or not ident.get("away_team"):
            continue
        wrong_teams = (
            (p.get("away_team") or "").upper() != ident["away_team"]
            or (p.get("home_team") or "").upper() != ident["home_team"]
        )
        wrong_date = bool(ident.get("date") and p.get("date") and p.get("date") != ident["date"])
        if not (wrong_teams or wrong_date):
            continue
        ph = p.get("predicted_home_win_prob")
        pa = p.get("predicted_away_win_prob")
        pred_winner = p.get("predicted_winner")
        if wrong_teams and ph is not None and pa is not None:
            pred_winner = (
                ident["home_team"] if float(ph) >= float(pa) else ident["away_team"]
            )
        event = {
            "date": ident.get("date") or p.get("date"),
            "game_id": int(gid) if str(gid).isdigit() else gid,
            "away_team": ident["away_team"],
            "home_team": ident["home_team"],
            "predicted_winner": pred_winner,
            "predicted_home_win_prob": ph,
            "predicted_away_win_prob": pa,
            "model_confidence": p.get("model_confidence"),
            "metrics_used": p.get("metrics_used") or {},
            "extra_metadata": {
                "integrity_repair": True,
                "corrected_matchup_from": f"{p.get('away_team')}@{p.get('home_team')}_{p.get('date')}",
            },
        }
        append_prediction_event(event)
        preds[gid] = event
        resolved_map[gid] = gid
        stats["matchup_corrections"] += 1
    print(f"🩹 Matchup/date corrections from boxscore: {stats['matchup_corrections']}")

    # --- 3) Quick normalize winners that only need label fix (no API) ---
    for gid, o in list(outs.items()):
        nw = normalize_winner(
            o.get("actual_winner"),
            o.get("away_team"),
            o.get("home_team"),
            o.get("actual_away_score"),
            o.get("actual_home_score"),
        )
        if nw and nw != o.get("actual_winner"):
            append_outcome_event(
                game_id=str(gid),
                date=o.get("date"),
                away_team=o.get("away_team"),
                home_team=o.get("home_team"),
                actual_away_score=o.get("actual_away_score"),
                actual_home_score=o.get("actual_home_score"),
                actual_winner=nw,
                lead_after_p1=o.get("lead_after_p1"),
                winner_normalized=True,
                **{
                    k: o.get(k)
                    for k in (
                        "home_goals",
                        "away_goals",
                        "home_shots",
                        "away_shots",
                        "home_xg",
                        "away_xg",
                        "home_goalie",
                        "away_goalie",
                    )
                    if o.get(k) is not None
                },
            )
            o["actual_winner"] = nw
            outs[str(gid)] = o
            stats["winners_normalized"] += 1
    print(f"🏷️  Winners normalized (home/away→team): {stats['winners_normalized']}")

    # --- 4) Build unique official games that need full refresh ---
    # Group by resolved official id
    by_official: Dict[str, Dict[str, Any]] = {}
    for old, rid in resolved_map.items():
        p = preds.get(old) or preds.get(rid) or {}
        date = p.get("date")
        if not date:
            continue
        entry = by_official.setdefault(
            rid,
            {
                "game_id": rid,
                "date": date,
                "away_team": p.get("away_team"),
                "home_team": p.get("home_team"),
                "aliases": set(),
            },
        )
        entry["aliases"].add(old)
        if old != rid:
            entry["aliases"].add(rid)

    need_fetch: List[Dict[str, Any]] = []
    for rid, meta in by_official.items():
        date = meta.get("date") or ""
        if date > today:
            continue
        # Live/future today: still rewrite IDs but don't invent outcomes
        o = outs.get(rid) or {}
        # Also check if any alias has outcome but official doesn't
        if not o.get("actual_winner"):
            for a in meta["aliases"]:
                if outs.get(a, {}).get("actual_winner"):
                    o = outs[a]
                    break

        # Schedule completeness
        day_games = schedule_cache.get(date) or []
        sched = next((g for g in day_games if str(g.get("id")) == rid), None)
        state = (sched or {}).get("gameState")
        away_score = ((sched or {}).get("awayTeam") or {}).get("score")
        home_score = ((sched or {}).get("homeTeam") or {}).get("score")
        is_complete = state in ("FINAL", "OFF", "OFFICIAL") or (
            date < today and away_score is not None and home_score is not None
        )
        if not is_complete:
            continue

        # Verify score consistency with schedule when we have an outcome
        score_mismatch = False
        if o.get("actual_winner") and away_score is not None and home_score is not None:
            try:
                if int(o.get("actual_away_score")) != int(away_score) or int(
                    o.get("actual_home_score")
                ) != int(home_score):
                    score_mismatch = True
            except Exception:
                score_mismatch = True

        if score_mismatch or _needs_outcome_refresh({**o, "date": date}, today):
            need_fetch.append({**meta, "sched": sched, "score_mismatch": score_mismatch})

    print(f"🌐 Refreshing {len(need_fetch)} completed games (scores/P1/goalies/metrics)...")
    client.prefetch_games([c["game_id"] for c in need_fetch], max_workers=max_workers)

    def _refresh_one(c: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        rid = c["game_id"]
        data = client.get_comprehensive_game_data(rid, include_right_rail=False, use_cache=True)
        box = (data or {}).get("boxscore") or {}
        landing = (data or {}).get("landing") or {}
        away = (c.get("away_team") or (box.get("awayTeam") or {}).get("abbrev") or "").upper()
        home = (c.get("home_team") or (box.get("homeTeam") or {}).get("abbrev") or "").upper()
        away_score = (box.get("awayTeam") or {}).get("score")
        home_score = (box.get("homeTeam") or {}).get("score")
        if away_score is None or home_score is None:
            sched = c.get("sched") or {}
            away_score = ((sched.get("awayTeam") or {}).get("score"))
            home_score = ((sched.get("homeTeam") or {}).get("score"))
        if away_score is None or home_score is None or not away or not home:
            return None
        away_score = int(away_score)
        home_score = int(home_score)
        winner = _winner_from_scores(away, home, away_score, home_score)
        lead = _lead_after_p1_from_landing(landing, away, home)
        home_goalie = _goalie_id_from_box(box, "homeTeam")
        away_goalie = _goalie_id_from_box(box, "awayTeam")
        metrics = {
            "home_goals": home_score,
            "away_goals": away_score,
            "home_shots": (box.get("homeTeam") or {}).get("sog"),
            "away_shots": (box.get("awayTeam") or {}).get("sog"),
            "home_goalie": home_goalie,
            "away_goalie": away_goalie,
        }
        # Optional advanced metrics from PBP
        pbp = (data or {}).get("play_by_play")
        if pbp:
            try:
                from analyzers.advanced_metrics_analyzer import AdvancedMetricsAnalyzer

                analyzer = AdvancedMetricsAnalyzer(pbp)
                h_id = (box.get("homeTeam") or {}).get("id")
                a_id = (box.get("awayTeam") or {}).get("id")
                report = analyzer.generate_comprehensive_report(a_id, h_id)
                h_rep = report.get("home_team", {})
                a_rep = report.get("away_team", {})
                metrics["home_xg"] = h_rep.get("expected_goals")
                metrics["away_xg"] = a_rep.get("expected_goals")
                metrics["home_corsi_pct"] = (h_rep.get("possession") or {}).get("corsi_pct")
                metrics["away_corsi_pct"] = (a_rep.get("possession") or {}).get("corsi_pct")
            except Exception:
                pass
        return {
            "game_id": rid,
            "date": c.get("date"),
            "away_team": away,
            "home_team": home,
            "away_score": away_score,
            "home_score": home_score,
            "actual_winner": winner,
            "lead_after_p1": lead,
            "metrics": metrics,
            "aliases": c.get("aliases") or {rid},
            "score_mismatch": c.get("score_mismatch"),
        }

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        results = list(ex.map(_refresh_one, need_fetch))

    for res in results:
        if not res:
            continue
        append_outcome_event(
            game_id=str(res["game_id"]),
            date=res["date"],
            away_team=res["away_team"],
            home_team=res["home_team"],
            actual_away_score=res["away_score"],
            actual_home_score=res["home_score"],
            actual_winner=res["actual_winner"],
            lead_after_p1=res["lead_after_p1"],
            integrity_repair=True,
            **{k: v for k, v in (res.get("metrics") or {}).items() if v is not None},
        )
        outs[str(res["game_id"])] = {
            "actual_winner": res["actual_winner"],
            "actual_away_score": res["away_score"],
            "actual_home_score": res["home_score"],
            "lead_after_p1": res["lead_after_p1"],
            "away_team": res["away_team"],
            "home_team": res["home_team"],
            "date": res["date"],
            **(res.get("metrics") or {}),
        }
        stats["outcomes_refreshed"] += 1
        if res.get("score_mismatch"):
            stats["score_mismatches_fixed"] += 1

        # Mirror onto stale aliases so no year shows missing under old keys
        for alias in res.get("aliases") or []:
            alias = str(alias)
            if alias == str(res["game_id"]):
                continue
            if outs.get(alias, {}).get("actual_winner") == res["actual_winner"] and outs.get(
                alias, {}
            ).get("actual_away_score") == res["away_score"]:
                # Still rewrite if winner was side-label or missing lead
                prev = outs.get(alias) or {}
                if (
                    str(prev.get("actual_winner") or "").lower() not in ("home", "away")
                    and prev.get("lead_after_p1") is not None
                    and prev.get("home_goalie")
                ):
                    continue
            append_outcome_event(
                game_id=alias,
                date=res["date"],
                away_team=res["away_team"],
                home_team=res["home_team"],
                actual_away_score=res["away_score"],
                actual_home_score=res["home_score"],
                actual_winner=res["actual_winner"],
                lead_after_p1=res["lead_after_p1"],
                mirrored_from_game_id=str(res["game_id"]),
                integrity_repair=True,
                **{k: v for k, v in (res.get("metrics") or {}).items() if v is not None},
            )
            outs[alias] = outs[str(res["game_id"])]
            stats["outcomes_mirrored"] += 1

    print(f"✅ Outcomes refreshed: {stats['outcomes_refreshed']}")
    print(f"🔗 Mirrored to aliases: {stats['outcomes_mirrored']}")
    print(f"🩺 Score mismatches fixed: {stats['score_mismatches_fixed']}")

    # --- 5) Clear skip list of fixed IDs ---
    if SKIP_PATH.exists():
        try:
            payload = json.loads(SKIP_PATH.read_text())
            old = set(payload.get("game_ids") or [])
            keep = set()
            for gid in old:
                if is_valid_nhl_game_id(gid) and not outs.get(str(gid), {}).get("actual_winner"):
                    keep.add(gid)
            SKIP_PATH.write_text(json.dumps({"game_ids": sorted(keep)}, indent=2))
            print(f"🧹 Skip list {len(old)} → {len(keep)}")
        except Exception as e:
            print(f"⚠️ Skip list cleanup: {e}")

    # --- 6) Rebuild hist view (deduped) ---
    try:
        from utils.build_predictions_history_view import write_view

        write_view()
        print("💾 Rebuilt data/win_probability_predictions_v2.json")
    except Exception as e:
        print(f"⚠️ Could not rebuild hist view: {e}")

    # --- 7) Final audit ---
    preds2 = load_latest_by_game_id(PREDICTION_EVENTS_PATH)
    outs2 = load_latest_by_game_id(OUTCOME_EVENTS_PATH)
    still_past = []
    live = []
    bad_winner = 0
    synth_past = 0
    for gid, p in preds2.items():
        date = p.get("date") or ""
        rid = resolve_game_id(
            game_id=gid,
            away_team=p.get("away_team"),
            home_team=p.get("home_team"),
            date=date,
            schedule_cache=schedule_cache,
            verify_matchup=True,
        )
        has = (
            outs2.get(str(gid), {}).get("actual_winner")
            or outs2.get(str(rid or ""), {}).get("actual_winner")
            or p.get("actual_winner")
        )
        if date >= today:
            if not has:
                live.append(p)
            continue
        if not has:
            still_past.append(p)
            continue
        # winner consistency on official rows
        o = outs2.get(str(rid or gid)) or outs2.get(str(gid)) or {}
        w = normalize_winner(
            o.get("actual_winner") or has,
            o.get("away_team") or p.get("away_team"),
            o.get("home_team") or p.get("home_team"),
            o.get("actual_away_score"),
            o.get("actual_home_score"),
        )
        try:
            aw, hw = int(o.get("actual_away_score")), int(o.get("actual_home_score"))
            expect = _winner_from_scores(
                (o.get("away_team") or p.get("away_team") or "").upper(),
                (o.get("home_team") or p.get("home_team") or "").upper(),
                aw,
                hw,
            )
            if w != expect:
                bad_winner += 1
        except Exception:
            pass
        if date < today and (not is_valid_nhl_game_id(gid) or (rid and str(gid) != str(rid))):
            # Count only if hist view would still show synthetic as primary — view dedupes now
            if not is_valid_nhl_game_id(gid):
                synth_past += 1

    stats["still_past_missing"] = len(still_past)
    stats["live_or_future"] = len(live)
    stats["bad_winner_remaining"] = bad_winner

    print("=" * 60)
    for k, v in stats.items():
        print(f"{k}: {v}")
    for p in still_past[:20]:
        print(f"   ❌ {p.get('date')} {p.get('away_team')}@{p.get('home_team')} id={p.get('game_id')}")

    return stats


if __name__ == "__main__":
    s = repair_outcomes_integrity()
    raise SystemExit(1 if s.get("still_past_missing", 0) or s.get("bad_winner_remaining", 0) else 0)
