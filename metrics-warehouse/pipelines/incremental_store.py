#!/usr/bin/env python3
"""Incremental warehouse updates — only process games since the last curated run.

Default daily path:
  1. Read curated processed_games watermark
  2. Diff vs current-season completed RS finals
  3. Fetch/aggregate ONLY the new game IDs
  4. Merge count totals into existing stores; recompute rates

Full rebuild only when:
  - curated missing / empty
  - schema_version mismatch
  - WAREHOUSE_FULL_REBUILD=1
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from paths import CURATED, ensure_dirs

SKIP_MERGE_KEYS = frozenset(
    {
        "player_id",
        "name",
        "team",
        "schema_version",
        "rates",
        "rates_stable",
        "instat",
        "on_ice",
        "sources",
        "position",
        "grain",
        "source_note",
    }
)


def env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes")


def want_full_rebuild() -> bool:
    return env_flag("WAREHOUSE_FULL_REBUILD", False)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def prior_skater_team_stores() -> Tuple[dict, dict]:
    sk = load_json(CURATED / "skaters_season.json") or load_json(
        CURATED / "skaters" / "nhl_pbp_microstats.json"
    )
    tm = load_json(CURATED / "teams" / "nhl_pbp_microstats.json")
    return sk, tm


def processed_game_set(*stores: dict) -> Set[str]:
    out: Set[str] = set()
    for st in stores:
        for gid in st.get("processed_games") or []:
            out.add(str(gid))
    return out


def schema_ok(store: dict, expected: int) -> bool:
    """True if store is usable for append.

    Missing schema_version on a non-empty season store is treated as compatible
    (stamp will be written on next write). Only an *explicit* different version
    forces a full rebuild.
    """
    if not store:
        return False
    sv = store.get("schema_version")
    if sv is None:
        rows = store.get("skaters") or store.get("teams") or {}
        if isinstance(rows, dict) and rows:
            first = next(iter(rows.values()))
            if isinstance(first, dict):
                sv = first.get("schema_version")
                rates = first.get("rates") if isinstance(first.get("rates"), dict) else {}
                sv = sv or rates.get("schema_version")
    if sv is None:
        # Legacy curated without stamp — OK if it has games.
        return bool(store.get("processed_games") or store.get("skaters") or store.get("teams"))
    try:
        return int(sv) == int(expected)
    except (TypeError, ValueError):
        return False


def new_game_ids(all_ids: List[str], already: Set[str]) -> List[str]:
    """Preserve API order; only IDs not yet curated."""
    return [str(g) for g in all_ids if str(g) not in already]


def strip_rates(row: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in row.items() if k not in SKIP_MERGE_KEYS or k in {"player_id", "name", "team", "schema_version"}}


def merge_count_rows(
    base: Dict[Any, Dict[str, Any]],
    incoming: Dict[Any, Dict[str, Any]],
    *,
    id_key: str,
) -> Dict[Any, Dict[str, Any]]:
    """Add numeric totals from incoming into base (mutates/returns base)."""
    for kid, row in incoming.items():
        key = kid
        if key not in base:
            base[key] = strip_rates(dict(row))
            continue
        dest = base[key]
        if row.get("name"):
            dest["name"] = row["name"]
        if row.get("team"):
            dest["team"] = row["team"]
        if row.get(id_key) is not None:
            dest[id_key] = row[id_key]
        for k, v in row.items():
            if k in SKIP_MERGE_KEYS or k == id_key:
                continue
            if isinstance(v, bool):
                continue
            if isinstance(v, (int, float)):
                prev = dest.get(k, 0) or 0
                if isinstance(v, float) or isinstance(prev, float):
                    dest[k] = float(prev) + float(v)
                else:
                    dest[k] = int(prev) + int(v)
        if row.get("schema_version") is not None:
            dest["schema_version"] = row["schema_version"]
    return base


def write_incremental_status(
    *,
    mode: str,
    prior_count: int,
    new_ids: List[str],
    after_count: int,
    full_rebuild: bool,
) -> Path:
    ensure_dirs()
    payload = {
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "mode": mode,
        "full_rebuild": full_rebuild,
        "prior_game_count": prior_count,
        "new_games": new_ids,
        "new_game_count": len(new_ids),
        "after_game_count": after_count,
        "skipped_historical_refetch": (not full_rebuild) and len(new_ids) == 0,
    }
    out = CURATED / "status" / "incremental.json"
    out.write_text(json.dumps(payload, indent=2))
    return out


def decide_skater_plan(
    all_ids: List[str],
    *,
    schema_version: int,
) -> Dict[str, Any]:
    """Return plan: full | append | noop."""
    sk, tm = prior_skater_team_stores()
    prior_games = processed_game_set(sk, tm)
    prior_count = len(prior_games)
    full = want_full_rebuild()
    if full:
        return {
            "action": "full",
            "reason": "WAREHOUSE_FULL_REBUILD=1",
            "ids": list(all_ids),
            "prior_games": prior_games,
            "prior_count": prior_count,
            "sk": sk,
            "tm": tm,
        }
    if not sk or not tm or prior_count == 0:
        return {
            "action": "full",
            "reason": "missing_or_empty_curated",
            "ids": list(all_ids),
            "prior_games": prior_games,
            "prior_count": prior_count,
            "sk": sk,
            "tm": tm,
        }
    if not schema_ok(sk, schema_version) or not schema_ok(tm, schema_version):
        return {
            "action": "full",
            "reason": "schema_mismatch",
            "ids": list(all_ids),
            "prior_games": prior_games,
            "prior_count": prior_count,
            "sk": sk,
            "tm": tm,
        }
    fresh = new_game_ids(all_ids, prior_games)
    if not fresh:
        return {
            "action": "noop",
            "reason": "no_new_completed_rs_games",
            "ids": [],
            "prior_games": prior_games,
            "prior_count": prior_count,
            "sk": sk,
            "tm": tm,
        }
    return {
        "action": "append",
        "reason": f"{len(fresh)}_new_games",
        "ids": fresh,
        "prior_games": prior_games,
        "prior_count": prior_count,
        "sk": sk,
        "tm": tm,
    }
