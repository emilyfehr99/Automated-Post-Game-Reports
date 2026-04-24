from __future__ import annotations

import argparse
import json
import math
import os
import time
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
import requests


NHL_API_BASE = "https://api-web.nhle.com/v1"


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


def is_5v5_goalie_in_net(code: Optional[str]) -> bool:
    sit = parse_situation_code(code)
    if sit is None:
        return False
    return (
        sit.away_goalie == 1
        and sit.home_goalie == 1
        and sit.away_skaters == 5
        and sit.home_skaters == 5
    )


def pp_team_id_from_situation(
    code: Optional[str], away_team_id: int, home_team_id: int
) -> Optional[int]:
    sit = parse_situation_code(code)
    if sit is None:
        return None

    # Only treat as PP when both goalies are in net (exclude empty-net states).
    if sit.away_goalie != 1 or sit.home_goalie != 1:
        return None

    if sit.away_skaters > sit.home_skaters:
        return away_team_id
    if sit.home_skaters > sit.away_skaters:
        return home_team_id
    return None


def mmss_to_elapsed_seconds(mmss: str) -> int:
    mm, ss = mmss.split(":")
    return int(mm) * 60 + int(ss)


def is_tv_timeout_stoppage(play: Dict[str, Any]) -> bool:
    if play.get("typeDescKey") != "stoppage":
        return False
    details = play.get("details") or {}
    secondary = str(details.get("secondaryReason") or "").strip().lower()
    if secondary == "tv-timeout":
        return True
    hay = " ".join(
        [
            str(details.get("reason") or ""),
            str(details.get("secondaryReason") or ""),
            str(play.get("descKey") or ""),
        ]
    ).lower()
    return ("tv" in hay) and ("timeout" in hay)


def get_json(url: str, retries: int = 5, timeout_s: int = 30) -> Dict[str, Any]:
    last_exc: Optional[Exception] = None
    headers = {
        "User-Agent": "automated-post-game-reports tv-timeout-pp-study",
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
    return Path(".cache") / "nhl_tv_timeout_pp"


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
                if g.get("gameType") == 2:  # 2 == regular season
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


def pbp_to_events_df(pbp: Dict[str, Any]) -> pd.DataFrame:
    away_id = int(pbp["awayTeam"]["id"])
    home_id = int(pbp["homeTeam"]["id"])

    rows: List[Dict[str, Any]] = []
    for p in pbp.get("plays", []):
        period = int(p["periodDescriptor"]["number"])
        time_in_period = str(p["timeInPeriod"])
        elapsed = mmss_to_elapsed_seconds(time_in_period)
        abs_elapsed = (period - 1) * 20 * 60 + elapsed

        details = p.get("details") or {}
        owner = details.get("eventOwnerTeamId")
        owner_id = int(owner) if owner is not None else None

        sit_code = p.get("situationCode")
        pp_team_id = pp_team_id_from_situation(sit_code, away_id, home_id)
        is5v5 = is_5v5_goalie_in_net(sit_code)

        rows.append(
            {
                "gameId": int(pbp["id"]),
                "eventId": int(p["eventId"]),
                "sortOrder": int(p.get("sortOrder") or 0),
                "period": period,
                "absElapsedSec": abs_elapsed,
                "typeDescKey": p.get("typeDescKey"),
                "situationCode": sit_code,
                "is5v5": is5v5,
                "ppTeamId": pp_team_id,
                "eventOwnerTeamId": owner_id,
                "zoneCode": details.get("zoneCode"),
                "tvTimeout": is_tv_timeout_stoppage(p),
            }
        )

    df = pd.DataFrame.from_records(rows)
    df.sort_values(["sortOrder", "eventId"], inplace=True, ignore_index=True)
    return df


def tag_faceoff_oz_5v5(df: pd.DataFrame) -> pd.Series:
    return (
        (df["typeDescKey"] == "faceoff")
        & (df["is5v5"] == True)  # noqa: E712
        & (df["zoneCode"] == "O")
        & (df["eventOwnerTeamId"].notna())
    )


def stoppage_to_pp_goal_rate(events: pd.DataFrame, tv_only: bool, window_sec: int) -> RateCI:
    stoppages = events[
        (events["typeDescKey"] == "stoppage")
        & (events["ppTeamId"].notna())
        & (events["tvTimeout"] == bool(tv_only))
    ]
    goals = events[events["typeDescKey"] == "goal"]

    k = 0
    for _, s in stoppages.iterrows():
        s_abs = int(s["absElapsedSec"])
        s_period = int(s["period"])
        pp_team = int(s["ppTeamId"])
        cand = goals[
            (goals["period"] == s_period)
            & (goals["absElapsedSec"] > s_abs)
            & (goals["absElapsedSec"] <= s_abs + window_sec)
            & (goals["eventOwnerTeamId"] == pp_team)
            & (goals["ppTeamId"] == pp_team)
        ]
        if len(cand) > 0:
            k += 1

    n = int(len(stoppages))
    rate = k / n if n else float("nan")
    lo, hi = wilson_ci(k, n) if n else (float("nan"), float("nan"))
    return RateCI(n=n, k=k, rate=rate, ci_low=lo, ci_high=hi)


def oz_faceoff_5v5_to_goal_rate(events: pd.DataFrame, tv_before: bool, window_sec: int) -> RateCI:
    oz_faceoffs = events[tag_faceoff_oz_5v5(events)]
    tv_stoppages = events[(events["typeDescKey"] == "stoppage") & (events["tvTimeout"])]
    goals_5v5 = events[(events["typeDescKey"] == "goal") & (events["is5v5"] == True)]  # noqa: E712

    k = 0
    n = 0
    for _, f in oz_faceoffs.iterrows():
        f_abs = int(f["absElapsedSec"])
        f_period = int(f["period"])
        team_id = int(f["eventOwnerTeamId"])

        tv_prior = tv_stoppages[
            (tv_stoppages["period"] == f_period)
            & (tv_stoppages["absElapsedSec"] >= f_abs - window_sec)
            & (tv_stoppages["absElapsedSec"] < f_abs)
        ]
        has_tv = len(tv_prior) > 0
        if bool(tv_before) != has_tv:
            continue

        n += 1
        cand_goals = goals_5v5[
            (goals_5v5["period"] == f_period)
            & (goals_5v5["absElapsedSec"] > f_abs)
            & (goals_5v5["absElapsedSec"] <= f_abs + window_sec)
            & (goals_5v5["eventOwnerTeamId"] == team_id)
        ]
        if len(cand_goals) > 0:
            k += 1

    rate = k / n if n else float("nan")
    lo, hi = wilson_ci(k, n) if n else (float("nan"), float("nan"))
    return RateCI(n=n, k=k, rate=rate, ci_low=lo, ci_high=hi)


def format_rate(label: str, r: RateCI) -> str:
    if r.n == 0:
        return f"{label}: n=0"
    return f"{label}: {r.k}/{r.n} = {r.rate:.3%} (95% CI {r.ci_low:.3%}–{r.ci_high:.3%})"


def default_season_start_years() -> List[int]:
    current_start = date.today().year - 1
    return [current_start - 2, current_start - 1, current_start]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window-sec", type=int, default=int(os.getenv("WINDOW_SEC", "60")))
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
        "--out",
        type=Path,
        default=Path("data") / "tv_timeout_pp_summary.json",
    )
    args = ap.parse_args()

    args.cache_dir.mkdir(parents=True, exist_ok=True)

    total_pp_tv = RateCI(0, 0, float("nan"), float("nan"), float("nan"))
    total_pp_non = RateCI(0, 0, float("nan"), float("nan"), float("nan"))
    total_oz_tv = RateCI(0, 0, float("nan"), float("nan"), float("nan"))
    total_oz_non = RateCI(0, 0, float("nan"), float("nan"), float("nan"))

    def add(a: RateCI, b: RateCI) -> RateCI:
        n = a.n + b.n
        k = a.k + b.k
        rate = k / n if n else float("nan")
        lo, hi = wilson_ci(k, n) if n else (float("nan"), float("nan"))
        return RateCI(n=n, k=k, rate=rate, ci_low=lo, ci_high=hi)

    for y in list(args.season_start_years):
        game_ids = list(iter_regular_season_game_ids(y, cache_dir=args.cache_dir))
        if args.max_games and args.max_games > 0:
            game_ids = game_ids[: args.max_games]
        for gid in game_ids:
            pbp = fetch_pbp(gid, cache_dir=args.cache_dir, force=args.force)
            events = pbp_to_events_df(pbp)

            pp_tv = stoppage_to_pp_goal_rate(events, tv_only=True, window_sec=args.window_sec)
            pp_non = stoppage_to_pp_goal_rate(events, tv_only=False, window_sec=args.window_sec)
            oz_tv = oz_faceoff_5v5_to_goal_rate(events, tv_before=True, window_sec=args.window_sec)
            oz_non = oz_faceoff_5v5_to_goal_rate(events, tv_before=False, window_sec=args.window_sec)

            total_pp_tv = add(total_pp_tv, pp_tv)
            total_pp_non = add(total_pp_non, pp_non)
            total_oz_tv = add(total_oz_tv, oz_tv)
            total_oz_non = add(total_oz_non, oz_non)

    lift_pp = (
        (total_pp_tv.rate / total_pp_non.rate)
        if (total_pp_non.n and total_pp_non.k > 0)
        else float("nan")
    )
    lift_oz = (
        (total_oz_tv.rate / total_oz_non.rate)
        if (total_oz_non.n and total_oz_non.k > 0)
        else float("nan")
    )

    summary = {
        "generatedAtUtc": datetime.utcnow().isoformat() + "Z",
        "seasonStartYears": list(args.season_start_years),
        "windowSec": int(args.window_sec),
        "ppGoalWithinWindowAfterTvTimeoutStoppage_duringPP": asdict(total_pp_tv),
        "ppGoalWithinWindowAfterNonTvStoppage_duringPP": asdict(total_pp_non),
        "lift_tv_vs_non_tv_pp_goal_rate": lift_pp,
        "goalWithinWindowAfter5v5OZFaceoff_tvTimeoutBefore": asdict(total_oz_tv),
        "goalWithinWindowAfter5v5OZFaceoff_noTvTimeoutBefore": asdict(total_oz_non),
        "lift_tv_vs_non_tv_oz_goal_rate": lift_oz,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(format_rate("PP goal within window after TV-timeout stoppage (during PP)", total_pp_tv))
    print(format_rate("PP goal within window after non-TV stoppage (during PP)", total_pp_non))
    print(f"Lift (TV/non-TV) PP goal rate: {lift_pp:.3f}" if total_pp_non.n else "Lift PP: n/a")
    print(format_rate("5v5 OZ faceoff -> goal by OZ team (TV timeout within window before faceoff)", total_oz_tv))
    print(
        format_rate(
            "5v5 OZ faceoff -> goal by OZ team (no TV timeout within window before faceoff)",
            total_oz_non,
        )
    )
    print(f"Lift (TV/non-TV) 5v5 OZ faceoff goal rate: {lift_oz:.3f}" if total_oz_non.n else "Lift OZ: n/a")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

