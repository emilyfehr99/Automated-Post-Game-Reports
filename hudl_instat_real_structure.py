#!/usr/bin/env python3
"""
Hudl Instat Real Structure Mapper
Based on actual Hudl Instat tabs: OVERVIEW, GAMES, SKATERS, GOALIES, LINES, SHOT MAP, FACEOFFS, EPISODES SEARCH
"""

import json
import time
import logging
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
class HudlInstatTab:
    """Represents a Hudl Instat tab"""
    name: str
    description: str
    data_types: List[str]
    export_options: List[str]
    priority: int

class HudlInstatRealStructureMapper:
    """Mapper for actual Hudl Instat tab structure"""
    
    def __init__(self, headless: bool = False, user_identifier: str = None):
        """Initialize the real structure mapper"""
        self.driver = None
        self.headless = headless
        self.user_identifier = user_identifier or "real_structure_mapper"
        self.is_authenticated = False
        
        # Define actual Hudl Instat tabs based on real structure
        self.instat_tabs = self._define_real_tabs()
        
    def _define_real_tabs(self) -> List[HudlInstatTab]:
        """Define the actual Hudl Instat tabs"""
        
        tabs = [
            HudlInstatTab(
                name="OVERVIEW",
                description="Home page showing recent games with download buttons",
                data_types=["recent_games", "game_summaries", "team_overview"],
                export_options=["game_csv_download"],
                priority=1
            ),
            HudlInstatTab(
                name="GAMES",
                description="Complete games list and game details",
                data_types=["games_list", "game_details", "game_stats"],
                export_options=["game_csv_download", "bulk_download"],
                priority=1
            ),
            HudlInstatTab(
                name="SKATERS",
                description="Skater statistics and performance data",
                data_types=["skater_stats", "skater_performance", "skater_analytics"],
                export_options=["skater_csv_download", "skater_export"],
                priority=1
            ),
            HudlInstatTab(
                name="GOALIES",
                description="Goalie statistics and performance data",
                data_types=["goalie_stats", "goalie_performance", "goalie_analytics"],
                export_options=["goalie_csv_download", "goalie_export"],
                priority=1
            ),
            HudlInstatTab(
                name="LINES",
                description="Line combinations and line performance",
                data_types=["line_combinations", "line_performance", "line_analytics"],
                export_options=["lines_csv_download", "lines_export"],
                priority=2
            ),
            HudlInstatTab(
                name="SHOT MAP",
                description="Shot location and shot analysis data",
                data_types=["shot_locations", "shot_analysis", "shot_effectiveness"],
                export_options=["shot_map_export", "shot_data_download"],
                priority=2
            ),
            HudlInstatTab(
                name="FACEOFFS",
                description="Faceoff statistics and analysis",
                data_types=["faceoff_stats", "faceoff_analysis", "faceoff_performance"],
                export_options=["faceoff_csv_download", "faceoff_export"],
                priority=2
            ),
            HudlInstatTab(
                name="EPISODES SEARCH",
                description="Video episodes and search functionality",
                data_types=["video_episodes", "episode_metadata", "search_results"],
                export_options=["episode_export", "video_download"],
                priority=3
            )
        ]
        
        return tabs
    
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
            
            # Add user-specific profile
            profile_dir = f"/tmp/hudl_profile_{self.user_identifier}"
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument(f"--profile-directory=Profile_{self.user_identifier}")
            
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
    
    def map_team_page_real_structure(self, team_id: str) -> Dict[str, Any]:
        """Map the actual Hudl Instat team page structure"""
        logger.info(f"🗺️ Mapping real Hudl Instat structure for team {team_id}")
        
        if not self.is_authenticated:
            logger.error("❌ Must authenticate before mapping structure")
            return {"error": "Authentication required"}
        
        team_url = f"https://app.hudl.com/instat/hockey/teams/{team_id}"
        
        try:
            # Navigate to team page
            self.driver.get(team_url)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)  # Wait for dynamic content
            
            mapping = {
                "team_id": team_id,
                "url": team_url,
                "mapping_timestamp": datetime.now().isoformat(),
                "page_title": self.driver.title,
                "current_url": self.driver.current_url,
                "tabs_analysis": {},
                "overview_games": [],
                "export_buttons_found": [],
                "data_sections": {}
            }
            
            # Analyze each tab
            for tab in self.instat_tabs:
                logger.info(f"🔍 Analyzing tab: {tab.name}")
                tab_analysis = self._analyze_tab(tab)
                mapping["tabs_analysis"][tab.name] = tab_analysis
            
            # Special analysis for OVERVIEW page (home page with games)
            mapping["overview_games"] = self._analyze_overview_games()
            
            # Find all export/download buttons
            mapping["export_buttons_found"] = self._find_all_export_buttons()
            
            # Analyze data sections
            mapping["data_sections"] = self._analyze_data_sections()
            
            logger.info("✅ Real structure mapping completed")
            return mapping
            
        except Exception as e:
            logger.error(f"❌ Error mapping real structure: {e}")
            return {"error": str(e), "team_id": team_id}
    
    def _analyze_tab(self, tab: HudlInstatTab) -> Dict[str, Any]:
        """Analyze a specific tab"""
        try:
            # Look for the tab element
            tab_elements = self.driver.find_elements(By.XPATH, 
                f"//*[contains(text(), '{tab.name}') and (self::a or self::button or self::*[@role='tab'])]")
            
            tab_analysis = {
                "tab_name": tab.name,
                "description": tab.description,
                "found": len(tab_elements) > 0,
                "clickable": False,
                "active": False,
                "data_sections": [],
                "export_buttons": [],
                "priority": tab.priority
            }
            
            if tab_elements:
                for tab_element in tab_elements:
                    if tab_element.is_displayed():
                        tab_analysis["clickable"] = tab_element.is_enabled()
                        tab_analysis["active"] = "active" in tab_element.get_attribute("class")
                        
                        # Try to click the tab to analyze its content
                        try:
                            ActionChains(self.driver).move_to_element(tab_element).click().perform()
                            time.sleep(2)  # Wait for content to load
                            
                            # Analyze content after clicking
                            tab_analysis["data_sections"] = self._analyze_tab_content(tab)
                            tab_analysis["export_buttons"] = self._find_tab_export_buttons()
                            
                        except Exception as e:
                            logger.warning(f"⚠️  Could not click tab {tab.name}: {e}")
            
            return tab_analysis
            
        except Exception as e:
            logger.warning(f"⚠️  Error analyzing tab {tab.name}: {e}")
            return {"tab_name": tab.name, "error": str(e)}
    
    def _analyze_tab_content(self, tab: HudlInstatTab) -> List[Dict[str, Any]]:
        """Analyze content within a tab"""
        content_sections = []
        
        try:
            # Look for data tables
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
            for table in tables:
                if table.is_displayed():
                    content_sections.append({
                        "type": "table",
                        "rows": len(table.find_elements(By.CSS_SELECTOR, "tr")),
                        "columns": len(table.find_elements(By.CSS_SELECTOR, "th")),
                        "class": table.get_attribute("class")
                    })
            
            # Look for data lists
            lists = self.driver.find_elements(By.CSS_SELECTOR, ".list, .data-list, ul, ol")
            for list_elem in lists:
                if list_elem.is_displayed():
                    items = list_elem.find_elements(By.CSS_SELECTOR, "li, .item, .list-item")
                    content_sections.append({
                        "type": "list",
                        "items": len(items),
                        "class": list_elem.get_attribute("class")
                    })
            
            # Look for charts/graphs
            charts = self.driver.find_elements(By.CSS_SELECTOR, ".chart, .graph, canvas, svg")
            for chart in charts:
                if chart.is_displayed():
                    content_sections.append({
                        "type": "chart",
                        "class": chart.get_attribute("class"),
                        "tag": chart.tag_name
                    })
            
        except Exception as e:
            logger.warning(f"⚠️  Error analyzing tab content for {tab.name}: {e}")
        
        return content_sections
    
    def _analyze_overview_games(self) -> List[Dict[str, Any]]:
        """Analyze games shown on the OVERVIEW page"""
        games = []
        
        try:
            # Look for game elements on the overview page
            game_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".game, .match, .game-item, .game-card, [data-game-id]")
            
            for game_element in game_elements:
                if game_element.is_displayed():
                    game_data = {
                        "element_class": game_element.get_attribute("class"),
                        "game_id": game_element.get_attribute("data-game-id"),
                        "text_content": game_element.text.strip()[:200],  # First 200 chars
                        "has_download_button": bool(game_element.find_elements(By.CSS_SELECTOR, 
                            "button[title*='download'], .download, .export, [data-testid*='download']")),
                        "download_buttons": []
                    }
                    
                    # Find download buttons within this game element
                    download_buttons = game_element.find_elements(By.CSS_SELECTOR, 
                        "button, a, .download, .export")
                    
                    for button in download_buttons:
                        if "download" in button.text.lower() or "export" in button.text.lower():
                            game_data["download_buttons"].append({
                                "text": button.text.strip(),
                                "class": button.get_attribute("class"),
                                "title": button.get_attribute("title"),
                                "clickable": button.is_enabled()
                            })
                    
                    games.append(game_data)
            
        except Exception as e:
            logger.warning(f"⚠️  Error analyzing overview games: {e}")
        
        return games
    
    def _find_all_export_buttons(self) -> List[Dict[str, Any]]:
        """Find all export/download buttons on the page"""
        export_buttons = []
        
        try:
            # Look for various export button patterns
            button_selectors = [
                "button[title*='download']",
                "button[title*='export']", 
                ".download",
                ".export",
                "[data-testid*='download']",
                "[data-testid*='export']",
                "a[href*='.csv']",
                "a[href*='.xlsx']",
                "a[href*='.pdf']"
            ]
            
            for selector in button_selectors:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    if button.is_displayed():
                        export_buttons.append({
                            "text": button.text.strip(),
                            "tag": button.tag_name,
                            "class": button.get_attribute("class"),
                            "title": button.get_attribute("title"),
                            "href": button.get_attribute("href"),
                            "data_testid": button.get_attribute("data-testid"),
                            "clickable": button.is_enabled(),
                            "selector_used": selector
                        })
            
        except Exception as e:
            logger.warning(f"⚠️  Error finding export buttons: {e}")
        
        return export_buttons
    
    def _find_tab_export_buttons(self) -> List[Dict[str, Any]]:
        """Find export buttons within the current tab"""
        return self._find_all_export_buttons()  # For now, use the same method
    
    def _analyze_data_sections(self) -> Dict[str, Any]:
        """Analyze data sections across all tabs"""
        sections = {
            "tables": [],
            "lists": [],
            "charts": [],
            "forms": [],
            "export_areas": []
        }
        
        try:
            # Tables
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
            for table in tables:
                if table.is_displayed():
                    sections["tables"].append({
                        "class": table.get_attribute("class"),
                        "rows": len(table.find_elements(By.CSS_SELECTOR, "tr")),
                        "columns": len(table.find_elements(By.CSS_SELECTOR, "th")),
                        "has_export": bool(table.find_elements(By.CSS_SELECTOR, ".export, .download"))
                    })
            
            # Lists
            lists = self.driver.find_elements(By.CSS_SELECTOR, "ul, ol, .list")
            for list_elem in lists:
                if list_elem.is_displayed():
                    sections["lists"].append({
                        "class": list_elem.get_attribute("class"),
                        "items": len(list_elem.find_elements(By.CSS_SELECTOR, "li")),
                        "has_export": bool(list_elem.find_elements(By.CSS_SELECTOR, ".export, .download"))
                    })
            
            # Charts
            charts = self.driver.find_elements(By.CSS_SELECTOR, "canvas, svg, .chart, .graph")
            for chart in charts:
                if chart.is_displayed():
                    sections["charts"].append({
                        "class": chart.get_attribute("class"),
                        "tag": chart.tag_name,
                        "has_export": bool(chart.find_elements(By.CSS_SELECTOR, ".export, .download"))
                    })
            
        except Exception as e:
            logger.warning(f"⚠️  Error analyzing data sections: {e}")
        
        return sections
    
    def get_tab_summary(self) -> Dict[str, Any]:
        """Get a summary of all tabs"""
        summary = {
            "total_tabs": len(self.instat_tabs),
            "tabs": []
        }
        
        for tab in self.instat_tabs:
            summary["tabs"].append({
                "name": tab.name,
                "description": tab.description,
                "data_types": tab.data_types,
                "export_options": tab.export_options,
                "priority": tab.priority
            })
        
        return summary
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 WebDriver closed")

def main():
    """Main function to demonstrate the real structure mapper"""
    print("🏒 Hudl Instat Real Structure Mapper")
    print("=" * 60)
    
    # Initialize mapper
    mapper = HudlInstatRealStructureMapper(headless=False)
    
    # Show tab summary
    summary = mapper.get_tab_summary()
    print(f"\n📋 Hudl Instat Tabs:")
    for tab in summary["tabs"]:
        print(f"  {tab['name']} (P{tab['priority']}): {tab['description']}")
        print(f"    Data types: {', '.join(tab['data_types'])}")
        print(f"    Export options: {', '.join(tab['export_options'])}")
        print()
    
    try:
        # Authenticate
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        if not mapper.authenticate(HUDL_USERNAME, HUDL_PASSWORD):
            print("❌ Authentication failed")
            return
        
        # Map team page structure
        team_id = "21479"  # Bobcats team ID
        mapping = mapper.map_team_page_real_structure(team_id)
        
        # Save mapping results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hudl_real_structure_mapping_{team_id}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(mapping, f, indent=2)
        
        print(f"📄 Real structure mapping saved to: {filename}")
        
        # Print summary
        print(f"\n📊 Mapping Summary:")
        print(f"  Tabs analyzed: {len(mapping.get('tabs_analysis', {}))}")
        print(f"  Overview games found: {len(mapping.get('overview_games', []))}")
        print(f"  Export buttons found: {len(mapping.get('export_buttons_found', []))}")
        
        # Show tab analysis
        for tab_name, tab_data in mapping.get('tabs_analysis', {}).items():
            if tab_data.get('found'):
                print(f"  ✅ {tab_name}: {len(tab_data.get('data_sections', []))} sections, {len(tab_data.get('export_buttons', []))} export buttons")
            else:
                print(f"  ❌ {tab_name}: Not found")
        
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        mapper.close()

if __name__ == "__main__":
    main()
