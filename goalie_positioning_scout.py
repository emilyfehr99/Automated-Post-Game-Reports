#!/usr/bin/env python3
"""
Goalie positioning analysis for pre-scouting
Shows how each goalie positions themselves relative to the net
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def analyze_goalie_positioning_for_scouting():
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
    
    print("=== SHOT LOCATION ANALYSIS FOR PRE-SCOUTING ===")
    print("NOTE: Coordinates represent SHOT LOCATIONS, not goalie positioning")
    print(f"Defending net location: X = {net_x:.2f}, Y = {net_y:.2f}")
    print(f"Goalies analyzed: {list(goalies)}")
    
    # Calculate positioning metrics for each goalie
    positioning_metrics = []
    
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        saves = goalie_subset[goalie_subset['action'] == 'Saves']
        goals = goalie_subset[goalie_subset['action'] == 'Goals against']
        
        # Calculate distances from net
        saves_distances = np.sqrt((saves['pos_x'] - net_x)**2 + (saves['pos_y'] - net_y)**2)
        goals_distances = np.sqrt((goals['pos_x'] - net_x)**2 + (goals['pos_y'] - net_y)**2)
        
        # Positioning metrics
        avg_save_distance = saves_distances.mean()
        median_save_distance = saves_distances.median()
        std_save_distance = saves_distances.std()
        min_save_distance = saves_distances.min()
        max_save_distance = saves_distances.max()
        
        avg_goal_distance = goals_distances.mean() if len(goals) > 0 else np.nan
        median_goal_distance = goals_distances.median() if len(goals) > 0 else np.nan
        
        # Calculate positioning relative to net (X and Y separately)
        saves_x_distance = abs(saves['pos_x'] - net_x)
        saves_y_distance = abs(saves['pos_y'] - net_y)
        
        avg_x_distance = saves_x_distance.mean()
        avg_y_distance = saves_y_distance.mean()
        
        # Calculate positioning consistency (lower std = more consistent positioning)
        x_consistency = 1 / saves_x_distance.std() if saves_x_distance.std() > 0 else 0
        y_consistency = 1 / saves_y_distance.std() if saves_y_distance.std() > 0 else 0
        
        # Categorize positioning style
        if avg_save_distance < 10:
            positioning_style = "Deep in Net"
        elif avg_save_distance < 15:
            positioning_style = "Moderate Depth"
        elif avg_save_distance < 20:
            positioning_style = "Aggressive"
        else:
            positioning_style = "Very Aggressive"
        
        # Calculate save percentage by distance from net
        close_saves = saves[saves_distances < 12]  # Within 12 units
        far_saves = saves[saves_distances >= 12]
        
        close_goals = goals[goals_distances < 12] if len(goals) > 0 else pd.DataFrame()
        far_goals = goals[goals_distances >= 12] if len(goals) > 0 else pd.DataFrame()
        
        close_save_pct = len(close_saves) / (len(close_saves) + len(close_goals)) * 100 if (len(close_saves) + len(close_goals)) > 0 else 0
        far_save_pct = len(far_saves) / (len(far_saves) + len(far_goals)) * 100 if (len(far_saves) + len(far_goals)) > 0 else 0
        
        positioning_metrics.append({
            'goalie': goalie,
            'team': goalie_teams[goalie],
            'total_saves': len(saves),
            'total_goals': len(goals),
            'avg_distance_from_net': avg_save_distance,
            'median_distance_from_net': median_save_distance,
            'std_distance_from_net': std_save_distance,
            'min_distance_from_net': min_save_distance,
            'max_distance_from_net': max_save_distance,
            'avg_x_distance': avg_x_distance,
            'avg_y_distance': avg_y_distance,
            'x_consistency': x_consistency,
            'y_consistency': y_consistency,
            'positioning_style': positioning_style,
            'close_save_pct': close_save_pct,
            'far_save_pct': far_save_pct,
            'close_saves': len(close_saves),
            'far_saves': len(far_saves),
            'close_goals': len(close_goals),
            'far_goals': len(far_goals)
        })
    
    # Convert to DataFrame
    positioning_df = pd.DataFrame(positioning_metrics)
    
    print("\n=== GOALIE POSITIONING METRICS ===")
    print(positioning_df[['goalie', 'team', 'avg_distance_from_net', 'positioning_style', 'close_save_pct', 'far_save_pct']].to_string(index=False))
    
    # Create positioning categories
    print("\n=== POSITIONING STYLE ANALYSIS ===")
    style_counts = positioning_df['positioning_style'].value_counts()
    print(style_counts)
    
    # Rank goalies by aggressiveness (farther from net = more aggressive)
    positioning_df_sorted = positioning_df.sort_values('avg_distance_from_net', ascending=False)
    
    print("\n=== GOALIE RANKINGS BY POSITIONING ===")
    print("Most Aggressive (farthest from net) to Most Conservative (closest to net):")
    for i, (_, row) in enumerate(positioning_df_sorted.iterrows(), 1):
        print(f"{i}. {row['goalie']} ({row['team']}) - {row['positioning_style']} - {row['avg_distance_from_net']:.2f} units from net")
    
    # Create detailed scouting report
    print("\n=== DETAILED SCOUTING REPORT ===")
    for _, row in positioning_df.iterrows():
        print(f"\n--- {row['goalie']} ({row['team']}) ---")
        print(f"Positioning Style: {row['positioning_style']}")
        print(f"Average Distance from Net: {row['avg_distance_from_net']:.2f} units")
        print(f"Positioning Consistency: X={row['x_consistency']:.3f}, Y={row['y_consistency']:.3f}")
        print(f"Close Range Performance: {row['close_save_pct']:.1f}% ({row['close_saves']} saves, {row['close_goals']} goals)")
        print(f"Far Range Performance: {row['far_save_pct']:.1f}% ({row['far_saves']} saves, {row['far_goals']} goals)")
        
        # Scouting insights
        if row['avg_distance_from_net'] < 10:
            print("  📍 SCOUTING NOTE: Plays deep in net - good for covering rebounds, vulnerable to long shots")
        elif row['avg_distance_from_net'] < 15:
            print("  📍 SCOUTING NOTE: Moderate depth - balanced positioning, good for most situations")
        elif row['avg_distance_from_net'] < 20:
            print("  📍 SCOUTING NOTE: Aggressive positioning - cuts down angles, vulnerable to dekes")
        else:
            print("  📍 SCOUTING NOTE: Very aggressive - high risk/high reward, excellent for breakaways")
        
        if row['x_consistency'] > 0.1:
            print("  📍 SCOUTING NOTE: Very consistent X positioning - predictable movement")
        if row['y_consistency'] > 0.1:
            print("  📍 SCOUTING NOTE: Very consistent Y positioning - stays centered well")
    
    # Create visualizations
    print("\n=== CREATING POSITIONING VISUALIZATIONS ===")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Plot 1: Distance from net by goalie
    axes[0, 0].bar(positioning_df['goalie'], positioning_df['avg_distance_from_net'])
    axes[0, 0].set_title('Average Distance from Net by Goalie')
    axes[0, 0].set_ylabel('Distance from Net (units)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Positioning consistency
    x = np.arange(len(positioning_df))
    width = 0.35
    axes[0, 1].bar(x - width/2, positioning_df['x_consistency'], width, label='X Consistency')
    axes[0, 1].bar(x + width/2, positioning_df['y_consistency'], width, label='Y Consistency')
    axes[0, 1].set_title('Positioning Consistency by Goalie')
    axes[0, 1].set_ylabel('Consistency Score')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(positioning_df['goalie'], rotation=45)
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Save percentage by distance
    axes[0, 2].bar(positioning_df['goalie'], positioning_df['close_save_pct'], 
                   alpha=0.7, label='Close Range', color='green')
    axes[0, 2].bar(positioning_df['goalie'], positioning_df['far_save_pct'], 
                   alpha=0.7, label='Far Range', color='blue')
    axes[0, 2].set_title('Save Percentage by Distance Range')
    axes[0, 2].set_ylabel('Save Percentage (%)')
    axes[0, 2].tick_params(axis='x', rotation=45)
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3)
    
    # Plot 4: Shot locations by goalie (corrected interpretation) - Full rink view
    colors = ['red', 'blue', 'green', 'orange']
    
    # Get full rink dimensions
    all_coords = goalie_data[['pos_x', 'pos_y']].dropna()
    rink_x_min, rink_x_max = all_coords['pos_x'].min(), all_coords['pos_x'].max()
    rink_y_min, rink_y_max = all_coords['pos_y'].min(), all_coords['pos_y'].max()
    
    # Show all coordinates as background
    axes[1, 0].scatter(all_coords['pos_x'], all_coords['pos_y'], 
                      alpha=0.1, s=5, color='gray', label='All rink activity')
    
    for i, goalie in enumerate(goalies):
        goalie_saves = goalie_data[(goalie_data['player'] == goalie) & (goalie_data['action'] == 'Saves')]
        goalie_goals = goalie_data[(goalie_data['player'] == goalie) & (goalie_data['action'] == 'Goals against')]
        
        axes[1, 0].scatter(goalie_saves['pos_x'], goalie_saves['pos_y'], 
                          c=colors[i % len(colors)], alpha=0.6, label=f'{goalie} (Saves)', s=50)
        if len(goalie_goals) > 0:
            axes[1, 0].scatter(goalie_goals['pos_x'], goalie_goals['pos_y'], 
                              c=colors[i % len(colors)], alpha=0.8, label=f'{goalie} (Goals)', s=100, marker='x')
    
    # Mark both nets
    axes[1, 0].scatter(net_x, net_y, c='blue', s=200, marker='s', label='Defending Net')
    axes[1, 0].scatter(rink_x_min, net_y, c='orange', s=200, marker='s', label='Offensive Net')
    
    # Add zone lines
    zone_boundary_1 = rink_x_min + (rink_x_max - rink_x_min) / 3
    zone_boundary_2 = rink_x_min + 2 * (rink_x_max - rink_x_min) / 3
    axes[1, 0].axvline(x=zone_boundary_1, color='purple', linestyle='--', alpha=0.7, label='Zone Boundary')
    axes[1, 0].axvline(x=zone_boundary_2, color='purple', linestyle='--', alpha=0.7)
    
    axes[1, 0].set_xlabel('X Position')
    axes[1, 0].set_ylabel('Y Position')
    axes[1, 0].set_title('Shot Locations by Goalie - Full Rink View')
    axes[1, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 5: Distance distribution by goalie
    for i, goalie in enumerate(goalies):
        goalie_saves = goalie_data[(goalie_data['player'] == goalie) & (goalie_data['action'] == 'Saves')]
        distances = np.sqrt((goalie_saves['pos_x'] - net_x)**2 + (goalie_saves['pos_y'] - net_y)**2)
        axes[1, 1].hist(distances, bins=15, alpha=0.6, label=goalie, color=colors[i % len(colors)])
    
    axes[1, 1].set_xlabel('Distance from Net')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('Distance Distribution by Goalie')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    # Plot 6: Positioning style comparison
    style_avg_distance = positioning_df.groupby('positioning_style')['avg_distance_from_net'].mean()
    axes[1, 2].bar(style_avg_distance.index, style_avg_distance.values)
    axes[1, 2].set_title('Average Distance by Positioning Style')
    axes[1, 2].set_ylabel('Average Distance from Net')
    axes[1, 2].tick_params(axis='x', rotation=45)
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/emilyfehr8/CascadeProjects/goalie_positioning_scout_analysis.png', 
                dpi=300, bbox_inches='tight')
    print("Positioning analysis visualization saved as 'goalie_positioning_scout_analysis.png'")
    
    # Create summary table for easy reference
    print("\n=== QUICK REFERENCE TABLE ===")
    summary_table = positioning_df[['goalie', 'team', 'positioning_style', 'avg_distance_from_net', 'close_save_pct', 'far_save_pct']].copy()
    summary_table.columns = ['Goalie', 'Team', 'Style', 'Avg Distance', 'Close Save %', 'Far Save %']
    print(summary_table.to_string(index=False))
    
    return positioning_df

if __name__ == "__main__":
    positioning_df = analyze_goalie_positioning_for_scouting()
