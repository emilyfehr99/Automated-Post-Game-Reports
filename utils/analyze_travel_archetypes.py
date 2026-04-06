import json
import pandas as pd
import numpy as np
import math
from pathlib import Path
from datetime import datetime

TEAM_COORDINATES = {
    'ANA': (33.80, -117.88), 'BOS': (42.36, -71.06), 'BUF': (42.89, -78.88),
    'CGY': (51.05, -114.07), 'CAR': (35.80, -78.72), 'CHI': (41.88, -87.67),
    'COL': (39.75, -105.01), 'CBJ': (39.97, -83.00), 'DAL': (32.79, -96.81),
    'DET': (42.34, -83.05), 'EDM': (53.55, -113.49), 'FLA': (26.12, -80.14),
    'LAK': (34.04, -118.27), 'MIN': (44.94, -93.10), 'MTL': (45.51, -73.57),
    'NSH': (36.16, -86.78), 'NJD': (40.73, -74.17), 'NYI': (40.71, -73.60),
    'NYR': (40.75, -73.99), 'OTT': (45.42, -75.70), 'PHI': (39.90, -75.17),
    'PIT': (40.44, -79.99), 'SJS': (37.33, -121.90), 'SEA': (47.62, -122.35),
    'STL': (38.63, -90.20), 'TBL': (27.95, -82.45), 'TOR': (43.65, -79.38),
    'UTA': (40.76, -111.89), 'VAN': (49.28, -123.12), 'VGK': (36.17, -115.14),
    'WSH': (38.90, -77.04), 'WPG': (49.90, -97.14)
}

def calculate_distance(city1, city2):
    if city1 == city2 or city1 not in TEAM_COORDINATES or city2 not in TEAM_COORDINATES:
        return 0.0
    lat1, lon1 = TEAM_COORDINATES[city1]
    lat2, lon2 = TEAM_COORDINATES[city2]
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def analyze():
    file_path = Path('data/win_probability_predictions_v2.json')
    if not file_path.exists():
        file_path = Path('win_probability_predictions_v2.json')
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    preds = data.get('predictions', [])
    sorted_preds = sorted(preds, key=lambda x: x.get('date', ''))
    
    team_history = {} # {team: last_city}
    team_stats = {} # {team: {'high_travel_games': 0, 'high_travel_wins': 0, 'low_travel_games': 0, 'low_travel_wins': 0}}

    for p in sorted_preds:
        home = p.get('home_team')
        away = p.get('away_team')
        actual_winner = p.get('actual_winner')
        
        if not home or not away or not actual_winner:
            continue
            
        # Update Away Travel
        last_city = team_history.get(away, away)
        dist = calculate_distance(last_city, home)
        
        if away not in team_stats:
            team_stats[away] = {'high_travel_games': 0, 'high_travel_wins': 0, 'low_travel_games': 0, 'low_travel_wins': 0}
        
        if dist > 1000:
            team_stats[away]['high_travel_games'] += 1
            if actual_winner == away:
                team_stats[away]['high_travel_wins'] += 1
        else:
            team_stats[away]['low_travel_games'] += 1
            if actual_winner == away:
                team_stats[away]['low_travel_wins'] += 1
                
        # Update history
        team_history[home] = home
        team_history[away] = home # After game, both are at home city
        
    # Calculate Ratios
    archetypes = {}
    for team, stats in team_stats.items():
        high_win_rate = stats['high_travel_wins'] / stats['high_travel_games'] if stats['high_travel_games'] > 0 else 0
        low_win_rate = stats['low_travel_wins'] / stats['low_travel_games'] if stats['low_travel_games'] > 0 else 0
        
        # A team is a "Road Warrior" if they perform BETTER or EQUAL on high travel vs low travel
        is_road_warrior = high_win_rate >= (low_win_rate * 0.9) and stats['high_travel_games'] >= 3
        
        archetypes[team] = {
            'high_travel_win_rate': round(high_win_rate, 3),
            'low_travel_win_rate': round(low_win_rate, 3),
            'high_travel_count': stats['high_travel_games'],
            'is_road_warrior': is_road_warrior
        }
        
    with open('team_travel_archetypes.json', 'w') as f:
        json.dump(archetypes, f, indent=4)
        
    print(f"✅ Analyzed {len(preds)} games. Saved archetypes for {len(archetypes)} teams.")
    
    # Print Top Road Warriors
    rw = [team for team, d in archetypes.items() if d['is_road_warrior']]
    print(f"Top Road Warriors: {', '.join(rw[:10])}...")

if __name__ == "__main__":
    analyze()
