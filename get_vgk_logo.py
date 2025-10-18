#!/usr/bin/env python3
"""
Get VGK Logo - Download Vegas Golden Knights logo specifically
"""

import requests
import os
from PIL import Image

def get_vgk_logo():
    """Get VGK logo from different sources"""
    sources = [
        "https://a.espncdn.com/i/teamlogos/nhl/500/54.png",
        "https://a.espncdn.com/i/teamlogos/nhl/500-dark/54.png", 
        "https://a.espncdn.com/i/teamlogos/nhl/500-light/54.png",
        "https://a.espncdn.com/i/teamlogos/nhl/100/54.png",
        "https://a.espncdn.com/i/teamlogos/nhl/200/54.png",
        "https://a.espncdn.com/i/teamlogos/nhl/500/vegas.png",
        "https://a.espncdn.com/i/teamlogos/nhl/500/vgk.png"
    ]
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    for url in sources:
        try:
            print(f"Trying: {url}")
            response = session.get(url, timeout=10)
            if response.status_code == 200 and len(response.content) > 1000:
                with open("real_nhl_logos/VGK.png", 'wb') as f:
                    f.write(response.content)
                
                # Verify it's a valid image
                with Image.open("real_nhl_logos/VGK.png") as img:
                    print(f"✅ Downloaded VGK logo: {img.size} pixels")
                    return True
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    return False

if __name__ == "__main__":
    get_vgk_logo()
