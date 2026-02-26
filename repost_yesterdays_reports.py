#!/usr/bin/env python3
"""
Script to repost (retweet) yesterday's NHL game reports.
Run daily to bring previous day's reports back to the timeline.
"""

import os
import sys
import tweepy
import pytz
import json
import time
from pathlib import Path
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
        self.posted_tweets_file = Path('posted_tweets.json')
        
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

    def find_yesterdays_reports(self):
        """Find tweets from yesterday that are reports (from local JSON)"""
        now = datetime.now(CENTRAL_TZ)
        yesterday = now - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        
        print(f"🔍 Looking for reports from: {yesterday_str} (Central Time)")
        
        if not self.posted_tweets_file.exists():
            print(f"ℹ️  No {self.posted_tweets_file} found. No reports to repost.")
            return []
            
        reports_found = []
        
        try:
            with open(self.posted_tweets_file, 'r') as f:
                data = json.load(f)
                
            if yesterday_str in data:
                reports = data[yesterday_str]
                for report in reports:
                    # Create a simple object to match what the rest of the code expects
                    # The existing code expects an object with .id attribute
                    class Tweet:
                        def __init__(self, id, text):
                            self.id = id
                            self.text = text
                            
                    tweet = Tweet(report['tweet_id'], report.get('description', 'Unknown Report'))
                    reports_found.append(tweet)
                    print(f"   found: {tweet.text} (ID: {tweet.id})")
            else:
                print(f"ℹ️  No entries found for {yesterday_str} in local file.")
                
        except Exception as e:
            print(f"❌ Error reading posted tweets file: {e}")
            return []
            
        print(f"✅ Found {len(reports_found)} reports from yesterday.")
        # Deduplicate by game_id to only repost the latest version if multiple exist
        unique_reports = {}
        for r in reports_found:
            # If multiple reports for the same game, the later one is usually better
            unique_reports[r.text] = r
            
        final_reports = list(unique_reports.values())
        print(f"✅ Filtered to {len(final_reports)} unique reports.")
        return final_reports

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
            if i > 1:
                # Add a delay between retweets to avoid 429 rate limits
                wait_time = 30
                print(f"   ⏳ Waiting {wait_time} seconds before next retweet...")
                time.sleep(wait_time)
                
            print(f"[{i}/{len(reports)}] Processing tweet {tweet.id}...")
            
            if self.dry_run:
                print(f"   [DRY RUN] Would retweet: {tweet.text[:50]}...")
                successful += 1
                continue
                
            try:
                # Use keyword argument and catching more specific exceptions if needed
                self.client.retweet(tweet_id=tweet.id)
                print(f"   ✅ Retweeted successfully!")
                successful += 1
            except Exception as e:
                # Check directly for 'already retweeted' error to not count as failure
                error_str = str(e)
                if "already retweeted" in error_str.lower():
                    print(f"   ℹ️  Already retweeted.")
                    successful += 1
                elif "429" in error_str:
                    print(f"   ❌ Hit Twitter Rate Limit (429). Stopping further attempts.")
                    failed += (len(reports) - i + 1)
                    break
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
