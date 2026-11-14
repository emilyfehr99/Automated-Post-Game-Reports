#!/usr/bin/env python3
"""On-ice microstats from NHL shift charts × PBP events.

Honest scope: attributes SC / shots / goals for/against to skaters on ice.
Does NOT invent entries-on-ice without a reliable entry clock match.
"""

from __future__ import annotations

import json
import os
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from paths import CURATED, ensure_dirs

USER_AGENT = "metrics-warehouse/1.0"


def _clock_seconds(value: Optional[str]) -> int:
    if not value or ":" not in value:
        return 0
    m, s = value.split(":")
    return int(m) * 60 + int(s)


def fetch_shifts(game_id: str) -> List[dict]:
    url = f"https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId={game_id}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return list((json.load(resp).get("data")) or [])
    except Exception:
        return []


def fetch_pbp(game_id: str) -> Optional[dict]:
    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.load(resp)
    except Exception:
        return None


def _build_shift_index(shifts: List[dict]) -> Dict[Tuple[int, int], List[Tuple[int, int, int]]]:
    """(teamId, period) → list of (start_s, end_s, playerId)."""
    idx: Dict[Tuple[int, int], List[Tuple[int, int, int]]] = defaultdict(list)
    for sh in shifts:
        pid = sh.get("playerId")
        tid = sh.get("teamId")
        period = sh.get("period")
        if not pid or not tid or not period:
            continue
        start = _clock_seconds(sh.get("startTime"))
        end = _clock_seconds(sh.get("endTime"))
        if end < start:
            continue
        idx[(int(tid), int(period))].append((start, end, int(pid)))
    return idx


def _on_ice_at(
    idx: Dict[Tuple[int, int], List[Tuple[int, int, int]]],
    team_id: int,
    period: int,
    second: int,
) -> Set[int]:
    out: Set[int] = set()
    for start, end, pid in idx.get((team_id, period), []):
        if start <= second <= end:
            out.add(pid)
    return out


def _is_sc(x: float, y: float) -> bool:
    # same 25ft proxy as PBP microstats
    import math

    return math.sqrt((x - 89.0) ** 2 + y ** 2) <= 25.0


def process_game(game_id: str) -> Dict[int, Dict[str, Any]]:
    pbp = fetch_pbp(game_id)
    shifts = fetch_shifts(game_id)
    if not pbp or not shifts:
        return {}
    home_id = int((pbp.get("homeTeam") or {}).get("id") or 0)
    away_id = int((pbp.get("awayTeam") or {}).get("id") or 0)
    if not home_id or not away_id:
        return {}
    idx = _build_shift_index(shifts)
    players: Dict[int, Dict[str, Any]] = defaultdict(
        lambda: {
            "player_id": 0,
            "games": 0,
            "on_ice_shots_for": 0,
            "on_ice_shots_against": 0,
            "on_ice_sc_for": 0,
            "on_ice_sc_against": 0,
            "on_ice_goals_for": 0,
            "on_ice_goals_against": 0,
        }
    )

    for play in pbp.get("plays") or []:
        kind = play.get("typeDescKey")
        if kind not in {"shot-on-goal", "missed-shot", "goal"}:
            continue
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        if owner is None or details.get("xCoord") is None:
            continue
        owner = int(owner)
        period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        second = _clock_seconds(play.get("timeInPeriod"))
        x = float(details["xCoord"])
        y = float(details.get("yCoord") or 0)
        # crude SC in raw coords (not attack-flipped) — still relative danger near either net
        sc = min(
            (x - 89) ** 2 + y ** 2,
            (x + 89) ** 2 + y ** 2,
        ) ** 0.5 <= 25.0

        for_team = owner
        against = away_id if owner == home_id else home_id
        for_ice = _on_ice_at(idx, for_team, period, second)
        ag_ice = _on_ice_at(idx, against, period, second)
        # skip empty/partial benches
        if len(for_ice) < 3 or len(ag_ice) < 3:
            continue
        for pid in for_ice:
            r = players[pid]
            r["player_id"] = pid
            r["on_ice_shots_for"] += 1
            if sc:
                r["on_ice_sc_for"] += 1
            if kind == "goal":
                r["on_ice_goals_for"] += 1
        for pid in ag_ice:
            r = players[pid]
            r["player_id"] = pid
            r["on_ice_shots_against"] += 1
            if sc:
                r["on_ice_sc_against"] += 1
            if kind == "goal":
                r["on_ice_goals_against"] += 1

    for r in players.values():
        r["games"] = 1
    return dict(players)


def aggregate(
    game_ids: List[str], *, workers: int = 8, merge_existing: bool = False
) -> Dict[str, Any]:
    season: Dict[int, Dict[str, Any]] = {}
    ok: List[str] = []
    workers = max(1, int(os.getenv("WAREHOUSE_PBP_WORKERS", str(workers))))
    path = CURATED / "skaters" / "on_ice_microstats.json"

    prior_games: List[str] = []
    if merge_existing and path.exists():
        try:
            prior = json.loads(path.read_text())
            prior_games = [str(g) for g in (prior.get("processed_games") or [])]
            for pid, row in (prior.get("skaters") or {}).items():
                key = int(pid) if str(pid).isdigit() else pid
                season[key] = {k: v for k, v in row.items() if k != "rates"}
            print(f"🧊 on-ice merge: prior={len(prior_games)} + new={len(game_ids)}")
        except Exception:
            season = {}
            prior_games = []
            merge_existing = False

    if not game_ids and merge_existing and season:
        # nothing new — keep file
        print("⏭️  on-ice: no new games")
        return json.loads(path.read_text()) if path.exists() else {}

    if game_ids:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(process_game, gid): gid for gid in game_ids}
            for i, fut in enumerate(as_completed(futs), 1):
                gid = futs[fut]
                try:
                    rows = fut.result()
                except Exception:
                    rows = {}
                if rows:
                    ok.append(str(gid))
                    for pid, gstats in rows.items():
                        if pid not in season:
                            season[pid] = dict(gstats)
                            season[pid]["games"] = 0
                        agg = season[pid]
                        for k, v in gstats.items():
                            if k in {"player_id"}:
                                continue
                            if isinstance(v, (int, float)):
                                agg[k] = int(agg.get(k, 0) or 0) + int(v)
                if i % 20 == 0 or i == len(game_ids):
                    print(f"  on-ice … {i}/{len(game_ids)} ({len(ok)} ok)", flush=True)

    out = {}
    for pid, s in season.items():
        g = max(1, int(s.get("games") or 0))
        sc_f = int(s.get("on_ice_sc_for") or 0)
        sc_a = int(s.get("on_ice_sc_against") or 0)
        rates = {
            "on_ice_sc_diff_per_game": round((sc_f - sc_a) / g, 2),
            "on_ice_sc_for_per_game": round(sc_f / g, 2),
            "on_ice_sc_against_per_game": round(sc_a / g, 2),
            "on_ice_shots_diff_per_game": round(
                (int(s.get("on_ice_shots_for") or 0) - int(s.get("on_ice_shots_against") or 0)) / g,
                2,
            ),
            "source": "nhl_shiftcharts_x_pbp",
        }
        out[str(pid)] = {**s, "rates": rates}

    processed = list(dict.fromkeys([*prior_games, *[str(g) for g in ok]])) if merge_existing else [str(g) for g in ok]
    payload = {
        "processed_games": processed,
        "game_count": len(processed),
        "skaters": out,
        "skater_count": len(out),
        "note": "on-ice SC/shots/goals only; entries-on-ice not claimed",
        "merge_existing": merge_existing,
    }
    ensure_dirs()
    path.write_text(json.dumps(payload, indent=2))
    print(f"🧊 on-ice: {payload['skater_count']} skaters from {payload['game_count']} games → {path}")
    return payload


if __name__ == "__main__":
    from nhl_skater_game_microstats import recent_final_game_ids

    ids = recent_final_game_ids(int(os.getenv("WAREHOUSE_SKATER_LOOKBACK", "40")))
    aggregate(ids)
