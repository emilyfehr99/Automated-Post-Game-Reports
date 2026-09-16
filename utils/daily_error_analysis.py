#!/usr/bin/env python3
"""
Daily error analysis.

Generates a compact report of the biggest misses (high confidence wrong picks),
including model-vs-market probability deltas and key feature values.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytz

try:
    from utils.event_store import load_latest_by_game_id, PREDICTION_EVENTS_PATH, OUTCOME_EVENTS_PATH
except Exception:
    from event_store import load_latest_by_game_id, PREDICTION_EVENTS_PATH, OUTCOME_EVENTS_PATH


def _as_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def _as_int(x: Any) -> Optional[int]:
    try:
        if x is None:
            return None
        return int(float(x))
    except Exception:
        return None


def _winner_side(actual_winner: Any, away: str, home: str) -> Optional[str]:
    if not actual_winner:
        return None
    s = str(actual_winner).strip()
    if s.lower() in ("away", "home"):
        return s.lower()
    if away and s == away:
        return "away"
    if home and s == home:
        return "home"
    return None


def analyze(date_str: str, *, top_k: int = 10) -> Dict[str, Any]:
    preds_by = load_latest_by_game_id(PREDICTION_EVENTS_PATH)
    outs_by = load_latest_by_game_id(OUTCOME_EVENTS_PATH)

    rows = []
    for gid, p in preds_by.items():
        if str(p.get("date")) != date_str:
            continue
        o = outs_by.get(gid) or {}
        if not o.get("actual_winner"):
            continue

        away = p.get("away_team")
        home = p.get("home_team")
        away_p = _as_float(p.get("away_win_prob"))
        home_p = _as_float(p.get("home_win_prob"))
        if away_p is None or home_p is None:
            continue
        # normalize
        s = away_p + home_p
        if s <= 0:
            continue
        away_p /= s
        home_p /= s

        pick_side = "away" if away_p >= home_p else "home"
        actual_side = _winner_side(o.get("actual_winner"), away, home)
        if actual_side not in ("away", "home"):
            continue

        correct = pick_side == actual_side
        conf = max(away_p, home_p)

        market_away = _as_float(p.get("market_away_prob"))
        market_home = _as_float(p.get("market_home_prob"))
        if market_away is not None and market_home is not None:
            ms = market_away + market_home
            if ms > 0:
                market_away /= ms
                market_home /= ms

        feats = (p.get("metrics_used") or {}) if isinstance(p.get("metrics_used"), dict) else {}
        key_feats = {}
        for k in [
            "elo_diff",
            "rest_diff",
            "gsax_diff",
            "finish_diff",
            "is_playoff",
            "series_score_diff",
            "is_elimination_game",
            "home_b2b",
            "away_b2b",
        ]:
            if k in feats:
                key_feats[k] = feats.get(k)

        rows.append(
            {
                "date": date_str,
                "game_id": str(gid),
                "away_team": away,
                "home_team": home,
                "p_away": away_p,
                "p_home": home_p,
                "pick_side": pick_side,
                "actual_side": actual_side,
                "correct": bool(correct),
                "confidence": conf,
                "market_p_away": market_away,
                "market_p_home": market_home,
                "delta_p_away_minus_market": (None if market_away is None else float(away_p - market_away)),
                "key_features": key_feats,
            }
        )

    wrong = sorted([r for r in rows if not r["correct"]], key=lambda r: r["confidence"], reverse=True)
    top_wrong = wrong[: int(top_k)]

    return {
        "date": date_str,
        "n_with_outcomes": len(rows),
        "accuracy": (None if not rows else float(sum(1 for r in rows if r["correct"]) / len(rows))),
        "top_wrong": top_wrong,
    }


def main():
    central = pytz.timezone("US/Central")
    target = (datetime.now(central).date() - timedelta(days=1)).strftime("%Y-%m-%d")
    out = analyze(target, top_k=12)
    Path("artifacts").mkdir(exist_ok=True)
    out_path = Path("artifacts") / f"daily_error_analysis_{target}.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(str(out_path))
    print(json.dumps({"date": target, "n_with_outcomes": out.get("n_with_outcomes"), "accuracy": out.get("accuracy")}, indent=2))


if __name__ == "__main__":
    main()

