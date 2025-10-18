#!/usr/bin/env python3
"""
Test Hudl Instat Access
Simple test to check if we can access the site
"""

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_hudl_access():
    """Test if we can access Hudl Instat"""
    print("🏒 Testing Hudl Instat Access")
    print("=" * 40)
    
    # Test 1: Basic HTTP request
    print("1. Testing basic HTTP access...")
    try:
        response = requests.get("https://app.hudl.com", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Title: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ HTTP access failed: {e}")
    
    # Test 2: Selenium access
    print("\n2. Testing Selenium access...")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get("https://app.hudl.com")
        print(f"   Title: {driver.title}")
        print(f"   URL: {driver.current_url}")
        
        driver.quit()
        print("   ✅ Selenium access successful")
        
    except Exception as e:
        print(f"   ❌ Selenium access failed: {e}")
    
    # Test 3: Hudl Instat specific
    print("\n3. Testing Hudl Instat specific...")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get("https://app.hudl.com/instat/hockey")
        print(f"   Title: {driver.title}")
        print(f"   URL: {driver.current_url}")
        
        # Check if we can find login elements
        from selenium.webdriver.common.by import By
        try:
            login_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[name='email']")
            print(f"   Login elements found: {len(login_elements)}")
        except:
            print("   No login elements found")
        
        driver.quit()
        print("   ✅ Hudl Instat access successful")
        
    except Exception as e:
        print(f"   ❌ Hudl Instat access failed: {e}")

if __name__ == "__main__":
    test_hudl_access()
