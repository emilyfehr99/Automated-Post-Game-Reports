#!/usr/bin/env python3
"""
Enhanced passing analysis using all available NHL data
"""

import requests
import json
from collections import defaultdict

def analyze_enhanced_passing():
    print("🏒 ENHANCED PASSING ANALYSIS")
    print("=" * 50)
    
    # Get play-by-play data
    url = 'https://api-web.nhle.com/v1/gamecenter/2024030416/play-by-play'
    response = requests.get(url)
    data = response.json()
    
    plays = data.get('plays', [])
    print(f"Total plays: {len(plays)}")
    
    # Analyze all events for passing-related data
    pass_events = []
    assist_events = []
    giveaway_events = []
    takeaway_events = []
    
    for i, play in enumerate(plays):
        event_type = play.get('typeDescKey', '').lower()
        details = play.get('details', {})
        
        # Look for any event that might involve passing
        if 'goal' in event_type and details.get('assistPlayerId'):
            assist_events.append({
                'play_index': i,
                'event_type': event_type,
                'assist_player_id': details.get('assistPlayerId'),
                'scoring_player_id': details.get('scoringPlayerId'),
                'time': play.get('timeInPeriod', '0:00'),
                'period': play.get('periodDescriptor', {}).get('number', 1),
                'x': details.get('xCoord', 0),
                'y': details.get('yCoord', 0),
                'team_id': details.get('eventOwnerTeamId'),
                'details': details
            })
        
        elif event_type == 'giveaway':
            giveaway_events.append({
                'play_index': i,
                'event_type': event_type,
                'player_id': details.get('playerId'),
                'time': play.get('timeInPeriod', '0:00'),
                'period': play.get('periodDescriptor', {}).get('number', 1),
                'x': details.get('xCoord', 0),
                'y': details.get('yCoord', 0),
                'team_id': details.get('eventOwnerTeamId'),
                'details': details
            })
        
        elif event_type == 'takeaway':
            takeaway_events.append({
                'play_index': i,
                'event_type': event_type,
                'player_id': details.get('playerId'),
                'time': play.get('timeInPeriod', '0:00'),
                'period': play.get('periodDescriptor', {}).get('number', 1),
                'x': details.get('xCoord', 0),
                'y': details.get('yCoord', 0),
                'team_id': details.get('eventOwnerTeamId'),
                'details': details
            })
    
    print(f"\n📊 PASSING-RELATED EVENTS FOUND:")
    print(f"  Assists: {len(assist_events)}")
    print(f"  Giveaways: {len(giveaway_events)}")
    print(f"  Takeaways: {len(takeaway_events)}")
    
    # Show sample events
    print(f"\n🔍 SAMPLE ASSIST EVENTS:")
    for event in assist_events[:3]:
        print(f"  Play {event['play_index']}: {event['event_type']} - Assist: {event['assist_player_id']}, Goal: {event['scoring_player_id']}")
        print(f"    Time: {event['time']} Period {event['period']}, Team: {event['team_id']}")
    
    print(f"\n🔍 SAMPLE GIVEAWAY EVENTS:")
    for event in giveaway_events[:3]:
        print(f"  Play {event['play_index']}: {event['event_type']} - Player: {event['player_id']}")
        print(f"    Time: {event['time']} Period {event['period']}, Team: {event['team_id']}")
    
    print(f"\n🔍 SAMPLE TAKEAWAY EVENTS:")
    for event in takeaway_events[:3]:
        print(f"  Play {event['play_index']}: {event['event_type']} - Player: {event['player_id']}")
        print(f"    Time: {event['time']} Period {event['period']}, Team: {event['team_id']}")
    
    # Look for shot events that might be related to passes
    shot_events = []
    for i, play in enumerate(plays):
        event_type = play.get('typeDescKey', '').lower()
        details = play.get('details', {})
        
        if 'shot' in event_type:
            shot_events.append({
                'play_index': i,
                'event_type': event_type,
                'player_id': details.get('shootingPlayerId'),
                'time': play.get('timeInPeriod', '0:00'),
                'period': play.get('periodDescriptor', {}).get('number', 1),
                'x': details.get('xCoord', 0),
                'y': details.get('yCoord', 0),
                'team_id': details.get('eventOwnerTeamId'),
                'is_goal': 'goal' in event_type,
                'details': details
            })
    
    print(f"\n📊 SHOT EVENTS FOUND: {len(shot_events)}")
    
    # Analyze dangerous passes using assists and giveaways/takeaways
    print(f"\n🎯 DANGEROUS PASS ANALYSIS:")
    
    # Combine all pass-like events
    all_pass_events = assist_events + giveaway_events + takeaway_events
    all_pass_events.sort(key=lambda x: (x['period'], x['time']))
    
    print(f"Total pass-like events: {len(all_pass_events)}")
    
    # Find dangerous passes (passes followed by shots within 10 seconds)
    dangerous_passes = []
    
    for pass_event in all_pass_events:
        pass_time_seconds = convert_time_to_seconds(pass_event['time'], pass_event['period'])
        
        # Find shots by the same team within 10 seconds
        team_shots = []
        for shot in shot_events:
            shot_time_seconds = convert_time_to_seconds(shot['time'], shot['period'])
            
            if (shot['team_id'] == pass_event['team_id'] and 
                shot_time_seconds > pass_time_seconds and 
                shot_time_seconds <= pass_time_seconds + 10):
                team_shots.append(shot)
        
        if len(team_shots) >= 1:  # At least 1 shot generated
            dangerous_passes.append({
                'pass_event': pass_event,
                'shots_generated': len(team_shots),
                'goals_scored': sum(1 for shot in team_shots if shot['is_goal']),
                'team_shots': team_shots
            })
    
    print(f"Dangerous passes found: {len(dangerous_passes)}")
    
    # Show most dangerous passes
    dangerous_passes.sort(key=lambda x: x['shots_generated'], reverse=True)
    
    print(f"\n🏆 TOP 3 MOST DANGEROUS PASSES:")
    for i, dangerous_pass in enumerate(dangerous_passes[:3]):
        pass_event = dangerous_pass['pass_event']
        print(f"  #{i+1}: {pass_event['event_type']} by Player {pass_event.get('assist_player_id', pass_event.get('player_id', 'Unknown'))}")
        print(f"    Time: {pass_event['time']} Period {pass_event['period']}")
        print(f"    Shots generated: {dangerous_pass['shots_generated']}")
        print(f"    Goals scored: {dangerous_pass['goals_scored']}")
        print()

def convert_time_to_seconds(time_str, period):
    """Convert time string (MM:SS) to total seconds in game"""
    try:
        if ':' in time_str:
            minutes, seconds = map(int, time_str.split(':'))
            period_seconds = (20 - minutes) * 60 - seconds  # Time remaining in period
        else:
            period_seconds = 0
        
        # Add previous periods (assuming 20-minute periods)
        total_seconds = (period - 1) * 20 * 60 + period_seconds
        return total_seconds
    except:
        return 0

if __name__ == "__main__":
    analyze_enhanced_passing()
