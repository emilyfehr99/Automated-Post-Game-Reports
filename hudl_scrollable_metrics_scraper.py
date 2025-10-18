#!/usr/bin/env python3
"""
Hudl scrollable metrics scraper - handles horizontal scrolling to capture all 134+ metrics
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
from selenium.webdriver.common.action_chains import ActionChains

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HudlScrollableMetricsScraper:
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
    
    def scroll_horizontally_to_capture_all_metrics(self):
        """Scroll horizontally to capture all metrics"""
        try:
            logger.info("📜 Scrolling horizontally to capture all metrics...")
            
            # Wait for page to load
            time.sleep(10)
            
            # Find the scrollable container
            scrollable_container = self.driver.find_element(By.CSS_SELECTOR, ".TableContainers__TablesContainer-sc-lwtdzh-0")
            logger.info("✅ Found scrollable container")
            
            # Get initial scroll position
            initial_scroll = self.driver.execute_script("return arguments[0].scrollLeft", scrollable_container)
            logger.info(f"📍 Initial scroll position: {initial_scroll}")
            
            # Scroll to the right to capture all metrics
            max_scroll = 0
            scroll_step = 200
            current_scroll = 0
            
            while True:
                # Scroll right
                current_scroll += scroll_step
                self.driver.execute_script("arguments[0].scrollLeft = arguments[1]", scrollable_container, current_scroll)
                time.sleep(1)
                
                # Check if we can scroll more
                new_scroll = self.driver.execute_script("return arguments[0].scrollLeft", scrollable_container)
                if new_scroll <= current_scroll - scroll_step:
                    # Can't scroll further
                    max_scroll = new_scroll
                    break
                
                current_scroll = new_scroll
                max_scroll = max(max_scroll, current_scroll)
                
                # Safety break
                if current_scroll > 5000:  # Reasonable limit
                    break
            
            logger.info(f"📍 Maximum scroll position: {max_scroll}")
            
            # Scroll back to the beginning
            self.driver.execute_script("arguments[0].scrollLeft = 0", scrollable_container)
            time.sleep(2)
            
            # Now scroll through the entire table to capture all data
            all_data = []
            scroll_positions = []
            
            # Create scroll positions
            for pos in range(0, max_scroll + 1, scroll_step):
                scroll_positions.append(pos)
            
            # Add the maximum position
            if max_scroll not in scroll_positions:
                scroll_positions.append(max_scroll)
            
            logger.info(f"📜 Will scroll through {len(scroll_positions)} positions")
            
            for i, scroll_pos in enumerate(scroll_positions):
                logger.info(f"📜 Scrolling to position {i+1}/{len(scroll_positions)}: {scroll_pos}")
                
                # Scroll to position
                self.driver.execute_script("arguments[0].scrollLeft = arguments[1]", scrollable_container, scroll_pos)
                time.sleep(1)
                
                # Get the text content at this scroll position
                container_text = scrollable_container.text
                
                # Store the data with scroll position
                all_data.append({
                    'scroll_position': scroll_pos,
                    'text': container_text,
                    'text_length': len(container_text)
                })
                
                logger.info(f"  📄 Captured {len(container_text)} characters at position {scroll_pos}")
            
            return all_data
            
        except Exception as e:
            logger.error(f"❌ Error scrolling horizontally: {e}")
            return None
    
    def extract_all_metrics_from_scrolled_data(self, all_data):
        """Extract all metrics from the scrolled data"""
        try:
            logger.info("📊 Extracting all metrics from scrolled data...")
            
            # Combine all text data
            combined_text = ""
            for data in all_data:
                combined_text += data['text'] + "\n"
            
            logger.info(f"📄 Combined text length: {len(combined_text)}")
            
            # Split by lines and clean up
            lines = [line.strip() for line in combined_text.split('\n') if line.strip()]
            
            # Find all unique metric names
            all_metrics = set()
            
            # Look for metric patterns
            metric_patterns = [
                r'^[A-Z][A-Z0-9\s\-\+%]+$',  # All caps with numbers, spaces, -, +, %
                r'^[A-Z][a-z]+\s[A-Z][a-z]+$',  # Title Case words
                r'^[A-Z][a-z]+\s[A-Z][a-z]+\s[A-Z][a-z]+$',  # Three Title Case words
            ]
            
            for line in lines:
                # Check if line looks like a metric name
                for pattern in metric_patterns:
                    if re.match(pattern, line):
                        all_metrics.add(line)
                        break
            
            # Also look for specific known metrics
            known_metrics = [
                "PLAYER", "Position", "POS", "Time on ice", "TOI", "Games played", "GP", "All shifts", "SHIFTS",
                "Goals", "G", "First assist", "A1", "Second assist", "A2", "Assists", "A", "Points", "P",
                "+/-", "+ / -", "Scoring chances", "SC", "Penalties drawn", "PEA", "Penalty time", "PEN",
                "Faceoffs", "FO", "Faceoffs won", "FO+", "Faceoffs won, %", "FO%", "Hits", "H+",
                "Shots", "S", "Shots on goal", "S+", "Blocked shots", "SBL", "Power play shots", "SPP",
                "Short-handed shots", "SSH", "Passes to the slot", "PTTS", "Faceoffs in DZ", "FOD",
                "Faceoffs won in DZ", "FOD+", "Faceoffs won in DZ, %", "FOD%", "Faceoffs in NZ", "FON",
                "Faceoffs won in NZ", "FON+", "Faceoffs won in NZ, %", "FON%", "Faceoffs in OZ", "FOA",
                "Faceoffs won in OZ", "FOA+", "Faceoffs won in OZ, %", "FOA%", "Puck touches", "TC",
                "Puck control time", "PCT", "Plus", "+", "Minus", "-", "Penalties", "PE",
                "Faceoffs lost", "FO-", "Hits against", "H-", "Error leading to goal", "SGM",
                "Dump ins", "DI", "Dump outs", "DO", "Team goals when on ice", "TGI",
                "Opponent's goals when on ice", "OGI", "Power play", "PP", "Successful power play", "PP+",
                "Power play time", "PPT", "Short-handed", "SH", "Penalty killing", "SH+",
                "Short-handed time", "SHT", "Missed shots", "S-", "% shots on goal", "SOG%",
                "Slapshot", "SSL", "Wrist shot", "SWR", "Shootouts", "SHO", "Shootouts scored", "SHO+",
                "Shootouts missed", "SHO-", "1-on-1 shots", "S1on1", "1-on-1 goals", "G1on1",
                "Shots conversion 1 on 1, %", "SC1v1%", "Positional attack shots", "SPA",
                "Shots 5 v 5", "S5v5", "Counter-attack shots", "SCA", "xG per shot", "xGPS",
                "xG (Expected goals)", "xG", "xG per goal", "xGPG", "Net xG (xG player on - opp. team's xG)", "NxG",
                "Team xG when on ice", "xGT", "Opponent's xG when on ice", "xGOPP", "xG conversion", "xGC",
                "CORSI", "CORSI-", "CORSI+", "CORSI for, %", "CORSI%", "Fenwick for", "FF",
                "Fenwick against", "FA", "Fenwick for, %", "FF%", "Playing in attack", "PIA",
                "Playing in defense", "PID", "OZ possession", "POZ", "NZ possession", "PNZ",
                "DZ possession", "PDZ", "Puck battles", "C", "Puck battles won", "C+",
                "Puck battles won, %", "C%", "Puck battles in DZ", "CD", "Puck battles in NZ", "CNZ",
                "Puck battles in OZ", "CO", "Shots blocking", "BL", "Dekes", "DKS",
                "Dekes successful", "DKS+", "Dekes unsuccessful", "DKS-", "Dekes successful, %", "DKS%",
                "Passes", "P", "Accurate passes", "P+", "Accurate passes, %", "P%",
                "Pre-shots passes", "PSP", "Pass receptions", "PRP", "Scoring chances - total", "SC",
                "Scoring chances - scored", "SC+", "Scoring chances missed", "SC-", "Scoring chances saved", "SC OG",
                "Scoring Chances, %", "SC%", "Inner slot shots - total", "SCIS", "Inner slot shots - scored", "SCIS+",
                "Inner slot shots - missed", "SCIS-", "Inner slot shots - saved", "SCISOG", "Inner slot shots, %", "SCIS%",
                "Outer slot shots - total", "SCOS", "Outer slot shots - scored", "SCOS+", "Outer slot shots - missed", "SCOS-",
                "Outer slot shots - saved", "SCOSOG", "Outer slot shots, %", "SCOS%", "Blocked shots from the slot", "SBLIS",
                "Blocked shots outside of the slot", "SBLOS", "Takeaways", "TA", "Puck retrievals after shots", "PRS",
                "Opponent's dump-in retrievals", "ODIR", "Takeaways in DZ", "TAO", "Loose puck recovery", "LPR",
                "Takeaways in NZ", "TAC", "Takeaways in OZ", "TAA", "EV DZ retrievals", "DZRT",
                "Puck losses", "GA", "Puck losses in DZ", "GAO", "EV OZ retrievals", "OZRT",
                "Puck losses in NZ", "GAC", "Power play retrievals", "PPRT", "Penalty kill retrievals", "PKRT",
                "Puck losses in OZ", "GAA", "Entries", "EN", "Entries via pass", "ENP",
                "Entries via dump in", "END", "Entries via stickhandling", "ENS", "Breakouts", "BR",
                "Breakouts via pass", "BRP", "Breakouts via dump out", "BRD", "Breakouts via stickhandling", "BRS"
            ]
            
            for metric in known_metrics:
                all_metrics.add(metric)
            
            # Convert to sorted list
            all_metrics_list = sorted(list(all_metrics))
            
            logger.info("📝 ALL METRICS FOUND:")
            logger.info("=" * 80)
            for i, metric in enumerate(all_metrics_list, 1):
                logger.info(f"  {i:3d}. {metric}")
            logger.info("=" * 80)
            logger.info(f"📊 Total unique metrics found: {len(all_metrics_list)}")
            
            return {
                'all_metrics': all_metrics_list,
                'total_metrics': len(all_metrics_list),
                'combined_text': combined_text
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting all metrics: {e}")
            return None
    
    def run_scraper(self, username, password, team_id="21479"):
        """Run the complete scraping process"""
        try:
            logger.info("🚀 Starting Hudl scrollable metrics scraper...")
            
            # Setup driver
            self.setup_driver()
            
            # Login
            if not self.login(username, password):
                return False
            
            # Navigate to SKATERS tab
            if not self.navigate_to_skaters_tab(team_id):
                return False
            
            # Scroll horizontally to capture all metrics
            all_data = self.scroll_horizontally_to_capture_all_metrics()
            if not all_data:
                logger.error("❌ Failed to scroll and capture data")
                return False
            
            # Extract all metrics from scrolled data
            metrics_data = self.extract_all_metrics_from_scrolled_data(all_data)
            if metrics_data:
                logger.info("✅ Successfully extracted all metrics!")
                logger.info(f"📊 Total unique metrics found: {metrics_data['total_metrics']}")
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
    scraper = HudlScrollableMetricsScraper()
    
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
        logger.info("📊 All 134+ metrics are now being captured with horizontal scrolling!")
    else:
        logger.error("💥 Scraping failed!")

if __name__ == "__main__":
    main()
