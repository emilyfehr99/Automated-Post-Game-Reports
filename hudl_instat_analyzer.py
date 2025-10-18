#!/usr/bin/env python3
"""
Hudl Instat Site Analyzer and Mini API
Analyzes the structure of Hudl Instat hockey team pages and creates a mini API wrapper

⚠️  LEGAL DISCLAIMER:
This tool is for educational purposes only. Ensure you have proper authorization
from Hudl before using this for any commercial purposes. Review Hudl's Terms of
Service and consider contacting them about official API access.
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class HudlTeamData:
    """Data structure for Hudl team information"""
    team_id: str
    team_name: str
    league: str
    season: str
    players: List[Dict[str, Any]]
    games: List[Dict[str, Any]]
    stats: Dict[str, Any]
    last_updated: str

class HudlInstatAnalyzer:
    """Analyzer for Hudl Instat hockey team pages"""
    
    def __init__(self, headless: bool = True, user_identifier: str = None):
        """Initialize the Hudl Instat analyzer"""
        self.base_url = "https://app.hudl.com/instat/hockey/teams"
        self.session = requests.Session()
        self.driver = None
        self.headless = headless
        self.is_authenticated = False
        self.user_identifier = user_identifier or "default_user"
        self.session_id = None
        
        # Setup session headers with unique user agent to avoid conflicts
        unique_ua = f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 HudlAPI-{self.user_identifier}'
        self.session.headers.update({
            'User-Agent': unique_ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        })
    
    def setup_driver(self):
        """Setup Chrome WebDriver for JavaScript-heavy sites"""
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
            chrome_options.add_argument("--disable-images")  # Faster loading
            
            # Add user-specific profile to avoid session conflicts
            profile_dir = f"/tmp/hudl_profile_{self.user_identifier}"
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument(f"--profile-directory=Profile_{self.user_identifier}")
            
            # Additional options to prevent conflicts
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            # Find Chrome binary
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser"
            ]
            
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_options.binary_location = path
                    break
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Chrome WebDriver: {e}")
            return False
    
    def analyze_site_structure(self, team_id: str) -> Dict[str, Any]:
        """Analyze the structure of a Hudl Instat team page"""
        if not self.driver:
            if not self.setup_driver():
                return {"error": "Failed to initialize WebDriver"}
        
        team_url = f"{self.base_url}/{team_id}"
        logger.info(f"🔍 Analyzing Hudl Instat team page: {team_url}")
        
        try:
            # Navigate to the team page
            self.driver.get(team_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if we're redirected to login
            current_url = self.driver.current_url
            if "login" in current_url.lower() or "signin" in current_url.lower():
                logger.warning("🔒 Page requires authentication - redirected to login")
                return {
                    "requires_auth": True,
                    "login_url": current_url,
                    "team_id": team_id,
                    "analysis": "Authentication required to access team data"
                }
            
            # Analyze page structure
            analysis = {
                "team_id": team_id,
                "url": team_url,
                "current_url": current_url,
                "requires_auth": False,
                "page_title": self.driver.title,
                "elements_found": {},
                "api_endpoints": [],
                "data_structure": {}
            }
            
            # Look for common data elements
            try:
                # Check for team name
                team_name_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "h1, .team-name, .team-title, [data-testid*='team']")
                if team_name_elements:
                    analysis["elements_found"]["team_name"] = [el.text for el in team_name_elements if el.text.strip()]
                
                # Look for player data
                player_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    ".player, .roster-item, [data-testid*='player']")
                analysis["elements_found"]["players"] = len(player_elements)
                
                # Look for game data
                game_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    ".game, .match, [data-testid*='game']")
                analysis["elements_found"]["games"] = len(game_elements)
                
                # Look for stats/analytics sections
                stats_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    ".stats, .analytics, .metrics, [data-testid*='stat']")
                analysis["elements_found"]["stats"] = len(stats_elements)
                
            except Exception as e:
                logger.warning(f"⚠️  Error analyzing page elements: {e}")
            
            # Look for API calls in network traffic
            try:
                # Get network logs (if available)
                logs = self.driver.get_log('performance')
                api_calls = []
                for log in logs:
                    message = json.loads(log['message'])
                    if message['message']['method'] == 'Network.responseReceived':
                        url = message['message']['params']['response']['url']
                        if any(keyword in url.lower() for keyword in ['api', 'data', 'json', 'ajax']):
                            api_calls.append(url)
                
                analysis["api_endpoints"] = api_calls[:10]  # Limit to first 10
                
            except Exception as e:
                logger.warning(f"⚠️  Could not analyze network traffic: {e}")
            
            # Analyze page source for data patterns
            page_source = self.driver.page_source
            
            # Look for JSON data in script tags
            import re
            json_pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});'
            json_matches = re.findall(json_pattern, page_source)
            if json_matches:
                try:
                    initial_state = json.loads(json_matches[0])
                    analysis["data_structure"]["initial_state"] = initial_state
                except:
                    pass
            
            # Look for other data patterns
            data_patterns = [
                r'window\.__DATA__\s*=\s*({.*?});',
                r'window\.teamData\s*=\s*({.*?});',
                r'window\.playerData\s*=\s*({.*?});'
            ]
            
            for pattern in data_patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    try:
                        data = json.loads(matches[0])
                        analysis["data_structure"]["embedded_data"] = data
                        break
                    except:
                        continue
            
            logger.info(f"✅ Analysis complete for team {team_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing site: {e}")
            return {"error": str(e), "team_id": team_id}
    
    def check_session_conflict(self) -> bool:
        """Check if there's a session conflict (another user logged in)"""
        try:
            # Check if we're being redirected to login due to session conflict
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            conflict_indicators = [
                "another session",
                "logged in elsewhere",
                "session expired",
                "please log in again",
                "multiple sessions"
            ]
            
            for indicator in conflict_indicators:
                if indicator in page_source:
                    logger.warning(f"⚠️  Potential session conflict detected: {indicator}")
                    return True
            
            return False
        except:
            return False
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with Hudl Instat (requires valid credentials)"""
        if not self.driver:
            if not self.setup_driver():
                return False
        
        try:
            # Navigate to login page
            login_url = "https://app.hudl.com/login"
            self.driver.get(login_url)
            
            # Wait for login form
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email']"))
            )
            
            # Check for existing session conflicts
            if self.check_session_conflict():
                logger.warning("⚠️  Session conflict detected - another user may be logged in")
                logger.info("💡 Consider using a different user identifier or waiting for the other session to timeout")
            
            # Find and fill login form
            email_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']")
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
            
            email_field.send_keys(username)
            password_field.send_keys(password)
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            submit_button.click()
            
            # Wait for redirect or error
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.current_url != login_url
            )
            
            # Check if authentication was successful
            if "login" not in self.driver.current_url.lower():
                self.is_authenticated = True
                # Store session info
                self.session_id = f"{self.user_identifier}_{int(time.time())}"
                logger.info(f"✅ Successfully authenticated with Hudl Instat (Session: {self.session_id})")
                return True
            else:
                logger.error("❌ Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def extract_team_data(self, team_id: str) -> Optional[HudlTeamData]:
        """Extract structured data from a team page (requires authentication)"""
        if not self.is_authenticated:
            logger.error("❌ Must authenticate before extracting data")
            return None
        
        team_url = f"{self.base_url}/{team_id}"
        self.driver.get(team_url)
        
        try:
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract team information
            team_name = "Unknown Team"
            try:
                name_element = self.driver.find_element(By.CSS_SELECTOR, "h1, .team-name")
                team_name = name_element.text
            except:
                pass
            
            # Extract player data (this would need to be customized based on actual page structure)
            players = []
            try:
                player_elements = self.driver.find_elements(By.CSS_SELECTOR, ".player, .roster-item")
                for player in player_elements:
                    player_data = {
                        "name": player.text.strip(),
                        "position": "Unknown",
                        "number": "Unknown"
                    }
                    players.append(player_data)
            except:
                pass
            
            # Extract game data
            games = []
            try:
                game_elements = self.driver.find_elements(By.CSS_SELECTOR, ".game, .match")
                for game in game_elements:
                    game_data = {
                        "date": "Unknown",
                        "opponent": "Unknown",
                        "score": "Unknown"
                    }
                    games.append(game_data)
            except:
                pass
            
            return HudlTeamData(
                team_id=team_id,
                team_name=team_name,
                league="Hockey",
                season="2024-25",
                players=players,
                games=games,
                stats={},
                last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            
        except Exception as e:
            logger.error(f"❌ Error extracting team data: {e}")
            return None
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 WebDriver closed")

class HudlInstatMiniAPI:
    """Mini API wrapper for Hudl Instat data"""
    
    def __init__(self, username: str = None, password: str = None, user_identifier: str = None):
        """Initialize the mini API"""
        self.user_identifier = user_identifier or f"user_{int(time.time())}"
        self.analyzer = HudlInstatAnalyzer(user_identifier=self.user_identifier)
        self.username = username
        self.password = password
        self.authenticated = False
        
        if username and password:
            self.authenticate(username, password)
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with Hudl Instat"""
        self.authenticated = self.analyzer.authenticate(username, password)
        return self.authenticated
    
    def get_team_info(self, team_id: str) -> Dict[str, Any]:
        """Get team information"""
        if not self.authenticated:
            return {"error": "Authentication required"}
        
        team_data = self.analyzer.extract_team_data(team_id)
        if team_data:
            return {
                "team_id": team_data.team_id,
                "team_name": team_data.team_name,
                "league": team_data.league,
                "season": team_data.season,
                "player_count": len(team_data.players),
                "game_count": len(team_data.games),
                "last_updated": team_data.last_updated
            }
        return {"error": "Failed to extract team data"}
    
    def get_team_players(self, team_id: str) -> List[Dict[str, Any]]:
        """Get team players"""
        if not self.authenticated:
            return [{"error": "Authentication required"}]
        
        team_data = self.analyzer.extract_team_data(team_id)
        if team_data:
            return team_data.players
        return [{"error": "Failed to extract player data"}]
    
    def get_team_games(self, team_id: str) -> List[Dict[str, Any]]:
        """Get team games"""
        if not self.authenticated:
            return [{"error": "Authentication required"}]
        
        team_data = self.analyzer.extract_team_data(team_id)
        if team_data:
            return team_data.games
        return [{"error": "Failed to extract game data"}]
    
    def analyze_team_structure(self, team_id: str) -> Dict[str, Any]:
        """Analyze team page structure without authentication"""
        return self.analyzer.analyze_site_structure(team_id)
    
    def close(self):
        """Close the analyzer"""
        self.analyzer.close()

def main():
    """Main function to demonstrate the analyzer"""
    print("🏒 Hudl Instat Site Analyzer")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = HudlInstatAnalyzer()
    
    # Analyze the specific team page
    team_id = "21479"
    analysis = analyzer.analyze_site_structure(team_id)
    
    print(f"\n📊 Analysis Results for Team {team_id}:")
    print(json.dumps(analysis, indent=2))
    
    # Close analyzer
    analyzer.close()
    
    print("\n⚠️  LEGAL NOTICE:")
    print("This tool is for educational purposes only.")
    print("Ensure you have proper authorization from Hudl before using commercially.")
    print("Consider contacting Hudl about official API access.")

if __name__ == "__main__":
    main()
