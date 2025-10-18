#!/usr/bin/env python3
"""
Daily Data Collector for AJHL API
Runs at 3:30 AM Eastern to collect fresh data from Hudl
"""

import schedule
import time
import logging
import sqlite3
from datetime import datetime
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper
from ajhl_teams_config import get_all_teams

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_daily_data():
    """Collect fresh data from Hudl and store in database"""
    try:
        logger.info("🌅 Starting daily data collection at 3:30 AM Eastern...")
        
        # Initialize scraper
        scraper = HudlCompleteMetricsScraper()
        scraper.setup_driver()
        
        # Authenticate
        username = "chaserochon777@gmail.com"
        password = "357Chaser!468"
        
        if not scraper.login(username, password):
            logger.error("❌ Authentication failed")
            return False
        
        logger.info("✅ Authentication successful")
        
        # Connect to database
        conn = sqlite3.connect('ajhl_comprehensive.db')
        cursor = conn.cursor()
        
        # Clear old data
        cursor.execute("DELETE FROM players")
        cursor.execute("DELETE FROM teams")
        conn.commit()
        
        # Get all teams
        teams_dict = get_all_teams()
        total_players = 0
        
        # Collect data for each team
        for team_id, team_data in teams_dict.items():
            logger.info(f"🏒 Collecting data for {team_data['team_name']}...")
            
            # Insert team data
            cursor.execute("""
                INSERT INTO teams (team_id, team_name, city, province, hudl_id, active, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                team_id,
                team_data['team_name'],
                team_data['city'],
                team_data['province'],
                team_data['hudl_team_id'],
                team_data['is_active'],
                datetime.now().isoformat()
            ))
            
            # Get players for this team
            players = scraper.get_team_players(team_id)
            
            if players:
                logger.info(f"   ✅ Found {len(players)} players")
                
                # Insert player data
                for player in players:
                    cursor.execute("""
                        INSERT INTO players (player_id, team_id, name, position, metrics, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        f"{player.get('name', '').lower().replace(' ', '_')}_{team_id}",
                        team_id,
                        player.get('name', ''),
                        player.get('position', ''),
                        str(player),  # Store as JSON string
                        datetime.now().isoformat()
                    ))
                    total_players += 1
            else:
                logger.warning(f"   ⚠️ No players found for {team_data['team_name']}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"🎉 Daily data collection complete!")
        logger.info(f"📊 Teams: {len(teams_dict)}")
        logger.info(f"📊 Players: {total_players}")
        logger.info(f"🕐 Completed at: {datetime.now().isoformat()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Daily data collection failed: {e}")
        return False
    finally:
        if 'scraper' in locals() and scraper.driver:
            scraper.driver.quit()

def run_daily_collection():
    """Run the daily collection immediately for testing"""
    logger.info("🧪 Running daily collection now for testing...")
    return collect_daily_data()

if __name__ == "__main__":
    # Schedule daily collection at 3:30 AM Eastern
    schedule.every().day.at("03:30").do(collect_daily_data)
    
    logger.info("⏰ Daily data collector scheduled for 3:30 AM Eastern")
    logger.info("🔄 Running initial collection now...")
    
    # Run initial collection
    run_daily_collection()
    
    # Keep running to check schedule
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
