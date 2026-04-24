from __future__ import annotations

import argparse
import json
import math
import os
import time
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
import requests

NHL_API_BASE = "https://api-web.nhle.com/v1"
REG_PERIODS = 3
PERIOD_SEC = 20 * 60


@dataclass(frozen=True)
class Situation:
    away_goalie: int
    away_skaters: int
    home_skaters: int
    home_goalie: int


@dataclass(frozen=True)
class RateCI:
    n: int
    k: int
    rate: float
    ci_low: float
    ci_high: float


def wilson_ci(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * math.sqrt((phat * (1 - phat) + z**2 / (4 * n)) / n)) / denom
    return max(0.0, center - half), min(1.0, center + half)


def mmss_to_seconds(mmss: str) -> int:
    mm, ss = mmss.split(":")
    return int(mm) * 60 + int(ss)


def parse_situation_code(code: Optional[str]) -> Optional[Situation]:
    if not code:
        return None
    s = str(code).zfill(4)
    if len(s) != 4 or not s.isdigit():
        return None
    return Situation(
        away_goalie=int(s[0]),
        away_skaters=int(s[1]),
        home_skaters=int(s[2]),
        home_goalie=int(s[3]),
    )


def get_json(url: str, retries: int = 5, timeout_s: int = 30) -> Dict[str, Any]:
    last_exc: Optional[Exception] = None
    headers = {
        "User-Agent": "automated-post-game-reports timeout-goalie-pull-study",
        "Accept": "application/json",
    }
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=timeout_s)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last_exc = e
            time.sleep(min(8.0, 0.5 * (2**attempt)) + 0.05 * attempt)
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("Failed to fetch JSON (unknown error)")


def default_cache_dir() -> Path:
    return Path(".cache") / "nhl_timeout_goalie_pull"


def get_season_dates(season_start_year: int) -> Tuple[str, str]:
    probe_date = f"{season_start_year:04d}-10-01"
    j = get_json(f"{NHL_API_BASE}/schedule/{probe_date}")
    return j["regularSeasonStartDate"], j["regularSeasonEndDate"]


def iter_regular_season_game_ids(season_start_year: int, cache_dir: Path) -> Iterable[int]:
    sched_dir = cache_dir / "schedules"
    sched_dir.mkdir(parents=True, exist_ok=True)
    cache_path = sched_dir / f"regular_game_ids_{season_start_year}.json"
    if cache_path.exists():
        ids = json.loads(cache_path.read_text(encoding="utf-8"))
        for gid in ids:
            yield int(gid)
        return

    regular_start, regular_end = get_season_dates(season_start_year)
    date_cursor = regular_start
    collected: List[int] = []
    while True:
        j = get_json(f"{NHL_API_BASE}/schedule/{date_cursor}")
        for day in j.get("gameWeek", []):
            for g in day.get("games") or []:
                if g.get("gameType") == 2:  # regular season
                    gid = int(g["id"])
                    collected.append(gid)
                    yield gid
        next_date = j.get("nextStartDate")
        if not next_date or next_date > regular_end:
            break
        date_cursor = next_date

    cache_path.write_text(json.dumps(sorted(set(collected))), encoding="utf-8")


def fetch_pbp(game_id: int, cache_dir: Path, force: bool = False) -> Dict[str, Any]:
    pbp_dir = cache_dir / "pbp"
    pbp_dir.mkdir(parents=True, exist_ok=True)
    path = pbp_dir / f"{game_id}.json"
    if path.exists() and not force:
        return json.loads(path.read_text(encoding="utf-8"))
    j = get_json(f"{NHL_API_BASE}/gamecenter/{game_id}/play-by-play")
    path.write_text(json.dumps(j), encoding="utf-8")
    return j


def is_team_timeout_stoppage(play: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    if play.get("typeDescKey") != "stoppage":
        return False, None
    d = play.get("details") or {}
    sec = str(d.get("secondaryReason") or "").strip().lower()
    if sec in {"home-timeout", "visitor-timeout"}:
        return True, sec
    # some games use `reason` only
    reason = str(d.get("reason") or "").strip().lower()
    if reason in {"home-timeout", "visitor-timeout"}:
        return True, reason
    return False, None


def build_events(pbp: Dict[str, Any]) -> pd.DataFrame:
    away_id = int(pbp["awayTeam"]["id"])
    home_id = int(pbp["homeTeam"]["id"])

    # Build a flat event log for regulation only (period 1-3).
    rows: List[Dict[str, Any]] = []
    home_score = 0
    away_score = 0

    plays = sorted(pbp.get("plays", []), key=lambda p: (int(p.get("sortOrder") or 0), int(p.get("eventId") or 0)))
    for p in plays:
        period = int(p["periodDescriptor"]["number"])
        if period > REG_PERIODS:
            continue
        time_in_period = str(p["timeInPeriod"])
        time_remaining = str(p["timeRemaining"])
        elapsed_period = mmss_to_seconds(time_in_period)
        rem_period = mmss_to_seconds(time_remaining)
        abs_elapsed = (period - 1) * PERIOD_SEC + elapsed_period
        rem_game = (REG_PERIODS - period) * PERIOD_SEC + rem_period

        details = p.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        owner_id = int(owner) if owner is not None else None
        sit_code = p.get("situationCode")
        sit = parse_situation_code(sit_code)

        # Score before this play (except goal updates score at the goal event itself).
        pre_home = home_score
        pre_away = away_score

        if p.get("typeDescKey") == "goal":
            # The feed includes updated scores on the goal event.
            try:
                home_score = int(details.get("homeScore"))
                away_score = int(details.get("awayScore"))
            except Exception:
                # fall back to pre + 1 if we know owner
                if owner_id == home_id:
                    home_score += 1
                elif owner_id == away_id:
                    away_score += 1

        is_timeout, timeout_kind = is_team_timeout_stoppage(p)
        rows.append(
            {
                "gameId": int(pbp["id"]),
                "awayTeamId": away_id,
                "homeTeamId": home_id,
                "eventId": int(p["eventId"]),
                "sortOrder": int(p.get("sortOrder") or 0),
                "period": period,
                "absElapsedSec": abs_elapsed,
                "remGameSec": rem_game,
                "typeDescKey": p.get("typeDescKey"),
                "situationCode": sit_code,
                "awayGoalie": sit.away_goalie if sit else None,
                "homeGoalie": sit.home_goalie if sit else None,
                "eventOwnerTeamId": owner_id,
                "preHomeScore": pre_home,
                "preAwayScore": pre_away,
                "isTeamTimeout": bool(is_timeout),
                "teamTimeoutKind": timeout_kind,  # home-timeout / visitor-timeout
            }
        )

    df = pd.DataFrame.from_records(rows)
    df.sort_values(["sortOrder", "eventId"], inplace=True, ignore_index=True)
    return df


def _rate_ci(k: int, n: int) -> RateCI:
    rate = k / n if n else float("nan")
    lo, hi = wilson_ci(k, n) if n else (float("nan"), float("nan"))
    return RateCI(n=n, k=k, rate=rate, ci_low=lo, ci_high=hi)


def _bucket_label(rem_game_sec: int, bucket_min: int) -> str:
    # bucket_min in minutes, bucket is [m, m+bucket_min) in remaining minutes.
    m = rem_game_sec // 60
    start = (m // bucket_min) * bucket_min
    end = start + bucket_min
    return f"{start:02d}-{end:02d}"


def analyze_timeouts(
    events: pd.DataFrame,
    *,
    diff: int,
    windows_sec: List[int],
    bucket_min: int,
) -> Dict[str, Any]:
    """
    Trailing team team-timeouts when down by `diff` at the moment of timeout.
    """
    home_id = int(events["homeTeamId"].iloc[0])
    away_id = int(events["awayTeamId"].iloc[0])

    timeout_events = events[events["isTeamTimeout"]].copy()
    if timeout_events.empty:
        return {"diff": diff, "buckets": {}, "overall": {}}

    goals = events[events["typeDescKey"] == "goal"].copy()

    # Accumulators
    buckets: Dict[str, Dict[str, int]] = {}
    overall: Dict[str, int] = {}

    for _, t in timeout_events.iterrows():
        kind = str(t["teamTimeoutKind"] or "")
        if kind == "home-timeout":
            caller = home_id
            caller_score = int(t["preHomeScore"])
            opp_score = int(t["preAwayScore"])
        elif kind == "visitor-timeout":
            caller = away_id
            caller_score = int(t["preAwayScore"])
            opp_score = int(t["preHomeScore"])
        else:
            continue

        score_diff = opp_score - caller_score
        if score_diff != diff:
            continue

        rem_game = int(t["remGameSec"])
        b = _bucket_label(rem_game, bucket_min)
        buckets.setdefault(b, {})
        overall.setdefault("n", 0)
        overall["n"] += 1
        buckets[b].setdefault("n", 0)
        buckets[b]["n"] += 1

        t_abs = int(t["absElapsedSec"])
        t_period = int(t["period"])

        # Goals by caller / against caller within each window
        for w in windows_sec:
            key_for = f"gf_{w}"
            key_against = f"ga_{w}"
            overall.setdefault(key_for, 0)
            overall.setdefault(key_against, 0)
            buckets[b].setdefault(key_for, 0)
            buckets[b].setdefault(key_against, 0)

            cand = goals[
                (goals["period"] == t_period)
                & (goals["absElapsedSec"] > t_abs)
                & (goals["absElapsedSec"] <= t_abs + w)
            ]
            if cand.empty:
                continue
            if (cand["eventOwnerTeamId"] == caller).any():
                overall[key_for] += 1
                buckets[b][key_for] += 1
            if (cand["eventOwnerTeamId"] != caller).any():
                overall[key_against] += 1
                buckets[b][key_against] += 1

        # Also: did caller score at any point before end of regulation (after timeout)?
        overall.setdefault("gf_rest_of_game", 0)
        buckets[b].setdefault("gf_rest_of_game", 0)
        later_goals = goals[(goals["absElapsedSec"] > t_abs)]
        if (later_goals["eventOwnerTeamId"] == caller).any():
            overall["gf_rest_of_game"] += 1
            buckets[b]["gf_rest_of_game"] += 1

    # Convert to rates
    out_buckets: Dict[str, Any] = {}
    for b, c in sorted(buckets.items()):
        n = c.get("n", 0)
        stats = {"n": n}
        for w in windows_sec:
            stats[f"gf_{w}"] = asdict(_rate_ci(c.get(f"gf_{w}", 0), n))
            stats[f"ga_{w}"] = asdict(_rate_ci(c.get(f"ga_{w}", 0), n))
        stats["gf_rest_of_game"] = asdict(_rate_ci(c.get("gf_rest_of_game", 0), n))
        out_buckets[b] = stats

    n_all = overall.get("n", 0)
    out_overall = {"n": n_all}
    for w in windows_sec:
        out_overall[f"gf_{w}"] = asdict(_rate_ci(overall.get(f"gf_{w}", 0), n_all))
        out_overall[f"ga_{w}"] = asdict(_rate_ci(overall.get(f"ga_{w}", 0), n_all))
    out_overall["gf_rest_of_game"] = asdict(_rate_ci(overall.get("gf_rest_of_game", 0), n_all))

    return {"diff": diff, "bucketMinutes": bucket_min, "windowsSec": windows_sec, "overall": out_overall, "buckets": out_buckets}


def analyze_goalie_pulls(
    events: pd.DataFrame,
    *,
    diff: int,
    windows_sec: List[int],
    bucket_min: int,
) -> Dict[str, Any]:
    """
    Any empty-net (goalie != 1) segment start while trailing by `diff`.
    """
    home_id = int(events["homeTeamId"].iloc[0])
    away_id = int(events["awayTeamId"].iloc[0])
    goals = events[events["typeDescKey"] == "goal"].copy()

    buckets: Dict[str, Dict[str, int]] = {}
    overall: Dict[str, int] = {"n": 0}

    prev_home_empty = False
    prev_away_empty = False

    for _, r in events.iterrows():
        away_goalie = r["awayGoalie"]
        home_goalie = r["homeGoalie"]
        if pd.isna(away_goalie) or pd.isna(home_goalie):
            continue

        cur_away_empty = int(away_goalie) != 1
        cur_home_empty = int(home_goalie) != 1

        # Determine score pre-event
        pre_home = int(r["preHomeScore"])
        pre_away = int(r["preAwayScore"])

        def handle_pull(team_id: int, rem_game_sec: int, abs_elapsed: int, period: int) -> None:
            overall["n"] += 1
            b = _bucket_label(rem_game_sec, bucket_min)
            buckets.setdefault(b, {})
            buckets[b].setdefault("n", 0)
            buckets[b]["n"] += 1

            for w in windows_sec:
                gf_k = f"gf_{w}"
                ga_k = f"ga_{w}"
                overall.setdefault(gf_k, 0)
                overall.setdefault(ga_k, 0)
                buckets[b].setdefault(gf_k, 0)
                buckets[b].setdefault(ga_k, 0)

                cand = goals[
                    (goals["period"] == period)
                    & (goals["absElapsedSec"] > abs_elapsed)
                    & (goals["absElapsedSec"] <= abs_elapsed + w)
                ]
                if cand.empty:
                    continue
                if (cand["eventOwnerTeamId"] == team_id).any():
                    overall[gf_k] += 1
                    buckets[b][gf_k] += 1
                if (cand["eventOwnerTeamId"] != team_id).any():
                    overall[ga_k] += 1
                    buckets[b][ga_k] += 1

            # rest of regulation
            overall.setdefault("gf_rest_of_game", 0)
            overall.setdefault("ga_rest_of_game", 0)
            buckets[b].setdefault("gf_rest_of_game", 0)
            buckets[b].setdefault("ga_rest_of_game", 0)
            later_goals = goals[(goals["absElapsedSec"] > abs_elapsed)]
            if (later_goals["eventOwnerTeamId"] == team_id).any():
                overall["gf_rest_of_game"] += 1
                buckets[b]["gf_rest_of_game"] += 1
            if (later_goals["eventOwnerTeamId"] != team_id).any():
                overall["ga_rest_of_game"] += 1
                buckets[b]["ga_rest_of_game"] += 1

        # Away pull start
        if cur_away_empty and not prev_away_empty:
            trailing = pre_home - pre_away
            if trailing == diff:
                handle_pull(
                    away_id,
                    int(r["remGameSec"]),
                    int(r["absElapsedSec"]),
                    int(r["period"]),
                )

        # Home pull start
        if cur_home_empty and not prev_home_empty:
            trailing = pre_away - pre_home
            if trailing == diff:
                handle_pull(
                    home_id,
                    int(r["remGameSec"]),
                    int(r["absElapsedSec"]),
                    int(r["period"]),
                )

        prev_away_empty = cur_away_empty
        prev_home_empty = cur_home_empty

    # Convert to rates
    out_buckets: Dict[str, Any] = {}
    for b, c in sorted(buckets.items()):
        n = c.get("n", 0)
        stats = {"n": n}
        for w in windows_sec:
            stats[f"gf_{w}"] = asdict(_rate_ci(c.get(f"gf_{w}", 0), n))
            stats[f"ga_{w}"] = asdict(_rate_ci(c.get(f"ga_{w}", 0), n))
        stats["gf_rest_of_game"] = asdict(_rate_ci(c.get("gf_rest_of_game", 0), n))
        stats["ga_rest_of_game"] = asdict(_rate_ci(c.get("ga_rest_of_game", 0), n))
        out_buckets[b] = stats

    n_all = overall.get("n", 0)
    out_overall = {"n": n_all}
    for w in windows_sec:
        out_overall[f"gf_{w}"] = asdict(_rate_ci(overall.get(f"gf_{w}", 0), n_all))
        out_overall[f"ga_{w}"] = asdict(_rate_ci(overall.get(f"ga_{w}", 0), n_all))
    out_overall["gf_rest_of_game"] = asdict(_rate_ci(overall.get("gf_rest_of_game", 0), n_all))
    out_overall["ga_rest_of_game"] = asdict(_rate_ci(overall.get("ga_rest_of_game", 0), n_all))

    return {"diff": diff, "bucketMinutes": bucket_min, "windowsSec": windows_sec, "overall": out_overall, "buckets": out_buckets}


def default_season_start_years() -> List[int]:
    current_start = date.today().year - 1
    return [current_start - 2, current_start - 1, current_start]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--max-games", type=int, default=0)
    ap.add_argument(
        "--season-start-years",
        type=int,
        nargs="*",
        default=default_season_start_years(),
    )
    ap.add_argument("--cache-dir", type=Path, default=default_cache_dir())
    ap.add_argument(
        "--windows-sec",
        type=int,
        nargs="*",
        default=[60, 120],
        help="Outcome windows in seconds (default: 60 120).",
    )
    ap.add_argument(
        "--bucket-min",
        type=int,
        default=int(os.getenv("BUCKET_MIN", "2")),
        help="Bucket size in minutes of game time remaining.",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("data") / "timeout_goalie_pull_optimization.json",
    )
    args = ap.parse_args()

    args.cache_dir.mkdir(parents=True, exist_ok=True)
    windows = list(args.windows_sec)

    # Aggregate across games by concatenating per-game results (by summing counts).
    # We'll just re-run per-game analyzers and merge bucket counts in Python dicts.
    def merge_rate_ci_dict(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        # Not used for final; we keep raw counts elsewhere.
        out = dict(a)
        out.update(b)
        return out

    # Raw count accumulators (we'll reuse the per-game outputs but sum their k/n).
    def sum_bucket_stats(dst: Dict[str, Any], src: Dict[str, Any]) -> None:
        for bucket, stats in src.items():
            dst.setdefault(bucket, {"n": 0})
            dst[bucket]["n"] += int(stats.get("n", 0))
            for key, val in stats.items():
                if key == "n":
                    continue
                # val is RateCI dict
                if isinstance(val, dict) and "k" in val and "n" in val:
                    dst[bucket].setdefault(key, {"k": 0, "n": 0})
                    dst[bucket][key]["k"] += int(val.get("k", 0))
                    dst[bucket][key]["n"] += int(val.get("n", 0))

    def recompute_rates(buckets_raw: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for b, s in sorted(buckets_raw.items()):
            n = int(s.get("n", 0))
            out[b] = {"n": n}
            for k, v in s.items():
                if k == "n":
                    continue
                if isinstance(v, dict) and "k" in v:
                    out[b][k] = asdict(_rate_ci(int(v["k"]), n))
        return out

    def sum_overall(dst: Dict[str, Any], src: Dict[str, Any]) -> None:
        dst["n"] = dst.get("n", 0) + int(src.get("n", 0))
        for k, v in src.items():
            if k == "n":
                continue
            if isinstance(v, dict) and "k" in v and "n" in v:
                dst.setdefault(k, {"k": 0, "n": 0})
                dst[k]["k"] += int(v.get("k", 0))
                dst[k]["n"] += int(v.get("n", 0))

    def recompute_overall(overall_raw: Dict[str, Any]) -> Dict[str, Any]:
        n = int(overall_raw.get("n", 0))
        out = {"n": n}
        for k, v in overall_raw.items():
            if k == "n":
                continue
            if isinstance(v, dict) and "k" in v:
                out[k] = asdict(_rate_ci(int(v["k"]), n))
        return out

    # storage for each diff and action type
    results: Dict[str, Any] = {
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "seasonStartYears": list(args.season_start_years),
        "windowsSec": windows,
        "bucketMinutes": int(args.bucket_min),
        "timeout": {},
        "goaliePull": {},
    }

    for diff in (1, 2):
        timeout_buckets_raw: Dict[str, Any] = {}
        pull_buckets_raw: Dict[str, Any] = {}
        timeout_overall_raw: Dict[str, Any] = {"n": 0}
        pull_overall_raw: Dict[str, Any] = {"n": 0}

        for y in list(args.season_start_years):
            game_ids = list(iter_regular_season_game_ids(y, cache_dir=args.cache_dir))
            if args.max_games and args.max_games > 0:
                game_ids = game_ids[: args.max_games]

            for gid in game_ids:
                pbp = fetch_pbp(gid, cache_dir=args.cache_dir, force=args.force)
                ev = build_events(pbp)
                if ev.empty:
                    continue
                t_out = analyze_timeouts(ev, diff=diff, windows_sec=windows, bucket_min=int(args.bucket_min))
                p_out = analyze_goalie_pulls(ev, diff=diff, windows_sec=windows, bucket_min=int(args.bucket_min))

                # Sum buckets/overall using k/n from the already computed rate dicts.
                sum_bucket_stats(timeout_buckets_raw, t_out["buckets"])
                sum_bucket_stats(pull_buckets_raw, p_out["buckets"])
                sum_overall(timeout_overall_raw, t_out["overall"])
                sum_overall(pull_overall_raw, p_out["overall"])

        results["timeout"][str(diff)] = {
            "diff": diff,
            "overall": recompute_overall(timeout_overall_raw),
            "buckets": recompute_rates(timeout_buckets_raw),
        }
        results["goaliePull"][str(diff)] = {
            "diff": diff,
            "overall": recompute_overall(pull_overall_raw),
            "buckets": recompute_rates(pull_buckets_raw),
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

