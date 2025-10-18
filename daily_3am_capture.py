#!/usr/bin/env python3
"""
Daily 4 AM Eastern Network Data Capture for Hudl Instat
Automatically captures network data every day at 4 AM Eastern
Exactly like your manual process but automated!
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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from credentials_database import CredentialsDatabase
from discord_notification import send_discord_notification
from error_monitoring_system import ErrorMonitoringSystem

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DailyNetworkCapture:
    """Daily automated network data capture"""
    
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
        """Setup Chrome driver"""
        try:
            logger.info("🔧 Setting up Chrome driver...")
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-images")  # Faster loading
            
            # Use system-installed chromedriver
            service = Service("/opt/homebrew/bin/chromedriver")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("✅ Chrome driver setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up driver: {e}")
            return False
    
    def login_and_navigate(self) -> bool:
        """Login and navigate to team data page"""
        try:
            logger.info("🔐 Logging in and navigating to team data...")
            
            # Get credentials from database
            creds = self.get_credentials()
            username = creds['username']
            password = creds['password']
            team_id = creds['team_id']
            
            # Navigate to login page
            self.driver.get("https://app.hudl.com/login")
            time.sleep(3)
            
            # Login
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            email_field.clear()
            email_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            time.sleep(5)
            
            # Navigate to team page
            team_url = f"https://app.hudl.com/instat/hockey/teams/{team_id}"
            self.driver.get(team_url)
            time.sleep(5)
            
            logger.info("✅ Login and navigation successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Login/navigation error: {e}")
            return False
    
    def capture_network_data(self) -> Dict[str, Any]:
        """Capture network data using JavaScript"""
        try:
            logger.info("📡 Capturing network data...")
            
            # JavaScript to capture network requests
            capture_script = """
            // Capture all network requests
            const networkData = {
                timestamp: new Date().toISOString(),
                requests: [],
                responses: []
            };
            
            // Override fetch to capture requests
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                const options = args[1] || {};
                
                // Log the request
                networkData.requests.push({
                    url: url,
                    method: options.method || 'GET',
                    headers: options.headers || {},
                    body: options.body || null
                });
                
                // Make the actual request
                return originalFetch.apply(this, args)
                    .then(response => {
                        // Clone the response to read it
                        const clonedResponse = response.clone();
                        
                        // Try to read the response body
                        clonedResponse.text().then(text => {
                            try {
                                const jsonData = JSON.parse(text);
                                networkData.responses.push({
                                    url: url,
                                    status: response.status,
                                    data: jsonData
                                });
                            } catch (e) {
                                // Not JSON, store as text
                                networkData.responses.push({
                                    url: url,
                                    status: response.status,
                                    data: text
                                });
                            }
                        }).catch(e => {
                            // Couldn't read response
                            networkData.responses.push({
                                url: url,
                                status: response.status,
                                data: null
                            });
                        });
                        
                        return response;
                    });
            };
            
            // Override XMLHttpRequest to capture requests
            const originalXHR = window.XMLHttpRequest;
            window.XMLHttpRequest = function() {
                const xhr = new originalXHR();
                const originalOpen = xhr.open;
                const originalSend = xhr.send;
                
                xhr.open = function(method, url, ...args) {
                    this._method = method;
                    this._url = url;
                    return originalOpen.apply(this, [method, url, ...args]);
                };
                
                xhr.send = function(data) {
                    // Log the request
                    networkData.requests.push({
                        url: this._url,
                        method: this._method,
                        headers: {},
                        body: data
                    });
                    
                    // Add response listener
                    this.addEventListener('load', function() {
                        try {
                            const jsonData = JSON.parse(this.responseText);
                            networkData.responses.push({
                                url: this._url,
                                status: this.status,
                                data: jsonData
                            });
                        } catch (e) {
                            networkData.responses.push({
                                url: this._url,
                                status: this.status,
                                data: this.responseText
                            });
                        }
                    });
                    
                    return originalSend.apply(this, [data]);
                };
                
                return xhr;
            };
            
            // Return the network data
            return networkData;
            """
            
            # Execute the capture script
            result = self.driver.execute_script(capture_script)
            
            # Wait for requests to be captured
            time.sleep(15)
            
            # Get the captured data
            captured_data = self.driver.execute_script("return networkData;")
            
            logger.info(f"✅ Captured {len(captured_data.get('requests', []))} requests")
            logger.info(f"✅ Captured {len(captured_data.get('responses', []))} responses")
            
            return captured_data
            
        except Exception as e:
            logger.error(f"❌ Network capture error: {e}")
            return {}
    
    def save_network_data(self, data: Dict[str, Any]) -> str:
        """Save network data to files and SQL database"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save complete data as JSON
            json_file = os.path.join(self.output_dir, f"network_data_{timestamp}.json")
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Save individual responses as separate files (like manual process)
            for i, response in enumerate(data.get('responses', [])):
                if 'instatscout.com' in response.get('url', ''):
                    # Save as text file (like manual process)
                    response_file = os.path.join(self.output_dir, f"response_{timestamp}_{i}.txt")
                    with open(response_file, 'w') as f:
                        f.write(json.dumps(response['data'], indent=2))
            
            # Save to SQL database
            self.save_to_database(data, timestamp)
            
            logger.info(f"✅ Network data saved to {json_file}")
            logger.info(f"✅ Data also saved to SQL database")
            return json_file
            
        except Exception as e:
            logger.error(f"❌ Error saving data: {e}")
            return ""
    
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
            requests_count = len(data.get('requests', []))
            responses_count = len(data.get('responses', []))
            raw_data = json.dumps(data)
            
            cursor.execute('''
                INSERT INTO daily_captures 
                (capture_date, capture_time, team_id, requests_count, responses_count, raw_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime('%Y-%m-%d'),
                timestamp,
                '21479',  # Lloydminster Bobcats
                requests_count,
                responses_count,
                raw_data
            ))
            
            # Process and save player data if available
            self.process_and_save_player_data(data, cursor)
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Data saved to SQL database: {requests_count} requests, {responses_count} responses")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving to database: {e}")
            return False
    
    def process_and_save_player_data(self, data: Dict[str, Any], cursor) -> None:
        """Process and save player data from captured responses"""
        try:
            for response in data.get('responses', []):
                if 'instatscout.com' in response.get('url', '') and response.get('status') == 200:
                    response_data = response.get('data', {})
                    
                    # Look for player data in the response
                    if isinstance(response_data, dict):
                        # Check for team stats data
                        if 'data' in response_data and isinstance(response_data['data'], list):
                            for item in response_data['data']:
                                if isinstance(item, dict) and 'player_id' in item:
                                    # This looks like player data
                                    self.save_player_to_database(item, cursor)
                                    
        except Exception as e:
            logger.error(f"❌ Error processing player data: {e}")
    
    def save_player_to_database(self, player_data: Dict[str, Any], cursor) -> None:
        """Save individual player data to database"""
        try:
            player_id = player_data.get('player_id', '')
            name = player_data.get('name_eng', '')
            team_id = '21479'  # Lloydminster Bobcats
            
            if not player_id or not name:
                return
                
            # Check if player exists
            cursor.execute("SELECT player_id FROM players WHERE player_id = ?", (player_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing player
                cursor.execute('''
                    UPDATE players 
                    SET name = ?, last_updated = ?, metrics = ?
                    WHERE player_id = ?
                ''', (
                    name,
                    datetime.now().isoformat(),
                    json.dumps(player_data),
                    player_id
                ))
            else:
                # Insert new player
                cursor.execute('''
                    INSERT INTO players (player_id, team_id, name, metrics, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    player_id,
                    team_id,
                    name,
                    json.dumps(player_data),
                    datetime.now().isoformat()
                ))
                
        except Exception as e:
            logger.error(f"❌ Error saving player {player_data.get('player_id', 'unknown')}: {e}")
    
    def run_daily_capture(self) -> bool:
        """Run the daily capture process"""
        try:
            logger.info("🚀 Starting daily 3 AM network data capture...")
            
            # Setup driver
            if not self.setup_driver():
                return False
            
            # Login and navigate
            if not self.login_and_navigate():
                return False
            
            # Capture network data
            captured_data = self.capture_network_data()
            
            if not captured_data:
                logger.error("❌ No data captured")
                return False
            
            # Save data
            output_file = self.save_network_data(captured_data)
            
            if output_file:
                logger.info("✅ Daily capture completed successfully!")
                
                # Send Discord notification
                try:
                    logger.info("📱 Sending Discord notification...")
                    send_discord_notification()
                    logger.info("✅ Discord notification sent!")
                except Exception as e:
                    logger.error(f"❌ Discord notification failed: {e}")
                
                return True
            else:
                logger.error("❌ Failed to save captured data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Daily capture error: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def setup_daily_schedule():
    """Setup daily schedule to run at 4 AM Eastern"""
    logger.info("⏰ Setting up daily schedule for 4 AM Eastern...")
    
    # Create capture instance
    capture = DailyNetworkCapture()
    
    # Schedule daily capture at 4 AM Eastern
    schedule.every().day.at("04:00").do(capture.run_daily_capture)
    
    logger.info("✅ Daily schedule set for 4 AM Eastern")
    logger.info("🔄 System will run continuously and capture data daily at 4 AM Eastern")
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def main():
    """Main function"""
    logger.info("🎯 Daily 4 AM Eastern Network Data Capture System")
    logger.info("=" * 50)
    
    # Test the capture system first
    capture = DailyNetworkCapture()
    
    # Run a test capture
    logger.info("🧪 Running test capture...")
    success = capture.run_daily_capture()
    
    if success:
        logger.info("✅ Test capture successful!")
        logger.info("🚀 Starting daily 4 AM Eastern schedule...")
        
        # Start the daily schedule
        setup_daily_schedule()
    else:
        logger.error("❌ Test capture failed - please check credentials")

if __name__ == "__main__":
    main()
