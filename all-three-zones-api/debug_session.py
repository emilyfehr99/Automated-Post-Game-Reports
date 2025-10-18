#!/usr/bin/env python3
"""
Debug script to check session response format
"""

import requests
import json
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_session():
    """Debug the session response format"""
    logger.info("🔍 Debugging Session Response")
    logger.info("=" * 40)
    
    try:
        session = requests.Session()
        
        # Get the login page first
        login_page = session.get('https://www.allthreezones.com/player-cards.html')
        logger.info(f"✅ Login page status: {login_page.status_code}")
        
        # JSON-RPC authentication
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
        
        # Try validate_user
        validate_payload = {
            "method": "validate_user",
            "params": [Config.A3Z_USERNAME, Config.A3Z_PASSWORD],
            "id": 1
        }
        
        validate_response = session.post(
            'https://www.allthreezones.com/ajax/api/JsonRPC/Membership/',
            json=validate_payload,
            headers=headers
        )
        
        logger.info(f"✅ Validate user status: {validate_response.status_code}")
        logger.info(f"✅ Validate user response: {validate_response.text}")
        
        # Try get_session_details
        session_payload = {
            "method": "Member::get_session_details",
            "params": [],
            "id": 0
        }
        
        session_response = session.post(
            'https://www.allthreezones.com/ajax/api/JsonRPC/Membership/',
            json=session_payload,
            headers=headers
        )
        
        logger.info(f"✅ Session details status: {session_response.status_code}")
        logger.info(f"✅ Session details response: {session_response.text}")
        
        # Try different method names
        alternative_methods = [
            "get_session_details",
            "Member.get_session_details", 
            "getSessionDetails",
            "validate_session"
        ]
        
        for method in alternative_methods:
            alt_payload = {
                "method": method,
                "params": [],
                "id": 0
            }
            
            alt_response = session.post(
                'https://www.allthreezones.com/ajax/api/JsonRPC/Membership/',
                json=alt_payload,
                headers=headers
            )
            
            logger.info(f"✅ {method} status: {alt_response.status_code}")
            logger.info(f"✅ {method} response: {alt_response.text}")
        
        # Try to access player cards page
        player_response = session.get('https://www.allthreezones.com/player-cards.html')
        logger.info(f"✅ Player cards status: {player_response.status_code}")
        logger.info(f"✅ Player cards URL: {player_response.url}")
        
        # Save the response
        with open('debug_session_response.html', 'w', encoding='utf-8') as f:
            f.write(player_response.text)
        logger.info("✅ Saved session response to debug_session_response.html")
        
    except Exception as e:
        logger.error(f"❌ Error during session debug: {e}")

if __name__ == "__main__":
    debug_session() 