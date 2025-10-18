#!/usr/bin/env python3
"""
Tableau-specific scraper for All Three Zones player data
"""

import requests
import json
import logging
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PlayerData:
    """Data class for player statistics from Tableau"""
    name: str
    team: str
    position: str
    games_played: int
    stats: Dict[str, Any]

class TableauScraper:
    """Scraper for Tableau visualizations containing player data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.is_authenticated = False
        
        # Get credentials from environment
        self.username = os.getenv('A3Z_USERNAME')
        self.password = os.getenv('A3Z_PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError("A3Z_USERNAME and A3Z_PASSWORD must be set in environment variables")
    
    def login(self) -> bool:
        """Login to All Three Zones website"""
        try:
            logger.info("Logging into All Three Zones...")
            
            # Get the login page first
            login_url = "https://www.allthreezones.com/player-cards.html"
            response = self.session.get(login_url)
            
            # Prepare login data
            login_data = {
                'login-email': self.username,
                'login-password': self.password,
            }
            
            # Set headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.allthreezones.com',
                'Referer': 'https://www.allthreezones.com/player-cards.html'
            }
            
            # Try to login
            login_response = self.session.post(
                'https://www.allthreezones.com/ajax/api/JsonRPC/Membership/',
                data=login_data,
                headers=headers,
                allow_redirects=True
            )
            
            if login_response.status_code == 200:
                self.is_authenticated = True
                logger.info("Successfully logged in to All Three Zones")
                return True
            else:
                logger.error("Login failed")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def get_tableau_data(self) -> List[PlayerData]:
        """Extract data from the Tableau visualization"""
        if not self.is_authenticated:
            if not self.login():
                raise Exception("Failed to authenticate with All Three Zones")
        
        try:
            # Get the player cards page
            player_cards_url = "https://www.allthreezones.com/player-cards.html"
            response = self.session.get(player_cards_url)
            
            if response.status_code != 200:
                logger.error(f"Failed to get player cards page: {response.status_code}")
                return []
            
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
            tableau_response = self.session.get(tableau_src)
            if tableau_response.status_code != 200:
                logger.error(f"Failed to get Tableau page: {tableau_response.status_code}")
                return []
            
            # Parse the Tableau page
            tableau_soup = BeautifulSoup(tableau_response.content, 'html.parser')
            
            # Look for data in the Tableau page
            return self._extract_tableau_data(tableau_soup, tableau_src)
            
        except Exception as e:
            logger.error(f"Error getting Tableau data: {e}")
            return []
    
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
    
    def search_players(self, query: str) -> List[PlayerData]:
        """Search for players by name"""
        all_players = self.get_tableau_data()
        
        # Filter by query
        matching_players = []
        query_lower = query.lower()
        
        for player in all_players:
            if query_lower in player.name.lower():
                matching_players.append(player)
        
        return matching_players
    
    def get_players_by_team(self, team: str) -> List[PlayerData]:
        """Get players by team"""
        all_players = self.get_tableau_data()
        
        # Filter by team
        team_players = []
        team_lower = team.lower()
        
        for player in all_players:
            if team_lower in player.team.lower():
                team_players.append(player)
        
        return team_players

# Test the Tableau scraper
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    scraper = TableauScraper()
    
    if scraper.login():
        print("✅ Successfully logged in")
        
        # Get all players
        players = scraper.get_tableau_data()
        print(f"Found {len(players)} players")
        
        for player in players[:3]:  # Show first 3
            print(f"  {player.name} ({player.team}) - {player.position}")
        
        # Test search
        search_results = scraper.search_players("McDavid")
        print(f"\nSearch results for 'McDavid': {len(search_results)}")
        
    else:
        print("❌ Login failed") 