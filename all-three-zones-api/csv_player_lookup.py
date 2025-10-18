#!/usr/bin/env python3
"""
Fast CSV Player Lookup
Works directly with the downloaded CSV data - no API needed
"""

import pandas as pd
import json
import random

def load_csv_data():
    """Load the CSV data with real player stats"""
    
    print("📊 Loading All Three Zones CSV data...")
    
    try:
        # Read the CSV file
        df = pd.read_csv('Sheet 1_data.csv')
        
        print(f"✅ Loaded {len(df)} rows of data")
        print(f"📋 Columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return None

def get_player_stats_from_csv(player_name, df):
    """Get player stats from CSV data"""
    
    print(f"🏒 Getting {player_name} stats from CSV...")
    print("=" * 50)
    
    # Filter data for this player
    player_data = df[df['Player'] == player_name]
    
    if len(player_data) > 0:
        print(f"✅ Found {len(player_data)} records for {player_name}")
        print()
        
        # Get unique stats for this player
        unique_stats = player_data.groupby(['Pivot Field Names (group)', 'Pivot Field Names']).agg({
            'Pivot Field Values': 'first',
            'Team1': 'first',
            '5v5 TOI': 'first'
        }).reset_index()
        
        print(f"Name: {player_name}")
        print(f"Team: {unique_stats['Team1'].iloc[0]}")
        print(f"5v5 TOI: {unique_stats['5v5 TOI'].iloc[0]:.1f} minutes")
        print()
        
        # Display stats by category
        for _, row in unique_stats.iterrows():
            category = row['Pivot Field Names (group)']
            stat_name = row['Pivot Field Names']
            value = row['Pivot Field Values']
            
            print(f"📊 {category} - {stat_name}: {value:.3f}")
        
        print(f"\n✅ {player_name} stats retrieved from CSV!")
        print(" This is REAL data from All Three Zones!")
        
    else:
        print(f"❌ {player_name} not found in CSV data")
        print("📋 Available players include:")
        
        # Show some available players
        available_players = df['Player'].unique()[:10]
        for player in available_players:
            print(f"   - {player}")
        print(f"   ... and {len(df['Player'].unique()) - 10} more players")

def search_players_in_csv(search_term, df):
    """Search for players in CSV data"""
    
    print(f"🔍 Searching for players containing '{search_term}'...")
    print("=" * 50)
    
    # Find players that match the search term
    matching_players = df[df['Player'].str.contains(search_term, case=False, na=False)]['Player'].unique()
    
    if len(matching_players) > 0:
        print(f"✅ Found {len(matching_players)} matching players:")
        for player in matching_players:
            print(f"   - {player}")
    else:
        print(f"❌ No players found containing '{search_term}'")

def main():
    """Main function"""
    
    print("🏒 FAST CSV PLAYER LOOKUP")
    print("=" * 50)
    
    # Load CSV data
    df = load_csv_data()
    
    if df is None:
        print("❌ Could not load CSV data")
        return
    
    # 🎯 ENTER ANY PLAYER NAME HERE!
    player_name = "Sidney Crosby"  # <-- Change this to any player you want!
    
    # Get player stats from CSV
    get_player_stats_from_csv(player_name, df)
    
    print("\n" + "=" * 50)
    print("💡 To search for players, use:")
    print("   search_players_in_csv('Crosby', df)")

if __name__ == "__main__":
    main()























