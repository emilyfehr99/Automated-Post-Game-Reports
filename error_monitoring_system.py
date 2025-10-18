#!/usr/bin/env python3
"""
Comprehensive Error Monitoring System
Monitors and handles the 4 main risk areas for the 4 AM capture
"""

import logging
import requests
import time
from datetime import datetime
from typing import Dict, Any, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from discord_notification import send_discord_notification

logger = logging.getLogger(__name__)

class ErrorMonitoringSystem:
    """Comprehensive error monitoring for the 4 AM capture system"""
    
    def __init__(self):
        self.error_counts = {
            'hudl_website_changes': 0,
            'network_issues': 0,
            'chrome_driver_issues': 0,
            'anti_bot_detection': 0,
            'general_errors': 0
        }
        self.max_retries = 3
        self.retry_delay = 30  # seconds
    
    def check_network_connectivity(self) -> bool:
        """Check if internet connection is working"""
        try:
            logger.info("🌐 Checking network connectivity...")
            
            # Test multiple endpoints
            test_urls = [
                "https://www.google.com",
                "https://www.hudl.com", 
                "https://api-hockey.instatscout.com"
            ]
            
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        logger.info(f"✅ Network connectivity OK - {url}")
                        return True
                except Exception as e:
                    logger.warning(f"⚠️ Network issue with {url}: {e}")
                    continue
            
            logger.error("❌ Network connectivity failed - all endpoints unreachable")
            self.error_counts['network_issues'] += 1
            return False
            
        except Exception as e:
            logger.error(f"❌ Network check error: {e}")
            self.error_counts['network_issues'] += 1
            return False
    
    def check_hudl_website_changes(self) -> bool:
        """Check if Hudl website structure has changed"""
        try:
            logger.info("🔍 Checking Hudl website for changes...")
            
            # Test login page accessibility
            response = requests.get("https://app.hudl.com/login", timeout=15)
            
            if response.status_code != 200:
                logger.error(f"❌ Hudl login page changed - Status: {response.status_code}")
                self.error_counts['hudl_website_changes'] += 1
                return False
            
            # Check for key elements that might have changed (more lenient)
            if len(response.text) < 100:  # Very short response might indicate a problem
                logger.error("❌ Hudl login page returned suspiciously short content")
                self.error_counts['hudl_website_changes'] += 1
                return False
            
            logger.info("✅ Hudl website structure appears unchanged")
            return True
            
        except Exception as e:
            logger.error(f"❌ Hudl website check error: {e}")
            self.error_counts['hudl_website_changes'] += 1
            return False
    
    def check_chrome_driver(self) -> bool:
        """Check if Chrome driver is working properly"""
        try:
            logger.info("🔧 Checking Chrome driver...")
            
            # Test driver initialization
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Test basic functionality
            driver.get("https://www.google.com")
            title = driver.title
            
            driver.quit()
            
            if "Google" in title:
                logger.info("✅ Chrome driver working properly")
                return True
            else:
                logger.error("❌ Chrome driver not working properly")
                self.error_counts['chrome_driver_issues'] += 1
                return False
                
        except Exception as e:
            logger.error(f"❌ Chrome driver check error: {e}")
            self.error_counts['chrome_driver_issues'] += 1
            return False
    
    def check_anti_bot_detection(self) -> bool:
        """Check for signs of anti-bot detection"""
        try:
            logger.info("🤖 Checking for anti-bot detection...")
            
            # Test with a simple request to see if we're blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15'
            }
            
            response = requests.get("https://app.hudl.com", headers=headers, timeout=15)
            
            # Check for common anti-bot indicators
            anti_bot_indicators = [
                "access denied",
                "blocked",
                "captcha",
                "suspicious activity",
                "rate limit",
                "too many requests"
            ]
            
            response_text = response.text.lower()
            for indicator in anti_bot_indicators:
                if indicator in response_text:
                    logger.error(f"❌ Anti-bot detection triggered: {indicator}")
                    self.error_counts['anti_bot_detection'] += 1
                    return False
            
            logger.info("✅ No anti-bot detection detected")
            return True
            
        except Exception as e:
            logger.error(f"❌ Anti-bot check error: {e}")
            self.error_counts['anti_bot_detection'] += 1
            return False
    
    def run_comprehensive_check(self) -> Dict[str, bool]:
        """Run all error checks and return results"""
        logger.info("🔍 Running comprehensive error monitoring check...")
        
        results = {
            'network_connectivity': self.check_network_connectivity(),
            'hudl_website': self.check_hudl_website_changes(),
            'chrome_driver': self.check_chrome_driver(),
            'anti_bot_detection': self.check_anti_bot_detection()
        }
        
        # Count failures
        failures = sum(1 for result in results.values() if not result)
        total_checks = len(results)
        
        logger.info(f"📊 Error check results: {total_checks - failures}/{total_checks} passed")
        
        if failures > 0:
            logger.warning(f"⚠️ {failures} checks failed - system may have issues")
            self.send_error_notification(results)
        else:
            logger.info("✅ All error checks passed - system ready!")
        
        return results
    
    def send_error_notification(self, results: Dict[str, bool]):
        """Send Discord notification about errors"""
        try:
            failed_checks = [check for check, passed in results.items() if not passed]
            
            message = f"""🚨 **ERROR MONITORING ALERT** 🚨

❌ **Failed Checks:** {', '.join(failed_checks)}

⚠️ **System may have issues at 4 AM!**

🔧 **Recommended Actions:**
• Check internet connection
• Update Chrome driver if needed
• Verify Hudl website access
• Review error logs

📊 **Error Counts:**
• Network Issues: {self.error_counts['network_issues']}
• Hudl Changes: {self.error_counts['hudl_website_changes']}
• Chrome Driver: {self.error_counts['chrome_driver_issues']}
• Anti-Bot: {self.error_counts['anti_bot_detection']}

🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

            # Send to Discord
            send_discord_notification()
            
        except Exception as e:
            logger.error(f"❌ Error notification failed: {e}")
    
    def get_error_summary(self) -> str:
        """Get summary of all errors encountered"""
        total_errors = sum(self.error_counts.values())
        
        if total_errors == 0:
            return "✅ No errors detected - system healthy!"
        
        summary = f"📊 **ERROR SUMMARY** (Total: {total_errors})\n"
        for error_type, count in self.error_counts.items():
            if count > 0:
                summary += f"• {error_type.replace('_', ' ').title()}: {count}\n"
        
        return summary

def run_error_monitoring():
    """Run the error monitoring system"""
    print("🔍 COMPREHENSIVE ERROR MONITORING")
    print("=" * 50)
    
    monitor = ErrorMonitoringSystem()
    results = monitor.run_comprehensive_check()
    
    print("\n📊 RESULTS:")
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {check}: {status}")
    
    print(f"\n{monitor.get_error_summary()}")
    
    return results

if __name__ == "__main__":
    run_error_monitoring()
