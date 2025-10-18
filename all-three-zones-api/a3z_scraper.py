import os
import time
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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

class AllThreeZonesScraper:
    """Scraper for All Three Zones hockey data site"""
    
    def __init__(self):
        self.base_url = "https://www.allthreezones.com"
        self.session = requests.Session()
        self.driver = None
        self.is_authenticated = False
        
        # Get credentials from config
        self.username = Config.A3Z_USERNAME
        self.password = Config.A3Z_PASSWORD
        
        if not self.username or not self.password:
            raise ValueError("A3Z_USERNAME and A3Z_PASSWORD must be set in environment variables or credentials.py")
    
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            
            # Try to find Chrome in common locations
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium"
            ]
            
            chrome_found = False
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_options.binary_location = path
                    chrome_found = True
                    logger.info(f"Found Chrome at: {path}")
                    break
            
            if not chrome_found:
                logger.warning("Chrome not found in common locations, trying default")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome WebDriver: {e}")
            logger.info("Falling back to requests-only mode")
            self.driver = None
            return None
    
    def login(self) -> bool:
        """Login to All Three Zones website"""
        try:
            # Try Selenium first if available
            if not self.driver:
                self.setup_driver()
            
            if self.driver:
                logger.info("Using Selenium for login...")
                return self._login_with_selenium()
            else:
                logger.info("Using requests for login...")
                return self._login_with_requests()
                
        except Exception as e:
            logger.error(f"Failed to login: {e}")
            return False
    
    def _login_with_selenium(self) -> bool:
        """Login using Selenium WebDriver"""
        try:
            logger.info("Navigating to All Three Zones login page...")
            # Go directly to the player cards page which has the login form
            self.driver.get("https://www.allthreezones.com/player-cards.html")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for login form elements - based on the actual site structure
            try:
                # Try to find email/username field
                username_field = None
                try:
                    username_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.NAME, "login-email"))
                    )
                except:
                    try:
                        username_field = self.driver.find_element(By.NAME, "email")
                    except:
                        try:
                            username_field = self.driver.find_element(By.NAME, "username")
                        except:
                            username_field = self.driver.find_element(By.ID, "email")
                
                # Find password field
                password_field = self.driver.find_element(By.NAME, "login-password")
                
                # Fill in credentials
                username_field.clear()
                username_field.send_keys(self.username)
                
                password_field.clear()
                password_field.send_keys(self.password)
                
                # Find and click login button
                login_button = None
                try:
                    login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Log in')]")
                except:
                    try:
                        login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                    except:
                        login_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
                
                login_button.click()
                
                # Wait for successful login
                time.sleep(5)
                
                # Check if login was successful - look for player cards content
                page_source = self.driver.page_source.lower()
                if "player" in page_source and ("card" in page_source or "stats" in page_source):
                    self.is_authenticated = True
                    logger.info("Successfully logged in to All Three Zones")
                    return True
                else:
                    logger.error("Login failed - still on login page")
                    return False
                    
            except Exception as e:
                logger.error(f"Error during Selenium login: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup driver or navigate to site: {e}")
            return False
    
    def _login_with_requests(self) -> bool:
        """Login using requests session"""
        try:
            logger.info("Attempting login with requests...")
            
            # Get the login page first to get any CSRF tokens
            response = self.session.get("https://www.allthreezones.com/player-cards.html")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for CSRF token
            csrf_token = None
            csrf_input = soup.find('input', {'name': 'csrf_token'}) or \
                        soup.find('input', {'name': '_token'}) or \
                        soup.find('input', {'name': 'authenticity_token'})
            
            if csrf_input:
                csrf_token = csrf_input.get('value')
                logger.info("Found CSRF token")
            
            # Prepare login data
            login_data = {
                'login-email': self.username,  # Correct field name from the form
                'login-password': self.password,  # Correct field name from the form
            }
            
            if csrf_token:
                login_data['csrf_token'] = csrf_token
            
            # Set headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.allthreezones.com',
                'Referer': 'https://www.allthreezones.com/player-cards.html'
            }
            
            # Try different login endpoints
            login_endpoints = [
                'https://www.allthreezones.com/ajax/api/JsonRPC/Membership/',
                'https://www.allthreezones.com/login',
                'https://www.allthreezones.com/auth/login',
                'https://www.allthreezones.com/player-cards.html'
            ]
            
            for endpoint in login_endpoints:
                try:
                    logger.info(f"Trying login endpoint: {endpoint}")
                    login_response = self.session.post(
                        endpoint,
                        data=login_data,
                        headers=headers,
                        allow_redirects=True
                    )
                    
                    # Check if login was successful
                    if login_response.status_code == 200:
                        # Check if we're still on login page or have access to content
                        if "login" not in login_response.url.lower() or "player" in login_response.text.lower():
                            self.is_authenticated = True
                            logger.info("Successfully logged in using requests session")
                            return True
                    
                except Exception as e:
                    logger.warning(f"Failed to login with endpoint {endpoint}: {e}")
                    continue
            
            logger.error("All login attempts failed")
            return False
                
        except Exception as e:
            logger.error(f"Requests login failed: {e}")
            return False
    
    def get_player_data(self, player_name: str = None, team: str = None) -> List[PlayerData]:
        """Extract player data from the Tableau visualization"""
        if not self.is_authenticated:
            if not self.login():
                raise Exception("Failed to authenticate with All Three Zones")
        
        try:
            # Get the player cards page
            player_cards_url = "https://www.allthreezones.com/player-cards.html"
            
            if self.driver:
                self.driver.get(player_cards_url)
                time.sleep(3)  # Wait for page to load
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            else:
                response = self.session.get(player_cards_url)
                soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the Tableau iframe
            tableau_iframe = soup.find('iframe', class_='tableauViz')
            if not tableau_iframe:
                logger.error("No Tableau iframe found")
                return []
            
            # Extract the Tableau URL
            tableau_src = tableau_iframe.get('src')
            if not tableau_src:
                logger.error("No Tableau src found")
                return []
            
            logger.info(f"Found Tableau URL: {tableau_src}")
            
            # Get the Tableau page
            if self.driver:
                self.driver.get(tableau_src)
                time.sleep(5)  # Wait for Tableau to load
                tableau_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            else:
                tableau_response = self.session.get(tableau_src)
                tableau_soup = BeautifulSoup(tableau_response.content, 'html.parser')
            
            # Extract data from Tableau
            players = self._extract_tableau_data(tableau_soup, tableau_src)
            
            # Filter by player name or team if specified
            if player_name:
                players = [p for p in players if player_name.lower() in p.name.lower()]
            if team:
                players = [p for p in players if team.lower() in p.team.lower()]
            
            return players
            
        except Exception as e:
            logger.error(f"Error getting player data: {e}")
            return []
    
    def _parse_player_data(self, soup: BeautifulSoup, player_name: str = None, team: str = None) -> List[PlayerData]:
        """Parse player data from BeautifulSoup object"""
        players = []
        
        try:
            # Look for various possible player data structures
            # Try different selectors that might contain player information
            player_elements = []
            
            # Look for tables with player data
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) > 2:  # Likely a data row
                        player_elements.append(row)
            
            # Look for div elements that might contain player cards
            player_divs = soup.find_all('div', class_=lambda x: x and any(word in x.lower() for word in ['player', 'card', 'stat']))
            player_elements.extend(player_divs)
            
            # Look for any elements with player names
            name_elements = soup.find_all(text=lambda text: text and any(word in text.lower() for word in ['mcdavid', 'crosby', 'ovechkin', 'matthews']))
            for name_elem in name_elements:
                parent = name_elem.parent
                if parent and parent not in player_elements:
                    player_elements.append(parent)
            
            logger.info(f"Found {len(player_elements)} potential player elements")
            
            for element in player_elements:
                try:
                    # Extract player information - try multiple approaches
                    name = self._extract_player_name(element)
                    team_name = self._extract_player_team(element)
                    position = self._extract_player_position(element)
                    
                    if name and name != "Unknown":
                        # Extract stats
                        stats = self._extract_player_stats(element)
                        
                        player_data = PlayerData(
                            name=name,
                            team=team_name,
                            position=position,
                            games_played=stats.get('games_played', 0),
                            stats=stats
                        )
                        
                        players.append(player_data)
                        logger.info(f"Parsed player: {name} ({team_name})")
                    
                except Exception as e:
                    logger.warning(f"Error parsing player element: {e}")
                    continue
            
            # Filter by player name or team if specified
            if player_name:
                players = [p for p in players if player_name.lower() in p.name.lower()]
            if team:
                players = [p for p in players if team.lower() in p.team.lower()]
            
            logger.info(f"Successfully parsed {len(players)} players")
            
        except Exception as e:
            logger.error(f"Error parsing player data: {e}")
        
        return players
    
    def _extract_player_name(self, element) -> str:
        """Extract player name from element"""
        # Try multiple approaches to find player name
        name_selectors = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'span', 'div', 'td', 'th'
        ]
        
        for selector in name_selectors:
            name_elem = element.find(selector)
            if name_elem:
                text = name_elem.get_text(strip=True)
                if text and len(text) > 2 and len(text) < 50:
                    return text
        
        # Look for text that might be a player name
        text = element.get_text(strip=True)
        if text and len(text) > 2 and len(text) < 50:
            return text
        
        return "Unknown"
    
    def _extract_player_team(self, element) -> str:
        """Extract player team from element"""
        # Look for team information
        team_keywords = ['oilers', 'leafs', 'canadiens', 'bruins', 'rangers', 'penguins', 'capitals']
        
        text = element.get_text(strip=True).lower()
        for keyword in team_keywords:
            if keyword in text:
                return keyword.title()
        
        return "Unknown"
    
    def _extract_player_position(self, element) -> str:
        """Extract player position from element"""
        # Look for position indicators
        position_keywords = ['c', 'lw', 'rw', 'd', 'g', 'center', 'left wing', 'right wing', 'defense', 'goalie']
        
        text = element.get_text(strip=True).lower()
        for keyword in position_keywords:
            if keyword in text:
                return keyword.upper()
        
        return "Unknown"
    
    def _extract_tableau_data(self, soup: BeautifulSoup, tableau_url: str) -> List[PlayerData]:
        """Extract player data from Tableau page"""
        players = []
        
        try:
            # Look for JavaScript data in the Tableau page
            scripts = soup.find_all('script')
            
            for script in scripts:
                script_text = script.get_text()
                
                # Look for player data in JavaScript
                if 'player' in script_text.lower() or 'data' in script_text.lower():
                    logger.info("Found potential data script")
                    
                    # Try to extract JSON data
                    import re
                    json_matches = re.findall(r'\{[^{}]*"player"[^{}]*\}', script_text)
                    for match in json_matches:
                        try:
                            data = json.loads(match)
                            if 'player' in data:
                                player = self._parse_player_from_json(data)
                                if player:
                                    players.append(player)
                        except json.JSONDecodeError:
                            continue
            
            # If no data found in scripts, try to get data via Tableau API
            if not players:
                players = self._get_tableau_api_data(tableau_url)
            
            logger.info(f"Extracted {len(players)} players from Tableau")
            return players
            
        except Exception as e:
            logger.error(f"Error extracting Tableau data: {e}")
            return []
    
    def _get_tableau_api_data(self, tableau_url: str) -> List[PlayerData]:
        """Try to get data via Tableau's API"""
        players = []
        
        try:
            # Extract the view ID from the URL
            # URL format: https://public.tableau.com/views/2021A3ZPlayerCardsWebversion/PlayerCards
            import re
            view_match = re.search(r'/views/([^/]+)/([^?]+)', tableau_url)
            if not view_match:
                logger.error("Could not extract view ID from Tableau URL")
                return []
            
            view_id = view_match.group(1)
            sheet_name = view_match.group(2)
            
            logger.info(f"Tableau view: {view_id}, sheet: {sheet_name}")
            
            # Try to get data via Tableau's data API
            data_url = f"https://public.tableau.com/views/{view_id}/{sheet_name}/data"
            response = self.session.get(data_url)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    players = self._parse_tableau_api_data(data)
                except json.JSONDecodeError:
                    logger.warning("Could not parse Tableau API response as JSON")
            
        except Exception as e:
            logger.error(f"Error getting Tableau API data: {e}")
        
        return players
    
    def _parse_tableau_api_data(self, data: Dict[str, Any]) -> List[PlayerData]:
        """Parse data from Tableau API response"""
        players = []
        
        try:
            # The structure depends on the Tableau API response
            # This is a placeholder - we'll need to adjust based on actual response
            if 'data' in data:
                for row in data['data']:
                    player = self._parse_player_from_api_row(row)
                    if player:
                        players.append(player)
            
        except Exception as e:
            logger.error(f"Error parsing Tableau API data: {e}")
        
        return players
    
    def _parse_player_from_json(self, data: Dict[str, Any]) -> Optional[PlayerData]:
        """Parse player data from JSON object"""
        try:
            name = data.get('player', data.get('name', 'Unknown'))
            team = data.get('team', 'Unknown')
            position = data.get('position', 'Unknown')
            games_played = data.get('games_played', data.get('gp', 0))
            
            # Extract stats
            stats = {}
            for key, value in data.items():
                if key not in ['player', 'name', 'team', 'position', 'games_played', 'gp']:
                    stats[key] = value
            
            return PlayerData(
                name=name,
                team=team,
                position=position,
                games_played=games_played,
                stats=stats
            )
            
        except Exception as e:
            logger.warning(f"Error parsing player JSON: {e}")
            return None
    
    def _parse_player_from_api_row(self, row: Dict[str, Any]) -> Optional[PlayerData]:
        """Parse player data from API row"""
        try:
            # This will need to be customized based on the actual API response structure
            name = row.get('player', row.get('name', 'Unknown'))
            team = row.get('team', 'Unknown')
            position = row.get('position', 'Unknown')
            games_played = row.get('games_played', row.get('gp', 0))
            
            # Extract stats
            stats = {}
            for key, value in row.items():
                if key not in ['player', 'name', 'team', 'position', 'games_played', 'gp']:
                    stats[key] = value
            
            return PlayerData(
                name=name,
                team=team,
                position=position,
                games_played=games_played,
                stats=stats
            )
            
        except Exception as e:
            logger.warning(f"Error parsing API row: {e}")
            return None
    
    def _extract_player_stats(self, card) -> Dict[str, Any]:
        """Extract statistics from a player card"""
        stats = {}
        
        try:
            # Look for common stat elements
            stat_elements = card.find_all('td', class_='stat') or \
                          card.find_all('span', class_='stat') or \
                          card.find_all('div', class_='stat')
            
            for elem in stat_elements:
                # Try to extract stat name and value
                stat_name = elem.get('data-stat') or elem.get('class', [''])[0]
                stat_value = elem.get_text(strip=True)
                
                if stat_name and stat_value:
                    try:
                        # Try to convert to number if possible
                        if '.' in stat_value:
                            stats[stat_name] = float(stat_value)
                        else:
                            stats[stat_name] = int(stat_value)
                    except ValueError:
                        stats[stat_name] = stat_value
            
        except Exception as e:
            logger.warning(f"Error extracting stats: {e}")
        
        return stats
    
    def get_team_data(self, team_name: str = None) -> Dict[str, Any]:
        """Get team-level statistics"""
        if not self.is_authenticated:
            if not self.login():
                raise Exception("Failed to authenticate with All Three Zones")
        
        try:
            team_url = f"{self.base_url}/team-pages" if not team_name else f"{self.base_url}/team/{team_name}"
            
            if self.driver:
                self.driver.get(team_url)
                time.sleep(2)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            else:
                response = self.session.get(team_url)
                soup = BeautifulSoup(response.content, 'html.parser')
            
            return self._parse_team_data(soup, team_name)
            
        except Exception as e:
            logger.error(f"Error getting team data: {e}")
            return {}
    
    def _parse_team_data(self, soup: BeautifulSoup, team_name: str = None) -> Dict[str, Any]:
        """Parse team data from BeautifulSoup object"""
        team_data = {}
        
        try:
            # Look for team statistics tables or cards
            team_stats = soup.find('table', class_='team-stats') or \
                        soup.find('div', class_='team-stats') or \
                        soup.find('div', class_='stats-container')
            
            if team_stats:
                # Extract team statistics
                stat_rows = team_stats.find_all('tr') or team_stats.find_all('div', class_='stat-row')
                
                for row in stat_rows:
                    try:
                        stat_name_elem = row.find('td', class_='stat-name') or row.find('span', class_='stat-name')
                        stat_value_elem = row.find('td', class_='stat-value') or row.find('span', class_='stat-value')
                        
                        if stat_name_elem and stat_value_elem:
                            stat_name = stat_name_elem.get_text(strip=True)
                            stat_value = stat_value_elem.get_text(strip=True)
                            
                            try:
                                if '.' in stat_value:
                                    team_data[stat_name] = float(stat_value)
                                else:
                                    team_data[stat_name] = int(stat_value)
                            except ValueError:
                                team_data[stat_name] = stat_value
                    
                    except Exception as e:
                        logger.warning(f"Error parsing team stat row: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Error parsing team data: {e}")
        
        return team_data
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        if self.session:
            self.session.close()

# Example usage
if __name__ == "__main__":
    scraper = AllThreeZonesScraper()
    try:
        if scraper.login():
            # Get all player data
            players = scraper.get_player_data()
            print(f"Found {len(players)} players")
            
            # Get team data
            team_data = scraper.get_team_data()
            print(f"Team data: {team_data}")
        else:
            print("Failed to login")
    finally:
        scraper.close() 