#!/usr/bin/env python3
"""
Beautiful Goalie Analytics Dashboard
Professional design with improved aesthetics and organization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import math
from matplotlib.patches import Circle, Rectangle
import matplotlib.patches as mpatches

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_beautiful_goalie_dashboard():
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
    
    print("=== CREATING BEAUTIFUL GOALIE DASHBOARD ===")
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
    
    # Create beautiful dashboard with custom styling
    fig = plt.figure(figsize=(24, 18))
    fig.patch.set_facecolor('#f8f9fa')
    
    # Create a more organized grid layout
    gs = fig.add_gridspec(4, 4, hspace=0.4, wspace=0.3, 
                         left=0.05, right=0.95, top=0.93, bottom=0.05)
    
    # Define beautiful color scheme
    colors = {
        'primary': '#2E86AB',      # Blue
        'secondary': '#A23B72',    # Pink
        'accent': '#F18F01',       # Orange
        'success': '#C73E1D',      # Red
        'goalie1': '#FF6B6B',      # Coral
        'goalie2': '#4ECDC4',      # Teal
        'goalie3': '#45B7D1',      # Sky Blue
        'goalie4': '#96CEB4',      # Mint
        'net': '#2C3E50',          # Dark Blue
        'background': '#F8F9FA',   # Light Gray
        'text': '#2C3E50'          # Dark Gray
    }
    
    goalie_colors = [colors['goalie1'], colors['goalie2'], colors['goalie3'], colors['goalie4']]
    
    # 1. MAIN TITLE AND SUMMARY (Top Row)
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.axis('off')
    
    # Calculate overall stats
    total_saves = len(goalie_data[goalie_data['action'] == 'Saves'])
    total_goals = len(goalie_data[goalie_data['action'] == 'Goals against'])
    overall_save_pct = (total_saves / (total_saves + total_goals) * 100) if (total_saves + total_goals) > 0 else 0
    
    ax_title.text(0.5, 0.7, 'GOALIE ANALYTICS DASHBOARD', 
                  fontsize=32, fontweight='bold', ha='center', va='center',
                  color=colors['text'], transform=ax_title.transAxes)
    
    ax_title.text(0.5, 0.3, f'Overall Performance: {overall_save_pct:.1f}% ({total_saves} saves, {total_goals} goals)',
                  fontsize=16, ha='center', va='center',
                  color=colors['primary'], transform=ax_title.transAxes)
    
    # 2. SAVE PERCENTAGE BY DISTANCE (Top Left)
    ax1 = fig.add_subplot(gs[1, 0])
    ax1.set_facecolor('white')
    
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
                    label='Close Range (<15 units)', color=colors['success'], alpha=0.8)
    bars2 = ax1.bar(x + width/2, distance_df['far_save_pct'], width, 
                    label='Far Range (≥15 units)', color=colors['primary'], alpha=0.8)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    for bar in bars2:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    ax1.set_title('Save % by Shot Distance', fontsize=14, fontweight='bold', color=colors['text'])
    ax1.set_ylabel('Save Percentage (%)', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([name.split()[0] for name in distance_df['goalie']], fontweight='bold')
    ax1.legend(frameon=True, fancybox=True, shadow=True)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(0, 105)
    
    # 3. SAVE PERCENTAGE BY ANGLE (Top Center)
    ax2 = fig.add_subplot(gs[1, 1])
    ax2.set_facecolor('white')
    
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
                    label='Front of Net', color=colors['success'], alpha=0.8)
    bars2 = ax2.bar(x, angle_df['side_save_pct'], width, 
                    label='Side Angles', color=colors['accent'], alpha=0.8)
    bars3 = ax2.bar(x + width, angle_df['behind_save_pct'], width, 
                    label='Behind Net', color=colors['secondary'], alpha=0.8)
    
    # Add value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    ax2.set_title('Save % by Shot Angle', fontsize=14, fontweight='bold', color=colors['text'])
    ax2.set_ylabel('Save Percentage (%)', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([name.split()[0] for name in angle_df['goalie']], fontweight='bold')
    ax2.legend(frameon=True, fancybox=True, shadow=True)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, 105)
    
    # 4. SHOT DISTANCE DISTRIBUTION (Top Right)
    ax3 = fig.add_subplot(gs[1, 2])
    ax3.set_facecolor('white')
    
    for i, goalie in enumerate(goalies):
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        distances = goalie_subset['shot_distance']
        ax3.hist(distances, bins=12, alpha=0.7, label=goalie.split()[0], 
                color=goalie_colors[i % len(goalie_colors)], density=True, edgecolor='white', linewidth=1)
    
    ax3.set_xlabel('Shot Distance from Net', fontweight='bold')
    ax3.set_ylabel('Density', fontweight='bold')
    ax3.set_title('Shot Distance Distribution', fontsize=14, fontweight='bold', color=colors['text'])
    ax3.legend(frameon=True, fancybox=True, shadow=True)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 5. SHOT ANGLE DISTRIBUTION (Top Far Right)
    ax4 = fig.add_subplot(gs[1, 3])
    ax4.set_facecolor('white')
    
    for i, goalie in enumerate(goalies):
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        angles = goalie_subset['shot_angle']
        ax4.hist(angles, bins=15, alpha=0.7, label=goalie.split()[0], 
                color=goalie_colors[i % len(goalie_colors)], density=True, edgecolor='white', linewidth=1)
    
    ax4.set_xlabel('Shot Angle (degrees)', fontweight='bold')
    ax4.set_ylabel('Density', fontweight='bold')
    ax4.set_title('Shot Angle Distribution', fontsize=14, fontweight='bold', color=colors['text'])
    ax4.legend(frameon=True, fancybox=True, shadow=True)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 6. SAVE PERCENTAGE HEAT MAP (Middle Left)
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.set_facecolor('white')
    
    # Create a grid for heat map
    x_min, x_max = goalie_data['pos_x'].min(), goalie_data['pos_x'].max()
    y_min, y_max = goalie_data['pos_y'].min(), goalie_data['pos_y'].max()
    
    # Create grid
    x_bins = np.linspace(x_min, x_max, 25)
    y_bins = np.linspace(y_min, y_max, 20)
    
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
                   extent=[x_min, x_max, y_min, y_max], vmin=0, vmax=100, alpha=0.8)
    
    # Add net
    net_circle = Circle((net_x, net_y), 3, color=colors['net'], alpha=0.9, zorder=10)
    ax5.add_patch(net_circle)
    ax5.text(net_x, net_y, 'NET', ha='center', va='center', color='white', 
             fontweight='bold', fontsize=10, zorder=11)
    
    ax5.set_xlabel('X Position', fontweight='bold')
    ax5.set_ylabel('Y Position', fontweight='bold')
    ax5.set_title('Save % Heat Map', fontsize=14, fontweight='bold', color=colors['text'])
    ax5.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax5, shrink=0.8)
    cbar.set_label('Save %', fontweight='bold')
    
    # 7. SHOT LOCATIONS WITH TRAJECTORIES (Middle Center)
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.set_facecolor('white')
    
    # Add rink background
    rink_rect = Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, 
                         linewidth=3, edgecolor=colors['text'], facecolor='none', alpha=0.3)
    ax6.add_patch(rink_rect)
    
    # Add center line
    center_y = (y_min + y_max) / 2
    ax6.axhline(y=center_y, color=colors['text'], linestyle='--', alpha=0.5, linewidth=2)
    
    for i, goalie in enumerate(goalies):
        goalie_saves = goalie_data[(goalie_data['player'] == goalie) & (goalie_data['action'] == 'Saves')]
        goalie_goals = goalie_data[(goalie_data['player'] == goalie) & (goalie_data['action'] == 'Goals against')]
        
        # Plot saves
        ax6.scatter(goalie_saves['pos_x'], goalie_saves['pos_y'], 
                   c=goalie_colors[i % len(goalie_colors)], alpha=0.7, 
                   label=f'{goalie.split()[0]} (Saves)', s=60, edgecolors='white', linewidth=1)
        
        # Plot goals
        if len(goalie_goals) > 0:
            ax6.scatter(goalie_goals['pos_x'], goalie_goals['pos_y'], 
                       c=goalie_colors[i % len(goalie_colors)], alpha=1.0, 
                       label=f'{goalie.split()[0]} (Goals)', s=120, marker='X', 
                       edgecolors='white', linewidth=2)
        
        # Draw trajectory lines for sample shots
        sample_shots = goalie_saves.sample(min(2, len(goalie_saves)))
        for _, shot in sample_shots.iterrows():
            ax6.plot([shot['pos_x'], net_x], [shot['pos_y'], net_y], 
                    color=goalie_colors[i % len(goalie_colors)], alpha=0.4, linewidth=2, zorder=1)
    
    # Add net
    net_circle = Circle((net_x, net_y), 3, color=colors['net'], alpha=0.9, zorder=10)
    ax6.add_patch(net_circle)
    ax6.text(net_x, net_y, 'NET', ha='center', va='center', color='white', 
             fontweight='bold', fontsize=10, zorder=11)
    
    ax6.set_xlabel('X Position', fontweight='bold')
    ax6.set_ylabel('Y Position', fontweight='bold')
    ax6.set_title('Shot Locations & Trajectories', fontsize=14, fontweight='bold', color=colors['text'])
    ax6.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True, fancybox=True, shadow=True)
    ax6.grid(True, alpha=0.3)
    ax6.set_xlim(x_min - 5, x_max + 5)
    ax6.set_ylim(y_min - 5, y_max + 5)
    
    # 8. PERFORMANCE SUMMARY CARDS (Middle Right)
    ax8 = fig.add_subplot(gs[2, 2])
    ax8.axis('off')
    
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
    
    y_pos = 0.9
    for i, data in enumerate(performance_data):
        # Card background
        card = Rectangle((0.05, y_pos - 0.15), 0.9, 0.12, 
                        facecolor=goalie_colors[i % len(goalie_colors)], 
                        alpha=0.2, transform=ax8.transAxes)
        ax8.add_patch(card)
        
        # Goalie name
        ax8.text(0.1, y_pos, f"{i+1}. {data['goalie']}", 
                fontsize=14, fontweight='bold', color=colors['text'], transform=ax8.transAxes)
        
        # Stats
        ax8.text(0.1, y_pos - 0.05, f"Save %: {data['save_pct']:.1f}% ({data['saves']}/{data['saves']+data['goals']})", 
                fontsize=11, color=colors['text'], transform=ax8.transAxes)
        ax8.text(0.1, y_pos - 0.1, f"Avg Distance: {data['avg_distance']:.1f} units", 
                fontsize=11, color=colors['text'], transform=ax8.transAxes)
        
        y_pos -= 0.2
    
    # 9. SEQUENCE ANALYSIS (Middle Far Right)
    ax9 = fig.add_subplot(gs[2, 3])
    ax9.set_facecolor('white')
    
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
    
    bars1 = ax9.bar(x - width/2, pass_df['pass_save_pct'], width, 
                    label='After Pass', color=colors['secondary'], alpha=0.8)
    bars2 = ax9.bar(x + width/2, pass_df['overall_save_pct'], width, 
                    label='Overall', color=colors['primary'], alpha=0.8)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax9.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    ax9.set_title('Save % After Pass', fontsize=14, fontweight='bold', color=colors['text'])
    ax9.set_ylabel('Save Percentage (%)', fontweight='bold')
    ax9.set_xticks(x)
    ax9.set_xticklabels([name.split()[0] for name in pass_df['goalie']], fontweight='bold')
    ax9.legend(frameon=True, fancybox=True, shadow=True)
    ax9.grid(True, alpha=0.3, axis='y')
    ax9.set_ylim(0, 105)
    
    # 10. ZONE ANALYSIS (Bottom Left)
    ax10 = fig.add_subplot(gs[3, 0])
    ax10.set_facecolor('white')
    
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
    
    bars1 = ax10.bar(x - width, zone_df['defensive_zone'], width, 
                     label='Defensive Zone', color=colors['success'], alpha=0.8)
    bars2 = ax10.bar(x, zone_df['neutral_zone'], width, 
                     label='Neutral Zone', color=colors['accent'], alpha=0.8)
    bars3 = ax10.bar(x + width, zone_df['offensive_zone'], width, 
                     label='Offensive Zone', color=colors['primary'], alpha=0.8)
    
    # Add value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax10.text(bar.get_x() + bar.get_width()/2., height + 1,
                         f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    ax10.set_title('Save % by Zone', fontsize=14, fontweight='bold', color=colors['text'])
    ax10.set_ylabel('Save Percentage (%)', fontweight='bold')
    ax10.set_xticks(x)
    ax10.set_xticklabels([name.split()[0] for name in zone_df['goalie']], fontweight='bold')
    ax10.legend(frameon=True, fancybox=True, shadow=True)
    ax10.grid(True, alpha=0.3, axis='y')
    ax10.set_ylim(0, 105)
    
    # 11. REBOUND ANALYSIS (Bottom Center)
    ax11 = fig.add_subplot(gs[3, 1])
    ax11.set_facecolor('white')
    
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
    bars = ax11.bar(x, rebound_df['rebound_save_pct'], color=colors['accent'], alpha=0.8)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax11.text(bar.get_x() + bar.get_width()/2., height + 1,
                     f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    ax11.set_title('Save % on Rebounds', fontsize=14, fontweight='bold', color=colors['text'])
    ax11.set_ylabel('Save Percentage (%)', fontweight='bold')
    ax11.set_xticks(x)
    ax11.set_xticklabels([name.split()[0] for name in rebound_df['goalie']], fontweight='bold')
    ax11.grid(True, alpha=0.3, axis='y')
    ax11.set_ylim(0, 105)
    
    # 12. KEY INSIGHTS (Bottom Right)
    ax12 = fig.add_subplot(gs[3, 2:])
    ax12.axis('off')
    
    # Calculate key insights
    insights = []
    
    # Best overall performer
    best_goalie = max(goalies, key=lambda g: len(goalie_data[(goalie_data['player'] == g) & (goalie_data['action'] == 'Saves')]) / 
                     len(goalie_data[goalie_data['player'] == g]) * 100)
    best_save_pct = len(goalie_data[(goalie_data['player'] == best_goalie) & (goalie_data['action'] == 'Saves')]) / \
                   len(goalie_data[goalie_data['player'] == best_goalie]) * 100
    insights.append(f"🏆 Best Performer: {best_goalie.split()[0]} ({best_save_pct:.1f}%)")
    
    # Most shots faced
    most_shots_goalie = max(goalies, key=lambda g: len(goalie_data[goalie_data['player'] == g]))
    most_shots = len(goalie_data[goalie_data['player'] == most_shots_goalie])
    insights.append(f"📊 Most Active: {most_shots_goalie.split()[0]} ({most_shots} shots)")
    
    # Longest average distance
    longest_dist_goalie = max(goalies, key=lambda g: goalie_data[goalie_data['player'] == g]['shot_distance'].mean())
    longest_dist = goalie_data[goalie_data['player'] == longest_dist_goalie]['shot_distance'].mean()
    insights.append(f"🎯 Farthest Shots: {longest_dist_goalie.split()[0]} ({longest_dist:.1f} units avg)")
    
    # Add insights text
    insight_text = "KEY INSIGHTS\n\n" + "\n".join(insights)
    ax12.text(0.05, 0.9, insight_text, transform=ax12.transAxes, fontsize=14,
              verticalalignment='top', fontfamily='sans-serif', fontweight='bold',
              color=colors['text'],
              bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['background'], 
                       edgecolor=colors['primary'], linewidth=2, alpha=0.9))
    
    # Save the beautiful dashboard
    plt.savefig('/Users/emilyfehr8/CascadeProjects/beautiful_goalie_dashboard.png', 
                dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    print("Beautiful goalie dashboard saved as 'beautiful_goalie_dashboard.png'")
    
    return goalie_data

if __name__ == "__main__":
    goalie_data = create_beautiful_goalie_dashboard()
