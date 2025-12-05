#!/usr/bin/env python3
"""
Comprehensive Player Data Extractor
Extracts player names, jersey numbers, and metric values from both HTML and JSON formats
"""

import re
import json
import logging
from collections import defaultdict, OrderedDict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensivePlayerDataExtractor:
    def __init__(self):
        self.metrics = {}
        self.players = []
        
    def extract_metrics_from_textfile(self):
        """Extract all metrics from textfile.txt"""
        try:
            logger.info("🔍 Extracting metrics from textfile.txt...")
            
            with open('hudl-scraping/textfile.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern to match T9n wrapper elements with data-lexic
            pattern = r'<span data-lexic="(\d+)" class="T9n__T9nWrapper-sc-nijj7l-0 huyyNB">([^<]+)</span>'
            matches = re.findall(pattern, content)
            
            # Group by lexic ID
            metrics_by_lexic = defaultdict(lambda: {'lexic_id': '', 'full_name': '', 'abbreviation': '', 'all_texts': []})
            
            for lexic_id, text in matches:
                lexic_id = int(lexic_id)
                text = text.strip()
                
                if not text:
                    continue
                    
                metrics_by_lexic[lexic_id]['lexic_id'] = lexic_id
                metrics_by_lexic[lexic_id]['all_texts'].append(text)
                
                # Determine if this is the full name or abbreviation
                if len(text) > 3 and not text.isupper() and not text.isdigit():
                    if not metrics_by_lexic[lexic_id]['full_name']:
                        metrics_by_lexic[lexic_id]['full_name'] = text
                elif len(text) <= 3 and text.isupper():
                    if not metrics_by_lexic[lexic_id]['abbreviation']:
                        metrics_by_lexic[lexic_id]['abbreviation'] = text
            
            self.metrics = dict(sorted(metrics_by_lexic.items()))
            logger.info(f"✅ Extracted {len(self.metrics)} unique metrics")
            return self.metrics
            
        except Exception as e:
            logger.error(f"❌ Error extracting metrics: {e}")
            return {}
    
    def extract_players_from_html(self):
        """Extract player data from HTML format in textfile.txt"""
        try:
            logger.info("🔍 Extracting players from HTML format...")
            
            with open('hudl-scraping/textfile.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # More flexible pattern to match player rows
            player_rows = re.findall(r'<div role="row"[^>]*>.*?</div>', content, re.DOTALL)
            
            players = []
            for row in player_rows:
                # Extract player info
                player_match = re.search(r'href="/instat/hockey/players/(\d+)"[^>]*>.*?<span[^>]*>(\d+)</span><span[^>]*>([^<]+)</span>', row)
                if player_match:
                    player_id = player_match.group(1)
                    jersey_number = player_match.group(2)
                    player_name = player_match.group(3)
                    
                    # Extract all cell values - more comprehensive pattern
                    cell_pattern = r'<div role="cell"[^>]*class="[^"]*"[^>]*>([^<]*)</div>'
                    cells = re.findall(cell_pattern, row)
                    
                    # Also try a simpler pattern
                    if not cells:
                        cell_pattern = r'<div role="cell"[^>]*>([^<]*)</div>'
                        cells = re.findall(cell_pattern, row)
                    
                    # Skip the first cell (player info) and get the rest
                    metric_values = cells[1:] if len(cells) > 1 else []
                    
                    # Filter out empty values and clean up
                    metric_values = [v.strip() for v in metric_values if v.strip()]
                    
                    player_data = {
                        'player_id': player_id,
                        'jersey_number': jersey_number,
                        'player_name': player_name,
                        'metric_values': metric_values
                    }
                    
                    players.append(player_data)
            
            logger.info(f"✅ Extracted {len(players)} players from HTML")
            return players
            
        except Exception as e:
            logger.error(f"❌ Error extracting players from HTML: {e}")
            return []
    
    def extract_players_from_json(self):
        """Extract player data from JSON format in new.txt"""
        try:
            logger.info("🔍 Extracting players from JSON format...")
            
            with open('hudl-scraping/new.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find JSON objects in the content
            json_objects = []
            start = 0
            while True:
                start = content.find('{', start)
                if start == -1:
                    break
                
                # Find matching closing brace
                brace_count = 0
                end = start
                for i, char in enumerate(content[start:], start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                
                if brace_count == 0:
                    json_str = content[start:end]
                    try:
                        json_obj = json.loads(json_str)
                        if 'player_id' in json_obj and 'name_eng' in json_obj:
                            json_objects.append(json_obj)
                    except:
                        pass
                
                start = end
            
            logger.info(f"✅ Found {len(json_objects)} JSON player objects")
            return json_objects
            
        except Exception as e:
            logger.error(f"❌ Error extracting players from JSON: {e}")
            return []
    
    def map_metrics_to_players(self, html_players, json_players):
        """Map metrics to players using both HTML and JSON data"""
        try:
            logger.info("🔍 Mapping metrics to players...")
            
            # Create a mapping of player IDs to their data
            player_map = {}
            
            # Add HTML players
            for player in html_players:
                player_id = player['player_id']
                player_map[player_id] = {
                    'player_id': player_id,
                    'jersey_number': player['jersey_number'],
                    'player_name': player['player_name'],
                    'metric_values': player['metric_values'],
                    'source': 'html'
                }
            
            # Add JSON players
            for player in json_players:
                player_id = str(player['player_id'])
                if player_id not in player_map:
                    player_map[player_id] = {
                        'player_id': player_id,
                        'jersey_number': player.get('num', ''),
                        'player_name': player.get('name_eng', ''),
                        'metric_values': [],
                        'source': 'json',
                        'json_data': player
                    }
                else:
                    # Merge JSON data with existing HTML data
                    player_map[player_id]['json_data'] = player
                    player_map[player_id]['source'] = 'both'
            
            # Create comprehensive player list
            comprehensive_players = []
            for player_id, player_data in player_map.items():
                comprehensive_players.append(player_data)
            
            logger.info(f"✅ Mapped {len(comprehensive_players)} comprehensive players")
            return comprehensive_players
            
        except Exception as e:
            logger.error(f"❌ Error mapping metrics to players: {e}")
            return []
    
    def create_metric_mapping(self):
        """Create a mapping of metric positions to metric names"""
        try:
            logger.info("🔍 Creating metric mapping...")
            
            # Create ordered list of metrics based on lexic ID
            ordered_metrics = []
            for lexic_id, metric_data in sorted(self.metrics.items()):
                ordered_metrics.append({
                    'lexic_id': lexic_id,
                    'full_name': metric_data['full_name'],
                    'abbreviation': metric_data['abbreviation']
                })
            
            logger.info(f"✅ Created mapping for {len(ordered_metrics)} metrics")
            return ordered_metrics
            
        except Exception as e:
            logger.error(f"❌ Error creating metric mapping: {e}")
            return []
    
    def extract_comprehensive_data(self):
        """Extract comprehensive player and metric data"""
        try:
            logger.info("🚀 Starting comprehensive data extraction...")
            
            # Extract metrics
            metrics = self.extract_metrics_from_textfile()
            if not metrics:
                logger.error("❌ No metrics extracted")
                return {}
            
            # Extract players from HTML
            html_players = self.extract_players_from_html()
            
            # Extract players from JSON
            json_players = self.extract_players_from_json()
            
            # Map metrics to players
            comprehensive_players = self.map_metrics_to_players(html_players, json_players)
            
            # Create metric mapping
            metric_mapping = self.create_metric_mapping()
            
            # Create comprehensive result
            result = {
                'metrics': metrics,
                'metric_mapping': metric_mapping,
                'players': comprehensive_players,
                'html_players_count': len(html_players),
                'json_players_count': len(json_players),
                'total_players': len(comprehensive_players),
                'total_metrics': len(metrics)
            }
            
            # Save results
            with open('comprehensive_player_data.json', 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            logger.info("✅ Comprehensive data extraction completed!")
            logger.info(f"📊 Total metrics: {result['total_metrics']}")
            logger.info(f"📊 Total players: {result['total_players']}")
            logger.info(f"📊 HTML players: {result['html_players_count']}")
            logger.info(f"📊 JSON players: {result['json_players_count']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive data extraction: {e}")
            return {}

def main():
    """Main function"""
    extractor = ComprehensivePlayerDataExtractor()
    result = extractor.extract_comprehensive_data()
    
    if result:
        logger.info("🎉 SUCCESS! Comprehensive data extraction completed!")
        
        # Show sample data
        if result['players']:
            sample_player = result['players'][0]
            logger.info(f"📊 Sample player: {sample_player['player_name']} (#{sample_player['jersey_number']})")
            logger.info(f"📊 Metric values: {len(sample_player.get('metric_values', []))}")
        
        if result['metrics']:
            sample_metrics = list(result['metrics'].items())[:5]
            logger.info("📊 Sample metrics:")
            for lexic_id, metric in sample_metrics:
                logger.info(f"   {lexic_id}: {metric['full_name']} ({metric['abbreviation']})")
    else:
        logger.error("❌ FAILED! Comprehensive data extraction failed!")

if __name__ == "__main__":
    main()
