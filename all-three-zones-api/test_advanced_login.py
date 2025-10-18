#!/usr/bin/env python3
"""
Advanced login test for All Three Zones
"""

import requests
import json
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_advanced_login():
    """Test advanced login methods"""
    logger.info("🔐 Testing Advanced Login Methods")
    logger.info("=" * 50)
    
    try:
        session = requests.Session()
        
        # Method 1: JSON-RPC with proper headers
        logger.info("1. Testing JSON-RPC login...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.allthreezones.com',
            'Referer': 'https://www.allthreezones.com/player-cards.html'
        }
        
        payload = {
            "method": "validate_user",
            "params": [Config.A3Z_USERNAME, Config.A3Z_PASSWORD],
            "id": 1
        }
        
        response = session.post(
            'https://www.allthreezones.com/ajax/api/JsonRPC/Membership/',
            json=payload,
            headers=headers
        )
        
        logger.info(f"✅ JSON-RPC status: {response.status_code}")
        logger.info(f"✅ Response: {response.text}")
        
        # Method 2: Try form-based login
        logger.info("\n2. Testing form-based login...")
        
        form_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.allthreezones.com',
            'Referer': 'https://www.allthreezones.com/player-cards.html'
        }
        
        form_data = {
            'login-email': Config.A3Z_USERNAME,
            'login-password': Config.A3Z_PASSWORD
        }
        
        form_response = session.post(
            'https://www.allthreezones.com/player-cards.html',
            data=form_data,
            headers=form_headers,
            allow_redirects=True
        )
        
        logger.info(f"✅ Form login status: {form_response.status_code}")
        logger.info(f"✅ Final URL: {form_response.url}")
        
        # Method 3: Try to get the login page first, then login
        logger.info("\n3. Testing session-based login...")
        
        # Get the login page first
        login_page = session.get('https://www.allthreezones.com/player-cards.html')
        logger.info(f"✅ Login page status: {login_page.status_code}")
        
        # Try login again
        session_response = session.post(
            'https://www.allthreezones.com/ajax/api/JsonRPC/Membership/',
            json=payload,
            headers=headers
        )
        
        logger.info(f"✅ Session login status: {session_response.status_code}")
        
        # Test if we can access the player cards page
        logger.info("\n4. Testing player cards access...")
        
        player_response = session.get('https://www.allthreezones.com/player-cards.html')
        logger.info(f"✅ Player cards status: {player_response.status_code}")
        logger.info(f"✅ Player cards URL: {player_response.url}")
        
        # Check if we're still on login page
        if "Log In" in player_response.text:
            logger.error("❌ Still on login page - authentication failed")
            
            # Save the response for debugging
            with open('advanced_login_debug.html', 'w', encoding='utf-8') as f:
                f.write(player_response.text)
            logger.info("✅ Saved debug page to advanced_login_debug.html")
            
            return False
        else:
            logger.info("✅ Successfully accessed player cards page!")
            
            # Save the successful response
            with open('successful_player_cards.html', 'w', encoding='utf-8') as f:
                f.write(player_response.text)
            logger.info("✅ Saved successful page to successful_player_cards.html")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error during advanced login test: {e}")
        return False

def main():
    """Main test function"""
    if test_advanced_login():
        logger.info("\n🎉 Advanced login test completed successfully!")
        logger.info("You can now search for Sidney Crosby!")
    else:
        logger.error("\n❌ Advanced login test failed")
        logger.info("Check the debug files for more information")

if __name__ == "__main__":
    main() 