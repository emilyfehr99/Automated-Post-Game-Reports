#!/usr/bin/env python3
"""
Test Working Scraper
Simple test to see if the working scraper is functioning
"""

import time
import json
import logging
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_scraper():
    """Test the working scraper"""
    try:
        logger.info("🚀 Testing Working Scraper...")
        
        # Use the working scraper
        scraper = HudlCompleteMetricsScraper()
        
        if not scraper.setup_driver():
            logger.error("❌ Driver setup failed")
            return False
        
        logger.info("✅ Driver setup successful")
        
        # Login
        username = "chaserochon777@gmail.com"
        password = "357Chaser!468"
        
        if not scraper.login(username, password):
            logger.error("❌ Login failed")
            return False
        
        logger.info("✅ Login successful")
        
        # Get team players data
        players = scraper.get_team_players("21479")
        
        if not players:
            logger.error("❌ No players data found")
            return False
        
        logger.info(f"✅ Found {len(players)} players")
        
        # Print first player as example
        if players:
            first_player = players[0]
            logger.info(f"📊 First player: {first_player.get('name', 'Unknown')}")
            logger.info(f"📊 Player metrics: {len(first_player.get('metrics', {}))}")
            
            # Show some metrics
            metrics = first_player.get('metrics', {})
            logger.info("📊 Sample metrics:")
            for i, (key, value) in enumerate(list(metrics.items())[:10]):
                logger.info(f"  {i+1:2d}. {key}: {value}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in test scraper: {e}")
        return False
    finally:
        if 'scraper' in locals() and scraper.driver:
            scraper.driver.quit()

def main():
    """Main function"""
    success = test_scraper()
    
    if success:
        logger.info("✅ Test completed successfully")
    else:
        logger.error("❌ Test failed")

if __name__ == "__main__":
    main()
