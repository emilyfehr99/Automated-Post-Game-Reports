"""
GitHub Actions Runner for Automatic NHL Report Posting
Optimized for scheduled execution in GitHub Actions environment
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from nhl_api_client import NHLAPIClient
from twitter_poster import TwitterPoster
from twitter_config import TEAM_HASHTAGS
import json
import subprocess


class GitHubActionsRunner:
    def __init__(self):
        """Initialize the GitHub Actions runner"""
        self.client = NHLAPIClient()
        self.processed_games_file = Path('processed_games.json')
        self.processed_games = self.load_processed_games()
        
    def load_processed_games(self):
        """Load previously processed game IDs"""
        if self.processed_games_file.exists():
            try:
                with open(self.processed_games_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('games', []))
            except Exception as e:
                print(f"⚠️  Could not load processed games: {e}")
        return set()
    
    def save_processed_games(self):
        """Save processed game IDs"""
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
    
    def generate_and_post_game(self, game_id, away_team, home_team):
        """Generate report and post to Twitter for a single game"""
        print(f"\n{'='*60}")
        print(f"🏒 PROCESSING: {away_team} @ {home_team}")
        print(f"{'='*60}")
        
        # Generate the report
        print(f"\n📊 Generating report for {away_team} @ {home_team}...")
        try:
            # Import and run the PDF generator directly
            from pdf_report_generator import NHLReportGenerator
            
            generator = NHLReportGenerator()
            pdf_path = generator.generate_report(game_id)
            
            if not pdf_path or not Path(pdf_path).exists():
                print(f"❌ Report generation failed")
                return False
            
            print(f"✅ Report generated: {pdf_path}")
            
            # Convert PDF to PNG
            from pdf_to_image_converter import PDFToImageConverter
            converter = PDFToImageConverter()
            
            output_dir = Path("/tmp/nhl_images")
            output_dir.mkdir(exist_ok=True)
            
            image_path = converter.convert_single_pdf(pdf_path, output_dir)
            
            if not image_path or not Path(image_path).exists():
                print(f"❌ Image conversion failed")
                return False
            
            print(f"✅ Image converted: {image_path}")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Post to Twitter
        print(f"\n🐦 Posting {away_team} @ {home_team} to Twitter...")
        try:
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
            import traceback
            traceback.print_exc()
            return False
    
    def run(self):
        """Main execution for GitHub Actions"""
        print("="*60)
        print("🤖 NHL REPORT AUTOMATION - GITHUB ACTIONS")
        print("="*60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
        print(f"📋 Previously processed: {len(self.processed_games)} games")
        print("="*60)
        
        # Get today's games
        games = self.get_todays_games()
        print(f"\n🔍 Found {len(games)} games today")
        
        newly_completed = []
        
        # Check for completed games
        for game in games:
            game_id = str(game.get('id'))
            game_state = game.get('gameState', 'UNKNOWN')
            away_team = game.get('awayTeam', {}).get('abbrev', 'UNK')
            home_team = game.get('homeTeam', {}).get('abbrev', 'UNK')
            
            print(f"   {away_team} @ {home_team}: {game_state}")
            
            # Check if completed and not processed
            if game_state in ['FINAL', 'OFF'] and game_id not in self.processed_games:
                print(f"      ✅ NEW COMPLETED GAME!")
                newly_completed.append({
                    'id': game_id,
                    'away': away_team,
                    'home': home_team
                })
        
        if not newly_completed:
            print(f"\n✅ No new completed games to process")
            return
        
        print(f"\n🚀 Processing {len(newly_completed)} new game(s)...")
        
        # Process each newly completed game
        success_count = 0
        for game_info in newly_completed:
            try:
                if self.generate_and_post_game(
                    game_info['id'],
                    game_info['away'],
                    game_info['home']
                ):
                    self.processed_games.add(game_info['id'])
                    success_count += 1
                    print(f"✅ COMPLETED: {game_info['away']} @ {game_info['home']}")
                else:
                    print(f"⚠️  FAILED: {game_info['away']} @ {game_info['home']}")
                    
            except Exception as e:
                print(f"❌ Error processing game: {e}")
                continue
        
        # Save processed games
        self.save_processed_games()
        
        print(f"\n{'='*60}")
        print(f"🎉 Run Complete!")
        print(f"✅ Successfully posted: {success_count}/{len(newly_completed)}")
        print(f"📊 Total processed games: {len(self.processed_games)}")
        print("="*60)


if __name__ == '__main__':
    runner = GitHubActionsRunner()
    runner.run()

