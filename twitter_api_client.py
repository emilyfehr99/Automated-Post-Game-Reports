#!/usr/bin/env python3
"""
Twitter API Client for monitoring X posts
"""

import os
import requests
import json
from datetime import datetime, timedelta
import pytz

class TwitterAPIClient:
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.base_url = 'https://api.twitter.com/2'
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }
    
    def get_user_id(self, username):
        """Get user ID from username"""
        try:
            url = f"{self.base_url}/users/by/username/{username}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return data['data']['id']
            else:
                print(f"❌ Error getting user ID: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting user ID: {e}")
            return None
    
    def get_user_tweets(self, user_id, since_id=None, max_results=10):
        """Get recent tweets from a user"""
        try:
            url = f"{self.base_url}/users/{user_id}/tweets"
            params = {
                'max_results': max_results,
                'tweet.fields': 'created_at,public_metrics,context_annotations',
                'exclude': 'retweets,replies'
            }
            
            if since_id:
                params['since_id'] = since_id
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error getting tweets: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting tweets: {e}")
            return None
    
    def filter_nhl_tweets(self, tweets_data):
        """Filter tweets for NHL-related content"""
        if not tweets_data or 'data' not in tweets_data:
            return []
        
        nhl_keywords = [
            'nhl', 'hockey', 'post-game', 'report', 'game', 'final',
            'shots', 'goals', 'assists', 'save', 'period', 'overtime'
        ]
        
        nhl_tweets = []
        for tweet in tweets_data['data']:
            text = tweet['text'].lower()
            if any(keyword in text for keyword in nhl_keywords):
                nhl_tweets.append(tweet)
        
        return nhl_tweets

def main():
    """Test the Twitter API client"""
    client = TwitterAPIClient()
    
    if not client.bearer_token:
        print("❌ TWITTER_BEARER_TOKEN not set")
        return
    
    # Get user ID
    user_id = client.get_user_id('emilyfehr99')
    if not user_id:
        print("❌ Could not get user ID")
        return
    
    print(f"✅ User ID: {user_id}")
    
    # Get recent tweets
    tweets_data = client.get_user_tweets(user_id)
    if tweets_data:
        print(f"✅ Found {len(tweets_data.get('data', []))} tweets")
        
        # Filter for NHL tweets
        nhl_tweets = client.filter_nhl_tweets(tweets_data)
        print(f"🏒 Found {len(nhl_tweets)} NHL-related tweets")
        
        for tweet in nhl_tweets[:3]:  # Show first 3
            print(f"📱 {tweet['text'][:100]}...")
    else:
        print("❌ No tweets found")

if __name__ == "__main__":
    main()
