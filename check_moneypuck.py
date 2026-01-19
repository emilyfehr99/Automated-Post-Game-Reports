import requests

def check_url(season):
    url = f"https://moneypuck.com/moneypuck/playerData/seasonSummary/{season}/regular/skaters.csv"
    print(f"Checking {url}...")
    try:
        r = requests.head(url, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            # Check content length or first few bytes
            r_get = requests.get(url, stream=True)
            chunk = next(r_get.iter_content(chunk_size=100))
            print(f"Content Start: {chunk}")
            return True
    except Exception as e:
        print(f"Error: {e}")
    return False

print("--- Checking Season 2024 (2024-2025) ---")
check_url('2024')

print("\n--- Checking Season 2025 (2025-2026) ---")
check_url('2025')
