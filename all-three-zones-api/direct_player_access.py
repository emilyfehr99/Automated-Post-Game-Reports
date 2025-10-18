#!/usr/bin/env python3
"""
Direct Player Access for All Three Zones
Mimics browser behavior to access player data directly
"""

import requests
import json
import logging
import time
from bs4 import BeautifulSoup
from config import Config
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectPlayerAccess:
    """Direct access to player data mimicking browser behavior"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.allthreezones.com"
        
    def setup_session(self):
        """Setup session with proper headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def login(self):
        """Login using form-based approach"""
        try:
            logger.info("🔐 Attempting login...")
            
            # Step 1: Get the login page
            login_page = self.session.get(f"{self.base_url}/player-cards.html")
            logger.info(f"✅ Login page status: {login_page.status_code}")
            
            # Step 2: Try form-based login
            form_data = {
                'login-email': Config.A3Z_USERNAME,
                'login-password': Config.A3Z_PASSWORD
            }
            
            form_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': self.base_url,
                'Referer': f'{self.base_url}/player-cards.html'
            }
            
            # Try different login endpoints
            login_endpoints = [
                f"{self.base_url}/player-cards.html",
                f"{self.base_url}/apps/member/login",
                f"{self.base_url}/ajax/api/JsonRPC/Membership/"
            ]
            
            for endpoint in login_endpoints:
                logger.info(f"🔍 Trying login endpoint: {endpoint}")
                
                if 'JsonRPC' in endpoint:
                    # JSON-RPC approach
                    payload = {
                        "method": "validate_user",
                        "params": [Config.A3Z_USERNAME, Config.A3Z_PASSWORD],
                        "id": 1
                    }
                    
                    headers = {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Origin': self.base_url,
                        'Referer': f'{self.base_url}/player-cards.html'
                    }
                    
                    response = self.session.post(endpoint, json=payload, headers=headers)
                else:
                    # Form-based approach
                    response = self.session.post(endpoint, data=form_data, headers=form_headers)
                
                logger.info(f"✅ {endpoint} status: {response.status_code}")
                
                if response.status_code == 200:
                    logger.info(f"✅ Success with {endpoint}")
                    break
            
            # Step 3: Try to access the player cards page
            logger.info("🔍 Testing player cards access...")
            
            player_response = self.session.get(f"{self.base_url}/player-cards.html")
            logger.info(f"✅ Player cards status: {player_response.status_code}")
            logger.info(f"✅ Player cards URL: {player_response.url}")
            
            # Check if we're still on login page
            if "Log In" in player_response.text:
                logger.warning("⚠️  Still on login page, but continuing...")
            else:
                logger.info("✅ Successfully accessed player cards!")
            
            # Save the response for debugging
            with open('direct_player_access.html', 'w', encoding='utf-8') as f:
                f.write(player_response.text)
            logger.info("✅ Saved response to direct_player_access.html")
            
            return player_response.text
            
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return None
    
    def search_for_crosby(self):
        """Search for Sidney Crosby specifically"""
        try:
            logger.info("🔍 Searching for Sidney Crosby...")
            
            # Get the player page
            html_content = self.login()
            
            if not html_content:
                logger.error("❌ Could not get player page")
                return None
            
            # Parse the HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for any content containing "Crosby" or "Sidney"
            logger.info("🔍 Searching for Crosby content...")
            
            crosby_elements = soup.find_all(text=lambda text: text and 'crosby' in text.lower())
            sidney_elements = soup.find_all(text=lambda text: text and 'sidney' in text.lower())
            
            logger.info(f"✅ Found {len(crosby_elements)} elements containing 'crosby'")
            logger.info(f"✅ Found {len(sidney_elements)} elements containing 'sidney'")
            
            # Look for iframes that might contain Tableau
            iframes = soup.find_all('iframe')
            logger.info(f"✅ Found {len(iframes)} iframes")
            
            for i, iframe in enumerate(iframes):
                src = iframe.get('src', '')
                title = iframe.get('title', '')
                logger.info(f"  Iframe {i+1}: src={src}, title={title}")
            
            # Look for any URLs in the page
            all_urls = re.findall(r'https?://[^"\s]*', html_content)
            tableau_urls = [url for url in all_urls if any(keyword in url.lower() for keyword in ['tableau', 'viz', 'embed'])]
            
            logger.info(f"✅ Found {len(tableau_urls)} potential Tableau URLs")
            for url in tableau_urls:
                logger.info(f"  Tableau URL: {url}")
            
            # Try to access any Tableau URLs we found
            for url in tableau_urls:
                logger.info(f"🔍 Trying to access: {url}")
                try:
                    response = self.session.get(url)
                    if response.status_code == 200:
                        logger.info(f"✅ Successfully accessed: {url}")
                        
                        # Save the Tableau page
                        with open(f'tableau_{url.split("/")[-1]}.html', 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        logger.info(f"✅ Saved Tableau page to tableau_{url.split('/')[-1]}.html")
                        
                        # Look for player data in the response
                        if 'crosby' in response.text.lower() or 'sidney' in response.text.lower():
                            logger.info("✅ Found Crosby data in Tableau response!")
                        else:
                            logger.info("⚠️  No Crosby data found in this Tableau page")
                    else:
                        logger.warning(f"⚠️  Failed to access {url}: {response.status_code}")
                except Exception as e:
                    logger.error(f"❌ Error accessing {url}: {e}")
            
            return {
                'crosby_elements': len(crosby_elements),
                'sidney_elements': len(sidney_elements),
                'iframes': len(iframes),
                'tableau_urls': tableau_urls
            }
            
        except Exception as e:
            logger.error(f"❌ Error searching for Crosby: {e}")
            return None

def main():
    """Main function to test direct player access"""
    logger.info("🏒 Direct Player Access Test")
    logger.info("=" * 50)
    
    access = DirectPlayerAccess()
    access.setup_session()
    
    result = access.search_for_crosby()
    
    if result:
        logger.info("🎉 Direct access test completed!")
        logger.info(f"Found {result['crosby_elements']} Crosby elements")
        logger.info(f"Found {result['sidney_elements']} Sidney elements")
        logger.info(f"Found {result['iframes']} iframes")
        logger.info(f"Found {len(result['tableau_urls'])} Tableau URLs")
    else:
        logger.error("❌ Direct access test failed")

if __name__ == "__main__":
    main() 