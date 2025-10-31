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

    # Prepare models
    model = ImprovedSelfLearningModelV2(); model.deterministic = True
    model.feature_flags['use_per_goalie_gsax'] = False
    model.feature_flags['use_rest_bucket_adj'] = False

    model_after = ImprovedSelfLearningModelV2(); model_after.deterministic = True
    model_after.feature_flags['use_per_goalie_gsax'] = True
    model_after.feature_flags['use_rest_bucket_adj'] = True
    w = model_after.model_data.get('model_weights', {})
    w['rest_days_weight'] = max(0.3, w.get('rest_days_weight', 0.0))
    w['goalie_performance_weight'] = max(0.2, w.get('goalie_performance_weight', 0.0))

    printed_b2b = 0
    printed_goalie = 0

    for delta in range(1, 8):
        date_str = (now_ct - timedelta(days=delta)).strftime('%Y-%m-%d')
        prev_str = (now_ct - timedelta(days=delta+1)).strftime('%Y-%m-%d')
        games = get_games_on_date(api, date_str)
        prev_games = get_games_on_date(api, prev_str)
        prev_teams = set()
        for g in prev_games:
            if g['away']:
                prev_teams.add(g['away'])
            if g['home']:
                prev_teams.add(g['home'])

        for g in games:
            away_b2b = g['away'] in prev_teams
            home_b2b = g['home'] in prev_teams
            # Single-sided B2B demo
            if printed_b2b < 3 and (away_b2b ^ home_b2b):
                bef = model.ensemble_predict(g['away'], g['home'], game_date=date_str)
                aft = model_after.ensemble_predict(g['away'], g['home'], game_date=date_str)
                comps = model_after.debug_situational_components(g['away'], g['home'], date_str)
                print(f"[SINGLE-SIDED B2B] {g['away']} @ {g['home']} ({date_str})  |  "
                      f"BEF {bef['away_prob']*100:.1f}% | {bef['home_prob']*100:.1f}%   "
                      f"AFT {aft['away_prob']*100:.1f}% | {aft['home_prob']*100:.1f}%   "
                      f"Δ {(aft['away_prob']-bef['away_prob'])*100:+.1f} / {(aft['home_prob']-bef['home_prob'])*100:+.1f}  "
                      f"[rest A/H: {comps['away_rest']}, {comps['home_rest']}; goalie A/H: {comps['away_goalie_perf']}, {comps['home_goalie_perf']}]")
                printed_b2b += 1

            # Goalie GSAX demo: show a game where either side goalie perf != 0.5
            if printed_goalie < 3:
                comps = model_after.debug_situational_components(g['away'], g['home'], date_str)
                if comps['away_goalie_perf'] and comps['home_goalie_perf'] and (abs(comps['away_goalie_perf']-0.5) > 1e-6 or abs(comps['home_goalie_perf']-0.5) > 1e-6):
                    bef = model.ensemble_predict(g['away'], g['home'], game_date=date_str)
                    aft = model_after.ensemble_predict(g['away'], g['home'], game_date=date_str)
                    print(f"[GOALIE GSAX] {g['away']} @ {g['home']} ({date_str})  |  "
                          f"BEF {bef['away_prob']*100:.1f}% | {bef['home_prob']*100:.1f}%   "
                          f"AFT {aft['away_prob']*100:.1f}% | {aft['home_prob']*100:.1f}%   "
                          f"Δ {(aft['away_prob']-bef['away_prob'])*100:+.1f} / {(aft['home_prob']-bef['home_prob'])*100:+.1f}  "
                          f"[goalie A/H: {comps['away_goalie_perf']}, {comps['home_goalie_perf']}]")
                    printed_goalie += 1

        if printed_b2b >= 3 and printed_goalie >= 3:
            break

    if printed_b2b == 0:
        print('No single-sided B2B found in last 7 days.')
    if printed_goalie == 0:
        print('No non-neutral goalie GSAX matches found in last 7 days.')


if __name__ == '__main__':
    main()


