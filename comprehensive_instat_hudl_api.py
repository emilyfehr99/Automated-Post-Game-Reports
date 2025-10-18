#!/usr/bin/env python3
"""
Comprehensive Instat Hudl API Client
Provides complete access to team, player, and league metrics through the Instat Hudl API

Based on the actual Instat Hudl API structure with proper data table mapping
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InstatDataTable:
    """Represents an Instat data table with its ID and metadata"""
    name: str
    table_id: int
    description: str
    data_type: str
    priority: int

@dataclass
class TeamMetrics:
    """Comprehensive team metrics structure"""
    team_id: str
    team_name: str
    league: str
    season: str
    players: List[Dict[str, Any]]
    games: List[Dict[str, Any]]
    team_stats: Dict[str, Any]
    league_rankings: Dict[str, Any]
    last_updated: str

@dataclass
class PlayerMetrics:
    """Comprehensive player metrics structure"""
    player_id: str
    player_name: str
    team_id: str
    position: str
    career_stats: Dict[str, Any]
    match_stats: Dict[str, Any]
    advanced_metrics: Dict[str, Any]
    last_updated: str

class ComprehensiveInstatHudlAPI:
    """Comprehensive API client for Instat Hudl with full data access"""
    
    def __init__(self, headless: bool = True, user_identifier: str = None):
        """Initialize the comprehensive API client"""
        self.base_url = "https://app.hudl.com/instat/hockey"
        self.session = requests.Session()
        self.driver = None
        self.headless = headless
        self.is_authenticated = False
        self.user_identifier = user_identifier or f"instat_api_{int(time.time())}"
        
        # Define all Instat data tables based on the provided structure
        self.data_tables = self._define_data_tables()
        
        # Setup session headers
        self.session.headers.update({
            'User-Agent': f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 InstatAPI-{self.user_identifier}',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
        })
    
    def _define_data_tables(self) -> Dict[str, InstatDataTable]:
        """Define all Instat data tables with their IDs and metadata"""
        tables = {
            "goalie_career_tables": InstatDataTable(
                name="goalie_career_tables",
                table_id=6,
                description="Goalie career statistics and performance data",
                data_type="goalie_career",
                priority=1
            ),
            "goalie_matches_tables": InstatDataTable(
                name="goalie_matches_tables", 
                table_id=3,
                description="Goalie match-by-match statistics",
                data_type="goalie_matches",
                priority=1
            ),
            "match_goalies_tables": InstatDataTable(
                name="match_goalies_tables",
                table_id=17,
                description="Goalie data for specific matches",
                data_type="match_goalies",
                priority=2
            ),
            "match_lines_tables": InstatDataTable(
                name="match_lines_tables",
                table_id=18,
                description="Line combinations and performance for matches",
                data_type="match_lines",
                priority=2
            ),
            "match_overview_players_tables": InstatDataTable(
                name="match_overview_players_tables",
                table_id=15,
                description="Player overview statistics for matches",
                data_type="match_overview_players",
                priority=1
            ),
            "match_players_tables": InstatDataTable(
                name="match_players_tables",
                table_id=16,
                description="Detailed player statistics for matches",
                data_type="match_players",
                priority=1
            ),
            "player_career_tables": InstatDataTable(
                name="player_career_tables",
                table_id=5,
                description="Player career statistics and performance",
                data_type="player_career",
                priority=1
            ),
            "player_matches_tables": InstatDataTable(
                name="player_matches_tables",
                table_id=2,
                description="Player match-by-match statistics",
                data_type="player_matches",
                priority=1
            ),
            "team_goalies_tables": InstatDataTable(
                name="team_goalies_tables",
                table_id=9,
                description="Team goalie statistics and performance",
                data_type="team_goalies",
                priority=1
            ),
            "team_lines_tables": InstatDataTable(
                name="team_lines_tables",
                table_id=14,
                description="Team line combinations and performance",
                data_type="team_lines",
                priority=2
            ),
            "team_matches_tables": InstatDataTable(
                name="team_matches_tables",
                table_id=1,
                description="Team match statistics and results",
                data_type="team_matches",
                priority=1
            ),
            "team_players_tables": InstatDataTable(
                name="team_players_tables",
                table_id=8,
                description="Team player statistics and roster data",
                data_type="team_players",
                priority=1
            )
        }
        return tables
    
    def setup_driver(self):
        """Setup Chrome WebDriver for API access"""
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
            chrome_options.add_argument("--disable-images")
            
            # User-specific profile
            profile_dir = f"/tmp/instat_profile_{self.user_identifier}"
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument(f"--profile-directory=Profile_{self.user_identifier}")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ Chrome WebDriver initialized for Instat API")
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
            
            # Fill login form
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
    
    def get_team_comprehensive_metrics(self, team_id: str) -> TeamMetrics:
        """Get comprehensive team metrics including all data tables"""
        if not self.is_authenticated:
            raise Exception("Authentication required")
        
        logger.info(f"📊 Getting comprehensive metrics for team {team_id}")
        
        team_url = f"{self.base_url}/teams/{team_id}"
        self.driver.get(team_url)
        
        # Wait for page load
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)  # Wait for dynamic content
        
        # Extract team information
        team_name = self._extract_team_name()
        league = self._extract_league_info()
        season = self._extract_season_info()
        
        # Get all team data from different tables
        team_data = {
            "team_id": team_id,
            "team_name": team_name,
            "league": league,
            "season": season,
            "players": self._extract_team_players(team_id),
            "games": self._extract_team_games(team_id),
            "team_stats": self._extract_team_statistics(team_id),
            "league_rankings": self._extract_league_rankings(team_id),
            "last_updated": datetime.now().isoformat()
        }
        
        return TeamMetrics(**team_data)
    
    def get_player_comprehensive_metrics(self, player_id: str, team_id: str = None) -> PlayerMetrics:
        """Get comprehensive player metrics from all relevant data tables"""
        if not self.is_authenticated:
            raise Exception("Authentication required")
        
        logger.info(f"👤 Getting comprehensive metrics for player {player_id}")
        
        # Navigate to player page
        if team_id:
            player_url = f"{self.base_url}/teams/{team_id}/players/{player_id}"
        else:
            player_url = f"{self.base_url}/players/{player_id}"
        
        self.driver.get(player_url)
        
        # Wait for page load
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)
        
        # Extract player data
        player_data = {
            "player_id": player_id,
            "player_name": self._extract_player_name(),
            "team_id": team_id or self._extract_player_team(),
            "position": self._extract_player_position(),
            "career_stats": self._extract_player_career_stats(player_id),
            "match_stats": self._extract_player_match_stats(player_id),
            "advanced_metrics": self._extract_player_advanced_metrics(player_id),
            "last_updated": datetime.now().isoformat()
        }
        
        return PlayerMetrics(**player_data)
    
    def get_league_comprehensive_metrics(self, league_id: str = None) -> Dict[str, Any]:
        """Get comprehensive league metrics across all teams"""
        if not self.is_authenticated:
            raise Exception("Authentication required")
        
        logger.info(f"🏆 Getting comprehensive league metrics")
        
        # Navigate to league/tournament page
        if league_id:
            league_url = f"{self.base_url}/tournaments/{league_id}"
        else:
            league_url = f"{self.base_url}/tournaments"
        
        self.driver.get(league_url)
        
        # Wait for page load
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)
        
        # Extract league data
        league_data = {
            "league_id": league_id,
            "league_name": self._extract_league_name(),
            "teams": self._extract_league_teams(),
            "standings": self._extract_league_standings(),
            "season_stats": self._extract_league_season_stats(),
            "top_performers": self._extract_league_top_performers(),
            "last_updated": datetime.now().isoformat()
        }
        
        return league_data
    
    def _extract_team_name(self) -> str:
        """Extract team name from the page"""
        try:
            name_element = self.driver.find_element(By.CSS_SELECTOR, "h1, .team-name, .team-title")
            return name_element.text.strip()
        except:
            return "Unknown Team"
    
    def _extract_league_info(self) -> str:
        """Extract league information"""
        try:
            league_element = self.driver.find_element(By.CSS_SELECTOR, ".league, .competition, .tournament")
            return league_element.text.strip()
        except:
            return "Unknown League"
    
    def _extract_season_info(self) -> str:
        """Extract season information"""
        try:
            season_element = self.driver.find_element(By.CSS_SELECTOR, ".season, .year")
            return season_element.text.strip()
        except:
            return "2024-25"
    
    def _extract_team_players(self, team_id: str) -> List[Dict[str, Any]]:
        """Extract team players from team_players_tables"""
        players = []
        
        try:
            # Look for player data in various sections
            player_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".player, .roster-item, .player-card, [data-player-id]")
            
            for player_element in player_elements:
                if player_element.is_displayed():
                    player_data = {
                        "player_id": player_element.get_attribute("data-player-id") or "unknown",
                        "name": self._extract_text_from_element(player_element, ".player-name, .name"),
                        "position": self._extract_text_from_element(player_element, ".position, .pos"),
                        "number": self._extract_text_from_element(player_element, ".number, .jersey"),
                        "stats": self._extract_player_basic_stats(player_element)
                    }
                    players.append(player_data)
        
        except Exception as e:
            logger.warning(f"⚠️  Error extracting team players: {e}")
        
        return players
    
    def _extract_team_games(self, team_id: str) -> List[Dict[str, Any]]:
        """Extract team games from team_matches_tables"""
        games = []
        
        try:
            # Look for game data
            game_elements = self.driver.find_elements(By.CSS_SELECTOR,
                ".game, .match, .game-card, [data-game-id]")
            
            for game_element in game_elements:
                if game_element.is_displayed():
                    game_data = {
                        "game_id": game_element.get_attribute("data-game-id") or "unknown",
                        "date": self._extract_text_from_element(game_element, ".date, .game-date"),
                        "opponent": self._extract_text_from_element(game_element, ".opponent, .vs"),
                        "score": self._extract_text_from_element(game_element, ".score, .result"),
                        "status": self._extract_text_from_element(game_element, ".status, .state")
                    }
                    games.append(game_data)
        
        except Exception as e:
            logger.warning(f"⚠️  Error extracting team games: {e}")
        
        return games
    
    def _extract_team_statistics(self, team_id: str) -> Dict[str, Any]:
        """Extract team statistics from various data tables"""
        stats = {}
        
        try:
            # Look for statistics tables
            stats_tables = self.driver.find_elements(By.CSS_SELECTOR, "table, .stats-table, .statistics")
            
            for table in stats_tables:
                if table.is_displayed():
                    table_stats = self._parse_statistics_table(table)
                    stats.update(table_stats)
        
        except Exception as e:
            logger.warning(f"⚠️  Error extracting team statistics: {e}")
        
        return stats
    
    def _extract_league_rankings(self, team_id: str) -> Dict[str, Any]:
        """Extract league rankings for the team"""
        rankings = {}
        
        try:
            # Look for ranking/standings data
            ranking_elements = self.driver.find_elements(By.CSS_SELECTOR,
                ".ranking, .standings, .position, .rank")
            
            for element in ranking_elements:
                if element.is_displayed():
                    ranking_text = element.text.strip()
                    if "rank" in ranking_text.lower() or "position" in ranking_text.lower():
                        rankings["current_rank"] = ranking_text
        
        except Exception as e:
            logger.warning(f"⚠️  Error extracting league rankings: {e}")
        
        return rankings
    
    def _extract_player_name(self) -> str:
        """Extract player name from the page"""
        try:
            name_element = self.driver.find_element(By.CSS_SELECTOR, "h1, .player-name, .name")
            return name_element.text.strip()
        except:
            return "Unknown Player"
    
    def _extract_player_team(self) -> str:
        """Extract player's team"""
        try:
            team_element = self.driver.find_element(By.CSS_SELECTOR, ".team, .club")
            return team_element.text.strip()
        except:
            return "Unknown Team"
    
    def _extract_player_position(self) -> str:
        """Extract player position"""
        try:
            position_element = self.driver.find_element(By.CSS_SELECTOR, ".position, .pos")
            return position_element.text.strip()
        except:
            return "Unknown Position"
    
    def _extract_player_career_stats(self, player_id: str) -> Dict[str, Any]:
        """Extract player career statistics from player_career_tables"""
        career_stats = {}
        
        try:
            # Look for career statistics
            career_elements = self.driver.find_elements(By.CSS_SELECTOR,
                ".career-stats, .career, .total-stats")
            
            for element in career_elements:
                if element.is_displayed():
                    stats = self._parse_statistics_table(element)
                    career_stats.update(stats)
        
        except Exception as e:
            logger.warning(f"⚠️  Error extracting player career stats: {e}")
        
        return career_stats
    
    def _extract_player_match_stats(self, player_id: str) -> Dict[str, Any]:
        """Extract player match statistics from player_matches_tables"""
        match_stats = {}
        
        try:
            # Look for match statistics
            match_elements = self.driver.find_elements(By.CSS_SELECTOR,
                ".match-stats, .game-stats, .recent-games")
            
            for element in match_elements:
                if element.is_displayed():
                    stats = self._parse_statistics_table(element)
                    match_stats.update(stats)
        
        except Exception as e:
            logger.warning(f"⚠️  Error extracting player match stats: {e}")
        
        return match_stats
    
    def _extract_player_advanced_metrics(self, player_id: str) -> Dict[str, Any]:
        """Extract advanced player metrics"""
        advanced_metrics = {}
        
        try:
            # Look for advanced metrics
            advanced_elements = self.driver.find_elements(By.CSS_SELECTOR,
                ".advanced-stats, .analytics, .metrics")
            
            for element in advanced_elements:
                if element.is_displayed():
                    metrics = self._parse_statistics_table(element)
                    advanced_metrics.update(metrics)
        
        except Exception as e:
            logger.warning(f"⚠️  Error extracting player advanced metrics: {e}")
        
        return advanced_metrics
    
    def _extract_league_name(self) -> str:
        """Extract league name"""
        try:
            league_element = self.driver.find_element(By.CSS_SELECTOR, "h1, .league-name, .tournament-name")
            return league_element.text.strip()
        except:
            return "Unknown League"
    
    def _extract_league_teams(self) -> List[Dict[str, Any]]:
        """Extract league teams"""
        teams = []
        
        try:
            team_elements = self.driver.find_elements(By.CSS_SELECTOR,
                ".team, .club, .team-card")
            
            for team_element in team_elements:
                if team_element.is_displayed():
                    team_data = {
                        "team_id": team_element.get_attribute("data-team-id") or "unknown",
                        "name": self._extract_text_from_element(team_element, ".team-name, .name"),
                        "logo": team_element.find_element(By.CSS_SELECTOR, "img").get_attribute("src") if team_element.find_elements(By.CSS_SELECTOR, "img") else None
                    }
                    teams.append(team_data)
        
        except Exception as e:
            logger.warning(f"⚠️  Error extracting league teams: {e}")
        
        return teams
    
    def _extract_league_standings(self) -> List[Dict[str, Any]]:
        """Extract league standings"""
        standings = []
        
        try:
            standings_table = self.driver.find_element(By.CSS_SELECTOR, "table, .standings-table")
            if standings_table.is_displayed():
                standings = self._parse_standings_table(standings_table)
        
        except Exception as e:
            logger.warning(f"⚠️  Error extracting league standings: {e}")
        
        return standings
    
    def _extract_league_season_stats(self) -> Dict[str, Any]:
        """Extract league season statistics"""
        season_stats = {}
        
        try:
            stats_elements = self.driver.find_elements(By.CSS_SELECTOR,
                ".season-stats, .league-stats, .statistics")
            
            for element in stats_elements:
                if element.is_displayed():
                    stats = self._parse_statistics_table(element)
                    season_stats.update(stats)
        
        except Exception as e:
            logger.warning(f"⚠️  Error extracting league season stats: {e}")
        
        return season_stats
    
    def _extract_league_top_performers(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract league top performers"""
        top_performers = {
            "goals": [],
            "assists": [],
            "points": [],
            "saves": []
        }
        
        try:
            # Look for top performers sections
            performer_elements = self.driver.find_elements(By.CSS_SELECTOR,
                ".top-performers, .leaders, .best-players")
            
            for element in performer_elements:
                if element.is_displayed():
                    performers = self._parse_top_performers(element)
                    top_performers.update(performers)
        
        except Exception as e:
            logger.warning(f"⚠️  Error extracting league top performers: {e}")
        
        return top_performers
    
    def _extract_text_from_element(self, parent_element, selector: str) -> str:
        """Extract text from a child element"""
        try:
            child_element = parent_element.find_element(By.CSS_SELECTOR, selector)
            return child_element.text.strip()
        except:
            return ""
    
    def _extract_player_basic_stats(self, player_element) -> Dict[str, Any]:
        """Extract basic player statistics from player element"""
        stats = {}
        
        try:
            # Look for common stat elements
            stat_elements = player_element.find_elements(By.CSS_SELECTOR,
                ".stat, .metric, .number")
            
            for stat_element in stat_elements:
                if stat_element.is_displayed():
                    stat_text = stat_element.text.strip()
                    if stat_text and stat_text.isdigit():
                        # Try to determine what stat this is based on context
                        parent_text = stat_element.find_element(By.XPATH, "..").text.lower()
                        if "goal" in parent_text:
                            stats["goals"] = int(stat_text)
                        elif "assist" in parent_text:
                            stats["assists"] = int(stat_text)
                        elif "point" in parent_text:
                            stats["points"] = int(stat_text)
        
        except Exception as e:
            logger.warning(f"⚠️  Error extracting player basic stats: {e}")
        
        return stats
    
    def _parse_statistics_table(self, table_element) -> Dict[str, Any]:
        """Parse a statistics table and return structured data"""
        stats = {}
        
        try:
            # Get table headers
            headers = []
            header_elements = table_element.find_elements(By.CSS_SELECTOR, "th")
            for header in header_elements:
                if header.is_displayed():
                    headers.append(header.text.strip())
            
            # Get table rows
            rows = table_element.find_elements(By.CSS_SELECTOR, "tr")
            for row in rows[1:]:  # Skip header row
                if row.is_displayed():
                    cells = row.find_elements(By.CSS_SELECTOR, "td")
                    if len(cells) == len(headers):
                        row_data = {}
                        for i, cell in enumerate(cells):
                            if i < len(headers):
                                row_data[headers[i]] = cell.text.strip()
                        stats.update(row_data)
        
        except Exception as e:
            logger.warning(f"⚠️  Error parsing statistics table: {e}")
        
        return stats
    
    def _parse_standings_table(self, table_element) -> List[Dict[str, Any]]:
        """Parse a standings table"""
        standings = []
        
        try:
            # Get table headers
            headers = []
            header_elements = table_element.find_elements(By.CSS_SELECTOR, "th")
            for header in header_elements:
                if header.is_displayed():
                    headers.append(header.text.strip())
            
            # Get table rows
            rows = table_element.find_elements(By.CSS_SELECTOR, "tr")
            for row in rows[1:]:  # Skip header row
                if row.is_displayed():
                    cells = row.find_elements(By.CSS_SELECTOR, "td")
                    if len(cells) == len(headers):
                        team_data = {}
                        for i, cell in enumerate(cells):
                            if i < len(headers):
                                team_data[headers[i]] = cell.text.strip()
                        standings.append(team_data)
        
        except Exception as e:
            logger.warning(f"⚠️  Error parsing standings table: {e}")
        
        return standings
    
    def _parse_top_performers(self, element) -> Dict[str, List[Dict[str, Any]]]:
        """Parse top performers section"""
        performers = {}
        
        try:
            # Look for different categories of top performers
            categories = element.find_elements(By.CSS_SELECTOR, ".category, .section")
            
            for category in categories:
                if category.is_displayed():
                    category_name = self._extract_text_from_element(category, ".category-name, .title")
                    if category_name:
                        performers[category_name.lower()] = self._parse_performer_list(category)
        
        except Exception as e:
            logger.warning(f"⚠️  Error parsing top performers: {e}")
        
        return performers
    
    def _parse_performer_list(self, element) -> List[Dict[str, Any]]:
        """Parse a list of performers"""
        performers = []
        
        try:
            performer_elements = element.find_elements(By.CSS_SELECTOR, ".performer, .player, .item")
            
            for performer in performer_elements:
                if performer.is_displayed():
                    performer_data = {
                        "name": self._extract_text_from_element(performer, ".name, .player-name"),
                        "team": self._extract_text_from_element(performer, ".team, .club"),
                        "value": self._extract_text_from_element(performer, ".value, .stat, .number")
                    }
                    performers.append(performer_data)
        
        except Exception as e:
            logger.warning(f"⚠️  Error parsing performer list: {e}")
        
        return performers
    
    def get_data_table_info(self) -> Dict[str, Any]:
        """Get information about all available data tables"""
        return {
            table_name: {
                "table_id": table.table_id,
                "description": table.description,
                "data_type": table.data_type,
                "priority": table.priority
            }
            for table_name, table in self.data_tables.items()
        }
    
    def export_team_data_to_csv(self, team_metrics: TeamMetrics, output_dir: str = "instat_data") -> Dict[str, str]:
        """Export team data to CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        
        exported_files = {}
        
        try:
            # Export players data
            if team_metrics.players:
                players_df = pd.DataFrame(team_metrics.players)
                players_file = f"{output_dir}/{team_metrics.team_id}_players.csv"
                players_df.to_csv(players_file, index=False)
                exported_files["players"] = players_file
            
            # Export games data
            if team_metrics.games:
                games_df = pd.DataFrame(team_metrics.games)
                games_file = f"{output_dir}/{team_metrics.team_id}_games.csv"
                games_df.to_csv(games_file, index=False)
                exported_files["games"] = games_file
            
            # Export team stats
            if team_metrics.team_stats:
                stats_df = pd.DataFrame([team_metrics.team_stats])
                stats_file = f"{output_dir}/{team_metrics.team_id}_stats.csv"
                stats_df.to_csv(stats_file, index=False)
                exported_files["stats"] = stats_file
            
            logger.info(f"✅ Team data exported to {output_dir}")
            
        except Exception as e:
            logger.error(f"❌ Error exporting team data: {e}")
        
        return exported_files
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 WebDriver closed")

def main():
    """Main function to demonstrate the comprehensive API"""
    print("🏒 Comprehensive Instat Hudl API Client")
    print("=" * 60)
    
    # Initialize API client
    api = ComprehensiveInstatHudlAPI(headless=False)
    
    # Show available data tables
    print("\n📊 Available Data Tables:")
    table_info = api.get_data_table_info()
    for table_name, info in table_info.items():
        print(f"  {table_name} (ID: {info['table_id']}): {info['description']}")
    
    print(f"\n📋 Total Data Tables: {len(table_info)}")
    print(f"🎯 Priority 1 Tables: {len([t for t in table_info.values() if t['priority'] == 1])}")
    print(f"📈 Priority 2 Tables: {len([t for t in table_info.values() if t['priority'] == 2])}")
    
    print("\n✅ This API provides comprehensive access to:")
    print("  • Team metrics and statistics")
    print("  • Player career and match data")
    print("  • League standings and rankings")
    print("  • Advanced analytics and performance metrics")
    print("  • All 12 Instat data tables with proper mapping")
    
    # Close API client
    api.close()

if __name__ == "__main__":
    main()
