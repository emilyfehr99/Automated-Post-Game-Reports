#!/usr/bin/env python3
"""
Test Database Integration - Shows what gets saved to SQL database
"""

import sqlite3
import json
from datetime import datetime

def test_database_integration():
    """Test what gets saved to the database"""
    
    print("🧪 TESTING DATABASE INTEGRATION")
    print("=" * 50)
    
    # Simulate captured data (like what would come from 4 AM capture)
    mock_captured_data = {
        "requests": [
            {
                "url": "https://www.hudl.com/app/metropole/shim/api-hockey.instatscout.com/data",
                "method": "POST",
                "headers": {"Authorization": "Bearer token123"},
                "body": {"proc": "scout_uni_overview_team_stat", "params": {"_p_team_id": 21479}}
            }
        ],
        "responses": [
            {
                "url": "https://www.hudl.com/app/metropole/shim/api-hockey.instatscout.com/data",
                "status": 200,
                "data": {
                    "data": [
                        {
                            "player_id": "test_player_1",
                            "name_eng": "Test Player 1",
                            "params": {
                                "goals": 15,
                                "assists": 20,
                                "points": 35
                            }
                        },
                        {
                            "player_id": "test_player_2", 
                            "name_eng": "Test Player 2",
                            "params": {
                                "goals": 8,
                                "assists": 12,
                                "points": 20
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    try:
        conn = sqlite3.connect('ajhl_comprehensive.db')
        cursor = conn.cursor()
        
        # Create daily_captures table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_captures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                capture_date TEXT NOT NULL,
                capture_time TEXT NOT NULL,
                team_id TEXT,
                requests_count INTEGER,
                responses_count INTEGER,
                raw_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert test capture
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        requests_count = len(mock_captured_data.get('requests', []))
        responses_count = len(mock_captured_data.get('responses', []))
        raw_data = json.dumps(mock_captured_data)
        
        cursor.execute('''
            INSERT INTO daily_captures 
            (capture_date, capture_time, team_id, requests_count, responses_count, raw_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d'),
            timestamp,
            '21479',  # Lloydminster Bobcats
            requests_count,
            responses_count,
            raw_data
        ))
        
        # Process and save test player data
        for response in mock_captured_data.get('responses', []):
            if response.get('status') == 200:
                response_data = response.get('data', {})
                if 'data' in response_data:
                    for item in response_data['data']:
                        if 'player_id' in item:
                            player_id = item.get('player_id', '')
                            name = item.get('name_eng', '')
                            team_id = '21479'
                            
                            if player_id and name:
                                # Check if player exists
                                cursor.execute("SELECT player_id FROM players WHERE player_id = ?", (player_id,))
                                exists = cursor.fetchone()
                                
                                if exists:
                                    # Update existing player
                                    cursor.execute('''
                                        UPDATE players 
                                        SET name = ?, last_updated = ?, metrics = ?
                                        WHERE player_id = ?
                                    ''', (
                                        name,
                                        datetime.now().isoformat(),
                                        json.dumps(item),
                                        player_id
                                    ))
                                else:
                                    # Insert new player
                                    cursor.execute('''
                                        INSERT INTO players (player_id, team_id, name, metrics, last_updated)
                                        VALUES (?, ?, ?, ?, ?)
                                    ''', (
                                        player_id,
                                        team_id,
                                        name,
                                        json.dumps(item),
                                        datetime.now().isoformat()
                                    ))
        
        conn.commit()
        
        # Show what was saved
        print("✅ TEST DATA SAVED TO DATABASE")
        print()
        
        # Show daily captures
        cursor.execute("SELECT * FROM daily_captures ORDER BY created_at DESC LIMIT 1")
        capture = cursor.fetchone()
        if capture:
            print("📅 DAILY CAPTURE RECORD:")
            print(f"   • Date: {capture[1]}")
            print(f"   • Time: {capture[2]}")
            print(f"   • Team ID: {capture[3]}")
            print(f"   • Requests: {capture[4]}")
            print(f"   • Responses: {capture[5]}")
            print(f"   • Created: {capture[7]}")
        
        print()
        
        # Show updated players
        cursor.execute("SELECT name, player_id, last_updated FROM players WHERE player_id LIKE 'test_%'")
        test_players = cursor.fetchall()
        if test_players:
            print("👥 TEST PLAYERS SAVED:")
            for player in test_players:
                print(f"   • {player[0]} (ID: {player[1]}) - Updated: {player[2]}")
        
        print()
        print("🎯 THIS IS EXACTLY WHAT HAPPENS AT 4 AM:")
        print("   • Network data captured from Hudl Instat")
        print("   • JSON files saved to daily_network_data/")
        print("   • SQL database updated with new data")
        print("   • Discord notification sent to your phone")
        print("   • All 189+ players updated with latest metrics")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_database_integration()
