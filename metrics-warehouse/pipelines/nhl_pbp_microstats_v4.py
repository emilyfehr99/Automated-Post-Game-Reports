#!/usr/bin/env python3
"""Schema-v4 microstat extensions (NHL PBP sequences only).

Honest labels:
  - All counters here are NHL official PBP geometry/sequence proxies.
  - True InStat entries/battles/FC tags are NOT invented here — see combine_microstats.py.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from nhl_pbp_microstats import (
    BLUE_X,
    DOT_X,
    ENTRY_GAP_S,
    FOLLOW_WINDOW_S,
    GOAL_X,
    OFFENSE_CONTROLLED,
    RUSH_WINDOW_S,
    STOPPAGES,
    UNBLOCKED_SHOTS,
    _attack_sign,
    _clock_seconds,
    _dump_follow_up,
    _exit_after_dz_recovery,
    _home_attack_sign,
    _is_slot,
    _landing_key,
    _rink_xy,
    _zone_for,
    classify_landing,
    entry_kind,
)

SCHEMA_VERSION = 4
EXIT_ENTRY_CHAIN_S = 12.0
NZ_PLAY_WINDOW_S = 12.0
CYCLE_LOOKBACK_S = 15.0
CYCLE_MIN_OZ_EVENTS = 3
REBOUND_WINDOW_S = 3.0
BEHIND_NET_TO_SLOT_S = 5.0
DUMP_LANDINGS = (
    "strong_corner",
    "weak_corner",
    "strong_rim",
    "weak_rim",
    "deep_slot",
    "short_nz",
)


def v4_empty_fields() -> Dict[str, Any]:
    row: Dict[str, Any] = {
        # Exit → entry chain
        "controlled_exits_chain_eligible": 0,
        "controlled_exits_to_controlled_entry": 0,
        # NZ play outcomes
        "nz_plays": 0,
        "nz_plays_advance": 0,
        "nz_plays_die": 0,
        # Cycle vs rush (rush_shots already in v3)
        "cycle_shots": 0,
        "cycle_goals": 0,
        # Retrieval quality after DZ takeaway
        "dz_ret_to_controlled_exit": 0,
        "dz_ret_to_dump_out": 0,
        "dz_ret_to_giveaway": 0,
        "dz_ret_exit_time_sum": 0.0,
        "dz_ret_exit_time_n": 0,
        # Rebound second chances
        "rebound_shot_opportunities": 0,
        "rebound_second_chance_shots": 0,
        "rebound_second_chance_goals": 0,
        # Behind-net / low-to-high
        "behind_net_touches": 0,
        "behind_net_to_slot_shot": 0,
        "behind_net_to_slot_goal": 0,
        # Strength / period splits (key event counts)
        "ev5v5_entries": 0,
        "ev5v5_controlled_entries": 0,
        "ev5v5_dump_ins": 0,
        "ev5v5_scoring_chances": 0,
        "ev5v5_giveaways": 0,
        "st_entries": 0,  # non-5v5
        "st_scoring_chances": 0,
        "p1_entries": 0,
        "p1_scoring_chances": 0,
        "p1_giveaways": 0,
        "p1_dump_ins": 0,
        "p3_entries": 0,
        "p3_scoring_chances": 0,
        "p3_giveaways": 0,
        "p3_dump_ins": 0,
        "schema_version": SCHEMA_VERSION,
        "source_note": "nhl_pbp_sequence_proxy",
    }
    for land in DUMP_LANDINGS:
        row[f"dump_landing_{land}"] = 0  # may already exist on base
        row[f"dump_rec_{land}"] = 0
        row[f"dump_att_{land}"] = 0
    return row


def _is_5v5(situation_code: Optional[str]) -> bool:
    return situation_code == "1551"


def _ensure_v4(row: Dict[str, Any]) -> None:
    for k, v in v4_empty_fields().items():
        if k not in row:
            row[k] = v
        elif k == "schema_version":
            row[k] = SCHEMA_VERSION


def _controlled_entry_after_exit(
    plays: List[dict],
    start: int,
    team: int,
    home_id: int,
    home_signs: Dict[int, int],
    period: int,
    second: int,
) -> bool:
    last = plays[start]
    for index in range(start + 1, len(plays)):
        play = plays[index]
        play_period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if play_period != period:
            return False
        kind = play.get("typeDescKey")
        if kind in STOPPAGES:
            return False
        sec = _clock_seconds(play.get("timeInPeriod"))
        if sec - second > EXIT_ENTRY_CHAIN_S:
            return False
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        zone = details.get("zoneCode")
        if (
            owner is None
            or zone not in {"O", "D", "N"}
            or details.get("xCoord") is None
            or details.get("yCoord") is None
        ):
            continue
        prev = last.get("details") or {}
        if prev.get("xCoord") is None or prev.get("zoneCode") not in {"O", "D", "N"}:
            last = play
            continue
        now_z = _zone_for(int(owner), zone, team)
        prev_z = _zone_for(int(prev["eventOwnerTeamId"]), prev["zoneCode"], team)
        if now_z == "O" and prev_z in {"N", "D"}:
            sign = _attack_sign(home_signs, period, team, home_id)
            if sign is None:
                return False
            x1r, _y1 = _rink_xy(play, home_signs, home_id)
            x0r, _y0 = _rink_xy(last, home_signs, home_id)
            mode = entry_kind(last, play, team, sec - _clock_seconds(last.get("timeInPeriod")), x0r * sign, x1r * sign)
            return mode in {"controlled", "shot_first"}
        last = play
    return False


def _nz_play_outcome(
    plays: List[dict], start: int, team: int, period: int, second: int
) -> str:
    """Return 'advance' | 'die' after a NZ possession starts.

    Advance = puck reaches the team's OZ (any event whose zone maps to O for
    this team — includes dumps where the opponent is first to touch in their D).
    Die = giveaway while still NZ/DZ, retreat to DZ without OZ, stoppage, or
    window expiry.
    """
    for play in plays[start + 1 :]:
        play_period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if play_period != period:
            return "die"
        dt = _clock_seconds(play.get("timeInPeriod")) - second
        if dt > NZ_PLAY_WINDOW_S:
            return "die"
        kind = play.get("typeDescKey")
        if kind in STOPPAGES:
            return "die"
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        zone = details.get("zoneCode")
        if owner is None or zone not in {"O", "D", "N"}:
            continue
        tz = _zone_for(int(owner), zone, team)
        # Puck in our OZ = successful NZ advance (carry OR dump)
        if tz == "O":
            return "advance"
        if int(owner) == team and kind == "giveaway":
            return "die"
        if int(owner) == team and tz == "D":
            return "die"
        # Opp gains a NZ/DZ touch without the puck having entered our OZ
        if int(owner) != team and tz in {"N", "D"} and kind in {
            "takeaway",
            "hit",
            "blocked-shot",
        } | UNBLOCKED_SHOTS:
            return "die"
    return "die"


def _oz_event_count_before_shot(
    plays: List[dict],
    shot_index: int,
    team: int,
    period: int,
    second: int,
) -> int:
    n = 0
    for i in range(shot_index - 1, -1, -1):
        play = plays[i]
        play_period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if play_period != period:
            break
        dt = second - _clock_seconds(play.get("timeInPeriod"))
        if dt > CYCLE_LOOKBACK_S or dt < 0:
            break
        kind = play.get("typeDescKey")
        if kind in STOPPAGES:
            break
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        zone = details.get("zoneCode")
        if owner == team and zone == "O":
            n += 1
        elif owner is not None and int(owner) != team:
            break
    return n


def _rebound_follow(
    plays: List[dict], start: int, team: int, period: int, second: int
) -> Tuple[bool, bool]:
    """(second_chance_shot, second_chance_goal) within rebound window."""
    for play in plays[start + 1 :]:
        play_period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if play_period != period:
            return False, False
        dt = _clock_seconds(play.get("timeInPeriod")) - second
        if dt > REBOUND_WINDOW_S:
            return False, False
        kind = play.get("typeDescKey")
        if kind in STOPPAGES:
            return False, False
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        if owner is None:
            continue
        if int(owner) != team:
            if kind in UNBLOCKED_SHOTS or kind == "takeaway":
                return False, False
            continue
        if kind in UNBLOCKED_SHOTS:
            return True, kind == "goal"
    return False, False


def _behind_net_to_slot(
    plays: List[dict],
    start: int,
    team: int,
    home_id: int,
    home_signs: Dict[int, int],
    period: int,
    second: int,
) -> Tuple[bool, bool]:
    for play in plays[start + 1 :]:
        play_period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if play_period != period:
            return False, False
        dt = _clock_seconds(play.get("timeInPeriod")) - second
        if dt > BEHIND_NET_TO_SLOT_S:
            return False, False
        kind = play.get("typeDescKey")
        if kind in STOPPAGES:
            return False, False
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        if owner != team or kind not in UNBLOCKED_SHOTS or details.get("xCoord") is None:
            continue
        sign = _attack_sign(home_signs, period, team, home_id)
        if sign is None:
            continue
        x, y = _rink_xy(play, home_signs, home_id)
        if _is_slot(x * sign, y * sign):
            return True, kind == "goal"
    return False, False


def _retrieval_first_outcome(
    plays: List[dict], start: int, team: int, period: int, second: int
) -> Tuple[Optional[str], Optional[float]]:
    """('controlled'|'dump'|'giveaway', seconds) after DZ takeaway."""
    for play in plays[start + 1 :]:
        play_period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        if play_period != period:
            return None, None
        dt = _clock_seconds(play.get("timeInPeriod")) - second
        if dt > 12:
            return None, None
        kind = play.get("typeDescKey")
        if kind in STOPPAGES:
            return None, None
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        zone = details.get("zoneCode")
        if owner is None or zone not in {"O", "D", "N"}:
            continue
        if int(owner) == team and kind == "giveaway":
            return "giveaway", float(dt)
        tz = _zone_for(int(owner), zone, team)
        if int(owner) == team and tz in {"N", "O"}:
            if kind in OFFENSE_CONTROLLED or kind == "hit":
                return "controlled", float(dt)
            return "dump", float(dt)
        if int(owner) != team and zone == "O":
            return "giveaway", float(dt)
    return None, None


def enrich_game_v4(pbp: dict, out: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Mutate per-team microstat rows with v4 counters."""
    plays = pbp.get("plays") or []
    if len(plays) < 20 or not out:
        return out

    home = pbp.get("homeTeam") or {}
    away = pbp.get("awayTeam") or {}
    home_id = int(home.get("id") or 0)
    away_id = int(away.get("id") or 0)
    home_abbr = home.get("abbrev") or "H"
    away_abbr = away.get("abbrev") or "A"
    names = {home_id: home_abbr, away_id: away_abbr}
    for row in out.values():
        _ensure_v4(row)

    home_signs = _home_attack_sign(plays, home_id)
    last_poss_change: Dict[int, float] = {home_id: -999.0, away_id: -999.0}
    # Last zone where this team last touched the puck (owner-perspective zone)
    last_touch_zone: Dict[int, Optional[str]] = {home_id: None, away_id: None}

    # Pass A: shots/cycle/rebound/behind-net/NZ/retrieval + period/strength SC-giveaways
    for index, play in enumerate(plays):
        kind = play.get("typeDescKey") or ""
        details = play.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        zone = details.get("zoneCode")
        period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        second = _clock_seconds(play.get("timeInPeriod"))
        game_sec = (period - 1) * 1200 + second
        sit = play.get("situationCode")
        ev = _is_5v5(sit)

        if kind in STOPPAGES:
            # break NZ streaks on stoppages
            if kind != "faceoff":
                last_touch_zone[home_id] = None
                last_touch_zone[away_id] = None
            continue

        if owner is None or zone not in {"O", "D", "N"}:
            continue
        owner = int(owner)
        if owner not in names:
            continue
        row = out[names[owner]]
        _ensure_v4(row)

        if kind == "giveaway":
            if ev:
                row["ev5v5_giveaways"] += 1
            if period == 1:
                row["p1_giveaways"] += 1
            elif period == 3:
                row["p3_giveaways"] += 1
            last_poss_change[away_id if owner == home_id else home_id] = float(game_sec)

        if kind == "takeaway":
            last_poss_change[owner] = float(game_sec)
            if zone == "D":
                # Mirror base classifier (same denom/rules) + time-to-exit when successful
                outcome = _exit_after_dz_recovery(
                    plays,
                    index,
                    owner,
                    period,
                    second,
                    home_id=home_id,
                    home_signs=home_signs,
                )
                if outcome == "controlled":
                    row["dz_ret_to_controlled_exit"] += 1
                elif outcome == "dump":
                    row["dz_ret_to_dump_out"] += 1
                else:
                    row["dz_ret_to_giveaway"] += 1  # failed bucket (legacy key)
                # time-to-exit: scan until leave DZ
                for play2 in plays[index + 1 :]:
                    p2 = int((play2.get("periodDescriptor") or {}).get("number") or 0)
                    if p2 != period:
                        break
                    dt2 = _clock_seconds(play2.get("timeInPeriod")) - second
                    if dt2 > 15:
                        break
                    if outcome not in {"controlled", "dump"}:
                        break
                    d2 = play2.get("details") or {}
                    if d2.get("eventOwnerTeamId") == owner and d2.get("zoneCode") in {"N", "O"}:
                        row["dz_ret_exit_time_sum"] += float(dt2)
                        row["dz_ret_exit_time_n"] += 1
                        break

        # NZ play: first team touch in NZ after a non-NZ touch (true possession starts)
        if zone == "N" and kind != "faceoff":
            prev_z = last_touch_zone.get(owner)
            if prev_z != "N":
                outcome = _nz_play_outcome(plays, index, owner, period, second)
                row["nz_plays"] += 1
                if outcome == "advance":
                    row["nz_plays_advance"] += 1
                else:
                    row["nz_plays_die"] += 1
            last_touch_zone[owner] = "N"
        elif zone in {"O", "D"}:
            last_touch_zone[owner] = zone

        # Behind-net: attacking-frame x strictly past the goal line
        if (
            details.get("xCoord") is not None
            and details.get("yCoord") is not None
            and kind not in STOPPAGES
        ):
            sign = _attack_sign(home_signs, period, owner, home_id)
            if sign is not None and zone == "O":
                x, y = _rink_xy(play, home_signs, home_id)
                x_att = x * sign
                if x_att > GOAL_X:
                    row["behind_net_touches"] += 1
                    to_slot, to_goal = _behind_net_to_slot(
                        plays, index, owner, home_id, home_signs, period, second
                    )
                    if to_slot:
                        row["behind_net_to_slot_shot"] += 1
                    if to_goal:
                        row["behind_net_to_slot_goal"] += 1

        if kind in UNBLOCKED_SHOTS and details.get("xCoord") is not None:
            if ev:
                # SC proxy counted in base; here only 5v5 SC via distance already in base —
                # count all unblocked as SC bucket only when base marks SC — skip duplicate.
                pass
            sign = _attack_sign(home_signs, period, owner, home_id)
            rush = game_sec - last_poss_change[owner] <= RUSH_WINDOW_S and last_poss_change[owner] > 0
            if zone == "O" and not rush:
                oz_n = _oz_event_count_before_shot(plays, index, owner, period, second)
                if oz_n >= CYCLE_MIN_OZ_EVENTS:
                    row["cycle_shots"] += 1
                    if kind == "goal":
                        row["cycle_goals"] += 1
            # Rebound opportunity: non-goal shot
            if kind in {"shot-on-goal", "missed-shot"} and zone == "O":
                row["rebound_shot_opportunities"] += 1
                sc_shot, sc_goal = _rebound_follow(plays, index, owner, period, second)
                if sc_shot:
                    row["rebound_second_chance_shots"] += 1
                if sc_goal:
                    row["rebound_second_chance_goals"] += 1

            # period / strength SC: use distance SC from base geometry
            if sign is not None:
                from nhl_pbp_microstats import _is_scoring_chance

                x, y = _rink_xy(play, home_signs, home_id)
                if _is_scoring_chance(x * sign, y * sign):
                    if ev:
                        row["ev5v5_scoring_chances"] += 1
                    else:
                        row["st_scoring_chances"] += 1
                    if period == 1:
                        row["p1_scoring_chances"] += 1
                    elif period == 3:
                        row["p3_scoring_chances"] += 1

    # Pass B: entry/exit chains + dump recovery by landing + period/strength entries
    last: Optional[dict] = None
    for index, play in enumerate(plays):
        kind = play.get("typeDescKey")
        period = int((play.get("periodDescriptor") or {}).get("number") or 0)
        second = _clock_seconds(play.get("timeInPeriod"))
        details = play.get("details") or {}
        sit = play.get("situationCode")
        ev = _is_5v5(sit)

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
            continue
        if last is None or int((last.get("periodDescriptor") or {}).get("number") or 0) != period:
            last = play
            continue
        dt = second - _clock_seconds(last.get("timeInPeriod"))
        if dt <= 0 or dt > ENTRY_GAP_S:
            last = play
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
            _ensure_v4(row)
            sign = _attack_sign(home_signs, period, team, home_id)
            if sign is None:
                continue
            x1_raw, y1_raw = _rink_xy(play, home_signs, home_id)
            x0_raw, y0_raw = _rink_xy(last, home_signs, home_id)
            x1, y1 = x1_raw * sign, y1_raw * sign
            x0, y0 = x0_raw * sign, y0_raw * sign

            if now_zone == "O" and prev_zone in {"N", "D"}:
                mode = entry_kind(last, play, team, dt, x0, x1)
                if period == 1:
                    row["p1_entries"] += 1
                    if mode == "dump":
                        row["p1_dump_ins"] += 1
                elif period == 3:
                    row["p3_entries"] += 1
                    if mode == "dump":
                        row["p3_dump_ins"] += 1
                if ev:
                    row["ev5v5_entries"] += 1
                    if mode == "dump":
                        row["ev5v5_dump_ins"] += 1
                    else:
                        row["ev5v5_controlled_entries"] += 1
                else:
                    row["st_entries"] += 1

                if mode == "dump":
                    landing = classify_landing(y0, x1, y1)
                    lk = _landing_key(landing).replace("dump_landing_", "")
                    row[f"dump_att_{lk}"] = int(row.get(f"dump_att_{lk}") or 0) + 1
                    recovered, _, _ = _dump_follow_up(
                        plays, index, team, home_id, home_signs, period, second
                    )
                    if recovered:
                        row[f"dump_rec_{lk}"] = int(row.get(f"dump_rec_{lk}") or 0) + 1

            if prev_zone == "D" and now_zone in {"N", "O"} and int(owner) == team:
                xk_controlled = kind in OFFENSE_CONTROLLED or kind == "hit"
                if xk_controlled:
                    row["controlled_exits_chain_eligible"] += 1
                    if _controlled_entry_after_exit(
                        plays, index, team, home_id, home_signs, period, second
                    ):
                        row["controlled_exits_to_controlled_entry"] += 1

        last = play

    return out


def rates_v4(totals: Dict[str, Any], games: int) -> Dict[str, Any]:
    g = max(1, games)
    rates: Dict[str, Any] = {"schema_version": SCHEMA_VERSION}

    elig = int(totals.get("controlled_exits_chain_eligible", 0))
    chained = int(totals.get("controlled_exits_to_controlled_entry", 0))
    rates["exit_to_entry_chain_pct"] = round(100.0 * chained / elig, 1) if elig else None
    rates["exit_to_entry_chain_per_game"] = round(chained / g, 2)

    nz = int(totals.get("nz_plays", 0))
    nz_adv = int(totals.get("nz_plays_advance", 0))
    rates["nz_advance_pct"] = round(100.0 * nz_adv / nz, 1) if nz else None
    rates["nz_plays_per_game"] = round(nz / g, 2)
    rates["nz_die_pct"] = (
        round(100.0 * int(totals.get("nz_plays_die", 0)) / nz, 1) if nz else None
    )

    cycle = int(totals.get("cycle_shots", 0))
    rush = int(totals.get("rush_shots", 0))
    mix = cycle + rush
    rates["cycle_shots_per_game"] = round(cycle / g, 2)
    rates["rush_shots_per_game"] = round(rush / g, 2)
    rates["cycle_shot_share_pct"] = round(100.0 * cycle / mix, 1) if mix else None
    rates["rush_shot_share_pct"] = round(100.0 * rush / mix, 1) if mix else None

    dump_rec_by_bin = {}
    for land in DUMP_LANDINGS:
        att = int(totals.get(f"dump_att_{land}", 0))
        rec = int(totals.get(f"dump_rec_{land}", 0))
        dump_rec_by_bin[land] = round(100.0 * rec / att, 1) if att else None
    rates["dump_recovery_pct_by_landing"] = dump_rec_by_bin

    # Prefer base denom (all DZ takeaways). v4 keys kept for time-to-exit only.
    dz_rec = int(totals.get("dz_recoveries", 0))
    ret_c = int(totals.get("dz_recovery_to_controlled_exit", 0)) or int(
        totals.get("dz_ret_to_controlled_exit", 0)
    )
    ret_d = int(totals.get("dz_recovery_to_dump_exit", 0)) or int(
        totals.get("dz_ret_to_dump_out", 0)
    )
    ret_g = int(totals.get("dz_recovery_failed", 0)) or int(
        totals.get("dz_ret_to_giveaway", 0)
    )
    # Do NOT use resolved-only denom — that made 1/1 = 100% ghosts
    rates["retrieval_to_controlled_exit_pct"] = (
        round(100.0 * ret_c / dz_rec, 1) if dz_rec else None
    )
    rates["retrieval_to_dump_out_pct"] = round(100.0 * ret_d / dz_rec, 1) if dz_rec else None
    rates["retrieval_botched_giveaway_pct"] = (
        round(100.0 * ret_g / dz_rec, 1) if dz_rec else None
    )
    rates["retrieval_controlled_per_game"] = round(ret_c / g, 2)
    tn = int(totals.get("dz_ret_exit_time_n", 0))
    rates["retrieval_avg_time_to_exit_s"] = (
        round(float(totals.get("dz_ret_exit_time_sum", 0.0)) / tn, 2) if tn else None
    )

    reb_opp = int(totals.get("rebound_shot_opportunities", 0))
    reb_sc = int(totals.get("rebound_second_chance_shots", 0))
    rates["rebound_second_chance_pct"] = (
        round(100.0 * reb_sc / reb_opp, 1) if reb_opp else None
    )
    rates["rebound_second_chance_per_game"] = round(reb_sc / g, 2)

    bn = int(totals.get("behind_net_touches", 0))
    bn_slot = int(totals.get("behind_net_to_slot_shot", 0))
    rates["behind_net_to_slot_pct"] = round(100.0 * bn_slot / bn, 1) if bn else None
    rates["behind_net_touches_per_game"] = round(bn / g, 2)

    rates["ev5v5_controlled_entry_pct"] = (
        round(
            100.0
            * int(totals.get("ev5v5_controlled_entries", 0))
            / int(totals.get("ev5v5_entries", 0)),
            1,
        )
        if int(totals.get("ev5v5_entries", 0))
        else None
    )
    rates["p1_entries_per_game"] = round(int(totals.get("p1_entries", 0)) / g, 2)
    rates["p3_entries_per_game"] = round(int(totals.get("p3_entries", 0)) / g, 2)
    rates["p1_sc_per_game"] = round(int(totals.get("p1_scoring_chances", 0)) / g, 2)
    rates["p3_sc_per_game"] = round(int(totals.get("p3_scoring_chances", 0)) / g, 2)
    p1e = int(totals.get("p1_entries", 0))
    p3e = int(totals.get("p3_entries", 0))
    rates["p3_vs_p1_entry_ratio"] = round(p3e / p1e, 2) if p1e else None

    rates["source"] = "nhl_pbp_sequence_proxy"
    return rates
