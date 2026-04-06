import requests
import json
import time

url = "https://sportsbook.draftkings.com/api/odds/v1/leagues/42133/offers/gamelines.json"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}
r = requests.get(url, headers=headers)
data = r.json()

print("Top level keys:", list(data.keys()))
if 'events' in data:
    for e in data['events'][:2]:
        print(f"\nEvent: {e.get('name')}")
        
if 'offers' in data:
    print(f"\nOffers sample: {data['offers'][:2]}")
