"""
Derive playoff participation and series-win depth from NHL api-web playoff-bracket JSON.

Bracket shape: https://api-web.nhle.com/v1/playoff-bracket/{year}
where {year} is the calendar year the Cup is awarded (e.g. season 20222023 -> 2023).
"""

from __future__ import annotations

from typing import Dict, Optional, Set, Tuple


def _team_abbrev(team: dict) -> str:
    if not isinstance(team, dict):
        return ""
    return str(team.get("abbrev") or "").strip().upper()


def series_winner_abbrev(series: dict) -> Optional[str]:
    """Return winning team abbrev, or None if undecided."""
    if not isinstance(series, dict):
        return None
    win_id = series.get("winningTeamId")
    if win_id is not None:
        for key in ("topSeedTeam", "bottomSeedTeam"):
            t = series.get(key) or {}
            if t.get("id") == win_id:
                ab = _team_abbrev(t)
                return ab or None
    try:
        w1 = int(series.get("topSeedWins"))
        w2 = int(series.get("bottomSeedWins"))
    except Exception:
        return None
    t1 = _team_abbrev(series.get("topSeedTeam") or {})
    t2 = _team_abbrev(series.get("bottomSeedTeam") or {})
    if not t1 or not t2:
        return None
    if w1 >= 4:
        return t1
    if w2 >= 4:
        return t2
    return None


def playoff_outcomes_from_bracket(bracket: dict) -> Tuple[Set[str], Dict[str, int]]:
    """
    Returns:
      playoff_teams: team abbrevs that appear in any playoff series (round >= 1)
      series_wins: per-team count of best-of-7 series won (0..4 for typical format)
    """
    playoff_teams: Set[str] = set()
    series_wins: Dict[str, int] = {}

    series_list = bracket.get("series") if isinstance(bracket, dict) else None
    if not isinstance(series_list, list):
        return playoff_teams, series_wins

    for s in series_list:
        if not isinstance(s, dict):
            continue
        rnd = s.get("playoffRound")
        try:
            rnd = int(rnd) if rnd is not None else None
        except Exception:
            rnd = None
        if rnd is None or rnd < 1:
            continue

        t1 = _team_abbrev(s.get("topSeedTeam") or {})
        t2 = _team_abbrev(s.get("bottomSeedTeam") or {})
        if t1:
            playoff_teams.add(t1)
        if t2:
            playoff_teams.add(t2)

        wabbr = series_winner_abbrev(s)
        if wabbr:
            series_wins[wabbr] = series_wins.get(wabbr, 0) + 1

    return playoff_teams, series_wins


def labels_for_standings_team(
    team: str,
    playoff_teams: Set[str],
    series_wins: Dict[str, int],
    cup_winner: Optional[str],
) -> Dict[str, int]:
    """Binary / ordinal labels aligned with TeamSeasonRow fields."""
    ab = str(team).strip().upper()
    sw = int(series_wins.get(ab, 0))
    made = 1 if ab in playoff_teams else 0
    cup = 1 if (cup_winner and ab == str(cup_winner).strip().upper()) or sw >= 4 else 0
    return {
        "made_playoffs": made,
        "playoff_series_wins": sw if made else 0,
        "won_round_1": 1 if sw >= 1 else 0,
        "won_round_2": 1 if sw >= 2 else 0,
        # Won conference finals round (Stanley Cup Finalist); champion has sw == 4
        "won_conference": 1 if sw >= 3 else 0,
        "won_cup": cup,
    }
