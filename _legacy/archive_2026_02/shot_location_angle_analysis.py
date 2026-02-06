#!/usr/bin/env python3
"""
Shot location and angle analysis for goalie scouting
Calculates save percentage by location and shot angles to the net
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import math

def analyze_shot_locations_and_angles():
    # Load the data
    print("Loading goalie data...")
    df = pd.read_csv('/Users/emilyfehr8/Desktop/goalie stuff incl.csv')
    
    # Identify goalies and their teams
    goalie_actions = df[df['action'].isin(['Saves', 'Goals against'])]
    goalies = goalie_actions['player'].unique()
    goalie_teams = {}
    for goalie in goalies:
        team = goalie_actions[goalie_actions['player'] == goalie]['team'].iloc[0]
        goalie_teams[goalie] = team
    
    # Add goalie team column
    df['goalie_team'] = df['player'].map(goalie_teams)
    
    # Filter for goalie-specific data
    goalie_data = df[df['player'].isin(goalies)].copy()
    
    # Net location (from previous analysis)
    net_x = 60.69
    net_y = 12.96
    
    print("=== SHOT LOCATION AND ANGLE ANALYSIS ===")
    print(f"Defending net location: X = {net_x:.2f}, Y = {net_y:.2f}")
    print(f"Goalies analyzed: {list(goalies)}")
    
    # Calculate shot angles and distances
    def calculate_shot_angle(shot_x, shot_y, net_x, net_y):
        """Calculate angle from shot location to net center"""
        dx = net_x - shot_x
        dy = net_y - shot_y
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        # Normalize to 0-360 degrees
        if angle_deg < 0:
            angle_deg += 360
        return angle_deg
    
    def calculate_shot_distance(shot_x, shot_y, net_x, net_y):
        """Calculate distance from shot to net"""
        return math.sqrt((shot_x - net_x)**2 + (shot_y - net_y)**2)
    
    # Add shot metrics to data
    goalie_data['shot_distance'] = goalie_data.apply(
        lambda row: calculate_shot_distance(row['pos_x'], row['pos_y'], net_x, net_y), axis=1
    )
    goalie_data['shot_angle'] = goalie_data.apply(
        lambda row: calculate_shot_angle(row['pos_x'], row['pos_y'], net_x, net_y), axis=1
    )
    
    # Analyze by goalie
    goalie_analysis = []
    
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        saves = goalie_subset[goalie_subset['action'] == 'Saves']
        goals = goalie_subset[goalie_subset['action'] == 'Goals against']
        
        # Basic metrics
        total_shots = len(saves) + len(goals)
        save_pct = (len(saves) / total_shots * 100) if total_shots > 0 else 0
        
        # Distance metrics
        avg_distance = goalie_subset['shot_distance'].mean()
        min_distance = goalie_subset['shot_distance'].min()
        max_distance = goalie_subset['shot_distance'].max()
        
        # Angle metrics
        avg_angle = goalie_subset['shot_angle'].mean()
        angle_std = goalie_subset['shot_angle'].std()
        
        # High-danger area (close shots)
        close_shots = goalie_subset[goalie_subset['shot_distance'] < 15]
        close_saves = len(close_shots[close_shots['action'] == 'Saves'])
        close_goals = len(close_shots[close_shots['action'] == 'Goals against'])
        close_save_pct = (close_saves / (close_saves + close_goals) * 100) if (close_saves + close_goals) > 0 else 0
        
        # Far shots
        far_shots = goalie_subset[goalie_subset['shot_distance'] >= 15]
        far_saves = len(far_shots[far_shots['action'] == 'Saves'])
        far_goals = len(far_shots[far_shots['action'] == 'Goals against'])
        far_save_pct = (far_saves / (far_saves + far_goals) * 100) if (far_saves + far_goals) > 0 else 0
        
        # Angle analysis - shots from different angles
        # Front of net (angles 0-30 and 330-360)
        front_angles = goalie_subset[
            (goalie_subset['shot_angle'] <= 30) | (goalie_subset['shot_angle'] >= 330)
        ]
        front_saves = len(front_angles[front_angles['action'] == 'Saves'])
        front_goals = len(front_angles[front_angles['action'] == 'Goals against'])
        front_save_pct = (front_saves / (front_saves + front_goals) * 100) if (front_saves + front_goals) > 0 else 0
        
        # Side angles (30-150 and 210-330)
        side_angles = goalie_subset[
            ((goalie_subset['shot_angle'] > 30) & (goalie_subset['shot_angle'] <= 150)) |
            ((goalie_subset['shot_angle'] > 210) & (goalie_subset['shot_angle'] < 330))
        ]
        side_saves = len(side_angles[side_angles['action'] == 'Saves'])
        side_goals = len(side_angles[side_angles['action'] == 'Goals against'])
        side_save_pct = (side_saves / (side_saves + side_goals) * 100) if (side_saves + side_goals) > 0 else 0
        
        # Behind net angles (150-210)
        behind_angles = goalie_subset[
            (goalie_subset['shot_angle'] > 150) & (goalie_subset['shot_angle'] <= 210)
        ]
        behind_saves = len(behind_angles[behind_angles['action'] == 'Saves'])
        behind_goals = len(behind_angles[behind_angles['action'] == 'Goals against'])
        behind_save_pct = (behind_saves / (behind_saves + behind_goals) * 100) if (behind_saves + behind_goals) > 0 else 0
        
        goalie_analysis.append({
            'goalie': goalie,
            'team': goalie_teams[goalie],
            'total_shots': total_shots,
            'saves': len(saves),
            'goals': len(goals),
            'save_pct': save_pct,
            'avg_distance': avg_distance,
            'min_distance': min_distance,
            'max_distance': max_distance,
            'avg_angle': avg_angle,
            'angle_std': angle_std,
            'close_save_pct': close_save_pct,
            'far_save_pct': far_save_pct,
            'front_save_pct': front_save_pct,
            'side_save_pct': side_save_pct,
            'behind_save_pct': behind_save_pct,
            'close_shots': close_saves + close_goals,
            'far_shots': far_saves + far_goals,
            'front_shots': front_saves + front_goals,
            'side_shots': side_saves + side_goals,
            'behind_shots': behind_saves + behind_goals
        })
    
    # Convert to DataFrame
    analysis_df = pd.DataFrame(goalie_analysis)
    
    print("\n=== SHOT LOCATION AND ANGLE METRICS ===")
    print(analysis_df[['goalie', 'team', 'save_pct', 'avg_distance', 'close_save_pct', 'far_save_pct', 'front_save_pct', 'side_save_pct']].to_string(index=False))
    
    # Create visualizations
    print("\n=== CREATING SHOT LOCATION AND ANGLE VISUALIZATIONS ===")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Plot 1: Save percentage by distance
    axes[0, 0].bar(analysis_df['goalie'], analysis_df['close_save_pct'], 
                   alpha=0.7, label='Close Range (<15 units)', color='red')
    axes[0, 0].bar(analysis_df['goalie'], analysis_df['far_save_pct'], 
                   alpha=0.7, label='Far Range (≥15 units)', color='blue')
    axes[0, 0].set_title('Save Percentage by Shot Distance')
    axes[0, 0].set_ylabel('Save Percentage (%)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Save percentage by angle
    x = np.arange(len(analysis_df))
    width = 0.25
    axes[0, 1].bar(x - width, analysis_df['front_save_pct'], width, label='Front of Net', color='green')
    axes[0, 1].bar(x, analysis_df['side_save_pct'], width, label='Side Angles', color='orange')
    axes[0, 1].bar(x + width, analysis_df['behind_save_pct'], width, label='Behind Net', color='purple')
    axes[0, 1].set_title('Save Percentage by Shot Angle')
    axes[0, 1].set_ylabel('Save Percentage (%)')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(analysis_df['goalie'], rotation=45)
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Shot distance distribution
    for i, goalie in enumerate(goalies):
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        distances = goalie_subset['shot_distance']
        axes[0, 2].hist(distances, bins=15, alpha=0.6, label=goalie, color=plt.cm.tab10(i))
    
    axes[0, 2].set_xlabel('Shot Distance from Net')
    axes[0, 2].set_ylabel('Frequency')
    axes[0, 2].set_title('Shot Distance Distribution by Goalie')
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3)
    
    # Plot 4: Shot angle distribution
    for i, goalie in enumerate(goalies):
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        angles = goalie_subset['shot_angle']
        axes[1, 0].hist(angles, bins=20, alpha=0.6, label=goalie, color=plt.cm.tab10(i))
    
    axes[1, 0].set_xlabel('Shot Angle (degrees)')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Shot Angle Distribution by Goalie')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 5: Shot location heat map (save percentage)
    # Create a grid for heat map
    x_min, x_max = goalie_data['pos_x'].min(), goalie_data['pos_x'].max()
    y_min, y_max = goalie_data['pos_y'].min(), goalie_data['pos_y'].max()
    
    # Create grid
    x_bins = np.linspace(x_min, x_max, 20)
    y_bins = np.linspace(y_min, y_max, 15)
    
    # Calculate save percentage for each grid cell
    heatmap_data = np.zeros((len(y_bins)-1, len(x_bins)-1))
    
    for i in range(len(y_bins)-1):
        for j in range(len(x_bins)-1):
            # Find shots in this grid cell
            cell_shots = goalie_data[
                (goalie_data['pos_x'] >= x_bins[j]) & (goalie_data['pos_x'] < x_bins[j+1]) &
                (goalie_data['pos_y'] >= y_bins[i]) & (goalie_data['pos_y'] < y_bins[i+1])
            ]
            
            if len(cell_shots) > 0:
                saves = len(cell_shots[cell_shots['action'] == 'Saves'])
                goals = len(cell_shots[cell_shots['action'] == 'Goals against'])
                heatmap_data[i, j] = (saves / (saves + goals) * 100) if (saves + goals) > 0 else 0
            else:
                heatmap_data[i, j] = np.nan
    
    im = axes[1, 1].imshow(heatmap_data, cmap='RdYlGn', aspect='auto', 
                           extent=[x_min, x_max, y_min, y_max], vmin=0, vmax=100)
    axes[1, 1].scatter(net_x, net_y, c='black', s=200, marker='s', label='Net')
    axes[1, 1].set_xlabel('X Position')
    axes[1, 1].set_ylabel('Y Position')
    axes[1, 1].set_title('Save Percentage Heat Map')
    axes[1, 1].legend()
    plt.colorbar(im, ax=axes[1, 1], label='Save Percentage (%)')
    
    # Plot 6: Shot locations with angles
    colors = ['red', 'blue', 'green', 'orange']
    for i, goalie in enumerate(goalies):
        goalie_saves = goalie_data[(goalie_data['player'] == goalie) & (goalie_data['action'] == 'Saves')]
        goalie_goals = goalie_data[(goalie_data['player'] == goalie) & (goalie_data['action'] == 'Goals against')]
        
        # Plot saves
        axes[1, 2].scatter(goalie_saves['pos_x'], goalie_saves['pos_y'], 
                          c=colors[i % len(colors)], alpha=0.6, label=f'{goalie} (Saves)', s=50)
        
        # Plot goals
        if len(goalie_goals) > 0:
            axes[1, 2].scatter(goalie_goals['pos_x'], goalie_goals['pos_y'], 
                              c=colors[i % len(colors)], alpha=0.8, label=f'{goalie} (Goals)', s=100, marker='x')
        
        # Draw angle lines for a few shots
        sample_shots = goalie_saves.sample(min(5, len(goalie_saves)))
        for _, shot in sample_shots.iterrows():
            axes[1, 2].plot([shot['pos_x'], net_x], [shot['pos_y'], net_y], 
                           color=colors[i % len(colors)], alpha=0.3, linewidth=1)
    
    axes[1, 2].scatter(net_x, net_y, c='black', s=200, marker='s', label='Net')
    axes[1, 2].set_xlabel('X Position')
    axes[1, 2].set_ylabel('Y Position')
    axes[1, 2].set_title('Shot Locations with Angle Lines')
    axes[1, 2].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/emilyfehr8/CascadeProjects/shot_location_angle_analysis.png', 
                dpi=300, bbox_inches='tight')
    print("Shot location and angle analysis saved as 'shot_location_angle_analysis.png'")
    
    # Create detailed scouting report
    print("\n=== DETAILED SHOT LOCATION SCOUTING REPORT ===")
    for _, row in analysis_df.iterrows():
        print(f"\n--- {row['goalie']} ({row['team']}) ---")
        print(f"Overall Save Percentage: {row['save_pct']:.1f}% ({row['saves']} saves, {row['goals']} goals)")
        print(f"Average Shot Distance: {row['avg_distance']:.2f} units")
        print(f"Shot Distance Range: {row['min_distance']:.2f} - {row['max_distance']:.2f} units")
        print(f"Average Shot Angle: {row['avg_angle']:.1f}°")
        
        print(f"\nSave Percentage by Distance:")
        print(f"  Close Range (<15 units): {row['close_save_pct']:.1f}% ({row['close_shots']} shots)")
        print(f"  Far Range (≥15 units): {row['far_save_pct']:.1f}% ({row['far_shots']} shots)")
        
        print(f"\nSave Percentage by Angle:")
        print(f"  Front of Net (0-30°, 330-360°): {row['front_save_pct']:.1f}% ({row['front_shots']} shots)")
        print(f"  Side Angles (30-150°, 210-330°): {row['side_save_pct']:.1f}% ({row['side_shots']} shots)")
        print(f"  Behind Net (150-210°): {row['behind_save_pct']:.1f}% ({row['behind_shots']} shots)")
        
        # Scouting insights
        print(f"\n📍 SCOUTING INSIGHTS:")
        if row['close_save_pct'] < 70:
            print(f"  - Vulnerable to close-range shots ({row['close_save_pct']:.1f}% save rate)")
        if row['far_save_pct'] > 90:
            print(f"  - Excellent on long-range shots ({row['far_save_pct']:.1f}% save rate)")
        if row['front_save_pct'] < 60:
            print(f"  - Weak on shots from front of net ({row['front_save_pct']:.1f}% save rate)")
        if row['side_save_pct'] > 85:
            print(f"  - Strong on side-angle shots ({row['side_save_pct']:.1f}% save rate)")
    
    return analysis_df, goalie_data

if __name__ == "__main__":
    analysis_df, goalie_data = analyze_shot_locations_and_angles()
