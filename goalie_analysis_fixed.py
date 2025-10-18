#!/usr/bin/env python3
"""
Fixed goalie analysis based on the actual data structure
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_goalie_data_fixed():
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
    
    # Define zones
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
    
    goalie_data['zone'] = goalie_data.apply(
        lambda row: define_zone(row['pos_x'], row['team'], row['goalie_team']), 
        axis=1
    )
    
    # Helper function for save percentage
    def calc_save_pct(saves, goals):
        total = saves + goals
        if total > 0:
            return (saves / total) * 100
        else:
            return np.nan
    
    # Helper for slot area (high-danger)
    def is_slot(pos_x, pos_y):
        return (abs(pos_x) < 30) & (abs(pos_y) < 15)
    
    print("=== MAIN ISSUES IDENTIFIED ===")
    print("1. The dataset uses 'Shots against' instead of 'Shots' for goalie analysis")
    print("2. No 'Power play shots' or 'Short-handed shots' actions found")
    print("3. No 'Passes to the slot' actions found")
    print("4. Shot data is in 'Shots against' column, not 'Shots'")
    print("5. Duration is constant (12) for all entries")
    
    print("\n=== CORRECTED ANALYSIS ===")
    
    # 1. Save Percentage Metrics
    print("\n1. SAVE PERCENTAGE METRICS")
    print("-" * 40)
    
    # Overall Save Percentage
    overall_save_pct = goalie_data.groupby('player').agg({
        'action': lambda x: {
            'saves': (x == 'Saves').sum(),
            'goals_against': (x == 'Goals against').sum()
        }
    }).reset_index()
    
    overall_save_pct[['saves', 'goals_against']] = overall_save_pct['action'].apply(pd.Series)
    overall_save_pct['save_pct'] = overall_save_pct.apply(
        lambda row: calc_save_pct(row['saves'], row['goals_against']), axis=1
    )
    
    print("Overall Save Percentage:")
    print(overall_save_pct[['player', 'saves', 'goals_against', 'save_pct']])
    
    # Save Percentage by Zone
    save_pct_by_zone = goalie_data[goalie_data['action'].isin(['Saves', 'Goals against'])].groupby(['player', 'zone']).agg({
        'action': lambda x: {
            'saves': (x == 'Saves').sum(),
            'goals_against': (x == 'Goals against').sum()
        }
    }).reset_index()
    
    save_pct_by_zone[['saves', 'goals_against']] = save_pct_by_zone['action'].apply(pd.Series)
    save_pct_by_zone['save_pct'] = save_pct_by_zone.apply(
        lambda row: calc_save_pct(row['saves'], row['goals_against']), axis=1
    )
    
    print("\nSave Percentage by Zone:")
    print(save_pct_by_zone[['player', 'zone', 'saves', 'goals_against', 'save_pct']])
    
    # Save Percentage by Half
    save_pct_by_half = goalie_data[goalie_data['action'].isin(['Saves', 'Goals against'])].groupby(['player', 'half']).agg({
        'action': lambda x: {
            'saves': (x == 'Saves').sum(),
            'goals_against': (x == 'Goals against').sum()
        }
    }).reset_index()
    
    save_pct_by_half[['saves', 'goals_against']] = save_pct_by_half['action'].apply(pd.Series)
    save_pct_by_half['save_pct'] = save_pct_by_half.apply(
        lambda row: calc_save_pct(row['saves'], row['goals_against']), axis=1
    )
    
    print("\nSave Percentage by Half:")
    print(save_pct_by_half[['player', 'half', 'saves', 'goals_against', 'save_pct']])
    
    # 2. Workload Metrics
    print("\n2. WORKLOAD METRICS")
    print("-" * 40)
    
    # Shot Suppression Rate (using 'Shots against' instead of 'Shots')
    shot_suppression = goalie_data[goalie_data['action'] == 'Shots against'].groupby(['player', 'half']).agg({
        'action': 'count',
        'duration': 'sum'
    }).reset_index()
    shot_suppression.columns = ['player', 'half', 'shots_against', 'duration_half']
    shot_suppression['shot_rate_per_min'] = shot_suppression['shots_against'] / (shot_suppression['duration_half'] / 60)
    
    print("Shot Suppression Rate by Half (Shots against per minute):")
    print(shot_suppression[['player', 'half', 'shots_against', 'shot_rate_per_min']])
    
    # Goals Against Average
    total_duration = goalie_data['duration'].sum()
    gaa = goalie_data[goalie_data['action'] == 'Goals against'].groupby('player').agg({
        'action': 'count'
    }).reset_index()
    gaa.columns = ['player', 'goals_against']
    gaa['gaa'] = gaa['goals_against'] / (total_duration / 60)
    
    print("\nGoals Against Average (per 60 minutes):")
    print(gaa)
    
    # High-Danger Shots Faced (using 'Shots against' with position data)
    high_danger_shots = goalie_data[
        (goalie_data['action'] == 'Shots against') & 
        is_slot(goalie_data['pos_x'], goalie_data['pos_y'])
    ].groupby('player').size().reset_index(name='high_danger_shots')
    
    print("\nHigh-Danger Shots Faced (in slot area):")
    print(high_danger_shots)
    
    # Shot Location Metrics
    shot_locations = goalie_data[goalie_data['action'] == 'Shots against'].groupby('player').agg({
        'action': 'count',
        'pos_x': ['mean', 'var'],
        'pos_y': ['mean', 'var']
    }).reset_index()
    
    shot_locations.columns = ['player', 'shots', 'avg_pos_x', 'var_pos_x', 'avg_pos_y', 'var_pos_y']
    
    print("\nShot Location Metrics (Average and Variance):")
    print(shot_locations)
    
    # 3. Additional Analysis
    print("\n3. ADDITIONAL ANALYSIS")
    print("-" * 40)
    
    # Rebound Analysis (saves followed by more saves/goals)
    rebound_analysis = []
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie].sort_values('start')
        rebound_sequences = 0
        rebound_saves = 0
        rebound_goals = 0
        
        for i in range(len(goalie_subset) - 5):
            current_action = goalie_subset.iloc[i]['action']
            if current_action == 'Saves':
                # Check next 5 actions for saves/goals
                next_actions = goalie_subset.iloc[i+1:i+6]['action'].tolist()
                if 'Saves' in next_actions or 'Goals against' in next_actions:
                    rebound_sequences += 1
                    if 'Saves' in next_actions:
                        rebound_saves += 1
                    if 'Goals against' in next_actions:
                        rebound_goals += 1
        
        rebound_analysis.append({
            'player': goalie,
            'rebound_sequences': rebound_sequences,
            'rebound_saves': rebound_saves,
            'rebound_goals': rebound_goals,
            'rebound_save_pct': calc_save_pct(rebound_saves, rebound_goals)
        })
    
    rebound_df = pd.DataFrame(rebound_analysis)
    print("Rebound Analysis:")
    print(rebound_df)
    
    # Create visualization
    print("\n4. CREATING VISUALIZATIONS")
    print("-" * 40)
    
    # Save percentage comparison
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Overall save percentage
    axes[0, 0].bar(overall_save_pct['player'], overall_save_pct['save_pct'])
    axes[0, 0].set_title('Overall Save Percentage')
    axes[0, 0].set_ylabel('Save Percentage (%)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Save percentage by zone
    if len(save_pct_by_zone) > 0:
        pivot_zone = save_pct_by_zone.pivot(index='player', columns='zone', values='save_pct')
        pivot_zone.plot(kind='bar', ax=axes[0, 1])
        axes[0, 1].set_title('Save Percentage by Zone')
        axes[0, 1].set_ylabel('Save Percentage (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].legend(title='Zone')
    
    # Shot rate per minute
    if len(shot_suppression) > 0:
        pivot_shots = shot_suppression.pivot(index='player', columns='half', values='shot_rate_per_min')
        pivot_shots.plot(kind='bar', ax=axes[1, 0])
        axes[1, 0].set_title('Shot Rate per Minute by Half')
        axes[1, 0].set_ylabel('Shots per Minute')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].legend(title='Half')
    
    # Goals against average
    axes[1, 1].bar(gaa['player'], gaa['gaa'])
    axes[1, 1].set_title('Goals Against Average (per 60 min)')
    axes[1, 1].set_ylabel('GAA')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('/Users/emilyfehr8/CascadeProjects/goalie_analysis_results.png', dpi=300, bbox_inches='tight')
    print("Visualization saved as 'goalie_analysis_results.png'")
    
    # Summary report
    print("\n5. SUMMARY REPORT")
    print("=" * 50)
    print("Key Findings:")
    print(f"- Total goalies analyzed: {len(goalies)}")
    print(f"- Total saves: {overall_save_pct['saves'].sum()}")
    print(f"- Total goals against: {overall_save_pct['goals_against'].sum()}")
    print(f"- Overall save percentage: {overall_save_pct['save_pct'].mean():.2f}%")
    print(f"- Best save percentage: {overall_save_pct['save_pct'].max():.2f}% ({overall_save_pct.loc[overall_save_pct['save_pct'].idxmax(), 'player']})")
    print(f"- Total shots against: {shot_suppression['shots_against'].sum()}")
    print(f"- High-danger shots faced: {high_danger_shots['high_danger_shots'].sum()}")
    
    return goalie_data, overall_save_pct, save_pct_by_zone, save_pct_by_half, shot_suppression, gaa

if __name__ == "__main__":
    goalie_data, overall_save_pct, save_pct_by_zone, save_pct_by_half, shot_suppression, gaa = analyze_goalie_data_fixed()
