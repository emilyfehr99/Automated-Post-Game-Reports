#!/usr/bin/env python3
"""
Backfill ALL missing game outcomes across every season in the repo.

- Resolves synthetic IDs like BOS@WPG_2026-10-02 → official NHL game IDs
- Fetches final scores / winners for every completed missing game
- Writes corrected prediction + outcome events
- Rebuilds win_probability_predictions_v2.json
- Clears skip-list entries that are now fixed

Does NOT invent outcomes for games that are still live / not played.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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


SKIP_PATH = Path("data/outcome_skip_game_ids.json")


def _today_ct() -> str:
    if ZoneInfo is not None:
        return datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d")
    return datetime.now().strftime("%Y-%m-%d")


def _winner(away: str, home: str, away_score: int, home_score: int) -> str:
    if away_score > home_score:
        return away
    if home_score > away_score:
        return home
    return "TIE"


def _collect_candidates() -> List[Dict[str, Any]]:
    preds = load_latest_by_game_id(PREDICTION_EVENTS_PATH)
    outs = load_latest_by_game_id(OUTCOME_EVENTS_PATH)
    hist_path = Path("data/win_probability_predictions_v2.json")
    hist = []
    if hist_path.exists():
        hist = json.loads(hist_path.read_text()).get("predictions") or []

    by_key: Dict[str, Dict[str, Any]] = {}

    def _add(p: Dict[str, Any], source: str):
        gid = p.get("game_id")
        away = p.get("away_team")
        home = p.get("home_team")
        date = p.get("date")
        key = f"{away}@{home}_{date}_{gid}"
        if key in by_key:
            return
        # Already has outcome in events under this or resolvable id?
        if outs.get(str(gid), {}).get("actual_winner") or p.get("actual_winner"):
            return
        by_key[key] = {
            "game_id": gid,
            "away_team": away,
            "home_team": home,
            "date": date,
            "source": source,
            "pred": p,
        }

    for p in preds.values():
        _add(p, "events")
    for p in hist:
        _add(p, "hist")
    return list(by_key.values())


def backfill_all_outcomes() -> Dict[str, int]:
    today = _today_ct()
    client = NHLAPIClient(timeout=8, pool_size=32)
    candidates = _collect_candidates()
    print(f"📋 Candidates missing outcomes: {len(candidates)}")

    dates = [c.get("date") for c in candidates if c.get("date")]
    print(f"🗺️  Prefetching schedules for {len(set(dates))} dates...")
    schedule_cache = prefetch_schedules(dates)

    resolved = []
    unresolved = []
    for c in candidates:
        rid = resolve_game_id(
            game_id=c.get("game_id"),
            away_team=c.get("away_team"),
            home_team=c.get("home_team"),
            date=c.get("date"),
            schedule_cache=schedule_cache,
            session=client.session,
        )
        if rid:
            c["resolved_game_id"] = rid
            resolved.append(c)
        else:
            unresolved.append(c)

    print(f"✅ Resolved to NHL IDs: {len(resolved)}")
    print(f"⚠️  Still unresolved: {len(unresolved)}")
    for u in unresolved[:20]:
        print(f"   • {u.get('date')} {u.get('away_team')}@{u.get('home_team')} id={u.get('game_id')}")

    # If synthetic id was used, append a corrected prediction event under the real id.
    rewritten = 0
    existing_preds = load_latest_by_game_id(PREDICTION_EVENTS_PATH)
    for c in resolved:
        rid = c["resolved_game_id"]
        old = str(c.get("game_id"))
        if is_valid_nhl_game_id(old) and str(old) == rid:
            continue
        # Copy latest prediction fields onto real game id
        src = c.get("pred") or {}
        if existing_preds.get(rid) and existing_preds[rid].get("away_team"):
            continue
        event = {
            "date": c.get("date") or src.get("date"),
            "game_id": int(rid) if rid.isdigit() else rid,
            "home_team": c.get("home_team"),
            "away_team": c.get("away_team"),
            "predicted_winner": src.get("predicted_winner"),
            "predicted_home_win_prob": src.get("predicted_home_win_prob") or src.get("home_win_prob"),
            "predicted_away_win_prob": src.get("predicted_away_win_prob") or src.get("away_win_prob"),
            "model_confidence": src.get("model_confidence"),
            "metrics_used": src.get("metrics_used") or {},
            "extra_metadata": {
                "rewritten_from_game_id": old,
                "backfill": True,
            },
        }
        append_prediction_event(event)
        rewritten += 1
    print(f"📝 Rewrote prediction events with real game IDs: {rewritten}")

    # Determine which resolved games are completed and missing outcomes.
    outs = load_latest_by_game_id(OUTCOME_EVENTS_PATH)
    need_fetch = []
    for c in resolved:
        rid = c["resolved_game_id"]
        if outs.get(rid, {}).get("actual_winner"):
            continue
        if (c.get("pred") or {}).get("actual_winner"):
            # Sync from prediction record
            p = c["pred"]
            append_outcome_event(
                game_id=rid,
                date=c.get("date"),
                away_team=c.get("away_team"),
                home_team=c.get("home_team"),
                actual_away_score=p.get("actual_away_score"),
                actual_home_score=p.get("actual_home_score"),
                actual_winner=p.get("actual_winner"),
                lead_after_p1=p.get("lead_after_p1"),
                synced_from_prediction=True,
            )
            outs[rid] = {"actual_winner": p.get("actual_winner")}
            continue

        # Schedule completeness check
        day_games = schedule_cache.get(c.get("date") or "") or []
        sched = next((g for g in day_games if str(g.get("id")) == rid), None)
        state = (sched or {}).get("gameState")
        away_score = ((sched or {}).get("awayTeam") or {}).get("score")
        home_score = ((sched or {}).get("homeTeam") or {}).get("score")
        date = c.get("date") or ""
        is_complete = state in ("FINAL", "OFF", "OFFICIAL") or (
            date < today and away_score is not None and home_score is not None
        )
        if not is_complete:
            if date >= today:
                print(f"⏳ Not finished yet: {date} {c.get('away_team')}@{c.get('home_team')} ({rid})")
            continue
        need_fetch.append(c)

    print(f"🌐 Fetching boxscores for {len(need_fetch)} completed games...")
    client.prefetch_games([c["resolved_game_id"] for c in need_fetch], max_workers=16)

    filled = 0

    def _one(c):
        rid = c["resolved_game_id"]
        data = client.get_comprehensive_game_data(rid, include_right_rail=False, use_cache=True)
        if not data:
            return None
        box = data.get("boxscore") or {}
        away_score = (box.get("awayTeam") or {}).get("score")
        home_score = (box.get("homeTeam") or {}).get("score")
        if away_score is None or home_score is None:
            # fall back to schedule scores
            day_games = schedule_cache.get(c.get("date") or "") or []
            sched = next((g for g in day_games if str(g.get("id")) == rid), None) or {}
            away_score = ((sched.get("awayTeam") or {}).get("score"))
            home_score = ((sched.get("homeTeam") or {}).get("score"))
        if away_score is None or home_score is None:
            return None
        away = c.get("away_team")
        home = c.get("home_team")
        return {
            "game_id": rid,
            "date": c.get("date"),
            "away_team": away,
            "home_team": home,
            "away_score": int(away_score),
            "home_score": int(home_score),
            "actual_winner": _winner(away, home, int(away_score), int(home_score)),
        }

    with ThreadPoolExecutor(max_workers=16) as ex:
        results = list(ex.map(_one, need_fetch))

    for res in results:
        if not res:
            continue
        append_outcome_event(
            game_id=res["game_id"],
            date=res["date"],
            away_team=res["away_team"],
            home_team=res["home_team"],
            actual_away_score=res["away_score"],
            actual_home_score=res["home_score"],
            actual_winner=res["actual_winner"],
            backfill=True,
        )
        filled += 1
        print(
            f"✅ {res['date']} {res['away_team']} {res['away_score']}-{res['home_score']} "
            f"{res['home_team']} → {res['actual_winner']} ({res['game_id']})"
        )

    # Rebuild hist JSON (applies outcomes onto predictions view)
    try:
        from utils.build_predictions_history_view import write_view

        write_view()
        print("💾 Rebuilt data/win_probability_predictions_v2.json")
    except Exception as e:
        print(f"⚠️ Could not rebuild hist view: {e}")

    # Clear skip list entries that are now resolved / filled
    if SKIP_PATH.exists():
        try:
            payload = json.loads(SKIP_PATH.read_text())
            old = set(payload.get("game_ids") or [])
            keep = set()
            for gid in old:
                if is_valid_nhl_game_id(gid):
                    # keep only if still missing outcome and not finished
                    if not load_latest_by_game_id(OUTCOME_EVENTS_PATH).get(str(gid), {}).get("actual_winner"):
                        keep.add(gid)
                else:
                    # drop synthetic keys once resolved
                    continue
            SKIP_PATH.write_text(json.dumps({"game_ids": sorted(keep)}, indent=2))
            print(f"🧹 Skip list {len(old)} → {len(keep)}")
        except Exception as e:
            print(f"⚠️ Skip list cleanup: {e}")

    # Mirror outcomes onto any stale/wrong prediction game_ids that resolve
    # to an already-filled official id (so no year shows "missing").
    outs2 = load_latest_by_game_id(OUTCOME_EVENTS_PATH)
    preds2 = load_latest_by_game_id(PREDICTION_EVENTS_PATH)
    mirrored = 0
    still = []
    for gid, p in preds2.items():
        if outs2.get(str(gid), {}).get("actual_winner") or p.get("actual_winner"):
            continue
        rid = resolve_game_id(
            game_id=gid,
            away_team=p.get("away_team"),
            home_team=p.get("home_team"),
            date=p.get("date"),
            schedule_cache=schedule_cache,
            verify_matchup=True,
        )
        if rid and outs2.get(str(rid), {}).get("actual_winner"):
            src = outs2[str(rid)]
            append_outcome_event(
                game_id=str(gid),
                date=p.get("date") or src.get("date"),
                away_team=p.get("away_team") or src.get("away_team"),
                home_team=p.get("home_team") or src.get("home_team"),
                actual_away_score=src.get("actual_away_score"),
                actual_home_score=src.get("actual_home_score"),
                actual_winner=src.get("actual_winner"),
                lead_after_p1=src.get("lead_after_p1"),
                mirrored_from_game_id=str(rid),
            )
            outs2[str(gid)] = {"actual_winner": src.get("actual_winner")}
            mirrored += 1
            continue
        still.append(p)

    if mirrored:
        print(f"🔗 Mirrored outcomes onto {mirrored} stale/wrong prediction IDs")
        try:
            from utils.build_predictions_history_view import write_view
            write_view()
        except Exception:
            pass

    live_or_future = [p for p in still if (p.get("date") or "") >= today]
    truly_missing = [p for p in still if (p.get("date") or "") < today]

    # Also patch hist JSON rows in-place for any remaining past gaps with known schedule scores.
    hist_path = Path("data/win_probability_predictions_v2.json")
    hist_fixed = 0
    if hist_path.exists() and truly_missing == []:
        pass
    elif hist_path.exists():
        hist_data = json.loads(hist_path.read_text())
        rows = hist_data.get("predictions") or []
        for row in rows:
            if row.get("actual_winner"):
                continue
            date = row.get("date") or ""
            if date >= today:
                continue
            rid = resolve_game_id(
                game_id=row.get("game_id"),
                away_team=row.get("away_team"),
                home_team=row.get("home_team"),
                date=date,
                schedule_cache=schedule_cache,
                verify_matchup=True,
            )
            src = outs2.get(str(rid) or "", {})
            if not src.get("actual_winner"):
                continue
            row["game_id"] = int(rid) if str(rid).isdigit() else rid
            row["actual_winner"] = src.get("actual_winner")
            row["actual_away_score"] = src.get("actual_away_score")
            row["actual_home_score"] = src.get("actual_home_score")
            hist_fixed += 1
        if hist_fixed:
            hist_path.write_text(json.dumps(hist_data, separators=(",", ":")))
            print(f"💾 Patched {hist_fixed} hist JSON rows with outcomes")

    # Recompute missing after mirror/patch
    outs2 = load_latest_by_game_id(OUTCOME_EVENTS_PATH)
    preds2 = load_latest_by_game_id(PREDICTION_EVENTS_PATH)
    still = []
    for gid, p in preds2.items():
        if outs2.get(str(gid), {}).get("actual_winner") or p.get("actual_winner"):
            continue
        rid = resolve_game_id(
            game_id=gid,
            away_team=p.get("away_team"),
            home_team=p.get("home_team"),
            date=p.get("date"),
            schedule_cache=schedule_cache,
            verify_matchup=True,
        )
        if rid and outs2.get(str(rid), {}).get("actual_winner"):
            continue
        still.append(p)
    live_or_future = [p for p in still if (p.get("date") or "") >= today]
    truly_missing = [p for p in still if (p.get("date") or "") < today]

    print("=" * 60)
    print(f"Filled via API: {filled}")
    print(f"Prediction IDs rewritten: {rewritten}")
    print(f"Mirrored onto stale IDs: {mirrored}")
    print(f"Still open (today/future/live): {len(live_or_future)}")
    print(f"Still missing past games: {len(truly_missing)}")
    for p in truly_missing[:30]:
        print(f"   ❌ {p.get('date')} {p.get('away_team')}@{p.get('home_team')} id={p.get('game_id')}")

    return {
        "filled": filled,
        "rewritten": rewritten,
        "mirrored": mirrored,
        "unresolved": len(unresolved),
        "still_past_missing": len(truly_missing),
        "live_or_future": len(live_or_future),
    }


if __name__ == "__main__":
    stats = backfill_all_outcomes()
    # Non-zero only if past games remain missing after backfill.
    raise SystemExit(1 if stats.get("still_past_missing", 0) else 0)
