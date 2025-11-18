#!/usr/bin/env python3
"""
Enhanced scroll scraper using specific scroll attributes from jsviewer.js.txt analysis
Targets TableScrollWrapper and uses proper scroll state management
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

class EnhancedScrollScraper:
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
    
    def find_table_scroll_wrapper(self):
        """Find the specific TableScrollWrapper component"""
        try:
            logger.info("🔍 Looking for TableScrollWrapper components...")
            
            # Try multiple selectors for TableScrollWrapper
            wrapper_selectors = [
                "div[class*='TableScrollWrapper']",
                "div[class*='Table__TableScrollWrapper']",
                "div[class*='TableContainers__TableScrollWrapper']",
                "div[class*='TableScrollWrapper']",
                "div[class*='table-scroll']",
                "div[class*='scroll-wrapper']",
                "div[class*='table-wrapper']"
            ]
            
            for selector in wrapper_selectors:
                try:
                    wrappers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if wrappers:
                        logger.info(f"✅ Found {len(wrappers)} TableScrollWrapper(s) with selector: {selector}")
                        return wrappers
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Also try to find by role or data attributes
            role_wrappers = self.driver.find_elements(By.CSS_SELECTOR, "div[role='table'], div[role='grid']")
            if role_wrappers:
                logger.info(f"✅ Found {len(role_wrappers)} table/grid elements by role")
                return role_wrappers
            
            logger.warning("⚠️ No TableScrollWrapper found")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error finding TableScrollWrapper: {e}")
            return []
    
    def get_scroll_state(self, element):
        """Get scroll state properties from element"""
        try:
            scroll_state = self.driver.execute_script("""
                return {
                    scrollLeft: arguments[0].scrollLeft,
                    scrollTop: arguments[0].scrollTop,
                    scrollWidth: arguments[0].scrollWidth,
                    scrollHeight: arguments[0].scrollHeight,
                    clientWidth: arguments[0].clientWidth,
                    clientHeight: arguments[0].clientHeight,
                    hasHorizontalScroll: arguments[0].scrollWidth > arguments[0].clientWidth,
                    hasVerticalScroll: arguments[0].scrollHeight > arguments[0].clientHeight
                };
            """, element)
            
            logger.info(f"📊 Scroll State: {scroll_state}")
            return scroll_state
            
        except Exception as e:
            logger.error(f"❌ Error getting scroll state: {e}")
            return None
    
    def scroll_with_state_management(self, element):
        """Scroll using proper state management like the JavaScript implementation"""
        try:
            logger.info("📜 Starting enhanced scroll with state management...")
            
            # Get initial scroll state
            initial_state = self.get_scroll_state(element)
            if not initial_state:
                return False
            
            if not initial_state['hasHorizontalScroll']:
                logger.info("⚠️ No horizontal scroll available")
                return False
            
            # Set up scroll state tracking
            scroll_offset = initial_state['scrollLeft']
            scroll_direction = "forward"
            is_scrolling = True
            scroll_update_was_requested = True
            
            logger.info(f"📊 Initial scroll state: offset={scroll_offset}, direction={scroll_direction}")
            
            # Scroll in steps with proper state management
            scroll_width = initial_state['scrollWidth']
            client_width = initial_state['clientWidth']
            max_scroll = scroll_width - client_width
            
            logger.info(f"📊 Scroll dimensions: width={scroll_width}, client={client_width}, max={max_scroll}")
            
            # Scroll step by step
            step_size = client_width // 4
            current_offset = 0
            
            while current_offset < max_scroll:
                # Update scroll state
                scroll_offset = current_offset
                scroll_direction = "forward" if current_offset > scroll_offset else "backward"
                
                # Set scroll position
                self.driver.execute_script("arguments[0].scrollLeft = arguments[1];", element, current_offset)
                
                # Wait for scroll to complete
                time.sleep(1)
                
                # Check if scroll was successful
                new_state = self.get_scroll_state(element)
                if new_state and new_state['scrollLeft'] == current_offset:
                    logger.info(f"✅ Scrolled to position {current_offset}/{max_scroll}")
                else:
                    logger.warning(f"⚠️ Scroll to {current_offset} may not have completed")
                
                # Move to next position
                current_offset += step_size
                
                # Update scroll state
                scroll_update_was_requested = False
                is_scrolling = False
                
                # Small delay to allow content to load
                time.sleep(0.5)
            
            # Scroll back to beginning
            self.driver.execute_script("arguments[0].scrollLeft = 0;", element)
            time.sleep(1)
            
            logger.info("✅ Enhanced scroll with state management complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced scroll: {e}")
            return False
    
    def scroll_with_debouncing(self, element):
        """Scroll using debounced approach like the JavaScript implementation"""
        try:
            logger.info("📜 Starting debounced scroll...")
            
            # Get scroll dimensions
            scroll_state = self.get_scroll_state(element)
            if not scroll_state or not scroll_state['hasHorizontalScroll']:
                return False
            
            scroll_width = scroll_state['scrollWidth']
            client_width = scroll_state['clientWidth']
            max_scroll = scroll_width - client_width
            
            # Debounced scroll function
            def debounced_scroll(offset):
                self.driver.execute_script("arguments[0].scrollLeft = arguments[1];", element, offset)
                time.sleep(0.1)  # Debounce delay
            
            # Scroll in smaller steps with debouncing
            step_size = client_width // 8
            current_offset = 0
            
            while current_offset < max_scroll:
                debounced_scroll(current_offset)
                current_offset += step_size
                time.sleep(0.2)  # Additional debounce
            
            # Reset to beginning
            debounced_scroll(0)
            time.sleep(1)
            
            logger.info("✅ Debounced scroll complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in debounced scroll: {e}")
            return False
    
    def scroll_with_animation_listener(self, element):
        """Scroll using animation listener approach"""
        try:
            logger.info("📜 Starting scroll with animation listener...")
            
            # Set up animation listener
            self.driver.execute_script("""
                arguments[0].__scrollAnimationListener = function(e) {
                    console.log('Scroll animation event:', e);
                };
                arguments[0].addEventListener('scroll', arguments[0].__scrollAnimationListener, true);
            """, element)
            
            # Get scroll dimensions
            scroll_state = self.get_scroll_state(element)
            if not scroll_state or not scroll_state['hasHorizontalScroll']:
                return False
            
            scroll_width = scroll_state['scrollWidth']
            client_width = scroll_state['clientWidth']
            max_scroll = scroll_width - client_width
            
            # Scroll with animation
            step_size = client_width // 6
            current_offset = 0
            
            while current_offset < max_scroll:
                # Smooth scroll with animation
                self.driver.execute_script("""
                    arguments[0].scrollTo({
                        left: arguments[1],
                        behavior: 'smooth'
                    });
                """, element, current_offset)
                
                time.sleep(1.5)  # Wait for animation
                current_offset += step_size
            
            # Reset with animation
            self.driver.execute_script("""
                arguments[0].scrollTo({
                    left: 0,
                    behavior: 'smooth'
                });
            """, element)
            
            time.sleep(2)
            
            # Clean up animation listener
            self.driver.execute_script("""
                if (arguments[0].__scrollAnimationListener) {
                    arguments[0].removeEventListener('scroll', arguments[0].__scrollAnimationListener, true);
                    delete arguments[0].__scrollAnimationListener;
                }
            """, element)
            
            logger.info("✅ Animation listener scroll complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in animation listener scroll: {e}")
            return False
    
    def scroll_with_resize_triggers(self, element):
        """Scroll using resize triggers approach"""
        try:
            logger.info("📜 Starting scroll with resize triggers...")
            
            # Set up resize triggers
            self.driver.execute_script("""
                if (!arguments[0].__resizeTriggers) {
                    arguments[0].__resizeTriggers = document.createElement('div');
                    arguments[0].__resizeTriggers.className = 'resize-triggers';
                    
                    var expandTrigger = document.createElement('div');
                    expandTrigger.className = 'expand-trigger';
                    expandTrigger.appendChild(document.createElement('div'));
                    
                    var contractTrigger = document.createElement('div');
                    contractTrigger.className = 'contract-trigger';
                    
                    arguments[0].__resizeTriggers.appendChild(expandTrigger);
                    arguments[0].__resizeTriggers.appendChild(contractTrigger);
                    arguments[0].appendChild(arguments[0].__resizeTriggers);
                }
            """, element)
            
            # Get scroll dimensions
            scroll_state = self.get_scroll_state(element)
            if not scroll_state or not scroll_state['hasHorizontalScroll']:
                return False
            
            scroll_width = scroll_state['scrollWidth']
            client_width = scroll_state['clientWidth']
            max_scroll = scroll_width - client_width
            
            # Scroll with resize trigger monitoring
            step_size = client_width // 5
            current_offset = 0
            
            while current_offset < max_scroll:
                # Scroll and monitor resize
                self.driver.execute_script("""
                    arguments[0].scrollLeft = arguments[1];
                    // Trigger resize event
                    if (arguments[0].__resizeTriggers) {
                        arguments[0].__resizeTriggers.dispatchEvent(new Event('resize'));
                    }
                """, element, current_offset)
                
                time.sleep(1)
                current_offset += step_size
            
            # Reset
            self.driver.execute_script("arguments[0].scrollLeft = 0;", element)
            time.sleep(1)
            
            logger.info("✅ Resize triggers scroll complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in resize triggers scroll: {e}")
            return False
    
    def extract_all_metrics_after_scrolling(self):
        """Extract ALL metrics after scrolling"""
        try:
            logger.info("📊 Extracting ALL metrics after enhanced scrolling...")
            
            all_metrics = set()
            
            # Get all column headers
            column_headers = self.driver.find_elements(By.CSS_SELECTOR, "[role='columnheader']")
            for header in column_headers:
                text = header.text.strip()
                if text and len(text) > 1:
                    all_metrics.add(text)
            
            # Get all table headers
            table_headers = self.driver.find_elements(By.CSS_SELECTOR, "th, .header, [class*='header']")
            for header in table_headers:
                text = header.text.strip()
                if text and len(text) > 1:
                    all_metrics.add(text)
            
            # Get all data attributes
            data_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-metric], [data-field], [data-column], [data-lexic]")
            for element in data_elements:
                for attr in ['data-metric', 'data-field', 'data-column', 'data-lexic']:
                    value = element.get_attribute(attr)
                    if value:
                        all_metrics.add(value)
            
            # Get all text content and extract potential metrics
            page_text = self.driver.page_source
            
            # Look for patterns that might indicate metrics
            import re
            
            # Look for metric patterns in the HTML
            metric_patterns = [
                r'data-lexic="(\d+)"',  # From JS analysis
                r'class="[^"]*metric[^"]*"',
                r'class="[^"]*stat[^"]*"',
                r'data-field="([^"]+)"',
                r'data-column="([^"]+)"',
                r'data-testid="([^"]+)"',
                r'aria-label="([^"]+)"'
            ]
            
            for pattern in metric_patterns:
                matches = re.findall(pattern, page_text)
                for match in matches:
                    if isinstance(match, str) and len(match) > 1:
                        all_metrics.add(match)
            
            logger.info(f"📊 Total unique metrics found: {len(all_metrics)}")
            return sorted(list(all_metrics))
            
        except Exception as e:
            logger.error(f"❌ Error extracting all metrics: {e}")
            return None
    
    def get_comprehensive_metrics(self, team_id="21479"):
        """Get comprehensive metrics using all scroll methods"""
        try:
            if not self.navigate_to_skaters_tab(team_id):
                return None
            
            # Find TableScrollWrapper
            wrappers = self.find_table_scroll_wrapper()
            if not wrappers:
                logger.error("❌ No TableScrollWrapper found")
                return None
            
            # Try all scroll methods on each wrapper
            for i, wrapper in enumerate(wrappers):
                logger.info(f"📊 Processing wrapper {i+1}/{len(wrappers)}")
                
                # Method 1: State management scroll
                logger.info("🔄 Trying state management scroll...")
                self.scroll_with_state_management(wrapper)
                
                # Method 2: Debounced scroll
                logger.info("🔄 Trying debounced scroll...")
                self.scroll_with_debouncing(wrapper)
                
                # Method 3: Animation listener scroll
                logger.info("🔄 Trying animation listener scroll...")
                self.scroll_with_animation_listener(wrapper)
                
                # Method 4: Resize triggers scroll
                logger.info("🔄 Trying resize triggers scroll...")
                self.scroll_with_resize_triggers(wrapper)
            
            # Extract all metrics after all scrolling methods
            all_metrics = self.extract_all_metrics_after_scrolling()
            
            if all_metrics:
                logger.info(f"🎉 COMPREHENSIVE METRICS FOUND: {len(all_metrics)}")
                logger.info("=" * 80)
                for i, metric in enumerate(all_metrics, 1):
                    logger.info(f"  {i:3d}. {metric}")
                logger.info("=" * 80)
                
                return {
                    'total_metrics': len(all_metrics),
                    'metrics': all_metrics
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting comprehensive metrics: {e}")
            return None
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

def test_enhanced_scroll_scraper():
    """Test the enhanced scroll scraper"""
    scraper = EnhancedScrollScraper()
    
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
    test_enhanced_scroll_scraper()
