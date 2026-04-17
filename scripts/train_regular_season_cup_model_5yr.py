#!/usr/bin/env python3
"""
Train a simple model to quantify how regular-season performance predicts Cup wins.

Because the target is extremely imbalanced (1 Cup winner per season), this is best
treated as a *ranking* / prior model rather than a calibrated probability model.

Outputs:
  - data/reg_season_cup_model_5yr.json         (coefficients + feature stats)
  - data/cup_prior_current.json               (current-season per-team cup prior)
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
    # Prefer richer historical aggregates if present
    hist_root = _DATA_DIR / "historical"
    seasons = ["20202021", "20212022", "20222023", "20232024", "20242025"]
    hist_rows = []
    for s in seasons:
        agg_path = hist_root / s / "team_season_aggregate.json"
        if not agg_path.exists():
            continue
        try:
            agg = json.loads(agg_path.read_text())
            teams = agg.get("teams", {})
            for team, feats in teams.items():
                row = {"season": s, "team": team}
                for k, v in feats.items():
                    if isinstance(v, (int, float)):
                        row[k] = float(v)
                hist_rows.append(row)
        except Exception:
            continue

    if hist_rows:
        df = pd.DataFrame(hist_rows)
        # Create labels from playoff bracket winners derived by the dataset builder JSON (source of truth)
        label_path = _DATA_DIR / "reg_season_cup_5yr.json"
        if not label_path.exists():
            raise SystemExit("Missing data/reg_season_cup_5yr.json (run build_regular_season_cup_dataset_5yr.py).")
        labels = json.loads(label_path.read_text()).get("rows", [])
        label_map = {(r["season"], r["team"]): int(r.get("won_cup", 0)) for r in labels}
        df["won_cup"] = df.apply(lambda r: label_map.get((str(r["season"]), str(r["team"])), 0), axis=1)

        # Use a feature set intersection: core FEATURES + any HIST_FEATURE_PREFIXES that exist
        base_feats = [f for f in FEATURES if f in df.columns]
        hist_feats = [f for f in HIST_FEATURE_PREFIXES if f in df.columns]
        used_features = list(dict.fromkeys(base_feats + hist_feats))
    else:
        ds_path = _DATA_DIR / "reg_season_cup_5yr.csv"
        if not ds_path.exists():
            raise SystemExit("Missing data/reg_season_cup_5yr.csv. Run build_regular_season_cup_dataset_5yr.py first.")
        df = pd.read_csv(ds_path)
        used_features = FEATURES

    X = df[used_features].fillna(0.0).astype(float)
    y = df["won_cup"].astype(int)

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
    rows = extract_rows_from_web_standings(standings, current_season)
    cur = pd.DataFrame(rows)
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

    print("✅ Wrote data/reg_season_cup_model_5yr.json and data/cup_prior_current.json")


if __name__ == "__main__":
    main()

