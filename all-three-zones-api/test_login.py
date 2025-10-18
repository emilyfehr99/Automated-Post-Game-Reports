#!/usr/bin/env python3
"""
Test script to verify All Three Zones login functionality
"""

import os
import sys
import logging
from dotenv import load_dotenv
from a3z_scraper import AllThreeZonesScraper
from config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_login():
    """Test login functionality"""
    logger.info("Testing All Three Zones login...")
    
    try:
        # Create scraper instance
        scraper = AllThreeZonesScraper()
        
        # Test login
        if scraper.login():
            logger.info("✅ Successfully logged in to All Three Zones!")
            
            # Test getting player data
            logger.info("Testing player data retrieval...")
            players = scraper.get_player_data()
            
            if players:
                logger.info(f"✅ Successfully retrieved {len(players)} players")
                for i, player in enumerate(players[:3]):  # Show first 3 players
                    logger.info(f"  Player {i+1}: {player.name} ({player.team})")
            else:
                logger.warning("⚠️  No players found - may need to adjust parsing logic")
            
            # Test team data
            logger.info("Testing team data retrieval...")
            team_data = scraper.get_team_data()
            
            if team_data:
                logger.info(f"✅ Successfully retrieved team data with {len(team_data)} stats")
            else:
                logger.warning("⚠️  No team data found - may need to adjust parsing logic")
            
        else:
            logger.error("❌ Failed to login to All Three Zones")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during login test: {e}")
        return False
    finally:
        if 'scraper' in locals():
            scraper.close()
    
    return True

def main():
    """Main test function"""
    logger.info("Starting All Three Zones login test...")
    
    if test_login():
        logger.info("🎉 Login test completed successfully!")
        logger.info("\nThe API is ready to use. Start it with:")
        logger.info("python3 run.py")
    else:
        logger.error("❌ Login test failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 