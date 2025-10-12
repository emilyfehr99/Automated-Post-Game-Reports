"""
Automated Twitter Posting System for NHL Post-Game Reports
Posts generated reports to Twitter with proper team hashtags and threading
"""

import os
import sys
import tweepy
from datetime import datetime, timedelta
from pathlib import Path
import re
from twitter_config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TEAM_HASHTAGS,
    NHL_SEASON_START
)


class TwitterPoster:
    def __init__(self):
        """Initialize Twitter API client"""
        print("🔐 Authenticating with Twitter API...")
        
        try:
            # Authenticate with Twitter API v1.1 (for media upload)
            auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
            auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
            self.api = tweepy.API(auth)
            
            # Authenticate with Twitter API v2 (for posting)
            self.client = tweepy.Client(
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
            )
            
            # Verify credentials
            self.api.verify_credentials()
            print("✅ Successfully authenticated with Twitter!")
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            sys.exit(1)
    
    def calculate_week_and_day(self, date_str):
        """
        Calculate the week and day number based on NHL season start
        Args:
            date_str: Date in format 'YYYY-MM-DD'
        Returns:
            tuple: (week_number, day_number)
        """
        season_start = datetime.strptime(NHL_SEASON_START, '%Y-%m-%d')
        current_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        days_since_start = (current_date - season_start).days
        week_number = (days_since_start // 7) + 1
        day_number = (days_since_start % 7) + 1
        
        return week_number, day_number
    
    def extract_teams_from_filename(self, filename):
        """
        Extract team abbreviations from report filename
        Args:
            filename: Report filename (e.g., 'nhl_postgame_report_LAK_vs_WPG_20251011_220011.png')
        Returns:
            tuple: (away_team, home_team) or (None, None) if not found
        """
        # Pattern: team_vs_team
        match = re.search(r'_([A-Z]{3})_vs_([A-Z]{3})_', filename)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
    def get_team_hashtags(self, away_team, home_team):
        """
        Get hashtags for both teams
        Args:
            away_team: Away team abbreviation
            home_team: Home team abbreviation
        Returns:
            str: Formatted tweet text with hashtags
        """
        away_hashtag = TEAM_HASHTAGS.get(away_team, f'#{away_team}')
        home_hashtag = TEAM_HASHTAGS.get(home_team, f'#{home_team}')
        
        return f"{away_hashtag} vs {home_hashtag}"
    
    def upload_media(self, image_path):
        """
        Upload media to Twitter
        Args:
            image_path: Path to image file
        Returns:
            str: Media ID
        """
        try:
            media = self.api.media_upload(filename=str(image_path))
            return media.media_id_string
        except Exception as e:
            print(f"❌ Failed to upload media: {e}")
            return None
    
    def post_thread(self, image_folder, date_str):
        """
        Post a thread of game reports for a specific date
        Args:
            image_folder: Path to folder containing generated images
            date_str: Date in format 'YYYY-MM-DD'
        """
        # Find all report images for this date
        image_folder = Path(image_folder)
        if not image_folder.exists():
            print(f"❌ Image folder not found: {image_folder}")
            return
        
        # Get all PNG files sorted by name
        image_files = sorted(image_folder.glob('nhl_postgame_report_*.png'))
        
        if not image_files:
            print(f"❌ No report images found in: {image_folder}")
            return
        
        print(f"\n🏒 Found {len(image_files)} reports to post")
        
        # Calculate week and day
        week, day = self.calculate_week_and_day(date_str)
        formatted_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d, %Y')
        
        # Create thread parent tweet
        parent_text = f"Week {week} Day {day} - NHL Post-Game Reports 🏒\n{formatted_date}"
        
        print(f"\n📱 Creating thread: \"{parent_text}\"")
        
        try:
            # Post parent tweet
            parent_tweet = self.client.create_tweet(text=parent_text)
            parent_id = parent_tweet.data['id']
            print(f"✅ Thread created (ID: {parent_id})")
            
            # Post each game report as a reply
            current_reply_id = parent_id
            
            for i, image_file in enumerate(image_files, 1):
                # Extract teams from filename
                away_team, home_team = self.extract_teams_from_filename(image_file.name)
                
                if not away_team or not home_team:
                    print(f"⚠️  Could not extract teams from: {image_file.name}")
                    continue
                
                # Get team hashtags
                tweet_text = self.get_team_hashtags(away_team, home_team)
                
                # Upload image
                print(f"\n📤 Uploading image {i}/{len(image_files)}: {away_team} vs {home_team}")
                media_id = self.upload_media(image_file)
                
                if not media_id:
                    print(f"⚠️  Skipping {image_file.name} - media upload failed")
                    continue
                
                # Post reply tweet with image
                try:
                    reply_tweet = self.client.create_tweet(
                        text=tweet_text,
                        media_ids=[media_id],
                        in_reply_to_tweet_id=current_reply_id
                    )
                    current_reply_id = reply_tweet.data['id']
                    print(f"✅ Posted: {tweet_text}")
                    
                except Exception as e:
                    print(f"❌ Failed to post tweet for {away_team} vs {home_team}: {e}")
                    continue
            
            print(f"\n🎉 Thread complete! Posted {len(image_files)} reports")
            print(f"🔗 View thread: https://twitter.com/user/status/{parent_id}")
            
        except Exception as e:
            print(f"❌ Failed to create thread: {e}")
            return


def main():
    """Main entry point for Twitter posting"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Post NHL Post-Game Reports to Twitter'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Date to post reports for (format: YYYY-MM-DD)',
        default=datetime.now().strftime('%Y-%m-%d')
    )
    parser.add_argument(
        '--image-folder',
        type=str,
        help='Path to folder containing report images (optional)'
    )
    
    args = parser.parse_args()
    
    # Determine image folder path
    if args.image_folder:
        image_folder = args.image_folder
    else:
        # Default to Desktop folder with date
        formatted_date = args.date.replace('-', '_')
        image_folder = f"/Users/emilyfehr8/Desktop/NHL_Images_{formatted_date}"
    
    print("=" * 60)
    print("🐦 NHL Post-Game Report Twitter Poster")
    print("=" * 60)
    print(f"📅 Date: {args.date}")
    print(f"📁 Image folder: {image_folder}")
    print("=" * 60)
    
    # Initialize poster and post thread
    poster = TwitterPoster()
    poster.post_thread(image_folder, args.date)


if __name__ == '__main__':
    main()

