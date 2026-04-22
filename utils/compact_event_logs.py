#!/usr/bin/env python3

"""
Compact JSONL event logs by keeping only the latest record per game_id.
Prevents unbounded growth / slow reads over time.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from utils.event_store import OUTCOME_EVENTS_PATH, PREDICTION_EVENTS_PATH, load_latest_by_game_id


def compact(path: Path) -> int:
    latest: Dict[str, dict] = load_latest_by_game_id(path)
    if not latest:
        return 0
    # stable ordering
    rows = list(latest.values())
    rows.sort(key=lambda r: (str(r.get("date") or ""), str(r.get("game_id") or "")))
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp, "w") as f:
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

