#!/usr/bin/env python3

"""
Compact JSONL event logs by keeping only the latest record per game_id.
Prevents unbounded growth / slow reads over time.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from utils.event_store import OUTCOME_EVENTS_PATH, PREDICTION_EVENTS_PATH, load_latest_by_game_id
except Exception:
    from event_store import OUTCOME_EVENTS_PATH, PREDICTION_EVENTS_PATH, load_latest_by_game_id


def _is_official_id(gid: Any) -> bool:
    s = str(gid or "").strip()
    return s.isdigit() and len(s) >= 8


def _season_prefix(date_str: Optional[str]) -> str:
    if not date_str or len(date_str) < 7:
        return "2026"
    try:
        y = int(date_str[:4])
        m = int(date_str[5:7])
        return str(y) if m >= 7 else str(y - 1)
    except Exception:
        return "2026"


def _merge_event_records(existing: Dict[str, Any], new_r: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two event records for the same game/matchup, keeping richest fields and official ID."""
    gid1 = existing.get("game_id")
    gid2 = new_r.get("game_id")
    off1 = _is_official_id(gid1)
    off2 = _is_official_id(gid2)
    d = existing.get("date") or new_r.get("date")
    pref = _season_prefix(d)

    if off1 and off2:
        s1 = str(gid1)
        s2 = str(gid2)
        if s1.startswith(pref) and not s2.startswith(pref):
            best_gid = gid1
        elif s2.startswith(pref) and not s1.startswith(pref):
            best_gid = gid2
        else:
            best_gid = gid2  # later
    elif off1:
        best_gid = gid1
    elif off2:
        best_gid = gid2
    else:
        best_gid = gid2

    merged = dict(existing)
    for k, v in new_r.items():
        if v is not None:
            if k == "extra_metadata" and isinstance(merged.get("extra_metadata"), dict) and isinstance(v, dict):
                m_meta = dict(merged["extra_metadata"])
                m_meta.update(v)
                merged["extra_metadata"] = m_meta
            elif k == "metrics_used" and isinstance(merged.get("metrics_used"), dict) and isinstance(v, dict):
                m_mu = dict(merged["metrics_used"])
                m_mu.update(v)
                merged["metrics_used"] = m_mu
            else:
                merged[k] = v

    merged["game_id"] = int(best_gid) if str(best_gid).isdigit() else best_gid
    # Record synthetic alias if merged into official ID
    for orig in (gid1, gid2):
        if orig and not _is_official_id(orig) and str(orig) != str(merged["game_id"]):
            merged.setdefault("extra_metadata", {})
            if isinstance(merged["extra_metadata"], dict):
                merged["extra_metadata"].setdefault("source_game_id", str(orig))
    return merged


def compact(path: Path) -> int:
    if not path.exists():
        return 0

    all_rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                all_rows.append(json.loads(line))
            except Exception:
                continue

    if not all_rows:
        return 0

    # Build matchup -> official ID map
    matchup_to_official: Dict[tuple, str] = {}
    for r in all_rows:
        gid = str(r.get("game_id", ""))
        d = str(r.get("date") or "")
        a = (str(r.get("away_team") or "")).upper()
        h = (str(r.get("home_team") or "")).upper()
        if _is_official_id(gid) and d and a and h:
            matchup_to_official[(d, a, h)] = gid

    rows_by_key: Dict[str, Dict[str, Any]] = {}
    for r in all_rows:
        gid = str(r.get("game_id", ""))
        d = str(r.get("date") or "")
        a = (str(r.get("away_team") or "")).upper()
        h = (str(r.get("home_team") or "")).upper()
        
        # If synthetic composite @ ID and an official ID exists for this matchup, merge into official
        if "@" in gid and (d, a, h) in matchup_to_official:
            key = str(matchup_to_official[(d, a, h)])
        elif d and a and h and not _is_official_id(gid):
            key = f"{d}_{a}_{h}"
        else:
            key = gid

        if key in rows_by_key:
            rows_by_key[key] = _merge_event_records(rows_by_key[key], r)
        else:
            rows_by_key[key] = r

    # Stable ordering by date, then game_id
    rows = list(rows_by_key.values())
    rows.sort(key=lambda r: (str(r.get("date") or ""), str(r.get("game_id") or "")))
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)
    return len(rows)


def main() -> None:
    n1 = compact(PREDICTION_EVENTS_PATH)
    n2 = compact(OUTCOME_EVENTS_PATH)
    print(f"COMPACTED_PREDICTIONS={n1}")
    print(f"COMPACTED_OUTCOMES={n2}")


if __name__ == "__main__":
    main()


