#!/usr/bin/env python3
"""
Comprehensive metrics scraper that tries to access ALL 136+ metrics
by exploring different sections and tabs of the Hudl interface
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

class ComprehensiveMetricsScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.all_metrics = set()
        self.all_players = []
        
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
    
    def explore_all_sections(self, team_id="21479"):
        """Explore all possible sections to find comprehensive metrics"""
        try:
            logger.info(f"🔍 Exploring ALL sections for team {team_id}...")
            
            # Go to team page
            team_url = f"https://app.hudl.com/instat/hockey/teams/{team_id}"
            self.driver.get(team_url)
            time.sleep(5)
            
            # Find all possible tabs/sections
            tabs_to_explore = [
                "SKATERS", "Skaters", "skaters",
                "GOALIES", "Goalies", "goalies", 
                "LINES", "Lines", "lines",
                "SHOTS", "Shots", "shots",
                "FACEOFFS", "Faceoffs", "faceoffs",
                "OVERVIEW", "Overview", "overview",
                "GAMES", "Games", "games",
                "CAREER", "Career", "career",
                "ANALYTICS", "Analytics", "analytics",
                "ADVANCED", "Advanced", "advanced"
            ]
            
            for tab_text in tabs_to_explore:
                try:
                    logger.info(f"🔍 Exploring tab: {tab_text}")
                    
                    # Try different selectors for the tab
                    tab_selectors = [
                        f"//a[contains(text(), '{tab_text}')]",
                        f"//button[contains(text(), '{tab_text}')]",
                        f"//div[contains(text(), '{tab_text}')]",
                        f"//span[contains(text(), '{tab_text}')]",
                        f"[data-tab='{tab_text.lower()}']",
                        f"[data-section='{tab_text.lower()}']"
                    ]
                    
                    tab_found = False
                    for selector in tab_selectors:
                        try:
                            tab_element = self.driver.find_element(By.XPATH, selector)
                            if tab_element.is_displayed() and tab_element.is_enabled():
                                tab_element.click()
                                time.sleep(3)
                                tab_found = True
                                logger.info(f"✅ Clicked tab: {tab_text}")
                                break
                        except:
                            continue
                    
                    if tab_found:
                        # Scroll to load all data
                        self.scroll_comprehensively()
                        
                        # Extract metrics from this section
                        self.extract_metrics_from_section(tab_text)
                        
                        # Try to find sub-tabs or additional sections
                        self.explore_sub_sections()
                        
                except Exception as e:
                    logger.info(f"⚠️ Could not explore tab {tab_text}: {e}")
                    continue
            
            # Try to find export/download buttons that might reveal more data
            self.try_export_buttons()
            
            # Try to find filter options that might show more metrics
            self.try_filter_options()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exploring sections: {e}")
            return False
    
    def scroll_comprehensively(self):
        """Comprehensive scrolling to load all possible data"""
        try:
            logger.info("📜 Comprehensive scrolling...")
            
            # Vertical scrolling
            for i in range(10):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
            
            # Horizontal scrolling for tables
            try:
                tables = self.driver.find_elements(By.CSS_SELECTOR, "table, .table, [class*='table']")
                for table in tables:
                    # Scroll horizontally
                    self.driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollWidth;", table)
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].scrollLeft = 0;", table)
                    time.sleep(1)
            except:
                pass
            
            # Try to find and click "Show All" or "View All" buttons
            show_all_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Show All') or contains(text(), 'View All') or contains(text(), 'Load More')]")
            for button in show_all_buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        time.sleep(2)
                        logger.info("📜 Clicked show all button")
                except:
                    pass
            
        except Exception as e:
            logger.error(f"❌ Scrolling error: {e}")
    
    def extract_metrics_from_section(self, section_name):
        """Extract metrics from current section"""
        try:
            logger.info(f"📊 Extracting metrics from {section_name}...")
            
            # Get all text content
            page_text = self.driver.page_source
            
            # Look for table headers
            header_elements = self.driver.find_elements(By.CSS_SELECTOR, "th, .header, [class*='header'], [class*='column']")
            for element in header_elements:
                text = element.text.strip()
                if text and len(text) > 1 and text not in ['', 'PLAYER', 'POS', 'TOI']:
                    self.all_metrics.add(text)
            
            # Look for data attributes that might contain metric names
            data_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-metric], [data-field], [data-column]")
            for element in data_elements:
                for attr in ['data-metric', 'data-field', 'data-column']:
                    value = element.get_attribute(attr)
                    if value:
                        self.all_metrics.add(value)
            
            # Look for class names that might indicate metrics
            class_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='metric'], [class*='stat'], [class*='data']")
            for element in class_elements:
                class_name = element.get_attribute('class')
                if class_name:
                    parts = class_name.split()
                    for part in parts:
                        if 'metric' in part.lower() or 'stat' in part.lower():
                            self.all_metrics.add(part)
            
            logger.info(f"📊 Found {len(self.all_metrics)} total metrics so far")
            
        except Exception as e:
            logger.error(f"❌ Error extracting metrics from {section_name}: {e}")
    
    def explore_sub_sections(self):
        """Explore sub-sections within current section"""
        try:
            # Look for dropdown menus or sub-tabs
            dropdowns = self.driver.find_elements(By.CSS_SELECTOR, "select, .dropdown, [class*='dropdown']")
            for dropdown in dropdowns:
                try:
                    dropdown.click()
                    time.sleep(1)
                    # Try to select different options
                    options = dropdown.find_elements(By.CSS_SELECTOR, "option, .option, [class*='option']")
                    for option in options:
                        try:
                            option.click()
                            time.sleep(2)
                            self.extract_metrics_from_section("sub-section")
                        except:
                            continue
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error exploring sub-sections: {e}")
    
    def try_export_buttons(self):
        """Try to find and use export buttons"""
        try:
            logger.info("📤 Looking for export buttons...")
            
            export_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Export') or contains(text(), 'Download') or contains(text(), 'CSV')]")
            for button in export_buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        time.sleep(2)
                        logger.info("📤 Clicked export button")
                        
                        # Look for metric selection options in export modal
                        self.extract_metrics_from_export_modal()
                        
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error with export buttons: {e}")
    
    def extract_metrics_from_export_modal(self):
        """Extract metrics from export modal if it opens"""
        try:
            # Look for checkboxes or options in export modal
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'], .checkbox, [class*='checkbox']")
            for checkbox in checkboxes:
                try:
                    label = checkbox.find_element(By.XPATH, "following-sibling::*[1] | preceding-sibling::*[1]")
                    text = label.text.strip()
                    if text:
                        self.all_metrics.add(text)
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error extracting from export modal: {e}")
    
    def try_filter_options(self):
        """Try to find filter options that might reveal more metrics"""
        try:
            logger.info("🔍 Looking for filter options...")
            
            filter_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Filter') or contains(text(), 'Options') or contains(text(), 'Settings')]")
            for button in filter_buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        time.sleep(2)
                        self.extract_metrics_from_section("filter")
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error with filter options: {e}")
    
    def get_comprehensive_metrics(self, team_id="21479"):
        """Get comprehensive metrics for team"""
        try:
            if not self.explore_all_sections(team_id):
                return None
            
            logger.info(f"🎉 COMPREHENSIVE METRICS FOUND: {len(self.all_metrics)}")
            logger.info("=" * 80)
            for i, metric in enumerate(sorted(self.all_metrics), 1):
                logger.info(f"  {i:3d}. {metric}")
            logger.info("=" * 80)
            
            return {
                'total_metrics': len(self.all_metrics),
                'metrics': sorted(list(self.all_metrics))
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting comprehensive metrics: {e}")
            return None
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

def test_comprehensive_scraper():
    """Test the comprehensive scraper"""
    scraper = ComprehensiveMetricsScraper()
    
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
    test_comprehensive_scraper()
