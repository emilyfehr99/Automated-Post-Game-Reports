#!/usr/bin/env python3
"""
Quick test script to generate a single report with win probability
"""

from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator
import sys

def generate_test_report(game_id):
    """Generate a report for testing"""
    print(f"🏒 Testing report generation for game {game_id}...")
    
    # Initialize clients
    client = NHLAPIClient()
    generator = PostGameReportGenerator()
    
    # Fetch game data
    print("📊 Fetching game data...")
    game_center = client.get_game_center(game_id)
    boxscore = client.get_game_boxscore(game_id)
    pbp = client.get_play_by_play(game_id)
    
    if not boxscore or not pbp:
        print("❌ Could not fetch game data")
        return False
    
    # Get team info
    away_team = boxscore['awayTeam']['abbrev']
    home_team = boxscore['homeTeam']['abbrev']
    
    print(f"🎮 Game: {away_team} @ {home_team}")
    
    # Generate report
    print("📄 Generating PDF...")
    pdf_path = f"/Users/emilyfehr8/Desktop/test_report_{away_team}_vs_{home_team}.pdf"
    
    game_data = {
        'game_center': game_center,
        'boxscore': boxscore,
        'play_by_play': pbp
    }
    
    generator.generate_report(game_data, pdf_path, game_id)
    
    print(f"✅ Report saved to: {pdf_path}")
    return True

if __name__ == "__main__":
    # Test with yesterday's TBL @ DET game
    # Game ID format: 2025020XXX
    game_id = "2025020073"  # TBL @ DET from Oct 17
    
    if len(sys.argv) > 1:
        game_id = sys.argv[1]
    
    success = generate_test_report(game_id)
    
    if success:
        print("🎉 Test complete!")
    else:
        print("❌ Test failed")
        sys.exit(1)

