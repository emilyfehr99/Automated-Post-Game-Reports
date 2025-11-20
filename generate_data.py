import json
import random
import requests
from datetime import datetime

def generate_team_stats():
    print("Fetching standings...")
    try:
        response = requests.get("https://api-web.nhle.com/v1/standings/now")
        data = response.json()
        standings = data.get('standings', [])
    except Exception as e:
        print(f"Error fetching standings: {e}")
        return

    teams_data = {}
    
    for team in standings:
        abbrev = team['teamAbbrev']['default']
        name = team['teamName']['default']
        
        print(f"Processing {name} ({abbrev})...")
        
        # Base stats from standings
        gp = team['gamesPlayed']
        wins = team['wins']
        losses = team['losses']
        otl = team['otLosses']
        points = team['points']
        gf = team['goalFor']
        ga = team['goalAgainst']
        
        # Simulate advanced metrics based on team performance
        # Better teams get better metrics generally
        win_pct = points / (gp * 2) if gp > 0 else 0.5
        
        # Helper to generate realistic metric
        def gen_metric(base, var, correlation=0):
            # correlation: 1 = strong positive with win_pct, -1 = strong negative
            factor = 1 + (win_pct - 0.5) * correlation
            return round(random.gauss(base, var) * factor, 2)
            
        # Generate home and away splits (simplified)
        stats = {
            "home": {
                "gs": [gen_metric(55, 10, 0.8) for _ in range(gp // 2)],
                "xg": [gen_metric(3.2, 0.8, 0.7) for _ in range(gp // 2)],
                "corsi_pct": [gen_metric(50, 5, 0.6) for _ in range(gp // 2)],
                "fenwick_pct": [gen_metric(50, 5, 0.6) for _ in range(gp // 2)],
                "pdo": [gen_metric(100, 2, 0.3) for _ in range(gp // 2)],
                "ozs": [gen_metric(50, 5, 0.5) for _ in range(gp // 2)],
                "nzs": [gen_metric(50, 5, 0) for _ in range(gp // 2)],
                "dzs": [gen_metric(50, 5, -0.5) for _ in range(gp // 2)],
                "goals": [gen_metric(3.1, 1.5, 0.7) for _ in range(gp // 2)],
                "shots": [gen_metric(31, 4, 0.6) for _ in range(gp // 2)],
                "hits": [gen_metric(22, 6, 0.1) for _ in range(gp // 2)],
                "blocked_shots": [gen_metric(14, 4, -0.2) for _ in range(gp // 2)],
                "giveaways": [gen_metric(8, 3, -0.3) for _ in range(gp // 2)],
                "takeaways": [gen_metric(7, 3, 0.4) for _ in range(gp // 2)],
                "penalty_minutes": [gen_metric(8, 4, -0.1) for _ in range(gp // 2)],
                "power_play_pct": [gen_metric(22, 5, 0.6) for _ in range(gp // 2)],
                "penalty_kill_pct": [gen_metric(80, 5, 0.6) for _ in range(gp // 2)],
                "faceoff_pct": [gen_metric(50, 4, 0.3) for _ in range(gp // 2)],
                "games": list(range(gp // 2)),
                
                # New metrics
                "nzt": [gen_metric(15, 3, -0.4) for _ in range(gp // 2)], # Neutral Zone Turnovers
                "nztsa": [gen_metric(0.5, 0.2, -0.5) for _ in range(gp // 2)], # NZ Turnovers to Shots Against
                "fc": [gen_metric(12, 3, 0.5) for _ in range(gp // 2)], # Forecheck shots
                "rush": [gen_metric(8, 2, 0.6) for _ in range(gp // 2)], # Rush shots
                "lat": [gen_metric(18, 4, 0.5) for _ in range(gp // 2)], # Lateral movement
                "long_movement": [gen_metric(45, 8, 0.2) for _ in range(gp // 2)], # Longitudinal movement
                "hdc": [gen_metric(10, 3, 0.7) for _ in range(gp // 2)], # High Danger Chances
                "hdca": [gen_metric(9, 3, -0.6) for _ in range(gp // 2)], # High Danger Chances Against
                "period_dzs": [gen_metric(15, 4, -0.4) for _ in range(gp // 2)], # Period Defensive Zone Starts
            },
            "away": {
                "gs": [gen_metric(50, 10, 0.8) for _ in range(gp // 2)],
                "xg": [gen_metric(2.9, 0.8, 0.7) for _ in range(gp // 2)],
                "corsi_pct": [gen_metric(48, 5, 0.6) for _ in range(gp // 2)],
                "fenwick_pct": [gen_metric(48, 5, 0.6) for _ in range(gp // 2)],
                "pdo": [gen_metric(99, 2, 0.3) for _ in range(gp // 2)],
                "ozs": [gen_metric(48, 5, 0.5) for _ in range(gp // 2)],
                "nzs": [gen_metric(50, 5, 0) for _ in range(gp // 2)],
                "dzs": [gen_metric(52, 5, -0.5) for _ in range(gp // 2)],
                "goals": [gen_metric(2.8, 1.5, 0.7) for _ in range(gp // 2)],
                "shots": [gen_metric(29, 4, 0.6) for _ in range(gp // 2)],
                "hits": [gen_metric(20, 6, 0.1) for _ in range(gp // 2)],
                "blocked_shots": [gen_metric(15, 4, -0.2) for _ in range(gp // 2)],
                "giveaways": [gen_metric(9, 3, -0.3) for _ in range(gp // 2)],
                "takeaways": [gen_metric(6, 3, 0.4) for _ in range(gp // 2)],
                "penalty_minutes": [gen_metric(9, 4, -0.1) for _ in range(gp // 2)],
                "power_play_pct": [gen_metric(20, 5, 0.6) for _ in range(gp // 2)],
                "penalty_kill_pct": [gen_metric(78, 5, 0.6) for _ in range(gp // 2)],
                "faceoff_pct": [gen_metric(49, 4, 0.3) for _ in range(gp // 2)],
                "games": list(range(gp // 2)),
                
                # New metrics
                "nzt": [gen_metric(16, 3, -0.4) for _ in range(gp // 2)],
                "nztsa": [gen_metric(0.6, 0.2, -0.5) for _ in range(gp // 2)],
                "fc": [gen_metric(10, 3, 0.5) for _ in range(gp // 2)],
                "rush": [gen_metric(7, 2, 0.6) for _ in range(gp // 2)],
                "lat": [gen_metric(16, 4, 0.5) for _ in range(gp // 2)],
                "long_movement": [gen_metric(42, 8, 0.2) for _ in range(gp // 2)],
                "hdc": [gen_metric(9, 3, 0.7) for _ in range(gp // 2)],
                "hdca": [gen_metric(10, 3, -0.6) for _ in range(gp // 2)],
                "period_dzs": [gen_metric(16, 4, -0.4) for _ in range(gp // 2)],
            }
        }
        
        teams_data[abbrev] = stats

    output = {"teams": teams_data}
    
    with open('season_2025_2026_team_stats.json', 'w') as f:
        json.dump(output, f, indent=2)
        
    print("Generated season_2025_2026_team_stats.json")

if __name__ == "__main__":
    generate_team_stats()
