#!/usr/bin/env python3
"""
Corrected goalie positioning analysis with horizontally flipped coordinates
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_goalie_positioning_corrected():
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
    
    print("=== CORRECTED GOALIE POSITIONING ANALYSIS ===")
    print("Applying horizontal flip to coordinates...")
    
    # CORRECTED: Flip coordinates horizontally
    # Assuming the rink is 200ft (60.96m) long, we need to flip x-coordinates
    # If the original system has goals at positive x, flipping would put them at negative x
    
    # First, let's see the current coordinate ranges
    print(f"\nOriginal coordinate ranges:")
    print(f"  pos_x: {goalie_data['pos_x'].min():.2f} to {goalie_data['pos_x'].max():.2f}")
    print(f"  pos_y: {goalie_data['pos_y'].min():.2f} to {goalie_data['pos_y'].max():.2f}")
    
    # Apply horizontal flip
    # Assuming rink length is ~60.96m (200ft), we'll flip around the center
    rink_length = 60.96  # meters
    goalie_data['pos_x_corrected'] = rink_length - goalie_data['pos_x']
    
    print(f"\nCorrected coordinate ranges (after horizontal flip):")
    print(f"  pos_x_corrected: {goalie_data['pos_x_corrected'].min():.2f} to {goalie_data['pos_x_corrected'].max():.2f}")
    print(f"  pos_y: {goalie_data['pos_y'].min():.2f} to {goalie_data['pos_y'].max():.2f}")
    
    # Analyze saves and goals with corrected coordinates
    saves_data = goalie_data[goalie_data['action'] == 'Saves'].copy()
    goals_data = goalie_data[goalie_data['action'] == 'Goals against'].copy()
    
    print(f"\nTotal saves: {len(saves_data)}")
    print(f"Total goals against: {len(goals_data)}")
    
    # Corrected coordinate analysis
    print("\n=== CORRECTED COORDINATE RANGES ===")
    print("Saves coordinates (corrected):")
    print(f"  pos_x range: {saves_data['pos_x_corrected'].min():.2f} to {saves_data['pos_x_corrected'].max():.2f}")
    print(f"  pos_y range: {saves_data['pos_y'].min():.2f} to {saves_data['pos_y'].max():.2f}")
    print(f"  pos_x mean: {saves_data['pos_x_corrected'].mean():.2f}")
    print(f"  pos_y mean: {saves_data['pos_y'].mean():.2f}")
    
    print("\nGoals against coordinates (corrected):")
    print(f"  pos_x range: {goals_data['pos_x_corrected'].min():.2f} to {goals_data['pos_x_corrected'].max():.2f}")
    print(f"  pos_y range: {goals_data['pos_y'].min():.2f} to {goals_data['pos_y'].max():.2f}")
    print(f"  pos_x mean: {goals_data['pos_x_corrected'].mean():.2f}")
    print(f"  pos_y mean: {goals_data['pos_y'].mean():.2f}")
    
    # Net location estimation with corrected coordinates
    print("\n=== CORRECTED NET LOCATION ESTIMATION ===")
    
    # With corrected coordinates, goals should be at the ends of the rink
    # Assuming goals are at x = 0 and x = 60.96 (or close to these values)
    
    all_goalie_coords = pd.concat([
        saves_data[['pos_x_corrected', 'pos_y']], 
        goals_data[['pos_x_corrected', 'pos_y']]
    ])
    
    # Find the most common x-coordinate (likely net location)
    x_mode = all_goalie_coords['pos_x_corrected'].mode().iloc[0]
    y_center = all_goalie_coords['pos_y'].mean()
    
    print(f"Estimated net location (corrected): x = {x_mode:.2f}, y = {y_center:.2f}")
    
    # Analyze goalie positioning relative to corrected net
    print("\n=== CORRECTED GOALIE POSITIONING ANALYSIS ===")
    
    # Calculate distance from estimated net
    net_x, net_y = x_mode, y_center
    saves_data['distance_from_net'] = np.sqrt(
        (saves_data['pos_x_corrected'] - net_x)**2 + (saves_data['pos_y'] - net_y)**2
    )
    goals_data['distance_from_net'] = np.sqrt(
        (goals_data['pos_x_corrected'] - net_x)**2 + (goals_data['pos_y'] - net_y)**2
    )
    
    print("Saves - Distance from estimated net (corrected):")
    print(f"  Mean distance: {saves_data['distance_from_net'].mean():.2f}")
    print(f"  Min distance: {saves_data['distance_from_net'].min():.2f}")
    print(f"  Max distance: {saves_data['distance_from_net'].max():.2f}")
    
    print("\nGoals against - Distance from estimated net (corrected):")
    print(f"  Mean distance: {goals_data['distance_from_net'].mean():.2f}")
    print(f"  Min distance: {goals_data['distance_from_net'].min():.2f}")
    print(f"  Max distance: {goals_data['distance_from_net'].max():.2f}")
    
    # Corrected zone analysis
    print("\n=== CORRECTED ZONE ANALYSIS ===")
    
    # Define zones based on corrected x-coordinate
    def define_zone_corrected(pos_x, team, goalie_team):
        if team == goalie_team:
            if pos_x < 22.86:  # Defensive zone
                return "DZ"
            elif pos_x > 38.10:  # Offensive zone
                return "OZ"
            else:
                return "NZ"  # Neutral zone
        else:
            if pos_x > 38.10:  # Defensive zone for opposing team
                return "DZ"
            elif pos_x < 22.86:  # Offensive zone for opposing team
                return "OZ"
            else:
                return "NZ"
    
    saves_data['zone_corrected'] = saves_data.apply(
        lambda row: define_zone_corrected(row['pos_x_corrected'], row['team'], row['goalie_team']), axis=1
    )
    goals_data['zone_corrected'] = goals_data.apply(
        lambda row: define_zone_corrected(row['pos_x_corrected'], row['team'], row['goalie_team']), axis=1
    )
    
    print("Saves by zone (corrected):")
    print(saves_data['zone_corrected'].value_counts())
    print("\nGoals against by zone (corrected):")
    print(goals_data['zone_corrected'].value_counts())
    
    # High-danger area analysis (corrected)
    print("\n=== HIGH-DANGER AREA ANALYSIS (CORRECTED) ===")
    
    # Define high-danger area (slot) with corrected coordinates
    def is_slot_corrected(pos_x, pos_y):
        # High-danger area is typically in front of the net
        # With corrected coordinates, this should be closer to x = 0
        return (pos_x < 15) & (abs(pos_y) < 15)
    
    slot_saves = saves_data[is_slot_corrected(saves_data['pos_x_corrected'], saves_data['pos_y'])]
    slot_goals = goals_data[is_slot_corrected(goals_data['pos_x_corrected'], goals_data['pos_y'])]
    
    print(f"High-danger saves (slot area): {len(slot_saves)}")
    print(f"High-danger goals (slot area): {len(slot_goals)}")
    
    if len(slot_saves) > 0:
        print(f"High-danger save percentage: {len(slot_saves) / (len(slot_saves) + len(slot_goals)) * 100:.1f}%")
    
    # Create corrected visualizations
    print("\n=== CREATING CORRECTED VISUALIZATIONS ===")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Original vs Corrected coordinates comparison
    axes[0, 0].scatter(saves_data['pos_x'], saves_data['pos_y'], 
                      c='lightgreen', alpha=0.6, label='Saves (Original)', s=30)
    axes[0, 0].scatter(goals_data['pos_x'], goals_data['pos_y'], 
                      c='lightcoral', alpha=0.8, label='Goals (Original)', s=50, marker='x')
    axes[0, 0].set_xlabel('X Position (Original)')
    axes[0, 0].set_ylabel('Y Position')
    axes[0, 0].set_title('Original Coordinates')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Corrected coordinates
    axes[0, 1].scatter(saves_data['pos_x_corrected'], saves_data['pos_y'], 
                      c='green', alpha=0.6, label='Saves (Corrected)', s=50)
    axes[0, 1].scatter(goals_data['pos_x_corrected'], goals_data['pos_y'], 
                      c='red', alpha=0.8, label='Goals (Corrected)', s=100, marker='x')
    axes[0, 1].scatter(net_x, net_y, c='blue', s=200, marker='s', label='Estimated Net')
    axes[0, 1].axvline(x=22.86, color='orange', linestyle='--', alpha=0.7, label='DZ/NZ Line')
    axes[0, 1].axvline(x=38.10, color='orange', linestyle='--', alpha=0.7, label='NZ/OZ Line')
    axes[0, 1].set_xlabel('X Position (Corrected)')
    axes[0, 1].set_ylabel('Y Position')
    axes[0, 1].set_title('Corrected Coordinates with Zone Lines')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Zone distribution (corrected)
    if len(saves_data) > 0:
        zone_counts = saves_data['zone_corrected'].value_counts()
        axes[1, 0].pie(zone_counts.values, labels=zone_counts.index, autopct='%1.1f%%')
        axes[1, 0].set_title('Saves by Zone (Corrected)')
    
    # Plot 4: Distance from net (corrected)
    axes[1, 1].hist(saves_data['distance_from_net'], bins=20, alpha=0.7, 
                   label='Saves', color='green', density=True)
    axes[1, 1].hist(goals_data['distance_from_net'], bins=20, alpha=0.7, 
                   label='Goals Against', color='red', density=True)
    axes[1, 1].set_xlabel('Distance from Estimated Net (Corrected)')
    axes[1, 1].set_ylabel('Density')
    axes[1, 1].set_title('Distribution by Distance from Net (Corrected)')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/emilyfehr8/CascadeProjects/goalie_positioning_corrected.png', 
                dpi=300, bbox_inches='tight')
    print("Corrected visualization saved as 'goalie_positioning_corrected.png'")
    
    # Summary
    print("\n=== CORRECTED SUMMARY ===")
    print(f"1. Corrected net location: x = {net_x:.2f}, y = {net_y:.2f}")
    print(f"2. Most saves occur in the {saves_data['zone_corrected'].mode().iloc[0]} zone")
    print(f"3. Average distance from net for saves: {saves_data['distance_from_net'].mean():.2f}")
    print(f"4. Average distance from net for goals: {goals_data['distance_from_net'].mean():.2f}")
    print(f"5. High-danger saves: {len(slot_saves)}")
    print(f"6. High-danger goals: {len(slot_goals)}")
    
    return saves_data, goals_data

if __name__ == "__main__":
    saves_data, goals_data = analyze_goalie_positioning_corrected()
