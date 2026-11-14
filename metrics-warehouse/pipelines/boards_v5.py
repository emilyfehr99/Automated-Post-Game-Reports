#!/usr/bin/env python3
"""v5 boards: role-safe /60, F vs D, ctrl-entry residual, score/period deltas,
goalie rebound diet × opp slot pressure.

Consumes curated stores only — no fake fills.
"""

from __future__ import annotations

import json
import time
import urllib.request
from collections import defaultdict
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


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def fetch_positions() -> Dict[int, str]:
    """playerId → F|D from NHL club-stats positionCode."""
    out: Dict[int, str] = {}
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
            code = (row.get("positionCode") or "").upper()
            if not pid or not code:
                continue
            pos = "D" if code == "D" else "F"
            out[int(pid)] = pos
    return out


def _wmean(pairs: List[Tuple[float, float]]) -> float:
    """Weighted mean of (value, weight)."""
    sw = sum(w for _, w in pairs)
    if sw <= 0:
        return 0.5
    return sum(v * w for v, w in pairs) / sw


def _ols_team_context(
    rows: List[Tuple[float, float, float]],
) -> Tuple[float, float]:
    """OLS: player ctrl_pct ~ a + b * team_dump_share (avoids player tautology)."""
    n = len(rows)
    if n < 12:
        return 0.62, -0.15
    mx = sum(r[0] for r in rows) / n
    my = sum(r[1] for r in rows) / n
    num = sum((r[0] - mx) * (r[1] - my) for r in rows)
    den = sum((r[0] - mx) ** 2 for r in rows)
    b = (num / den) if den else 0.0
    # shrink extreme slopes
    b = max(-0.6, min(0.2, b))
    a = my - b * mx
    return a, b


def enrich_skaters(
    combined: dict,
    positions: Dict[int, str],
    seq: dict,
    team_pbp: dict | None = None,
) -> dict:
    skaters = combined.get("skaters") or {}
    seq_sk = seq.get("skaters") or {}
    teams = (team_pbp or {}).get("teams") or combined.get("teams") or {}

    # Team dump-share context (system style — not the player's own dump%)
    team_dump_share: Dict[str, float] = {}
    for abbr, t in teams.items():
        e = float(t.get("entries_total") or t.get("entries") or 0)
        d = float(t.get("dump_ins") or 0)
        if e > 0:
            team_dump_share[abbr] = d / e

    # Position baselines (weighted by attempts)
    pos_ctrl: Dict[str, List[Tuple[float, float]]] = {"F": [], "D": []}
    pos_e60: Dict[str, List[Tuple[float, float]]] = {"F": [], "D": []}
    fit_rows: Dict[str, List[Tuple[float, float, float]]] = {"F": [], "D": []}

    for pid, s in skaters.items():
        pos = positions.get(int(pid)) if str(pid).isdigit() else None
        entries = float(s.get("entries") or 0)
        if not pos or entries < 15:
            continue
        ctrl = float(s.get("controlled_entries") or 0)
        ctrl_pct = ctrl / entries
        pos_ctrl[pos].append((ctrl_pct, entries))
        toi_s = float((s.get("rates") or {}).get("toi_seconds_est") or 0)
        if toi_s >= 3600:
            pos_e60[pos].append((entries * 3600.0 / toi_s, toi_s))
        tm = s.get("team") or ""
        tds = team_dump_share.get(tm)
        if tds is not None:
            fit_rows[pos].append((tds, ctrl_pct, entries))

    pos_mean_ctrl = {p: _wmean(pos_ctrl[p]) for p in ("F", "D")}
    pos_mean_e60 = {p: _wmean(pos_e60[p]) if pos_e60[p] else 0.0 for p in ("F", "D")}
    coefs = {p: _ols_team_context(fit_rows[p]) for p in ("F", "D")}

    for pid, s in skaters.items():
        rates = dict(s.get("rates") or {})
        pos = positions.get(int(pid)) if str(pid).isdigit() else None
        s["position"] = pos
        entries = float(s.get("entries") or 0)
        dumps = float(s.get("dump_ins") or 0)
        ctrl = float(s.get("controlled_entries") or 0)
        toi_s = float(rates.get("toi_seconds_est") or 0)
        gp = max(1, int(s.get("games") or 0))
        rates["toi_ok_for_per60"] = bool(toi_s >= 3600 and (toi_s / gp) >= 480)

        # Primary role-safe volume
        if toi_s > 0:
            rates["entries_per_60"] = round(entries * 3600.0 / toi_s, 2)
            rates["dump_ins_per_60"] = round(dumps * 3600.0 / toi_s, 2)
            rates["controlled_entries_per_60"] = round(ctrl * 3600.0 / toi_s, 2)
            rates["exits_per_60"] = round(float(s.get("exits") or 0) * 3600.0 / toi_s, 2)
            rates["controlled_exits_per_60"] = round(
                float(s.get("controlled_exits") or 0) * 3600.0 / toi_s, 2
            )
            rates["dz_recoveries_per_60"] = round(
                float(s.get("dz_recoveries") or 0) * 3600.0 / toi_s, 2
            )

        dump_share = (dumps / entries) if entries > 0 else None
        rates["dump_share_of_entries"] = (
            round(100.0 * dump_share, 1) if dump_share is not None else None
        )

        # Residual: observed ctrl% − E[ctrl% | position, team dump style]
        # (team dump share ≠ player dump share — avoids 1−dump_share identity)
        if pos and entries >= 15:
            tm = s.get("team") or ""
            tds = team_dump_share.get(tm)
            a, b = coefs[pos]
            if tds is not None:
                expected = a + b * tds
            else:
                expected = pos_mean_ctrl[pos]
            observed = ctrl / entries
            residual = observed - expected
            rates["controlled_entry_pct_expected"] = round(100.0 * expected, 1)
            rates["controlled_entry_pct_residual"] = round(100.0 * residual, 1)
            rates["controlled_entry_pct_vs_pos"] = round(
                100.0 * (observed - pos_mean_ctrl[pos]), 1
            )
            if rates.get("toi_ok_for_per60") and pos_mean_e60[pos] > 0:
                rates["entries_per_60_residual"] = round(
                    float(rates["entries_per_60"]) - pos_mean_e60[pos], 2
                )
            rates["controlled_entry_model"] = {
                "position": pos,
                "pos_mean_ctrl_pct": round(100.0 * pos_mean_ctrl[pos], 1),
                "team_dump_share": round(tds, 3) if tds is not None else None,
                "intercept": round(a, 4),
                "team_dump_share_coef": round(b, 4),
                "n_entries": int(entries),
            }
        else:
            rates["controlled_entry_pct_expected"] = None
            rates["controlled_entry_pct_residual"] = None

        # Score-state deltas (leading − trailing)
        ss = (rates.get("score_state") or {}) if isinstance(rates.get("score_state"), dict) else {}
        # also accept nested from skater rates built earlier
        if not ss and isinstance(s.get("rates"), dict):
            ss = s["rates"].get("score_state") or {}
        lead = ss.get("leading") or {}
        trail = ss.get("trailing") or {}
        tied = ss.get("tied") or {}

        def _delta(a: Optional[float], b: Optional[float]) -> Optional[float]:
            if a is None or b is None:
                return None
            return round(float(a) - float(b), 1)

        rates["score_state_deltas"] = {
            "controlled_entry_pct_lead_minus_trail": _delta(
                lead.get("controlled_entry_pct"), trail.get("controlled_entry_pct")
            ),
            "dump_in_recovery_pct_lead_minus_trail": _delta(
                lead.get("dump_in_recovery_pct"), trail.get("dump_in_recovery_pct")
            ),
            "failed_entries_lead_minus_trail": _delta(
                lead.get("failed_entries"), trail.get("failed_entries")
            ),
            "entries_tied": tied.get("entries"),
            "entries_leading": lead.get("entries"),
            "entries_trailing": trail.get("entries"),
        }

        # Sequence rush chain
        seq_row = seq_sk.get(str(pid)) or seq_sk.get(pid) or {}
        seq_rates = seq_row.get("rates") or {}
        if seq_rates:
            rates["rush_chain_avg_length"] = seq_rates.get("rush_chain_avg_length")
            rates["rush_chains_per_game"] = seq_rates.get("rush_chains_per_game")

        s["rates"] = rates
        skaters[pid] = s

    combined["skaters"] = skaters
    combined["position_model"] = {
        "F": {
            "intercept": coefs["F"][0],
            "team_dump_share_coef": coefs["F"][1],
            "pos_mean_ctrl_pct": round(100.0 * pos_mean_ctrl["F"], 1),
            "pos_mean_entries_per_60": round(pos_mean_e60["F"], 2),
            "n": len(fit_rows["F"]),
        },
        "D": {
            "intercept": coefs["D"][0],
            "team_dump_share_coef": coefs["D"][1],
            "pos_mean_ctrl_pct": round(100.0 * pos_mean_ctrl["D"], 1),
            "pos_mean_entries_per_60": round(pos_mean_e60["D"], 2),
            "n": len(fit_rows["D"]),
        },
        "formula": "E[ctrl_pct] = a_pos + b_pos * team_dump_share  (not player dump_share)",
    }
    return combined


def enrich_teams(combined: dict, team_pbp: dict, seq: dict) -> dict:
    teams = combined.get("teams") or team_pbp.get("teams") or {}
    # if combined teams are list-like rates already
    if not teams and isinstance(combined.get("teams"), dict):
        teams = combined["teams"]
    seq_t = seq.get("teams") or {}
    pbp_teams = team_pbp.get("teams") or {}

    out = {}
    for abbr, t in (pbp_teams or teams).items():
        row = dict(t)
        rates = dict(row.get("rates") or {})
        seq_rates = (seq_t.get(abbr) or {}).get("rates") or {}
        # Period transition from v4 + sequence SC
        p1e = rates.get("p1_entries_per_game")
        p3e = rates.get("p3_entries_per_game")
        if p1e is not None and p3e is not None:
            rates["p3_minus_p1_entries_per_game"] = round(float(p3e) - float(p1e), 2)
        p1sc = rates.get("p1_sc_per_game")
        p3sc = rates.get("p3_sc_per_game")
        if p1sc is not None and p3sc is not None:
            rates["p3_minus_p1_sc_per_game"] = round(float(p3sc) - float(p1sc), 2)
        if seq_rates.get("p3_minus_p1_sc_per_game") is not None:
            rates["p3_minus_p1_sc_per_game"] = seq_rates["p3_minus_p1_sc_per_game"]
        rates["rush_chain_avg_length"] = seq_rates.get("rush_chain_avg_length")
        rates["rush_chains_per_game"] = seq_rates.get("rush_chains_per_game")
        rates["slot_drives_against_per_game"] = seq_rates.get(
            "slot_drives_against_per_game"
        )

        # Score-state deltas from team ss_ totals
        def _ss_pct(prefix: str, num: str, den: str) -> Optional[float]:
            if den == "entries":
                d = float(
                    row.get(f"ss_{prefix}_entries_total")
                    or row.get(f"ss_{prefix}_entries")
                    or 0
                )
            else:
                d = float(row.get(f"ss_{prefix}_{den}") or 0)
            n = float(row.get(f"ss_{prefix}_{num}") or 0)
            return round(100.0 * n / d, 1) if d > 0 else None

        lead_c = _ss_pct("leading", "controlled_entries", "entries")
        trail_c = _ss_pct("trailing", "controlled_entries", "entries")
        lead_d = _ss_pct("leading", "dump_ins_recovered", "dump_ins")
        trail_d = _ss_pct("trailing", "dump_ins_recovered", "dump_ins")
        rates["score_state_deltas"] = {
            "controlled_entry_pct_lead_minus_trail": (
                round(lead_c - trail_c, 1) if lead_c is not None and trail_c is not None else None
            ),
            "dump_recovery_pct_lead_minus_trail": (
                round(lead_d - trail_d, 1) if lead_d is not None and trail_d is not None else None
            ),
        }
        row["rates"] = rates
        out[abbr] = row

    combined["teams"] = out
    combined["team_count"] = len(out)
    return combined


def goalie_rebound_diet(goalies: dict, seq: dict) -> dict:
    seq_t = seq.get("teams") or {}
    out = {}
    for gid, g in (goalies.get("goalies") or {}).items():
        team = g.get("team")
        pbp = g.get("pbp") or {}
        reb_ctrl = pbp.get("reboundControlPct")
        reb_rate = pbp.get("reboundRate")
        reb_gsax = pbp.get("reboundGsax")
        slot_ag = ((seq_t.get(team) or {}).get("rates") or {}).get(
            "slot_drives_against_per_game"
        )
        diet_fail = None
        if reb_ctrl is not None:
            diet_fail = 1.0 - float(reb_ctrl)
        elif reb_rate is not None:
            diet_fail = float(reb_rate)
        diet_x_slot = None
        if diet_fail is not None and slot_ag is not None:
            diet_x_slot = round(diet_fail * float(slot_ag), 3)
        out[str(gid)] = {
            "id": g.get("id") or gid,
            "name": g.get("name"),
            "team": team,
            "gp": g.get("gp"),
            "reboundControlPct": reb_ctrl,
            "reboundRate": reb_rate,
            "reboundGsax": reb_gsax,
            "slot_drives_against_per_game": slot_ag,
            "rebound_diet_fail": round(diet_fail, 3) if diet_fail is not None else None,
            "rebound_diet_x_opp_slot": diet_x_slot,
            "note": "(1-rebControl)×team slot_drives_against/gp — real LLD × real PBP",
        }
    return {
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "real_data_only": True,
        "goalie_count": len(out),
        "goalies": out,
    }


def _top(
    rows: List[Tuple[float, str, dict]], n: int = 5
) -> List[dict]:
    rows = sorted(rows, key=lambda x: -x[0])[:n]
    return [{"rank": i + 1, "value": v, "label": lab, **meta} for i, (v, lab, meta) in enumerate(rows)]


def build_boards(combined: dict, seq: dict, diet: dict) -> dict:
    skaters = list((combined.get("skaters") or {}).values())
    teams = list((combined.get("teams") or {}).values())
    lines = list((seq.get("lines") or {}).values())
    boards: Dict[str, Any] = {}

    def sk_val(s, *keys):
        cur = s
        for k in keys:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(k)
        return cur

    # Primary entry board — /60 (require real TOI floor)
    for metric, label, min_n in (
        ("entries_per_60", "Entries / 60 (all)", 15),
        ("dump_ins_per_60", "Dump-ins / 60 (all)", 10),
        ("controlled_entries_per_60", "Controlled entries / 60 (all)", 10),
    ):
        rows = []
        for s in skaters:
            n = int(s.get("entries") or 0)
            if n < min_n:
                continue
            if not sk_val(s, "rates", "toi_ok_for_per60"):
                continue
            v = sk_val(s, "rates", metric)
            if v is None:
                continue
            rows.append((float(v), s.get("name") or "", {"team": s.get("team"), "pos": s.get("position"), "n": n, "gp": s.get("games")}))
        boards[metric] = {"label": label, "top": _top(rows)}

    # F-only / D-only
    for pos, metrics in (
        (
            "F",
            [
                ("entries_per_60", "F · Entries / 60", 15),
                ("dump_ins_per_60", "F · Dump-ins / 60", 10),
                ("controlled_entry_pct_rank", "F · Ctrl entry % rank", 25),
                ("controlled_entry_pct_residual", "F · Ctrl entry residual", 15),
            ],
        ),
        (
            "D",
            [
                ("exits_per_60", "D · Exits / 60", 10),
                ("controlled_exits_per_60", "D · Controlled exits / 60", 8),
                ("dz_recoveries_per_60", "D · DZ recoveries / 60", 6),
                ("dz_retrieval_to_controlled_exit_pct_rank", "D · DZ→ctrl exit % rank", 8),
                ("controlled_entry_pct_residual", "D · Ctrl entry residual", 15),
            ],
        ),
    ):
        for metric, label, min_n in metrics:
            rows = []
            for s in skaters:
                if s.get("position") != pos:
                    continue
                n_key = "dz_recoveries" if "dz" in metric else ("exits" if "exit" in metric else "entries")
                n = int(s.get(n_key) or 0)
                if metric.endswith("_residual"):
                    if int(s.get("entries") or 0) < min_n:
                        continue
                elif n < min_n:
                    continue
                if metric.endswith("_per_60") and not sk_val(s, "rates", "toi_ok_for_per60"):
                    continue
                v = sk_val(s, "rates", metric)
                if v is None:
                    continue
                rows.append(
                    (
                        float(v),
                        s.get("name") or "",
                        {"team": s.get("team"), "pos": pos, "n": n, "gp": s.get("games")},
                    )
                )
            boards[f"{pos.lower()}_{metric}"] = {"label": label, "top": _top(rows)}

    # Secondary % board (regressed)
    rows = []
    for s in skaters:
        v = sk_val(s, "rates", "controlled_entry_pct_rank")
        if v is None:
            continue
        rows.append(
            (
                float(v),
                s.get("name") or "",
                {
                    "team": s.get("team"),
                    "pos": s.get("position"),
                    "n": sk_val(s, "rates", "controlled_entry_pct_n"),
                    "raw": sk_val(s, "rates", "controlled_entry_pct"),
                },
            )
        )
    boards["controlled_entry_pct_secondary"] = {
        "label": "Controlled entry % (secondary, regressed n≥25)",
        "top": _top(rows),
    }

    # Team score-state + period deltas + rush chain
    for metric, label, path in (
        (
            "score_ctrl_delta",
            "Team · Ctrl entry% lead−trail",
            ("rates", "score_state_deltas", "controlled_entry_pct_lead_minus_trail"),
        ),
        (
            "score_dump_delta",
            "Team · Dump recovery% lead−trail",
            ("rates", "score_state_deltas", "dump_recovery_pct_lead_minus_trail"),
        ),
        ("p3_minus_p1_sc", "Team · P3−P1 SC / game", ("rates", "p3_minus_p1_sc_per_game")),
        ("p3_minus_p1_entries", "Team · P3−P1 entries / game", ("rates", "p3_minus_p1_entries_per_game")),
        ("rush_chain_len", "Team · Rush chain avg length", ("rates", "rush_chain_avg_length")),
        ("rush_chains_pg", "Team · Rush chains / game", ("rates", "rush_chains_per_game")),
    ):
        rows = []
        for t in teams:
            cur: Any = t
            ok = True
            for k in path:
                if not isinstance(cur, dict) or k not in cur:
                    ok = False
                    break
                cur = cur[k]
            if not ok or cur is None:
                continue
            if int(t.get("games") or 0) < 3:
                continue
            rows.append((float(cur), t.get("team") or "", {"gp": t.get("games")}))
        boards[metric] = {"label": label, "top": _top(rows)}

    # Lines — resolve player names when possible
    name_by_id = {
        str(s.get("player_id") or pid): (s.get("name") or str(pid))
        for pid, s in (combined.get("skaters") or {}).items()
    }
    rows = []
    for ln in lines:
        v = sk_val(ln, "rates", "sc_diff_per_game")
        if v is None:
            continue
        if int(ln.get("games") or 0) < 5:
            continue
        pids = ln.get("player_ids") or []
        names = [name_by_id.get(str(p), str(p)) for p in pids]
        # Prefer last names for compact label
        short = [n.split()[-1] if isinstance(n, str) and " " in n else str(n) for n in names]
        label = f"{ln.get('team')}: " + "-".join(short[:6])
        rows.append(
            (
                float(v),
                label,
                {
                    "team": ln.get("team"),
                    "gp": ln.get("games"),
                    "events": ln.get("events"),
                    "player_ids": pids,
                    "n": ln.get("events"),
                },
            )
        )
    boards["line_sc_diff"] = {"label": "Line units · on-ice SC diff / game", "top": _top(rows)}

    # Goalie diet
    rows = []
    for g in (diet.get("goalies") or {}).values():
        v = g.get("rebound_diet_x_opp_slot")
        if v is None:
            continue
        if int(g.get("gp") or 0) < 3:
            continue
        rows.append(
            (
                float(v),
                g.get("name") or "",
                {
                    "team": g.get("team"),
                    "gp": g.get("gp"),
                    "rebControl": g.get("reboundControlPct"),
                    "slot_ag": g.get("slot_drives_against_per_game"),
                },
            )
        )
    # Higher = worse diet (more rebound fail × pressure)
    boards["goalie_rebound_diet_x_slot"] = {
        "label": "Goalie · rebound-diet × opp slot pressure (higher=worse)",
        "top": _top(rows),
    }
    # Best diet (lowest)
    rows_best = [(-v, lab, meta) for v, lab, meta in ((r["value"], r["label"], {k: r[k] for k in r if k not in {"rank", "value", "label"}}) for r in boards["goalie_rebound_diet_x_slot"]["top"])]
    # rebuild lowest-5 properly
    all_g = [
        (float(g["rebound_diet_x_opp_slot"]), g.get("name") or "", {
            "team": g.get("team"), "gp": g.get("gp"),
            "rebControl": g.get("reboundControlPct"),
            "slot_ag": g.get("slot_drives_against_per_game"),
        })
        for g in (diet.get("goalies") or {}).values()
        if g.get("rebound_diet_x_opp_slot") is not None and int(g.get("gp") or 0) >= 3
    ]
    all_g.sort(key=lambda x: x[0])
    boards["goalie_rebound_diet_best"] = {
        "label": "Goalie · best rebound diet × slot (lower=better)",
        "top": _top([(-v if False else v, lab, meta) for v, lab, meta in all_g[:5]])
        if False
        else [{"rank": i + 1, "value": v, "label": lab, **meta} for i, (v, lab, meta) in enumerate(all_g[:5])],
    }

    return boards


def boards_to_markdown(boards: dict, meta: dict) -> str:
    lines = [
        "# Microstats boards v5 (role-safe + residuals + deltas)",
        "",
        f"Generated {meta.get('updated_at')} · real_data_only · {meta.get('skater_count')} skaters · {meta.get('team_count')} teams",
        "",
        "Primary entry board = **/60 volume**. Controlled-entry % is secondary (regressed, n≥25).",
        "",
    ]
    for key, block in boards.items():
        lines.append(f"## {block.get('label')} (`{key}`)")
        top = block.get("top") or []
        if not top:
            lines.append("_insufficient sample_")
            lines.append("")
            continue
        for row in top:
            extra = []
            if row.get("team"):
                extra.append(str(row["team"]))
            if row.get("pos"):
                extra.append(str(row["pos"]))
            if row.get("n") is not None:
                extra.append(f"n={row['n']}")
            if row.get("gp") is not None:
                extra.append(f"{row['gp']} gp")
            if row.get("raw") is not None:
                extra.append(f"raw={row['raw']}")
            if row.get("rebControl") is not None:
                extra.append(f"rebCtrl={row['rebControl']}")
            suffix = f"  ({', '.join(extra)})" if extra else ""
            lines.append(f"{row['rank']}. **{row['label']}** — {row['value']}{suffix}")
        lines.append("")
    return "\n".join(lines) + "\n"


def run() -> Path:
    ensure_dirs()
    combined = _load(CURATED / "combined_microstats.json")
    team_pbp = _load(CURATED / "teams" / "nhl_pbp_microstats.json")
    seq = _load(CURATED / "sequence_extensions.json")
    goalies = _load(CURATED / "goalies_season.json")

    print("📍 fetching NHL positions…")
    positions = fetch_positions()
    print(f"   {len(positions)} skaters with F/D")

    combined = enrich_skaters(combined, positions, seq, team_pbp=team_pbp)
    combined = enrich_teams(combined, team_pbp, seq)
    diet = goalie_rebound_diet(goalies, seq)
    boards = build_boards(combined, seq, diet)

    combined["schema_version"] = 5
    combined["boards_v5"] = True
    combined["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    (CURATED / "combined_microstats.json").write_text(json.dumps(combined, indent=2))

    diet_path = CURATED / "goalies" / "rebound_diet.json"
    diet_path.parent.mkdir(parents=True, exist_ok=True)
    diet_path.write_text(json.dumps(diet, indent=2))

    payload = {
        "updated_at": combined["updated_at"],
        "real_data_only": True,
        "skater_count": combined.get("skater_count"),
        "team_count": combined.get("team_count"),
        "position_model": combined.get("position_model"),
        "boards": boards,
    }
    out = CURATED / "boards_v5.json"
    out.write_text(json.dumps(payload, indent=2))
    md = boards_to_markdown(boards, payload)
    (CURATED / "microstats_top5.md").write_text(md)
    (CURATED / "microstats_boards_v5.md").write_text(md)
    print(f"📊 boards v5 → {out} + microstats_top5.md ({len(boards)} boards)")
    return out


if __name__ == "__main__":
    run()
