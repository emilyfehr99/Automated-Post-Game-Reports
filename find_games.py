#!/usr/bin/env python3
import requests
import json

print("🔍 Finding recent NHL games...")

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

url = "https://api-web.nhle.com/v1/schedule/now"
response = session.get(url)

if response.status_code == 200:
    print("✅ Successfully retrieved schedule")
    data = response.json()
    
    print("\n📅 Recent NHL Games:")
    for game in data.get("gameWeek", [])[:5]:
        print(f"  {game['gameDate']}: {game['awayTeam']['abbrev']} vs {game['homeTeam']['abbrev']} (ID: {game['id']})")
        
    # Get the first game ID for analysis
    if data.get("gameWeek"):
        first_game = data["gameWeek"][0]
        game_id = first_game["id"]
        print(f"\n🎯 Using game ID: {game_id} for analysis")
        
        # Now analyze this game
        print(f"\n🏒 Analyzing game: {first_game['awayTeam']['abbrev']} vs {first_game['homeTeam']['abbrev']}")
        
        # Get game data
        game_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/feed/live"
        game_response = session.get(game_url)
        
        if game_response.status_code == 200:
            print("✅ Successfully retrieved game data")
            game_data = game_response.json()
            
            # Extract basic info
            game_info = game_data["game"]
            away_team = game_data["awayTeam"]["abbrev"]
            home_team = game_data["homeTeam"]["abbrev"]
            
            print(f"🏆 Final Score: {game_info.get('awayTeamScore', 0)} - {game_info.get('homeTeamScore', 0)}")
            
            # Count shots and goals
            plays = game_data.get("plays", [])
            shots = [p for p in plays if p.get("typeDescKey") == "shot"]
            goals = [p for p in plays if p.get("typeDescKey") == "goal"]
            
            print(f"🎯 Total Shots: {len(shots)}")
            print(f"🏆 Total Goals: {len(goals)}")
            
            print(f"\n🎉 Ready to create visualizations for Safari!")
            
        else:
            print(f"❌ Failed to get game data: {game_response.status_code}")
            
else:
    print(f"❌ Failed to get schedule: {response.status_code}")
