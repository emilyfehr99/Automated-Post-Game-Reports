#!/usr/bin/env python3
"""
Simple API Extractor
Uses the working scraper to get data and then tries to extract more metrics
"""

import time
import json
import logging
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_all_available_metrics():
    """Extract all available metrics using the working scraper"""
    try:
        logger.info("🚀 Starting Simple API Extractor...")
        
        # Use the working scraper
        scraper = HudlCompleteMetricsScraper()
        
        if not scraper.setup_driver():
            return {}
        
        # Login
        username = "chaserochon777@gmail.com"
        password = "357Chaser!468"
        
        if not scraper.login(username, password):
            logger.error("❌ Authentication failed")
            return {}
        
        logger.info("✅ Authentication successful")
        
        # Get team players data
        players = scraper.get_team_players("21479")
        
        if not players:
            logger.error("❌ No players data found")
            return {}
        
        logger.info(f"✅ Found {len(players)} players")
        
        # Try to get more comprehensive data by looking at the page source
        logger.info("🔍 Analyzing page source for additional metrics...")
        
        # Get page source
        page_source = scraper.driver.page_source
        
        # Look for metric-related data in the page source
        metric_data = {}
        
        # Look for JavaScript variables that might contain metric data
        try:
            js_variables = scraper.driver.execute_script("""
                var metrics = {};
                
                // Look for common variable names that might contain metric data
                var possibleVars = [
                    'metrics', 'stats', 'data', 'players', 'teamData', 
                    'overview', 'statistics', 'playerStats', 'teamStats',
                    'scoutData', 'instatData', 'hockeyData'
                ];
                
                for (var i = 0; i < possibleVars.length; i++) {
                    try {
                        if (window[possibleVars[i]]) {
                            metrics[possibleVars[i]] = window[possibleVars[i]];
                        }
                    } catch(e) {
                        // Variable doesn't exist or can't be accessed
                    }
                }
                
                return metrics;
            """)
            
            metric_data['js_variables'] = js_variables
            logger.info(f"📊 Found {len(js_variables)} JavaScript variables")
            
        except Exception as e:
            logger.error(f"❌ Error getting JS variables: {e}")
        
        # Look for data attributes
        try:
            data_attributes = scraper.driver.execute_script("""
                var dataAttrs = {};
                var elements = document.querySelectorAll('[data-*]');
                
                for (var i = 0; i < elements.length; i++) {
                    var element = elements[i];
                    var attrs = element.attributes;
                    
                    for (var j = 0; j < attrs.length; j++) {
                        var attr = attrs[j];
                        if (attr.name.startsWith('data-')) {
                            var key = attr.name;
                            if (!dataAttrs[key]) {
                                dataAttrs[key] = [];
                            }
                            dataAttrs[key].push(attr.value);
                        }
                    }
                }
                
                return dataAttrs;
            """)
            
            metric_data['data_attributes'] = data_attributes
            logger.info(f"📊 Found {len(data_attributes)} data attributes")
            
        except Exception as e:
            logger.error(f"❌ Error getting data attributes: {e}")
        
        # Look for all text content that might be metrics
        try:
            all_text = scraper.driver.execute_script("return document.body.innerText;")
            
            # Extract potential metric names from text
            potential_metrics = set()
            lines = all_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if (len(line) <= 10 and 
                    line.isupper() and 
                    not line.isdigit() and 
                    not ':' in line and
                    not ' ' in line and
                    line not in ['PLAYER', 'POS', 'TOI', 'GP', 'SHIFTS']):
                    potential_metrics.add(line)
            
            metric_data['potential_metrics'] = list(potential_metrics)
            logger.info(f"📊 Found {len(potential_metrics)} potential metrics")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing text content: {e}")
        
        # Look for table headers
        try:
            table_headers = scraper.driver.execute_script("""
                var headers = [];
                var headerElements = document.querySelectorAll('th, [role="columnheader"], .header, .column-header');
                
                for (var i = 0; i < headerElements.length; i++) {
                    var text = headerElements[i].innerText.trim();
                    if (text && text.length > 0) {
                        headers.push(text);
                    }
                }
                
                return headers;
            """)
            
            metric_data['table_headers'] = table_headers
            logger.info(f"📊 Found {len(table_headers)} table headers")
            
        except Exception as e:
            logger.error(f"❌ Error getting table headers: {e}")
        
        # Look for all elements with text that might be metrics
        try:
            all_elements = scraper.driver.execute_script("""
                var elements = [];
                var allElements = document.querySelectorAll('*');
                
                for (var i = 0; i < allElements.length; i++) {
                    var element = allElements[i];
                    var text = element.innerText.trim();
                    
                    if (text && 
                        text.length <= 10 && 
                        text.length > 1 &&
                        text.isUpperCase && 
                        !text.match(/\\d/) &&
                        !text.includes(':') &&
                        !text.includes(' ') &&
                        !['PLAYER', 'POS', 'TOI', 'GP', 'SHIFTS'].includes(text)) {
                        elements.push({
                            tag: element.tagName,
                            text: text,
                            className: element.className,
                            id: element.id
                        });
                    }
                }
                
                return elements;
            """)
            
            metric_data['metric_elements'] = all_elements
            logger.info(f"📊 Found {len(all_elements)} potential metric elements")
            
        except Exception as e:
            logger.error(f"❌ Error getting metric elements: {e}")
        
        # Combine all data
        results = {
            'players': players,
            'metric_analysis': metric_data,
            'total_players': len(players),
            'extraction_timestamp': time.time()
        }
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error in metric extraction: {e}")
        return {}
    finally:
        if 'scraper' in locals() and scraper.driver:
            scraper.driver.quit()

def main():
    """Main function"""
    results = extract_all_available_metrics()
    
    # Save results
    with open('simple_api_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("✅ Results saved to simple_api_results.json")
    
    # Print summary
    if results:
        logger.info(f"📊 Total players: {results.get('total_players', 0)}")
        
        if 'metric_analysis' in results:
            analysis = results['metric_analysis']
            logger.info(f"📊 Potential metrics: {len(analysis.get('potential_metrics', []))}")
            logger.info(f"📊 Table headers: {len(analysis.get('table_headers', []))}")
            logger.info(f"📊 Metric elements: {len(analysis.get('metric_elements', []))}")
            
            # Show some potential metrics
            if 'potential_metrics' in analysis:
                logger.info("📊 Sample potential metrics:")
                for i, metric in enumerate(analysis['potential_metrics'][:20]):
                    logger.info(f"  {i+1:2d}. {metric}")
                if len(analysis['potential_metrics']) > 20:
                    logger.info(f"  ... and {len(analysis['potential_metrics']) - 20} more")

if __name__ == "__main__":
    main()
