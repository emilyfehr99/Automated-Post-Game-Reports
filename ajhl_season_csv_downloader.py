#!/usr/bin/env python3
"""
AJHL Season CSV Downloader for 2025-2026 Season
Downloads detailed game stats CSV for all teams from Hudl Instat
"""

import json
import time
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from ajhl_teams_config import get_all_teams

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AJHLSeasonCSVDownloader:
    """Downloads 2025-2026 season CSV data for all AJHL teams"""
    
    def __init__(self, headless: bool = False):
        """Initialize the season CSV downloader"""
        self.driver = None
        self.headless = headless
        self.is_authenticated = False
        self.download_directory = None
        self.db_path = "ajhl_data/ajhl_database.db"
        self.season = "2025-2026"
        
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
            
            # Set up download directory
            self.download_directory = f"/tmp/ajhl_season_downloads_{self.season.replace('-', '_')}"
            os.makedirs(self.download_directory, exist_ok=True)
            
            chrome_options.add_experimental_option("prefs", {
                "download.default_directory": self.download_directory,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            })
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info(f"✅ Chrome WebDriver initialized for {self.season} season")
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
    
    def download_team_season_csv(self, team_id: str, team_name: str) -> Dict[str, Any]:
        """Download 2025-2026 season CSV for a specific team"""
        logger.info(f"📥 Downloading {self.season} season CSV for {team_name}...")
        
        if not self.is_authenticated:
            return {"error": "Must authenticate before downloading CSV"}
        
        try:
            # Navigate to team's games page
            team_games_url = f"https://app.hudl.com/instat/hockey/teams/{team_id}/games"
            self.driver.get(team_games_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)  # Wait for dynamic content
            
            result = {
                "team_id": team_id,
                "team_name": team_name,
                "season": self.season,
                "url": team_games_url,
                "download_timestamp": datetime.now().isoformat(),
                "success": False,
                "error": None,
                "csv_file_path": None
            }
            
            # Step 1: Find and click on season dropdown
            season_dropdown = self._find_season_dropdown()
            if not season_dropdown:
                result["error"] = f"Could not find season dropdown for {team_name}"
                return result
            
            # Step 2: Select 2025-2026 season
            if not self._select_season(season_dropdown):
                result["error"] = f"Could not select {self.season} season for {team_name}"
                return result
            
            # Step 3: Find and click "detailed game stats" button/link
            if not self._click_detailed_game_stats():
                result["error"] = f"Could not find detailed game stats option for {team_name}"
                return result
            
            # Step 4: Click download button
            if not self._click_download_button():
                result["error"] = f"Could not find download button for {team_name}"
                return result
            
            # Step 5: Select all checkboxes in download popup
            if not self._select_all_download_options():
                result["error"] = f"Could not select all download options for {team_name}"
                return result
            
            # Step 6: Confirm download
            if not self._confirm_download():
                result["error"] = f"Could not confirm download for {team_name}"
                return result
            
            # Step 7: Wait for download and get file path
            csv_file_path = self._wait_for_download()
            if csv_file_path:
                result["success"] = True
                result["csv_file_path"] = csv_file_path
                logger.info(f"✅ Successfully downloaded {self.season} CSV for {team_name}")
            else:
                result["error"] = f"Download completed but file not found for {team_name}"
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error downloading season CSV for {team_name}: {e}")
            return {"error": str(e), "team_name": team_name, "team_id": team_id}
    
    def _find_season_dropdown(self) -> Optional[Any]:
        """Find the season dropdown element"""
        try:
            # Look for common dropdown selectors
            selectors = [
                "select[name*='season']",
                "select[id*='season']",
                ".season-select",
                ".season-dropdown",
                "select[class*='season']",
                "select[data-testid*='season']"
            ]
            
            for selector in selectors:
                try:
                    dropdown = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if dropdown.is_displayed():
                        return dropdown
                except:
                    continue
            
            # Try to find by text content
            dropdowns = self.driver.find_elements(By.TAG_NAME, "select")
            for dropdown in dropdowns:
                if dropdown.is_displayed():
                    # Check if it contains season-related options
                    options = dropdown.find_elements(By.TAG_NAME, "option")
                    for option in options:
                        if self.season in option.text or "2025" in option.text:
                            return dropdown
            
            return None
            
        except Exception as e:
            logger.warning(f"Error finding season dropdown: {e}")
            return None
    
    def _select_season(self, dropdown) -> bool:
        """Select the 2025-2026 season from dropdown"""
        try:
            select = Select(dropdown)
            
            # Try to select by visible text
            try:
                select.select_by_visible_text(self.season)
                return True
            except:
                pass
            
            # Try to select by partial text
            try:
                select.select_by_visible_text("2025-2026")
                return True
            except:
                pass
            
            # Try to select by value
            try:
                select.select_by_value(self.season)
                return True
            except:
                pass
            
            # Look for options containing 2025
            options = select.options
            for option in options:
                if "2025" in option.text:
                    select.select_by_visible_text(option.text)
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error selecting season: {e}")
            return False
    
    def _click_detailed_game_stats(self) -> bool:
        """Click on detailed game stats option"""
        try:
            # Look for various possible selectors
            selectors = [
                "button:contains('detailed game stats')",
                "a:contains('detailed game stats')",
                "button:contains('Detailed Game Stats')",
                "a:contains('Detailed Game Stats')",
                "button:contains('game stats')",
                "a:contains('game stats')",
                ".detailed-stats",
                ".game-stats",
                "[data-testid*='detailed']",
                "[data-testid*='stats']"
            ]
            
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed() and element.is_enabled():
                        ActionChains(self.driver).move_to_element(element).click().perform()
                        time.sleep(2)
                        return True
                except:
                    continue
            
            # Try XPath search for text containing "detailed"
            try:
                element = self.driver.find_element(By.XPATH, "//*[contains(text(), 'detailed') and contains(text(), 'game')]")
                if element.is_displayed() and element.is_enabled():
                    ActionChains(self.driver).move_to_element(element).click().perform()
                    time.sleep(2)
                    return True
            except:
                pass
            
            return False
            
        except Exception as e:
            logger.warning(f"Error clicking detailed game stats: {e}")
            return False
    
    def _click_download_button(self) -> bool:
        """Click the download button"""
        try:
            # Look for download button selectors
            selectors = [
                "button:contains('download')",
                "a:contains('download')",
                "button:contains('Download')",
                "a:contains('Download')",
                ".download-btn",
                ".download-button",
                "[data-testid*='download']",
                "button[title*='download']",
                "a[title*='download']"
            ]
            
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed() and element.is_enabled():
                        ActionChains(self.driver).move_to_element(element).click().perform()
                        time.sleep(2)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"Error clicking download button: {e}")
            return False
    
    def _select_all_download_options(self) -> bool:
        """Select all checkboxes in the download popup"""
        try:
            # Wait for popup to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox']"))
            )
            
            # Find all checkboxes
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            
            # Select all unchecked checkboxes
            for checkbox in checkboxes:
                if checkbox.is_displayed() and not checkbox.is_selected():
                    try:
                        ActionChains(self.driver).move_to_element(checkbox).click().perform()
                        time.sleep(0.5)
                    except:
                        continue
            
            return True
            
        except Exception as e:
            logger.warning(f"Error selecting download options: {e}")
            return False
    
    def _confirm_download(self) -> bool:
        """Confirm the download"""
        try:
            # Look for confirm/ok/submit buttons
            selectors = [
                "button:contains('confirm')",
                "button:contains('Confirm')",
                "button:contains('ok')",
                "button:contains('OK')",
                "button:contains('submit')",
                "button:contains('Submit')",
                "button:contains('download')",
                "button:contains('Download')",
                ".confirm-btn",
                ".ok-btn",
                ".submit-btn",
                "[data-testid*='confirm']",
                "[data-testid*='submit']"
            ]
            
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed() and element.is_enabled():
                        ActionChains(self.driver).move_to_element(element).click().perform()
                        time.sleep(2)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"Error confirming download: {e}")
            return False
    
    def _wait_for_download(self, timeout: int = 30) -> Optional[str]:
        """Wait for download to complete and return file path"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if os.path.exists(self.download_directory):
                    files = os.listdir(self.download_directory)
                    csv_files = [f for f in files if f.endswith('.csv')]
                    if csv_files:
                        # Get the most recent CSV file
                        latest_file = max(csv_files, key=lambda x: os.path.getctime(os.path.join(self.download_directory, x)))
                        file_path = os.path.join(self.download_directory, latest_file)
                        return file_path
                time.sleep(1)
            
            return None
            
        except Exception as e:
            logger.warning(f"Error waiting for download: {e}")
            return None
    
    def download_all_teams_season_csv(self) -> Dict[str, Any]:
        """Download 2025-2026 season CSV for all AJHL teams"""
        logger.info(f"🏒 Starting {self.season} season CSV download for all AJHL teams...")
        
        if not self.is_authenticated:
            return {"error": "Must authenticate before downloading CSV"}
        
        all_teams = get_all_teams()
        results = {}
        successful_downloads = 0
        failed_downloads = 0
        
        for team_id, team_data in all_teams.items():
            team_name = team_data["team_name"]
            logger.info(f"\n📥 Processing {team_name}...")
            
            try:
                result = self.download_team_season_csv(team_id, team_name)
                results[team_id] = result
                
                if result.get("success"):
                    successful_downloads += 1
                    # Store CSV data in SQL database
                    self._store_csv_in_database(result)
                else:
                    failed_downloads += 1
                    logger.error(f"❌ Failed to download {team_name}: {result.get('error', 'Unknown error')}")
                
                # Delay between teams to avoid overwhelming the server
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Unexpected error processing {team_name}: {e}")
                results[team_id] = {"error": str(e), "team_name": team_name}
                failed_downloads += 1
        
        summary = {
            "season": self.season,
            "total_teams": len(all_teams),
            "successful_downloads": successful_downloads,
            "failed_downloads": failed_downloads,
            "download_timestamp": datetime.now().isoformat(),
            "results": results
        }
        
        logger.info(f"✅ Season CSV download complete: {successful_downloads}/{len(all_teams)} teams successful")
        return summary
    
    def _store_csv_in_database(self, download_result: Dict[str, Any]):
        """Store downloaded CSV data in SQL database"""
        try:
            csv_file_path = download_result.get("csv_file_path")
            if not csv_file_path or not os.path.exists(csv_file_path):
                return
            
            # Parse CSV and store in database
            # This would implement the actual CSV parsing and database storage
            logger.info(f"📊 Storing CSV data in database for {download_result['team_name']}")
            
            # TODO: Implement CSV parsing and database storage
            # This would read the CSV file and insert the data into the appropriate tables
            
        except Exception as e:
            logger.error(f"Error storing CSV in database: {e}")
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 WebDriver closed")

def main():
    """Main function to download season CSV data"""
    print(f"🏒 AJHL {2025-2026} Season CSV Downloader")
    print("=" * 60)
    
    downloader = AJHLSeasonCSVDownloader(headless=False)
    
    try:
        # Authenticate
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        if not downloader.authenticate(HUDL_USERNAME, HUDL_PASSWORD):
            print("❌ Authentication failed")
            return
        
        # Download all teams
        results = downloader.download_all_teams_season_csv()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ajhl_season_download_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Download results saved to: {filename}")
        
        # Print summary
        print(f"\n📊 Download Summary:")
        print(f"  Season: {results.get('season', 'Unknown')}")
        print(f"  Total teams: {results.get('total_teams', 0)}")
        print(f"  Successful downloads: {results.get('successful_downloads', 0)}")
        print(f"  Failed downloads: {results.get('failed_downloads', 0)}")
        
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        downloader.close()

if __name__ == "__main__":
    main()
