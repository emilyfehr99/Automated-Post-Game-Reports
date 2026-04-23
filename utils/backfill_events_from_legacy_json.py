#!/usr/bin/env python3

"""
One-time backfill: populate append-only JSONL event logs from the legacy
`data/win_probability_predictions_v2.json` file.

This makes retraining deterministic and schema-stable going forward.
Safe to re-run: it appends events, but downstream compaction keeps latest per game.
"""

from __future__ import annotations

import json
from pathlib import Path

try:
    from utils.event_store import append_outcome_event, append_prediction_event
except Exception:
    # Allows running as `python3 utils/backfill_events_from_legacy_json.py`
    from event_store import append_outcome_event, append_prediction_event


def main() -> None:
    legacy = Path("data/win_probability_predictions_v2.json")
    if not legacy.exists():
        legacy = Path("win_probability_predictions_v2.json")
    if not legacy.exists():
        raise SystemExit("Legacy predictions JSON not found")

    d = json.loads(legacy.read_text())
    preds = d.get("predictions", [])
    if not isinstance(preds, list) or not preds:
        print("No legacy predictions found")
        return

    pred_n = 0
    out_n = 0
    for p in preds:
        gid = p.get("game_id")
        if not gid:
            continue

        # Prediction event: store the full row (best-effort) as the canonical prediction record
        try:
            append_prediction_event(dict(p))
            pred_n += 1
        except Exception:
            pass

        # Outcome event: if actual exists, append an outcome record
        if p.get("actual_winner") and p.get("actual_winner") not in ("", None, "TIE"):
            try:
                mu = p.get("metrics_used") or {}
                lead_after_p1 = None
                if isinstance(mu, dict) and "lead_after_p1" in mu:
                    lead_after_p1 = mu.get("lead_after_p1")
                append_outcome_event(
                    game_id=str(gid),
                    date=p.get("date"),
                    away_team=p.get("away_team"),
                    home_team=p.get("home_team"),
                    actual_away_score=p.get("actual_away_score"),
                    actual_home_score=p.get("actual_home_score"),
                    actual_winner=p.get("actual_winner"),
                    lead_after_p1=lead_after_p1,
                )
                out_n += 1
            except Exception:
                pass

    print(f"BACKFILL_PREDICTIONS={pred_n}")
    print(f"BACKFILL_OUTCOMES={out_n}")


if __name__ == "__main__":
    main()

