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


def get_team_stats_path() -> Path:
    """
    Locate active team_stats file.
    Prefers current season (e.g. data/season_2026_2027_team_stats.json),
    then any matching pattern, falling back to data/season_2025_2026_team_stats.json.
    """
    tag = current_season_file_tag()
    candidates = [
        Path(f"data/season_{tag}_team_stats.json"),
        Path(f"season_{tag}_team_stats.json"),
    ]
    for c in candidates:
        if c.exists():
            return c

    # Search for any existing season team stats file
    matches = sorted(glob.glob("data/season_*_team_stats.json") + glob.glob("season_*_team_stats.json"), reverse=True)
    if matches:
        return Path(matches[0])

    # Default fallback
    return Path("data/season_2025_2026_team_stats.json")


def get_schedule_path() -> Path:
    """
    Locate active schedule file.
    """
    tag = current_season_file_tag()
    candidates = [
        Path(f"data/season_{tag}_schedule.json"),
        Path(f"season_{tag}_schedule.json"),
    ]
    for c in candidates:
        if c.exists():
            return c

    matches = sorted(glob.glob("data/season_*_schedule.json") + glob.glob("season_*_schedule.json"), reverse=True)
    if matches:
        return Path(matches[0])

    return Path("data/season_2025_2026_schedule.json")
