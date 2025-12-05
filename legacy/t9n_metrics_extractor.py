#!/usr/bin/env python3
"""
T9n Metrics Extractor
Extracts all metric names from T9n__T9nWrapper-sc-nijj7l-0 class elements in columnheader divs
"""

import time
import json
import logging
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class T9nMetricsExtractor:
    def __init__(self):
        self.scraper = HudlCompleteMetricsScraper()
        
    def extract_t9n_metrics(self, team_id: str = "21479"):
        """Extract all metrics using T9n__T9nWrapper-sc-nijj7l-0 class elements"""
        try:
            logger.info("🚀 Starting T9n Metrics Extraction...")
            
            if not self.scraper.setup_driver():
                return {}
            
            # Login
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
            
            # Extract all T9n wrapper elements
            logger.info("🔍 Extracting T9n wrapper elements...")
            t9n_data = self.scraper.driver.execute_script("""
                var t9nElements = [];
                var allElements = document.querySelectorAll('.T9n__T9nWrapper-sc-nijj7l-0');
                
                for (var i = 0; i < allElements.length; i++) {
                    var element = allElements[i];
                    var text = element.innerText.trim();
                    var className = element.className;
                    var dataLexic = element.getAttribute('data-lexic') || '';
                    var parentElement = element.parentElement;
                    var parentRole = parentElement ? parentElement.getAttribute('role') : '';
                    var parentClass = parentElement ? parentElement.className : '';
                    
                    if (text) {
                        t9nElements.push({
                            text: text,
                            className: className,
                            dataLexic: dataLexic,
                            parentRole: parentRole,
                            parentClass: parentClass,
                            isColumnHeader: parentRole === 'columnheader'
                        });
                    }
                }
                
                return t9nElements;
            """)
            
            logger.info(f"📊 Found {len(t9n_data)} T9n wrapper elements")
            
            # Filter for column header elements
            column_header_metrics = [elem for elem in t9n_data if elem['isColumnHeader']]
            logger.info(f"📊 Found {len(column_header_metrics)} T9n elements in column headers")
            
            # Group by data-lexic to find full names and abbreviations
            metrics_by_lexic = {}
            for elem in column_header_metrics:
                lexic_id = elem['dataLexic']
                if lexic_id:
                    if lexic_id not in metrics_by_lexic:
                        metrics_by_lexic[lexic_id] = {
                            'lexic_id': lexic_id,
                            'full_name': '',
                            'abbreviation': '',
                            'all_texts': []
                        }
                    
                    metrics_by_lexic[lexic_id]['all_texts'].append(elem['text'])
                    
                    # Determine if this is the full name or abbreviation
                    text = elem['text']
                    if len(text) > 3 and not text.isupper():
                        # Likely the full name
                        metrics_by_lexic[lexic_id]['full_name'] = text
                    elif len(text) <= 3 and text.isupper():
                        # Likely the abbreviation
                        metrics_by_lexic[lexic_id]['abbreviation'] = text
            
            logger.info(f"📊 Found {len(metrics_by_lexic)} unique metrics with lexic IDs")
            
            # Show all metrics found
            logger.info("📊 ALL METRICS FOUND:")
            logger.info("=" * 80)
            for i, (lexic_id, metric) in enumerate(sorted(metrics_by_lexic.items(), key=lambda x: x[0]), 1):
                full_name = metric['full_name'] or 'N/A'
                abbreviation = metric['abbreviation'] or 'N/A'
                logger.info(f"{i:3d}. ID {lexic_id}: {full_name} ({abbreviation})")
                if len(metric['all_texts']) > 2:
                    logger.info(f"     All texts: {', '.join(metric['all_texts'])}")
            
            # Also extract all column headers directly
            logger.info("🔍 Extracting all column headers...")
            column_headers = self.scraper.driver.execute_script("""
                var columnHeaders = [];
                var allHeaders = document.querySelectorAll('[role="columnheader"]');
                
                for (var i = 0; i < allHeaders.length; i++) {
                    var header = allHeaders[i];
                    var text = header.innerText.trim();
                    var className = header.className;
                    
                    if (text) {
                        columnHeaders.push({
                            text: text,
                            className: className
                        });
                    }
                }
                
                return columnHeaders;
            """)
            
            logger.info(f"📊 Found {len(column_headers)} column headers")
            
            # Show column headers
            logger.info("📊 COLUMN HEADERS FOUND:")
            logger.info("=" * 50)
            for i, header in enumerate(column_headers, 1):
                logger.info(f"{i:3d}. {header['text']}")
            
            # Now try to get player data with all these metrics
            logger.info("🔍 Getting player data...")
            players = self.scraper.get_team_players(team_id)
            
            if players:
                logger.info(f"✅ Found {len(players)} players")
                
                # Analyze first player's metrics
                first_player = players[0]
                player_metrics = first_player.get('metrics', {})
                logger.info(f"📊 First player has {len(player_metrics)} metrics")
                
                # Show first 20 metrics
                logger.info("📊 First 20 player metrics:")
                for i, (key, value) in enumerate(list(player_metrics.items())[:20], 1):
                    logger.info(f"  {i:2d}. {key}: {value}")
            else:
                logger.warning("⚠️ No players data found")
            
            results = {
                't9n_metrics': metrics_by_lexic,
                'column_headers': column_headers,
                'total_t9n_elements': len(t9n_data),
                'column_header_metrics': len(column_header_metrics),
                'unique_metrics': len(metrics_by_lexic),
                'players': players,
                'extraction_timestamp': time.time()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in T9n metrics extraction: {e}")
            return {}
        finally:
            if hasattr(self.scraper, 'driver') and self.scraper.driver:
                self.scraper.driver.quit()

def main():
    """Main function"""
    extractor = T9nMetricsExtractor()
    results = extractor.extract_t9n_metrics()
    
    # Save results
    with open('t9n_metrics_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("✅ Results saved to t9n_metrics_results.json")
    
    # Print summary
    if results:
        logger.info(f"📊 Total T9n elements: {results.get('total_t9n_elements', 0)}")
        logger.info(f"📊 Column header metrics: {results.get('column_header_metrics', 0)}")
        logger.info(f"📊 Unique metrics: {results.get('unique_metrics', 0)}")
        logger.info(f"📊 Column headers: {len(results.get('column_headers', []))}")
        logger.info(f"📊 Players: {len(results.get('players', []))}")

if __name__ == "__main__":
    main()
