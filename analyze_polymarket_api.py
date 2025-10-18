#!/usr/bin/env python3
"""
Analyze Polymarket API to understand the real data structure
"""

import requests
import json
from datetime import datetime

def analyze_polymarket_api():
    """Analyze the real Polymarket API response"""
    
    print("🔍 Analyzing Polymarket API...")
    
    # Try the API endpoint that was working
    endpoint = "https://clob.polymarket.com/markets"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"📡 Fetching from: {endpoint}")
        response = requests.get(endpoint, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Got {type(data)} with keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
            
            # Get the markets
            if isinstance(data, dict) and 'data' in data:
                markets = data['data']
                print(f"📊 Found {len(markets)} markets")
                
                # Analyze first few markets
                print("\n🔍 Analyzing first 5 markets:")
                for i, market in enumerate(markets[:5]):
                    print(f"\n--- Market {i+1} ---")
                    print(f"Type: {type(market)}")
                    print(f"Keys: {list(market.keys()) if isinstance(market, dict) else 'Not a dict'}")
                    
                    if isinstance(market, dict):
                        # Show key fields
                        for key in ['question', 'questionText', 'endDate', 'end_date', 'endTime', 'end_time', 'category', 'price', 'currentPrice', 'liquidity', 'volume']:
                            if key in market:
                                value = market[key]
                                print(f"  {key}: {type(value).__name__} = {str(value)[:100]}...")
                
                # Look for current vs old markets
                print(f"\n📅 Analyzing market dates and questions...")
                current_count = 0
                old_count = 0
                
                for market in markets[:20]:  # Check first 20
                    if isinstance(market, dict):
                        question = market.get('question', market.get('questionText', ''))
                        end_date = market.get('endDate', market.get('end_date', market.get('endTime', market.get('end_time', ''))))
                        
                        question_str = str(question).lower()
                        date_str = str(end_date)
                        
                        # Check if it's old
                        if any(year in question_str for year in ['2022', '2023']) or any(year in date_str for year in ['2022', '2023']):
                            old_count += 1
                            print(f"  ❌ OLD: {question[:80]}...")
                        elif any(year in question_str for year in ['2025', '2026', '2027', '2028']) or any(year in date_str for year in ['2025', '2026', '2027', '2028']):
                            current_count += 1
                            print(f"  ✅ CURRENT: {question[:80]}...")
                        else:
                            print(f"  ❓ UNKNOWN: {question[:80]}...")
                
                print(f"\n📊 Summary of first 20 markets:")
                print(f"  Current (2025+): {current_count}")
                print(f"  Old (2022-2023): {old_count}")
                print(f"  Unknown: {20 - current_count - old_count}")
                
                # Save sample data to file
                with open('polymarket_sample_data.json', 'w') as f:
                    json.dump(markets[:10], f, indent=2)
                print(f"\n💾 Saved sample data to polymarket_sample_data.json")
                
            else:
                print("❌ Unexpected data structure")
                print(f"Data: {data}")
                
        else:
            print(f"❌ API returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_polymarket_api()
