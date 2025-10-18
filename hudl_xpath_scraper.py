#!/usr/bin/env python3
"""
Hudl scraper using the specific XPath selectors provided by the user
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

class HudlXPathScraper:
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
    
    def extract_table_data_with_xpath(self):
        """Extract data using the specific XPath selectors"""
        try:
            logger.info("📊 Extracting table data using XPath selectors...")
            
            # Wait for page to load
            time.sleep(10)
            
            # Try the main table container XPath first
            try:
                logger.info("🔍 Looking for main table container...")
                main_table = self.driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div")
                logger.info("✅ Found main table container")
                
                # Look for rows within the main table
                rows = main_table.find_elements(By.XPATH, ".//tr")
                logger.info(f"📊 Found {len(rows)} rows in main table")
                
                if rows:
                    return self.extract_data_from_rows(rows, "main table")
                
            except Exception as e:
                logger.warning(f"⚠️  Main table not found: {e}")
            
            # Try the specific table data XPath
            try:
                logger.info("🔍 Looking for table data container...")
                table_data = self.driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div/div/div[2]")
                logger.info("✅ Found table data container")
                
                # Look for rows within the table data
                rows = table_data.find_elements(By.XPATH, ".//tr")
                logger.info(f"📊 Found {len(rows)} rows in table data")
                
                if rows:
                    return self.extract_data_from_rows(rows, "table data")
                
            except Exception as e:
                logger.warning(f"⚠️  Table data not found: {e}")
            
            # Try the scrollable container XPath
            try:
                logger.info("🔍 Looking for scrollable container...")
                scrollable_container = self.driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div/div/div[2]/div/div/div[2]")
                logger.info("✅ Found scrollable container")
                
                # Look for rows within the scrollable container
                rows = scrollable_container.find_elements(By.XPATH, ".//tr")
                logger.info(f"📊 Found {len(rows)} rows in scrollable container")
                
                if rows:
                    return self.extract_data_from_rows(rows, "scrollable container")
                
            except Exception as e:
                logger.warning(f"⚠️  Scrollable container not found: {e}")
            
            # Fallback: look for any table elements
            logger.info("🔍 Fallback: Looking for any table elements...")
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
            logger.info(f"📋 Found {len(tables)} table elements")
            
            for i, table in enumerate(tables):
                rows = table.find_elements(By.CSS_SELECTOR, "tr")
                logger.info(f"  Table {i+1}: {len(rows)} rows")
                
                if rows:
                    return self.extract_data_from_rows(rows, f"table {i+1}")
            
            logger.error("❌ No table data found with any method")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting table data: {e}")
            return None
    
    def extract_data_from_rows(self, rows, source):
        """Extract data from a list of table rows"""
        try:
            logger.info(f"📊 Extracting data from {source}...")
            
            if not rows:
                logger.warning("⚠️  No rows provided")
                return None
            
            # Extract headers
            headers = []
            if rows:
                header_cells = rows[0].find_elements(By.CSS_SELECTOR, "th, td")
                headers = [cell.text.strip() for cell in header_cells if cell.text.strip()]
                logger.info(f"📝 Headers: {headers}")
            
            # Extract data rows
            data_rows = []
            for i, row in enumerate(rows[1:], 1):  # Skip header row
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                row_data = [cell.text.strip() for cell in cells if cell.text.strip()]
                if row_data:  # Only add non-empty rows
                    data_rows.append(row_data)
                    if i <= 5:  # Log first 5 rows
                        logger.info(f"📊 Row {i}: {row_data}")
            
            logger.info(f"✅ Extracted {len(data_rows)} data rows from {source}")
            
            return {
                "headers": headers,
                "data": data_rows,
                "total_rows": len(data_rows),
                "source": source
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting data from rows: {e}")
            return None
    
    def scroll_to_load_all_data(self):
        """Scroll to load all data in the scrollable container"""
        try:
            logger.info("📜 Scrolling to load all data...")
            
            # Find the scrollable container
            scrollable_container = self.driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div/div/div[2]/div/div/div[2]")
            
            # Scroll to the bottom to load all data
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_container)
            time.sleep(3)
            
            # Scroll back to top
            self.driver.execute_script("arguments[0].scrollTop = 0", scrollable_container)
            time.sleep(2)
            
            logger.info("✅ Scrolling completed")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Could not scroll: {e}")
            return False
    
    def run_scraper(self, username, password, team_id="21479"):
        """Run the complete scraping process"""
        try:
            logger.info("🚀 Starting Hudl XPath scraper...")
            
            # Setup driver
            self.setup_driver()
            
            # Login
            if not self.login(username, password):
                return False
            
            # Navigate to SKATERS tab
            if not self.navigate_to_skaters_tab(team_id):
                return False
            
            # Scroll to load all data
            self.scroll_to_load_all_data()
            
            # Extract table data
            table_data = self.extract_table_data_with_xpath()
            if table_data:
                logger.info("✅ Successfully extracted table data!")
                logger.info(f"📊 Headers: {table_data['headers']}")
                logger.info(f"📊 Total data rows: {table_data['total_rows']}")
                logger.info(f"📊 Source: {table_data['source']}")
                return True
            else:
                logger.error("❌ Failed to extract table data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Scraper failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main function to run the scraper"""
    scraper = HudlXPathScraper()
    
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
    else:
        logger.error("💥 Scraping failed!")

if __name__ == "__main__":
    main()
