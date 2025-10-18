#!/usr/bin/env python3
"""
Test script to check if we can access the SKATERS table structure
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

def test_skaters_table_access():
    """Test accessing the SKATERS table without login"""
    driver = None
    try:
        logger.info("🔍 Testing SKATERS table access...")
        
        # Setup Chrome driver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        # Try to access the SKATERS page directly
        skaters_url = "https://hockey.instatscout.com/teams/21479/skaters"
        logger.info(f"🌐 Navigating to: {skaters_url}")
        
        driver.get(skaters_url)
        time.sleep(5)  # Wait for page to load
        
        # Check if we can find the table container
        try:
            table_container = driver.find_element(By.CSS_SELECTOR, ".TableContainers__TablesContainer-sc-lwtdzh-0")
            logger.info("✅ Found table container!")
            
            # Check for table rows
            rows = table_container.find_elements(By.CSS_SELECTOR, "tr")
            logger.info(f"📊 Found {len(rows)} table rows")
            
            # Check for any data
            if rows:
                first_row = rows[0]
                cells = first_row.find_elements(By.CSS_SELECTOR, "th, td")
                cell_texts = [cell.text.strip() for cell in cells if cell.text.strip()]
                logger.info(f"📝 First row data: {cell_texts}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Could not find table container: {e}")
            
            # Let's see what we can find on the page
            logger.info("🔍 Checking page content...")
            page_source = driver.page_source
            logger.info(f"📄 Page source length: {len(page_source)}")
            
            # Look for any table-related elements
            table_elements = driver.find_elements(By.CSS_SELECTOR, "table, [class*='table'], [class*='Table']")
            logger.info(f"📋 Found {len(table_elements)} table-related elements")
            
            for i, element in enumerate(table_elements[:5]):  # Show first 5
                try:
                    tag_name = element.tag_name
                    class_name = element.get_attribute("class")
                    logger.info(f"  Element {i+1}: <{tag_name}> class='{class_name}'")
                except:
                    logger.info(f"  Element {i+1}: [unable to get details]")
            
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    success = test_skaters_table_access()
    if success:
        logger.info("🎉 Test passed!")
    else:
        logger.info("💥 Test failed!")
