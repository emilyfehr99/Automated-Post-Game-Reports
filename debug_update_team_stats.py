#!/usr/bin/env python3
"""
Debug the update_team_stats method to find why all teams are getting the same data
"""

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

def debug_update_team_stats():
    print('🔍 DEBUGGING UPDATE_TEAM_STATS METHOD')
    print('=' * 45)
    
    model = ImprovedSelfLearningModelV2()
    
    # Clear team stats
    model.team_stats = {}
    
    # Create a test prediction
    test_prediction = {
        "away_team": "TBL",
        "home_team": "DET", 
        "date": "2025-01-01",
        "actual_away_score": 3,
        "actual_home_score": 2,
        "metrics_used": {
            "away_xg": 3.39,
            "home_xg": 2.77,
            "away_hdc": 12,
            "home_hdc": 7,
            "away_shots": 32,
            "home_shots": 31,
            "away_corsi_pct": 54.6,
            "home_corsi_pct": 45.4,
            "away_power_play_pct": 0.0,
            "home_power_play_pct": 33.3,
            "away_faceoff_pct": 45.8,
            "home_faceoff_pct": 54.2,
            "away_hits": 20,
            "home_hits": 27,
            "away_blocked_shots": 23,
            "home_blocked_shots": 13,
            "away_giveaways": 15,
            "home_giveaways": 16,
            "away_takeaways": 4,
            "home_takeaways": 4,
            "away_penalty_minutes": 6,
            "home_penalty_minutes": 6
        }
    }
    
    print('Before update_team_stats:')
    print(f'  TBL in team_stats: {"TBL" in model.team_stats}')
    print(f'  DET in team_stats: {"DET" in model.team_stats}')
    
    # Call update_team_stats
    model.update_team_stats(test_prediction)
    
    print('\\nAfter update_team_stats:')
    print(f'  TBL in team_stats: {"TBL" in model.team_stats}')
    print(f'  DET in team_stats: {"DET" in model.team_stats}')
    
    if "TBL" in model.team_stats:
        tbl_away_xg = model.team_stats["TBL"]["away"]["xg"]
        tbl_home_xg = model.team_stats["TBL"]["home"]["xg"]
        print(f'\\nTBL:')
        print(f'  Away xG: {tbl_away_xg}')
        print(f'  Home xG: {tbl_home_xg}')
        
        if tbl_away_xg == tbl_home_xg:
            print(f'  ❌ TBL away and home are identical!')
        else:
            print(f'  ✅ TBL away and home are different')
    
    if "DET" in model.team_stats:
        det_away_xg = model.team_stats["DET"]["away"]["xg"]
        det_home_xg = model.team_stats["DET"]["home"]["xg"]
        print(f'\\nDET:')
        print(f'  Away xG: {det_away_xg}')
        print(f'  Home xG: {det_home_xg}')
        
        if det_away_xg == det_home_xg:
            print(f'  ❌ DET away and home are identical!')
        else:
            print(f'  ✅ DET away and home are different')
    
    # Check if TBL away and DET home have the right values
    if "TBL" in model.team_stats and "DET" in model.team_stats:
        tbl_away_xg = model.team_stats["TBL"]["away"]["xg"]
        det_home_xg = model.team_stats["DET"]["home"]["xg"]
        
        print(f'\\nCross-check:')
        print(f'  TBL away xG: {tbl_away_xg}')
        print(f'  DET home xG: {det_home_xg}')
        print(f'  Expected TBL away: [3.39]')
        print(f'  Expected DET home: [2.77]')
        
        if tbl_away_xg == [3.39] and det_home_xg == [2.77]:
            print(f'  ✅ Values are correct!')
        else:
            print(f'  ❌ Values are wrong!')
            
        if tbl_away_xg == det_home_xg:
            print(f'  ❌ TBL away and DET home are identical!')
        else:
            print(f'  ✅ TBL away and DET home are different')

if __name__ == "__main__":
    debug_update_team_stats()
