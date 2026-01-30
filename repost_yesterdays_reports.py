#!/usr/bin/env python3
"""
Script to repost (retweet) yesterday's NHL game reports.
Run daily to bring previous day's reports back to the timeline.
"""

import os
import sys
import tweepy
import pytz
from datetime import datetime, timedelta
import argparse
from twitter_config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET
)

# Constants
CENTRAL_TZ = pytz.timezone('US/Central')

class ReportReposter:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        
        # Authenticate
        print("🔐 Authenticating with Twitter API...")
        try:
            self.client = tweepy.Client(
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
            )
            
            # Get own user ID
            response = self.client.get_me()
            if response.data:
                self.user_id = response.data.id
                self.username = response.data.username
                print(f"✅ Authenticated as: @{self.username} (ID: {self.user_id})")
            else:
                print("❌ Authentication failed: Could not get user info")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            sys.exit(1)

    def get_yesterdays_range(self):
        """Get start and end datetime for yesterday in Central Time"""
        now = datetime.now(CENTRAL_TZ)
        yesterday = now - timedelta(days=1)
        
        # Start of yesterday (00:00:00)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # End of yesterday (23:59:59)
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return start_date, end_date

    def is_report_tweet(self, tweet):
        """Check if a tweet looks like a game report"""
        text = tweet.text
        
        # Check for typical report indicators
        # 1. Contains "vs" or "@" with hashtags/teams
        # 2. Contains "Report" or "Analysis"
        # 3. Created by us (implicit since we fetch user tweets)
        
        if "vs" in text and "#" in text:
            return True
        if "Report" in text:
            return True
            
        return False

    def find_yesterdays_reports(self):
        """Find tweets from yesterday that are reports"""
        start_date, end_date = self.get_yesterdays_range()
        print(f"🔍 Looking for reports from: {start_date.strftime('%Y-%m-%d')} (Central Time)")
        
        reports_found = []
        
        try:
            # Fetch recent tweets
            # max_results=100 is good to cover a busy day
            response = self.client.get_users_tweets(
                id=self.user_id,
                max_results=100,
                tweet_fields=['created_at', 'text', 'public_metrics'],
                exclude=['retweets', 'replies']  # Only original tweets
            )
            
            if not response.data:
                print("ℹ️  No recent tweets found.")
                return []
                
            for tweet in response.data:
                # Convert tweet time (UTC) to Central
                created_at_utc = tweet.created_at
                created_at_central = created_at_utc.astimezone(CENTRAL_TZ)
                
                # Check if within yesterday's range
                if start_date <= created_at_central <= end_date:
                    if self.is_report_tweet(tweet):
                        reports_found.append(tweet)
                        print(f"   found: {tweet.text[:60]}... ({created_at_central.strftime('%H:%M')})")
        
        except Exception as e:
            print(f"❌ Error fetching tweets: {e}")
            return []
            
        print(f"✅ Found {len(reports_found)} reports from yesterday.")
        return reports_found

    def repost_reports(self):
        """Main execution: find and retweet"""
        reports = self.find_yesterdays_reports()
        
        if not reports:
            print("Types: No reports found to repost.")
            return

        print(f"\n🚀 Processing {len(reports)} reports...")
        
        successful = 0
        failed = 0
        
        for i, tweet in enumerate(reports, 1):
            print(f"[{i}/{len(reports)}] Processing tweet {tweet.id}...")
            
            if self.dry_run:
                print(f"   [DRY RUN] Would retweet: {tweet.text[:50]}...")
                successful += 1
                continue
                
            try:
                self.client.retweet(tweet.id)
                print(f"   ✅ Retweeted successfully!")
                successful += 1
            except Exception as e:
                # Check directly for 'already retweeted' error to not count as failure
                if "You have already retweeted this Tweet" in str(e):
                    print(f"   ℹ️  Already retweeted.")
                    successful += 1
                else:    
                    print(f"   ❌ Failed to retweet: {e}")
                    failed += 1
                    
        print(f"\n🎉 Finished!")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")

def main():
    parser = argparse.ArgumentParser(description='Repost yesterdays game reports')
    parser.add_argument('--dry-run', action='store_true', help='Check for tweets but do not actually retweet')
    args = parser.parse_args()
    
    reposter = ReportReposter(dry_run=args.dry_run)
    reposter.repost_reports()

if __name__ == "__main__":
    main()
