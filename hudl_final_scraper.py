#!/usr/bin/env python3
"""
Final Hudl scraper using the proven login method and targeting the SKATERS table
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HudlFinalScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Set up Chrome driver with proven settings"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-images")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        
    def login(self, username, password):
        """Login using the proven method"""
        try:
            logger.info("🔐 Logging into Hudl Instat...")
            
            # Use the working login URL
            login_url = "https://identity.hudl.com/u/login/identifier?state=hKFo2SB1a0VBRWdFRVRIOFhlNXpTRUlkamtRM0xwc3FmaTQtTKFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIEJLWnJRYndfNU1XakRaVDZRcnlpRkdRalRwczBqRFAxo2NpZNkgTWM2VVdxdXl5WTRLcXgzbE9URXlDQkRodmVGOTJDcVo"
            self.driver.get(login_url)
            
            # Wait for username field
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(username)
            
            # Click continue button
            continue_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            continue_button.click()
            
            # Wait for password field
            password_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            login_button.click()
            
            # Wait for redirect to Instat
            self.wait.until(
                EC.url_contains("instatscout.com")
            )
            
            logger.info("✅ Successfully logged in!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False
    
    def navigate_to_skaters_tab(self, team_id="21479"):
        """Navigate to the SKATERS tab for a specific team"""
        try:
            logger.info(f"🏒 Navigating to SKATERS tab for team {team_id}...")
            
            # Navigate to team page
            team_url = f"https://hockey.instatscout.com/teams/{team_id}"
            self.driver.get(team_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Click on SKATERS tab
            skaters_tab = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/skaters']"))
            )
            skaters_tab.click()
            
            # Wait for SKATERS page to load
            self.wait.until(
                EC.url_contains("/skaters")
            )
            
            logger.info("✅ Successfully navigated to SKATERS tab!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to navigate to SKATERS tab: {e}")
            return False
    
    def wait_for_table_and_extract_data(self):
        """Wait for table to load and extract data"""
        try:
            logger.info("⏳ Waiting for data table to load...")
            
            # Wait for the main table container
            table_container = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".TableContainers__TablesContainer-sc-lwtdzh-0"))
            )
            
            # Wait for table content to be visible
            self.wait.until(
                EC.visibility_of(table_container)
            )
            
            # Additional wait for dynamic content
            time.sleep(5)
            
            logger.info("✅ Table loaded successfully!")
            
            # Extract table data
            logger.info("📊 Extracting table data...")
            
            # Find all table rows
            rows = table_container.find_elements(By.CSS_SELECTOR, "tr")
            
            if not rows:
                logger.warning("⚠️  No table rows found")
                return None
            
            logger.info(f"📋 Found {len(rows)} table rows")
            
            # Extract header row
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
            
            logger.info(f"✅ Extracted {len(data_rows)} data rows")
            
            return {
                "headers": headers,
                "data": data_rows,
                "total_rows": len(data_rows)
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting table data: {e}")
            return None
    
    def find_download_buttons(self):
        """Look for download/export buttons"""
        try:
            logger.info("🔍 Looking for download buttons...")
            
            # Look for various download button patterns
            download_selectors = [
                "button[class*='download']",
                "button[class*='export']",
                "button[class*='csv']",
                "a[class*='download']",
                "a[class*='export']",
                "a[class*='csv']",
                "[data-testid*='download']",
                "[data-testid*='export']",
                "button[title*='download']",
                "button[title*='export']",
                "button[aria-label*='download']",
                "button[aria-label*='export']"
            ]
            
            download_buttons = []
            for selector in download_selectors:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                download_buttons.extend(buttons)
            
            if download_buttons:
                logger.info(f"✅ Found {len(download_buttons)} potential download buttons")
                for i, button in enumerate(download_buttons):
                    try:
                        button_text = button.text.strip()
                        button_class = button.get_attribute("class")
                        button_title = button.get_attribute("title")
                        logger.info(f"  Button {i+1}: '{button_text}' (class: {button_class}, title: {button_title})")
                    except:
                        logger.info(f"  Button {i+1}: [unable to get details]")
            else:
                logger.warning("⚠️  No download buttons found")
            
            return download_buttons
            
        except Exception as e:
            logger.error(f"❌ Error finding download buttons: {e}")
            return []
    
    def run_scraper(self, username, password, team_id="21479"):
        """Run the complete scraping process"""
        try:
            logger.info("🚀 Starting Hudl final scraper...")
            
            # Setup driver
            self.setup_driver()
            
            # Login
            if not self.login(username, password):
                return False
            
            # Navigate to SKATERS tab
            if not self.navigate_to_skaters_tab(team_id):
                return False
            
            # Wait for table and extract data
            table_data = self.wait_for_table_and_extract_data()
            if table_data:
                logger.info("✅ Successfully extracted table data!")
                logger.info(f"📊 Headers: {table_data['headers']}")
                logger.info(f"📊 Total data rows: {table_data['total_rows']}")
            else:
                logger.error("❌ Failed to extract table data")
                return False
            
            # Look for download buttons
            download_buttons = self.find_download_buttons()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Scraper failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main function to run the scraper"""
    scraper = HudlFinalScraper()
    
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
