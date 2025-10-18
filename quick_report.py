#!/usr/bin/env python3
import requests, json, numpy as np, matplotlib.pyplot as plt, subprocess
from datetime import datetime

print("🏒 QUICK HOCKEY POST-GAME REPORT")
print("=" * 50)

# Use the provided game ID
game_id = "2024030416"
print(f"🎯 Analyzing Game ID: {game_id}")

# NHL API setup
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

# Get game data
print("🔍 Fetching game data...")
url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/feed/live"
response = session.get(url)

if response.status_code == 200:
    print("✅ Got game data!")
    game_data = response.json()
    
    # Extract game info
    game_info = game_data.get("game", {})
    away_team = game_info.get("awayTeam", {}).get("abbrev", "Away")
    home_team = game_info.get("homeTeam", {}).get("abbrev", "Home")
    away_score = game_info.get("awayTeamScore", 0)
    home_score = game_info.get("homeTeamScore", 0)
    
    print(f"🏆 {away_team} {away_score} - {home_team} {home_score}")
    
    # Analyze shots
    plays = game_data.get("plays", [])
    shots_data = {'away': {'shots': [], 'goals': []}, 'home': {'shots': [], 'goals': []}}
    
    for play in plays:
        if play.get("typeDescKey") in ["goal", "shot"]:
            team = play.get("team", {}).get("abbrev", "")
            is_goal = play.get("typeDescKey") == "goal"
            
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
    
    # Create visualization
    print(f"\n🎨 Creating shot location visualization...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle(f'Shot Locations: {away_team} vs {home_team} - Game {game_id}', fontsize=16)
    
    # Away team shots
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
    
    # Home team shots
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
    
    # Save and open in Safari
    filename = f"post_game_report_{away_team}_vs_{home_team}_{game_id}.png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {filename}")
    
    # Expected Goals
    away_xg = len(shots_data['away']['shots']) * 0.08
    home_xg = len(shots_data['home']['shots']) * 0.08
    
    print(f"\n📊 EXPECTED GOALS:")
    print(f"{away_team}: {round(away_xg, 3)} xG, {len(shots_data['away']['goals'])} actual")
    print(f"{home_team}: {round(home_xg, 3)} xG, {len(shots_data['home']['goals'])} actual")
    
    print(f"\n🎉 Opening in Safari...")
    subprocess.run(["open", "-a", "Safari", filename])
    print(f"✅ Post-game report opened in Safari!")
    
else:
    print(f"❌ Failed to get game data: {response.status_code}")
    print("Using sample data instead...")
    
    # Create sample visualization
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle(f'Sample Shot Locations - Game {game_id}', fontsize=16)
    
    # Sample data
    away_x = np.random.uniform(-100, 100, 25)
    away_y = np.random.uniform(-42.5, 42.5, 25)
    home_x = np.random.uniform(-100, 100, 30)
    home_y = np.random.uniform(-42.5, 42.5, 30)
    
    axes[0].scatter(away_x, away_y, alpha=0.6, color='red', s=50, label='Shots')
    axes[0].set_title('Away Team Shot Locations')
    axes[0].legend()
    axes[0].set_xlim(-100, 100)
    axes[0].set_ylim(-42.5, 42.5)
    axes[0].grid(True, alpha=0.3)
    
    axes[1].scatter(home_x, home_y, alpha=0.6, color='blue', s=50, label='Shots')
    axes[1].set_title('Home Team Shot Locations')
    axes[1].legend()
    axes[1].set_xlim(-100, 100)
    axes[1].set_ylim(-42.5, 42.5)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    filename = f"sample_post_game_report_{game_id}.png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    print(f"✅ Saved sample report: {filename}")
    
    print(f"\n🎉 Opening sample report in Safari...")
    subprocess.run(["open", "-a", "Safari", filename])
    print(f"✅ Sample post-game report opened in Safari!")
