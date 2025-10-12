"""
Automatic NHL Game Monitor and Twitter Poster
Monitors NHL games in real-time and automatically posts reports when games finish
"""

import time
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path
from nhl_api_client import NHLAPIClient
import json


class GameMonitor:
    def __init__(self, check_interval=60):
        """
        Initialize the game monitor
        Args:
            check_interval: How often to check for completed games (in seconds)
        """
        self.client = NHLAPIClient()
        self.check_interval = check_interval
        self.processed_games = set()  # Track games we've already processed
        self.processed_games_file = Path('processed_games.json')
        self.load_processed_games()
        
    def load_processed_games(self):
        """Load previously processed game IDs from file"""
        if self.processed_games_file.exists():
            try:
                with open(self.processed_games_file, 'r') as f:
                    data = json.load(f)
                    self.processed_games = set(data.get('games', []))
                    print(f"📋 Loaded {len(self.processed_games)} previously processed games")
            except Exception as e:
                print(f"⚠️  Could not load processed games: {e}")
                self.processed_games = set()
    
    def save_processed_games(self):
        """Save processed game IDs to file"""
        try:
            with open(self.processed_games_file, 'w') as f:
                json.dump({'games': list(self.processed_games)}, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save processed games: {e}")
    
    def get_todays_games(self):
        """Get all games for today"""
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            schedule = self.client.get_schedule(today, today)
            if schedule and 'gameWeek' in schedule:
                games = []
                for day in schedule['gameWeek']:
                    if 'games' in day:
                        games.extend(day['games'])
                return games
        except Exception as e:
            print(f"❌ Error fetching schedule: {e}")
        return []
    
    def check_for_completed_games(self):
        """Check for newly completed games"""
        print(f"\n🔍 Checking for completed games... ({datetime.now().strftime('%I:%M:%S %p')})")
        
        games = self.get_todays_games()
        newly_completed = []
        
        for game in games:
            game_id = str(game.get('id'))
            game_state = game.get('gameState', 'UNKNOWN')
            away_team = game.get('awayTeam', {}).get('abbrev', 'UNK')
            home_team = game.get('homeTeam', {}).get('abbrev', 'UNK')
            
            # Check if game is completed and not yet processed
            if game_state in ['FINAL', 'OFF'] and game_id not in self.processed_games:
                print(f"✅ NEW COMPLETED GAME: {away_team} @ {home_team} (ID: {game_id})")
                newly_completed.append({
                    'id': game_id,
                    'away': away_team,
                    'home': home_team,
                    'state': game_state
                })
        
        if not newly_completed:
            print(f"   No new completed games (monitoring {len(games)} games)")
        
        return newly_completed
    
    def generate_report(self, game_id, away_team, home_team):
        """Generate a report for a specific game"""
        print(f"\n📊 Generating report for {away_team} @ {home_team}...")
        
        try:
            # Run the single game report generator
            result = subprocess.run(
                ['python3', 'pdf_report_generator.py', game_id],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            if result.returncode == 0:
                print(f"✅ Report generated successfully for {away_team} @ {home_team}")
                return True
            else:
                print(f"❌ Report generation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return False
    
    def post_to_twitter(self, game_id, away_team, home_team):
        """Post a single game report to Twitter"""
        print(f"\n🐦 Posting {away_team} @ {home_team} to Twitter...")
        
        try:
            # Import here to avoid circular imports
            from twitter_poster import TwitterPoster
            from twitter_config import TEAM_HASHTAGS
            from pathlib import Path
            
            # Find the generated image for this game
            today = datetime.now().strftime('%Y_%m_%d')
            image_folder = Path(f"/Users/emilyfehr8/Desktop/NHL_Images_{today}")
            
            if not image_folder.exists():
                print(f"❌ Image folder not found: {image_folder}")
                return False
            
            # Find the specific game image
            game_images = list(image_folder.glob(f'nhl_postgame_report_{away_team}_vs_{home_team}_*.png'))
            
            if not game_images:
                print(f"❌ No image found for {away_team} vs {home_team}")
                return False
            
            image_path = game_images[0]
            
            # Initialize Twitter poster
            poster = TwitterPoster()
            
            # Get team hashtags
            away_hashtag = TEAM_HASHTAGS.get(away_team, f'#{away_team}')
            home_hashtag = TEAM_HASHTAGS.get(home_team, f'#{home_team}')
            tweet_text = f"{away_hashtag} vs {home_hashtag}"
            
            # Upload image
            media_id = poster.upload_media(image_path)
            
            if not media_id:
                print(f"❌ Failed to upload image")
                return False
            
            # Post tweet
            tweet = poster.client.create_tweet(
                text=tweet_text,
                media_ids=[media_id]
            )
            
            tweet_id = tweet.data['id']
            print(f"✅ Posted to Twitter: {tweet_text}")
            print(f"   🔗 https://twitter.com/user/status/{tweet_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error posting to Twitter: {e}")
            return False
    
    def process_game(self, game_info):
        """Process a newly completed game: generate report and post to Twitter"""
        game_id = game_info['id']
        away_team = game_info['away']
        home_team = game_info['home']
        
        print(f"\n{'='*60}")
        print(f"🏒 PROCESSING: {away_team} @ {home_team}")
        print(f"{'='*60}")
        
        # Step 1: Generate report
        if not self.generate_report(game_id, away_team, home_team):
            print(f"⚠️  Skipping Twitter post due to report generation failure")
            return False
        
        # Wait a moment for file system to sync
        time.sleep(2)
        
        # Step 2: Post to Twitter
        if not self.post_to_twitter(game_id, away_team, home_team):
            print(f"⚠️  Twitter posting failed, but report was generated")
            # Still mark as processed since report was generated
        
        # Mark as processed
        self.processed_games.add(game_id)
        self.save_processed_games()
        
        print(f"✅ COMPLETED: {away_team} @ {home_team}")
        
        return True
    
    def run(self):
        """Main monitoring loop"""
        print("="*60)
        print("🤖 NHL GAME MONITOR - AUTOMATIC MODE")
        print("="*60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"⏱️  Check interval: {self.check_interval} seconds")
        print(f"📋 Previously processed: {len(self.processed_games)} games")
        print("="*60)
        print("\n🔄 Starting monitoring loop...")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Check for completed games
                newly_completed = self.check_for_completed_games()
                
                # Process each newly completed game
                for game_info in newly_completed:
                    try:
                        self.process_game(game_info)
                    except Exception as e:
                        print(f"❌ Error processing game: {e}")
                        continue
                
                # Wait before next check
                if newly_completed:
                    print(f"\n⏳ Waiting {self.check_interval} seconds before next check...")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            print(f"📊 Total games processed this session: {len(self.processed_games)}")
            print("👋 Goodbye!")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automatically monitor NHL games and post reports to Twitter'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset processed games list and start fresh'
    )
    
    args = parser.parse_args()
    
    # Reset processed games if requested
    if args.reset:
        processed_file = Path('processed_games.json')
        if processed_file.exists():
            processed_file.unlink()
            print("✅ Processed games list reset")
    
    # Start monitoring
    monitor = GameMonitor(check_interval=args.interval)
    monitor.run()


if __name__ == '__main__':
    main()

