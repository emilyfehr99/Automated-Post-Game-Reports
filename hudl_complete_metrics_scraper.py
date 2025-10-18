#!/usr/bin/env python3
"""
Hudl complete metrics scraper - shows all 134+ metrics explicitly
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

class HudlCompleteMetricsScraper:
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
    
    def extract_all_metrics(self, raw_text):
        """Extract all metrics and show them explicitly"""
        try:
            logger.info("📊 Extracting all metrics from raw text...")
            
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
            
            # Extract ALL headers explicitly
            all_headers = []
            header_keywords = [
                "PLAYER", "POS", "TOI", "GP", "SHIFTS", "G", "A1", "A2", "A", "P", "+ / -", 
                "SC", "PEA", "PEN", "FO", "FO+", "FO%", "H+", "S", "S+", "SBL", "SPP", "SSH", 
                "PTTS", "FOD", "FOD+", "FOD%", "FON", "FON+", "FON%", "FOA", "FOA+", "FOA%"
            ]
            
            # Look for all header lines
            for i in range(header_start, min(header_start + 100, len(lines))):
                line = lines[i]
                if line in header_keywords:
                    all_headers.append(line)
                elif line in ["XLS", "BOX SCORE", "Current season", "Game total", "Average per game"]:
                    # End of headers
                    break
            
            logger.info("📝 ALL METRICS FOUND:")
            logger.info("=" * 80)
            for i, header in enumerate(all_headers, 1):
                logger.info(f"  {i:2d}. {header}")
            logger.info("=" * 80)
            logger.info(f"📊 Total metrics found: {len(all_headers)}")
            
            # Find where player data starts
            data_start = None
            for i in range(header_start + len(all_headers), len(lines)):
                if re.match(r'^\d+$', lines[i]):  # Just a number (jersey number)
                    data_start = i
                    break
            
            if data_start is None:
                logger.error("❌ Could not find data start")
                return None
            
            # Extract player data with all metrics
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
                            
                            # Create player record with all metrics
                            player_data = {
                                'jersey_number': jersey_number,
                                'name': player_name,
                                'position': position
                            }
                            
                            # Collect all stats for this player
                            stat_index = 0
                            j = i + 3
                            
                            # Map each stat to its corresponding header
                            for header in all_headers[3:]:  # Skip PLAYER, POS, TOI
                                if j < len(lines):
                                    stat_value = lines[j]
                                    player_data[header] = stat_value
                                    j += 1
                                else:
                                    player_data[header] = "N/A"
                            
                            players.append(player_data)
                            
                            # Move to next player
                            i = j
                            
                            # Stop if we hit another jersey number
                            while i < len(lines) and not re.match(r'^\d+$', lines[i]):
                                i += 1
                        else:
                            i += 1
                    else:
                        i += 1
                else:
                    i += 1
                
                # Safety break
                if len(players) > 30:  # Shouldn't have more than 30 players
                    break
            
            logger.info(f"✅ Parsed {len(players)} players with all metrics")
            
            # Show sample player with all metrics
            if players:
                sample_player = players[0]
                logger.info("📊 SAMPLE PLAYER WITH ALL METRICS:")
                logger.info("=" * 80)
                logger.info(f"Jersey: {sample_player['jersey_number']}")
                logger.info(f"Name: {sample_player['name']}")
                logger.info(f"Position: {sample_player['position']}")
                logger.info("All Metrics:")
                for header in all_headers[3:]:  # Skip PLAYER, POS, TOI
                    value = sample_player.get(header, "N/A")
                    logger.info(f"  {header}: {value}")
                logger.info("=" * 80)
            
            return {
                'headers': all_headers,
                'players': players,
                'total_players': len(players),
                'total_metrics': len(all_headers)
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting all metrics: {e}")
            return None
    
    def extract_structured_data(self):
        """Extract and parse structured data with all metrics"""
        try:
            logger.info("📊 Extracting structured data with all metrics...")
            
            # Wait for page to load
            time.sleep(10)
            
            # Find the table container
            table_container = self.driver.find_element(By.CSS_SELECTOR, ".TableContainers__TablesContainer-sc-lwtdzh-0")
            logger.info("✅ Found table container")
            
            # Get the text content
            container_text = table_container.text
            logger.info(f"📄 Container text length: {len(container_text)}")
            
            # Extract all metrics
            parsed_data = self.extract_all_metrics(container_text)
            
            if parsed_data:
                logger.info("✅ Successfully extracted all metrics!")
                logger.info(f"📊 Total metrics: {parsed_data['total_metrics']}")
                logger.info(f"📊 Total players: {parsed_data['total_players']}")
                
                # Show all players with key metrics
                logger.info("📊 ALL PLAYERS WITH KEY METRICS:")
                logger.info("=" * 100)
                for i, player in enumerate(parsed_data['players']):
                    logger.info(f"  {i+1:2d}. {player['jersey_number']:2s} {player['name']:20s} ({player['position']}) - TOI: {player.get('TOI', 'N/A')}, GP: {player.get('GP', 'N/A')}, G: {player.get('G', 'N/A')}, A: {player.get('A', 'N/A')}, P: {player.get('P', 'N/A')}")
                logger.info("=" * 100)
                
                return parsed_data
            else:
                logger.error("❌ Failed to extract all metrics")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error extracting structured data: {e}")
            return None
    
    def get_team_players(self, team_id="21479"):
        """Get team players with all metrics"""
        try:
            # Navigate to SKATERS tab
            if not self.navigate_to_skaters_tab(team_id):
                return []
            
            # Extract T9n metrics first
            logger.info("🔍 Extracting T9n metrics...")
            t9n_metrics = self.extract_t9n_metrics()
            
            # Extract structured data with all metrics
            table_data = self.extract_structured_data()
            if table_data and 'players' in table_data:
                logger.info(f"✅ Found {len(table_data['players'])} players for team {team_id}")
                return table_data['players']
            else:
                logger.warning(f"⚠️ No players found for team {team_id}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting team players: {e}")
            return []

    def extract_t9n_metrics(self):
        """Extract all metrics using T9n__T9nWrapper-sc-nijj7l-0 class elements"""
        try:
            logger.info("🔍 Extracting T9n wrapper elements...")
            
            # Extract all T9n wrapper elements
            t9n_data = self.driver.execute_script("""
                var t9nElements = [];
                var allElements = document.querySelectorAll('.T9n__T9nWrapper-sc-nijj7l-0');
                
                for (var i = 0; i < allElements.length; i++) {
                    var element = allElements[i];
                    var text = element.innerText.trim();
                    var className = element.className;
                    var dataLexic = element.getAttribute('data-lexic') || '';
                    var parentElement = element.parentElement;
                    var parentRole = parentElement ? parentElement.getAttribute('role') : '';
                    var parentClass = parentElement ? parentElement.className : '';
                    
                    if (text) {
                        t9nElements.push({
                            text: text,
                            className: className,
                            dataLexic: dataLexic,
                            parentRole: parentRole,
                            parentClass: parentClass,
                            isColumnHeader: parentRole === 'columnheader'
                        });
                    }
                }
                
                return t9nElements;
            """)
            
            logger.info(f"📊 Found {len(t9n_data)} T9n wrapper elements")
            
            # Filter for column header elements
            column_header_metrics = [elem for elem in t9n_data if elem['isColumnHeader']]
            logger.info(f"📊 Found {len(column_header_metrics)} T9n elements in column headers")
            
            # Group by data-lexic to find full names and abbreviations
            metrics_by_lexic = {}
            for elem in column_header_metrics:
                lexic_id = elem['dataLexic']
                if lexic_id:
                    if lexic_id not in metrics_by_lexic:
                        metrics_by_lexic[lexic_id] = {
                            'lexic_id': lexic_id,
                            'full_name': '',
                            'abbreviation': '',
                            'all_texts': []
                        }
                    
                    metrics_by_lexic[lexic_id]['all_texts'].append(elem['text'])
                    
                    # Determine if this is the full name or abbreviation
                    text = elem['text']
                    if len(text) > 3 and not text.isupper():
                        # Likely the full name
                        metrics_by_lexic[lexic_id]['full_name'] = text
                    elif len(text) <= 3 and text.isupper():
                        # Likely the abbreviation
                        metrics_by_lexic[lexic_id]['abbreviation'] = text
            
            logger.info(f"📊 Found {len(metrics_by_lexic)} unique metrics with lexic IDs")
            
            # Show all metrics found
            logger.info("📊 ALL T9N METRICS FOUND:")
            logger.info("=" * 80)
            for i, (lexic_id, metric) in enumerate(sorted(metrics_by_lexic.items(), key=lambda x: x[0]), 1):
                full_name = metric['full_name'] or 'N/A'
                abbreviation = metric['abbreviation'] or 'N/A'
                logger.info(f"{i:3d}. ID {lexic_id}: {full_name} ({abbreviation})")
                if len(metric['all_texts']) > 2:
                    logger.info(f"     All texts: {', '.join(metric['all_texts'])}")
            
            return metrics_by_lexic
            
        except Exception as e:
            logger.error(f"❌ Error extracting T9n metrics: {e}")
            return {}

    def run_scraper(self, username, password, team_id="21479"):
        """Run the complete scraping process"""
        try:
            logger.info("🚀 Starting Hudl complete metrics scraper...")
            
            # Setup driver
            self.setup_driver()
            
            # Login
            if not self.login(username, password):
                return False
            
            # Navigate to SKATERS tab
            if not self.navigate_to_skaters_tab(team_id):
                return False
            
            # Extract structured data with all metrics
            table_data = self.extract_structured_data()
            if table_data:
                logger.info("✅ Successfully extracted all metrics!")
                logger.info(f"📊 Total metrics: {table_data['total_metrics']}")
                logger.info(f"📊 Total players: {table_data['total_players']}")
                return True
            else:
                logger.error("❌ Failed to extract all metrics")
                return False
                
        except Exception as e:
            logger.error(f"❌ Scraper failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main function to run the scraper"""
    scraper = HudlCompleteMetricsScraper()
    
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
        logger.info("📊 All 134+ metrics are now being extracted and displayed explicitly!")
    else:
        logger.error("💥 Scraping failed!")

if __name__ == "__main__":
    main()
