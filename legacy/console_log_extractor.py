#!/usr/bin/env python3
"""
Console Log Extractor
Captures console logs from the browser to see what API calls are being made
"""

import time
import json
import logging
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_console_logs():
    """Extract console logs to see API calls"""
    try:
        logger.info("🚀 Starting Console Log Extractor...")
        
        # Use the working scraper
        scraper = HudlCompleteMetricsScraper()
        
        if not scraper.setup_driver():
            return {}
        
        # Enable console logging
        scraper.driver.execute_cdp_cmd('Runtime.enable', {})
        scraper.driver.execute_cdp_cmd('Network.enable', {})
        
        # Login
        username = "chaserochon777@gmail.com"
        password = "357Chaser!468"
        
        if not scraper.login(username, password):
            logger.error("❌ Authentication failed")
            return {}
        
        logger.info("✅ Authentication successful")
        
        # Navigate to team page
        team_url = "https://hockey.instatscout.com/instat/hockey/teams/21479"
        scraper.driver.get(team_url)
        time.sleep(3)
        
        # Click on SKATERS tab
        logger.info("🔍 Clicking SKATERS tab...")
        skaters_tab = scraper.driver.find_element("xpath", "//a[contains(text(), 'SKATERS')]")
        skaters_tab.click()
        time.sleep(5)
        
        # Get console logs
        logger.info("🔍 Capturing console logs...")
        logs = scraper.driver.get_log('browser')
        
        console_messages = []
        for log in logs:
            if log['level'] in ['INFO', 'WARNING', 'ERROR']:
                console_messages.append({
                    'level': log['level'],
                    'message': log['message'],
                    'timestamp': log['timestamp']
                })
        
        logger.info(f"📊 Captured {len(console_messages)} console messages")
        
        # Get network logs
        logger.info("🔍 Capturing network logs...")
        performance_logs = scraper.driver.get_log('performance')
        
        network_requests = []
        for log in performance_logs:
            message = json.loads(log['message'])
            if message['message']['method'] == 'Network.responseReceived':
                response = message['message']['params']['response']
                if '/api/' in response['url'] or 'scout' in response['url']:
                    network_requests.append({
                        'url': response['url'],
                        'status': response['status'],
                        'headers': response.get('headers', {}),
                        'timestamp': log['timestamp']
                    })
        
        logger.info(f"📊 Captured {len(network_requests)} network requests")
        
        # Get the current page data
        page_data = scraper.driver.execute_script("""
            return {
                url: window.location.href,
                title: document.title,
                allText: document.body.innerText.substring(0, 10000), // First 10k chars
                elementCount: document.querySelectorAll('*').length
            };
        """)
        
        results = {
            'console_messages': console_messages,
            'network_requests': network_requests,
            'page_data': page_data,
            'total_console_messages': len(console_messages),
            'total_network_requests': len(network_requests)
        }
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error in console log extraction: {e}")
        return {}
    finally:
        if 'scraper' in locals() and scraper.driver:
            scraper.driver.quit()

def main():
    """Main function"""
    results = extract_console_logs()
    
    # Save results
    with open('console_log_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("✅ Results saved to console_log_results.json")
    
    # Print summary
    if results:
        logger.info(f"📊 Console messages: {results.get('total_console_messages', 0)}")
        logger.info(f"📊 Network requests: {results.get('total_network_requests', 0)}")
        
        # Show some console messages
        if 'console_messages' in results:
            logger.info("📊 Sample console messages:")
            for i, msg in enumerate(results['console_messages'][:10]):
                logger.info(f"  {i+1:2d}. [{msg['level']}] {msg['message'][:100]}...")
        
        # Show network requests
        if 'network_requests' in results:
            logger.info("📊 Network requests:")
            for i, req in enumerate(results['network_requests'][:10]):
                logger.info(f"  {i+1:2d}. {req['url']} (Status: {req['status']})")

if __name__ == "__main__":
    main()
