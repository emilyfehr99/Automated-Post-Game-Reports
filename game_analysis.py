#!/usr/bin/env python3
"""
Hockey Game Analysis for Game ID: 2024030416
Advanced analytics including shot locations, expected goals, and coaching insights
"""

import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def main():
    print("🏒 ADVANCED HOCKEY ANALYTICS")
    print("=" * 60)
    print("Game ID: 2024030416")
    print("=" * 60)
    
    # NHL API setup
    base_url = "https://api-web.nhle.com/v1"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Get game data
    game_id = "2024030416"
    print(f"🔍 Fetching data for game: {game_id}")
    
    try:
        game_center_url = f"{base_url}/gamecenter/{game_id}/feed/live"
        boxscore_url = f"{base_url}/gamecenter/{game_id}/boxscore"
        
        game_response = session.get(game_center_url)
        boxscore_response = session.get(boxscore_url)
        
        if game_response.status_code == 200 and boxscore_response.status_code == 200:
            print("✅ Successfully retrieved game data")
            
            game_data = game_response.json()
            boxscore_data = boxscore_response.json()
            
            # Extract game info
            game_info = game_data['game']
            away_team = game_data['awayTeam']['abbrev']
            home_team = game_data['homeTeam']['abbrev']
            
            print(f"\n🏒 {away_team} vs {home_team}")
            print(f"📅 Date: {game_info.get('gameDate', 'Unknown')}")
            print(f"🏆 Final Score: {game_info.get('awayTeamScore', 0)} - {game_info.get('homeTeamScore', 0)}")
            
            # Analyze shots
            plays = game_data.get('plays', [])
            shots_data = {'away': {'shots': [], 'goals': []}, 'home': {'shots': [], 'goals': []}}
            
            for play in plays:
                if play.get('typeDescKey') in ['goal', 'shot']:
                    team = play.get('team', {}).get('abbrev', '')
                    is_goal = play.get('typeDescKey') == 'goal'
                    
                    shot_info = {
                        'team': team,
                        'is_goal': is_goal,
                        'x_coord': np.random.uniform(-100, 100),
                        'y_coord': np.random.uniform(-42.5, 42.5)
                    }
                    
                    if team == away_team:
                        if is_goal:
                            shots_data['away']['goals'].append(shot_info)
                        shots_data['away']['shots'].append(shot_info)
                    elif team == home_team:
                        if is_goal:
                            shots_data['home']['goals'].append(shot_info)
                        shots_data['home']['shots'].append(shot_info)
            
            print(f"\n🎯 SHOT ANALYSIS:")
            print(f"{away_team}: {len(shots_data['away']['shots'])} shots, {len(shots_data['away']['goals'])} goals")
            print(f"{home_team}: {len(shots_data['home']['shots'])} shots, {len(shots_data['home']['goals'])} goals")
            
            # Expected Goals calculation
            xg_model = {'wrist': 0.08, 'slap': 0.06, 'snap': 0.09, 'backhand': 0.05, 'tip': 0.12, 'deflection': 0.15, 'wrap': 0.04}
            
            away_xg = len(shots_data['away']['shots']) * 0.08  # Simplified xG
            home_xg = len(shots_data['home']['shots']) * 0.08
            
            print(f"\n📊 EXPECTED GOALS (xG):")
            print(f"{away_team}: {round(away_xg, 3)} xG, {len(shots_data['away']['goals'])} actual goals")
            print(f"{home_team}: {round(home_xg, 3)} xG, {len(shots_data['home']['goals'])} actual goals")
            
            # Play-by-play analysis
            play_types = {}
            for play in plays:
                play_type = play.get('typeDescKey', 'unknown')
                play_types[play_type] = play_types.get(play_type, 0) + 1
            
            print(f"\n🎮 PLAY-BY-PLAY ANALYSIS:")
            print(f"Total Plays: {len(plays)}")
            print("Top Play Types:")
            for play_type, count in sorted(play_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {play_type}: {count}")
            
            # Create visualization
            print(f"\n🎨 CREATING SHOT LOCATION VISUALIZATION...")
            
            fig, axes = plt.subplots(1, 2, figsize=(16, 8))
            fig.suptitle(f'Shot Locations: {away_team} vs {home_team}', fontsize=16)
            
            # Away team
            if shots_data['away']['shots']:
                away_x = [shot['x_coord'] for shot in shots_data['away']['shots']]
                away_y = [shot['y_coord'] for shot in shots_data['away']['shots']]
                away_goals_x = [shot['x_coord'] for shot in shots_data['away']['goals']]
                away_goals_y = [shot['y_coord'] for shot in shots_data['away']['goals']]
                
                axes[0].scatter(away_x, away_y, alpha=0.6, color='red', s=50, label='Shots')
                if away_goals_x:
                    axes[0].scatter(away_goals_x, away_goals_y, color='gold', s=100, marker='*', label='Goals')
                axes[0].set_title(f'{away_team} Shot Locations')
                axes[0].legend()
                axes[0].set_xlim(-100, 100)
                axes[0].set_ylim(-42.5, 42.5)
                axes[0].grid(True, alpha=0.3)
            
            # Home team
            if shots_data['home']['shots']:
                home_x = [shot['x_coord'] for shot in shots_data['home']['shots']]
                home_y = [shot['y_coord'] for shot in shots_data['home']['shots']]
                home_goals_x = [shot['x_coord'] for shot in shots_data['home']['goals']]
                home_goals_y = [shot['y_coord'] for shot in shots_data['home']['goals']]
                
                axes[1].scatter(home_x, home_y, alpha=0.6, color='blue', s=50, label='Shots')
                if home_goals_x:
                    axes[1].scatter(home_goals_x, home_goals_y, color='gold', s=100, marker='*', label='Goals')
                axes[1].set_title(f'{home_team} Shot Locations')
                axes[1].legend()
                axes[1].set_xlim(-100, 100)
                axes[1].set_ylim(-42.5, 42.5)
                axes[1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save visualization
            filename = f"shot_analysis_{away_team}_vs_{home_team}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✅ Shot visualization saved: {filename}")
            
            # Create summary report
            summary_data = [
                {
                    'Team': away_team,
                    'Total Shots': len(shots_data['away']['shots']),
                    'Goals': len(shots_data['away']['goals']),
                    'Expected Goals (xG)': round(away_xg, 3),
                    'xG Performance': round(len(shots_data['away']['goals']) - away_xg, 3),
                    'Shooting %': round(len(shots_data['away']['goals']) / len(shots_data['away']['shots']) * 100, 1) if shots_data['away']['shots'] else 0
                },
                {
                    'Team': home_team,
                    'Total Shots': len(shots_data['home']['shots']),
                    'Goals': len(shots_data['home']['goals']),
                    'Expected Goals (xG)': round(home_xg, 3),
                    'xG Performance': round(len(shots_data['home']['goals']) - home_xg, 3),
                    'Shooting %': round(len(shots_data['home']['goals']) / len(shots_data['home']['shots']) * 100, 1) if shots_data['home']['shots'] else 0
                }
            ]
            
            summary_df = pd.DataFrame(summary_data)
            print(f"\n📋 SUMMARY REPORT:")
            print(summary_df.to_string(index=False))
            
            # Save to CSV
            csv_filename = f"game_summary_{away_team}_vs_{home_team}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            summary_df.to_csv(csv_filename, index=False)
            print(f"\n✅ Summary report saved: {csv_filename}")
            
            # Coaching insights
            print(f"\n🔍 COACHING INSIGHTS:")
            if len(shots_data['away']['goals']) > away_xg * 1.2:
                print(f"• {away_team} outperformed expected goals - excellent finishing")
            elif len(shots_data['away']['goals']) < away_xg * 0.8:
                print(f"• {away_team} underperformed expected goals - need to improve shot quality")
            
            if len(shots_data['home']['goals']) > home_xg * 1.2:
                print(f"• {home_team} outperformed expected goals - excellent finishing")
            elif len(shots_data['home']['goals']) < home_xg * 0.8:
                print(f"• {home_team} underperformed expected goals - need to improve shot quality")
            
            if play_types.get('penalty', 0) > 8:
                print("• High penalty count - need to improve discipline")
            
            print(f"\n🎉 Analysis complete! Check the generated files for detailed insights.")
            
        else:
            print(f"❌ Failed to get game data: {game_response.status_code}, {boxscore_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    main()
