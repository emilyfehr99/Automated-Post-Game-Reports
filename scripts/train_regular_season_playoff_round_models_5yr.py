#!/usr/bin/env python3
"""
Train interpretable models on **playoff teams only**: regular-season features vs playoff depth.

Targets (from build_regular_season_cup_dataset_5yr.py / playoff-bracket parsing):
  - won_round_1: won at least one best-of-7 series  - won_round_2: won at least two series
  - won_conference: won at least three (reached Stanley Cup Final)
  - won_cup: won four series

Requires:
  - data/reg_season_cup_5yr.json (standings + playoff labels)
  - data/historical/<season>/team_season_aggregate.json (microstats), optional — merged when present

Writes data/reg_season_playoff_round_models_5yr.json.

For simulations, run scripts/train_regular_season_cup_model_5yr.py to refresh
data/reg_season_team_features_current.json (same feature columns as these models).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _SCRIPT_DIR.parent
_DATA_DIR = _PROJECT_DIR / "data"

sys.path.insert(0, str(_SCRIPT_DIR))
from train_regular_season_cup_model_5yr import (  # noqa: E402
    FEATURES,
    HIST_FEATURE_PREFIXES,
    enrich_df_with_historical_microstats,
    load_reg_season_cup_rows,
)

TARGETS: List[Tuple[str, str]] = [
    ("won_round_1", "Won at least one playoff series (advanced past R1)"),
    ("won_round_2", "Won at least two playoff series"),
    ("won_conference", "Won conference finals (Stanley Cup Finalist; three series wins)"),
    ("won_cup", "Won Stanley Cup (four series)"),
]


def main() -> None:
    rows = load_reg_season_cup_rows()
    df = enrich_df_with_historical_microstats(pd.DataFrame(rows))
    if "made_playoffs" not in df.columns:
        raise SystemExit("reg_season_cup_5yr rows missing made_playoffs (rebuild dataset).")
    df = df[df["made_playoffs"] == 1].copy()
    if len(df) < 30:
        raise SystemExit(f"Too few playoff-team rows after merge: {len(df)}")

    base_feats = [f for f in FEATURES if f in df.columns]
    hist_feats = [f for f in HIST_FEATURE_PREFIXES if f in df.columns]
    used_features = list(dict.fromkeys(base_feats + hist_feats))
    if len(used_features) < 3:
        raise SystemExit("Not enough feature columns overlap for training.")

    X = df[used_features].fillna(0.0).astype(float)

    models_out: Dict[str, object] = {
        "meta": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "rows_playoff_teams": int(len(df)),
            "seasons": sorted(df["season"].unique().tolist()),
            "source": "train_regular_season_playoff_round_models_5yr.py",
            "features_used": used_features,
        },
        "targets": {},
    }

    for col, description in TARGETS:
        if col not in df.columns:
            continue
        y = df[col].astype(int)
        if y.sum() < 2 or y.sum() >= len(y) - 1:
            models_out["targets"][col] = {
                "description": description,
                "skipped": True,
                "reason": "need at least 2 positives and 2 negatives",
            }
            continue
        pipe = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        penalty="l2",
                        C=0.5,
                        class_weight="balanced",
                        solver="lbfgs",
                        max_iter=2000,
                    ),
                ),
            ]
        )
        pipe.fit(X, y)
        scaler: StandardScaler = pipe.named_steps["scaler"]
        clf: LogisticRegression = pipe.named_steps["clf"]
        coefs = {f: float(c) for f, c in zip(used_features, clf.coef_[0])}
        models_out["targets"][col] = {
            "description": description,
            "positives": int(y.sum()),
            "negatives": int(len(y) - y.sum()),
            "logistic": {"intercept": float(clf.intercept_[0]), "coef": coefs},
            "scaler": {
                "mean": {f: float(m) for f, m in zip(used_features, scaler.mean_)},
                "scale": {f: float(s) for f, s in zip(used_features, scaler.scale_)},
            },
        }

    out_path = _DATA_DIR / "reg_season_playoff_round_models_5yr.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(models_out, indent=2))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
