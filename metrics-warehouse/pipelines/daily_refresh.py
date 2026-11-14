#!/usr/bin/env python3
"""Daily entrypoint for personal metric warehouse (CI / scheduled).

Default: append-only since last curated run (no historical PBP refetch).
Full season rebuild only when WAREHOUSE_FULL_REBUILD=1.

Runs InStat live when auth secrets or header cache are available.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipelines"))

from auth_env import prepare_instat_auth  # noqa: E402
from build_warehouse import build  # noqa: E402
from incremental_store import env_flag, want_full_rebuild  # noqa: E402


def _prior_game_count() -> int:
    from paths import CURATED
    import json

    for name in ("skaters_season.json", "teams/nhl_pbp_microstats.json"):
        p = CURATED / name if "/" not in name else CURATED.joinpath(*name.split("/"))
        if not p.exists():
            continue
        try:
            d = json.loads(p.read_text())
            n = d.get("game_count") or len(d.get("processed_games") or [])
            if n:
                return int(n)
        except Exception:
            continue
    return 0


def main() -> int:
    lookback = int(os.getenv("WAREHOUSE_SKATER_LOOKBACK", "60"))
    skip_instat = env_flag("WAREHOUSE_SKIP_INSTAT", False)
    full_rebuild = want_full_rebuild()
    # Season-scoped game discovery stays on (current RS finals only).
    # Append is the default; full rebuild is explicit.
    os.environ["WAREHOUSE_SEASON_BACKFILL"] = "1"
    if full_rebuild:
        os.environ["WAREHOUSE_FULL_REBUILD"] = "1"
        print("🧱 FULL rebuild — all completed RS games (explicit)")
        lookback = max(lookback, 9999)
    else:
        os.environ.pop("WAREHOUSE_FULL_REBUILD", None)
        print("⚡ APPEND mode — only games since last curated run")

    prior = _prior_game_count()
    if prior:
        print(f"📊 prior curated game_count={prior}")

    if not skip_instat:
        live = prepare_instat_auth()
        if live:
            os.environ.pop("INSTAT_SKIP_LIVE", None)
        else:
            os.environ["INSTAT_SKIP_LIVE"] = "1"

    build(
        skater_lookback=lookback,
        skip_instat=skip_instat,
    )

    try:
        from instat_action_pbp import aggregate_if_ready

        aggregate_if_ready()
    except Exception as e:
        print(f"⚠️ instat_action_pbp status skipped: {e}")

    # Sequence + boards: append new games only unless full rebuild
    try:
        import json
        from paths import CURATED
        from nhl_skater_game_microstats import season_completed_game_ids
        from sequence_extensions import aggregate as seq_aggregate
        from boards_v5 import run as boards_v5_run
        from incremental_store import load_json, new_game_ids, processed_game_set

        all_ids = season_completed_game_ids()
        seq_prior = load_json(CURATED / "sequence_extensions.json")
        if full_rebuild:
            print(f"🔗 sequence FULL over {len(all_ids)} RS games")
            seq_aggregate(all_ids, merge_existing=False)
        else:
            already = processed_game_set(seq_prior)
            fresh = new_game_ids(all_ids, already)
            print(f"🔗 sequence APPEND prior={len(already)} new={len(fresh)}")
            seq_aggregate(fresh if fresh else [], merge_existing=True)
        boards_v5_run()
    except Exception as e:
        print(f"⚠️ boards_v5 / sequence skipped: {e}")

    try:
        import json
        from paths import CURATED

        sk = json.loads((CURATED / "skaters_season.json").read_text())
        after = int(sk.get("game_count") or len(sk.get("processed_games") or []) or 0)
        mode = sk.get("mode")
        inc = json.loads((CURATED / "status" / "incremental.json").read_text()) if (
            CURATED / "status" / "incremental.json"
        ).exists() else {}
        print(
            f"📊 after curated game_count={after} mode={mode} "
            f"(Δ={after - prior:+d}) new_this_run={inc.get('new_game_count')}"
        )
        if mode not in {"season_append", "season_backfill"}:
            print(f"⚠️ unexpected mode={mode}")
        if prior and after < prior:
            print(f"⚠️ game_count shrank {prior}→{after}")
        elif after > prior:
            print(f"✅ {after - prior} new completed RS game(s) folded into warehouse")
        elif inc.get("skipped_historical_refetch"):
            print("✅ caught up — no historical refetch")
    except Exception as e:
        print(f"⚠️ post-build game_count check skipped: {e}")

    try:
        from paths import APGR, CURATED
        import shutil

        pub = APGR / "data" / "metrics_warehouse"
        pub.mkdir(parents=True, exist_ok=True)
        for name in (
            "manifest.json",
            "teams_season.json",
            "skaters_season.json",
            "goalies_season.json",
            "boards_v5.json",
            "sequence_extensions.json",
            "combined_microstats.json",
            "microstats_top5.md",
            "microstats_boards_v5.md",
        ):
            src = CURATED / name
            if src.exists():
                shutil.copy2(src, pub / name)
        for sub in ("status", "teams", "skaters", "goalies", "lines"):
            status_src = CURATED / sub
            if status_src.is_dir():
                dest = pub / sub
                dest.mkdir(parents=True, exist_ok=True)
                for f in status_src.glob("*.json"):
                    shutil.copy2(f, dest / f.name)
        print(f"📤 Published warehouse views → {pub}")
    except Exception as e:
        print(f"⚠️ Publish to APGR skipped: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
