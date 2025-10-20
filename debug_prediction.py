#!/usr/bin/env python3
"""
Debug script to investigate WPG @ CGY prediction issue
"""

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
import json

def debug_prediction():
    print('🔍 DEBUGGING WPG @ CGY PREDICTION')
    print('=' * 50)
    
    # Initialize model
    model = ImprovedSelfLearningModelV2()
    
    # Get team performance data
    print('\n📊 TEAM PERFORMANCE DATA:')
    wpg_perf = model.get_team_performance('WPG', is_home=False)
    cgy_perf = model.get_team_performance('CGY', is_home=True)
    
    print(f'\nWPG (Away) Performance:')
    for key, value in wpg_perf.items():
        if isinstance(value, float):
            print(f'  {key}: {value:.3f}')
        else:
            print(f'  {key}: {value}')
    
    print(f'\nCGY (Home) Performance:')
    for key, value in cgy_perf.items():
        if isinstance(value, float):
            print(f'  {key}: {value:.3f}')
        else:
            print(f'  {key}: {value}')
    
    # Test individual prediction methods
    print('\n🎯 INDIVIDUAL PREDICTION METHODS:')
    
    # Traditional method
    traditional = model.predict_game('WPG', 'CGY')
    print(f'\nTraditional Method:')
    print(f'  WPG: {traditional["away_prob"]:.1f}%')
    print(f'  CGY: {traditional["home_prob"]:.1f}%')
    print(f'  Confidence: {traditional["prediction_confidence"]:.1f}%')
    
    # Form-based method
    form_based = model._form_based_predict('WPG', 'CGY')
    print(f'\nForm-based Method:')
    print(f'  WPG: {form_based["away_prob"]:.1f}%')
    print(f'  CGY: {form_based["home_prob"]:.1f}%')
    print(f'  Confidence: {form_based["prediction_confidence"]:.1f}%')
    
    # Momentum method
    momentum = model._momentum_based_predict('WPG', 'CGY')
    print(f'\nMomentum Method:')
    print(f'  WPG: {momentum["away_prob"]:.1f}%')
    print(f'  CGY: {momentum["home_prob"]:.1f}%')
    print(f'  Confidence: {momentum["prediction_confidence"]:.1f}%')
    
    # Ensemble method
    ensemble = model.ensemble_predict('WPG', 'CGY')
    print(f'\nEnsemble Method:')
    print(f'  WPG: {ensemble["away_prob"]:.1f}%')
    print(f'  CGY: {ensemble["home_prob"]:.1f}%')
    print(f'  Confidence: {ensemble["prediction_confidence"]:.1f}%')
    print(f'  Weights: {ensemble["ensemble_weights"]}')
    
    # Check model weights
    print('\n⚖️ MODEL WEIGHTS:')
    weights = model.get_current_weights()
    for key, value in weights.items():
        if value > 0:
            print(f'  {key}: {value:.3f}')
    
    # Check team stats data
    print('\n📈 TEAM STATS DATA:')
    if 'WPG' in model.team_stats:
        wpg_data = model.team_stats['WPG']
        print(f'\nWPG Team Stats:')
        for venue in ['home', 'away']:
            if venue in wpg_data:
                venue_data = wpg_data[venue]
                print(f'  {venue}:')
                print(f'    games: {len(venue_data.get("games", []))}')
                print(f'    goals: {venue_data.get("goals", [])}')
                print(f'    xg: {venue_data.get("xg", [])}')
                print(f'    hdc: {venue_data.get("hdc", [])}')
    
    if 'CGY' in model.team_stats:
        cgy_data = model.team_stats['CGY']
        print(f'\nCGY Team Stats:')
        for venue in ['home', 'away']:
            if venue in cgy_data:
                venue_data = cgy_data[venue]
                print(f'  {venue}:')
                print(f'    games: {len(venue_data.get("games", []))}')
                print(f'    goals: {venue_data.get("goals", [])}')
                print(f'    xg: {venue_data.get("xg", [])}')
                print(f'    hdc: {venue_data.get("hdc", [])}')

if __name__ == "__main__":
    debug_prediction()
