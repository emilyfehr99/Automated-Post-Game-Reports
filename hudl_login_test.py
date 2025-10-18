#!/usr/bin/env python3
"""
Hudl Login Test
Test the actual login process
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

def test_hudl_login():
    """Test Hudl login process"""
    print("🏒 Testing Hudl Login Process")
    print("=" * 40)
    
    driver = None
    try:
        # Setup Chrome
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to login
        print("1. Navigating to login page...")
        driver.get("https://app.hudl.com/login")
        time.sleep(3)
        
        print(f"   Current URL: {driver.current_url}")
        print(f"   Page title: {driver.title}")
        
        # Look for login form
        print("\n2. Looking for login form...")
        
        # Try different selectors for email field
        email_selectors = [
            "input[type='email']",
            "input[name='email']",
            "input[placeholder*='email']",
            "input[placeholder*='Email']",
            "#email",
            "#username",
            "input[name='username']"
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
                print(f"     {i+1}. type='{inp.get_attribute('type')}', name='{inp.get_attribute('name')}', placeholder='{inp.get_attribute('placeholder')}'")
            return False
        
        # Look for password field
        password_selectors = [
            "input[type='password']",
            "input[name='password']",
            "input[placeholder*='password']",
            "input[placeholder*='Password']",
            "#password"
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
        
        if not password_field:
            print("   ❌ No password field found")
            return False
        
        # Fill in credentials
        print("\n3. Filling in credentials...")
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        
        email_field.clear()
        email_field.send_keys(HUDL_USERNAME)
        print(f"   ✅ Entered email: {HUDL_USERNAME}")
        
        password_field.clear()
        password_field.send_keys(HUDL_PASSWORD)
        print(f"   ✅ Entered password")
        
        # Look for submit button
        print("\n4. Looking for submit button...")
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Sign In')",
            "button:contains('Login')",
            "button:contains('Log In')",
            ".submit-button",
            "#submit"
        ]
        
        submit_button = None
        for selector in submit_selectors:
            try:
                if ":contains(" in selector:
                    elements = driver.find_elements(By.XPATH, f"//button[contains(text(), 'Sign In') or contains(text(), 'Login') or contains(text(), 'Log In')]")
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements and elements[0].is_displayed() and elements[0].is_enabled():
                    submit_button = elements[0]
                    print(f"   ✅ Found submit button with selector: {selector}")
                    print(f"   Button text: '{submit_button.text}'")
                    break
            except:
                continue
        
        if not submit_button:
            print("   ❌ No submit button found")
            print("   Available buttons:")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for i, btn in enumerate(buttons):
                print(f"     {i+1}. text='{btn.text}', type='{btn.get_attribute('type')}', class='{btn.get_attribute('class')}'")
            return False
        
        # Submit form
        print("\n5. Submitting form...")
        submit_button.click()
        time.sleep(5)  # Wait for redirect
        
        print(f"   Current URL after submit: {driver.current_url}")
        print(f"   Page title after submit: {driver.title}")
        
        # Check if login was successful
        if "login" not in driver.current_url.lower() and "identity" not in driver.current_url.lower():
            print("   ✅ Login appears successful!")
            
            # Try to navigate to Instat
            print("\n6. Navigating to Instat...")
            driver.get("https://app.hudl.com/instat/hockey")
            time.sleep(3)
            
            print(f"   Instat URL: {driver.current_url}")
            print(f"   Instat title: {driver.title}")
            
            # Try to find team page
            print("\n7. Looking for team navigation...")
            team_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='teams'], a[href*='team']")
            print(f"   Found {len(team_links)} team-related links")
            
            for i, link in enumerate(team_links[:5]):  # Show first 5
                print(f"     {i+1}. {link.text} -> {link.get_attribute('href')}")
            
            return True
        else:
            print("   ❌ Login failed - still on login page")
            return False
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        return False
    finally:
        if driver:
            driver.quit()
            print("\n🔒 Browser closed")

if __name__ == "__main__":
    test_hudl_login()
