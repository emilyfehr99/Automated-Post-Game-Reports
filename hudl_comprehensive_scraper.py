#!/usr/bin/env python3
"""
Comprehensive Hudl Instat Scraper
Gets comprehensive player data from the SKATERS tab
"""

import time
import logging
import json
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

def comprehensive_hudl_scraper():
    """Comprehensive scraper that gets all player data"""
    print("🏒 Comprehensive Hudl Instat Scraper")
    print("=" * 50)
    
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
        
        # Step 1: Login
        print("1. Logging in...")
        if not login_to_hudl(driver):
            print("❌ Login failed")
            return False
        
        # Step 2: Navigate to team skaters page
        print("\n2. Navigating to Lloydminster Bobcats SKATERS...")
        bobcats_url = "https://app.hudl.com/instat/hockey/teams/21479/skaters"
        driver.get(bobcats_url)
        time.sleep(10)  # Wait longer for dynamic content
        
        print(f"   URL: {driver.current_url}")
        print(f"   Title: {driver.title}")
        
        # Step 3: Wait for page to fully load
        print("\n3. Waiting for page to load...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(5)
        
        # Step 4: Look for all possible data elements
        print("\n4. Analyzing page content...")
        
        # Look for tables
        tables = driver.find_elements(By.CSS_SELECTOR, "table")
        print(f"   Found {len(tables)} tables")
        
        # Look for divs that might contain data
        data_divs = driver.find_elements(By.CSS_SELECTOR, "div[class*='table'], div[class*='data'], div[class*='stats']")
        print(f"   Found {len(data_divs)} data divs")
        
        # Look for lists
        lists = driver.find_elements(By.CSS_SELECTOR, "ul, ol")
        print(f"   Found {len(lists)} lists")
        
        # Look for any elements with player names
        player_elements = driver.find_elements(By.CSS_SELECTOR, "*")
        player_names = []
        for elem in player_elements:
            text = elem.text.strip()
            if text and len(text) > 2 and len(text) < 50 and text.replace(" ", "").isalpha():
                player_names.append(text)
        
        unique_names = list(set(player_names))[:10]  # First 10 unique names
        print(f"   Found potential player names: {unique_names}")
        
        # Step 5: Look for download/export buttons with more selectors
        print("\n5. Looking for download/export buttons...")
        download_selectors = [
            "button[title*='download']",
            "button[title*='export']",
            "button[title*='Download']",
            "button[title*='Export']",
            ".download",
            ".export",
            "[data-testid*='download']",
            "[data-testid*='export']",
            "a[href*='.csv']",
            "a[href*='.xlsx']",
            "button:contains('Download')",
            "button:contains('Export')",
            "a:contains('CSV')",
            "a:contains('Excel')"
        ]
        
        download_buttons = []
        for selector in download_selectors:
            try:
                if ":contains(" in selector:
                    elements = driver.find_elements(By.XPATH, f"//button[contains(text(), 'Download') or contains(text(), 'Export')] | //a[contains(text(), 'CSV') or contains(text(), 'Excel')]")
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        download_buttons.append(elem)
            except:
                continue
        
        print(f"   Found {len(download_buttons)} download buttons")
        for i, btn in enumerate(download_buttons):
            print(f"     {i+1}. {btn.text} - {btn.get_attribute('title')} - {btn.get_attribute('class')}")
        
        # Step 6: Look for any clickable elements that might trigger data export
        print("\n6. Looking for clickable elements...")
        clickable_elements = driver.find_elements(By.CSS_SELECTOR, "button, a, [role='button']")
        print(f"   Found {len(clickable_elements)} clickable elements")
        
        # Show first 10 clickable elements
        for i, elem in enumerate(clickable_elements[:10]):
            if elem.is_displayed():
                print(f"     {i+1}. {elem.tag_name} - {elem.text[:50]} - {elem.get_attribute('class')}")
        
        # Step 7: Try to find any data in the page source
        print("\n7. Analyzing page source for data...")
        page_source = driver.page_source
        
        # Look for common data patterns
        data_indicators = [
            "goals", "assists", "points", "shots", "hits", "faceoffs",
            "time on ice", "plus minus", "penalties", "power play"
        ]
        
        found_indicators = []
        for indicator in data_indicators:
            if indicator.lower() in page_source.lower():
                found_indicators.append(indicator)
        
        print(f"   Found data indicators: {found_indicators}")
        
        # Step 8: Look for any JavaScript that might load data
        print("\n8. Looking for JavaScript data...")
        scripts = driver.find_elements(By.TAG_NAME, "script")
        print(f"   Found {len(scripts)} script tags")
        
        # Look for any data in script tags
        for i, script in enumerate(scripts[:5]):  # First 5 scripts
            script_content = script.get_attribute('innerHTML')
            if script_content and len(script_content) > 100:
                print(f"     Script {i+1}: {len(script_content)} characters")
                if any(indicator in script_content.lower() for indicator in data_indicators):
                    print(f"       Contains data indicators!")
        
        # Step 9: Try to interact with any buttons to see if they reveal data
        print("\n9. Trying to interact with buttons...")
        interactive_buttons = [btn for btn in clickable_elements if btn.is_displayed() and btn.is_enabled()]
        
        for i, btn in enumerate(interactive_buttons[:5]):  # Try first 5 buttons
            try:
                print(f"   Trying button {i+1}: {btn.text[:30]}...")
                btn.click()
                time.sleep(2)
                
                # Check if anything changed
                new_tables = driver.find_elements(By.CSS_SELECTOR, "table")
                if len(new_tables) > len(tables):
                    print(f"     ✅ New tables appeared! Now {len(new_tables)} tables")
                    tables = new_tables
                
                # Check for new download buttons
                new_downloads = driver.find_elements(By.CSS_SELECTOR, "button[title*='download'], button[title*='export']")
                if len(new_downloads) > len(download_buttons):
                    print(f"     ✅ New download buttons appeared! Now {len(new_downloads)} buttons")
                    download_buttons = new_downloads
                
            except Exception as e:
                print(f"     ❌ Error clicking button: {e}")
        
        # Step 10: Final analysis
        print("\n10. Final analysis...")
        print(f"   Final table count: {len(tables)}")
        print(f"   Final download button count: {len(download_buttons)}")
        
        if tables:
            print("   📊 Tables found - analyzing content...")
            for i, table in enumerate(tables):
                rows = table.find_elements(By.CSS_SELECTOR, "tr")
                cols = table.find_elements(By.CSS_SELECTOR, "th, td")
                print(f"     Table {i+1}: {len(rows)} rows, {len(cols)} cells")
                
                if rows:
                    # Show first row
                    first_row = rows[0]
                    cells = first_row.find_elements(By.CSS_SELECTOR, "td, th")
                    cell_texts = [cell.text.strip() for cell in cells]
                    print(f"       First row: {cell_texts}")
        
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

def login_to_hudl(driver):
    """Login to Hudl Instat"""
    try:
        # Go to login page
        driver.get("https://app.hudl.com/instat/hockey")
        time.sleep(5)
        
        # Find username field
        username_field = driver.find_element(By.ID, "username")
        username_field.clear()
        username_field.send_keys("chaserochon777@gmail.com")
        
        # Click Continue
        continue_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'][name='action'][value='default']")
        continue_button.click()
        time.sleep(5)
        
        # Find password field
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_field.clear()
        password_field.send_keys("357Chaser!468")
        
        # Click Continue
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(10)
        
        # Check if login successful
        if "login" not in driver.current_url.lower() and "identity" not in driver.current_url.lower():
            print("   ✅ Login successful!")
            return True
        else:
            print("   ❌ Login failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False

if __name__ == "__main__":
    comprehensive_hudl_scraper()
