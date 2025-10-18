#!/usr/bin/env python3
"""
Selenium-based Tableau Data Extractor for All Three Zones
Uses real browser automation to access Tableau iframe data
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeleniumTableauExtractor:
    """Extract data from Tableau iframes using Selenium"""
    
    def __init__(self):
        self.driver = None
        self.base_url = "https://www.allthreezones.com"
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        try:
            chrome_options = Options()
            # Uncomment the line below to run headless (no browser window)
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
    
    def login(self):
        """Login to All Three Zones using Selenium"""
        try:
            logger.info("🔐 Logging in with Selenium...")
            
            # Navigate to the login page
            self.driver.get(f"{self.base_url}/player-cards.html")
            logger.info("✅ Navigated to player cards page")
            
            # Wait for page to load
            time.sleep(3)
            
            # Look for login form elements
            try:
                # Try to find email field
                email_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "login-email"))
                )
                email_field.clear()
                email_field.send_keys(Config.A3Z_USERNAME)
                logger.info("✅ Entered email")
                
                # Find password field
                password_field = self.driver.find_element(By.NAME, "login-password")
                password_field.clear()
                password_field.send_keys(Config.A3Z_PASSWORD)
                logger.info("✅ Entered password")
                
                # Find and click login button
                login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                login_button.click()
                logger.info("✅ Clicked login button")
                
                # Wait for page to load after login
                time.sleep(5)
                
                # Check if we're still on login page
                if "Log In" in self.driver.page_source:
                    logger.warning("⚠️  Still on login page, trying alternative approach")
                    return False
                else:
                    logger.info("✅ Successfully logged in!")
                    return True
                    
            except Exception as e:
                logger.error(f"❌ Error during login: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def find_tableau_iframes(self):
        """Find all Tableau iframes on the page"""
        try:
            logger.info("🔍 Looking for Tableau iframes...")
            
            # Wait for page to load
            time.sleep(3)
            
            # Find all iframes
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            logger.info(f"✅ Found {len(iframes)} iframes")
            
            tableau_iframes = []
            for i, iframe in enumerate(iframes):
                src = iframe.get_attribute("src")
                title = iframe.get_attribute("title")
                
                logger.info(f"  Iframe {i+1}: src={src}, title={title}")
                
                if src and ("tableau" in src.lower() or "viz" in src.lower()):
                    tableau_iframes.append(iframe)
                    logger.info(f"✅ Found Tableau iframe: {src}")
            
            return tableau_iframes
            
        except Exception as e:
            logger.error(f"❌ Error finding iframes: {e}")
            return []
    
    def extract_data_from_iframe(self, iframe):
        """Extract data from a specific iframe"""
        try:
            logger.info("📊 Extracting data from iframe...")
            
            # Switch to the iframe
            self.driver.switch_to.frame(iframe)
            logger.info("✅ Switched to iframe")
            
            # Wait for iframe content to load
            time.sleep(3)
            
            # Look for player data elements
            page_source = self.driver.page_source
            
            # Look for Crosby data
            if "crosby" in page_source.lower() or "sidney" in page_source.lower():
                logger.info("✅ Found Crosby data in iframe!")
                
                # Save the iframe content
                with open('tableau_iframe_content.html', 'w', encoding='utf-8') as f:
                    f.write(page_source)
                logger.info("✅ Saved iframe content to tableau_iframe_content.html")
                
                # Look for specific data elements
                try:
                    # Look for player name elements
                    player_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Crosby') or contains(text(), 'Sidney')]")
                    logger.info(f"✅ Found {len(player_elements)} Crosby-related elements")
                    
                    for i, elem in enumerate(player_elements[:5]):  # Show first 5
                        logger.info(f"  Element {i+1}: {elem.text}")
                        
                except Exception as e:
                    logger.warning(f"⚠️  Error finding specific elements: {e}")
                
                return True
            else:
                logger.info("⚠️  No Crosby data found in this iframe")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error extracting from iframe: {e}")
            return False
        finally:
            # Switch back to main content
            self.driver.switch_to.default_content()
    
    def search_for_crosby(self):
        """Search for Sidney Crosby using browser automation"""
        try:
            logger.info("🔍 Searching for Sidney Crosby with Selenium...")
            
            # Setup driver
            if not self.setup_driver():
                logger.error("❌ Failed to setup driver")
                return False
            
            # Login
            if not self.login():
                logger.error("❌ Failed to login")
                return False
            
            # Find Tableau iframes
            tableau_iframes = self.find_tableau_iframes()
            
            if not tableau_iframes:
                logger.warning("⚠️  No Tableau iframes found")
                return False
            
            # Extract data from each iframe
            found_data = False
            for i, iframe in enumerate(tableau_iframes):
                logger.info(f"🔍 Processing iframe {i+1}/{len(tableau_iframes)}")
                
                if self.extract_data_from_iframe(iframe):
                    found_data = True
                    break
            
            if found_data:
                logger.info("🎉 Successfully extracted Crosby data!")
                return True
            else:
                logger.warning("⚠️  No Crosby data found in any iframe")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during search: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Browser closed")

def main():
    """Main function to test Selenium Tableau extraction"""
    logger.info("🏒 Selenium Tableau Data Extractor")
    logger.info("=" * 50)
    
    extractor = SeleniumTableauExtractor()
    
    if extractor.search_for_crosby():
        logger.info("🎉 Successfully extracted Sidney Crosby data!")
        logger.info("\nNext steps:")
        logger.info("1. Check tableau_iframe_content.html for the extracted data")
        logger.info("2. Integrate this with the API")
        logger.info("3. Search for other players")
    else:
        logger.error("❌ Failed to extract Crosby data")

if __name__ == "__main__":
    main() 