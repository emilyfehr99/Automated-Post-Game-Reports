#!/usr/bin/env python3
"""
Debug script to examine the page content and find Tableau iframe
"""

import requests
from bs4 import BeautifulSoup
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_tableau_page():
    """Debug the page content to find Tableau iframe"""
    try:
        session = requests.Session()
        
        # Import config for credentials
        from config import Config
        
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
        login_response = session.post(
            'https://www.allthreezones.com/ajax/api/JsonRPC/Membership/',
            data=login_data,
            headers=headers,
            allow_redirects=True
        )
        
        print(f"Login status: {login_response.status_code}")
        
        # Get the player cards page
        player_cards_url = "https://www.allthreezones.com/player-cards.html"
        response = session.get(player_cards_url)
        
        print(f"Player cards status: {response.status_code}")
        print(f"Player cards URL: {response.url}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Save the page content
        with open('debug_player_cards.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Saved page content to debug_player_cards.html")
        
        # Look for iframes
        iframes = soup.find_all('iframe')
        print(f"\nFound {len(iframes)} iframes:")
        
        for i, iframe in enumerate(iframes):
            src = iframe.get('src', 'No src')
            title = iframe.get('title', 'No title')
            class_names = iframe.get('class', [])
            print(f"  Iframe {i+1}:")
            print(f"    Src: {src}")
            print(f"    Title: {title}")
            print(f"    Classes: {class_names}")
        
        # Look for Tableau-specific elements
        tableau_elements = soup.find_all(class_=lambda x: x and 'tableau' in x.lower())
        print(f"\nFound {len(tableau_elements)} Tableau elements:")
        
        for i, elem in enumerate(tableau_elements):
            print(f"  Tableau element {i+1}:")
            print(f"    Tag: {elem.name}")
            print(f"    Classes: {elem.get('class', [])}")
            print(f"    Text: {elem.get_text()[:100]}...")
        
        # Look for any script tags that might contain Tableau
        scripts = soup.find_all('script')
        tableau_scripts = []
        
        for script in scripts:
            script_text = script.get_text()
            if 'tableau' in script_text.lower():
                tableau_scripts.append(script)
        
        print(f"\nFound {len(tableau_scripts)} scripts containing 'tableau':")
        
        for i, script in enumerate(tableau_scripts):
            print(f"  Script {i+1}:")
            script_text = script.get_text()
            # Look for URLs in the script
            import re
            urls = re.findall(r'https?://[^\s"\'<>]+', script_text)
            for url in urls[:3]:  # Show first 3 URLs
                print(f"    URL: {url}")
        
        # Check if we're still on login page
        if "Log In" in response.text:
            print("\n❌ Still on login page - authentication failed")
        else:
            print("\n✅ Successfully accessed player cards page")
            
            # Look for any content that might indicate we're on the right page
            page_text = response.text.lower()
            if 'player' in page_text:
                print("✅ Found 'player' in page content")
            if 'tableau' in page_text:
                print("✅ Found 'tableau' in page content")
            if 'card' in page_text:
                print("✅ Found 'card' in page content")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_tableau_page() 