#!/usr/bin/env python3
"""
Hudl Instat Tab and Data Section Mapper
Comprehensive mapping of all tabs, sections, and data export options in Hudl Instat
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from hudl_page_structure_analyzer import HudlPageStructureAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HudlInstatTabMapper:
    """Comprehensive mapper for Hudl Instat tabs and data sections"""
    
    def __init__(self, headless: bool = False, user_identifier: str = None):
        """Initialize the tab mapper"""
        self.analyzer = HudlPageStructureAnalyzer(headless, user_identifier)
        self.driver = None
        self.is_authenticated = False
        
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with Hudl Instat"""
        return self.analyzer.authenticate(username, password)
    
    def map_team_page_tabs(self, team_id: str) -> Dict[str, Any]:
        """Map all tabs and data sections for a team page"""
        logger.info(f"🗺️ Mapping tabs and data sections for team {team_id}")
        
        if not self.analyzer.is_authenticated:
            logger.error("❌ Must authenticate before mapping tabs")
            return {"error": "Authentication required"}
        
        # Get the driver from analyzer
        self.driver = self.analyzer.driver
        
        try:
            # Navigate to team page
            team_url = f"{self.analyzer.base_url}/{team_id}"
            self.driver.get(team_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)  # Additional wait for dynamic content
            
            mapping = {
                "team_id": team_id,
                "url": team_url,
                "mapping_timestamp": datetime.now().isoformat(),
                "main_navigation": self._map_main_navigation(),
                "team_tabs": self._map_team_tabs(),
                "data_sections": self._map_data_sections(),
                "export_options": self._map_export_options(),
                "player_data_tabs": self._map_player_data_tabs(),
                "game_data_tabs": self._map_game_data_tabs(),
                "analytics_tabs": self._map_analytics_tabs(),
                "reports_tabs": self._map_reports_tabs(),
                "video_tabs": self._map_video_tabs(),
                "scouting_tabs": self._map_scouting_tabs()
            }
            
            logger.info("✅ Tab mapping completed successfully")
            return mapping
            
        except Exception as e:
            logger.error(f"❌ Error mapping tabs: {e}")
            return {"error": str(e), "team_id": team_id}
    
    def _map_main_navigation(self) -> Dict[str, Any]:
        """Map the main navigation structure"""
        logger.info("🧭 Mapping main navigation...")
        
        navigation = {
            "primary_nav": [],
            "secondary_nav": [],
            "breadcrumbs": [],
            "user_menu": []
        }
        
        try:
            # Primary navigation (usually top level)
            primary_nav = self.driver.find_elements(By.CSS_SELECTOR, 
                ".main-nav, .primary-nav, .top-nav, nav[role='navigation']")
            
            for nav in primary_nav:
                links = nav.find_elements(By.CSS_SELECTOR, "a, button")
                for link in links:
                    if link.text.strip() and link.is_displayed():
                        navigation["primary_nav"].append({
                            "text": link.text.strip(),
                            "href": link.get_attribute("href"),
                            "class": link.get_attribute("class"),
                            "active": "active" in link.get_attribute("class")
                        })
            
            # Secondary navigation (usually sidebar or sub-menu)
            secondary_nav = self.driver.find_elements(By.CSS_SELECTOR, 
                ".sidebar, .side-nav, .secondary-nav, .sub-nav")
            
            for nav in secondary_nav:
                links = nav.find_elements(By.CSS_SELECTOR, "a, button")
                for link in links:
                    if link.text.strip() and link.is_displayed():
                        navigation["secondary_nav"].append({
                            "text": link.text.strip(),
                            "href": link.get_attribute("href"),
                            "class": link.get_attribute("class"),
                            "level": self._get_nav_level(link)
                        })
            
            # Breadcrumbs
            breadcrumbs = self.driver.find_elements(By.CSS_SELECTOR, 
                ".breadcrumb, .breadcrumbs, [aria-label*='breadcrumb']")
            
            for breadcrumb in breadcrumbs:
                items = breadcrumb.find_elements(By.CSS_SELECTOR, "a, span")
                for item in items:
                    if item.text.strip():
                        navigation["breadcrumbs"].append({
                            "text": item.text.strip(),
                            "href": item.get_attribute("href"),
                            "current": "current" in item.get_attribute("class")
                        })
            
        except Exception as e:
            logger.warning(f"⚠️  Error mapping main navigation: {e}")
        
        return navigation
    
    def _map_team_tabs(self) -> Dict[str, Any]:
        """Map team-specific tabs"""
        logger.info("🏒 Mapping team tabs...")
        
        team_tabs = {
            "overview": [],
            "roster": [],
            "games": [],
            "statistics": [],
            "analytics": [],
            "reports": [],
            "video": [],
            "scouting": []
        }
        
        try:
            # Look for tab containers
            tab_containers = self.driver.find_elements(By.CSS_SELECTOR, 
                ".tabs, .tab-list, .nav-tabs, [role='tablist']")
            
            for container in tab_containers:
                tabs = container.find_elements(By.CSS_SELECTOR, 
                    "a, button, .tab, .tab-item, [role='tab']")
                
                for tab in tabs:
                    if tab.text.strip() and tab.is_displayed():
                        tab_text = tab.text.strip().lower()
                        tab_data = {
                            "text": tab.text.strip(),
                            "href": tab.get_attribute("href"),
                            "class": tab.get_attribute("class"),
                            "active": "active" in tab.get_attribute("class"),
                            "clickable": tab.is_enabled()
                        }
                        
                        # Categorize tabs
                        if any(keyword in tab_text for keyword in ["overview", "summary", "home"]):
                            team_tabs["overview"].append(tab_data)
                        elif any(keyword in tab_text for keyword in ["roster", "players", "squad"]):
                            team_tabs["roster"].append(tab_data)
                        elif any(keyword in tab_text for keyword in ["games", "matches", "schedule"]):
                            team_tabs["games"].append(tab_data)
                        elif any(keyword in tab_text for keyword in ["stats", "statistics", "numbers"]):
                            team_tabs["statistics"].append(tab_data)
                        elif any(keyword in tab_text for keyword in ["analytics", "analysis", "metrics"]):
                            team_tabs["analytics"].append(tab_data)
                        elif any(keyword in tab_text for keyword in ["reports", "reporting"]):
                            team_tabs["reports"].append(tab_data)
                        elif any(keyword in tab_text for keyword in ["video", "videos", "film"]):
                            team_tabs["video"].append(tab_data)
                        elif any(keyword in tab_text for keyword in ["scout", "scouting"]):
                            team_tabs["scouting"].append(tab_data)
            
        except Exception as e:
            logger.warning(f"⚠️  Error mapping team tabs: {e}")
        
        return team_tabs
    
    def _map_data_sections(self) -> Dict[str, Any]:
        """Map data sections and content areas"""
        logger.info("📊 Mapping data sections...")
        
        sections = {
            "team_info": [],
            "player_lists": [],
            "game_lists": [],
            "statistics_tables": [],
            "charts_graphs": [],
            "data_export_areas": []
        }
        
        try:
            # Team information sections
            team_info_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".team-info, .team-details, .team-header, .team-summary")
            
            for element in team_info_elements:
                if element.is_displayed():
                    sections["team_info"].append({
                        "class": element.get_attribute("class"),
                        "text_content": element.text.strip()[:200],  # First 200 chars
                        "has_export": bool(element.find_elements(By.CSS_SELECTOR, ".export, .download"))
                    })
            
            # Player lists
            player_lists = self.driver.find_elements(By.CSS_SELECTOR, 
                ".player-list, .roster, .squad, table[data-type='players']")
            
            for player_list in player_lists:
                if player_list.is_displayed():
                    sections["player_lists"].append({
                        "class": player_list.get_attribute("class"),
                        "player_count": len(player_list.find_elements(By.CSS_SELECTOR, ".player, tr")),
                        "has_export": bool(player_list.find_elements(By.CSS_SELECTOR, ".export, .download"))
                    })
            
            # Game lists
            game_lists = self.driver.find_elements(By.CSS_SELECTOR, 
                ".game-list, .matches, .schedule, table[data-type='games']")
            
            for game_list in game_lists:
                if game_list.is_displayed():
                    sections["game_lists"].append({
                        "class": game_list.get_attribute("class"),
                        "game_count": len(game_list.find_elements(By.CSS_SELECTOR, ".game, tr")),
                        "has_export": bool(game_list.find_elements(By.CSS_SELECTOR, ".export, .download"))
                    })
            
            # Statistics tables
            stats_tables = self.driver.find_elements(By.CSS_SELECTOR, 
                "table, .stats-table, .statistics, .data-table")
            
            for table in stats_tables:
                if table.is_displayed():
                    sections["statistics_tables"].append({
                        "class": table.get_attribute("class"),
                        "rows": len(table.find_elements(By.CSS_SELECTOR, "tr")),
                        "columns": len(table.find_elements(By.CSS_SELECTOR, "th")),
                        "has_export": bool(table.find_elements(By.CSS_SELECTOR, ".export, .download"))
                    })
            
        except Exception as e:
            logger.warning(f"⚠️  Error mapping data sections: {e}")
        
        return sections
    
    def _map_export_options(self) -> Dict[str, Any]:
        """Map all export and download options"""
        logger.info("💾 Mapping export options...")
        
        export_options = {
            "csv_exports": [],
            "excel_exports": [],
            "pdf_exports": [],
            "bulk_exports": [],
            "data_selection_forms": [],
            "export_buttons": []
        }
        
        try:
            # Look for all export-related elements
            export_elements = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Export') or contains(text(), 'Download') or contains(text(), 'CSV') or contains(text(), 'Excel') or contains(text(), 'PDF') or contains(@class, 'export') or contains(@class, 'download')]")
            
            for element in export_elements:
                if element.is_displayed() and element.tag_name in ["button", "a", "input"]:
                    export_data = {
                        "text": element.text.strip(),
                        "tag": element.tag_name,
                        "class": element.get_attribute("class"),
                        "href": element.get_attribute("href"),
                        "title": element.get_attribute("title"),
                        "data_testid": element.get_attribute("data-testid")
                    }
                    
                    # Categorize by type
                    text_lower = element.text.strip().lower()
                    if "csv" in text_lower:
                        export_options["csv_exports"].append(export_data)
                    elif "excel" in text_lower or "xlsx" in text_lower:
                        export_options["excel_exports"].append(export_data)
                    elif "pdf" in text_lower:
                        export_options["pdf_exports"].append(export_data)
                    elif "bulk" in text_lower or "all" in text_lower:
                        export_options["bulk_exports"].append(export_data)
                    else:
                        export_options["export_buttons"].append(export_data)
            
            # Look for data selection forms
            forms = self.driver.find_elements(By.CSS_SELECTOR, 
                "form, .form, .data-selection, .export-form, .filter-form")
            
            for form in forms:
                if form.is_displayed():
                    form_data = {
                        "class": form.get_attribute("class"),
                        "id": form.get_attribute("id"),
                        "action": form.get_attribute("action"),
                        "inputs": [],
                        "selects": [],
                        "checkboxes": []
                    }
                    
                    # Analyze form elements
                    inputs = form.find_elements(By.CSS_SELECTOR, "input, select, textarea")
                    for input_elem in inputs:
                        input_type = input_elem.get_attribute("type") or input_elem.tag_name
                        input_data = {
                            "type": input_type,
                            "name": input_elem.get_attribute("name"),
                            "id": input_elem.get_attribute("id"),
                            "placeholder": input_elem.get_attribute("placeholder"),
                            "value": input_elem.get_attribute("value")
                        }
                        
                        if input_type == "checkbox":
                            form_data["checkboxes"].append(input_data)
                        elif input_type == "select":
                            form_data["selects"].append(input_data)
                        else:
                            form_data["inputs"].append(input_data)
                    
                    if form_data["inputs"] or form_data["selects"] or form_data["checkboxes"]:
                        export_options["data_selection_forms"].append(form_data)
            
        except Exception as e:
            logger.warning(f"⚠️  Error mapping export options: {e}")
        
        return export_options
    
    def _map_player_data_tabs(self) -> Dict[str, Any]:
        """Map player-specific data tabs and sections"""
        logger.info("👥 Mapping player data tabs...")
        
        player_tabs = {
            "roster_overview": [],
            "player_stats": [],
            "individual_performance": [],
            "player_analytics": [],
            "position_analysis": []
        }
        
        try:
            # Look for player-related sections
            player_sections = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Player') or contains(text(), 'Roster') or contains(text(), 'Individual') or contains(@class, 'player')]")
            
            for section in player_sections:
                if section.is_displayed():
                    section_text = section.text.strip().lower()
                    section_data = {
                        "text": section.text.strip(),
                        "class": section.get_attribute("class"),
                        "has_export": bool(section.find_elements(By.CSS_SELECTOR, ".export, .download"))
                    }
                    
                    if "roster" in section_text:
                        player_tabs["roster_overview"].append(section_data)
                    elif "stat" in section_text:
                        player_tabs["player_stats"].append(section_data)
                    elif "individual" in section_text:
                        player_tabs["individual_performance"].append(section_data)
                    elif "analytics" in section_text:
                        player_tabs["player_analytics"].append(section_data)
                    elif "position" in section_text:
                        player_tabs["position_analysis"].append(section_data)
            
        except Exception as e:
            logger.warning(f"⚠️  Error mapping player data tabs: {e}")
        
        return player_tabs
    
    def _map_game_data_tabs(self) -> Dict[str, Any]:
        """Map game-specific data tabs and sections"""
        logger.info("🏆 Mapping game data tabs...")
        
        game_tabs = {
            "game_schedule": [],
            "game_results": [],
            "game_analysis": [],
            "play_by_play": [],
            "game_stats": []
        }
        
        try:
            # Look for game-related sections
            game_sections = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Game') or contains(text(), 'Match') or contains(text(), 'Schedule') or contains(@class, 'game')]")
            
            for section in game_sections:
                if section.is_displayed():
                    section_text = section.text.strip().lower()
                    section_data = {
                        "text": section.text.strip(),
                        "class": section.get_attribute("class"),
                        "has_export": bool(section.find_elements(By.CSS_SELECTOR, ".export, .download"))
                    }
                    
                    if "schedule" in section_text:
                        game_tabs["game_schedule"].append(section_data)
                    elif "result" in section_text:
                        game_tabs["game_results"].append(section_data)
                    elif "analysis" in section_text:
                        game_tabs["game_analysis"].append(section_data)
                    elif "play" in section_text and "play" in section_text:
                        game_tabs["play_by_play"].append(section_data)
                    elif "stat" in section_text:
                        game_tabs["game_stats"].append(section_data)
            
        except Exception as e:
            logger.warning(f"⚠️  Error mapping game data tabs: {e}")
        
        return game_tabs
    
    def _map_analytics_tabs(self) -> Dict[str, Any]:
        """Map analytics and performance tabs"""
        logger.info("📈 Mapping analytics tabs...")
        
        analytics_tabs = {
            "team_analytics": [],
            "performance_metrics": [],
            "advanced_stats": [],
            "trend_analysis": [],
            "comparative_analysis": []
        }
        
        try:
            # Look for analytics-related sections
            analytics_sections = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Analytics') or contains(text(), 'Performance') or contains(text(), 'Metrics') or contains(@class, 'analytics')]")
            
            for section in analytics_sections:
                if section.is_displayed():
                    section_text = section.text.strip().lower()
                    section_data = {
                        "text": section.text.strip(),
                        "class": section.get_attribute("class"),
                        "has_export": bool(section.find_elements(By.CSS_SELECTOR, ".export, .download"))
                    }
                    
                    if "team" in section_text:
                        analytics_tabs["team_analytics"].append(section_data)
                    elif "performance" in section_text:
                        analytics_tabs["performance_metrics"].append(section_data)
                    elif "advanced" in section_text:
                        analytics_tabs["advanced_stats"].append(section_data)
                    elif "trend" in section_text:
                        analytics_tabs["trend_analysis"].append(section_data)
                    elif "comparative" in section_text or "compare" in section_text:
                        analytics_tabs["comparative_analysis"].append(section_data)
            
        except Exception as e:
            logger.warning(f"⚠️  Error mapping analytics tabs: {e}")
        
        return analytics_tabs
    
    def _map_reports_tabs(self) -> Dict[str, Any]:
        """Map reports and reporting tabs"""
        logger.info("📄 Mapping reports tabs...")
        
        reports_tabs = {
            "game_reports": [],
            "player_reports": [],
            "team_reports": [],
            "custom_reports": [],
            "scheduled_reports": []
        }
        
        try:
            # Look for reports-related sections
            reports_sections = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Report') or contains(text(), 'Summary') or contains(@class, 'report')]")
            
            for section in reports_sections:
                if section.is_displayed():
                    section_text = section.text.strip().lower()
                    section_data = {
                        "text": section.text.strip(),
                        "class": section.get_attribute("class"),
                        "has_export": bool(section.find_elements(By.CSS_SELECTOR, ".export, .download"))
                    }
                    
                    if "game" in section_text:
                        reports_tabs["game_reports"].append(section_data)
                    elif "player" in section_text:
                        reports_tabs["player_reports"].append(section_data)
                    elif "team" in section_text:
                        reports_tabs["team_reports"].append(section_data)
                    elif "custom" in section_text:
                        reports_tabs["custom_reports"].append(section_data)
                    elif "schedule" in section_text:
                        reports_tabs["scheduled_reports"].append(section_data)
            
        except Exception as e:
            logger.warning(f"⚠️  Error mapping reports tabs: {e}")
        
        return reports_tabs
    
    def _map_video_tabs(self) -> Dict[str, Any]:
        """Map video and film analysis tabs"""
        logger.info("🎥 Mapping video tabs...")
        
        video_tabs = {
            "game_videos": [],
            "highlight_videos": [],
            "analysis_videos": [],
            "video_library": [],
            "video_export": []
        }
        
        try:
            # Look for video-related sections
            video_sections = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Video') or contains(text(), 'Film') or contains(@class, 'video')]")
            
            for section in video_sections:
                if section.is_displayed():
                    section_text = section.text.strip().lower()
                    section_data = {
                        "text": section.text.strip(),
                        "class": section.get_attribute("class"),
                        "has_export": bool(section.find_elements(By.CSS_SELECTOR, ".export, .download"))
                    }
                    
                    if "game" in section_text:
                        video_tabs["game_videos"].append(section_data)
                    elif "highlight" in section_text:
                        video_tabs["highlight_videos"].append(section_data)
                    elif "analysis" in section_text:
                        video_tabs["analysis_videos"].append(section_data)
                    elif "library" in section_text:
                        video_tabs["video_library"].append(section_data)
                    elif "export" in section_text:
                        video_tabs["video_export"].append(section_data)
            
        except Exception as e:
            logger.warning(f"⚠️  Error mapping video tabs: {e}")
        
        return video_tabs
    
    def _map_scouting_tabs(self) -> Dict[str, Any]:
        """Map scouting and analysis tabs"""
        logger.info("🔍 Mapping scouting tabs...")
        
        scouting_tabs = {
            "opponent_analysis": [],
            "player_scouting": [],
            "tactical_analysis": [],
            "formation_analysis": [],
            "scout_reports": []
        }
        
        try:
            # Look for scouting-related sections
            scouting_sections = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Scout') or contains(text(), 'Opponent') or contains(text(), 'Tactical') or contains(@class, 'scout')]")
            
            for section in scouting_sections:
                if section.is_displayed():
                    section_text = section.text.strip().lower()
                    section_data = {
                        "text": section.text.strip(),
                        "class": section.get_attribute("class"),
                        "has_export": bool(section.find_elements(By.CSS_SELECTOR, ".export, .download"))
                    }
                    
                    if "opponent" in section_text:
                        scouting_tabs["opponent_analysis"].append(section_data)
                    elif "player" in section_text:
                        scouting_tabs["player_scouting"].append(section_data)
                    elif "tactical" in section_text:
                        scouting_tabs["tactical_analysis"].append(section_data)
                    elif "formation" in section_text:
                        scouting_tabs["formation_analysis"].append(section_data)
                    elif "report" in section_text:
                        scouting_tabs["scout_reports"].append(section_data)
            
        except Exception as e:
            logger.warning(f"⚠️  Error mapping scouting tabs: {e}")
        
        return scouting_tabs
    
    def _get_nav_level(self, element) -> int:
        """Determine navigation level of an element"""
        try:
            level = 0
            parent = element.find_element(By.XPATH, "..")
            while parent and level < 10:  # Prevent infinite loop
                if parent.tag_name in ["nav", "ul", "ol"]:
                    level += 1
                parent = parent.find_element(By.XPATH, "..")
            return level
        except:
            return 0
    
    def close(self):
        """Close the analyzer"""
        self.analyzer.close()

def main():
    """Main function to demonstrate the tab mapper"""
    print("🗺️ Hudl Instat Tab and Data Section Mapper")
    print("=" * 60)
    
    # Initialize mapper
    mapper = HudlInstatTabMapper(headless=False)
    
    try:
        # Authenticate
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        if not mapper.authenticate(HUDL_USERNAME, HUDL_PASSWORD):
            print("❌ Authentication failed")
            return
        
        # Map team page tabs
        team_id = "21479"  # Bobcats team ID
        mapping = mapper.map_team_page_tabs(team_id)
        
        # Save mapping results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hudl_tab_mapping_{team_id}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(mapping, f, indent=2)
        
        print(f"📄 Tab mapping saved to: {filename}")
        
        # Print summary
        print(f"\n📊 Mapping Summary:")
        print(f"  Main navigation items: {len(mapping.get('main_navigation', {}).get('primary_nav', []))}")
        print(f"  Team tabs found: {sum(len(tabs) for tabs in mapping.get('team_tabs', {}).values())}")
        print(f"  Data sections: {sum(len(sections) for sections in mapping.get('data_sections', {}).values())}")
        print(f"  Export options: {sum(len(options) for options in mapping.get('export_options', {}).values())}")
        print(f"  Player data tabs: {sum(len(tabs) for tabs in mapping.get('player_data_tabs', {}).values())}")
        print(f"  Game data tabs: {sum(len(tabs) for tabs in mapping.get('game_data_tabs', {}).values())}")
        print(f"  Analytics tabs: {sum(len(tabs) for tabs in mapping.get('analytics_tabs', {}).values())}")
        print(f"  Reports tabs: {sum(len(tabs) for tabs in mapping.get('reports_tabs', {}).values())}")
        print(f"  Video tabs: {sum(len(tabs) for tabs in mapping.get('video_tabs', {}).values())}")
        print(f"  Scouting tabs: {sum(len(tabs) for tabs in mapping.get('scouting_tabs', {}).values())}")
        
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        mapper.close()

if __name__ == "__main__":
    main()
