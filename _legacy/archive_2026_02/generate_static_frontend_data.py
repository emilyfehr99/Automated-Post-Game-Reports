
import json
import os
import shutil
import sys
from datetime import datetime

# Helper to load JSON
def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {}

def generate_static_data():
    print("Generating static frontend data...")
    
    # Paths
    ROOT_DIR = os.getcwd()
    DATA_DIR = os.path.join(ROOT_DIR, 'data')
    PUBLIC_DATA_DIR = os.path.join(ROOT_DIR, 'nhl-analytics', 'public', 'data')
    
    # Ensure output dir exists
    os.makedirs(PUBLIC_DATA_DIR, exist_ok=True)
    
    # 1. PROCESS TEAM METRICS (The heavy calculation)
    stats_file = os.path.join(DATA_DIR, 'season_2025_2026_team_stats.json')
    data = load_json(stats_file)
    teams = data.get('teams', data)
    
    print(f"Processing metrics for {len(teams)} teams...")
    
    def avg(lst):
        if not lst or len(lst) == 0: return 0
        numeric_values = [x for x in lst if isinstance(x, (int, float))]
        if not numeric_values: return 0
        return sum(numeric_values) / len(numeric_values)
        
    def get_text_mode(lst):
        if not lst: return "N/A"
        text_values = [x for x in lst if isinstance(x, str)]
        if not text_values: return "N/A"
        from collections import Counter
        return Counter(text_values).most_common(1)[0][0]

    metrics = {}
    
    # TEAM COLORS MAPPING
    team_colors = {
        'ANA': '#F47A38', 'ARI': '#8C2633', 'BOS': '#FFB81C', 'BUF': '#002654',
        'CGY': '#C8102E', 'CAR': '#CC0000', 'CHI': '#CF0A2C', 'COL': '#6F263D',
        'CBJ': '#002654', 'DAL': '#006847', 'DET': '#CE1126', 'EDM': '#FF4C00',
        'FLA': '#B9975B', 'LAK': '#111111', 'MIN': '#154734', 'MTL': '#AF1E2D',
        'NSH': '#FFB81C', 'NJD': '#CE1126', 'NYI': '#00539B', 'NYR': '#0038A8',
        'OTT': '#C52032', 'PHI': '#F74902', 'PIT': '#FCB514', 'SJS': '#006D75',
        'SEA': '#99D9D9', 'STL': '#002F87', 'TBL': '#002868', 'TOR': '#00205B',
        'UTA': '#71AFE5', 'VAN': '#00205B', 'VGK': '#B4975A', 'WSH': '#041E42',
        'WPG': '#041E42'
    }

    for team_abbrev, team_data in teams.items():
        home_stats = team_data.get('home', {})
        away_stats = team_data.get('away', {})
        
        # Calculate combined metrics
        combined_lat = home_stats.get('lat', []) + away_stats.get('lat', [])
        combined_long = home_stats.get('long_movement', []) + away_stats.get('long_movement', [])
        
        metrics[team_abbrev] = {
            'gs': round((avg(home_stats.get('gs', [])) + avg(away_stats.get('gs', []))) / 2, 1),
            'nzts': round((avg(home_stats.get('nzt', [])) + avg(away_stats.get('nzt', []))) / 2),
            'nztsa': round((avg(home_stats.get('nztsa', [])) + avg(away_stats.get('nztsa', []))) / 2, 1),
            'ozs': round((avg(home_stats.get('ozs', [])) + avg(away_stats.get('ozs', []))) / 2),
            'nzs': round((avg(home_stats.get('nzs', [])) + avg(away_stats.get('nzs', []))) / 2),
            'dzs': round((avg(home_stats.get('period_dzs', [])) + avg(away_stats.get('period_dzs', []))) / 2),
            'fc': round((avg(home_stats.get('fc', [])) + avg(away_stats.get('fc', []))) / 2),
            'rush': round((avg(home_stats.get('rush', [])) + avg(away_stats.get('rush', []))) / 2),
            
            'lat': get_text_mode(combined_lat),
            'long_movement': get_text_mode(combined_long),
            
            'xg': round((avg(home_stats.get('xg', [])) + avg(away_stats.get('xg', []))) / 2, 2),
            'hdc': round((avg(home_stats.get('hdc', [])) + avg(away_stats.get('hdc', []))) / 2, 1),
            'hdca': round((avg(home_stats.get('hdca', [])) + avg(away_stats.get('hdca', []))) / 2, 1),
            'shots': round((avg(home_stats.get('shots', [])) + avg(away_stats.get('shots', []))) / 2, 1),
            'goals': round((avg(home_stats.get('goals', [])) + avg(away_stats.get('goals', []))) / 2, 2),
            'ga_gp': round((avg(home_stats.get('opp_goals', [])) + avg(away_stats.get('opp_goals', []))) / 2, 2),
            
            'corsi_pct': round((avg(home_stats.get('corsi_pct', [])) + avg(away_stats.get('corsi_pct', []))) / 2, 1),
            
            'hits': round((avg(home_stats.get('hits', [])) + avg(away_stats.get('hits', []))) / 2, 1),
            'blocks': round((avg(home_stats.get('blocked_shots', [])) + avg(away_stats.get('blocked_shots', []))) / 2, 1),
            'giveaways': round((avg(home_stats.get('giveaways', [])) + avg(away_stats.get('giveaways', []))) / 2, 1),
            'takeaways': round((avg(home_stats.get('takeaways', [])) + avg(away_stats.get('takeaways', []))) / 2, 1),
            'pim': round((avg(home_stats.get('penalty_minutes', [])) + avg(away_stats.get('penalty_minutes', []))) / 2, 1),
            
            'pp_pct': round((avg(home_stats.get('power_play_pct', [])) + avg(away_stats.get('power_play_pct', []))) / 2, 1),
            'pk_pct': round((avg(home_stats.get('penalty_kill_pct', [])) + avg(away_stats.get('penalty_kill_pct', []))) / 2, 1),
            'fo_pct': round((avg(home_stats.get('faceoff_pct', [])) + avg(away_stats.get('faceoff_pct', []))) / 2, 1),
            
            'color': team_colors.get(team_abbrev.upper(), '#888888')
        }
        
    metrics_path = os.path.join(PUBLIC_DATA_DIR, 'team_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f)
    print(f"✅ Saved team metrics to {metrics_path}")

    # 2. COPY PREDICTIONS
    pred_src = os.path.join(DATA_DIR, 'win_probability_predictions_v2.json')
    pred_dst = os.path.join(PUBLIC_DATA_DIR, 'predictions.json')
    try:
        shutil.copy2(pred_src, pred_dst)
        print(f"✅ Copied predictions to {pred_dst}")
    except Exception as e:
        print(f"⚠️ Failed to copy predictions: {e}")

    # 3. SAVE TIMESTAMP
    with open(os.path.join(PUBLIC_DATA_DIR, 'meta.json'), 'w') as f:
        json.dump({'last_updated': datetime.now().isoformat()}, f)
    
    print("\nStatic data generation complete!")

if __name__ == "__main__":
    generate_static_data()
