#!/usr/bin/env python3
"""
Build data/playoff_series_historical_5yr.json from NHL Web API schedule data.

Aligns seasons with data/reg_season_cup_5yr.json meta (20202021–20242025 playoffs):
  - Per-game combined goals (gameType 3, final).
  - Per-series: games played and total goals, grouped by seriesUrl (best-of-7).

Used by models/playoff_predictor.py for series Monte Carlo goal draws (Poisson mean)
and reference series-length statistics. Re-run after seasons advance:
  python3 scripts/build_playoff_series_historical_5yr.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import requests

_PROJECT = Path(__file__).resolve().parent.parent
SCHEDULE_URL = "https://api-web.nhle.com/v1/schedule/{:%Y-%m-%d}"

# Playoff date windows covering 2020–21 through 2024–25 Stanley Cup playoffs (approximate).
PLAYOFF_WINDOWS: list[tuple[date, date]] = [
    (date(2021, 5, 16), date(2021, 7, 12)),
    (date(2022, 4, 18), date(2022, 6, 28)),
    (date(2023, 4, 17), date(2023, 6, 28)),
    (date(2024, 4, 17), date(2024, 6, 28)),
    (date(2025, 4, 18), date(2025, 6, 28)),
]

_SEASONS_LABEL = ["20202021", "20212022", "20222023", "20232024", "20242025"]


def _iter_dates(a: date, b: date):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


def fetch_playoff_games_by_series() -> tuple[list[int], dict[str, list[int]], int]:
    """
    Returns:
      per_game_totals: combined goals per playoff game
      series_game_totals: series_key -> list of per-game combined goals in that series
      http_calls
    """
    per_game_totals: list[int] = []
    # series_key -> list of combined goals per game in order seen
    series_goals: dict[str, list[int]] = defaultdict(list)
    seen_game_ids: set[int] = set()
    calls = 0

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
                    if gid is None or int(gid) in seen_game_ids:
                        continue
                    seen_game_ids.add(int(gid))
                    at = g.get("awayTeam") or {}
                    ht = g.get("homeTeam") or {}
                    try:
                        ascr = int(at.get("score"))
                        hscr = int(ht.get("score"))
                    except (TypeError, ValueError):
                        continue
                    combined = ascr + hscr
                    per_game_totals.append(combined)

                    # seriesUrl order flips between games (e.g. bruins-vs-mapleleafs vs mapleleafs-vs-bruins).
                    # Prefer stable team pair from seriesStatus, else sorted abbrevs.
                    ss = g.get("seriesStatus") or {}
                    top = (ss.get("topSeedTeamAbbrev") or "").strip()
                    bot = (ss.get("bottomSeedTeamAbbrev") or "").strip()
                    season = g.get("season")
                    rnd = ss.get("round")
                    if top and bot:
                        a, b = sorted([top, bot])
                        key = f"{season}|r{rnd}|{a}-{b}"
                    else:
                        aa = (at.get("abbrev") or at.get("abbreviation") or "").strip()
                        ha = (ht.get("abbrev") or ht.get("abbreviation") or "").strip()
                        surl = (g.get("seriesUrl") or "").strip()
                        if surl:
                            key = surl
                        else:
                            x, y = sorted([aa, ha])
                            key = f"{season}|{x}-{y}"
                    series_goals[key].append(combined)
            time.sleep(0.12)

    return per_game_totals, dict(series_goals), calls


def main() -> None:
    out_path = _PROJECT / "data" / "playoff_series_historical_5yr.json"
    print("Fetching NHL playoff games (gameType 3), grouping by series...")
    per_game, series_map, calls = fetch_playoff_games_by_series()
    print(f"  HTTP calls: {calls}, playoff games: {len(per_game)}, series buckets: {len(series_map)}")

    arr = np.array(per_game, dtype=np.float64) if per_game else np.array([5.5])
    pg_mean = float(np.mean(arr))
    pg_std = float(np.std(arr)) if len(arr) > 1 else 1.2
    p05, p50, p95 = [float(x) for x in np.percentile(arr, [5, 50, 95])]

    lengths: list[int] = []
    series_totals: list[int] = []
    for _key, goals in series_map.items():
        if not goals:
            continue
        n = len(goals)
        if n < 4 or n > 7:
            continue
        lengths.append(n)
        series_totals.append(int(sum(goals)))

    len_arr = np.array(lengths, dtype=np.float64) if lengths else np.array([6.0])
    tot_arr = np.array(series_totals, dtype=np.float64) if series_totals else np.array([35.0])

    hist_len: dict[str, float] = {}
    for lg in (4, 5, 6, 7):
        hist_len[str(lg)] = round(float(np.mean(len_arr == lg)), 6) if len(len_arr) else 0.0

    payload = {
        "source": "scripts/build_playoff_series_historical_5yr.py",
        "meta": {
            "seasons_covered": _SEASONS_LABEL,
            "nhl_schedule_api": "https://api-web.nhle.com/v1/schedule/{date}",
            "playoff_windows_utc": [[a.isoformat(), b.isoformat()] for a, b in PLAYOFF_WINDOWS],
            "note": (
                "Empirical playoff distributions from NHL schedule API. "
                "Series keys use seriesStatus top/bottom seeds (seriesUrl flips order between games). "
                "Win probabilities in PlayoffSeriesPredictor come from "
                "cup_prior_current.json + reg_season_playoff_round_models_5yr.json (5yr RS-trained)."
            ),
        },
        "per_game_combined_goals": {
            "n_games": len(per_game),
            "mean": round(pg_mean, 4),
            "std": round(pg_std, 4),
            "p05": round(p05, 3),
            "p50": round(p50, 3),
            "p95": round(p95, 3),
        },
        "series_length_games": {
            "n_series": len(lengths),
            "mean": round(float(np.mean(len_arr)), 4),
            "std": round(float(np.std(len_arr)), 4) if len(len_arr) > 1 else 0.0,
            "histogram_p": hist_len,
            "prob_series_goes_seven": round(float(np.mean(len_arr == 7.0)), 6) if len(len_arr) else 0.0,
        },
        "series_total_goals": {
            "n_series": len(series_totals),
            "mean": round(float(np.mean(tot_arr)), 4),
            "std": round(float(np.std(tot_arr)), 4) if len(tot_arr) > 1 else 0.0,
        },
        "poisson_series_game": {
            "method": (
                "Series goal draws use Poisson(mu) per regulation game with "
                "mu = per_game_combined_goals.mean, clipped to [floor, ceiling] from mean ± 2*std."
            ),
            "poisson_mean_floor": round(max(1.75, pg_mean - 2.0 * pg_std), 4),
            "poisson_mean_ceiling": round(min(8.25, pg_mean + 2.0 * pg_std), 4),
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
