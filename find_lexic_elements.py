#!/usr/bin/env python3
"""
Find Lexic Elements
Finds elements with specific data-lexic attributes from the lexical analysis
"""

import time
import json
import logging
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_lexic_elements():
    """Find elements with specific data-lexic attributes"""
    try:
        logger.info("🚀 Starting Lexic Elements Finder...")
        
        # Use the working scraper
        scraper = HudlCompleteMetricsScraper()
        
        if not scraper.setup_driver():
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
        
        # Look for specific data-lexic elements
        target_lexic_ids = ["3605", "4239", "3148", "4311"]  # Box Score, Select All, Download XLS, Advanced
        
        for lexic_id in target_lexic_ids:
            logger.info(f"🔍 Looking for elements with data-lexic='{lexic_id}'...")
            
            # Find elements with this specific data-lexic attribute
            elements = scraper.driver.find_elements("css selector", f"[data-lexic='{lexic_id}']")
            
            if elements:
                logger.info(f"✅ Found {len(elements)} elements with data-lexic='{lexic_id}'")
                
                for i, element in enumerate(elements):
                    try:
                        text = element.text.strip()
                        title = element.get_attribute('title') or ''
                        className = element.get_attribute('class') or ''
                        id_attr = element.get_attribute('id') or ''
                        tag_name = element.tag_name
                        role = element.get_attribute('role') or ''
                        onclick = element.get_attribute('onclick') or ''
                        
                        logger.info(f"  Element {i+1}:")
                        logger.info(f"    Text: '{text}'")
                        logger.info(f"    Title: '{title}'")
                        logger.info(f"    Class: '{className}'")
                        logger.info(f"    ID: '{id_attr}'")
                        logger.info(f"    Tag: '{tag_name}'")
                        logger.info(f"    Role: '{role}'")
                        logger.info(f"    Onclick: '{onclick}'")
                        logger.info(f"    Is Displayed: {element.is_displayed()}")
                        logger.info(f"    Is Enabled: {element.is_enabled()}")
                        logger.info("")
                        
                        # Try to click the element if it looks clickable
                        if (element.is_displayed() and element.is_enabled() and 
                            (text or title) and 
                            any(word in (text + title).lower() for word in ['box', 'score', 'select', 'all', 'download', 'xls', 'advanced'])):
                            
                            logger.info(f"🎯 Attempting to click element with data-lexic='{lexic_id}': '{text or title}'")
                            try:
                                element.click()
                                time.sleep(2)
                                
                                # Check if a modal or new content appeared
                                modal_elements = scraper.driver.find_elements("css selector", 
                                    "[class*='modal'], [class*='Modal'], [class*='popup'], [class*='Popup'], [class*='overlay'], [class*='Overlay']")
                                
                                if modal_elements:
                                    logger.info(f"✅ Modal appeared after clicking data-lexic='{lexic_id}'!")
                                    for j, modal in enumerate(modal_elements):
                                        modal_text = modal.text.strip()
                                        if modal_text:
                                            logger.info(f"  Modal {j+1}: '{modal_text[:100]}...'")
                                else:
                                    logger.info(f"⚠️ No modal appeared after clicking data-lexic='{lexic_id}'")
                                
                            except Exception as e:
                                logger.error(f"❌ Error clicking element with data-lexic='{lexic_id}': {e}")
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing element {i+1} with data-lexic='{lexic_id}': {e}")
            else:
                logger.info(f"❌ No elements found with data-lexic='{lexic_id}'")
        
        # Also look for any elements containing the text we're looking for
        logger.info("🔍 Looking for elements containing target text...")
        target_texts = ["Box score", "BOX SCORE", "Select all", "SELECT ALL", "Download XLS", "Advanced"]
        
        for target_text in target_texts:
            logger.info(f"🔍 Looking for elements containing '{target_text}'...")
            
            # Use XPath to find elements containing this text
            xpath = f"//*[contains(text(), '{target_text}')]"
            elements = scraper.driver.find_elements("xpath", xpath)
            
            if elements:
                logger.info(f"✅ Found {len(elements)} elements containing '{target_text}'")
                
                for i, element in enumerate(elements):
                    try:
                        text = element.text.strip()
                        title = element.get_attribute('title') or ''
                        className = element.get_attribute('class') or ''
                        id_attr = element.get_attribute('id') or ''
                        tag_name = element.tag_name
                        data_lexic = element.get_attribute('data-lexic') or ''
                        
                        logger.info(f"  Element {i+1}:")
                        logger.info(f"    Text: '{text}'")
                        logger.info(f"    Title: '{title}'")
                        logger.info(f"    Class: '{className}'")
                        logger.info(f"    ID: '{id_attr}'")
                        logger.info(f"    Tag: '{tag_name}'")
                        logger.info(f"    Data-lexic: '{data_lexic}'")
                        logger.info(f"    Is Displayed: {element.is_displayed()}")
                        logger.info(f"    Is Enabled: {element.is_enabled()}")
                        logger.info("")
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing element {i+1} containing '{target_text}': {e}")
            else:
                logger.info(f"❌ No elements found containing '{target_text}'")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in find lexic elements: {e}")
        return False
    finally:
        if 'scraper' in locals() and scraper.driver:
            scraper.driver.quit()

def main():
    """Main function"""
    success = find_lexic_elements()
    
    if success:
        logger.info("✅ Lexic elements finder completed successfully")
    else:
        logger.error("❌ Lexic elements finder failed")

if __name__ == "__main__":
    main()
