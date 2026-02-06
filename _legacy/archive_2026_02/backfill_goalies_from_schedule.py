#!/usr/bin/env python3
from datetime import datetime, timedelta
import pytz
from nhl_api_client import NHLAPIClient
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from pdf_report_generator import PostGameReportGenerator


def in_current_season(date_str: str) -> bool:
    # Heuristic: current season starts Oct 1 of current year
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
    except Exception:
        return False
    start = datetime(dt.year, 10, 1)
    if dt.month < 7:
        # Jan-Jun are part of the same season year that started previous Oct
        start = datetime(dt.year - 1, 10, 1)
    return dt >= start


def main(days_back: int = 30):
    api = NHLAPIClient()
    model = ImprovedSelfLearningModelV2()
    gen = PostGameReportGenerator()
    ct = pytz.timezone('US/Central')
    now_ct = datetime.now(ct)
    updated = 0

    for d in range(1, days_back + 1):
        date_str = (now_ct - timedelta(days=d)).strftime('%Y-%m-%d')
        if not in_current_season(date_str):
            continue
        sched = api.get_game_schedule(date_str)
        if not sched or 'gameWeek' not in sched:
            continue
        for day in sched['gameWeek']:
            if day.get('date') != date_str:
                continue
            for g in day.get('games', []):
                gid = str(g.get('id'))
                away = (g.get('awayTeam', {}) or {}).get('abbrev')
                home = (g.get('homeTeam', {}) or {}).get('abbrev')
                if not away or not home:
                    continue
                try:
                    box = api.get_game_boxscore(gid)
                    game_data = api.get_game_center(gid)
                    if not box or not game_data:
                        continue
                    boxscore = {'awayTeam': box.get('awayTeam', {}), 'homeTeam': box.get('homeTeam', {})}

                    # Build id->(name, teamAbbrev) map from PBP rosterSpots (most reliable)
                    pbp = game_data.get('play_by_play', {})
                    roster = pbp.get('rosterSpots', [])
                    id_to = {}
                    away_id = (boxscore.get('awayTeam') or {}).get('id')
                    home_id = (boxscore.get('homeTeam') or {}).get('id')
                    for r in roster:
                        try:
                            pid = str(r.get('playerId') or r.get('id') or r.get('personId'))
                            # Build name from firstName/lastName dicts
                            name = None
                            if r.get('person'):
                                name = r['person'].get('fullName')
                            if not name:
                                fn = r.get('firstName', {}).get('default') if isinstance(r.get('firstName'), dict) else None
                                ln = r.get('lastName', {}).get('default') if isinstance(r.get('lastName'), dict) else None
                                if fn or ln:
                                    name = f"{fn or ''} {ln or ''}".strip()
                            # Get team from rosterSpot teamId -> match to away/home team id
                            team_id = r.get('teamId')
                            team_abbr = None
                            if team_id == away_id:
                                team_abbr = away
                            elif team_id == home_id:
                                team_abbr = home
                            if pid and name and team_abbr:
                                id_to[pid] = (name, team_abbr)
                        except Exception:
                            continue

                    # Extract starters from PBP (goalie in net at start)
                    # Find first goalie ID per team from plays
                    away_goalie_id = None
                    home_goalie_id = None
                    plays = pbp.get('plays') or []
                    for ev in plays[:50]:
                        details = ev.get('details') or {}
                        gid = details.get('goalieInNetId') or details.get('goalieId')
                        if gid:
                            gid_str = str(gid)
                            # Check which team this goalie belongs to via id_to mapping
                            if gid_str in id_to:
                                name, team = id_to[gid_str]
                                if team == away and away_goalie_id is None:
                                    away_goalie_id = (gid_str, name)
                                elif team == home and home_goalie_id is None:
                                    home_goalie_id = (gid_str, name)
                        # Stop once we have both
                        if away_goalie_id and home_goalie_id:
                            break
                    
                    def extract_from_pbp(side_key: str):
                        if side_key == 'awayTeam':
                            if away_goalie_id:
                                return (away_goalie_id[1], away)
                        else:
                            if home_goalie_id:
                                return (home_goalie_id[1], home)
                        return None

                    def extract_from_box(box_team):
                        starters = box_team.get('goalies') or box_team.get('starters')
                        if starters and isinstance(starters, list):
                            for ga in starters:
                                nm = (ga.get('name') or ga.get('firstLastName') or ga.get('playerName')) if isinstance(ga, dict) else None
                                if nm:
                                    return nm
                        players = box_team.get('players') or []
                        it = players.values() if isinstance(players, dict) else players
                        # Highest TOI fallback
                        best = None
                        best_toi = -1
                        for p in it:
                            try:
                                pos = p.get('positionCode') or p.get('position', {}).get('code')
                                name = p.get('name') or p.get('firstLastName') or p.get('playerName')
                                if (pos == 'G' or pos == 'GOALIE') and name:
                                    toi = p.get('toi') or p.get('timeOnIce') or '0:00'
                                    # Convert MM:SS to minutes*60+seconds integer for comparison
                                    s = str(toi)
                                    parts = s.split(':')
                                    val = 0
                                    try:
                                        if len(parts) == 2:
                                            val = int(parts[0]) * 60 + int(parts[1])
                                        elif len(parts) == 3:
                                            val = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                                    except Exception:
                                        val = 0
                                    if val > best_toi:
                                        best_toi = val
                                        best = name
                            except Exception:
                                continue
                        return best

                    away_g = extract_from_pbp('awayTeam')
                    home_g = extract_from_pbp('homeTeam')
                    # If PBP failed, fallback to box teams with highest TOI (name only, team from schedule)
                    away_fallback_name = extract_from_box(boxscore['awayTeam'])
                    home_fallback_name = extract_from_box(boxscore['homeTeam'])
                    away_goalie = away_g or ( (away_fallback_name, away) if away_fallback_name else None )
                    home_goalie = home_g or ( (home_fallback_name, home) if home_fallback_name else None )
                    # Update goalie stats via xG and goals
                    away_xg, home_xg = gen._calculate_xg_from_plays(game_data)
                    away_goals = int((box.get('awayTeam') or {}).get('score', 0))
                    home_goals = int((box.get('homeTeam') or {}).get('score', 0))
                    gs = model.model_data.setdefault('goalie_stats', {})
                    if away_goalie:
                        if isinstance(away_goalie, tuple):
                            away_name, away_team_abbr = away_goalie
                        else:
                            away_name, away_team_abbr = away_goalie, away
                        ag = gs.setdefault(away_name, {'games': 0, 'xga_sum': 0.0, 'ga_sum': 0.0})
                        ag['games'] += 1
                        ag['xga_sum'] += float(home_xg or 0.0)
                        ag['ga_sum'] += float(home_goals or 0.0)
                        model.goalie_history.setdefault((away_team_abbr or away).upper(), []).append((date_str, away_name))
                    if home_goalie:
                        if isinstance(home_goalie, tuple):
                            home_name, home_team_abbr = home_goalie
                        else:
                            home_name, home_team_abbr = home_goalie, home
                        hg = gs.setdefault(home_name, {'games': 0, 'xga_sum': 0.0, 'ga_sum': 0.0})
                        hg['games'] += 1
                        hg['xga_sum'] += float(away_xg or 0.0)
                        hg['ga_sum'] += float(away_goals or 0.0)
                        model.goalie_history.setdefault((home_team_abbr or home).upper(), []).append((date_str, home_name))
                    updated += 1
                except Exception:
                    continue

    for t in model.goalie_history:
        model.goalie_history[t].sort(key=lambda x: x[0])
    model.save_model_data()
    print('Schedule-based goalie backfill updates:', updated)
    print('Teams with goalie_history entries:', len(model.goalie_history or {}))


if __name__ == '__main__':
    main(30)


