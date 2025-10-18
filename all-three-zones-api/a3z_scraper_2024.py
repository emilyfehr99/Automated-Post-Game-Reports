
import os
import time
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

# Import configuration
from config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PlayerData:
    """Data class for player statistics"""
    name: str
    team: str
    position: str
    games_played: int
    stats: Dict[str, Any]

class AllThreeZonesScraper2024:
    """Scraper for All Three Zones hockey data site with 2024-25 season support"""
    
    def __init__(self):
        self.base_url = "https://www.allthreezones.com"
        self.session = requests.Session()
        self.driver = None
        self.is_authenticated = False
        
        # Get credentials from config
        self.username = Config.A3Z_USERNAME
        self.password = Config.A3Z_PASSWORD
        
        if not self.username or not self.password:
            raise ValueError("A3Z_USERNAME and A3Z_PASSWORD must be set in config")
    
    def setup_driver(self):
        """Setup Chrome driver with options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Find Chrome executable
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser"
            ]
            
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    chrome_options.binary_location = chrome_path
                    logger.info(f"Found Chrome at: {chrome_path}")
                    break
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome driver setup successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def login(self):
        """Login to All Three Zones"""
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False
            
            logger.info("Using Selenium for login...")
            logger.info("Navigating to All Three Zones login page...")
            
            # Navigate to login page
            self.driver.get("https://www.allthreezones.com/player-cards.html")
            time.sleep(3)
            
            # Look for login form
            try:
                # Try to find email field
                email_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "login-email"))
                )
                email_field.send_keys(self.username)
                
                # Find password field
                password_field = self.driver.find_element(By.NAME, "login-password")
                password_field.send_keys(self.password)
                
                # Find and click login button
                login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign In')]")
                login_button.click()
                
                time.sleep(5)  # Wait for login to complete
                
                # Check if login was successful
                if "login" not in self.driver.current_url.lower():
                    self.is_authenticated = True
                    logger.info("Successfully logged in to All Three Zones")
                    return True
                else:
                    logger.error("Login failed - still on login page")
                    return False
                    
            except Exception as e:
                logger.error(f"Login form not found or error: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def select_season_2024_25(self):
        """Select the 2024-25 season from the dropdown"""
        try:
            if not self.is_authenticated:
                if not self.login():
                    return False
            
            logger.info("Selecting 2024-25 season...")
            
            # Wait for page to load
            time.sleep(3)
            
            # Look for year dropdown - try different selectors
            year_selectors = [
                "select[name*='year']",
                "select[id*='year']",
                "select[class*='year']",
                "select",
                ".year-select",
                "#year-select"
            ]
            
            year_dropdown = None
            for selector in year_selectors:
                try:
                    year_dropdown = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found year dropdown with selector: {selector}")
                    break
                except:
                    continue
            
            if not year_dropdown:
                logger.warning("No year dropdown found - may already be on 2024-25 season")
                return True
            
            # Create Select object
            select = Select(year_dropdown)
            
            # Look for 2024-25 option
            options = [option.text for option in select.options]
            logger.info(f"Available year options: {options}")
            
            # Try different variations of 2024-25
            target_options = ["2024-25", "2024-2025", "2024", "2025", "24-25"]
            
            for target in target_options:
                try:
                    select.select_by_visible_text(target)
                    logger.info(f"Selected season: {target}")
                    time.sleep(3)  # Wait for data to load
                    return True
                except:
                    continue
            
            logger.warning("Could not find 2024-25 season option")
            return False
            
        except Exception as e:
            logger.error(f"Error selecting season: {e}")
            return False
    
    def get_all_players_2024_25(self):
        """Get all players for the 2024-25 season"""
        try:
            if not self.is_authenticated:
                if not self.login():
                    return []
            
            # Select 2024-25 season
            if not self.select_season_2024_25():
                logger.warning("Could not select 2024-25 season, proceeding anyway")
            
            # Wait for data to load
            time.sleep(5)
            
            # Get page source and extract data
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Look for player data in the page
            players = self._extract_player_data_from_page(soup)
            
            logger.info(f"Found {len(players)} players for 2024-25 season")
            return players
            
        except Exception as e:
            logger.error(f"Error getting 2024-25 players: {e}")
            return []
    
    def _extract_player_data_from_page(self, soup: BeautifulSoup) -> List[PlayerData]:
        """Extract player data from the page"""
        players = []
        
        try:
            # Look for player data in various formats
            # This is a simplified version - would need to be adjusted based on actual page structure
            
            # Look for tables with player data
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        try:
                            name = cells[0].get_text(strip=True)
                            team = cells[1].get_text(strip=True) if len(cells) > 1 else "Unknown"
                            position = cells[2].get_text(strip=True) if len(cells) > 2 else "Unknown"
                            
                            if name and name != "Unknown" and len(name) > 2:
                                player = PlayerData(
                                    name=name,
                                    team=team,
                                    position=position,
                                    games_played=0,
                                    stats={}
                                )
                                players.append(player)
                        except:
                            continue
            
            # If no table data found, look for other data structures
            if not players:
                # Look for div elements with player information
                player_divs = soup.find_all('div', class_=lambda x: x and 'player' in x.lower())
                for div in player_divs:
                    text = div.get_text(strip=True)
                    if len(text) > 5 and any(word in text.lower() for word in ['crosby', 'mcdavid', 'ovechkin']):
                        # This is a placeholder - would need proper parsing
                        pass
            
        except Exception as e:
            logger.error(f"Error extracting player data: {e}")
        
        return players
    
    def close(self):
        """Close the scraper"""
        if self.driver:
            self.driver.quit()
            logger.info("Scraper closed")
