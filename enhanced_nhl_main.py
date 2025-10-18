#!/usr/bin/env python3
"""
Enhanced NHL Report Generator - Main Application
Complete application with all advanced features from 2025 NHL API
"""

import os
import sys
from datetime import datetime, timedelta
from enhanced_nhl_api_client import EnhancedNHLAPIClient
from enhanced_nhl_report_generator import EnhancedNHLReportGenerator
from nhl_advanced_analytics import NHLAdvancedAnalytics

def main():
    """Main function for the Enhanced NHL Report Generator"""
    print("🏒 ENHANCED NHL POST-GAME REPORT GENERATOR - 2025 EDITION 🏒")
    print("=" * 70)
    print("✨ Features:")
    print("  • Real-time NHL API integration (2025 endpoints)")
    print("  • Advanced player analytics with game logs")
    print("  • Play-by-play analysis with shot locations")
    print("  • Real-time standings and historical context")
    print("  • Advanced visualizations and interactive charts")
    print("  • Comprehensive goalie performance analysis")
    print("  • Momentum tracking and game flow analysis")
    print("=" * 70)
    
    # Initialize components
    print("\n🔧 Initializing Enhanced NHL API Client...")
    api_client = EnhancedNHLAPIClient()
    
    print("📊 Initializing Advanced Analytics Engine...")
    analytics = NHLAdvancedAnalytics()
    
    print("📝 Initializing Enhanced Report Generator...")
    report_generator = EnhancedNHLReportGenerator()
    
    print("✅ All components initialized successfully!")
    
    # Test API connectivity
    print("\n🌐 Testing API connectivity...")
    test_api_connectivity(api_client)
    
    # Get user input for game selection
    print("\n🎯 Game Selection Options:")
    print("1. Find recent game between specific teams")
    print("2. Use specific game ID")
    print("3. Generate report for today's games")
    print("4. Test with sample data")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        handle_team_search(api_client, report_generator)
    elif choice == "2":
        handle_specific_game(api_client, report_generator)
    elif choice == "3":
        handle_todays_games(api_client, report_generator)
    elif choice == "4":
        handle_sample_data(report_generator)
    else:
        print("❌ Invalid choice. Exiting.")
        return
    
    print("\n🎉 Enhanced NHL Report Generator completed!")

def test_api_connectivity(api_client):
    """Test API connectivity and show available data"""
    print("Testing NHL API endpoints...")
    
    # Test standings
    standings = api_client.get_standings()
    if standings:
        print("✅ Standings API: Connected")
    else:
        print("❌ Standings API: Failed")
    
    # Test schedule
    schedule = api_client.get_schedule()
    if schedule:
        print("✅ Schedule API: Connected")
    else:
        print("❌ Schedule API: Failed")
    
    # Test team info
    team_info = api_client.get_team_info(22)  # Edmonton Oilers
    if team_info:
        print("✅ Team Info API: Connected")
    else:
        print("❌ Team Info API: Failed")
    
    # Test player stats
    skater_stats = api_client.get_skater_stats(limit=5)
    if skater_stats:
        print("✅ Player Stats API: Connected")
    else:
        print("❌ Player Stats API: Failed")
    
    # Test game data
    recent_game = api_client.find_recent_game('EDM', 'FLA', days_back=30)
    if recent_game:
        print(f"✅ Game Data API: Connected (Found recent game: {recent_game})")
    else:
        print("❌ Game Data API: Failed")

def handle_team_search(api_client, report_generator):
    """Handle team search functionality"""
    print("\n🔍 Team Search")
    team1 = input("Enter first team abbreviation (e.g., EDM): ").strip().upper()
    team2 = input("Enter second team abbreviation (e.g., FLA): ").strip().upper()
    
    if not api_client.validate_team_abbrev(team1) or not api_client.validate_team_abbrev(team2):
        print("❌ Invalid team abbreviation(s)")
        return
    
    print(f"Searching for recent games between {team1} and {team2}...")
    game_id = api_client.find_recent_game(team1, team2, days_back=60)
    
    if game_id:
        print(f"✅ Found game: {game_id}")
        generate_report(api_client, report_generator, game_id)
    else:
        print(f"❌ No recent games found between {team1} and {team2}")

def handle_specific_game(api_client, report_generator):
    """Handle specific game ID input"""
    print("\n🎮 Specific Game ID")
    game_id = input("Enter game ID (e.g., 2024030416): ").strip()
    
    if not game_id:
        print("❌ No game ID provided")
        return
    
    print(f"Fetching data for game {game_id}...")
    game_data = api_client.get_game_center(game_id)
    
    if game_data:
        print("✅ Game data found")
        generate_report(api_client, report_generator, game_id)
    else:
        print("❌ Game data not found")

def handle_todays_games(api_client, report_generator):
    """Handle today's games"""
    print("\n📅 Today's Games")
    
    schedule = api_client.get_schedule()
    if not schedule or 'gameWeek' not in schedule:
        print("❌ No games scheduled for today")
        return
    
    games = []
    for day in schedule['gameWeek']:
        for game in day.get('games', []):
            games.append(game)
    
    if not games:
        print("❌ No games found for today")
        return
    
    print(f"Found {len(games)} game(s) today:")
    for i, game in enumerate(games, 1):
        away_team = game.get('awayTeam', {}).get('abbrev', 'Unknown')
        home_team = game.get('homeTeam', {}).get('abbrev', 'Unknown')
        game_id = game.get('id', 'Unknown')
        print(f"{i}. {away_team} @ {home_team} (ID: {game_id})")
    
    choice = input(f"\nSelect game (1-{len(games)}) or 'all' for all games: ").strip()
    
    if choice.lower() == 'all':
        for game in games:
            game_id = str(game.get('id', ''))
            if game_id:
                generate_report(api_client, report_generator, game_id)
    else:
        try:
            game_index = int(choice) - 1
            if 0 <= game_index < len(games):
                game_id = str(games[game_index].get('id', ''))
                generate_report(api_client, report_generator, game_id)
            else:
                print("❌ Invalid game selection")
        except ValueError:
            print("❌ Invalid input")

def handle_sample_data(report_generator):
    """Handle sample data generation"""
    print("\n🧪 Sample Data Generation")
    print("Generating report with sample data for demonstration...")
    
    # Use a known game ID for testing
    sample_game_id = "2024030416"
    generate_report(None, report_generator, sample_game_id)

def generate_report(api_client, report_generator, game_id):
    """Generate the enhanced report"""
    print(f"\n📊 Generating Enhanced Report for Game {game_id}...")
    
    try:
        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"enhanced_nhl_report_{game_id}_{timestamp}.pdf"
        
        # Generate the report
        result = report_generator.generate_enhanced_report(game_id, output_filename)
        
        if result:
            print(f"✅ Enhanced report generated: {result}")
            
            # Show file size
            if os.path.exists(result):
                file_size = os.path.getsize(result) / (1024 * 1024)  # MB
                print(f"📁 File size: {file_size:.2f} MB")
            
            # Offer to open the file
            open_file = input("\nWould you like to open the report? (y/n): ").strip().lower()
            if open_file == 'y':
                try:
                    if sys.platform == "darwin":  # macOS
                        os.system(f"open {result}")
                    elif sys.platform == "win32":  # Windows
                        os.system(f"start {result}")
                    else:  # Linux
                        os.system(f"xdg-open {result}")
                except Exception as e:
                    print(f"Could not open file: {e}")
        else:
            print("❌ Failed to generate report")
    
    except Exception as e:
        print(f"❌ Error generating report: {e}")

def show_advanced_features():
    """Show advanced features available"""
    print("\n🚀 ADVANCED FEATURES AVAILABLE:")
    print("=" * 50)
    print("📊 Analytics:")
    print("  • Shot location heatmaps")
    print("  • Game momentum tracking")
    print("  • Player performance radars")
    print("  • Team comparison dashboards")
    print("  • Goalie performance analysis")
    print("  • Standings context integration")
    
    print("\n🎯 Data Sources:")
    print("  • Real-time NHL API (2025 endpoints)")
    print("  • Play-by-play data with coordinates")
    print("  • Advanced player statistics")
    print("  • Historical game context")
    print("  • League standings and leaders")
    
    print("\n📈 Visualizations:")
    print("  • Interactive charts and graphs")
    print("  • Professional PDF layouts")
    print("  • Team color schemes")
    print("  • Statistical comparisons")
    print("  • Game flow analysis")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Enhanced NHL Report Generator interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
