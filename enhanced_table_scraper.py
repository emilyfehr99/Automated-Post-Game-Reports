#!/usr/bin/env python3
"""
Enhanced table scraper that targets the specific table structure
with columnheader elements and implements modal checkbox selection
"""

import time
import logging
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

class EnhancedTableScraper:
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
            self.driver.get("https://app.hudl.com/instat/hockey/")
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
    
    def navigate_to_skaters_tab(self, team_id="21479"):
        """Navigate to SKATERS tab for the team"""
        try:
            logger.info(f"🏒 Navigating to SKATERS tab for team {team_id}...")
            
            # Go to team page
            team_url = f"https://app.hudl.com/instat/hockey/teams/{team_id}"
            self.driver.get(team_url)
            time.sleep(5)
            
            # Find and click on SKATERS tab
            skaters_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'SKATERS') or contains(text(), 'Skaters')]")))
            skaters_tab.click()
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Navigation error: {e}")
            return False
    
    def find_and_click_export_button(self):
        """Find and click the export button to open the modal"""
        try:
            logger.info("📤 Looking for export button...")
            
            # Look for export buttons with various selectors
            export_selectors = [
                "button[title*='Export']",
                "button[aria-label*='Export']",
                "button[data-testid*='export']",
                "button[class*='export']",
                "a[href*='export']",
                "button:contains('Export')",
                "a:contains('Export')",
                "[data-lexic='13445']",  # From JS analysis
                "button[data-lexic='13445']"
            ]
            
            for selector in export_selectors:
                try:
                    if ":contains" in selector:
                        # Use XPath for text-based selectors
                        xpath = f"//button[contains(text(), 'Export')] | //a[contains(text(), 'Export')]"
                        elements = self.driver.find_elements(By.XPATH, xpath)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            logger.info(f"✅ Found export button: {selector}")
                            element.click()
                            time.sleep(2)
                            return True
                            
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Also try to find by SVG icon (from JS analysis)
            svg_elements = self.driver.find_elements(By.CSS_SELECTOR, "svg, [class*='svg'], [data-icon*='export']")
            for element in svg_elements:
                try:
                    parent = element.find_element(By.XPATH, "..")
                    if parent.tag_name in ['button', 'a'] and parent.is_displayed():
                        logger.info("✅ Found export button by SVG icon")
                        parent.click()
                        time.sleep(2)
                        return True
                except:
                    continue
            
            logger.warning("⚠️ No export button found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error finding export button: {e}")
            return False
    
    def select_all_checkboxes_in_modal(self):
        """Select all checkboxes in the export modal"""
        try:
            logger.info("☑️ Looking for checkboxes in modal...")
            
            # Wait for modal to appear
            time.sleep(3)
            
            # Look for checkboxes in the modal
            checkbox_selectors = [
                "input[type='checkbox']",
                ".checkbox input",
                "[class*='checkbox'] input",
                "input[class*='checkbox']",
                "input[data-testid*='checkbox']",
                "input[aria-label*='checkbox']"
            ]
            
            checkboxes_found = 0
            checkboxes_checked = 0
            
            for selector in checkbox_selectors:
                try:
                    checkboxes = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for checkbox in checkboxes:
                        if checkbox.is_displayed():
                            checkboxes_found += 1
                            if not checkbox.is_selected():
                                checkbox.click()
                                checkboxes_checked += 1
                                logger.info(f"☑️ Checked checkbox: {checkbox.get_attribute('name') or 'unnamed'}")
                except Exception as e:
                    logger.debug(f"Checkbox selector {selector} failed: {e}")
                    continue
            
            logger.info(f"✅ Found {checkboxes_found} checkboxes, checked {checkboxes_checked}")
            return checkboxes_found > 0
            
        except Exception as e:
            logger.error(f"❌ Error selecting checkboxes: {e}")
            return False
    
    def scroll_table_horizontally(self):
        """Scroll the table horizontally to load all columns"""
        try:
            logger.info("📜 Scrolling table horizontally...")
            
            # Find the table scroll wrapper (from JS analysis)
            table_wrappers = self.driver.find_elements(By.CSS_SELECTOR, 
                "div[class*='TableScrollWrapper'], div[class*='Table__TableScrollWrapper']")
            
            logger.info(f"📊 Found {len(table_wrappers)} table scroll wrappers")
            
            for i, wrapper in enumerate(table_wrappers):
                try:
                    logger.info(f"📊 Processing wrapper {i+1}/{len(table_wrappers)}")
                    
                    # Check if wrapper has horizontal scroll
                    has_horizontal_scroll = self.driver.execute_script("""
                        return arguments[0].scrollWidth > arguments[0].clientWidth;
                    """, wrapper)
                    
                    if has_horizontal_scroll:
                        logger.info(f"✅ Wrapper {i+1} has horizontal scroll!")
                        
                        # Get scroll dimensions
                        scroll_width = self.driver.execute_script("return arguments[0].scrollWidth;", wrapper)
                        client_width = self.driver.execute_script("return arguments[0].clientWidth;", wrapper)
                        
                        logger.info(f"📊 Scroll width: {scroll_width}, Client width: {client_width}")
                        
                        # Scroll horizontally in steps
                        scroll_step = client_width // 4
                        current_scroll = 0
                        
                        while current_scroll < scroll_width:
                            # Scroll to current position
                            self.driver.execute_script("arguments[0].scrollLeft = arguments[1];", wrapper, current_scroll)
                            time.sleep(1)  # Wait for content to load
                            
                            logger.info(f"📜 Scrolled to position {current_scroll}/{scroll_width}")
                            
                            # Move to next position
                            current_scroll += scroll_step
                        
                        # Scroll back to beginning
                        self.driver.execute_script("arguments[0].scrollLeft = 0;", wrapper)
                        time.sleep(1)
                        
                        logger.info(f"✅ Completed horizontal scrolling for wrapper {i+1}")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing wrapper {i+1}: {e}")
                    continue
            
            # Also try to find tables with columnheader elements
            tables_with_headers = self.driver.find_elements(By.CSS_SELECTOR, 
                "table, div[role='table'], div[class*='table']")
            
            for i, table in enumerate(tables_with_headers):
                try:
                    # Check if table has columnheader elements
                    headers = table.find_elements(By.CSS_SELECTOR, "[role='columnheader']")
                    if headers:
                        logger.info(f"📊 Table {i+1} has {len(headers)} column headers")
                        
                        # Check for horizontal scroll
                        has_horizontal_scroll = self.driver.execute_script("""
                            return arguments[0].scrollWidth > arguments[0].clientWidth;
                        """, table)
                        
                        if has_horizontal_scroll:
                            logger.info(f"✅ Table {i+1} has horizontal scroll!")
                            
                            # Scroll through the table
                            scroll_width = self.driver.execute_script("return arguments[0].scrollWidth;", table)
                            client_width = self.driver.execute_script("return arguments[0].clientWidth;", table)
                            
                            scroll_step = client_width // 4
                            current_scroll = 0
                            
                            while current_scroll < scroll_width:
                                self.driver.execute_script("arguments[0].scrollLeft = arguments[1];", table, current_scroll)
                                time.sleep(1)
                                current_scroll += scroll_step
                                
                            # Reset scroll position
                            self.driver.execute_script("arguments[0].scrollLeft = 0;", table)
                            time.sleep(1)
                            
                except Exception as e:
                    logger.error(f"❌ Error processing table {i+1}: {e}")
                    continue
            
            logger.info("✅ Horizontal scrolling complete!")
            
        except Exception as e:
            logger.error(f"❌ Error in horizontal scrolling: {e}")
    
    def extract_all_metrics_after_scrolling(self):
        """Extract all metrics after scrolling and modal interaction"""
        try:
            logger.info("📊 Extracting all metrics after scrolling...")
            
            # Get all column headers
            all_headers = set()
            
            # Look for columnheader elements
            column_headers = self.driver.find_elements(By.CSS_SELECTOR, "[role='columnheader']")
            for header in column_headers:
                text = header.text.strip()
                if text and len(text) > 1:
                    all_headers.add(text)
            
            # Look for table headers
            table_headers = self.driver.find_elements(By.CSS_SELECTOR, "th, .header, [class*='header']")
            for header in table_headers:
                text = header.text.strip()
                if text and len(text) > 1:
                    all_headers.add(text)
            
            # Look for data attributes
            data_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-metric], [data-field], [data-column]")
            for element in data_elements:
                for attr in ['data-metric', 'data-field', 'data-column']:
                    value = element.get_attribute(attr)
                    if value:
                        all_headers.add(value)
            
            logger.info(f"🎉 COMPREHENSIVE METRICS FOUND: {len(all_headers)}")
            logger.info("=" * 80)
            for i, metric in enumerate(sorted(all_headers), 1):
                logger.info(f"  {i:3d}. {metric}")
            logger.info("=" * 80)
            
            return {
                'total_metrics': len(all_headers),
                'metrics': sorted(list(all_headers))
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting metrics: {e}")
            return None
    
    def get_comprehensive_metrics(self, team_id="21479"):
        """Get comprehensive metrics with modal and scrolling"""
        try:
            if not self.navigate_to_skaters_tab(team_id):
                return None
            
            # Try to find and click export button
            if self.find_and_click_export_button():
                # Select all checkboxes in modal
                self.select_all_checkboxes_in_modal()
                
                # Close modal (try to find OK or Apply button)
                try:
                    ok_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'OK') or contains(text(), 'Apply') or contains(text(), 'Confirm')]")
                    for button in ok_buttons:
                        if button.is_displayed():
                            button.click()
                            time.sleep(2)
                            break
                except:
                    pass
            
            # Scroll table horizontally
            self.scroll_table_horizontally()
            
            # Extract all metrics
            return self.extract_all_metrics_after_scrolling()
            
        except Exception as e:
            logger.error(f"❌ Error getting comprehensive metrics: {e}")
            return None
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

def test_enhanced_table_scraper():
    """Test the enhanced table scraper"""
    scraper = EnhancedTableScraper()
    
    try:
        scraper.setup_driver()
        
        # Login
        username = "chaserochon777@gmail.com"
        password = "357Chaser!468"
        
        if scraper.login(username, password):
            # Get comprehensive metrics
            result = scraper.get_comprehensive_metrics("21479")
            
            if result:
                print(f"✅ Success! Found {result['total_metrics']} comprehensive metrics")
                print(f"📊 Metrics: {result['metrics']}")
            else:
                print("❌ Failed to get comprehensive metrics")
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    test_enhanced_table_scraper()
