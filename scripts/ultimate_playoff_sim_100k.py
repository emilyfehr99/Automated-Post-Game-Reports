import requests
import json
import time
import random
from collections import Counter
from playoff_predictor import PlayoffSeriesPredictor

BASE_URL = 'https://api-web.nhle.com/v1'

# 🚑 ULTIMATE 2026 INJURY & MOMENTUM OVERRIDES
# Penalties specifically targeting win probability per game
INJURY_PENALTIES = {
    "FLA": -0.15, # Total roster collapse (Barkov, Reinhart, Ekblad out)
    "TBL": -0.02, # Hagel (Day-to-Day)
    "COL": -0.03, # Makar (Day-to-Day - High risk floor)
    "MTL": -0.04, # Carrier out 2-4 weeks
    "VAN": -0.02, # Kane out
}

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
        if r.status_code == 200: return r.json().get('standings', [])
    except: return []
    return []

def organize_playoff_field(standings):
    east = [s for s in standings if s['conferenceAbbrev'] == 'E']
    west = [s for s in standings if s['conferenceAbbrev'] == 'W']
    
    def get_conference_bracket(conf_teams):
        divisions = sorted(list(set([t['divisionAbbrev'] for t in conf_teams])))
        div_teams = {d: sorted([t for t in conf_teams if t['divisionAbbrev'] == d], 
                               key=lambda x: x['points'], reverse=True) for d in divisions}
        q_ids = set()
        for d in divisions:
            for t in div_teams[d][:3]: q_ids.add(t['teamAbbrev']['default'])
        wildcards = sorted([t for t in conf_teams if t['teamAbbrev']['default'] not in q_ids], 
                           key=lambda x: x['points'], reverse=True)[:2]
        div_winners = sorted([div_teams[d][0] for d in divisions], key=lambda x: x['points'], reverse=True)
        pairs = []
        pairs.append((wildcards[1]['teamAbbrev']['default'], div_winners[0]['teamAbbrev']['default']))
        dw1_div = div_winners[0]['divisionAbbrev']
        pairs.append((div_teams[dw1_div][2]['teamAbbrev']['default'], div_teams[dw1_div][1]['teamAbbrev']['default']))
        pairs.append((wildcards[0]['teamAbbrev']['default'], div_winners[1]['teamAbbrev']['default']))
        dw2_div = div_winners[1]['divisionAbbrev']
        pairs.append((div_teams[dw2_div][2]['teamAbbrev']['default'], div_teams[dw2_div][1]['teamAbbrev']['default']))
        return pairs
    return get_conference_bracket(east), get_conference_bracket(west)

def run_ultimate_monte_carlo(iterations=100000):
    predictor = PlayoffSeriesPredictor()
    standings = fetch_standings()
    if not standings: return
    
    east_r1, west_r1 = organize_playoff_field(standings)
    print(f"💎 EXECUTING {iterations} ULTIMATE PRECISION TOURNAMENT RUNS...")
    
    prob_cache = {}
    
    def get_series_winner(away, home):
        aw_g, hm_g = STARTERS.get(away), STARTERS.get(home)
        cache_key = (away, home, aw_g, hm_g)
        
        if cache_key not in prob_cache:
            res_ath = predictor.model.predict_score(away, home, away_goalie=aw_g, home_goalie=hm_g)
            p_ath = float(res_ath['away_win_prob'])
            res_ata = predictor.model.predict_score(home, away, away_goalie=hm_g, home_goalie=aw_g)
            p_ata = 1.0 - float(res_ata['away_win_prob'])
            
            # Apply 5-Year DNA + Injury/Momentum Modifiers
            a_dna = predictor.get_team_playoff_modifier(away)
            h_dna = predictor.get_team_playoff_modifier(home)
            a_inj = INJURY_PENALTIES.get(away, 0.0)
            h_inj = INJURY_PENALTIES.get(home, 0.0)
            
            # Aggregate Final Win Probability Delta
            final_net = (a_dna + a_inj) - (h_dna + h_inj)
            
            p_ath = min(0.99, max(0.01, p_ath + final_net))
            p_ata = min(0.99, max(0.01, p_ata + final_net))
            prob_cache[cache_key] = (p_ath, p_ata)
            
        p_ath, p_ata = prob_cache[cache_key]
        aw_w, hm_w = 0, 0
        for v in ['h','h','a','a','h','a','h']:
            p = p_ath if v == 'h' else p_ata
            if random.random() < p: aw_w += 1
            else: hm_w += 1
            if aw_w == 4 or hm_w == 4: return away if aw_w == 4 else home

    cup_winners = []
    for i in range(iterations):
        e_r1 = [get_series_winner(a, h) for a, h in east_r1]
        w_r1 = [get_series_winner(a, h) for a, h in west_r1]
        e_r2 = [get_series_winner(e_r1[0], e_r1[1]), get_series_winner(e_r1[2], e_r1[3])]
        w_r2 = [get_series_winner(w_r1[0], w_r1[1]), get_series_winner(w_r1[2], w_r1[3])]
        ec, wc = get_series_winner(e_r2[0], e_r2[1]), get_series_winner(w_r2[0], w_r2[1])
        cup_winners.append(get_series_winner(ec, wc))
        if (i+1) % 25000 == 0: print(f"  🏁 {i+1} stress tests complete...")
    
    winner_counts = Counter(cup_winners)
    print("\n🏆 THE ULTIMATE 2026 CHAMPIONSHIP PROBABILITY (100,000 RUNS)")
    print("="*60)
    print(f"{'Team':<10} | {'Cup Odds':>10} | {'Confidence Level'}")
    print("-" * 60)
    for team, count in winner_counts.most_common():
        prob = count/iterations
        conf = "HIGH" if prob > 0.15 else "MODERATE" if prob > 0.05 else "LOW"
        print(f"{team:<10} | {prob:>9.2%} | {conf}")

if __name__ == '__main__':
    run_ultimate_monte_carlo(100000)
