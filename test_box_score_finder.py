#!/usr/bin/env python3
"""
Test Box Score Finder
Simple test to find Box Score elements
"""

import time
import logging
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_box_score_finder():
    """Test finding Box Score elements"""
    try:
        logger.info("🚀 Starting Box Score Finder Test...")
        
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
        
        # Look for Box Score elements using multiple methods
        logger.info("🔍 Looking for Box Score elements...")
        
        # Method 1: Look for elements with data-lexic="3605"
        try:
            elements = scraper.driver.find_elements("css selector", "[data-lexic='3605']")
            logger.info(f"📊 Found {len(elements)} elements with data-lexic='3605'")
            for i, element in enumerate(elements):
                text = element.text.strip()
                logger.info(f"  Element {i+1}: '{text}'")
        except Exception as e:
            logger.error(f"❌ Error with data-lexic search: {e}")
        
        # Method 2: Look for elements containing "Box score"
        try:
            elements = scraper.driver.find_elements("xpath", "//*[contains(text(), 'Box score') or contains(text(), 'BOX SCORE')]")
            logger.info(f"📊 Found {len(elements)} elements containing 'Box score'")
            for i, element in enumerate(elements):
                text = element.text.strip()
                tag = element.tag_name
                logger.info(f"  Element {i+1}: '{text}' ({tag})")
        except Exception as e:
            logger.error(f"❌ Error with text search: {e}")
        
        # Method 3: Look for all clickable elements
        try:
            elements = scraper.driver.find_elements("css selector", "button, a, [role='button'], [onclick]")
            logger.info(f"📊 Found {len(elements)} clickable elements")
            
            box_score_elements = []
            for element in elements:
                text = element.text.strip()
                if 'box' in text.lower() and 'score' in text.lower():
                    box_score_elements.append(element)
            
            logger.info(f"📊 Found {len(box_score_elements)} clickable Box Score elements")
            for i, element in enumerate(box_score_elements):
                text = element.text.strip()
                tag = element.tag_name
                logger.info(f"  Clickable {i+1}: '{text}' ({tag})")
        except Exception as e:
            logger.error(f"❌ Error with clickable search: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in test box score finder: {e}")
        return False
    finally:
        if 'scraper' in locals() and scraper.driver:
            scraper.driver.quit()

def main():
    """Main function"""
    success = test_box_score_finder()
    
    if success:
        logger.info("✅ Box Score finder test completed successfully")
    else:
        logger.error("❌ Box Score finder test failed")

if __name__ == "__main__":
    main()
