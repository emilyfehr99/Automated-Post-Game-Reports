#!/usr/bin/env python3
"""
Scroll Metrics Capture Script
Properly scrolls through the Hudl Instat page to capture ALL metrics (40+ per player)
"""

import time
import json
import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Any
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from credentials_database import CredentialsDatabase

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScrollMetricsCapture:
    """Capture all metrics by properly scrolling through the page"""
    
    def __init__(self):
        self.driver = None
        self.credentials_db = CredentialsDatabase()
    
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
            firefox_options.add_argument("--width=1920")
            firefox_options.add_argument("--height=1080")
            # Don't run headless so we can see the scrolling
            
            # Setup driver
            service = Service("/opt/homebrew/bin/geckodriver")
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            
            logger.info("✅ Firefox driver setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up Firefox driver: {e}")
            return False
    
    def login_and_navigate(self) -> bool:
        """Login to Hudl and navigate to the metrics page"""
        try:
            logger.info("🔐 Logging into Hudl...")
            
            # Get credentials
            creds = self.get_credentials()
            
            # Navigate to login page
            self.driver.get("https://app.hudl.com/login")
            time.sleep(3)
            
            # Try to find and fill login form
            try:
                # Look for email field
                email_selectors = [
                    "input[name='email']",
                    "input[type='email']",
                    "input[placeholder*='email' i]",
                    "input[placeholder*='Email' i]"
                ]
                
                email_field = None
                for selector in email_selectors:
                    try:
                        email_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                
                if email_field:
                    email_field.clear()
                    email_field.send_keys(creds['username'])
                    logger.info("✅ Email entered")
                
                # Look for password field
                password_selectors = [
                    "input[name='password']",
                    "input[type='password']",
                    "input[placeholder*='password' i]",
                    "input[placeholder*='Password' i]"
                ]
                
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                
                if password_field:
                    password_field.clear()
                    password_field.send_keys(creds['password'])
                    logger.info("✅ Password entered")
                
                # Look for login button
                login_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Login')",
                    "button:contains('Sign In')",
                    ".login-button",
                    "#login-button"
                ]
                
                login_button = None
                for selector in login_selectors:
                    try:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                
                if login_button:
                    login_button.click()
                    logger.info("✅ Login button clicked")
                    time.sleep(5)
                    
            except Exception as e:
                logger.warning(f"⚠️ Login form interaction failed: {e}")
            
            # Navigate to the metrics page
            logger.info("📊 Navigating to metrics page...")
            self.driver.get("https://app.hudl.com/metropole/shim/api-hockey.instatscout.com/data")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during login and navigation: {e}")
            return False
    
    def scroll_and_capture_metrics(self) -> Dict[str, Any]:
        """Scroll through the page to capture all metrics"""
        try:
            logger.info("📜 Starting scroll and capture process...")
            
            # Wait for page to load
            time.sleep(3)
            
            # Get initial page source
            initial_source = self.driver.page_source
            initial_metrics = self.extract_metrics_from_html(initial_source)
            logger.info(f"📊 Initial metrics found: {len(initial_metrics)}")
            
            # Scroll down multiple times to load all metrics
            scroll_positions = []
            all_metrics = set()
            
            # Convert initial metrics to set
            for metric in initial_metrics:
                all_metrics.add((metric['name'], metric['value']))
            
            # Scroll down in increments
            for i in range(10):  # Scroll 10 times
                try:
                    # Get current scroll position
                    current_scroll = self.driver.execute_script("return window.pageYOffset;")
                    scroll_positions.append(current_scroll)
                    
                    # Scroll down
                    self.driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(2)  # Wait for content to load
                    
                    # Check if we've reached the bottom
                    new_scroll = self.driver.execute_script("return window.pageYOffset;")
                    if new_scroll == current_scroll:
                        logger.info("📜 Reached bottom of page")
                        break
                    
                    # Extract metrics from current view
                    current_source = self.driver.page_source
                    current_metrics = self.extract_metrics_from_html(current_source)
                    
                    # Add new metrics
                    new_metrics_count = 0
                    for metric in current_metrics:
                        metric_tuple = (metric['name'], metric['value'])
                        if metric_tuple not in all_metrics:
                            all_metrics.add(metric_tuple)
                            new_metrics_count += 1
                    
                    logger.info(f"📊 Scroll {i+1}: Found {len(current_metrics)} metrics, {new_metrics_count} new")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error during scroll {i+1}: {e}")
                    continue
            
            # Convert back to list
            final_metrics = [{'name': name, 'value': value} for name, value in all_metrics]
            
            logger.info(f"🎉 Scroll complete! Total unique metrics: {len(final_metrics)}")
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_metrics': len(final_metrics),
                'scroll_positions': scroll_positions,
                'metrics': final_metrics,
                'page_source': self.driver.page_source
            }
            
        except Exception as e:
            logger.error(f"❌ Error during scroll and capture: {e}")
            return None
    
    def extract_metrics_from_html(self, html_content: str) -> List[Dict[str, str]]:
        """Extract metrics from HTML content"""
        try:
            import re
            
            metrics = []
            
            # Look for metric patterns in the HTML
            # This is a simplified pattern - you might need to adjust based on actual HTML structure
            
            # Pattern for metric name and value pairs
            metric_patterns = [
                r'<div[^>]*class="[^"]*metric[^"]*"[^>]*>.*?<span[^>]*class="[^"]*name[^"]*"[^>]*>(.*?)</span>.*?<span[^>]*class="[^"]*value[^"]*"[^>]*>(.*?)</span>',
                r'<td[^>]*class="[^"]*metric[^"]*"[^>]*>.*?<span[^>]*>(.*?)</span>.*?<span[^>]*>(.*?)</span>',
                r'<div[^>]*data-metric="([^"]*)"[^>]*>([^<]*)</div>',
                r'<span[^>]*class="[^"]*metric-name[^"]*"[^>]*>(.*?)</span>.*?<span[^>]*class="[^"]*metric-value[^"]*"[^>]*>(.*?)</span>'
            ]
            
            for pattern in metric_patterns:
                matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    if len(match) >= 2:
                        name = match[0].strip()
                        value = match[1].strip()
                        if name and value and name != value:
                            metrics.append({'name': name, 'value': value})
            
            # Also look for any text that might be metrics
            # This is a fallback approach
            lines = html_content.split('\n')
            for line in lines:
                # Look for lines that might contain metric data
                if ':' in line and any(char.isdigit() for char in line):
                    # Try to extract metric name and value
                    parts = line.split(':')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        value = parts[1].strip()
                        if len(name) < 20 and len(value) < 20:  # Reasonable lengths
                            metrics.append({'name': name, 'value': value})
            
            # Remove duplicates
            unique_metrics = []
            seen = set()
            for metric in metrics:
                key = (metric['name'], metric['value'])
                if key not in seen:
                    seen.add(key)
                    unique_metrics.append(metric)
            
            return unique_metrics
            
        except Exception as e:
            logger.error(f"❌ Error extracting metrics: {e}")
            return []
    
    def save_metrics_to_database(self, metrics_data: Dict[str, Any]) -> bool:
        """Save captured metrics to database"""
        try:
            conn = sqlite3.connect('ajhl_comprehensive.db')
            cursor = conn.cursor()
            
            # Clear existing comprehensive_metrics data
            cursor.execute("DELETE FROM comprehensive_metrics")
            logger.info("✅ Cleared existing comprehensive_metrics data")
            
            # Save metrics
            total_saved = 0
            for metric in metrics_data.get('metrics', []):
                cursor.execute('''
                    INSERT INTO comprehensive_metrics 
                    (team_id, player_id, metric_name, metric_value, metric_type, discovered_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    '21479',  # Team ID
                    'scroll_capture',  # Player ID for scroll capture
                    metric['name'],
                    metric['value'],
                    'comprehensive',
                    datetime.now().isoformat()
                ))
                total_saved += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Saved {total_saved} metrics to database")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving metrics to database: {e}")
            return False
    
    def run_capture(self) -> bool:
        """Run the complete capture process"""
        try:
            logger.info("🚀 Starting scroll metrics capture...")
            
            # Setup driver
            if not self.setup_driver():
                return False
            
            try:
                # Login and navigate
                if not self.login_and_navigate():
                    return False
                
                # Scroll and capture metrics
                metrics_data = self.scroll_and_capture_metrics()
                if not metrics_data:
                    return False
                
                # Save to database
                if self.save_metrics_to_database(metrics_data):
                    logger.info("✅ Scroll capture completed successfully!")
                    return True
                else:
                    return False
                    
            finally:
                # Keep driver open for a bit to see results
                time.sleep(10)
                if self.driver:
                    self.driver.quit()
                    logger.info("🔒 Firefox driver closed")
                
        except Exception as e:
            logger.error(f"❌ Error in scroll capture: {e}")
            return False

def main():
    """Main function"""
    print("📜 SCROLL METRICS CAPTURE")
    print("=" * 40)
    
    capture = ScrollMetricsCapture()
    
    if capture.run_capture():
        print("🎉 Scroll capture completed successfully!")
    else:
        print("❌ Scroll capture failed!")

if __name__ == "__main__":
    main()
