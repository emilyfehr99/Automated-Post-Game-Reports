#!/usr/bin/env python3
"""Verify warehouse curated stores for the current season (no multi-season bleed)."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipelines"))
from paths import CURATED  # noqa: E402

SEASON = os.getenv("NHL_SEASON", "20262027")
UA = {"User-Agent": "mw-verify/1"}


def _load(p: Path):
    return json.loads(p.read_text())


def expected_rs_ids() -> set[str]:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    expr = f'season={SEASON} and gameType=2 and gameDate<="{today}"'
    ids: set[str] = set()
    start = 0
    total = None
    while total is None or start < total:
        url = f"https://api.nhle.com/stats/rest/en/game?cayenneExp={quote(expr)}&limit=100&start={start}"
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=45) as resp:
            payload = json.load(resp)
        rows = payload.get("data") or []
        total = int(payload.get("total") or 0)
        for r in rows:
            state = int(r.get("gameStateId") or 0)
            if r.get("id") and state >= 5:
                ids.add(str(r["id"]))
        start += len(rows) or 1
        if not rows:
            break
    return ids


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    expected = expected_rs_ids()
    print(f"expected_rs={len(expected)} season={SEASON}")

    sk_path = CURATED / "skaters_season.json"
    if not sk_path.exists():
        errors.append("missing skaters_season.json")
        print("FAIL", errors)
        return 1
    sk = _load(sk_path)
    proc = set(str(x) for x in (sk.get("processed_games") or []))
    bad_season = [g for g in proc if not (g.startswith(SEASON[:4]) and len(g) >= 6 and g[4:6] == "02")]
    missing = expected - proc
    extra = proc - expected
    print(
        f"skaters mode={sk.get('mode')} season={sk.get('season')} "
        f"games={len(proc)} skaters={sk.get('skater_count')} "
        f"missing={len(missing)} extra={len(extra)} bad_ids={len(bad_season)}"
    )
    if sk.get("season") and sk.get("season") != SEASON:
        errors.append(f"skater season field {sk.get('season')} != {SEASON}")
    # Season-scoped modes: full rebuild or append-since-last-run.
    require_season = os.getenv("WAREHOUSE_SEASON_BACKFILL", "1").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    if require_season and sk.get("mode") not in {"season_backfill", "season_append"}:
        errors.append(
            f"skater mode={sk.get('mode')} — need season_backfill|season_append"
        )
    if bad_season:
        errors.append(f"{len(bad_season)} non-current-RS game ids in skater store")
    # Tight gap: schedule runs 2x/day; >5 missing means finals aren't being picked up.
    if len(missing) > 5:
        errors.append(f"missing {len(missing)} completed RS games (tolerance 5)")
        sample = sorted(missing)[:8]
        print(f"missing_sample={sample}")
    elif missing:
        warnings.append(f"missing {len(missing)} RS games (within tolerance)")
    if extra:
        warnings.append(f"{len(extra)} processed games not in expected set")

    players = sk.get("skaters") or {}
    max_g = max((int(p.get("games") or 0) for p in players.values()), default=0)
    # YTD through mid-Nov ~20 GP; allow 35 cushion for schedule
    if max_g > 40:
        errors.append(f"max player games {max_g} suggests multi-season bleed")
    print(f"max_player_games={max_g}")

    team_pbp = CURATED / "teams" / "nhl_pbp_microstats.json"
    if not team_pbp.exists():
        errors.append("missing teams/nhl_pbp_microstats.json")
    else:
        tp = _load(team_pbp)
        print(f"team_pbp teams={tp.get('team_count')} games={tp.get('game_count')}")
        if int(tp.get("team_count") or 0) < 32:
            errors.append(f"team_pbp team_count {tp.get('team_count')} < 32")

    teams = _load(CURATED / "teams_season.json")
    empty_micro = 0
    stale_adv = 0
    for abbr, row in (teams.get("teams") or {}).items():
        micro = row.get("microstats") or {}
        if not micro:
            empty_micro += 1
        adv = row.get("advanced")
        if isinstance(adv, dict) and int(adv.get("games") or 0) > 30:
            # Current RS mid-Nov ~20 GP; >30 with warehouse ~17 is multi-season bleed
            wh = int((row.get("pbp_totals") or {}).get("games") or 0)
            if wh and int(adv.get("games") or 0) > wh + 3:
                stale_adv += 1
    print(
        f"teams_combined={teams.get('team_count')} empty_microstats={empty_micro} "
        f"stale_advanced_published={stale_adv} real_data_only={teams.get('real_data_only')}"
    )
    if empty_micro:
        errors.append(f"{empty_micro} teams missing microstats in combined store")
    if stale_adv:
        errors.append(f"{stale_adv} teams still publish multi-season advanced as current")
    if teams.get("real_data_only") is not True:
        errors.append("teams_season.real_data_only must be true")

    # Combined honesty / no imputed stand-ins
    comb_path = CURATED / "combined_microstats.json"
    if comb_path.exists():
        comb = _load(comb_path)
        hon = comb.get("honesty") or {}
        print(
            f"combined honesty real_data_only={hon.get('real_data_only')} "
            f"no_imputation={hon.get('no_imputation')} no_proxy={hon.get('no_proxy_standins')}"
        )
        if hon.get("no_imputation") is not True:
            errors.append("combined honesty.no_imputation missing")
        # Spot-check: forbidden keys must stay null on skaters
        from real_data import FORBIDDEN_IMPUTED_KEYS, PROXY_STANDIN_KEYS, assert_no_imputed

        bad = 0
        for pid, s in list((comb.get("skaters") or {}).items())[:200]:
            inst = s.get("instat") or {}
            for e in assert_no_imputed(inst, path=f"skater.{pid}.instat"):
                errors.append(e)
                bad += 1
            for k in PROXY_STANDIN_KEYS:
                if k in inst and inst.get(k) is not None and not str(k).endswith("_note"):
                    errors.append(f"skater.{pid}.instat still has proxy stand-in {k}")
                    bad += 1
            for k in FORBIDDEN_IMPUTED_KEYS:
                if k in inst and inst.get(k) is not None:
                    bad += 1
        print(f"imputation_spotcheck_bad={bad}")

    instat = _load(CURATED / "status" / "instat.json")
    print(f"instat live_auth={instat.get('live_auth_ok')} ok={instat.get('ok')}")
    if not instat.get("live_auth_ok"):
        warnings.append("InStat live_auth_ok=false")
    live = instat.get("live") or {}
    if int(live.get("skater_rows") or 0) < 500:
        warnings.append(f"InStat skater_rows low: {live.get('skater_rows')}")
    if len(live.get("teams_ok") or []) < 32:
        warnings.append(f"InStat teams_ok={len(live.get('teams_ok') or [])}")

    g = _load(CURATED / "goalies_season.json")
    print(f"goalies_lld={g.get('goalie_count')}")
    if int(g.get("goalie_count") or 0) < 50:
        errors.append("LLD goalie_count unexpectedly low")

    print("---")
    for w in warnings:
        print("WARN:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        print("VERDICT: FAIL")
        return 1
    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
