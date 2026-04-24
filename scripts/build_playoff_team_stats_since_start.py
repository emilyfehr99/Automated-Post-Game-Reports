from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Reuse existing metrics computation logic.
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
UTILS_DIR = REPO_ROOT / "utils"
if str(UTILS_DIR) not in sys.path:
    sys.path.insert(0, str(UTILS_DIR))
ANALYZERS_DIR = REPO_ROOT / "analyzers"
if str(ANALYZERS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYZERS_DIR))
MODELS_DIR = REPO_ROOT / "models"
if str(MODELS_DIR) not in sys.path:
    sys.path.insert(0, str(MODELS_DIR))

from utils.generate_real_team_stats import RealTeamStatsGenerator  # noqa: E402
from utils.nhl_api_client import NHLAPIClient  # noqa: E402


@dataclass(frozen=True)
class GameStub:
    game_id: str
    game_date: str


def _daterange(start: date, end: date) -> List[date]:
    out = []
    d = start
    while d <= end:
        out.append(d)
        d += timedelta(days=1)
    return out


def collect_playoff_game_ids_since(start_date: str, *, max_days: int = 60) -> List[GameStub]:
    """
    Uses NHL schedule endpoint to collect playoff (gameType==3) gameIds since start_date.
    """
    api = NHLAPIClient()
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.now().date()

    # Guardrail so a bad date doesn't request years of schedules.
    if (end - start).days > max_days:
        raise SystemExit(f"Refusing to scan {(end-start).days} days (> {max_days}). Increase max_days if intended.")

    stubs: Dict[str, GameStub] = {}
    for d in _daterange(start, end):
        sched = api.get_game_schedule(d.isoformat()) or {}
        for day in sched.get("gameWeek", []) or []:
            for g in day.get("games", []) or []:
                if int(g.get("gameType") or 0) != 3:
                    continue
                gid = str(g.get("id"))
                if not gid:
                    continue
                stubs[gid] = GameStub(game_id=gid, game_date=str(day.get("date") or d.isoformat()))
    return sorted(stubs.values(), key=lambda s: (s.game_date, s.game_id))


def _ensure_team_entry(teams: Dict[str, Any], abbrev: str) -> None:
    if abbrev in teams:
        return
    teams[abbrev] = {"home": {}, "away": {}}


def _append_metric(team_side: Dict[str, Any], key: str, value: Any) -> None:
    team_side.setdefault(key, [])
    team_side[key].append(value)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--playoff-start-date", default="2026-04-18", help="YYYY-MM-DD")
    ap.add_argument("--out", type=Path, default=Path("data") / "playoff_team_stats_since_start.json")
    ap.add_argument("--max-days", type=int, default=90)
    ap.add_argument("--max-games", type=int, default=0)
    ap.add_argument("--enable-sprites", action="store_true", help="Enable sprite-backed metrics (slower, may 403).")
    args = ap.parse_args()

    out_path: Path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    stubs = collect_playoff_game_ids_since(args.playoff_start_date, max_days=int(args.max_days))
    if args.max_games and args.max_games > 0:
        stubs = stubs[: args.max_games]

    gen = RealTeamStatsGenerator(enable_sprites=bool(args.enable_sprites))
    api = NHLAPIClient()

    teams: Dict[str, Any] = {}
    processed: List[str] = []
    errors: List[Dict[str, Any]] = []

    for idx, stub in enumerate(stubs, start=1):
        gid = stub.game_id
        try:
            game_data = api.get_comprehensive_game_data(gid)
            if not game_data or "boxscore" not in game_data:
                raise RuntimeError("Missing game_data/boxscore")

            box = game_data["boxscore"]
            home = box.get("homeTeam", {})
            away = box.get("awayTeam", {})
            home_abbrev = str(home.get("abbrev") or "").upper()
            away_abbrev = str(away.get("abbrev") or "").upper()
            home_id = home.get("id")
            away_id = away.get("id")
            if not home_abbrev or not away_abbrev or not home_id or not away_id:
                raise RuntimeError("Missing team abbrev/id")

            _ensure_team_entry(teams, home_abbrev)
            _ensure_team_entry(teams, away_abbrev)

            # Compute the same metrics as the season team stats generator.
            home_metrics = gen.calculate_game_metrics(game_data, home_id, is_home=True)
            away_metrics = gen.calculate_game_metrics(game_data, away_id, is_home=False)
            if not home_metrics or not away_metrics:
                raise RuntimeError("calculate_game_metrics returned None")

            # Append metrics to per-team, per-venue arrays.
            home_side = teams[home_abbrev]["home"]
            away_side = teams[away_abbrev]["away"]

            for k, v in home_metrics.items():
                _append_metric(home_side, k, v)
            for k, v in away_metrics.items():
                _append_metric(away_side, k, v)

            # Always append gameId and opponent (aligns arrays).
            _append_metric(home_side, "games", gid)
            _append_metric(home_side, "opponents", away_abbrev)
            _append_metric(home_side, "game_dates", stub.game_date)

            _append_metric(away_side, "games", gid)
            _append_metric(away_side, "opponents", home_abbrev)
            _append_metric(away_side, "game_dates", stub.game_date)

            processed.append(gid)
        except Exception as e:  # noqa: BLE001
            errors.append({"game_id": gid, "error": str(e)})

    payload = {
        "meta": {
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "playoffStartDate": args.playoff_start_date,
            "nGamesScheduled": len(stubs),
            "nGamesProcessed": len(processed),
            "nErrors": len(errors),
            "enableSprites": bool(args.enable_sprites),
        },
        "processed_games": processed,
        "errors": errors[:200],
        "teams": teams,
    }

    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} (processed={len(processed)}/{len(stubs)}, errors={len(errors)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

