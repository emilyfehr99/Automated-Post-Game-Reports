#!/usr/bin/env python3
"""
Test script to authenticate using form submission like the actual site
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

def test_form_login():
    """Test login using form submission"""
    try:
        session = requests.Session()
        
        # First, get the login page to establish session
        login_url = "https://www.allthreezones.com/player-cards.html"
        response = session.get(login_url)
        print(f"Initial page status: {response.status_code}")
        
        # Set headers for form submission
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.allthreezones.com',
            'Referer': 'https://www.allthreezones.com/player-cards.html'
        }
        
        # Import config for credentials
        from config import Config
        
        # Try different form submission approaches
        login_attempts = [
            # Attempt 1: Direct form submission
            {
                'url': 'https://www.allthreezones.com/player-cards.html',
                'data': {
                    'login-email': Config.A3Z_USERNAME,
                    'login-password': Config.A3Z_PASSWORD
                }
            },
            # Attempt 2: Try the membership endpoint
            {
                'url': 'https://www.allthreezones.com/apps/member/login',
                'data': {
                    'login-email': Config.A3Z_USERNAME,
                    'login-password': Config.A3Z_PASSWORD
                }
            },
            # Attempt 3: Try with different field names
            {
                'url': 'https://www.allthreezones.com/player-cards.html',
                'data': {
                    'email': Config.A3Z_USERNAME,
                    'password': Config.A3Z_PASSWORD
                }
            }
        ]
        
        for i, attempt in enumerate(login_attempts):
            print(f"\n--- Attempt {i+1} ---")
            print(f"URL: {attempt['url']}")
            print(f"Data: {attempt['data']}")
            
            try:
                login_response = session.post(
                    attempt['url'],
                    data=attempt['data'],
                    headers=headers,
                    allow_redirects=True
                )
                
                print(f"Status: {login_response.status_code}")
                print(f"Final URL: {login_response.url}")
                
                # Check if we're still on login page
                if "Log In" in login_response.text:
                    print("❌ Still on login page")
                else:
                    print("✅ Successfully logged in!")
                    
                    # Try to access player cards
                    player_response = session.get("https://www.allthreezones.com/player-cards.html")
                    print(f"Player cards status: {player_response.status_code}")
                    
                    if "Log In" not in player_response.text:
                        print("✅ Successfully accessed player cards!")
                        
                        # Save the page
                        with open(f'player_cards_attempt_{i+1}.html', 'w', encoding='utf-8') as f:
                            f.write(player_response.text)
                        print(f"Saved to player_cards_attempt_{i+1}.html")
                        
                        # Look for player data
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(player_response.content, 'html.parser')
                        
                        # Look for tables
                        tables = soup.find_all('table')
                        print(f"Found {len(tables)} tables")
                        
                        # Look for any content that might be player data
                        page_text = soup.get_text().lower()
                        if any(keyword in page_text for keyword in ['player', 'stats', 'hockey', 'nhl']):
                            print("✅ Found player-related content!")
                        else:
                            print("⚠️  No player content found")
                        
                        return True
                    else:
                        print("❌ Still redirected to login")
                
            except Exception as e:
                print(f"Error in attempt {i+1}: {e}")
        
        print("\n❌ All login attempts failed")
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_form_login() 