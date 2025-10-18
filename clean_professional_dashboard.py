#!/usr/bin/env python3
"""
Clean Professional Goalie Analytics Dashboard
Using Arial Black for bold, clean typography
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import math
from matplotlib.patches import Circle, Rectangle
import matplotlib.patches as mpatches

def create_clean_dashboard():
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
    
    print("=== CREATING CLEAN PROFESSIONAL DASHBOARD ===")
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
    
    # Set up the figure with clean styling
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.weight'] = 'normal'
    plt.rcParams['axes.linewidth'] = 1.5
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    
    # Create clean dashboard
    fig = plt.figure(figsize=(22, 16))
    fig.patch.set_facecolor('#FFFFFF')
    
    # Create organized grid layout
    gs = fig.add_gridspec(4, 3, hspace=0.35, wspace=0.25, 
                         left=0.08, right=0.95, top=0.90, bottom=0.08)
    
    # Define clean color scheme
    colors = {
        'primary': '#1a1a1a',      # Black
        'secondary': '#666666',    # Gray
        'accent': '#e74c3c',       # Red
        'success': '#27ae60',      # Green
        'warning': '#f39c12',      # Orange
        'info': '#3498db',         # Blue
        'goalie1': '#e74c3c',      # Red
        'goalie2': '#3498db',      # Blue
        'goalie3': '#27ae60',      # Green
        'goalie4': '#f39c12',      # Orange
        'background': '#FFFFFF',   # White
        'light_gray': '#f8f9fa'    # Light Gray
    }
    
    goalie_colors = [colors['goalie1'], colors['goalie2'], colors['goalie3'], colors['goalie4']]
    
    # 1. MAIN TITLE (Top Row)
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.axis('off')
    
    # Calculate overall stats
    total_saves = len(goalie_data[goalie_data['action'] == 'Saves'])
    total_goals = len(goalie_data[goalie_data['action'] == 'Goals against'])
    overall_save_pct = (total_saves / (total_saves + total_goals) * 100) if (total_saves + total_goals) > 0 else 0
    
    ax_title.text(0.5, 0.6, 'GOALIE ANALYTICS DASHBOARD', 
                  fontsize=42, fontweight='bold', ha='center', va='center',
                  color=colors['primary'], transform=ax_title.transAxes,
                  fontfamily='Arial Black')
    
    ax_title.text(0.5, 0.2, f'OVERALL PERFORMANCE: {overall_save_pct:.1f}% ({total_saves} SAVES, {total_goals} GOALS)',
                  fontsize=20, ha='center', va='center',
                  color=colors['secondary'], transform=ax_title.transAxes,
                  fontweight='bold')
    
    # 2. SAVE PERCENTAGE BY DISTANCE (Top Left)
    ax1 = fig.add_subplot(gs[1, 0])
    ax1.set_facecolor(colors['background'])
    
    # Calculate save percentage by distance
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
    
    bars1 = ax1.bar(x - width/2, distance_df['close_save_pct'], width, 
                    label='CLOSE RANGE (<15 UNITS)', color=colors['accent'], alpha=0.9, edgecolor='white', linewidth=2)
    bars2 = ax1.bar(x + width/2, distance_df['far_save_pct'], width, 
                    label='FAR RANGE (≥15 UNITS)', color=colors['info'], alpha=0.9, edgecolor='white', linewidth=2)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    for bar in bars2:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax1.set_title('SAVE % BY SHOT DISTANCE', fontsize=18, fontweight='bold', color=colors['primary'], pad=20)
    ax1.set_ylabel('SAVE PERCENTAGE (%)', fontweight='bold', fontsize=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels([name.split()[0] for name in distance_df['goalie']], fontweight='bold', fontsize=11)
    ax1.legend(frameon=True, fancybox=False, shadow=False, fontsize=10, loc='upper right')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(0, 105)
    
    # 3. SAVE PERCENTAGE BY ANGLE (Top Center)
    ax2 = fig.add_subplot(gs[1, 1])
    ax2.set_facecolor(colors['background'])
    
    # Calculate save percentage by angle
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
    
    bars1 = ax2.bar(x - width, angle_df['front_save_pct'], width, 
                    label='FRONT OF NET', color=colors['success'], alpha=0.9, edgecolor='white', linewidth=2)
    bars2 = ax2.bar(x, angle_df['side_save_pct'], width, 
                    label='SIDE ANGLES', color=colors['warning'], alpha=0.9, edgecolor='white', linewidth=2)
    bars3 = ax2.bar(x + width, angle_df['behind_save_pct'], width, 
                    label='BEHIND NET', color=colors['accent'], alpha=0.9, edgecolor='white', linewidth=2)
    
    # Add value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    ax2.set_title('SAVE % BY SHOT ANGLE', fontsize=18, fontweight='bold', color=colors['primary'], pad=20)
    ax2.set_ylabel('SAVE PERCENTAGE (%)', fontweight='bold', fontsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels([name.split()[0] for name in angle_df['goalie']], fontweight='bold', fontsize=11)
    ax2.legend(frameon=True, fancybox=False, shadow=False, fontsize=10, loc='upper right')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, 105)
    
    # 4. SHOT DISTANCE DISTRIBUTION (Top Right)
    ax3 = fig.add_subplot(gs[1, 2])
    ax3.set_facecolor(colors['background'])
    
    for i, goalie in enumerate(goalies):
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        distances = goalie_subset['shot_distance']
        ax3.hist(distances, bins=10, alpha=0.7, label=goalie.split()[0], 
                color=goalie_colors[i % len(goalie_colors)], density=True, edgecolor='white', linewidth=1.5)
    
    ax3.set_xlabel('SHOT DISTANCE FROM NET', fontweight='bold', fontsize=12)
    ax3.set_ylabel('DENSITY', fontweight='bold', fontsize=12)
    ax3.set_title('SHOT DISTANCE DISTRIBUTION', fontsize=18, fontweight='bold', color=colors['primary'], pad=20)
    ax3.legend(frameon=True, fancybox=False, shadow=False, fontsize=10)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 5. SAVE PERCENTAGE HEAT MAP (Middle Left)
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.set_facecolor(colors['background'])
    
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
    
    im = ax4.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', 
                   extent=[x_min, x_max, y_min, y_max], vmin=0, vmax=100, alpha=0.8)
    
    # Add net
    net_circle = Circle((net_x, net_y), 2, color=colors['primary'], alpha=0.9, zorder=10)
    ax4.add_patch(net_circle)
    ax4.text(net_x, net_y, 'NET', ha='center', va='center', color='white', 
             fontweight='bold', fontsize=10, zorder=11)
    
    ax4.set_xlabel('X POSITION', fontweight='bold', fontsize=12)
    ax4.set_ylabel('Y POSITION', fontweight='bold', fontsize=12)
    ax4.set_title('SAVE % HEAT MAP', fontsize=18, fontweight='bold', color=colors['primary'], pad=20)
    ax4.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax4, shrink=0.8)
    cbar.set_label('SAVE %', fontweight='bold', fontsize=10)
    
    # 6. SHOT LOCATIONS WITH TRAJECTORIES (Middle Center)
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.set_facecolor(colors['background'])
    
    # Add rink background
    rink_rect = Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, 
                         linewidth=2, edgecolor=colors['primary'], facecolor='none', alpha=0.5)
    ax5.add_patch(rink_rect)
    
    # Add center line
    center_y = (y_min + y_max) / 2
    ax5.axhline(y=center_y, color=colors['primary'], linestyle='-', alpha=0.3, linewidth=1)
    
    for i, goalie in enumerate(goalies):
        goalie_saves = goalie_data[(goalie_data['player'] == goalie) & (goalie_data['action'] == 'Saves')]
        goalie_goals = goalie_data[(goalie_data['player'] == goalie) & (goalie_data['action'] == 'Goals against')]
        
        # Plot saves
        ax5.scatter(goalie_saves['pos_x'], goalie_saves['pos_y'], 
                   c=goalie_colors[i % len(goalie_colors)], alpha=0.8, 
                   label=f'{goalie.split()[0]} (SAVES)', s=60, edgecolors='white', linewidth=1.5)
        
        # Plot goals
        if len(goalie_goals) > 0:
            ax5.scatter(goalie_goals['pos_x'], goalie_goals['pos_y'], 
                       c=goalie_colors[i % len(goalie_colors)], alpha=1.0, 
                       label=f'{goalie.split()[0]} (GOALS)', s=100, marker='X', 
                       edgecolors='white', linewidth=2)
        
        # Draw trajectory lines for sample shots
        sample_shots = goalie_saves.sample(min(2, len(goalie_saves)))
        for _, shot in sample_shots.iterrows():
            ax5.plot([shot['pos_x'], net_x], [shot['pos_y'], net_y], 
                    color=goalie_colors[i % len(goalie_colors)], alpha=0.4, linewidth=2, zorder=1)
    
    # Add net
    net_circle = Circle((net_x, net_y), 2, color=colors['primary'], alpha=0.9, zorder=10)
    ax5.add_patch(net_circle)
    ax5.text(net_x, net_y, 'NET', ha='center', va='center', color='white', 
             fontweight='bold', fontsize=10, zorder=11)
    
    ax5.set_xlabel('X POSITION', fontweight='bold', fontsize=12)
    ax5.set_ylabel('Y POSITION', fontweight='bold', fontsize=12)
    ax5.set_title('SHOT LOCATIONS & TRAJECTORIES', fontsize=18, fontweight='bold', color=colors['primary'], pad=20)
    ax5.grid(True, alpha=0.3)
    ax5.set_xlim(x_min - 3, x_max + 3)
    ax5.set_ylim(y_min - 3, y_max + 3)
    
    # 7. PERFORMANCE SUMMARY (Middle Right)
    ax6 = fig.add_subplot(gs[2, 2])
    ax6.axis('off')
    
    # Create performance cards
    performance_data = []
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        saves = len(goalie_subset[goalie_subset['action'] == 'Saves'])
        goals = len(goalie_subset[goalie_subset['action'] == 'Goals against'])
        total_shots = saves + goals
        save_pct = (saves / total_shots * 100) if total_shots > 0 else 0
        avg_distance = goalie_subset['shot_distance'].mean()
        
        performance_data.append({
            'goalie': goalie.split()[0],
            'save_pct': save_pct,
            'saves': saves,
            'goals': goals,
            'avg_distance': avg_distance
        })
    
    # Sort by save percentage
    performance_data.sort(key=lambda x: x['save_pct'], reverse=True)
    
    y_pos = 0.95
    for i, data in enumerate(performance_data):
        # Card background - larger cards
        card = Rectangle((0.02, y_pos - 0.18), 0.96, 0.16, 
                        facecolor=goalie_colors[i % len(goalie_colors)], 
                        alpha=0.1, transform=ax6.transAxes)
        ax6.add_patch(card)
        
        # Goalie name - larger font
        ax6.text(0.05, y_pos - 0.02, f"{i+1}. {data['goalie']}", 
                fontsize=18, fontweight='bold', color=colors['primary'], transform=ax6.transAxes)
        
        # Stats - larger fonts and better spacing
        ax6.text(0.05, y_pos - 0.08, f"SAVE %: {data['save_pct']:.1f}% ({data['saves']}/{data['saves']+data['goals']})", 
                fontsize=14, color=colors['secondary'], transform=ax6.transAxes, fontweight='bold')
        ax6.text(0.05, y_pos - 0.16, f"AVG DISTANCE: {data['avg_distance']:.1f} UNITS", 
                fontsize=14, color=colors['secondary'], transform=ax6.transAxes, fontweight='bold')
        
        y_pos -= 0.22
    
    # 8. ZONE ANALYSIS (Bottom Left)
    ax7 = fig.add_subplot(gs[3, 0])
    ax7.set_facecolor(colors['background'])
    
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
    
    bars1 = ax7.bar(x - width, zone_df['defensive_zone'], width, 
                     label='DEFENSIVE ZONE', color=colors['success'], alpha=0.9, edgecolor='white', linewidth=2)
    bars2 = ax7.bar(x, zone_df['neutral_zone'], width, 
                     label='NEUTRAL ZONE', color=colors['warning'], alpha=0.9, edgecolor='white', linewidth=2)
    bars3 = ax7.bar(x + width, zone_df['offensive_zone'], width, 
                     label='OFFENSIVE ZONE', color=colors['info'], alpha=0.9, edgecolor='white', linewidth=2)
    
    # Add value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax7.text(bar.get_x() + bar.get_width()/2., height + 1,
                         f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    ax7.set_title('SAVE % BY ZONE', fontsize=18, fontweight='bold', color=colors['primary'], pad=20)
    ax7.set_ylabel('SAVE PERCENTAGE (%)', fontweight='bold', fontsize=12)
    ax7.set_xticks(x)
    ax7.set_xticklabels([name.split()[0] for name in zone_df['goalie']], fontweight='bold', fontsize=11)
    ax7.legend(frameon=True, fancybox=False, shadow=False, fontsize=10, loc='upper right')
    ax7.grid(True, alpha=0.3, axis='y')
    ax7.set_ylim(0, 105)
    
    # 9. SEQUENCE ANALYSIS (Bottom Center)
    ax8 = fig.add_subplot(gs[3, 1])
    ax8.set_facecolor(colors['background'])
    
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
    
    bars1 = ax8.bar(x - width/2, pass_df['pass_save_pct'], width, 
                    label='AFTER PASS', color=colors['accent'], alpha=0.9, edgecolor='white', linewidth=2)
    bars2 = ax8.bar(x + width/2, pass_df['overall_save_pct'], width, 
                    label='OVERALL', color=colors['secondary'], alpha=0.9, edgecolor='white', linewidth=2)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax8.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax8.set_title('SAVE % AFTER PASS', fontsize=18, fontweight='bold', color=colors['primary'], pad=20)
    ax8.set_ylabel('SAVE PERCENTAGE (%)', fontweight='bold', fontsize=12)
    ax8.set_xticks(x)
    ax8.set_xticklabels([name.split()[0] for name in pass_df['goalie']], fontweight='bold', fontsize=11)
    ax8.legend(frameon=True, fancybox=False, shadow=False, fontsize=10, loc='upper right')
    ax8.grid(True, alpha=0.3, axis='y')
    ax8.set_ylim(0, 105)
    
    # 10. KEY INSIGHTS (Bottom Right)
    ax9 = fig.add_subplot(gs[3, 2])
    ax9.axis('off')
    
    # Calculate key insights
    insights = []
    
    # Best overall performer
    best_goalie = max(goalies, key=lambda g: len(goalie_data[(goalie_data['player'] == g) & (goalie_data['action'] == 'Saves')]) / 
                     len(goalie_data[goalie_data['player'] == g]) * 100)
    best_save_pct = len(goalie_data[(goalie_data['player'] == best_goalie) & (goalie_data['action'] == 'Saves')]) / \
                   len(goalie_data[goalie_data['player'] == best_goalie]) * 100
    insights.append(f"BEST PERFORMER: {best_goalie.split()[0]} ({best_save_pct:.1f}%)")
    
    # Most shots faced
    most_shots_goalie = max(goalies, key=lambda g: len(goalie_data[goalie_data['player'] == g]))
    most_shots = len(goalie_data[goalie_data['player'] == most_shots_goalie])
    insights.append(f"MOST ACTIVE: {most_shots_goalie.split()[0]} ({most_shots} SHOTS)")
    
    # Longest average distance
    longest_dist_goalie = max(goalies, key=lambda g: goalie_data[goalie_data['player'] == g]['shot_distance'].mean())
    longest_dist = goalie_data[goalie_data['player'] == longest_dist_goalie]['shot_distance'].mean()
    insights.append(f"FARTHEST SHOTS: {longest_dist_goalie.split()[0]} ({longest_dist:.1f} UNITS AVG)")
    
    # Add insights text
    insight_text = "KEY INSIGHTS\n\n" + "\n".join(insights)
    ax9.text(0.05, 0.9, insight_text, transform=ax9.transAxes, fontsize=14,
              verticalalignment='top', fontfamily='Arial', fontweight='bold',
              color=colors['primary'],
              bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['light_gray'], 
                       edgecolor=colors['primary'], linewidth=2, alpha=0.9))
    
    # Add legend for shot locations below the insights
    legend_elements = []
    for i, goalie in enumerate(goalies):
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                        markerfacecolor=goalie_colors[i % len(goalie_colors)], 
                                        markersize=8, label=f'{goalie.split()[0]} (SAVES)'))
        legend_elements.append(plt.Line2D([0], [0], marker='X', color='w', 
                                        markerfacecolor=goalie_colors[i % len(goalie_colors)], 
                                        markersize=10, label=f'{goalie.split()[0]} (GOALS)'))
    
    ax9.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(0.98, 0.02), 
              frameon=True, fancybox=False, shadow=False, fontsize=8, ncol=2)
    
    # Save the dashboard
    plt.savefig('/Users/emilyfehr8/CascadeProjects/clean_professional_dashboard.png', 
                dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    print("Clean professional dashboard saved as 'clean_professional_dashboard.png'")
    
    return goalie_data

if __name__ == "__main__":
    goalie_data = create_clean_dashboard()
