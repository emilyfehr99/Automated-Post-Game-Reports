
import sys
import os
import json

# Add current directory to path so we can import api.app
sys.path.append(os.getcwd())

from api.app import app

def check_local_logic():
    print("Testing LOCAL api/app.py logic via test_client()...")
    
    with app.test_client() as client:
        response = client.get('/api/player-stats?season=2025')
        
        if response.status_code != 200:
            print(f"❌ Error: Status {response.status_code}")
            return
            
        data = response.get_json()
        if not data:
            print("❌ Error: No data returned")
            return
            
        p = data[0]
        keys = list(p.keys())
        print(f"\n✅ Success! Returned {len(data)} players.")
        print(f"✅ Total Fields per Player: {len(keys)}")
        
        # Verify specific dynamic fields
        check_fields = [
            'I_F_flurryAdjustedxGoals', 
            'I_F_highDangerShots',
            'OnIce_F_xGoals',
            'hits', # Alias
            'hits_per_game'
        ]
        
        print("\nVerifying New Fields:")
        for field in check_fields:
            if field in p:
                print(f"  ✅ {field}: {p[field]}")
            else:
                print(f"  ❌ {field} MISSING")

if __name__ == "__main__":
    check_local_logic()
