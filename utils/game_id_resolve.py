#!/usr/bin/env python3
"""Resolve synthetic matchup keys (AWAY@HOME_YYYY-MM-DD) to official NHL game IDs."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Iterable, Optional, Tuple

import requests

_MATCHUP_RE = re.compile(
    r"^([A-Z]{2,3})@([A-Z]{2,3})(?:_(\d{4}-\d{2}-\d{2}))?$"
)


def is_valid_nhl_game_id(game_id) -> bool:
    s = str(game_id or "")
    return s.isdigit() and len(s) >= 8


def parse_matchup_key(game_id) -> Optional[Tuple[str, str, Optional[str]]]:
    m = _MATCHUP_RE.match(str(game_id or ""))
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def fetch_schedule_day(date_str: str, session: Optional[requests.Session] = None) -> list:
    sess = session or requests.Session()
    sess.headers.setdefault("User-Agent", "Mozilla/5.0")
    try:
        resp = sess.get(f"https://api-web.nhle.com/v1/schedule/{date_str}", timeout=8)
        if resp.status_code != 200:
            return []
        data = resp.json()
        games = []
        for day in data.get("gameWeek") or []:
            if day.get("date") == date_str:
                games.extend(day.get("games") or [])
        return games
    except Exception:
        return []


def _lookup_matchup(
    away: str,
    home: str,
    day: str,
    cache: Dict[str, list],
    session: Optional[requests.Session] = None,
) -> Optional[str]:
    if day not in cache:
        cache[day] = fetch_schedule_day(day, session=session)
    for g in cache.get(day) or []:
        a = ((g.get("awayTeam") or {}).get("abbrev") or "").upper()
        h = ((g.get("homeTeam") or {}).get("abbrev") or "").upper()
        if a == away and h == home and g.get("id"):
            return str(g["id"])
    return None


def resolve_game_id(
    *,
    game_id=None,
    away_team: Optional[str] = None,
    home_team: Optional[str] = None,
    date: Optional[str] = None,
    schedule_cache: Optional[Dict[str, list]] = None,
    session: Optional[requests.Session] = None,
    verify_matchup: bool = True,
    nearby_days: int = 2,
) -> Optional[str]:
    """Return official NHL game id string, or None if unresolved.

    Important: numeric IDs are verified against away/home/date when provided.
    Stale/wrong season IDs (e.g. 202502… for a 2026-10 game) are corrected.
    """
    away = (away_team or "").upper() or None
    home = (home_team or "").upper() or None
    day = date

    parsed = parse_matchup_key(game_id) if game_id else None
    if parsed:
        away = away or parsed[0]
        home = home or parsed[1]
        day = day or parsed[2]

    cache = schedule_cache if schedule_cache is not None else {}

    if is_valid_nhl_game_id(game_id) and not (verify_matchup and away and home and day):
        return str(game_id)

    if is_valid_nhl_game_id(game_id) and away and home and day:
        # Accept stored id only if it matches this matchup on this date.
        if day not in cache:
            cache[day] = fetch_schedule_day(day, session=session)
        for g in cache.get(day) or []:
            if str(g.get("id")) != str(game_id):
                continue
            a = ((g.get("awayTeam") or {}).get("abbrev") or "").upper()
            h = ((g.get("homeTeam") or {}).get("abbrev") or "").upper()
            if a == away and h == home:
                return str(game_id)
        # Wrong id for this matchup — fall through to matchup lookup.

    if not (away and home and day):
        return str(game_id) if is_valid_nhl_game_id(game_id) else None

    found = _lookup_matchup(away, home, day, cache, session=session)
    if found:
        return found

    # Phantom date rows: search nearby days for the same matchup.
    if nearby_days > 0:
        from datetime import datetime, timedelta

        try:
            base = datetime.strptime(day, "%Y-%m-%d")
        except Exception:
            return None
        for delta in range(1, nearby_days + 1):
            for candidate in (
                (base - timedelta(days=delta)).strftime("%Y-%m-%d"),
                (base + timedelta(days=delta)).strftime("%Y-%m-%d"),
            ):
                found = _lookup_matchup(away, home, candidate, cache, session=session)
                if found:
                    return found
    return None


def prefetch_schedules(dates: Iterable[str], max_workers: int = 12) -> Dict[str, list]:
    dates = sorted({d for d in dates if d})
    cache: Dict[str, list] = {}
    if not dates:
        return cache
    sess = requests.Session()
    sess.headers["User-Agent"] = "Mozilla/5.0"

    def _one(d):
        return d, fetch_schedule_day(d, session=sess)

    with ThreadPoolExecutor(max_workers=min(max_workers, max(1, len(dates)))) as ex:
        for d, games in ex.map(lambda x: _one(x), dates):
            cache[d] = games
    return cache
