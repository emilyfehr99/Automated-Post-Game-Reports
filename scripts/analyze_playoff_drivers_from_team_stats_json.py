from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests

NHL_API_BASE = "https://api-web.nhle.com/v1"


def _get_json(url: str, retries: int = 5, timeout_s: int = 30) -> Dict[str, Any]:
    last_exc: Optional[Exception] = None
    headers = {"User-Agent": "automated-post-game-reports playoff-drivers-team-stats", "Accept": "application/json"}
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=timeout_s)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last_exc = e
            time.sleep(min(8.0, 0.5 * (2**attempt)) + 0.05 * attempt)
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("Failed to fetch JSON")


def default_cache_dir() -> Path:
    return Path(".cache") / "nhl_playoff_drivers_team_stats"


def fetch_landing(game_id: str, cache_dir: Path) -> Dict[str, Any]:
    land_dir = cache_dir / "landing"
    land_dir.mkdir(parents=True, exist_ok=True)
    p = land_dir / f"{game_id}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    j = _get_json(f"{NHL_API_BASE}/gamecenter/{game_id}/landing")
    p.write_text(json.dumps(j), encoding="utf-8")
    return j


def fetch_pbp(game_id: str, cache_dir: Path) -> Dict[str, Any]:
    pbp_dir = cache_dir / "pbp"
    pbp_dir.mkdir(parents=True, exist_ok=True)
    p = pbp_dir / f"{game_id}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    j = _get_json(f"{NHL_API_BASE}/gamecenter/{game_id}/play-by-play")
    p.write_text(json.dumps(j), encoding="utf-8")
    return j


def _to_game_id(v: Any) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip()
    if len(s) >= 10 and s[:10].isdigit():
        return s[:10]
    return None


def extract_team_game_rows(team_stats_path: Path) -> pd.DataFrame:
    """
    Converts season_2025_2026_team_stats.json into one row per team-game-side:
    columns include team, side(home/away), game_id, and metric values for that game.
    """
    d = json.loads(team_stats_path.read_text(encoding="utf-8"))
    teams = d.get("teams", {})
    rows: List[Dict[str, Any]] = []

    for team, team_blob in teams.items():
        for side in ("home", "away"):
            blob = team_blob.get(side) or {}
            games = blob.get("games") or []
            # Identify per-game metric arrays (numeric lists) that align with games index.
            metric_keys = [k for k, v in blob.items() if isinstance(v, list) and k != "games"]
            for i, g in enumerate(games):
                gid = _to_game_id(g)
                if gid is None:
                    continue
                r: Dict[str, Any] = {"team": team, "side": side, "game_id": gid}
                for mk in metric_keys:
                    arr = blob.get(mk) or []
                    if i >= len(arr):
                        continue
                    val = arr[i]
                    # attempt numeric
                    try:
                        r[mk] = float(val)
                    except Exception:
                        continue
                rows.append(r)

    df = pd.DataFrame(rows)
    return df.drop_duplicates(subset=["team", "side", "game_id"])


def outcomes_for_games(game_ids: List[str], cache_dir: Path, cutoff_date: str) -> pd.DataFrame:
    out = []
    for gid in game_ids:
        # quick filter using landing
        land = fetch_landing(gid, cache_dir)
        game_date = str(land.get("gameDate") or "")
        game_type = int(land.get("gameType") or 0)
        if not game_date or game_date < cutoff_date or game_type != 3:
            continue
        pbp = fetch_pbp(gid, cache_dir)
        home = pbp.get("homeTeam", {})
        away = pbp.get("awayTeam", {})
        out.append(
            {
                "game_id": str(pbp.get("id")),
                "gameDate": str(pbp.get("gameDate") or game_date),
                "home_team": str(home.get("abbrev") or ""),
                "away_team": str(away.get("abbrev") or ""),
                "home_goals": int(home.get("score") or 0),
                "away_goals": int(away.get("score") or 0),
            }
        )
    return pd.DataFrame(out)


def rank_metric_diffs(
    merged: pd.DataFrame, metric_cols: List[str], target_col: str
) -> List[Dict[str, Any]]:
    rows = []
    for m in metric_cols:
        s = merged[m]
        t = merged[target_col]
        df = pd.DataFrame({"x": s, "y": t}).dropna()
        n = int(len(df))
        if n < 10:
            pearson = None
            spearman = None
        else:
            pearson = float(df["x"].corr(df["y"], method="pearson"))
            spearman = float(df["x"].corr(df["y"], method="spearman"))
        rows.append({"metric_diff": m, "n": n, "pearson_r": pearson, "spearman_rho": spearman})
    # Prefer metrics with enough samples; then sort by |pearson|.
    rows.sort(
        key=lambda r: (
            0 if (r["pearson_r"] is not None and r["n"] >= 10) else 1,
            -abs(r["pearson_r"] or 0.0),
            -r["n"],
        )
    )
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--playoff-start-date", default="2026-04-18", help="YYYY-MM-DD")
    ap.add_argument(
        "--team-stats",
        type=Path,
        default=Path("data") / "season_2025_2026_team_stats.json",
    )
    ap.add_argument("--cache-dir", type=Path, default=default_cache_dir())
    ap.add_argument("--out", type=Path, default=Path("data") / "playoff_drivers_from_team_stats.json")
    ap.add_argument("--max-games", type=int, default=0)
    args = ap.parse_args()

    args.cache_dir.mkdir(parents=True, exist_ok=True)

    team_games = extract_team_game_rows(args.team_stats)

    # playoff gameIds embed gameType == 03 (positions 5-6)
    candidate_game_ids = sorted(set(g for g in team_games["game_id"].astype(str).tolist() if len(g) >= 6 and g[4:6] == "03"))

    if args.max_games and args.max_games > 0:
        candidate_game_ids = candidate_game_ids[: args.max_games]

    outcomes = outcomes_for_games(candidate_game_ids, args.cache_dir, args.playoff_start_date)
    if outcomes.empty:
        raise SystemExit(f"No playoff outcomes found since {args.playoff_start_date}.")

    # join: home side rows for home_team, away side rows for away_team
    home_rows = team_games[team_games["side"] == "home"].rename(columns={"team": "home_team"}).copy()
    away_rows = team_games[team_games["side"] == "away"].rename(columns={"team": "away_team"}).copy()

    merged = outcomes.merge(home_rows, on=["game_id", "home_team"], how="left", suffixes=("", "_home"))
    merged = merged.merge(away_rows, on=["game_id", "away_team"], how="left", suffixes=("", "_away"))

    # identify shared metric columns that exist for both (home side and away side)
    metric_keys = sorted(set(team_games.columns) - {"team", "side", "game_id"})
    diff_cols = []
    for k in metric_keys:
        h = k
        a = k + "_away"
        if h in merged.columns and a in merged.columns:
            diff = f"diff__{k}"
            merged[diff] = pd.to_numeric(merged[h], errors="coerce") - pd.to_numeric(merged[a], errors="coerce")
            diff_cols.append(diff)

    merged["home_win"] = (merged["home_goals"] > merged["away_goals"]).astype(int)
    merged["goal_diff"] = (merged["home_goals"] - merged["away_goals"]).astype(int)

    ranked = {
        "home_win": rank_metric_diffs(merged, diff_cols, "home_win"),
        "home_goals": rank_metric_diffs(merged, diff_cols, "home_goals"),
        "away_goals": rank_metric_diffs(merged, diff_cols, "away_goals"),
        "goal_diff": rank_metric_diffs(merged, diff_cols, "goal_diff"),
    }

    payload = {
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "cutoffDate": args.playoff_start_date,
        "nGames": int(len(outcomes)),
        "note": "Computes correlations between (home_metric - away_metric) from season_2025_2026_team_stats.json per-game arrays and playoff outcomes since cutoffDate. Metrics with n<10 have correlations omitted.",
        "rankedCorrelations": ranked,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {args.out} (nGames={payload['nGames']}, nDiffMetrics={len(diff_cols)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

