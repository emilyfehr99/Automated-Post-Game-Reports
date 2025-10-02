#!/usr/bin/env python3
"""
NHL Post-Game Report Batch Generator
Generates reports for all games from a specific date
Automatically converts PDFs to images and cleans up PDFs
"""

import sys
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from pdf2image import convert_from_path
from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator

def convert_pdfs_to_images(pdf_folder, image_folder, dpi=300):
    """
    Convert all PDF files in a folder to images and return list of generated images
    
    Args:
        pdf_folder (str): Path to folder containing PDF files
        image_folder (str): Path to folder where images will be saved
        dpi (int): DPI for the output images
    
    Returns:
        list: List of generated image file paths
    """
    pdf_folder = Path(pdf_folder)
    image_folder = Path(image_folder)
    
    if not pdf_folder.exists():
        print(f"❌ PDF folder not found: {pdf_folder}")
        return []
    
    # Create image folder if it doesn't exist
    image_folder.mkdir(parents=True, exist_ok=True)
    
    # Find all PDF files
    pdf_files = list(pdf_folder.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in: {pdf_folder}")
        return []
    
    print(f"🔄 Converting {len(pdf_files)} PDFs to images...")
    print(f"📁 PDF folder: {pdf_folder}")
    print(f"📁 Image folder: {image_folder}")
    print(f"📐 DPI: {dpi}")
    
    generated_images = []
    
    for pdf_file in pdf_files:
        try:
            print(f"  🔄 Converting: {pdf_file.name}")
            
            # Convert PDF to images (only first page)
            images = convert_from_path(pdf_file, dpi=dpi, first_page=1, last_page=1)
            
            if images:
                # Only process the first page
                image = images[0]
                base_name = pdf_file.stem
                output_filename = f"{base_name}.png"
                output_path = image_folder / output_filename
                
                # Save image
                image.save(output_path, format='PNG')
                generated_images.append(str(output_path))
                
                print(f"    ✅ Page 1: {output_filename}")
                
        except Exception as e:
            print(f"    ❌ Error converting {pdf_file.name}: {str(e)}")
            continue
    
    print(f"✅ PDF to image conversion complete: {len(generated_images)} images generated")
    return generated_images

def main():
    print("🏒 NHL Post-Game Report Batch Generator 🏒")
    print("=" * 50)
    
    # Initialize API client
    print("Initializing NHL API client...")
    nhl_client = NHLAPIClient()
    
    # Target date for daily automation: previous day's games (script runs at 5 AM)
    # Can be overridden with TARGET_DATE environment variable
    target_date = os.environ.get('TARGET_DATE', (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))
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
    
    # Create output folders on Desktop
    desktop_path = os.path.expanduser("~/Desktop")
    pdf_folder = os.path.join(desktop_path, f"NHL_Reports_{target_date.replace('-', '_')}")
    image_folder = os.path.join(desktop_path, f"NHL_Images_{target_date.replace('-', '_')}")
    
    # Recreate the PDF folder to ensure only current run's reports are present
    if os.path.exists(pdf_folder):
        try:
            shutil.rmtree(pdf_folder)
        except Exception as e:
            print(f"⚠️  Could not remove existing PDF folder, attempting to continue: {e}")
    os.makedirs(pdf_folder, exist_ok=True)
    print(f"📁 Prepared fresh PDF folder: {pdf_folder}")
    
    print(f"📁 Images will be saved to: {image_folder}")
    
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
            
            # Check if game has shot coordinate data
            print(f"  🎯 Checking shot coordinate data...")
            has_shot_coords = False
            if 'play_by_play' in game_data and 'plays' in game_data['play_by_play']:
                plays = game_data['play_by_play']['plays']
                shot_plays = [p for p in plays if p.get('typeDescKey') in ['goal', 'shot-on-goal', 'missed-shot', 'blocked-shot']]
                
                # Check if any shots have valid coordinates
                for play in shot_plays:
                    details = play.get('details', {})
                    x_coord = details.get('xCoord')
                    y_coord = details.get('yCoord')
                    if x_coord is not None and y_coord is not None and (x_coord != 0 and y_coord != 0):
                        has_shot_coords = True
                        break
            
            if not has_shot_coords:
                print(f"  ⏭️  Skipping game - no shot coordinate data available")
                continue
            
            print(f"  ✅ Shot coordinate data found - proceeding with report generation")
            
            # Generate PDF report
            print(f"  📄 Generating PDF report...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"nhl_postgame_report_{away_team}_vs_{home_team}_{timestamp}.pdf"
            report_filename = pdf_generator.generate_report(game_data, output_filename, game_id)
            
            if report_filename:
                # The report_filename is now the full path to the temp file
                source_path = report_filename
                destination_path = os.path.join(pdf_folder, os.path.basename(report_filename))
                
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
    print(f"\n🎯 PDF GENERATION COMPLETE")
    print(f"=" * 30)
    print(f"📊 Total games processed: {len(games)}")
    print(f"✅ Successful reports: {successful_reports}")
    print(f"❌ Failed reports: {failed_reports}")
    
    if successful_reports > 0:
        print(f"\n📁 PDFs saved in: {pdf_folder}")
        print(f"📅 Date processed: {target_date}")
        print(f"📋 Generated PDF files:")
        for i, file_path in enumerate(generated_files, 1):
            filename = os.path.basename(file_path)
            print(f"  {i:2d}. {filename}")
        
        # Convert PDFs to images
        print(f"\n🔄 Converting PDFs to images...")
        generated_images = convert_pdfs_to_images(pdf_folder, image_folder, dpi=300)
        
        if generated_images:
            print(f"\n📁 Images saved in: {image_folder}")
            print(f"📋 Generated image files:")
            for i, image_path in enumerate(generated_images, 1):
                filename = os.path.basename(image_path)
                print(f"  {i:2d}. {filename}")
            
            # Clean up PDF folder
            print(f"\n🗑️  Cleaning up PDF folder...")
            try:
                shutil.rmtree(pdf_folder)
                print(f"✅ PDF folder deleted: {pdf_folder}")
            except Exception as e:
                print(f"⚠️  Could not delete PDF folder: {e}")
                print(f"📁 PDF folder still exists: {pdf_folder}")
        else:
            print(f"❌ No images were generated, keeping PDF folder")
    
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
