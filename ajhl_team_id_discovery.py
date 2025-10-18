#!/usr/bin/env python3
"""
AJHL Team ID Discovery System
Discovers Hudl Instat team IDs for all AJHL teams
"""

import json
import time
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from ajhl_team_config import AJHL_TEAMS, update_team_hudl_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AJHLTeamIDDiscovery:
    """Discovers Hudl Instat team IDs for AJHL teams"""
    
    def __init__(self, headless: bool = True):
        """Initialize the team ID discovery system"""
        self.driver = None
        self.headless = headless
        self.is_authenticated = False
        self.discovered_ids = {}
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ Chrome WebDriver initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to setup Chrome WebDriver: {e}")
            return False
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with Hudl Instat"""
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
            
            # Find and fill login form
            email_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']")
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
            
            email_field.send_keys(username)
            password_field.send_keys(password)
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            submit_button.click()
            
            # Wait for redirect
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.current_url != login_url
            )
            
            if "login" not in self.driver.current_url.lower():
                self.is_authenticated = True
                logger.info("✅ Successfully authenticated with Hudl Instat")
                return True
            else:
                logger.error("❌ Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def search_for_team(self, team_name: str, city: str = None) -> Optional[str]:
        """Search for a team and extract its Hudl team ID"""
        logger.info(f"🔍 Searching for: {team_name}")
        
        try:
            # Navigate to search page or use search functionality
            search_url = "https://app.hudl.com/instat/hockey"
            self.driver.get(search_url)
            time.sleep(3)
            
            # Look for search functionality
            search_terms = [team_name]
            if city:
                search_terms.append(f"{team_name} {city}")
                search_terms.append(f"{city} {team_name}")
            
            for search_term in search_terms:
                try:
                    # Look for search input
                    search_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                        "input[type='search'], input[placeholder*='search'], input[name*='search']")
                    
                    if search_inputs:
                        search_input = search_inputs[0]
                        search_input.clear()
                        search_input.send_keys(search_term)
                        
                        # Look for search button
                        search_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                            "button[type='submit'], .search-button, [data-testid*='search']")
                        
                        if search_buttons:
                            search_buttons[0].click()
                            time.sleep(3)
                            
                            # Look for team results
                            team_id = self._extract_team_id_from_results(team_name)
                            if team_id:
                                return team_id
                    
                    # Try direct URL search patterns
                    team_id = self._try_direct_url_patterns(team_name, city)
                    if team_id:
                        return team_id
                        
                except Exception as e:
                    logger.warning(f"⚠️  Search attempt failed for '{search_term}': {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error searching for {team_name}: {e}")
            return None
    
    def _extract_team_id_from_results(self, team_name: str) -> Optional[str]:
        """Extract team ID from search results"""
        try:
            # Look for team links or elements that might contain team IDs
            team_links = self.driver.find_elements(By.CSS_SELECTOR, 
                "a[href*='/teams/'], .team-link, [data-team-id]")
            
            for link in team_links:
                href = link.get_attribute("href")
                text = link.text.lower()
                
                if team_name.lower() in text and "/teams/" in href:
                    # Extract team ID from URL
                    team_id = href.split("/teams/")[-1].split("/")[0]
                    if team_id.isdigit():
                        logger.info(f"✅ Found team ID for {team_name}: {team_id}")
                        return team_id
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️  Error extracting team ID: {e}")
            return None
    
    def _try_direct_url_patterns(self, team_name: str, city: str = None) -> Optional[str]:
        """Try direct URL patterns to find team IDs"""
        # Common URL patterns for Hudl Instat teams
        url_patterns = [
            f"https://app.hudl.com/instat/hockey/teams",
            f"https://hockey.instatscout.com/teams",
            f"https://app.hudl.com/instat/hockey/teams/search"
        ]
        
        for base_url in url_patterns:
            try:
                self.driver.get(base_url)
                time.sleep(3)
                
                # Look for team listings or search results
                team_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".team, .team-item, .team-card, [data-team-id]")
                
                for element in team_elements:
                    text = element.text.lower()
                    if team_name.lower() in text:
                        # Try to extract team ID from various attributes
                        team_id = (element.get_attribute("data-team-id") or 
                                 element.get_attribute("data-id") or
                                 element.get_attribute("id"))
                        
                        if team_id and team_id.isdigit():
                            logger.info(f"✅ Found team ID for {team_name}: {team_id}")
                            return team_id
                
            except Exception as e:
                logger.warning(f"⚠️  Direct URL pattern failed: {e}")
                continue
        
        return None
    
    def discover_all_team_ids(self) -> Dict[str, Any]:
        """Discover team IDs for all AJHL teams"""
        logger.info("🏒 Starting AJHL team ID discovery...")
        
        discovery_results = {
            "discovery_timestamp": datetime.now().isoformat(),
            "teams_processed": 0,
            "teams_found": 0,
            "teams_not_found": 0,
            "discovered_ids": {},
            "errors": []
        }
        
        for team_id, team_data in AJHL_TEAMS.items():
            if team_data['hudl_team_id']:
                logger.info(f"✅ {team_data['team_name']} already has Hudl ID: {team_data['hudl_team_id']}")
                discovery_results["discovered_ids"][team_id] = team_data['hudl_team_id']
                discovery_results["teams_found"] += 1
                continue
            
            logger.info(f"🔍 Discovering ID for: {team_data['team_name']}")
            discovery_results["teams_processed"] += 1
            
            try:
                found_id = self.search_for_team(team_data['team_name'], team_data['city'])
                
                if found_id:
                    discovery_results["discovered_ids"][team_id] = found_id
                    discovery_results["teams_found"] += 1
                    
                    # Update the team configuration
                    update_team_hudl_id(team_id, found_id)
                    logger.info(f"✅ Discovered ID for {team_data['team_name']}: {found_id}")
                else:
                    discovery_results["teams_not_found"] += 1
                    logger.warning(f"⚠️  Could not find Hudl ID for {team_data['team_name']}")
                
                # Delay between searches to avoid overwhelming the server
                time.sleep(2)
                
            except Exception as e:
                discovery_results["teams_not_found"] += 1
                error_msg = f"Error discovering {team_data['team_name']}: {str(e)}"
                discovery_results["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        # Save discovery results
        results_file = f"ajhl_team_discovery_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(discovery_results, f, indent=2)
        
        logger.info(f"📄 Discovery results saved to: {results_file}")
        logger.info(f"✅ Discovery complete: {discovery_results['teams_found']}/{discovery_results['teams_processed']} teams found")
        
        return discovery_results
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 WebDriver closed")

def main():
    """Main function for team ID discovery"""
    print("🏒 AJHL Team ID Discovery System")
    print("=" * 50)
    
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        discovery = AJHLTeamIDDiscovery(headless=False)
        
        if not discovery.authenticate(HUDL_USERNAME, HUDL_PASSWORD):
            print("❌ Authentication failed")
            return
        
        # Discover all team IDs
        results = discovery.discover_all_team_ids()
        
        print(f"\n📊 Discovery Results:")
        print(f"  Teams processed: {results['teams_processed']}")
        print(f"  Teams found: {results['teams_found']}")
        print(f"  Teams not found: {results['teams_not_found']}")
        
        if results['discovered_ids']:
            print(f"\n✅ Discovered Team IDs:")
            for team_id, hudl_id in results['discovered_ids'].items():
                team_name = AJHL_TEAMS[team_id]['team_name']
                print(f"  {team_name}: {hudl_id}")
        
        if results['errors']:
            print(f"\n❌ Errors:")
            for error in results['errors']:
                print(f"  {error}")
        
        discovery.close()
        
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
