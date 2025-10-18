#!/usr/bin/env python3
"""
Debug script to examine All Three Zones login page structure
"""

import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def examine_login_page():
    """Examine the login page structure"""
    try:
        # Get the login page
        url = "https://www.allthreezones.com/player-cards.html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"URL: {response.url}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for form elements
        forms = soup.find_all('form')
        print(f"\nFound {len(forms)} forms:")
        
        for i, form in enumerate(forms):
            print(f"\nForm {i+1}:")
            print(f"  Action: {form.get('action', 'No action')}")
            print(f"  Method: {form.get('method', 'No method')}")
            
            # Look for input fields
            inputs = form.find_all('input')
            print(f"  Input fields:")
            for inp in inputs:
                input_type = inp.get('type', 'text')
                input_name = inp.get('name', 'No name')
                input_id = inp.get('id', 'No id')
                print(f"    Type: {input_type}, Name: {input_name}, ID: {input_id}")
        
        # Look for buttons
        buttons = soup.find_all('button')
        print(f"\nFound {len(buttons)} buttons:")
        for button in buttons:
            button_text = button.get_text(strip=True)
            button_type = button.get('type', 'No type')
            print(f"  Text: '{button_text}', Type: {button_type}")
        
        # Look for any login-related text
        login_texts = soup.find_all(text=lambda text: text and 'login' in text.lower())
        print(f"\nLogin-related text:")
        for text in login_texts:
            print(f"  '{text.strip()}'")
        
        # Save the page content for inspection
        with open('login_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\nSaved page content to login_page.html")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    examine_login_page() 