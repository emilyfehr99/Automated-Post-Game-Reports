#!/usr/bin/env python3
"""
Test script for NHL API functionality
"""

from nhl_api_client import NHLAPIClient
import json

def test_nhl_api():
    """Test various NHL API endpoints"""
    print("🧪 Testing NHL API functionality...")
    
    nhl_client = NHLAPIClient()
    
    # Test 1: Get team info for Florida Panthers
    print("\n1. Testing team info retrieval...")
    try:
        team_info = nhl_client.get_team_info(13)  # FLA team ID
        if team_info:
            print(f"✅ Florida Panthers info retrieved: {team_info.get('name', 'Unknown')}")
        else:
            print("❌ Failed to get team info")
    except Exception as e:
        print(f"❌ Error getting team info: {e}")
    
    # Test 2: Get team roster
    print("\n2. Testing roster retrieval...")
    try:
        roster = nhl_client.get_team_roster(13)
        if roster:
            print(f"✅ Roster retrieved with {len(roster.get('forwards', []))} forwards")
        else:
            print("❌ Failed to get roster")
    except Exception as e:
        print(f"❌ Error getting roster: {e}")
    
    # Test 3: Get recent schedule
    print("\n3. Testing schedule retrieval...")
    try:
        schedule = nhl_client.get_game_schedule()
        if schedule:
            print(f"✅ Schedule retrieved for today")
            if 'gameWeek' in schedule:
                total_games = sum(len(day.get('games', [])) for day in schedule['gameWeek'])
                print(f"   Total games today: {total_games}")
        else:
            print("❌ Failed to get schedule")
    except Exception as e:
        print(f"❌ Error getting schedule: {e}")
    
    # Test 4: Find recent FLA vs EDM game
    print("\n4. Testing game search...")
    try:
        game_id = nhl_client.find_recent_game('FLA', 'EDM', days_back=365)
        if game_id:
            print(f"✅ Found recent FLA vs EDM game: {game_id}")
            
            # Test 5: Get game data
            print("\n5. Testing game data retrieval...")
            game_data = nhl_client.get_comprehensive_game_data(game_id)
            if game_data and game_data.get('game_center'):
                print(f"✅ Game data retrieved successfully")
                game_info = game_data['game_center']['game']
                away_team = game_data['game_center']['awayTeam']
                home_team = game_data['game_center']['homeTeam']
                print(f"   {away_team.get('abbrev', 'Unknown')} {game_info.get('awayTeamScore', 0)} - {home_team.get('abbrev', 'Unknown')} {game_info.get('homeTeamScore', 0)}")
                print(f"   Date: {game_info.get('gameDate', 'Unknown')}")
            else:
                print("❌ Failed to get game data")
        else:
            print("❌ No recent FLA vs EDM games found")
    except Exception as e:
        print(f"❌ Error searching for games: {e}")
    
    # Test 6: Test with different teams
    print("\n6. Testing with different team combinations...")
    test_combinations = [
        ('BOS', 'TOR'),  # Boston vs Toronto
        ('NYR', 'NYI'),  # Rangers vs Islanders
        ('CHI', 'DET'),  # Chicago vs Detroit
    ]
    
    for team1, team2 in test_combinations:
        try:
            game_id = nhl_client.find_recent_game(team1, team2, days_back=60)
            if game_id:
                print(f"✅ Found recent {team1} vs {team2} game: {game_id}")
            else:
                print(f"❌ No recent {team1} vs {team2} games found")
        except Exception as e:
            print(f"❌ Error searching for {team1} vs {team2}: {e}")

if __name__ == "__main__":
    test_nhl_api()
