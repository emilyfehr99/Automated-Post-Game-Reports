#!/usr/bin/env python3
"""Real-data-only guards for the metrics warehouse.

Policy:
  - Counts/rates must come from live NHL PBP, NHL club stats, InStat gear pulls,
    or LLD goalie files — never invented, sampled, or imputed.
  - Unavailable action-PBP fields stay null with an explicit reason.
  - Multi-season APGR blobs must not be labeled as current RS.
  - No silent fallback that swaps one metric for another (e.g. DI for END).
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

# Never publish non-null values under these keys — action PBP required.
FORBIDDEN_IMPUTED_KEYS = {
    "puck_battle_win_pct",
    "puck_battle_win_pct_by_zone",
    "fc_to_shot_pct_true",
    "botched_retrievals_instat",
}

# Keys that are misleading stand-ins; strip from published derived/top5.
PROXY_STANDIN_KEYS = {
    "oz_recovery_to_sc_proxy",
    "oz_recovery_to_sc_proxy_note",
    "forecheck_recoveries_proxy",
}


def is_nullish(v: Any) -> bool:
    return v is None or v == "" or v == "--"


def assert_no_imputed(row: Dict[str, Any], *, path: str = "") -> List[str]:
    """Return error strings if forbidden keys hold non-null values."""
    errs: List[str] = []
    for k in FORBIDDEN_IMPUTED_KEYS:
        if k in row and not is_nullish(row.get(k)):
            errs.append(f"{path}.{k} has non-null value (forbidden imputation)")
        note = row.get(f"{k}_note")
        # notes alone are fine
        _ = note
    unavail = row.get("unavailable")
    if isinstance(unavail, dict):
        for k, meta in unavail.items():
            if isinstance(meta, dict) and not is_nullish(meta.get("value")):
                errs.append(f"{path}.unavailable.{k}.value must be null")
    return errs


def strip_proxy_standins(row: Dict[str, Any]) -> Dict[str, Any]:
    out = {k: v for k, v in row.items() if k not in PROXY_STANDIN_KEYS}
    return out


def current_season_advanced_ok(
    advanced_games: Optional[int],
    *,
    warehouse_team_games: Optional[int],
    cushion: int = 3,
) -> bool:
    """Reject multi-season APGR advanced rows posing as current RS."""
    if advanced_games is None or advanced_games <= 0:
        return False
    if warehouse_team_games is None or warehouse_team_games <= 0:
        # Without a warehouse GP anchor, only allow clearly early-season sizes
        return advanced_games <= 30
    return advanced_games <= int(warehouse_team_games) + cushion


def team_games_from_pbp(pbp_team: Dict[str, Any]) -> Optional[int]:
    if not pbp_team:
        return None
    for key in ("games", "game_count", "gp"):
        if pbp_team.get(key) is not None:
            try:
                return int(pbp_team[key])
            except (TypeError, ValueError):
                pass
    # Infer from a per-game rate if totals exist
    rates = pbp_team.get("rates") or {}
    entries = pbp_team.get("entries_total")
    epg = rates.get("entries_per_game")
    if entries and epg:
        try:
            g = int(round(float(entries) / float(epg)))
            if g > 0:
                return g
        except (TypeError, ValueError, ZeroDivisionError):
            pass
    return None
