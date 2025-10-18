#!/usr/bin/env python3
"""
Hudl scraper using the correct login URL
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HudlCorrectLoginScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Set up Chrome driver"""
        chrome_options = Options()
        # Don't run headless for debugging
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        
    def login(self, username, password):
        """Login using the correct URL"""
        try:
            logger.info("🔐 Starting login process...")
            
            # Use the correct login URL
            login_url = "https://www.hudl.com/login"
            logger.info(f"🌐 Navigating to: {login_url}")
            self.driver.get(login_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Check current URL
            current_url = self.driver.current_url
            logger.info(f"📍 Current URL: {current_url}")
            
            # Find username field
            try:
                username_field = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[type='text'], input[name='username'], input[name='email']"))
                )
                logger.info("✅ Found username field")
                username_field.clear()
                username_field.send_keys(username)
            except TimeoutException:
                logger.error("❌ Username field not found")
                return False
            
            # Find password field
            try:
                password_field = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
                )
                logger.info("✅ Found password field")
                password_field.clear()
                password_field.send_keys(password)
            except TimeoutException:
                logger.error("❌ Password field not found")
                return False
            
            # Find and click submit button
            try:
                submit_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"))
                )
                logger.info("✅ Found submit button")
                submit_button.click()
            except TimeoutException:
                logger.error("❌ Submit button not found")
                return False
            
            # Wait for redirect
            time.sleep(5)
            
            # Check current URL after login
            current_url = self.driver.current_url
            logger.info(f"📍 Current URL after login: {current_url}")
            
            # Check if we're logged in by looking for logout or profile elements
            try:
                # Look for elements that indicate successful login
                profile_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='profile'], [class*='user'], [class*='account']")
                if profile_elements:
                    logger.info("✅ Found profile elements - login successful!")
                    return True
                else:
                    logger.warning("⚠️  No profile elements found, but continuing...")
                    return True
            except:
                logger.warning("⚠️  Could not verify login status, but continuing...")
                return True
            
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False
    
    def navigate_to_skaters(self, team_id="21479"):
        """Navigate to SKATERS tab"""
        try:
            logger.info(f"🏒 Navigating to SKATERS tab for team {team_id}...")
            
            # Navigate to team page
            team_url = f"https://hockey.instatscout.com/teams/{team_id}"
            logger.info(f"🌐 Navigating to: {team_url}")
            self.driver.get(team_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Check current URL
            current_url = self.driver.current_url
            logger.info(f"📍 Current URL: {current_url}")
            
            # Look for SKATERS tab
            try:
                skaters_tab = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/skaters']"))
                )
                logger.info("✅ Found SKATERS tab")
                skaters_tab.click()
                
                # Wait for navigation
                time.sleep(3)
                
                # Check URL after click
                current_url = self.driver.current_url
                logger.info(f"📍 Current URL after clicking SKATERS: {current_url}")
                
                return True
                
            except TimeoutException:
                logger.error("❌ SKATERS tab not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            return False
    
    def extract_skaters_data(self):
        """Extract data from SKATERS table"""
        try:
            logger.info("📊 Extracting SKATERS data...")
            
            # Wait for table to load
            time.sleep(5)
            
            # Look for the table container
            try:
                table_container = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".TableContainers__TablesContainer-sc-lwtdzh-0"))
                )
                logger.info("✅ Found table container")
            except TimeoutException:
                logger.error("❌ Table container not found")
                
                # Let's see what's on the page
                logger.info("🔍 Checking page content...")
                page_source = self.driver.page_source
                logger.info(f"📄 Page source length: {len(page_source)}")
                
                # Look for any table elements
                table_elements = self.driver.find_elements(By.CSS_SELECTOR, "table, [class*='table'], [class*='Table']")
                logger.info(f"📋 Found {len(table_elements)} table-related elements")
                
                # Look for the specific class pattern
                specific_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='TableContainer']")
                logger.info(f"📋 Found {len(specific_elements)} TableContainer elements")
                
                for i, element in enumerate(specific_elements[:3]):
                    try:
                        class_name = element.get_attribute("class")
                        logger.info(f"  Element {i+1}: class='{class_name}'")
                    except:
                        logger.info(f"  Element {i+1}: [unable to get details]")
                
                return None
            
            # Extract table data
            rows = table_container.find_elements(By.CSS_SELECTOR, "tr")
            logger.info(f"📊 Found {len(rows)} table rows")
            
            if not rows:
                logger.warning("⚠️  No table rows found")
                return None
            
            # Extract headers
            headers = []
            if rows:
                header_cells = rows[0].find_elements(By.CSS_SELECTOR, "th, td")
                headers = [cell.text.strip() for cell in header_cells if cell.text.strip()]
                logger.info(f"📝 Headers: {headers}")
            
            # Extract data rows
            data_rows = []
            for i, row in enumerate(rows[1:], 1):
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                row_data = [cell.text.strip() for cell in cells if cell.text.strip()]
                if row_data:
                    data_rows.append(row_data)
                    if i <= 3:  # Log first 3 rows
                        logger.info(f"📊 Row {i}: {row_data}")
            
            logger.info(f"✅ Extracted {len(data_rows)} data rows")
            
            return {
                "headers": headers,
                "data": data_rows,
                "total_rows": len(data_rows)
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting data: {e}")
            return None
    
    def run_scraper(self, username, password, team_id="21479"):
        """Run the complete scraping process"""
        try:
            logger.info("🚀 Starting Hudl correct login scraper...")
            
            # Setup driver
            self.setup_driver()
            
            # Login
            if not self.login(username, password):
                logger.error("❌ Login failed, stopping")
                return False
            
            # Navigate to SKATERS
            if not self.navigate_to_skaters(team_id):
                logger.error("❌ Navigation failed, stopping")
                return False
            
            # Extract data
            data = self.extract_skaters_data()
            if data:
                logger.info("✅ Successfully extracted data!")
                logger.info(f"📊 Headers: {data['headers']}")
                logger.info(f"📊 Total rows: {data['total_rows']}")
                return True
            else:
                logger.error("❌ Failed to extract data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Scraper failed: {e}")
            return False
        finally:
            if self.driver:
                logger.info("🔄 Keeping browser open for inspection...")
                input("Press Enter to close browser...")
                self.driver.quit()

def main():
    """Main function"""
    scraper = HudlCorrectLoginScraper()
    
    # Use credentials
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
