#!/usr/bin/env python3
"""Season pass: rush-chain length, line on-ice units, slot-drives against.

Real NHL PBP + shift charts only — no invented events.
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
RUSH_WINDOW_S = 8.0
UNBLOCKED = frozenset({"shot-on-goal", "missed-shot", "goal"})
STOPPAGES = frozenset({"stoppage", "faceoff", "period-end", "game-end", "period-start"})


def _clock(value: Optional[str]) -> int:
    if not value or ":" not in value:
        return 0
    m, s = value.split(":")
    return int(m) * 60 + int(s)


def _fetch(url: str) -> Optional[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.load(resp)
    except Exception:
        return None


def _fetch_shifts(game_id: str) -> List[dict]:
    url = f"https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId={game_id}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return list((json.load(resp).get("data")) or [])
    except Exception:
        return []


def _is_slot(x: float, y: float) -> bool:
    return abs(x) >= 54 and abs(y) <= 22 and abs(x) <= 89


def _shift_index(shifts: List[dict]) -> Dict[Tuple[int, int], List[Tuple[int, int, int]]]:
    idx: Dict[Tuple[int, int], List[Tuple[int, int, int]]] = defaultdict(list)
    for sh in shifts:
        pid, tid, period = sh.get("playerId"), sh.get("teamId"), sh.get("period")
        if not pid or not tid or not period:
            continue
        start, end = _clock(sh.get("startTime")), _clock(sh.get("endTime"))
        if end < start:
            continue
        idx[(int(tid), int(period))].append((start, end, int(pid)))
    return idx


def _on_ice(
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


def process_game(game_id: str) -> Dict[str, Any]:
    pbp = _fetch(f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play")
    if not pbp:
        return {}
    home = pbp.get("homeTeam") or {}
    away = pbp.get("awayTeam") or {}
    home_id = int(home.get("id") or 0)
    away_id = int(away.get("id") or 0)
    home_abbr = home.get("abbrev") or ""
    away_abbr = away.get("abbrev") or ""
    if not home_id or not away_id:
        return {}

    shifts = _fetch_shifts(game_id)
    sidx = _shift_index(shifts) if shifts else {}

    plays = list(pbp.get("plays") or [])
    last_poss: Dict[int, float] = {home_id: -999.0, away_id: -999.0}
    chain_events: Dict[int, int] = {home_id: 0, away_id: 0}

    team = {
        home_abbr: {
            "team": home_abbr,
            "rush_chains": 0,
            "rush_chain_events_sum": 0,
            "slot_drives_against": 0,
            "p1_entries": 0,
            "p3_entries": 0,
            "p1_sc": 0,
            "p3_sc": 0,
        },
        away_abbr: {
            "team": away_abbr,
            "rush_chains": 0,
            "rush_chain_events_sum": 0,
            "slot_drives_against": 0,
            "p1_entries": 0,
            "p3_entries": 0,
            "p1_sc": 0,
            "p3_sc": 0,
        },
    }
    tid_to_abbr = {home_id: home_abbr, away_id: away_abbr}
    skaters: Dict[int, Dict[str, Any]] = defaultdict(
        lambda: {
            "player_id": 0,
            "rush_chains": 0,
            "rush_chain_events_sum": 0,
            "games": 0,
        }
    )
    lines: Dict[str, Dict[str, Any]] = {}

    def bump_line(pids: Set[int], team_abbr: str, sc_for: bool, goal: bool) -> None:
        if len(pids) < 5:
            return
        # Use full 5-man unit on ice (F+D); honest line/pair composite.
        key_ids = tuple(sorted(pids))
        key = f"{team_abbr}:" + "-".join(str(i) for i in key_ids)
        row = lines.get(key)
        if row is None:
            row = {
                "line_id": key,
                "team": team_abbr,
                "player_ids": list(key_ids),
                "events": 0,
                "sc_for": 0,
                "sc_against": 0,
                "goals_for": 0,
                "goals_against": 0,
                "games": 0,
            }
            lines[key] = row
        row["events"] += 1
        if sc_for:
            row["sc_for"] += 1
            if goal:
                row["goals_for"] += 1
        else:
            row["sc_against"] += 1
            if goal:
                row["goals_against"] += 1

    for play in plays:
        kind = play.get("typeDescKey")
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        second = _clock(play.get("timeInPeriod"))
        game_sec = (period - 1) * 1200 + second

        if kind in {"takeaway", "giveaway"} and owner in (home_id, away_id):
            owner = int(owner)
            # possession changes hands
            if kind == "takeaway":
                last_poss[owner] = float(game_sec)
                chain_events[owner] = 0
            else:
                opp = away_id if owner == home_id else home_id
                last_poss[opp] = float(game_sec)
                chain_events[opp] = 0
            continue

        if owner not in (home_id, away_id):
            continue
        owner = int(owner)
        abbr = tid_to_abbr[owner]
        opp = away_id if owner == home_id else home_id
        opp_abbr = tid_to_abbr[opp]

        if kind not in STOPPAGES:
            if last_poss[owner] > 0 and 0 <= game_sec - last_poss[owner] <= RUSH_WINDOW_S:
                chain_events[owner] += 1

        if kind in UNBLOCKED and details.get("xCoord") is not None:
            x = float(details["xCoord"])
            y = float(details.get("yCoord") or 0)
            # attack-ish slot near either net
            slot = _is_slot(x, y) or _is_slot(-x, y)
            sc = min((x - 89) ** 2 + y ** 2, (x + 89) ** 2 + y ** 2) ** 0.5 <= 25.0
            is_rush = (
                last_poss[owner] > 0
                and 0 <= game_sec - last_poss[owner] <= RUSH_WINDOW_S
            )
            if is_rush and sc:
                n_ev = max(1, chain_events[owner])
                team[abbr]["rush_chains"] += 1
                team[abbr]["rush_chain_events_sum"] += n_ev
                pid = details.get("shootingPlayerId") or details.get("scoringPlayerId")
                if pid:
                    sk = skaters[int(pid)]
                    sk["player_id"] = int(pid)
                    sk["rush_chains"] += 1
                    sk["rush_chain_events_sum"] += n_ev

            if slot:
                team[opp_abbr]["slot_drives_against"] += 1

            if period == 1 and sc:
                team[abbr]["p1_sc"] += 1
            elif period == 3 and sc:
                team[abbr]["p3_sc"] += 1

            if sidx:
                for_ice = _on_ice(sidx, owner, period, second)
                ag_ice = _on_ice(sidx, opp, period, second)
                if len(for_ice) >= 5:
                    bump_line(for_ice, abbr, sc_for=True, goal=(kind == "goal"))
                if len(ag_ice) >= 5:
                    bump_line(ag_ice, opp_abbr, sc_for=False, goal=(kind == "goal"))

        # entry-ish: controlled carry from NZ→OZ is hard; use zone-start faceoffs skip.
        # Period entry volume already in v4; here only SC period splits above.

    for sk in skaters.values():
        sk["games"] = 1
    for ln in lines.values():
        ln["games"] = 1

    return {
        "game_id": game_id,
        "teams": team,
        "skaters": dict(skaters),
        "lines": lines,
    }


def _goalie_ids() -> Set[int]:
    path = CURATED / "goalies_season.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text())
    except Exception:
        return set()
    out: Set[int] = set()
    for gid in (data.get("goalies") or {}):
        try:
            out.add(int(gid))
        except (TypeError, ValueError):
            continue
    return out


def aggregate(game_ids: List[str], *, workers: int = 12) -> Path:
    ensure_dirs()
    workers = max(1, int(os.getenv("WAREHOUSE_PBP_WORKERS", str(workers))))
    teams: Dict[str, Dict[str, Any]] = {}
    skaters: Dict[int, Dict[str, Any]] = {}
    lines: Dict[str, Dict[str, Any]] = {}
    ok: List[str] = []
    goalie_ids = _goalie_ids()

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(process_game, gid): gid for gid in game_ids}
        for i, fut in enumerate(as_completed(futs), 1):
            gid = futs[fut]
            try:
                row = fut.result()
            except Exception:
                row = {}
            if not row:
                continue
            ok.append(gid)
            for abbr, t in (row.get("teams") or {}).items():
                if abbr not in teams:
                    teams[abbr] = {**t, "games": 0}
                agg = teams[abbr]
                agg["games"] = int(agg.get("games") or 0) + 1
                for k, v in t.items():
                    if k in {"team"}:
                        continue
                    if isinstance(v, (int, float)):
                        agg[k] = int(agg.get(k) or 0) + int(v)
            for pid, s in (row.get("skaters") or {}).items():
                if pid not in skaters:
                    skaters[pid] = {**s, "games": 0}
                agg = skaters[pid]
                agg["games"] = int(agg.get("games") or 0) + 1
                for k, v in s.items():
                    if k in {"player_id"}:
                        continue
                    if isinstance(v, (int, float)) and k != "games":
                        agg[k] = int(agg.get(k) or 0) + int(v)
            for lid, ln in (row.get("lines") or {}).items():
                pids = [int(p) for p in (ln.get("player_ids") or []) if int(p) not in goalie_ids]
                if len(pids) < 5:
                    continue
                pids = sorted(pids)[:5]  # 5 skaters only
                team_abbr = ln.get("team") or ""
                lid5 = f"{team_abbr}:" + "-".join(str(i) for i in pids)
                if lid5 not in lines:
                    lines[lid5] = {
                        **ln,
                        "line_id": lid5,
                        "player_ids": pids,
                        "games": 0,
                    }
                agg = lines[lid5]
                agg["games"] = int(agg.get("games") or 0) + 1
                for k, v in ln.items():
                    if k in {"line_id", "team", "player_ids", "games"}:
                        continue
                    if isinstance(v, (int, float)):
                        agg[k] = int(agg.get(k) or 0) + int(v)
            if i % 25 == 0 or i == len(game_ids):
                print(f"  sequence … {i}/{len(game_ids)} ({len(ok)} ok)", flush=True)

    team_out = {}
    for abbr, t in teams.items():
        g = max(1, int(t.get("games") or 0))
        chains = int(t.get("rush_chains") or 0)
        ev = int(t.get("rush_chain_events_sum") or 0)
        rates = {
            "rush_chains_per_game": round(chains / g, 2),
            "rush_chain_avg_length": round(ev / chains, 2) if chains else None,
            "slot_drives_against_per_game": round(int(t.get("slot_drives_against") or 0) / g, 2),
            "p1_sc_per_game": round(int(t.get("p1_sc") or 0) / g, 2),
            "p3_sc_per_game": round(int(t.get("p3_sc") or 0) / g, 2),
            "p3_minus_p1_sc_per_game": round(
                (int(t.get("p3_sc") or 0) - int(t.get("p1_sc") or 0)) / g, 2
            ),
        }
        team_out[abbr] = {**t, "rates": rates}

    skater_out = {}
    for pid, s in skaters.items():
        g = max(1, int(s.get("games") or 0))
        chains = int(s.get("rush_chains") or 0)
        ev = int(s.get("rush_chain_events_sum") or 0)
        skater_out[str(pid)] = {
            **s,
            "rates": {
                "rush_chains_per_game": round(chains / g, 2),
                "rush_chain_avg_length": round(ev / chains, 2) if chains else None,
            },
        }

    line_out = {}
    for lid, ln in lines.items():
        g = max(1, int(ln.get("games") or 0))
        ev = max(1, int(ln.get("events") or 0))
        sc_f = int(ln.get("sc_for") or 0)
        sc_a = int(ln.get("sc_against") or 0)
        if g < 3 or ev < 20:
            continue  # drop tiny samples
        line_out[lid] = {
            **ln,
            "rates": {
                "sc_diff_per_game": round((sc_f - sc_a) / g, 2),
                "sc_for_per_game": round(sc_f / g, 2),
                "sc_against_per_game": round(sc_a / g, 2),
                "events_per_game": round(ev / g, 2),
            },
        }

    payload = {
        "updated_at": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
        "real_data_only": True,
        "game_count": len(ok),
        "processed_games": ok,
        "teams": team_out,
        "team_count": len(team_out),
        "skaters": skater_out,
        "skater_count": len(skater_out),
        "lines": line_out,
        "line_count": len(line_out),
        "note": "5-man on-ice units (not pure FFF lines); rush chain = events in ≤8s after poss change to rush SC",
    }
    out = CURATED / "sequence_extensions.json"
    out.write_text(json.dumps(payload, indent=2))
    (CURATED / "lines" / "on_ice_units.json").parent.mkdir(parents=True, exist_ok=True)
    (CURATED / "lines" / "on_ice_units.json").write_text(
        json.dumps(
            {
                "updated_at": payload["updated_at"],
                "line_count": payload["line_count"],
                "game_count": payload["game_count"],
                "lines": line_out,
                "note": payload["note"],
            },
            indent=2,
        )
    )
    print(
        f"🔗 sequence: {payload['team_count']} teams, {payload['skater_count']} skaters, "
        f"{payload['line_count']} lines ← {payload['game_count']} games → {out}"
    )
    return out


if __name__ == "__main__":
    from nhl_skater_game_microstats import season_completed_game_ids

    ids = season_completed_game_ids()
    aggregate(ids)
