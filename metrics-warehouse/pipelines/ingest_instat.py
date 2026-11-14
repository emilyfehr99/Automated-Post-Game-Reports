#!/usr/bin/env python3
"""InStat enrichment for the personal warehouse.

1. Always mirrors Last Line of Defense instat-aggs / shot pointers (works offline).
2. Live pull via InStatAPI.init_session (header cache or INSTAT_DEDICATED_ACCOUNT=1):
   - goalie season rows per NHL team (gear 9)
   - skater season rows per NHL team (gear 1)
3. Soft-fails with curated/status/instat.json — never blocks NHL PBP warehouse path.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from paths import CURATED, HUDL, LLD, RAW, SCRAPING, ensure_dirs, season_label

# auth_env.prepare_instat_auth() (called from daily_refresh) sets dedicated-account
# flags for CI. Only default to never-login when nothing opted in.
if (
    os.getenv("INSTAT_DEDICATED_ACCOUNT", "").strip() != "1"
    and os.getenv("ALLOW_INSTAT_LOGIN", "").strip() != "1"
    and not (os.getenv("INSTAT_X_AUTH_TOKEN", "").strip() and os.getenv("INSTAT_AUTHORIZATION", "").strip())
):
    os.environ.setdefault("INSTAT_NEVER_LOGIN", "1")


def _status(ok: bool, **kwargs: Any) -> Path:
    ensure_dirs()
    payload = {"updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "ok": ok, **kwargs}
    path = CURATED / "status" / "instat.json"
    path.write_text(json.dumps(payload, indent=2))
    return path


def _num(row: dict, *keys: str) -> Optional[float]:
    for k in keys:
        if k not in row or row[k] is None or row[k] == "":
            continue
        try:
            return float(row[k])
        except (TypeError, ValueError):
            continue
    return None


def enrich_instat_skater_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Wire human-readable aliases onto gear-1 cryptic columns.

    Gear abbreviations (NHL season table):
      EN / ENP / END ≈ stickhandle / pass / dump entry volume proxies
      DI / DO ≈ dump-ins / dump-outs
      TA / LPR / OZRT / DZRT ≈ takeaways / loose-puck / zone recoveries
      BRS ≈ battles engaged (volume; win% needs action PBP)
      H+ / H- ≈ hits for / against
      FA ≈ failed attacks / high-volume failed-play proxy
    """
    out = dict(row)
    en = _num(row, "EN", "EN (ES)")
    enp = _num(row, "ENP", "ENP (ES)")
    end = _num(row, "END", "END (ES)")
    di = _num(row, "DI", "DI (ES)")
    do = _num(row, "DO", "DO (ES)")
    ta = _num(row, "TA")
    ta_oz = _num(row, "TA (OZ)")
    ta_dz = _num(row, "TA (DZ)")
    lpr = _num(row, "LPR", "LPR (DZ)")
    ozrt = _num(row, "OZRT (OZ)", "OZRT")
    dzrt = _num(row, "DZRT (DZ)", "DZRT")
    brs = _num(row, "BRS", "BR", "BR (ES)")
    h_plus = _num(row, "H+", "H+ (ES)")
    h_minus = _num(row, "H-", "H- (ES)")
    fa = _num(row, "FA")

    # Aliases only — never substitute one gear column for another.
    out["entries_stickhandle"] = en
    out["entries_pass"] = enp
    out["entries_dump"] = end
    out["dump_ins"] = di
    out["dump_outs"] = do
    out["takeaways"] = ta
    out["takeaways_oz"] = ta_oz
    out["takeaways_dz"] = ta_dz
    out["loose_puck_recoveries"] = lpr
    out["oz_recoveries"] = ozrt
    out["dz_recoveries"] = dzrt
    out["battles_engaged"] = brs
    out["hits_for"] = h_plus
    out["hits_against"] = h_minus
    out["failed_attacks"] = fa

    # Gear-1 Slot Pass (param 271) — real volume, not action-PBP.
    ptts = _num(row, "PTTS", "Slot Pass", "Slot Passes")
    out["passes_to_slot"] = ptts
    out["passes_to_slot_source"] = "instat_gear1_PTTS" if ptts is not None else None

    # ENS (param 105, adjacent to END=104) — gear "successful entry" volume.
    # Distinct from raw EN/ENP/END; prior player_cards logic used action PBP for
    # the same concept — gear ENS is the season aggregate of that tag family.
    ens = _num(row, "ENS")
    out["successful_entries_instat_tagged"] = ens
    out["successful_entries_instat_tagged_source"] = (
        "instat_gear1_ENS" if ens is not None else None
    )

    # Carry-in % only when END is present (no DI stand-in).
    ctrl = (en or 0.0) + (enp or 0.0)
    if end is not None and (ctrl + end) > 0:
        out["carry_in_pct"] = round(100.0 * ctrl / (ctrl + end), 1)
        out["carry_in_pct_note"] = "EN+ENP over EN+ENP+END (gear-1 only)"
    else:
        out["carry_in_pct"] = None
        out["carry_in_pct_note"] = "null — END missing; will not substitute DI"

    # Battle win% not in gear-1 — stay null (no fake %).
    out["puck_battle_win_pct"] = None
    out["puck_battle_win_pct_note"] = (
        "null — gear-1 has BRS volume only; win% needs InStat action PBP"
    )
    cont = row.get("CONT")
    if isinstance(cont, str) and "/" in cont:
        try:
            w, a = cont.split("/", 1)
            w_f, a_f = float(w), float(a)
            if a_f > 0:
                out["cont_ratio_pct"] = round(100.0 * w_f / a_f, 1)
                out["cont_ratio_pct_note"] = "raw CONT gear string — not battle win%"
        except ValueError:
            pass

    # Real OZ takeaways only — do not fall back to OZRT under a forecheck name.
    out.pop("forecheck_recoveries_proxy", None)
    out["forecheck_recoveries_oz_takeaways"] = ta_oz
    out["real_data_only"] = True
    out["warehouse_aliases_version"] = 2
    return out


def reenrich_existing_flat() -> Optional[Path]:
    """Re-apply aliases to curated flat without a live pull."""
    path = CURATED / "skaters" / "instat_season_flat.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    rows = [enrich_instat_skater_row(r) for r in (data.get("skaters") or []) if isinstance(r, dict)]
    data["skaters"] = rows
    data["count"] = len(rows)
    data["aliases_version"] = 1
    path.write_text(json.dumps(data, indent=2))
    return path


def _copy_lld_instat_artifacts() -> Dict[str, Any]:
    label = season_label()
    copied: Dict[str, Any] = {}
    for name in (f"instat-aggs.json", f"instat-shots-{label}", "instat-shots"):
        src = LLD / "data" / name
        if not src.exists():
            continue
        if src.is_dir():
            n = sum(1 for _ in src.glob("*.json"))
            (RAW / "instat" / f"{name.replace('/', '_')}.pointer.json").write_text(
                json.dumps({"source": str(src), "files": n}, indent=2)
            )
            copied[name] = {"path": str(src), "files": n, "mirrored": False}
        else:
            dest = RAW / "instat" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(src.read_text())
            copied[name] = {"path": str(dest), "mirrored": True}

    aggs = LLD / "data" / "instat-aggs.json"
    if aggs.exists():
        data = json.loads(aggs.read_text())
        out = CURATED / "goalies" / "instat_aggs.json"
        out.write_text(json.dumps(data, indent=2))
        copied["curated_goalies_instat_aggs"] = str(out)
    return copied


async def _fetch_team_skaters(api, team_id: int, season_id: int) -> List[dict]:
    import instat_api as instat_mod

    instat_mod.TEAM_ID = team_id
    instat_mod.SEASON_ID = season_id
    matches = await api.get_matches_list()
    match_ids = api._extract_match_ids(matches)
    if not match_ids:
        return []
    skaters = await api.get_team_skaters(match_ids)
    col_map = await api._build_col_map(1)
    return api._parse_player_rows(skaters, col_map)


async def _live_pull() -> Dict[str, Any]:
    sys.path.insert(0, str(HUDL))
    sys.path.insert(0, str(SCRAPING))

    from playwright.async_api import async_playwright
    from instat_api import InStatAPI
    from player_cards.goalie_source import _build_summary, _fetch_team_goalie_rows
    from player_cards.leagues import NHL_INSTAT_TEAM_IDS, SEASON_TO_INSTAT

    label = season_label()
    season_id = SEASON_TO_INSTAT.get(label) or SEASON_TO_INSTAT.get(f"{label}") or 38
    team_limit = int(os.getenv("INSTAT_TEAM_LIMIT", "32"))
    teams = list(NHL_INSTAT_TEAM_IDS.items())[:team_limit]

    result: Dict[str, Any] = {
        "auth_ok": False,
        "season_id": season_id,
        "season_label": label,
        "goalie_summaries": 0,
        "skater_rows": 0,
        "teams_ok": [],
        "errors": [],
    }

    api = InStatAPI()
    async with async_playwright() as p:
        authed = await api.init_session(p)
        result["auth_ok"] = bool(authed)
        if not authed:
            result["errors"].append(
                "init_session failed — refresh ~/.cache/player-cards/instat_headers_cache.json "
                "or set INSTAT_DEDICATED_ACCOUNT=1 with HUDL_USERNAME/PASSWORD"
            )
            await api.close()
            return result

        goalie_summaries: List[dict] = []
        skaters_by_team: Dict[str, list] = {}

        for abbr, tid in teams:
            try:
                grows = await _fetch_team_goalie_rows(tid, season_id, api)
                for row in grows or []:
                    summary = _build_summary(row)
                    summary["team"] = abbr
                    summary["raw_player"] = row.get("Player")
                    goalie_summaries.append(summary)
            except Exception as e:
                result["errors"].append(f"goalies {abbr}: {e}")
                if "401" in str(e) or "Unauthorized" in str(e):
                    break

            try:
                srows = await _fetch_team_skaters(api, tid, season_id)
                skaters_by_team[abbr] = srows or []
                result["teams_ok"].append(abbr)
            except Exception as e:
                result["errors"].append(f"skaters {abbr}: {e}")
                if "401" in str(e) or "Unauthorized" in str(e):
                    break

        await api.close()

    if goalie_summaries:
        (CURATED / "goalies" / "instat_league.json").write_text(
            json.dumps({"season_id": season_id, "goalies": goalie_summaries}, indent=2)
        )
        result["goalie_summaries"] = len(goalie_summaries)

    if skaters_by_team:
        (CURATED / "skaters" / "instat_season_by_team.json").write_text(
            json.dumps({"season_id": season_id, "teams": skaters_by_team}, indent=2)
        )
        flat = []
        for abbr, rows in skaters_by_team.items():
            for r in rows or []:
                if isinstance(r, dict):
                    flat.append(enrich_instat_skater_row({**r, "nhl_team": abbr}))
        (CURATED / "skaters" / "instat_season_flat.json").write_text(
            json.dumps({"season_id": season_id, "skaters": flat, "count": len(flat)}, indent=2)
        )
        result["skater_rows"] = len(flat)
        result["skaters_by_team"] = {k: len(v) for k, v in skaters_by_team.items()}

    (RAW / "instat" / "live_pull_summary.json").write_text(
        json.dumps(result, indent=2, default=str)
    )
    return result


def ingest(live: bool = True) -> Dict[str, Any]:
    ensure_dirs()
    mirrored = _copy_lld_instat_artifacts()
    live_result: Dict[str, Any] = {"skipped": not live}
    if live:
        try:
            live_result = asyncio.run(_live_pull())
        except Exception as e:
            live_result = {"auth_ok": False, "errors": [str(e)]}
    # Always refresh aliases on any existing flat file (live or prior)
    reenrich_existing_flat()

    ok = bool(live_result.get("auth_ok")) or bool(mirrored)
    _status(
        ok,
        live_auth_ok=bool(live_result.get("auth_ok")),
        mirrored_lld=mirrored,
        live={k: v for k, v in live_result.items() if k != "goalies"},
        note=(
            "InStat live pull OK"
            if live_result.get("auth_ok")
            else "Live InStat auth failed — mirrored LLD artifacts when available. "
            "Fix: INSTAT_DEDICATED_ACCOUNT=1 + HUDL creds, or refresh instat_headers_cache.json"
        ),
    )
    print(
        f"📡 InStat: live_auth={live_result.get('auth_ok')} "
        f"goalies={live_result.get('goalie_summaries')} "
        f"skaters={live_result.get('skater_rows')} "
        f"mirrored={list(mirrored)} "
        f"errors={list(live_result.get('errors') or [])[:2]}"
    )
    return {"mirrored": mirrored, "live": live_result}


if __name__ == "__main__":
    ingest(live=os.getenv("INSTAT_SKIP_LIVE", "").strip() != "1")
