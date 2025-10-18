#!/usr/bin/env python3
"""
Browser API Interceptor
Uses Selenium to intercept API calls made by the browser and extract the data
"""

import time
import json
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BrowserAPIInterceptor:
    def __init__(self):
        self.driver = None
        self.api_calls = []
        
    def setup_driver(self):
        """Set up Chrome driver with logging enabled"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Enable logging to capture network requests
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--log-level=0")
            chrome_options.add_argument("--v=1")
            
            # Enable DevTools logging
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--log-level=0")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Enable network domain
            self.driver.execute_cdp_cmd('Network.enable', {})
            
            logger.info("✅ Chrome driver setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up driver: {e}")
            return False
    
    def login(self, username: str, password: str) -> bool:
        """Login to Hudl Instat using the same method as the working scraper"""
        try:
            logger.info("🔐 Logging into Hudl Instat...")
            
            self.driver.get("https://hockey.instatscout.com/instat/hockey/login")
            time.sleep(3)
            
            # Find and fill username - try multiple selectors
            username_selectors = [
                "input[name='email']",
                "input[type='email']", 
                "input[placeholder*='email' i]",
                "input[placeholder*='Email' i]",
                "input[id*='email' i]",
                "input[id*='Email' i]"
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not username_field:
                logger.error("❌ Could not find username field")
                return False
            
            username_field.clear()
            username_field.send_keys(username)
            
            # Find and fill password - try multiple selectors
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[placeholder*='password' i]",
                "input[placeholder*='Password' i]",
                "input[id*='password' i]",
                "input[id*='Password' i]"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not password_field:
                logger.error("❌ Could not find password field")
                return False
            
            password_field.clear()
            password_field.send_keys(password)
            
            # Find and click login button - try multiple selectors
            login_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Login')",
                "button:contains('Sign In')",
                "button:contains('Log In')",
                ".login-button",
                "#login-button"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    if ":contains(" in selector:
                        login_button = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{selector.split(':contains(')[1].split(')')[0]}')]")
                    else:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not login_button:
                logger.error("❌ Could not find login button")
                return False
            
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
    
    def intercept_api_calls(self, team_id: str = "21479"):
        """Navigate to team page and intercept API calls"""
        try:
            logger.info(f"🔍 Navigating to team {team_id} page...")
            
            # Navigate to team page
            team_url = f"https://hockey.instatscout.com/instat/hockey/teams/{team_id}"
            self.driver.get(team_url)
            time.sleep(3)
            
            # Click on SKATERS tab to trigger API calls
            logger.info("🔍 Clicking SKATERS tab to trigger API calls...")
            skaters_tab = self.driver.find_element(By.XPATH, "//a[contains(text(), 'SKATERS')]")
            skaters_tab.click()
            time.sleep(3)
            
            # Get network logs
            logger.info("🔍 Capturing network requests...")
            logs = self.driver.get_log('performance')
            
            api_calls = []
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    response = message['message']['params']['response']
                    url = response['url']
                    
                    # Look for API calls
                    if '/api/' in url or 'scout_uni' in url or 'scout_param' in url:
                        api_calls.append({
                            'url': url,
                            'status': response['status'],
                            'headers': response.get('headers', {}),
                            'timestamp': log['timestamp']
                        })
            
            logger.info(f"📊 Found {len(api_calls)} API calls")
            return api_calls
            
        except Exception as e:
            logger.error(f"❌ Error intercepting API calls: {e}")
            return []
    
    def execute_api_call_in_browser(self, team_id: str = "21479"):
        """Execute API calls directly in the browser context"""
        try:
            logger.info(f"🔍 Executing API calls in browser context for team {team_id}")
            
            # Navigate to team page
            team_url = f"https://hockey.instatscout.com/instat/hockey/teams/{team_id}"
            self.driver.get(team_url)
            time.sleep(3)
            
            # Click on SKATERS tab
            skaters_tab = self.driver.find_element(By.XPATH, "//a[contains(text(), 'SKATERS')]")
            skaters_tab.click()
            time.sleep(3)
            
            # Execute API calls directly in browser
            api_calls = [
                {
                    'name': 'team_overview',
                    'script': '''
                        fetch('/api/scout_uni_overview_team_stat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest'
                            },
                            body: JSON.stringify({
                                params: {
                                    _p_team_id: 21479,
                                    _p_season_id: 34,
                                    _p_tournament_id: null
                                },
                                proc: "scout_uni_overview_team_stat"
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            window.apiResults = window.apiResults || {};
                            window.apiResults.team_overview = data;
                            console.log('Team overview API result:', data);
                        })
                        .catch(error => console.error('Team overview API error:', error));
                    '''
                },
                {
                    'name': 'lexical_params',
                    'script': '''
                        fetch('/api/scout_param_lexical', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest'
                            },
                            body: JSON.stringify({
                                params: {
                                    lang: "en",
                                    phrases: [1021, 15994, 15995, 17890, 16630]
                                },
                                proc: "scout_param_lexical"
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            window.apiResults = window.apiResults || {};
                            window.apiResults.lexical_params = data;
                            console.log('Lexical params API result:', data);
                        })
                        .catch(error => console.error('Lexical params API error:', error));
                    '''
                },
                {
                    'name': 'team_players',
                    'script': '''
                        fetch('/api/scout_uni_team_players_stat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest'
                            },
                            body: JSON.stringify({
                                params: {
                                    _p_team_id: 21479,
                                    _p_season_id: 34,
                                    _p_tournament_id: null
                                },
                                proc: "scout_uni_team_players_stat"
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            window.apiResults = window.apiResults || {};
                            window.apiResults.team_players = data;
                            console.log('Team players API result:', data);
                        })
                        .catch(error => console.error('Team players API error:', error));
                    '''
                }
            ]
            
            # Execute each API call
            for call in api_calls:
                logger.info(f"🔍 Executing {call['name']} API call...")
                try:
                    self.driver.execute_script(call['script'])
                    time.sleep(2)  # Wait for API call to complete
                except Exception as e:
                    logger.error(f"❌ Error executing {call['name']}: {e}")
            
            # Wait for all API calls to complete
            time.sleep(5)
            
            # Get results from browser
            logger.info("🔍 Retrieving API results from browser...")
            results = self.driver.execute_script("return window.apiResults || {};")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error executing API calls: {e}")
            return {}
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function"""
    logger.info("🚀 Starting Browser API Interceptor...")
    
    interceptor = BrowserAPIInterceptor()
    
    try:
        # Setup driver
        if not interceptor.setup_driver():
            return
        
        # Login
        username = "chaserochon777@gmail.com"
        password = "357Chaser!468"
        
        if not interceptor.login(username, password):
            return
        
        # Execute API calls
        results = interceptor.execute_api_call_in_browser()
        
        # Save results
        with open('browser_api_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("✅ Results saved to browser_api_results.json")
        
        # Print summary
        for key, value in results.items():
            if isinstance(value, dict):
                logger.info(f"📊 {key}: {len(value)} keys")
            else:
                logger.info(f"📊 {key}: {type(value)}")
    
    finally:
        interceptor.close()

if __name__ == "__main__":
    main()
