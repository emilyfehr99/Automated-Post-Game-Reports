#!/usr/bin/env python3
"""
AJHL Robust Scraper
Enhanced scraping system with better error handling, retry logic, and API-ready structure
"""

import json
import time
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import backoff
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingMethod(Enum):
    SELENIUM = "selenium"
    REQUESTS = "requests"
    HYBRID = "hybrid"

@dataclass
class ScrapingResult:
    """Standardized result structure for all scraping methods"""
    success: bool
    data: Dict[str, Any]
    method_used: ScrapingMethod
    timestamp: datetime
    error: Optional[str] = None
    retry_count: int = 0

class AJHLRobustScraper:
    """Enhanced scraper with multiple methods and robust error handling"""
    
    def __init__(self, headless: bool = True, user_identifier: str = None):
        """Initialize the robust scraper"""
        self.headless = headless
        self.user_identifier = user_identifier or "robust_scraper"
        self.driver = None
        self.session = None
        self.is_authenticated = False
        
        # Scraping configuration
        self.scraping_config = {
            "max_retries": 3,
            "retry_delay": 5,
            "timeout": 30,
            "preferred_method": ScrapingMethod.SELENIUM,
            "fallback_methods": [ScrapingMethod.REQUESTS, ScrapingMethod.HYBRID]
        }
        
        # API-ready data structure
        self.data_schema = {
            "team_info": {
                "team_id": str,
                "team_name": str,
                "league": str,
                "last_updated": str
            },
            "games": {
                "game_id": str,
                "date": str,
                "opponent": str,
                "home_away": str,
                "result": str,
                "data_files": List[str]
            },
            "players": {
                "player_id": str,
                "name": str,
                "position": str,
                "stats": Dict[str, Any]
            },
            "goaltenders": {
                "goalie_id": str,
                "name": str,
                "stats": Dict[str, Any]
            }
        }
    
    def setup_driver(self) -> bool:
        """Setup Chrome WebDriver with enhanced configuration"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            chrome_options.add_argument("--disable-css")
            
            # Add user-specific profile
            profile_dir = f"/tmp/hudl_profile_{self.user_identifier}"
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument(f"--profile-directory=Profile_{self.user_identifier}")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ Enhanced Chrome WebDriver initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Chrome WebDriver: {e}")
            return False
    
    def setup_session(self) -> bool:
        """Setup requests session for API-like calls"""
        try:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            logger.info("✅ Requests session initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup requests session: {e}")
            return False
    
    @backoff.on_exception(
        backoff.expo,
        (TimeoutException, NoSuchElementException, WebDriverException),
        max_tries=3,
        max_time=300
    )
    def authenticate_selenium(self, username: str, password: str) -> bool:
        """Authenticate using Selenium with retry logic"""
        if not self.driver:
            if not self.setup_driver():
                return False
        
        try:
            # Navigate to login page
            login_url = "https://app.hudl.com/login"
            self.driver.get(login_url)
            
            # Wait for login form with multiple selectors
            selectors = [
                "input[type='email']",
                "input[name='email']",
                "input[placeholder*='email']",
                "input[placeholder*='Email']"
            ]
            
            email_field = None
            for selector in selectors:
                try:
                    email_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not email_field:
                raise TimeoutException("Could not find email field")
            
            # Find password field
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
            # Fill form
            email_field.clear()
            email_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for redirect
            WebDriverWait(self.driver, 15).until(
                lambda driver: driver.current_url != login_url
            )
            
            if "login" not in self.driver.current_url.lower():
                self.is_authenticated = True
                logger.info("✅ Selenium authentication successful")
                return True
            else:
                logger.error("❌ Selenium authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Selenium authentication error: {e}")
            return False
    
    def authenticate_requests(self, username: str, password: str) -> bool:
        """Authenticate using requests session (API-like approach)"""
        if not self.session:
            if not self.setup_session():
                return False
        
        try:
            # Get login page to extract CSRF tokens
            login_url = "https://app.hudl.com/login"
            response = self.session.get(login_url)
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get login page: {response.status_code}")
                return False
            
            # Extract CSRF token if present
            csrf_token = None
            if 'csrf' in response.text.lower():
                # Look for CSRF token in various formats
                import re
                csrf_patterns = [
                    r'name="csrf_token"\s+value="([^"]+)"',
                    r'name="_token"\s+value="([^"]+)"',
                    r'"csrf_token":\s*"([^"]+)"'
                ]
                
                for pattern in csrf_patterns:
                    match = re.search(pattern, response.text)
                    if match:
                        csrf_token = match.group(1)
                        break
            
            # Prepare login data
            login_data = {
                'email': username,
                'password': password
            }
            
            if csrf_token:
                login_data['csrf_token'] = csrf_token
            
            # Submit login
            login_response = self.session.post(
                "https://app.hudl.com/login",
                data=login_data,
                allow_redirects=True
            )
            
            # Check if login was successful
            if "dashboard" in login_response.url.lower() or "instat" in login_response.url.lower():
                self.is_authenticated = True
                logger.info("✅ Requests authentication successful")
                return True
            else:
                logger.error("❌ Requests authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Requests authentication error: {e}")
            return False
    
    def authenticate(self, username: str, password: str, method: ScrapingMethod = None) -> bool:
        """Authenticate using preferred method with fallbacks"""
        method = method or self.scraping_config["preferred_method"]
        
        logger.info(f"🔐 Authenticating using {method.value} method...")
        
        if method == ScrapingMethod.SELENIUM:
            success = self.authenticate_selenium(username, password)
            if not success and ScrapingMethod.REQUESTS in self.scraping_config["fallback_methods"]:
                logger.info("🔄 Falling back to requests method...")
                success = self.authenticate_requests(username, password)
        elif method == ScrapingMethod.REQUESTS:
            success = self.authenticate_requests(username, password)
            if not success and ScrapingMethod.SELENIUM in self.scraping_config["fallback_methods"]:
                logger.info("🔄 Falling back to selenium method...")
                success = self.authenticate_selenium(username, password)
        else:
            # Try both methods
            success = self.authenticate_selenium(username, password)
            if not success:
                success = self.authenticate_requests(username, password)
        
        return success
    
    def scrape_team_data_selenium(self, team_id: str) -> ScrapingResult:
        """Scrape team data using Selenium"""
        if not self.driver or not self.is_authenticated:
            return ScrapingResult(
                success=False,
                data={},
                method_used=ScrapingMethod.SELENIUM,
                timestamp=datetime.now(),
                error="Driver not initialized or not authenticated"
            )
        
        try:
            team_url = f"https://app.hudl.com/instat/hockey/teams/{team_id}"
            self.driver.get(team_url)
            
            # Wait for page load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            
            # Extract team data
            team_data = self._extract_team_data_selenium()
            
            return ScrapingResult(
                success=True,
                data=team_data,
                method_used=ScrapingMethod.SELENIUM,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return ScrapingResult(
                success=False,
                data={},
                method_used=ScrapingMethod.SELENIUM,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    def scrape_team_data_requests(self, team_id: str) -> ScrapingResult:
        """Scrape team data using requests (API-like approach)"""
        if not self.session or not self.is_authenticated:
            return ScrapingResult(
                success=False,
                data={},
                method_used=ScrapingMethod.REQUESTS,
                timestamp=datetime.now(),
                error="Session not initialized or not authenticated"
            )
        
        try:
            # Try to find API endpoints
            api_endpoints = [
                f"https://app.hudl.com/api/instat/hockey/teams/{team_id}",
                f"https://app.hudl.com/instat/hockey/teams/{team_id}/data",
                f"https://api.hudl.com/instat/hockey/teams/{team_id}"
            ]
            
            team_data = {}
            for endpoint in api_endpoints:
                try:
                    response = self.session.get(endpoint)
                    if response.status_code == 200:
                        team_data = response.json()
                        break
                except:
                    continue
            
            if not team_data:
                # Fallback to scraping the HTML page
                team_url = f"https://app.hudl.com/instat/hockey/teams/{team_id}"
                response = self.session.get(team_url)
                
                if response.status_code == 200:
                    team_data = self._extract_team_data_requests(response.text)
                else:
                    raise Exception(f"Failed to get team page: {response.status_code}")
            
            return ScrapingResult(
                success=True,
                data=team_data,
                method_used=ScrapingMethod.REQUESTS,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return ScrapingResult(
                success=False,
                data={},
                method_used=ScrapingMethod.REQUESTS,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    def scrape_team_data(self, team_id: str, method: ScrapingMethod = None) -> ScrapingResult:
        """Scrape team data using preferred method with fallbacks"""
        method = method or self.scraping_config["preferred_method"]
        
        logger.info(f"📊 Scraping team {team_id} using {method.value} method...")
        
        if method == ScrapingMethod.SELENIUM:
            result = self.scrape_team_data_selenium(team_id)
            if not result.success and ScrapingMethod.REQUESTS in self.scraping_config["fallback_methods"]:
                logger.info("🔄 Falling back to requests method...")
                result = self.scrape_team_data_requests(team_id)
        elif method == ScrapingMethod.REQUESTS:
            result = self.scrape_team_data_requests(team_id)
            if not result.success and ScrapingMethod.SELENIUM in self.scraping_config["fallback_methods"]:
                logger.info("🔄 Falling back to selenium method...")
                result = self.scrape_team_data_selenium(team_id)
        else:
            # Try both methods
            result = self.scrape_team_data_selenium(team_id)
            if not result.success:
                result = self.scrape_team_data_requests(team_id)
        
        return result
    
    def _extract_team_data_selenium(self) -> Dict[str, Any]:
        """Extract team data from Selenium page"""
        try:
            team_data = {
                "team_info": {},
                "games": [],
                "players": [],
                "goaltenders": []
            }
            
            # Extract team info
            try:
                team_name = self.driver.find_element(By.CSS_SELECTOR, ".team-name, .PageCardUI__Name").text
                team_data["team_info"]["team_name"] = team_name
            except:
                pass
            
            # Extract games data
            try:
                game_elements = self.driver.find_elements(By.CSS_SELECTOR, ".game, .match, .game-item")
                for game in game_elements:
                    game_data = {
                        "game_id": game.get_attribute("data-game-id") or "",
                        "date": "",
                        "opponent": "",
                        "home_away": "",
                        "result": "",
                        "data_files": []
                    }
                    team_data["games"].append(game_data)
            except:
                pass
            
            return team_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting team data: {e}")
            return {}
    
    def _extract_team_data_requests(self, html_content: str) -> Dict[str, Any]:
        """Extract team data from HTML content"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            team_data = {
                "team_info": {},
                "games": [],
                "players": [],
                "goaltenders": []
            }
            
            # Extract team info
            team_name_elem = soup.find(class_="team-name") or soup.find(class_="PageCardUI__Name")
            if team_name_elem:
                team_data["team_info"]["team_name"] = team_name_elem.get_text().strip()
            
            # Extract games data
            game_elements = soup.find_all(class_=["game", "match", "game-item"])
            for game in game_elements:
                game_data = {
                    "game_id": game.get("data-game-id") or "",
                    "date": "",
                    "opponent": "",
                    "home_away": "",
                    "result": "",
                    "data_files": []
                }
                team_data["games"].append(game_data)
            
            return team_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting team data from HTML: {e}")
            return {}
    
    def get_api_ready_data(self, team_id: str) -> Dict[str, Any]:
        """Get data in API-ready format"""
        result = self.scrape_team_data(team_id)
        
        if result.success:
            # Transform data to API format
            api_data = {
                "success": True,
                "team_id": team_id,
                "method_used": result.method_used.value,
                "timestamp": result.timestamp.isoformat(),
                "data": result.data
            }
        else:
            api_data = {
                "success": False,
                "team_id": team_id,
                "error": result.error,
                "timestamp": result.timestamp.isoformat()
            }
        
        return api_data
    
    def close(self):
        """Close all resources"""
        if self.driver:
            self.driver.quit()
        if self.session:
            self.session.close()
        logger.info("🔒 Resources closed")

def main():
    """Main function to demonstrate the robust scraper"""
    print("🏒 AJHL Robust Scraper")
    print("=" * 40)
    
    scraper = AJHLRobustScraper(headless=False)
    
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        
        # Test authentication
        if scraper.authenticate(HUDL_USERNAME, HUDL_PASSWORD):
            print("✅ Authentication successful")
            
            # Test team data scraping
            team_id = "21479"  # Lloydminster Bobcats
            result = scraper.scrape_team_data(team_id)
            
            if result.success:
                print(f"✅ Team data scraped successfully using {result.method_used.value}")
                print(f"📊 Data: {json.dumps(result.data, indent=2)}")
            else:
                print(f"❌ Team data scraping failed: {result.error}")
            
            # Get API-ready data
            api_data = scraper.get_api_ready_data(team_id)
            print(f"🔌 API-ready data: {json.dumps(api_data, indent=2)}")
            
        else:
            print("❌ Authentication failed")
    
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
