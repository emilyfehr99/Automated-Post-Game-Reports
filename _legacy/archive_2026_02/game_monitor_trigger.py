#!/usr/bin/env python3
"""
NHL Game Monitor - Triggers GitHub Actions when games finish
Monitors NHL API for game status changes and triggers workflow instantly
"""

import os
import time
import requests
from datetime import datetime
import pytz

# Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = 'emilyfehr99/Automated-Post-Game-Reports'
CHECK_INTERVAL = 120  # Check every 2 minutes

# Track triggered games
triggered_games = set()

def get_todays_games():
    """Get all games from today in Central Time"""
    central_tz = pytz.timezone('US/Central')
    today = datetime.now(central_tz).strftime('%Y-%m-%d')
    
    url = f'https://api-web.nhle.com/v1/schedule/{today}'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        games = []
        if 'gameWeek' in data:
            for day in data['gameWeek']:
                if 'games' in day:
                    games.extend(day['games'])
        return games
    except Exception as e:
        print(f"⚠️  Error fetching schedule: {e}")
        return []

def trigger_workflow(game_id, away_team, home_team):
    """Trigger GitHub Actions workflow via repository_dispatch"""
    if not GITHUB_TOKEN:
        print("❌ ERROR: GITHUB_TOKEN environment variable not set!")
        return False
    
    url = f'https://api.github.com/repos/{GITHUB_REPO}/dispatches'
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {GITHUB_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'event_type': 'game-finished',
        'client_payload': {
            'game_id': game_id,
            'away_team': away_team,
            'home_team': home_team
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ Triggered workflow for {away_team} @ {home_team}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main monitoring loop"""
    print("🏒 NHL Game Monitor Started")
    print(f"📡 Checking every {CHECK_INTERVAL}s")
    print(f"🔗 Repo: {GITHUB_REPO}")
    print("-" * 60)
    
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN not set!")
        print("   Create at: https://github.com/settings/tokens")
        return
    
    while True:
        try:
            now = datetime.now(pytz.timezone('US/Central'))
            print(f"\n⏰ {now.strftime('%Y-%m-%d %I:%M %p CT')} - Checking...")
            
            games = get_todays_games()
            for game in games:
                game_id = str(game.get('id'))
                game_state = game.get('gameState', 'UNKNOWN')
                away = game.get('awayTeam', {}).get('abbrev', 'UNK')
                home = game.get('homeTeam', {}).get('abbrev', 'UNK')
                
                if game_state in ['FINAL', 'OFF'] and game_id not in triggered_games:
                    print(f"   🎯 GAME FINISHED: {away} @ {home}")
                    if trigger_workflow(game_id, away, home):
                        triggered_games.add(game_id)
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n🛑 Stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
