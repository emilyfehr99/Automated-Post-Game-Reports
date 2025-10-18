#!/usr/bin/env python3
"""
Find Clickable Box Score Element
Finds the actual clickable element that triggers the Box Score modal
"""

import time
import json
import logging
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_clickable_box_score():
    """Find the actual clickable Box Score element"""
    try:
        logger.info("🚀 Starting Clickable Box Score Finder...")
        
        # Use the working scraper
        scraper = HudlCompleteMetricsScraper()
        
        if not scraper.setup_driver():
            return False
        
        # Login
        username = "chaserochon777@gmail.com"
        password = "357Chaser!468"
        
        if not scraper.login(username, password):
            logger.error("❌ Authentication failed")
            return False
        
        logger.info("✅ Authentication successful")
        
        # Navigate to team page
        team_url = "https://hockey.instatscout.com/instat/hockey/teams/21479"
        scraper.driver.get(team_url)
        time.sleep(3)
        
        # Click on SKATERS tab
        logger.info("🔍 Clicking SKATERS tab...")
        skaters_tab = scraper.driver.find_element("xpath", "//a[contains(text(), 'SKATERS')]")
        skaters_tab.click()
        time.sleep(3)
        
        # Get all clickable elements that might contain Box Score
        logger.info("🔍 Getting all clickable elements...")
        clickable_elements = scraper.driver.execute_script("""
            var clickableElements = [];
            var allElements = document.querySelectorAll('button, a, [role="button"], [onclick], [class*="click"], [class*="button"], [class*="btn"], [class*="link"], [class*="tab"], [class*="menu"], [class*="item"]');
            
            for (var i = 0; i < allElements.length; i++) {
                var element = allElements[i];
                var text = element.innerText.trim();
                var title = element.title || '';
                var className = element.className || '';
                var id = element.id || '';
                var dataLexic = element.getAttribute('data-lexic') || '';
                var tagName = element.tagName;
                var role = element.getAttribute('role') || '';
                var onclick = element.getAttribute('onclick') || '';
                
                if (text || title || className || id || dataLexic) {
                    clickableElements.push({
                        text: text,
                        title: title,
                        className: className,
                        id: id,
                        dataLexic: dataLexic,
                        tagName: tagName,
                        role: role,
                        onclick: onclick
                    });
                }
            }
            
            return clickableElements;
        """)
        
        logger.info(f"📊 Found {len(clickable_elements)} clickable elements")
        
        # Look for Box Score related clickable elements
        box_score_clickable = []
        for element in clickable_elements:
            text = element.get('text', '').lower()
            title = element.get('title', '').lower()
            className = element.get('className', '').lower()
            data_lexic = element.get('dataLexic', '')
            
            if (('box' in text and 'score' in text) or 
                ('box' in title and 'score' in title) or
                ('box' in className and 'score' in className) or
                data_lexic == '3605'):
                box_score_clickable.append(element)
        
        logger.info(f"📊 Found {len(box_score_clickable)} Box Score clickable elements")
        
        # Show Box Score clickable elements
        for i, element in enumerate(box_score_clickable):
            logger.info(f"  Box Score Clickable {i+1}:")
            logger.info(f"    Text: '{element.get('text', '')}'")
            logger.info(f"    Title: '{element.get('title', '')}'")
            logger.info(f"    Class: '{element.get('className', '')}'")
            logger.info(f"    ID: '{element.get('id', '')}'")
            logger.info(f"    Data-lexic: '{element.get('dataLexic', '')}'")
            logger.info(f"    Tag: '{element.get('tagName', '')}'")
            logger.info(f"    Role: '{element.get('role', '')}'")
            logger.info(f"    Onclick: '{element.get('onclick', '')}'")
            logger.info("")
        
        # Look for Select All related clickable elements
        select_all_clickable = []
        for element in clickable_elements:
            text = element.get('text', '').lower()
            title = element.get('title', '').lower()
            className = element.get('className', '').lower()
            data_lexic = element.get('dataLexic', '')
            
            if (('select' in text and 'all' in text) or 
                ('select' in title and 'all' in title) or
                ('select' in className and 'all' in className) or
                data_lexic == '4239'):
                select_all_clickable.append(element)
        
        logger.info(f"📊 Found {len(select_all_clickable)} Select All clickable elements")
        
        # Show Select All clickable elements
        for i, element in enumerate(select_all_clickable):
            logger.info(f"  Select All Clickable {i+1}:")
            logger.info(f"    Text: '{element.get('text', '')}'")
            logger.info(f"    Title: '{element.get('title', '')}'")
            logger.info(f"    Class: '{element.get('className', '')}'")
            logger.info(f"    ID: '{element.get('id', '')}'")
            logger.info(f"    Data-lexic: '{element.get('dataLexic', '')}'")
            logger.info(f"    Tag: '{element.get('tagName', '')}'")
            logger.info(f"    Role: '{element.get('role', '')}'")
            logger.info(f"    Onclick: '{element.get('onclick', '')}'")
            logger.info("")
        
        # Look for Download XLS related clickable elements
        download_clickable = []
        for element in clickable_elements:
            text = element.get('text', '').lower()
            title = element.get('title', '').lower()
            className = element.get('className', '').lower()
            data_lexic = element.get('dataLexic', '')
            
            if (('download' in text and 'xls' in text) or 
                ('download' in title and 'xls' in title) or
                ('download' in className and 'xls' in className) or
                data_lexic == '3148'):
                download_clickable.append(element)
        
        logger.info(f"📊 Found {len(download_clickable)} Download XLS clickable elements")
        
        # Show Download clickable elements
        for i, element in enumerate(download_clickable):
            logger.info(f"  Download Clickable {i+1}:")
            logger.info(f"    Text: '{element.get('text', '')}'")
            logger.info(f"    Title: '{element.get('title', '')}'")
            logger.info(f"    Class: '{element.get('className', '')}'")
            logger.info(f"    ID: '{element.get('id', '')}'")
            logger.info(f"    Data-lexic: '{element.get('dataLexic', '')}'")
            logger.info(f"    Tag: '{element.get('tagName', '')}'")
            logger.info(f"    Role: '{element.get('role', '')}'")
            logger.info(f"    Onclick: '{element.get('onclick', '')}'")
            logger.info("")
        
        # Save results
        results = {
            'box_score_clickable': box_score_clickable,
            'select_all_clickable': select_all_clickable,
            'download_clickable': download_clickable,
            'total_clickable_elements': len(clickable_elements)
        }
        
        with open('clickable_elements.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("✅ Results saved to clickable_elements.json")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in find clickable box score: {e}")
        return False
    finally:
        if 'scraper' in locals() and scraper.driver:
            scraper.driver.quit()

def main():
    """Main function"""
    success = find_clickable_box_score()
    
    if success:
        logger.info("✅ Clickable Box Score finder completed successfully")
    else:
        logger.error("❌ Clickable Box Score finder failed")

if __name__ == "__main__":
    main()
