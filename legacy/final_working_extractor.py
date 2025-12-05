#!/usr/bin/env python3
"""
Final Working Player Metric Extractor
Extracts individual player data with correct row parsing and cell value extraction
"""

import re
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_players_final():
    """Extract players with final working row parsing"""
    try:
        logger.info("🔍 Extracting players with final working method...")
        
        with open('hudl-scraping/textfile.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all player rows by looking for the specific pattern
        player_row_pattern = r'<div role="row" class="Table__TableRow-sc-2etlst-3 RNiTu" style="position: absolute; left: 0px; top: \d+px; height: 30px; width: auto; min-width: 100%;">'
        
        # Find all start positions
        start_matches = list(re.finditer(player_row_pattern, content))
        logger.info(f"📊 Found {len(start_matches)} player row starts")
        
        players = []
        for i, start_match in enumerate(start_matches):
            start_pos = start_match.start()
            
            # Find the matching closing </div> tag
            pos = start_pos
            div_count = 0
            found_start = False
            
            while pos < len(content):
                if content[pos:pos+4] == '<div':
                    div_count += 1
                    found_start = True
                elif content[pos:pos+6] == '</div>':
                    div_count -= 1
                    if found_start and div_count == 0:
                        # Found the matching closing tag
                        end_pos = pos + 6
                        row = content[start_pos:end_pos]
                        
                        # Extract player info from this specific row
                        player_link_match = re.search(r'<a class="styled__PLayerNavLink-sc-r181ky-0 cVkPVn" href="/instat/hockey/players/(\d+)"[^>]*>.*?<span class="styled__PlayerNumber-sc-r181ky-3 bOpdrm">(\d+)</span>.*?<span class="styled__PlayerName-sc-r181ky-2 kgrDyf">([^<]+)</span>', row, re.DOTALL)
                        
                        if player_link_match:
                            player_id = player_link_match.group(1)
                            jersey_number = player_link_match.group(2)
                            player_name = player_link_match.group(3)
                            
                            # Extract ALL cell values from this specific row
                            value_pattern = r'>([^<]+)</div>'
                            value_matches = re.findall(value_pattern, row)
                            
                            # Clean up values - remove player name and jersey number
                            cleaned_values = []
                            for value in value_matches:
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
                        break
                pos += 1
        
        logger.info(f"✅ Extracted {len(players)} players with metric values")
        return players
        
    except Exception as e:
        logger.error(f"❌ Error extracting players final: {e}")
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

def create_final_mapping(players, metrics):
    """Create final mapping of players to metrics"""
    try:
        logger.info("🔍 Creating final player-metric mapping...")
        
        # Create ordered list of metrics
        ordered_metrics = []
        for lexic_id, metric_data in sorted(metrics.items()):
            ordered_metrics.append({
                'lexic_id': lexic_id,
                'full_name': metric_data['full_name'],
                'abbreviation': metric_data['abbreviation']
            })
        
        # Map players to their metrics
        final_data = {
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
            
            final_data['players'].append(player_data)
        
        logger.info(f"✅ Created final mapping for {len(final_data['players'])} players")
        return final_data
        
    except Exception as e:
        logger.error(f"❌ Error creating final mapping: {e}")
        return {}

def main():
    """Main function"""
    # Extract players with metrics
    players = extract_players_final()
    
    if not players:
        logger.error("❌ No players extracted!")
        return
    
    # Extract metrics
    metrics = extract_metrics_from_textfile()
    
    if not metrics:
        logger.error("❌ No metrics extracted!")
        return
    
    # Create final mapping
    final_data = create_final_mapping(players, metrics)
    
    if final_data:
        logger.info(f"🎉 SUCCESS! Final data extraction completed!")
        logger.info(f"📊 Total players: {len(final_data['players'])}")
        logger.info(f"📊 Total metrics: {len(final_data['metrics'])}")
        
        # Show sample data
        if final_data['players']:
            sample_player = final_data['players'][0]
            logger.info(f"📊 Sample player: {sample_player['player_name']} (#{sample_player['jersey_number']})")
            logger.info(f"📊 Total metrics: {sample_player['total_metrics']}")
            logger.info(f"📊 Sample metrics: {list(sample_player['metrics'].items())[:5]}")
        
        # Save results
        with open('final_working_data.json', 'w') as f:
            json.dump(final_data, f, indent=2)
        
        logger.info("✅ Results saved to final_working_data.json")
    else:
        logger.error("❌ FAILED! Final mapping failed!")

if __name__ == "__main__":
    main()