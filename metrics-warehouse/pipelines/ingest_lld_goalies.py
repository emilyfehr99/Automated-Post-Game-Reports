#!/usr/bin/env python3
"""Ingest Last Line of Defense (nhl-goalie-hub) goalie metrics into the warehouse.

Canonical goalie advanced store — GSAx, danger splits, rebound control, derived
process metrics, and InStat charted fields when present on the hub artifact.
"""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Any, Dict

from paths import CURATED, LLD, RAW, ensure_dirs, season_label


# Flatten keys we always want at the top of each curated goalie row
_TOP_ADV = (
    "gsax", "gsax60", "gsaxPerGp", "xGA", "xSvp", "dSvp", "gsaa",
    "toiMin", "saPer60", "hdSa", "hdGa", "hdSvp", "mdSa", "mdGa", "mdSvp",
    "ldSa", "ldGa", "ldSvp", "evSvp", "ppSvp", "shSvp", "qualityStartPct",
    "svpPercentile",
)

_PBP_KEYS = (
    "reboundControlPct", "reboundRate", "reboundsAllowed", "reboundSa",
    "reboundGa", "reboundSvp", "reboundGsax", "reboundXg",
    "rushSa", "rushGa", "rushSvp", "rushGsax",
    "offWingSa", "offWingSvp", "onWingSa", "onWingSvp",
    "hdGsax", "mdGsax", "ldGsax", "gsax", "goalsAgainst",
)

_DERIVED_KEYS = (
    "freezeRate", "controlledRebShare", "uncontrolledRebShare",
    "hdFreezeShare", "hdCtrlShare", "hdUnctrlShare",
    "ewProxy", "counter", "positional", "screenRush",
    "hrQsPct", "rbsPct", "gameSvpSigma", "gameGsaxSigma",
    "nhlQsPct",
)


def _find_goalies_path() -> Path | None:
    label = season_label()
    candidates = [
        LLD / "data" / f"goalies-{label}.json",
        LLD / "data" / "goalies-2026-27.json",
        LLD / "data" / "goalies-2025-26.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    # any goalies-*.json
    matches = sorted((LLD / "data").glob("goalies-*.json"), reverse=True)
    return matches[0] if matches else None


def _season_block(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Hub uses `season` dict; `seasonTotals` is often an empty list."""
    for key in ("season", "seasonTotals"):
        block = raw.get(key)
        if isinstance(block, dict) and block:
            return block
        if isinstance(block, list):
            for item in block:
                if isinstance(item, dict) and (
                    item.get("gamesPlayed") is not None or item.get("gameTypeId") in (2, "2", None)
                ):
                    # prefer regular season if tagged
                    if item.get("gameTypeId") in (2, "2", None) or "gamesPlayed" in item:
                        return item
            if block and isinstance(block[0], dict):
                return block[0]
    return {}


def flatten_goalie(gid: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    adv = raw.get("adv") or {}
    pbp = adv.get("pbp") or {}
    derived = adv.get("derived") or {}
    instat = adv.get("instat") or {}
    season_totals = _season_block(raw)
    ext = raw.get("ext") if isinstance(raw.get("ext"), dict) else {}

    row: Dict[str, Any] = {
        "id": raw.get("id") or gid,
        "name": raw.get("name") or f"{raw.get('firstName','')} {raw.get('lastName','')}".strip(),
        "team": raw.get("team"),
        "catches": raw.get("catches"),
        "source": "last_line_of_defense",
        # traditional volume
        "gp": season_totals.get("gamesPlayed") or season_totals.get("gp"),
        "gs": season_totals.get("gamesStarted") or season_totals.get("gs"),
        "w": season_totals.get("wins") or season_totals.get("w"),
        "l": season_totals.get("losses") or season_totals.get("l"),
        "otl": season_totals.get("otLosses") or season_totals.get("otl"),
        "sa": season_totals.get("shotsAgainst") or season_totals.get("sa"),
        "ga": season_totals.get("goalsAgainst") or season_totals.get("ga"),
        "svPct": season_totals.get("savePctg") or season_totals.get("svPct"),
        "gaa": season_totals.get("goalsAgainstAverage")
        or season_totals.get("goalsAgainstAvg")
        or season_totals.get("gaa"),
        "so": season_totals.get("shutouts") or season_totals.get("so"),
        "toi": season_totals.get("timeOnIce") or season_totals.get("toi"),
        "ext": ext,
    }

    for k in _TOP_ADV:
        if k in adv:
            row[k] = adv[k]

    row["pbp"] = {k: pbp[k] for k in _PBP_KEYS if k in pbp}
    # keep full pbp blob for completeness
    row["pbp_full"] = pbp
    row["derived"] = {k: derived[k] for k in _DERIVED_KEYS if k in derived}
    row["derived_full"] = derived
    row["instat"] = instat if isinstance(instat, dict) else {}
    row["areas"] = adv.get("areas")
    row["edge"] = adv.get("edge")
    row["bio"] = raw.get("bio")
    row["last5Games"] = raw.get("last5Games")
    return row


def ingest() -> Path:
    ensure_dirs()
    src = _find_goalies_path()
    status = {
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "ok": False,
        "source": None,
        "goalie_count": 0,
        "error": None,
    }
    if not src:
        status["error"] = f"No goalies-*.json under {LLD / 'data'}"
        (CURATED / "status" / "lld_goalies.json").write_text(json.dumps(status, indent=2))
        raise FileNotFoundError(status["error"])

    # raw mirror
    raw_copy = RAW / "lld" / src.name
    shutil.copy2(src, raw_copy)

    data = json.loads(src.read_text())
    goalies_raw = data.get("goalies") or {}
    curated: Dict[str, Any] = {}
    for gid, g in goalies_raw.items():
        if isinstance(g, dict):
            curated[str(gid)] = flatten_goalie(str(gid), g)

    payload = {
        "updated_at": status["updated_at"],
        "source_file": str(src),
        "league": data.get("league"),
        "xgModel_present": bool(data.get("xgModel")),
        "goalie_count": len(curated),
        "goalies": curated,
        "metric_families": {
            "traditional": ["gp", "gs", "w", "l", "otl", "sa", "ga", "svPct", "gaa", "so", "toi"],
            "value": list(_TOP_ADV),
            "pbp_process": list(_PBP_KEYS),
            "derived_process": list(_DERIVED_KEYS),
            "instat_charted": "present_when_hub_has_adv.instat",
        },
    }
    out = CURATED / "goalies" / "lld_season.json"
    out.write_text(json.dumps(payload, indent=2))
    (CURATED / "goalies_season.json").write_text(json.dumps(payload, indent=2))

    status["ok"] = True
    status["source"] = str(src)
    status["goalie_count"] = len(curated)
    (CURATED / "status" / "lld_goalies.json").write_text(json.dumps(status, indent=2))
    print(f"🧤 LLD goalies: {len(curated)} → {out}")
    return out


if __name__ == "__main__":
    ingest()
