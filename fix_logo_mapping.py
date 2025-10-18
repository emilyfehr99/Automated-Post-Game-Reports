#!/usr/bin/env python3
"""
Fix Logo Mapping - Download correct logos with proper team ID mapping
"""

import requests
import os
from PIL import Image

def fix_logo_mapping():
    """Fix the team ID mapping and download correct logos"""
    
    # Corrected ESPN team ID mapping
    correct_espn_ids = {
        'EDM': 23,  # Edmonton Oilers (was 22, but that's Vancouver)
        'VAN': 22,  # Vancouver Canucks (was 23, but that's Edmonton)
        'VGK': 54,  # Vegas Golden Knights
        'FLA': 13,  # Florida Panthers
        'BOS': 6,   # Boston Bruins
        'TOR': 10,  # Toronto Maple Leafs
        'MTL': 8,   # Montreal Canadiens
        'OTT': 9,   # Ottawa Senators
        'BUF': 7,   # Buffalo Sabres
        'DET': 17,  # Detroit Red Wings
        'TBL': 14,  # Tampa Bay Lightning
        'CAR': 12,  # Carolina Hurricanes
        'WSH': 15,  # Washington Capitals
        'PIT': 5,   # Pittsburgh Penguins
        'NYR': 3,   # New York Rangers
        'NYI': 2,   # New York Islanders
        'NJD': 1,   # New Jersey Devils
        'PHI': 4,   # Philadelphia Flyers
        'CBJ': 29,  # Columbus Blue Jackets
        'NSH': 18,  # Nashville Predators
        'STL': 19,  # St. Louis Blues
        'MIN': 30,  # Minnesota Wild
        'WPG': 52,  # Winnipeg Jets
        'COL': 21,  # Colorado Avalanche
        'ARI': 53,  # Arizona Coyotes
        'SJS': 28,  # San Jose Sharks
        'LAK': 26,  # Los Angeles Kings
        'ANA': 24,  # Anaheim Ducks
        'CGY': 20,  # Calgary Flames
        'SEA': 55,  # Seattle Kraken
        'CHI': 16,  # Chicago Blackhawks
        'DAL': 25   # Dallas Stars
    }
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    # Create corrected logos directory
    output_dir = "corrected_nhl_logos"
    os.makedirs(output_dir, exist_ok=True)
    
    print("🏒 Fixing logo mapping and downloading correct logos...")
    print("=" * 60)
    
    # Focus on EDM and VAN first to fix the immediate issue
    priority_teams = ['EDM', 'VAN', 'VGK']
    
    for team_abbrev in priority_teams:
        team_id = correct_espn_ids[team_abbrev]
        url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{team_id}.png"
        
        print(f"Downloading {team_abbrev} (ID: {team_id})...")
        print(f"  URL: {url}")
        
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200 and len(response.content) > 1000:
                logo_path = os.path.join(output_dir, f"{team_abbrev}.png")
                with open(logo_path, 'wb') as f:
                    f.write(response.content)
                
                # Verify it's a valid image
                with Image.open(logo_path) as img:
                    print(f"  ✅ Downloaded {team_abbrev} logo: {img.size} pixels")
            else:
                print(f"  ❌ Failed to download {team_abbrev}: HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error downloading {team_abbrev}: {e}")
    
    print(f"\n✅ Corrected logos saved to {output_dir}/")
    return output_dir

if __name__ == "__main__":
    fix_logo_mapping()
