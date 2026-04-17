#!/usr/bin/env python3
"""
Build a 5-season dataset linking regular-season team performance to playoff outcomes.

Outputs:
  - data/reg_season_cup_5yr.csv
  - data/reg_season_cup_5yr.json
  - data/reg_season_history/raw/standings_{season}.json  (legacy statsapi)
  - data/reg_season_history/raw/playoffs_carousel_{season}.json (api-web)

Each row is an end-of-regular-season team. Labels include `made_playoffs` and
`playoff_series_wins` (0–4) from `api-web` playoff-bracket series winners, plus
`won_round_1` … `won_cup` for modeling depth-of-run vs regular-season features.

Standings-derived metrics support the same features for the current season from NHL endpoints.
"""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import requests

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _SCRIPT_DIR.parent
_DATA_DIR = _PROJECT_DIR / "data"
sys.path.insert(0, str(_PROJECT_DIR / "utils"))
from playoff_bracket_outcomes import labels_for_standings_team, playoff_outcomes_from_bracket

WEB_BASE = "https://api-web.nhle.com/v1"


def _http_get_json(url: str, timeout_s: int = 30) -> dict:
    r = requests.get(url, timeout=timeout_s, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return r.json()


def fetch_standings_by_date(date_str: str) -> dict:
    url = f"{WEB_BASE}/standings/{date_str}"
    return _http_get_json(url)


def find_final_regular_season_standings_date(season: str) -> Tuple[str, dict]:
    """
    Find a date near end-of-season where standings are populated.
    We search backwards from June 30 of season end-year to April 1.
    """
    year_end = int(season[4:8])
    start = datetime(year_end, 6, 30, tzinfo=timezone.utc)
    end = datetime(year_end, 4, 1, tzinfo=timezone.utc)
    cur = start
    while cur >= end:
        d = cur.strftime("%Y-%m-%d")
        try:
            data = fetch_standings_by_date(d)
            if isinstance(data, dict) and data.get("standings"):
                return d, data
        except Exception:
            pass
        cur = cur - timedelta(days=1)
    raise RuntimeError(f"Could not locate final standings date for season={season}")


def fetch_playoffs_carousel(season: str) -> dict:
    # season like "20242025" (api-web carousel also accepts this form)
    url = f"{WEB_BASE}/playoff-series/carousel/{season}/"
    return _http_get_json(url)


def fetch_playoff_bracket(year: int) -> dict:
    # year like 2021, 2022, ...
    url = f"{WEB_BASE}/playoff-bracket/{year}"
    return _http_get_json(url)


def cache_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def extract_cup_winner_from_carousel(carousel: dict) -> Optional[str]:
    """
    Best-effort parser: find a series that looks like the Final, then return the team with 4 wins.
    Payload shapes vary, so we scan for team1/team2 nodes similar to the existing simulation script.
    """
    def walk(obj):
        if isinstance(obj, dict):
            yield obj
            for v in obj.values():
                yield from walk(v)
        elif isinstance(obj, list):
            for x in obj:
                yield from walk(x)

    finalists = []
    for node in walk(carousel):
        if not isinstance(node, dict):
            continue
        t1 = node.get("team1")
        t2 = node.get("team2")
        if not isinstance(t1, dict) or not isinstance(t2, dict):
            continue

        ab1 = t1.get("abbrev") or (t1.get("teamAbbrev", {}) if isinstance(t1.get("teamAbbrev"), dict) else {}).get("default")
        ab2 = t2.get("abbrev") or (t2.get("teamAbbrev", {}) if isinstance(t2.get("teamAbbrev"), dict) else {}).get("default")
        if not ab1 or not ab2:
            continue

        w1 = t1.get("wins") or t1.get("seriesWins") or t1.get("winCount")
        w2 = t2.get("wins") or t2.get("seriesWins") or t2.get("winCount")
        try:
            w1 = int(w1)
            w2 = int(w2)
        except Exception:
            continue

        # Some payloads contain round metadata; try to keep only likely final series
        rnd = node.get("round") or node.get("roundNumber") or node.get("seriesRound")
        try:
            rnd = int(rnd) if rnd is not None else None
        except Exception:
            rnd = None

        finalists.append((rnd, ab1, w1, ab2, w2))

    # Prefer round==4 if present
    round4 = [x for x in finalists if x[0] == 4]
    candidates = round4 if round4 else finalists
    for rnd, ab1, w1, ab2, w2 in candidates:
        if w1 >= 4 or w2 >= 4:
            return ab1 if w1 > w2 else ab2
    return None


def extract_cup_winner_from_playoff_bracket(bracket: dict) -> Optional[str]:
    """
    Best-effort parser for /v1/playoff-bracket/{year}.
    We scan for nodes containing two teams and a series score where a team has 4 wins.
    """
    # Typical shape: { "series": [ ... ] } where SCF has playoffRound==4
    if isinstance(bracket, dict) and isinstance(bracket.get("series"), list):
        finals = [s for s in bracket["series"] if isinstance(s, dict) and (s.get("playoffRound") == 4 or s.get("seriesTitle") == "Stanley Cup Final")]
        if finals:
            s = finals[0]
            ts = s.get("topSeedTeam", {}) or {}
            bs = s.get("bottomSeedTeam", {}) or {}
            ab1 = (ts.get("abbrev") or "").upper()
            ab2 = (bs.get("abbrev") or "").upper()
            try:
                w1 = int(s.get("topSeedWins"))
                w2 = int(s.get("bottomSeedWins"))
            except Exception:
                w1 = w2 = None
            if ab1 and ab2 and w1 is not None and w2 is not None:
                return ab1 if w1 > w2 else ab2

    # Fallback: scan any nested dict for the same pattern
    def walk(obj):
        if isinstance(obj, dict):
            yield obj
            for v in obj.values():
                yield from walk(v)
        elif isinstance(obj, list):
            for x in obj:
                yield from walk(x)

    for node in walk(bracket):
        if not isinstance(node, dict):
            continue
        if node.get("seriesTitle") != "Stanley Cup Final" and node.get("playoffRound") != 4:
            continue
        ts = node.get("topSeedTeam", {}) or {}
        bs = node.get("bottomSeedTeam", {}) or {}
        ab1 = (ts.get("abbrev") or "").upper()
        ab2 = (bs.get("abbrev") or "").upper()
        try:
            w1 = int(node.get("topSeedWins"))
            w2 = int(node.get("bottomSeedWins"))
        except Exception:
            continue
        if ab1 and ab2:
            return ab1 if w1 > w2 else ab2
    return None


@dataclass
class TeamSeasonRow:
    season: str
    team: str
    conference: str
    division: str
    points: int
    games_played: int
    wins: int
    losses: int
    ot_losses: int
    points_pct: float
    goals_for: int
    goals_against: int
    goal_diff: int
    league_rank_points: int
    division_rank: int
    conference_rank: int
    made_playoffs: int
    playoff_series_wins: int
    won_round_1: int
    won_round_2: int
    won_conference: int
    won_cup: int


def _safe_float(x, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def extract_rows_from_web_standings(
    standings: dict,
    season: str,
    cup_winner: Optional[str],
    playoff_teams: Set[str],
    series_wins: Dict[str, int],
) -> List[TeamSeasonRow]:
    tmp = []
    for s in standings.get("standings", []):
        team = (s.get("teamAbbrev") or {}).get("default", "")
        if not team:
            continue
        points = int(s.get("points", 0) or 0)
        gp = int(s.get("gamesPlayed", 0) or 0)
        wins = int(s.get("wins", 0) or 0)
        losses = int(s.get("losses", 0) or 0)
        ot = int(s.get("otLosses", 0) or 0)
        points_pct = _safe_float(s.get("pointPctg", 0.0), 0.0)
        gf = int(s.get("goalFor", 0) or 0)
        ga = int(s.get("goalAgainst", 0) or 0)
        gd = gf - ga
        division_rank = int(s.get("divisionSequence", 99) or 99)
        conference_rank = int(s.get("conferenceSequence", 99) or 99)
        conf = s.get("conferenceAbbrev", "")
        div = s.get("divisionAbbrev", "")

        tmp.append({
            "team": team,
            "conference": conf,
            "division": div,
            "points": points,
            "gp": gp,
            "wins": wins,
            "losses": losses,
            "ot": ot,
            "points_pct": points_pct,
            "gf": gf,
            "ga": ga,
            "gd": gd,
            "division_rank": division_rank,
            "conference_rank": conference_rank,
        })

    # League rank by points (tie-break ignored; acceptable for a learning signal)
    tmp_sorted = sorted(tmp, key=lambda x: x["points"], reverse=True)
    league_rank = {t["team"]: i + 1 for i, t in enumerate(tmp_sorted)}

    rows: List[TeamSeasonRow] = []
    for t in tmp:
        team = t["team"]
        labs = labels_for_standings_team(team, playoff_teams, series_wins, cup_winner)
        rows.append(TeamSeasonRow(
            season=season,
            team=team,
            conference=t["conference"],
            division=t["division"],
            points=t["points"],
            games_played=t["gp"],
            wins=t["wins"],
            losses=t["losses"],
            ot_losses=t["ot"],
            points_pct=t["points_pct"],
            goals_for=t["gf"],
            goals_against=t["ga"],
            goal_diff=t["gd"],
            league_rank_points=int(league_rank.get(team, 99)),
            division_rank=t["division_rank"],
            conference_rank=t["conference_rank"],
            made_playoffs=int(labs["made_playoffs"]),
            playoff_series_wins=int(labs["playoff_series_wins"]),
            won_round_1=int(labs["won_round_1"]),
            won_round_2=int(labs["won_round_2"]),
            won_conference=int(labs["won_conference"]),
            won_cup=int(labs["won_cup"]),
        ))
    return rows


def main():
    seasons = [
        "20202021",
        "20212022",
        "20222023",
        "20232024",
        "20242025",
    ]

    out_csv = _DATA_DIR / "reg_season_cup_5yr.csv"
    out_json = _DATA_DIR / "reg_season_cup_5yr.json"
    raw_dir = _DATA_DIR / "reg_season_history" / "raw"

    all_rows: List[TeamSeasonRow] = []

    for season in seasons:
        standings_path = raw_dir / f"standings_final_{season}.json"
        carousel_path = raw_dir / f"playoffs_carousel_{season}.json"
        bracket_path = raw_dir / f"playoff_bracket_{season}.json"

        final_date, standings = find_final_regular_season_standings_date(season)
        cache_json(standings_path, {"season": season, "final_date": final_date, "payload": standings})

        year_end = int(season[4:8])
        bracket = fetch_playoff_bracket(year_end)
        cache_json(bracket_path, bracket)
        playoff_teams, series_wins = playoff_outcomes_from_bracket(bracket)

        cup_winner = None
        try:
            carousel = fetch_playoffs_carousel(season)
            cache_json(carousel_path, carousel)
            cup_winner = extract_cup_winner_from_carousel(carousel)
        except Exception:
            cup_winner = None

        if not cup_winner:
            cup_winner = extract_cup_winner_from_playoff_bracket(bracket)

        if not cup_winner:
            raise RuntimeError(f"Could not parse Cup winner for season={season} (carousel + bracket fallback failed)")

        rows = extract_rows_from_web_standings(standings, season, cup_winner, playoff_teams, series_wins)
        all_rows.extend(rows)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(all_rows[0]).keys()))
        w.writeheader()
        for r in all_rows:
            w.writerow(asdict(r))

    payload = {
        "meta": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "seasons": seasons,
            "rows": len(all_rows),
            "cup_winners": sum(r.won_cup for r in all_rows),
            "playoff_teams": sum(r.made_playoffs for r in all_rows),
            "note": "Playoff labels from api-web playoff-bracket; use made_playoffs=1 for playoff-only modeling.",
            "source": "build_regular_season_cup_dataset_5yr.py",
        },
        "rows": [asdict(r) for r in all_rows],
    }
    cache_json(out_json, payload)
    print(f"✅ Wrote {out_csv} and {out_json}")


if __name__ == "__main__":
    main()

