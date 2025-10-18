#!/usr/bin/env python3
"""
Verify Goals After Passes Analysis
Check if we're properly capturing both saves AND goals after passes
"""

import pandas as pd
import numpy as np

def verify_goals_after_passes():
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
    
    # Sort data by start time for sequence analysis
    goalie_data = goalie_data.sort_values('start').reset_index(drop=True)
    
    print("=== VERIFYING GOALS AFTER PASSES ===")
    print(f"Goalies analyzed: {list(goalies)}")
    print(f"Total actions in dataset: {len(goalie_data)}")
    
    # Check what actions exist
    all_actions = goalie_data['action'].unique()
    print(f"\nAll unique actions: {sorted(all_actions)}")
    
    # Count saves and goals
    total_saves = len(goalie_data[goalie_data['action'] == 'Saves'])
    total_goals = len(goalie_data[goalie_data['action'] == 'Goals against'])
    print(f"\nTotal saves: {total_saves}")
    print(f"Total goals: {total_goals}")
    
    # Analyze each goalie individually
    for goalie in goalies:
        print(f"\n{'='*60}")
        print(f"ANALYZING GOALIE: {goalie}")
        print(f"{'='*60}")
        
        goalie_subset = goalie_data[goalie_data['player'] == goalie].copy().reset_index(drop=True)
        print(f"Total actions for {goalie}: {len(goalie_subset)}")
        
        # Count saves and goals for this goalie
        goalie_saves = len(goalie_subset[goalie_subset['action'] == 'Saves'])
        goalie_goals = len(goalie_subset[goalie_subset['action'] == 'Goals against'])
        print(f"Saves: {goalie_saves}")
        print(f"Goals: {goalie_goals}")
        
        # Find all pass actions
        pass_indices = goalie_subset[goalie_subset['action'].isin(['Accurate passes', 'Passes', 'Passes to the slot'])].index.tolist()
        print(f"Pass actions found: {len(pass_indices)}")
        
        # Find shots after passes within 5 actions
        pass_shot_sequences = []
        
        for pass_idx in pass_indices:
            # Look for shots within 5 actions after this pass
            for i in range(1, 6):  # 1 to 5 actions after
                check_idx = pass_idx + i
                if check_idx < len(goalie_subset):
                    action = goalie_subset.iloc[check_idx]['action']
                    if action in ['Saves', 'Goals against']:
                        sequence = {
                            'pass_index': pass_idx,
                            'shot_index': check_idx,
                            'pass_action': goalie_subset.iloc[pass_idx]['action'],
                            'shot_action': action,
                            'pass_time': goalie_subset.iloc[pass_idx]['start'],
                            'shot_time': goalie_subset.iloc[check_idx]['start'],
                            'actions_between': i - 1
                        }
                        pass_shot_sequences.append(sequence)
        
        print(f"\nShots after passes found: {len(pass_shot_sequences)}")
        
        # Count saves vs goals after passes
        saves_after_pass = len([seq for seq in pass_shot_sequences if seq['shot_action'] == 'Saves'])
        goals_after_pass = len([seq for seq in pass_shot_sequences if seq['shot_action'] == 'Goals against'])
        
        print(f"Saves after passes: {saves_after_pass}")
        print(f"Goals after passes: {goals_after_pass}")
        
        if len(pass_shot_sequences) > 0:
            print(f"\nDetailed breakdown:")
            for i, seq in enumerate(pass_shot_sequences):
                print(f"  Sequence {i+1}: {seq['shot_action']} at time {seq['shot_time']} (after {seq['pass_action']} at time {seq['pass_time']})")
            
            if goals_after_pass > 0:
                print(f"\n*** GOALS AFTER PASSES FOUND! ***")
                print("This goalie has goals that occur after passes within 5 actions.")
            else:
                print(f"\nNo goals found after passes for this goalie.")
        else:
            print("No shots found within 5 actions after any pass")
    
    # Overall summary
    print(f"\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")
    
    total_pass_shot_sequences = 0
    total_saves_after_pass = 0
    total_goals_after_pass = 0
    
    for goalie in goalies:
        goalie_subset = goalie_data[goalie_data['player'] == goalie].copy().reset_index(drop=True)
        pass_indices = goalie_subset[goalie_subset['action'].isin(['Accurate passes', 'Passes', 'Passes to the slot'])].index.tolist()
        
        pass_shot_sequences = []
        for pass_idx in pass_indices:
            for i in range(1, 6):
                check_idx = pass_idx + i
                if check_idx < len(goalie_subset):
                    action = goalie_subset.iloc[check_idx]['action']
                    if action in ['Saves', 'Goals against']:
                        pass_shot_sequences.append(action)
        
        saves_after_pass = len([action for action in pass_shot_sequences if action == 'Saves'])
        goals_after_pass = len([action for action in pass_shot_sequences if action == 'Goals against'])
        
        total_pass_shot_sequences += len(pass_shot_sequences)
        total_saves_after_pass += saves_after_pass
        total_goals_after_pass += goals_after_pass
        
        print(f"{goalie}: {saves_after_pass} saves, {goals_after_pass} goals after passes")
    
    print(f"\nTOTAL ACROSS ALL GOALIES:")
    print(f"Shots after passes: {total_pass_shot_sequences}")
    print(f"Saves after passes: {total_saves_after_pass}")
    print(f"Goals after passes: {total_goals_after_pass}")
    
    if total_goals_after_pass > 0:
        print(f"\n*** GOALS AFTER PASSES CONFIRMED! ***")
        print(f"Save percentage after passes: {(total_saves_after_pass / total_pass_shot_sequences) * 100:.1f}%")
    else:
        print(f"\n*** NO GOALS AFTER PASSES FOUND ***")
        print("All shots after passes were saves (100% save percentage)")

if __name__ == "__main__":
    verify_goals_after_passes()
