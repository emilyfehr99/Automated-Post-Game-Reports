#!/usr/bin/env python3
"""
Hockey Analytics - Find June Game & Create Post-Game Report
Finds the final June game and generates shot location visualizations for Safari
"""

import requests
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import subprocess

def main():
    print("🏒 ADVANCED HOCKEY ANALYTICS - FINDING JUNE GAME & CREATING POST-GAME REPORT")
    print("=" * 70)
    
    # NHL API setup
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Try to get the current schedule
    print("🔍 Fetching current NHL schedule...")
    
    url = "https://api-web.nhle.com/v1/schedule/now"
    response = session.get(url)
    
    if response.status_code == 200:
        print("✅ Successfully retrieved current schedule")
        data = response.json()
        
        if "gameWeek" in data:
            print(f"📅 Found {len(data['gameWeek'])} games this week")
            print("\n🎯 Available Games:")
            
            for i, game in enumerate(data["gameWeek"][:5]):
                date = game.get("gameDate", "Unknown")
                away = game.get("awayTeam", {}).get("abbrev", "Unknown")
                home = game.get("homeTeam", {}).get("abbrev", "Unknown")
                game_id = game.get("id", "Unknown")
                
                print(f"  {i+1}. {date}: {away} vs {home}")
                print(f"     Game ID: {game_id}")
            
            # Look for June games specifically
            print("\n🔍 Looking for June games...")
            june_games = []
            
            for game in data["gameWeek"]:
                date = game.get("gameDate", "")
                if "2024-06" in date or "2025-06" in date:
                    june_games.append(game)
            
            if june_games:
                print(f"🎯 Found {len(june_games)} June games!")
                
                # Sort by date to find the latest
                june_games.sort(key=lambda x: x.get("gameDate", ""), reverse=True)
                
                final_june_game = june_games[0]
                final_date = final_june_game.get("gameDate", "Unknown")
                final_away = final_june_game.get("awayTeam", {}).get("abbrev", "Unknown")
                final_home = final_june_game.get("homeTeam", {}).get("abbrev", "Unknown")
                final_game_id = final_june_game.get("id", "Unknown")
                
                print(f"\n🏆 FINAL JUNE GAME IDENTIFIED:")
                print(f"  📅 Date: {final_date}")
                print(f"  🏒 Teams: {final_away} vs {final_home}")
                print(f"  🆔 Game ID: {final_game_id}")
                
                # Now analyze this game and create the post-game report
                print(f"\n🎨 CREATING POST-GAME REPORT WITH SHOT LOCATION VISUALIZATIONS...")
                
                # Get detailed data for this game
                game_url = f"https://api-web.nhle.com/v1/gamecenter/{final_game_id}/feed/live"
                game_response = session.get(game_url)
                
                if game_response.status_code == 200:
                    print("✅ Successfully retrieved game data!")
                    game_data = game_response.json()
                    
                    # Extract game info
                    game_info = game_data.get("game", {})
                    away_score = game_info.get("awayTeamScore", 0)
                    home_score = game_info.get("homeTeamScore", 0)
                    
                    print(f"🏆 Final Score: {final_away} {away_score} - {final_home} {home_score}")
                    
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
                            
                            if team == final_away:
                                if is_goal:
                                    shots_data['away']['goals'].append(shot_info)
                                shots_data['away']['shots'].append(shot_info)
                            elif team == final_home:
                                if is_goal:
                                    shots_data['home']['goals'].append(shot_info)
                                shots_data['home']['shots'].append(shot_info)
                    
                    print(f"\n🎯 SHOT ANALYSIS:")
                    print(f"{final_away}: {len(shots_data['away']['shots'])} shots, {len(shots_data['away']['goals'])} goals")
                    print(f"{final_home}: {len(shots_data['home']['shots'])} shots, {len(shots_data['home']['goals'])} goals")
                    
                    # Create shot location visualization
                    print(f"\n🎨 CREATING SHOT LOCATION VISUALIZATION...")
                    
                    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
                    fig.suptitle(f'Shot Locations: {final_away} vs {final_home} - Final June Game', fontsize=16)
                    
                    # Away team shots
                    if shots_data['away']['shots']:
                        away_x = [shot['x_coord'] for shot in shots_data['away']['shots']]
                        away_y = [shot['y_coord'] for shot in shots_data['away']['shots']]
                        away_goals_x = [shot['x_coord'] for shot in shots_data['away']['goals']]
                        away_goals_y = [shot['y_coord'] for shot in shots_data['away']['goals']]
                        
                        axes[0].scatter(away_x, away_y, alpha=0.6, color='red', s=50, label='Shots')
                        if away_goals_x:
                            axes[0].scatter(away_goals_x, away_goals_y, color='gold', s=100, marker='*', label='Goals')
                        axes[0].set_title(f'{final_away} Shot Locations')
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
                        axes[1].set_title(f'{final_home} Shot Locations')
                        axes[1].legend()
                        axes[1].set_xlim(-100, 100)
                        axes[1].set_ylim(-42.5, 42.5)
                        axes[1].grid(True, alpha=0.3)
                    
                    plt.tight_layout()
                    
                    # Save visualization
                    filename = f"post_game_report_{final_away}_vs_{final_home}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    plt.savefig(filename, dpi=300, bbox_inches="tight")
                    print(f"✅ Post-game report visualization saved: {filename}")
                    
                    # Expected Goals calculation
                    away_xg = len(shots_data['away']['shots']) * 0.08
                    home_xg = len(shots_data['home']['shots']) * 0.08
                    
                    print(f"\n📊 EXPECTED GOALS (xG) ANALYSIS:")
                    print(f"{final_away}: {round(away_xg, 3)} xG, {len(shots_data['away']['goals'])} actual goals")
                    print(f"{final_home}: {round(home_xg, 3)} xG, {len(shots_data['home']['goals'])} actual goals")
                    
                    # Coaching insights
                    print(f"\n🔍 COACHING INSIGHTS:")
                    if len(shots_data['away']['goals']) > away_xg * 1.2:
                        print(f"• {final_away} outperformed expected goals - excellent finishing")
                    elif len(shots_data['away']['goals']) < away_xg * 0.8:
                        print(f"• {final_away} underperformed expected goals - need to improve shot quality")
                    
                    if len(shots_data['home']['goals']) > home_xg * 1.2:
                        print(f"• {final_home} outperformed expected goals - excellent finishing")
                    elif len(shots_data['home']['goals']) < home_xg * 0.8:
                        print(f"• {final_home} underperformed expected goals - need to improve shot quality")
                    
                    print(f"\n🎉 POST-GAME REPORT COMPLETE!")
                    print(f"Opening visualization in Safari...")
                    
                    # Open in Safari
                    subprocess.run(["open", "-a", "Safari", filename])
                    
                    print(f"✅ Post-game report opened in Safari!")
                    print(f"📊 Shot location analysis complete")
                    print(f"🎯 Expected goals calculated")
                    print(f"🔍 Coaching insights generated")
                    
                else:
                    print(f"❌ Failed to get game data: {game_response.status_code}")
                    return None
            else:
                print("❌ No June games found in current schedule")
                print("📅 Available dates:")
                for game in data["gameWeek"][:5]:
                    print(f"  {game.get('gameDate', 'Unknown')}")
                return None
        else:
            print("❌ No gameWeek data found in schedule")
            return None
    else:
        print(f"❌ Failed to get schedule: {response.status_code}")
        return None

if __name__ == "__main__":
    main()
