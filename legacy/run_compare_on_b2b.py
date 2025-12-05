#!/usr/bin/env python3
from datetime import datetime, timedelta
import pytz
from nhl_api_client import NHLAPIClient
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2


def get_games_on_date(api: NHLAPIClient, date_str: str):
    sched = api.get_game_schedule(date_str)
    games = []
    if sched and 'gameWeek' in sched:
        for day in sched['gameWeek']:
            if day.get('date') == date_str:
                for g in day.get('games', []):
                    games.append({
                        'id': str(g.get('id')),
                        'away': g.get('awayTeam', {}).get('abbrev'),
                        'home': g.get('homeTeam', {}).get('abbrev'),
                    })
    return games


def main():
    api = NHLAPIClient()
    ct = pytz.timezone('US/Central')
    now_ct = datetime.now(ct)
    date_str = (now_ct - timedelta(days=2)).strftime('%Y-%m-%d')  # try two days ago
    prev_str = (now_ct - timedelta(days=3)).strftime('%Y-%m-%d')

    games = get_games_on_date(api, date_str)
    prev_games = get_games_on_date(api, prev_str)
    prev_teams = set()
    for g in prev_games:
        if g['away']:
            prev_teams.add(g['away'])
        if g['home']:
            prev_teams.add(g['home'])

    b2b_candidates = [g for g in games if g['away'] in prev_teams or g['home'] in prev_teams]
    if not b2b_candidates:
        print('No B2B candidates found on', date_str)
        return

    model = ImprovedSelfLearningModelV2()
    model.deterministic = True
    # BEFORE
    model.feature_flags['use_per_goalie_gsax'] = False
    model.feature_flags['use_rest_bucket_adj'] = False

    # AFTER
    model_after = ImprovedSelfLearningModelV2()
    model_after.deterministic = True
    model_after.feature_flags['use_per_goalie_gsax'] = True
    model_after.feature_flags['use_rest_bucket_adj'] = True
    w = model_after.model_data.get('model_weights', {})
    w['goalie_performance_weight'] = max(0.2, w.get('goalie_performance_weight', 0.0))
    w['rest_days_weight'] = max(0.2, w.get('rest_days_weight', 0.0))

    print('B2B BEFORE vs AFTER on', date_str)
    for g in b2b_candidates[:5]:
        bef = model.ensemble_predict(g['away'], g['home'], game_date=date_str)
        aft = model_after.ensemble_predict(g['away'], g['home'], game_date=date_str)
        comps = model_after.debug_situational_components(g['away'], g['home'], date_str)
        print(f"{g['away']} @ {g['home']}  |  "
              f"BEF {bef['away_prob']*100:.1f}% | {bef['home_prob']*100:.1f}%   "
              f"AFT {aft['away_prob']*100:.1f}% | {aft['home_prob']*100:.1f}%   "
              f"Δ {(aft['away_prob']-bef['away_prob'])*100:+.1f} / {(aft['home_prob']-bef['home_prob'])*100:+.1f}  "
              f"[rest A/H: {comps['away_rest']}, {comps['home_rest']}; goalie A/H: {comps['away_goalie_perf']}, {comps['home_goalie_perf']}]")


if __name__ == '__main__':
    main()


