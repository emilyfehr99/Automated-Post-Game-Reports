#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from utils.event_store import (
    OUTCOME_EVENTS_PATH,
    PREDICTION_EVENTS_PATH,
    load_latest_by_game_id,
)


def build_view() -> Dict[str, Any]:
    preds = load_latest_by_game_id(PREDICTION_EVENTS_PATH)
    outs = load_latest_by_game_id(OUTCOME_EVENTS_PATH)

    rows: List[Dict[str, Any]] = []
    for gid, p in preds.items():
        row = dict(p)
        o = outs.get(gid) or {}
        for k in ["actual_winner", "actual_away_score", "actual_home_score"]:
            if o.get(k) is not None:
                row[k] = o.get(k)
        # Carry P1 lead into metrics_used if present
        if o.get("lead_after_p1") is not None:
            mu = row.get("metrics_used") or {}
            if not isinstance(mu, dict):
                mu = {}
            mu["lead_after_p1"] = o.get("lead_after_p1")
            row["metrics_used"] = mu
        rows.append(row)

    # Deterministic ordering
    rows.sort(key=lambda r: (str(r.get("date") or ""), str(r.get("game_id") or "")))
    return {"predictions": rows}


def write_view(out_path: Path = Path("data/win_probability_predictions_v2.json")) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    view = build_view()
    out_path.write_text(json.dumps(view, indent=2))
    return out_path


if __name__ == "__main__":
    p = write_view()
    print(f"WROTE_VIEW={p}")

