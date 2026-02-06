#!/usr/bin/env python3
"""
Analysis of goalie positioning and net locations based on coordinate data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_goalie_positioning():
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
    
    print("=== GOALIE POSITIONING ANALYSIS ===")
    print(f"Goalies analyzed: {list(goalies)}")
    
    # Analyze saves coordinates
    saves_data = goalie_data[goalie_data['action'] == 'Saves'].copy()
    goals_data = goalie_data[goalie_data['action'] == 'Goals against'].copy()
    
    print(f"\nTotal saves: {len(saves_data)}")
    print(f"Total goals against: {len(goals_data)}")
    
    # Coordinate analysis
    print("\n=== COORDINATE RANGES ===")
    print("Saves coordinates:")
    print(f"  pos_x range: {saves_data['pos_x'].min():.2f} to {saves_data['pos_x'].max():.2f}")
    print(f"  pos_y range: {saves_data['pos_y'].min():.2f} to {saves_data['pos_y'].max():.2f}")
    print(f"  pos_x mean: {saves_data['pos_x'].mean():.2f}")
    print(f"  pos_y mean: {saves_data['pos_y'].mean():.2f}")
    
    print("\nGoals against coordinates:")
    print(f"  pos_x range: {goals_data['pos_x'].min():.2f} to {goals_data['pos_x'].max():.2f}")
    print(f"  pos_y range: {goals_data['pos_y'].min():.2f} to {goals_data['pos_y'].max():.2f}")
    print(f"  pos_x mean: {goals_data['pos_x'].mean():.2f}")
    print(f"  pos_y mean: {goals_data['pos_y'].mean():.2f}")
    
    # Net location estimation
    print("\n=== NET LOCATION ESTIMATION ===")
    
    # Assuming standard hockey rink dimensions
    # NHL rink is 200ft x 85ft (60.96m x 25.91m)
    # Goals are typically at the ends of the rink
    
    # Based on coordinate patterns, estimate net locations
    # Most saves/goals seem to be in the offensive zone (positive x values)
    
    # Estimate net location based on coordinate clustering
    all_goalie_coords = pd.concat([saves_data[['pos_x', 'pos_y']], goals_data[['pos_x', 'pos_y']]])
    
    # Find the most common x-coordinate (likely net location)
    x_mode = all_goalie_coords['pos_x'].mode().iloc[0]
    y_center = all_goalie_coords['pos_y'].mean()
    
    print(f"Estimated net location: x = {x_mode:.2f}, y = {y_center:.2f}")
    
    # Analyze goalie positioning relative to net
    print("\n=== GOALIE POSITIONING ANALYSIS ===")
    
    # Calculate distance from estimated net
    net_x, net_y = x_mode, y_center
    saves_data['distance_from_net'] = np.sqrt(
        (saves_data['pos_x'] - net_x)**2 + (saves_data['pos_y'] - net_y)**2
    )
    goals_data['distance_from_net'] = np.sqrt(
        (goals_data['pos_x'] - net_x)**2 + (goals_data['pos_y'] - net_y)**2
    )
    
    print("Saves - Distance from estimated net:")
    print(f"  Mean distance: {saves_data['distance_from_net'].mean():.2f}")
    print(f"  Min distance: {saves_data['distance_from_net'].min():.2f}")
    print(f"  Max distance: {saves_data['distance_from_net'].max():.2f}")
    
    print("\nGoals against - Distance from estimated net:")
    print(f"  Mean distance: {goals_data['distance_from_net'].mean():.2f}")
    print(f"  Min distance: {goals_data['distance_from_net'].min():.2f}")
    print(f"  Max distance: {goals_data['distance_from_net'].max():.2f}")
    
    # Zone analysis
    print("\n=== ZONE ANALYSIS ===")
    
    # Define zones based on x-coordinate
    def define_zone(pos_x, team, goalie_team):
        if team == goalie_team:
            if pos_x < -22.86:
                return "DZ"
            elif pos_x > 38.10:
                return "OZ"
            else:
                return "NZ"
        else:
            if pos_x > 22.86:
                return "DZ"
            elif pos_x < -38.10:
                return "OZ"
            else:
                return "NZ"
    
    saves_data['zone'] = saves_data.apply(
        lambda row: define_zone(row['pos_x'], row['team'], row['goalie_team']), axis=1
    )
    goals_data['zone'] = goals_data.apply(
        lambda row: define_zone(row['pos_x'], row['team'], row['goalie_team']), axis=1
    )
    
    print("Saves by zone:")
    print(saves_data['zone'].value_counts())
    print("\nGoals against by zone:")
    print(goals_data['zone'].value_counts())
    
    # Rebound sequence analysis
    print("\n=== REBOUND SEQUENCE ANALYSIS ===")
    
    # Sort by start time to analyze sequences
    goalie_data_sorted = goalie_data.sort_values('start')
    
    rebound_sequences = []
    for goalie in goalies:
        goalie_subset = goalie_data_sorted[goalie_data_sorted['player'] == goalie]
        
        for i in range(len(goalie_subset) - 5):
            current_row = goalie_subset.iloc[i]
            if current_row['action'] in ['Saves', 'Goals against']:
                # Check if any of the previous 5 actions were saves
                prev_actions = goalie_subset.iloc[max(0, i-5):i]['action'].tolist()
                if 'Saves' in prev_actions:
                    rebound_sequences.append({
                        'goalie': goalie,
                        'action': current_row['action'],
                        'pos_x': current_row['pos_x'],
                        'pos_y': current_row['pos_y'],
                        'zone': current_row.get('zone', 'Unknown'),
                        'start_time': current_row['start']
                    })
    
    rebound_df = pd.DataFrame(rebound_sequences)
    
    if len(rebound_df) > 0:
        print(f"Total rebound sequences: {len(rebound_df)}")
        print("\nRebound sequences by goalie:")
        print(rebound_df['goalie'].value_counts())
        
        print("\nRebound sequences by zone:")
        print(rebound_df['zone'].value_counts())
        
        print("\nRebound sequence coordinates:")
        print(f"  pos_x range: {rebound_df['pos_x'].min():.2f} to {rebound_df['pos_x'].max():.2f}")
        print(f"  pos_y range: {rebound_df['pos_y'].min():.2f} to {rebound_df['pos_y'].max():.2f}")
    else:
        print("No rebound sequences found")
    
    # Create visualizations
    print("\n=== CREATING VISUALIZATIONS ===")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Saves vs Goals coordinates
    axes[0, 0].scatter(saves_data['pos_x'], saves_data['pos_y'], 
                      c='green', alpha=0.6, label='Saves', s=50)
    axes[0, 0].scatter(goals_data['pos_x'], goals_data['pos_y'], 
                      c='red', alpha=0.8, label='Goals Against', s=100, marker='x')
    axes[0, 0].scatter(net_x, net_y, c='blue', s=200, marker='s', label='Estimated Net')
    axes[0, 0].set_xlabel('X Position')
    axes[0, 0].set_ylabel('Y Position')
    axes[0, 0].set_title('Goalie Actions by Position')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Distance from net
    axes[0, 1].hist(saves_data['distance_from_net'], bins=20, alpha=0.7, 
                   label='Saves', color='green', density=True)
    axes[0, 1].hist(goals_data['distance_from_net'], bins=20, alpha=0.7, 
                   label='Goals Against', color='red', density=True)
    axes[0, 1].set_xlabel('Distance from Estimated Net')
    axes[0, 1].set_ylabel('Density')
    axes[0, 1].set_title('Distribution of Actions by Distance from Net')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Zone analysis
    if len(saves_data) > 0:
        zone_counts = saves_data['zone'].value_counts()
        axes[1, 0].pie(zone_counts.values, labels=zone_counts.index, autopct='%1.1f%%')
        axes[1, 0].set_title('Saves by Zone')
    
    # Plot 4: Rebound sequences
    if len(rebound_df) > 0:
        rebound_by_goalie = rebound_df['goalie'].value_counts()
        axes[1, 1].bar(rebound_by_goalie.index, rebound_by_goalie.values)
        axes[1, 1].set_xlabel('Goalie')
        axes[1, 1].set_ylabel('Number of Rebound Sequences')
        axes[1, 1].set_title('Rebound Sequences by Goalie')
        axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('/Users/emilyfehr8/CascadeProjects/goalie_positioning_analysis.png', 
                dpi=300, bbox_inches='tight')
    print("Visualization saved as 'goalie_positioning_analysis.png'")
    
    # Summary
    print("\n=== SUMMARY ===")
    print(f"1. Estimated net location: x = {net_x:.2f}, y = {net_y:.2f}")
    print(f"2. Most saves occur in the {saves_data['zone'].mode().iloc[0]} zone")
    print(f"3. Average distance from net for saves: {saves_data['distance_from_net'].mean():.2f}")
    print(f"4. Average distance from net for goals: {goals_data['distance_from_net'].mean():.2f}")
    print(f"5. Total rebound sequences: {len(rebound_df)}")
    
    return saves_data, goals_data, rebound_df

if __name__ == "__main__":
    saves_data, goals_data, rebound_df = analyze_goalie_positioning()
