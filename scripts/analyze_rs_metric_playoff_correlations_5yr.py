#!/usr/bin/env python3
"""
Point-biserial / rank correlations: regular-season metrics vs playoff outcomes (5 seasons).

Uses the same rows and feature merge as train_regular_season_playoff_round_models_5yr.py:
  - data/reg_season_cup_5yr.json (standings + labels from playoff-bracket parsing)
  - data/historical/<season>/team_season_aggregate.json microstats when present

Binary targets (from dataset):
  - won_round_1 — won a first-round series (advanced past Round 1)
  - won_round_2 — won at least two series (see meta in reg_season_cup_5yr)
  - won_cup     — won Stanley Cup

"made second round" in common parlance ≈ won_round_1 here (beat R1 opponent).

Outputs:
  - data/rs_metric_playoff_correlations_5yr.json

Note: Tactical DNA metrics used in models/playoff_predictor.py (rebound_gen_rate, etc.)
live in team_advanced_metrics.json for the *current* season snapshot only; they are not
in historical team_season_aggregate.json unless you backfill them separately. This
analysis correlates **standings + merged historical microstat columns** only.
"""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

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

try:
    from scipy.stats import pearsonr, spearmanr
except ImportError:
    pearsonr = None  # type: ignore[misc, assignment]
    spearmanr = None  # type: ignore[misc, assignment]

TARGETS: dict[str, str] = {
    "won_round_1": "Won first-round series (advanced to second playoff round)",
    "won_round_2": "Won at least two playoff series (dataset label)",
    "won_cup": "Won Stanley Cup",
}

# Columns to never treat as numeric predictors
_ID_COLS = frozenset(
    {
        "season",
        "team",
        "conference",
        "division",
        "made_playoffs",
        "playoff_series_wins",
        "won_final",
        "won_conference",
    }
)


def _safe_pearson(x: np.ndarray, y: np.ndarray) -> tuple[float | None, float | None]:
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 3:
        return None, None
    x2 = x[mask].astype(float)
    y2 = y[mask].astype(float)
    if np.std(x2) < 1e-12 or np.std(y2) < 1e-12:
        return None, None
    if pearsonr is not None:
        r, p = pearsonr(x2, y2)
        return float(r), float(p)
    r = float(np.corrcoef(x2, y2)[0, 1])
    # two-sided p approx (t on n-2 df)
    n = len(x2)
    if n < 3 or abs(r) >= 1.0:
        return r, None
    t = r * math.sqrt((n - 2) / max(1e-15, 1 - r * r))
    # |t| ~ not easily without scipy; leave p None
    return r, None


def _safe_spearman(x: np.ndarray, y: np.ndarray) -> tuple[float | None, float | None]:
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 3:
        return None, None
    x2 = x[mask].astype(float)
    y2 = y[mask].astype(float)
    if np.std(x2) < 1e-12:
        return None, None
    if spearmanr is not None:
        res = spearmanr(x2, y2)
        return float(res.correlation), float(res.pvalue)
    return None, None


def _numeric_feature_columns(df: pd.DataFrame) -> list[str]:
    skip = set(_ID_COLS) | set(TARGETS.keys())
    out: list[str] = []
    for c in df.columns:
        if c in skip:
            continue
        if df[c].dtype == object:
            continue
        if str(df[c].dtype).startswith("datetime"):
            continue
        out.append(c)
    return sorted(out)


def _correlation_block(
    df: pd.DataFrame,
    target: str,
    metrics: list[str],
) -> dict[str, Any]:
    y = df[target].astype(float).values
    rows: list[dict[str, Any]] = []
    for m in metrics:
        x = pd.to_numeric(df[m], errors="coerce").astype(float).values
        r_p, p_p = _safe_pearson(x, y)
        r_s, p_s = _safe_spearman(x, y)
        rows.append(
            {
                "metric": m,
                "n_nonnull": int(np.sum(np.isfinite(x) & np.isfinite(y))),
                "pearson_r": r_p,
                "pearson_p": p_p,
                "spearman_rho": r_s,
                "spearman_p": p_s,
            }
        )
    rows.sort(key=lambda z: abs(z["pearson_r"] or 0.0), reverse=True)
    return {"target": target, "description": TARGETS[target], "by_metric": rows}


def main() -> None:
    raw = load_reg_season_cup_rows()
    df = enrich_df_with_historical_microstats(pd.DataFrame(raw))
    for t in TARGETS:
        if t not in df.columns:
            raise SystemExit(f"Dataset missing column {t} (rebuild reg_season_cup_5yr).")

    metrics = _numeric_feature_columns(df)
    if len(metrics) < 2:
        raise SystemExit("Too few numeric metric columns after load.")

    df_play = df[df["made_playoffs"] == 1].copy()

    out: dict[str, Any] = {
        "meta": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source": "analyze_rs_metric_playoff_correlations_5yr.py",
            "rows_all_teams": int(len(df)),
            "rows_playoff_teams": int(len(df_play)),
            "seasons": sorted(df["season"].astype(str).unique().tolist()),
            "targets": TARGETS,
            "note": (
                "Pearson r between each numeric RS feature and binary outcome is the point-biserial "
                "correlation (same formula). Spearman is rank-based; better for heavy-tailed metrics. "
                "won_cup is very sparse (~5 positives / 5 seasons) — interpret with caution. "
                "Playoff-only subset conditions on made_playoffs=1."
            ),
            "games_goals_projection_note": (
                "Projected series length and goals (avg_remaining_games, projected_total_goals_series, "
                "projected_goals_per_game) are produced in models/playoff_predictor.simulate_series using "
                "5-year data/playoff_series_historical_5yr.json for goals and 5yr RS-trained priors for win rates; "
                "exported by scripts/simulate_2026_playoffs_master.py — not from this correlation table."
            ),
        },
        "all_teams": [_correlation_block(df, t, metrics) for t in TARGETS],
        "playoff_teams_only": [_correlation_block(df_play, t, metrics) for t in TARGETS],
    }

    out_path = _DATA_DIR / "rs_metric_playoff_correlations_5yr.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
