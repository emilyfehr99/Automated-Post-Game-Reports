#!/usr/bin/env python3
"""
Lexic Metrics Extractor
Extracts all metrics using data-lexic attributes and their text content
"""

import time
import json
import logging
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LexicMetricsExtractor:
    def __init__(self):
        self.scraper = HudlCompleteMetricsScraper()
        
    def extract_all_lexic_metrics(self, team_id: str = "21479"):
        """Extract all metrics using data-lexic attributes"""
        try:
            logger.info("🚀 Starting Lexic Metrics Extraction...")
            
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
            
            # Extract all data-lexic elements
            logger.info("🔍 Extracting all data-lexic elements...")
            lexic_data = self.scraper.driver.execute_script("""
                var lexicElements = [];
                var allElements = document.querySelectorAll('[data-lexic]');
                
                for (var i = 0; i < allElements.length; i++) {
                    var element = allElements[i];
                    var lexicId = element.getAttribute('data-lexic');
                    var text = element.innerText.trim();
                    var className = element.className;
                    var tagName = element.tagName;
                    var parentText = element.parentElement ? element.parentElement.innerText.trim() : '';
                    
                    if (lexicId && text) {
                        lexicElements.push({
                            lexicId: lexicId,
                            text: text,
                            className: className,
                            tagName: tagName,
                            parentText: parentText
                        });
                    }
                }
                
                return lexicElements;
            """)
            
            logger.info(f"📊 Found {len(lexic_data)} data-lexic elements")
            
            # Group by lexic ID to find all text variations
            lexic_groups = {}
            for element in lexic_data:
                lexic_id = element['lexicId']
                if lexic_id not in lexic_groups:
                    lexic_groups[lexic_id] = []
                lexic_groups[lexic_id].append(element)
            
            logger.info(f"📊 Found {len(lexic_groups)} unique lexic IDs")
            
            # Extract metrics (focus on column headers)
            metrics = {}
            column_headers = []
            
            for lexic_id, elements in lexic_groups.items():
                # Look for elements that are likely metric names
                for element in elements:
                    text = element['text']
                    className = element['className']
                    tagName = element['tagName']
                    
                    # Check if this looks like a metric name (not just an abbreviation)
                    if (len(text) > 3 and 
                        not text.isdigit() and 
                        not text.isupper() and
                        ('TableHeaderCell' in className or 'columnheader' in className.lower())):
                        
                        if lexic_id not in metrics:
                            metrics[lexic_id] = {
                                'primary_text': text,
                                'lexic_id': lexic_id,
                                'all_texts': []
                            }
                        
                        metrics[lexic_id]['all_texts'].append({
                            'text': text,
                            'className': className,
                            'tagName': tagName
                        })
                        
                        column_headers.append({
                            'lexic_id': lexic_id,
                            'text': text,
                            'className': className
                        })
            
            logger.info(f"📊 Found {len(metrics)} potential metrics")
            logger.info(f"📊 Found {len(column_headers)} column headers")
            
            # Show all metrics found
            logger.info("📊 ALL METRICS FOUND:")
            logger.info("=" * 50)
            for i, (lexic_id, metric) in enumerate(sorted(metrics.items(), key=lambda x: x[0]), 1):
                logger.info(f"{i:3d}. ID {lexic_id}: {metric['primary_text']}")
                if len(metric['all_texts']) > 1:
                    for alt_text in metric['all_texts'][1:]:
                        logger.info(f"     Alt: {alt_text['text']}")
            
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
                'lexic_metrics': metrics,
                'column_headers': column_headers,
                'total_lexic_elements': len(lexic_data),
                'unique_lexic_ids': len(lexic_groups),
                'players': players,
                'extraction_timestamp': time.time()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in lexic metrics extraction: {e}")
            return {}
        finally:
            if hasattr(self.scraper, 'driver') and self.scraper.driver:
                self.scraper.driver.quit()

def main():
    """Main function"""
    extractor = LexicMetricsExtractor()
    results = extractor.extract_all_lexic_metrics()
    
    # Save results
    with open('lexic_metrics_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("✅ Results saved to lexic_metrics_results.json")
    
    # Print summary
    if results:
        logger.info(f"📊 Total lexic elements: {results.get('total_lexic_elements', 0)}")
        logger.info(f"📊 Unique lexic IDs: {results.get('unique_lexic_ids', 0)}")
        logger.info(f"📊 Metrics found: {len(results.get('lexic_metrics', {}))}")
        logger.info(f"📊 Column headers: {len(results.get('column_headers', []))}")
        logger.info(f"📊 Players: {len(results.get('players', []))}")

if __name__ == "__main__":
    main()
