#!/usr/bin/env python3
"""
Find Box Score Button
Simple script to find and click the Box Score button
"""

import time
import json
import logging
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_box_score_button():
    """Find and click the Box Score button"""
    try:
        logger.info("🚀 Starting Box Score Button Finder...")
        
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
        
        # Get all elements on the page
        logger.info("🔍 Getting all elements on the page...")
        all_elements = scraper.driver.execute_script("""
            var elements = [];
            var allElements = document.querySelectorAll('*');
            
            for (var i = 0; i < allElements.length; i++) {
                var element = allElements[i];
                var text = element.innerText.trim();
                var title = element.title || '';
                var className = element.className || '';
                var id = element.id || '';
                var dataLexic = element.getAttribute('data-lexic') || '';
                
                if (text || title || className || id || dataLexic) {
                    elements.push({
                        text: text,
                        title: title,
                        className: className,
                        id: id,
                        dataLexic: dataLexic,
                        tagName: element.tagName
                    });
                }
            }
            
            return elements;
        """)
        
        logger.info(f"📊 Found {len(all_elements)} elements on the page")
        
        # Look for Box Score related elements
        box_score_elements = []
        for element in all_elements:
            text = element.get('text', '').lower()
            title = element.get('title', '').lower()
            className = element.get('className', '').lower()
            data_lexic = element.get('dataLexic', '')
            
            if (('box' in text and 'score' in text) or 
                ('box' in title and 'score' in title) or
                ('box' in className and 'score' in className) or
                data_lexic == '3605'):
                box_score_elements.append(element)
        
        logger.info(f"📊 Found {len(box_score_elements)} Box Score related elements")
        
        # Show Box Score elements
        for i, element in enumerate(box_score_elements):
            logger.info(f"  Box Score {i+1}:")
            logger.info(f"    Text: '{element.get('text', '')}'")
            logger.info(f"    Title: '{element.get('title', '')}'")
            logger.info(f"    Class: '{element.get('className', '')}'")
            logger.info(f"    ID: '{element.get('id', '')}'")
            logger.info(f"    Data-lexic: '{element.get('dataLexic', '')}'")
            logger.info(f"    Tag: '{element.get('tagName', '')}'")
            logger.info("")
        
        # Look for Select All related elements
        select_all_elements = []
        for element in all_elements:
            text = element.get('text', '').lower()
            title = element.get('title', '').lower()
            className = element.get('className', '').lower()
            data_lexic = element.get('dataLexic', '')
            
            if (('select' in text and 'all' in text) or 
                ('select' in title and 'all' in title) or
                ('select' in className and 'all' in className) or
                data_lexic == '4239'):
                select_all_elements.append(element)
        
        logger.info(f"📊 Found {len(select_all_elements)} Select All related elements")
        
        # Show Select All elements
        for i, element in enumerate(select_all_elements):
            logger.info(f"  Select All {i+1}:")
            logger.info(f"    Text: '{element.get('text', '')}'")
            logger.info(f"    Title: '{element.get('title', '')}'")
            logger.info(f"    Class: '{element.get('className', '')}'")
            logger.info(f"    ID: '{element.get('id', '')}'")
            logger.info(f"    Data-lexic: '{element.get('dataLexic', '')}'")
            logger.info(f"    Tag: '{element.get('tagName', '')}'")
            logger.info("")
        
        # Look for Download XLS related elements
        download_elements = []
        for element in all_elements:
            text = element.get('text', '').lower()
            title = element.get('title', '').lower()
            className = element.get('className', '').lower()
            data_lexic = element.get('dataLexic', '')
            
            if (('download' in text and 'xls' in text) or 
                ('download' in title and 'xls' in title) or
                ('download' in className and 'xls' in className) or
                data_lexic == '3148'):
                download_elements.append(element)
        
        logger.info(f"📊 Found {len(download_elements)} Download XLS related elements")
        
        # Show Download elements
        for i, element in enumerate(download_elements):
            logger.info(f"  Download {i+1}:")
            logger.info(f"    Text: '{element.get('text', '')}'")
            logger.info(f"    Title: '{element.get('title', '')}'")
            logger.info(f"    Class: '{element.get('className', '')}'")
            logger.info(f"    ID: '{element.get('id', '')}'")
            logger.info(f"    Data-lexic: '{element.get('dataLexic', '')}'")
            logger.info(f"    Tag: '{element.get('tagName', '')}'")
            logger.info("")
        
        # Save results
        results = {
            'box_score_elements': box_score_elements,
            'select_all_elements': select_all_elements,
            'download_elements': download_elements,
            'total_elements': len(all_elements)
        }
        
        with open('box_score_elements.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("✅ Results saved to box_score_elements.json")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in find box score button: {e}")
        return False
    finally:
        if 'scraper' in locals() and scraper.driver:
            scraper.driver.quit()

def main():
    """Main function"""
    success = find_box_score_button()
    
    if success:
        logger.info("✅ Box Score button finder completed successfully")
    else:
        logger.error("❌ Box Score button finder failed")

if __name__ == "__main__":
    main()
