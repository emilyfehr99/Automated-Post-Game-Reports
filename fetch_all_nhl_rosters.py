#!/usr/bin/env python3
"""
Fetch All NHL Rosters and Create Complete Player Database
This script fetches all NHL team rosters and creates a comprehensive player ID to name mapping
"""

import requests
import json
import time
import os

def fetch_team_roster(team_id):
    """Fetch roster for a specific team"""
    try:
        # Try multiple NHL API endpoints
        endpoints = [
            f"https://statsapi.web.nhl.com/api/v1/teams/{team_id}/roster",
            f"https://api-web.nhle.com/v1/teams/{team_id}/roster",
            f"https://api.nhle.com/stats/rest/en/teams/{team_id}/roster"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Successfully fetched roster for team {team_id} from {endpoint}")
                    return data
            except Exception as e:
                print(f"⚠️ Failed to fetch from {endpoint}: {e}")
                continue
        
        print(f"❌ Failed to fetch roster for team {team_id}")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching team {team_id}: {e}")
        return None

def extract_players_from_roster(roster_data, team_id):
    """Extract player information from roster data"""
    players = {}
    
    if not roster_data:
        return players
    
    # Try different roster data structures
    roster_sections = [
        roster_data.get('roster', []),
        roster_data.get('forwards', []),
        roster_data.get('defensemen', []),
        roster_data.get('goalies', []),
        roster_data.get('skaters', []),
        roster_data.get('players', [])
    ]
    
    for section in roster_sections:
        if isinstance(section, list):
            for player in section:
                player_id = player.get('person', {}).get('id') or player.get('id')
                if player_id:
                    # Extract name information
                    person = player.get('person', {})
                    full_name = person.get('fullName', '')
                    first_name = person.get('firstName', '')
                    last_name = person.get('lastName', '')
                    
                    # If no full name, construct from first and last
                    if not full_name and first_name and last_name:
                        full_name = f"{first_name} {last_name}"
                    
                    if full_name:
                        players[player_id] = {
                            'name': full_name,
                            'first_name': first_name,
                            'last_name': last_name,
                            'team_id': team_id,
                            'position': player.get('position', {}).get('code', 'Unknown')
                        }
    
    return players

def fetch_all_nhl_teams():
    """Fetch all NHL teams"""
    try:
        endpoints = [
            "https://statsapi.web.nhl.com/api/v1/teams",
            "https://api-web.nhle.com/v1/teams",
            "https://api.nhle.com/stats/rest/en/teams"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Successfully fetched teams from {endpoint}")
                    return data
            except Exception as e:
                print(f"⚠️ Failed to fetch teams from {endpoint}: {e}")
                continue
        
        return None
        
    except Exception as e:
        print(f"❌ Error fetching teams: {e}")
        return None

def main():
    """Main function to fetch all NHL rosters"""
    print("🏒 FETCHING ALL NHL ROSTERS 🏒")
    print("=" * 50)
    
    # NHL team IDs (all 32 teams)
    nhl_team_ids = [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10,  # Original 6 + expansion
        12, 13, 14, 15, 16, 17, 18, 19, 20, 21,  # More teams
        22, 23, 24, 25, 26, 28, 29, 30, 52, 53, 54, 55  # Rest of teams
    ]
    
    all_players = {}
    successful_teams = 0
    
    for team_id in nhl_team_ids:
        print(f"\n📥 Fetching roster for team {team_id}...")
        roster_data = fetch_team_roster(team_id)
        
        if roster_data:
            players = extract_players_from_roster(roster_data, team_id)
            all_players.update(players)
            successful_teams += 1
            print(f"   Found {len(players)} players")
        else:
            print(f"   ❌ Failed to fetch roster")
        
        time.sleep(0.5)  # Be nice to the API
    
    print(f"\n📊 SUMMARY:")
    print(f"   Teams processed: {successful_teams}/{len(nhl_team_ids)}")
    print(f"   Total players found: {len(all_players)}")
    
    # Save to JSON file
    output_file = "nhl_players_database.json"
    with open(output_file, 'w') as f:
        json.dump(all_players, f, indent=2)
    
    print(f"✅ Player database saved to {output_file}")
    
    # Show sample of players
    print(f"\n🔍 SAMPLE PLAYERS:")
    sample_count = 0
    for player_id, player_data in all_players.items():
        if sample_count < 10:
            print(f"   {player_id}: {player_data['name']} ({player_data.get('position', 'Unknown')})")
            sample_count += 1
    
    return all_players

if __name__ == "__main__":
    main()
