#!/usr/bin/env python3
"""
Create detailed players table with individual columns for each metric
"""

import sqlite3
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_detailed_players_table():
    """Create a new table with individual columns for each metric"""
    try:
        # Connect to database
        conn = sqlite3.connect('ajhl_comprehensive.db')
        cursor = conn.cursor()
        
        # Create new detailed players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players_detailed (
                player_id VARCHAR PRIMARY KEY,
                team_id VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                position VARCHAR,
                jersey_number VARCHAR,
                gp VARCHAR,
                shifts VARCHAR,
                goals VARCHAR,
                a1 VARCHAR,
                a2 VARCHAR,
                assists VARCHAR,
                points VARCHAR,
                plus_minus VARCHAR,
                sc VARCHAR,
                pea VARCHAR,
                pen VARCHAR,
                fo VARCHAR,
                fo_plus VARCHAR,
                fo_percent VARCHAR,
                h_plus VARCHAR,
                shots VARCHAR,
                shots_plus VARCHAR,
                sbl VARCHAR,
                spp VARCHAR,
                ssh VARCHAR,
                ptts VARCHAR,
                fod VARCHAR,
                fod_plus VARCHAR,
                fod_percent VARCHAR,
                fon VARCHAR,
                fon_plus VARCHAR,
                fon_percent VARCHAR,
                foa VARCHAR,
                foa_plus VARCHAR,
                foa_percent VARCHAR,
                last_updated DATETIME
            )
        """)
        
        # Get all players from original table
        cursor.execute("SELECT * FROM players")
        players = cursor.fetchall()
        
        logger.info(f"Found {len(players)} players to migrate")
        
        # Clear existing detailed table
        cursor.execute("DELETE FROM players_detailed")
        
        # Migrate each player
        for player in players:
            player_id, team_id, jersey_number, name, position, metrics_json, last_updated = player
            
            try:
                metrics = json.loads(metrics_json)
                
                # Insert into detailed table
                cursor.execute("""
                    INSERT INTO players_detailed (
                        player_id, team_id, name, position, jersey_number, gp, shifts,
                        goals, a1, a2, assists, points, plus_minus, sc, pea, pen,
                        fo, fo_plus, fo_percent, h_plus, shots, shots_plus, sbl,
                        spp, ssh, ptts, fod, fod_plus, fod_percent, fon, fon_plus,
                        fon_percent, foa, foa_plus, foa_percent, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    player_id,
                    team_id,
                    name,
                    position,
                    metrics.get('jersey_number', ''),
                    metrics.get('GP', ''),
                    metrics.get('SHIFTS', ''),
                    metrics.get('G', ''),
                    metrics.get('A1', ''),
                    metrics.get('A2', ''),
                    metrics.get('A', ''),
                    metrics.get('P', ''),
                    metrics.get('+ / -', ''),
                    metrics.get('SC', ''),
                    metrics.get('PEA', ''),
                    metrics.get('PEN', ''),
                    metrics.get('FO', ''),
                    metrics.get('FO+', ''),
                    metrics.get('FO%', ''),
                    metrics.get('H+', ''),
                    metrics.get('S', ''),
                    metrics.get('S+', ''),
                    metrics.get('SBL', ''),
                    metrics.get('SPP', ''),
                    metrics.get('SSH', ''),
                    metrics.get('PTTS', ''),
                    metrics.get('FOD', ''),
                    metrics.get('FOD+', ''),
                    metrics.get('FOD%', ''),
                    metrics.get('FON', ''),
                    metrics.get('FON+', ''),
                    metrics.get('FON%', ''),
                    metrics.get('FOA', ''),
                    metrics.get('FOA+', ''),
                    metrics.get('FOA%', ''),
                    last_updated
                ))
                
            except Exception as e:
                logger.error(f"Error processing player {name}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Detailed players table created successfully!")
        logger.info("📊 Each metric now has its own column")
        logger.info("🔍 You can now query individual metrics easily")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating detailed table: {e}")
        return False

if __name__ == "__main__":
    create_detailed_players_table()
