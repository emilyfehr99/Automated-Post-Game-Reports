import requests
import json
import time
import random
import sys
from collections import Counter, defaultdict
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
        
        bracket_pairs = []
        # Match 1: DivWinner1 vs WC2
        bracket_pairs.append((wildcards[1]['teamAbbrev']['default'], div_winners[0]['teamAbbrev']['default']))
        # Match 2: DivWinner1's Division 2nd vs 3rd
        dw1_div = div_winners[0]['divisionAbbrev']
        bracket_pairs.append((div_teams[dw1_div][2]['teamAbbrev']['default'], div_teams[dw1_div][1]['teamAbbrev']['default']))
        # Match 3: DivWinner2 vs WC1
        bracket_pairs.append((wildcards[0]['teamAbbrev']['default'], div_winners[1]['teamAbbrev']['default']))
        # Match 4: DivWinner2's Division 2nd vs 3rd
        dw2_div = div_winners[1]['divisionAbbrev']
        bracket_pairs.append((div_teams[dw2_div][2]['teamAbbrev']['default'], div_teams[dw2_div][1]['teamAbbrev']['default']))
            
        return bracket_pairs

    return get_conference_bracket(east), get_conference_bracket(west)

def run_tournament_monte_carlo(iterations=100000):
    predictor = PlayoffSeriesPredictor()
    standings = fetch_standings()
    if not standings:
        print('Error fetching standings.')
        return
        
    east_r1, west_r1 = organize_playoff_field(standings)
    
    # Trackers for advancement
    advancement = defaultdict(lambda: Counter()) # team -> {round_number: wins}
    
    # Pre-cache game win probs to speed up sims
    prob_cache = {}

    def get_series_winner(away, home):
        key = tuple(sorted([away, home]))
        if key not in prob_cache:
            # Get consistent win probs for this matchup
            p_away_at_home = predictor.calculate_game_win_prob(away, home)
            p_home_at_away = predictor.calculate_game_win_prob(home, away)
            p_away_at_away = 1 - p_home_at_away
            prob_cache[key] = (away, home, p_away_at_home, p_away_at_away)
        
        a_team, h_team, p_ath, p_ata = prob_cache[key]
        
        a_wins = 0
        h_wins = 0
        # H-H-A-A-H-A-H
        for venue in ['h','h','a','a','h','a','h']:
            p = p_ath if venue == 'h' else p_ata
            if random.random() < p:
                a_wins += 1
            else:
                h_wins += 1
            if a_wins == 4 or h_wins == 4:
                winner = a_team if a_wins == 4 else h_team
                return winner

    print(f"🏒 STARTING {iterations:,} TOURNAMENT SIMULATIONS (High-Fidelity xG Mode)...")
    start_time = time.time()
    
    for _ in range(iterations):
        # Round 1 (Division Semis)
        e_r1_winners = [get_series_winner(p[0], p[1]) for p in east_r1]
        w_r1_winners = [get_series_winner(p[0], p[1]) for p in west_r1]
        
        for w in e_r1_winners + w_r1_winners: advancement[w][1] += 1
        
        # Round 2 (Division Finals)
        e_r2_winners = [
            get_series_winner(e_r1_winners[0], e_r1_winners[1]),
            get_series_winner(e_r1_winners[2], e_r1_winners[3])
        ]
        w_r2_winners = [
            get_series_winner(w_r1_winners[0], w_r1_winners[1]),
            get_series_winner(w_r1_winners[2], w_r1_winners[3])
        ]
        
        for w in e_r2_winners + w_r2_winners: advancement[w][2] += 1
        
        # Round 3 (Conference Finals)
        e_r3_winner = get_series_winner(e_r2_winners[0], e_r2_winners[1])
        w_r3_winner = get_series_winner(w_r2_winners[0], w_r2_winners[1])
        
        advancement[e_r3_winner][3] += 1
        advancement[w_r3_winner][3] += 1
        
        # Round 4 (Stanley Cup Finals)
        cup_winner = get_series_winner(e_r3_winner, w_r3_winner)
        advancement[cup_winner][4] += 1
        
    duration = time.time() - start_time
    print(f"✅ Simulation Complete in {duration:.1f}s\n")
    
    # Reporting
    print(f"{'Team':<5} | {'R2%':>6} | {'R3%':>6} | {'Finals%':>7} | {'CUP WIN%':>9}")
    print("-" * 50)
    
    final_results = []
    for team in advancement:
        stats = advancement[team]
        final_results.append({
            'team': team,
            'r2': stats[1] / iterations,
            'r3': stats[2] / iterations,
            'fin': stats[3] / iterations,
            'cup': stats[4] / iterations
        })
    
    final_results.sort(key=lambda x: x['cup'], reverse=True)
    for res in final_results:
        print(f"{res['team']:<5} | {res['r2']:>6.1%} | {res['r3']:>6.1%} | {res['fin']:>7.1%} | {res['cup']:>9.2%}")

if __name__ == '__main__':
    # Increase recursion depth for safety if needed
    import sys
    sys.setrecursionlimit(2000)
    run_tournament_monte_carlo(100000)
