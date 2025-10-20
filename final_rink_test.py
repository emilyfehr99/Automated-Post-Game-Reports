#!/usr/bin/env python3
"""
Final test to generate a plot with the new rink image and actual shot data
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.image import imread
from nhl_api_client import NHLAPIClient

def final_rink_test():
    """Generate final test plot with new rink image and actual shot data"""
    
    print("🏒 Final Rink Image Test with Actual Shot Data")
    print("=" * 55)
    
    # Get game data
    nhl_client = NHLAPIClient()
    game_id = '2025020092'
    game_data = nhl_client.get_comprehensive_game_data(game_id)
    
    if not game_data:
        print("❌ Could not fetch game data")
        return
    
    # Get team information
    away_team = game_data.get('boxscore', {}).get('awayTeam', {})
    home_team = game_data.get('boxscore', {}).get('homeTeam', {})
    
    away_team_id = away_team.get('id')
    home_team_id = home_team.get('id')
    
    print(f"Teams: {away_team.get('abbrev')} @ {home_team.get('abbrev')}")
    
    # Extract shots (same logic as report generator)
    away_shots = []
    home_shots = []
    away_goals = []
    home_goals = []
    
    plays = game_data.get('play_by_play', {}).get('plays', [])
    
    for play in plays:
        details = play.get('details', {})
        event_type = play.get('typeDescKey', '')
        event_team = details.get('eventOwnerTeamId')
        
        x_coord = details.get('xCoord', 0)
        y_coord = details.get('yCoord', 0)
        
        if x_coord is not None and y_coord is not None:
            if event_team == away_team_id and event_type in ['shot-on-goal', 'missed-shot', 'blocked-shot']:
                if x_coord > 0:
                    flipped_x, flipped_y = -x_coord, -y_coord
                else:
                    flipped_x, flipped_y = x_coord, y_coord
                away_shots.append((flipped_x, flipped_y))
                
            elif event_team == away_team_id and event_type == 'goal':
                if x_coord > 0:
                    flipped_x, flipped_y = -x_coord, -y_coord
                else:
                    flipped_x, flipped_y = x_coord, y_coord
                away_goals.append((flipped_x, flipped_y))
                
            elif event_team == home_team_id and event_type in ['shot-on-goal', 'missed-shot', 'blocked-shot']:
                if x_coord < 0:
                    flipped_x, flipped_y = -x_coord, -y_coord
                else:
                    flipped_x, flipped_y = x_coord, y_coord
                home_shots.append((flipped_x, flipped_y))
                
            elif event_team == home_team_id and event_type == 'goal':
                if x_coord < 0:
                    flipped_x, flipped_y = -x_coord, -y_coord
                else:
                    flipped_x, flipped_y = x_coord, y_coord
                home_goals.append((flipped_x, flipped_y))
    
    print(f"Extracted: {len(away_shots)} away shots, {len(home_shots)} home shots")
    print(f"Goals: {len(away_goals)} away goals, {len(home_goals)} home goals")
    
    # Load rink image
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rink_path = os.path.join(script_dir, 'F300E016-E2BD-450A-B624-5BADF3853AC0.jpeg')
    
    print(f"\n🏒 Loading rink image from: {rink_path}")
    print(f"File exists: {os.path.exists(rink_path)}")
    
    if os.path.exists(rink_path):
        file_size = os.path.getsize(rink_path)
        print(f"File size: {file_size} bytes")
    
    # Create the plot
    plt.ioff()
    fig, ax = plt.subplots(figsize=(8, 5.5))
    
    try:
        if os.path.exists(rink_path):
            rink_img = imread(rink_path)
            print(f"✅ Rink image loaded successfully!")
            print(f"   Shape: {rink_img.shape}")
            print(f"   Dtype: {rink_img.dtype}")
            
            # Display the rink image
            ax.imshow(rink_img, extent=[-100, 100, -42.5, 42.5], aspect='equal', alpha=0.75, zorder=0)
            print(f"✅ Rink image displayed on plot")
        else:
            print(f"❌ Rink image not found")
            return
    except Exception as e:
        print(f"❌ Error loading rink image: {e}")
        return
    
    # Plot shots
    if away_shots:
        away_x, away_y = zip(*away_shots)
        ax.scatter(away_x, away_y, c='red', s=30, alpha=0.7, label=f'{away_team.get("abbrev")} Shots', zorder=1)
        print(f"✅ Plotted {len(away_shots)} {away_team.get('abbrev')} shots")
    
    if home_shots:
        home_x, home_y = zip(*home_shots)
        ax.scatter(home_x, home_y, c='blue', s=30, alpha=0.7, label=f'{home_team.get("abbrev")} Shots', zorder=1)
        print(f"✅ Plotted {len(home_shots)} {home_team.get('abbrev')} shots")
    
    # Plot goals
    if away_goals:
        away_gx, away_gy = zip(*away_goals)
        ax.scatter(away_gx, away_gy, c='red', s=100, marker='*', alpha=1.0, label=f'{away_team.get("abbrev")} Goals', zorder=2)
        print(f"✅ Plotted {len(away_goals)} {away_team.get('abbrev')} goals")
    
    if home_goals:
        home_gx, home_gy = zip(*home_goals)
        ax.scatter(home_gx, home_gy, c='blue', s=100, marker='*', alpha=1.0, label=f'{home_team.get("abbrev")} Goals', zorder=2)
        print(f"✅ Plotted {len(home_goals)} {home_team.get('abbrev')} goals")
    
    # Set plot properties
    ax.set_xlim(-100, 100)
    ax.set_ylim(-42.5, 42.5)
    ax.set_title(f'{away_team.get("abbrev")} @ {home_team.get("abbrev")} - Shot Locations with NEW Rink Image')
    ax.legend()
    
    # Save the plot
    output_path = os.path.join(script_dir, 'final_rink_test_plot.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ Final test plot saved to: {output_path}")
    
    if os.path.exists(output_path):
        plot_size = os.path.getsize(output_path)
        print(f"Plot file size: {plot_size} bytes")
    
    # Copy to desktop for inspection
    desktop_path = os.path.expanduser('~/Desktop')
    desktop_output = os.path.join(desktop_path, 'FINAL_RINK_TEST_WITH_SHOTS.png')
    os.system(f'cp "{output_path}" "{desktop_output}"')
    print(f"📁 Copied to desktop: {desktop_output}")
    
    print(f"\n🎯 This plot shows:")
    print(f"   - NEW rink image from your desktop")
    print(f"   - Actual shot data from the game")
    print(f"   - Red dots = BOS shots, Blue dots = UTA shots")
    print(f"   - Stars = Goals")

if __name__ == "__main__":
    final_rink_test()
