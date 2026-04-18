#!/usr/bin/env python3
"""
Build data/playoff_scoring_calibration.json from:
  (1) NHL Web API schedule: playoff games (gameType 3) with final scores — empirical combined GPG.
  (2) ScorePredictionModel: mean of (away_expected + home_expected) over all team pairs — model scale.

Run after updating team stats / score model inputs so the anchor tracks the current model.
  python3 scripts/build_playoff_scoring_calibration.py
"""
from __future__ import annotations

import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import requests

_PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT))
sys.path.insert(0, str(_PROJECT / "models"))

from score_prediction_model import ScorePredictionModel  # noqa: E402

SCHEDULE_URL = "https://api-web.nhle.com/v1/schedule/{:%Y-%m-%d}"

# Approximate playoff windows (fetch schedule each day; cheap games filter to gameType 3).
# Multi-year windows (~75 days each). Trim if you need a faster local run.
PLAYOFF_WINDOWS: list[tuple[date, date]] = [
    (date(2022, 4, 18), date(2022, 6, 28)),
    (date(2023, 4, 17), date(2023, 6, 28)),
    (date(2024, 4, 17), date(2024, 6, 28)),
    (date(2025, 4, 18), date(2025, 6, 28)),
]


def _iter_dates(a: date, b: date):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


def fetch_playoff_combined_goals() -> tuple[list[int], int]:
    """Returns (list of home+away total goals per playoff game, http_calls)."""
    totals: list[int] = []
    calls = 0
    seen_ids: set[int] = set()
    for start, end in PLAYOFF_WINDOWS:
        for d in _iter_dates(start, end):
            url = SCHEDULE_URL.format(d)
            try:
                r = requests.get(url, timeout=25)
                calls += 1
                if r.status_code != 200:
                    continue
                data = r.json()
            except Exception:
                continue
            for week in data.get("gameWeek") or []:
                for g in week.get("games") or []:
                    if g.get("gameType") != 3:
                        continue
                    st = g.get("gameState")
                    if st not in ("OFF", "FINAL"):
                        continue
                    gid = g.get("id")
                    if gid in seen_ids:
                        continue
                    seen_ids.add(int(gid))
                    at = g.get("awayTeam") or {}
                    ht = g.get("homeTeam") or {}
                    try:
                        ascr = int(at.get("score"))
                        hscr = int(ht.get("score"))
                    except (TypeError, ValueError):
                        continue
                    totals.append(ascr + hscr)
            time.sleep(0.12)
    return totals, calls


def compute_model_lambda_mean() -> tuple[float, int]:
    m = ScorePredictionModel()
    teams = sorted((m.team_stats.get("teams") or {}).keys()) if getattr(m, "team_stats", None) else []
    if len(teams) < 4:
        return 5.5, 0
    sums: list[float] = []
    for away in teams:
        for home in teams:
            if away == home:
                continue
            ps = m.predict_score(away, home)
            sums.append(float(ps.get("away_expected") or 0) + float(ps.get("home_expected") or 0))
    return float(np.mean(sums)), len(sums)


def main() -> None:
    out_path = _PROJECT / "data" / "playoff_scoring_calibration.json"
    print("Fetching NHL playoff game totals (gameType 3)...")
    totals, calls = fetch_playoff_combined_goals()
    print(f"  HTTP calls: {calls}, playoff games with scores: {len(totals)}")
    if len(totals) < 50:
        print("::warning::Few playoff games fetched; check network or API. Using available sample.")

    arr = np.array(totals, dtype=np.float64) if totals else np.array([5.5])
    emp_mean = float(np.mean(arr))
    emp_std = float(np.std(arr)) if len(arr) > 1 else 1.2
    p05, p50, p95 = [float(x) for x in np.percentile(arr, [5, 50, 95])]

    print("Computing model combined-λ mean over all team pairs...")
    model_mean, n_pairs = compute_model_lambda_mean()
    print(f"  model_mean={model_mean:.4f} over {n_pairs} ordered pairs")

    scale = emp_mean / model_mean if model_mean > 1e-6 else 1.0
    # λ bounds: data-driven band (mean ± k·σ), clamped to plausible Poisson means
    lam_floor = max(1.75, emp_mean - 2.0 * emp_std)
    lam_ceiling = min(8.25, emp_mean + 2.0 * emp_std)

    payload = {
        "source": "scripts/build_playoff_scoring_calibration.py",
        "nhl_schedule_api": "https://api-web.nhle.com/v1/schedule/{date}",
        "playoff_windows_utc": [[a.isoformat(), b.isoformat()] for a, b in PLAYOFF_WINDOWS],
        "nhl_playoff_combined_goals": {
            "n_games": len(totals),
            "mean": round(emp_mean, 4),
            "std": round(emp_std, 4),
            "p05": round(p05, 3),
            "p50": round(p50, 3),
            "p95": round(p95, 3),
        },
        "model_combined_lambda_mean": round(model_mean, 4),
        "model_combined_lambda_n_pairs": n_pairs,
        "calibration": {
            "scale_raw_lambda_to_match_nhl_mean": round(scale, 6),
            "poisson_mean_floor": round(lam_floor, 4),
            "poisson_mean_ceiling": round(lam_ceiling, 4),
            "method": "lam_eff = clip(raw * (nhl_mean / model_lambda_mean), floor, ceiling); raw = λ_away+λ_home from predict_score",
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
