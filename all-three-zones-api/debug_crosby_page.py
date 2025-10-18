#!/usr/bin/env python3
"""
Debug script to examine the page content and understand why we're not finding Sidney Crosby data
"""

import requests
from bs4 import BeautifulSoup
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_crosby_page():
    """Debug the page content to understand why we're not finding Crosby data"""
    logger.info("🔍 Debugging Sidney Crosby Page Content")
    logger.info("=" * 60)
    
    try:
        # Import config for credentials
        from config import Config
        
        session = requests.Session()
        
        # Login first
        login_data = {
            'login-email': Config.A3Z_USERNAME,
            'login-password': Config.A3Z_PASSWORD,
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.allthreezones.com',
            'Referer': 'https://www.allthreezones.com/player-cards.html'
        }
        
        # Login
        logger.info("1. Attempting login...")
        login_response = session.post(
            'https://www.allthreezones.com/ajax/api/JsonRPC/Membership/',
            data=login_data,
            headers=headers,
            allow_redirects=True
        )
        
        logger.info(f"✅ Login status: {login_response.status_code}")
        
        # Get the player cards page
        logger.info("\n2. Getting player cards page...")
        player_cards_url = "https://www.allthreezones.com/player-cards.html"
        response = session.get(player_cards_url)
        
        logger.info(f"✅ Player cards status: {response.status_code}")
        logger.info(f"✅ Final URL: {response.url}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Save the page content for inspection
        with open('debug_crosby_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        logger.info("✅ Saved page content to debug_crosby_page.html")
        
        # Check if we're still on login page
        if "Log In" in response.text:
            logger.error("❌ Still on login page - authentication failed")
            return False
        
        logger.info("✅ Successfully authenticated!")
        
        # Look for page title
        title = soup.title.get_text() if soup.title else "No title"
        logger.info(f"\n3. Page title: {title}")
        
        # Look for any content containing "Crosby"
        logger.info("\n4. Searching for Crosby content...")
        crosby_elements = soup.find_all(text=lambda text: text and 'crosby' in text.lower())
        logger.info(f"✅ Found {len(crosby_elements)} elements containing 'crosby'")
        
        for i, elem in enumerate(crosby_elements[:5]):  # Show first 5
            logger.info(f"  Element {i+1}: '{elem.strip()}'")
        
        # Look for any content containing "Sidney"
        logger.info("\n5. Searching for Sidney content...")
        sidney_elements = soup.find_all(text=lambda text: text and 'sidney' in text.lower())
        logger.info(f"✅ Found {len(sidney_elements)} elements containing 'sidney'")
        
        for i, elem in enumerate(sidney_elements[:5]):  # Show first 5
            logger.info(f"  Element {i+1}: '{elem.strip()}'")
        
        # Look for iframes
        logger.info("\n6. Examining iframes...")
        iframes = soup.find_all('iframe')
        logger.info(f"✅ Found {len(iframes)} iframes")
        
        for i, iframe in enumerate(iframes):
            src = iframe.get('src', 'No src')
            title = iframe.get('title', 'No title')
            class_names = iframe.get('class', [])
            logger.info(f"  Iframe {i+1}:")
            logger.info(f"    Src: {src}")
            logger.info(f"    Title: {title}")
            logger.info(f"    Classes: {class_names}")
        
        # Look for Tableau-specific elements
        logger.info("\n7. Examining Tableau elements...")
        tableau_elements = soup.find_all(class_=lambda x: x and 'tableau' in x.lower())
        logger.info(f"✅ Found {len(tableau_elements)} Tableau elements")
        
        for i, elem in enumerate(tableau_elements):
            logger.info(f"  Tableau element {i+1}:")
            logger.info(f"    Tag: {elem.name}")
            logger.info(f"    Classes: {elem.get('class', [])}")
            logger.info(f"    Text: {elem.get_text()[:100]}...")
        
        # Look for any script tags that might contain Tableau
        logger.info("\n8. Examining scripts for Tableau...")
        scripts = soup.find_all('script')
        tableau_scripts = []
        
        for script in scripts:
            script_text = script.get_text()
            if 'tableau' in script_text.lower():
                tableau_scripts.append(script)
        
        logger.info(f"✅ Found {len(tableau_scripts)} scripts containing 'tableau'")
        
        for i, script in enumerate(tableau_scripts):
            logger.info(f"  Script {i+1}:")
            script_text = script.get_text()
            # Look for URLs in the script
            if 'http' in script_text:
                lines = script_text.split('\n')
                for line in lines:
                    if 'http' in line and 'tableau' in line.lower():
                        logger.info(f"    Found Tableau URL: {line.strip()}")
        
        # Look for any div elements that might contain player data
        logger.info("\n9. Examining div elements for player data...")
        player_divs = soup.find_all('div', class_=lambda x: x and any(word in x.lower() for word in ['player', 'card', 'stat', 'data', 'table']))
        logger.info(f"✅ Found {len(player_divs)} potential player-related divs")
        
        for i, div in enumerate(player_divs[:10]):  # Show first 10
            class_names = div.get('class', [])
            text = div.get_text(strip=True)[:200]  # First 200 chars
            logger.info(f"  Div {i+1} classes: {class_names}")
            logger.info(f"  Text: {text}")
        
        # Look for any tables
        logger.info("\n10. Examining tables...")
        tables = soup.find_all('table')
        logger.info(f"✅ Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            logger.info(f"  Table {i+1}: {len(rows)} rows")
            if rows:
                # Show first few rows
                for j, row in enumerate(rows[:3]):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    logger.info(f"    Row {j+1}: {cell_texts}")
        
        logger.info("\n🎉 Page analysis completed!")
        logger.info("\nNext steps:")
        logger.info("1. Check debug_crosby_page.html for full page content")
        logger.info("2. Look for Tableau iframe URLs in the scripts")
        logger.info("3. Examine the page structure to understand data location")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during page analysis: {e}")
        return False

if __name__ == "__main__":
    debug_crosby_page() 