#!/usr/bin/env python3
"""
Working Player Metric Extractor
Extracts individual player data with correct cell value extraction
"""

import re
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_players_working():
    """Extract players with working cell value extraction"""
    try:
        logger.info("🔍 Extracting players with working cell extraction...")
        
        with open('hudl-scraping/textfile.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use the exact pattern from the HTML structure we saw
        # Each player row starts with: <div role="row" class="Table__TableRow-sc-2etlst-3 RNiTu" style="position: absolute; left: 0px; top: XXXpx; height: 30px; width: auto; min-width: 100%;">
        
        # Find all player rows by looking for the specific pattern
        player_row_pattern = r'<div role="row" class="Table__TableRow-sc-2etlst-3 RNiTu" style="position: absolute; left: 0px; top: \d+px; height: 30px; width: auto; min-width: 100%;">.*?</div>'
        
        # Find all player rows
        player_rows = re.findall(player_row_pattern, content, re.DOTALL)
        logger.info(f"📊 Found {len(player_rows)} player rows with position styling")
        
        players = []
        for i, row in enumerate(player_rows):
            # Extract player info from this specific row
            player_link_match = re.search(r'<a class="styled__PLayerNavLink-sc-r181ky-0 cVkPVn" href="/instat/hockey/players/(\d+)"[^>]*>.*?<span class="styled__PlayerNumber-sc-r181ky-3 bOpdrm">(\d+)</span>.*?<span class="styled__PlayerName-sc-r181ky-2 kgrDyf">([^<]+)</span>', row, re.DOTALL)
            
            if player_link_match:
                player_id = player_link_match.group(1)
                jersey_number = player_link_match.group(2)
                player_name = player_link_match.group(3)
                
                # Extract ALL cell values from this specific row only
                # Use a more specific pattern that matches the exact HTML structure
                cell_values = re.findall(r'<div role="cell"[^>]*class="Table__TableCell-sc-2etlst-5[^"]*"[^>]*>([^<]*)</div>', row)
                
                # Clean up values - remove player name and jersey number
                cleaned_values = []
                for value in cell_values:
                    value = value.strip()
                    if value and value != player_name and value != jersey_number and value != player_id:
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
        logger.error(f"❌ Error extracting players working: {e}")
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

def create_working_mapping(players, metrics):
    """Create working mapping of players to metrics"""
    try:
        logger.info("🔍 Creating working player-metric mapping...")
        
        # Create ordered list of metrics
        ordered_metrics = []
        for lexic_id, metric_data in sorted(metrics.items()):
            ordered_metrics.append({
                'lexic_id': lexic_id,
                'full_name': metric_data['full_name'],
                'abbreviation': metric_data['abbreviation']
            })
        
        # Map players to their metrics
        working_data = {
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
            
            working_data['players'].append(player_data)
        
        logger.info(f"✅ Created working mapping for {len(working_data['players'])} players")
        return working_data
        
    except Exception as e:
        logger.error(f"❌ Error creating working mapping: {e}")
        return {}

def main():
    """Main function"""
    # Extract players with metrics
    players = extract_players_working()
    
    if not players:
        logger.error("❌ No players extracted!")
        return
    
    # Extract metrics
    metrics = extract_metrics_from_textfile()
    
    if not metrics:
        logger.error("❌ No metrics extracted!")
        return
    
    # Create working mapping
    working_data = create_working_mapping(players, metrics)
    
    if working_data:
        logger.info(f"🎉 SUCCESS! Working data extraction completed!")
        logger.info(f"📊 Total players: {len(working_data['players'])}")
        logger.info(f"📊 Total metrics: {len(working_data['metrics'])}")
        
        # Show sample data
        if working_data['players']:
            sample_player = working_data['players'][0]
            logger.info(f"📊 Sample player: {sample_player['player_name']} (#{sample_player['jersey_number']})")
            logger.info(f"📊 Total metrics: {sample_player['total_metrics']}")
            logger.info(f"📊 Sample metrics: {list(sample_player['metrics'].items())[:5]}")
        
        # Save results
        with open('working_player_data.json', 'w') as f:
            json.dump(working_data, f, indent=2)
        
        logger.info("✅ Results saved to working_player_data.json")
    else:
        logger.error("❌ FAILED! Working mapping failed!")

if __name__ == "__main__":
    main()
