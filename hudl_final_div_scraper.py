#!/usr/bin/env python3
"""
Final Hudl scraper for div-based table structures with proper data parsing
"""

import time
import logging
import re
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

class HudlFinalDivScraper:
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
    
    def parse_player_data(self, raw_text):
        """Parse the raw text data into structured player information"""
        try:
            logger.info("📊 Parsing player data from raw text...")
            
            # Split by lines and clean up
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            
            # Find the header line (contains column names)
            header_line = None
            header_index = 0
            
            for i, line in enumerate(lines):
                if 'PLAYER' in line and 'POS' in line and 'TOI' in line:
                    header_line = line
                    header_index = i
                    break
            
            if not header_line:
                logger.error("❌ Could not find header line")
                return None
            
            # Extract headers
            headers = header_line.split()
            logger.info(f"📝 Headers: {headers}")
            
            # Extract player data (everything after the header)
            player_lines = lines[header_index + 1:]
            
            players_data = []
            current_player = {}
            
            for line in player_lines:
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Check if this looks like a player line (starts with a number)
                if re.match(r'^\d+', line.strip()):
                    # If we have a current player, save it
                    if current_player:
                        players_data.append(current_player)
                    
                    # Start new player
                    parts = line.split()
                    if len(parts) >= 3:
                        current_player = {
                            'jersey_number': parts[0],
                            'name': parts[1],
                            'position': parts[2],
                            'raw_data': line
                        }
                else:
                    # This might be additional data for the current player
                    if current_player:
                        current_player['raw_data'] += ' ' + line
            
            # Add the last player
            if current_player:
                players_data.append(current_player)
            
            logger.info(f"✅ Parsed {len(players_data)} players")
            
            # Log first few players
            for i, player in enumerate(players_data[:5]):
                logger.info(f"📊 Player {i+1}: {player['jersey_number']} {player['name']} ({player['position']})")
            
            return {
                'headers': headers,
                'players': players_data,
                'total_players': len(players_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Error parsing player data: {e}")
            return None
    
    def extract_structured_data(self):
        """Extract structured data from the div-based table"""
        try:
            logger.info("📊 Extracting structured data from div-based table...")
            
            # Wait for page to load
            time.sleep(10)
            
            # Find the table container
            table_container = self.driver.find_element(By.CSS_SELECTOR, ".TableContainers__TablesContainer-sc-lwtdzh-0")
            logger.info("✅ Found table container")
            
            # Get the text content
            container_text = table_container.text
            logger.info(f"📄 Container text length: {len(container_text)}")
            
            # Parse the data
            parsed_data = self.parse_player_data(container_text)
            
            if parsed_data:
                logger.info("✅ Successfully extracted structured data!")
                logger.info(f"📊 Headers: {parsed_data['headers']}")
                logger.info(f"📊 Total players: {parsed_data['total_players']}")
                
                # Show sample of parsed data
                for i, player in enumerate(parsed_data['players'][:3]):
                    logger.info(f"📊 Player {i+1}: {player['jersey_number']} {player['name']} ({player['position']})")
                
                return parsed_data
            else:
                logger.error("❌ Failed to parse data")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error extracting structured data: {e}")
            return None
    
    def find_download_buttons(self):
        """Look for download/export buttons"""
        try:
            logger.info("🔍 Looking for download buttons...")
            
            # Look for various download button patterns
            download_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button[title*='download'], button[title*='export'], .download, .export, [data-testid*='download']")
            
            logger.info(f"Found {len(download_buttons)} download buttons")
            
            for i, btn in enumerate(download_buttons):
                logger.info(f"  {i+1}. {btn.text} - {btn.get_attribute('title')} - {btn.get_attribute('class')}")
            
            return download_buttons
            
        except Exception as e:
            logger.error(f"❌ Error finding download buttons: {e}")
            return []
    
    def run_scraper(self, username, password, team_id="21479"):
        """Run the complete scraping process"""
        try:
            logger.info("🚀 Starting Hudl final div scraper...")
            
            # Setup driver
            self.setup_driver()
            
            # Login
            if not self.login(username, password):
                return False
            
            # Navigate to SKATERS tab
            if not self.navigate_to_skaters_tab(team_id):
                return False
            
            # Extract structured data
            table_data = self.extract_structured_data()
            if table_data:
                logger.info("✅ Successfully extracted structured table data!")
                logger.info(f"📊 Headers: {table_data['headers']}")
                logger.info(f"📊 Total players: {table_data['total_players']}")
                
                # Show all players
                logger.info("📊 All players:")
                for i, player in enumerate(table_data['players']):
                    logger.info(f"  {i+1:2d}. {player['jersey_number']:2s} {player['name']:20s} ({player['position']})")
                
                return True
            else:
                logger.error("❌ Failed to extract structured data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Scraper failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main function to run the scraper"""
    scraper = HudlFinalDivScraper()
    
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
        logger.info("🎉 Scraping completed successfully!")
        logger.info("📊 The scraper is now working and extracting player data from the div-based table structure!")
    else:
        logger.error("💥 Scraping failed!")

if __name__ == "__main__":
    main()
