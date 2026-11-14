#!/usr/bin/env python3
"""Build personal metric warehouse: teams + skaters + goalies (+ InStat when available)."""

from __future__ import annotations

import json
import os
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipelines"))

from paths import CURATED, ensure_dirs  # noqa: E402


def _run(name: str, fn, *args, **kwargs):
    t0 = time.time()
    try:
        result = fn(*args, **kwargs)
        print(f"✅ {name} ({time.time()-t0:.1f}s)")
        return {"ok": True, "result": str(result) if result is not None else None}
    except Exception as e:
        print(f"❌ {name}: {e}")
        traceback.print_exc()
        return {"ok": False, "error": str(e)}


def build(
    *,
    skater_lookback: int | None = None,
    skip_skaters: bool = False,
    skip_instat: bool = False,
    skip_lld: bool = False,
    skip_teams: bool = False,
) -> Path:
    ensure_dirs()
    lookback = skater_lookback or int(os.getenv("WAREHOUSE_SKATER_LOOKBACK", "40"))
    report = {
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "steps": {},
    }

    if not skip_lld:
        from ingest_lld_goalies import ingest as ingest_lld

        report["steps"]["lld_goalies"] = _run("lld_goalies", ingest_lld)

    # Skaters first so team PBP microstats exist before APGR team merge.
    if not skip_skaters:
        from nhl_skater_game_microstats import main as skater_main

        season_bf = os.getenv("WAREHOUSE_SEASON_BACKFILL", "").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        report["steps"]["skater_pbp"] = _run(
            "skater_pbp", skater_main, lookback, season_backfill=season_bf
        )

    if not skip_teams:
        from ingest_apgr_teams import ingest as ingest_teams

        report["steps"]["apgr_teams"] = _run("apgr_teams", ingest_teams)

    if not skip_instat:
        from ingest_instat import ingest as ingest_instat

        skip_live = os.getenv("INSTAT_SKIP_LIVE", "").strip() == "1"
        report["steps"]["instat"] = _run("instat", ingest_instat, not skip_live)

    # Index manifest
    manifest = {
        "updated_at": report["updated_at"],
        "stores": {
            "teams": str(CURATED / "teams_season.json"),
            "skaters_nhl_pbp": str(CURATED / "skaters_season.json"),
            "skaters_instat": str(CURATED / "skaters" / "instat_season_flat.json"),
            "goalies_lld": str(CURATED / "goalies_season.json"),
            "goalies_instat_league": str(CURATED / "goalies" / "instat_league.json"),
            "goalies_instat_aggs": str(CURATED / "goalies" / "instat_aggs.json"),
            "status_instat": str(CURATED / "status" / "instat.json"),
            "status_lld": str(CURATED / "status" / "lld_goalies.json"),
        },
        "build": report["steps"],
    }
    out = CURATED / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2))
    (CURATED / "status" / "last_build.json").write_text(json.dumps(report, indent=2))
    print(f"📦 Warehouse manifest → {out}")
    return out


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--skater-lookback", type=int, default=None)
    p.add_argument("--skip-skaters", action="store_true")
    p.add_argument("--skip-instat", action="store_true")
    p.add_argument("--skip-lld", action="store_true")
    p.add_argument("--skip-teams", action="store_true")
    args = p.parse_args()
    build(
        skater_lookback=args.skater_lookback,
        skip_skaters=args.skip_skaters,
        skip_instat=args.skip_instat,
        skip_lld=args.skip_lld,
        skip_teams=args.skip_teams,
    )
