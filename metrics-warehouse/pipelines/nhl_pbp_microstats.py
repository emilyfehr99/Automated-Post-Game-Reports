#!/usr/bin/env python3
"""NHL official PBP microstats for the daily advanced-metrics path.

Ports dump-in / controlled-entry heuristics from nhl-dump-in-research and adds
zone turnover, rush/entry scoring-chance, forecheck-recovery (OZ takeaway),
DZ retrieval→exit, slot-drive, dump recovery, failed entry/exit (by lane/type),
score-state splits, and forecheck pressure composite.

Honest limits (do NOT invent from NHL PBP alone):
  - puck battle win% by zone (InStat action / gear aliases)
  - true positive vs failed touches (vendor-tagged)
  - true InStat forecheck recoveries / slot drives / retrieval tags
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

# NHL feet frame (matches nhl-dump-in-research)
BLUE_X = 25.0
DOT_X = 69.0
GOAL_X = 89.0
DOT_Y = 22.0
RIM_Y = 42.5 - (4.0 / 0.3048)
SIDE_MARGIN_FT = 1.0 / 0.3048
ENTRY_GAP_S = 20.0
FOLLOW_WINDOW_S = 10.0
RUSH_WINDOW_S = 6.0
SLOT_DRIVE_WINDOW_S = 5.0
SLOT_CONVERT_WINDOW_S = 6.0
SC_DIST_FT = 25.0
# NHL PBP is sparse — 15s timed out many real breakouts (20–30s gaps with no events).
RETRIEVAL_EXIT_WINDOW_S = 25.0
FAILED_ENTRY_WINDOW_S = 8.0
FAILED_EXIT_WINDOW_S = 7.0
ZONE_TO_SA_WINDOW_S = 8.0
SCHEMA_VERSION = 4

SHOT_ATTEMPTS = frozenset({"shot-on-goal", "missed-shot", "goal", "blocked-shot"})
UNBLOCKED_SHOTS = frozenset({"shot-on-goal", "missed-shot", "goal"})
SHOT_FIRST = frozenset({"shot-on-goal", "missed-shot", "goal", "blocked-shot"})
OFFENSE_CONTROLLED = frozenset({"shot-on-goal", "missed-shot", "goal", "takeaway"})
POSSESSION_EVENTS = frozenset(
    {
        "shot-on-goal",
        "missed-shot",
        "goal",
        "blocked-shot",
        "takeaway",
        "hit",
        "faceoff",
    }
)
STOPPAGES = frozenset({"stoppage", "faceoff", "period-end", "game-end", "period-start"})
_ZONE_SUFFIX = {"O": "oz", "N": "nz", "D": "dz"}
_SS_KEYS = ("tied", "leading", "trailing")
_LANES = ("left", "middle", "right")
_ENTRY_TYPES = ("dump", "controlled", "shot_first")
_EXIT_TYPES = ("dump", "controlled", "other")


def _empty_team() -> Dict[str, Any]:
    row: Dict[str, Any] = {
        # Turnovers
        "giveaways_oz": 0,
        "giveaways_nz": 0,
        "giveaways_dz": 0,
        "takeaways_oz": 0,
        "takeaways_nz": 0,
        "takeaways_dz": 0,
        # Touch proxies (not InStat-tagged)
        "positive_touches_oz": 0,
        "positive_touches_nz": 0,
        "positive_touches_dz": 0,
        "failed_touches_oz": 0,
        "failed_touches_nz": 0,
        "failed_touches_dz": 0,
        # Forecheck
        "forecheck_recoveries": 0,  # OZ takeaways (PBP proxy)
        # Entries / exits
        "entries_total": 0,
        "controlled_entries": 0,
        "dump_ins": 0,
        "shot_first_entries": 0,
        "exits_total": 0,
        "controlled_exits": 0,
        "dump_outs": 0,
        # Dump landing mix
        "dump_landing_strong_corner": 0,
        "dump_landing_weak_corner": 0,
        "dump_landing_strong_rim": 0,
        "dump_landing_weak_rim": 0,
        "dump_landing_deep_slot": 0,
        "dump_landing_short_nz": 0,
        # Dump recovery + SC off entry mode
        "dump_ins_recovered": 0,
        "dump_ins_with_follow": 0,
        "sc_off_dump": 0,
        "sc_off_carry": 0,
        "sc_off_shot_first": 0,
        # Scoring chances
        "scoring_chances": 0,
        "sc_off_rush": 0,
        "sc_off_entry": 0,
        "rush_shots": 0,
        "rush_goals": 0,
        "entry_shots": 0,
        # Slot drives (geometry proxy) + conversion
        "slot_drives": 0,
        "slot_drives_via_carry": 0,
        "slot_drives_via_pass": 0,
        "slot_drives_to_shot": 0,
        "slot_drives_to_sc": 0,
        "slot_drives_to_goal": 0,
        # DZ retrieval → exit
        "dz_recoveries": 0,
        "dz_recovery_to_exit": 0,
        "dz_recovery_to_controlled_exit": 0,
        "dz_recovery_to_dump_exit": 0,
        "dz_recovery_failed": 0,
        # Zone TO → shot against
        "zone_to_oz": 0,
        "zone_to_nz": 0,
        "zone_to_dz": 0,
        "zone_to_sa_oz": 0,
        "zone_to_sa_nz": 0,
        "zone_to_sa_dz": 0,
        # Failed entries / exits + denials
        "failed_entries": 0,
        "failed_exits": 0,
        "entry_denials": 0,  # opponent failed entries (we force)
        "forced_failed_exits": 0,  # opponent failed exits
        # Schema
        "schema_version": SCHEMA_VERSION,
    }
    for lane in _LANES:
        row[f"failed_entries_{lane}"] = 0
        row[f"failed_exits_{lane}"] = 0
        row[f"entries_{lane}"] = 0
        row[f"exits_{lane}"] = 0
    for et in _ENTRY_TYPES:
        row[f"failed_entries_{et}"] = 0
    for xt in _EXIT_TYPES:
        row[f"failed_exits_{xt}"] = 0
        row[f"exits_{xt}"] = 0
    for ss in _SS_KEYS:
        for key in (
            "entries_total",
            "controlled_entries",
            "dump_ins",
            "dump_ins_recovered",
            "scoring_chances",
            "giveaways_oz",
            "giveaways_nz",
            "giveaways_dz",
            "takeaways_oz",
            "takeaways_nz",
            "takeaways_dz",
            "forecheck_recoveries",
            "failed_entries",
            "failed_exits",
            "sc_off_dump",
            "sc_off_carry",
            "slot_drives",
            "dz_recoveries",
            "dz_recovery_to_controlled_exit",
        ):
            row[f"ss_{ss}_{key}"] = 0
    return row


def _clock_seconds(value: Optional[str]) -> int:
    if not value or ":" not in value:
        return 0
    minutes, seconds = value.split(":")
    return int(minutes) * 60 + int(seconds)


def _zone_for(owner: int, zone: str, team: int) -> Optional[str]:
    if zone not in ("O", "D", "N"):
        return None
    if owner == team:
        return zone
    return {"O": "D", "D": "O", "N": "N"}[zone]


def _home_attack_sign(plays: List[dict], home_id: int) -> Dict[int, int]:
    buckets: Dict[int, List[float]] = {}
    for play in plays:
        details = play.get("details") or {}
        period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if details.get("eventOwnerTeamId") != home_id or details.get("zoneCode") != "O":
            continue
        x = details.get("xCoord")
        if period <= 0 or x is None:
            continue
        buckets.setdefault(period, []).append(float(x))
    signs: Dict[int, int] = {}
    for period, xs in buckets.items():
        if len(xs) < 3:
            continue
        median = sorted(xs)[len(xs) // 2]
        if median > 0:
            signs[period] = 1
        elif median < 0:
            signs[period] = -1
    for play in plays:
        side = play.get("homeTeamDefendingSide")
        period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if side == "left":
            signs[period] = 1
        elif side == "right":
            signs[period] = -1
    return signs


def _rink_xy(play: dict, home_signs: Dict[int, int], home_id: int) -> Tuple[float, float]:
    details = play.get("details") or {}
    x = float(details["xCoord"])
    y = float(details["yCoord"])
    if play.get("typeDescKey") != "blocked-shot":
        return x, y
    period = int((play.get("periodDescriptor") or {}).get("number") or 0)
    home_sign = home_signs.get(period)
    owner = details.get("eventOwnerTeamId")
    zone = details.get("zoneCode")
    if home_sign is None or owner is None or zone not in {"O", "D"}:
        return x, y
    oz_sign = home_sign if int(owner) == home_id else -home_sign
    expected = oz_sign if zone == "O" else -oz_sign
    if x * expected < 0:
        return -x, y
    return x, y


def _attack_sign(home_signs: Dict[int, int], period: int, team: int, home_id: int) -> Optional[int]:
    sign = home_signs.get(period)
    if sign is None:
        return None
    return sign if team == home_id else -sign


def _same_side(y0: float, y1: float) -> bool:
    if abs(y0) <= SIDE_MARGIN_FT or abs(y1) <= SIDE_MARGIN_FT:
        return True
    return (y0 > 0) == (y1 > 0)


def classify_landing(y_origin: float, x_touch: float, y_touch: float) -> str:
    side = "Strong Side" if _same_side(y_origin, y_touch) else "Weak Side"
    if x_touch < BLUE_X - 3.0:
        return "Short / NZ"
    if x_touch >= GOAL_X or (x_touch >= DOT_X and abs(y_touch) >= DOT_Y):
        return f"{side} Corner"
    if abs(y_touch) >= RIM_Y and x_touch < DOT_X:
        return f"{side} Rim"
    return "Deep Slot / Middle"


def _landing_key(label: str) -> str:
    mapping = {
        "Strong Side Corner": "dump_landing_strong_corner",
        "Weak Side Corner": "dump_landing_weak_corner",
        "Strong Side Rim": "dump_landing_strong_rim",
        "Weak Side Rim": "dump_landing_weak_rim",
        "Deep Slot / Middle": "dump_landing_deep_slot",
        "Short / NZ": "dump_landing_short_nz",
    }
    return mapping.get(label, "dump_landing_deep_slot")


def _lane_from_y(y_att: float) -> str:
    """Attacking-frame Y: left = +Y, right = −Y (NHL standard)."""
    if y_att > DOT_Y:
        return "left"
    if y_att < -DOT_Y:
        return "right"
    return "middle"


def entry_kind(
    previous: dict, arrival: dict, team: int, dt: float, x_prev: float, x_arr: float
) -> str:
    prev_owner = (previous.get("details") or {}).get("eventOwnerTeamId")
    arr_owner = (arrival.get("details") or {}).get("eventOwnerTeamId")
    kind = arrival.get("typeDescKey")
    if kind in SHOT_FIRST:
        return "shot_first"
    if (
        prev_owner == team
        and arr_owner != team
        and kind == "hit"
        and x_prev > -15.0
        and x_arr < BLUE_X + 18.0
        and dt <= 3.0
    ):
        return "controlled"
    if kind in OFFENSE_CONTROLLED and arr_owner == team:
        return "controlled"
    return "dump"


def _exit_kind(kind: str, owner: int, team: int) -> str:
    if kind in OFFENSE_CONTROLLED or (kind == "hit" and owner == team):
        return "controlled"
    if kind == "giveaway" or kind not in OFFENSE_CONTROLLED:
        if kind in {"hit"} and owner == team:
            return "controlled"
        if kind in OFFENSE_CONTROLLED:
            return "controlled"
        return "dump"
    return "other"


def _shot_distance_to_net(x_att: float, y_att: float) -> float:
    return math.sqrt((x_att - GOAL_X) ** 2 + y_att ** 2)


def _is_scoring_chance(x_att: float, y_att: float) -> bool:
    return _shot_distance_to_net(x_att, y_att) <= SC_DIST_FT


def _is_slot(x_att: float, y_att: float) -> bool:
    return x_att >= DOT_X and abs(y_att) <= DOT_Y


def _score_state(team: int, home_id: int, home_g: int, away_g: int) -> str:
    my = home_g if team == home_id else away_g
    opp = away_g if team == home_id else home_g
    if my == opp:
        return "tied"
    return "leading" if my > opp else "trailing"


def _bump_ss(row: Dict[str, Any], ss: str, key: str, n: int = 1) -> None:
    k = f"ss_{ss}_{key}"
    if k in row:
        row[k] += n


def _follow_sc_in_window(
    plays: List[dict],
    start: int,
    team: int,
    home_id: int,
    home_signs: Dict[int, int],
    period: int,
    second: int,
    window_s: float,
) -> Tuple[int, int, int]:
    """Return (shots, scoring_chances, goals) for team in OZ within window."""
    shots = 0
    sc = 0
    goals = 0
    for offset, play in enumerate(plays[start:]):
        play_period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if play_period != period:
            break
        dt = _clock_seconds(play.get("timeInPeriod")) - second
        if dt > window_s:
            break
        kind = play.get("typeDescKey")
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        zone = details.get("zoneCode")
        if offset == 0:
            if owner == team and kind in UNBLOCKED_SHOTS and details.get("xCoord") is not None:
                shots += 1
                sign = _attack_sign(home_signs, period, team, home_id)
                if sign is not None:
                    x, y = _rink_xy(play, home_signs, home_id)
                    if _is_scoring_chance(x * sign, y * sign):
                        sc += 1
                if kind == "goal":
                    goals += 1
            continue
        if kind in STOPPAGES:
            break
        if owner == team and zone == "O" and kind in UNBLOCKED_SHOTS and details.get("xCoord") is not None:
            shots += 1
            sign = _attack_sign(home_signs, period, team, home_id)
            if sign is not None:
                x, y = _rink_xy(play, home_signs, home_id)
                if _is_scoring_chance(x * sign, y * sign):
                    sc += 1
            if kind == "goal":
                goals += 1
                break
        elif kind == "goal" and owner is not None and int(owner) != team:
            break
    return shots, sc, goals


def _dump_follow_up(
    plays: List[dict],
    start: int,
    team: int,
    home_id: int,
    home_signs: Dict[int, int],
    period: int,
    second: int,
) -> Tuple[bool, int, int]:
    """Recovery = later entering-team OZ event (not the dump arrival itself)."""
    recovered = False
    shots = 0
    sc = 0
    for offset, play in enumerate(plays[start:]):
        play_period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if play_period != period:
            break
        dt = _clock_seconds(play.get("timeInPeriod")) - second
        if dt > FOLLOW_WINDOW_S:
            break
        kind = play.get("typeDescKey")
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        zone = details.get("zoneCode")
        x = details.get("xCoord")
        if offset == 0:
            if owner == team and kind in UNBLOCKED_SHOTS and x is not None:
                shots += 1
                sign = _attack_sign(home_signs, period, team, home_id)
                if sign is not None:
                    rx, ry = _rink_xy(play, home_signs, home_id)
                    if _is_scoring_chance(rx * sign, ry * sign):
                        sc += 1
            continue
        if kind in STOPPAGES:
            break
        if owner is not None and zone in {"O", "D", "N"} and x is not None:
            if _zone_for(int(owner), zone, team) != "O":
                break
        if owner == team and zone == "O":
            recovered = True
            if kind in UNBLOCKED_SHOTS and x is not None:
                shots += 1
                sign = _attack_sign(home_signs, period, team, home_id)
                if sign is not None:
                    rx, ry = _rink_xy(play, home_signs, home_id)
                    if _is_scoring_chance(rx * sign, ry * sign):
                        sc += 1
            if kind == "goal":
                break
        elif kind == "goal" and owner is not None and int(owner) != team:
            break
    return recovered, shots, sc


def _exit_after_dz_recovery(
    plays: List[dict],
    start: int,
    team: int,
    period: int,
    second: int,
    *,
    home_id: Optional[int] = None,
    home_signs: Optional[Dict[int, int]] = None,
) -> str:
    """Classify DZ takeaway follow-up. Always returns one of:
      controlled | dump | failed

    Exit = puck leaves DZ for this team (zone N/O OR attacking-frame x > −BLUE_X).
    Controlled = team-owned possession-family / hit on that exit touch.
    Dump = team reaches NZ/OZ via non-possession event (chip/ice).
    Failed = giveaway, opp gains it in our DZ, stoppage, or window expiry.
    """
    for play in plays[start + 1 :]:
        play_period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if play_period != period:
            return "failed"
        dt = _clock_seconds(play.get("timeInPeriod")) - second
        if dt > RETRIEVAL_EXIT_WINDOW_S:
            return "failed"
        kind = play.get("typeDescKey")
        if kind in STOPPAGES:
            return "failed"
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        zone = details.get("zoneCode")
        if owner is None or zone not in {"O", "D", "N"}:
            continue
        owner_i = int(owner)
        team_zone = _zone_for(owner_i, zone, team)

        # Geometry assist when zone tags lag the puck
        x_att = None
        if (
            home_id is not None
            and home_signs is not None
            and details.get("xCoord") is not None
            and details.get("yCoord") is not None
        ):
            sign = _attack_sign(home_signs, period, team, home_id)
            if sign is not None:
                x_raw, _y = _rink_xy(play, home_signs, home_id)
                x_att = x_raw * sign

        left_dz = team_zone in {"N", "O"} or (x_att is not None and x_att > -BLUE_X)

        # Giveaway after the puck is already out of DZ = exited then coughed it up (dump)
        if owner_i == team and kind == "giveaway":
            return "dump" if left_dz else "failed"

        if left_dz and owner_i == team:
            if kind in OFFENSE_CONTROLLED or kind == "hit":
                return "controlled"
            # team event outside DZ that isn't a clean possession touch
            return "dump"

        if left_dz and owner_i != team:
            # puck is out of our DZ but opponent has it — breakout failed
            return "failed"

        if owner_i != team and team_zone == "D" and kind in {
            "takeaway",
            "hit",
        } | UNBLOCKED_SHOTS | {"blocked-shot"}:
            return "failed"
    return "failed"


def _failed_entry_follow(
    plays: List[dict], start: int, team: int, period: int, second: int
) -> bool:
    """True if entry possession dies via TO / opp event before a team shot."""
    for play in plays[start + 1 :]:
        play_period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if play_period != period:
            return False
        dt = _clock_seconds(play.get("timeInPeriod")) - second
        if dt > FAILED_ENTRY_WINDOW_S:
            return False
        kind = play.get("typeDescKey")
        if kind in STOPPAGES:
            return False
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        zone = details.get("zoneCode")
        if owner is None:
            continue
        owner = int(owner)
        if owner == team and kind in UNBLOCKED_SHOTS:
            return False
        if owner == team and kind == "giveaway":
            return True
        if owner != team and zone in {"O", "N", "D"}:
            # opp gains meaningful touch in our OZ / NZ shortly after entry
            if zone in {"D", "N"} or kind in {"takeaway", "hit"} | UNBLOCKED_SHOTS:
                return True
    return False


def _failed_exit_follow(
    plays: List[dict], start: int, team: int, period: int, second: int
) -> bool:
    """True if after DZ exit the puck comes back under opp pressure quickly."""
    for play in plays[start + 1 :]:
        play_period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if play_period != period:
            return False
        dt = _clock_seconds(play.get("timeInPeriod")) - second
        if dt > FAILED_EXIT_WINDOW_S:
            return False
        kind = play.get("typeDescKey")
        if kind in STOPPAGES:
            return False
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        zone = details.get("zoneCode")
        if owner is None or zone not in {"O", "D", "N"}:
            continue
        owner = int(owner)
        if owner != team and (
            kind in UNBLOCKED_SHOTS
            or kind == "takeaway"
            or (zone == "O" and kind in POSSESSION_EVENTS)
        ):
            return True
        if owner == team and kind == "giveaway":
            return True
    return False


def _opp_shot_after_to(
    plays: List[dict], start: int, team: int, period: int, second: int
) -> bool:
    """True if opponent gets an unblocked shot soon after our giveaway."""
    for play in plays[start + 1 :]:
        play_period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if play_period != period:
            return False
        dt = _clock_seconds(play.get("timeInPeriod")) - second
        if dt > ZONE_TO_SA_WINDOW_S:
            return False
        kind = play.get("typeDescKey")
        if kind in STOPPAGES:
            return False
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        if owner is None:
            continue
        if int(owner) != team and kind in UNBLOCKED_SHOTS:
            return True
        if int(owner) == team and kind in UNBLOCKED_SHOTS:
            return False
    return False


def _slot_drive_conversion(
    plays: List[dict],
    start: int,
    team: int,
    home_id: int,
    home_signs: Dict[int, int],
    period: int,
    second: int,
) -> Tuple[bool, bool, bool]:
    """(to_shot, to_sc, to_goal) after a slot-drive event."""
    to_shot = to_sc = to_goal = False
    for play in plays[start:]:
        play_period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if play_period != period:
            break
        dt = _clock_seconds(play.get("timeInPeriod")) - second
        if dt > SLOT_CONVERT_WINDOW_S:
            break
        kind = play.get("typeDescKey")
        if kind in STOPPAGES and dt > 0:
            break
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        if owner != team or kind not in UNBLOCKED_SHOTS:
            continue
        if details.get("xCoord") is None:
            continue
        to_shot = True
        sign = _attack_sign(home_signs, period, team, home_id)
        if sign is not None:
            x, y = _rink_xy(play, home_signs, home_id)
            if _is_scoring_chance(x * sign, y * sign):
                to_sc = True
        if kind == "goal":
            to_goal = True
            break
    return to_shot, to_sc, to_goal


def compute_game_microstats(pbp: dict) -> Dict[str, Dict[str, Any]]:
    """Compute per-abbrev microstats for one NHL gamecenter PBP payload."""
    plays = pbp.get("plays") or []
    if len(plays) < 20:
        return {}

    home = pbp.get("homeTeam") or {}
    away = pbp.get("awayTeam") or {}
    home_id = int(home.get("id") or 0)
    away_id = int(away.get("id") or 0)
    home_abbr = home.get("abbrev") or "H"
    away_abbr = away.get("abbrev") or "A"
    if not home_id or not away_id:
        return {}

    names = {home_id: home_abbr, away_id: away_abbr}
    out = {home_abbr: _empty_team(), away_abbr: _empty_team()}
    home_signs = _home_attack_sign(plays, home_id)

    home_goals = 0
    away_goals = 0
    last_poss_change: Dict[int, float] = {home_id: -999.0, away_id: -999.0}
    last_team_event: Dict[int, Optional[dict]] = {home_id: None, away_id: None}

    # ── Pass 1: turnovers, touches, forecheck, DZ retrieval, rush SC, slot drives, TO→SA
    for index, play in enumerate(plays):
        kind = play.get("typeDescKey") or ""
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        zone = details.get("zoneCode")
        period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        second = _clock_seconds(play.get("timeInPeriod"))
        game_sec = (period - 1) * 1200 + second

        # Track score for score-state splits (goals counted after attribution uses pre-goal state)
        if kind == "goal" and owner is not None:
            if int(owner) == home_id:
                # bump after using current state below
                pass

        if owner is None or zone not in {"O", "D", "N"}:
            if kind == "goal" and owner is not None:
                if int(owner) == home_id:
                    home_goals += 1
                elif int(owner) == away_id:
                    away_goals += 1
            continue
        owner = int(owner)
        if owner not in names:
            if kind == "goal":
                if owner == home_id:
                    home_goals += 1
                elif owner == away_id:
                    away_goals += 1
            continue
        abbr = names[owner]
        row = out[abbr]
        ss = _score_state(owner, home_id, home_goals, away_goals)

        zsuf = _ZONE_SUFFIX[zone]
        if kind == "giveaway":
            row[f"giveaways_{zsuf}"] += 1
            row[f"failed_touches_{zsuf}"] += 1
            row[f"zone_to_{zsuf}"] += 1
            _bump_ss(row, ss, f"giveaways_{zsuf}")
            if _opp_shot_after_to(plays, index, owner, period, second):
                row[f"zone_to_sa_{zsuf}"] += 1
            last_poss_change[away_id if owner == home_id else home_id] = float(game_sec)

        elif kind == "takeaway":
            row[f"takeaways_{zsuf}"] += 1
            row[f"positive_touches_{zsuf}"] += 1
            _bump_ss(row, ss, f"takeaways_{zsuf}")
            if zone == "O":
                row["forecheck_recoveries"] += 1
                _bump_ss(row, ss, "forecheck_recoveries")
            if zone == "D":
                row["dz_recoveries"] += 1
                _bump_ss(row, ss, "dz_recoveries")
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
                    row["dz_recovery_to_exit"] += 1
                if exit_mode == "controlled":
                    row["dz_recovery_to_controlled_exit"] += 1
                    _bump_ss(row, ss, "dz_recovery_to_controlled_exit")
                elif exit_mode == "dump":
                    row["dz_recovery_to_dump_exit"] = int(row.get("dz_recovery_to_dump_exit") or 0) + 1
                else:
                    row["dz_recovery_failed"] = int(row.get("dz_recovery_failed") or 0) + 1
            last_poss_change[owner] = float(game_sec)

        elif kind in POSSESSION_EVENTS and kind != "faceoff":
            row[f"positive_touches_{zsuf}"] += 1

        if kind in UNBLOCKED_SHOTS and details.get("xCoord") is not None and details.get("yCoord") is not None:
            sign = _attack_sign(home_signs, period, owner, home_id)
            if sign is not None:
                x, y = _rink_xy(play, home_signs, home_id)
                x_att, y_att = x * sign, y * sign
                is_sc = _is_scoring_chance(x_att, y_att)
                if is_sc:
                    row["scoring_chances"] += 1
                    _bump_ss(row, ss, "scoring_chances")
                rush = game_sec - last_poss_change[owner] <= RUSH_WINDOW_S and last_poss_change[owner] > 0
                if rush:
                    row["rush_shots"] += 1
                    if kind == "goal":
                        row["rush_goals"] += 1
                    if is_sc:
                        row["sc_off_rush"] += 1

        # Slot drive: arrive in slot from outside on ANY touch (not only shots).
        # Prior bug: counting only on shots made slot_drive_to_shot_pct ≈ 100% by construction.
        if (
            kind in POSSESSION_EVENTS
            and kind != "faceoff"
            and details.get("xCoord") is not None
            and details.get("yCoord") is not None
        ):
            sign = _attack_sign(home_signs, period, owner, home_id)
            if sign is not None:
                x, y = _rink_xy(play, home_signs, home_id)
                x_att, y_att = x * sign, y * sign
                if _is_slot(x_att, y_att):
                    prev = last_team_event.get(owner)
                    if prev is not None:
                        prev_period = int((prev.get("periodDescriptor") or {}).get("number") or 0)
                        prev_sec = _clock_seconds(prev.get("timeInPeriod"))
                        if prev_period == period and 0 < (second - prev_sec) <= SLOT_DRIVE_WINDOW_S:
                            pdet = prev.get("details") or {}
                            if pdet.get("xCoord") is not None:
                                px, py = _rink_xy(prev, home_signs, home_id)
                                if not _is_slot(px * sign, py * sign):
                                    row["slot_drives"] += 1
                                    _bump_ss(row, ss, "slot_drives")
                                    prev_player = pdet.get("playerId") or pdet.get("shootingPlayerId")
                                    cur_player = details.get("playerId") or details.get("shootingPlayerId")
                                    if prev_player and cur_player and prev_player == cur_player:
                                        row["slot_drives_via_carry"] += 1
                                    else:
                                        row["slot_drives_via_pass"] += 1
                                    to_shot, to_sc, to_goal = _slot_drive_conversion(
                                        plays, index, owner, home_id, home_signs, period, second
                                    )
                                    if to_shot:
                                        row["slot_drives_to_shot"] += 1
                                    if to_sc:
                                        row["slot_drives_to_sc"] += 1
                                    if to_goal:
                                        row["slot_drives_to_goal"] += 1

        last_team_event[owner] = play
        if kind == "goal":
            if owner == home_id:
                home_goals += 1
            elif owner == away_id:
                away_goals += 1

    # ── Pass 2: entries / dumps / exits / failed entry-exit / dump recovery
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
            abbr = names[team]
            row = out[abbr]
            sign = _attack_sign(home_signs, period, team, home_id)
            if sign is None:
                continue
            x1_raw, y1_raw = _rink_xy(play, home_signs, home_id)
            x0_raw, y0_raw = _rink_xy(last, home_signs, home_id)
            x1, y1 = x1_raw * sign, y1_raw * sign
            x0, y0 = x0_raw * sign, y0_raw * sign
            lane = _lane_from_y(y1)
            ss = _score_state(team, home_id, home_goals, away_goals)

            # Entries
            if now_zone == "O" and prev_zone in {"N", "D"}:
                row["entries_total"] += 1
                row[f"entries_{lane}"] += 1
                _bump_ss(row, ss, "entries_total")
                mode = entry_kind(last, play, team, dt, x0, x1)
                if mode == "dump":
                    row["dump_ins"] += 1
                    _bump_ss(row, ss, "dump_ins")
                    landing = classify_landing(y0, x1, y1)
                    row[_landing_key(landing)] += 1
                    recovered, _dshots, _dsc = _dump_follow_up(
                        plays, index, team, home_id, home_signs, period, second
                    )
                    row["dump_ins_with_follow"] += 1
                    if recovered:
                        row["dump_ins_recovered"] += 1
                        _bump_ss(row, ss, "dump_ins_recovered")
                elif mode == "controlled":
                    row["controlled_entries"] += 1
                    _bump_ss(row, ss, "controlled_entries")
                else:
                    row["shot_first_entries"] += 1
                    row["controlled_entries"] += 1
                    _bump_ss(row, ss, "controlled_entries")

                # Single SC source for all entry modes (avoids dump-follow vs window double count)
                shots, sc, _goals = _follow_sc_in_window(
                    plays, index, team, home_id, home_signs, period, second, FOLLOW_WINDOW_S
                )
                row["entry_shots"] += shots
                row["sc_off_entry"] += sc
                if mode == "dump" and sc:
                    row["sc_off_dump"] += sc
                    _bump_ss(row, ss, "sc_off_dump", sc)
                elif mode == "controlled" and sc:
                    row["sc_off_carry"] += sc
                    _bump_ss(row, ss, "sc_off_carry", sc)
                elif mode == "shot_first" and sc:
                    row["sc_off_shot_first"] += sc

                failed = _failed_entry_follow(plays, index, team, period, second)
                if failed:
                    row["failed_entries"] += 1
                    row[f"failed_entries_{lane}"] += 1
                    row[f"failed_entries_{mode}"] += 1
                    _bump_ss(row, ss, "failed_entries")
                    # credit opposing team as denial
                    opp = away_id if team == home_id else home_id
                    out[names[opp]]["entry_denials"] += 1

            # Exits: D → N/O
            if prev_zone == "D" and now_zone in {"N", "O"} and int(owner) == team:
                row["exits_total"] += 1
                row[f"exits_{lane}"] += 1
                xk = _exit_kind(kind or "", int(owner), team)
                if xk == "controlled":
                    row["controlled_exits"] += 1
                    row["exits_controlled"] += 1
                elif xk == "dump":
                    row["dump_outs"] += 1
                    row["exits_dump"] += 1
                else:
                    row["exits_other"] += 1
                    row["controlled_exits"] += 1

                if _failed_exit_follow(plays, index, team, period, second):
                    row["failed_exits"] += 1
                    row[f"failed_exits_{lane}"] += 1
                    row[f"failed_exits_{xk}"] += 1
                    _bump_ss(row, ss, "failed_exits")
                    opp = away_id if team == home_id else home_id
                    out[names[opp]]["forced_failed_exits"] += 1

        last = play
        if kind == "goal" and owner is not None:
            if int(owner) == home_id:
                home_goals += 1
            elif int(owner) == away_id:
                away_goals += 1

    # Schema v4 sequence extensions (exit→entry, NZ, cycle, dump-bin recovery, …)
    try:
        from nhl_pbp_microstats_v4 import enrich_game_v4

        out = enrich_game_v4(pbp, out)
    except Exception:
        pass
    return out


def rates_from_totals(totals: Dict[str, Any], games: int) -> Dict[str, Any]:
    """Derive rates / percentages from season aggregates."""
    g = max(1, games)
    rates: Dict[str, Any] = {"schema_version": SCHEMA_VERSION}

    for zone in ("oz", "nz", "dz"):
        gives = int(totals.get(f"giveaways_{zone}", 0))
        rates[f"giveaways_{zone}_per_game"] = round(gives / g, 2)
        pos = int(totals.get(f"positive_touches_{zone}", 0))
        fail = int(totals.get(f"failed_touches_{zone}", 0))
        touch_n = pos + fail
        rates[f"positive_touch_pct_{zone}"] = round(100.0 * pos / touch_n, 1) if touch_n else None
        zto = int(totals.get(f"zone_to_{zone}", 0))
        zsa = int(totals.get(f"zone_to_sa_{zone}", 0))
        rates[f"zone_to_shot_against_pct_{zone}"] = round(100.0 * zsa / zto, 1) if zto else None
        rates[f"zone_to_{zone}_per_game"] = round(zto / g, 2)

    entries = int(totals.get("entries_total", 0))
    dumps = int(totals.get("dump_ins", 0))
    controlled = int(totals.get("controlled_entries", 0))
    rates["controlled_entry_pct"] = round(100.0 * controlled / entries, 1) if entries else None
    rates["dump_in_pct"] = round(100.0 * dumps / entries, 1) if entries else None
    rates["dump_ins_per_game"] = round(dumps / g, 2)
    rates["controlled_entries_per_game"] = round(controlled / g, 2)
    rates["entries_per_game"] = round(entries / g, 2)

    dump_follow = int(totals.get("dump_ins_with_follow", 0)) or dumps
    dump_rec = int(totals.get("dump_ins_recovered", 0))
    rates["dump_in_recovery_pct"] = round(100.0 * dump_rec / dump_follow, 1) if dump_follow else None
    rates["dump_ins_recovered_per_game"] = round(dump_rec / g, 2)

    exits = int(totals.get("exits_total", 0))
    c_ex = int(totals.get("controlled_exits", 0))
    rates["controlled_exit_pct"] = round(100.0 * c_ex / exits, 1) if exits else None
    rates["controlled_exits_per_game"] = round(c_ex / g, 2)
    rates["dump_outs_per_game"] = round(int(totals.get("dump_outs", 0)) / g, 2)

    sc = int(totals.get("scoring_chances", 0))
    rates["sc_per_game"] = round(sc / g, 2)
    rates["sc_off_rush_per_game"] = round(int(totals.get("sc_off_rush", 0)) / g, 2)
    rates["sc_off_entry_per_game"] = round(int(totals.get("sc_off_entry", 0)) / g, 2)
    rates["sc_off_entry_pct"] = (
        round(100.0 * int(totals.get("sc_off_entry", 0)) / entries, 1) if entries else None
    )
    rates["sc_off_dump_per_game"] = round(int(totals.get("sc_off_dump", 0)) / g, 2)
    rates["sc_off_carry_per_game"] = round(int(totals.get("sc_off_carry", 0)) / g, 2)
    sc_dump = int(totals.get("sc_off_dump", 0))
    sc_carry = int(totals.get("sc_off_carry", 0))
    sc_modes = sc_dump + sc_carry
    rates["sc_off_dump_share_pct"] = round(100.0 * sc_dump / sc_modes, 1) if sc_modes else None
    rates["sc_off_carry_share_pct"] = round(100.0 * sc_carry / sc_modes, 1) if sc_modes else None
    rates["sc_per_dump_in"] = round(sc_dump / dumps, 3) if dumps else None
    rates["sc_per_controlled_entry"] = round(sc_carry / controlled, 3) if controlled else None

    rates["forecheck_recoveries_per_game"] = round(
        int(totals.get("forecheck_recoveries", 0)) / g, 2
    )
    rates["rush_shots_per_game"] = round(int(totals.get("rush_shots", 0)) / g, 2)
    slot_n = int(totals.get("slot_drives", 0))
    rates["slot_drives_per_game"] = round(slot_n / g, 2)
    rates["slot_drive_to_shot_pct"] = (
        round(100.0 * int(totals.get("slot_drives_to_shot", 0)) / slot_n, 1) if slot_n else None
    )
    rates["slot_drive_to_sc_pct"] = (
        round(100.0 * int(totals.get("slot_drives_to_sc", 0)) / slot_n, 1) if slot_n else None
    )
    rates["slot_drive_to_goal_pct"] = (
        round(100.0 * int(totals.get("slot_drives_to_goal", 0)) / slot_n, 1) if slot_n else None
    )

    dz_rec = int(totals.get("dz_recoveries", 0))
    dz_ex = int(totals.get("dz_recovery_to_exit", 0))
    dz_cex = int(totals.get("dz_recovery_to_controlled_exit", 0))
    dz_dex = int(totals.get("dz_recovery_to_dump_exit", 0))
    dz_fail = int(totals.get("dz_recovery_failed", 0))
    # Always denom = all DZ takeaways (never drop unresolved — they count as failed)
    rates["dz_recovery_to_exit_pct"] = round(100.0 * dz_ex / dz_rec, 1) if dz_rec else None
    rates["dz_retrieval_to_controlled_exit_pct"] = (
        round(100.0 * dz_cex / dz_rec, 1) if dz_rec else None
    )
    # Alias — same formula (old v4 used resolved-only denom and inflated %)
    rates["retrieval_to_controlled_exit_pct"] = rates["dz_retrieval_to_controlled_exit_pct"]
    rates["dz_retrieval_dump_exit_pct"] = round(100.0 * dz_dex / dz_rec, 1) if dz_rec else None
    rates["dz_retrieval_failed_pct"] = round(100.0 * dz_fail / dz_rec, 1) if dz_rec else None
    rates["dz_recoveries_per_game"] = round(dz_rec / g, 2)
    rates["dz_controlled_exit_from_retrieval_per_game"] = round(dz_cex / g, 2)
    rates["dz_retrieval_outcomes"] = {
        "controlled": dz_cex,
        "dump": dz_dex,
        "failed": dz_fail,
        "n": dz_rec,
    }

    fe = int(totals.get("failed_entries", 0))
    fx = int(totals.get("failed_exits", 0))
    rates["failed_entries_per_game"] = round(fe / g, 2)
    rates["failed_exits_per_game"] = round(fx / g, 2)
    rates["failed_entry_pct"] = round(100.0 * fe / entries, 1) if entries else None
    rates["failed_exit_pct"] = round(100.0 * fx / exits, 1) if exits else None
    rates["entry_denials_per_game"] = round(int(totals.get("entry_denials", 0)) / g, 2)
    rates["forced_failed_exits_per_game"] = round(
        int(totals.get("forced_failed_exits", 0)) / g, 2
    )

    rates["failed_entries_by_lane"] = {
        lane: int(totals.get(f"failed_entries_{lane}", 0)) for lane in _LANES
    }
    rates["failed_exits_by_lane"] = {
        lane: int(totals.get(f"failed_exits_{lane}", 0)) for lane in _LANES
    }
    rates["failed_entries_by_type"] = {
        et: int(totals.get(f"failed_entries_{et}", 0)) for et in _ENTRY_TYPES
    }
    rates["failed_exits_by_type"] = {
        xt: int(totals.get(f"failed_exits_{xt}", 0)) for xt in _EXIT_TYPES
    }
    rates["entries_by_lane"] = {lane: int(totals.get(f"entries_{lane}", 0)) for lane in _LANES}
    rates["exits_by_lane"] = {lane: int(totals.get(f"exits_{lane}", 0)) for lane in _LANES}

    # Score-state rate blocks
    score_state: Dict[str, Any] = {}
    for ss in _SS_KEYS:
        block: Dict[str, Any] = {}
        ss_entries = int(totals.get(f"ss_{ss}_entries_total", 0))
        ss_dumps = int(totals.get(f"ss_{ss}_dump_ins", 0))
        ss_ctrl = int(totals.get(f"ss_{ss}_controlled_entries", 0))
        ss_rec = int(totals.get(f"ss_{ss}_dump_ins_recovered", 0))
        block["entries"] = ss_entries
        block["dump_ins"] = ss_dumps
        block["controlled_entries"] = ss_ctrl
        block["controlled_entry_pct"] = (
            round(100.0 * ss_ctrl / ss_entries, 1) if ss_entries else None
        )
        block["dump_in_recovery_pct"] = (
            round(100.0 * ss_rec / ss_dumps, 1) if ss_dumps else None
        )
        block["sc"] = int(totals.get(f"ss_{ss}_scoring_chances", 0))
        block["sc_off_dump"] = int(totals.get(f"ss_{ss}_sc_off_dump", 0))
        block["sc_off_carry"] = int(totals.get(f"ss_{ss}_sc_off_carry", 0))
        block["forecheck_recoveries"] = int(totals.get(f"ss_{ss}_forecheck_recoveries", 0))
        block["failed_entries"] = int(totals.get(f"ss_{ss}_failed_entries", 0))
        block["failed_exits"] = int(totals.get(f"ss_{ss}_failed_exits", 0))
        block["failed_entry_pct"] = (
            round(100.0 * block["failed_entries"] / ss_entries, 1) if ss_entries else None
        )
        dzr = int(totals.get(f"ss_{ss}_dz_recoveries", 0))
        dzc = int(totals.get(f"ss_{ss}_dz_recovery_to_controlled_exit", 0))
        block["dz_retrieval_to_controlled_exit_pct"] = (
            round(100.0 * dzc / dzr, 1) if dzr else None
        )
        score_state[ss] = block
    rates["score_state"] = score_state

    # Forecheck pressure composite (0–100 soft-cap blend)
    fc_pg = float(rates["forecheck_recoveries_per_game"] or 0)
    dump_rec_pct = float(rates["dump_in_recovery_pct"] or 0)
    oz_ta_pg = round(int(totals.get("takeaways_oz", 0)) / g, 2)
    rates["takeaways_oz_per_game"] = oz_ta_pg
    denials_pg = float(rates["entry_denials_per_game"] or 0)
    forced_fx_pg = float(rates["forced_failed_exits_per_game"] or 0)
    # soft caps based on typical NHL ranges
    c_fc = min(1.0, fc_pg / 8.0)
    c_dr = min(1.0, dump_rec_pct / 55.0)
    c_oz = min(1.0, oz_ta_pg / 5.0)
    c_den = min(1.0, denials_pg / 6.0)
    c_fx = min(1.0, forced_fx_pg / 5.0)
    rates["forecheck_pressure_index"] = round(
        100.0 * (0.30 * c_fc + 0.20 * c_dr + 0.20 * c_oz + 0.15 * c_den + 0.15 * c_fx), 1
    )
    rates["forecheck_pressure_components"] = {
        "forecheck_recoveries_per_game": fc_pg,
        "dump_in_recovery_pct": rates["dump_in_recovery_pct"],
        "takeaways_oz_per_game": oz_ta_pg,
        "entry_denials_per_game": denials_pg,
        "forced_failed_exits_per_game": forced_fx_pg,
    }

    dump_keys = [
        "dump_landing_strong_corner",
        "dump_landing_weak_corner",
        "dump_landing_strong_rim",
        "dump_landing_weak_rim",
        "dump_landing_deep_slot",
        "dump_landing_short_nz",
    ]
    dump_total = sum(int(totals.get(k, 0)) for k in dump_keys) or 0
    rates["dump_landing_mix"] = {
        k.replace("dump_landing_", ""): round(100.0 * int(totals.get(k, 0)) / dump_total, 1)
        if dump_total
        else None
        for k in dump_keys
    }

    rates["puck_battle_win_pct_by_zone"] = None
    rates["puck_battle_win_pct_by_zone_note"] = "requires_instat_action_pbp_not_gear"

    try:
        from nhl_pbp_microstats_v4 import rates_v4

        rates.update(rates_v4(totals, games))
        rates["schema_version"] = SCHEMA_VERSION
    except Exception:
        pass

    return rates


# Metric catalog for research / expansion (daily NHL + InStat overlap)
NHL_DAILY_MICROSTATS_CATALOG: Dict[str, Dict[str, str]] = {
    "giveaways_by_zone": {"status": "automated", "source": "nhl_pbp", "notes": "giveaway counts O/N/D"},
    "turnover_rate_per_zone": {"status": "automated", "source": "nhl_pbp", "notes": "per-game giveaway rates by zone"},
    "positive_vs_failed_touches_by_zone": {
        "status": "proxy",
        "source": "nhl_pbp",
        "notes": "positive=takeaway/shot/hit; failed=giveaway — not InStat touch tags",
    },
    "forecheck_recoveries": {"status": "proxy", "source": "nhl_pbp", "notes": "OZ takeaways"},
    "forecheck_pressure_composite": {
        "status": "automated",
        "source": "nhl_pbp",
        "notes": "0-100 blend of FC recoveries, dump recovery%, OZ TA, denials, forced failed exits",
    },
    "controlled_exits": {"status": "proxy", "source": "nhl_pbp", "notes": "D→N/O with possession-family first event"},
    "controlled_entries": {"status": "automated", "source": "nhl_pbp", "notes": "dump-in research entry_kind"},
    "dump_ins": {"status": "automated", "source": "nhl_pbp", "notes": "non-controlled first OZ touch"},
    "dump_in_locations": {"status": "automated", "source": "nhl_pbp", "notes": "corner/rim/slot/short bins"},
    "dump_in_recovery_pct": {
        "status": "automated",
        "source": "nhl_pbp",
        "notes": "later OZ own event within 10s (arrival excluded)",
    },
    "scoring_chances_off_rush": {"status": "automated", "source": "nhl_pbp", "notes": "SC within 6s of possession change"},
    "scoring_chances_off_entries": {"status": "automated", "source": "nhl_pbp", "notes": "SC within 10s of entry"},
    "sc_off_dump_vs_carry": {
        "status": "automated",
        "source": "nhl_pbp",
        "notes": "SC in entry window split by dump vs controlled",
    },
    "slot_driving_plays": {"status": "proxy", "source": "nhl_pbp", "notes": "slot arrival after outside-slot own event ≤5s"},
    "slot_drive_conversion": {
        "status": "automated",
        "source": "nhl_pbp",
        "notes": "slot drive → shot/SC/goal within 6s",
    },
    "dz_recovery_to_exit_rate": {"status": "proxy", "source": "nhl_pbp", "notes": "DZ takeaway → N/O within 12s"},
    "dz_retrieval_to_controlled_exit_pct": {
        "status": "automated",
        "source": "nhl_pbp",
        "notes": "DZ takeaway → controlled exit within 12s",
    },
    "zone_to_shot_against": {
        "status": "automated",
        "source": "nhl_pbp",
        "notes": "giveaway → opp unblocked shot within 8s by zone",
    },
    "failed_entries": {
        "status": "automated",
        "source": "nhl_pbp",
        "notes": "entry then TO/opp touch before shot; by lane + type",
    },
    "failed_exits": {
        "status": "automated",
        "source": "nhl_pbp",
        "notes": "exit then opp press/shot within 7s; by lane + type",
    },
    "score_state_splits": {
        "status": "automated",
        "source": "nhl_pbp",
        "notes": "tied/leading/trailing splits for entries, dumps, SC, FC, failures",
    },
    "puck_battle_win_rate_by_zone": {
        "status": "partial",
        "source": "instat",
        "notes": "wired via instat flat aliases when present; else missing",
    },
    "carry_in_pct": {
        "status": "partial",
        "source": "instat+nhl_pbp",
        "notes": "InStat EN/ENP/END alias + PBP controlled_entry_pct",
    },
    "entry_denials": {"status": "automated", "source": "nhl_pbp", "notes": "opp failed entries credited as denials"},
    "cycle_shots": {"status": "proxy", "source": "nhl_pbp", "notes": "existing ExperimentalMetricsAnalyzer"},
    "nz_turnovers_to_shots": {"status": "proxy", "source": "nhl_pbp", "notes": "existing nzt/nztsa in team stats"},
    "passes_to_slot": {"status": "missing", "source": "instat", "notes": "InStat action"},
    "royal_road_shots": {"status": "missing", "source": "instat_or_tracking", "notes": "needs pass path"},
    "fc_to_shot_pct": {"status": "missing", "source": "instat", "notes": "needs true FC recoveries"},
    "shot_first_entries": {"status": "automated", "source": "nhl_pbp", "notes": "entry arrival is shot attempt"},
    "dump_outs": {"status": "proxy", "source": "nhl_pbp", "notes": "uncontrolled D→N/O exit"},
    "entry_shots": {"status": "automated", "source": "nhl_pbp", "notes": "shots within 10s of entry"},
    "rush_goals": {"status": "automated", "source": "nhl_pbp", "notes": "goals in rush window"},
    "slot_drives_via_carry": {"status": "proxy", "source": "nhl_pbp", "notes": "same player into slot"},
    "slot_drives_via_pass": {"status": "proxy", "source": "nhl_pbp", "notes": "teammate then slot shot"},
    "takeaways_by_zone": {"status": "automated", "source": "nhl_pbp", "notes": "O/N/D takeaways"},
    "skater_grain_all_of_above": {
        "status": "automated",
        "source": "metrics-warehouse/pipelines/nhl_skater_game_microstats.py",
        "notes": "per-player season aggregates",
    },
    "goalie_lld_full": {
        "status": "automated",
        "source": "nhl-goalie-hub → metrics-warehouse ingest_lld_goalies",
        "notes": "GSAx, danger, rebound, derived, instat charted",
    },
    "instat_skater_season": {
        "status": "conditional",
        "source": "instat_api gear 1",
        "notes": "requires auth; see curated/status/instat.json",
    },
    "instat_goalie_season": {
        "status": "conditional",
        "source": "instat_api gear 9",
        "notes": "requires auth; LLD aggs mirrored always",
    },
}
