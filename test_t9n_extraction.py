#!/usr/bin/env python3
"""
Test T9n Extraction
Tests the T9n extraction method on the working scraper
"""

import time
import json
import logging
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_t9n_extraction():
    """Test T9n extraction method"""
    try:
        logger.info("🚀 Starting T9n Extraction Test...")
        
        # Use the working scraper
        scraper = HudlCompleteMetricsScraper()
        
        if not scraper.setup_driver():
            logger.error("❌ Driver setup failed")
            return False
        
        # Login
        username = "chaserochon777@gmail.com"
        password = "357Chaser!468"
        
        if not scraper.login(username, password):
            logger.error("❌ Authentication failed")
            return False
        
        logger.info("✅ Authentication successful")
        
        # Navigate to team page
        team_url = "https://hockey.instatscout.com/instat/hockey/teams/21479"
        scraper.driver.get(team_url)
        time.sleep(3)
        
        # Click on SKATERS tab
        logger.info("🔍 Clicking SKATERS tab...")
        skaters_tab = scraper.driver.find_element("xpath", "//a[contains(text(), 'SKATERS')]")
        skaters_tab.click()
        time.sleep(3)
        
        # Extract T9n metrics
        logger.info("🔍 Extracting T9n metrics...")
        t9n_metrics = scraper.extract_t9n_metrics()
        
        if t9n_metrics:
            logger.info(f"✅ Successfully extracted {len(t9n_metrics)} T9n metrics!")
            
            # Save results
            with open('t9n_test_results.json', 'w') as f:
                json.dump(t9n_metrics, f, indent=2, default=str)
            
            logger.info("✅ Results saved to t9n_test_results.json")
            return True
        else:
            logger.error("❌ No T9n metrics extracted")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error in T9n extraction test: {e}")
        return False
    finally:
        if 'scraper' in locals() and scraper.driver:
            scraper.driver.quit()

def main():
    """Main function"""
    success = test_t9n_extraction()
    
    if success:
        logger.info("✅ T9n extraction test completed successfully")
    else:
        logger.error("❌ T9n extraction test failed")

if __name__ == "__main__":
    main()
