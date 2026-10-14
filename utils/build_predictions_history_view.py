#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from utils.event_store import (
        OUTCOME_EVENTS_PATH,
        PREDICTION_EVENTS_PATH,
        load_latest_by_game_id,
    )
except Exception:
    # Allows running as `python3 utils/build_predictions_history_view.py`
    from event_store import (
        OUTCOME_EVENTS_PATH,
        PREDICTION_EVENTS_PATH,
        load_latest_by_game_id,
    )


def _is_official_id(gid) -> bool:
    s = str(gid or "")
    return s.isdigit() and len(s) >= 8


def _normalize_winner(
    winner: Any,
    away_team: Optional[str],
    home_team: Optional[str],
    away_score: Any = None,
    home_score: Any = None,
) -> Any:
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
    if away_score is not None and home_score is not None and away and home:
        try:
            a, h = int(away_score), int(home_score)
            if a > h:
                return away
            if h > a:
                return home
            if low in ("home", "away", "tie"):
                return "TIE" if a == h else (away if a > h else home)
        except Exception:
            pass
    return w.upper() if len(w) <= 3 else w


def _matchup_key(p: Dict[str, Any]) -> str:
    return f"{(p.get('away_team') or '').upper()}@{(p.get('home_team') or '').upper()}_{p.get('date') or ''}"


def _richer(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Prefer native official-id rows over remapped aliases; then richer fields."""

    def _score(row: Dict[str, Any]) -> int:
        meta = row.get("extra_metadata") or {}
        remapped = bool(isinstance(meta, dict) and meta.get("source_game_id"))
        return (
            (10 if _is_official_id(row.get("game_id")) else 0)
            + (0 if remapped else 5)  # prefer rows that already used the official id
            + (3 if row.get("predicted_winner") else 0)
            + (2 if row.get("predicted_home_win_prob") is not None else 0)
            + (1 if row.get("metrics_used") else 0)
        )

    return a if _score(a) >= _score(b) else b


def build_view() -> Dict[str, Any]:
    preds = load_latest_by_game_id(PREDICTION_EVENTS_PATH)
    outs = load_latest_by_game_id(OUTCOME_EVENTS_PATH)

    # Resolve aliases: prefer official NHL ids; collapse duplicate matchups.
    try:
        from utils.game_id_resolve import resolve_game_id, prefetch_schedules
    except Exception:
        try:
            from game_id_resolve import resolve_game_id, prefetch_schedules
        except Exception:
            resolve_game_id = None
            prefetch_schedules = None

    schedule_cache = {}
    if prefetch_schedules is not None:
        schedule_cache = prefetch_schedules([p.get("date") for p in preds.values() if p.get("date")])

    # First pass: rewrite game_id to official when resolvable, then dedupe by matchup.
    enriched: List[Dict[str, Any]] = []
    for gid, p in preds.items():
        row = dict(p)
        official = None
        if resolve_game_id is not None:
            try:
                official = resolve_game_id(
                    game_id=gid,
                    away_team=p.get("away_team"),
                    home_team=p.get("home_team"),
                    date=p.get("date"),
                    schedule_cache=schedule_cache,
                    verify_matchup=True,
                )
            except Exception:
                official = None
        if official and str(official) != str(gid):
            row["game_id"] = int(official) if str(official).isdigit() else official
            row.setdefault("extra_metadata", {})
            if isinstance(row["extra_metadata"], dict):
                row["extra_metadata"]["source_game_id"] = gid
        elif _is_official_id(gid):
            row["game_id"] = int(gid) if str(gid).isdigit() else gid
        enriched.append(row)

    by_matchup: Dict[str, Dict[str, Any]] = {}
    by_official: Dict[str, Dict[str, Any]] = {}
    for row in enriched:
        gid = str(row.get("game_id"))
        if _is_official_id(gid):
            prev = by_official.get(gid)
            by_official[gid] = row if prev is None else _richer(prev, row)
        key = _matchup_key(row)
        if key.endswith("_") or key.startswith("@"):
            # incomplete matchup — keep by game id only
            continue
        prev = by_matchup.get(key)
        by_matchup[key] = row if prev is None else _richer(prev, row)

    # Prefer official-id index; fill any matchup-only leftovers
    chosen: Dict[str, Dict[str, Any]] = dict(by_official)
    for key, row in by_matchup.items():
        gid = str(row.get("game_id"))
        if _is_official_id(gid):
            chosen[gid] = _richer(chosen[gid], row) if gid in chosen else row
            continue
        # synthetic with no official resolution — keep only if no official for same matchup
        has_official = any(_matchup_key(r) == key for r in by_official.values())
        if not has_official:
            chosen[f"synth:{key}"] = row

    rows: List[Dict[str, Any]] = []
    for row in chosen.values():
        # Legacy compatibility: some producers write home_win_prob/away_win_prob (0..1),
        # while legacy consumers expect predicted_*_win_prob.
        try:
            if row.get("predicted_home_win_prob") is None and row.get("home_win_prob") is not None:
                row["predicted_home_win_prob"] = float(row["home_win_prob"]) * 100.0
            if row.get("predicted_away_win_prob") is None and row.get("away_win_prob") is not None:
                row["predicted_away_win_prob"] = float(row["away_win_prob"]) * 100.0
        except Exception:
            pass

        # Ensure invariants when possible (best-effort; do not crash view build).
        try:
            ph = row.get("predicted_home_win_prob")
            pa = row.get("predicted_away_win_prob")
            if ph is not None and pa is not None:
                ph = float(ph)
                pa = float(pa)
                # If these look like decimals, normalize to percents.
                if 0.0 <= ph <= 1.0 and 0.0 <= pa <= 1.0:
                    ph *= 100.0
                    pa *= 100.0
                    row["predicted_home_win_prob"] = ph
                    row["predicted_away_win_prob"] = pa
                s = ph + pa
                if s > 0 and abs(s - 100.0) > 1e-3:
                    # Renormalize (protect downstream analyses)
                    row["predicted_home_win_prob"] = 100.0 * ph / s
                    row["predicted_away_win_prob"] = 100.0 * pa / s
        except Exception:
            pass

        # Ensure predicted_winner is populated for accuracy calculations
        if not row.get("predicted_winner"):
            ph = row.get("predicted_home_win_prob")
            pa = row.get("predicted_away_win_prob")
            if ph is not None and pa is not None and row.get("home_team") and row.get("away_team"):
                row["predicted_winner"] = row["home_team"] if float(ph) >= float(pa) else row["away_team"]
            elif (
                row.get("home_win_prob") is not None
                and row.get("away_win_prob") is not None
                and row.get("home_team")
                and row.get("away_team")
            ):
                row["predicted_winner"] = (
                    row["home_team"]
                    if float(row["home_win_prob"]) >= float(row["away_win_prob"])
                    else row["away_team"]
                )

        # Outcome resolution: by game_id, by source_game_id, or by matchup key
        gid = str(row.get("game_id"))
        o = outs.get(gid) or {}
        if not o.get("actual_winner"):
            src = (row.get("extra_metadata") or {}).get("source_game_id")
            if src:
                o = outs.get(str(src)) or o
        if not o.get("actual_winner"):
            mkey = _matchup_key(row)
            for out_r in outs.values():
                if _matchup_key(out_r) == mkey and out_r.get("actual_winner"):
                    o = out_r
                    break

        for k in (
            "actual_winner",
            "actual_away_score",
            "actual_home_score",
            "home_goalie",
            "away_goalie",
            "home_shots",
            "away_shots",
            "home_xg",
            "away_xg",
        ):
            if o.get(k) is not None:
                row[k] = o.get(k)

        row["actual_winner"] = _normalize_winner(
            row.get("actual_winner"),
            row.get("away_team"),
            row.get("home_team"),
            row.get("actual_away_score"),
            row.get("actual_home_score"),
        )

        mu = row.get("metrics_used") or {}
        if not isinstance(mu, dict):
            mu = {}
        if o.get("lead_after_p1") is not None:
            mu["lead_after_p1"] = o.get("lead_after_p1")
        if o.get("home_goalie") and not mu.get("home_goalie"):
            mu["home_goalie"] = o.get("home_goalie")
        if o.get("away_goalie") and not mu.get("away_goalie"):
            mu["away_goalie"] = o.get("away_goalie")
        if mu:
            row["metrics_used"] = mu

        # Accuracy if both sides known
        if row.get("actual_winner") and row.get("predicted_winner"):
            row["prediction_accuracy"] = (
                1.0 if str(row["actual_winner"]).upper() == str(row["predicted_winner"]).upper() else 0.0
            )

        # First-class scoreline promotion and projected scoreline
        meta = row.get("extra_metadata") or {}
        if not isinstance(meta, dict):
            meta = {}

        phg = row.get("predicted_home_goals")
        if phg is None:
            phg = meta.get("predicted_home_goals")
        if phg is None:
            phg = row.get("home_score")

        pag = row.get("predicted_away_goals")
        if pag is None:
            pag = meta.get("predicted_away_goals")
        if pag is None:
            pag = row.get("away_score")

        if phg is not None and pag is not None:
            try:
                row["predicted_home_goals"] = int(round(float(phg)))
                row["predicted_away_goals"] = int(round(float(pag)))
                row["predicted_total_goals"] = row["predicted_home_goals"] + row["predicted_away_goals"]
                row["projected_score"] = (
                    f"{row.get('away_team')} {row['predicted_away_goals']} - {row.get('home_team')} {row['predicted_home_goals']}"
                )
            except Exception:
                pass

        # Error tracking metrics when actual score is available
        aas = row.get("actual_away_score")
        ahs = row.get("actual_home_score")
        if aas is not None and ahs is not None:
            try:
                aas_int = int(round(float(aas)))
                ahs_int = int(round(float(ahs)))
                row["actual_away_score"] = aas_int
                row["actual_home_score"] = ahs_int
                row["actual_score"] = f"{row.get('away_team')} {aas_int} - {row.get('home_team')} {ahs_int}"

                if row.get("predicted_home_goals") is not None and row.get("predicted_away_goals") is not None:
                    row["exact_score_match"] = bool(
                        row["predicted_away_goals"] == aas_int and row["predicted_home_goals"] == ahs_int
                    )
                    pred_margin = row["predicted_home_goals"] - row["predicted_away_goals"]
                    act_margin = ahs_int - aas_int
                    row["score_margin_error"] = abs(pred_margin - act_margin)
                    pred_total = row["predicted_home_goals"] + row["predicted_away_goals"]
                    act_total = ahs_int + aas_int
                    row["total_goals_error"] = abs(pred_total - act_total)
            except Exception:
                pass

        rows.append(row)

    # Deterministic ordering
    rows.sort(key=lambda r: (str(r.get("date") or ""), str(r.get("game_id") or "")))
    return {"predictions": rows}


def write_view(out_path: Path = Path("data/win_probability_predictions_v2.json")) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    view = build_view()
    out_path.write_text(json.dumps(view, indent=2))
    return out_path


if __name__ == "__main__":
    p = write_view()
    print(f"WROTE_VIEW={p}")
