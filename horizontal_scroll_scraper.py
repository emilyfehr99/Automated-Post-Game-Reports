#!/usr/bin/env python3
"""
Horizontal scroll scraper to get ALL 135+ metrics from the skaters table
Based on the JavaScript analysis showing overflow:auto tables
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

class HorizontalScrollScraper:
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
    
    def scroll_horizontally_to_load_all_metrics(self):
        """Scroll horizontally through the table to load all 135+ metrics"""
        try:
            logger.info("📜 Scrolling horizontally to load ALL metrics...")
            
            # Find the table container with horizontal scrolling
            # Based on JS analysis: overflow:auto;position:relative;max-height:620px
            table_containers = self.driver.find_elements(By.CSS_SELECTOR, 
                "div[style*='overflow:auto'], div[style*='overflow-x:auto'], .table, table")
            
            logger.info(f"📊 Found {len(table_containers)} potential table containers")
            
            for i, container in enumerate(table_containers):
                try:
                    logger.info(f"📊 Processing container {i+1}/{len(table_containers)}")
                    
                    # Check if this container has horizontal scroll
                    has_horizontal_scroll = self.driver.execute_script("""
                        return arguments[0].scrollWidth > arguments[0].clientWidth;
                    """, container)
                    
                    if has_horizontal_scroll:
                        logger.info(f"✅ Container {i+1} has horizontal scroll!")
                        
                        # Get initial scroll position and width
                        initial_scroll_left = self.driver.execute_script("return arguments[0].scrollLeft;", container)
                        scroll_width = self.driver.execute_script("return arguments[0].scrollWidth;", container)
                        client_width = self.driver.execute_script("return arguments[0].clientWidth;", container)
                        
                        logger.info(f"📊 Scroll info: left={initial_scroll_left}, width={scroll_width}, client={client_width}")
                        
                        # Scroll horizontally in steps to load all content
                        scroll_step = client_width // 4  # Scroll in quarters
                        current_scroll = 0
                        
                        while current_scroll < scroll_width:
                            # Scroll to current position
                            self.driver.execute_script("arguments[0].scrollLeft = arguments[1];", container, current_scroll)
                            time.sleep(1)  # Wait for content to load
                            
                            # Extract metrics from current view
                            self.extract_metrics_from_current_view()
                            
                            # Move to next position
                            current_scroll += scroll_step
                            
                            logger.info(f"📜 Scrolled to position {current_scroll}/{scroll_width}")
                        
                        # Scroll back to beginning
                        self.driver.execute_script("arguments[0].scrollLeft = 0;", container)
                        time.sleep(1)
                        
                        logger.info(f"✅ Completed horizontal scrolling for container {i+1}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing container {i+1}: {e}")
                    continue
            
            # Also try to find and scroll any table elements specifically
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
            for i, table in enumerate(tables):
                try:
                    logger.info(f"📊 Processing table {i+1}/{len(tables)}")
                    
                    # Check if table has horizontal scroll
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
                            self.extract_metrics_from_current_view()
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
    
    def extract_metrics_from_current_view(self):
        """Extract metrics from the current view"""
        try:
            # Look for table headers
            headers = self.driver.find_elements(By.CSS_SELECTOR, "th, .header, [class*='header']")
            for header in headers:
                text = header.text.strip()
                if text and len(text) > 1:
                    logger.info(f"📊 Found header: {text}")
            
            # Look for data attributes
            data_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-metric], [data-field], [data-column]")
            for element in data_elements:
                for attr in ['data-metric', 'data-field', 'data-column']:
                    value = element.get_attribute(attr)
                    if value:
                        logger.info(f"📊 Found data attribute: {attr}={value}")
            
        except Exception as e:
            logger.error(f"❌ Error extracting metrics from current view: {e}")
    
    def get_all_metrics_with_horizontal_scroll(self, team_id="21479"):
        """Get all metrics using horizontal scrolling"""
        try:
            if not self.navigate_to_skaters_tab(team_id):
                return None
            
            # Scroll horizontally to load all metrics
            self.scroll_horizontally_to_load_all_metrics()
            
            # Extract final comprehensive data
            logger.info("📊 Extracting final comprehensive data...")
            
            # Get all text content after scrolling
            page_text = self.driver.page_source
            logger.info(f"📄 Page text length after scrolling: {len(page_text)}")
            
            # Look for all possible headers
            all_headers = set()
            
            # Table headers
            headers = self.driver.find_elements(By.CSS_SELECTOR, "th, .header, [class*='header']")
            for header in headers:
                text = header.text.strip()
                if text and len(text) > 1:
                    all_headers.add(text)
            
            # Data attributes
            data_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-metric], [data-field], [data-column]")
            for element in data_elements:
                for attr in ['data-metric', 'data-field', 'data-column']:
                    value = element.get_attribute(attr)
                    if value:
                        all_headers.add(value)
            
            # Class names that might indicate metrics
            class_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='metric'], [class*='stat'], [class*='data']")
            for element in class_elements:
                class_name = element.get_attribute('class')
                if class_name:
                    parts = class_name.split()
                    for part in parts:
                        if 'metric' in part.lower() or 'stat' in part.lower():
                            all_headers.add(part)
            
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
            logger.error(f"❌ Error getting all metrics: {e}")
            return None
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

def test_horizontal_scroll_scraper():
    """Test the horizontal scroll scraper"""
    scraper = HorizontalScrollScraper()
    
    try:
        scraper.setup_driver()
        
        # Login
        username = "chaserochon777@gmail.com"
        password = "357Chaser!468"
        
        if scraper.login(username, password):
            # Get comprehensive metrics with horizontal scrolling
            result = scraper.get_all_metrics_with_horizontal_scroll("21479")
            
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
    test_horizontal_scroll_scraper()
