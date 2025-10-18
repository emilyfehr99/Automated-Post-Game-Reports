#!/usr/bin/env python3
"""
Test different login URLs to find the correct one
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_login_urls():
    """Test different login URLs"""
    driver = None
    try:
        logger.info("🔍 Testing different login URLs...")
        
        # Setup Chrome driver
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        # Test URLs
        test_urls = [
            "https://identity.hudl.com/u/login/identifier",
            "https://www.hudl.com/login",
            "https://hockey.instatscout.com/login",
            "https://hockey.instatscout.com/",
            "https://www.hudl.com/"
        ]
        
        for i, url in enumerate(test_urls):
            try:
                logger.info(f"\n🌐 Test {i+1}: {url}")
                driver.get(url)
                time.sleep(3)
                
                current_url = driver.current_url
                logger.info(f"📍 Current URL: {current_url}")
                
                # Check for username/email fields
                username_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[type='text'], input[name='username'], input[name='email']")
                logger.info(f"📝 Found {len(username_fields)} username/email fields")
                
                # Check for password fields
                password_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
                logger.info(f"🔒 Found {len(password_fields)} password fields")
                
                # Check for submit buttons
                submit_buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                logger.info(f"🔘 Found {len(submit_buttons)} submit buttons")
                
                # Check page title
                title = driver.title
                logger.info(f"📄 Page title: {title}")
                
                if username_fields and password_fields:
                    logger.info("✅ This looks like a login page!")
                    break
                else:
                    logger.info("❌ Not a login page")
                    
            except Exception as e:
                logger.error(f"❌ Error testing {url}: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False
    finally:
        if driver:
            input("Press Enter to close browser...")
            driver.quit()

if __name__ == "__main__":
    test_login_urls()
