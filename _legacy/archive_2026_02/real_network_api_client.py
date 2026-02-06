#!/usr/bin/env python3
"""
Real Network API Client for Hudl Instat
Based on actual network request from browser dev tools
"""

import time
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RealNetworkAPIConfig:
    """Configuration based on real network request"""
    base_url: str = "https://www.hudl.com/app/metropole/shim/api-hockey.instatscout.com"
    api_endpoint: str = "/data"
    session: Optional[requests.Session] = None
    
    def __post_init__(self):
        if self.session is None:
            self.session = requests.Session()
            # Set headers based on real network request
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://app.hudl.com/instat/hockey/teams/21479',
                'Origin': 'https://app.hudl.com',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"'
            })

class RealNetworkAPIClient:
    """API client based on real network request structure"""
    
    def __init__(self, config: RealNetworkAPIConfig = None):
        self.config = config or RealNetworkAPIConfig()
        self.session = self.config.session
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Set up Chrome driver for authentication"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 30)
            logger.info("✅ Chrome driver setup successful")
            return True
        except Exception as e:
            logger.error(f"❌ Driver setup failed: {e}")
            return False
        
    def login_and_get_auth(self, username: str, password: str) -> bool:
        """Login and extract all authentication data"""
        try:
            logger.info("🔐 Logging into Hudl Instat to get authentication...")
            
            # Go to Hudl Instat
            self.driver.get("https://app.hudl.com/instat/hockey")
            time.sleep(5)
            
            # Find username field
            username_field = self.driver.find_element(By.ID, "username")
            username_field.clear()
            username_field.send_keys(username)
            
            # Find and click Continue button
            continue_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'][name='action'][value='default']")
            continue_button.click()
            time.sleep(5)
            
            # Find password field
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_field.clear()
            password_field.send_keys(password)
            
            # Find and click submit button
            submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")
            if submit_buttons:
                submit_buttons[0].click()
                time.sleep(10)
                
                # Check if login was successful
                if "login" not in self.driver.current_url.lower() and "identity" not in self.driver.current_url.lower():
                    logger.info("✅ Login successful!")
                    
                    # Extract cookies and set them in the session
                    cookies = self.driver.get_cookies()
                    for cookie in cookies:
                        self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
                    
                    # Extract additional headers that might be needed
                    self._extract_additional_headers()
                    
                    logger.info(f"🍪 Extracted {len(cookies)} cookies for API calls")
                    return True
                else:
                    logger.error("❌ Login failed - still on login page")
                    return False
            else:
                logger.error("❌ No submit button found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False
    
    def _extract_additional_headers(self):
        """Extract additional headers that might be needed for API calls"""
        try:
            # Get current page headers
            current_headers = self.driver.execute_script("""
                return {
                    'userAgent': navigator.userAgent,
                    'language': navigator.language,
                    'platform': navigator.platform,
                    'cookie': document.cookie
                };
            """)
            
            # Update session headers with browser data
            if current_headers:
                self.session.headers.update({
                    'User-Agent': current_headers.get('userAgent', self.session.headers.get('User-Agent')),
                    'Accept-Language': current_headers.get('language', 'en-US,en;q=0.9'),
                })
            
            logger.info("✅ Additional headers extracted from browser")
            
        except Exception as e:
            logger.error(f"❌ Error extracting additional headers: {e}")
    
    def _make_request(self, proc: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Hudl Instat API using real network structure"""
        url = f"{self.config.base_url}{self.config.api_endpoint}"
        
        # Based on the real network request structure
        payload = {
            "body": {
                "params": params,
                "proc": proc
            }
        }
        
        logger.info(f"🔗 Making API request to {proc}")
        logger.info(f"📊 Params: {params}")
        logger.info(f"🌐 URL: {url}")
        
        try:
            response = self.session.post(url, json=payload)
            
            logger.info(f"📊 Response status: {response.status_code}")
            logger.info(f"📊 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ API request successful for {proc}")
                return data
            else:
                logger.error(f"❌ API request failed for {proc}: {response.status_code}")
                logger.error(f"❌ Response: {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API request failed for {proc}: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error for {proc}: {e}")
            return {}
    
    def get_team_statistics(self, team_id: str, season_id: str = "34", tournament_id: str = None) -> Dict[str, Any]:
        """Get team statistics using scout_uni_overview_team_stat"""
        params = {
            "_p_team_id": team_id,
            "_p_season_id": season_id
        }
        
        if tournament_id:
            params["_p_tournament_id"] = tournament_id
            
        return self._make_request("scout_uni_overview_team_stat", params)
    
    def get_team_players(self, team_id: str, season_id: str = "34", tournament_id: str = None) -> Dict[str, Any]:
        """Get team players using scout_uni_overview_team_players"""
        params = {
            "_p_team_id": team_id,
            "_p_season_id": season_id
        }
        
        if tournament_id:
            params["_p_tournament_id"] = tournament_id
            
        return self._make_request("scout_uni_overview_team_players", params)
    
    def get_lexical_parameters(self, phrase_ids: List[int], lang: str = "en") -> Dict[str, Any]:
        """Get lexical parameters using scout_param_lexical"""
        params = {
            "lang": lang,
            "phrases": phrase_ids
        }
        
        return self._make_request("scout_param_lexical", params)
    
    def get_comprehensive_team_data(self, team_id: str, season_id: str = "34", tournament_id: str = None) -> Dict[str, Any]:
        """Get comprehensive team data"""
        logger.info(f"🚀 Getting comprehensive data for team {team_id}")
        
        # Get team statistics
        team_stats = self.get_team_statistics(team_id, season_id, tournament_id)
        
        # Get team players
        team_players = self.get_team_players(team_id, season_id, tournament_id)
        
        # Extract phrase IDs for lexical parameters
        phrase_ids = []
        if team_stats and 'data' in team_stats:
            phrase_ids = self._extract_phrase_ids(team_stats['data'])
        
        # Get lexical parameters
        lexical_params = {}
        if phrase_ids:
            lexical_params = self.get_lexical_parameters(phrase_ids)
        
        return {
            'team_statistics': team_stats,
            'team_players': team_players,
            'lexical_parameters': lexical_params,
            'team_id': team_id,
            'season_id': season_id,
            'tournament_id': tournament_id
        }
    
    def _extract_phrase_ids(self, data: List[Dict]) -> List[int]:
        """Extract phrase IDs from the data structure"""
        phrase_ids = []
        
        for item in data:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, (int, str)) and str(value).isdigit():
                        phrase_ids.append(int(value))
                    elif isinstance(value, dict):
                        phrase_ids.extend(self._extract_phrase_ids([value]))
        
        return list(set(phrase_ids))
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()

def main():
    """Test the real network API client"""
    client = RealNetworkAPIClient()
    
    try:
        # Setup driver
        if not client.setup_driver():
            logger.error("❌ Driver setup failed")
            return
        
        # Login and get authentication
        username = "chaserochon777@gmail.com"
        password = "357Chaser!468"
        
        if not client.login_and_get_auth(username, password):
            logger.error("❌ Authentication failed")
            return
        
        # Test with Lloydminster Bobcats (team_id: 21479)
        team_id = "21479"
        season_id = "34"
        
        logger.info(f"🧪 Testing real network API client with team {team_id}")
        
        # Test team statistics
        team_stats = client.get_team_statistics(team_id, season_id)
        logger.info(f"📊 Team stats response: {len(str(team_stats))} characters")
        
        # Test team players
        team_players = client.get_team_players(team_id, season_id)
        logger.info(f"👥 Team players response: {len(str(team_players))} characters")
        
        # Test comprehensive data
        comprehensive_data = client.get_comprehensive_team_data(team_id, season_id)
        logger.info(f"🎯 Comprehensive data: {len(str(comprehensive_data))} characters")
        
        # Save results for analysis
        with open("real_network_api_results.json", "w") as f:
            json.dump(comprehensive_data, f, indent=2)
        
        logger.info("✅ Real network API test results saved to real_network_api_results.json")
        
    finally:
        client.close()

if __name__ == "__main__":
    main()
