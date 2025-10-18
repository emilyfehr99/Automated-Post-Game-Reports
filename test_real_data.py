#!/usr/bin/env python3
"""
Test real NHL data and generate a working report
"""

import requests
from datetime import datetime

def test_nhl_data():
    print('🏒 Testing Real NHL Data 🏒')
    print('=' * 40)
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    # Test team roster (we know this works)
    print('Testing team roster API...')
    try:
        url = 'https://api-web.nhle.com/v1/roster/EDM/20242025'
        response = session.get(url, timeout=10)
        print(f'Roster API status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ Roster API working!')
            data = response.json()
            print(f'Found {len(data)} players in Edmonton roster')
            
            # Show first few players
            for i, player in enumerate(data[:3]):
                name = player.get('fullName', 'Unknown')
                position = player.get('position', 'Unknown')
                print(f'  {i+1}. {name} - {position}')
            
            return True
        else:
            print('❌ Roster API failed')
            return False
            
    except Exception as e:
        print(f'Error: {e}')
        return False

def create_working_report():
    """Create a working report with real data"""
    print('\n📊 Creating Working NHL Report...')
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    # Get real team data
    teams = ['EDM', 'FLA', 'TOR', 'BOS']
    team_data = {}
    
    for team in teams:
        try:
            url = f'https://api-web.nhle.com/v1/roster/{team}/20242025'
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                team_data[team] = data
                print(f'✅ Got {team} roster: {len(data)} players')
        except:
            print(f'❌ Failed to get {team} roster')
    
    if team_data:
        print(f'\n🎉 SUCCESS! Got real data for {len(team_data)} teams')
        print('This proves the NHL API is working with real data!')
        
        # Show some stats
        for team, players in team_data.items():
            positions = {}
            for player in players:
                pos = player.get('position', 'Unknown')
                positions[pos] = positions.get(pos, 0) + 1
            
            print(f'\n{team} Team Composition:')
            for pos, count in positions.items():
                print(f'  {pos}: {count} players')
        
        return True
    else:
        print('❌ No team data retrieved')
        return False

if __name__ == "__main__":
    success = test_nhl_data()
    if success:
        create_working_report()
    
    print('\n🏒 NHL API Test Complete! 🏒')
