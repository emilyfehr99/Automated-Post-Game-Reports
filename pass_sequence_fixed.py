#!/usr/bin/env python3
"""
Fixed Pass Sequence Analysis
Analyze all instances of shots after passes within 5 actions
"""

import pandas as pd
import numpy as np

def analyze_pass_sequences():
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
    
    print("=== PASS SEQUENCE ANALYSIS ===")
    print(f"Goalies analyzed: {list(goalies)}")
    print(f"Total actions in dataset: {len(goalie_data)}")
    
    # Check what pass-related actions exist
    all_actions = goalie_data['action'].unique()
    pass_actions = [action for action in all_actions if 'pass' in action.lower()]
    print(f"\nPass-related actions found: {pass_actions}")
    
    # Check what shot-related actions exist
    shot_actions = [action for action in all_actions if 'shot' in action.lower() or action in ['Saves', 'Goals against']]
    print(f"Shot-related actions found: {shot_actions}")
    
    # Analyze pass sequences for each goalie
    for goalie in goalies:
        print(f"\n{'='*60}")
        print(f"ANALYZING GOALIE: {goalie}")
        print(f"{'='*60}")
        
        goalie_subset = goalie_data[goalie_data['player'] == goalie].copy().reset_index(drop=True)
        print(f"Total actions for {goalie}: {len(goalie_subset)}")
        
        # Find all pass actions
        pass_indices = goalie_subset[goalie_subset['action'].isin(['Accurate passes', 'Passes', 'Passes to the slot'])].index.tolist()
        print(f"Pass actions found: {len(pass_indices)}")
        
        if len(pass_indices) > 0:
            print(f"Pass action indices: {pass_indices}")
            print("Pass actions details:")
            for idx in pass_indices:
                print(f"  Index {idx}: {goalie_subset.iloc[idx]['action']} at time {goalie_subset.iloc[idx]['start']}")
        
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
        
        if len(pass_shot_sequences) > 0:
            print("\nDetailed pass-shot sequences:")
            for i, seq in enumerate(pass_shot_sequences):
                print(f"  Sequence {i+1}:")
                print(f"    Pass: {seq['pass_action']} at time {seq['pass_time']} (index {seq['pass_index']})")
                print(f"    Shot: {seq['shot_action']} at time {seq['shot_time']} (index {seq['shot_index']})")
                print(f"    Actions between: {seq['actions_between']}")
                
                # Show the actual sequence (with bounds checking)
                start_idx = max(0, seq['pass_index'] - 2)
                end_idx = min(len(goalie_subset), seq['shot_index'] + 2)
                print(f"    Full sequence:")
                for j in range(start_idx, end_idx + 1):
                    if j < len(goalie_subset):  # Bounds check
                        marker = ""
                        if j == seq['pass_index']:
                            marker = " <- PASS"
                        elif j == seq['shot_index']:
                            marker = " <- SHOT"
                        print(f"      {j}: {goalie_subset.iloc[j]['action']} (time: {goalie_subset.iloc[j]['start']}){marker}")
                print()
            
            # Calculate save percentage after passes
            saves_after_pass = len([seq for seq in pass_shot_sequences if seq['shot_action'] == 'Saves'])
            goals_after_pass = len([seq for seq in pass_shot_sequences if seq['shot_action'] == 'Goals against'])
            total_shots_after_pass = saves_after_pass + goals_after_pass
            
            if total_shots_after_pass > 0:
                save_pct_after_pass = (saves_after_pass / total_shots_after_pass) * 100
                print(f"Save percentage after passes: {save_pct_after_pass:.1f}% ({saves_after_pass}/{total_shots_after_pass})")
            else:
                print("No shots after passes found")
        else:
            print("No shots found within 5 actions after any pass")
        
        # Also check overall save percentage for comparison
        overall_saves = len(goalie_subset[goalie_subset['action'] == 'Saves'])
        overall_goals = len(goalie_subset[goalie_subset['action'] == 'Goals against'])
        overall_total = overall_saves + overall_goals
        
        if overall_total > 0:
            overall_save_pct = (overall_saves / overall_total) * 100
            print(f"Overall save percentage: {overall_save_pct:.1f}% ({overall_saves}/{overall_total})")
        
        print(f"\nAll actions for {goalie}:")
        action_counts = goalie_subset['action'].value_counts()
        for action, count in action_counts.items():
            print(f"  {action}: {count}")
    
    # Summary analysis
    print(f"\n{'='*80}")
    print("SUMMARY ANALYSIS")
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
    
    if total_pass_shot_sequences > 0:
        overall_save_pct_after_pass = (total_saves_after_pass / total_pass_shot_sequences) * 100
        print(f"\nOVERALL: {total_saves_after_pass} saves, {total_goals_after_pass} goals after passes")
        print(f"Overall save percentage after passes: {overall_save_pct_after_pass:.1f}%")
    else:
        print("\nNo shots after passes found across all goalies")

if __name__ == "__main__":
    analyze_pass_sequences()
