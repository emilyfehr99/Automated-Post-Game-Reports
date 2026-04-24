from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests


NHL_API_BASE = "https://api-web.nhle.com/v1"


@dataclass(frozen=True)
class Corr:
    n: int
    pearson_r: Optional[float]
    spearman_rho: Optional[float]


def _get_json(url: str, retries: int = 5, timeout_s: int = 30) -> Dict[str, Any]:
    last_exc: Optional[Exception] = None
    headers = {
        "User-Agent": "automated-post-game-reports playoff-game-drivers",
        "Accept": "application/json",
    }
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
    return Path(".cache") / "nhl_playoff_drivers"


def fetch_pbp(game_id: str, cache_dir: Path) -> Dict[str, Any]:
    pbp_dir = cache_dir / "pbp"
    pbp_dir.mkdir(parents=True, exist_ok=True)
    p = pbp_dir / f"{game_id}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    j = _get_json(f"{NHL_API_BASE}/gamecenter/{game_id}/play-by-play")
    p.write_text(json.dumps(j), encoding="utf-8")
    return j


def fetch_landing(game_id: str, cache_dir: Path) -> Dict[str, Any]:
    """
    Lightweight endpoint with gameDate + gameType, used for fast filtering
    before downloading full play-by-play.
    """
    land_dir = cache_dir / "landing"
    land_dir.mkdir(parents=True, exist_ok=True)
    p = land_dir / f"{game_id}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    j = _get_json(f"{NHL_API_BASE}/gamecenter/{game_id}/landing")
    p.write_text(json.dumps(j), encoding="utf-8")
    return j


def load_team_game_logs(path: Path) -> pd.DataFrame:
    """
    Converts data/team_advanced_metrics.json -> one row per (team, game_id) with the per-game tactical fields.
    """
    d = json.loads(path.read_text(encoding="utf-8"))
    teams = d.get("teams", {})
    rows: List[Dict[str, Any]] = []
    for team, tdata in teams.items():
        for g in tdata.get("game_log", []) or []:
            rows.append(
                {
                    "team": team,
                    "game_id": str(g.get("game_id")),
                    # per-game metrics currently logged
                    "rapid_rebonds": g.get("rapid_rebonds"),
                    "quick_strikes": g.get("quick_strikes"),
                    "dzone_giveaways": g.get("dzone_giveaways"),
                }
            )
    df = pd.DataFrame(rows)
    # ensure numeric
    for c in ["rapid_rebonds", "quick_strikes", "dzone_giveaways"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["game_id", "team"])


def game_outcomes_from_pbp(pbp: Dict[str, Any]) -> Dict[str, Any]:
    away = pbp["awayTeam"]
    home = pbp["homeTeam"]
    game_date = str(pbp.get("gameDate") or "")
    game_type = int(pbp.get("gameType") or 0)

    # Try to use summary -> scoring, else use last goal play.
    home_score = None
    away_score = None

    try:
        home_score = int(pbp["homeTeam"]["score"])
        away_score = int(pbp["awayTeam"]["score"])
    except Exception:
        home_score = None
        away_score = None

    if home_score is None or away_score is None:
        for p in pbp.get("plays", []):
            if p.get("typeDescKey") == "goal":
                det = p.get("details") or {}
                try:
                    home_score = int(det.get("homeScore"))
                    away_score = int(det.get("awayScore"))
                except Exception:
                    pass

    if home_score is None or away_score is None:
        home_score = 0
        away_score = 0

    return {
        "game_id": str(pbp["id"]),
        "gameDate": game_date,
        "gameType": game_type,
        "home_team": str(home.get("abbrev")),
        "away_team": str(away.get("abbrev")),
        "home_goals": int(home_score),
        "away_goals": int(away_score),
    }


def _corr(x: pd.Series, y: pd.Series) -> Corr:
    df = pd.DataFrame({"x": x, "y": y}).dropna()
    n = int(len(df))
    if n < 10:
        return Corr(n=n, pearson_r=None, spearman_rho=None)
    pearson_r = float(df["x"].corr(df["y"], method="pearson"))
    spearman_rho = float(df["x"].corr(df["y"], method="spearman"))
    return Corr(n=n, pearson_r=pearson_r, spearman_rho=spearman_rho)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--playoff-start-date", default="2026-04-18", help="YYYY-MM-DD")
    ap.add_argument(
        "--team-logs",
        type=Path,
        default=Path("data") / "team_advanced_metrics.json",
    )
    ap.add_argument("--cache-dir", type=Path, default=default_cache_dir())
    ap.add_argument("--out", type=Path, default=Path("data") / "playoff_game_drivers_since_start.json")
    ap.add_argument("--max-games", type=int, default=0)
    args = ap.parse_args()

    cutoff = args.playoff_start_date
    args.cache_dir.mkdir(parents=True, exist_ok=True)

    team_games = load_team_game_logs(args.team_logs)
    game_ids = sorted(set(team_games["game_id"].astype(str).tolist()))
    # Fast prefilter: NHL gameId embeds gameType at positions 5-6 (1-indexed),
    # e.g. 2025030113 -> "03" for playoffs.
    game_ids = [gid for gid in game_ids if len(gid) >= 6 and gid[4:6] == "03"]

    # Pull outcomes for those games and filter to playoff games since cutoff
    outcomes: List[Dict[str, Any]] = []
    kept_ids: List[str] = []
    for gid in game_ids:
        landing = fetch_landing(gid, args.cache_dir)
        game_date = str(landing.get("gameDate") or "")
        game_type = int(landing.get("gameType") or 0)

        if not game_date:
            continue
        if game_date < cutoff:
            continue
        if game_type != 3:  # 3 == playoffs
            continue

        pbp = fetch_pbp(gid, args.cache_dir)
        o = game_outcomes_from_pbp(pbp)
        outcomes.append(o)
        kept_ids.append(gid)
        if args.max_games and len(outcomes) >= args.max_games:
            break

    if not outcomes:
        raise SystemExit(f"No playoff games found in team logs since {cutoff}.")

    out_df = pd.DataFrame(outcomes)

    # Expand to team-level rows for modeling: one row per team-game
    team_side = []
    for _, r in out_df.iterrows():
        team_side.append(
            {
                "game_id": r["game_id"],
                "team": r["home_team"],
                "goals_for": int(r["home_goals"]),
                "goals_against": int(r["away_goals"]),
                "win": int(r["home_goals"] > r["away_goals"]),
            }
        )
        team_side.append(
            {
                "game_id": r["game_id"],
                "team": r["away_team"],
                "goals_for": int(r["away_goals"]),
                "goals_against": int(r["home_goals"]),
                "win": int(r["away_goals"] > r["home_goals"]),
            }
        )

    outcome_team = pd.DataFrame(team_side)
    merged = outcome_team.merge(team_games, on=["game_id", "team"], how="left")

    metrics = ["rapid_rebonds", "quick_strikes", "dzone_giveaways"]
    targets = ["win", "goals_for", "goals_against"]

    ranked: Dict[str, Any] = {}
    for target in targets:
        rows = []
        for m in metrics:
            c = _corr(merged[m], merged[target])
            rows.append(
                {
                    "metric": m,
                    "n": c.n,
                    "pearson_r": c.pearson_r,
                    "spearman_rho": c.spearman_rho,
                }
            )
        # sort by abs pearson_r when available, else 0
        rows.sort(key=lambda r: abs(r["pearson_r"] or 0.0), reverse=True)
        ranked[target] = rows

    payload = {
        "generatedAtUtc": datetime.utcnow().isoformat() + "Z",
        "cutoffDate": cutoff,
        "note": "Uses per-game tactical logs in data/team_advanced_metrics.json (team.game_log) and joins to NHL PBP game outcomes; filtered to gameType==3 (playoffs) and gameDate>=cutoffDate.",
        "nGames": int(len(out_df)),
        "nTeamGames": int(len(merged)),
        "metricsAvailable": metrics,
        "targets": targets,
        "rankedCorrelations": ranked,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {args.out} (nGames={payload['nGames']}, nTeamGames={payload['nTeamGames']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

