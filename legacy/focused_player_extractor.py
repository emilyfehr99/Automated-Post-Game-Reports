#!/usr/bin/env python3
"""
Focused Player Data Extractor
Extracts specific player data like Caden Steinke from the HTML structure
"""

import re
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_specific_player_data():
    """Extract specific player data from the HTML structure"""
    try:
        logger.info("🔍 Extracting specific player data...")
        
        with open('hudl-scraping/textfile.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the specific pattern you showed me
        # <div role="row" class="Table__TableRow-sc-2etlst-3 RNiTu" style="position: absolute; left: 0px; top: 420px; height: 30px; width: auto; min-width: 100%;">
        # <div role="cell" class="Table__TableCell-sc-2etlst-5 gPUYuB"><a class="styled__PLayerNavLink-sc-r181ky-0 cVkPVn" href="/instat/hockey/players/587037" target="_blank"><span class="styled__PlayerNumber-sc-r181ky-3 bOpdrm">27</span><span class="styled__PlayerName-sc-r181ky-2 kgrDyf">Caden Steinke</span></a></div>
        
        # Pattern to match player rows with specific structure
        player_row_pattern = r'<div role="row"[^>]*style="position: absolute; left: 0px; top: (\d+)px[^>]*>.*?</div>'
        player_rows = re.findall(player_row_pattern, content, re.DOTALL)
        
        logger.info(f"📊 Found {len(player_rows)} player rows with position styling")
        
        # Extract all player rows
        all_player_rows = re.findall(r'<div role="row"[^>]*>.*?</div>', content, re.DOTALL)
        logger.info(f"📊 Found {len(all_player_rows)} total player rows")
        
        players = []
        for i, row in enumerate(all_player_rows):
            # Look for player link pattern
            player_link_match = re.search(r'href="/instat/hockey/players/(\d+)"[^>]*>.*?<span[^>]*>(\d+)</span><span[^>]*>([^<]+)</span>', row)
            
            if player_link_match:
                player_id = player_link_match.group(1)
                jersey_number = player_link_match.group(2)
                player_name = player_link_match.group(3)
                
                # Extract all cell values from this row
                # Look for both patterns: <div role="cell" class="Table__TableCell-sc-2etlst-5 eLdYbn">value</div>
                # and <div role="cell" class="Table__TableCell-sc-2etlst-5 gPUYuB">value</div>
                
                cell_values = []
                
                # Pattern 1: eLdYbn class cells
                eLdYbn_cells = re.findall(r'<div role="cell"[^>]*class="[^"]*eLdYbn[^"]*"[^>]*>([^<]*)</div>', row)
                cell_values.extend(eLdYbn_cells)
                
                # Pattern 2: gPUYuB class cells (but not the player name cell)
                gPUYuB_cells = re.findall(r'<div role="cell"[^>]*class="[^"]*gPUYuB[^"]*"[^>]*>([^<]*)</div>', row)
                # Filter out the player name cell
                gPUYuB_cells = [cell for cell in gPUYuB_cells if cell.strip() and not cell.strip().isdigit() and len(cell.strip()) > 1]
                cell_values.extend(gPUYuB_cells)
                
                # Pattern 3: NEqXp class cells (position)
                NEqXp_cells = re.findall(r'<div role="cell"[^>]*class="[^"]*NEqXp[^"]*"[^>]*>([^<]*)</div>', row)
                cell_values.extend(NEqXp_cells)
                
                # Clean up values
                cell_values = [v.strip() for v in cell_values if v.strip()]
                
                player_data = {
                    'player_id': player_id,
                    'jersey_number': jersey_number,
                    'player_name': player_name,
                    'metric_values': cell_values,
                    'row_index': i
                }
                
                players.append(player_data)
                
                # Log first few players for debugging
                if i < 5:
                    logger.info(f"📊 Player {i+1}: {player_name} (#{jersey_number}) - {len(cell_values)} values")
                    logger.info(f"   Values: {cell_values[:10]}...")  # Show first 10 values
        
        logger.info(f"✅ Extracted {len(players)} players with metric values")
        return players
        
    except Exception as e:
        logger.error(f"❌ Error extracting specific player data: {e}")
        return []

def main():
    """Main function"""
    players = extract_specific_player_data()
    
    if players:
        logger.info(f"🎉 SUCCESS! Extracted {len(players)} players!")
        
        # Show sample data
        for i, player in enumerate(players[:3]):
            logger.info(f"📊 Player {i+1}: {player['player_name']} (#{player['jersey_number']})")
            logger.info(f"   Metric values: {len(player['metric_values'])}")
            logger.info(f"   Sample values: {player['metric_values'][:5]}")
        
        # Save results
        with open('focused_player_data.json', 'w') as f:
            json.dump(players, f, indent=2)
        
        logger.info("✅ Results saved to focused_player_data.json")
    else:
        logger.error("❌ FAILED! No players extracted!")

if __name__ == "__main__":
    main()
