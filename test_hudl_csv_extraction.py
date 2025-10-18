#!/usr/bin/env python3
"""
Test Hudl CSV Extraction
Test the CSV extraction functionality for Bobcats games
"""

import json
from hudl_csv_extractor import HudlCSVExtractor

def test_csv_extraction():
    """Test CSV extraction for Bobcats games"""
    print("🏒 Testing Hudl CSV Extraction")
    print("=" * 50)
    
    # Initialize extractor
    extractor = HudlCSVExtractor(headless=False)  # Set to True for headless mode
    
    try:
        # Authenticate
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        if not extractor.authenticate(HUDL_USERNAME, HUDL_PASSWORD):
            print("❌ Authentication failed")
            return
        
        print("✅ Successfully authenticated")
        
        # Get games list
        print("\n🔍 Getting games list...")
        games = extractor.get_games_list()
        print(f"Found {len(games)} games")
        
        # Show first few games
        for i, game in enumerate(games[:5], 1):
            print(f"  {i}. {game.home_team} vs {game.away_team} ({game.score}) - {game.date}")
        
        # Download CSV for first game
        if games:
            print(f"\n📥 Downloading CSV for first game...")
            first_game = games[0]
            success = extractor.download_game_csv(first_game)
            
            if success:
                print(f"✅ Successfully downloaded CSV for: {first_game.home_team} vs {first_game.away_team}")
                
                # Process the CSV
                print(f"\n📊 Processing CSV data...")
                df = extractor.process_csv_data(first_game)
                if df is not None:
                    print(f"   Rows: {len(df)}")
                    print(f"   Columns: {list(df.columns)}")
                    print(f"   First few rows:")
                    print(df.head())
            else:
                print(f"❌ Failed to download CSV for: {first_game.home_team} vs {first_game.away_team}")
        
        # Export summary
        print(f"\n📄 Exporting games summary...")
        summary_file = extractor.export_games_summary()
        print(f"Summary exported to: {summary_file}")
        
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        extractor.close()

def main():
    """Main test function"""
    print("🏒 Hudl Instat CSV Extraction Test")
    print("=" * 60)
    print("This will test CSV extraction for your Bobcats games")
    print("Make sure you've updated hudl_credentials.py with your actual credentials")
    print()
    
    test_csv_extraction()

if __name__ == "__main__":
    main()
