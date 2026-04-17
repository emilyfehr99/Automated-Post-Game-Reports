#!/usr/bin/env python3
"""
Train a simple model to quantify how regular-season performance predicts Cup wins.

Because the target is extremely imbalanced (1 Cup winner per season), this is best
treated as a *ranking* / prior model rather than a calibrated probability model.

Outputs:
  - data/reg_season_cup_model_5yr.json         (coefficients + feature stats)
  - data/cup_prior_current.json               (current-season per-team cup prior)
  - data/reg_season_team_features_current.json (per-team feature row for round-depth priors in sims)
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


WEB_BASE = "https://api-web.nhle.com/v1"

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _SCRIPT_DIR.parent
_DATA_DIR = _PROJECT_DIR / "data"


FEATURES = [
    # Core quality
    "points_pct",
    "goal_diff",
    "goals_for",
    "goals_against",
    # Seeding / path proxies
    "league_rank_points",
    "division_rank",
    "conference_rank",
]

HIST_FEATURE_PREFIXES = [
    # allow richer microstats when historical aggregates exist
    "gs", "xg", "corsi_pct", "fenwick_pct", "pdo",
    "ozs", "nzs", "dzs", "period_dzs",
    "goals", "opp_goals", "shots",
    "hits", "blocked_shots", "giveaways", "takeaways", "penalty_minutes",
    "power_play_pct", "penalty_kill_pct", "faceoff_pct",
    "nzt", "nztsa", "fc", "rush",
    "hdc", "hdca", "opp_xg",
    "rebounds", "rush_shots", "cycle_shots", "forecheck_turnovers",
    "net_front_traffic_pct", "passes_per_goal", "avg_goal_distance",
    "east_west_play", "north_south_play",
    "zone_entry_carry_pct", "zone_entry_pass_pct",
]

_HIST_MICRO_KEYS = frozenset(HIST_FEATURE_PREFIXES)
_HIST_SEASONS = ("20202021", "20212022", "20222023", "20232024", "20242025")


def load_reg_season_cup_rows() -> List[dict]:
    """Standings + playoff labels from the 5-season dataset builder (required)."""
    label_path = _DATA_DIR / "reg_season_cup_5yr.json"
    if label_path.exists():
        rows = json.loads(label_path.read_text()).get("rows", [])
        if rows:
            return rows
    ds_path = _DATA_DIR / "reg_season_cup_5yr.csv"
    if ds_path.exists():
        return pd.read_csv(ds_path).to_dict(orient="records")
    raise SystemExit(
        "Missing data/reg_season_cup_5yr.json (or .csv). Run build_regular_season_cup_dataset_5yr.py."
    )


def enrich_df_with_historical_microstats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Left-join microstats from data/historical/<season>/team_season_aggregate.json.

    Training rows always come from reg_season_cup_5yr so Cup labels stay correct even
    when only some seasons or teams have been backfilled (partial aggregates).
    """
    out = df.copy()
    out["season"] = out["season"].astype(str)
    out["team"] = out["team"].astype(str).str.strip().str.upper()
    hist_root = _DATA_DIR / "historical"
    for s in _HIST_SEASONS:
        agg_path = hist_root / s / "team_season_aggregate.json"
        if not agg_path.exists():
            continue
        try:
            agg = json.loads(agg_path.read_text())
        except Exception:
            continue
        teams = agg.get("teams", {})
        for team, feats in teams.items():
            ab = str(team).strip().upper()
            mask = (out["season"] == s) & (out["team"] == ab)
            if not mask.any():
                continue
            for k, v in feats.items():
                if k == "games" or not isinstance(v, (int, float)):
                    continue
                if k not in _HIST_MICRO_KEYS:
                    continue
                out.loc[mask, k] = float(v)
    return out


def _http_get_json(url: str, timeout_s: int = 30) -> dict:
    r = requests.get(url, timeout=timeout_s, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return r.json()


def fetch_standings_by_date(date_str: str) -> dict:
    return _http_get_json(f"{WEB_BASE}/standings/{date_str}")


def extract_rows_from_web_standings(standings: dict, season: str) -> List[dict]:
    rows = []
    for s in standings.get("standings", []):
        team = (s.get("teamAbbrev") or {}).get("default", "")
        if not team:
            continue
        rows.append({
            "season": season,
            "team": team,
            "conference": s.get("conferenceAbbrev", ""),
            "division": s.get("divisionAbbrev", ""),
            "points": int(s.get("points", 0) or 0),
            "games_played": int(s.get("gamesPlayed", 0) or 0),
            "wins": int(s.get("wins", 0) or 0),
            "losses": int(s.get("losses", 0) or 0),
            "ot_losses": int(s.get("otLosses", 0) or 0),
            "points_pct": float(s.get("pointPctg") or 0.0),
            "goals_for": int(s.get("goalFor", 0) or 0),
            "goals_against": int(s.get("goalAgainst", 0) or 0),
            "goal_diff": int(s.get("goalFor", 0) or 0) - int(s.get("goalAgainst", 0) or 0),
            "division_rank": int(s.get("divisionSequence", 99) or 99),
            "conference_rank": int(s.get("conferenceSequence", 99) or 99),
        })
    tmp = sorted(rows, key=lambda r: r["points"], reverse=True)
    lr = {r["team"]: i + 1 for i, r in enumerate(tmp)}
    for r in rows:
        r["league_rank_points"] = int(lr.get(r["team"], 99))
    return rows


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def main():
    rows = load_reg_season_cup_rows()
    df = enrich_df_with_historical_microstats(pd.DataFrame(rows))

    base_feats = [f for f in FEATURES if f in df.columns]
    hist_feats = [f for f in HIST_FEATURE_PREFIXES if f in df.columns]
    used_features = list(dict.fromkeys(base_feats + hist_feats))
    if len(used_features) < 3:
        raise SystemExit("Not enough overlapping feature columns to train (check reg_season_cup_5yr dataset).")

    if "won_cup" not in df.columns:
        raise SystemExit("Dataset is missing won_cup (rebuild reg_season_cup_5yr).")

    X = df[used_features].fillna(0.0).astype(float)
    y = df["won_cup"].astype(int)
    if y.nunique() < 2:
        raise SystemExit(
            f"won_cup is single-class after load (positives={int(y.sum())}, rows={len(df)}). "
            "Rebuild data/reg_season_cup_5yr.json."
        )

    # Regularized logistic regression for interpretability
    pipe = Pipeline(steps=[
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            penalty="l2",
            C=0.5,
            class_weight="balanced",
            solver="lbfgs",
            max_iter=2000,
        )),
    ])
    pipe.fit(X, y)

    # Simple evaluation: per-season rank of actual winner
    df["score"] = pipe.predict_proba(X)[:, 1]
    winner_ranks = []
    for season, g in df.groupby("season"):
        g2 = g.sort_values("score", ascending=False).reset_index(drop=True)
        idx = int(g2.index[g2["won_cup"] == 1][0]) if (g2["won_cup"] == 1).any() else None
        winner_ranks.append({"season": season, "winner_rank": (idx + 1) if idx is not None else None})

    scaler: StandardScaler = pipe.named_steps["scaler"]
    clf: LogisticRegression = pipe.named_steps["clf"]
    coefs = {f: float(c) for f, c in zip(used_features, clf.coef_[0])}

    model_out = {
        "meta": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "rows": int(len(df)),
            "positives": int(y.sum()),
            "seasons": sorted(df["season"].unique().tolist()),
            "source": "train_regular_season_cup_model_5yr.py",
        },
        "features": FEATURES,
        "features_used": used_features,
        "scaler": {
            "mean": {f: float(m) for f, m in zip(used_features, scaler.mean_)},
            "scale": {f: float(s) for f, s in zip(used_features, scaler.scale_)},
        },
        "logistic": {
            "intercept": float(clf.intercept_[0]),
            "coef": coefs,
        },
        "winner_rank_by_season": winner_ranks,
    }

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with (_DATA_DIR / "reg_season_cup_model_5yr.json").open("w") as f:
        json.dump(model_out, f, indent=2)

    # Current-season cup priors from live standings
    current_season = "20252026"
    standings = fetch_standings_by_date("now")
    cur_rows = extract_rows_from_web_standings(standings, current_season)
    cur = pd.DataFrame(cur_rows)
    for col in used_features:
        if col not in cur.columns:
            cur[col] = 0.0
    curX = cur[used_features].fillna(0.0).astype(float)
    cur["cup_prior_score"] = pipe.predict_proba(curX)[:, 1]

    # Normalize into a "market-like" distribution summing to 1.0
    # (this is not a true probability, but works as a prior weight)
    eps = 1e-12
    s = float(cur["cup_prior_score"].sum()) + eps
    cur["cup_prior_norm"] = cur["cup_prior_score"] / s

    priors = {
        r["team"]: {
            "season": current_season,
            "cup_prior_score": float(r["cup_prior_score"]),
            "cup_prior_norm": float(r["cup_prior_norm"]),
            "points_pct": float(r["points_pct"]),
            "goal_diff": int(r["goal_diff"]),
            "league_rank_points": int(r["league_rank_points"]),
        }
        for r in cur.to_dict(orient="records")
    }

    with (_DATA_DIR / "cup_prior_current.json").open("w") as f:
        json.dump({
            "meta": {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "season": current_season,
                "source_model": "data/reg_season_cup_model_5yr.json",
            },
            "teams": priors,
        }, f, indent=2)

    # Feature rows for current season (standings + optional microstats) — used by
    # PlayoffSeriesPredictor with reg_season_playoff_round_models_5yr.json.
    team_feats: Dict[str, Dict[str, float]] = {}
    for r in cur.to_dict(orient="records"):
        ta = str(r.get("team", "")).strip().upper()
        if not ta:
            continue
        team_feats[ta] = {k: float(r[k]) for k in used_features if k in r}
    with (_DATA_DIR / "reg_season_team_features_current.json").open("w") as f:
        json.dump(
            {
                "meta": {
                    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                    "season": current_season,
                    "features_used": used_features,
                    "source": "train_regular_season_cup_model_5yr.py",
                },
                "teams": team_feats,
            },
            f,
            indent=2,
        )

    print(
        "✅ Wrote data/reg_season_cup_model_5yr.json, data/cup_prior_current.json, "
        "data/reg_season_team_features_current.json"
    )


if __name__ == "__main__":
    main()

