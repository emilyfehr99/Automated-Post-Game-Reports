#!/usr/bin/env python3
"""
Comprehensive Metrics Analysis - Discover ALL possible metrics from NHL API
"""

import requests
import json
from collections import defaultdict

def analyze_all_possible_metrics(game_id):
    """Analyze all possible metrics we can extract from NHL API data"""
    print(f"🔍 COMPREHENSIVE METRICS ANALYSIS FOR GAME {game_id}")
    print("=" * 80)
    
    play_by_play_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    
    try:
        response = requests.get(play_by_play_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Data fetched successfully")
            
            # Analyze all possible data sources
            print("\n📊 DATA SOURCES AVAILABLE:")
            print(f"Top-level keys: {list(data.keys())}")
            
            # 1. Game-level metrics
            print("\n🏒 GAME-LEVEL METRICS:")
            game_info = data.get('game', {})
            print(f"Game info keys: {list(game_info.keys())}")
            
            away_team = data.get('awayTeam', {})
            home_team = data.get('homeTeam', {})
            print(f"Away team keys: {list(away_team.keys())}")
            print(f"Home team keys: {list(home_team.keys())}")
            
            # 2. Roster analysis
            print("\n👥 ROSTER METRICS:")
            if 'rosterSpots' in data:
                roster_spots = data['rosterSpots']
                print(f"Roster spots: {len(roster_spots)}")
                
                # Analyze roster structure
                sample_spot = roster_spots[0]
                print(f"Roster spot keys: {list(sample_spot.keys())}")
                
                # Position analysis
                positions = defaultdict(int)
                teams = defaultdict(int)
                for spot in roster_spots:
                    pos = spot.get('positionCode', 'Unknown')
                    team = spot.get('teamId', 'Unknown')
                    positions[pos] += 1
                    teams[team] += 1
                
                print(f"Positions: {dict(positions)}")
                print(f"Teams: {dict(teams)}")
            
            # 3. Play-by-play analysis
            print("\n🎯 PLAY-BY-PLAY METRICS:")
            plays = data.get('plays', [])
            print(f"Total plays: {len(plays)}")
            
            # Analyze all play types
            play_types = defaultdict(int)
            play_details_keys = set()
            
            for play in plays:
                play_type = play.get('typeDescKey', 'unknown')
                play_types[play_type] += 1
                
                if 'details' in play:
                    details = play['details']
                    play_details_keys.update(details.keys())
            
            print(f"Play types found: {dict(play_types)}")
            print(f"All detail keys across plays: {sorted(play_details_keys)}")
            
            # 4. Detailed play analysis
            print("\n🔍 DETAILED PLAY METRICS:")
            
            # Analyze specific play types for unique metrics
            interesting_plays = ['goal', 'shot-on-goal', 'missed-shot', 'blocked-shot', 
                               'hit', 'faceoff', 'penalty', 'giveaway', 'takeaway']
            
            for play_type in interesting_plays:
                if play_type in play_types:
                    # Find a sample play of this type
                    sample_play = None
                    for play in plays:
                        if play.get('typeDescKey') == play_type:
                            sample_play = play
                            break
                    
                    if sample_play and 'details' in sample_play:
                        details = sample_play['details']
                        print(f"\n{play_type.upper()} metrics:")
                        for key, value in details.items():
                            print(f"  {key}: {value}")
            
            # 5. Time-based metrics
            print("\n⏰ TIME-BASED METRICS:")
            periods = defaultdict(list)
            for play in plays:
                period = play.get('periodDescriptor', {}).get('number', 1)
                time_remaining = play.get('timeRemaining', '20:00')
                periods[period].append(time_remaining)
            
            print(f"Periods: {list(periods.keys())}")
            print(f"Time samples: {dict(list(periods.items())[:3])}")  # First 3 periods
            
            # 6. Situation codes
            print("\n🎮 SITUATION METRICS:")
            situation_codes = defaultdict(int)
            for play in plays:
                situation = play.get('situationCode', '')
                if situation:
                    situation_codes[situation] += 1
            
            print(f"Situation codes: {dict(situation_codes)}")
            
            # 7. Zone analysis
            print("\n🏟️ ZONE METRICS:")
            zones = defaultdict(int)
            for play in plays:
                if 'details' in play:
                    zone = play['details'].get('zoneCode', '')
                    if zone:
                        zones[zone] += 1
            
            print(f"Zone codes: {dict(zones)}")
            
            # 8. Advanced metrics we can calculate
            print("\n📈 ADVANCED METRICS WE CAN CALCULATE:")
            advanced_metrics = [
                "Corsi (Shot Attempts)",
                "Fenwick (Unblocked Shot Attempts)", 
                "PDO (Save % + Shooting %)",
                "Zone Starts/Finishes",
                "Quality of Competition",
                "Quality of Teammates",
                "Expected Goals (xG) - Already implemented",
                "Expected Assists (xA)",
                "High-Danger Chances",
                "Rush Chances",
                "Rebound Chances",
                "Slot Shots",
                "Point Shots",
                "Power Play Efficiency",
                "Penalty Kill Efficiency",
                "Faceoff Win % by Zone",
                "Hit Effectiveness",
                "Giveaway/Takeaway Ratio",
                "Time on Ice (estimated)",
                "Shift Length Analysis",
                "Momentum Shifts",
                "Scoring Chances",
                "Shot Quality",
                "Passing Networks",
                "Defensive Zone Coverage",
                "Neutral Zone Play",
                "Offensive Zone Time",
                "Breakout Efficiency",
                "Forechecking Pressure",
                "Goalie Performance Metrics"
            ]
            
            for i, metric in enumerate(advanced_metrics, 1):
                print(f"  {i:2d}. {metric}")
            
            # 9. What we're currently missing
            print("\n❌ METRICS WE'RE CURRENTLY MISSING:")
            missing_metrics = [
                "Time on Ice (TOI) - Need to estimate from play frequency",
                "Shift Analysis - Need to track player entries/exits",
                "Quality of Competition - Need opponent analysis",
                "Quality of Teammates - Need linemate analysis", 
                "Zone Starts/Finishes - Need to track zone entries",
                "Expected Assists (xA) - Need passing data",
                "High-Danger Chances - Need shot location analysis",
                "Rush Chances - Need to identify rush plays",
                "Rebound Chances - Need to track shot sequences",
                "Slot Shots - Need precise location analysis",
                "Point Shots - Need defenseman shot analysis",
                "Power Play Efficiency - Need situation analysis",
                "Penalty Kill Efficiency - Need situation analysis",
                "Faceoff Win % by Zone - Need zone-specific analysis",
                "Hit Effectiveness - Need to correlate hits with outcomes",
                "Giveaway/Takeaway Ratio - Need turnover analysis",
                "Momentum Shifts - Need to track game flow",
                "Scoring Chances - Need to define and track",
                "Shot Quality - Need advanced xG model",
                "Passing Networks - Need assist chain analysis",
                "Defensive Zone Coverage - Need defensive metrics",
                "Neutral Zone Play - Need zone transition analysis",
                "Offensive Zone Time - Need possession tracking",
                "Breakout Efficiency - Need defensive zone analysis",
                "Forechecking Pressure - Need offensive pressure metrics",
                "Goalie Performance Metrics - Need save analysis"
            ]
            
            for i, metric in enumerate(missing_metrics, 1):
                print(f"  {i:2d}. {metric}")
            
            return data
        else:
            print(f"❌ API returned {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    game_id = "2024030242"
    analyze_all_possible_metrics(game_id)
