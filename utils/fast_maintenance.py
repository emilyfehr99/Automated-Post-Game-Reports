#!/usr/bin/env python3
"""Parallel maintenance: Edge scrape ∥ outcomes, then team stats (shared game cache)."""

from __future__ import annotations

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _d in ("models", "analyzers", "utils", "scrapers"):
    _p = str(ROOT / _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

os.environ.setdefault("FAST_CI", "1")
os.environ.setdefault("NHL_GAME_CACHE_DIR", str(ROOT / ".cache" / "nhl_games"))


def _run_edge() -> int:
    from scrapers.daily_edge_data_scraper import DailyEdgeDataScraper

    ok = DailyEdgeDataScraper().scrape_daily_edge_data()
    return 0 if ok else 1


def _run_outcomes() -> int:
    from utils.update_game_outcomes import update_game_outcomes

    update_game_outcomes()
    return 0


def _run_team_stats() -> int:
    from utils.generate_real_team_stats import RealTeamStatsGenerator

    RealTeamStatsGenerator().generate_all_team_stats()
    return 0


def main() -> int:
    t0 = time.time()
    print("🚀 FAST MAINTENANCE: Edge ∥ outcomes → team stats")
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_edge = ex.submit(_run_edge)
        f_out = ex.submit(_run_outcomes)
        edge_ec = f_edge.result()
        out_ec = f_out.result()
    print(f"⏱️ Edge+outcomes wall: {time.time()-t0:.1f}s (edge={edge_ec}, outcomes={out_ec})")

    t1 = time.time()
    stats_ec = _run_team_stats()
    print(f"⏱️ Team stats wall: {time.time()-t1:.1f}s (ec={stats_ec})")

    t2 = time.time()
    try:
        from utils.backfill_all_outcomes import backfill_all_outcomes
        stats = backfill_all_outcomes()
        print(f"⏱️ Full outcome backfill: {time.time()-t2:.1f}s past_missing={stats.get('still_past_missing')}")
    except Exception as e:
        print(f"⚠️ Backfill warning: {e}")

    print(f"✅ Maintenance complete in {time.time()-t0:.1f}s")
    return 0 if stats_ec == 0 else stats_ec


if __name__ == "__main__":
    raise SystemExit(main())
