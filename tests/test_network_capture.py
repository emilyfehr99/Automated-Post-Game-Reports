#!/usr/bin/env python3
"""
Test Network Data Capture for Hudl Instat
Test the automated network capture system
"""

import time
import json
import logging
import os
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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestNetworkCapture:
    """Test network data capture system"""
    
    def __init__(self):
        self.driver = None
        self.output_dir = "test_network_data"
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
            # Don't run headless for testing
            # chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            
            service = Service(ChromeDriverManager().install())
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
        """Save network data to files"""
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
            
            logger.info(f"✅ Network data saved to {json_file}")
            return json_file
            
        except Exception as e:
            logger.error(f"❌ Error saving data: {e}")
            return ""
    
    def run_test_capture(self) -> bool:
        """Run the test capture process"""
        try:
            logger.info("🚀 Starting test network data capture...")
            
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
                logger.info("✅ Test capture completed successfully!")
                return True
            else:
                logger.error("❌ Failed to save captured data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test capture error: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main function"""
    logger.info("🎯 Test Network Data Capture System")
    logger.info("=" * 50)
    
    # Create capture instance
    capture = TestNetworkCapture()
    
    # Run test capture
    success = capture.run_test_capture()
    
    if success:
        logger.info("✅ Test capture successful!")
        logger.info("📁 Check the 'test_network_data' folder for captured files")
        logger.info("🚀 System is ready for daily 4 AM Eastern captures!")
    else:
        logger.error("❌ Test capture failed")

if __name__ == "__main__":
    main()
