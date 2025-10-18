#!/usr/bin/env python3
"""
Test script for AJHL Season CSV Download
Tests the 2025-2026 season CSV download functionality
"""

import requests
import json
import time
from datetime import datetime

# API configuration
API_BASE_URL = "http://localhost:8005"
API_KEY = "test_key_123"

def test_api_endpoint(endpoint: str, method: str = "GET", data: dict = None):
    """Test an API endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"\n{'='*60}")
        print(f"Testing: {method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing Health Check...")
    result = test_api_endpoint("/health")
    
    if result:
        print(f"Status: {result.get('status', 'Unknown')}")
        print(f"Database available: {result.get('database_available', False)}")
        print(f"Teams in DB: {result.get('teams_in_db', 0)}")
        print(f"Players in DB: {result.get('players_in_db', 0)}")
    
    return result is not None

def test_all_teams():
    """Test getting all teams"""
    print("\n🏒 Testing All Teams...")
    result = test_api_endpoint("/teams")
    
    if result and result.get('success'):
        teams = result.get('teams', [])
        print(f"Total teams: {result.get('total_teams', 0)}")
        print(f"Teams with data: {result.get('teams_with_data', 0)}")
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        
        print(f"\nAll AJHL Teams:")
        for i, team in enumerate(teams, 1):
            print(f"  {i:2d}. {team.get('team_name', 'Unknown')} ({team.get('team_id', 'Unknown')})")
    
    return result is not None

def test_season_csv_download():
    """Test the season CSV download endpoint"""
    print("\n📥 Testing Season CSV Download...")
    print("⚠️  WARNING: This will attempt to download CSV data from Hudl Instat")
    print("⚠️  This requires valid Hudl credentials and may take several minutes")
    
    # Ask for confirmation
    response = input("\nDo you want to proceed with the CSV download? (y/N): ")
    if response.lower() != 'y':
        print("❌ CSV download cancelled by user")
        return False
    
    result = test_api_endpoint("/download/season-csv", method="POST")
    
    if result and result.get('success'):
        print(f"✅ Season CSV download completed!")
        print(f"Season: {result.get('season', 'Unknown')}")
        print(f"Total teams: {result.get('total_teams', 0)}")
        print(f"Successful downloads: {result.get('successful_downloads', 0)}")
        print(f"Failed downloads: {result.get('failed_downloads', 0)}")
        print(f"Data source: {result.get('data_source', 'Unknown')}")
        
        # Show results for each team
        results = result.get('results', {})
        if results:
            print(f"\nTeam Results:")
            for team_id, team_result in results.items():
                team_name = team_result.get('team_name', 'Unknown')
                success = team_result.get('success', False)
                status = "✅ Success" if success else "❌ Failed"
                error = team_result.get('error', '')
                print(f"  {team_name}: {status}")
                if error:
                    print(f"    Error: {error}")
    else:
        print(f"❌ Season CSV download failed")
        if result:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    return result is not None

def test_team_metrics_after_download():
    """Test team metrics after CSV download"""
    print("\n📊 Testing Team Metrics After Download...")
    
    # Test a few teams
    test_teams = ["Lloydminster Bobcats", "Brooks Bandits", "Okotoks Oilers"]
    
    for team_name in test_teams:
        print(f"\n🏒 Testing {team_name} metrics...")
        result = test_api_endpoint(f"/teams/name/{team_name}/metrics")
        
        if result:
            if result.get('success'):
                print(f"✅ Metrics available for {team_name}")
                # Would show actual metrics here
            else:
                print(f"ℹ️  {result.get('message', 'No message')}")
                print(f"Data source: {result.get('data_source', 'Unknown')}")

def main():
    """Run the season CSV download test"""
    print("🧪 AJHL Season CSV Download Test Suite")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"API Key: {API_KEY}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if API is running
    print("🔍 Checking if API is running...")
    health = test_api_endpoint("/health")
    if not health:
        print("❌ API is not running or not accessible")
        print("Please start the API server first:")
        print("  python ajhl_direct_site_api.py")
        return
    
    print("✅ API is running!")
    print()
    
    # Test basic functionality
    test_health_check()
    test_all_teams()
    
    # Test season CSV download
    csv_success = test_season_csv_download()
    
    # Test metrics after download
    if csv_success:
        test_team_metrics_after_download()
    
    print(f"\n🎉 Season CSV download test completed!")
    print(f"Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
