#!/usr/bin/env python3
"""Bridge to prior InStat *action* PBP logic (not gear-1).

These metrics already have real implementations — warehouse just doesn't store
NHL InStat match PBP CSVs yet. When CSVs land under curated/instat_pbp/, this
module aggregates them with the same definitions used elsewhere.

Prior sources (do not re-invent):
  - automated-scraping/player_cards/pbp_metrics.py
      Passes to the slot, Successful Entries, Botched Retrievals
  - automated-scraping/player_cards/qoc_qot.py
      Forecheck recoveries / FC-cycle shot windows
  - clarkson-analytics/pipeline/player_profiles.py
      Puck battles won/lost, Passes to Slot, Botched Retrievals, FC-to-Shot %
  - clarkson-analytics/scripts/compute_tactical_coaching_engine.py
      Battle win% by zone via pos_x bins

Gear-1 already covers (wired in ingest_instat / combine):
  - passes_to_slot ← PTTS (param 271 "Slot Pass")
  - successful_entries_instat_tagged ← ENS (param 105)

Still action-PBP-only:
  - puck_battle_win_pct_by_zone  ← "Puck battles won/lost" + zone
  - botched_retrievals_instat   ← DZ recovery → same-team turnover next event
  - fc_to_shot_pct_true         ← OZ recovery → FC/cycle shot window
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from paths import CURATED, ensure_dirs

PBP_DIR = CURATED / "instat_pbp"

# Action strings used by existing scrapers (exact InStat export labels).
BATTLE_WON = {"Puck battles won", "Puck battles won in OZ", "Puck battles won in DZ", "Puck battles won in NZ"}
BATTLE_LOST = {"Puck battles lost", "Puck battles lost in OZ", "Puck battles lost in DZ", "Puck battles lost in NZ"}
BATTLE_ANY = BATTLE_WON | BATTLE_LOST | {"Puck battles", "Puck battles in OZ"}
OZ_RECOVERY = {"Puck recoveries in OZ", "Puck recoveries"}
DZ_RECOVERY = {"Puck recoveries in DZ", "Puck recoveries"}
PASS_TO_SLOT = {"Passes to the slot"}
FC_SHOT_HINTS = {"Shots", "Shot", "Scoring chance"}  # refined by sequence window in full port


def status() -> Dict[str, Any]:
    ensure_dirs()
    files = sorted(PBP_DIR.glob("*.csv")) if PBP_DIR.exists() else []
    return {
        "pbp_dir": str(PBP_DIR),
        "csv_count": len(files),
        "ready": len(files) > 0,
        "gear1_available": ["passes_to_slot", "successful_entries_instat_tagged"],
        "pending_action_pbp": [
            "puck_battle_win_pct_by_zone",
            "botched_retrievals_instat",
            "fc_to_shot_pct_true",
        ],
        "ingest_hint": (
            "Drop NHL InStat match PBP CSVs into curated/instat_pbp/ "
            "(via automated-scraping player_cards/instat_pbp_fetch.py), then "
            "re-run this module."
        ),
    }


def aggregate_if_ready() -> Optional[Path]:
    """No-op until CSVs exist — never invent rows."""
    st = status()
    out = CURATED / "status" / "instat_action_pbp.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not st["ready"]:
        payload = {**st, "ok": False, "reason": "no_instat_pbp_csvs"}
        out.write_text(json.dumps(payload, indent=2))
        print(f"⏳ InStat action PBP not ready ({st['ingest_hint']})")
        return out
    # Full sequence port lands when first CSVs arrive; status only for now.
    payload = {**st, "ok": False, "reason": "csv_present_aggregator_pending_port"}
    out.write_text(json.dumps(payload, indent=2))
    print(f"📦 InStat action PBP: {st['csv_count']} CSVs — aggregator port next")
    return out


if __name__ == "__main__":
    aggregate_if_ready()
    print(json.dumps(status(), indent=2))
