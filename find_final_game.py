#!/usr/bin/env python3
"""
Find the Final NHL Game of June 2024-2025 Season
Locates the last game played to get the correct game ID for analysis
"""

import requests
import json
from datetime import datetime

def main():
    print("🏒 FINDING FINAL NHL GAME OF JUNE 2024-2025 SEASON")
    print("=" * 60)
    
    # NHL API setup
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Get the 2024-2025 season schedule
    print("🔍 Fetching 2024-2025 NHL season schedule...")
    
    # Try different endpoints to get the season schedule
    endpoints = [
        "https://api-web.nhle.com/v1/schedule/2024-2025",
        "https://api-web.nhle.com/v1/schedule/2024",
        "https://api-web.nhle.com/v1/schedule/now"
    ]
    
    schedule_data = None
    working_endpoint = None
    
    for endpoint in endpoints:
        try:
            print(f"  Trying: {endpoint}")
            response = session.get(endpoint)
            if response.status_code == 200:
                schedule_data = response.json()
                working_endpoint = endpoint
                print(f"✅ Success with: {endpoint}")
                break
            else:
                print(f"  ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    if not schedule_data:
        print("❌ Could not retrieve season schedule from any endpoint")
        return
    
    print(f"\n📅 Analyzing schedule from: {working_endpoint}")
    
    # Look for games in June
    june_games = []
    
    if "gameWeek" in schedule_data:
        # Current week format
        for game in schedule_data["gameWeek"]:
            game_date = game.get("gameDate", "")
            if "2024-06" in game_date or "2025-06" in game_date:
                june_games.append(game)
    
    elif "dates" in schedule_data:
        # Full season format
        for date_data in schedule_data["dates"]:
            date = date_data.get("date", "")
            if "2024-06" in date or "2025-06" in date:
                for game in date_data.get("games", []):
                    june_games.append(game)
    
    elif "games" in schedule_data:
        # Direct games format
        for game in schedule_data["games"]:
            game_date = game.get("gameDate", "")
            if "2024-06" in game_date or "2025-06" in game_date:
                june_games.append(game)
    
    if not june_games:
        print("❌ No June games found in the schedule")
        print("\n🔍 Checking what dates are available...")
        
        # Show available dates to understand the data structure
        if "gameWeek" in schedule_data:
            for game in schedule_data["gameWeek"][:5]:
                print(f"  Available: {game.get('gameDate', 'Unknown')}")
        elif "dates" in schedule_data:
            for date_data in schedule_data["dates"][:5]:
                print(f"  Available: {date_data.get('date', 'Unknown')}")
        elif "games" in schedule_data:
            for game in schedule_data["games"][:5]:
                print(f"  Available: {game.get('gameDate', 'Unknown')}")
        
        return
    
    print(f"\n🎯 Found {len(june_games)} June games!")
    
    # Sort games by date to find the latest
    june_games.sort(key=lambda x: x.get("gameDate", ""), reverse=True)
    
    print("\n📅 June Games (sorted by date):")
    for i, game in enumerate(june_games[:10]):  # Show top 10
        game_date = game.get("gameDate", "Unknown")
        away_team = game.get("awayTeam", {}).get("abbrev", "Unknown")
        home_team = game.get("homeTeam", {}).get("abbrev", "Unknown")
        game_id = game.get("id", "Unknown")
        status = game.get("gameState", "Unknown")
        
        print(f"  {i+1}. {game_date}: {away_team} vs {home_team}")
        print(f"     Game ID: {game_id} | Status: {status}")
    
    # Get the final (latest) June game
    final_june_game = june_games[0]
    final_game_date = final_june_game.get("gameDate", "Unknown")
    final_away_team = final_june_game.get("awayTeam", {}).get("abbrev", "Unknown")
    final_home_team = final_june_game.get("homeTeam", {}).get("abbrev", "Unknown")
    final_game_id = final_june_game.get("id", "Unknown")
    
    print(f"\n🏆 FINAL JUNE GAME IDENTIFIED:")
    print(f"  📅 Date: {final_game_date}")
    print(f"  🏒 Teams: {final_away_team} vs {final_home_team}")
    print(f"  🆔 Game ID: {final_game_id}")
    
    # Now let's get detailed data for this game
    print(f"\n🔍 Fetching detailed data for game {final_game_id}...")
    
    game_center_url = f"https://api-web.nhle.com/v1/gamecenter/{final_game_id}/feed/live"
    game_response = session.get(game_center_url)
    
    if game_response.status_code == 200:
        print("✅ Successfully retrieved game data!")
        game_data = game_response.json()
        
        # Extract game info
        game_info = game_data.get("game", {})
        away_score = game_info.get("awayTeamScore", 0)
        home_score = game_info.get("homeTeamScore", 0)
        
        print(f"🏆 Final Score: {final_away_team} {away_score} - {final_home_team} {home_score}")
        
        # Count plays
        plays = game_data.get("plays", [])
        shots = [p for p in plays if p.get("typeDescKey") == "shot"]
        goals = [p for p in plays if p.get("typeDescKey") == "goal"]
        
        print(f"🎯 Total Shots: {len(shots)}")
        print(f"🏆 Total Goals: {len(goals)}")
        
        print(f"\n🎉 Ready to analyze game {final_game_id}!")
        print(f"   This is the final June game of the 2024-2025 season")
        print(f"   Use this Game ID for shot location analysis and expected goals")
        
        return final_game_id
        
    else:
        print(f"❌ Failed to get game data: {game_response.status_code}")
        return None

if __name__ == "__main__":
    main()
