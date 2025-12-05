#!/usr/bin/env python3
"""
API Data Extractor
Uses the working Hudl scraper to get authenticated and then extracts API data
"""

import time
import json
import logging
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIDataExtractor:
    def __init__(self):
        self.scraper = HudlCompleteMetricsScraper()
        
    def extract_api_data(self, team_id: str = "21479"):
        """Extract API data using the working scraper"""
        try:
            logger.info("🚀 Starting API Data Extraction...")
            
            # Setup and login using the working scraper
            if not self.scraper.setup_driver():
                return {}
            
            username = "chaserochon777@gmail.com"
            password = "357Chaser!468"
            
            if not self.scraper.login(username, password):
                logger.error("❌ Authentication failed")
                return {}
            
            logger.info("✅ Authentication successful")
            
            # Navigate to team page
            team_url = f"https://hockey.instatscout.com/instat/hockey/teams/{team_id}"
            self.scraper.driver.get(team_url)
            time.sleep(3)
            
            # Click on SKATERS tab
            logger.info("🔍 Clicking SKATERS tab...")
            skaters_tab = self.scraper.driver.find_element("xpath", "//a[contains(text(), 'SKATERS')]")
            skaters_tab.click()
            time.sleep(3)
            
            # Execute API calls directly in the browser
            logger.info("🔍 Executing API calls in browser...")
            
            # API Call 1: Team Overview Stats
            logger.info("📊 Getting team overview stats...")
            team_overview_script = '''
                fetch('/api/scout_uni_overview_team_stat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        params: {
                            _p_team_id: 21479,
                            _p_season_id: 34,
                            _p_tournament_id: null
                        },
                        proc: "scout_uni_overview_team_stat"
                    })
                })
                .then(response => response.json())
                .then(data => {
                    window.teamOverviewData = data;
                    console.log('Team Overview Data:', data);
                })
                .catch(error => {
                    console.error('Team Overview Error:', error);
                    window.teamOverviewData = {error: error.message};
                });
            '''
            
            self.scraper.driver.execute_script(team_overview_script)
            time.sleep(2)
            
            # API Call 2: Lexical Parameters
            logger.info("📊 Getting lexical parameters...")
            lexical_script = '''
                fetch('/api/scout_param_lexical', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        params: {
                            lang: "en",
                            phrases: [1021, 15994, 15995, 17890, 16630]
                        },
                        proc: "scout_param_lexical"
                    })
                })
                .then(response => response.json())
                .then(data => {
                    window.lexicalData = data;
                    console.log('Lexical Data:', data);
                })
                .catch(error => {
                    console.error('Lexical Error:', error);
                    window.lexicalData = {error: error.message};
                });
            '''
            
            self.scraper.driver.execute_script(lexical_script)
            time.sleep(2)
            
            # API Call 3: Team Players Stats (try multiple endpoints)
            logger.info("📊 Getting team players stats...")
            players_endpoints = [
                "scout_uni_team_players_stat",
                "scout_uni_team_skaters_stat",
                "scout_uni_team_players_detailed",
                "scout_uni_team_players_comprehensive"
            ]
            
            for endpoint in players_endpoints:
                try:
                    players_script = f'''
                        fetch('/api/{endpoint}', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest'
                            }},
                            body: JSON.stringify({{
                                params: {{
                                    _p_team_id: 21479,
                                    _p_season_id: 34,
                                    _p_tournament_id: null
                                }},
                                proc: "{endpoint}"
                            }})
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            window.playersData = window.playersData || {{}};
                            window.playersData['{endpoint}'] = data;
                            console.log('Players Data ({endpoint}):', data);
                        }})
                        .catch(error => {{
                            console.error('Players Error ({endpoint}):', error);
                            window.playersData = window.playersData || {{}};
                            window.playersData['{endpoint}'] = {{error: error.message}};
                        }});
                    '''
                    
                    self.scraper.driver.execute_script(players_script)
                    time.sleep(1)
                except Exception as e:
                    logger.debug(f"Error with {endpoint}: {e}")
            
            # Wait for all API calls to complete
            time.sleep(5)
            
            # Get all results from browser
            logger.info("🔍 Retrieving API results...")
            results = {}
            
            try:
                team_overview = self.scraper.driver.execute_script("return window.teamOverviewData || {};")
                results['team_overview'] = team_overview
                logger.info(f"📊 Team Overview: {len(team_overview)} keys")
            except Exception as e:
                logger.error(f"❌ Error getting team overview: {e}")
            
            try:
                lexical_data = self.scraper.driver.execute_script("return window.lexicalData || {};")
                results['lexical'] = lexical_data
                logger.info(f"📊 Lexical: {len(lexical_data)} keys")
            except Exception as e:
                logger.error(f"❌ Error getting lexical data: {e}")
            
            try:
                players_data = self.scraper.driver.execute_script("return window.playersData || {};")
                results['players'] = players_data
                logger.info(f"📊 Players: {len(players_data)} endpoints")
            except Exception as e:
                logger.error(f"❌ Error getting players data: {e}")
            
            # Also get the current page data
            try:
                page_data = self.scraper.driver.execute_script("""
                    return {
                        url: window.location.href,
                        title: document.title,
                        allText: document.body.innerText,
                        allElements: document.querySelectorAll('*').length
                    };
                """)
                results['page_info'] = page_data
            except Exception as e:
                logger.error(f"❌ Error getting page data: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in API data extraction: {e}")
            return {}
        finally:
            if hasattr(self.scraper, 'driver') and self.scraper.driver:
                self.scraper.driver.quit()

def main():
    """Main function"""
    logger.info("🚀 Starting API Data Extractor...")
    
    extractor = APIDataExtractor()
    results = extractor.extract_api_data()
    
    # Save results
    with open('api_extraction_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("✅ Results saved to api_extraction_results.json")
    
    # Print summary
    for key, value in results.items():
        if isinstance(value, dict):
            logger.info(f"📊 {key}: {len(value)} keys")
            if key == 'players' and isinstance(value, dict):
                for endpoint, data in value.items():
                    if isinstance(data, dict):
                        logger.info(f"  📊 {endpoint}: {len(data)} keys")
        else:
            logger.info(f"📊 {key}: {type(value)}")

if __name__ == "__main__":
    main()
