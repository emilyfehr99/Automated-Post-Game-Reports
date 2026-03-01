import requests
import json

url = "https://www.bovada.lv/services/sports/content/v1/events/A/description/hockey/nhl"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    data = r.json()
    events = data[0].get('events', [])
    print(f"Events: {len(events)}")
    for e in events[:2]:
        print(f"  {e.get('description')} ({e.get('id')})")
        
        markets = e.get('displayGroups', [{}])[0].get('markets', [])
        ml_market = next((m for m in markets if m.get('description') == 'Moneyline'), None)
        if ml_market:
            outcomes = ml_market.get('outcomes', [])
            for o in outcomes:
                print(f"    {o.get('description')}: {o.get('price', {}).get('american')}")
except Exception as e:
    print(f"Error parsing bovada: {e}")
