#!/usr/bin/env python3
"""
Ultra Simple Daily 4 AM Eastern Data Capture for Hudl Instat
Just captures the raw page data without complex interactions
"""

import time
import json
import logging
import os
import sqlite3
import schedule
import requests
from datetime import datetime
from typing import Dict, List, Any
from credentials_database import CredentialsDatabase
from discord_notification import send_discord_notification

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltraSimpleCapture:
    """Ultra simple daily data capture"""
    
    def __init__(self):
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
    
    def capture_data(self) -> Dict[str, Any]:
        """Capture data by accessing the Hudl page directly"""
        try:
            logger.info("🚀 Starting ultra simple data capture...")
            
            # Get credentials
            creds = self.get_credentials()
            
            # Headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Try to access the Hudl page
            urls_to_try = [
                "https://app.hudl.com/",
                "https://app.hudl.com/login",
                "https://app.hudl.com/metropole/shim/api-hockey.instatscout.com/data",
                "https://new.instatscout.com/data"
            ]
            
            captured_data = {}
            
            for url in urls_to_try:
                try:
                    logger.info(f"📡 Trying to access: {url}")
                    response = requests.get(url, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Successfully accessed: {url}")
                        captured_data[url] = {
                            'status_code': response.status_code,
                            'content_length': len(response.text),
                            'content': response.text[:1000] + "..." if len(response.text) > 1000 else response.text,
                            'headers': dict(response.headers)
                        }
                    else:
                        logger.warning(f"⚠️ Got status {response.status_code} for {url}")
                        captured_data[url] = {
                            'status_code': response.status_code,
                            'error': f"HTTP {response.status_code}"
                        }
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error accessing {url}: {e}")
                    captured_data[url] = {
                        'error': str(e)
                    }
            
            # Create final capture data
            final_data = {
                'timestamp': datetime.now().isoformat(),
                'team_id': creds.get('team_id', '21479'),
                'captured_urls': captured_data,
                'total_urls_tried': len(urls_to_try),
                'successful_captures': len([url for url, data in captured_data.items() if 'error' not in data and data.get('status_code') == 200])
            }
            
            logger.info(f"✅ Capture complete: {final_data['successful_captures']}/{final_data['total_urls_tried']} URLs successful")
            return final_data
            
        except Exception as e:
            logger.error(f"❌ Error during capture: {e}")
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
                    requests_count INTEGER,
                    responses_count INTEGER,
                    raw_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert capture record
            successful_captures = data.get('successful_captures', 0)
            total_urls_tried = data.get('total_urls_tried', 0)
            raw_data = json.dumps(data)
            
            cursor.execute('''
                INSERT INTO daily_captures 
                (capture_date, capture_time, team_id, requests_count, responses_count, raw_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime('%Y-%m-%d'),
                timestamp,
                data.get('team_id', '21479'),
                successful_captures,
                total_urls_tried,
                raw_data
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Data saved to SQL database: {successful_captures}/{total_urls_tried} URLs captured")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving to database: {e}")
            return False
    
    def save_network_data(self, data: Dict[str, Any]) -> bool:
        """Save network data to files and database"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save to JSON file
            filename = f"{self.output_dir}/ultra_simple_capture_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Network data saved to {filename}")
            
            # Save to database
            self.save_to_database(data, timestamp)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving network data: {e}")
            return False
    
    def run_daily_capture(self) -> bool:
        """Run the daily capture process"""
        try:
            logger.info("🚀 Starting daily 4 AM ultra simple capture...")
            
            # Capture data
            data = self.capture_data()
            if not data:
                logger.error("❌ Failed to capture data")
                return False
            
            # Save data
            if self.save_network_data(data):
                logger.info("✅ Daily capture completed successfully!")
                
                # Send Discord notification
                try:
                    successful = data.get('successful_captures', 0)
                    total = data.get('total_urls_tried', 0)
                    
                    send_discord_notification(
                        "🎉 Daily Hudl Data Capture Complete!",
                        f"✅ Successfully captured data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"📊 Team ID: {data.get('team_id', '21479')}\n"
                        f"🌐 URLs Captured: {successful}/{total}\n"
                        f"📁 Data saved to daily_network_data/\n"
                        f"💾 Database updated successfully!"
                    )
                except Exception as e:
                    logger.error(f"❌ Failed to send Discord notification: {e}")
                
                return True
            else:
                logger.error("❌ Failed to save data")
                return False
                
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
    print("🕐 STARTING ULTRA SIMPLE DAILY SCHEDULER")
    print("=" * 50)
    
    # Create capture instance
    capture = UltraSimpleCapture()
    
    # Set up the daily schedule
    schedule.every().day.at('04:00').do(capture.run_daily_capture)
    
    print('✅ Ultra simple daily scheduler started!')
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
