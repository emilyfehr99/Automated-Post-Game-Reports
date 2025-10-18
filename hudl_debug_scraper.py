#!/usr/bin/env python3
"""
Hudl debug scraper - non-headless to see what's happening
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

class HudlDebugScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Set up Chrome driver in non-headless mode for debugging"""
        chrome_options = Options()
        # Don't run headless so we can see what's happening
        # chrome_options.add_argument("--headless")
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
    
    def debug_page_content(self):
        """Debug what's on the page"""
        try:
            logger.info("🔍 Debugging page content...")
            
            # Get page source length
            page_source = self.driver.page_source
            logger.info(f"📄 Page source length: {len(page_source)}")
            
            # Look for any table elements
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
            logger.info(f"📋 Found {len(tables)} table elements")
            
            # Look for divs with table-related classes
            table_divs = self.driver.find_elements(By.CSS_SELECTOR, "[class*='table'], [class*='Table']")
            logger.info(f"📋 Found {len(table_divs)} table-related divs")
            
            # Look for the specific table container
            specific_containers = self.driver.find_elements(By.CSS_SELECTOR, "[class*='TableContainer']")
            logger.info(f"📋 Found {len(specific_containers)} TableContainer elements")
            
            for i, container in enumerate(specific_containers[:3]):
                try:
                    class_name = container.get_attribute("class")
                    text_content = container.text.strip()[:100]
                    logger.info(f"  Container {i+1}: class='{class_name}', text='{text_content}...'")
                except:
                    logger.info(f"  Container {i+1}: [unable to get details]")
            
            # Look for any elements with data
            data_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='data'], [class*='Data']")
            logger.info(f"📊 Found {len(data_elements)} data-related elements")
            
            # Check if there are any loading indicators
            loading_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='loading'], [class*='Loading'], [class*='spinner']")
            logger.info(f"⏳ Found {len(loading_elements)} loading elements")
            
            # Check for any JavaScript errors in console
            logs = self.driver.get_log('browser')
            if logs:
                logger.info(f"🔍 Found {len(logs)} browser console logs")
                for log in logs[-5:]:  # Show last 5 logs
                    logger.info(f"  {log['level']}: {log['message']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error debugging page: {e}")
            return False
    
    def wait_for_data_and_extract(self):
        """Wait for data to load and extract it"""
        try:
            logger.info("📊 Waiting for data to load...")
            
            # Wait longer for dynamic content
            time.sleep(15)
            
            # Debug page content
            self.debug_page_content()
            
            # Try to wait for any table rows to appear
            try:
                self.wait.until(
                    lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "tr")) > 0
                )
                logger.info("✅ Table rows found!")
            except:
                logger.warning("⚠️  No table rows found after waiting")
            
            # Look for the table container
            try:
                table_container = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".TableContainers__TablesContainer-sc-lwtdzh-0"))
                )
                logger.info("✅ Found table container")
                
                # Extract table data
                rows = table_container.find_elements(By.CSS_SELECTOR, "tr")
                logger.info(f"📊 Found {len(rows)} table rows in container")
                
                if rows:
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
                            if i <= 5:  # Log first 5 rows
                                logger.info(f"📊 Row {i}: {row_data}")
                    
                    logger.info(f"✅ Extracted {len(data_rows)} data rows")
                    
                    return {
                        "headers": headers,
                        "data": data_rows,
                        "total_rows": len(data_rows)
                    }
                else:
                    logger.warning("⚠️  No rows found in table container")
                    return None
                    
            except:
                logger.error("❌ Table container not found")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error extracting data: {e}")
            return None
    
    def run_scraper(self, username, password, team_id="21479"):
        """Run the complete scraping process"""
        try:
            logger.info("🚀 Starting Hudl debug scraper...")
            
            # Setup driver
            self.setup_driver()
            
            # Login
            if not self.login(username, password):
                return False
            
            # Navigate to SKATERS tab
            if not self.navigate_to_skaters_tab(team_id):
                return False
            
            # Wait for data and extract
            table_data = self.wait_for_data_and_extract()
            if table_data:
                logger.info("✅ Successfully extracted table data!")
                logger.info(f"📊 Headers: {table_data['headers']}")
                logger.info(f"📊 Total data rows: {table_data['total_rows']}")
            else:
                logger.error("❌ Failed to extract table data")
            
            # Keep browser open for inspection
            logger.info("🔄 Browser will stay open for inspection...")
            input("Press Enter to close browser...")
            
            return table_data is not None
            
        except Exception as e:
            logger.error(f"❌ Scraper failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main function to run the scraper"""
    scraper = HudlDebugScraper()
    
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
