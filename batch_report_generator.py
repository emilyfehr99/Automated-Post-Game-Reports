#!/usr/bin/env python3
"""
NHL Post-Game Report Batch Generator
Generates reports for all games from a specific date
"""

import sys
import os
import shutil
from datetime import datetime, timedelta
from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator

def main():
    print("🏒 NHL Post-Game Report Batch Generator 🏒")
    print("=" * 50)
    
    # Initialize API client
    print("Initializing NHL API client...")
    nhl_client = NHLAPIClient()
    
    # Target date for daily automation: previous day's games (script runs at 5 AM)
    target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Fetching games for: {target_date}")
    
    # Get schedule for the date
    schedule_data = nhl_client.get_game_schedule(target_date)
    
    if not schedule_data:
        print(f"❌ Could not fetch schedule for {target_date}")
        return
    
    print(f"✅ Successfully fetched schedule data")
    
    # Extract games from schedule
    games = []
    if "gameWeek" in schedule_data:
        for day in schedule_data["gameWeek"]:
            if day.get("date") == target_date:
                games = day.get("games", [])
                break
    
    if not games:
        print(f"❌ No games found for {target_date}")
        return
    
    print(f"📅 Found {len(games)} games on {target_date}:")
    
    # Display games
    for i, game in enumerate(games, 1):
        away_team = game.get("awayTeam", {}).get("abbrev", "UNK")
        home_team = game.get("homeTeam", {}).get("abbrev", "UNK")
        game_id = game.get("id", "UNKNOWN")
        game_state = game.get("gameState", "UNKNOWN")
        
        print(f"  {i}. {away_team} @ {home_team} (ID: {game_id}) - {game_state}")
    
    print(f"\n🚀 Starting batch report generation...")
    
    # Create output folder on Desktop
    desktop_path = os.path.expanduser("~/Desktop")
    output_folder = os.path.join(desktop_path, "Recent Games")
    
    # Create the folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 Created output folder: {output_folder}")
    else:
        print(f"📁 Using existing output folder: {output_folder}")
    
    # Initialize PDF generator
    pdf_generator = PostGameReportGenerator()
    
    successful_reports = 0
    failed_reports = 0
    generated_files = []
    
    # Generate reports for each game
    for i, game in enumerate(games, 1):
        game_id = game.get("id")
        away_team = game.get("awayTeam", {}).get("abbrev", "UNK")
        home_team = game.get("homeTeam", {}).get("abbrev", "UNK")
        
        print(f"\n📊 Processing game {i}/{len(games)}: {away_team} @ {home_team} (ID: {game_id})")
        
        try:
            # Get comprehensive game data
            print(f"  🔍 Fetching game data...")
            game_data = nhl_client.get_comprehensive_game_data(game_id)
            
            if not game_data:
                print(f"  ❌ Failed to fetch data for game {game_id}")
                failed_reports += 1
                continue
            
            print(f"  ✅ Game data fetched successfully")
            
            # Generate PDF report
            print(f"  📄 Generating PDF report...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"nhl_postgame_report_{away_team}_vs_{home_team}_{timestamp}.pdf"
            report_filename = pdf_generator.generate_report(game_data, output_filename, game_id)
            
            if report_filename:
                # The report_filename is now the full path to the temp file
                source_path = report_filename
                destination_path = os.path.join(output_folder, os.path.basename(report_filename))
                
                try:
                    shutil.move(source_path, destination_path)
                    print(f"  ✅ Report generated and moved to: {destination_path}")
                    generated_files.append(destination_path)
                    successful_reports += 1
                except Exception as move_error:
                    print(f"  ⚠️  Report generated but failed to move: {move_error}")
                    print(f"  📁 Report saved in temp directory: {source_path}")
                    generated_files.append(source_path)
                    successful_reports += 1
            else:
                print(f"  ❌ Failed to generate report for game {game_id}")
                failed_reports += 1
                
        except Exception as e:
            print(f"  ❌ Error processing game {game_id}: {str(e)}")
            failed_reports += 1
            continue
    
    # Summary
    print(f"\n🎯 BATCH GENERATION COMPLETE")
    print(f"=" * 30)
    print(f"📊 Total games processed: {len(games)}")
    print(f"✅ Successful reports: {successful_reports}")
    print(f"❌ Failed reports: {failed_reports}")
    
    if successful_reports > 0:
        print(f"\n📁 Reports saved in: {output_folder}")
        print(f"📅 Date processed: {target_date}")
        print(f"📋 Generated files:")
        for i, file_path in enumerate(generated_files, 1):
            filename = os.path.basename(file_path)
            print(f"  {i:2d}. {filename}")
    
    return successful_reports, failed_reports

if __name__ == "__main__":
    try:
        successful, failed = main()
        sys.exit(0 if failed == 0 else 1)
    except KeyboardInterrupt:
        print(f"\n⚠️  Batch generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
