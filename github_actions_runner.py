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
from twitter_config import TEAM_HASHTAGS, TWITTER_API_KEY
from self_learning_model import SelfLearningModel
import json
import subprocess


class GitHubActionsRunner:
    def __init__(self):
        """Initialize the GitHub Actions runner"""
        self.client = NHLAPIClient()
        self.processed_games_file = Path('processed_games.json')
        self.processed_games = self.load_processed_games()
        self.learning_model = SelfLearningModel()
        
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
        """Get all games from today (based on Central Time)"""
        import pytz
        
        # Use proper Central Time (handles DST automatically)
        central_tz = pytz.timezone('US/Central')
        central_now = datetime.now(central_tz)
        today = central_now.strftime('%Y-%m-%d')
        
        print(f"🕐 Current time (CT): {central_now.strftime('%Y-%m-%d %I:%M:%S %p')}")
        print(f"📅 Checking games from: {today}")
        
        all_games = []
        
        try:
            schedule = self.client.get_game_schedule(today)
            if schedule and 'gameWeek' in schedule:
                for day in schedule['gameWeek']:
                    # Include games from today only
                    if day.get('date') == today and 'games' in day:
                        all_games.extend(day['games'])
        except Exception as e:
            print(f"❌ Error fetching schedule for {today}: {e}")
            import traceback
            traceback.print_exc()
        
        return all_games
    
    def generate_and_post_game(self, game_id, away_team, home_team):
        """Generate report and post to Twitter for a single game"""
        print(f"\n{'='*60}")
        print(f"🏒 PROCESSING: {away_team} @ {home_team}")
        print(f"{'='*60}")
        
        # Generate the report
        print(f"\n📊 Generating report for {away_team} @ {home_team}...")
        try:
            # Fetch comprehensive game data
            game_data = self.client.get_comprehensive_game_data(game_id)
            
            if not game_data:
                print(f"❌ Failed to fetch game data")
                return False
            
            # Create output filename
            output_filename = f"/tmp/nhl_postgame_report_{away_team}_vs_{home_team}_{game_id}.pdf"
            
            # Import and run the PDF generator
            from pdf_report_generator import PostGameReportGenerator
            
            generator = PostGameReportGenerator()
            pdf_path = generator.generate_report(game_data, output_filename, game_id)
            
            if not pdf_path or not Path(pdf_path).exists():
                print(f"❌ Report generation failed")
                return False
            
            print(f"✅ Report generated: {pdf_path}")
            
            # Learn from this game's data
            self.learn_from_game(game_data, game_id, away_team, home_team)
            
            # Convert PDF to PNG using pdf2image
            from pdf2image import convert_from_path
            
            output_dir = Path("/tmp/nhl_images")
            output_dir.mkdir(exist_ok=True)
            
            # Convert PDF to PNG
            pages = convert_from_path(pdf_path, dpi=300)
            
            if not pages:
                print(f"❌ PDF conversion failed - no pages")
                return False
            
            # Save first page as PNG
            image_filename = f"nhl_postgame_report_{away_team}_vs_{home_team}_{game_id}.png"
            image_path = output_dir / image_filename
            pages[0].save(image_path, 'PNG')
            
            if not image_path or not Path(image_path).exists():
                print(f"❌ Image conversion failed")
                # Clean up PDF
                try:
                    Path(pdf_path).unlink()
                except:
                    pass
                return False
            
            print(f"✅ Image converted: {image_path}")
            
            # Clean up PDF file (no longer needed)
            try:
                Path(pdf_path).unlink()
                print(f"🗑️  Cleaned up PDF: {pdf_path}")
            except Exception as e:
                print(f"⚠️  Could not delete PDF: {e}")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Post to Twitter
        print(f"\n🐦 Posting {away_team} @ {home_team} to Twitter...")
        try:
            # Debug: Check if environment variables are set
            import os
            api_key = os.getenv('TWITTER_API_KEY', '')
            api_secret = os.getenv('TWITTER_API_SECRET', '')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN', '')
            access_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
            
            print(f"Debug - Credential lengths:")
            print(f"  API Key: {len(api_key)} chars (expected 25)")
            print(f"  API Secret: {len(api_secret)} chars (expected 50)")
            print(f"  Access Token: {len(access_token)} chars (expected 50)")
            print(f"  Access Secret: {len(access_secret)} chars (expected 45)")
            
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
            
            # Clean up image file after successful post
            try:
                Path(image_path).unlink()
                print(f"🗑️  Cleaned up image: {image_path}")
            except Exception as e:
                print(f"⚠️  Could not delete image: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error posting to Twitter: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def learn_from_game(self, game_data, game_id, away_team, home_team):
        """Learn from completed game data to improve predictions"""
        try:
            # Get win probability prediction from the report generator
            from pdf_report_generator import PostGameReportGenerator
            generator = PostGameReportGenerator()
            
            # Calculate win probability using current model
            win_prob = generator.calculate_win_probability(game_data)
            
            # Determine actual winner
            away_goals = game_data['boxscore']['awayTeam'].get('score', 0)
            home_goals = game_data['boxscore']['homeTeam'].get('score', 0)
            
            actual_winner = None
            if away_goals > home_goals:
                actual_winner = "away"
            elif home_goals > away_goals:
                actual_winner = "home"
            # If tied, we don't learn from it (shootout/OT games)
            
            if actual_winner:
                # Extract metrics used in prediction
                metrics_used = {
                    "away_xg": 0.0,
                    "home_xg": 0.0,
                    "away_hdc": 0,
                    "home_hdc": 0,
                    "away_shots": game_data['boxscore']['awayTeam'].get('sog', 0),
                    "home_shots": game_data['boxscore']['homeTeam'].get('sog', 0),
                    "away_gs": 0.0,
                    "home_gs": 0.0
                }
                
                # Try to get more detailed metrics if available
                try:
                    away_xg, home_xg = generator._calculate_xg_from_plays(game_data)
                    away_hdc, home_hdc = generator._calculate_hdc_from_plays(game_data)
                    away_gs, home_gs = generator._calculate_game_scores(game_data)
                    
                    metrics_used.update({
                        "away_xg": away_xg,
                        "home_xg": home_xg,
                        "away_hdc": away_hdc,
                        "home_hdc": home_hdc,
                        "away_gs": away_gs,
                        "home_gs": home_gs
                    })
                except Exception as e:
                    print(f"⚠️  Could not extract detailed metrics: {e}")
                
                # Add prediction to learning model
                self.learning_model.add_prediction(
                    game_id=game_id,
                    date=datetime.now().strftime('%Y-%m-%d'),
                    away_team=away_team,
                    home_team=home_team,
                    predicted_away_prob=win_prob['away_probability'],
                    predicted_home_prob=win_prob['home_probability'],
                    metrics_used=metrics_used,
                    actual_winner=actual_winner
                )
                
                print(f"🧠 Learned from {away_team} @ {home_team}: {actual_winner} won")
                print(f"   Prediction: {win_prob['away_probability']:.1f}% vs {win_prob['home_probability']:.1f}%")
                
        except Exception as e:
            print(f"⚠️  Error learning from game: {e}")
    
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
                success = self.generate_and_post_game(
                    game_info['id'],
                    game_info['away'],
                    game_info['home']
                )
                
                if success:
                    # Only mark as processed if successfully posted
                    self.processed_games.add(game_info['id'])
                    self.save_processed_games()  # Save after each success
                    success_count += 1
                    print(f"✅ COMPLETED: {game_info['away']} @ {game_info['home']}")
                else:
                    print(f"⚠️  FAILED: {game_info['away']} @ {game_info['home']} - will retry next run")
                    
            except Exception as e:
                print(f"❌ Error processing game: {e}")
                import traceback
                traceback.print_exc()
                print(f"⚠️  Game {game_info['id']} not marked as processed - will retry next run")
                continue
        
        # Save processed games
        self.save_processed_games()
        
        # Run daily model update
        print(f"\n{'='*60}")
        print("🧠 UPDATING MODEL...")
        print("="*60)
        try:
            model_perf = self.learning_model.run_daily_update()
            print(f"📊 Model Performance: {model_perf['accuracy']:.3f} accuracy ({model_perf['correct_predictions']}/{model_perf['total_games']} games)")
            print(f"📈 Recent Accuracy: {model_perf['recent_accuracy']:.3f}")
        except Exception as e:
            print(f"⚠️  Error updating model: {e}")
        
        print(f"\n{'='*60}")
        print(f"🎉 Run Complete!")
        print(f"✅ Successfully posted: {success_count}/{len(newly_completed)}")
        print(f"📊 Total processed games: {len(self.processed_games)}")
        print("="*60)


if __name__ == '__main__':
    runner = GitHubActionsRunner()
    runner.run()

