#!/usr/bin/env python3
"""
Final Player Metric Extractor
Extracts player names, jersey numbers, and ALL metric values from the HTML structure
"""

import re
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_all_player_metrics():
    """Extract all player data with complete metric values"""
    try:
        logger.info("🔍 Extracting ALL player metrics from HTML...")
        
        with open('hudl-scraping/textfile.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract all player rows
        player_rows = re.findall(r'<div role="row"[^>]*>.*?</div>', content, re.DOTALL)
        logger.info(f"📊 Found {len(player_rows)} total player rows")
        
        players = []
        for i, row in enumerate(player_rows):
            # Look for player link pattern
            player_link_match = re.search(r'href="/instat/hockey/players/(\d+)"[^>]*>.*?<span[^>]*>(\d+)</span><span[^>]*>([^<]+)</span>', row)
            
            if player_link_match:
                player_id = player_link_match.group(1)
                jersey_number = player_link_match.group(2)
                player_name = player_link_match.group(3)
                
                # Extract ALL cell values from this row using multiple patterns
                all_cell_values = []
                
                # Pattern 1: Extract all div role="cell" elements
                cell_elements = re.findall(r'<div role="cell"[^>]*>([^<]*)</div>', row)
                all_cell_values.extend(cell_elements)
                
                # Clean up and filter values
                cleaned_values = []
                for value in all_cell_values:
                    value = value.strip()
                    if value and value != player_name and value != jersey_number:
                        cleaned_values.append(value)
                
                # Skip the first cell (player info) - it contains the player name and jersey
                metric_values = cleaned_values[1:] if len(cleaned_values) > 1 else cleaned_values
                
                player_data = {
                    'player_id': player_id,
                    'jersey_number': jersey_number,
                    'player_name': player_name,
                    'metric_values': metric_values,
                    'total_metrics': len(metric_values),
                    'row_index': i
                }
                
                players.append(player_data)
                
                # Log first few players for debugging
                if i < 5:
                    logger.info(f"📊 Player {i+1}: {player_name} (#{jersey_number}) - {len(metric_values)} metrics")
                    logger.info(f"   First 10 values: {metric_values[:10]}")
        
        logger.info(f"✅ Extracted {len(players)} players with metric values")
        return players
        
    except Exception as e:
        logger.error(f"❌ Error extracting player metrics: {e}")
        return []

def extract_metrics_from_textfile():
    """Extract all metrics from textfile.txt"""
    try:
        logger.info("🔍 Extracting metrics from textfile.txt...")
        
        with open('hudl-scraping/textfile.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match T9n wrapper elements with data-lexic
        pattern = r'<span data-lexic="(\d+)" class="T9n__T9nWrapper-sc-nijj7l-0 huyyNB">([^<]+)</span>'
        matches = re.findall(pattern, content)
        
        # Group by lexic ID
        metrics_by_lexic = {}
        for lexic_id, text in matches:
            lexic_id = int(lexic_id)
            text = text.strip()
            
            if not text:
                continue
                
            if lexic_id not in metrics_by_lexic:
                metrics_by_lexic[lexic_id] = {'lexic_id': lexic_id, 'full_name': '', 'abbreviation': '', 'all_texts': []}
            
            metrics_by_lexic[lexic_id]['all_texts'].append(text)
            
            # Determine if this is the full name or abbreviation
            if len(text) > 3 and not text.isupper() and not text.isdigit():
                if not metrics_by_lexic[lexic_id]['full_name']:
                    metrics_by_lexic[lexic_id]['full_name'] = text
            elif len(text) <= 3 and text.isupper():
                if not metrics_by_lexic[lexic_id]['abbreviation']:
                    metrics_by_lexic[lexic_id]['abbreviation'] = text
        
        logger.info(f"✅ Extracted {len(metrics_by_lexic)} unique metrics")
        return metrics_by_lexic
        
    except Exception as e:
        logger.error(f"❌ Error extracting metrics: {e}")
        return {}

def create_comprehensive_mapping(players, metrics):
    """Create comprehensive mapping of players to metrics"""
    try:
        logger.info("🔍 Creating comprehensive player-metric mapping...")
        
        # Create ordered list of metrics
        ordered_metrics = []
        for lexic_id, metric_data in sorted(metrics.items()):
            ordered_metrics.append({
                'lexic_id': lexic_id,
                'full_name': metric_data['full_name'],
                'abbreviation': metric_data['abbreviation']
            })
        
        # Map players to their metrics
        comprehensive_data = {
            'metrics': ordered_metrics,
            'players': []
        }
        
        for player in players:
            player_metrics = {}
            
            # Map each metric value to its corresponding metric name
            for i, value in enumerate(player['metric_values']):
                if i < len(ordered_metrics):
                    metric = ordered_metrics[i]
                    metric_key = metric['abbreviation'] if metric['abbreviation'] else metric['full_name']
                    if not metric_key:
                        metric_key = f"metric_{i+1}"
                    
                    player_metrics[metric_key] = value
            
            player_data = {
                'player_id': player['player_id'],
                'jersey_number': player['jersey_number'],
                'player_name': player['player_name'],
                'metrics': player_metrics,
                'total_metrics': len(player['metric_values'])
            }
            
            comprehensive_data['players'].append(player_data)
        
        logger.info(f"✅ Created comprehensive mapping for {len(comprehensive_data['players'])} players")
        return comprehensive_data
        
    except Exception as e:
        logger.error(f"❌ Error creating comprehensive mapping: {e}")
        return {}

def main():
    """Main function"""
    # Extract players with metrics
    players = extract_all_player_metrics()
    
    if not players:
        logger.error("❌ No players extracted!")
        return
    
    # Extract metrics
    metrics = extract_metrics_from_textfile()
    
    if not metrics:
        logger.error("❌ No metrics extracted!")
        return
    
    # Create comprehensive mapping
    comprehensive_data = create_comprehensive_mapping(players, metrics)
    
    if comprehensive_data:
        logger.info(f"🎉 SUCCESS! Comprehensive data extraction completed!")
        logger.info(f"📊 Total players: {len(comprehensive_data['players'])}")
        logger.info(f"📊 Total metrics: {len(comprehensive_data['metrics'])}")
        
        # Show sample data
        if comprehensive_data['players']:
            sample_player = comprehensive_data['players'][0]
            logger.info(f"📊 Sample player: {sample_player['player_name']} (#{sample_player['jersey_number']})")
            logger.info(f"📊 Total metrics: {sample_player['total_metrics']}")
            logger.info(f"📊 Sample metrics: {list(sample_player['metrics'].items())[:5]}")
        
        # Save results
        with open('final_comprehensive_data.json', 'w') as f:
            json.dump(comprehensive_data, f, indent=2)
        
        logger.info("✅ Results saved to final_comprehensive_data.json")
    else:
        logger.error("❌ FAILED! Comprehensive mapping failed!")

if __name__ == "__main__":
    main()
