#!/usr/bin/env python3
"""
Determine net locations based on coordinate patterns in the data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def determine_net_locations():
    # Load the data
    print("Loading goalie data...")
    df = pd.read_csv('/Users/emilyfehr8/Desktop/goalie stuff incl.csv')
    
    # Get all unique coordinates to understand the rink layout
    all_coords = df[['pos_x', 'pos_y']].dropna()
    
    print("=== COORDINATE SYSTEM ANALYSIS ===")
    print(f"Total coordinate points: {len(all_coords)}")
    print(f"X range: {all_coords['pos_x'].min():.2f} to {all_coords['pos_x'].max():.2f}")
    print(f"Y range: {all_coords['pos_y'].min():.2f} to {all_coords['pos_y'].max():.2f}")
    
    # Analyze goalie-specific actions (saves and goals)
    goalie_actions = df[df['action'].isin(['Saves', 'Goals against'])]
    
    print(f"\nGoalie actions: {len(goalie_actions)}")
    print(f"Goalie X range: {goalie_actions['pos_x'].min():.2f} to {goalie_actions['pos_x'].max():.2f}")
    print(f"Goalie Y range: {goalie_actions['pos_y'].min():.2f} to {goalie_actions['pos_y'].max():.2f}")
    
    # Look for coordinate clustering patterns
    print("\n=== COORDINATE CLUSTERING ANALYSIS ===")
    
    # Find the most common X coordinates (likely net locations)
    x_counts = goalie_actions['pos_x'].value_counts().head(10)
    print("Most common X coordinates (likely net locations):")
    for x, count in x_counts.items():
        print(f"  X = {x:.2f}: {count} occurrences")
    
    # Find the most common Y coordinates (likely net center)
    y_counts = goalie_actions['pos_y'].value_counts().head(10)
    print("\nMost common Y coordinates (likely net center):")
    for y, count in y_counts.items():
        print(f"  Y = {y:.2f}: {count} occurrences")
    
    # Analyze by action type
    print("\n=== ANALYSIS BY ACTION TYPE ===")
    
    saves = goalie_actions[goalie_actions['action'] == 'Saves']
    goals = goalie_actions[goalie_actions['action'] == 'Goals against']
    
    print(f"Saves - X range: {saves['pos_x'].min():.2f} to {saves['pos_x'].max():.2f}")
    print(f"Saves - Y range: {saves['pos_y'].min():.2f} to {saves['pos_y'].max():.2f}")
    print(f"Saves - X mean: {saves['pos_x'].mean():.2f}")
    print(f"Saves - Y mean: {saves['pos_y'].mean():.2f}")
    
    print(f"\nGoals - X range: {goals['pos_x'].min():.2f} to {goals['pos_x'].max():.2f}")
    print(f"Goals - Y range: {goals['pos_y'].min():.2f} to {goals['pos_y'].max():.2f}")
    print(f"Goals - X mean: {goals['pos_x'].mean():.2f}")
    print(f"Goals - Y mean: {goals['pos_y'].mean():.2f}")
    
    # Try different net location hypotheses
    print("\n=== NET LOCATION HYPOTHESES ===")
    
    # Hypothesis 1: Net at the most common X coordinate
    net_x_hypothesis1 = goalie_actions['pos_x'].mode().iloc[0]
    net_y_hypothesis1 = goalie_actions['pos_y'].mean()
    
    print(f"Hypothesis 1 - Net at most common X:")
    print(f"  Net location: X = {net_x_hypothesis1:.2f}, Y = {net_y_hypothesis1:.2f}")
    
    # Hypothesis 2: Net at the minimum X coordinate (closest to goal)
    net_x_hypothesis2 = goalie_actions['pos_x'].min()
    net_y_hypothesis2 = goalie_actions['pos_y'].mean()
    
    print(f"\nHypothesis 2 - Net at minimum X:")
    print(f"  Net location: X = {net_x_hypothesis2:.2f}, Y = {net_y_hypothesis2:.2f}")
    
    # Hypothesis 3: Net at the maximum X coordinate (furthest from goal)
    net_x_hypothesis3 = goalie_actions['pos_x'].max()
    net_y_hypothesis3 = goalie_actions['pos_y'].mean()
    
    print(f"\nHypothesis 3 - Net at maximum X:")
    print(f"  Net location: X = {net_x_hypothesis3:.2f}, Y = {net_y_hypothesis3:.2f}")
    
    # Calculate distances for each hypothesis
    print("\n=== DISTANCE ANALYSIS FOR EACH HYPOTHESIS ===")
    
    for i, (net_x, net_y) in enumerate([(net_x_hypothesis1, net_y_hypothesis1),
                                       (net_x_hypothesis2, net_y_hypothesis2),
                                       (net_x_hypothesis3, net_y_hypothesis3)], 1):
        
        saves_dist = np.sqrt((saves['pos_x'] - net_x)**2 + (saves['pos_y'] - net_y)**2)
        goals_dist = np.sqrt((goals['pos_x'] - net_x)**2 + (goals['pos_y'] - net_y)**2)
        
        print(f"Hypothesis {i}:")
        print(f"  Saves - Mean distance: {saves_dist.mean():.2f}")
        print(f"  Goals - Mean distance: {goals_dist.mean():.2f}")
        print(f"  Distance difference: {abs(saves_dist.mean() - goals_dist.mean()):.2f}")
    
    # Create visualization
    print("\n=== CREATING VISUALIZATION ===")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: All coordinates
    axes[0, 0].scatter(all_coords['pos_x'], all_coords['pos_y'], 
                      alpha=0.3, s=10, color='gray', label='All coordinates')
    axes[0, 0].scatter(goalie_actions['pos_x'], goalie_actions['pos_y'], 
                      c='red', alpha=0.8, s=50, label='Goalie actions')
    axes[0, 0].set_xlabel('X Position')
    axes[0, 0].set_ylabel('Y Position')
    axes[0, 0].set_title('All Coordinates vs Goalie Actions')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Saves vs Goals
    axes[0, 1].scatter(saves['pos_x'], saves['pos_y'], 
                      c='green', alpha=0.6, label='Saves', s=50)
    axes[0, 1].scatter(goals['pos_x'], goals['pos_y'], 
                      c='red', alpha=0.8, label='Goals Against', s=100, marker='x')
    axes[0, 1].set_xlabel('X Position')
    axes[0, 1].set_ylabel('Y Position')
    axes[0, 1].set_title('Saves vs Goals Against')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: X coordinate distribution
    axes[1, 0].hist(goalie_actions['pos_x'], bins=30, alpha=0.7, color='blue')
    axes[1, 0].axvline(x=net_x_hypothesis1, color='red', linestyle='--', label=f'Most common X = {net_x_hypothesis1:.2f}')
    axes[1, 0].axvline(x=net_x_hypothesis2, color='green', linestyle='--', label=f'Min X = {net_x_hypothesis2:.2f}')
    axes[1, 0].axvline(x=net_x_hypothesis3, color='orange', linestyle='--', label=f'Max X = {net_x_hypothesis3:.2f}')
    axes[1, 0].set_xlabel('X Position')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('X Coordinate Distribution')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Y coordinate distribution
    axes[1, 1].hist(goalie_actions['pos_y'], bins=30, alpha=0.7, color='purple')
    axes[1, 1].axvline(x=net_y_hypothesis1, color='red', linestyle='--', label=f'Mean Y = {net_y_hypothesis1:.2f}')
    axes[1, 1].set_xlabel('Y Position')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('Y Coordinate Distribution')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/emilyfehr8/CascadeProjects/net_location_analysis.png', 
                dpi=300, bbox_inches='tight')
    print("Analysis visualization saved as 'net_location_analysis.png'")
    
    # Summary
    print("\n=== SUMMARY ===")
    print("Based on the coordinate patterns, here are the most likely net locations:")
    print(f"1. Most common X coordinate: {net_x_hypothesis1:.2f}")
    print(f"2. Minimum X coordinate: {net_x_hypothesis2:.2f}")
    print(f"3. Maximum X coordinate: {net_x_hypothesis3:.2f}")
    print(f"4. Mean Y coordinate (net center): {net_y_hypothesis1:.2f}")
    print("\nPlease check the coordinate_system.png image to verify which hypothesis matches the actual net locations on the rink diagram.")
    
    return {
        'net_x_most_common': net_x_hypothesis1,
        'net_x_min': net_x_hypothesis2,
        'net_x_max': net_x_hypothesis3,
        'net_y_center': net_y_hypothesis1
    }

if __name__ == "__main__":
    net_locations = determine_net_locations()
