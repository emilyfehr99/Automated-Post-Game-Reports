import json
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import pearsonr

def load_game_data():
    path = Path('data/win_probability_predictions_v2.json')
    if not path.exists():
        path = Path('win_probability_predictions_v2.json')
        
    with open(path, 'r') as f:
        data = json.load(f)
    print(f"DEBUG: Loaded JSON with {len(data.get('predictions', []))} total entries")
    return data.get('predictions', [])

def analyze_drivers():
    print("🏒 ANALYZING SCORING DRIVERS PER TEAM")
    print("=" * 60)
    
    preds = load_game_data()
    team_data = {}  # {team: {'goals': [], 'xg': [], 'corsi': []}}
    
    # 1. Collect Data
    processed_count = 0
    skipped_count = 0
    no_metrics_count = 0
    
    debug_limit = 20
    
    for i, p in enumerate(preds):
        # Check for completed game
        if 'actual_home_score' not in p and 'actual_winner' not in p:
            skipped_count += 1
            continue
            
        metrics = p.get('metrics_used', {})
        if not metrics:
            no_metrics_count += 1
            if i < debug_limit:
                print(f"DEBUG [{i}]: No metrics_used. Keys: {p.keys()}")
            continue
        
        # Home Data
        home = p.get('home_team')
        h_goals = p.get('actual_home_score')
        if h_goals is None: h_goals = metrics.get('home_goals')
        
        h_xg = metrics.get('home_xg', 0.0)
        h_corsi = metrics.get('home_corsi_pct', 50.0)
        
        added_home = False
        if h_goals is not None and h_xg > 0.0:
            if home not in team_data: team_data[home] = {'goals': [], 'xg': [], 'corsi': []}
            team_data[home]['goals'].append(float(h_goals))
            team_data[home]['xg'].append(float(h_xg))
            team_data[home]['corsi'].append(float(h_corsi))
            added_home = True
        elif i < debug_limit:
             print(f"DEBUG [{i}] SKIP HOME {home}: h_goals={h_goals} h_xg={h_xg}")
            
        # Away Data
        away = p.get('away_team')
        a_goals = p.get('actual_away_score')
        if a_goals is None: a_goals = metrics.get('away_goals')
        
        a_xg = metrics.get('away_xg', 0.0)
        a_corsi = metrics.get('away_corsi_pct', 50.0)
        
        added_away = False
        if a_goals is not None and a_xg > 0.0:
            if away not in team_data: team_data[away] = {'goals': [], 'xg': [], 'corsi': []}
            team_data[away]['goals'].append(float(a_goals))
            team_data[away]['xg'].append(float(a_xg))
            team_data[away]['corsi'].append(float(a_corsi))
            added_away = True
        elif i < debug_limit:
             print(f"DEBUG [{i}] SKIP AWAY {away}: a_goals={a_goals} a_xg={a_xg}")
            
        if added_home or added_away:
            processed_count += 1
            
    print(f"✅ Processed {processed_count} games with extracted data")
    print(f"⚠️ Skipped {skipped_count} future/incomplete games")
    print(f"⚠️ Skipped {no_metrics_count} completed games missing 'metrics_used'")
    
    # 2. Calculate Correlations
    results = []
    
    for team, stats in team_data.items():
        if len(stats['goals']) < 5: 
            # print(f"Skipping {team}: only {len(stats['goals'])} samples")
            continue
            
        # Goals vs xG Correlation
        if len(set(stats['goals'])) > 1 and len(set(stats['xg'])) > 1:
             corr_xg, _ = pearsonr(stats['goals'], stats['xg'])
        else:
             corr_xg = 0.0
        
        # Goals vs Corsi Correlation
        if len(set(stats['goals'])) > 1 and len(set(stats['corsi'])) > 1:
            corr_corsi, _ = pearsonr(stats['goals'], stats['corsi'])
        else:
             corr_corsi = 0.0
        
        # Finishing Ability (Goals over xG per game)
        total_goals = sum(stats['goals'])
        total_xg = sum(stats['xg'])
        games = len(stats['goals'])
        finish_per_game = (total_goals - total_xg) / games
        
        results.append({
            'team': team,
            'corr_xg': corr_xg,
            'corr_corsi': corr_corsi,
            'finish_pg': finish_per_game,
            'samples': games
        })
        
    # 3. Display Results
    if not results:
        print("❌ No team met the sample size threshold (>5 games).")
        return pd.DataFrame()
        
    df = pd.DataFrame(results)
    
    print("\n📊 TOP FINISHERS (Goals > xG)")
    print("-" * 50)
    print(df.sort_values('finish_pg', ascending=False)[['team', 'finish_pg', 'corr_xg', 'samples']].head(10).to_string(index=False))
    
    print("\n\n📉 UNDERPERFORMERS (Goals < xG)")
    print("-" * 50)
    print(df.sort_values('finish_pg', ascending=True)[['team', 'finish_pg', 'corr_xg', 'samples']].head(10).to_string(index=False))
    
    print("\n\n🤖 MOST PREDICTABLE OFFENSES (High xG Correlation)")
    print("-" * 50)
    print(df.sort_values('corr_xg', ascending=False)[['team', 'corr_xg', 'finish_pg', 'samples']].head(10).to_string(index=False))

    return df

if __name__ == "__main__":
    analyze_drivers()
