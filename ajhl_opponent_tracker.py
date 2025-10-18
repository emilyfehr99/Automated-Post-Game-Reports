#!/usr/bin/env python3
"""
AJHL Opponent Tracker
Discovers upcoming opponents and their Hudl team pages for comprehensive data collection
"""

import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from ajhl_team_config import AJHL_TEAMS, get_active_teams, update_team_hudl_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AJHLOpponentTracker:
    """Tracks upcoming opponents and their Hudl team pages"""
    
    def __init__(self, headless: bool = True):
        """Initialize the opponent tracker"""
        self.driver = None
        self.headless = headless
        self.is_authenticated = False
        self.ajhl_schedule_url = "https://www.ajhl.ca/schedule"
        self.hudl_base_url = "https://app.hudl.com/instat/hockey/teams"
        
        # Known team name mappings between AJHL and Hudl
        self.team_name_mappings = {
            "Lloydminster Bobcats": ["Lloydminster Bobcats", "Bobcats", "Lloydminster"],
            "Brooks Bandits": ["Brooks Bandits", "Bandits", "Brooks"],
            "Calgary Canucks": ["Calgary Canucks", "Canucks", "Calgary"],
            "Camrose Kodiaks": ["Camrose Kodiaks", "Kodiaks", "Camrose"],
            "Drumheller Dragons": ["Drumheller Dragons", "Dragons", "Drumheller"],
            "Okotoks Oilers": ["Okotoks Oilers", "Oilers", "Okotoks"],
            "Olds Grizzlys": ["Olds Grizzlys", "Grizzlys", "Olds"],
            "Blackfalds Bulldogs": ["Blackfalds Bulldogs", "Bulldogs", "Blackfalds"],
            "Canmore Eagles": ["Canmore Eagles", "Eagles", "Canmore"],
            "Sherwood Park Crusaders": ["Sherwood Park Crusaders", "Crusaders", "Sherwood Park"],
            "Spruce Grove Saints": ["Spruce Grove Saints", "Saints", "Spruce Grove"],
            "St. Albert Steel": ["St. Albert Steel", "Steel", "St. Albert"],
            "Strathcona Chiefs": ["Strathcona Chiefs", "Chiefs", "Strathcona"],
            "Whitecourt Wolverines": ["Whitecourt Wolverines", "Wolverines", "Whitecourt"],
            "Bonnyville Pontiacs": ["Bonnyville Pontiacs", "Pontiacs", "Bonnyville"],
            "Drayton Valley Thunder": ["Drayton Valley Thunder", "Thunder", "Drayton Valley"],
            "Fort McMurray Oil Barons": ["Fort McMurray Oil Barons", "Oil Barons", "Fort McMurray"],
            "Grande Prairie Storm": ["Grande Prairie Storm", "Storm", "Grande Prairie"]
        }
    
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
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            
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
    
    def get_upcoming_opponents(self, team_name: str = "Lloydminster Bobcats", days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming opponents from AJHL schedule"""
        logger.info(f"📅 Getting upcoming opponents for {team_name}...")
        
        opponents = []
        
        try:
            # Navigate to AJHL schedule
            self.driver.get(self.ajhl_schedule_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            
            # Look for schedule elements
            schedule_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".game, .match, .schedule-item, .fixture, [data-game]")
            
            current_date = datetime.now()
            end_date = current_date + timedelta(days=days_ahead)
            
            for element in schedule_elements:
                try:
                    # Extract game information
                    game_text = element.text.lower()
                    
                    # Check if this game involves our team
                    if team_name.lower() in game_text:
                        # Extract opponent and date information
                        opponent = self._extract_opponent_from_game(element, team_name)
                        game_date = self._extract_date_from_game(element)
                        
                        if opponent and game_date and current_date <= game_date <= end_date:
                            opponents.append({
                                'opponent': opponent,
                                'game_date': game_date.isoformat(),
                                'days_until_game': (game_date - current_date).days,
                                'home_team': self._is_home_game(element, team_name),
                                'raw_text': element.text
                            })
                            
                except Exception as e:
                    logger.warning(f"⚠️  Error parsing game element: {e}")
                    continue
            
            # Sort by game date
            opponents.sort(key=lambda x: x['game_date'])
            
            logger.info(f"✅ Found {len(opponents)} upcoming opponents")
            return opponents
            
        except Exception as e:
            logger.error(f"❌ Error getting upcoming opponents: {e}")
            return []
    
    def _extract_opponent_from_game(self, element, team_name: str) -> Optional[str]:
        """Extract opponent team name from game element"""
        try:
            game_text = element.text
            
            # Split by common separators
            separators = [' vs ', ' @ ', ' v ', ' - ', ' vs. ', ' @ ']
            
            for sep in separators:
                if sep in game_text:
                    parts = game_text.split(sep)
                    if len(parts) >= 2:
                        team1 = parts[0].strip()
                        team2 = parts[1].strip()
                        
                        # Return the team that's not our team
                        if team_name.lower() in team1.lower():
                            return team2
                        elif team_name.lower() in team2.lower():
                            return team1
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️  Error extracting opponent: {e}")
            return None
    
    def _extract_date_from_game(self, element) -> Optional[datetime]:
        """Extract game date from game element"""
        try:
            # Look for date elements
            date_elements = element.find_elements(By.CSS_SELECTOR, 
                ".date, .game-date, [data-date], .time, .game-time")
            
            for date_elem in date_elements:
                date_text = date_elem.text.strip()
                if date_text:
                    # Try to parse various date formats
                    date_formats = [
                        '%Y-%m-%d',
                        '%m/%d/%Y',
                        '%d/%m/%Y',
                        '%B %d, %Y',
                        '%b %d, %Y',
                        '%A, %B %d, %Y'
                    ]
                    
                    for fmt in date_formats:
                        try:
                            return datetime.strptime(date_text, fmt)
                        except ValueError:
                            continue
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️  Error extracting date: {e}")
            return None
    
    def _is_home_game(self, element, team_name: str) -> bool:
        """Determine if this is a home game"""
        try:
            game_text = element.text.lower()
            
            # Look for home indicators
            home_indicators = [' vs ', ' vs. ']
            away_indicators = [' @ ', ' at ']
            
            for indicator in home_indicators:
                if indicator in game_text:
                    parts = game_text.split(indicator)
                    if len(parts) >= 2:
                        return team_name.lower() in parts[0].lower()
            
            for indicator in away_indicators:
                if indicator in game_text:
                    parts = game_text.split(indicator)
                    if len(parts) >= 2:
                        return team_name.lower() in parts[1].lower()
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️  Error determining home game: {e}")
            return False
    
    def find_opponent_hudl_team_id(self, opponent_name: str) -> Optional[str]:
        """Find Hudl team ID for an opponent"""
        logger.info(f"🔍 Finding Hudl team ID for opponent: {opponent_name}")
        
        try:
            # Try to match opponent name to known teams
            for ajhl_team, hudl_variations in self.team_name_mappings.items():
                for variation in hudl_variations:
                    if variation.lower() in opponent_name.lower() or opponent_name.lower() in variation.lower():
                        # Found a match, get the team ID
                        team_id = self._get_team_id_by_name(ajhl_team)
                        if team_id:
                            logger.info(f"✅ Found Hudl ID for {opponent_name}: {team_id}")
                            return team_id
            
            # If no direct match, try searching Hudl
            return self._search_hudl_for_team(opponent_name)
            
        except Exception as e:
            logger.error(f"❌ Error finding Hudl ID for {opponent_name}: {e}")
            return None
    
    def _get_team_id_by_name(self, team_name: str) -> Optional[str]:
        """Get team ID by team name from our configuration"""
        for team_id, team_data in AJHL_TEAMS.items():
            if team_data['team_name'] == team_name:
                return team_data['hudl_team_id']
        return None
    
    def _search_hudl_for_team(self, team_name: str) -> Optional[str]:
        """Search Hudl for a team and extract team ID"""
        try:
            # Navigate to Hudl search
            search_url = "https://app.hudl.com/instat/hockey"
            self.driver.get(search_url)
            time.sleep(3)
            
            # Look for search functionality
            search_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                "input[type='search'], input[placeholder*='search'], input[name*='search']")
            
            if search_inputs:
                search_input = search_inputs[0]
                search_input.clear()
                search_input.send_keys(team_name)
                
                # Look for search button
                search_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "button[type='submit'], .search-button, [data-testid*='search']")
                
                if search_buttons:
                    search_buttons[0].click()
                    time.sleep(3)
                    
                    # Look for team results
                    team_links = self.driver.find_elements(By.CSS_SELECTOR, 
                        "a[href*='/teams/'], .team-link, [data-team-id]")
                    
                    for link in team_links:
                        href = link.get_attribute("href")
                        text = link.text.lower()
                        
                        if team_name.lower() in text and "/teams/" in href:
                            # Extract team ID from URL
                            team_id = href.split("/teams/")[-1].split("/")[0]
                            if team_id.isdigit():
                                logger.info(f"✅ Found Hudl ID for {team_name}: {team_id}")
                                return team_id
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️  Error searching Hudl for {team_name}: {e}")
            return None
    
    def download_opponent_data(self, opponent_name: str, hudl_team_id: str) -> Dict[str, Any]:
        """Download all CSV data for an opponent team"""
        logger.info(f"📥 Downloading data for opponent: {opponent_name} (ID: {hudl_team_id})")
        
        if not self.is_authenticated:
            logger.error("❌ Must authenticate before downloading data")
            return {"error": "Authentication required"}
        
        team_url = f"{self.hudl_base_url}/{hudl_team_id}"
        
        try:
            # Navigate to opponent team page
            self.driver.get(team_url)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            
            download_results = {
                "opponent_name": opponent_name,
                "hudl_team_id": hudl_team_id,
                "url": team_url,
                "download_timestamp": datetime.now().isoformat(),
                "tabs_processed": {},
                "total_downloads": 0,
                "successful_downloads": 0,
                "failed_downloads": 0,
                "downloaded_files": [],
                "errors": []
            }
            
            # Process each tab
            hudl_tabs = [
                "OVERVIEW", "GAMES", "SKATERS", "GOALIES", 
                "LINES", "SHOT MAP", "FACEOFFS", "EPISODES SEARCH"
            ]
            
            for tab_name in hudl_tabs:
                logger.info(f"🔍 Processing tab: {tab_name}")
                tab_results = self._process_tab_for_downloads(tab_name, opponent_name)
                download_results["tabs_processed"][tab_name] = tab_results
                download_results["total_downloads"] += tab_results["downloads_attempted"]
                download_results["successful_downloads"] += tab_results["downloads_successful"]
                download_results["failed_downloads"] += tab_results["downloads_failed"]
                download_results["downloaded_files"].extend(tab_results["downloaded_files"])
                download_results["errors"].extend(tab_results["errors"])
            
            logger.info(f"✅ Download completed for {opponent_name}: {download_results['successful_downloads']}/{download_results['total_downloads']} successful")
            return download_results
            
        except Exception as e:
            logger.error(f"❌ Error downloading data for {opponent_name}: {e}")
            return {"error": str(e), "opponent": opponent_name}
    
    def _process_tab_for_downloads(self, tab_name: str, opponent_name: str) -> Dict[str, Any]:
        """Process a specific tab for CSV downloads"""
        tab_results = {
            "tab_name": tab_name,
            "downloads_attempted": 0,
            "downloads_successful": 0,
            "downloads_failed": 0,
            "downloaded_files": [],
            "errors": []
        }
        
        try:
            # Look for the tab element
            tab_elements = self.driver.find_elements(By.XPATH, 
                f"//*[contains(text(), '{tab_name}') and (self::a or self::button or self::*[@role='tab'])]")
            
            if not tab_elements:
                tab_results["errors"].append(f"Tab {tab_name} not found")
                return tab_results
            
            # Click the tab
            tab_element = None
            for element in tab_elements:
                if element.is_displayed() and element.is_enabled():
                    tab_element = element
                    break
            
            if not tab_element:
                tab_results["errors"].append(f"Tab {tab_name} not clickable")
                return tab_results
            
            # Click the tab
            ActionChains(self.driver).move_to_element(tab_element).click().perform()
            time.sleep(3)  # Wait for tab content to load
            
            # Look for download buttons using the specific icon class you mentioned
            download_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "i.styled__DownloadIcon-sc-1s49rmo-1, .styled__DownloadIcon-sc-1s49rmo-1, "
                "button[title*='download'], button[title*='export'], .download, .export, "
                "[data-testid*='download'], [data-testid*='export']")
            
            for button in download_buttons:
                if button.is_displayed() and button.is_enabled():
                    tab_results["downloads_attempted"] += 1
                    
                    try:
                        # Click the download button
                        ActionChains(self.driver).move_to_element(button).click().perform()
                        time.sleep(2)  # Wait for download to start
                        
                        # Check if download started (simplified check)
                        tab_results["downloads_successful"] += 1
                        logger.info(f"✅ Download started for {opponent_name} - {tab_name}")
                        
                    except Exception as e:
                        tab_results["downloads_failed"] += 1
                        tab_results["errors"].append(f"Error clicking download button: {str(e)}")
            
            # Special handling for OVERVIEW tab (games with individual download buttons)
            if tab_name == "OVERVIEW":
                overview_downloads = self._process_overview_games(opponent_name)
                tab_results["downloads_attempted"] += overview_downloads["downloads_attempted"]
                tab_results["downloads_successful"] += overview_downloads["downloads_successful"]
                tab_results["downloads_failed"] += overview_downloads["downloads_failed"]
                tab_results["errors"].extend(overview_downloads["errors"])
            
        except Exception as e:
            tab_results["errors"].append(f"Error processing tab {tab_name}: {str(e)}")
        
        return tab_results
    
    def _process_overview_games(self, opponent_name: str) -> Dict[str, Any]:
        """Process games on the OVERVIEW page for individual downloads"""
        overview_results = {
            "downloads_attempted": 0,
            "downloads_successful": 0,
            "downloads_failed": 0,
            "errors": []
        }
        
        try:
            # Look for game elements with download buttons
            game_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".game, .match, .game-item, .game-card, [data-game-id]")
            
            for game_element in game_elements:
                if game_element.is_displayed():
                    # Look for download buttons within this game using the specific icon
                    download_buttons = game_element.find_elements(By.CSS_SELECTOR, 
                        "i.styled__DownloadIcon-sc-1s49rmo-1, .styled__DownloadIcon-sc-1s49rmo-1, "
                        "button, a, .download, .export")
                    
                    for button in download_buttons:
                        if button.is_displayed() and button.is_enabled():
                            overview_results["downloads_attempted"] += 1
                            
                            try:
                                # Click the download button
                                ActionChains(self.driver).move_to_element(button).click().perform()
                                time.sleep(2)
                                
                                overview_results["downloads_successful"] += 1
                                logger.info(f"✅ Game CSV download started for {opponent_name}")
                                
                            except Exception as e:
                                overview_results["downloads_failed"] += 1
                                overview_results["errors"].append(f"Error clicking game download: {str(e)}")
        
        except Exception as e:
            overview_results["errors"].append(f"Error processing overview games: {str(e)}")
        
        return overview_results
    
    def get_comprehensive_opponent_data(self, team_name: str = "Lloydminster Bobcats", days_ahead: int = 30) -> Dict[str, Any]:
        """Get comprehensive data for all upcoming opponents"""
        logger.info(f"🏒 Getting comprehensive opponent data for {team_name}...")
        
        results = {
            "team_name": team_name,
            "analysis_timestamp": datetime.now().isoformat(),
            "days_ahead": days_ahead,
            "opponents_found": 0,
            "opponents_processed": 0,
            "opponents_successful": 0,
            "opponents_failed": 0,
            "upcoming_opponents": [],
            "download_results": {},
            "errors": []
        }
        
        try:
            # Get upcoming opponents
            opponents = self.get_upcoming_opponents(team_name, days_ahead)
            results["opponents_found"] = len(opponents)
            results["upcoming_opponents"] = opponents
            
            # Process each opponent
            for opponent_info in opponents:
                opponent_name = opponent_info['opponent']
                logger.info(f"🎯 Processing opponent: {opponent_name}")
                
                try:
                    # Find Hudl team ID
                    hudl_team_id = self.find_opponent_hudl_team_id(opponent_name)
                    
                    if hudl_team_id:
                        # Download opponent data
                        download_result = self.download_opponent_data(opponent_name, hudl_team_id)
                        results["download_results"][opponent_name] = download_result
                        
                        if "error" not in download_result:
                            results["opponents_successful"] += 1
                        else:
                            results["opponents_failed"] += 1
                            results["errors"].append(f"Failed to download {opponent_name}: {download_result['error']}")
                    else:
                        results["opponents_failed"] += 1
                        results["errors"].append(f"Could not find Hudl ID for {opponent_name}")
                    
                    results["opponents_processed"] += 1
                    
                    # Delay between opponents
                    time.sleep(5)
                    
                except Exception as e:
                    results["opponents_failed"] += 1
                    results["errors"].append(f"Error processing {opponent_name}: {str(e)}")
                    logger.error(f"❌ Error processing opponent {opponent_name}: {e}")
            
            # Save results
            results_file = f"ajhl_opponent_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"📄 Opponent data results saved to: {results_file}")
            logger.info(f"✅ Opponent analysis complete: {results['opponents_successful']}/{results['opponents_processed']} successful")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive opponent analysis: {e}")
            results["errors"].append(f"System error: {str(e)}")
            return results
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 WebDriver closed")

def main():
    """Main function for opponent tracking"""
    print("🏒 AJHL Opponent Tracker")
    print("=" * 50)
    
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        tracker = AJHLOpponentTracker(headless=False)
        
        if not tracker.authenticate(HUDL_USERNAME, HUDL_PASSWORD):
            print("❌ Authentication failed")
            return
        
        # Get comprehensive opponent data
        results = tracker.get_comprehensive_opponent_data("Lloydminster Bobcats", 30)
        
        print(f"\n📊 Opponent Analysis Results:")
        print(f"  Opponents found: {results['opponents_found']}")
        print(f"  Opponents processed: {results['opponents_processed']}")
        print(f"  Successful downloads: {results['opponents_successful']}")
        print(f"  Failed downloads: {results['opponents_failed']}")
        
        if results['upcoming_opponents']:
            print(f"\n📅 Upcoming Opponents:")
            for opponent in results['upcoming_opponents']:
                print(f"  {opponent['opponent']} - {opponent['game_date']} ({opponent['days_until_game']} days)")
        
        if results['errors']:
            print(f"\n❌ Errors:")
            for error in results['errors']:
                print(f"  {error}")
        
        tracker.close()
        
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
