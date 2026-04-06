import requests
import json
import time
import random
from collections import Counter
from playoff_predictor import PlayoffSeriesPredictor

BASE_URL = 'https://api-web.nhle.com/v1'

# 🏆 PROJECTED 2026 PLAYOFF STARTERS (Identified via GSAX DNA)
STARTERS = {
    "COL": "8481529", "MIN": "8482661", "DAL": "8479193",
    "WPG": "8477465", "UTA": "8477970", "EDM": "8478971",
    "NSH": "8481020", "VGK": "8479394", "ANA": "8482477",
    "LAK": "8478406", "VAN": "8477992", "SEA": "8478406",
    "FLA": "8473507", "TBL": "8477831", "BOS": "8480022",
    "TOR": "8478499", "MTL": "8484170", "NYR": "8478048",
    "CAR": "8481611", "PIT": "8483703", "NYI": "8479496",
    "CBJ": "8482982", "BUF": "8480382", "PHI": "8480002"
}

def fetch_standings():
    try:
        r = requests.get(f'{BASE_URL}/standings/now')
        if r.status_code == 200:
            return r.json().get('standings', [])
    except: return []
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
        bracket_pairs.append((wildcards[1]['teamAbbrev']['default'], div_winners[0]['teamAbbrev']['default']))
        dw1_div = div_winners[0]['divisionAbbrev']
        bracket_pairs.append((div_teams[dw1_div][2]['teamAbbrev']['default'], div_teams[dw1_div][1]['teamAbbrev']['default']))
        bracket_pairs.append((wildcards[0]['teamAbbrev']['default'], div_winners[1]['teamAbbrev']['default']))
        dw2_div = div_winners[1]['divisionAbbrev']
        bracket_pairs.append((div_teams[dw2_div][2]['teamAbbrev']['default'], div_teams[dw2_div][1]['teamAbbrev']['default']))
        return bracket_pairs

    return get_conference_bracket(east), get_conference_bracket(west)

def run_goalie_monte_carlo(iterations=10000):
    predictor = PlayoffSeriesPredictor()
    standings = fetch_standings()
    if not standings: return
    
    east_r1, west_r1 = organize_playoff_field(standings)
    print(f"🏒 STARTING 10,000 GOALIE-ADJUSTED TOURNAMENT SIMULATIONS...")
    
    prob_cache = {}
    
    def get_series_winner(away, home):
        away_g = STARTERS.get(away)
        home_g = STARTERS.get(home)
        
        if (away, home, away_g, home_g) not in prob_cache:
            # Need to pass goalies to score prediction model. 
            # We modify calculate_game_win_prob in predictor to accept goalies.
            # For now, we simulate using the score_model directly via predictor logic.
            res_ath = predictor.model.predict_score(away, home, away_goalie=away_g, home_goalie=home_g)
            p_ath = float(res_ath['away_win_prob'])
            
            res_ata = predictor.model.predict_score(home, away, away_goalie=home_g, home_goalie=away_g)
            p_ata = 1.0 - float(res_ata['away_win_prob'])
            
            # Apply Playoff Modifiers
            a_mod = predictor.get_team_playoff_modifier(away)
            h_mod = predictor.get_team_playoff_modifier(home)
            net = a_mod - h_mod
            
            p_ath = min(0.99, max(0.01, p_ath + net))
            p_ata = min(0.99, max(0.01, p_ata + net))
            prob_cache[(away, home, away_g, home_g)] = (p_ath, p_ata)
            
        p_ath, p_ata = prob_cache[(away, home, away_g, home_g)]
        a_w, h_w = 0, 0
        for v in ['h','h','a','a','h','a','h']:
            p = p_ath if v == 'h' else p_ata
            if random.random() < p: a_w += 1
            else: h_w += 1
            if a_w == 4 or h_w == 4: return away if a_w == 4 else home

    cup_winners = []
    finalists = []
    for i in range(iterations):
        e_r1 = [get_series_winner(a, h) for a, h in east_r1]
        w_r1 = [get_series_winner(a, h) for a, h in west_r1]
        e_r2 = [get_series_winner(e_r1[0], e_r1[1]), get_series_winner(e_r1[2], e_r1[3])]
        w_r2 = [get_series_winner(w_r1[0], w_r1[1]), get_series_winner(w_r1[2], w_r1[3])]
        ec, wc = get_series_winner(e_r2[0], e_r2[1]), get_series_winner(w_r2[0], w_r2[1])
        finalists.extend([ec, wc])
        cup_winners.append(get_series_winner(ec, wc))
    
    winner_counts = Counter(cup_winners)
    final_counts = Counter(finalists)
    
    print("\n🏆 FINAL 2026 CHAMPION ODDS (GOALIE-ADJUSTED)")
    print("="*60)
    print(f"{'Team':<10} | {'Cup Prob':>10} | {'Finals Prob':>12}")
    print("-" * 60)
    for team, count in winner_counts.most_common():
        print(f"{team:<10} | {count/iterations:>9.1%} | {final_counts[team]/iterations:>11.1%}")

if __name__ == '__main__':
    run_goalie_monte_carlo(10000)
