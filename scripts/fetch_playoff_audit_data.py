import requests
import json
import time

BASE_URL = "https://api-web.nhle.com/v1"

def fetch_standings(date):
    url = f"{BASE_URL}/standings/{date}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_bracket(year):
    url = f"{BASE_URL}/playoff-bracket/{year}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_playoff_audit_data():
    audit_data = {
        "2022_2023": {
            "regular_season": None,
            "playoffs": None
        },
        "2023_2024": {
            "regular_season": None,
            "playoffs": None
        }
    }
    
    # 2022-2023 Season (Ended around April 14, 2023)
    print("Fetching 2022-23 regular season standings...")
    audit_data["2022_2023"]["regular_season"] = fetch_standings("2023-04-14")
    time.sleep(1)
    print("Fetching 2023 playoff bracket...")
    audit_data["2022_2023"]["playoffs"] = fetch_bracket("2022") # Series for 2022-23 season
    time.sleep(1)
    
    # 2023-2024 Season (Ended around April 18, 2024)
    print("Fetching 2023-24 regular season standings...")
    audit_data["2023_2024"]["regular_season"] = fetch_standings("2024-04-18")
    time.sleep(1)
    print("Fetching 2024 playoff bracket...")
    audit_data["2023_2024"]["playoffs"] = fetch_bracket("2023") # Series for 2023-24 season
    
    with open("data/playoff_audit_data.json", "w") as f:
        json.dump(audit_data, f, indent=2)
    print("Data saved to data/playoff_audit_data.json")

if __name__ == "__main__":
    get_playoff_audit_data()
