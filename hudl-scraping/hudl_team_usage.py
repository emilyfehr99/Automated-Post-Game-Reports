#!/usr/bin/env python3
"""
Hudl Instat Team Usage Example
Shows how your team can use the shared Hudl account without conflicts
"""

import json
import time
from hudl_multi_user_manager import HudlMultiUserManager

def main():
    """Example of how your team can use the shared Hudl account"""
    print("🏒 Hudl Instat Team Usage Example")
    print("=" * 50)
    
    # Initialize the multi-user manager
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD, TEAM_MEMBERS
        manager = HudlMultiUserManager(HUDL_USERNAME, HUDL_PASSWORD)
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
        return
    
    print("👥 Team Members:")
    for user_id, name in TEAM_MEMBERS.items():
        print(f"  - {user_id}: {name}")
    
    # Example: Emily (you) accessing team data
    print(f"\n👤 Emily accessing team data...")
    team_id = "21479"
    
    # Get team info
    team_info = manager.get_team_info("emily", team_id)
    print(f"Team Info: {json.dumps(team_info, indent=2)}")
    
    # Get players
    players = manager.get_team_players("emily", team_id)
    print(f"Found {len(players)} players")
    
    # Example: Coach accessing the same data (won't conflict)
    print(f"\n👤 Coach accessing team data...")
    coach_team_info = manager.get_team_info("coach1", team_id)
    print(f"Coach got team info: {coach_team_info.get('team_name', 'Unknown')}")
    
    # Show current session status
    print(f"\n📊 Current Session Status:")
    status = manager.get_session_status()
    print(json.dumps(status, indent=2))
    
    # Clean up
    manager.close_all_sessions()
    print("\n✅ All sessions closed")

if __name__ == "__main__":
    main()
