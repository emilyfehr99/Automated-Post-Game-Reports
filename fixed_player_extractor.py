#!/usr/bin/env python3
"""
Fixed Player Metric Extractor
Properly extracts individual player data without cross-contamination
"""

import re
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_players_properly():
    """Extract players with proper row separation"""
    try:
        logger.info("🔍 Extracting players with proper row separation...")
        
        with open('hudl-scraping/textfile.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content by player rows more carefully
        # Look for the specific pattern that indicates a player row
        player_row_pattern = r'<div role="row"[^>]*style="[^"]*position:\s*absolute[^"]*"[^>]*>.*?<a class="styled__PLayerNavLink-sc-r181ky-0 cVkPVn" href="/instat/hockey/players/(\d+)"[^>]*>.*?<span class="styled__PlayerNumber-sc-r181ky-3 bOpdrm">(\d+)</span>.*?<span class="styled__PlayerName-sc-r181ky-2 kgrDyf">([^<]+)</span>.*?</a>.*?</div>'
        
        # Find all player rows
        player_matches = re.findall(player_row_pattern, content, re.DOTALL)
        logger.info(f"📊 Found {len(player_matches)} player rows with position styling")
        
        # If no matches with position styling, try without it
        if not player_matches:
            player_row_pattern = r'<div role="row"[^>]*>.*?<a class="styled__PLayerNavLink-sc-r181ky-0 cVkPVn" href="/instat/hockey/players/(\d+)"[^>]*>.*?<span class="styled__PlayerNumber-sc-r181ky-3 bOpdrm">(\d+)</span>.*?<span class="styled__PlayerName-sc-r181ky-2 kgrDyf">([^<]+)</span>.*?</a>.*?</div>'
            player_matches = re.findall(player_row_pattern, content, re.DOTALL)
            logger.info(f"📊 Found {len(player_matches)} total player rows")
        
        players = []
        for i, (player_id, jersey_number, player_name) in enumerate(player_matches):
            # Now find the specific row for this player
            # Use a more specific pattern to find just this player's row
            specific_row_pattern = rf'<div role="row"[^>]*>.*?<a class="styled__PLayerNavLink-sc-r181ky-0 cVkPVn" href="/instat/hockey/players/{re.escape(player_id)}"[^>]*>.*?<span class="styled__PlayerNumber-sc-r181ky-3 bOpdrm">{re.escape(jersey_number)}</span>.*?<span class="styled__PlayerName-sc-r181ky-2 kgrDyf">{re.escape(player_name)}</span>.*?</a>(.*?)</div>'
            
            row_match = re.search(specific_row_pattern, content, re.DOTALL)
            if row_match:
                row_content = row_match.group(0)
                
                # Extract cell values from this specific row only
                cell_values = re.findall(r'<div role="cell"[^>]*>([^<]*)</div>', row_content)
                
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
        logger.error(f"❌ Error extracting players properly: {e}")
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

def create_fixed_mapping(players, metrics):
    """Create fixed mapping of players to metrics"""
    try:
        logger.info("🔍 Creating fixed player-metric mapping...")
        
        # Create ordered list of metrics
        ordered_metrics = []
        for lexic_id, metric_data in sorted(metrics.items()):
            ordered_metrics.append({
                'lexic_id': lexic_id,
                'full_name': metric_data['full_name'],
                'abbreviation': metric_data['abbreviation']
            })
        
        # Map players to their metrics
        fixed_data = {
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
            
            fixed_data['players'].append(player_data)
        
        logger.info(f"✅ Created fixed mapping for {len(fixed_data['players'])} players")
        return fixed_data
        
    except Exception as e:
        logger.error(f"❌ Error creating fixed mapping: {e}")
        return {}

def main():
    """Main function"""
    # Extract players with metrics
    players = extract_players_properly()
    
    if not players:
        logger.error("❌ No players extracted!")
        return
    
    # Extract metrics
    metrics = extract_metrics_from_textfile()
    
    if not metrics:
        logger.error("❌ No metrics extracted!")
        return
    
    # Create fixed mapping
    fixed_data = create_fixed_mapping(players, metrics)
    
    if fixed_data:
        logger.info(f"🎉 SUCCESS! Fixed data extraction completed!")
        logger.info(f"📊 Total players: {len(fixed_data['players'])}")
        logger.info(f"📊 Total metrics: {len(fixed_data['metrics'])}")
        
        # Show sample data
        if fixed_data['players']:
            sample_player = fixed_data['players'][0]
            logger.info(f"📊 Sample player: {sample_player['player_name']} (#{sample_player['jersey_number']})")
            logger.info(f"📊 Total metrics: {sample_player['total_metrics']}")
            logger.info(f"📊 Sample metrics: {list(sample_player['metrics'].items())[:5]}")
        
        # Save results
        with open('fixed_player_data.json', 'w') as f:
            json.dump(fixed_data, f, indent=2)
        
        logger.info("✅ Results saved to fixed_player_data.json")
    else:
        logger.error("❌ FAILED! Fixed mapping failed!")

if __name__ == "__main__":
    main()
