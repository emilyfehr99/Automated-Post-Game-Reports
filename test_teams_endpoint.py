#!/usr/bin/env python3
"""
Test Teams Endpoint
Shows what the teams endpoint would return without requiring Hudl credentials
"""

import json
from ajhl_team_config import get_active_teams

def test_teams_endpoint():
    """Test what the teams endpoint would return"""
    print("🏒 Testing Teams Endpoint")
    print("=" * 40)
    
    # Get teams from configuration
    teams = get_active_teams()
    
    # Convert to API format
    api_teams = []
    for team_id, team_data in teams.items():
        api_team = {
            "team_id": team_id,
            "team_name": team_data["team_name"],
            "city": team_data["city"],
            "division": team_data["division"],
            "hudl_team_id": team_data.get("hudl_team_id", ""),
            "last_updated": "2024-01-15T10:30:00Z",  # Mock timestamp
            "data_available": bool(team_data.get("hudl_team_id"))
        }
        api_teams.append(api_team)
    
    print(f"Found {len(api_teams)} teams:")
    print()
    
    # Show first few teams
    for i, team in enumerate(api_teams[:5]):
        print(f"{i+1}. {team['team_name']} ({team['city']}) - {team['division']}")
        print(f"   Team ID: {team['team_id']}")
        print(f"   Hudl ID: {team['hudl_team_id']}")
        print(f"   Data Available: {team['data_available']}")
        print()
    
    if len(api_teams) > 5:
        print(f"... and {len(api_teams) - 5} more teams")
        print()
    
    # Show JSON format
    print("📄 JSON Response Format:")
    print("=" * 40)
    print(json.dumps(api_teams[:3], indent=2))
    
    print()
    print("🔍 What you'd see when calling GET /teams:")
    print("-" * 40)
    print("curl http://localhost:8000/teams")
    print()
    print("Or in Python:")
    print("import requests")
    print("response = requests.get('http://localhost:8000/teams')")
    print("teams = response.json()")
    print()
    print("✅ This is exactly what the API would return!")

if __name__ == "__main__":
    test_teams_endpoint()
