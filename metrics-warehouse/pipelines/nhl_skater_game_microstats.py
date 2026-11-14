#!/usr/bin/env python3
"""Player-grain NHL PBP microstats (personal warehouse).

Attributes giveaways/takeaways/shots/entries/dumps/SC/rush/slot-drive proxies
to player_id from official gamecenter play-by-play.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "pipelines"

# Prefer vendored copy; fall back to APGR analyzers when present.
# Local PIPE must stay first so SCHEMA_VERSION / new helpers resolve here.
_apgr = Path(os.environ.get("APGR_ROOT", "/Users/emilyfehr8/CascadeProjects/automated-post-game-reports"))
for _p in (_apgr / "analyzers", _apgr):
    if _p.is_dir():
        sys.path.insert(0, str(_p))
sys.path.insert(0, str(PIPE))

from paths import CURATED, ensure_dirs  # noqa: E402

from nhl_pbp_microstats import (  # noqa: E402
    ENTRY_GAP_S,
    FOLLOW_WINDOW_S,
    OFFENSE_CONTROLLED,
    RUSH_WINDOW_S,
    SCHEMA_VERSION,
    SLOT_DRIVE_WINDOW_S,
    UNBLOCKED_SHOTS,
    _attack_sign,
    _clock_seconds,
    _dump_follow_up,
    _exit_after_dz_recovery,
    _failed_entry_follow,
    _failed_exit_follow,
    _home_attack_sign,
    _is_scoring_chance,
    _is_slot,
    _lane_from_y,
    _opp_shot_after_to,
    _rink_xy,
    _score_state,
    _slot_drive_conversion,
    _zone_for,
    classify_landing,
    compute_game_microstats,
    entry_kind,
    rates_from_totals,
)

USER_AGENT = "metrics-warehouse/1.0"


def _empty_player() -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "player_id": 0,
        "name": "",
        "team": "",
        "games": 0,
        "schema_version": SCHEMA_VERSION,
        "giveaways_oz": 0,
        "giveaways_nz": 0,
        "giveaways_dz": 0,
        "takeaways_oz": 0,
        "takeaways_nz": 0,
        "takeaways_dz": 0,
        "forecheck_recoveries": 0,
        "shots": 0,
        "goals": 0,
        "scoring_chances": 0,
        "sc_off_rush": 0,
        "sc_off_entry": 0,
        "sc_off_dump": 0,
        "sc_off_carry": 0,
        "rush_shots": 0,
        "entries": 0,
        "controlled_entries": 0,
        "dump_ins": 0,
        "dump_ins_recovered": 0,
        "dump_ins_with_follow": 0,
        "exits": 0,
        "controlled_exits": 0,
        "dump_outs": 0,
        "slot_drives": 0,
        "slot_drives_via_carry": 0,
        "slot_drives_via_pass": 0,
        "slot_drives_to_shot": 0,
        "slot_drives_to_sc": 0,
        "slot_drives_to_goal": 0,
        "dz_recoveries": 0,
        "dz_recovery_to_exit": 0,
        "dz_recovery_to_controlled_exit": 0,
        "zone_to_oz": 0,
        "zone_to_nz": 0,
        "zone_to_dz": 0,
        "zone_to_sa_oz": 0,
        "zone_to_sa_nz": 0,
        "zone_to_sa_dz": 0,
        "failed_entries": 0,
        "failed_exits": 0,
        "failed_entries_left": 0,
        "failed_entries_middle": 0,
        "failed_entries_right": 0,
        "failed_entries_dump": 0,
        "failed_entries_controlled": 0,
        "failed_entries_shot_first": 0,
        "failed_exits_left": 0,
        "failed_exits_middle": 0,
        "failed_exits_right": 0,
        "failed_exits_dump": 0,
        "failed_exits_controlled": 0,
        "failed_exits_other": 0,
        "hits": 0,
        "blocks": 0,
        "dump_landing_strong_corner": 0,
        "dump_landing_weak_corner": 0,
        "dump_landing_strong_rim": 0,
        "dump_landing_weak_rim": 0,
        "dump_landing_deep_slot": 0,
        "dump_landing_short_nz": 0,
    }
    for ss in ("tied", "leading", "trailing"):
        for key in (
            "entries",
            "dump_ins",
            "dump_ins_recovered",
            "controlled_entries",
            "scoring_chances",
            "forecheck_recoveries",
            "failed_entries",
            "failed_exits",
            "sc_off_dump",
            "sc_off_carry",
        ):
            row[f"ss_{ss}_{key}"] = 0
    return row


def _landing_key(label: str) -> str:
    return {
        "Strong Side Corner": "dump_landing_strong_corner",
        "Weak Side Corner": "dump_landing_weak_corner",
        "Strong Side Rim": "dump_landing_strong_rim",
        "Weak Side Rim": "dump_landing_weak_rim",
        "Deep Slot / Middle": "dump_landing_deep_slot",
        "Short / NZ": "dump_landing_short_nz",
    }.get(label, "dump_landing_deep_slot")


def _player_id_from_play(play: dict) -> Optional[int]:
    details = play.get("details") or {}
    kind = play.get("typeDescKey") or ""
    for key in (
        "shootingPlayerId",
        "scoringPlayerId",
        "playerId",
        "hittingPlayerId",
        "winningPlayerId",
        "blockingPlayerId",
    ):
        pid = details.get(key)
        if pid:
            return int(pid)
    # giveaway/takeaway often only have eventOwnerTeamId — no player in some feeds
    if kind in {"giveaway", "takeaway"}:
        pid = details.get("playerId")
        if pid:
            return int(pid)
    return None


def _roster_names(pbp: dict) -> Dict[int, str]:
    out: Dict[int, str] = {}
    for spot in pbp.get("rosterSpots") or []:
        pid = spot.get("playerId")
        if not pid:
            continue
        first = (spot.get("firstName") or {}).get("default") or ""
        last = (spot.get("lastName") or {}).get("default") or ""
        out[int(pid)] = f"{first} {last}".strip()
    return out


def _team_for_player(pbp: dict, player_id: int) -> str:
    home_id = int((pbp.get("homeTeam") or {}).get("id") or 0)
    away_id = int((pbp.get("awayTeam") or {}).get("id") or 0)
    home_abbr = (pbp.get("homeTeam") or {}).get("abbrev") or "H"
    away_abbr = (pbp.get("awayTeam") or {}).get("abbrev") or "A"
    for spot in pbp.get("rosterSpots") or []:
        if int(spot.get("playerId") or 0) == player_id:
            tid = int(spot.get("teamId") or 0)
            if tid == home_id:
                return home_abbr
            if tid == away_id:
                return away_abbr
    return ""


def process_game(pbp: dict) -> Dict[int, Dict[str, Any]]:
    plays = pbp.get("plays") or []
    if len(plays) < 20:
        return {}

    home = pbp.get("homeTeam") or {}
    away = pbp.get("awayTeam") or {}
    home_id = int(home.get("id") or 0)
    away_id = int(away.get("id") or 0)
    if not home_id or not away_id:
        return {}

    names = _roster_names(pbp)
    home_signs = _home_attack_sign(plays, home_id)
    players: Dict[int, Dict[str, Any]] = {}
    seen_in_game: set[int] = set()

    def row(pid: int) -> Dict[str, Any]:
        if pid not in players:
            r = _empty_player()
            r["player_id"] = pid
            r["name"] = names.get(pid, f"Player {pid}")
            r["team"] = _team_for_player(pbp, pid)
            players[pid] = r
        return players[pid]

    last_poss_change: Dict[int, float] = {home_id: -999.0, away_id: -999.0}
    last_player_event: Dict[int, Optional[dict]] = defaultdict(lambda: None)
    team_of: Dict[int, int] = {}
    for spot in pbp.get("rosterSpots") or []:
        pid = spot.get("playerId")
        tid = spot.get("teamId")
        if pid and tid:
            team_of[int(pid)] = int(tid)

    home_goals = 0
    away_goals = 0

    def _bump_ss(r: Dict[str, Any], ss: str, key: str, n: int = 1) -> None:
        k = f"ss_{ss}_{key}"
        if k in r:
            r[k] += n

    # Pass 1 — event attribution
    for index, play in enumerate(plays):
        kind = play.get("typeDescKey") or ""
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        zone = details.get("zoneCode")
        period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        second = _clock_seconds(play.get("timeInPeriod"))
        game_sec = (period - 1) * 1200 + second
        pid = _player_id_from_play(play)

        if owner is None or zone not in {"O", "D", "N"}:
            if kind == "goal" and owner is not None:
                if int(owner) == home_id:
                    home_goals += 1
                elif int(owner) == away_id:
                    away_goals += 1
            continue
        owner = int(owner)
        ss = _score_state(owner, home_id, home_goals, away_goals)

        if kind == "giveaway" and pid:
            seen_in_game.add(pid)
            r = row(pid)
            zkey = {"O": "giveaways_oz", "N": "giveaways_nz", "D": "giveaways_dz"}[zone]
            r[zkey] += 1
            zto = {"O": "zone_to_oz", "N": "zone_to_nz", "D": "zone_to_dz"}[zone]
            r[zto] += 1
            if _opp_shot_after_to(plays, index, owner, period, second):
                r[{"O": "zone_to_sa_oz", "N": "zone_to_sa_nz", "D": "zone_to_sa_dz"}[zone]] += 1
            opp = away_id if owner == home_id else home_id
            last_poss_change[opp] = float(game_sec)

        elif kind == "takeaway" and pid:
            seen_in_game.add(pid)
            r = row(pid)
            r[{"O": "takeaways_oz", "N": "takeaways_nz", "D": "takeaways_dz"}[zone]] += 1
            if zone == "O":
                r["forecheck_recoveries"] += 1
                _bump_ss(r, ss, "forecheck_recoveries")
            if zone == "D":
                r["dz_recoveries"] += 1
                exit_mode = _exit_after_dz_recovery(
                    plays,
                    index,
                    owner,
                    period,
                    second,
                    home_id=home_id,
                    home_signs=home_signs,
                )
                if exit_mode in {"controlled", "dump"}:
                    r["dz_recovery_to_exit"] += 1
                if exit_mode == "controlled":
                    r["dz_recovery_to_controlled_exit"] += 1
            last_poss_change[owner] = float(game_sec)

        elif kind == "hit" and pid:
            seen_in_game.add(pid)
            row(pid)["hits"] += 1

        elif kind == "blocked-shot" and pid:
            seen_in_game.add(pid)
            row(pid)["blocks"] += 1

        elif kind in UNBLOCKED_SHOTS and pid and details.get("xCoord") is not None:
            seen_in_game.add(pid)
            r = row(pid)
            r["shots"] += 1
            if kind == "goal":
                r["goals"] += 1
            sign = _attack_sign(home_signs, period, owner, home_id)
            if sign is not None:
                x, y = _rink_xy(play, home_signs, home_id)
                x_att, y_att = x * sign, y * sign
                is_sc = _is_scoring_chance(x_att, y_att)
                if is_sc:
                    r["scoring_chances"] += 1
                    _bump_ss(r, ss, "scoring_chances")
                if game_sec - last_poss_change[owner] <= RUSH_WINDOW_S and last_poss_change[owner] > 0:
                    r["rush_shots"] += 1
                    if is_sc:
                        r["sc_off_rush"] += 1
                if _is_slot(x_att, y_att):
                    team_prev = None
                    for other_pid, ev in list(last_player_event.items()):
                        if ev is None:
                            continue
                        if team_of.get(other_pid) != owner:
                            continue
                        op = int((ev.get("periodDescriptor") or {}).get("number") or 0)
                        os_ = _clock_seconds(ev.get("timeInPeriod"))
                        if op == period and 0 < (second - os_) <= SLOT_DRIVE_WINDOW_S:
                            team_prev = (other_pid, ev)
                            break
                    if team_prev:
                        opid, pev = team_prev
                        psign = _attack_sign(home_signs, period, owner, home_id)
                        pdet = pev.get("details") or {}
                        if psign is not None and pdet.get("xCoord") is not None:
                            px, py = _rink_xy(pev, home_signs, home_id)
                            if not _is_slot(px * psign, py * psign):
                                r["slot_drives"] += 1
                                if opid == pid:
                                    r["slot_drives_via_carry"] += 1
                                else:
                                    r["slot_drives_via_pass"] += 1
                                to_shot, to_sc, to_goal = _slot_drive_conversion(
                                    plays, index, owner, home_id, home_signs, period, second
                                )
                                if to_shot:
                                    r["slot_drives_to_shot"] += 1
                                if to_sc:
                                    r["slot_drives_to_sc"] += 1
                                if to_goal:
                                    r["slot_drives_to_goal"] += 1

            last_player_event[pid] = play

        if kind == "goal" and owner in (home_id, away_id):
            if owner == home_id:
                home_goals += 1
            else:
                away_goals += 1

    # Pass 2 — entries / exits / dump recovery / failed by lane
    home_goals = 0
    away_goals = 0
    last: Optional[dict] = None
    for index, play in enumerate(plays):
        kind = play.get("typeDescKey")
        period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        second = _clock_seconds(play.get("timeInPeriod"))
        details = play.get("details") or {}
        if kind in {"stoppage", "period-start", "period-end", "game-end", "shootout-complete"}:
            last = None
            continue
        if kind == "faceoff":
            last = play
            continue
        owner = details.get("eventOwnerTeamId")
        zone = details.get("zoneCode")
        if (
            owner is None
            or zone not in {"O", "D", "N"}
            or details.get("xCoord") is None
            or details.get("yCoord") is None
        ):
            if kind == "goal" and owner is not None:
                if int(owner) == home_id:
                    home_goals += 1
                elif int(owner) == away_id:
                    away_goals += 1
            continue
        if last is None or int((last.get("periodDescriptor") or {}).get("number") or 0) != period:
            last = play
            if kind == "goal":
                if int(owner) == home_id:
                    home_goals += 1
                elif int(owner) == away_id:
                    away_goals += 1
            continue
        dt = second - _clock_seconds(last.get("timeInPeriod"))
        if dt <= 0 or dt > ENTRY_GAP_S:
            last = play
            if kind == "goal":
                if int(owner) == home_id:
                    home_goals += 1
                elif int(owner) == away_id:
                    away_goals += 1
            continue

        for team in (home_id, away_id):
            now_zone = _zone_for(int(owner), zone, team)
            prev = last.get("details") or {}
            prev_owner = prev.get("eventOwnerTeamId")
            prev_zone_code = prev.get("zoneCode")
            if (
                prev_owner is None
                or prev_zone_code not in {"O", "D", "N"}
                or prev.get("xCoord") is None
                or prev.get("yCoord") is None
            ):
                continue
            prev_zone = _zone_for(int(prev_owner), prev_zone_code, team)
            sign = _attack_sign(home_signs, period, team, home_id)
            if sign is None:
                continue
            x1_raw, y1_raw = _rink_xy(play, home_signs, home_id)
            x0_raw, y0_raw = _rink_xy(last, home_signs, home_id)
            x1, y1 = x1_raw * sign, y1_raw * sign
            x0, y0 = x0_raw * sign, y0_raw * sign
            lane = _lane_from_y(y1)
            ss = _score_state(team, home_id, home_goals, away_goals)

            if now_zone == "O" and prev_zone in {"N", "D"}:
                arr_pid = _player_id_from_play(play)
                if arr_pid is None or team_of.get(arr_pid) != team:
                    arr_pid = None
                    lp_pid = _player_id_from_play(last) if last else None
                    if lp_pid and team_of.get(lp_pid) == team:
                        arr_pid = lp_pid
                if not arr_pid:
                    continue
                seen_in_game.add(arr_pid)
                r = row(arr_pid)
                r["entries"] += 1
                _bump_ss(r, ss, "entries")
                mode = entry_kind(last, play, team, dt, x0, x1)
                if mode == "dump":
                    r["dump_ins"] += 1
                    _bump_ss(r, ss, "dump_ins")
                    r[_landing_key(classify_landing(y0, x1, y1))] += 1
                    recovered, _ds, dsc = _dump_follow_up(
                        plays, index, team, home_id, home_signs, period, second
                    )
                    r["dump_ins_with_follow"] += 1
                    if recovered:
                        r["dump_ins_recovered"] += 1
                        _bump_ss(r, ss, "dump_ins_recovered")
                    if dsc:
                        r["sc_off_dump"] += dsc
                        _bump_ss(r, ss, "sc_off_dump", dsc)
                else:
                    r["controlled_entries"] += 1
                    _bump_ss(r, ss, "controlled_entries")
                for nxt in plays[index : index + 25]:
                    np = int((nxt.get("periodDescriptor") or {}).get("number") or 0)
                    if np != period:
                        break
                    ndt = _clock_seconds(nxt.get("timeInPeriod")) - second
                    if ndt > FOLLOW_WINDOW_S:
                        break
                    nk = nxt.get("typeDescKey")
                    nd = nxt.get("details") or {}
                    if nk in UNBLOCKED_SHOTS and nd.get("eventOwnerTeamId") == team:
                        nsign = _attack_sign(home_signs, period, team, home_id)
                        if nsign is not None and nd.get("xCoord") is not None:
                            nx, ny = _rink_xy(nxt, home_signs, home_id)
                            if _is_scoring_chance(nx * nsign, ny * nsign):
                                sp = _player_id_from_play(nxt)
                                if sp:
                                    seen_in_game.add(sp)
                                    row(sp)["sc_off_entry"] += 1
                                    if mode == "controlled":
                                        row(sp)["sc_off_carry"] += 1
                                        _bump_ss(row(sp), ss, "sc_off_carry")
                                break
                if _failed_entry_follow(plays, index, team, period, second):
                    r["failed_entries"] += 1
                    r[f"failed_entries_{lane}"] += 1
                    r[f"failed_entries_{mode}"] += 1
                    _bump_ss(r, ss, "failed_entries")

            if prev_zone == "D" and now_zone in {"N", "O"} and int(owner) == team:
                pid = _player_id_from_play(play)
                if pid and team_of.get(pid) == team:
                    seen_in_game.add(pid)
                    r = row(pid)
                    r["exits"] += 1
                    xk = "controlled" if (kind in OFFENSE_CONTROLLED or kind == "hit") else "dump"
                    if xk == "controlled":
                        r["controlled_exits"] += 1
                    else:
                        r["dump_outs"] += 1
                    if _failed_exit_follow(plays, index, team, period, second):
                        r["failed_exits"] += 1
                        r[f"failed_exits_{lane}"] += 1
                        r[f"failed_exits_{xk}"] += 1
                        _bump_ss(r, ss, "failed_exits")

        last = play
        if kind == "goal" and owner is not None:
            if int(owner) == home_id:
                home_goals += 1
            elif int(owner) == away_id:
                away_goals += 1

    for pid in seen_in_game:
        if pid in players:
            players[pid]["games"] = 1
    return players


def fetch_pbp(game_id: str | int) -> Optional[dict]:
    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.load(resp)
    except Exception:
        return None


def _empty_team_row() -> Dict[str, Any]:
    from nhl_pbp_microstats import _empty_team

    return _empty_team()


def _accumulate_games(
    game_ids: List[str], *, workers: int = 12
) -> Tuple[Dict[int, Dict[str, Any]], Dict[str, Dict[str, Any]], List[str]]:
    """Fetch PBPs and sum raw totals only (no rates)."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    season: Dict[int, Dict[str, Any]] = {}
    teams: Dict[str, Dict[str, Any]] = {}
    processed: List[str] = []
    workers = max(1, int(os.getenv("WAREHOUSE_PBP_WORKERS", str(workers))))
    if not game_ids:
        return season, teams, processed

    def _one(gid: str):
        pbp = fetch_pbp(gid)
        if not pbp:
            return gid, None, None
        try:
            team_ms = compute_game_microstats(pbp)
        except Exception:
            team_ms = None
        return gid, process_game(pbp), team_ms

    results = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_one, gid): gid for gid in game_ids}
        for i, fut in enumerate(as_completed(futs), 1):
            gid, game_players, team_ms = fut.result()
            if game_players:
                results.append((gid, game_players, team_ms))
            if i % 50 == 0 or i == len(game_ids):
                print(f"  … {i}/{len(game_ids)} games fetched ({len(results)} ok)", flush=True)

    for gid, game_players, team_ms in results:
        processed.append(str(gid))
        for pid, gstats in game_players.items():
            if pid not in season:
                season[pid] = _empty_player()
                season[pid]["player_id"] = pid
                season[pid]["name"] = gstats.get("name") or ""
                season[pid]["team"] = gstats.get("team") or ""
            agg = season[pid]
            if gstats.get("team"):
                agg["team"] = gstats["team"]
            if gstats.get("name"):
                agg["name"] = gstats["name"]
            for k, v in gstats.items():
                if k in {"player_id", "name", "team", "schema_version"}:
                    continue
                if isinstance(v, (int, float)):
                    agg[k] = int(agg.get(k, 0) or 0) + int(v)
            agg["schema_version"] = SCHEMA_VERSION
        if team_ms:
            for abbr, row in team_ms.items():
                if abbr not in teams:
                    teams[abbr] = _empty_team_row()
                    teams[abbr]["team"] = abbr
                    teams[abbr]["games"] = 0
                t = teams[abbr]
                t["games"] = int(t.get("games") or 0) + 1
                t["schema_version"] = SCHEMA_VERSION
                for k, v in row.items():
                    if k in {"schema_version", "source_note"}:
                        continue
                    if isinstance(v, bool):
                        continue
                    if isinstance(v, float):
                        t[k] = float(t.get(k, 0) or 0) + float(v)
                    elif isinstance(v, int):
                        t[k] = int(t.get(k, 0) or 0) + int(v)
    return season, teams, processed


def _finalize_rates(
    season: Dict[Any, Dict[str, Any]],
    teams: Dict[str, Dict[str, Any]],
    processed: List[str],
) -> Dict[str, Any]:
    """Attach rates to summed totals."""
    out_players = {}
    for pid, s in season.items():
        # Drop nested rate blobs if re-finalizing a curated row
        s = {k: v for k, v in s.items() if k != "rates"}
        g = max(1, int(s.get("games") or 0))
        entries = int(s.get("entries") or 0)
        dumps = int(s.get("dump_ins") or 0)
        dump_follow = int(s.get("dump_ins_with_follow") or 0) or dumps
        slot_n = int(s.get("slot_drives") or 0)
        dz_rec = int(s.get("dz_recoveries") or 0)
        exits = int(s.get("exits") or 0)
        rates = {
            "schema_version": SCHEMA_VERSION,
            "forecheck_recoveries_per_game": round(int(s.get("forecheck_recoveries") or 0) / g, 2),
            "sc_per_game": round(int(s.get("scoring_chances") or 0) / g, 2),
            "sc_off_rush_per_game": round(int(s.get("sc_off_rush") or 0) / g, 2),
            "sc_off_entry_per_game": round(int(s.get("sc_off_entry") or 0) / g, 2),
            "sc_off_dump_per_game": round(int(s.get("sc_off_dump") or 0) / g, 2),
            "sc_off_carry_per_game": round(int(s.get("sc_off_carry") or 0) / g, 2),
            "dump_ins_per_game": round(dumps / g, 2),
            "dump_in_recovery_pct": (
                round(100.0 * int(s.get("dump_ins_recovered") or 0) / dump_follow, 1)
                if dump_follow
                else None
            ),
            "controlled_entry_pct": (
                round(100.0 * int(s.get("controlled_entries") or 0) / entries, 1)
                if entries
                else None
            ),
            "slot_drives_per_game": round(slot_n / g, 2),
            "slot_drive_to_shot_pct": (
                round(100.0 * int(s.get("slot_drives_to_shot") or 0) / slot_n, 1) if slot_n else None
            ),
            "slot_drive_to_sc_pct": (
                round(100.0 * int(s.get("slot_drives_to_sc") or 0) / slot_n, 1) if slot_n else None
            ),
            "dz_recovery_to_exit_pct": (
                round(100.0 * int(s.get("dz_recovery_to_exit") or 0) / dz_rec, 1) if dz_rec else None
            ),
            "dz_retrieval_to_controlled_exit_pct": (
                round(100.0 * int(s.get("dz_recovery_to_controlled_exit") or 0) / dz_rec, 1)
                if dz_rec
                else None
            ),
            "failed_entry_pct": (
                round(100.0 * int(s.get("failed_entries") or 0) / entries, 1) if entries else None
            ),
            "failed_exit_pct": (
                round(100.0 * int(s.get("failed_exits") or 0) / exits, 1) if exits else None
            ),
            "failed_entries_by_lane": {
                "left": int(s.get("failed_entries_left") or 0),
                "middle": int(s.get("failed_entries_middle") or 0),
                "right": int(s.get("failed_entries_right") or 0),
            },
            "failed_exits_by_lane": {
                "left": int(s.get("failed_exits_left") or 0),
                "middle": int(s.get("failed_exits_middle") or 0),
                "right": int(s.get("failed_exits_right") or 0),
            },
            "failed_entries_by_type": {
                "dump": int(s.get("failed_entries_dump") or 0),
                "controlled": int(s.get("failed_entries_controlled") or 0),
                "shot_first": int(s.get("failed_entries_shot_first") or 0),
            },
            "failed_exits_by_type": {
                "dump": int(s.get("failed_exits_dump") or 0),
                "controlled": int(s.get("failed_exits_controlled") or 0),
                "other": int(s.get("failed_exits_other") or 0),
            },
            "giveaways_dz_per_game": round(int(s.get("giveaways_dz") or 0) / g, 2),
            "zone_to_shot_against_pct_dz": (
                round(
                    100.0
                    * int(s.get("zone_to_sa_dz") or 0)
                    / int(s.get("zone_to_dz") or 0),
                    1,
                )
                if int(s.get("zone_to_dz") or 0)
                else None
            ),
        }
        score_state = {}
        for ss in ("tied", "leading", "trailing"):
            se = int(s.get(f"ss_{ss}_entries") or 0)
            sd = int(s.get(f"ss_{ss}_dump_ins") or 0)
            score_state[ss] = {
                "entries": se,
                "dump_ins": sd,
                "controlled_entry_pct": (
                    round(100.0 * int(s.get(f"ss_{ss}_controlled_entries") or 0) / se, 1)
                    if se
                    else None
                ),
                "dump_in_recovery_pct": (
                    round(100.0 * int(s.get(f"ss_{ss}_dump_ins_recovered") or 0) / sd, 1)
                    if sd
                    else None
                ),
                "sc": int(s.get(f"ss_{ss}_scoring_chances") or 0),
                "failed_entries": int(s.get(f"ss_{ss}_failed_entries") or 0),
                "failed_exits": int(s.get(f"ss_{ss}_failed_exits") or 0),
            }
        rates["score_state"] = score_state
        out_players[str(pid)] = {**s, "rates": rates}

    out_teams = {}
    for abbr, t in teams.items():
        t = {k: v for k, v in t.items() if k != "rates"}
        g = max(1, int(t.get("games") or 0))
        out_teams[abbr] = {**t, "rates": rates_from_totals(t, g)}

    # stable unique order
    seen = set()
    ordered = []
    for g in processed:
        sg = str(g)
        if sg not in seen:
            seen.add(sg)
            ordered.append(sg)

    return {
        "processed_games": ordered,
        "skaters": out_players,
        "skater_count": len(out_players),
        "teams": out_teams,
        "team_count": len(out_teams),
    }


def aggregate_games(game_ids: List[str], *, workers: int = 12) -> Dict[str, Any]:
    season, teams, processed = _accumulate_games(game_ids, workers=workers)
    return _finalize_rates(season, teams, processed)


def _apgr_history_path() -> Path:
    from paths import APGR

    return APGR / "data" / "win_probability_predictions_v2.json"


def _current_season_compact() -> str:
    return os.getenv("NHL_SEASON", "20262027")


def _is_current_rs_game_id(gid: str, season: str | None = None) -> bool:
    """NHL id layout: YYYYYTNNNN — T=02 regular season for season YYYY/(YYYY+1)."""
    season = season or _current_season_compact()
    start_year = season[:4]
    g = str(gid)
    return len(g) >= 6 and g.startswith(start_year) and g[4:6] == "02"


def recent_final_game_ids(limit: int = 80) -> List[str]:
    """Prefer APGR prediction history (current RS only); fall back to NHL completed RS."""
    hist = _apgr_history_path()
    season = _current_season_compact()
    if hist.exists():
        data = json.loads(hist.read_text())
        ids = [
            str(pr.get("game_id"))
            for pr in data.get("predictions", [])
            if pr.get("actual_winner")
            and pr.get("game_id")
            and _is_current_rs_game_id(str(pr.get("game_id")), season)
        ]
        ids = list(dict.fromkeys(reversed(ids)))
        print(
            f"📋 APGR history: {len(ids)} current-RS ({season}) decided games "
            f"(using {min(limit, len(ids))})"
        )
        if ids:
            return ids[:limit]
    return season_completed_game_ids(limit=limit)


def season_completed_game_ids(
    season: str | None = None, *, limit: int | None = None
) -> List[str]:
    """Completed regular-season game IDs (gameDate <= today) via NHL stats API."""
    from datetime import datetime, timezone
    from urllib.parse import quote

    season = season or os.getenv("NHL_SEASON", "20262027")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    expr = f"season={season} and gameType=2 and gameDate<=\"{today}\""
    ids: List[str] = []
    start = 0
    total = None
    while total is None or start < total:
        url = (
            "https://api.nhle.com/stats/rest/en/game?"
            f"cayenneExp={quote(expr)}&limit=100&start={start}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=45) as resp:
            payload = json.load(resp)
        rows = payload.get("data") or []
        total = int(payload.get("total") or 0)
        if not rows:
            break
        for r in rows:
            gid = r.get("id")
            # gameStateId 1 = scheduled/FUT; completed finals are typically 6/7.
            state = int(r.get("gameStateId") or 0)
            if gid and state >= 5:
                ids.append(str(gid))
        start += len(rows)
    ids = list(dict.fromkeys(ids))
    if limit is not None and limit > 0:
        ids = ids[-limit:]
    print(f"📋 Season {season} completed RS games (≤{today}, state≥5): {len(ids)}")
    return ids


def _write_payload(payload: Dict[str, Any], *, season: str, mode: str) -> Path:
    payload = dict(payload)
    payload["mode"] = mode
    payload["season"] = season
    payload["game_type"] = "2"
    payload["schema_version"] = SCHEMA_VERSION
    payload["game_count"] = len(payload.get("processed_games") or [])
    out = CURATED / "skaters" / "nhl_pbp_microstats.json"
    skater_view = {k: v for k, v in payload.items() if k not in {"teams", "team_count"}}
    out.write_text(json.dumps(skater_view, indent=2))
    (CURATED / "skaters_season.json").write_text(json.dumps(skater_view, indent=2))
    team_out = {
        "updated_at": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
        "season": season,
        "mode": mode,
        "schema_version": SCHEMA_VERSION,
        "game_count": payload["game_count"],
        "processed_games": payload.get("processed_games"),
        "team_count": payload.get("team_count"),
        "teams": payload.get("teams") or {},
    }
    (CURATED / "teams" / "nhl_pbp_microstats.json").write_text(json.dumps(team_out, indent=2))
    print(
        f"💾 {payload['skater_count']} skaters + {payload.get('team_count', 0)} teams "
        f"from {payload['game_count']} games ({mode}) → {out}"
    )
    return out


def main(lookback: int = 60, *, season_backfill: bool = False) -> Path:
    ensure_dirs()
    season = _current_season_compact()
    season_scope = season_backfill or os.getenv("WAREHOUSE_SEASON_BACKFILL", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )

    if season_scope:
        all_ids = season_completed_game_ids(season=season)
        from incremental_store import (
            decide_skater_plan,
            merge_count_rows,
            write_incremental_status,
        )

        plan = decide_skater_plan(all_ids, schema_version=SCHEMA_VERSION)
        action = plan["action"]
        print(
            f"🏒 Skater plan={action} ({plan['reason']}) "
            f"prior={plan['prior_count']} season_rs={len(all_ids)} fetch={len(plan['ids'])}"
        )

        if action == "noop":
            sk, tm = plan["sk"], plan["tm"]
            payload = {
                "processed_games": list(sk.get("processed_games") or sorted(plan["prior_games"])),
                "skaters": sk.get("skaters") or {},
                "skater_count": sk.get("skater_count") or len(sk.get("skaters") or {}),
                "teams": tm.get("teams") or {},
                "team_count": tm.get("team_count") or len(tm.get("teams") or {}),
            }
            mode = "season_append"
            out = _write_payload(payload, season=season, mode=mode)
            write_incremental_status(
                mode=mode,
                prior_count=plan["prior_count"],
                new_ids=[],
                after_count=len(payload["processed_games"]),
                full_rebuild=False,
            )
            print("⏭️  no new RS finals — skipped historical PBP refetch")
            new_ids_for_on_ice: List[str] = []
        elif action == "append":
            new_season, new_teams, new_processed = _accumulate_games(plan["ids"])
            base_skaters: Dict[Any, Dict[str, Any]] = {}
            for pid, row in (plan["sk"].get("skaters") or {}).items():
                key = int(pid) if str(pid).isdigit() else pid
                base_skaters[key] = {k: v for k, v in row.items() if k != "rates"}
            base_teams: Dict[str, Dict[str, Any]] = {}
            for abbr, row in (plan["tm"].get("teams") or {}).items():
                base_teams[abbr] = {k: v for k, v in row.items() if k != "rates"}
            merge_count_rows(base_skaters, new_season, id_key="player_id")
            merge_count_rows(base_teams, new_teams, id_key="team")
            merged_games = list(plan["sk"].get("processed_games") or sorted(plan["prior_games"]))
            merged_games.extend(new_processed)
            payload = _finalize_rates(base_skaters, base_teams, merged_games)
            mode = "season_append"
            out = _write_payload(payload, season=season, mode=mode)
            write_incremental_status(
                mode=mode,
                prior_count=plan["prior_count"],
                new_ids=list(new_processed),
                after_count=len(payload["processed_games"]),
                full_rebuild=False,
            )
            print(f"✅ appended {len(new_processed)} new game(s); total={len(payload['processed_games'])}")
            new_ids_for_on_ice = list(new_processed)
        else:
            payload = aggregate_games(plan["ids"])
            mode = "season_backfill"
            out = _write_payload(payload, season=season, mode=mode)
            write_incremental_status(
                mode=mode,
                prior_count=plan["prior_count"],
                new_ids=list(payload.get("processed_games") or []),
                after_count=len(payload.get("processed_games") or []),
                full_rebuild=True,
            )
            new_ids_for_on_ice = list(payload.get("processed_games") or [])
    else:
        ids = recent_final_game_ids(lookback)
        print(f"🏒 Skater microstats lookback: {len(ids)} games")
        payload = aggregate_games(ids)
        mode = "incremental"
        out = _write_payload(payload, season=season, mode=mode)
        new_ids_for_on_ice = list(payload.get("processed_games") or [])

    # On-ice: only new games when appending; full list on rebuild
    try:
        from on_ice_microstats import aggregate as on_ice_aggregate

        if season_scope and mode == "season_append" and not new_ids_for_on_ice:
            print("⏭️  on-ice: nothing new")
        elif season_scope and mode == "season_append":
            on_ice_aggregate(new_ids_for_on_ice, merge_existing=True)
        else:
            on_ice_aggregate(list(payload.get("processed_games") or []), merge_existing=False)
    except Exception as e:
        print(f"⚠️ on-ice skipped: {e}")
    try:
        from combine_microstats import combine, top5_report

        combine()
        top5_report()
    except Exception as e:
        print(f"⚠️ combine/top5 skipped: {e}")
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    backfill = "--season" in args or os.getenv("WAREHOUSE_SEASON_BACKFILL", "").strip() in ("1", "true", "yes")
    nums = [a for a in args if a.isdigit()]
    lookback = int(nums[0]) if nums else 40
    main(lookback, season_backfill=backfill)
