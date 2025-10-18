#!/usr/bin/env python3
"""
Tableau Data Extractor for All Three Zones
Uses authenticated session to extract player data from Tableau visualizations
"""

import requests
import json
import logging
import re
from bs4 import BeautifulSoup
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TableauDataExtractor:
    """Extract data from Tableau visualizations on All Three Zones"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.allthreezones.com"
        self.is_authenticated = False
        
    def authenticate(self):
        """Authenticate with All Three Zones"""
        try:
            logger.info("🔐 Authenticating with All Three Zones...")
            
            # Get the login page first
            login_page = self.session.get(f"{self.base_url}/player-cards.html")
            
            # JSON-RPC authentication
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': self.base_url,
                'Referer': f'{self.base_url}/player-cards.html'
            }
            
            payload = {
                "method": "validate_user",
                "params": [Config.A3Z_USERNAME, Config.A3Z_PASSWORD],
                "id": 1
            }
            
            response = self.session.post(
                f'{self.base_url}/ajax/api/JsonRPC/Membership/',
                json=payload,
                headers=headers
            )
            
            logger.info(f"✅ Authentication response: {response.status_code}")
            
            # Check session details
            session_payload = {
                "method": "Member::get_session_details",
                "params": [],
                "id": 0
            }
            
            session_response = self.session.post(
                f'{self.base_url}/ajax/api/JsonRPC/Membership/',
                json=session_payload,
                headers=headers
            )
            
            if session_response.status_code == 200:
                session_data = session_response.json()
                if session_data.get('result', {}).get('data', {}).get('logged_in'):
                    self.is_authenticated = True
                    logger.info("✅ Successfully authenticated!")
                    return True
                else:
                    logger.error("❌ Authentication failed - not logged in")
                    return False
            else:
                logger.error(f"❌ Session check failed: {session_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def get_player_page(self, player_name=None):
        """Get the player cards page with authenticated session"""
        try:
            if not self.is_authenticated:
                if not self.authenticate():
                    return None
            
            logger.info(f"📊 Getting player page for: {player_name or 'all players'}")
            
            # Try different URLs that might contain player data
            urls_to_try = [
                f"{self.base_url}/player-cards.html",
                f"{self.base_url}/tableau-vizzes.html",
                f"{self.base_url}/apps/member/player-cards",
                f"{self.base_url}/apps/member/tableau"
            ]
            
            for url in urls_to_try:
                logger.info(f"🔍 Trying URL: {url}")
                response = self.session.get(url)
                
                if response.status_code == 200:
                    logger.info(f"✅ Successfully accessed: {url}")
                    
                    # Save the page for debugging
                    with open(f'player_page_{url.split("/")[-1]}.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    logger.info(f"✅ Saved page to player_page_{url.split('/')[-1]}.html")
                    
                    return response.text
                else:
                    logger.warning(f"⚠️  Failed to access {url}: {response.status_code}")
            
            logger.error("❌ Could not access any player pages")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting player page: {e}")
            return None
    
    def extract_tableau_urls(self, html_content):
        """Extract Tableau URLs from the HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            tableau_urls = []
            
            # Look for iframe src attributes
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src', '')
                if 'tableau' in src.lower():
                    tableau_urls.append(src)
                    logger.info(f"✅ Found Tableau iframe: {src}")
            
            # Look for script tags containing Tableau URLs
            scripts = soup.find_all('script')
            for script in scripts:
                script_text = script.get_text()
                # Look for Tableau URLs in JavaScript
                tableau_patterns = [
                    r'https?://[^"\s]*tableau[^"\s]*',
                    r'https?://[^"\s]*viz[^"\s]*',
                    r'https?://[^"\s]*embed[^"\s]*'
                ]
                
                for pattern in tableau_patterns:
                    matches = re.findall(pattern, script_text, re.IGNORECASE)
                    for match in matches:
                        if match not in tableau_urls:
                            tableau_urls.append(match)
                            logger.info(f"✅ Found Tableau URL in script: {match}")
            
            # Look for any URLs that might be Tableau
            all_urls = re.findall(r'https?://[^"\s]*', html_content)
            for url in all_urls:
                if any(keyword in url.lower() for keyword in ['tableau', 'viz', 'embed', 'public.tableau']):
                    if url not in tableau_urls:
                        tableau_urls.append(url)
                        logger.info(f"✅ Found potential Tableau URL: {url}")
            
            logger.info(f"✅ Found {len(tableau_urls)} Tableau URLs")
            return tableau_urls
            
        except Exception as e:
            logger.error(f"❌ Error extracting Tableau URLs: {e}")
            return []
    
    def extract_player_data_from_tableau(self, tableau_url):
        """Extract player data from a Tableau URL"""
        try:
            logger.info(f"📊 Extracting data from Tableau URL: {tableau_url}")
            
            # Try to access the Tableau URL
            response = self.session.get(tableau_url)
            
            if response.status_code == 200:
                logger.info("✅ Successfully accessed Tableau URL")
                
                # Save the Tableau page
                with open('tableau_page.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logger.info("✅ Saved Tableau page to tableau_page.html")
                
                # Look for JSON data in the page
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for script tags with data
                scripts = soup.find_all('script')
                for script in scripts:
                    script_text = script.get_text()
                    
                    # Look for JSON data
                    if 'data' in script_text.lower() and ('player' in script_text.lower() or 'stats' in script_text.lower()):
                        logger.info("✅ Found potential data in script")
                        logger.info(f"Script content: {script_text[:500]}...")
                
                return response.text
            else:
                logger.warning(f"⚠️  Failed to access Tableau URL: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error extracting data from Tableau: {e}")
            return None
    
    def search_for_player(self, player_name):
        """Search for a specific player"""
        try:
            logger.info(f"🔍 Searching for player: {player_name}")
            
            # Get the player page
            html_content = self.get_player_page(player_name)
            
            if not html_content:
                logger.error("❌ Could not get player page")
                return []
            
            # Extract Tableau URLs
            tableau_urls = self.extract_tableau_urls(html_content)
            
            if not tableau_urls:
                logger.warning("⚠️  No Tableau URLs found")
                return []
            
            # Try to extract data from each Tableau URL
            player_data = []
            for url in tableau_urls:
                data = self.extract_player_data_from_tableau(url)
                if data:
                    player_data.append({
                        'player_name': player_name,
                        'tableau_url': url,
                        'data': data
                    })
            
            logger.info(f"✅ Found data for {len(player_data)} Tableau visualizations")
            return player_data
            
        except Exception as e:
            logger.error(f"❌ Error searching for player: {e}")
            return []

def main():
    """Main function to test the Tableau data extractor"""
    logger.info("🏒 All Three Zones Tableau Data Extractor")
    logger.info("=" * 60)
    
    extractor = TableauDataExtractor()
    
    # Test authentication
    if not extractor.authenticate():
        logger.error("❌ Authentication failed")
        return
    
    # Test getting player page
    html_content = extractor.get_player_page()
    
    if html_content:
        # Extract Tableau URLs
        tableau_urls = extractor.extract_tableau_urls(html_content)
        
        if tableau_urls:
            logger.info(f"✅ Found {len(tableau_urls)} Tableau URLs")
            for i, url in enumerate(tableau_urls):
                logger.info(f"  {i+1}. {url}")
            
            # Try to extract data from the first URL
            if tableau_urls:
                data = extractor.extract_player_data_from_tableau(tableau_urls[0])
                if data:
                    logger.info("✅ Successfully extracted Tableau data!")
                else:
                    logger.warning("⚠️  Could not extract data from Tableau")
        else:
            logger.warning("⚠️  No Tableau URLs found")
    
    logger.info("\n🎉 Tableau data extraction test completed!")

if __name__ == "__main__":
    main() 