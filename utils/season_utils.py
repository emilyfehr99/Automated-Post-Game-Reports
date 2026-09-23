"""
Season Utilities for NHL Automated Post-Game Reports
Dynamically resolves season year strings (e.g., '20262027') and active file paths on disk.
"""

from __future__ import annotations

import glob
from datetime import datetime
from pathlib import Path


def current_season_string(now: datetime | None = None) -> str:
    """Return 8-digit season string like '20262027' based on current date."""
    if now is None:
        now = datetime.now()
    year = now.year
    # NHL season rolls over in July
    if now.month >= 7:
        start_year = year
        end_year = year + 1
    else:
        start_year = year - 1
        end_year = year
    return f"{start_year}{end_year}"


def current_season_file_tag(now: datetime | None = None) -> str:
    """Return file tag like '2026_2027' based on current date."""
    if now is None:
        now = datetime.now()
    year = now.year
    if now.month >= 7:
        start_year = year
        end_year = year + 1
    else:
        start_year = year - 1
        end_year = year
    return f"{start_year}_{end_year}"


def _is_valid_team_stats_file(path: Path, min_teams: int = 30) -> bool:
    """Validate that team stats file contains comprehensive venue data for at least min_teams."""
    if not path.exists():
        return False
    try:
        import json
        with open(path, "r") as f:
            d = json.load(f)
        teams = d.get("teams", d)
        if not isinstance(teams, dict) or len(teams) < min_teams:
            return False
        # Verify structure contains home/away venue breakdowns with games
        venue_teams = 0
        for team_data in teams.values():
            if isinstance(team_data, dict):
                home_games = len(team_data.get("home", {}).get("games", []))
                away_games = len(team_data.get("away", {}).get("games", []))
                if home_games > 0 or away_games > 0:
                    venue_teams += 1
        return venue_teams >= min_teams
    except Exception:
        return False


def get_team_stats_path(min_teams: int = 30) -> Path:
    """
    Locate active team_stats file.
    Prefers current season if populated with at least `min_teams` teams,
    otherwise falls back to the most recent complete season dynamically discovered on disk.
    """
    tag = current_season_file_tag()
    candidates = [
        Path(f"data/season_{tag}_team_stats.json"),
        Path(f"season_{tag}_team_stats.json"),
    ]
    for c in candidates:
        if _is_valid_team_stats_file(c, min_teams=min_teams):
            return c

    # Search for any existing season team stats file with at least min_teams in reverse sorted order
    matches = sorted(
        glob.glob("data/season_*_team_stats.json") + glob.glob("season_*_team_stats.json"),
        reverse=True,
    )
    for m in matches:
        p = Path(m)
        if _is_valid_team_stats_file(p, min_teams=min_teams):
            return p

    # Fallback to any valid season stats file with at least 1 team
    for m in matches:
        p = Path(m)
        if _is_valid_team_stats_file(p, min_teams=1):
            return p

    return Path(f"data/season_{tag}_team_stats.json")


def get_schedule_path() -> Path:
    """
    Locate active schedule file.
    Prefers current season schedule, otherwise falls back to most recent schedule on disk.
    """
    tag = current_season_file_tag()
    candidates = [
        Path(f"data/season_{tag}_schedule.json"),
        Path(f"season_{tag}_schedule.json"),
    ]
    for c in candidates:
        if c.exists():
            return c

    matches = sorted(
        glob.glob("data/season_*_schedule.json") + glob.glob("season_*_schedule.json"),
        reverse=True,
    )
    if matches:
        return Path(matches[0])

    return Path(f"data/season_{tag}_schedule.json")
