#!/usr/bin/env python3
"""
X Post Monitor for NHL Reports
Monitors @emilyfehr99's X posts and sends Discord notifications
"""

import os
import json
import requests
import time
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
import re
from twitter_api_client import TwitterAPIClient

class XPostMonitor:
    def __init__(self):
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        self.x_username = os.getenv('X_USERNAME', 'emilyfehr99')
        self.state_file = 'x_post_state.json'
        self.central_tz = pytz.timezone('US/Central')
        self.twitter_client = TwitterAPIClient()
        
    def load_state(self):
        """Load the last known post state"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading state: {e}")
        return {'last_post_id': None, 'last_check': None, 'today_posts': 0}
    
    def save_state(self, state):
        """Save the current post state"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def get_x_posts(self, since_id=None):
        """Get recent posts from X account using Twitter API"""
        try:
            # Get user ID
            user_id = self.twitter_client.get_user_id(self.x_username)
            if not user_id:
                print(f"❌ Could not get user ID for @{self.x_username}")
                return []
            
            # Get recent tweets
            tweets_data = self.twitter_client.get_user_tweets(user_id, since_id=since_id)
            if not tweets_data:
                return []
            
            # Filter for NHL-related tweets
            nhl_tweets = self.twitter_client.filter_nhl_tweets(tweets_data)
            
            # Format tweets for our use
            formatted_posts = []
            for tweet in nhl_tweets:
                formatted_posts.append({
                    'id': tweet['id'],
                    'text': tweet['text'],
                    'created_at': tweet['created_at'],
                    'url': f'https://x.com/{self.x_username}/status/{tweet["id"]}'
                })
            
            return formatted_posts
            
        except Exception as e:
            print(f"❌ Error getting X posts: {e}")
            return []
    
    def extract_game_info(self, post_text):
        """Extract game information from post text"""
        # Look for team abbreviations in the format "TEAM1 @ TEAM2"
        game_match = re.search(r'([A-Z]{2,4})\s*@\s*([A-Z]{2,4})', post_text)
        if game_match:
            away_team = game_match.group(1)
            home_team = game_match.group(2)
            return f"{away_team} @ {home_team}"
        
        # Look for other NHL-related patterns
        if any(keyword in post_text.lower() for keyword in ['nhl', 'hockey', 'post-game', 'report']):
            return "NHL Game Report"
        
        return "NHL Post"
    
    def send_discord_notification(self, post, game_info, today_count):
        """Send Discord notification about new X post"""
        if not self.discord_webhook:
            print("❌ Discord webhook URL not configured")
            return False
        
        try:
            # Create Discord embed
            embed = {
                "title": "🏒 New NHL Report Posted!",
                "description": f"**{game_info}**\n\n{post['text'][:500]}{'...' if len(post['text']) > 500 else ''}",
                "color": 3447003,  # Blue color
                "fields": [
                    {
                        "name": "📊 Today's Progress",
                        "value": f"{today_count} report(s) posted today",
                        "inline": True
                    },
                    {
                        "name": "🔗 View Post",
                        "value": f"[Click here]({post['url']})",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": f"Posted by @{self.x_username} • {datetime.now(self.central_tz).strftime('%Y-%m-%d %H:%M CT')}"
                },
                "thumbnail": {
                    "url": "https://cdn-icons-png.flaticon.com/512/3048/3048127.png"
                }
            }
            
            payload = {
                "content": f"🏒 **New NHL Report Posted!** 🏒",
                "embeds": [embed]
            }
            
            response = requests.post(self.discord_webhook, json=payload)
            
            if response.status_code == 204:
                print(f"✅ Discord notification sent for {game_info}")
                return True
            else:
                print(f"❌ Discord notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Discord notification: {e}")
            return False
    
    def run(self):
        """Main monitoring loop"""
        print("🔍 X Post Monitor - Checking for new NHL reports...")
        
        # Load previous state
        state = self.load_state()
        
        # Get today's date
        today = datetime.now(self.central_tz).strftime('%Y-%m-%d')
        
        # Reset daily counter if it's a new day
        if state.get('last_check') != today:
            state['today_posts'] = 0
            state['last_check'] = today
        
        try:
            # Get recent posts (only new ones since last check)
            posts = self.get_x_posts(since_id=state.get('last_post_id'))
            
            # All posts returned are new (since we used since_id)
            new_posts = posts
            
            # Process new posts
            for post in new_posts:
                game_info = self.extract_game_info(post['text'])
                state['today_posts'] += 1
                
                print(f"📱 New post detected: {game_info}")
                print(f"📊 Today's count: {state['today_posts']}")
                
                # Send Discord notification
                self.send_discord_notification(post, game_info, state['today_posts'])
                
                # Update last post ID
                state['last_post_id'] = post['id']
                
                # Small delay between notifications
                time.sleep(1)
            
            # Save updated state
            self.save_state(state)
            
            if new_posts:
                print(f"✅ Processed {len(new_posts)} new post(s)")
            else:
                print("ℹ️  No new posts found")
                
        except Exception as e:
            print(f"❌ Error in monitoring loop: {e}")

def main():
    """Main function"""
    monitor = XPostMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
