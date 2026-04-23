#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

try:
    from utils.event_store import (
        OUTCOME_EVENTS_PATH,
        PREDICTION_EVENTS_PATH,
        load_latest_by_game_id,
    )
except Exception:
    # Allows running as `python3 utils/build_predictions_history_view.py`
    from event_store import (
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
        # Legacy compatibility: some producers write home_win_prob/away_win_prob (0..1),
        # while legacy consumers expect predicted_*_win_prob.
        try:
            if row.get("predicted_home_win_prob") is None and row.get("home_win_prob") is not None:
                row["predicted_home_win_prob"] = float(row["home_win_prob"]) * 100.0
            if row.get("predicted_away_win_prob") is None and row.get("away_win_prob") is not None:
                row["predicted_away_win_prob"] = float(row["away_win_prob"]) * 100.0
        except Exception:
            pass

        # Ensure invariants when possible (best-effort; do not crash view build).
        try:
            ph = row.get("predicted_home_win_prob")
            pa = row.get("predicted_away_win_prob")
            if ph is not None and pa is not None:
                ph = float(ph)
                pa = float(pa)
                # If these look like decimals, normalize to percents.
                if 0.0 <= ph <= 1.0 and 0.0 <= pa <= 1.0:
                    ph *= 100.0
                    pa *= 100.0
                    row["predicted_home_win_prob"] = ph
                    row["predicted_away_win_prob"] = pa
                s = ph + pa
                if s > 0 and abs(s - 100.0) > 1e-3:
                    # Renormalize (protect downstream analyses)
                    row["predicted_home_win_prob"] = 100.0 * ph / s
                    row["predicted_away_win_prob"] = 100.0 * pa / s
        except Exception:
            pass
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

