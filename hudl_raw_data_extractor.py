#!/usr/bin/env python3
"""
Hudl raw data extractor - shows exactly what data we're getting
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HudlRawDataExtractor:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Set up Chrome driver using the proven method"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute script to remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 30)
        
    def login(self, username, password):
        """Login using the proven method"""
        try:
            logger.info("🔐 Logging into Hudl Instat...")
            
            # Go to Hudl Instat
            self.driver.get("https://app.hudl.com/instat/hockey")
            time.sleep(5)
            
            # Find username field
            username_field = self.driver.find_element(By.ID, "username")
            username_field.clear()
            username_field.send_keys(username)
            
            # Find and click Continue button
            continue_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'][name='action'][value='default']")
            continue_button.click()
            time.sleep(5)
            
            # Find password field
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_field.clear()
            password_field.send_keys(password)
            
            # Find and click submit button
            submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")
            if submit_buttons:
                submit_buttons[0].click()
                time.sleep(10)
                
                # Check if login was successful
                if "login" not in self.driver.current_url.lower() and "identity" not in self.driver.current_url.lower():
                    logger.info("✅ Login successful!")
                    return True
                else:
                    logger.error("❌ Login failed - still on login page")
                    return False
            else:
                logger.error("❌ No submit button found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False
    
    def navigate_to_skaters_tab(self, team_id="21479"):
        """Navigate to the SKATERS tab"""
        try:
            logger.info(f"🏒 Navigating to SKATERS tab for team {team_id}...")
            
            # Navigate to team page
            bobcats_url = f"https://app.hudl.com/instat/hockey/teams/{team_id}"
            self.driver.get(bobcats_url)
            time.sleep(5)
            
            # Look for SKATERS tab
            skaters_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='skaters']")
            if skaters_links:
                skaters_links[0].click()
                time.sleep(5)
                return True
            else:
                logger.error("❌ No SKATERS links found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            return False
    
    def extract_and_analyze_data(self):
        """Extract and analyze the raw data structure"""
        try:
            logger.info("📊 Extracting and analyzing raw data...")
            
            # Wait for page to load
            time.sleep(10)
            
            # Find the table container
            table_container = self.driver.find_element(By.CSS_SELECTOR, ".TableContainers__TablesContainer-sc-lwtdzh-0")
            logger.info("✅ Found table container")
            
            # Get the text content
            container_text = table_container.text
            logger.info(f"📄 Container text length: {len(container_text)}")
            
            # Show the raw text structure
            logger.info("📄 Raw text content:")
            logger.info("=" * 80)
            logger.info(container_text)
            logger.info("=" * 80)
            
            # Split by lines and analyze
            lines = [line.strip() for line in container_text.split('\n') if line.strip()]
            logger.info(f"📊 Found {len(lines)} non-empty lines")
            
            # Show first 20 lines
            logger.info("📄 First 20 lines:")
            for i, line in enumerate(lines[:20]):
                logger.info(f"  {i+1:2d}: {line}")
            
            # Look for patterns
            logger.info("🔍 Looking for patterns...")
            
            # Find lines that look like headers
            header_candidates = []
            for i, line in enumerate(lines):
                if any(word in line.upper() for word in ['PLAYER', 'POS', 'TOI', 'GP', 'SHIFTS']):
                    header_candidates.append((i, line))
            
            logger.info(f"📝 Found {len(header_candidates)} potential header lines:")
            for i, (line_num, line) in enumerate(header_candidates):
                logger.info(f"  {i+1}. Line {line_num}: {line}")
            
            # Find lines that look like player data (start with numbers)
            import re
            player_candidates = []
            for i, line in enumerate(lines):
                if re.match(r'^\d+', line.strip()):
                    player_candidates.append((i, line))
            
            logger.info(f"👥 Found {len(player_candidates)} potential player lines:")
            for i, (line_num, line) in enumerate(player_candidates[:10]):  # Show first 10
                logger.info(f"  {i+1}. Line {line_num}: {line}")
            
            return {
                'raw_text': container_text,
                'lines': lines,
                'header_candidates': header_candidates,
                'player_candidates': player_candidates
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting data: {e}")
            return None
    
    def run_scraper(self, username, password, team_id="21479"):
        """Run the complete scraping process"""
        try:
            logger.info("🚀 Starting Hudl raw data extractor...")
            
            # Setup driver
            self.setup_driver()
            
            # Login
            if not self.login(username, password):
                return False
            
            # Navigate to SKATERS tab
            if not self.navigate_to_skaters_tab(team_id):
                return False
            
            # Extract and analyze data
            data = self.extract_and_analyze_data()
            if data:
                logger.info("✅ Successfully extracted and analyzed data!")
                logger.info(f"📊 Found {len(data['lines'])} lines of data")
                logger.info(f"📝 Found {len(data['header_candidates'])} header candidates")
                logger.info(f"👥 Found {len(data['player_candidates'])} player candidates")
                return True
            else:
                logger.error("❌ Failed to extract data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Scraper failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main function to run the scraper"""
    scraper = HudlRawDataExtractor()
    
    # Use credentials from hudl_credentials.py
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        username = HUDL_USERNAME
        password = HUDL_PASSWORD
    except ImportError:
        logger.error("❌ Please create hudl_credentials.py with HUDL_USERNAME and HUDL_PASSWORD")
        return
    
    # Run scraper
    success = scraper.run_scraper(username, password)
    
    if success:
        logger.info("🎉 Data extraction completed successfully!")
        logger.info("📊 Now we can see the exact structure of the div-based table data!")
    else:
        logger.error("💥 Data extraction failed!")

if __name__ == "__main__":
    main()
