#!/usr/bin/env python3
"""
Real Hudl Instat Scraper
Based on the actual HTML structure from the login page
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

def real_hudl_scraper():
    """Real Hudl scraper based on actual HTML structure"""
    print("🏒 Real Hudl Instat Scraper")
    print("=" * 40)
    
    driver = None
    try:
        # Setup Chrome
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Step 1: Go to Hudl Instat
        print("1. Going to Hudl Instat...")
        driver.get("https://app.hudl.com/instat/hockey")
        time.sleep(5)
        
        print(f"   URL: {driver.current_url}")
        print(f"   Title: {driver.title}")
        
        # Step 2: Find the username field (email field)
        print("\n2. Looking for username field...")
        username_field = driver.find_element(By.ID, "username")
        print(f"   ✅ Found username field: {username_field.get_attribute('name')}")
        
        # Step 3: Find the password field (it's hidden initially)
        print("\n3. Looking for password field...")
        password_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        print(f"   Found {len(password_fields)} password fields")
        
        # Step 4: Fill in username and submit
        print("\n4. Filling in username...")
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        
        username_field.clear()
        username_field.send_keys(HUDL_USERNAME)
        print(f"   ✅ Entered username: {HUDL_USERNAME}")
        
        # Step 5: Find and click Continue button
        print("\n5. Looking for Continue button...")
        continue_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'][name='action'][value='default']")
        print(f"   ✅ Found Continue button: {continue_button.text}")
        
        # Click Continue to go to password page
        print("\n6. Clicking Continue...")
        continue_button.click()
        time.sleep(5)
        
        print(f"   After Continue URL: {driver.current_url}")
        print(f"   After Continue title: {driver.title}")
        
        # Step 7: Look for password field on the new page
        print("\n7. Looking for password field on new page...")
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        print(f"   ✅ Found password field")
        
        # Step 8: Fill in password
        print("\n8. Filling in password...")
        password_field.clear()
        password_field.send_keys(HUDL_PASSWORD)
        print(f"   ✅ Entered password")
        
        # Step 9: Find and click submit button
        print("\n9. Looking for submit button...")
        submit_buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")
        print(f"   Found {len(submit_buttons)} submit buttons")
        
        for i, btn in enumerate(submit_buttons):
            print(f"     {i+1}. {btn.text} - {btn.get_attribute('name')} - {btn.get_attribute('value')}")
        
        if submit_buttons:
            submit_button = submit_buttons[0]
            print(f"   Clicking submit button: {submit_button.text}")
            submit_button.click()
            time.sleep(10)
            
            print(f"   After submit URL: {driver.current_url}")
            print(f"   After submit title: {driver.title}")
            
            # Check if login was successful
            if "login" not in driver.current_url.lower() and "identity" not in driver.current_url.lower():
                print("   ✅ Login successful!")
                
                # Step 10: Navigate to Lloydminster Bobcats
                print("\n10. Navigating to Lloydminster Bobcats...")
                bobcats_url = "https://app.hudl.com/instat/hockey/teams/21479"
                driver.get(bobcats_url)
                time.sleep(5)
                
                print(f"   Bobcats URL: {driver.current_url}")
                print(f"   Bobcats title: {driver.title}")
                
                # Step 11: Look for SKATERS tab
                print("\n11. Looking for SKATERS tab...")
                skaters_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='skaters']")
                print(f"   Found {len(skaters_links)} skaters links")
                
                for i, link in enumerate(skaters_links):
                    print(f"     {i+1}. {link.text} -> {link.get_attribute('href')}")
                
                if skaters_links:
                    print("\n12. Clicking SKATERS tab...")
                    skaters_links[0].click()
                    time.sleep(5)
                    
                    print(f"   After click URL: {driver.current_url}")
                    print(f"   After click title: {driver.title}")
                    
                    # Step 13: Look for download/export buttons
                    print("\n13. Looking for download/export buttons...")
                    download_buttons = driver.find_elements(By.CSS_SELECTOR, 
                        "button[title*='download'], button[title*='export'], .download, .export, [data-testid*='download']")
                    print(f"   Found {len(download_buttons)} download buttons")
                    
                    for i, btn in enumerate(download_buttons):
                        print(f"     {i+1}. {btn.text} - {btn.get_attribute('title')} - {btn.get_attribute('class')}")
                    
                    # Step 14: Look for data tables
                    print("\n14. Looking for data tables...")
                    tables = driver.find_elements(By.CSS_SELECTOR, "table")
                    print(f"   Found {len(tables)} tables")
                    
                    for i, table in enumerate(tables):
                        rows = table.find_elements(By.CSS_SELECTOR, "tr")
                        cols = table.find_elements(By.CSS_SELECTOR, "th")
                        print(f"     {i+1}. {len(rows)} rows, {len(cols)} columns")
                        
                        # Show first few rows of data
                        if rows:
                            print(f"        First row: {rows[0].text[:100]}...")
                
                return True
            else:
                print("   ❌ Login failed - still on login page")
                return False
        else:
            print("   ❌ No submit button found")
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
    real_hudl_scraper()
