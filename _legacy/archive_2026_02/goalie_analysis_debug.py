#!/usr/bin/env python3
"""
Debug analysis for goalie data to identify issues causing zeros in R calculations
"""

import pandas as pd
import numpy as np

def analyze_goalie_data():
    # Load the data
    print("Loading goalie data...")
    df = pd.read_csv('/Users/emilyfehr8/Desktop/goalie stuff incl.csv')
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Check for missing values
    print("\n=== MISSING VALUES ===")
    print(df.isnull().sum())
    
    # Check data types
    print("\n=== DATA TYPES ===")
    print(df.dtypes)
    
    # Identify goalies (players with Saves or Goals against)
    goalie_actions = df[df['action'].isin(['Saves', 'Goals against'])]
    goalies = goalie_actions['player'].unique()
    print(f"\n=== GOALIES FOUND ===")
    print(f"Goalies: {list(goalies)}")
    
    # Get goalie teams
    goalie_teams = {}
    for goalie in goalies:
        team = goalie_actions[goalie_actions['player'] == goalie]['team'].iloc[0]
        goalie_teams[goalie] = team
        print(f"{goalie}: {team}")
    
    # Add goalie team column
    df['goalie_team'] = df['player'].map(goalie_teams)
    
    # Filter for goalie-specific data
    goalie_data = df[df['player'].isin(goalies)].copy()
    print(f"\nGoalie data shape: {goalie_data.shape}")
    
    # Check action frequencies
    print("\n=== ACTION FREQUENCIES ===")
    action_counts = goalie_data['action'].value_counts()
    print(action_counts)
    
    # Check critical actions
    critical_actions = ['Saves', 'Goals against', 'Shots', 'Power play shots', 
                       'Short-handed shots', 'Accurate passes', 'Passes', 'Passes to the slot']
    
    print("\n=== CRITICAL ACTIONS CHECK ===")
    for action in critical_actions:
        count = (goalie_data['action'] == action).sum()
        print(f"{action}: {count}")
    
    # Check coordinate ranges
    print("\n=== COORDINATE ANALYSIS ===")
    shots_data = goalie_data[goalie_data['action'] == 'Shots']
    print(f"Total shots: {len(shots_data)}")
    if len(shots_data) > 0:
        print(f"pos_x range: {shots_data['pos_x'].min():.2f} to {shots_data['pos_x'].max():.2f}")
        print(f"pos_y range: {shots_data['pos_y'].min():.2f} to {shots_data['pos_y'].max():.2f}")
        
        # Check for shots by opposing team
        opposing_shots = shots_data[shots_data['team'] != shots_data['goalie_team']]
        print(f"Shots by opposing team: {len(opposing_shots)}")
        
        # Check slot shots
        slot_shots = opposing_shots[
            (abs(opposing_shots['pos_x']) < 30) & 
            (abs(opposing_shots['pos_y']) < 15)
        ]
        print(f"Slot shots (|pos_x| < 30, |pos_y| < 15): {len(slot_shots)}")
    
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
    
    # Calculate save percentages
    print("\n=== SAVE PERCENTAGE ANALYSIS ===")
    
    # Overall save percentage
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie]
        saves = (goalie_subset['action'] == 'Saves').sum()
        goals_against = (goalie_subset['action'] == 'Goals against').sum()
        total = saves + goals_against
        
        print(f"\n{goalie}:")
        print(f"  Saves: {saves}")
        print(f"  Goals against: {goals_against}")
        print(f"  Total shots faced: {total}")
        if total > 0:
            save_pct = (saves / total) * 100
            print(f"  Save percentage: {save_pct:.2f}%")
        else:
            print(f"  Save percentage: N/A (no shots faced)")
    
    # Check for rebound sequences
    print("\n=== REBOUND ANALYSIS ===")
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie].sort_values('start')
        
        # Look for saves followed by more saves/goals within 5 actions
        rebound_sequences = 0
        for i in range(len(goalie_subset) - 5):
            current_action = goalie_subset.iloc[i]['action']
            if current_action == 'Saves':
                # Check next 5 actions for saves/goals
                next_actions = goalie_subset.iloc[i+1:i+6]['action'].tolist()
                if 'Saves' in next_actions or 'Goals against' in next_actions:
                    rebound_sequences += 1
        
        print(f"{goalie}: {rebound_sequences} rebound sequences found")
    
    # Check for pass sequences
    print("\n=== PASS SEQUENCE ANALYSIS ===")
    for goalie in goalie_data['goalie_team'].unique():
        if pd.isna(goalie):
            continue
            
        team_data = goalie_data[goalie_data['goalie_team'] == goalie]
        opposing_shots = team_data[
            (team_data['action'] == 'Shots') & 
            (team_data['team'] != team_data['goalie_team'])
        ]
        
        pass_sequences = 0
        for i in range(len(team_data) - 1):
            current_row = team_data.iloc[i]
            next_row = team_data.iloc[i + 1] if i + 1 < len(team_data) else None
            
            if (current_row['action'] == 'Shots' and 
                current_row['team'] != current_row['goalie_team'] and
                next_row and next_row['action'] in ['Saves', 'Goals against']):
                
                # Check if any of the previous 5 actions were passes
                prev_actions = team_data.iloc[max(0, i-5):i]['action'].tolist()
                pass_actions = ['Accurate passes', 'Passes', 'Passes to the slot']
                if any(action in pass_actions for action in prev_actions):
                    pass_sequences += 1
        
        print(f"Team {goalie}: {pass_sequences} pass sequences found")
    
    # Check duration issues
    print("\n=== DURATION ANALYSIS ===")
    print(f"Duration range: {goalie_data['duration'].min()} to {goalie_data['duration'].max()}")
    print(f"Zero duration entries: {(goalie_data['duration'] == 0).sum()}")
    print(f"Total duration: {goalie_data['duration'].sum()}")
    
    # Check for data quality issues
    print("\n=== DATA QUALITY ISSUES ===")
    
    # Check for empty strings
    for col in ['player', 'team', 'action']:
        empty_count = (goalie_data[col] == '').sum()
        print(f"Empty {col}: {empty_count}")
    
    # Check for inconsistent team names
    print("\nTeam names in dataset:")
    print(goalie_data['team'].value_counts())
    
    print("\nGoalie team names:")
    print(goalie_data['goalie_team'].value_counts())
    
    return goalie_data

if __name__ == "__main__":
    goalie_data = analyze_goalie_data()
