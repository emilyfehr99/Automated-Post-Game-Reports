import json
import pandas as pd
from pathlib import Path

def analyze_efficiency():
    print("🏒 ANALYZING SCORING EFFICIENCY (FINISH FACTOR)")
    print("=" * 60)
    
    path = Path('season_2025_2026_team_stats.json')
    if not path.exists():
        print("❌ Stats file not found.")
        return
        
    with open(path, 'r') as f:
        data = json.load(f)
        
    teams_data = data.get('teams', {})
    
    results = []
    
    for team, stats in teams_data.items():
        xg_sum = stats.get('xg_sum', 0)
        gs_sum = stats.get('gs_sum', 0)
        gp = stats.get('games_played', 1)
        
        if gp < 5 or xg_sum == 0:
            continue
            
        finish_factor = gs_sum / xg_sum
        goals_above_expected = gs_sum - xg_sum
        gae_per_game = goals_above_expected / gp
        
        results.append({
            'team': team,
            'gp': gp,
            'finish_factor': finish_factor,
            'xg_avg': stats.get('xg_avg', 0),
            'goals_avg': stats.get('gs_avg', 0),
            'gae_pg': gae_per_game
        })
        
    df = pd.DataFrame(results)
    
    print("\n🎯 ELITE FINISHERS (Snipers / High Skill)")
    print("   (Teams that score purely on shooting talent, independent of chance volume)")
    print("-" * 60)
    print(df.sort_values('finish_factor', ascending=False)[
        ['team', 'finish_factor', 'xg_avg', 'goals_avg', 'gae_pg']
    ].head(10).to_string(index=False, formatters={
        'finish_factor': '{:.2f}x'.format,
        'xg_avg': '{:.2f}'.format,
        'goals_avg': '{:.2f}'.format,
        'gae_pg': '{:+.2f}'.format
    }))
    
    print("\n\n🧱 SNAKEBITTEN / LOW FINISH (Volume Reliant)")
    print("   (Teams that need HIGH xG to score because they miss often)")
    print("-" * 60)
    print(df.sort_values('finish_factor', ascending=True)[
        ['team', 'finish_factor', 'xg_avg', 'goals_avg', 'gae_pg']
    ].head(10).to_string(index=False, formatters={
        'finish_factor': '{:.2f}x'.format,
        'xg_avg': '{:.2f}'.format,
        'goals_avg': '{:.2f}'.format,
        'gae_pg': '{:+.2f}'.format
    }))
    
    # Save the factors for the model to use
    profile_data = {
        row['team']: row['finish_factor'] 
        for _, row in df.iterrows()
    }
    
    with open('team_scoring_profiles.json', 'w') as f:
        json.dump(profile_data, f, indent=2)
        print("\n✅ Saved Team Finishing Profiles to 'team_scoring_profiles.json'")

if __name__ == "__main__":
    analyze_efficiency()
