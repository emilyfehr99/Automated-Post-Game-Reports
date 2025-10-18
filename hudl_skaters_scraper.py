#!/usr/bin/env python3
"""
Hudl Instat SKATERS Tab Scraper
Scrapes comprehensive player data from the SKATERS tab
"""

import json
import time
import logging
import csv
import io
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
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

@dataclass
class PlayerData:
    """Represents comprehensive player data from SKATERS tab"""
    player_id: str
    name: str
    position: str
    team_id: str
    last_updated: str
    main_stats: Dict[str, Any]
    shooting: Dict[str, Any]
    faceoffs: Dict[str, Any]
    physical_play: Dict[str, Any]
    puck_battles: Dict[str, Any]
    recoveries_losses: Dict[str, Any]
    special_teams: Dict[str, Any]
    expected_goals: Dict[str, Any]
    passes: Dict[str, Any]
    entries_breakouts: Dict[str, Any]
    advanced_stats: Dict[str, Any]
    playtime_phases: Dict[str, Any]
    scoring_chances: Dict[str, Any]
    passport: Dict[str, Any]

class HudlSkatersScraper:
    """Scraper for comprehensive player data from SKATERS tab"""
    
    def __init__(self, headless: bool = True):
        """Initialize the scraper"""
        self.driver = None
        self.headless = headless
        self.is_authenticated = False
        
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
            chrome_options.add_argument("--disable-images")
            # chrome_options.add_argument("--disable-javascript")  # Commented out - we need JS for Hudl
            
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
    
    def scrape_team_skaters(self, team_id: str) -> List[PlayerData]:
        """Scrape comprehensive skater data for a team"""
        logger.info(f"🏒 Scraping skaters for team {team_id}")
        
        if not self.is_authenticated:
            logger.error("❌ Must authenticate before scraping")
            return []
        
        team_url = f"https://app.hudl.com/instat/hockey/teams/{team_id}/skaters"
        
        try:
            # Navigate to team skaters page
            self.driver.get(team_url)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(5)  # Wait for dynamic content
            
            # Look for download/export button
            download_button = self._find_download_button()
            if download_button:
                logger.info("📥 Found download button, attempting to download CSV")
                csv_data = self._download_skaters_csv(download_button)
                if csv_data:
                    return self._parse_skaters_csv(csv_data, team_id)
            
            # If no download button, try to scrape table data directly
            logger.info("🔍 No download button found, scraping table data directly")
            return self._scrape_table_data(team_id)
            
        except Exception as e:
            logger.error(f"❌ Error scraping team skaters: {e}")
            return []
    
    def _find_download_button(self) -> Optional[Any]:
        """Find the download/export button for skaters data"""
        try:
            # Look for various download button patterns
            download_selectors = [
                "button[title*='download']",
                "button[title*='export']",
                ".download",
                ".export",
                "[data-testid*='download']",
                "[data-testid*='export']",
                "a[href*='.csv']",
                "button:contains('Download')",
                "button:contains('Export')",
                "a:contains('CSV')"
            ]
            
            for selector in download_selectors:
                try:
                    if ":contains(" in selector:
                        # Use XPath for text-based selectors
                        xpath = f"//button[contains(text(), 'Download')] | //button[contains(text(), 'Export')] | //a[contains(text(), 'CSV')]"
                        elements = self.driver.find_elements(By.XPATH, xpath)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            logger.info(f"✅ Found download button: {element.text} ({selector})")
                            return element
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            logger.warning("⚠️  No download button found")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding download button: {e}")
            return None
    
    def _download_skaters_csv(self, download_button) -> Optional[str]:
        """Download the skaters CSV data"""
        try:
            # Click the download button
            ActionChains(self.driver).move_to_element(download_button).click().perform()
            time.sleep(3)  # Wait for download to start
            
            # Check if we can get the CSV data directly
            # This is a simplified approach - in practice, you'd need to handle file downloads
            logger.info("📥 Download initiated - CSV data would be processed here")
            return None  # Placeholder for actual CSV processing
            
        except Exception as e:
            logger.error(f"❌ Error downloading CSV: {e}")
            return None
    
    def _parse_skaters_csv(self, csv_data: str, team_id: str) -> List[PlayerData]:
        """Parse CSV data into PlayerData objects"""
        players = []
        
        try:
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            
            for row in csv_reader:
                player = self._create_player_from_csv_row(row, team_id)
                if player:
                    players.append(player)
            
            logger.info(f"✅ Parsed {len(players)} players from CSV")
            return players
            
        except Exception as e:
            logger.error(f"❌ Error parsing CSV: {e}")
            return []
    
    def _create_player_from_csv_row(self, row: Dict[str, str], team_id: str) -> Optional[PlayerData]:
        """Create PlayerData object from CSV row"""
        try:
            # Extract basic info
            player_id = row.get('player_id', '')
            name = row.get('name', '')
            position = row.get('position', '')
            
            if not name:
                return None
            
            # Create comprehensive player data structure
            player = PlayerData(
                player_id=player_id,
                name=name,
                position=position,
                team_id=team_id,
                last_updated=datetime.now().isoformat(),
                main_stats=self._extract_main_stats(row),
                shooting=self._extract_shooting_stats(row),
                faceoffs=self._extract_faceoff_stats(row),
                physical_play=self._extract_physical_play_stats(row),
                puck_battles=self._extract_puck_battle_stats(row),
                recoveries_losses=self._extract_recovery_stats(row),
                special_teams=self._extract_special_teams_stats(row),
                expected_goals=self._extract_expected_goals_stats(row),
                passes=self._extract_passing_stats(row),
                entries_breakouts=self._extract_zone_play_stats(row),
                advanced_stats=self._extract_advanced_stats(row),
                playtime_phases=self._extract_playtime_stats(row),
                scoring_chances=self._extract_scoring_chances_stats(row),
                passport=self._extract_passport_stats(row)
            )
            
            return player
            
        except Exception as e:
            logger.error(f"❌ Error creating player from CSV row: {e}")
            return None
    
    def _extract_main_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract main statistics from CSV row"""
        return {
            "time_on_ice": row.get('time_on_ice', '0:00'),
            "games_played": int(row.get('games_played', 0)),
            "all_shifts": int(row.get('all_shifts', 0)),
            "goals": int(row.get('goals', 0)),
            "first_assist": int(row.get('first_assist', 0)),
            "second_assist": int(row.get('second_assist', 0)),
            "assists": int(row.get('assists', 0)),
            "puck_touches": int(row.get('puck_touches', 0)),
            "points": int(row.get('points', 0)),
            "plus_minus": int(row.get('plus_minus', 0)),
            "plus": int(row.get('plus', 0)),
            "minus": int(row.get('minus', 0)),
            "scoring_chances": int(row.get('scoring_chances', 0)),
            "team_goals_when_on_ice": int(row.get('team_goals_when_on_ice', 0)),
            "opponent_goals_when_on_ice": int(row.get('opponent_goals_when_on_ice', 0)),
            "penalties": int(row.get('penalties', 0)),
            "penalties_drawn": int(row.get('penalties_drawn', 0)),
            "penalty_time": row.get('penalty_time', '0:00')
        }
    
    def _extract_shooting_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract shooting statistics from CSV row"""
        return {
            "shots": int(row.get('shots', 0)),
            "shots_on_goal": int(row.get('shots_on_goal', 0)),
            "blocked_shots": int(row.get('blocked_shots', 0)),
            "missed_shots": int(row.get('missed_shots', 0)),
            "shots_on_goal_percentage": float(row.get('shots_on_goal_percentage', 0.0)),
            "slapshot": int(row.get('slapshot', 0)),
            "wrist_shot": int(row.get('wrist_shot', 0)),
            "shootouts": int(row.get('shootouts', 0)),
            "shootouts_scored": int(row.get('shootouts_scored', 0)),
            "shootouts_missed": int(row.get('shootouts_missed', 0)),
            "one_on_one_shots": int(row.get('one_on_one_shots', 0)),
            "one_on_one_goals": int(row.get('one_on_one_goals', 0)),
            "power_play_shots": int(row.get('power_play_shots', 0)),
            "short_handed_shots": int(row.get('short_handed_shots', 0)),
            "shots_5v5": int(row.get('shots_5v5', 0)),
            "positional_attack_shots": int(row.get('positional_attack_shots', 0)),
            "counter_attack_shots": int(row.get('counter_attack_shots', 0))
        }
    
    def _extract_faceoff_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract faceoff statistics from CSV row"""
        return {
            "faceoffs": int(row.get('faceoffs', 0)),
            "faceoffs_won": int(row.get('faceoffs_won', 0)),
            "faceoffs_lost": int(row.get('faceoffs_lost', 0)),
            "faceoffs_won_percentage": float(row.get('faceoffs_won_percentage', 0.0)),
            "faceoffs_in_dz": int(row.get('faceoffs_in_dz', 0)),
            "faceoffs_in_nz": int(row.get('faceoffs_in_nz', 0)),
            "faceoffs_in_oz": int(row.get('faceoffs_in_oz', 0))
        }
    
    def _extract_physical_play_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract physical play statistics from CSV row"""
        return {
            "hits": int(row.get('hits', 0)),
            "hits_against": int(row.get('hits_against', 0)),
            "error_leading_to_goal": int(row.get('error_leading_to_goal', 0)),
            "dump_ins": int(row.get('dump_ins', 0)),
            "dump_outs": int(row.get('dump_outs', 0))
        }
    
    def _extract_puck_battle_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract puck battle statistics from CSV row"""
        return {
            "puck_battles": int(row.get('puck_battles', 0)),
            "puck_battles_won": int(row.get('puck_battles_won', 0)),
            "puck_battles_won_percentage": float(row.get('puck_battles_won_percentage', 0.0)),
            "puck_battles_in_dz": int(row.get('puck_battles_in_dz', 0)),
            "puck_battles_in_nz": int(row.get('puck_battles_in_nz', 0)),
            "puck_battles_in_oz": int(row.get('puck_battles_in_oz', 0)),
            "shots_blocking": int(row.get('shots_blocking', 0)),
            "dekes": int(row.get('dekes', 0)),
            "dekes_successful": int(row.get('dekes_successful', 0)),
            "dekes_unsuccessful": int(row.get('dekes_unsuccessful', 0))
        }
    
    def _extract_recovery_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract recovery statistics from CSV row"""
        return {
            "takeaways": int(row.get('takeaways', 0)),
            "takeaways_in_dz": int(row.get('takeaways_in_dz', 0)),
            "takeaways_in_nz": int(row.get('takeaways_in_nz', 0)),
            "takeaways_in_oz": int(row.get('takeaways_in_oz', 0)),
            "puck_losses": int(row.get('puck_losses', 0)),
            "puck_losses_in_dz": int(row.get('puck_losses_in_dz', 0)),
            "puck_losses_in_nz": int(row.get('puck_losses_in_nz', 0)),
            "puck_losses_in_oz": int(row.get('puck_losses_in_oz', 0)),
            "puck_retrievals_after_shots": int(row.get('puck_retrievals_after_shots', 0)),
            "opponent_dump_in_retrievals": int(row.get('opponent_dump_in_retrievals', 0)),
            "loose_puck_recovery": int(row.get('loose_puck_recovery', 0)),
            "ev_dz_retrievals": int(row.get('ev_dz_retrievals', 0)),
            "ev_oz_retrievals": int(row.get('ev_oz_retrievals', 0)),
            "power_play_retrievals": int(row.get('power_play_retrievals', 0)),
            "penalty_kill_retrievals": int(row.get('penalty_kill_retrievals', 0))
        }
    
    def _extract_special_teams_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract special teams statistics from CSV row"""
        return {
            "power_play": int(row.get('power_play', 0)),
            "successful_power_play": int(row.get('successful_power_play', 0)),
            "power_play_time": row.get('power_play_time', '0:00'),
            "short_handed": int(row.get('short_handed', 0)),
            "penalty_killing": int(row.get('penalty_killing', 0)),
            "short_handed_time": row.get('short_handed_time', '0:00')
        }
    
    def _extract_expected_goals_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract expected goals statistics from CSV row"""
        return {
            "xg": float(row.get('xg', 0.0)),
            "xg_per_shot": float(row.get('xg_per_shot', 0.0)),
            "xg_expected_goals": float(row.get('xg_expected_goals', 0.0)),
            "xg_per_goal": float(row.get('xg_per_goal', 0.0)),
            "net_xg": float(row.get('net_xg', 0.0)),
            "team_xg_when_on_ice": float(row.get('team_xg_when_on_ice', 0.0)),
            "opponent_xg_when_on_ice": float(row.get('opponent_xg_when_on_ice', 0.0)),
            "xg_conversion": float(row.get('xg_conversion', 0.0))
        }
    
    def _extract_passing_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract passing statistics from CSV row"""
        return {
            "passes": int(row.get('passes', 0)),
            "accurate_passes": int(row.get('accurate_passes', 0)),
            "accurate_passes_percentage": float(row.get('accurate_passes_percentage', 0.0)),
            "passes_to_slot": int(row.get('passes_to_slot', 0)),
            "pre_shots_passes": int(row.get('pre_shots_passes', 0)),
            "pass_receptions": int(row.get('pass_receptions', 0))
        }
    
    def _extract_zone_play_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract zone play statistics from CSV row"""
        return {
            "entries": int(row.get('entries', 0)),
            "entries_via_pass": int(row.get('entries_via_pass', 0)),
            "entries_via_dump_in": int(row.get('entries_via_dump_in', 0)),
            "entries_via_stickhandling": int(row.get('entries_via_stickhandling', 0)),
            "breakouts": int(row.get('breakouts', 0)),
            "breakouts_via_pass": int(row.get('breakouts_via_pass', 0)),
            "breakouts_via_dump_out": int(row.get('breakouts_via_dump_out', 0)),
            "breakouts_via_stickhandling": int(row.get('breakouts_via_stickhandling', 0))
        }
    
    def _extract_advanced_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract advanced statistics from CSV row"""
        return {
            "corsi": int(row.get('corsi', 0)),
            "corsi_minus": int(row.get('corsi_minus', 0)),
            "corsi_plus": int(row.get('corsi_plus', 0)),
            "corsi_for_percentage": float(row.get('corsi_for_percentage', 0.0)),
            "fenwick_for": int(row.get('fenwick_for', 0)),
            "fenwick_against": int(row.get('fenwick_against', 0)),
            "fenwick_for_percentage": float(row.get('fenwick_for_percentage', 0.0))
        }
    
    def _extract_playtime_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract playtime statistics from CSV row"""
        return {
            "playing_in_attack": row.get('playing_in_attack', '0:00'),
            "playing_in_defense": row.get('playing_in_defense', '0:00'),
            "oz_possession": int(row.get('oz_possession', 0)),
            "nz_possession": int(row.get('nz_possession', 0)),
            "dz_possession": int(row.get('dz_possession', 0))
        }
    
    def _extract_scoring_chances_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract scoring chances statistics from CSV row"""
        return {
            "scoring_chances_total": int(row.get('scoring_chances_total', 0)),
            "scoring_chances_scored": int(row.get('scoring_chances_scored', 0)),
            "scoring_chances_missed": int(row.get('scoring_chances_missed', 0)),
            "scoring_chances_saved": int(row.get('scoring_chances_saved', 0)),
            "scoring_chances_percentage": float(row.get('scoring_chances_percentage', 0.0)),
            "inner_slot_shots_total": int(row.get('inner_slot_shots_total', 0)),
            "inner_slot_shots_scored": int(row.get('inner_slot_shots_scored', 0)),
            "inner_slot_shots_missed": int(row.get('inner_slot_shots_missed', 0)),
            "inner_slot_shots_saved": int(row.get('inner_slot_shots_saved', 0)),
            "outer_slot_shots_total": int(row.get('outer_slot_shots_total', 0)),
            "outer_slot_shots_scored": int(row.get('outer_slot_shots_scored', 0)),
            "outer_slot_shots_missed": int(row.get('outer_slot_shots_missed', 0)),
            "outer_slot_shots_saved": int(row.get('outer_slot_shots_saved', 0)),
            "blocked_shots_from_slot": int(row.get('blocked_shots_from_slot', 0)),
            "blocked_shots_outside_slot": int(row.get('blocked_shots_outside_slot', 0))
        }
    
    def _extract_passport_stats(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Extract passport information from CSV row"""
        return {
            "date_of_birth": row.get('date_of_birth', ''),
            "nationality": row.get('nationality', ''),
            "national_team": row.get('national_team', ''),
            "height": row.get('height', ''),
            "weight": row.get('weight', ''),
            "contract": row.get('contract', ''),
            "active_hand": row.get('active_hand', '')
        }
    
    def _scrape_table_data(self, team_id: str) -> List[PlayerData]:
        """Scrape data directly from the table (fallback method)"""
        # This would be implemented to scrape the actual table data
        # For now, return empty list as placeholder
        logger.info("🔍 Table scraping not implemented yet")
        return []
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 WebDriver closed")

def main():
    """Main function to test the scraper"""
    print("🏒 Hudl Instat SKATERS Tab Scraper")
    print("=" * 60)
    
    # Initialize scraper
    scraper = HudlSkatersScraper(headless=False)
    
    try:
        # Authenticate
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        if not scraper.authenticate(HUDL_USERNAME, HUDL_PASSWORD):
            print("❌ Authentication failed")
            return
        
        # Test with Lloydminster Bobcats
        team_id = "21479"
        players = scraper.scrape_team_skaters(team_id)
        
        if players:
            print(f"✅ Successfully scraped {len(players)} players")
            
            # Show sample player data
            if players:
                player = players[0]
                print(f"\n👤 Sample Player: {player.name} ({player.position})")
                print(f"  Goals: {player.main_stats['goals']}")
                print(f"  Assists: {player.main_stats['assists']}")
                print(f"  Points: {player.main_stats['points']}")
                print(f"  Shots: {player.shooting['shots']}")
                print(f"  Corsi: {player.advanced_stats['corsi']}")
        else:
            print("❌ No players found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
