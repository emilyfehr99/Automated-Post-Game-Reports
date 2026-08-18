from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


_DEFAULT_SCHEDULE_PATH = Path("data/season_2025_2026_schedule.json")


def _as_int(x: Any) -> Optional[int]:
    try:
        if x is None:
            return None
        return int(str(x).strip())
    except Exception:
        return None


def _team_abbrev(team_obj: Any) -> Optional[str]:
    if isinstance(team_obj, dict):
        return team_obj.get("abbrev") or team_obj.get("triCode")
    return None


@lru_cache(maxsize=2)
def _load_schedule(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
    except Exception:
        return []
    return data if isinstance(data, list) else []


@lru_cache(maxsize=2048)
def is_playoff_game(game_id: Any, *, schedule_path: Path = _DEFAULT_SCHEDULE_PATH) -> bool:
    """
    Best-effort playoff detection.
    - Prefer schedule gameType == 3 when the game exists in schedule JSON.
    - Fall back to NHL id prefix 202503* heuristic.
    """
    gid = _as_int(game_id)
    if gid is None:
        return False
    # Fast heuristic: NHL playoff ids in this repo use 202503xxxx
    if str(gid).startswith("202503"):
        return True
    games = _load_schedule(str(schedule_path))
    for g in games:
        try:
            if _as_int(g.get("id")) != gid:
                continue
            gt = _as_int(g.get("gameType"))
            return bool(gt == 3)
        except Exception:
            continue
    return False


@lru_cache(maxsize=4096)
def series_context_for_game(
    game_id: Any,
    away_team: str,
    home_team: str,
    *,
    schedule_path: Path = _DEFAULT_SCHEDULE_PATH,
) -> Dict[str, Any]:
    """
    Compute series score context (wins-to-date) using the cached schedule JSON.
    Returns JSON-serializable dict, keyed to the *current* game's home/away teams.
    """
    gid = _as_int(game_id)
    if gid is None or not away_team or not home_team:
        return {}

    games = _load_schedule(str(schedule_path))
    # Identify series by the unordered pair of teams (robust to venue swaps)
    pair = tuple(sorted([away_team, home_team]))

    series_games: List[Dict[str, Any]] = []
    for g in games:
        try:
            if _as_int(g.get("gameType")) != 3:
                continue
            a = _team_abbrev((g.get("awayTeam") or {}))
            h = _team_abbrev((g.get("homeTeam") or {}))
            if not a or not h:
                continue
            if tuple(sorted([a, h])) != pair:
                continue
            series_games.append(g)
        except Exception:
            continue

    # Sort by startTimeUTC (then id) so we only count games strictly before current one.
    def _sort_key(g: Dict[str, Any]) -> Tuple[str, int]:
        return (str(g.get("startTimeUTC") or ""), _as_int(g.get("id")) or -1)

    series_games.sort(key=_sort_key)

    wins: Dict[str, int] = {away_team: 0, home_team: 0}
    game_num = 1

    for g in series_games:
        g_id = _as_int(g.get("id"))
        if g_id == gid:
            break
        state = str(g.get("gameState") or "").upper()
        score = g.get("score") or {}
        a_s = score.get("awayScore")
        h_s = score.get("homeScore")
        # Only count completed games with a score.
        if state not in ("FINAL", "OFF", "OFFICIAL") and (a_s is None or h_s is None):
            continue
        try:
            a_i = int(a_s)
            h_i = int(h_s)
        except Exception:
            continue
        a_team = _team_abbrev((g.get("awayTeam") or {}))
        h_team = _team_abbrev((g.get("homeTeam") or {}))
        if not a_team or not h_team:
            continue
        if a_i > h_i:
            wins[a_team] = wins.get(a_team, 0) + 1
        elif h_i > a_i:
            wins[h_team] = wins.get(h_team, 0) + 1
        game_num += 1

    away_w = int(wins.get(away_team, 0))
    home_w = int(wins.get(home_team, 0))
    elimination_away = bool(home_w == 3 and away_w < 3)
    elimination_home = bool(away_w == 3 and home_w < 3)

    return {
        "series_away_wins": away_w,
        "series_home_wins": home_w,
        "series_game_number": int(game_num),
        "series_score_diff_home_minus_away": int(home_w - away_w),
        "is_elimination_game": bool(elimination_away or elimination_home),
        "elimination_game_for_away": bool(elimination_away),
        "elimination_game_for_home": bool(elimination_home),
    }

