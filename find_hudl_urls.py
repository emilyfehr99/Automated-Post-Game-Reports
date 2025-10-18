#!/usr/bin/env python3
"""
Find Correct Hudl Instat URLs
"""

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_hudl_urls():
    """Test different Hudl Instat URLs"""
    print("🏒 Testing Hudl Instat URLs")
    print("=" * 40)
    
    urls_to_test = [
        "https://app.hudl.com/instat/hockey",
        "https://hockey.instatscout.com",
        "https://instatscout.com/hockey",
        "https://app.hudl.com/instat",
        "https://www.hudl.com/instat/hockey",
        "https://hudl.com/instat/hockey"
    ]
    
    for url in urls_to_test:
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  Title: {response.text[:100]}...")
            else:
                print(f"  Error: {response.text[:100]}...")
        except Exception as e:
            print(f"  Exception: {e}")
    
    # Test with Selenium
    print(f"\n🔍 Testing with Selenium...")
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        for url in urls_to_test:
            print(f"\nSelenium testing: {url}")
            try:
                driver.get(url)
                print(f"  Title: {driver.title}")
                print(f"  URL: {driver.current_url}")
                
                # Look for login elements
                from selenium.webdriver.common.by import By
                login_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[type='password']")
                print(f"  Login elements: {len(login_elements)}")
                
            except Exception as e:
                print(f"  Error: {e}")
        
    except Exception as e:
        print(f"❌ Selenium error: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_hudl_urls()
