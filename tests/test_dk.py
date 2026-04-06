import requests

url = "https://sportsbook-us-co.draftkings.com//sites/US-CO-SB/api/v5/eventgroups/42133"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}
try:
    r = requests.get(url, headers=headers)
    print("Status:", r.status_code)
    data = r.json()
    events = data.get('eventGroup', {}).get('events', [])
    print(f"Found {len(events)} events")
    for event in events:
         print(event.get('name'))
except Exception as e:
    print(e)
