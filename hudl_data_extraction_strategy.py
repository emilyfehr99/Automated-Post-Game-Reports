#!/usr/bin/env python3
"""
Hudl Data Extraction Strategy
Comprehensive strategy for extracting data from all Hudl Instat tabs and sections
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
class DataExtractionTarget:
    """Represents a specific data extraction target"""
    tab_name: str
    section_name: str
    data_type: str
    selector: str
    export_method: str
    priority: int
    description: str

class HudlDataExtractionStrategy:
    """Comprehensive data extraction strategy for Hudl Instat"""
    
    def __init__(self, headless: bool = False, user_identifier: str = None):
        """Initialize the data extraction strategy"""
        self.driver = None
        self.headless = headless
        self.user_identifier = user_identifier or "data_extractor"
        self.is_authenticated = False
        
        # Define comprehensive data extraction targets
        self.extraction_targets = self._define_extraction_targets()
        
    def _define_extraction_targets(self) -> List[DataExtractionTarget]:
        """Define all data extraction targets based on Hudl Instat structure"""
        
        targets = [
            # Team Overview Data
            DataExtractionTarget(
                tab_name="Overview",
                section_name="Team Information",
                data_type="team_info",
                selector=".team-info, .team-details, .team-header",
                export_method="text_extraction",
                priority=1,
                description="Basic team information and details"
            ),
            
            # Roster Data
            DataExtractionTarget(
                tab_name="Roster",
                section_name="Player List",
                data_type="roster",
                selector=".player-list, .roster, table[data-type='players']",
                export_method="table_extraction",
                priority=1,
                description="Complete team roster with player details"
            ),
            
            DataExtractionTarget(
                tab_name="Roster",
                section_name="Player Statistics",
                data_type="player_stats",
                selector=".player-stats, .individual-stats, table[data-type='player-stats']",
                export_method="table_extraction",
                priority=2,
                description="Individual player statistics"
            ),
            
            # Games Data
            DataExtractionTarget(
                tab_name="Games",
                section_name="Game Schedule",
                data_type="game_schedule",
                selector=".game-schedule, .schedule, table[data-type='schedule']",
                export_method="table_extraction",
                priority=1,
                description="Upcoming and past game schedule"
            ),
            
            DataExtractionTarget(
                tab_name="Games",
                section_name="Game Results",
                data_type="game_results",
                selector=".game-results, .results, table[data-type='results']",
                export_method="table_extraction",
                priority=1,
                description="Game results and scores"
            ),
            
            DataExtractionTarget(
                tab_name="Games",
                section_name="Play by Play",
                data_type="play_by_play",
                selector=".play-by-play, .pbp, table[data-type='pbp']",
                export_method="table_extraction",
                priority=3,
                description="Detailed play-by-play data"
            ),
            
            # Statistics Data
            DataExtractionTarget(
                tab_name="Statistics",
                section_name="Team Statistics",
                data_type="team_stats",
                selector=".team-stats, .stats-table, table[data-type='team-stats']",
                export_method="table_extraction",
                priority=1,
                description="Overall team statistics"
            ),
            
            DataExtractionTarget(
                tab_name="Statistics",
                section_name="Season Statistics",
                data_type="season_stats",
                selector=".season-stats, .yearly-stats, table[data-type='season']",
                export_method="table_extraction",
                priority=2,
                description="Season-long statistical data"
            ),
            
            DataExtractionTarget(
                tab_name="Statistics",
                section_name="Period Statistics",
                data_type="period_stats",
                selector=".period-stats, .period-breakdown, table[data-type='period']",
                export_method="table_extraction",
                priority=3,
                description="Statistics broken down by period"
            ),
            
            # Analytics Data
            DataExtractionTarget(
                tab_name="Analytics",
                section_name="Performance Metrics",
                data_type="performance_metrics",
                selector=".performance-metrics, .metrics, table[data-type='performance']",
                export_method="table_extraction",
                priority=2,
                description="Advanced performance metrics"
            ),
            
            DataExtractionTarget(
                tab_name="Analytics",
                section_name="Shot Analysis",
                data_type="shot_analysis",
                selector=".shot-analysis, .shots, table[data-type='shots']",
                export_method="table_extraction",
                priority=2,
                description="Shot location and effectiveness data"
            ),
            
            DataExtractionTarget(
                tab_name="Analytics",
                section_name="Passing Analysis",
                data_type="passing_analysis",
                selector=".passing-analysis, .passes, table[data-type='passes']",
                export_method="table_extraction",
                priority=2,
                description="Passing patterns and effectiveness"
            ),
            
            DataExtractionTarget(
                tab_name="Analytics",
                section_name="Zone Analysis",
                data_type="zone_analysis",
                selector=".zone-analysis, .zones, table[data-type='zones']",
                export_method="table_extraction",
                priority=3,
                description="Zone-specific performance data"
            ),
            
            # Reports Data
            DataExtractionTarget(
                tab_name="Reports",
                section_name="Game Reports",
                data_type="game_reports",
                selector=".game-reports, .reports, table[data-type='reports']",
                export_method="table_extraction",
                priority=2,
                description="Post-game analysis reports"
            ),
            
            DataExtractionTarget(
                tab_name="Reports",
                section_name="Player Reports",
                data_type="player_reports",
                selector=".player-reports, .individual-reports, table[data-type='player-reports']",
                export_method="table_extraction",
                priority=3,
                description="Individual player performance reports"
            ),
            
            # Video Data
            DataExtractionTarget(
                tab_name="Video",
                section_name="Game Videos",
                data_type="game_videos",
                selector=".game-videos, .videos, .video-list",
                export_method="link_extraction",
                priority=3,
                description="Links to game video content"
            ),
            
            DataExtractionTarget(
                tab_name="Video",
                section_name="Highlight Videos",
                data_type="highlight_videos",
                selector=".highlight-videos, .highlights, .video-highlights",
                export_method="link_extraction",
                priority=3,
                description="Links to highlight video content"
            ),
            
            # Scouting Data
            DataExtractionTarget(
                tab_name="Scouting",
                section_name="Opponent Analysis",
                data_type="opponent_analysis",
                selector=".opponent-analysis, .opponents, table[data-type='opponents']",
                export_method="table_extraction",
                priority=2,
                description="Opponent team analysis data"
            ),
            
            DataExtractionTarget(
                tab_name="Scouting",
                section_name="Tactical Analysis",
                data_type="tactical_analysis",
                selector=".tactical-analysis, .tactics, table[data-type='tactics']",
                export_method="table_extraction",
                priority=3,
                description="Tactical formation and strategy data"
            )
        ]
        
        return targets
    
    def setup_driver(self):
        """Setup Chrome WebDriver for data extraction"""
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
            logger.info("✅ Chrome WebDriver initialized for data extraction")
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
    
    def extract_team_data_comprehensive(self, team_id: str) -> Dict[str, Any]:
        """Extract comprehensive data from all available tabs and sections"""
        logger.info(f"📊 Extracting comprehensive data for team {team_id}")
        
        if not self.is_authenticated:
            logger.error("❌ Must authenticate before extracting data")
            return {"error": "Authentication required"}
        
        team_url = f"https://app.hudl.com/instat/hockey/teams/{team_id}"
        
        try:
            # Navigate to team page
            self.driver.get(team_url)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)  # Wait for dynamic content
            
            extraction_results = {
                "team_id": team_id,
                "url": team_url,
                "extraction_timestamp": datetime.now().isoformat(),
                "extracted_data": {},
                "extraction_summary": {
                    "total_targets": len(self.extraction_targets),
                    "successful_extractions": 0,
                    "failed_extractions": 0,
                    "extraction_errors": []
                }
            }
            
            # Extract data from each target
            for target in self.extraction_targets:
                try:
                    logger.info(f"🎯 Extracting {target.tab_name} - {target.section_name}")
                    
                    # Try to navigate to the tab if it exists
                    self._navigate_to_tab(target.tab_name)
                    
                    # Extract data based on the target
                    data = self._extract_data_from_target(target)
                    
                    if data:
                        extraction_results["extracted_data"][target.data_type] = {
                            "tab_name": target.tab_name,
                            "section_name": target.section_name,
                            "data": data,
                            "extraction_method": target.export_method,
                            "priority": target.priority,
                            "description": target.description
                        }
                        extraction_results["extraction_summary"]["successful_extractions"] += 1
                        logger.info(f"✅ Successfully extracted {target.data_type}")
                    else:
                        extraction_results["extraction_summary"]["failed_extractions"] += 1
                        logger.warning(f"⚠️  No data found for {target.data_type}")
                    
                    # Small delay between extractions
                    time.sleep(1)
                    
                except Exception as e:
                    error_msg = f"Error extracting {target.data_type}: {str(e)}"
                    extraction_results["extraction_summary"]["extraction_errors"].append(error_msg)
                    extraction_results["extraction_summary"]["failed_extractions"] += 1
                    logger.error(f"❌ {error_msg}")
            
            logger.info(f"✅ Comprehensive extraction completed: {extraction_results['extraction_summary']['successful_extractions']}/{extraction_results['extraction_summary']['total_targets']} successful")
            return extraction_results
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive extraction: {e}")
            return {"error": str(e), "team_id": team_id}
    
    def _navigate_to_tab(self, tab_name: str) -> bool:
        """Navigate to a specific tab if it exists"""
        try:
            # Look for tab elements
            tab_elements = self.driver.find_elements(By.XPATH, 
                f"//*[contains(text(), '{tab_name}') and (self::a or self::button or self::*[@role='tab'])]")
            
            for tab in tab_elements:
                if tab.is_displayed() and tab.is_enabled():
                    # Click the tab
                    ActionChains(self.driver).move_to_element(tab).click().perform()
                    time.sleep(2)  # Wait for tab content to load
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️  Could not navigate to tab {tab_name}: {e}")
            return False
    
    def _extract_data_from_target(self, target: DataExtractionTarget) -> Optional[Dict[str, Any]]:
        """Extract data from a specific target"""
        try:
            # Find elements matching the selector
            elements = self.driver.find_elements(By.CSS_SELECTOR, target.selector)
            
            if not elements:
                return None
            
            extracted_data = {
                "elements_found": len(elements),
                "extraction_method": target.export_method,
                "data": []
            }
            
            for element in elements:
                if element.is_displayed():
                    if target.export_method == "table_extraction":
                        table_data = self._extract_table_data(element)
                        if table_data:
                            extracted_data["data"].append(table_data)
                    
                    elif target.export_method == "text_extraction":
                        text_data = self._extract_text_data(element)
                        if text_data:
                            extracted_data["data"].append(text_data)
                    
                    elif target.export_method == "link_extraction":
                        link_data = self._extract_link_data(element)
                        if link_data:
                            extracted_data["data"].append(link_data)
            
            return extracted_data if extracted_data["data"] else None
            
        except Exception as e:
            logger.warning(f"⚠️  Error extracting data from {target.data_type}: {e}")
            return None
    
    def _extract_table_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract data from a table element"""
        try:
            # Get table headers
            headers = []
            header_elements = element.find_elements(By.CSS_SELECTOR, "th")
            for header in header_elements:
                if header.text.strip():
                    headers.append(header.text.strip())
            
            # Get table rows
            rows = []
            row_elements = element.find_elements(By.CSS_SELECTOR, "tr")
            
            for row in row_elements:
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                if cells:  # Skip header rows
                    row_data = []
                    for cell in cells:
                        row_data.append(cell.text.strip())
                    rows.append(row_data)
            
            return {
                "type": "table",
                "headers": headers,
                "rows": rows,
                "row_count": len(rows),
                "column_count": len(headers)
            }
            
        except Exception as e:
            logger.warning(f"⚠️  Error extracting table data: {e}")
            return None
    
    def _extract_text_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract text data from an element"""
        try:
            text_content = element.text.strip()
            if text_content:
                return {
                    "type": "text",
                    "content": text_content,
                    "tag": element.tag_name,
                    "class": element.get_attribute("class")
                }
            return None
            
        except Exception as e:
            logger.warning(f"⚠️  Error extracting text data: {e}")
            return None
    
    def _extract_link_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract link data from an element"""
        try:
            links = element.find_elements(By.CSS_SELECTOR, "a")
            link_data = []
            
            for link in links:
                if link.get_attribute("href"):
                    link_data.append({
                        "text": link.text.strip(),
                        "href": link.get_attribute("href"),
                        "title": link.get_attribute("title")
                    })
            
            return {
                "type": "links",
                "links": link_data,
                "link_count": len(link_data)
            } if link_data else None
            
        except Exception as e:
            logger.warning(f"⚠️  Error extracting link data: {e}")
            return None
    
    def get_extraction_strategy_summary(self) -> Dict[str, Any]:
        """Get a summary of the extraction strategy"""
        strategy_summary = {
            "total_extraction_targets": len(self.extraction_targets),
            "tabs_covered": list(set(target.tab_name for target in self.extraction_targets)),
            "data_types": list(set(target.data_type for target in self.extraction_targets)),
            "extraction_methods": list(set(target.export_method for target in self.extraction_targets)),
            "priority_breakdown": {
                "priority_1": len([t for t in self.extraction_targets if t.priority == 1]),
                "priority_2": len([t for t in self.extraction_targets if t.priority == 2]),
                "priority_3": len([t for t in self.extraction_targets if t.priority == 3])
            }
        }
        
        return strategy_summary
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 WebDriver closed")

def main():
    """Main function to demonstrate the data extraction strategy"""
    print("📊 Hudl Data Extraction Strategy")
    print("=" * 60)
    
    # Initialize strategy
    strategy = HudlDataExtractionStrategy(headless=False)
    
    # Show strategy summary
    summary = strategy.get_extraction_strategy_summary()
    print(f"\n📋 Extraction Strategy Summary:")
    print(f"  Total targets: {summary['total_extraction_targets']}")
    print(f"  Tabs covered: {', '.join(summary['tabs_covered'])}")
    print(f"  Data types: {', '.join(summary['data_types'])}")
    print(f"  Extraction methods: {', '.join(summary['extraction_methods'])}")
    print(f"  Priority breakdown: P1={summary['priority_breakdown']['priority_1']}, P2={summary['priority_breakdown']['priority_2']}, P3={summary['priority_breakdown']['priority_3']}")
    
    try:
        # Authenticate
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        if not strategy.authenticate(HUDL_USERNAME, HUDL_PASSWORD):
            print("❌ Authentication failed")
            return
        
        # Extract comprehensive data
        team_id = "21479"  # Bobcats team ID
        results = strategy.extract_team_data_comprehensive(team_id)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hudl_comprehensive_extraction_{team_id}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Extraction results saved to: {filename}")
        
        # Print summary
        if "extraction_summary" in results:
            summary = results["extraction_summary"]
            print(f"\n📊 Extraction Results:")
            print(f"  Successful: {summary['successful_extractions']}")
            print(f"  Failed: {summary['failed_extractions']}")
            print(f"  Success rate: {(summary['successful_extractions'] / summary['total_targets'] * 100):.1f}%")
            
            if summary['extraction_errors']:
                print(f"\n❌ Errors encountered:")
                for error in summary['extraction_errors'][:5]:  # Show first 5 errors
                    print(f"  - {error}")
        
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        strategy.close()

if __name__ == "__main__":
    main()
