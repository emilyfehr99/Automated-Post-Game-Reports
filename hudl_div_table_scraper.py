#!/usr/bin/env python3
"""
Hudl scraper for div-based table structures
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

class HudlDivTableScraper:
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
    
    def extract_div_table_data(self):
        """Extract data from div-based table structure"""
        try:
            logger.info("📊 Extracting div-based table data...")
            
            # Wait for page to load
            time.sleep(10)
            
            # Find the table container
            table_container = self.driver.find_element(By.CSS_SELECTOR, ".TableContainers__TablesContainer-sc-lwtdzh-0")
            logger.info("✅ Found table container")
            
            # Get the text content to see what we have
            container_text = table_container.text
            logger.info(f"📄 Container text length: {len(container_text)}")
            logger.info(f"📄 First 500 chars: {container_text[:500]}")
            
            # Look for div elements that might represent rows
            div_rows = table_container.find_elements(By.CSS_SELECTOR, "div")
            logger.info(f"📊 Found {len(div_rows)} div elements in container")
            
            # Look for elements with specific patterns that might be rows
            potential_rows = []
            
            # Look for divs with specific classes that might be rows
            row_selectors = [
                "div[class*='row']",
                "div[class*='Row']",
                "div[class*='item']",
                "div[class*='Item']",
                "div[class*='player']",
                "div[class*='Player']",
                "div[class*='data']",
                "div[class*='Data']"
            ]
            
            for selector in row_selectors:
                elements = table_container.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"📊 Found {len(elements)} elements with selector: {selector}")
                    potential_rows.extend(elements)
            
            # If no specific row elements found, look for divs with text content
            if not potential_rows:
                logger.info("🔍 Looking for divs with text content...")
                for div in div_rows:
                    if div.text.strip() and len(div.text.strip()) > 10:  # Has meaningful text
                        potential_rows.append(div)
                        if len(potential_rows) <= 5:  # Log first 5
                            logger.info(f"  Potential row: {div.text.strip()[:100]}...")
            
            logger.info(f"📊 Found {len(potential_rows)} potential row elements")
            
            if potential_rows:
                # Extract data from potential rows
                headers = []
                data_rows = []
                
                # Try to identify headers (usually first few elements)
                for i, row in enumerate(potential_rows[:10]):  # Check first 10
                    row_text = row.text.strip()
                    if row_text:
                        if i < 3:  # First few might be headers
                            headers.append(row_text)
                        else:
                            data_rows.append(row_text)
                        logger.info(f"📊 Row {i+1}: {row_text[:100]}...")
                
                logger.info(f"✅ Extracted {len(headers)} headers and {len(data_rows)} data rows")
                
                return {
                    "headers": headers,
                    "data": data_rows,
                    "total_rows": len(data_rows),
                    "raw_text": container_text
                }
            else:
                logger.warning("⚠️  No potential row elements found")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error extracting div table data: {e}")
            return None
    
    def extract_text_based_data(self):
        """Extract data by parsing the text content"""
        try:
            logger.info("📊 Extracting text-based data...")
            
            # Find the table container
            table_container = self.driver.find_element(By.CSS_SELECTOR, ".TableContainers__TablesContainer-sc-lwtdzh-0")
            
            # Get the full text content
            full_text = table_container.text
            logger.info(f"📄 Full text length: {len(full_text)}")
            
            # Split by lines and process
            lines = full_text.split('\n')
            logger.info(f"📊 Found {len(lines)} lines of text")
            
            # Filter out empty lines and very short lines
            meaningful_lines = [line.strip() for line in lines if line.strip() and len(line.strip()) > 2]
            logger.info(f"📊 Found {len(meaningful_lines)} meaningful lines")
            
            # Look for header patterns
            headers = []
            data_rows = []
            
            # Common header patterns
            header_keywords = ['PLAYER', 'POS', 'TOI', 'GP', 'SHIFTS', 'G', 'A1', 'A2', 'A', 'P', '+/-']
            
            for i, line in enumerate(meaningful_lines):
                # Check if this line contains header keywords
                if any(keyword in line.upper() for keyword in header_keywords):
                    if i < 5:  # Headers are usually at the top
                        headers.append(line)
                        logger.info(f"📝 Header: {line}")
                else:
                    # This might be a data row
                    data_rows.append(line)
                    if len(data_rows) <= 10:  # Log first 10 data rows
                        logger.info(f"📊 Data: {line}")
            
            logger.info(f"✅ Extracted {len(headers)} headers and {len(data_rows)} data rows")
            
            return {
                "headers": headers,
                "data": data_rows,
                "total_rows": len(data_rows),
                "full_text": full_text
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting text-based data: {e}")
            return None
    
    def run_scraper(self, username, password, team_id="21479"):
        """Run the complete scraping process"""
        try:
            logger.info("🚀 Starting Hudl div table scraper...")
            
            # Setup driver
            self.setup_driver()
            
            # Login
            if not self.login(username, password):
                return False
            
            # Navigate to SKATERS tab
            if not self.navigate_to_skaters_tab(team_id):
                return False
            
            # Try div-based extraction first
            table_data = self.extract_div_table_data()
            if not table_data:
                # Fallback to text-based extraction
                logger.info("🔄 Trying text-based extraction...")
                table_data = self.extract_text_based_data()
            
            if table_data:
                logger.info("✅ Successfully extracted table data!")
                logger.info(f"📊 Headers: {table_data['headers']}")
                logger.info(f"📊 Total data rows: {table_data['total_rows']}")
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
    scraper = HudlDivTableScraper()
    
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
