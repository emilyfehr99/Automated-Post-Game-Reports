#!/usr/bin/env python3
"""
Fix Metrics Extraction Script
Properly extracts player metrics from the players table and saves them to comprehensive_metrics
"""

import sqlite3
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_metrics_extraction():
    """Fix the metrics extraction and save properly to comprehensive_metrics table"""
    try:
        conn = sqlite3.connect('ajhl_comprehensive.db')
        cursor = conn.cursor()
        
        logger.info("🔧 Starting metrics extraction fix...")
        
        # Get all players with their metrics
        cursor.execute("SELECT player_id, name, metrics FROM players WHERE metrics IS NOT NULL")
        players = cursor.fetchall()
        
        logger.info(f"Found {len(players)} players with metrics data")
        
        # Clear existing comprehensive_metrics data
        cursor.execute("DELETE FROM comprehensive_metrics")
        logger.info("✅ Cleared existing comprehensive_metrics data")
        
        total_metrics_saved = 0
        
        for player_id, name, metrics_json in players:
            try:
                # Parse the metrics JSON
                metrics = json.loads(metrics_json)
                
                logger.info(f"Processing player: {name} (ID: {player_id})")
                
                # Extract metrics from the JSON structure
                player_metrics = {}
                
                # Handle different JSON structures
                if isinstance(metrics, dict):
                    # Look for metrics in different possible locations
                    if 'params' in metrics:
                        player_metrics = metrics['params']
                    elif 'metrics' in metrics:
                        player_metrics = metrics['metrics']
                    else:
                        # Use the metrics dict directly if it contains metric data
                        # Filter out non-metric fields
                        exclude_fields = ['player_id', 'name', 'name_eng', 'jersey_number', 'position']
                        player_metrics = {k: v for k, v in metrics.items() if k not in exclude_fields}
                
                # Save each metric to comprehensive_metrics table
                for metric_name, metric_value in player_metrics.items():
                    if metric_name and metric_value is not None and str(metric_value).strip() != '':
                        cursor.execute('''
                            INSERT INTO comprehensive_metrics 
                            (team_id, player_id, metric_name, metric_value, metric_type, discovered_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            '21479',  # Team ID
                            player_id,
                            metric_name,
                            str(metric_value),
                            'comprehensive',
                            datetime.now().isoformat()
                        ))
                        total_metrics_saved += 1
                
                logger.info(f"✅ Saved {len(player_metrics)} metrics for {name}")
                
            except Exception as e:
                logger.error(f"❌ Error processing player {player_id}: {e}")
                continue
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        logger.info(f"🎉 Metrics extraction fix completed!")
        logger.info(f"📊 Total metrics saved: {total_metrics_saved}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in metrics extraction fix: {e}")
        return False

def verify_fix():
    """Verify that the fix worked correctly"""
    try:
        conn = sqlite3.connect('ajhl_comprehensive.db')
        cursor = conn.cursor()
        
        # Check total metrics count
        cursor.execute("SELECT COUNT(*) FROM comprehensive_metrics")
        total_metrics = cursor.fetchone()[0]
        
        # Check metrics per player
        cursor.execute("""
            SELECT player_id, COUNT(*) as metric_count 
            FROM comprehensive_metrics 
            GROUP BY player_id 
            ORDER BY metric_count DESC 
            LIMIT 10
        """)
        top_players = cursor.fetchall()
        
        # Check sample metrics
        cursor.execute("""
            SELECT player_id, metric_name, metric_value 
            FROM comprehensive_metrics 
            WHERE metric_value != 'N/A' 
            ORDER BY discovered_at DESC 
            LIMIT 10
        """)
        sample_metrics = cursor.fetchall()
        
        print("🔍 VERIFICATION RESULTS:")
        print("=" * 40)
        print(f"📊 Total metrics in database: {total_metrics}")
        print()
        print("👥 Top players by metric count:")
        for player_id, count in top_players:
            print(f"  • {player_id}: {count} metrics")
        print()
        print("📋 Sample metrics with values:")
        for player_id, metric_name, metric_value in sample_metrics:
            print(f"  • {player_id} - {metric_name}: {metric_value}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying fix: {e}")
        return False

if __name__ == "__main__":
    print("🔧 FIXING METRICS EXTRACTION...")
    print("=" * 50)
    
    # Run the fix
    if fix_metrics_extraction():
        print("✅ Fix completed successfully!")
        
        # Verify the fix
        print("\n🔍 Verifying fix...")
        verify_fix()
    else:
        print("❌ Fix failed!")
