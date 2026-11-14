#!/usr/bin/env python3
"""Generate a single-team card from season-to-date RS warehouse microstats.

Uses only 2026-27 regular-season curated PBP (+ optional standing via NHL API).
Does not invent InStat action metrics.
"""

from __future__ import annotations

import html
import json
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from paths import CURATED, ensure_dirs

USER_AGENT = "metrics-warehouse/1.0"
SEASON = "20262027"
GAME_TYPE = "2"  # NHL stats API gameType
GAME_TYPE_IN_ID = "02"  # chars [4:6] in YYYYYTNNNN game ids

TEAM_NAMES = {
    "ANA": "Anaheim Ducks", "BOS": "Boston Bruins", "BUF": "Buffalo Sabres",
    "CAR": "Carolina Hurricanes", "CBJ": "Columbus Blue Jackets", "CGY": "Calgary Flames",
    "CHI": "Chicago Blackhawks", "COL": "Colorado Avalanche", "DAL": "Dallas Stars",
    "DET": "Detroit Red Wings", "EDM": "Edmonton Oilers", "FLA": "Florida Panthers",
    "LAK": "Los Angeles Kings", "MIN": "Minnesota Wild", "MTL": "Montréal Canadiens",
    "NSH": "Nashville Predators", "NJD": "New Jersey Devils", "NYI": "New York Islanders",
    "NYR": "New York Rangers", "OTT": "Ottawa Senators", "PHI": "Philadelphia Flyers",
    "PIT": "Pittsburgh Penguins", "SEA": "Seattle Kraken", "SJS": "San Jose Sharks",
    "STL": "St. Louis Blues", "TBL": "Tampa Bay Lightning", "TOR": "Toronto Maple Leafs",
    "UTA": "Utah Mammoth", "VAN": "Vancouver Canucks", "VGK": "Vegas Golden Knights",
    "WPG": "Winnipeg Jets", "WSH": "Washington Capitals",
}

PRIMARY = {
    "ANA": "#F47A38", "BOS": "#FFB81C", "BUF": "#003087", "CAR": "#CC0000",
    "CBJ": "#002654", "CGY": "#C8102E", "CHI": "#CF0A2C", "COL": "#6F263D",
    "DAL": "#006847", "DET": "#CE1126", "EDM": "#FF4C00", "FLA": "#C8102E",
    "LAK": "#111111", "MIN": "#154734", "MTL": "#AF1E2D", "NSH": "#FFB81C",
    "NJD": "#CE1126", "NYI": "#00539B", "NYR": "#0038A8", "OTT": "#C52032",
    "PHI": "#F74902", "PIT": "#FCB514", "SEA": "#99D9D9", "SJS": "#006D75",
    "STL": "#002F87", "TBL": "#002868", "TOR": "#00205B", "UTA": "#6CACE4",
    "VAN": "#00205B", "VGK": "#B4975A", "WPG": "#041E42", "WSH": "#C8102E",
}

# (rate_key, label, higher_is_better)
CARD_METRICS: List[Tuple[str, str, bool]] = [
    ("controlled_entry_pct", "Controlled entry %", True),
    ("dump_in_recovery_pct", "Dump-in recovery %", True),
    ("nz_advance_pct", "NZ advance %", True),
    ("exit_to_entry_chain_pct", "Exit→entry chain %", True),
    ("dz_retrieval_to_controlled_exit_pct", "DZ retrieval→ctrl exit %", True),
    ("failed_entry_pct", "Failed entry %", False),
    ("failed_exit_pct", "Failed exit %", False),
    ("forecheck_pressure_index", "Forecheck pressure", True),
    ("rebound_second_chance_pct", "Rebound 2nd-chance %", True),
    ("slot_drive_to_shot_pct", "Slot-drive→shot %", True),
    ("sc_off_dump_per_game", "SC off dump / GP", True),
    ("sc_off_carry_per_game", "SC off carry / GP", True),
    ("zone_to_shot_against_pct_dz", "DZ TO→shot against %", False),
    ("ev5v5_controlled_entry_pct", "5v5 controlled entry %", True),
]


def _load_team_store() -> Dict[str, Any]:
    path = CURATED / "teams" / "nhl_pbp_microstats.json"
    if not path.exists():
        raise FileNotFoundError(f"missing {path} — run season backfill first")
    return json.loads(path.read_text())


def assert_rs_season(store: Dict[str, Any]) -> None:
    season = str(store.get("season") or "")
    if season != SEASON:
        raise ValueError(f"expected season {SEASON}, got {season}")
    ids = store.get("processed_games") or []
    bad = [
        g
        for g in ids
        if not (str(g).startswith("2026") and str(g)[4:6] == GAME_TYPE_IN_ID)
    ]
    if bad:
        raise ValueError(f"non-RS-2026 game ids present: {bad[:5]}")


def fetch_standing(abbr: str) -> Dict[str, Any]:
    url = "https://api-web.nhle.com/v1/standings/now"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rows = json.load(resp).get("standings") or []
    except Exception:
        return {}
    for r in rows:
        if (r.get("teamAbbrev") or {}).get("default") == abbr:
            return {
                "wins": r.get("wins"),
                "losses": r.get("losses"),
                "ot_losses": r.get("otLosses"),
                "points": r.get("points"),
                "games_played": r.get("gamesPlayed"),
                "goal_diff": r.get("goalDifferential"),
                "division": (r.get("divisionName") or ""),
                "conference": (r.get("conferenceName") or ""),
                "streak_code": (r.get("streakCode") or ""),
                "streak_count": r.get("streakCount"),
            }
    return {}


def _fmt(v: Any, pct: bool = False) -> str:
    if v is None:
        return "—"
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "—"
    return f"{f:.1f}%" if pct else f"{f:.2f}".rstrip("0").rstrip(".")


def _bar_row(label: str, value: Optional[float], lo: float, hi: float, invert: bool = False) -> str:
    if value is None:
        return (
            f'<div class="row"><span class="lbl">{html.escape(label)}</span>'
            f'<span class="track"><span class="fill" style="width:0%"></span></span>'
            f'<span class="val">—</span></div>'
        )
    span = (hi - lo) or 1.0
    norm = (value - lo) / span
    if invert:
        norm = 1.0 - norm
    width = 12 + 88 * max(0.0, min(1.0, norm))
    disp = f"{value:.1f}" if abs(value) >= 10 or value == int(value) else f"{value:.2f}"
    if " %" in label or label.endswith("%"):
        disp = f"{value:.1f}"
    return (
        f'<div class="row"><span class="lbl">{html.escape(label)}</span>'
        f'<span class="track"><span class="fill" style="width:{width:.0f}%"></span></span>'
        f'<span class="val">{html.escape(disp)}</span></div>'
    )


def render_html(abbr: str, row: Dict[str, Any], league: Dict[str, Dict[str, Any]], standing: Dict[str, Any]) -> str:
    rates = row.get("rates") or {}
    gp = int(row.get("games") or 0)
    primary = PRIMARY.get(abbr, "#111")
    name = TEAM_NAMES.get(abbr, abbr)

    # league ranges for bar scaling
    ranges: Dict[str, Tuple[float, float]] = {}
    for key, _lbl, _hib in CARD_METRICS:
        vals = []
        for t in league.values():
            v = (t.get("rates") or {}).get(key)
            if v is not None:
                vals.append(float(v))
        if vals:
            ranges[key] = (min(vals), max(vals))
        else:
            ranges[key] = (0.0, 1.0)

    offense = "".join(
        _bar_row(lbl, rates.get(key), *ranges[key], invert=not hib)
        for key, lbl, hib in CARD_METRICS[:5]
    )
    defense = "".join(
        _bar_row(lbl, rates.get(key), *ranges[key], invert=not hib)
        for key, lbl, hib in CARD_METRICS[5:10]
    )
    volume = "".join(
        _bar_row(lbl, rates.get(key), *ranges[key], invert=not hib)
        for key, lbl, hib in CARD_METRICS[10:]
    )

    w = standing.get("wins", "—")
    l = standing.get("losses", "—")
    otl = standing.get("ot_losses", "—")
    pts = standing.get("points", "—")
    streak = ""
    if standing.get("streak_code") and standing.get("streak_count"):
        streak = f"{standing['streak_code']}{standing['streak_count']}"

    dump_bins = rates.get("dump_recovery_pct_by_landing") or {}
    bin_cells = "".join(
        f'<div class="bin"><b>{html.escape(k.replace("_", " "))}</b><span>{_fmt(v)}</span></div>'
        for k, v in dump_bins.items()
        if v is not None
    ) or '<div class="bin"><b>n/a</b><span>—</span></div>'

    score = rates.get("score_state") or {}
    ss_rows = ""
    for ss in ("tied", "leading", "trailing"):
        block = score.get(ss) or {}
        ss_rows += (
            f'<tr><td>{ss}</td><td>{block.get("entries", "—")}</td>'
            f'<td>{_fmt(block.get("controlled_entry_pct"))}</td>'
            f'<td>{_fmt(block.get("dump_in_recovery_pct"))}</td>'
            f'<td>{_fmt(block.get("failed_entry_pct"))}</td></tr>'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{html.escape(name)} · Warehouse Team Card</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root {{
  --ink:#0f172a; --muted:#64748b; --line:#e2e8f0; --bg:#f8fafc;
  --primary:{primary}; --card:#fff;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:#0b1220; font-family:'IBM Plex Sans',system-ui,sans-serif; color:var(--ink); }}
.card {{
  width:1100px; margin:24px auto; background:var(--card); border-radius:16px; overflow:hidden;
  box-shadow:0 20px 60px rgba(0,0,0,.35);
}}
.header {{
  display:grid; grid-template-columns:1.4fr .9fr; gap:16px; padding:22px 28px;
  background:linear-gradient(135deg, var(--primary), #0f172a 70%); color:#fff;
}}
.eyebrow {{ font-size:12px; letter-spacing:.14em; text-transform:uppercase; opacity:.8; }}
h1 {{ margin:4px 0 6px; font-size:34px; line-height:1.05; }}
.sub {{ font-size:13px; opacity:.85; }}
.hero {{
  display:flex; gap:14px; justify-content:flex-end; align-items:stretch;
}}
.hero .tile {{
  background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.18);
  border-radius:12px; padding:10px 14px; min-width:88px; text-align:center;
}}
.hero .tile b {{ display:block; font-size:26px; font-family:'IBM Plex Mono',monospace; }}
.hero .tile span {{ font-size:11px; text-transform:uppercase; letter-spacing:.08em; opacity:.8; }}
.badge {{
  display:inline-block; margin-top:10px; padding:4px 10px; border-radius:999px;
  background:rgba(255,255,255,.14); font-size:11px; letter-spacing:.06em;
}}
.grid {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:0; border-top:1px solid var(--line); }}
.col {{ padding:16px 18px; border-right:1px solid var(--line); }}
.col:last-child {{ border-right:none; }}
.h {{ font-size:11px; text-transform:uppercase; letter-spacing:.12em; color:var(--muted); margin-bottom:10px; font-weight:700; }}
.row {{ display:grid; grid-template-columns:1.3fr 1fr 48px; gap:8px; align-items:center; margin:6px 0; }}
.lbl {{ font-size:12px; color:var(--ink); }}
.track {{ height:8px; background:#eef2f7; border-radius:99px; overflow:hidden; }}
.fill {{ display:block; height:100%; background:var(--primary); border-radius:99px; }}
.val {{ font-size:12px; font-family:'IBM Plex Mono',monospace; text-align:right; color:var(--muted); }}
.bins {{ display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin-top:8px; }}
.bin {{ background:var(--bg); border:1px solid var(--line); border-radius:10px; padding:8px; }}
.bin b {{ display:block; font-size:10px; text-transform:uppercase; color:var(--muted); }}
.bin span {{ font-family:'IBM Plex Mono',monospace; font-size:14px; }}
table {{ width:100%; border-collapse:collapse; font-size:12px; }}
th, td {{ padding:6px 4px; border-bottom:1px solid var(--line); text-align:right; }}
th:first-child, td:first-child {{ text-align:left; }}
th {{ color:var(--muted); font-weight:600; font-size:10px; text-transform:uppercase; letter-spacing:.06em; }}
.footer {{
  padding:12px 18px; background:var(--bg); border-top:1px solid var(--line);
  font-size:11px; color:var(--muted); display:flex; justify-content:space-between;
}}
</style>
</head>
<body>
<article class="card">
  <header class="header">
    <div>
      <div class="eyebrow">Metrics Warehouse · NHL Regular Season</div>
      <h1>{html.escape(name)}</h1>
      <div class="sub">{html.escape(standing.get("conference") or "")} · {html.escape(standing.get("division") or "")} · 2026-27 RS</div>
      <div class="badge">PBP microstats schema v4 · {gp} GP in warehouse · gameType=2</div>
    </div>
    <div class="hero">
      <div class="tile"><b>{html.escape(str(pts))}</b><span>Points</span></div>
      <div class="tile"><b>{w}-{l}-{otl}</b><span>W-L-OT</span></div>
      <div class="tile"><b>{gp}</b><span>GP</span></div>
      <div class="tile"><b>{html.escape(streak or "—")}</b><span>Streak</span></div>
    </div>
  </header>
  <div class="grid">
    <div class="col"><div class="h">Transition</div>{offense}</div>
    <div class="col"><div class="h">Pressure / Defense</div>{defense}</div>
    <div class="col"><div class="h">Chance Creation</div>{volume}
      <div class="h" style="margin-top:16px">Dump recovery by landing</div>
      <div class="bins">{bin_cells}</div>
    </div>
  </div>
  <div class="grid" style="grid-template-columns:1.2fr .8fr">
    <div class="col">
      <div class="h">Score-state splits</div>
      <table>
        <tr><th>State</th><th>Entries</th><th>Ctrl%</th><th>Dump rec%</th><th>Fail ent%</th></tr>
        {ss_rows}
      </table>
    </div>
    <div class="col">
      <div class="h">Key rates</div>
      <table>
        <tr><td>Entries / GP</td><td>{_fmt(rates.get("entries_per_game"))}</td></tr>
        <tr><td>FC recoveries / GP</td><td>{_fmt(rates.get("forecheck_recoveries_per_game"))}</td></tr>
        <tr><td>NZ plays / GP</td><td>{_fmt(rates.get("nz_plays_per_game"))}</td></tr>
        <tr><td>DZ ctrl-exit / GP</td><td>{_fmt(rates.get("dz_controlled_exit_from_retrieval_per_game"))}</td></tr>
        <tr><td>Slot drives / GP</td><td>{_fmt(rates.get("slot_drives_per_game"))}</td></tr>
      </table>
    </div>
  </div>
  <div class="footer">
    <span>Source: NHL gamecenter PBP · 2026-27 RS only · real event counts · no fake/sample/imputed metrics</span>
    <span>Generated {html.escape(time.strftime("%Y-%m-%d %H:%M"))}</span>
  </div>
</article>
</body>
</html>"""


def build_card(abbr: str) -> Dict[str, Any]:
    ensure_dirs()
    abbr = abbr.upper()
    store = _load_team_store()
    assert_rs_season(store)
    # stamp game_type if missing
    if store.get("game_type") != GAME_TYPE:
        store["game_type"] = GAME_TYPE
        (CURATED / "teams" / "nhl_pbp_microstats.json").write_text(json.dumps(store, indent=2))

    teams = store.get("teams") or {}
    if abbr not in teams:
        raise KeyError(f"{abbr} not in warehouse teams ({len(teams)} present)")

    standing = fetch_standing(abbr)
    html_str = render_html(abbr, teams[abbr], teams, standing)
    out_dir = CURATED / "team_cards"
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / f"{abbr}_2026-27_rs.html"
    html_path.write_text(html_str, encoding="utf-8")
    json_path = out_dir / f"{abbr}_2026-27_rs.json"
    payload = {
        "team": abbr,
        "season": SEASON,
        "game_type": GAME_TYPE,
        "games": teams[abbr].get("games"),
        "standing": standing,
        "rates": teams[abbr].get("rates"),
        "html": str(html_path),
        "source": "metrics-warehouse curated RS PBP",
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    png_path = None
    try:
        # Optional PNG via playwright if available in player_cards
        import sys

        sys.path.insert(0, str(Path("/Users/emilyfehr8/CascadeProjects/automated-scraping")))
        from player_cards.png_export import html_to_png

        png_path = out_dir / f"{abbr}_2026-27_rs.png"
        html_to_png(html_path, png_path)
    except Exception as e:
        png_path = None
        payload["png_error"] = str(e)

    return {"html": str(html_path), "json": str(json_path), "png": str(png_path) if png_path else None, "games": teams[abbr].get("games")}


def build_all() -> List[Dict[str, Any]]:
    store = _load_team_store()
    assert_rs_season(store)
    out = []
    for abbr in sorted((store.get("teams") or {}).keys()):
        out.append(build_card(abbr))
        print(f"  ✓ {abbr}", flush=True)
    return out


if __name__ == "__main__":
    import sys

    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "--all" in sys.argv:
        build_all()
    else:
        tri = (args[0] if args else "CBJ").upper()
        result = build_card(tri)
        print(json.dumps(result, indent=2))
