#!/usr/bin/env python3
"""Daily entrypoint for personal metric warehouse (CI / scheduled).

Runs InStat live when auth secrets or header cache are available.
Does not skip InStat merely because CI=true.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipelines"))

from auth_env import prepare_instat_auth  # noqa: E402
from build_warehouse import build  # noqa: E402


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
    skip_instat = os.getenv("WAREHOUSE_SKIP_INSTAT", "").strip().lower() in ("1", "true", "yes")
    # Default = season-to-date so every newly final RS game is pulled on each run.
    # Opt into thin incremental only with WAREHOUSE_INCREMENTAL=1.
    incremental = os.getenv("WAREHOUSE_INCREMENTAL", "").strip().lower() in ("1", "true", "yes")
    season_bf = os.getenv("WAREHOUSE_SEASON_BACKFILL", "1" if not incremental else "0").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    prior = _prior_game_count()
    if season_bf:
        os.environ["WAREHOUSE_SEASON_BACKFILL"] = "1"
        os.environ.pop("WAREHOUSE_INCREMENTAL", None)
        print("🧱 season-to-date PBP rebuild (all completed RS games — new finals auto-included)")
        lookback = max(lookback, 9999)
    else:
        print(f"⚡ incremental lookback={lookback} (WAREHOUSE_INCREMENTAL=1)")
    if prior:
        print(f"📊 prior curated game_count={prior}")

    live = False
    if not skip_instat:
        live = prepare_instat_auth()
        if live:
            os.environ.pop("INSTAT_SKIP_LIVE", None)
        else:
            # Mirror-only path (still ingest LLD instat-aggs)
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

    # Rush chains / lines / slot-against + role-safe boards (v5)
    try:
        from nhl_skater_game_microstats import season_completed_game_ids
        from sequence_extensions import aggregate as seq_aggregate
        from boards_v5 import run as boards_v5_run

        if season_bf:
            ids = season_completed_game_ids()
            print(f"🔗 sequence extensions over {len(ids)} RS games")
            seq_aggregate(ids)
        boards_v5_run()
    except Exception as e:
        print(f"⚠️ boards_v5 / sequence skipped: {e}")

    # Confirm growth / parity after rebuild (season path must keep pace with NHL finals).
    try:
        import json
        from paths import CURATED

        sk = json.loads((CURATED / "skaters_season.json").read_text())
        after = int(sk.get("game_count") or len(sk.get("processed_games") or []) or 0)
        mode = sk.get("mode")
        print(f"📊 after curated game_count={after} mode={mode} (Δ={after - prior:+d})")
        if season_bf and mode != "season_backfill":
            print("⚠️ expected mode=season_backfill for auto new-game inclusion")
        if season_bf and prior and after < prior:
            print(f"⚠️ game_count shrank {prior}→{after} — check season filter / API")
        elif season_bf and after > prior:
            print(f"✅ {after - prior} new completed RS game(s) folded into warehouse")
    except Exception as e:
        print(f"⚠️ post-build game_count check skipped: {e}")

    # Publish thin copies into APGR data for model / Discord consumers
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
