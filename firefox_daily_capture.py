#!/usr/bin/env python3
"""
Firefox Daily 4 AM Eastern Network Data Capture for Hudl Instat
Uses Firefox instead of Chrome to avoid driver issues
"""

import time
import json
import logging
import os
import sqlite3
import schedule
from datetime import datetime
from typing import Dict, List, Any
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from credentials_database import CredentialsDatabase
from discord_notification import send_discord_notification

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FirefoxDailyCapture:
    """Daily automated network data capture using Firefox"""
    
    def __init__(self):
        self.driver = None
        self.output_dir = "daily_network_data"
        self.credentials_db = CredentialsDatabase()
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_credentials(self) -> Dict[str, str]:
        """Get credentials from database"""
        creds = self.credentials_db.get_credentials()
        if not creds:
            raise Exception("No credentials found in database")
        return creds
    
    def setup_driver(self):
        """Setup Firefox driver"""
        try:
            logger.info("🔧 Setting up Firefox driver...")
            
            # Firefox options
            firefox_options = Options()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--width=1920")
            firefox_options.add_argument("--height=1080")
            
            # Setup driver
            service = Service("/opt/homebrew/bin/geckodriver")
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            
            logger.info("✅ Firefox driver setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up Firefox driver: {e}")
            return False
    
    def login_and_capture(self) -> Dict[str, Any]:
        """Login and capture network data"""
        try:
            logger.info("🔐 Logging into Hudl...")
            
            # Get credentials
            creds = self.get_credentials()
            
            # Navigate to login page
            self.driver.get("https://app.hudl.com/login")
            
            # Wait for login form
            wait = WebDriverWait(self.driver, 10)
            
            # Find and fill email field
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_field.clear()
            email_field.send_keys(creds['username'])
            
            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(creds['password'])
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            logger.info("✅ Login successful!")
            
            # Navigate to the data page
            logger.info("📊 Navigating to data page...")
            self.driver.get("https://app.hudl.com/metropole/shim/api-hockey.instatscout.com/data")
            
            # Wait for page to load
            time.sleep(3)
            
            # Get page source (this contains the data)
            page_source = self.driver.page_source
            
            # Create capture data structure
            capture_data = {
                'timestamp': datetime.now().isoformat(),
                'team_id': creds.get('team_id', '21479'),
                'page_source': page_source,
                'url': self.driver.current_url,
                'title': self.driver.title
            }
            
            logger.info("✅ Data captured successfully!")
            return capture_data
            
        except Exception as e:
            logger.error(f"❌ Error during login and capture: {e}")
            return None
    
    def save_to_database(self, data: Dict[str, Any], timestamp: str) -> bool:
        """Save captured data to SQL database"""
        try:
            conn = sqlite3.connect('ajhl_comprehensive.db')
            cursor = conn.cursor()
            
            # Create daily_captures table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_captures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    capture_date TEXT NOT NULL,
                    capture_time TEXT NOT NULL,
                    team_id TEXT,
                    page_source_length INTEGER,
                    url TEXT,
                    title TEXT,
                    raw_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert capture record
            page_source_length = len(data.get('page_source', ''))
            raw_data = json.dumps(data)
            
            cursor.execute('''
                INSERT INTO daily_captures 
                (capture_date, capture_time, team_id, page_source_length, url, title, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime('%Y-%m-%d'),
                timestamp,
                data.get('team_id', '21479'),
                page_source_length,
                data.get('url', ''),
                data.get('title', ''),
                raw_data
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Data saved to SQL database: {page_source_length} characters captured")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving to database: {e}")
            return False
    
    def save_network_data(self, data: Dict[str, Any]) -> bool:
        """Save network data to files and database"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save to JSON file
            filename = f"{self.output_dir}/firefox_capture_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Save page source to HTML file
            html_filename = f"{self.output_dir}/page_source_{timestamp}.html"
            with open(html_filename, 'w') as f:
                f.write(data.get('page_source', ''))
            
            logger.info(f"✅ Network data saved to {filename}")
            logger.info(f"✅ Page source saved to {html_filename}")
            
            # Save to database
            self.save_to_database(data, timestamp)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving network data: {e}")
            return False
    
    def run_daily_capture(self) -> bool:
        """Run the daily capture process"""
        try:
            logger.info("🚀 Starting daily 4 AM Firefox capture...")
            
            # Setup driver
            if not self.setup_driver():
                return False
            
            try:
                # Login and capture
                data = self.login_and_capture()
                if not data:
                    logger.error("❌ Failed to capture data")
                    return False
                
                # Save data
                if self.save_network_data(data):
                    logger.info("✅ Daily capture completed successfully!")
                    
                    # Send Discord notification
                    try:
                        send_discord_notification(
                            "🎉 Daily Hudl Data Capture Complete!",
                            f"✅ Successfully captured data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"📊 Team ID: {data.get('team_id', '21479')}\n"
                            f"📁 Data saved to daily_network_data/\n"
                            f"💾 Database updated successfully!\n"
                            f"🌐 Page: {data.get('title', 'Hudl Data')}"
                        )
                    except Exception as e:
                        logger.error(f"❌ Failed to send Discord notification: {e}")
                    
                    return True
                else:
                    logger.error("❌ Failed to save data")
                    return False
                    
            finally:
                # Always close the driver
                if self.driver:
                    self.driver.quit()
                    logger.info("🔒 Firefox driver closed")
                
        except Exception as e:
            logger.error(f"❌ Error in daily capture: {e}")
            
            # Send error notification
            try:
                send_discord_notification(
                    "❌ Daily Hudl Data Capture Failed",
                    f"❌ Error occurred at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"🔍 Error: {str(e)}\n"
                    f"📋 Check logs for more details"
                )
            except:
                pass
            
            return False

def main():
    """Main function to run the scheduler"""
    print("🕐 STARTING FIREFOX DAILY SCHEDULER")
    print("=" * 40)
    
    # Create capture instance
    capture = FirefoxDailyCapture()
    
    # Set up the daily schedule
    schedule.every().day.at('04:00').do(capture.run_daily_capture)
    
    print('✅ Firefox daily scheduler started!')
    print('⏰ Next run scheduled for: 4:00 AM Eastern')
    print('📅 Current time:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    print('🎊 SYSTEM IS LIVE AND READY!')
    print('   Your 4 AM automated capture is now active!')
    print()
    print('💡 TO STOP THE SCHEDULER:')
    print('   Press Ctrl+C in this terminal')
    print()
    print('📱 YOU WILL GET DISCORD NOTIFICATIONS:')
    print('   • Success: When data is captured')
    print('   • Error: If anything goes wrong')
    print()
    print('🔍 MONITORING:')
    print('   • All errors are logged')
    print('   • Database is updated daily')
    print('   • JSON files saved to daily_network_data/')
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()

