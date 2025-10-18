#!/usr/bin/env python3
"""
Comprehensive Goalie Analytics Dashboard
Includes all shot location, angle, and sequence analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import math

def create_comprehensive_goalie_dashboard():
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
    
    print("=== COMPREHENSIVE GOALIE ANALYTICS DASHBOARD ===")
    print(f"Defending net location: X = {net_x:.2f}, Y = {net_y:.2f}")
    print(f"Goalies analyzed: {list(goalies)}")
    
    # Calculate shot angles and distances
    def calculate_shot_angle(shot_x, shot_y, net_x, net_y):
        """Calculate angle from shot location to net center"""
        dx = net_x - shot_x
        dy = net_y - shot_y
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
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
    
    # Sort data by start time for sequence analysis
    goalie_data = goalie_data.sort_values('start')
    
    # Create comprehensive dashboard
    fig = plt.figure(figsize=(24, 16))
    gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
    
    # Colors for goalies
    colors = ['red', 'blue', 'green', 'orange']
    
    # 1. Save Percentage by Distance (Top Left)
    ax1 = fig.add_subplot(gs[0, 0])
    
    # Calculate save percentage by distance for each goalie
    distance_analysis = []
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        close_shots = goalie_subset[goalie_subset['shot_distance'] < 15]
        far_shots = goalie_subset[goalie_subset['shot_distance'] >= 15]
        
        close_saves = len(close_shots[close_shots['action'] == 'Saves'])
        close_goals = len(close_shots[close_shots['action'] == 'Goals against'])
        close_save_pct = (close_saves / (close_saves + close_goals) * 100) if (close_saves + close_goals) > 0 else 0
        
        far_saves = len(far_shots[far_shots['action'] == 'Saves'])
        far_goals = len(far_shots[far_shots['action'] == 'Goals against'])
        far_save_pct = (far_saves / (far_saves + far_goals) * 100) if (far_saves + far_goals) > 0 else 0
        
        distance_analysis.append({
            'goalie': goalie,
            'close_save_pct': close_save_pct,
            'far_save_pct': far_save_pct
        })
    
    distance_df = pd.DataFrame(distance_analysis)
    
    x = np.arange(len(distance_df))
    width = 0.35
    ax1.bar(x - width/2, distance_df['close_save_pct'], width, label='Close Range (<15 units)', color='red', alpha=0.7)
    ax1.bar(x + width/2, distance_df['far_save_pct'], width, label='Far Range (≥15 units)', color='blue', alpha=0.7)
    ax1.set_title('Save Percentage by Shot Distance', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Save Percentage (%)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(distance_df['goalie'], rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Save Percentage by Angle (Top Center)
    ax2 = fig.add_subplot(gs[0, 1])
    
    # Calculate save percentage by angle for each goalie
    angle_analysis = []
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        
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
        
        angle_analysis.append({
            'goalie': goalie,
            'front_save_pct': front_save_pct,
            'side_save_pct': side_save_pct,
            'behind_save_pct': behind_save_pct
        })
    
    angle_df = pd.DataFrame(angle_analysis)
    
    x = np.arange(len(angle_df))
    width = 0.25
    ax2.bar(x - width, angle_df['front_save_pct'], width, label='Front of Net', color='green', alpha=0.7)
    ax2.bar(x, angle_df['side_save_pct'], width, label='Side Angles', color='orange', alpha=0.7)
    ax2.bar(x + width, angle_df['behind_save_pct'], width, label='Behind Net', color='purple', alpha=0.7)
    ax2.set_title('Save Percentage by Shot Angle', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Save Percentage (%)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(angle_df['goalie'], rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Shot Distance Distribution (Top Right)
    ax3 = fig.add_subplot(gs[0, 2])
    
    for i, goalie in enumerate(goalies):
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        distances = goalie_subset['shot_distance']
        ax3.hist(distances, bins=15, alpha=0.6, label=goalie, color=colors[i % len(colors)], density=True)
    
    ax3.set_xlabel('Shot Distance from Net')
    ax3.set_ylabel('Density')
    ax3.set_title('Shot Distance Distribution by Goalie', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Shot Angle Distribution (Top Far Right)
    ax4 = fig.add_subplot(gs[0, 3])
    
    for i, goalie in enumerate(goalies):
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        angles = goalie_subset['shot_angle']
        ax4.hist(angles, bins=20, alpha=0.6, label=goalie, color=colors[i % len(colors)], density=True)
    
    ax4.set_xlabel('Shot Angle (degrees)')
    ax4.set_ylabel('Density')
    ax4.set_title('Shot Angle Distribution by Goalie', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Save Percentage Heat Map (Middle Left)
    ax5 = fig.add_subplot(gs[1, 0])
    
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
    
    im = ax5.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', 
                   extent=[x_min, x_max, y_min, y_max], vmin=0, vmax=100)
    ax5.scatter(net_x, net_y, c='black', s=200, marker='s', label='Net')
    ax5.set_xlabel('X Position')
    ax5.set_ylabel('Y Position')
    ax5.set_title('Save Percentage Heat Map', fontsize=14, fontweight='bold')
    ax5.legend()
    plt.colorbar(im, ax=ax5, label='Save Percentage (%)')
    
    # 6. Shot Locations with Angle Lines (Middle Center)
    ax6 = fig.add_subplot(gs[1, 1])
    
    for i, goalie in enumerate(goalies):
        goalie_saves = goalie_data[(goalie_data['player'] == goalie) & (goalie_data['action'] == 'Saves')]
        goalie_goals = goalie_data[(goalie_data['player'] == goalie) & (goalie_data['action'] == 'Goals against')]
        
        # Plot saves
        ax6.scatter(goalie_saves['pos_x'], goalie_saves['pos_y'], 
                   c=colors[i % len(colors)], alpha=0.6, label=f'{goalie} (Saves)', s=50)
        
        # Plot goals
        if len(goalie_goals) > 0:
            ax6.scatter(goalie_goals['pos_x'], goalie_goals['pos_y'], 
                       c=colors[i % len(colors)], alpha=0.8, label=f'{goalie} (Goals)', s=100, marker='x')
        
        # Draw angle lines for a few shots
        sample_shots = goalie_saves.sample(min(3, len(goalie_saves)))
        for _, shot in sample_shots.iterrows():
            ax6.plot([shot['pos_x'], net_x], [shot['pos_y'], net_y], 
                    color=colors[i % len(colors)], alpha=0.3, linewidth=1)
    
    ax6.scatter(net_x, net_y, c='black', s=200, marker='s', label='Net')
    ax6.set_xlabel('X Position')
    ax6.set_ylabel('Y Position')
    ax6.set_title('Shot Locations with Angle Lines', fontsize=14, fontweight='bold')
    ax6.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax6.grid(True, alpha=0.3)
    
    # 7. Save Percentage After Pass (Middle Right)
    ax7 = fig.add_subplot(gs[1, 2])
    
    # Analyze save percentage after passes
    pass_analysis = []
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie].copy()
        
        # Look for shots that follow passes within 5 actions
        pass_sequences = []
        for i in range(len(goalie_subset) - 5):
            current_row = goalie_subset.iloc[i]
            if current_row['action'] in ['Saves', 'Goals against']:
                # Check if any of the previous 5 actions were passes
                prev_actions = goalie_subset.iloc[max(0, i-5):i]['action'].tolist()
                if any(action in ['Accurate passes', 'Passes'] for action in prev_actions):
                    pass_sequences.append({
                        'action': current_row['action'],
                        'goalie': goalie
                    })
        
        if pass_sequences:
            pass_df = pd.DataFrame(pass_sequences)
            pass_saves = len(pass_df[pass_df['action'] == 'Saves'])
            pass_goals = len(pass_df[pass_df['action'] == 'Goals against'])
            pass_save_pct = (pass_saves / (pass_saves + pass_goals) * 100) if (pass_saves + pass_goals) > 0 else 0
        else:
            pass_save_pct = 0
        
        # Overall save percentage for comparison
        overall_saves = len(goalie_subset[goalie_subset['action'] == 'Saves'])
        overall_goals = len(goalie_subset[goalie_subset['action'] == 'Goals against'])
        overall_save_pct = (overall_saves / (overall_saves + overall_goals) * 100) if (overall_saves + overall_goals) > 0 else 0
        
        pass_analysis.append({
            'goalie': goalie,
            'pass_save_pct': pass_save_pct,
            'overall_save_pct': overall_save_pct
        })
    
    pass_df = pd.DataFrame(pass_analysis)
    
    x = np.arange(len(pass_df))
    width = 0.35
    ax7.bar(x - width/2, pass_df['pass_save_pct'], width, label='After Pass', color='purple', alpha=0.7)
    ax7.bar(x + width/2, pass_df['overall_save_pct'], width, label='Overall', color='gray', alpha=0.7)
    ax7.set_title('Save Percentage After Pass', fontsize=14, fontweight='bold')
    ax7.set_ylabel('Save Percentage (%)')
    ax7.set_xticks(x)
    ax7.set_xticklabels(pass_df['goalie'], rotation=45)
    ax7.legend()
    ax7.grid(True, alpha=0.3)
    
    # 8. Rebound Analysis (Middle Far Right)
    ax8 = fig.add_subplot(gs[1, 3])
    
    # Analyze rebound sequences
    rebound_analysis = []
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie].copy()
        
        # Look for saves/goals that follow previous saves within 5 actions
        rebound_sequences = []
        for i in range(len(goalie_subset) - 5):
            current_row = goalie_subset.iloc[i]
            if current_row['action'] in ['Saves', 'Goals against']:
                # Check if any of the previous 5 actions were saves
                prev_actions = goalie_subset.iloc[max(0, i-5):i]['action'].tolist()
                if 'Saves' in prev_actions:
                    rebound_sequences.append({
                        'action': current_row['action'],
                        'goalie': goalie
                    })
        
        if rebound_sequences:
            rebound_df = pd.DataFrame(rebound_sequences)
            rebound_saves = len(rebound_df[rebound_df['action'] == 'Saves'])
            rebound_goals = len(rebound_df[rebound_df['action'] == 'Goals against'])
            rebound_save_pct = (rebound_saves / (rebound_saves + rebound_goals) * 100) if (rebound_saves + rebound_goals) > 0 else 0
        else:
            rebound_save_pct = 0
        
        rebound_analysis.append({
            'goalie': goalie,
            'rebound_save_pct': rebound_save_pct,
            'rebound_sequences': len(rebound_sequences)
        })
    
    rebound_df = pd.DataFrame(rebound_analysis)
    
    x = np.arange(len(rebound_df))
    ax8.bar(x, rebound_df['rebound_save_pct'], color='brown', alpha=0.7)
    ax8.set_title('Save Percentage on Rebounds', fontsize=14, fontweight='bold')
    ax8.set_ylabel('Save Percentage (%)')
    ax8.set_xticks(x)
    ax8.set_xticklabels(rebound_df['goalie'], rotation=45)
    ax8.grid(True, alpha=0.3)
    
    # 9. Zone Analysis (Bottom Left)
    ax9 = fig.add_subplot(gs[2, 0])
    
    # Define zones
    zone_boundary_1 = x_min + (x_max - x_min) / 3
    zone_boundary_2 = x_min + 2 * (x_max - x_min) / 3
    
    def categorize_zone(pos_x):
        if pos_x < zone_boundary_1:
            return "Defensive Zone"
        elif pos_x > zone_boundary_2:
            return "Offensive Zone"
        else:
            return "Neutral Zone"
    
    zone_analysis = []
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie].copy()
        goalie_subset['zone'] = goalie_subset['pos_x'].apply(categorize_zone)
        
        zone_save_pcts = []
        for zone in ['Defensive Zone', 'Neutral Zone', 'Offensive Zone']:
            zone_shots = goalie_subset[goalie_subset['zone'] == zone]
            if len(zone_shots) > 0:
                saves = len(zone_shots[zone_shots['action'] == 'Saves'])
                goals = len(zone_shots[zone_shots['action'] == 'Goals against'])
                save_pct = (saves / (saves + goals) * 100) if (saves + goals) > 0 else 0
                zone_save_pcts.append(save_pct)
            else:
                zone_save_pcts.append(0)
        
        zone_analysis.append({
            'goalie': goalie,
            'defensive_zone': zone_save_pcts[0],
            'neutral_zone': zone_save_pcts[1],
            'offensive_zone': zone_save_pcts[2]
        })
    
    zone_df = pd.DataFrame(zone_analysis)
    
    x = np.arange(len(zone_df))
    width = 0.25
    ax9.bar(x - width, zone_df['defensive_zone'], width, label='Defensive Zone', color='red', alpha=0.7)
    ax9.bar(x, zone_df['neutral_zone'], width, label='Neutral Zone', color='yellow', alpha=0.7)
    ax9.bar(x + width, zone_df['offensive_zone'], width, label='Offensive Zone', color='green', alpha=0.7)
    ax9.set_title('Save Percentage by Zone', fontsize=14, fontweight='bold')
    ax9.set_ylabel('Save Percentage (%)')
    ax9.set_xticks(x)
    ax9.set_xticklabels(zone_df['goalie'], rotation=45)
    ax9.legend()
    ax9.grid(True, alpha=0.3)
    
    # 10. Time-based Analysis (Bottom Center)
    ax10 = fig.add_subplot(gs[2, 1])
    
    # Analyze save percentage by half
    half_analysis = []
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        
        for half in goalie_subset['half'].unique():
            half_shots = goalie_subset[goalie_subset['half'] == half]
            if len(half_shots) > 0:
                saves = len(half_shots[half_shots['action'] == 'Saves'])
                goals = len(half_shots[half_shots['action'] == 'Goals against'])
                save_pct = (saves / (saves + goals) * 100) if (saves + goals) > 0 else 0
                half_analysis.append({
                    'goalie': goalie,
                    'half': half,
                    'save_pct': save_pct
                })
    
    half_df = pd.DataFrame(half_analysis)
    
    # Create grouped bar chart
    unique_goalies = half_df['goalie'].unique()
    unique_halves = sorted(half_df['half'].unique())
    
    x = np.arange(len(unique_goalies))
    width = 0.35
    
    for i, half in enumerate(unique_halves):
        half_data = half_df[half_df['half'] == half]
        half_save_pcts = []
        for goalie in unique_goalies:
            goalie_half = half_data[half_data['goalie'] == goalie]
            if len(goalie_half) > 0:
                half_save_pcts.append(goalie_half['save_pct'].iloc[0])
            else:
                half_save_pcts.append(0)
        
        ax10.bar(x + i*width, half_save_pcts, width, label=f'Half {half}', alpha=0.7)
    
    ax10.set_title('Save Percentage by Half', fontsize=14, fontweight='bold')
    ax10.set_ylabel('Save Percentage (%)')
    ax10.set_xticks(x + width/2)
    ax10.set_xticklabels(unique_goalies, rotation=45)
    ax10.legend()
    ax10.grid(True, alpha=0.3)
    
    # 11. Shot Quality Analysis (Bottom Right)
    ax11 = fig.add_subplot(gs[2, 2])
    
    # Calculate shot quality metrics
    quality_analysis = []
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        
        # High-danger shots (close and in front of net)
        high_danger = goalie_subset[
            (goalie_subset['shot_distance'] < 15) & 
            ((goalie_subset['shot_angle'] <= 30) | (goalie_subset['shot_angle'] >= 330))
        ]
        
        if len(high_danger) > 0:
            hd_saves = len(high_danger[high_danger['action'] == 'Saves'])
            hd_goals = len(high_danger[high_danger['action'] == 'Goals against'])
            hd_save_pct = (hd_saves / (hd_saves + hd_goals) * 100) if (hd_saves + hd_goals) > 0 else 0
        else:
            hd_save_pct = 0
        
        # Low-danger shots (far and from sides)
        low_danger = goalie_subset[
            (goalie_subset['shot_distance'] >= 15) & 
            (goalie_subset['shot_angle'] > 30) & (goalie_subset['shot_angle'] < 330)
        ]
        
        if len(low_danger) > 0:
            ld_saves = len(low_danger[low_danger['action'] == 'Saves'])
            ld_goals = len(low_danger[low_danger['action'] == 'Goals against'])
            ld_save_pct = (ld_saves / (ld_saves + ld_goals) * 100) if (ld_saves + ld_goals) > 0 else 0
        else:
            ld_save_pct = 0
        
        quality_analysis.append({
            'goalie': goalie,
            'high_danger_save_pct': hd_save_pct,
            'low_danger_save_pct': ld_save_pct
        })
    
    quality_df = pd.DataFrame(quality_analysis)
    
    x = np.arange(len(quality_df))
    width = 0.35
    ax11.bar(x - width/2, quality_df['high_danger_save_pct'], width, label='High Danger', color='red', alpha=0.7)
    ax11.bar(x + width/2, quality_df['low_danger_save_pct'], width, label='Low Danger', color='green', alpha=0.7)
    ax11.set_title('Save Percentage by Shot Quality', fontsize=14, fontweight='bold')
    ax11.set_ylabel('Save Percentage (%)')
    ax11.set_xticks(x)
    ax11.set_xticklabels(quality_df['goalie'], rotation=45)
    ax11.legend()
    ax11.grid(True, alpha=0.3)
    
    # 12. Summary Statistics (Bottom Far Right)
    ax12 = fig.add_subplot(gs[2, 3])
    ax12.axis('off')
    
    # Calculate summary statistics
    summary_stats = []
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        saves = len(goalie_subset[goalie_subset['action'] == 'Saves'])
        goals = len(goalie_subset[goalie_subset['action'] == 'Goals against'])
        total_shots = saves + goals
        save_pct = (saves / total_shots * 100) if total_shots > 0 else 0
        avg_distance = goalie_subset['shot_distance'].mean()
        
        summary_stats.append(f"{goalie}: {save_pct:.1f}% ({saves}/{total_shots}), {avg_distance:.1f} units avg")
    
    summary_text = "SUMMARY STATISTICS\n\n" + "\n".join(summary_stats)
    ax12.text(0.1, 0.9, summary_text, transform=ax12.transAxes, fontsize=10,
              verticalalignment='top', fontfamily='monospace',
              bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
    
    # Add overall title
    fig.suptitle('Comprehensive Goalie Analytics Dashboard', fontsize=20, fontweight='bold', y=0.98)
    
    plt.savefig('/Users/emilyfehr8/CascadeProjects/comprehensive_goalie_dashboard.png', 
                dpi=300, bbox_inches='tight')
    print("Comprehensive goalie dashboard saved as 'comprehensive_goalie_dashboard.png'")
    
    # Print detailed analysis
    print("\n=== DETAILED ANALYSIS SUMMARY ===")
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        saves = len(goalie_subset[goalie_subset['action'] == 'Saves'])
        goals = len(goalie_subset[goalie_subset['action'] == 'Goals against'])
        total_shots = saves + goals
        save_pct = (saves / total_shots * 100) if total_shots > 0 else 0
        
        print(f"\n{goalie}:")
        print(f"  Overall: {save_pct:.1f}% ({saves}/{total_shots})")
        print(f"  Average shot distance: {goalie_subset['shot_distance'].mean():.1f} units")
        print(f"  Average shot angle: {goalie_subset['shot_angle'].mean():.1f}°")
    
    return goalie_data

if __name__ == "__main__":
    goalie_data = create_comprehensive_goalie_dashboard()
