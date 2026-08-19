from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class FreshnessResult:
    ok: bool
    reason: str
    age_seconds: Optional[float] = None


def _file_age_seconds(path: Path) -> Optional[float]:
    try:
        st = path.stat()
        return float(time.time() - float(st.st_mtime))
    except Exception:
        return None


def require_file_fresh(path: Path, *, max_age_seconds: float, label: str) -> FreshnessResult:
    age = _file_age_seconds(path)
    if age is None:
        return FreshnessResult(False, f"{label} missing or unreadable: {path}", None)
    if age > float(max_age_seconds):
        return FreshnessResult(False, f"{label} is stale (age={age/3600.0:.1f}h > {max_age_seconds/3600.0:.1f}h): {path}", age)
    return FreshnessResult(True, f"{label} fresh (age={age/3600.0:.1f}h): {path}", age)


try:
    from season_utils import get_schedule_path, get_team_stats_path
except ImportError:
    from .season_utils import get_schedule_path, get_team_stats_path


def require_team_stats_fresh(*, max_age_hours: float = 36.0) -> FreshnessResult:
    p = get_team_stats_path()
    return require_file_fresh(p, max_age_seconds=float(max_age_hours) * 3600.0, label="team stats")


def require_schedule_fresh(*, max_age_hours: float = 36.0) -> FreshnessResult:
    p = get_schedule_path()
    return require_file_fresh(p, max_age_seconds=float(max_age_hours) * 3600.0, label="schedule cache")


def require_market_odds_fresh(market_odds: Dict[str, Any], *, max_age_hours: float = 6.0) -> FreshnessResult:
    if not isinstance(market_odds, dict) or not market_odds:
        return FreshnessResult(False, "market odds empty (scrape failed or returned no games)", None)
    now = time.time()
    ages = []
    for _k, v in market_odds.items():
        if not isinstance(v, dict):
            continue
        ts = v.get("timestamp")
        try:
            if ts is None:
                continue
            ages.append(float(now - float(ts)))
        except Exception:
            continue
    if not ages:
        return FreshnessResult(False, "market odds missing timestamps", None)
    age = float(min(ages))  # best case (most recent)
    if age > float(max_age_hours) * 3600.0:
        return FreshnessResult(False, f"market odds stale (best_age={age/3600.0:.1f}h > {max_age_hours:.1f}h)", age)
    return FreshnessResult(True, f"market odds fresh (best_age={age/3600.0:.1f}h)", age)


def fail_fast_if_stale(*, market_odds: Optional[Dict[str, Any]] = None) -> None:
    """
    Convenience wrapper used by workflows/scripts.
    Raises RuntimeError with a clear message if any critical input is stale.
    """
    checks = [
        require_team_stats_fresh(),
        require_schedule_fresh(),
    ]
    if market_odds is not None:
        checks.append(require_market_odds_fresh(market_odds))
    bad = [c for c in checks if not c.ok]
    if bad:
        raise RuntimeError(" | ".join([c.reason for c in bad]))

