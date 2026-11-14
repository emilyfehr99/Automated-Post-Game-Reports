"""Warehouse path constants."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "curated"
RAW = ROOT / "raw"
SCHEMAS = ROOT / "schemas"
DOCS = ROOT / "docs"

CASCADE = Path(os.getenv("CASCADE_ROOT", "/Users/emilyfehr8/CascadeProjects"))

# CI layouts:
#   - nhl-goalie-hub workflow: workspace = hub, scraping at ./automated-scraping,
#     warehouse at ./metrics-warehouse (vendored), APGR checked out beside or via APGR_ROOT
#   - local CascadeProjects sibling layout
_WS = Path(os.getenv("GITHUB_WORKSPACE", "") or "")


def _resolve(env_key: str, *candidates: Path) -> Path:
    override = os.getenv(env_key, "").strip()
    if override:
        return Path(override)
    for c in candidates:
        if c and Path(c).exists():
            return Path(c)
    return Path(candidates[-1])


APGR = _resolve(
    "APGR_ROOT",
    CASCADE / "automated-post-game-reports",
    _WS / "Automated-Post-Game-Reports" if _WS else Path(""),
    _WS / "automated-post-game-reports" if _WS else Path(""),
    ROOT.parent / "automated-post-game-reports",
)
LLD = _resolve(
    "LLD_ROOT",
    CASCADE / "nhl-goalie-hub",
    _WS if _WS and (_WS / "data").exists() and (_WS / "tools").exists() else Path(""),
    ROOT.parent,  # when vendored inside goalie hub
    ROOT.parent / "nhl-goalie-hub",
)
SCRAPING = _resolve(
    "AUTOMATED_SCRAPING_ROOT",
    CASCADE / "automated-scraping",
    _WS / "automated-scraping" if _WS else Path(""),
    ROOT.parent / "automated-scraping",
)
HUDL = SCRAPING / "hudl-scraping"


def season_label(season: str | None = None) -> str:
    """20262027 → 2026-27"""
    s = season or os.getenv("NHL_SEASON", "20262027")
    if "-" in s:
        return s
    return f"{s[:4]}-{s[6:]}"


def season_id_compact(season: str | None = None) -> str:
    s = season or os.getenv("NHL_SEASON", "20262027")
    if "-" in s:
        a, b = s.split("-", 1)
        return f"{a}20{b}" if len(b) == 2 else f"{a}{b}"
    return s


def ensure_dirs() -> None:
    for p in (
        CURATED,
        RAW / "nhl_pbp",
        RAW / "instat",
        RAW / "lld",
        CURATED / "teams",
        CURATED / "skaters",
        CURATED / "goalies",
        CURATED / "status",
        CURATED / "teams",
    ):
        p.mkdir(parents=True, exist_ok=True)
