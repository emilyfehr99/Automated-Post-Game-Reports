#!/usr/bin/env python3
"""
Enhanced Hudl scraper that scrolls to get ALL 136+ comprehensive metrics
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
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedHudlScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Set up Chrome driver"""
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
        """Login to Hudl Instat"""
        try:
            logger.info("🔐 Logging into Hudl Instat...")
            
            # Go to Hudl Instat
            self.driver.get("https://instatscout.com/")
            time.sleep(3)
            
            # Find and click login button
            login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/login']")))
            login_button.click()
            time.sleep(2)
            
            # Enter credentials
            email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "email")))
            password_field = self.driver.find_element(By.NAME, "password")
            
            email_field.clear()
            email_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            time.sleep(5)
            
            # Check if login successful
            if "dashboard" in self.driver.current_url or "teams" in self.driver.current_url:
                logger.info("✅ Login successful!")
                return True
            else:
                logger.error("❌ Login failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def navigate_to_team_players(self, team_id="21479"):
        """Navigate to team players page with scrolling to load all data"""
        try:
            logger.info(f"🏒 Navigating to team {team_id} players...")
            
            # Go to team page
            team_url = f"https://instatscout.com/teams/{team_id}"
            self.driver.get(team_url)
            time.sleep(5)
            
            # Find and click on SKATERS tab
            skaters_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'SKATERS') or contains(text(), 'Skaters')]")))
            skaters_tab.click()
            time.sleep(3)
            
            # Scroll to load all data
            logger.info("📜 Scrolling to load all metrics...")
            self.scroll_to_load_all_data()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Navigation error: {e}")
            return False
    
    def scroll_to_load_all_data(self):
        """Scroll through the page to load all dynamic content"""
        try:
            # Get initial page height
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Scroll down multiple times to trigger lazy loading
            for i in range(10):  # Scroll 10 times
                logger.info(f"📜 Scroll {i+1}/10...")
                
                # Scroll to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Scroll back up a bit to trigger more loading
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")
                time.sleep(1)
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    logger.info("📜 No new content loaded, continuing...")
                else:
                    logger.info(f"📜 New content loaded! Height: {last_height} -> {new_height}")
                    last_height = new_height
                
                # Try to find and click "Load More" or similar buttons
                try:
                    load_more_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Load More') or contains(text(), 'Show More') or contains(text(), 'View All')]")
                    for button in load_more_buttons:
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            time.sleep(2)
                            logger.info("📜 Clicked load more button")
                except:
                    pass
                
                # Try to find horizontal scroll elements and scroll them
                try:
                    horizontal_scrolls = self.driver.find_elements(By.CSS_SELECTOR, "[style*='overflow-x: auto'], [style*='overflow-x: scroll']")
                    for scroll_element in horizontal_scrolls:
                        self.driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollWidth;", scroll_element)
                        time.sleep(0.5)
                except:
                    pass
            
            # Final scroll to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            logger.info("✅ Scrolling complete!")
            
        except Exception as e:
            logger.error(f"❌ Scrolling error: {e}")
    
    def extract_all_metrics(self):
        """Extract all available metrics after scrolling"""
        try:
            logger.info("📊 Extracting ALL metrics after scrolling...")
            
            # Wait for table to be present
            table_container = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table, .table, [class*='table']")))
            
            # Get all text content
            page_text = table_container.text
            logger.info(f"📄 Page text length: {len(page_text)}")
            
            # Split into lines
            lines = page_text.split('\n')
            logger.info(f"📄 Total lines: {len(lines)}")
            
            # Find all headers (look for patterns that indicate column headers)
            all_headers = []
            header_patterns = [
                r'^[A-Z][A-Z\s/%-]+$',  # Uppercase headers
                r'^[A-Z][a-z]+\s[A-Z][a-z]+$',  # Two word headers
                r'^[A-Z][a-z]+\s[%]$',  # Headers with %
                r'^[A-Z][a-z]+\s[+]$',  # Headers with +
                r'^[A-Z][a-z]+\s[-]$',  # Headers with -
            ]
            
            for line in lines:
                line = line.strip()
                if any(re.match(pattern, line) for pattern in header_patterns):
                    if line not in all_headers and len(line) > 1:
                        all_headers.append(line)
            
            # Also look for headers in table structure
            try:
                header_elements = self.driver.find_elements(By.CSS_SELECTOR, "th, .header, [class*='header']")
                for element in header_elements:
                    text = element.text.strip()
                    if text and text not in all_headers and len(text) > 1:
                        all_headers.append(text)
            except:
                pass
            
            logger.info(f"📝 ALL HEADERS FOUND ({len(all_headers)}):")
            logger.info("=" * 80)
            for i, header in enumerate(all_headers, 1):
                logger.info(f"  {i:2d}. {header}")
            logger.info("=" * 80)
            
            # Extract player data
            players = []
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Look for jersey numbers (player rows)
                if re.match(r'^\d+$', line):
                    jersey_number = line
                    
                    # Get player name (usually next line)
                    if i + 1 < len(lines):
                        name = lines[i + 1].strip()
                    else:
                        name = "Unknown"
                    
                    # Get position (usually next line after name)
                    if i + 2 < len(lines):
                        position = lines[i + 2].strip()
                    else:
                        position = "Unknown"
                    
                    # Create player data
                    player_data = {
                        'jersey_number': jersey_number,
                        'name': name,
                        'position': position
                    }
                    
                    # Extract all metrics for this player
                    j = i + 3  # Start after jersey, name, position
                    metric_index = 0
                    
                    while j < len(lines) and metric_index < len(all_headers):
                        stat_line = lines[j].strip()
                        
                        if stat_line and not re.match(r'^\d+$', stat_line):  # Not another jersey number
                            if metric_index < len(all_headers):
                                header = all_headers[metric_index]
                                player_data[header] = stat_line
                                metric_index += 1
                            j += 1
                        else:
                            break
                    
                    players.append(player_data)
                    
                    # Move to next player
                    i = j
                else:
                    i += 1
                
                # Safety break
                if len(players) > 30:
                    break
            
            logger.info(f"✅ Extracted {len(players)} players with {len(all_headers)} metrics each")
            
            # Show sample player
            if players:
                sample_player = players[0]
                logger.info("📊 SAMPLE PLAYER WITH ALL METRICS:")
                logger.info("=" * 80)
                logger.info(f"Jersey: {sample_player['jersey_number']}")
                logger.info(f"Name: {sample_player['name']}")
                logger.info(f"Position: {sample_player['position']}")
                logger.info("All Metrics:")
                for key, value in sample_player.items():
                    if key not in ['jersey_number', 'name', 'position']:
                        logger.info(f"  {key}: {value}")
                logger.info("=" * 80)
            
            return {
                'headers': all_headers,
                'players': players,
                'total_players': len(players),
                'total_metrics': len(all_headers)
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting metrics: {e}")
            return None
    
    def get_team_players(self, team_id="21479"):
        """Get all team players with comprehensive metrics"""
        try:
            if not self.navigate_to_team_players(team_id):
                return []
            
            return self.extract_all_metrics()
            
        except Exception as e:
            logger.error(f"❌ Error getting team players: {e}")
            return []
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

def test_enhanced_scraper():
    """Test the enhanced scraper"""
    scraper = EnhancedHudlScraper()
    
    try:
        scraper.setup_driver()
        
        # Login
        username = "chaserochon777@gmail.com"
        password = "357Chaser!468"
        
        if scraper.login(username, password):
            # Get team players
            result = scraper.get_team_players("21479")
            
            if result:
                print(f"✅ Success! Found {result['total_players']} players with {result['total_metrics']} metrics each")
                print(f"📊 Headers: {result['headers']}")
            else:
                print("❌ Failed to get team players")
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    test_enhanced_scraper()
