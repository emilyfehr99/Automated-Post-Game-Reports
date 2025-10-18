import requests

print("🏒 NHL API Quick Test 🏒")
print("=" * 30)

# Test Florida Panthers team info
print("\n1. Florida Panthers Team Info:")
url = "https://api-web.nhle.com/v1/teams/13"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print(f"   Name: {data.get('name', 'N/A')}")
    print(f"   Abbrev: {data.get('abbrev', 'N/A')}")
    print(f"   Conference: {data.get('conferenceName', 'N/A')}")
    print(f"   Division: {data.get('divisionName', 'N/A')}")
else:
    print(f"   Failed: {response.status_code}")

# Test team roster
print("\n2. Florida Panthers Roster:")
url = "https://api-web.nhle.com/v1/teams/13/roster"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print(f"   Forwards: {len(data.get('forwards', []))}")
    print(f"   Defensemen: {len(data.get('defensemen', []))}")
    print(f"   Goalies: {len(data.get('goalies', []))}")
else:
    print(f"   Failed: {response.status_code}")

# Test standings
print("\n3. League Standings:")
url = "https://api-web.nhle.com/v1/standings/now"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print(f"   Teams in standings: {len(data.get('standings', []))}")
else:
    print(f"   Failed: {response.status_code}")

print("\n✅ API test completed!")
