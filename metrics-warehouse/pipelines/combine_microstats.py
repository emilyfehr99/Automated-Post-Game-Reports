#!/usr/bin/env python3
"""Combine NHL PBP microstats + InStat gear + NHL TOI.

Rules (no fake data):
  - PBP sequence metrics: from curated team/skater PBP only.
  - InStat: only real gear columns / derived ratios from those columns.
  - Action-PBP-only metrics (true battle win%, passes-to-slot, true FC→shot,
    InStat botched retrievals): explicitly null with reason — never imputed.
"""

from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from paths import CURATED, ensure_dirs

USER_AGENT = "metrics-warehouse/1.0"
NHL_TEAMS = [
    "ANA", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL", "DAL", "DET",
    "EDM", "FLA", "LAK", "MIN", "MTL", "NSH", "NJD", "NYI", "NYR", "OTT",
    "PHI", "PIT", "SEA", "SJS", "STL", "TBL", "TOR", "UTA", "VAN", "VGK",
    "WPG", "WSH",
]

# Still need match-level InStat action PBP (logic exists in player_cards /
# clarkson-analytics — warehouse does not store NHL InStat PBP CSVs yet).
UNAVAILABLE_ACTION_PBP = {
    "puck_battle_win_pct_by_zone": "requires_instat_action_pbp_won_lost_by_zone",
    "fc_to_shot_pct_true": "requires_instat_action_pbp_oz_recovery_to_fc_shot",
    "botched_retrievals_instat": "requires_instat_action_pbp_dz_recovery_to_turnover",
}

# Wired from gear-1 (real columns) — no longer unavailable.
GEAR1_NOW_AVAILABLE = {
    "passes_to_slot": "PTTS / Slot Pass (param 271)",
    "successful_entries_instat_tagged": "ENS (param 105)",
}


def _toi_to_seconds(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s or s in {"--", "null"}:
        return None
    if ":" in s:
        parts = s.split(":")
        try:
            if len(parts) == 2:
                return int(parts[0]) * 60 + float(parts[1])
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        except ValueError:
            return None
    try:
        return float(s)
    except ValueError:
        return None


def fetch_club_toi() -> Dict[int, Dict[str, Any]]:
    """playerId → {toi_seconds_season_est, avg_toi_per_game, gp, team, name}."""
    out: Dict[int, Dict[str, Any]] = {}
    for abbr in NHL_TEAMS:
        url = f"https://api-web.nhle.com/v1/club-stats/{abbr}/now"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.load(resp)
        except Exception:
            continue
        for row in data.get("skaters") or []:
            pid = row.get("playerId")
            if not pid:
                continue
            avg = _toi_to_seconds(row.get("avgTimeOnIcePerGame"))
            gp = int(row.get("gamesPlayed") or 0)
            if avg is None or gp <= 0:
                continue
            first = (row.get("firstName") or {}).get("default") or ""
            last = (row.get("lastName") or {}).get("default") or ""
            out[int(pid)] = {
                "player_id": int(pid),
                "name": f"{first} {last}".strip(),
                "team": abbr,
                "gp_nhl": gp,
                "avg_toi_per_game_s": avg,
                "toi_seconds_est": avg * gp,
                "source": "nhl_club_stats",
            }
    return out


def _num(row: dict, *keys: str) -> Optional[float]:
    for k in keys:
        if k not in row or row[k] is None or row[k] == "":
            continue
        try:
            return float(row[k])
        except (TypeError, ValueError):
            continue
    return None


def instat_derived(row: Dict[str, Any]) -> Dict[str, Any]:
    """Only ratios from real gear numbers. No invented battle win% / slot passes."""
    from real_data import strip_proxy_standins

    en = _num(row, "entries_stickhandle", "EN")
    enp = _num(row, "entries_pass", "ENP")
    end = _num(row, "entries_dump", "END")
    do = _num(row, "dump_outs", "DO")
    ta_oz = _num(row, "takeaways_oz", "TA (OZ)")
    ozrt = _num(row, "oz_recoveries", "OZRT (OZ)")
    dzrt = _num(row, "dz_recoveries", "DZRT (DZ)")
    lpr = _num(row, "loose_puck_recoveries", "LPR")
    brs = _num(row, "battles_engaged", "BRS")
    fa = _num(row, "failed_attacks", "FA")
    ptts = _num(row, "passes_to_slot", "PTTS", "Slot Pass")
    ens = _num(row, "successful_entries_instat_tagged", "ENS")
    gp = _num(row, "GP") or 0.0

    ctrl = (en or 0.0) + (enp or 0.0)
    # No DI→END substitution — carry-in only when END exists.
    carry = (
        round(100.0 * ctrl / (ctrl + end), 1)
        if end is not None and (ctrl + end) > 0
        else None
    )

    derived = {
        "source": "instat_gear1",
        "real_data_only": True,
        "carry_in_pct": carry,
        "entries_controlled_gear": ctrl if (en is not None or enp is not None) else None,
        "entries_dump_gear": end,
        "dump_outs_gear": do,
        "battles_engaged": brs,
        "battles_engaged_per_game": round(brs / gp, 2) if brs is not None and gp > 0 else None,
        "oz_recoveries": ozrt,
        "dz_recoveries_gear": dzrt,
        "loose_puck_recoveries": lpr,
        "takeaways_oz_gear": ta_oz,
        "failed_attacks_per_game": round(fa / gp, 2) if fa is not None and gp > 0 else None,
        "passes_to_slot": ptts,
        "passes_to_slot_per_game": round(ptts / gp, 2) if ptts is not None and gp > 0 else None,
        "successful_entries_instat_tagged": ens,
        "successful_entries_instat_tagged_per_game": (
            round(ens / gp, 2) if ens is not None and gp > 0 else None
        ),
        "gear1_available": GEAR1_NOW_AVAILABLE,
        "unavailable": {
            k: {"value": None, "reason": v}
            for k, v in {
                **UNAVAILABLE_ACTION_PBP,
                "oz_recovery_to_sc_proxy": "not_published_misleading_standin_for_fc_to_shot",
                "forecheck_recoveries_proxy": "not_published_no_ozrt_fallback",
            }.items()
        },
    }
    return strip_proxy_standins(derived)


def _per60(count: float, toi_s: float) -> Optional[float]:
    if toi_s <= 0:
        return None
    return round(count * 3600.0 / toi_s, 2)


def combine() -> Path:
    ensure_dirs()
    teams_path = CURATED / "teams" / "nhl_pbp_microstats.json"
    skaters_path = CURATED / "skaters_season.json"
    instat_path = CURATED / "skaters" / "instat_season_flat.json"
    on_ice_path = CURATED / "skaters" / "on_ice_microstats.json"

    teams_payload = json.loads(teams_path.read_text()) if teams_path.exists() else {}
    skaters_payload = json.loads(skaters_path.read_text()) if skaters_path.exists() else {}
    instat_payload = json.loads(instat_path.read_text()) if instat_path.exists() else {}
    on_ice_payload = json.loads(on_ice_path.read_text()) if on_ice_path.exists() else {}

    toi_map = fetch_club_toi()

    # ── Teams: attach share baselines + v4 rates already present
    teams_out: Dict[str, Any] = {}
    team_rows = teams_payload.get("teams") or {}
    # league totals for share
    league_entries = sum(int(t.get("entries_total") or 0) for t in team_rows.values())
    for abbr, t in team_rows.items():
        rates = dict(t.get("rates") or {})
        g = max(1, int(t.get("games") or 0))
        entries = int(t.get("entries_total") or 0)
        rates["share_of_league_entries_pct"] = (
            round(100.0 * entries / league_entries, 2) if league_entries else None
        )
        # per-60 team approx using 60*g minutes of team ice (5 skaters × 60 ≈ 300 min/game)
        # Honest team per-60: events per 60 team-minutes = events / (g * 60) * 60 = per game.
        # Use per-60-of-5v5-skater-ice ≈ count / (g * 5) for rough skater-equivalent.
        rates["entries_per_60_team_ice"] = round(entries / g, 2)  # = per game; labeled
        rates["entries_per_60_team_ice_note"] = "equals_per_game_for_team_grain"
        teams_out[abbr] = {
            **{k: v for k, v in t.items() if k != "rates"},
            "rates": rates,
            "grain": "team",
            "sources": ["nhl_pbp"],
        }

    # ── Skaters: PBP + TOI per-60 + share of team
    skaters_raw = skaters_payload.get("skaters") or {}
    # team entry totals from skater sums
    team_entry_sum: Dict[str, int] = {}
    for s in skaters_raw.values():
        tm = s.get("team") or ""
        team_entry_sum[tm] = team_entry_sum.get(tm, 0) + int(s.get("entries") or 0)

    instat_by_name: Dict[str, dict] = {}
    for r in instat_payload.get("skaters") or []:
        name = (r.get("Player") or "").strip().lower()
        if name:
            instat_by_name[name] = r

    on_ice_by_id = {
        str(k): v for k, v in (on_ice_payload.get("skaters") or {}).items()
    }

    skaters_out: Dict[str, Any] = {}
    for pid, s in skaters_raw.items():
        rates = dict(s.get("rates") or {})
        toi_info = toi_map.get(int(pid)) if str(pid).isdigit() else None
        toi_s = float((toi_info or {}).get("toi_seconds_est") or 0.0)
        gp = max(1, int(s.get("games") or 0))
        if toi_info:
            rates["toi_seconds_est"] = toi_s
            rates["avg_toi_per_game_s"] = toi_info.get("avg_toi_per_game_s")
            rates["toi_source"] = "nhl_club_stats"
            for metric, key in (
                ("entries_per_60", "entries"),
                ("dump_ins_per_60", "dump_ins"),
                ("controlled_entries_per_60", "controlled_entries"),
                ("forecheck_recoveries_per_60", "forecheck_recoveries"),
                ("scoring_chances_per_60", "scoring_chances"),
                ("failed_entries_per_60", "failed_entries"),
                ("slot_drives_per_60", "slot_drives"),
                ("dz_recoveries_per_60", "dz_recoveries"),
            ):
                rates[metric] = _per60(float(s.get(key) or 0), toi_s)
        else:
            rates["toi_seconds_est"] = None
            rates["toi_source"] = "missing_club_stats"
            rates["per_60_note"] = "skipped_without_toi"

        tm = s.get("team") or ""
        te = team_entry_sum.get(tm) or 0
        rates["share_of_team_entries_pct"] = (
            round(100.0 * int(s.get("entries") or 0) / te, 1) if te else None
        )

        name = (s.get("name") or "").strip()
        inst = instat_by_name.get(name.lower())
        instat_block = instat_derived(inst) if inst else {
            "source": None,
            "note": "no_instat_name_match",
            "unavailable": {
                k: {"value": None, "reason": v} for k, v in UNAVAILABLE_ACTION_PBP.items()
            },
        }

        on_ice = on_ice_by_id.get(str(pid)) or on_ice_by_id.get(pid) or None

        skaters_out[str(pid)] = {
            **{k: v for k, v in s.items() if k != "rates"},
            "rates": rates,
            "instat": instat_block,
            "on_ice": on_ice,
            "sources": ["nhl_pbp"]
            + (["nhl_club_stats"] if toi_info else [])
            + (["instat_gear1"] if inst else [])
            + (["nhl_shiftcharts"] if on_ice else []),
        }

    # Shrink noisy % rates toward league prior; null rank_pct below denom floors.
    from sample_stability import attach_skater_stability, compute_priors_from_skaters

    priors = compute_priors_from_skaters(list(skaters_out.values()))
    skaters_out = {
        pid: attach_skater_stability(row, priors=priors)
        for pid, row in skaters_out.items()
    }

    payload = {
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "schema_version": 4,
        "season": "20262027",
        "season_label": "2026-27",
        "game_type": "2",
        "real_data_only": True,
        "honesty": {
            "real_data_only": True,
            "pbp": "NHL gamecenter event sequences (current RS finals only)",
            "instat_gear": "gear-1 columns only; carry_in_pct from EN/ENP/END when END present",
            "unavailable_without_action_pbp": list(UNAVAILABLE_ACTION_PBP.keys()),
            "gear1_now_available": GEAR1_NOW_AVAILABLE,
            "sample_stability": {
                "method": "empirical_bayes_shrinkage + wilson + min_attempts",
                "priors": {k: round(100.0 * v, 1) for k, v in priors.items()},
                "note": "raw_pct kept; rank_pct/regressed null or shrunk when n low",
            },
            "no_imputation": True,
            "no_proxy_standins": True,
            "no_sample_data": True,
        },
        "teams": teams_out,
        "team_count": len(teams_out),
        "skaters": skaters_out,
        "skater_count": len(skaters_out),
        "toi_players": len(toi_map),
        "instat_matched": sum(1 for s in skaters_out.values() if s.get("instat", {}).get("source")),
    }
    out = CURATED / "combined_microstats.json"
    out.write_text(json.dumps(payload, indent=2))
    print(
        f"🔗 combined: {payload['team_count']} teams, {payload['skater_count']} skaters, "
        f"toi={payload['toi_players']}, instat_matched={payload['instat_matched']} → {out}"
    )
    return out


def top5_report() -> str:
    path = CURATED / "combined_microstats.json"
    if not path.exists():
        combine()
    data = json.loads(path.read_text())
    teams = list((data.get("teams") or {}).values())
    skaters = list((data.get("skaters") or {}).values())

    lines: List[str] = []
    lines.append("# Microstats Top 5 (schema v4, no imputed nulls)\n")
    lines.append(
        f"Teams={data.get('team_count')} Skaters={data.get('skater_count')} "
        f"InStat matched={data.get('instat_matched')} "
        f"Unavailable (null): {', '.join(UNAVAILABLE_ACTION_PBP)}\n"
    )

    MIN_GP = 3  # equalize schedule; drop 1–2 gp noise

    def _rank_team(
        metric: str,
        label: str,
        min_games: int = MIN_GP,
        *,
        min_support: Optional[Tuple[str, int]] = None,
        min_support_per_game: Optional[Tuple[str, float]] = None,
    ):
        rows = []
        for t in teams:
            g = int(t.get("games") or 0)
            if g < min_games:
                continue
            if min_support:
                key, need = min_support
                if int(t.get(key) or 0) < need:
                    continue
            if min_support_per_game:
                key, need_pg = min_support_per_game
                if (int(t.get(key) or 0) / g) < need_pg:
                    continue
            r = (t.get("rates") or {}).get(metric)
            if r is None:
                continue
            rows.append((float(r), t.get("team") or "?", g))
        rows.sort(key=lambda x: -x[0])
        lines.append(f"## TEAM · {label} (`{metric}`)")
        if not rows:
            lines.append("_no data (min sample not met)_\n")
            return
        for i, (val, abbr, g) in enumerate(rows[:5], 1):
            lines.append(f"{i}. **{abbr}** — {val}  ({g} gp)")
        lines.append("")

    def _rank_skater(
        path_keys: Tuple[str, ...],
        label: str,
        min_games: int = MIN_GP,
        min_toi_s: float = 60 * 60,  # ~60 min season TOI in sample
        *,
        min_support: Optional[Tuple[str, int]] = None,
        require_toi: bool = True,
    ):
        rows = []
        for s in skaters:
            g = int(s.get("games") or 0)
            if g < min_games:
                continue
            if int(s.get("entries") or 0) == 0 and int(s.get("shots") or 0) == 0 and int(s.get("hits") or 0) == 0:
                continue
            if min_support:
                key, need = min_support
                if int(s.get(key) or 0) < need:
                    continue
            cur: Any = s
            for k in path_keys:
                cur = (cur or {}).get(k) if isinstance(cur, dict) else None
            if cur is None:
                continue
            toi = float(((s.get("rates") or {}).get("toi_seconds_est")) or 0)
            if require_toi and toi < min_toi_s:
                continue
            rows.append((float(cur), s.get("name") or "?", s.get("team") or "?", g))
        rows.sort(key=lambda x: -x[0])
        lines.append(f"## SKATER · {label} (`{'.'.join(path_keys)}`)")
        if not rows:
            lines.append("_no data / unavailable_\n")
            return
        for i, (val, name, tm, g) in enumerate(rows[:5], 1):
            lines.append(f"{i}. **{name}** ({tm}) — {val}  ({g} gp)")
        lines.append("")

    # Team specs: support = DENOMINATOR attempts (never numerator).
    # Prefer /game rates for volumes; % rates need min attempts + min GP.
    team_specs = [
        ("dump_in_recovery_pct", "Dump-in recovery %", ("dump_ins", 20)),
        ("dump_ins_recovered_per_game", "Dump recoveries / game", ("dump_ins", 15)),
        ("exit_to_entry_chain_pct", "Exit→entry chain %", ("controlled_exits_chain_eligible", 25)),
        ("nz_advance_pct", "NZ advance %", ("nz_plays", 25)),
        ("nz_plays_per_game", "NZ plays / game", ("nz_plays", 15)),
        ("cycle_shots_per_game", "Cycle shots / game", ("cycle_shots", 4)),
        ("rebound_second_chance_pct", "Rebound second-chance %", ("rebound_shot_opportunities", 50)),
        ("behind_net_to_slot_pct", "Behind-net → slot %", ("behind_net_touches", 20)),
        # ONE retrieval % (aliases share formula); floor on all DZ takeaways
        ("dz_retrieval_to_controlled_exit_pct", "DZ retrieval → controlled exit %", ("dz_recoveries", 6)),
        ("dz_controlled_exit_from_retrieval_per_game", "DZ ctrl-exit from retrieval / game", ("dz_recoveries", 6)),
        ("failed_entry_pct", "Failed entry % (higher = worse)", ("entries_total", 50)),
        ("failed_exit_pct", "Failed exit %", ("exits_total", 50)),
        ("forecheck_pressure_index", "Forecheck pressure index", None),
        ("forecheck_recoveries_per_game", "Forecheck recoveries / game", None),
        ("slot_drive_to_shot_pct", "Slot-drive → shot %", ("slot_drives", 10)),
        ("slot_drives_per_game", "Slot drives / game", ("slot_drives", 8)),
        ("sc_off_dump_per_game", "SC off dump / game", ("dump_ins", 15)),
        ("sc_off_carry_per_game", "SC off carry / game", ("controlled_entries", 25)),
        ("zone_to_shot_against_pct_dz", "DZ TO → shot against %", ("zone_to_dz", 20)),
        ("ev5v5_controlled_entry_pct", "5v5 controlled entry %", ("ev5v5_entries", 50)),
        ("controlled_entry_pct", "Controlled entry % (NHL PBP)", ("entries_total", 50)),
        ("entries_per_game", "Entries / game", ("entries_total", 40)),
    ]
    for metric, label, support in team_specs:
        _rank_team(metric, label, min_support=support)

    # Dump recovery by landing — one section with best corner recovery teams
    lines.append("## TEAM · Dump recovery % by landing (top team per bin)")
    bins = ["strong_corner", "weak_corner", "strong_rim", "weak_rim", "deep_slot", "short_nz"]
    for b in bins:
        best = []
        for t in teams:
            if int(t.get("games") or 0) < 2:
                continue
            mix = (t.get("rates") or {}).get("dump_recovery_pct_by_landing") or {}
            v = mix.get(b)
            if v is None:
                continue
            # require attempts
            if int(t.get(f"dump_att_{b}") or 0) < 3:
                continue
            best.append((float(v), t.get("team"), int(t.get(f"dump_att_{b}") or 0)))
        best.sort(key=lambda x: -x[0])
        if best:
            val, abbr, att = best[0]
            lines.append(f"- **{b}**: {abbr} {val}% (n={att})")
        else:
            lines.append(f"- **{b}**: _insufficient attempts_")
    lines.append("")

    # Skater: use *_rank (regressed, null if below floor) for noisy %.
    skater_specs = [
        (("rates", "dump_in_recovery_pct_rank"), "Dump-in recovery % (regressed, n≥12)", ("dump_ins", 12)),
        (("rates", "controlled_entry_pct_rank"), "Controlled entry % (regressed, n≥25)", ("entries", 25)),
        (("rates", "entries_per_60"), "Entries / 60", ("entries", 15)),
        (("rates", "dump_ins_per_60"), "Dump-ins / 60", ("dump_ins", 10)),
        (("rates", "forecheck_recoveries_per_60"), "Forecheck recoveries / 60", ("forecheck_recoveries", 5)),
        (("rates", "scoring_chances_per_60"), "SC / 60", ("scoring_chances", 8)),
        (("rates", "failed_entry_pct_rank"), "Failed entry % (regressed, n≥25)", ("entries", 25)),
        (("rates", "slot_drive_to_shot_pct_rank"), "Slot-drive → shot % (regressed, n≥10)", ("slot_drives", 10)),
        (("rates", "dz_retrieval_to_controlled_exit_pct_rank"), "DZ → controlled exit % (regressed, n≥8)", ("dz_recoveries", 8)),
        (("rates", "share_of_team_entries_pct"), "Share of team entries %", ("entries", 20)),
        (("instat", "carry_in_pct"), "InStat carry-in % (EN+ENP)/(EN+ENP+END)", ("entries", 15)),
        (("instat", "passes_to_slot_per_game"), "InStat passes to slot / GP (PTTS)", None),
        (("instat", "successful_entries_instat_tagged_per_game"), "InStat successful entries / GP (ENS)", None),
        (("instat", "battles_engaged_per_game"), "InStat battles engaged / GP", None),
        (("instat", "failed_attacks_per_game"), "InStat failed attacks / GP", None),
        (("on_ice", "rates", "on_ice_sc_diff_per_game"), "On-ice SC diff / game", None),
    ]
    for keys, label, support in skater_specs:
        _rank_skater(keys, label, min_support=support)

    lines.append("## Explicitly unavailable (null — not faked)")
    for k, reason in UNAVAILABLE_ACTION_PBP.items():
        lines.append(f"- `{k}`: {reason}")
    lines.append("")

    # Matrix: metrics as rows, rank columns as teams
    lines.append("## Matrix (teams in columns)")
    lines.append("")
    lines.append("| Metric | 1st | 2nd | 3rd | 4th | 5th |")
    lines.append("|---|---|---|---|---|---|")

    def _top5_cells(metric: str, min_support: Optional[Tuple[str, int]] = None) -> str:
        rows = []
        for t in teams:
            g = int(t.get("games") or 0)
            if g < MIN_GP:
                continue
            if min_support:
                key, need = min_support
                if int(t.get(key) or 0) < need:
                    continue
            r = (t.get("rates") or {}).get(metric)
            if r is None:
                continue
            rows.append((float(r), t.get("team") or "?", g))
        rows.sort(key=lambda x: -x[0])
        cells = []
        for i in range(5):
            if i < len(rows):
                cells.append(f"{rows[i][1]} {rows[i][0]} ({rows[i][2]}gp)")
            else:
                cells.append("—")
        return " | ".join(cells)

    for metric, label, support in team_specs:
        lines.append(f"| {label} | {_top5_cells(metric, support)} |")

    text = "\n".join(lines)
    out = CURATED / "microstats_top5.md"
    out.write_text(text)
    print(f"📊 wrote {out}")
    return text


if __name__ == "__main__":
    import sys

    if "--top5" in sys.argv:
        print(top5_report())
    else:
        combine()
        print(top5_report())
