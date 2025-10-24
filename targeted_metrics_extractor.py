#!/usr/bin/env python3
"""
Targeted Metrics Extractor
Uses the specific IDs from the lexical data to find and interact with the Box Score modal
"""

import time
import json
import logging
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TargetedMetricsExtractor:
    def __init__(self):
        self.scraper = HudlCompleteMetricsScraper()
        
        # Key IDs from lexical analysis
        self.BOX_SCORE_ID = "3605"
        self.SELECT_ALL_ID = "4239" 
        self.DOWNLOAD_XLS_ID = "3148"
        self.ADVANCED_ID = "4311"
        
    def extract_all_metrics(self, team_id: str = "21479"):
        """Extract all metrics using targeted approach"""
        try:
            logger.info("🚀 Starting Targeted Metrics Extraction...")
            
            if not self.scraper.setup_driver():
                return {}
            
            # Login
            username = "chaserochon777@gmail.com"
            password = "357Chaser!468"
            
            if not self.scraper.login(username, password):
                logger.error("❌ Authentication failed")
                return {}
            
            logger.info("✅ Authentication successful")
            
            # Navigate to team page
            team_url = f"https://hockey.instatscout.com/instat/hockey/teams/{team_id}"
            self.scraper.driver.get(team_url)
            time.sleep(3)
            
            # Click on SKATERS tab
            logger.info("🔍 Clicking SKATERS tab...")
            skaters_tab = self.scraper.driver.find_element("xpath", "//a[contains(text(), 'SKATERS')]")
            skaters_tab.click()
            time.sleep(3)
            
            # Look for Box Score button using multiple methods
            logger.info("🔍 Looking for Box Score button...")
            box_score_found = False
            
            # Method 1: Look for elements with data-lexic="3605"
            try:
                box_score_elements = self.scraper.driver.find_elements("css selector", f'[data-lexic="{self.BOX_SCORE_ID}"]')
                if box_score_elements:
                    logger.info(f"✅ Found {len(box_score_elements)} Box Score elements with data-lexic")
                    for i, element in enumerate(box_score_elements):
                        try:
                            text = element.text.strip()
                            logger.info(f"  Box Score {i+1}: '{text}'")
                            if 'box' in text.lower() and 'score' in text.lower():
                                logger.info(f"📊 Clicking Box Score element: '{text}'")
                                element.click()
                                time.sleep(3)
                                box_score_found = True
                                break
                        except Exception as e:
                            logger.debug(f"Error with Box Score element {i+1}: {e}")
            except Exception as e:
                logger.debug(f"Error with data-lexic search: {e}")
            
            # Method 2: Look for elements containing "Box score" text
            if not box_score_found:
                try:
                    box_score_elements = self.scraper.driver.find_elements("xpath", "//*[contains(text(), 'Box score') or contains(text(), 'BOX SCORE') or contains(text(), 'Box Score')]")
                    if box_score_elements:
                        logger.info(f"✅ Found {len(box_score_elements)} Box Score elements with text search")
                        for i, element in enumerate(box_score_elements):
                            try:
                                text = element.text.strip()
                                logger.info(f"  Box Score {i+1}: '{text}'")
                                if 'box' in text.lower() and 'score' in text.lower():
                                    logger.info(f"📊 Clicking Box Score element: '{text}'")
                                    element.click()
                                    time.sleep(3)
                                    box_score_found = True
                                    break
                            except Exception as e:
                                logger.debug(f"Error with Box Score element {i+1}: {e}")
                except Exception as e:
                    logger.debug(f"Error with text search: {e}")
            
            # Method 3: Look for Download XLS button (might trigger Box Score modal)
            if not box_score_found:
                try:
                    download_elements = self.scraper.driver.find_elements("css selector", f'[data-lexic="{self.DOWNLOAD_XLS_ID}"]')
                    if download_elements:
                        logger.info(f"✅ Found {len(download_elements)} Download XLS elements")
                        for i, element in enumerate(download_elements):
                            try:
                                text = element.text.strip()
                                logger.info(f"  Download {i+1}: '{text}'")
                                if 'download' in text.lower() or 'xls' in text.lower():
                                    logger.info(f"📊 Clicking Download XLS element: '{text}'")
                                    element.click()
                                    time.sleep(3)
                                    box_score_found = True
                                    break
                            except Exception as e:
                                logger.debug(f"Error with Download element {i+1}: {e}")
                except Exception as e:
                    logger.debug(f"Error with Download XLS search: {e}")
            
            if box_score_found:
                logger.info("🎉 Box Score modal opened! Looking for Select All...")
                
                # Wait for modal to load
                time.sleep(2)
                
                # Look for Select All button
                select_all_found = False
                
                # Method 1: Look for elements with data-lexic="4239"
                try:
                    select_all_elements = self.scraper.driver.find_elements("css selector", f'[data-lexic="{self.SELECT_ALL_ID}"]')
                    if select_all_elements:
                        logger.info(f"✅ Found {len(select_all_elements)} Select All elements with data-lexic")
                        for i, element in enumerate(select_all_elements):
                            try:
                                text = element.text.strip()
                                logger.info(f"  Select All {i+1}: '{text}'")
                                if 'select' in text.lower() and 'all' in text.lower():
                                    logger.info(f"📊 Clicking Select All element: '{text}'")
                                    element.click()
                                    time.sleep(1)
                                    select_all_found = True
                                    break
                            except Exception as e:
                                logger.debug(f"Error with Select All element {i+1}: {e}")
                except Exception as e:
                    logger.debug(f"Error with Select All data-lexic search: {e}")
                
                # Method 2: Look for elements containing "Select all" text
                if not select_all_found:
                    try:
                        select_all_elements = self.scraper.driver.find_elements("xpath", "//*[contains(text(), 'Select all') or contains(text(), 'SELECT ALL') or contains(text(), 'Select All')]")
                        if select_all_elements:
                            logger.info(f"✅ Found {len(select_all_elements)} Select All elements with text search")
                            for i, element in enumerate(select_all_elements):
                                try:
                                    text = element.text.strip()
                                    logger.info(f"  Select All {i+1}: '{text}'")
                                    if 'select' in text.lower() and 'all' in text.lower():
                                        logger.info(f"📊 Clicking Select All element: '{text}'")
                                        element.click()
                                        time.sleep(1)
                                        select_all_found = True
                                        break
                                except Exception as e:
                                    logger.debug(f"Error with Select All element {i+1}: {e}")
                    except Exception as e:
                        logger.debug(f"Error with Select All text search: {e}")
                
                if select_all_found:
                    logger.info("✅ Select All clicked! Looking for Apply/OK button...")
                    
                    # Look for Apply/OK button
                    apply_found = False
                    apply_selectors = [
                        "button:contains('OK')", "button:contains('Apply')", "button:contains('Submit')",
                        "button:contains('Confirm')", "button:contains('Done')", "button:contains('Close')",
                        "button[type='submit']", "input[type='submit']", ".apply-button", ".ok-button"
                    ]
                    
                    for selector in apply_selectors:
                        try:
                            if ":contains(" in selector:
                                xpath = f"//button[contains(text(), '{selector.split(':contains(')[1].split(')')[0]}')]"
                                apply_buttons = self.scraper.driver.find_elements("xpath", xpath)
                            else:
                                apply_buttons = self.scraper.driver.find_elements("css selector", selector)
                            
                            if apply_buttons:
                                logger.info(f"✅ Found {len(apply_buttons)} Apply buttons with selector: {selector}")
                                for i, button in enumerate(apply_buttons):
                                    try:
                                        text = button.text.strip()
                                        logger.info(f"  Apply {i+1}: '{text}'")
                                        if any(word in text.lower() for word in ['ok', 'apply', 'submit', 'confirm', 'done', 'close']):
                                            logger.info(f"📊 Clicking Apply button: '{text}'")
                                            button.click()
                                            time.sleep(2)
                                            apply_found = True
                                            break
                                    except Exception as e:
                                        logger.debug(f"Error with Apply button {i+1}: {e}")
                                if apply_found:
                                    break
                        except Exception as e:
                            logger.debug(f"Error with Apply selector {selector}: {e}")
                    
                    if apply_found:
                        logger.info("✅ Apply button clicked! Modal should be closed and all metrics selected.")
                    else:
                        logger.warning("⚠️ Apply button not found, trying to close modal...")
                        # Try to close modal with escape key
                        self.scraper.driver.execute_script("document.body.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));")
                        time.sleep(1)
                else:
                    logger.warning("⚠️ Select All button not found")
            else:
                logger.warning("⚠️ Box Score button not found")
            
            # Now try to extract data with all metrics selected
            logger.info("🔍 Extracting data with all metrics...")
            
            # Get team players data
            players = self.scraper.get_team_players(team_id)
            
            if not players:
                logger.error("❌ No players data found")
                return {}
            
            logger.info(f"✅ Found {len(players)} players")
            
            # Analyze the metrics we got
            if players:
                first_player = players[0]
                metrics = first_player.get('metrics', {})
                logger.info(f"📊 Player metrics count: {len(metrics)}")
                
                # Show all metrics
                logger.info("📊 All metrics found:")
                for i, (key, value) in enumerate(sorted(metrics.items()), 1):
                    logger.info(f"  {i:3d}. {key}: {value}")
            
            results = {
                'players': players,
                'total_players': len(players),
                'box_score_found': box_score_found,
                'select_all_found': select_all_found if 'select_all_found' in locals() else False,
                'apply_found': apply_found if 'apply_found' in locals() else False,
                'extraction_timestamp': time.time()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in targeted metrics extraction: {e}")
            return {}
        finally:
            if hasattr(self.scraper, 'driver') and self.scraper.driver:
                self.scraper.driver.quit()

def main():
    """Main function"""
    extractor = TargetedMetricsExtractor()
    results = extractor.extract_all_metrics()
    
    # Save results
    with open('targeted_metrics_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("✅ Results saved to targeted_metrics_results.json")
    
    # Print summary
    if results:
        logger.info(f"📊 Total players: {results.get('total_players', 0)}")
        logger.info(f"📊 Box Score found: {results.get('box_score_found', False)}")
        logger.info(f"📊 Select All found: {results.get('select_all_found', False)}")
        logger.info(f"📊 Apply found: {results.get('apply_found', False)}")

if __name__ == "__main__":
    main()
