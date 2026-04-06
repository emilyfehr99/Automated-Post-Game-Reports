import requests
import json
import time
import random
from playoff_predictor import PlayoffSeriesPredictor

BASE_URL = 'https://api-web.nhle.com/v1'

def fetch_standings():
    try:
        r = requests.get(f'{BASE_URL}/standings/now')
        if r.status_code == 200:
            return r.json().get('standings', [])
    except:
        return []
    return []

def organize_playoff_field(standings):
    east = [s for s in standings if s['conferenceAbbrev'] == 'E']
    west = [s for s in standings if s['conferenceAbbrev'] == 'W']
    
    def get_conference_bracket(conf_teams):
        divisions = sorted(list(set([t['divisionAbbrev'] for t in conf_teams])))
        div_teams = {d: sorted([t for t in conf_teams if t['divisionAbbrev'] == d], 
                               key=lambda x: x['points'], reverse=True) for d in divisions}
        
        qualifiers = []
        qualifier_ids = set()
        for d in divisions:
            top3 = div_teams[d][:3]
            qualifiers.extend(top3)
            for t in top3: qualifier_ids.add(t['teamAbbrev']['default'])
            
        rem_teams = sorted([t for t in conf_teams if t['teamAbbrev']['default'] not in qualifier_ids], 
                           key=lambda x: x['points'], reverse=True)
        wildcards = rem_teams[:2]
        
        div_winners = sorted([div_teams[d][0] for d in divisions], key=lambda x: x['points'], reverse=True)
        
        bracket = {'R1': [], 'div_winners': div_winners, 'wildcards': wildcards, 'div_teams': div_teams}
        
        # We need to maintain the bracket structure:
        # Match 1: DivWinner1 vs WC2
        # Match 2: DivWinner1's Division 2nd vs 3rd
        # Match 3: DivWinner2 vs WC1
        # Match 4: DivWinner2's Division 2nd vs 3rd
        
        # Match 1
        bracket['R1'].append({'away': wildcards[1]['teamAbbrev']['default'], 'home': div_winners[0]['teamAbbrev']['default']})
        # Match 2
        dw1_div = div_winners[0]['divisionAbbrev']
        bracket['R1'].append({'away': div_teams[dw1_div][2]['teamAbbrev']['default'], 'home': div_teams[dw1_div][1]['teamAbbrev']['default']})
        # Match 3
        bracket['R1'].append({'away': wildcards[0]['teamAbbrev']['default'], 'home': div_winners[1]['teamAbbrev']['default']})
        # Match 4
        dw2_div = div_winners[1]['divisionAbbrev']
        bracket['R1'].append({'away': div_teams[dw2_div][2]['teamAbbrev']['default'], 'home': div_teams[dw2_div][1]['teamAbbrev']['default']})
            
        return bracket

    return get_conference_bracket(east), get_conference_bracket(west)

def run_2026_simulation():
    predictor = PlayoffSeriesPredictor()
    standings = fetch_standings()
    if not standings:
        print('Error fetching standings.')
        return
        
    east_bracket, west_bracket = organize_playoff_field(standings)
    
    def simulate_bracket(bracket_info, conference_name):
        print(f'\n🏆 {conference_name.upper()} CONFERENCE SIMULATION')
        print('='*60)
        
        r1_winners = []
        for i, match in enumerate(bracket_info['R1'], 1):
            res = predictor.simulate_series(match['away'], match['home'])
            r1_winners.append(res['winner_projection'])
            print(f"  R1 Match {i}: {match['away']:>3} @ {match['home']:<3} -> {res['winner_projection']} wins ({max(res['away_series_win_prob'], res['home_series_win_prob']):.1%})")
            
        # R2 pairings: Winner(M1) vs Winner(M2) and Winner(M3) vs Winner(M4)
        r2_matches = [(r1_winners[0], r1_winners[1]), (r1_winners[2], r1_winners[3])]
        r2_winners = []
        for i, (a, h) in enumerate(r2_matches, 1):
            res = predictor.simulate_series(a, h)
            r2_winners.append(res['winner_projection'])
            print(f"  R2 Match {i}: {a:>3} vs {h:<3} -> {res['winner_projection']} wins ({max(res['away_series_win_prob'], res['home_series_win_prob']):.1%})")

        # R3 (Final)
        res = predictor.simulate_series(r2_winners[0], r2_winners[1])
        print(f"  🏆 {conference_name.upper()} CHAMPION: {res['winner_projection']} wins series ({max(res['away_series_win_prob'], res['home_series_win_prob']):.1%})")
        return res['winner_projection']

    east_champ = simulate_bracket(east_bracket, 'Eastern')
    west_champ = simulate_bracket(west_bracket, 'Western')
    
    print(f'\n✨ STANLEY CUP FINAL: {east_champ} vs {west_champ} ✨')
    print('='*60)
    final_res = predictor.simulate_series(east_champ, west_champ)
    print(f"  🏆 2026 CHAMPION: {final_res['winner_projection']} wins the Cup (Win Prob: {max(final_res['away_series_win_prob'], final_res['home_series_win_prob']):.1%})")

if __name__ == '__main__':
    run_2026_simulation()
