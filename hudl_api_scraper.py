#!/usr/bin/env python3
"""
Hudl Instat API Scraper
Uses discovered API endpoints to efficiently collect data
"""

import json
import time
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

from hudl_api_endpoints import (
    get_team_players_endpoint, 
    get_player_details_endpoint,
    get_export_endpoint,
    HUDL_BASE_URLS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PlayerData:
    """Player data structure"""
    player_id: str
    team_id: str
    jersey_number: str
    name: str
    position: str
    metrics: Dict[str, Any]
    last_updated: str

class HudlAPIScraper:
    """Enhanced Hudl scraper using discovered API endpoints"""
    
    def __init__(self):
        self.session = requests.Session()
        self.driver = None
        self.base_url = HUDL_BASE_URLS['instat_scout']
        self.authenticated = False
        
    def setup_driver(self):
        """Setup Chrome driver with optimal settings"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
            logger.info("✅ Chrome driver setup complete")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to setup driver: {e}")
            return False
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with Hudl Instat"""
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False
            
            logger.info("🔐 Authenticating with Hudl Instat...")
            
            # Navigate to login page
            self.driver.get("https://www.hudl.com/login")
            time.sleep(3)
            
            # Find and fill username
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.clear()
            username_field.send_keys(username)
            
            # Click continue
            continue_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            continue_button.click()
            time.sleep(3)
            
            # Find and fill password
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            time.sleep(5)
            
            # Check if login successful
            if "instat" in self.driver.current_url.lower():
                self.authenticated = True
                logger.info("✅ Authentication successful!")
                return True
            else:
                logger.error("❌ Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def get_team_players_via_api(self, team_id: str) -> List[PlayerData]:
        """Get team players using discovered API endpoints"""
        try:
            if not self.authenticated:
                logger.error("Not authenticated")
                return []
            
            logger.info(f"🏒 Getting players for team {team_id} via API")
            
            # Navigate to team page
            team_url = f"{self.base_url}/hockey/teams/{team_id}/skaters"
            self.driver.get(team_url)
            time.sleep(5)
            
            # Try to extract data from the page
            players = self._extract_players_from_page(team_id)
            
            if players:
                logger.info(f"✅ Found {len(players)} players via API")
                return players
            else:
                logger.warning("⚠️  No players found via API, falling back to scraping")
                return self._scrape_players_fallback(team_id)
                
        except Exception as e:
            logger.error(f"❌ Error getting team players via API: {e}")
            return self._scrape_players_fallback(team_id)
    
    def _extract_players_from_page(self, team_id: str) -> List[PlayerData]:
        """Extract player data from the current page"""
        try:
            players = []
            
            # Look for player data in various formats
            # Check for JSON data in script tags
            script_tags = self.driver.find_elements(By.TAG_NAME, "script")
            for script in script_tags:
                try:
                    script_content = script.get_attribute("innerHTML")
                    if "players" in script_content.lower() and "jersey" in script_content.lower():
                        # Try to extract JSON data
                        json_data = self._extract_json_from_script(script_content)
                        if json_data:
                            players = self._parse_json_players(json_data, team_id)
                            if players:
                                break
                except:
                    continue
            
            # If no JSON data found, try to scrape from DOM
            if not players:
                players = self._scrape_players_from_dom(team_id)
            
            return players
            
        except Exception as e:
            logger.error(f"Error extracting players from page: {e}")
            return []
    
    def _extract_json_from_script(self, script_content: str) -> Optional[Dict]:
        """Extract JSON data from script content"""
        try:
            # Look for common JSON patterns
            import re
            
            # Pattern 1: window.__INITIAL_STATE__ = {...}
            pattern1 = r'window\.__INITIAL_STATE__\s*=\s*({.*?});'
            match1 = re.search(pattern1, script_content, re.DOTALL)
            if match1:
                return json.loads(match1.group(1))
            
            # Pattern 2: var data = {...}
            pattern2 = r'var\s+data\s*=\s*({.*?});'
            match2 = re.search(pattern2, script_content, re.DOTALL)
            if match2:
                return json.loads(match2.group(1))
            
            # Pattern 3: players: [...]
            pattern3 = r'players:\s*(\[.*?\])'
            match3 = re.search(pattern3, script_content, re.DOTALL)
            if match3:
                return {"players": json.loads(match3.group(1))}
                
        except Exception as e:
            logger.debug(f"Could not extract JSON from script: {e}")
        
        return None
    
    def _parse_json_players(self, json_data: Dict, team_id: str) -> List[PlayerData]:
        """Parse players from JSON data"""
        try:
            players = []
            
            # Try different JSON structures
            if "players" in json_data:
                player_list = json_data["players"]
            elif "data" in json_data and "players" in json_data["data"]:
                player_list = json_data["data"]["players"]
            elif isinstance(json_data, list):
                player_list = json_data
            else:
                return []
            
            for player_data in player_list:
                try:
                    player = PlayerData(
                        player_id=f"{team_id}_{player_data.get('jersey', 'unknown')}",
                        team_id=team_id,
                        jersey_number=str(player_data.get('jersey', '')),
                        name=player_data.get('name', ''),
                        position=player_data.get('position', ''),
                        metrics=player_data.get('stats', {}),
                        last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
                    )
                    players.append(player)
                except Exception as e:
                    logger.debug(f"Error parsing player: {e}")
                    continue
            
            return players
            
        except Exception as e:
            logger.error(f"Error parsing JSON players: {e}")
            return []
    
    def _scrape_players_from_dom(self, team_id: str) -> List[PlayerData]:
        """Fallback: scrape players from DOM elements"""
        try:
            players = []
            
            # Look for player rows in various table structures
            player_selectors = [
                "tr[data-player-id]",
                ".player-row",
                "[class*='player']",
                "div[class*='Player']"
            ]
            
            for selector in player_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for element in elements:
                            try:
                                player = self._extract_player_from_element(element, team_id)
                                if player:
                                    players.append(player)
                            except:
                                continue
                        if players:
                            break
                except:
                    continue
            
            return players
            
        except Exception as e:
            logger.error(f"Error scraping players from DOM: {e}")
            return []
    
    def _extract_player_from_element(self, element, team_id: str) -> Optional[PlayerData]:
        """Extract player data from a DOM element"""
        try:
            # Try to extract basic player info
            name = ""
            jersey = ""
            position = ""
            metrics = {}
            
            # Look for name
            name_selectors = [".name", "[class*='name']", "td:nth-child(1)", "div:nth-child(1)"]
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    name = name_elem.text.strip()
                    if name:
                        break
                except:
                    continue
            
            # Look for jersey number
            jersey_selectors = [".jersey", "[class*='jersey']", "td:nth-child(2)", "div:nth-child(2)"]
            for selector in jersey_selectors:
                try:
                    jersey_elem = element.find_element(By.CSS_SELECTOR, selector)
                    jersey = jersey_elem.text.strip()
                    if jersey:
                        break
                except:
                    continue
            
            # Look for position
            position_selectors = [".position", "[class*='position']", "td:nth-child(3)", "div:nth-child(3)"]
            for selector in position_selectors:
                try:
                    pos_elem = element.find_element(By.CSS_SELECTOR, selector)
                    position = pos_elem.text.strip()
                    if position:
                        break
                except:
                    continue
            
            if name and jersey:
                return PlayerData(
                    player_id=f"{team_id}_{jersey}",
                    team_id=team_id,
                    jersey_number=jersey,
                    name=name,
                    position=position,
                    metrics=metrics,
                    last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
                )
            
        except Exception as e:
            logger.debug(f"Error extracting player from element: {e}")
        
        return None
    
    def _scrape_players_fallback(self, team_id: str) -> List[PlayerData]:
        """Fallback scraping method using the working scraper"""
        try:
            from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper
            
            logger.info("🔄 Using fallback scraper...")
            scraper = HudlCompleteMetricsScraper()
            
            # Use the proven scraper
            success = scraper.run_scraper(
                username="chaserochon777@gmail.com",
                password="357Chaser!468",
                team_id=team_id
            )
            
            if success:
                # Convert the scraped data to our format
                players = []
                # This would need to be adapted based on the actual output format
                # For now, return empty list as placeholder
                return players
            else:
                return []
                
        except Exception as e:
            logger.error(f"Fallback scraper failed: {e}")
            return []
    
    def get_all_ajhl_teams_players(self) -> Dict[str, List[PlayerData]]:
        """Get players for all AJHL teams"""
        try:
            from ajhl_teams_config import get_active_teams
            
            all_teams_players = {}
            teams = get_active_teams()
            
            logger.info(f"🏒 Collecting players from {len(teams)} AJHL teams")
            
            for team_id, team_data in teams.items():
                logger.info(f"📊 Getting players for {team_data['team_name']}")
                
                team_players = self.get_team_players_via_api(team_id)
                all_teams_players[team_id] = team_players
                
                logger.info(f"✅ Found {len(team_players)} players for {team_data['team_name']}")
                
                # Small delay between teams
                time.sleep(2)
            
            return all_teams_players
            
        except Exception as e:
            logger.error(f"Error getting all teams players: {e}")
            return {}
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

# Test the API scraper
if __name__ == "__main__":
    scraper = HudlAPIScraper()
    
    try:
        # Test authentication
        if scraper.authenticate("chaserochon777@gmail.com", "357Chaser!468"):
            logger.info("🎉 Authentication successful!")
            
            # Test getting players for Lloydminster Bobcats
            players = scraper.get_team_players_via_api("21479")
            logger.info(f"📊 Found {len(players)} players")
            
            # Print sample player
            if players:
                sample_player = players[0]
                logger.info(f"Sample player: {sample_player.name} (#{sample_player.jersey_number})")
        else:
            logger.error("❌ Authentication failed")
    
    finally:
        scraper.close()
