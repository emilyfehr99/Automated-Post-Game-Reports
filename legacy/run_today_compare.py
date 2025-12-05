#!/usr/bin/env python3
from datetime import datetime, timedelta
import pytz
from nhl_api_client import NHLAPIClient
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2


def get_todays_games():
    api = NHLAPIClient()
    ct = pytz.timezone('US/Central')
    now_ct = datetime.now(ct)
    today_str = now_ct.strftime('%Y-%m-%d')
    schedule = api.get_game_schedule(today_str)
    games = []
    if schedule and 'gameWeek' in schedule:
        for day in schedule['gameWeek']:
            if day.get('date') == today_str:
                for g in day.get('games', []):
                    games.append({
                        'id': str(g.get('id')),
                        'away': g.get('awayTeam', {}).get('abbrev'),
                        'home': g.get('homeTeam', {}).get('abbrev'),
                    })
    return games, today_str


def compute_predictions(model: ImprovedSelfLearningModelV2, games, date_str):
    out = []
    for g in games:
        res = model.ensemble_predict(g['away'], g['home'], game_date=date_str)
        out.append({
            'id': g['id'],
            'away': g['away'],
            'home': g['home'],
            'away_prob': res.get('away_prob'),
            'home_prob': res.get('home_prob'),
            'confidence': res.get('prediction_confidence'),
        })
    return out


def main():
    games, today_str = get_todays_games()
    if not games:
        print('No games today.')
        return

    # BEFORE: flags off, deterministic
    model = ImprovedSelfLearningModelV2()
    model.deterministic = True
    model.feature_flags['use_per_goalie_gsax'] = False
    model.feature_flags['use_rest_bucket_adj'] = False
    before = compute_predictions(model, games, today_str)

    # AFTER: flags on, deterministic, ensure small non-zero weights to manifest signal
    model_after = ImprovedSelfLearningModelV2()
    model_after.deterministic = True
    model_after.feature_flags['use_per_goalie_gsax'] = True
    model_after.feature_flags['use_rest_bucket_adj'] = True
    w = model_after.model_data.get('model_weights', {})
    # Temporarily boost to reveal impact clearly in the comparison
    w['goalie_performance_weight'] = max(0.2, w.get('goalie_performance_weight', 0.0))
    w['rest_days_weight'] = max(0.2, w.get('rest_days_weight', 0.0))
    w['sos_weight'] = max(0.05, w.get('sos_weight', 0.0))
    after = compute_predictions(model_after, games, today_str)

    # Print side-by-side
    print('TODAY PREDICTIONS - BEFORE vs AFTER (away% | home%)')
    for b, a in zip(before, after):
        if b['away'] != a['away'] or b['home'] != a['home']:
            continue
        comps = model_after.debug_situational_components(b['away'], b['home'], today_str)
        print(f"{b['away']} @ {b['home']}  |  "
              f"BEF {b['away_prob']*100:.1f}% | {b['home_prob']*100:.1f}%   "
              f"AFT {a['away_prob']*100:.1f}% | {a['home_prob']*100:.1f}%   "
              f"Δ {(a['away_prob']-b['away_prob'])*100:+.1f} / {(a['home_prob']-b['home_prob'])*100:+.1f}  "
              f"[rest A/H: {comps['away_rest']}, {comps['home_rest']}; goalie A/H: {comps['away_goalie_perf']}, {comps['home_goalie_perf']}]")


if __name__ == '__main__':
    main()


