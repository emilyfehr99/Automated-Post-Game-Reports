#!/usr/bin/env python3
"""
Flexible Selenium Tableau Data Extractor
Handles different login form structures and focuses on data extraction
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlexibleSeleniumExtractor:
    """Flexible Selenium extractor for Tableau data"""
    
    def __init__(self):
        self.driver = None
        self.base_url = "https://www.allthreezones.com"
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        try:
            chrome_options = Options()
            # Run with browser visible for debugging
            # chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Try to find Chrome
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser"
            ]
            
            for path in chrome_paths:
                try:
                    chrome_options.binary_location = path
                    self.driver = webdriver.Chrome(options=chrome_options)
                    logger.info(f"✅ Found Chrome at: {path}")
                    return True
                except:
                    continue
            
            # Try default Chrome
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("✅ Using default Chrome")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to setup Chrome: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error setting up driver: {e}")
            return False
    
    def flexible_login(self):
        """Flexible login that tries multiple approaches"""
        try:
            logger.info("🔐 Attempting flexible login...")
            
            # Navigate to the login page
            self.driver.get(f"{self.base_url}/player-cards.html")
            logger.info("✅ Navigated to player cards page")
            
            # Wait for page to load
            time.sleep(5)
            
            # Try multiple login approaches
            login_successful = False
            
            # Approach 1: Look for standard login form
            try:
                logger.info("🔍 Trying standard login form...")
                
                # Look for email field with different possible names
                email_selectors = [
                    "input[name='login-email']",
                    "input[name='email']",
                    "input[type='email']",
                    "input[placeholder*='email']",
                    "input[placeholder*='Email']"
                ]
                
                email_field = None
                for selector in email_selectors:
                    try:
                        email_field = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        logger.info(f"✅ Found email field with selector: {selector}")
                        break
                    except:
                        continue
                
                if email_field:
                    email_field.clear()
                    email_field.send_keys(Config.A3Z_USERNAME)
                    logger.info("✅ Entered email")
                    
                    # Look for password field
                    password_selectors = [
                        "input[name='login-password']",
                        "input[name='password']",
                        "input[type='password']",
                        "input[placeholder*='password']",
                        "input[placeholder*='Password']"
                    ]
                    
                    password_field = None
                    for selector in password_selectors:
                        try:
                            password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                            logger.info(f"✅ Found password field with selector: {selector}")
                            break
                        except:
                            continue
                    
                    if password_field:
                        password_field.clear()
                        password_field.send_keys(Config.A3Z_PASSWORD)
                        logger.info("✅ Entered password")
                        
                        # Try to submit the form
                        try:
                            # Look for submit button
                            submit_selectors = [
                                "button[type='submit']",
                                "input[type='submit']",
                                "button:contains('Login')",
                                "button:contains('Sign In')",
                                "input[value*='Login']",
                                "input[value*='Sign In']"
                            ]
                            
                            for selector in submit_selectors:
                                try:
                                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                                    submit_button.click()
                                    logger.info(f"✅ Clicked submit button with selector: {selector}")
                                    break
                                except:
                                    continue
                            else:
                                # Try pressing Enter on password field
                                password_field.send_keys(Keys.RETURN)
                                logger.info("✅ Pressed Enter on password field")
                            
                            # Wait for page to load
                            time.sleep(5)
                            
                            # Check if login was successful
                            if "Log In" not in self.driver.page_source:
                                logger.info("✅ Login appears successful!")
                                login_successful = True
                            else:
                                logger.warning("⚠️  Still on login page")
                                
                        except Exception as e:
                            logger.error(f"❌ Error submitting form: {e}")
                
            except Exception as e:
                logger.error(f"❌ Error with standard login: {e}")
            
            # Approach 2: Try JSON-RPC login if standard failed
            if not login_successful:
                try:
                    logger.info("🔍 Trying JSON-RPC login...")
                    
                    # Execute JavaScript to make JSON-RPC call
                    js_code = f"""
                    fetch('{self.base_url}/ajax/api/JsonRPC/Membership/', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        }},
                        body: JSON.stringify({{
                            "method": "validate_user",
                            "params": ["{Config.A3Z_USERNAME}", "{Config.A3Z_PASSWORD}"],
                            "id": 1
                        }})
                    }})
                    .then(response => response.json())
                    .then(data => console.log('Login response:', data));
                    """
                    
                    self.driver.execute_script(js_code)
                    logger.info("✅ Executed JSON-RPC login")
                    
                    # Wait and check if we can access the page
                    time.sleep(3)
                    self.driver.get(f"{self.base_url}/player-cards.html")
                    time.sleep(3)
                    
                    if "Log In" not in self.driver.page_source:
                        logger.info("✅ JSON-RPC login successful!")
                        login_successful = True
                    
                except Exception as e:
                    logger.error(f"❌ Error with JSON-RPC login: {e}")
            
            return login_successful
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def extract_tableau_data(self):
        """Extract data from Tableau visualizations"""
        try:
            logger.info("📊 Extracting Tableau data...")
            
            # Wait for page to load
            time.sleep(5)
            
            # Save the current page
            with open('selenium_page.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.info("✅ Saved page to selenium_page.html")
            
            # Look for iframes
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            logger.info(f"✅ Found {len(iframes)} iframes")
            
            tableau_data = []
            
            for i, iframe in enumerate(iframes):
                try:
                    src = iframe.get_attribute("src")
                    title = iframe.get_attribute("title")
                    
                    logger.info(f"  Iframe {i+1}: src={src}, title={title}")
                    
                    if src and ("tableau" in src.lower() or "viz" in src.lower()):
                        logger.info(f"✅ Found Tableau iframe: {src}")
                        
                        # Try to switch to iframe
                        try:
                            self.driver.switch_to.frame(iframe)
                            logger.info("✅ Switched to iframe")
                            
                            # Wait for iframe content to load
                            time.sleep(3)
                            
                            # Get iframe content
                            iframe_content = self.driver.page_source
                            
                            # Look for player data
                            if "crosby" in iframe_content.lower() or "sidney" in iframe_content.lower():
                                logger.info("✅ Found Crosby data in iframe!")
                                
                                # Save iframe content
                                with open(f'tableau_iframe_{i}.html', 'w', encoding='utf-8') as f:
                                    f.write(iframe_content)
                                logger.info(f"✅ Saved iframe content to tableau_iframe_{i}.html")
                                
                                # Look for specific data elements
                                try:
                                    # Look for any elements containing player data
                                    elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Crosby') or contains(text(), 'Sidney')]")
                                    logger.info(f"✅ Found {len(elements)} Crosby-related elements")
                                    
                                    for j, elem in enumerate(elements[:10]):  # Show first 10
                                        logger.info(f"    Element {j+1}: {elem.text}")
                                        
                                except Exception as e:
                                    logger.warning(f"⚠️  Error finding specific elements: {e}")
                                
                                tableau_data.append({
                                    'iframe_index': i,
                                    'src': src,
                                    'content': iframe_content
                                })
                            
                            # Switch back to main content
                            self.driver.switch_to.default_content()
                            
                        except Exception as e:
                            logger.error(f"❌ Error accessing iframe {i}: {e}")
                            self.driver.switch_to.default_content()
                
                except Exception as e:
                    logger.error(f"❌ Error processing iframe {i}: {e}")
            
            return tableau_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting Tableau data: {e}")
            return []
    
    def search_for_crosby(self):
        """Search for Sidney Crosby using flexible Selenium approach"""
        try:
            logger.info("🔍 Searching for Sidney Crosby with flexible Selenium...")
            
            # Setup driver
            if not self.setup_driver():
                logger.error("❌ Failed to setup driver")
                return False
            
            # Try flexible login
            if not self.flexible_login():
                logger.warning("⚠️  Login may have failed, but continuing...")
            
            # Extract Tableau data
            tableau_data = self.extract_tableau_data()
            
            if tableau_data:
                logger.info(f"🎉 Successfully extracted data from {len(tableau_data)} Tableau iframes!")
                return True
            else:
                logger.warning("⚠️  No Tableau data found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during search: {e}")
            return False
        finally:
            if self.driver:
                # Keep browser open for manual inspection
                logger.info("✅ Browser will remain open for manual inspection")
                logger.info("✅ Check the saved HTML files for extracted data")
                # self.driver.quit()

def main():
    """Main function to test flexible Selenium extraction"""
    logger.info("🏒 Flexible Selenium Tableau Data Extractor")
    logger.info("=" * 60)
    
    extractor = FlexibleSeleniumExtractor()
    
    if extractor.search_for_crosby():
        logger.info("🎉 Successfully extracted Sidney Crosby data!")
        logger.info("\nNext steps:")
        logger.info("1. Check selenium_page.html for the main page")
        logger.info("2. Check tableau_iframe_*.html files for iframe content")
        logger.info("3. Manually inspect the browser for additional data")
        logger.info("4. Integrate the extracted data with the API")
    else:
        logger.error("❌ Failed to extract Crosby data")

if __name__ == "__main__":
    main() 