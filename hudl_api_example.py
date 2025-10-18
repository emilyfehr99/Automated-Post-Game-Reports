#!/usr/bin/env python3
"""
Hudl Instat Mini API Example
Demonstrates how to use the mini API with your authorized credentials
"""

import json
from hudl_instat_analyzer import HudlInstatMiniAPI

def main():
    """Example usage of the Hudl Instat Mini API"""
    print("🏒 Hudl Instat Mini API Example")
    print("=" * 50)
    
    # Initialize the API (you'll need to add your credentials to hudl_credentials.py)
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        api = HudlInstatMiniAPI(HUDL_USERNAME, HUDL_PASSWORD)
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
        return
    except Exception as e:
        print(f"❌ Error initializing API: {e}")
        return
    
    if not api.authenticated:
        print("❌ Authentication failed. Please check your credentials.")
        return
    
    print("✅ Successfully authenticated with Hudl Instat!")
    
    # Example: Get team information
    team_id = "21479"
    print(f"\n📊 Getting information for team {team_id}...")
    
    team_info = api.get_team_info(team_id)
    print(f"Team Info: {json.dumps(team_info, indent=2)}")
    
    # Example: Get team players
    print(f"\n👥 Getting players for team {team_id}...")
    players = api.get_team_players(team_id)
    print(f"Found {len(players)} players:")
    for i, player in enumerate(players[:5], 1):  # Show first 5 players
        print(f"  {i}. {player}")
    
    # Example: Get team games
    print(f"\n🏆 Getting games for team {team_id}...")
    games = api.get_team_games(team_id)
    print(f"Found {len(games)} games:")
    for i, game in enumerate(games[:3], 1):  # Show first 3 games
        print(f"  {i}. {game}")
    
    # Example: Analyze team structure (this works without authentication)
    print(f"\n🔍 Analyzing team structure for team {team_id}...")
    structure = api.analyze_team_structure(team_id)
    print(f"Structure analysis: {json.dumps(structure, indent=2)}")
    
    # Close the API
    api.close()
    print("\n✅ API session closed")

if __name__ == "__main__":
    main()
