#!/usr/bin/env python3
"""Full-season warehouse backfill (NHL PBP skaters + InStat + LLD goalies + teams).

InStat season gear tables are season-scoped (one live pull covers YTD).
The gap from skipped runs is NHL PBP skater microstats across completed RS games.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipelines"))

os.environ["WAREHOUSE_SEASON_BACKFILL"] = "1"
os.environ["WAREHOUSE_FULL_REBUILD"] = "1"  # explicit full recompute


def main() -> int:
    from daily_refresh import main as daily_main

    return daily_main()


if __name__ == "__main__":
    raise SystemExit(main())
