#!/usr/bin/env python3
"""
Download from Reliable Source - Get NHL logos from a known reliable source
"""

import requests
import os
from PIL import Image

def download_from_reliable_source():
    """Download NHL logos from a reliable source with known team mappings"""
    
    # Use a different approach - try to find a source with known team mappings
    # Let's try some alternative sources
    
    sources = [
        # Try different ESPN patterns
        "https://a.espncdn.com/i/teamlogos/nhl/500/edmonton.png",
        "https://a.espncdn.com/i/teamlogos/nhl/500/vancouver.png", 
        "https://a.espncdn.com/i/teamlogos/nhl/500/vegas.png",
        "https://a.espncdn.com/i/teamlogos/nhl/500/washington.png",
        
        # Try with different sizes
        "https://a.espncdn.com/i/teamlogos/nhl/100/edmonton.png",
        "https://a.espncdn.com/i/teamlogos/nhl/200/edmonton.png",
        "https://a.espncdn.com/i/teamlogos/nhl/300/edmonton.png",
        
        # Try with team abbreviations
        "https://a.espncdn.com/i/teamlogos/nhl/500/edm.png",
        "https://a.espncdn.com/i/teamlogos/nhl/500/van.png",
        "https://a.espncdn.com/i/teamlogos/nhl/500/vgk.png",
        "https://a.espncdn.com/i/teamlogos/nhl/500/wsh.png",
    ]
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    print("🔍 Trying alternative ESPN URL patterns...")
    print("=" * 60)
    
    working_urls = []
    
    for url in sources:
        try:
            response = session.get(url, timeout=5)
            if response.status_code == 200 and len(response.content) > 1000:
                print(f"✅ Working: {url} ({len(response.content)} bytes)")
                working_urls.append(url)
                
                # Extract team name from URL
                team_name = url.split('/')[-1].replace('.png', '')
                filename = f"reliable_{team_name}.png"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"  Saved as: {filename}")
            else:
                print(f"❌ Failed: {url} (HTTP {response.status_code})")
        except Exception as e:
            print(f"❌ Error: {url} - {e}")
    
    print(f"\n📊 Found {len(working_urls)} working URLs")
    
    # If we found some working URLs, let's try to identify what teams they are
    if working_urls:
        print("\n🖼️ Downloaded logos - let's identify them...")
        for url in working_urls:
            team_name = url.split('/')[-1].replace('.png', '')
            filename = f"reliable_{team_name}.png"
            if os.path.exists(filename):
                try:
                    with Image.open(filename) as img:
                        print(f"  {filename}: {img.size} pixels")
                except Exception as e:
                    print(f"  {filename}: Error reading image - {e}")

if __name__ == "__main__":
    download_from_reliable_source()
