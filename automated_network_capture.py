#!/usr/bin/env python3
"""
Automated Network Data Capture for Hudl Instat
Automates the manual process of capturing network data from browser dev tools
Runs daily at 3 AM to capture fresh data
"""

import time
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import schedule

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NetworkDataCapture:
    """Automated network data capture from Hudl Instat"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.driver = None
        self.captured_data = {}
        self.output_dir = "captured_network_data"
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def setup_driver_with_network_logging(self):
        """Setup Chrome driver with network logging enabled"""
        try:
            logger.info("🔧 Setting up Chrome driver with network logging...")
            
            # Enable logging
            caps = DesiredCapabilities.CHROME
            caps['goog:loggingPrefs'] = {'performance': 'ALL'}
            
            # Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Faster loading
            chrome_options.add_argument("--disable-javascript")  # We only need network data
            
            # Set up service
            service = Service(ChromeDriverManager().install())
            
            # Create driver with logging capabilities
            self.driver = webdriver.Chrome(
                service=service, 
                options=chrome_options,
                desired_capabilities=caps
            )
            
            logger.info("✅ Chrome driver setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up driver: {e}")
            return False
    
    def login_to_hudl(self) -> bool:
        """Login to Hudl Instat"""
        try:
            logger.info("🔐 Logging into Hudl Instat...")
            
            # Navigate to login page
            self.driver.get("https://app.hudl.com/login")
            time.sleep(3)
            
            # Find and fill login form
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            email_field.clear()
            email_field.send_keys(self.username)
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "login" not in self.driver.current_url.lower():
                logger.info("✅ Login successful!")
                return True
            else:
                logger.error("❌ Login failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def navigate_to_team_data(self, team_id: str = "21479") -> bool:
        """Navigate to team data page"""
        try:
            logger.info(f"📊 Navigating to team {team_id} data...")
            
            # Navigate to team page
            team_url = f"https://app.hudl.com/instat/hockey/teams/{team_id}"
            self.driver.get(team_url)
            time.sleep(5)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info("✅ Successfully navigated to team data page")
            return True
            
        except Exception as e:
            logger.error(f"❌ Navigation error: {e}")
            return False
    
    def capture_network_data(self) -> Dict[str, Any]:
        """Capture network data from browser logs"""
        try:
            logger.info("📡 Capturing network data...")
            
            # Get performance logs
            logs = self.driver.get_log('performance')
            
            captured_data = {
                'timestamp': datetime.now().isoformat(),
                'team_id': '21479',
                'network_requests': [],
                'api_calls': [],
                'data_responses': []
            }
            
            for log in logs:
                try:
                    message = json.loads(log['message'])
                    
                    # Filter for network requests
                    if message['message']['method'] == 'Network.responseReceived':
                        response = message['message']['params']['response']
                        
                        # Look for API calls to instatscout.com
                        if 'instatscout.com' in response.get('url', ''):
                            request_data = {
                                'url': response['url'],
                                'status': response['status'],
                                'headers': response.get('headers', {}),
                                'timestamp': log['timestamp']
                            }
                            captured_data['api_calls'].append(request_data)
                    
                    # Filter for network responses
                    elif message['message']['method'] == 'Network.loadingFinished':
                        request_id = message['message']['params']['requestId']
                        
                        # Get response body if it's an API call
                        try:
                            response_body = self.driver.execute_cdp_cmd(
                                'Network.getResponseBody', 
                                {'requestId': request_id}
                            )
                            
                            if response_body and 'body' in response_body:
                                captured_data['data_responses'].append({
                                    'request_id': request_id,
                                    'body': response_body['body'],
                                    'timestamp': log['timestamp']
                                })
                        except:
                            pass  # Some responses can't be read
                            
                except Exception as e:
                    continue  # Skip malformed logs
            
            logger.info(f"✅ Captured {len(captured_data['api_calls'])} API calls")
            logger.info(f"✅ Captured {len(captured_data['data_responses'])} data responses")
            
            return captured_data
            
        except Exception as e:
            logger.error(f"❌ Network capture error: {e}")
            return {}
    
    def save_captured_data(self, data: Dict[str, Any]) -> str:
        """Save captured data to files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save complete data as JSON
            json_file = os.path.join(self.output_dir, f"network_data_{timestamp}.json")
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Save individual API calls as separate files
            for i, api_call in enumerate(data.get('api_calls', [])):
                api_file = os.path.join(self.output_dir, f"api_call_{timestamp}_{i}.txt")
                with open(api_file, 'w') as f:
                    f.write(f"URL: {api_call['url']}\n")
                    f.write(f"Status: {api_call['status']}\n")
                    f.write(f"Headers: {json.dumps(api_call['headers'], indent=2)}\n")
            
            # Save data responses as separate files
            for i, response in enumerate(data.get('data_responses', [])):
                response_file = os.path.join(self.output_dir, f"data_response_{timestamp}_{i}.txt")
                with open(response_file, 'w') as f:
                    f.write(response['body'])
            
            logger.info(f"✅ Data saved to {json_file}")
            return json_file
            
        except Exception as e:
            logger.error(f"❌ Error saving data: {e}")
            return ""
    
    def run_daily_capture(self) -> bool:
        """Run the complete daily capture process"""
        try:
            logger.info("🚀 Starting daily network data capture...")
            
            # Setup driver
            if not self.setup_driver_with_network_logging():
                return False
            
            # Login
            if not self.login_to_hudl():
                return False
            
            # Navigate to team data
            if not self.navigate_to_team_data():
                return False
            
            # Capture network data
            captured_data = self.capture_network_data()
            
            if not captured_data:
                logger.error("❌ No data captured")
                return False
            
            # Save data
            output_file = self.save_captured_data(captured_data)
            
            if output_file:
                logger.info("✅ Daily capture completed successfully!")
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
    
    def process_captured_data(self, data_file: str) -> Dict[str, Any]:
        """Process captured data to extract useful information"""
        try:
            logger.info(f"📊 Processing captured data from {data_file}...")
            
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            processed_data = {
                'team_id': data.get('team_id'),
                'timestamp': data.get('timestamp'),
                'players': [],
                'metrics': [],
                'team_stats': []
            }
            
            # Process data responses
            for response in data.get('data_responses', []):
                try:
                    response_body = json.loads(response['body'])
                    
                    # Look for player data
                    if 'players' in response_body:
                        processed_data['players'].extend(response_body['players'])
                    
                    # Look for metrics data
                    if 'metrics' in response_body:
                        processed_data['metrics'].extend(response_body['metrics'])
                    
                    # Look for team stats
                    if 'team_stats' in response_body:
                        processed_data['team_stats'].extend(response_body['team_stats'])
                        
                except json.JSONDecodeError:
                    continue  # Skip non-JSON responses
            
            logger.info(f"✅ Processed {len(processed_data['players'])} players")
            logger.info(f"✅ Processed {len(processed_data['metrics'])} metrics")
            
            return processed_data
            
        except Exception as e:
            logger.error(f"❌ Error processing data: {e}")
            return {}

def setup_daily_schedule():
    """Setup daily schedule to run at 3 AM"""
    logger.info("⏰ Setting up daily schedule for 3 AM...")
    
    # Create capture instance
    capture = NetworkDataCapture(
        username="your_username_here",  # Replace with actual credentials
        password="your_password_here"   # Replace with actual credentials
    )
    
    # Schedule daily capture at 3 AM
    schedule.every().day.at("03:00").do(capture.run_daily_capture)
    
    logger.info("✅ Daily schedule set for 3 AM")
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def main():
    """Main function"""
    logger.info("🎯 Automated Network Data Capture System")
    logger.info("=" * 50)
    
    # Test the capture system
    capture = NetworkDataCapture(
        username="your_username_here",  # Replace with actual credentials
        password="your_password_here"   # Replace with actual credentials
    )
    
    # Run a test capture
    logger.info("🧪 Running test capture...")
    success = capture.run_daily_capture()
    
    if success:
        logger.info("✅ Test capture successful!")
        logger.info("🚀 System ready for daily 3 AM captures")
    else:
        logger.error("❌ Test capture failed")

if __name__ == "__main__":
    main()
