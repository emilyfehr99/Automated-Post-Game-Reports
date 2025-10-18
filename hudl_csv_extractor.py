#!/usr/bin/env python3
"""
Hudl Instat CSV Extractor
Extracts play-by-play CSV data from Hudl Instat games for the Bobcats team
"""

import time
import json
import logging
import os
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GameData:
    """Represents a game with its data"""
    game_id: str
    home_team: str
    away_team: str
    score: str
    date: str
    league: str
    csv_downloaded: bool = False
    csv_path: Optional[str] = None

class HudlCSVExtractor:
    """Extracts CSV play-by-play data from Hudl Instat games"""
    
    def __init__(self, headless: bool = True, user_identifier: str = None):
        """Initialize the CSV extractor"""
        self.base_url = "https://app.hudl.com/instat/hockey/teams/21479"
        self.driver = None
        self.headless = headless
        self.user_identifier = user_identifier or "default_user"
        self.download_dir = f"/tmp/hudl_downloads_{self.user_identifier}"
        self.games_data = []
        
        # Create download directory
        os.makedirs(self.download_dir, exist_ok=True)
        
    def setup_driver(self):
        """Setup Chrome WebDriver for CSV extraction"""
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
            
            # Set download preferences
            prefs = {
                "download.default_directory": self.download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # User-specific profile
            profile_dir = f"/tmp/hudl_profile_{self.user_identifier}"
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument(f"--profile-directory=Profile_{self.user_identifier}")
            
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
            logger.info("✅ Chrome WebDriver initialized for CSV extraction")
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
                logger.info("✅ Successfully authenticated with Hudl Instat")
                return True
            else:
                logger.error("❌ Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def get_games_list(self) -> List[GameData]:
        """Get list of games from the team page"""
        try:
            logger.info("🔍 Getting games list from team page...")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".MatchRow-sc-ibjx1d-0"))
            )
            
            games = []
            
            # Find all game rows
            game_rows = self.driver.find_elements(By.CSS_SELECTOR, ".MatchRow-sc-ibjx1d-0")
            logger.info(f"Found {len(game_rows)} game rows")
            
            for row in game_rows:
                try:
                    # Extract game information
                    game_data = self._extract_game_info(row)
                    if game_data:
                        games.append(game_data)
                        logger.info(f"Extracted game: {game_data.home_team} vs {game_data.away_team} ({game_data.score})")
                except Exception as e:
                    logger.warning(f"Error extracting game info: {e}")
                    continue
            
            self.games_data = games
            logger.info(f"✅ Successfully extracted {len(games)} games")
            return games
            
        except Exception as e:
            logger.error(f"❌ Error getting games list: {e}")
            return []
    
    def _extract_game_info(self, row_element) -> Optional[GameData]:
        """Extract game information from a row element"""
        try:
            # Extract game ID from the link
            link_element = row_element.find_element(By.CSS_SELECTOR, "a[href*='/instat/hockey/matches/']")
            href = link_element.get_attribute("href")
            game_id = href.split("/matches/")[-1] if "/matches/" in href else "unknown"
            
            # Extract team names and score
            team_elements = row_element.find_elements(By.CSS_SELECTOR, ".MatchRow__TeamName-sc-ibjx1d-5")
            if len(team_elements) >= 3:
                home_team = team_elements[0].text.strip()
                score = team_elements[1].text.strip()
                away_team = team_elements[2].text.strip()
            else:
                return None
            
            # Extract date and league
            additional_info = row_element.find_element(By.CSS_SELECTOR, ".MatchRow__AdditionalInfo-sc-ibjx1d-4")
            info_text = additional_info.text.strip()
            
            # Parse date and league from info text
            date = "Unknown"
            league = "Unknown"
            if ". " in info_text:
                parts = info_text.split(". ", 1)
                date = parts[0]
                if len(parts) > 1:
                    league = parts[1]
            
            return GameData(
                game_id=game_id,
                home_team=home_team,
                away_team=away_team,
                score=score,
                date=date,
                league=league
            )
            
        except Exception as e:
            logger.warning(f"Error extracting game info from row: {e}")
            return None
    
    def download_game_csv(self, game: GameData, data_selections: Dict[str, List[str]] = None) -> bool:
        """Download CSV data for a specific game with custom data selections"""
        try:
            logger.info(f"📥 Downloading CSV for game: {game.home_team} vs {game.away_team}")
            
            # Navigate to game page
            game_url = f"https://app.hudl.com/instat/hockey/matches/{game.game_id}"
            self.driver.get(game_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for download button
            download_selectors = [
                ".styled__DownloadIcon-sc-1s49rmo-1",
                "[class*='DownloadIcon']",
                "[class*='download']",
                "i[class*='download']",
                "button[class*='download']"
            ]
            
            download_button = None
            for selector in download_selectors:
                try:
                    download_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if download_button.is_displayed():
                        break
                except:
                    continue
            
            if not download_button:
                logger.warning(f"⚠️  Download button not found for game {game.game_id}")
                return False
            
            # Click download button
            ActionChains(self.driver).move_to_element(download_button).click().perform()
            time.sleep(2)
            
            # Wait for the data selection popup to appear
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".styled__PopupCheckboxesWrapper-sc-mg4s9t-0"))
                )
                logger.info("✅ Data selection popup appeared")
            except:
                logger.warning("⚠️  Data selection popup not found, trying direct CSV download")
                return self._try_direct_csv_download()
            
            # Configure data selections
            if data_selections:
                self._configure_data_selections(data_selections)
            else:
                # Use default selections (all main statistics)
                self._configure_default_selections()
            
            # Change format to CSV if needed
            self._change_format_to_csv()
            
            # Click OK to start download
            ok_button = self.driver.find_element(By.CSS_SELECTOR, "button.styled__Button-sc-1qmng2y-2.lbnSyW")
            ok_button.click()
            time.sleep(3)
            
            logger.info("✅ CSV download initiated with selected data")
            
            # Wait for download to complete
            downloaded_files = self._wait_for_download()
            if downloaded_files:
                csv_file = downloaded_files[0]
                game.csv_downloaded = True
                game.csv_path = csv_file
                logger.info(f"✅ CSV downloaded: {csv_file}")
                return True
            else:
                logger.warning("⚠️  No CSV file downloaded")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error downloading CSV for game {game.game_id}: {e}")
            return False
    
    def _configure_data_selections(self, selections: Dict[str, List[str]]):
        """Configure specific data selections in the popup"""
        try:
            # Map selection categories to their checkboxes
            category_mapping = {
                'shifts': ['All shifts', 'Even strength shifts', 'Power play shifts', 'Penalty kill shifts'],
                'main_stats': ['Goals', 'Assists', 'Penalties', 'Hits'],
                'shots': ['Shots', 'Shots on goal', 'Blocked shots', 'Missed shots'],
                'passes': ['Passes', 'Accurate passes', 'Inaccurate passes', 'Passes to the slot'],
                'puck_battles': ['Puck battles', 'Puck battles won', 'Puck battles lost'],
                'entries_breakouts': ['Entries', 'Breakouts', 'Faceoffs', 'Faceoffs won', 'Faceoffs lost'],
                'goalie': ['Goals against', 'Shots against', 'Saves']
            }
            
            for category, items in selections.items():
                if category in category_mapping:
                    for item in items:
                        self._select_checkbox_by_text(item)
            
            logger.info("✅ Data selections configured")
            
        except Exception as e:
            logger.warning(f"⚠️  Error configuring data selections: {e}")
    
    def _configure_default_selections(self):
        """Configure default data selections (comprehensive play-by-play data)"""
        try:
            # Select key categories for play-by-play analysis
            default_selections = [
                'All shifts',
                'Goals', 'Assists', 'Penalties', 'Hits',
                'Shots', 'Shots on goal', 'Blocked shots',
                'Passes', 'Accurate passes', 'Inaccurate passes',
                'Puck battles', 'Puck battles won', 'Puck battles lost',
                'Entries', 'Breakouts',
                'Faceoffs', 'Faceoffs won', 'Faceoffs lost',
                'Goals against', 'Shots against', 'Saves'
            ]
            
            for selection in default_selections:
                self._select_checkbox_by_text(selection)
            
            logger.info("✅ Default data selections configured")
            
        except Exception as e:
            logger.warning(f"⚠️  Error configuring default selections: {e}")
    
    def _select_checkbox_by_text(self, text: str):
        """Select a checkbox by its text content"""
        try:
            # Look for checkbox with specific text
            xpath = f"//span[contains(text(), '{text}')]/ancestor::div[contains(@class, 'BlockCheckbox')]"
            checkbox = self.driver.find_element(By.XPATH, xpath)
            
            if checkbox.is_displayed():
                checkbox.click()
                logger.info(f"✅ Selected: {text}")
            else:
                logger.warning(f"⚠️  Checkbox not visible: {text}")
                
        except Exception as e:
            logger.warning(f"⚠️  Could not select checkbox '{text}': {e}")
    
    def _change_format_to_csv(self):
        """Change the format from XML to CSV"""
        try:
            # Find the format dropdown
            format_dropdown = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Format')]/following-sibling::div")
            format_dropdown.click()
            time.sleep(1)
            
            # Look for CSV option
            csv_option = self.driver.find_element(By.XPATH, "//span[contains(text(), 'CSV')]")
            csv_option.click()
            time.sleep(1)
            
            logger.info("✅ Format changed to CSV")
            
        except Exception as e:
            logger.warning(f"⚠️  Could not change format to CSV: {e}")
    
    def _try_direct_csv_download(self):
        """Try direct CSV download without data selection"""
        try:
            # Look for CSV download option
            csv_selectors = [
                "a[href*='.csv']",
                "button[data-testid*='csv']",
                "[class*='csv']",
                "text()='CSV'",
                "text()='Download CSV'"
            ]
            
            csv_option = None
            for selector in csv_selectors:
                try:
                    if "text()=" in selector:
                        csv_option = self.driver.find_element(By.XPATH, f"//*[contains(text(), 'CSV')]")
                    else:
                        csv_option = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if csv_option.is_displayed():
                        break
                except:
                    continue
            
            if csv_option:
                csv_option.click()
                time.sleep(3)
                logger.info("✅ Direct CSV download initiated")
                return True
            else:
                logger.warning("⚠️  No CSV download option found")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️  Direct CSV download failed: {e}")
            return False
    
    def _wait_for_download(self, timeout: int = 30) -> List[str]:
        """Wait for download to complete and return downloaded files"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check for downloaded files
                files = [f for f in os.listdir(self.download_dir) 
                        if f.endswith(('.csv', '.xlsx', '.txt')) and not f.startswith('.')]
                
                if files:
                    # Move files to avoid conflicts
                    for file in files:
                        old_path = os.path.join(self.download_dir, file)
                        new_path = os.path.join(self.download_dir, f"{int(time.time())}_{file}")
                        os.rename(old_path, new_path)
                    
                    return [os.path.join(self.download_dir, f) for f in os.listdir(self.download_dir) 
                           if f.endswith(('.csv', '.xlsx', '.txt')) and not f.startswith('.')]
                
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Error checking downloads: {e}")
                time.sleep(1)
        
        return []
    
    def download_all_games_csv(self, max_games: int = 5) -> List[GameData]:
        """Download CSV data for all games (limited to max_games)"""
        try:
            # Get games list first
            games = self.get_games_list()
            if not games:
                logger.error("❌ No games found")
                return []
            
            # Limit to most recent games
            games_to_process = games[:max_games]
            logger.info(f"📊 Processing {len(games_to_process)} games for CSV download")
            
            successful_downloads = []
            
            for i, game in enumerate(games_to_process, 1):
                logger.info(f"🔄 Processing game {i}/{len(games_to_process)}: {game.home_team} vs {game.away_team}")
                
                if self.download_game_csv(game):
                    successful_downloads.append(game)
                    logger.info(f"✅ Successfully downloaded CSV for game {i}")
                else:
                    logger.warning(f"⚠️  Failed to download CSV for game {i}")
                
                # Small delay between downloads
                time.sleep(2)
            
            logger.info(f"🎉 CSV download complete: {len(successful_downloads)}/{len(games_to_process)} successful")
            return successful_downloads
            
        except Exception as e:
            logger.error(f"❌ Error downloading all games CSV: {e}")
            return []
    
    def process_csv_data(self, game: GameData) -> Optional[pd.DataFrame]:
        """Process downloaded CSV data"""
        if not game.csv_path or not os.path.exists(game.csv_path):
            logger.warning(f"⚠️  No CSV file found for game {game.game_id}")
            return None
        
        try:
            # Read CSV file
            df = pd.read_csv(game.csv_path)
            logger.info(f"✅ Processed CSV: {len(df)} rows, {len(df.columns)} columns")
            logger.info(f"📊 Columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error processing CSV for game {game.game_id}: {e}")
            return None
    
    def export_games_summary(self, filename: str = None) -> str:
        """Export summary of all games and their CSV status"""
        if not filename:
            filename = f"bobcats_games_summary_{int(time.time())}.json"
        
        summary = {
            "team": "Lloydminster Bobcats",
            "team_id": "21479",
            "total_games": len(self.games_data),
            "csv_downloaded": sum(1 for game in self.games_data if game.csv_downloaded),
            "games": []
        }
        
        for game in self.games_data:
            summary["games"].append({
                "game_id": game.game_id,
                "home_team": game.home_team,
                "away_team": game.away_team,
                "score": game.score,
                "date": game.date,
                "league": game.league,
                "csv_downloaded": game.csv_downloaded,
                "csv_path": game.csv_path
            })
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"📄 Games summary exported to: {filename}")
        return filename
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 WebDriver closed")

def main():
    """Example usage of the CSV extractor"""
    print("🏒 Hudl Instat CSV Extractor")
    print("=" * 50)
    
    # Initialize extractor
    extractor = HudlCSVExtractor(headless=False)  # Set to False to see the browser
    
    try:
        # Authenticate
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        if not extractor.authenticate(HUDL_USERNAME, HUDL_PASSWORD):
            print("❌ Authentication failed")
            return
        
        # Download CSV data for recent games
        print("\n📥 Downloading CSV data for recent games...")
        successful_games = extractor.download_all_games_csv(max_games=3)
        
        print(f"\n✅ Successfully downloaded {len(successful_games)} games")
        
        # Process CSV data
        for game in successful_games:
            if game.csv_path:
                print(f"\n📊 Processing CSV for: {game.home_team} vs {game.away_team}")
                df = extractor.process_csv_data(game)
                if df is not None:
                    print(f"   Rows: {len(df)}")
                    print(f"   Columns: {list(df.columns)}")
        
        # Export summary
        summary_file = extractor.export_games_summary()
        print(f"\n📄 Summary exported to: {summary_file}")
        
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main()
