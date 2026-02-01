
import sys
import os
import json

# Add current directory to path
sys.path.append(os.getcwd())

from api.app import app

def check_metrics():
    print("Testing /api/team-metrics endpoint...")
    
    with app.test_client() as client:
        response = client.get('/api/team-metrics')
        
        if response.status_code != 200:
            print(f"❌ Error: Status {response.status_code}")
            return
            
        data = response.get_json()
        if not data:
            print("❌ Error: No data returned")
            return
            
        print(f"Returned metrics for {len(data)} teams.")
        
        for team in ['BOS', 'DAL', 'COL']:
            print(f"\n--- {team} ---")
            if team not in data:
                print("❌ MISSING in response")
                continue
                
            m = data[team]
            print(f"lat: {m.get('lat')}")
            print(f"long_movement: {m.get('long_movement')}")
            print(f"xg: {m.get('xg')}")
            print(f"hdc: {m.get('hdc')}")
            print(f"hits: {m.get('hits')}")
            print(f"cf%: {m.get('corsi_pct')}")

if __name__ == "__main__":
    check_metrics()
