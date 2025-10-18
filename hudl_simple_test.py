#!/usr/bin/env python3
"""
Simple Hudl Test
Basic test to get to the login page and try to log in
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

def simple_hudl_test():
    """Simple test of Hudl access"""
    print("🏒 Simple Hudl Test")
    print("=" * 30)
    
    driver = None
    try:
        # Setup Chrome
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Step 1: Go to Hudl Instat directly
        print("1. Going to Hudl Instat...")
        driver.get("https://app.hudl.com/instat/hockey")
        time.sleep(5)
        
        print(f"   URL: {driver.current_url}")
        print(f"   Title: {driver.title}")
        
        # Step 2: Look for login elements
        print("\n2. Looking for login elements...")
        
        # Look for email field
        email_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='email']")
        if not email_fields:
            email_fields = driver.find_elements(By.CSS_SELECTOR, "input[name='email']")
        if not email_fields:
            email_fields = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='email']")
        
        print(f"   Found {len(email_fields)} email fields")
        
        # Look for password field
        password_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        if not password_fields:
            password_fields = driver.find_elements(By.CSS_SELECTOR, "input[name='password']")
        
        print(f"   Found {len(password_fields)} password fields")
        
        # Look for submit buttons
        submit_buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")
        if not submit_buttons:
            submit_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
        
        print(f"   Found {len(submit_buttons)} submit buttons")
        
        # If we found login elements, try to log in
        if email_fields and password_fields and submit_buttons:
            print("\n3. Attempting login...")
            
            from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
            
            # Fill email
            email_field = email_fields[0]
            email_field.clear()
            email_field.send_keys(HUDL_USERNAME)
            print(f"   ✅ Entered email: {HUDL_USERNAME}")
            
            # Fill password
            password_field = password_fields[0]
            password_field.clear()
            password_field.send_keys(HUDL_PASSWORD)
            print(f"   ✅ Entered password")
            
            # Submit
            submit_button = submit_buttons[0]
            submit_button.click()
            print("   ✅ Clicked submit")
            
            # Wait for redirect
            time.sleep(10)
            
            print(f"\n4. After login:")
            print(f"   URL: {driver.current_url}")
            print(f"   Title: {driver.title}")
            
            # Check if we're logged in
            if "login" not in driver.current_url.lower() and "identity" not in driver.current_url.lower():
                print("   ✅ Login successful!")
                
                # Try to navigate to team page
                print("\n5. Navigating to Lloydminster Bobcats...")
                driver.get("https://app.hudl.com/instat/hockey/teams/21479")
                time.sleep(5)
                
                print(f"   Team URL: {driver.current_url}")
                print(f"   Team title: {driver.title}")
                
                # Look for SKATERS tab
                print("\n6. Looking for SKATERS tab...")
                skaters_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='skaters']")
                print(f"   Found {len(skaters_links)} skaters links")
                
                if skaters_links:
                    print("   Clicking SKATERS tab...")
                    skaters_links[0].click()
                    time.sleep(5)
                    
                    print(f"   After click URL: {driver.current_url}")
                    print(f"   After click title: {driver.title}")
                    
                    # Look for download buttons
                    print("\n7. Looking for download buttons...")
                    download_buttons = driver.find_elements(By.CSS_SELECTOR, 
                        "button[title*='download'], button[title*='export'], .download, .export")
                    print(f"   Found {len(download_buttons)} download buttons")
                    
                    for i, btn in enumerate(download_buttons):
                        print(f"     {i+1}. {btn.text} - {btn.get_attribute('title')}")
                
                return True
            else:
                print("   ❌ Login failed")
                return False
        else:
            print("   ❌ No login elements found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            driver.quit()
            print("\n🔒 Browser closed")

if __name__ == "__main__":
    simple_hudl_test()
