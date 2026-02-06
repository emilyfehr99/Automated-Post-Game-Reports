#!/usr/bin/env python3
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from pdf_report_generator import PostGameReportGenerator
from nhl_api_client import NHLAPIClient


def extract_starters(boxscore_team):
    # Prefer explicit goalies/starters if present
    starters = boxscore_team.get('goalies') or boxscore_team.get('starters')
    if starters and isinstance(starters, list):
        for g in starters:
            nm = (g.get('name') or g.get('firstLastName') or g.get('playerName')) if isinstance(g, dict) else None
            if nm:
                return nm
    # Fallback to players list
    players = boxscore_team.get('players') or []
    if isinstance(players, dict):
        players_iter = players.values()
    else:
        players_iter = players
    best = None
    for p in players_iter:
        try:
            pos = p.get('positionCode') or p.get('position', {}).get('code')
            starter = p.get('starter') or p.get('starting') or False
            name = p.get('name') or p.get('firstLastName') or p.get('playerName')
            if (pos == 'G' or pos == 'GOALIE') and name:
                best = name
                if starter:
                    return name
        except Exception:
            continue
    return best


def map_game_id(api: NHLAPIClient, date_str: str, away: str, home: str):
    try:
        sched = api.get_game_schedule(date_str)
        if not sched or 'gameWeek' not in sched:
            return None
        for day in sched['gameWeek']:
            if day.get('date') != date_str:
                continue
            for g in day.get('games', []):
                a = g.get('awayTeam', {}).get('abbrev')
                h = g.get('homeTeam', {}).get('abbrev')
                if a == away and h == home:
                    return str(g.get('id'))
    except Exception:
        return None
    return None


def main(max_games=400):
    model = ImprovedSelfLearningModelV2()
    api = NHLAPIClient()
    gen = PostGameReportGenerator()
    preds = [p for p in model.model_data.get('predictions', []) if p.get('actual_winner')]
    if not preds:
        print('No predictions with game_id to backfill.')
        return
    preds.sort(key=lambda p: p.get('date',''))
    preds = preds[-max_games:]
    updated = 0
    for p in preds:
        away_abbr = (p.get('away_team') or '').upper()
        home_abbr = (p.get('home_team') or '').upper()
        date_str = p.get('date')
        gid = p.get('game_id')
        gid = str(gid) if gid else map_game_id(api, date_str, away_abbr, home_abbr)
        try:
            game_data = api.get_game_center(gid)
            if not game_data:
                continue
            box = api.get_game_boxscore(gid)
            if not box:
                continue
            boxscore = {'awayTeam': box.get('awayTeam', {}), 'homeTeam': box.get('homeTeam', {})}
            away_team = away_abbr
            home_team = home_abbr
            away_goalie = extract_starters(boxscore['awayTeam'])
            home_goalie = extract_starters(boxscore['homeTeam'])
            away_xg, home_xg = gen._calculate_xg_from_plays(game_data)
            away_goals = int(p.get('actual_away_score') or 0)
            home_goals = int(p.get('actual_home_score') or 0)
            # Update goalie_stats
            gs = model.model_data.setdefault('goalie_stats', {})
            if away_goalie:
                ag = gs.setdefault(away_goalie, {'games': 0, 'xga_sum': 0.0, 'ga_sum': 0.0})
                ag['games'] += 1
                ag['xga_sum'] += float(home_xg)
                ag['ga_sum'] += float(home_goals)
                # History
                model.goalie_history.setdefault(away_team, []).append((p.get('date'), away_goalie))
            if home_goalie:
                hg = gs.setdefault(home_goalie, {'games': 0, 'xga_sum': 0.0, 'ga_sum': 0.0})
                hg['games'] += 1
                hg['xga_sum'] += float(away_xg)
                hg['ga_sum'] += float(away_goals)
                model.goalie_history.setdefault(home_team, []).append((p.get('date'), home_goalie))
            updated += 1
        except Exception as e:
            continue
    # Sort histories
    for t in model.goalie_history:
        model.goalie_history[t].sort(key=lambda x: x[0])
    model.save_model_data()
    print('Backfilled goalie starters for games:', updated)


if __name__ == '__main__':
    main()


