#!/usr/bin/env python3
"""
Test Bobcats API
Test the Hudl API specifically for the Bobcats team (ID: 21479)
"""

import json
import time
from hudl_bobcats_manager import HudlBobcatsManager
from hudl_identifier_helper import HudlIdentifierHelper

def test_bobcats_api():
    """Test the Bobcats API functionality"""
    print("🏒 Testing Bobcats API (Team ID: 21479)")
    print("=" * 60)
    
    # Initialize the Bobcats manager
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        bobcats = HudlBobcatsManager(HUDL_USERNAME, HUDL_PASSWORD)
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
        return
    
    # Initialize identifier helper
    helper = HudlIdentifierHelper()
    
    print(f"✅ Bobcats Manager initialized")
    print(f"   Team ID: 21479")
    print(f"   Team Name: Bobcats")
    
    # Test 1: Get team information
    print(f"\n📊 Test 1: Getting team information...")
    team_info = bobcats.get_team_info("emily")
    print(f"   Result: {json.dumps(team_info, indent=2)}")
    
    # Test 2: Get roster with Hudl identifiers
    print(f"\n👥 Test 2: Getting roster with Hudl identifiers...")
    roster = bobcats.get_team_roster("emily")
    print(f"   Players found: {len(roster.get('players', []))}")
    
    if roster.get('players'):
        print(f"   First few players:")
        for i, player in enumerate(roster['players'][:3], 1):
            print(f"     {i}. {player['name']} (ID: {player.get('hudl_player_id', 'N/A')})")
    
    # Test 3: Get games with Hudl identifiers
    print(f"\n🏆 Test 3: Getting games with Hudl identifiers...")
    games = bobcats.get_team_games("emily")
    print(f"   Games found: {len(games.get('games', []))}")
    
    if games.get('games'):
        print(f"   First few games:")
        for i, game in enumerate(games['games'][:3], 1):
            print(f"     {i}. {game['date']} vs {game['opponent']} (ID: {game.get('hudl_game_id', 'N/A')})")
    
    # Test 4: Build identifier mapping
    print(f"\n🆔 Test 4: Building identifier mapping...")
    all_data = {
        'team_info': team_info,
        'roster': roster,
        'games': games
    }
    
    # Combine all data for identifier extraction
    combined_data = {
        'team_id': team_info.get('team_id', '21479'),
        'team_name': team_info.get('team_name', 'Bobcats'),
        'players': roster.get('players', []),
        'games': games.get('games', [])
    }
    
    mapping = helper.build_identifier_mapping(combined_data)
    print(f"   Identifier mapping created:")
    print(f"     - Team: {mapping['summary']['by_type'].get('team', 0)}")
    print(f"     - Players: {mapping['summary']['by_type'].get('players', 0)}")
    print(f"     - Games: {mapping['summary']['by_type'].get('games', 0)}")
    print(f"     - Total: {mapping['summary']['total_identifiers']}")
    
    # Test 5: Generate identifier report
    print(f"\n📋 Test 5: Generating identifier report...")
    report = helper.generate_identifier_report(combined_data)
    print(report)
    
    # Test 6: Export data
    print(f"\n💾 Test 6: Exporting team data...")
    export_file = bobcats.export_team_data("emily")
    print(f"   Data exported to: {export_file}")
    
    # Test 7: Session status
    print(f"\n📊 Test 7: Session status...")
    status = bobcats.get_session_status()
    print(f"   Active sessions: {status['total_active']}")
    print(f"   Max concurrent: {status['max_concurrent']}")
    
    # Clean up
    print(f"\n🧹 Cleaning up...")
    bobcats.close_all_sessions()
    print(f"✅ All sessions closed")
    
    print(f"\n🎉 Bobcats API test completed!")
    print(f"   Team ID 21479 is ready for use with your Hudl credentials")

def main():
    """Main test function"""
    print("🏒 Hudl Bobcats API Test Suite")
    print("=" * 60)
    print("This will test the API with your Bobcats team (ID: 21479)")
    print("Make sure you've updated hudl_credentials.py with your actual credentials")
    print()
    
    # Check if credentials are set
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        if HUDL_USERNAME == "your_username_here":
            print("❌ Please update hudl_credentials.py with your actual Hudl credentials")
            return
    except ImportError:
        print("❌ hudl_credentials.py not found")
        return
    
    # Run the test
    test_bobcats_api()

if __name__ == "__main__":
    main()
