#!/usr/bin/env python3
"""
Get the REAL logo URLs from the NHL API
"""

import requests
import json

def get_real_logo_urls():
    """Get the actual logo URLs from NHL API"""
    print("🏒 GETTING REAL LOGO URLS FROM NHL API 🏒")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    # Get standings data which has teamLogo field
    standings_url = "https://api-web.nhle.com/v1/standings/now"
    
    try:
        response = session.get(standings_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            print("📊 Found standings data with team logos:")
            print()
            
            # Look for teams in the data
            if 'standings' in data:
                for conference in data['standings']:
                    if 'teamRecords' in conference:
                        for team in conference['teamRecords'][:4]:  # Just show first 4 teams
                            team_info = team.get('team', {})
                            team_name = team_info.get('abbrev', 'Unknown')
                            team_logo = team_info.get('teamLogo', '')
                            
                            print(f"🏒 {team_name}:")
                            print(f"   Logo URL: {team_logo}")
                            
                            if team_logo:
                                # Test if the logo URL works
                                try:
                                    logo_response = session.head(team_logo, timeout=5)
                                    if logo_response.status_code == 200:
                                        content_type = logo_response.headers.get('content-type', 'unknown')
                                        content_length = logo_response.headers.get('content-length', 'unknown')
                                        print(f"   ✅ Logo works! Type: {content_type}, Size: {content_length}")
                                    else:
                                        print(f"   ❌ Logo failed: {logo_response.status_code}")
                                except Exception as e:
                                    print(f"   ❌ Logo error: {e}")
                            print()
            
            # Also check schedule data for imageUrl
            print("\n" + "="*50)
            print("📅 CHECKING SCHEDULE DATA FOR IMAGE URLS")
            print("="*50)
            
            schedule_url = "https://api-web.nhle.com/v1/schedule/now"
            response = session.get(schedule_url, timeout=10)
            if response.status_code == 200:
                schedule_data = response.json()
                
                if 'gameWeek' in schedule_data and len(schedule_data['gameWeek']) > 0:
                    games = schedule_data['gameWeek'][0].get('games', [])
                    if games:
                        game = games[0]  # Get first game
                        away_team = game.get('awayTeam', {})
                        home_team = game.get('homeTeam', {})
                        
                        print(f"Away Team: {away_team.get('abbrev', 'Unknown')}")
                        print(f"  Image URL: {away_team.get('imageUrl', 'None')}")
                        
                        print(f"Home Team: {home_team.get('abbrev', 'Unknown')}")
                        print(f"  Image URL: {home_team.get('imageUrl', 'None')}")
                        
                        # Test these image URLs
                        for team_name, team_data in [("Away", away_team), ("Home", home_team)]:
                            image_url = team_data.get('imageUrl', '')
                            if image_url:
                                try:
                                    img_response = session.head(image_url, timeout=5)
                                    if img_response.status_code == 200:
                                        content_type = img_response.headers.get('content-type', 'unknown')
                                        print(f"  ✅ {team_name} image works! Type: {content_type}")
                                    else:
                                        print(f"  ❌ {team_name} image failed: {img_response.status_code}")
                                except Exception as e:
                                    print(f"  ❌ {team_name} image error: {e}")
            
        else:
            print(f"❌ API returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    get_real_logo_urls()
    
    print("\n" + "="*50)
    print("✅ REAL LOGO URL CHECK COMPLETE!")
    print("="*50)
    print("Now we know where the REAL NHL team logos are!")

if __name__ == "__main__":
    main()
