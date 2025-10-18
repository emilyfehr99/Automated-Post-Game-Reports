#!/usr/bin/env python3
"""
Find the Final NHL Game of June 2024-2025 Season
Locates the last game played to get the correct game ID for analysis
"""

import requests
import json

def main():
    print("🏒 FINDING FINAL NHL GAME OF JUNE 2024-2025 SEASON")
    print("=" * 60)
    
    # NHL API setup
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Try to get the current schedule
    print("🔍 Fetching current NHL schedule...")
    
    url = "https://api-web.nhle.com/v1/schedule/now"
    response = session.get(url)
    
    if response.status_code == 200:
        print("✅ Successfully retrieved current schedule")
        data = response.json()
        
        if "gameWeek" in data:
            print(f"📅 Found {len(data['gameWeek'])} games this week")
            print("\n🎯 Available Games:")
            
            for i, game in enumerate(data["gameWeek"][:10]):  # Show top 10
                date = game.get("gameDate", "Unknown")
                away = game.get("awayTeam", {}).get("abbrev", "Unknown")
                home = game.get("homeTeam", {}).get("abbrev", "Unknown")
                game_id = game.get("id", "Unknown")
                status = game.get("gameState", "Unknown")
                
                print(f"  {i+1}. {date}: {away} vs {home}")
                print(f"     Game ID: {game_id} | Status: {status}")
            
            # Look for June games specifically
            print("\n🔍 Looking for June games...")
            june_games = []
            
            for game in data["gameWeek"]:
                date = game.get("gameDate", "")
                if "2024-06" in date or "2025-06" in date:
                    june_games.append(game)
            
            if june_games:
                print(f"🎯 Found {len(june_games)} June games!")
                
                # Sort by date to find the latest
                june_games.sort(key=lambda x: x.get("gameDate", ""), reverse=True)
                
                final_june_game = june_games[0]
                final_date = final_june_game.get("gameDate", "Unknown")
                final_away = final_june_game.get("awayTeam", {}).get("abbrev", "Unknown")
                final_home = final_june_game.get("homeTeam", {}).get("abbrev", "Unknown")
                final_game_id = final_june_game.get("id", "Unknown")
                
                print(f"\n🏆 FINAL JUNE GAME IDENTIFIED:")
                print(f"  📅 Date: {final_date}")
                print(f"  🏒 Teams: {final_away} vs {final_home}")
                print(f"  🆔 Game ID: {final_game_id}")
                
                # Get detailed data for this game
                print(f"\n🔍 Fetching detailed data for game {final_game_id}...")
                
                game_url = f"https://api-web.nhle.com/v1/gamecenter/{final_game_id}/feed/live"
                game_response = session.get(game_url)
                
                if game_response.status_code == 200:
                    print("✅ Successfully retrieved game data!")
                    game_data = game_response.json()
                    
                    # Extract game info
                    game_info = game_data.get("game", {})
                    away_score = game_info.get("awayTeamScore", 0)
                    home_score = game_info.get("homeTeamScore", 0)
                    
                    print(f"🏆 Final Score: {final_away} {away_score} - {final_home} {home_score}")
                    
                    # Count plays
                    plays = game_data.get("plays", [])
                    shots = [p for p in plays if p.get("typeDescKey") == "shot"]
                    goals = [p for p in plays if p.get("typeDescKey") == "goal"]
                    
                    print(f"🎯 Total Shots: {len(shots)}")
                    print(f"🏆 Total Goals: {len(goals)}")
                    
                    print(f"\n🎉 Ready to analyze game {final_game_id}!")
                    print(f"   This appears to be the final June game available")
                    print(f"   Use this Game ID for shot location analysis and expected goals")
                    
                    return final_game_id
                    
                else:
                    print(f"❌ Failed to get game data: {game_response.status_code}")
                    return None
            else:
                print("❌ No June games found in current schedule")
                print("📅 Available dates:")
                for game in data["gameWeek"][:5]:
                    print(f"  {game.get('gameDate', 'Unknown')}")
                return None
        else:
            print("❌ No gameWeek data found in schedule")
            return None
    else:
        print(f"❌ Failed to get schedule: {response.status_code}")
        return None

if __name__ == "__main__":
    main()
