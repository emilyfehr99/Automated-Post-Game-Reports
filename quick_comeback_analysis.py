#!/usr/bin/env python3
"""Quick historical comeback analysis for live games"""

from advanced_live_predictions import AdvancedLivePredictor
from nhl_api_client import NHLAPIClient
from datetime import datetime, timedelta
from collections import defaultdict
import pytz

def parse_time_remaining(time_str):
    """Parse MM:SS time string to total seconds"""
    try:
        parts = time_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return 0

def find_comeback_record_fast(api, deficit, period, time_remaining_sec, days_back=30):
    """Quickly find historical comeback record"""
    ct_tz = pytz.timezone('US/Central')
    today = datetime.now(ct_tz)
    
    wins = 0
    total = 0
    
    # Sample games more efficiently - check every other day
    for day_offset in range(0, days_back, 2):
        date = (today - timedelta(days=day_offset)).strftime('%Y-%m-%d')
        try:
            schedule = api.get_game_schedule(date)
            if not schedule or 'gameWeek' not in schedule:
                continue
                
            for day in schedule['gameWeek']:
                if 'games' not in day:
                    continue
                    
                for game in day['games']:
                    if game.get('gameState') != 'OFF':
                        continue
                    
                    game_id = game.get('id')
                    if not game_id:
                        continue
                    
                    try:
                        # Just get boxscore for final score
                        boxscore = api.get_game_boxscore(game_id)
                        if not boxscore:
                            continue
                        
                        away_team = boxscore.get('awayTeam', {})
                        home_team = boxscore.get('homeTeam', {})
                        final_away = away_team.get('score', 0)
                        final_home = home_team.get('score', 0)
                        
                        # Get play-by-play but only sample key plays
                        pbp = api.get_play_by_play(game_id)
                        if not pbp or 'plays' not in pbp:
                            continue
                        
                        # Sample every 10th play in the target period
                        plays = [p for p in pbp['plays'] if p.get('periodDescriptor', {}).get('number') == period]
                        
                        for play in plays[::10]:  # Sample every 10th play
                            clock = play.get('timeInPeriod', '')
                            if ':' not in clock:
                                continue
                            
                            try:
                                parts = clock.split(':')
                                play_time_sec = int(parts[0]) * 60 + int(parts[1])
                                time_remaining = (20 * 60) - play_time_sec
                            except:
                                continue
                            
                            # Check if time matches (±1 minute for speed)
                            if abs(time_remaining - time_remaining_sec) > 60:
                                continue
                            
                            away_score = play.get('details', {}).get('awayScore', 0)
                            home_score = play.get('details', {}).get('homeScore', 0)
                            
                            score_diff = abs(away_score - home_score)
                            if score_diff == deficit:
                                total += 1
                                trailing_team_won = (away_score < home_score and final_away > final_home) or \
                                                  (home_score < away_score and final_home > final_away)
                                if trailing_team_won:
                                    wins += 1
                                
                                # Only count once per game
                                break
                                
                    except:
                        continue
                        
        except:
            continue
    
    return wins, total

# Get live games
predictor = AdvancedLivePredictor()
api = NHLAPIClient()
games = predictor.get_live_games()

print(f"🏒 HISTORICAL COMEBACK RECORDS\n{'='*60}\n")

for game in games:
    game_id = game.get('id')
    home_name = game.get('homeTeam', {}).get('name', {}).get('default', 'HOME')
    away_name = game.get('awayTeam', {}).get('name', {}).get('default', 'AWAY')
    
    metrics = predictor.get_advanced_live_metrics(game_id)
    if not metrics:
        continue
    
    away_score = metrics.get('away_score', 0)
    home_score = metrics.get('home_score', 0)
    period = metrics.get('current_period', 1)
    time_str = metrics.get('time_remaining', '20:00')
    time_remaining_sec = parse_time_remaining(time_str)
    
    if away_score < home_score:
        trailing_team = metrics.get('away_team', '')
        deficit = home_score - away_score
        team_name = away_name
    elif home_score < away_score:
        trailing_team = metrics.get('home_team', '')
        deficit = away_score - home_score
        team_name = home_name
    else:
        continue
    
    print(f"📊 {away_name} @ {home_name}")
    print(f"   Score: {away_name} {away_score} - {home_score} {home_name}")
    print(f"   Period {period}, {time_str} remaining")
    print(f"   {team_name} down by {deficit} goal{'s' if deficit > 1 else ''}")
    
    wins, total = find_comeback_record_fast(api, deficit, period, time_remaining_sec, days_back=30)
    
    if total > 0:
        win_pct = (wins / total) * 100
        print(f"   📈 Historical: {wins}-{total - wins} ({win_pct:.1f}% win rate)")
    else:
        print(f"   ❌ No data found")
    
    print()

