#!/usr/bin/env python3
"""
Hudl scraper using the proven working login method
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

class HudlProvenScraper:
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
        
        self.wait = WebDriverWait(self.driver, 20)
        
    def login(self, username, password):
        """Login using the proven method"""
        try:
            logger.info("🔐 Logging into Hudl Instat...")
            
            # Go to Hudl Instat
            self.driver.get("https://app.hudl.com/instat/hockey")
            time.sleep(5)
            
            logger.info(f"📍 Current URL: {self.driver.current_url}")
            logger.info(f"📄 Page title: {self.driver.title}")
            
            # Find username field
            username_field = self.driver.find_element(By.ID, "username")
            logger.info("✅ Found username field")
            
            # Fill in username
            username_field.clear()
            username_field.send_keys(username)
            logger.info(f"✅ Entered username: {username}")
            
            # Find and click Continue button
            continue_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'][name='action'][value='default']")
            logger.info("✅ Found Continue button")
            
            # Click Continue
            continue_button.click()
            time.sleep(5)
            
            logger.info(f"📍 After Continue URL: {self.driver.current_url}")
            
            # Find password field
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            logger.info("✅ Found password field")
            
            # Fill in password
            password_field.clear()
            password_field.send_keys(password)
            logger.info("✅ Entered password")
            
            # Find and click submit button
            submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")
            logger.info(f"Found {len(submit_buttons)} submit buttons")
            
            if submit_buttons:
                submit_button = submit_buttons[0]
                logger.info(f"Clicking submit button: {submit_button.text}")
                submit_button.click()
                time.sleep(10)
                
                logger.info(f"📍 After submit URL: {self.driver.current_url}")
                
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
            
            logger.info(f"📍 Team URL: {self.driver.current_url}")
            
            # Look for SKATERS tab
            skaters_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='skaters']")
            logger.info(f"Found {len(skaters_links)} skaters links")
            
            for i, link in enumerate(skaters_links):
                logger.info(f"  {i+1}. {link.text} -> {link.get_attribute('href')}")
            
            if skaters_links:
                logger.info("Clicking SKATERS tab...")
                skaters_links[0].click()
                time.sleep(5)
                
                logger.info(f"📍 After click URL: {self.driver.current_url}")
                return True
            else:
                logger.error("❌ No SKATERS links found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            return False
    
    def extract_skaters_data(self):
        """Extract data from SKATERS table"""
        try:
            logger.info("📊 Extracting SKATERS data...")
            
            # Wait for page to load and dynamic content
            logger.info("⏳ Waiting for dynamic content to load...")
            time.sleep(10)  # Increased wait time
            
            # Try to wait for table rows to appear
            try:
                self.wait.until(
                    lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".TableContainers__TablesContainer-sc-lwtdzh-0 tr")) > 0
                )
                logger.info("✅ Table rows loaded!")
            except:
                logger.warning("⚠️  Timeout waiting for table rows, continuing...")
            
            # Look for the table container
            try:
                table_container = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".TableContainers__TablesContainer-sc-lwtdzh-0"))
                )
                logger.info("✅ Found table container")
            except:
                logger.warning("⚠️  Table container not found, looking for any tables...")
                
                # Look for any tables
                tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
                logger.info(f"Found {len(tables)} tables")
                
                if not tables:
                    logger.error("❌ No tables found")
                    return None
                
                # Use the first table
                table_container = tables[0]
                logger.info("Using first table found")
            
            # Extract table data
            rows = table_container.find_elements(By.CSS_SELECTOR, "tr")
            logger.info(f"📊 Found {len(rows)} table rows")
            
            if not rows:
                logger.warning("⚠️  No table rows found")
                return None
            
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
            logger.error(f"❌ Error extracting data: {e}")
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
            logger.info("🚀 Starting Hudl proven scraper...")
            
            # Setup driver
            self.setup_driver()
            
            # Login
            if not self.login(username, password):
                return False
            
            # Navigate to SKATERS tab
            if not self.navigate_to_skaters_tab(team_id):
                return False
            
            # Extract data
            table_data = self.extract_skaters_data()
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
    scraper = HudlProvenScraper()
    
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
