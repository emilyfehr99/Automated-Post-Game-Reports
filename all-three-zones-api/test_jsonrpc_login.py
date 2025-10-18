#!/usr/bin/env python3
"""
Test script to authenticate using JSON-RPC API
"""

import requests
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_jsonrpc_login():
    """Test login using JSON-RPC API"""
    # Import config for credentials
    from config import Config
    
    try:
        session = requests.Session()
        
        # Set headers
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
        
        # JSON-RPC payload for validate_user
        payload = {
            "method": "validate_user",
            "params": [Config.A3Z_USERNAME, Config.A3Z_PASSWORD],
            "id": 1
        }
        
        # Make the JSON-RPC call
        rpc_url = "https://www.allthreezones.com/ajax/api/JsonRPC/Membership/"
        response = session.post(rpc_url, json=payload, headers=headers)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        try:
            result = response.json()
            print(f"Response JSON: {json.dumps(result, indent=2)}")
        except:
            print(f"Response text: {response.text}")
        
        # If login successful, try to access player cards
        if response.status_code == 200:
            print("\nTrying to access player cards page...")
            
            player_response = session.get("https://www.allthreezones.com/player-cards.html")
            print(f"Player cards status: {player_response.status_code}")
            print(f"Player cards URL: {player_response.url}")
            
            # Save the response
            with open('player_cards_after_login.html', 'w', encoding='utf-8') as f:
                f.write(player_response.text)
            print("Saved player cards page to player_cards_after_login.html")
            
            # Check if we're still on login page
            if "Log In" in player_response.text:
                print("❌ Still on login page - authentication failed")
            else:
                print("✅ Successfully accessed player cards page")
                
                # Look for player data
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(player_response.content, 'html.parser')
                
                # Look for tables
                tables = soup.find_all('table')
                print(f"\nFound {len(tables)} tables")
                
                # Look for any player-related content
                player_keywords = ['mcdavid', 'crosby', 'ovechkin', 'matthews', 'mackinnon', 'draisaitl']
                for keyword in player_keywords:
                    elements = soup.find_all(string=lambda text: text and keyword.lower() in text.lower())
                    if elements:
                        print(f"\nFound '{keyword}' in {len(elements)} elements")
                        for elem in elements[:3]:
                            print(f"  '{elem.strip()}'")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_jsonrpc_login() 