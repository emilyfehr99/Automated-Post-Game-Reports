#!/usr/bin/env python3
"""
Determine net locations based on center ice faceoff circle alignment
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analyze_net_locations_center_ice():
    # Load the data
    print("Loading goalie data...")
    df = pd.read_csv('/Users/emilyfehr8/Desktop/goalie stuff incl.csv')
    
    # Get all coordinates to understand the rink layout
    all_coords = df[['pos_x', 'pos_y']].dropna()
    
    print("=== RINK LAYOUT ANALYSIS ===")
    print(f"Total coordinate points: {len(all_coords)}")
    print(f"X range: {all_coords['pos_x'].min():.2f} to {all_coords['pos_x'].max():.2f}")
    print(f"Y range: {all_coords['pos_y'].min():.2f} to {all_coords['pos_y'].max():.2f}")
    
    # Calculate rink dimensions
    rink_width = all_coords['pos_y'].max() - all_coords['pos_y'].min()
    rink_length = all_coords['pos_x'].max() - all_coords['pos_x'].min()
    
    print(f"\nRink dimensions:")
    print(f"  Width (Y): {rink_width:.2f} units")
    print(f"  Length (X): {rink_length:.2f} units")
    
    # Center ice should be at the middle of the rink width
    center_ice_y = all_coords['pos_y'].min() + (rink_width / 2)
    print(f"\nCenter ice Y coordinate: {center_ice_y:.2f}")
    
    # Analyze goalie actions
    goalie_actions = df[df['action'].isin(['Saves', 'Goals against'])]
    saves = goalie_actions[goalie_actions['action'] == 'Saves']
    goals = goalie_actions[goalie_actions['action'] == 'Goals against']
    
    print(f"\n=== GOALIE ACTIONS ANALYSIS ===")
    print(f"Goalie actions: {len(goalie_actions)}")
    print(f"  Saves: {len(saves)}")
    print(f"  Goals against: {len(goals)}")
    
    # Find net locations based on center ice alignment
    print("\n=== NET LOCATION HYPOTHESES (CENTER ICE ALIGNED) ===")
    
    # Hypothesis 1: Net at the end of the rink (minimum X) - defensive zone
    net_x_defensive = all_coords['pos_x'].min()
    net_y_center = center_ice_y
    
    print(f"Hypothesis 1 - Defensive zone net:")
    print(f"  Net location: X = {net_x_defensive:.2f}, Y = {net_y_center:.2f}")
    
    # Hypothesis 2: Net at the other end of the rink (maximum X) - offensive zone
    net_x_offensive = all_coords['pos_x'].max()
    
    print(f"\nHypothesis 2 - Offensive zone net:")
    print(f"  Net location: X = {net_x_offensive:.2f}, Y = {net_y_center:.2f}")
    
    # Analyze which net the goalies are defending
    print("\n=== GOALIE POSITIONING ANALYSIS ===")
    
    # Calculate distances to both nets
    saves_dist_defensive = np.sqrt((saves['pos_x'] - net_x_defensive)**2 + (saves['pos_y'] - net_y_center)**2)
    saves_dist_offensive = np.sqrt((saves['pos_x'] - net_x_offensive)**2 + (saves['pos_y'] - net_y_center)**2)
    
    goals_dist_defensive = np.sqrt((goals['pos_x'] - net_x_defensive)**2 + (goals['pos_y'] - net_y_center)**2)
    goals_dist_offensive = np.sqrt((goals['pos_x'] - net_x_offensive)**2 + (goals['pos_y'] - net_y_center)**2)
    
    print(f"Saves distance to defensive net: {saves_dist_defensive.mean():.2f}")
    print(f"Saves distance to offensive net: {saves_dist_offensive.mean():.2f}")
    print(f"Goals distance to defensive net: {goals_dist_defensive.mean():.2f}")
    print(f"Goals distance to offensive net: {goals_dist_offensive.mean():.2f}")
    
    # Determine which net goalies are defending
    if saves_dist_defensive.mean() < saves_dist_offensive.mean():
        defending_net_x = net_x_defensive
        defending_net_y = net_y_center
        print(f"\n✅ Goalies are defending the DEFENSIVE ZONE net")
        print(f"   Net location: X = {defending_net_x:.2f}, Y = {defending_net_y:.2f}")
    else:
        defending_net_x = net_x_offensive
        defending_net_y = net_y_center
        print(f"\n✅ Goalies are defending the OFFENSIVE ZONE net")
        print(f"   Net location: X = {defending_net_x:.2f}, Y = {defending_net_y:.2f}")
    
    # Analyze zone distribution
    print("\n=== ZONE ANALYSIS ===")
    
    # Define zones based on rink thirds
    zone_boundary_1 = all_coords['pos_x'].min() + (rink_length / 3)
    zone_boundary_2 = all_coords['pos_x'].min() + (2 * rink_length / 3)
    
    print(f"Zone boundaries:")
    print(f"  Defensive zone: X < {zone_boundary_1:.2f}")
    print(f"  Neutral zone: {zone_boundary_1:.2f} ≤ X ≤ {zone_boundary_2:.2f}")
    print(f"  Offensive zone: X > {zone_boundary_2:.2f}")
    
    # Categorize goalie actions by zone
    def categorize_zone(pos_x):
        if pos_x < zone_boundary_1:
            return "Defensive Zone"
        elif pos_x > zone_boundary_2:
            return "Offensive Zone"
        else:
            return "Neutral Zone"
    
    saves['zone'] = saves['pos_x'].apply(categorize_zone)
    goals['zone'] = goals['pos_x'].apply(categorize_zone)
    
    print(f"\nSaves by zone:")
    print(saves['zone'].value_counts())
    print(f"\nGoals against by zone:")
    print(goals['zone'].value_counts())
    
    # High-danger area analysis (slot area in front of net)
    print("\n=== HIGH-DANGER AREA ANALYSIS ===")
    
    # Define high-danger area as close to the defending net
    defending_net_distance = np.sqrt((saves['pos_x'] - defending_net_x)**2 + (saves['pos_y'] - defending_net_y)**2)
    high_danger_threshold = 15  # Within 15 units of net
    
    high_danger_saves = saves[defending_net_distance < high_danger_threshold]
    high_danger_goals = goals[np.sqrt((goals['pos_x'] - defending_net_x)**2 + (goals['pos_y'] - defending_net_y)**2) < high_danger_threshold]
    
    print(f"High-danger saves (within {high_danger_threshold} units of net): {len(high_danger_saves)}")
    print(f"High-danger goals (within {high_danger_threshold} units of net): {len(high_danger_goals)}")
    
    if len(high_danger_saves) + len(high_danger_goals) > 0:
        high_danger_save_pct = len(high_danger_saves) / (len(high_danger_saves) + len(high_danger_goals)) * 100
        print(f"High-danger save percentage: {high_danger_save_pct:.1f}%")
    
    # Create visualization
    print("\n=== CREATING VISUALIZATION ===")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: All coordinates with net locations
    axes[0, 0].scatter(all_coords['pos_x'], all_coords['pos_y'], 
                      alpha=0.1, s=5, color='gray', label='All coordinates')
    axes[0, 0].scatter(saves['pos_x'], saves['pos_y'], 
                      c='green', alpha=0.6, label='Saves', s=50)
    axes[0, 0].scatter(goals['pos_x'], goals['pos_y'], 
                      c='red', alpha=0.8, label='Goals Against', s=100, marker='x')
    axes[0, 0].scatter(net_x_defensive, net_y_center, 
                      c='blue', s=200, marker='s', label='Defensive Net')
    axes[0, 0].scatter(net_x_offensive, net_y_center, 
                      c='orange', s=200, marker='s', label='Offensive Net')
    axes[0, 0].axvline(x=zone_boundary_1, color='purple', linestyle='--', alpha=0.7, label='Zone Boundary')
    axes[0, 0].axvline(x=zone_boundary_2, color='purple', linestyle='--', alpha=0.7)
    axes[0, 0].set_xlabel('X Position')
    axes[0, 0].set_ylabel('Y Position')
    axes[0, 0].set_title('Rink Layout with Net Locations')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Zone distribution
    zone_counts = saves['zone'].value_counts()
    axes[0, 1].pie(zone_counts.values, labels=zone_counts.index, autopct='%1.1f%%')
    axes[0, 1].set_title('Saves by Zone')
    
    # Plot 3: Distance from defending net
    defending_distances = np.sqrt((saves['pos_x'] - defending_net_x)**2 + (saves['pos_y'] - defending_net_y)**2)
    axes[1, 0].hist(defending_distances, bins=20, alpha=0.7, color='green', label='Saves')
    if len(goals) > 0:
        goal_distances = np.sqrt((goals['pos_x'] - defending_net_x)**2 + (goals['pos_y'] - defending_net_y)**2)
        axes[1, 0].hist(goal_distances, bins=20, alpha=0.7, color='red', label='Goals')
    axes[1, 0].set_xlabel('Distance from Defending Net')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Distance Distribution from Defending Net')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: High-danger area
    axes[1, 1].scatter(saves['pos_x'], saves['pos_y'], 
                      c='lightgreen', alpha=0.6, label='All Saves', s=30)
    axes[1, 1].scatter(high_danger_saves['pos_x'], high_danger_saves['pos_y'], 
                      c='green', alpha=0.8, label='High-Danger Saves', s=80)
    if len(high_danger_goals) > 0:
        axes[1, 1].scatter(high_danger_goals['pos_x'], high_danger_goals['pos_y'], 
                          c='red', alpha=0.8, label='High-Danger Goals', s=100, marker='x')
    axes[1, 1].scatter(defending_net_x, defending_net_y, 
                      c='blue', s=200, marker='s', label='Defending Net')
    # Draw high-danger circle
    circle = plt.Circle((defending_net_x, defending_net_y), high_danger_threshold, 
                       fill=False, color='red', linestyle='--', alpha=0.7, label='High-Danger Area')
    axes[1, 1].add_patch(circle)
    axes[1, 1].set_xlabel('X Position')
    axes[1, 1].set_ylabel('Y Position')
    axes[1, 1].set_title('High-Danger Area Analysis')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/emilyfehr8/CascadeProjects/net_location_center_ice_analysis.png', 
                dpi=300, bbox_inches='tight')
    print("Center ice analysis visualization saved as 'net_location_center_ice_analysis.png'")
    
    # Summary
    print("\n=== FINAL SUMMARY ===")
    print(f"✅ Defending net location: X = {defending_net_x:.2f}, Y = {defending_net_y:.2f}")
    print(f"✅ Center ice Y coordinate: {net_y_center:.2f}")
    print(f"✅ Rink dimensions: {rink_length:.2f} x {rink_width:.2f}")
    print(f"✅ High-danger saves: {len(high_danger_saves)}")
    print(f"✅ High-danger goals: {len(high_danger_goals)}")
    if len(high_danger_saves) + len(high_danger_goals) > 0:
        print(f"✅ High-danger save percentage: {high_danger_save_pct:.1f}%")
    
    return {
        'defending_net_x': defending_net_x,
        'defending_net_y': defending_net_y,
        'center_ice_y': net_y_center,
        'rink_length': rink_length,
        'rink_width': rink_width
    }

if __name__ == "__main__":
    net_locations = analyze_net_locations_center_ice()
