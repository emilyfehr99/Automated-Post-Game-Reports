"""
Discord Poster for NHL Game Reports
Sends game reports and images to a Discord channel via Webhook.
"""

import sys, os
_module_dirs = ['models', 'analyzers', 'scrapers', 'utils']
_base_dir = os.path.dirname(os.path.abspath(__file__))
for _d in _module_dirs:
    _p = os.path.join(_base_dir, _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)


import os
import sys
import requests
import json
from pathlib import Path

class DiscordPoster:
    def __init__(self, webhook_url=None):
        """
        Initialize Discord Poster
        Args:
            webhook_url: Discord Webhook URL (optional, defaults to env var DISCORD_WEBHOOK_URL)
        """
        self.webhook_url = webhook_url or os.getenv('DISCORD_WEBHOOK_URL')
        
        if not self.webhook_url:
            print("⚠️  No Discord Webhook URL provided. Discord posting will be disabled.")
            print("   (Set DISCORD_WEBHOOK_URL environment variable)")
    
    def send_report(self, text, image_path=None):
        """
        Send a report (text + optional image) to Discord
        Args:
            text: Message text (can include markdown)
            image_path: Path to image file (optional)
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.webhook_url:
            print("❌ Cannot post to Discord: No Webhook URL configured")
            return False
            
        print(f"📨 Sending to Discord...")
        
        try:
            # Prepare payload
            payload = {
                "content": text,
                "username": "NHL Game Reports",
                "avatar_url": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3a/05_NHL_Shield.svg/1200px-05_NHL_Shield.svg.png" 
            }
            
            # If we have an image, we need to send as multipart/form-data
            if image_path and Path(image_path).exists():
                with open(image_path, 'rb') as f:
                    # Discord requires 'payload_json' when sending files with JSON data
                    files = {
                        'file': (Path(image_path).name, f, 'image/png')
                    }
                    data = {
                        'payload_json': json.dumps(payload)
                    }
                    
                    response = requests.post(
                        self.webhook_url,
                        data=data,
                        files=files
                    )
            else:
                # Text only - simple JSON post
                response = requests.post(
                    self.webhook_url,
                    json=payload
                )
            
            if response.status_code in [200, 204]:
                print(f"✅ Automatically posted to Discord!")
                return True
            else:
                print(f"❌ Discord API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending to Discord: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    # Test block
    print("🧪 Testing Discord Poster...")
    poster = DiscordPoster()
    if poster.webhook_url:
        poster.send_report(
            "🧪 **Test Message**\nThis is a test notification from the Automated Report Runner.",
            # Optional: Add a path to a test image here if you have one
            # "../assets/test_image.png" 
        )
    else:
        print("   Skipping test (no webhook URL)")
