#!/usr/bin/env python3
"""
Debug script to examine authenticated All Three Zones page structure
"""

import requests
from bs4 import BeautifulSoup
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def examine_authenticated_page():
    """Examine the authenticated page structure"""
    try:
        # Create a session and login
        session = requests.Session()
        
        # Get the login page first
        login_url = "https://www.allthreezones.com/player-cards.html"
        response = session.get(login_url)
        
        # Import config for credentials
        from config import Config
        
        # Prepare login data
        login_data = {
            'login-email': Config.A3Z_USERNAME,
            'login-password': Config.A3Z_PASSWORD,
        }
        
        # Set headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.allthreezones.com',
            'Referer': 'https://www.allthreezones.com/player-cards.html'
        }
        
        # Try to login
        login_response = session.post(
            'https://www.allthreezones.com/ajax/api/JsonRPC/Membership/',
            data=login_data,
            headers=headers,
            allow_redirects=True
        )
        
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response URL: {login_response.url}")
        
        # Now get the player cards page
        player_cards_url = "https://www.allthreezones.com/player-cards.html"
        player_response = session.get(player_cards_url)
        
        print(f"\nPlayer cards response status: {player_response.status_code}")
        print(f"Player cards response URL: {player_response.url}")
        
        soup = BeautifulSoup(player_response.content, 'html.parser')
        
        # Save the authenticated page
        with open('authenticated_page.html', 'w', encoding='utf-8') as f:
            f.write(player_response.text)
        print(f"\nSaved authenticated page to authenticated_page.html")
        
        # Look for player-related content
        print(f"\nPage title: {soup.title.get_text() if soup.title else 'No title'}")
        
        # Look for tables
        tables = soup.find_all('table')
        print(f"\nFound {len(tables)} tables")
        
        for i, table in enumerate(tables):
            print(f"\nTable {i+1}:")
            rows = table.find_all('tr')
            print(f"  Rows: {len(rows)}")
            if rows:
                # Show first few rows
                for j, row in enumerate(rows[:3]):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    print(f"    Row {j+1}: {cell_texts}")
        
        # Look for div elements with player-related classes
        player_divs = soup.find_all('div', class_=lambda x: x and any(word in x.lower() for word in ['player', 'card', 'stat', 'data']))
        print(f"\nFound {len(player_divs)} player-related divs")
        
        for i, div in enumerate(player_divs[:5]):  # Show first 5
            class_names = div.get('class', [])
            text = div.get_text(strip=True)[:100]  # First 100 chars
            print(f"  Div {i+1} classes: {class_names}")
            print(f"  Text: {text}")
        
        # Look for any text that might be player names
        player_keywords = ['mcdavid', 'crosby', 'ovechkin', 'matthews', 'mackinnon', 'draisaitl']
        for keyword in player_keywords:
            elements = soup.find_all(text=lambda text: text and keyword.lower() in text.lower())
            if elements:
                print(f"\nFound '{keyword}' in {len(elements)} elements")
                for elem in elements[:3]:
                    print(f"  '{elem.strip()}'")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    examine_authenticated_page() 