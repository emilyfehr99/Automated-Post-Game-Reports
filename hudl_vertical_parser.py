#!/usr/bin/env python3
"""
Hudl vertical data parser - parses the vertical structure where each stat is on its own line
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

class HudlVerticalParser:
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
    
    def parse_vertical_data(self, raw_text):
        """Parse the vertical data structure into player records"""
        try:
            logger.info("📊 Parsing vertical data structure...")
            
            # Split by lines and clean up
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            
            # Find the header section
            header_start = None
            for i, line in enumerate(lines):
                if line == "PLAYER":
                    header_start = i
                    break
            
            if header_start is None:
                logger.error("❌ Could not find header start")
                return None
            
            # Extract headers (the next several lines after PLAYER)
            headers = []
            for i in range(header_start, min(header_start + 50, len(lines))):  # Look at next 50 lines
                line = lines[i]
                if line in ["PLAYER", "POS", "TOI", "GP", "SHIFTS", "G", "A1", "A2", "A", "P", "+ / -", "SC", "PEA", "PEN", "FO", "FO+", "FO%", "H+", "S", "S+", "SBL", "SPP", "SSH", "PTTS", "FOD", "FOD+", "FOD%", "FON", "FON+", "FON%", "FOA", "FOA+", "FOA%"]:
                    headers.append(line)
                elif line == "XLS" or line == "BOX SCORE":  # End of headers
                    break
            
            logger.info(f"📝 Headers: {headers}")
            
            # Find where player data starts (first line that's just a number)
            data_start = None
            for i in range(header_start + len(headers), len(lines)):
                if re.match(r'^\d+$', lines[i]):  # Just a number
                    data_start = i
                    break
            
            if data_start is None:
                logger.error("❌ Could not find data start")
                return None
            
            # Parse player data
            players = []
            i = data_start
            
            while i < len(lines):
                # Look for a line that's just a number (jersey number)
                if re.match(r'^\d+$', lines[i]):
                    jersey_number = lines[i]
                    
                    # The next line should be the player name
                    if i + 1 < len(lines):
                        player_name = lines[i + 1]
                        
                        # The next line should be position
                        if i + 2 < len(lines):
                            position = lines[i + 2]
                            
                            # Now collect all the stats for this player
                            player_data = {
                                'jersey_number': jersey_number,
                                'name': player_name,
                                'position': position
                            }
                            
                            # Collect stats (skip the first 3 lines we already processed)
                            stat_index = 0
                            j = i + 3
                            
                            while j < len(lines) and stat_index < len(headers) - 3:  # -3 because we already have jersey, name, position
                                stat_value = lines[j]
                                
                                # Map to header (skip PLAYER, POS, TOI which we already have)
                                if stat_index < len(headers) - 3:
                                    header_name = headers[3 + stat_index]  # Skip PLAYER, POS, TOI
                                    player_data[header_name] = stat_value
                                
                                stat_index += 1
                                j += 1
                                
                                # Stop if we hit another jersey number
                                if j < len(lines) and re.match(r'^\d+$', lines[j]):
                                    break
                            
                            players.append(player_data)
                            i = j  # Move to next player
                        else:
                            i += 1
                    else:
                        i += 1
                else:
                    i += 1
                
                # Safety break
                if len(players) > 50:  # Shouldn't have more than 50 players
                    break
            
            logger.info(f"✅ Parsed {len(players)} players")
            
            # Show first few players
            for i, player in enumerate(players[:5]):
                logger.info(f"📊 Player {i+1}: {player['jersey_number']} {player['name']} ({player['position']})")
                logger.info(f"    TOI: {player.get('TOI', 'N/A')}, GP: {player.get('GP', 'N/A')}, G: {player.get('G', 'N/A')}")
            
            return {
                'headers': headers,
                'players': players,
                'total_players': len(players)
            }
            
        except Exception as e:
            logger.error(f"❌ Error parsing vertical data: {e}")
            return None
    
    def extract_structured_data(self):
        """Extract and parse structured data from the div-based table"""
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
            
            # Parse the vertical data
            parsed_data = self.parse_vertical_data(container_text)
            
            if parsed_data:
                logger.info("✅ Successfully extracted structured data!")
                logger.info(f"📊 Headers: {parsed_data['headers']}")
                logger.info(f"📊 Total players: {parsed_data['total_players']}")
                
                # Show all players
                logger.info("📊 All players:")
                for i, player in enumerate(parsed_data['players']):
                    logger.info(f"  {i+1:2d}. {player['jersey_number']:2s} {player['name']:20s} ({player['position']}) - TOI: {player.get('TOI', 'N/A')}, GP: {player.get('GP', 'N/A')}, G: {player.get('G', 'N/A')}")
                
                return parsed_data
            else:
                logger.error("❌ Failed to parse data")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error extracting structured data: {e}")
            return None
    
    def run_scraper(self, username, password, team_id="21479"):
        """Run the complete scraping process"""
        try:
            logger.info("🚀 Starting Hudl vertical parser...")
            
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
    scraper = HudlVerticalParser()
    
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
        logger.info("📊 The scraper is now working and extracting structured player data from the div-based table!")
    else:
        logger.error("💥 Scraping failed!")

if __name__ == "__main__":
    main()
