#!/usr/bin/env python3
"""Ingest APGR team advanced + season stats into the personal warehouse."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

from paths import APGR, CURATED, ensure_dirs
from real_data import current_season_advanced_ok, team_games_from_pbp


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def ingest() -> Path:
    ensure_dirs()
    adv = _load_json(APGR / "data" / "team_advanced_metrics.json") or {}
    # season_*_team_stats.json — prefer current NHL season file when present
    season_files = sorted((APGR / "data").glob("season_*_team_stats.json"), reverse=True)
    prefer = [p for p in season_files if "2026_2027" in p.name or "20262027" in p.name]
    season_path = prefer[0] if prefer else (season_files[0] if season_files else None)
    season = _load_json(season_path) if season_path else {}
    edge = _load_json(APGR / "data" / "nhl_edge_data.json") or {}
    # Warehouse-owned PBP microstats (preferred over APGR until schema v2 lands there)
    pbp_teams = _load_json(CURATED / "teams" / "nhl_pbp_microstats.json") or {}
    pbp_by_abbr = (pbp_teams.get("teams") or {}) if isinstance(pbp_teams, dict) else {}

    teams_adv = (adv.get("teams") or {}) if isinstance(adv, dict) else {}
    teams_season = (season.get("teams") or {}) if isinstance(season, dict) else {}

    merged: Dict[str, Any] = {}
    skipped_stale_advanced = 0
    abbrevs = sorted(set(teams_adv) | set(teams_season) | set(pbp_by_abbr))
    for abbr in abbrevs:
        a_raw = teams_adv.get(abbr) or {}
        s = teams_season.get(abbr) or {}
        pbp = pbp_by_abbr.get(abbr) or {}
        wh_gp = team_games_from_pbp(pbp) if pbp else None
        adv_games = None
        try:
            adv_games = int(a_raw.get("games") or 0) or None
        except (TypeError, ValueError):
            adv_games = None
        # Real-data policy: do not publish multi-season APGR advanced as current RS.
        if a_raw and current_season_advanced_ok(adv_games, warehouse_team_games=wh_gp):
            a = a_raw
            a_hist = None
        elif a_raw:
            a = None
            a_hist = {
                "omitted_reason": "multi_season_or_stale_vs_warehouse_rs",
                "advanced_games": adv_games,
                "warehouse_games": wh_gp,
            }
            skipped_stale_advanced += 1
        else:
            a = None
            a_hist = None
        # season file often nests home/away
        if "home" in s or "away" in s:
            flat_s = {"home": s.get("home"), "away": s.get("away"), "raw": s}
        else:
            flat_s = s
        # Prefer warehouse PBP microstats only (real RS event counts). Never fall
        # back to APGR nested microstats that may be stale/partial.
        micro = pbp.get("rates") or {}
        merged[abbr] = {
            "team": abbr,
            "advanced": a,
            "advanced_history_omitted": a_hist,
            "microstats": micro,
            "pbp_totals": {k: v for k, v in pbp.items() if k not in {"rates", "team"}} if pbp else {},
            "season_stats": flat_s,
            "edge": (edge.get("teams") or edge.get(abbr) or edge).get(abbr)
            if isinstance(edge, dict)
            else None,
            "real_data_only": True,
        }
        if merged[abbr]["edge"] is None and isinstance(edge, dict):
            for key in ("teams", "team_stats", "data"):
                block = edge.get(key)
                if isinstance(block, dict) and abbr in block:
                    merged[abbr]["edge"] = block[abbr]
                    break

    payload = {
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "real_data_only": True,
        "sources": {
            "team_advanced_metrics": str(APGR / "data" / "team_advanced_metrics.json"),
            "season_team_stats": str(season_path) if season_path else None,
            "nhl_edge_data": str(APGR / "data" / "nhl_edge_data.json"),
            "nhl_pbp_microstats": str(CURATED / "teams" / "nhl_pbp_microstats.json"),
            "pbp_game_count": pbp_teams.get("game_count"),
            "pbp_season": pbp_teams.get("season"),
            "stale_advanced_omitted": skipped_stale_advanced,
            "microstats_schema_version": (pbp_teams.get("teams") or {})
            and ((next(iter((pbp_teams.get("teams") or {}).values()), {}) or {}).get("rates") or {}).get(
                "schema_version"
            ),
            "microstats_catalog": None,
        },
        "team_count": len(merged),
        "teams": merged,
    }
    out = CURATED / "teams" / "nhl_combined.json"
    out.write_text(json.dumps(payload, indent=2))
    (CURATED / "teams_season.json").write_text(json.dumps(payload, indent=2))
    print(f"🏒 Teams: {len(merged)} → {out}")
    return out


if __name__ == "__main__":
    ingest()
