#!/usr/bin/env python3
"""
Inspect Login Page
Detailed inspection of the Hudl login page
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inspect_login_page():
    """Inspect the login page in detail"""
    print("🏒 Inspecting Hudl Login Page")
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
        
        # Go to login page
        print("1. Going to login page...")
        driver.get("https://app.hudl.com/instat/hockey")
        time.sleep(5)
        
        print(f"   URL: {driver.current_url}")
        print(f"   Title: {driver.title}")
        
        # Get page source
        print("\n2. Analyzing page structure...")
        page_source = driver.page_source
        
        # Look for all input fields
        print("\n3. All input fields:")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for i, inp in enumerate(inputs):
            print(f"   {i+1}. type='{inp.get_attribute('type')}', name='{inp.get_attribute('name')}', id='{inp.get_attribute('id')}', placeholder='{inp.get_attribute('placeholder')}', class='{inp.get_attribute('class')}'")
        
        # Look for all buttons
        print("\n4. All buttons:")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for i, btn in enumerate(buttons):
            print(f"   {i+1}. text='{btn.text}', type='{btn.get_attribute('type')}', class='{btn.get_attribute('class')}', id='{btn.get_attribute('id')}'")
        
        # Look for all links
        print("\n5. All links:")
        links = driver.find_elements(By.TAG_NAME, "a")
        for i, link in enumerate(links[:10]):  # First 10 links
            print(f"   {i+1}. text='{link.text}', href='{link.get_attribute('href')}'")
        
        # Look for forms
        print("\n6. All forms:")
        forms = driver.find_elements(By.TAG_NAME, "form")
        for i, form in enumerate(forms):
            print(f"   {i+1}. action='{form.get_attribute('action')}', method='{form.get_attribute('method')}', class='{form.get_attribute('class')}'")
        
        # Look for specific elements that might be email fields
        print("\n7. Looking for email-related elements:")
        email_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], input[name*='email'], input[name*='username'], input[placeholder*='email'], input[placeholder*='Email']")
        for i, elem in enumerate(email_elements):
            print(f"   {i+1}. type='{elem.get_attribute('type')}', name='{elem.get_attribute('name')}', placeholder='{elem.get_attribute('placeholder')}', id='{elem.get_attribute('id')}'")
        
        # Check if there are any hidden fields
        print("\n8. Looking for hidden fields:")
        hidden_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='hidden']")
        for i, inp in enumerate(hidden_inputs):
            print(f"   {i+1}. name='{inp.get_attribute('name')}', value='{inp.get_attribute('value')}'")
        
        # Look for any elements with "email" in their attributes
        print("\n9. Elements containing 'email' in attributes:")
        all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
        email_related = []
        for elem in all_elements:
            attrs = ['id', 'name', 'class', 'placeholder', 'data-testid', 'aria-label']
            for attr in attrs:
                value = elem.get_attribute(attr)
                if value and 'email' in value.lower():
                    email_related.append((elem.tag_name, attr, value))
        
        for i, (tag, attr, value) in enumerate(email_related[:10]):
            print(f"   {i+1}. {tag}[{attr}]='{value}'")
        
        # Try to find the actual email field by looking at the page source
        print("\n10. Searching page source for email patterns:")
        if 'email' in page_source.lower():
            print("   ✅ Found 'email' in page source")
        if 'username' in page_source.lower():
            print("   ✅ Found 'username' in page source")
        if 'identifier' in page_source.lower():
            print("   ✅ Found 'identifier' in page source")
        
        # Look for any input that might be the email field
        print("\n11. Trying to find email field by visibility and interaction:")
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        for i, inp in enumerate(all_inputs):
            if inp.is_displayed() and inp.is_enabled():
                print(f"   {i+1}. Interactive input: type='{inp.get_attribute('type')}', name='{inp.get_attribute('name')}', placeholder='{inp.get_attribute('placeholder')}'")
                
                # Try to click on it and see what happens
                try:
                    inp.click()
                    print(f"      Clicked successfully")
                except:
                    print(f"      Could not click")
        
        return True
        
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
    inspect_login_page()
