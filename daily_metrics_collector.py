#!/usr/bin/env python3
"""
Daily metrics collector for Lloydminster Bobcats
Collects all 104+ metrics discovered through enhanced scrolling
Runs daily at 3:30 AM Eastern
"""

import time
import logging
import schedule
import sqlite3
from datetime import datetime, timezone
from selenium.webdriver.common.by import By
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper
from bobcats_data_collector import scroll_table_horizontally, extract_metrics_at_scroll_position

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_metrics_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database connection
DB_PATH = "ajhl_comprehensive.db"

def create_comprehensive_metrics_table():
    """Create table for comprehensive metrics if it doesn't exist"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create comprehensive metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comprehensive_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id TEXT NOT NULL,
                player_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value TEXT,
                metric_type TEXT,
                scroll_position INTEGER,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(team_id, player_id, metric_name, scroll_position)
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_comprehensive_metrics 
            ON comprehensive_metrics(team_id, player_id, metric_name)
        """)
        
        conn.commit()
        conn.close()
        logger.info("✅ Comprehensive metrics table created/verified")
        
    except Exception as e:
        logger.error(f"❌ Error creating comprehensive metrics table: {e}")

def collect_comprehensive_metrics():
    """Collect all 104+ metrics using enhanced scrolling"""
    try:
        logger.info("🏒 Starting comprehensive metrics collection...")
        
        # Initialize scraper
        scraper = HudlCompleteMetricsScraper()
        scraper.setup_driver()
        
        # Login
        username = "chaserochon777@gmail.com"
        password = "357Chaser!468"
        
        if not scraper.login(username, password):
            logger.error("❌ Login failed")
            return False
        
        # Navigate to SKATERS tab
        if not scraper.navigate_to_skaters_tab("21479"):
            logger.error("❌ Failed to navigate to SKATERS tab")
            return False
        
        # Get initial player data
        players = scraper.get_team_players("21479")
        if not players:
            logger.error("❌ No players found")
            return False
        
        logger.info(f"✅ Found {len(players)} players")
        
        # Enhanced scrolling to get all metrics
        logger.info("📜 Starting enhanced scrolling for comprehensive metrics...")
        scroll_table_horizontally(scraper.driver)
        
        # Extract all metrics after scrolling
        all_metrics = extract_all_metrics_after_scrolling(scraper.driver)
        
        if all_metrics:
            logger.info(f"🎉 Found {len(all_metrics)} comprehensive metrics!")
            
            # Save comprehensive metrics to database
            save_comprehensive_metrics_to_db("21479", players, all_metrics)
            
            logger.info("✅ Comprehensive metrics collection complete!")
            return True
        else:
            logger.error("❌ No comprehensive metrics found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in comprehensive metrics collection: {e}")
        return False
    finally:
        if 'scraper' in locals() and scraper.driver:
            scraper.driver.quit()

def extract_all_metrics_after_scrolling(driver):
    """Extract ALL metrics after horizontal scrolling"""
    try:
        logger.info("📊 Extracting ALL metrics after horizontal scrolling...")
        
        all_metrics = set()
        
        # Get all column headers from the table
        column_headers = driver.find_elements(By.CSS_SELECTOR, "[role='columnheader']")
        for header in column_headers:
            text = header.text.strip()
            if text and len(text) > 1 and text not in ['', 'PLAYER', 'POS', 'TOI']:
                all_metrics.add(text)
        
        # Get all table headers
        table_headers = driver.find_elements(By.CSS_SELECTOR, "th, .header, [class*='header']")
        for header in table_headers:
            text = header.text.strip()
            if text and len(text) > 1 and text not in ['', 'PLAYER', 'POS', 'TOI']:
                all_metrics.add(text)
        
        # Get all data attributes
        data_elements = driver.find_elements(By.CSS_SELECTOR, "[data-metric], [data-field], [data-column], [data-lexic]")
        for element in data_elements:
            for attr in ['data-metric', 'data-field', 'data-column', 'data-lexic']:
                value = element.get_attribute(attr)
                if value:
                    all_metrics.add(value)
        
        # Get all text content and extract potential metrics
        page_text = driver.page_source
        
        # Look for patterns that might indicate metrics
        import re
        
        # Look for metric patterns in the HTML
        metric_patterns = [
            r'data-lexic="(\d+)"',  # From JS analysis
            r'class="[^"]*metric[^"]*"',
            r'class="[^"]*stat[^"]*"',
            r'data-field="([^"]+)"',
            r'data-column="([^"]+)"',
            r'data-testid="([^"]+)"',
            r'aria-label="([^"]+)"'
        ]
        
        for pattern in metric_patterns:
            matches = re.findall(pattern, page_text)
            for match in matches:
                if isinstance(match, str) and len(match) > 1:
                    all_metrics.add(match)
        
        logger.info(f"📊 Total unique metrics found: {len(all_metrics)}")
        return sorted(list(all_metrics))
        
    except Exception as e:
        logger.error(f"❌ Error extracting all metrics: {e}")
        return None

def save_comprehensive_metrics_to_db(team_id, players, all_metrics):
    """Save comprehensive metrics to database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Clear existing comprehensive metrics for this team
        cursor.execute("DELETE FROM comprehensive_metrics WHERE team_id = ?", (team_id,))
        
        # Insert comprehensive metrics
        metrics_inserted = 0
        
        for player in players:
            player_id = player.get('player_id', f"player_{player.get('jersey_number', 'unknown')}")
            
            for metric in all_metrics:
                try:
                    cursor.execute("""
                        INSERT INTO comprehensive_metrics 
                        (team_id, player_id, metric_name, metric_value, metric_type, scroll_position)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        team_id,
                        player_id,
                        metric,
                        player.get(metric, 'N/A'),
                        'comprehensive',
                        0
                    ))
                    metrics_inserted += 1
                except Exception as e:
                    logger.debug(f"Error inserting metric {metric} for player {player_id}: {e}")
                    continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Saved {metrics_inserted} comprehensive metrics to database")
        
    except Exception as e:
        logger.error(f"❌ Error saving comprehensive metrics to database: {e}")

def get_comprehensive_metrics_summary():
    """Get summary of comprehensive metrics in database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get total metrics count
        cursor.execute("SELECT COUNT(DISTINCT metric_name) FROM comprehensive_metrics")
        total_metrics = cursor.fetchone()[0]
        
        # Get metrics by type
        cursor.execute("""
            SELECT metric_type, COUNT(DISTINCT metric_name) 
            FROM comprehensive_metrics 
            GROUP BY metric_type
        """)
        metrics_by_type = cursor.fetchall()
        
        # Get latest collection time
        cursor.execute("""
            SELECT MAX(discovered_at) 
            FROM comprehensive_metrics
        """)
        latest_collection = cursor.fetchone()[0]
        
        conn.close()
        
        logger.info(f"📊 Comprehensive Metrics Summary:")
        logger.info(f"  Total unique metrics: {total_metrics}")
        logger.info(f"  Metrics by type: {dict(metrics_by_type)}")
        logger.info(f"  Latest collection: {latest_collection}")
        
        return {
            'total_metrics': total_metrics,
            'metrics_by_type': dict(metrics_by_type),
            'latest_collection': latest_collection
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting comprehensive metrics summary: {e}")
        return None

def run_daily_collection():
    """Run daily collection at 3:30 AM Eastern"""
    try:
        logger.info("🌅 Starting daily comprehensive metrics collection...")
        
        # Create table if needed
        create_comprehensive_metrics_table()
        
        # Collect comprehensive metrics
        success = collect_comprehensive_metrics()
        
        if success:
            # Get summary
            summary = get_comprehensive_metrics_summary()
            if summary:
                logger.info(f"✅ Daily collection complete! Found {summary['total_metrics']} metrics")
            else:
                logger.info("✅ Daily collection complete!")
        else:
            logger.error("❌ Daily collection failed")
            
    except Exception as e:
        logger.error(f"❌ Error in daily collection: {e}")

def main():
    """Main function to set up daily collection"""
    try:
        logger.info("🚀 Starting Daily Comprehensive Metrics Collector...")
        
        # Create table
        create_comprehensive_metrics_table()
        
        # Schedule daily collection at 3:30 AM Eastern
        schedule.every().day.at("03:30").do(run_daily_collection)
        
        # Run initial collection
        logger.info("🔄 Running initial collection...")
        run_daily_collection()
        
        # Keep running
        logger.info("⏰ Daily collector running... Press Ctrl+C to stop")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("🛑 Daily collector stopped by user")
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main()
