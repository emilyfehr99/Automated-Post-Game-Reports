#!/usr/bin/env python3
"""
Comprehensive Hudl Test
Test the complete login flow and data access
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

def comprehensive_hudl_test():
    """Comprehensive test of Hudl access and login"""
    print("🏒 Comprehensive Hudl Test")
    print("=" * 50)
    
    driver = None
    try:
        # Setup Chrome with more realistic settings
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Step 1: Go to main Hudl page
        print("1. Going to main Hudl page...")
        driver.get("https://www.hudl.com")
        time.sleep(3)
        
        print(f"   URL: {driver.current_url}")
        print(f"   Title: {driver.title}")
        
        # Step 2: Look for login button
        print("\n2. Looking for login button...")
        login_buttons = driver.find_elements(By.CSS_SELECTOR, 
            "a[href*='login'], button:contains('Log in'), a:contains('Log in'), button:contains('Login'), a:contains('Login')")
        
        if not login_buttons:
            # Try XPath
            login_buttons = driver.find_elements(By.XPATH, 
                "//a[contains(text(), 'Log in') or contains(text(), 'Login')] | //button[contains(text(), 'Log in') or contains(text(), 'Login')]")
        
        print(f"   Found {len(login_buttons)} login buttons")
        for i, btn in enumerate(login_buttons):
            print(f"     {i+1}. {btn.text} -> {btn.get_attribute('href')}")
        
        if login_buttons:
            print("   Clicking first login button...")
            login_buttons[0].click()
            time.sleep(5)
            
            print(f"   After click URL: {driver.current_url}")
            print(f"   After click title: {driver.title}")
        
        # Step 3: Look for email field on current page
        print("\n3. Looking for email field...")
        email_selectors = [
            "input[type='email']",
            "input[name='email']",
            "input[placeholder*='email']",
            "input[placeholder*='Email']",
            "#email",
            "#username",
            "input[name='username']",
            "input[data-testid*='email']",
            "input[data-testid*='username']"
        ]
        
        email_field = None
        for selector in email_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    email_field = elements[0]
                    print(f"   ✅ Found email field with selector: {selector}")
                    break
            except:
                continue
        
        if not email_field:
            print("   ❌ No email field found")
            print("   Available input fields:")
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i, inp in enumerate(inputs):
                print(f"     {i+1}. type='{inp.get_attribute('type')}', name='{inp.get_attribute('name')}', placeholder='{inp.get_attribute('placeholder')}', id='{inp.get_attribute('id')}'")
            
            # Try to navigate directly to Instat
            print("\n4. Trying direct navigation to Instat...")
            driver.get("https://app.hudl.com/instat/hockey")
            time.sleep(5)
            
            print(f"   Instat URL: {driver.current_url}")
            print(f"   Instat title: {driver.title}")
            
            # Look for email field again
            for selector in email_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and elements[0].is_displayed():
                        email_field = elements[0]
                        print(f"   ✅ Found email field with selector: {selector}")
                        break
                except:
                    continue
        
        if email_field:
            # Look for password field
            print("\n5. Looking for password field...")
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[placeholder*='password']",
                "input[placeholder*='Password']",
                "#password",
                "input[data-testid*='password']"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and elements[0].is_displayed():
                        password_field = elements[0]
                        print(f"   ✅ Found password field with selector: {selector}")
                        break
                except:
                    continue
            
            if password_field:
                # Fill in credentials
                print("\n6. Filling in credentials...")
                from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
                
                email_field.clear()
                time.sleep(0.5)
                email_field.send_keys(HUDL_USERNAME)
                print(f"   ✅ Entered email: {HUDL_USERNAME}")
                
                password_field.clear()
                time.sleep(0.5)
                password_field.send_keys(HUDL_PASSWORD)
                print(f"   ✅ Entered password")
                
                # Look for submit button
                print("\n7. Looking for submit button...")
                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Sign In')",
                    "button:contains('Login')",
                    "button:contains('Log In')",
                    "button:contains('Continue')",
                    ".submit-button",
                    "#submit",
                    "button[data-testid*='submit']",
                    "button[data-testid*='login']"
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    try:
                        if ":contains(" in selector:
                            elements = driver.find_elements(By.XPATH, f"//button[contains(text(), 'Sign In') or contains(text(), 'Login') or contains(text(), 'Log In') or contains(text(), 'Continue')]")
                        else:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        if elements and elements[0].is_displayed() and elements[0].is_enabled():
                            submit_button = elements[0]
                            print(f"   ✅ Found submit button with selector: {selector}")
                            print(f"   Button text: '{submit_button.text}'")
                            break
                    except:
                        continue
                
                if submit_button:
                    # Submit form
                    print("\n8. Submitting form...")
                    submit_button.click()
                    time.sleep(10)  # Wait for redirect
                    
                    print(f"   Current URL after submit: {driver.current_url}")
                    print(f"   Page title after submit: {driver.title}")
                    
                    # Check if login was successful
                    if "login" not in driver.current_url.lower() and "identity" not in driver.current_url.lower():
                        print("   ✅ Login appears successful!")
                        
                        # Try to navigate to Instat
                        print("\n9. Navigating to Instat...")
                        driver.get("https://app.hudl.com/instat/hockey")
                        time.sleep(5)
                        
                        print(f"   Instat URL: {driver.current_url}")
                        print(f"   Instat title: {driver.title}")
                        
                        # Try to navigate to Lloydminster Bobcats
                        print("\n10. Navigating to Lloydminster Bobcats...")
                        bobcats_url = "https://app.hudl.com/instat/hockey/teams/21479"
                        driver.get(bobcats_url)
                        time.sleep(5)
                        
                        print(f"   Bobcats URL: {driver.current_url}")
                        print(f"   Bobcats title: {driver.title}")
                        
                        # Look for SKATERS tab
                        print("\n11. Looking for SKATERS tab...")
                        skaters_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='skaters']")
                        if not skaters_links:
                            skaters_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Skaters') or contains(text(), 'SKATERS')]")
                        
                        print(f"   Found {len(skaters_links)} skaters-related links")
                        for i, link in enumerate(skaters_links):
                            print(f"     {i+1}. {link.text} -> {link.get_attribute('href')}")
                        
                        if skaters_links:
                            print("\n12. Clicking on SKATERS tab...")
                            skaters_links[0].click()
                            time.sleep(5)
                            
                            print(f"   After click URL: {driver.current_url}")
                            print(f"   After click title: {driver.title}")
                            
                            # Look for download/export buttons
                            print("\n13. Looking for download/export buttons...")
                            download_buttons = driver.find_elements(By.CSS_SELECTOR, 
                                "button[title*='download'], button[title*='export'], .download, .export, [data-testid*='download']")
                            print(f"   Found {len(download_buttons)} download buttons")
                            
                            for i, btn in enumerate(download_buttons):
                                print(f"     {i+1}. {btn.text} - {btn.get_attribute('title')} - {btn.get_attribute('class')}")
                        
                        return True
                    else:
                        print("   ❌ Login failed - still on login page")
                        return False
                else:
                    print("   ❌ No submit button found")
                    return False
            else:
                print("   ❌ No password field found")
                return False
        else:
            print("   ❌ No email field found")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            driver.quit()
            print("\n🔒 Browser closed")

if __name__ == "__main__":
    comprehensive_hudl_test()
