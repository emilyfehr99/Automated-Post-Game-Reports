#!/usr/bin/env python3
"""
Backfill historical regular-season metrics using the same extraction logic as the
automated post-game reports.

Writes (incrementally) under:
  data/historical/<SEASON>/
    - processed_game_ids.json
    - team_game_rows.jsonl
    - team_season_aggregate.json
    - raw/gamecenter/<GAME_ID>.json   (optional, cache)

Usage examples:
  python scripts/backfill_historical_team_metrics.py --season 20222023
  python scripts/backfill_historical_team_metrics.py --season 20222023 --start-date 2023-01-01 --end-date 2023-02-01
  python scripts/backfill_historical_team_metrics.py --season 20222023 --max-games 200
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone

# Line-buffered logs in CI (GitHub Actions)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import requests

# Allow running from repo root without PYTHONPATH
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _SCRIPT_DIR.parent  # automated-post-game-reports/
sys.path.insert(0, str(_PROJECT_DIR))
sys.path.insert(0, str(_PROJECT_DIR / "utils"))
sys.path.insert(0, str(_PROJECT_DIR / "models"))
sys.path.insert(0, str(_PROJECT_DIR / "analyzers"))

from nhl_api_client import NHLAPIClient  # utils/nhl_api_client.py
from generate_real_team_stats import RealTeamStatsGenerator  # utils/generate_real_team_stats.py
from playoff_bracket_outcomes import playoff_outcomes_from_bracket


WEB_BASE = "https://api-web.nhle.com/v1"


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def daterange(start: date, end: date) -> List[date]:
    days = []
    cur = start
    while cur <= end:
        days.append(cur)
        cur += timedelta(days=1)
    return days


def season_date_window(season: str) -> Tuple[date, date]:
    # season "YYYYYYYY" meaning YYYY-YYYY+1
    y0 = int(season[:4])
    y1 = int(season[4:])
    # broad regular-season window (we'll just ignore dates with no games)
    return date(y0, 10, 1), date(y1, 4, 30)


def load_processed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text())
        games = data.get("games", [])
        return set(str(x) for x in games)
    except Exception:
        return set()


def save_processed_ids(path: Path, ids: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"games": sorted(ids)}, indent=2))


def append_jsonl(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def fetch_playoff_bracket_json(year: int) -> dict:
    url = f"{WEB_BASE}/playoff-bracket/{year}"
    r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return r.json()


def safe_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def extract_game_ids_for_date(api: NHLAPIClient, d: date, season: str) -> List[str]:
    """
    Pull schedule for the day and extract regular-season games.
    We filter to gameType==2 and season match where available.
    """
    ds = d.strftime("%Y-%m-%d")
    sched = api.get_game_schedule(ds)
    if not sched:
        return []

    ids = []
    for day in sched.get("gameWeek", []):
        if day.get("date") != ds:
            continue
        for g in day.get("games", []):
            # gameType is int (2 regular season)
            if g.get("gameType") != 2:
                continue
            gid = g.get("id")
            if gid:
                ids.append(str(gid))
    return ids


def build_team_season_aggregate(rows_path: Path) -> dict:
    """
    Build per-team aggregates from the JSONL rows.
    For now we compute means for numeric features and counts for games.
    """
    if not rows_path.exists():
        return {"teams": {}, "meta": {"games": 0}}

    sums: Dict[str, Dict[str, float]] = {}
    counts: Dict[str, Dict[str, int]] = {}
    game_counts: Dict[str, int] = {}

    with rows_path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            team = r.get("team")
            if not team:
                continue
            game_counts[team] = game_counts.get(team, 0) + 1
            for k, v in r.get("metrics", {}).items():
                if isinstance(v, (int, float)):
                    sums.setdefault(team, {}).setdefault(k, 0.0)
                    counts.setdefault(team, {}).setdefault(k, 0)
                    sums[team][k] += float(v)
                    counts[team][k] += 1

    teams = {}
    for team in game_counts.keys():
        agg = {"games": game_counts[team]}
        for k, s in sums.get(team, {}).items():
            c = counts.get(team, {}).get(k, 0)
            if c > 0:
                agg[k] = s / c
        teams[team] = agg

    return {
        "meta": {"generated_at_utc": datetime.now(timezone.utc).isoformat()},
        "teams": teams,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", required=True, help="Season like 20222023")
    parser.add_argument("--start-date", default=None, help="YYYY-MM-DD (optional)")
    parser.add_argument("--end-date", default=None, help="YYYY-MM-DD (optional)")
    parser.add_argument("--max-games", type=int, default=0, help="Stop after processing this many games (0 = no limit)")
    parser.add_argument("--cache-raw", action="store_true", help="Cache raw gamecenter payloads under data/historical/<season>/raw/")
    parser.add_argument(
        "--playoff-teams-only",
        action="store_true",
        help="Only retain regular-season rows for teams that appear in that season's playoff bracket (api-web).",
    )
    parser.add_argument(
        "--log-each-game",
        action="store_true",
        help="Print one line per game extracted (progress i/total, matchup). Use in CI to follow the run.",
    )
    args = parser.parse_args()

    season = args.season
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent  # automated-post-game-reports/
    out_dir = project_dir / "data" / "historical" / season
    processed_path = out_dir / "processed_game_ids.json"
    rows_path = out_dir / "team_game_rows.jsonl"
    agg_path = out_dir / "team_season_aggregate.json"
    meta_path = out_dir / "backfill_meta.json"

    api = NHLAPIClient()
    # Historical sprite endpoints often 403; disable sprites to keep backfill clean/fast.
    generator = RealTeamStatsGenerator(enable_sprites=False)

    playoff_teams: Optional[Set[str]] = None
    if args.playoff_teams_only:
        year = int(season[4:8])
        try:
            bracket = fetch_playoff_bracket_json(year)
            playoff_teams, _ = playoff_outcomes_from_bracket(bracket)
            if not playoff_teams:
                print("WARNING: Bracket returned no teams; including all teams.")
                playoff_teams = None
            else:
                print(f"Playoff-teams-only: {len(playoff_teams)} teams (Cup year {year})")
        except Exception as e:
            print(f"WARNING: Could not load playoff bracket for {year}: {e}. Including all teams.")
            playoff_teams = None

    if args.start_date and args.end_date:
        start = parse_date(args.start_date)
        end = parse_date(args.end_date)
    else:
        start, end = season_date_window(season)

    processed = load_processed_ids(processed_path)
    game_ids: List[str] = []
    for d in daterange(start, end):
        game_ids.extend(extract_game_ids_for_date(api, d, season))

    # de-dupe, stable
    game_ids = sorted(set(game_ids))
    to_process = [gid for gid in game_ids if gid not in processed]
    if args.max_games and args.max_games > 0:
        to_process = to_process[: args.max_games]

    n_already = len(processed)
    n_unique_scheduled = len(game_ids)
    n_queue = len(to_process)
    # Full RS: each team plays 82 games -> team-game sides = 82 * N_teams; unique games = that / 2
    print(
        f"\n{'='*72}\n"
        f"Season {season} | schedule scan: {n_unique_scheduled} regular-season games in date window\n"
        f"  Already processed (checkpoint): {n_already}\n"
        f"  Queued this run: {n_queue}\n"
        f"  (Full league ballpark: 32 teams x 82 GP => 2624 team-game sides, 1312 unique games; varies by season.)\n"
        f"{'='*72}\n",
        flush=True,
    )
    if n_queue == 0:
        print(f"Season {season}: nothing left to process; all scheduled games already in checkpoint.", flush=True)

    new_rows: List[dict] = []
    skipped: List[str] = []
    extracted_this_run = 0
    for i, gid in enumerate(to_process, 1):
        game_data = api.get_game_center(gid)
        if not game_data or "boxscore" not in game_data:
            skipped.append(f"{gid}: missing boxscore")
            if args.log_each_game:
                print(f"[{season}] {i}/{n_queue} game_id={gid} SKIP (no boxscore)", flush=True)
            continue

        if args.cache_raw:
            raw_path = out_dir / "raw" / "gamecenter" / f"{gid}.json"
            safe_write_json(raw_path, game_data)

        box = game_data.get("boxscore", {})
        away = box.get("awayTeam", {}) or {}
        home = box.get("homeTeam", {}) or {}
        away_id = away.get("id")
        home_id = home.get("id")
        away_abbr = away.get("abbrev")
        home_abbr = home.get("abbrev")

        if not away_id or not home_id or not away_abbr or not home_abbr:
            skipped.append(f"{gid}: incomplete boxscore teams")
            if args.log_each_game:
                print(f"[{season}] {i}/{n_queue} game_id={gid} SKIP (incomplete boxscore)", flush=True)
            continue

        gdate = box.get("gameDate") or box.get("gameDateISO") or ""

        # Extract the same metrics used in the current season stats generator
        away_metrics = generator.calculate_game_metrics(game_data, away_id, is_home=False)
        home_metrics = generator.calculate_game_metrics(game_data, home_id, is_home=True)
        if not away_metrics or not home_metrics:
            skipped.append(f"{gid}: metrics extraction failed")
            if args.log_each_game:
                print(f"[{season}] {i}/{n_queue} game_id={gid} {away_abbr} @ {home_abbr} SKIP (metrics)", flush=True)
            continue

        # Normalize shape into a JSONL "team-game row"
        # Keep metadata minimal; everything else lives under metrics.
        if playoff_teams is not None:
            if away_abbr in playoff_teams:
                new_rows.append({
                    "season": season,
                    "game_id": str(gid),
                    "date": (box.get("gameDate") or box.get("gameDateISO") or ""),
                    "team": str(away_abbr),
                    "opponent": str(home_abbr),
                    "venue": "away",
                    "metrics": away_metrics,
                })
            if home_abbr in playoff_teams:
                new_rows.append({
                    "season": season,
                    "game_id": str(gid),
                    "date": (box.get("gameDate") or box.get("gameDateISO") or ""),
                    "team": str(home_abbr),
                    "opponent": str(away_abbr),
                    "venue": "home",
                    "metrics": home_metrics,
                })
        else:
            new_rows.append({
                "season": season,
                "game_id": str(gid),
                "date": (box.get("gameDate") or box.get("gameDateISO") or ""),
                "team": str(away_abbr),
                "opponent": str(home_abbr),
                "venue": "away",
                "metrics": away_metrics,
            })
            new_rows.append({
                "season": season,
                "game_id": str(gid),
                "date": (box.get("gameDate") or box.get("gameDateISO") or ""),
                "team": str(home_abbr),
                "opponent": str(away_abbr),
                "venue": "home",
                "metrics": home_metrics,
            })

        if playoff_teams is not None:
            rows_this_game = (1 if away_abbr in playoff_teams else 0) + (1 if home_abbr in playoff_teams else 0)
        else:
            rows_this_game = 2
        if rows_this_game > 0:
            extracted_this_run += 1
        if args.log_each_game:
            if rows_this_game > 0:
                print(
                    f"[{season}] {i}/{n_queue} game_id={gid} {gdate} {away_abbr} @ {home_abbr} "
                    f"OK (+{rows_this_game} team-rows)",
                    flush=True,
                )
            else:
                print(
                    f"[{season}] {i}/{n_queue} game_id={gid} {gdate} {away_abbr} @ {home_abbr} "
                    f"SKIP (playoff-teams-only: no playoff club in this game)",
                    flush=True,
                )

        processed.add(str(gid))
        if i % 25 == 0:
            append_jsonl(rows_path, new_rows)
            new_rows = []
            save_processed_ids(processed_path, processed)

    if new_rows:
        append_jsonl(rows_path, new_rows)
        save_processed_ids(processed_path, processed)

    # rebuild aggregates (fast enough for now)
    agg = build_team_season_aggregate(rows_path)
    safe_write_json(agg_path, agg)

    teams_meta = agg.get("teams", {}) if isinstance(agg, dict) else {}
    gp_list = [int(t.get("games", 0)) for t in teams_meta.values() if isinstance(t, dict)]
    meta_games = 0
    try:
        meta_games = sum(1 for _ in rows_path.open() if _.strip())
    except Exception:
        meta_games = 0

    total_ck = len(load_processed_ids(processed_path))
    season_fully_checkpointed = n_unique_scheduled > 0 and total_ck >= n_unique_scheduled

    safe_write_json(meta_path, {
        "season": season,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "date_window": {"start": start.isoformat(), "end": end.isoformat()},
        "rows_path": str(rows_path),
        "schedule_games_in_window": n_unique_scheduled,
        "checkpoint_games_before_run": n_already,
        "games_queued_this_run": n_queue,
        "games_extracted_ok_this_run": extracted_this_run,
        "games_skipped_this_run": len(skipped),
        "checkpoint_games_after_run": total_ck,
        "season_checkpoint_full": season_fully_checkpointed,
        "jsonl_row_count": meta_games,
        "aggregate_team_count": len(teams_meta),
        "aggregate_gp_min": min(gp_list) if gp_list else 0,
        "aggregate_gp_max": max(gp_list) if gp_list else 0,
    })

    ck_note = (
        "FULL — all scheduled games checkpointed"
        if season_fully_checkpointed
        else "PARTIAL — re-run with same args to finish"
    )
    print(
        f"\n{'='*72}\n"
        f"SEASON {season} COMPLETE\n"
        f"  Schedule (RS games in window): {n_unique_scheduled}\n"
        f"  Checkpoint games now: {total_ck} ({ck_note})\n"
        f"  This run: queued {n_queue} | extracted OK {extracted_this_run} | skipped {len(skipped)}\n"
        f"  JSONL rows (total lines): {meta_games} | aggregate teams: {len(teams_meta)} "
        f"| GP min/max: {min(gp_list) if gp_list else 0}/{max(gp_list) if gp_list else 0}\n"
        f"  Files: {rows_path} | {agg_path}\n"
        f"{'='*72}\n",
        flush=True,
    )
    if skipped and not args.log_each_game:
        print(
            f"  Tip: {len(skipped)} game(s) had skip/errors; use --log-each-game for per-game lines.",
            flush=True,
        )

    print(f"Backfill finished for season={season}.", flush=True)


if __name__ == "__main__":
    main()

