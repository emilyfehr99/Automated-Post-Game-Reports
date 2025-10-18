#!/usr/bin/env python3
"""
Hudl Enhanced CSV Downloader
Enhanced downloader specifically targeting the correct download button icon:
<i class="styled__DownloadIcon-sc-1s49rmo-1 dMcfbw"></i>
"""

import json
import time
import logging
import os
from datetime import datetime
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HudlEnhancedCSVDownloader:
    """Enhanced CSV downloader with specific targeting of Hudl download buttons"""
    
    def __init__(self, headless: bool = False, user_identifier: str = None):
        """Initialize the enhanced CSV downloader"""
        self.driver = None
        self.headless = headless
        self.user_identifier = user_identifier or "enhanced_downloader"
        self.is_authenticated = False
        self.download_directory = None
        
        # Specific selectors for Hudl download buttons
        self.download_selectors = [
            # Primary selector from your HTML snippet
            "i.styled__DownloadIcon-sc-1s49rmo-1",
            ".styled__DownloadIcon-sc-1s49rmo-1",
            "i.styled__DownloadIcon-sc-1s49rmo-1.dMcfbw",
            
            # Fallback selectors
            "button[title*='download']",
            "button[title*='export']",
            "a[href*='.csv']",
            ".download",
            ".export",
            "[data-testid*='download']",
            "[data-testid*='export']",
            "button:contains('CSV')",
            "a:contains('CSV')",
            "button:contains('Download')",
            "a:contains('Download')",
            
            # Additional Hudl-specific selectors
            "[class*='Download']",
            "[class*='download']",
            "i[class*='download']",
            "button i[class*='download']",
            "a i[class*='download']"
        ]
        
        # Define the actual Hudl Instat tabs
        self.instat_tabs = [
            "OVERVIEW", "GAMES", "SKATERS", "GOALIES", 
            "LINES", "SHOT MAP", "FACEOFFS", "EPISODES SEARCH"
        ]
        
    def setup_driver(self):
        """Setup Chrome WebDriver with download configuration"""
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
            
            # Add user-specific profile
            profile_dir = f"/tmp/hudl_profile_{self.user_identifier}"
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument(f"--profile-directory=Profile_{self.user_identifier}")
            
            # Set up download directory
            self.download_directory = f"/tmp/hudl_downloads_{self.user_identifier}"
            os.makedirs(self.download_directory, exist_ok=True)
            
            chrome_options.add_experimental_option("prefs", {
                "download.default_directory": self.download_directory,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "download.extensions_to_open": "",
                "download.open_pdf_in_system_reader": False
            })
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info(f"✅ Enhanced Chrome WebDriver initialized with download directory: {self.download_directory}")
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
    
    def download_team_comprehensive_data(self, team_id: str, team_name: str = None) -> Dict[str, Any]:
        """Download comprehensive CSV data for a team from all tabs"""
        logger.info(f"📥 Downloading comprehensive data for team {team_id}...")
        
        if not self.is_authenticated:
            logger.error("❌ Must authenticate before downloading data")
            return {"error": "Authentication required"}
        
        team_url = f"https://app.hudl.com/instat/hockey/teams/{team_id}"
        
        try:
            # Navigate to team page
            self.driver.get(team_url)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)  # Wait for dynamic content
            
            download_results = {
                "team_id": team_id,
                "team_name": team_name or f"Team_{team_id}",
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
            for tab_name in self.instat_tabs:
                logger.info(f"🔍 Processing tab: {tab_name}")
                tab_results = self._process_tab_for_downloads(tab_name)
                download_results["tabs_processed"][tab_name] = tab_results
                download_results["total_downloads"] += tab_results["downloads_attempted"]
                download_results["successful_downloads"] += tab_results["downloads_successful"]
                download_results["failed_downloads"] += tab_results["downloads_failed"]
                download_results["downloaded_files"].extend(tab_results["downloaded_files"])
                download_results["errors"].extend(tab_results["errors"])
            
            # Get list of downloaded files
            downloaded_files = self._get_downloaded_files()
            download_results["downloaded_files"] = downloaded_files
            
            logger.info(f"✅ CSV download completed: {download_results['successful_downloads']}/{download_results['total_downloads']} successful")
            return download_results
            
        except Exception as e:
            logger.error(f"❌ Error downloading CSVs: {e}")
            return {"error": str(e), "team_id": team_id}
    
    def _process_tab_for_downloads(self, tab_name: str) -> Dict[str, Any]:
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
            
            # Look for download buttons using our enhanced selectors
            download_buttons = self._find_download_buttons()
            
            for button in download_buttons:
                tab_results["downloads_attempted"] += 1
                
                try:
                    # Scroll to button if needed
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(0.5)
                    
                    # Click the download button
                    ActionChains(self.driver).move_to_element(button).click().perform()
                    time.sleep(2)  # Wait for download to start
                    
                    # Check if download started
                    if self._check_download_started():
                        tab_results["downloads_successful"] += 1
                        logger.info(f"✅ CSV download started from {tab_name}")
                    else:
                        tab_results["downloads_failed"] += 1
                        tab_results["errors"].append(f"Download failed for element in {tab_name}")
                
                except Exception as e:
                    tab_results["downloads_failed"] += 1
                    tab_results["errors"].append(f"Error clicking download element in {tab_name}: {str(e)}")
            
            # Special handling for OVERVIEW tab (games with individual download buttons)
            if tab_name == "OVERVIEW":
                overview_downloads = self._process_overview_games()
                tab_results["downloads_attempted"] += overview_downloads["downloads_attempted"]
                tab_results["downloads_successful"] += overview_downloads["downloads_successful"]
                tab_results["downloads_failed"] += overview_downloads["downloads_failed"]
                tab_results["errors"].extend(overview_downloads["errors"])
            
        except Exception as e:
            tab_results["errors"].append(f"Error processing tab {tab_name}: {str(e)}")
        
        return tab_results
    
    def _find_download_buttons(self) -> List[Any]:
        """Find all download buttons using enhanced selectors"""
        download_buttons = []
        
        try:
            # Try each selector in order of priority
            for selector in self.download_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Additional validation for download buttons
                            if self._is_download_button(element):
                                download_buttons.append(element)
                                logger.debug(f"Found download button with selector: {selector}")
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Remove duplicates
            unique_buttons = []
            seen_elements = set()
            for button in download_buttons:
                element_id = id(button)
                if element_id not in seen_elements:
                    unique_buttons.append(button)
                    seen_elements.add(element_id)
            
            logger.info(f"Found {len(unique_buttons)} download buttons")
            return unique_buttons
            
        except Exception as e:
            logger.warning(f"⚠️  Error finding download buttons: {e}")
            return []
    
    def _is_download_button(self, element) -> bool:
        """Validate if an element is actually a download button"""
        try:
            # Check element properties
            tag_name = element.tag_name.lower()
            class_name = element.get_attribute("class") or ""
            title = element.get_attribute("title") or ""
            text = element.text.lower()
            
            # Look for download indicators
            download_indicators = [
                "download", "export", "csv", "excel", "data"
            ]
            
            # Check if any download indicator is present
            for indicator in download_indicators:
                if (indicator in class_name.lower() or 
                    indicator in title.lower() or 
                    indicator in text):
                    return True
            
            # Special check for the specific icon class you mentioned
            if "styled__DownloadIcon-sc-1s49rmo-1" in class_name:
                return True
            
            # Check if it's a clickable element with download-related attributes
            if (tag_name in ["button", "a"] and 
                (element.is_enabled() and element.is_displayed())):
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error validating download button: {e}")
            return False
    
    def _process_overview_games(self) -> Dict[str, Any]:
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
                    # Look for download buttons within this game
                    download_buttons = self._find_download_buttons_in_element(game_element)
                    
                    for button in download_buttons:
                        overview_results["downloads_attempted"] += 1
                        
                        try:
                            # Scroll to button
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                            time.sleep(0.5)
                            
                            # Click the download button
                            ActionChains(self.driver).move_to_element(button).click().perform()
                            time.sleep(2)
                            
                            if self._check_download_started():
                                overview_results["downloads_successful"] += 1
                                logger.info("✅ Game CSV download started from OVERVIEW")
                            else:
                                overview_results["downloads_failed"] += 1
                        
                        except Exception as e:
                            overview_results["downloads_failed"] += 1
                            overview_results["errors"].append(f"Error clicking game download: {str(e)}")
        
        except Exception as e:
            overview_results["errors"].append(f"Error processing overview games: {str(e)}")
        
        return overview_results
    
    def _find_download_buttons_in_element(self, parent_element) -> List[Any]:
        """Find download buttons within a specific element"""
        download_buttons = []
        
        try:
            for selector in self.download_selectors:
                try:
                    elements = parent_element.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled() and self._is_download_button(element):
                            download_buttons.append(element)
                except:
                    continue
        except Exception as e:
            logger.debug(f"Error finding download buttons in element: {e}")
        
        return download_buttons
    
    def _check_download_started(self) -> bool:
        """Check if a download has started"""
        try:
            # Check if there are any new files in the download directory
            if self.download_directory and os.path.exists(self.download_directory):
                files = os.listdir(self.download_directory)
                # Look for recently created files (within last 10 seconds)
                current_time = time.time()
                for file in files:
                    file_path = os.path.join(self.download_directory, file)
                    if os.path.isfile(file_path):
                        file_time = os.path.getmtime(file_path)
                        if current_time - file_time < 10:  # File created within last 10 seconds
                            return True
            return False
        except:
            return False
    
    def _get_downloaded_files(self) -> List[Dict[str, Any]]:
        """Get list of downloaded files"""
        downloaded_files = []
        
        try:
            if self.download_directory and os.path.exists(self.download_directory):
                files = os.listdir(self.download_directory)
                for file in files:
                    file_path = os.path.join(self.download_directory, file)
                    if os.path.isfile(file_path):
                        file_info = {
                            "filename": file,
                            "file_path": file_path,
                            "size_bytes": os.path.getsize(file_path),
                            "created_time": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                        }
                        downloaded_files.append(file_info)
        except Exception as e:
            logger.warning(f"⚠️  Error getting downloaded files: {e}")
        
        return downloaded_files
    
    def download_specific_game_csv(self, team_id: str, game_id: str = None) -> Dict[str, Any]:
        """Download CSV for a specific game"""
        logger.info(f"🎮 Downloading CSV for specific game: {game_id}")
        
        if not self.is_authenticated:
            logger.error("❌ Must authenticate before downloading game CSV")
            return {"error": "Authentication required"}
        
        try:
            # Navigate to team page
            team_url = f"https://app.hudl.com/instat/hockey/teams/{team_id}"
            self.driver.get(team_url)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            
            # Look for the specific game
            game_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                f"[data-game-id='{game_id}'], .game[data-id='{game_id}']")
            
            if not game_elements:
                # Try to find game by clicking on it from the overview
                game_elements = self.driver.find_elements(By.XPATH, 
                    f"//*[contains(text(), '{game_id}') or contains(@data-game-id, '{game_id}')]")
            
            if not game_elements:
                return {"error": f"Game {game_id} not found"}
            
            # Click on the game to open its page
            game_element = game_elements[0]
            ActionChains(self.driver).move_to_element(game_element).click().perform()
            time.sleep(3)  # Wait for game page to load
            
            # Look for download buttons on the game page
            download_buttons = self._find_download_buttons()
            
            for button in download_buttons:
                if button.is_displayed() and button.is_enabled():
                    # Click the download button
                    ActionChains(self.driver).move_to_element(button).click().perform()
                    time.sleep(3)
                    
                    if self._check_download_started():
                        return {
                            "success": True,
                            "game_id": game_id,
                            "message": "CSV download started successfully"
                        }
                    else:
                        return {"error": "Download failed to start"}
            
            return {"error": "No download button found for this game"}
            
        except Exception as e:
            logger.error(f"❌ Error downloading game CSV: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 WebDriver closed")

def main():
    """Main function to demonstrate the enhanced CSV downloader"""
    print("📥 Hudl Enhanced CSV Downloader")
    print("=" * 50)
    
    # Initialize downloader
    downloader = HudlEnhancedCSVDownloader(headless=False)
    
    try:
        # Authenticate
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        if not downloader.authenticate(HUDL_USERNAME, HUDL_PASSWORD):
            print("❌ Authentication failed")
            return
        
        # Download team CSVs
        team_id = "21479"  # Bobcats team ID
        results = downloader.download_team_comprehensive_data(team_id, "Lloydminster Bobcats")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hudl_enhanced_download_results_{team_id}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Download results saved to: {filename}")
        
        # Print summary
        print(f"\n📊 Download Summary:")
        print(f"  Total downloads attempted: {results['total_downloads']}")
        print(f"  Successful downloads: {results['successful_downloads']}")
        print(f"  Failed downloads: {results['failed_downloads']}")
        print(f"  Downloaded files: {len(results['downloaded_files'])}")
        
        # Show tab results
        for tab_name, tab_results in results.get('tabs_processed', {}).items():
            if tab_results['downloads_attempted'] > 0:
                print(f"  {tab_name}: {tab_results['downloads_successful']}/{tab_results['downloads_attempted']} successful")
        
        # Show downloaded files
        if results['downloaded_files']:
            print(f"\n📁 Downloaded Files:")
            for file_info in results['downloaded_files']:
                print(f"  - {file_info['filename']} ({file_info['size_bytes']} bytes)")
        
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        downloader.close()

if __name__ == "__main__":
    main()
