#!/usr/bin/env python3
"""
Test script for Hudl Instat Analyzer
Demonstrates how to use the analyzer and mini API
"""

import json
import sys
import os
from hudl_instat_analyzer import HudlInstatAnalyzer, HudlInstatMiniAPI

def test_site_analysis():
    """Test the site structure analysis without authentication"""
    print("🔍 Testing Hudl Instat Site Analysis")
    print("=" * 50)
    
    analyzer = HudlInstatAnalyzer(headless=True)
    
    try:
        # Analyze the team page structure
        team_id = "21479"
        analysis = analyzer.analyze_site_structure(team_id)
        
        print(f"\n📊 Analysis Results for Team {team_id}:")
        print(json.dumps(analysis, indent=2))
        
        # Check if authentication is required
        if analysis.get("requires_auth"):
            print("\n🔒 Authentication Required")
            print("To access team data, you'll need valid Hudl credentials")
            print("Contact Hudl about official API access for best results")
        else:
            print("\n✅ Site structure analyzed successfully")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
    finally:
        analyzer.close()

def test_with_credentials():
    """Test with credentials (if provided)"""
    print("\n🔐 Testing with Credentials")
    print("=" * 50)
    
    # Get credentials from environment, credentials file, or user input
    username = os.getenv('HUDL_USERNAME')
    password = os.getenv('HUDL_PASSWORD')
    
    # Try to import from credentials file
    if not username or not password:
        try:
            from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
            username = HUDL_USERNAME
            password = HUDL_PASSWORD
        except ImportError:
            pass
    
    if not username or not password or username == "your_username_here":
        print("⚠️  No valid credentials found")
        print("Please update hudl_credentials.py with your actual Hudl credentials")
        print("Or set HUDL_USERNAME and HUDL_PASSWORD environment variables")
        return
    
    api = HudlInstatMiniAPI(username, password)
    
    if api.authenticated:
        print("✅ Successfully authenticated")
        
        # Test getting team info
        team_id = "21479"
        team_info = api.get_team_info(team_id)
        print(f"\nTeam Info: {json.dumps(team_info, indent=2)}")
        
        # Test getting players
        players = api.get_team_players(team_id)
        print(f"\nPlayers found: {len(players)}")
        
    else:
        print("❌ Authentication failed")
    
    api.close()

def main():
    """Main test function"""
    print("🏒 Hudl Instat Analyzer Test Suite")
    print("=" * 60)
    
    # Test 1: Site analysis without authentication
    test_site_analysis()
    
    # Test 2: Test with credentials if available
    test_with_credentials()
    
    print("\n" + "=" * 60)
    print("📋 Summary:")
    print("1. The analyzer can examine site structure without authentication")
    print("2. Full data extraction requires valid Hudl credentials")
    print("3. Consider contacting Hudl about official API access")
    print("4. Always respect Hudl's Terms of Service")

if __name__ == "__main__":
    main()
