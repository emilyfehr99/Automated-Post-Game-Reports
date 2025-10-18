#!/usr/bin/env python3
"""
Download Real NHL Logos - Get actual NHL team logos from reliable sources
"""

import requests
import os
from PIL import Image
from io import BytesIO

class RealNHLLogoDownloader:
    def __init__(self, output_dir="real_nhl_logos"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        
        # Try different logo URL patterns
        self.logo_sources = [
            # ESPN logos
            "https://a.espncdn.com/i/teamlogos/nhl/500/{team_id}.png",
            "https://a.espncdn.com/i/teamlogos/nhl/500-dark/{team_id}.png",
            "https://a.espncdn.com/i/teamlogos/nhl/500-light/{team_id}.png",
            
            # Sports Reference
            "https://www.sports-reference.com/req/202403121/images/team-logos/{team_abbrev}.png",
            
            # NHL.com (try different patterns)
            "https://www.nhl.com/{team_abbrev}/image/team-logo",
            "https://assets.nhle.com/logos/nhl/{team_id}/light.png",
            "https://assets.nhle.com/logos/nhl/{team_id}/dark.png",
        ]
        
        # NHL team IDs and abbreviations
        self.teams = {
            'EDM': 22, 'VGK': 54, 'FLA': 13, 'BOS': 6, 'TOR': 10, 'MTL': 8, 'OTT': 9, 'BUF': 7,
            'DET': 17, 'TBL': 14, 'CAR': 12, 'WSH': 15, 'PIT': 5, 'NYR': 3, 'NYI': 2, 'NJD': 1,
            'PHI': 4, 'CBJ': 29, 'NSH': 18, 'STL': 19, 'MIN': 30, 'WPG': 52, 'COL': 21, 'ARI': 53,
            'SJS': 28, 'LAK': 26, 'ANA': 24, 'CGY': 20, 'VAN': 23, 'SEA': 55, 'CHI': 16, 'DAL': 25
        }
    
    def download_logo(self, team_abbrev, team_id):
        """Download real NHL team logo"""
        print(f"Downloading real logo for {team_abbrev} (ID: {team_id})...")
        
        for source in self.logo_sources:
            try:
                # Replace placeholders
                url = source.format(team_id=team_id, team_abbrev=team_abbrev)
                
                print(f"  Trying: {url}")
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200 and len(response.content) > 1000:  # Ensure it's not a small error page
                    # Save the logo
                    logo_path = os.path.join(self.output_dir, f"{team_abbrev}.png")
                    with open(logo_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Verify it's a valid image
                    try:
                        with Image.open(logo_path) as img:
                            print(f"  ✅ Downloaded valid logo: {img.size} pixels")
                            return logo_path
                    except Exception as e:
                        print(f"  ❌ Invalid image: {e}")
                        os.remove(logo_path)
                        continue
                else:
                    print(f"  ❌ HTTP {response.status_code} or too small")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue
        
        print(f"  ❌ Could not download real logo for {team_abbrev}")
        return None
    
    def download_all_logos(self):
        """Download all real NHL team logos"""
        print("🏒 Downloading REAL NHL team logos...")
        print("=" * 60)
        
        downloaded_count = 0
        
        for team_abbrev, team_id in self.teams.items():
            logo_path = self.download_logo(team_abbrev, team_id)
            if logo_path:
                downloaded_count += 1
            print()
        
        print(f"✅ Downloaded {downloaded_count}/{len(self.teams)} real NHL team logos")
        return downloaded_count

def main():
    """Download real NHL team logos"""
    downloader = RealNHLLogoDownloader()
    
    # Download all logos
    downloaded = downloader.download_all_logos()
    
    if downloaded > 0:
        print(f"\n🎉 Successfully downloaded {downloaded} real NHL team logos!")
        print("These are actual NHL team logos, not matplotlib-generated ones.")
    else:
        print("\n❌ No real logos were downloaded.")

if __name__ == "__main__":
    main()
