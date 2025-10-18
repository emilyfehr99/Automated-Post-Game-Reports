#!/usr/bin/env python3
"""
Database Summary - Shows what gets saved to SQL database
"""

import sqlite3
import json
from datetime import datetime

def show_database_summary():
    """Show what's currently in the database and what will be saved"""
    
    print("🗄️  SQL DATABASE SUMMARY")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('ajhl_comprehensive.db')
        cursor = conn.cursor()
        
        # Show current tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 TABLES IN DATABASE:")
        for table in tables:
            print(f"   • {table[0]}")
        
        print()
        
        # Show players table info
        cursor.execute("SELECT COUNT(*) FROM players")
        player_count = cursor.fetchone()[0]
        print(f"👥 PLAYERS IN DATABASE: {player_count}")
        
        if player_count > 0:
            cursor.execute("SELECT name, player_id, last_updated FROM players LIMIT 5")
            players = cursor.fetchall()
            print("   Recent players:")
            for player in players:
                print(f"   • {player[0]} (ID: {player[1]}) - Updated: {player[2]}")
        
        print()
        
        # Show daily_captures table (if it exists)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_captures';")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM daily_captures")
            capture_count = cursor.fetchone()[0]
            print(f"📅 DAILY CAPTURES: {capture_count}")
            
            if capture_count > 0:
                cursor.execute("SELECT capture_date, capture_time, requests_count, responses_count FROM daily_captures ORDER BY created_at DESC LIMIT 3")
                captures = cursor.fetchall()
                print("   Recent captures:")
                for capture in captures:
                    print(f"   • {capture[0]} {capture[1]} - {capture[2]} requests, {capture[3]} responses")
        else:
            print("📅 DAILY CAPTURES: Table will be created on first run")
        
        print()
        
        # Show what gets saved daily
        print("🚀 WHAT GETS SAVED DAILY AT 4 AM:")
        print("   📁 JSON Files:")
        print("      • Complete network data (requests + responses)")
        print("      • Individual API responses as text files")
        print("   🗄️  SQL Database:")
        print("      • daily_captures table: Capture metadata")
        print("      • players table: Updated player data")
        print("      • Raw API responses stored as JSON")
        print("      • Player metrics and statistics")
        
        print()
        print("📱 NOTIFICATIONS:")
        print("   • Discord message sent to your phone")
        print("   • Push notification on Discord app")
        print("   • Success confirmation with data counts")
        
        print()
        print("🎯 DATA LOCATIONS:")
        print("   • SQL Database: ajhl_comprehensive.db")
        print("   • JSON Files: daily_network_data/ folder")
        print("   • Discord: Your configured channel")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

if __name__ == "__main__":
    show_database_summary()
