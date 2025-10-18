#!/usr/bin/env python3
"""
Fix players table with individual columns for each metric
"""

import sqlite3
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_players_table():
    """Add individual columns for each metric to the existing players table"""
    try:
        # Connect to database
        conn = sqlite3.connect('ajhl_comprehensive.db')
        cursor = conn.cursor()
        
        # Add individual metric columns to existing players table
        metric_columns = [
            "jersey_number VARCHAR",
            "gp VARCHAR", 
            "shifts VARCHAR",
            "goals VARCHAR",
            "a1 VARCHAR",
            "a2 VARCHAR", 
            "assists VARCHAR",
            "points VARCHAR",
            "plus_minus VARCHAR",
            "sc VARCHAR",
            "pea VARCHAR",
            "pen VARCHAR",
            "fo VARCHAR",
            "fo_plus VARCHAR",
            "fo_percent VARCHAR",
            "h_plus VARCHAR",
            "shots VARCHAR",
            "shots_plus VARCHAR",
            "sbl VARCHAR",
            "spp VARCHAR",
            "ssh VARCHAR",
            "ptts VARCHAR",
            "fod VARCHAR",
            "fod_plus VARCHAR",
            "fod_percent VARCHAR",
            "fon VARCHAR",
            "fon_plus VARCHAR",
            "fon_percent VARCHAR",
            "foa VARCHAR",
            "foa_plus VARCHAR",
            "foa_percent VARCHAR"
        ]
        
        # Add each column
        for column in metric_columns:
            try:
                cursor.execute(f"ALTER TABLE players ADD COLUMN {column}")
                logger.info(f"Added column: {column}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info(f"Column already exists: {column}")
                else:
                    logger.error(f"Error adding column {column}: {e}")
        
        # Update the new columns with data from JSON
        cursor.execute("SELECT player_id, metrics FROM players")
        players = cursor.fetchall()
        
        for player_id, metrics_json in players:
            try:
                metrics = json.loads(metrics_json)
                
                # Update the player with individual metric values
                cursor.execute("""
                    UPDATE players SET
                        jersey_number = ?,
                        gp = ?,
                        shifts = ?,
                        goals = ?,
                        a1 = ?,
                        a2 = ?,
                        assists = ?,
                        points = ?,
                        plus_minus = ?,
                        sc = ?,
                        pea = ?,
                        pen = ?,
                        fo = ?,
                        fo_plus = ?,
                        fo_percent = ?,
                        h_plus = ?,
                        shots = ?,
                        shots_plus = ?,
                        sbl = ?,
                        spp = ?,
                        ssh = ?,
                        ptts = ?,
                        fod = ?,
                        fod_plus = ?,
                        fod_percent = ?,
                        fon = ?,
                        fon_plus = ?,
                        fon_percent = ?,
                        foa = ?,
                        foa_plus = ?,
                        foa_percent = ?
                    WHERE player_id = ?
                """, (
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
                    player_id
                ))
                
            except Exception as e:
                logger.error(f"Error updating player {player_id}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Players table updated with individual metric columns!")
        logger.info("📊 Each metric now has its own column")
        logger.info("🔍 You can now query individual metrics easily")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating players table: {e}")
        return False

if __name__ == "__main__":
    fix_players_table()
