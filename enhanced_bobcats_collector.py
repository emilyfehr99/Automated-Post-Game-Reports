#!/usr/bin/env python3
"""
Enhanced Bobcats data collector with scrolling to get ALL 136+ metrics
"""

import sqlite3
import json
import logging
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_enhanced_bobcats_data():
    """Collect Lloydminster Bobcats data with ALL metrics"""
    try:
        logger.info("🏒 Collecting ENHANCED Lloydminster Bobcats data...")
        
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
        
        # Navigate to team page
        team_url = f"https://app.hudl.com/instat/hockey/teams/21479"
        scraper.driver.get(team_url)
        time.sleep(5)
        
        # Find and click on SKATERS tab
        skaters_tab = scraper.wait.until(scraper.driver.find_element(By.XPATH, "//a[contains(text(), 'SKATERS') or contains(text(), 'Skaters')]"))
        skaters_tab.click()
        time.sleep(3)
        
        # Scroll to load ALL data
        logger.info("📜 Scrolling to load ALL 136+ metrics...")
        scroll_to_load_all_data(scraper.driver)
        
        # Extract data after scrolling
        logger.info("📊 Extracting ALL metrics after scrolling...")
        result = scraper.extract_structured_data()
        
        if not result or 'players' not in result:
            logger.error("❌ Failed to extract data")
            return False
        
        players = result['players']
        logger.info(f"✅ Found {len(players)} players with {result['total_metrics']} metrics each")
        
        # Connect to database
        conn = sqlite3.connect('ajhl_comprehensive.db')
        cursor = conn.cursor()
        
        # Clear old Bobcats data
        cursor.execute("DELETE FROM players WHERE team_id = '21479'")
        cursor.execute("DELETE FROM teams WHERE team_id = '21479'")
        conn.commit()
        
        # Insert Bobcats team data
        cursor.execute("""
            INSERT INTO teams (team_id, team_name, city, province, hudl_team_id, is_active, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "21479",
            "Lloydminster Bobcats",
            "Lloydminster",
            "AB",
            "21479",
            True,
            datetime.now().isoformat()
        ))
        
        # Insert player data with ALL metrics
        for player in players:
            cursor.execute("""
                INSERT INTO players (player_id, team_id, name, position, metrics, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                f"{player.get('name', '').lower().replace(' ', '_')}_21479",
                "21479",
                player.get('name', ''),
                player.get('position', ''),
                json.dumps(player),  # Store as JSON
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"🎉 Enhanced Bobcats data collection complete!")
        logger.info(f"📊 Players: {len(players)}")
        logger.info(f"📊 Total Metrics: {result['total_metrics']}")
        
        # Show sample player with ALL metrics
        if players:
            sample_player = players[0]
            logger.info("📋 SAMPLE PLAYER WITH ALL METRICS:")
            logger.info("=" * 80)
            logger.info(f"Jersey: {sample_player.get('jersey_number', 'N/A')}")
            logger.info(f"Name: {sample_player.get('name', 'Unknown')}")
            logger.info(f"Position: {sample_player.get('position', 'Unknown')}")
            logger.info("All Metrics:")
            for key, value in sample_player.items():
                if key not in ['jersey_number', 'name', 'position']:
                    logger.info(f"  {key}: {value}")
            logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced data collection failed: {e}")
        return False
    finally:
        if 'scraper' in locals() and scraper.driver:
            scraper.driver.quit()

def scroll_to_load_all_data(driver):
    """Scroll through the page to load all dynamic content"""
    try:
        # Get initial page height
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        # Scroll down multiple times to trigger lazy loading
        for i in range(20):  # Scroll 20 times
            logger.info(f"📜 Scroll {i+1}/20...")
            
            # Scroll to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Scroll back up a bit to trigger more loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")
            time.sleep(1)
            
            # Check if new content loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                logger.info("📜 No new content loaded, continuing...")
            else:
                logger.info(f"📜 New content loaded! Height: {last_height} -> {new_height}")
                last_height = new_height
            
            # Try to find and click "Load More" or similar buttons
            try:
                load_more_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Load More') or contains(text(), 'Show More') or contains(text(), 'View All')]")
                for button in load_more_buttons:
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        time.sleep(2)
                        logger.info("📜 Clicked load more button")
            except:
                pass
            
            # Try to find horizontal scroll elements and scroll them
            try:
                horizontal_scrolls = driver.find_elements(By.CSS_SELECTOR, "[style*='overflow-x: auto'], [style*='overflow-x: scroll']")
                for scroll_element in horizontal_scrolls:
                    driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollWidth;", scroll_element)
                    time.sleep(0.5)
            except:
                pass
        
        # Final scroll to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        logger.info("✅ Scrolling complete!")
        
    except Exception as e:
        logger.error(f"❌ Scrolling error: {e}")

if __name__ == "__main__":
    collect_enhanced_bobcats_data()
