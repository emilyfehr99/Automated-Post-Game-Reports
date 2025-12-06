"""
GitHub Actions Runner for Automatic NHL Report Posting
Optimized for scheduled execution in GitHub Actions environment
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import pytz
from nhl_api_client import NHLAPIClient
from twitter_poster import TwitterPoster
from twitter_config import TEAM_HASHTAGS, TWITTER_API_KEY
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from correlation_model import CorrelationModel
from pdf_report_generator import PostGameReportGenerator
import json
import subprocess
import numpy as np


class GitHubActionsRunner:
    def __init__(self):
        """Initialize the GitHub Actions runner"""
        self.client = NHLAPIClient()
        self.processed_games_file = Path('processed_games.json')
        self.processed_games = self.load_processed_games()
        self.learning_model = ImprovedSelfLearningModelV2()
        self.corr_model = CorrelationModel()
        self.report_generator = PostGameReportGenerator()
        self.team_stats_file = Path('season_2025_2026_team_stats.json')
        
    def load_processed_games(self):
        """Load previously processed game IDs"""
        file_path = str(self.processed_games_file.absolute())
        print(f"🔍 Looking for processed_games.json at: {file_path}")
        if self.processed_games_file.exists():
            try:
                with open(self.processed_games_file, 'r') as f:
                    data = json.load(f)
                    games = set(data.get('games', []))
                    print(f"✅ Loaded {len(games)} processed games from file")
                    if games:
                        print(f"   Games: {sorted(list(games))[:10]}...")  # Show first 10
                    return games
            except Exception as e:
                print(f"⚠️  Could not load processed games: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️  processed_games.json not found at {file_path}")
        return set()
    
    def save_processed_games(self):
        """Save processed game IDs"""
        try:
            file_path = str(self.processed_games_file.absolute())
            with open(self.processed_games_file, 'w') as f:
                json.dump({'games': list(self.processed_games)}, f, indent=2)
            print(f"💾 Saved {len(self.processed_games)} processed games to {file_path}")
        except Exception as e:
            print(f"⚠️  Could not save processed games: {e}")
            import traceback
            traceback.print_exc()
    
    def load_team_stats(self):
        """Load current team stats"""
        if self.team_stats_file.exists():
            try:
                with open(self.team_stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Could not load team stats: {e}")
        
        # Initialize empty structure
        return {
            'season': '2025-2026',
            'generated_at': datetime.utcnow().isoformat(),
            'total_games': 0,
            'teams': {}
        }
    
    def save_team_stats(self, stats):
        """Save team stats"""
        try:
            with open(self.team_stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save team stats: {e}")
    
    def update_team_stats_from_game(self, game_data):
        """Extract metrics from a completed game and update team stats"""
        try:
            # Get team info from boxscore
            boxscore = game_data.get('boxscore', {})
            away_team = boxscore.get('awayTeam', {})
            home_team = boxscore.get('homeTeam', {})
            
            away_abbrev = away_team.get('abbrev')
            home_abbrev = home_team.get('abbrev')
            
            if not away_abbrev or not home_abbrev:
                return
            
            # Extract metrics using the report generator
            away_xg, home_xg = self.report_generator._calculate_xg_from_plays(game_data)
            away_hdc, home_hdc = self.report_generator._calculate_hdc_from_plays(game_data)
            away_gs, home_gs = self.report_generator._calculate_game_scores(game_data)
            
            # Load current stats
            stats = self.load_team_stats()
            
            # Update stats for both teams
            for team_abbrev, xg, hdc, gs in [
                (away_abbrev, away_xg, away_hdc, away_gs),
                (home_abbrev, home_xg, home_hdc, home_gs)
            ]:
                if team_abbrev not in stats['teams']:
                    stats['teams'][team_abbrev] = {
                        'games_played': 0,
                        'xg_sum': 0.0,
                        'hdc_sum': 0.0,
                        'gs_sum': 0.0,
                        'xg_avg': 0.0,
                        'hdc_avg': 0.0,
                        'gs_avg': 0.0
                    }
                
                team_data = stats['teams'][team_abbrev]
                team_data['games_played'] += 1
                team_data['xg_sum'] += float(xg or 0.0)
                team_data['hdc_sum'] += float(hdc or 0.0)
                team_data['gs_sum'] += float(gs or 0.0)
                
                # Recalculate averages
                if team_data['games_played'] > 0:
                    team_data['xg_avg'] = team_data['xg_sum'] / team_data['games_played']
                    team_data['hdc_avg'] = team_data['hdc_sum'] / team_data['games_played']
                    team_data['gs_avg'] = team_data['gs_sum'] / team_data['games_played']
            
            # Update metadata
            stats['generated_at'] = datetime.utcnow().isoformat()
            stats['total_games'] = sum(team['games_played'] for team in stats['teams'].values())
            
            # Save updated stats
            self.save_team_stats(stats)
            print(f"✅ Updated team stats for {away_abbrev} vs {home_abbrev}")
            
        except Exception as e:
            print(f"⚠️  Error updating team stats: {e}")
    
    def get_todays_games(self):
        """Get all games from today and yesterday (based on Central Time)
        
        Checks both dates because:
        - Games can finish late at night (after midnight CT)
        - When running early morning (3-6 AM), we want yesterday's completed games
        - When running later, we want today's completed games
        """
        import pytz
        from datetime import timedelta
        
        # Use proper Central Time (handles DST automatically)
        central_tz = pytz.timezone('US/Central')
        central_now = datetime.now(central_tz)
        today = central_now.strftime('%Y-%m-%d')
        yesterday = (central_now - timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"🕐 Current time (CT): {central_now.strftime('%Y-%m-%d %I:%M:%S %p')}")
        print(f"📅 Checking games from: {yesterday} and {today}")
        
        all_games = []
        games_by_date = {}  # Track which date each game belongs to
        
        # Check both yesterday and today to catch games that finished overnight
        dates_to_check = [yesterday, today]
        
        for check_date in dates_to_check:
            try:
                schedule = self.client.get_game_schedule(check_date)
                if schedule and 'gameWeek' in schedule:
                    for day in schedule['gameWeek']:
                        if day.get('date') == check_date and 'games' in day:
                            for game in day['games']:
                                all_games.append(game)
                                # Store the date for this game
                                games_by_date[str(game.get('id'))] = check_date
                            print(f"   Found {len(day['games'])} games on {check_date}")
            except Exception as e:
                print(f"❌ Error fetching schedule for {check_date}: {e}")
                import traceback
                traceback.print_exc()
        
        # Store games_by_date for later use
        self.games_by_date = games_by_date
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
            
            # Update team stats from this completed game
            print(f"📈 Updating team stats from completed game...")
            self.update_team_stats_from_game(game_data)
            
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
                # Extract comprehensive metrics used in prediction
                metrics_used = {
                    "away_xg": 0.0, "home_xg": 0.0,
                    "away_hdc": 0, "home_hdc": 0,
                    "away_shots": game_data['boxscore']['awayTeam'].get('sog', 0),
                    "home_shots": game_data['boxscore']['homeTeam'].get('sog', 0),
                    "away_gs": 0.0, "home_gs": 0.0,
                    "away_goalie": None, "home_goalie": None,
                    "away_corsi_pct": 50.0, "home_corsi_pct": 50.0,
                    "away_power_play_pct": 0.0, "home_power_play_pct": 0.0,
                    "away_faceoff_pct": 50.0, "home_faceoff_pct": 50.0,
                    "away_hits": 0, "home_hits": 0,
                    "away_blocked_shots": 0, "home_blocked_shots": 0,
                    "away_giveaways": 0, "home_giveaways": 0,
                    "away_takeaways": 0, "home_takeaways": 0,
                    "away_penalty_minutes": 0, "home_penalty_minutes": 0
                }
                
                # Try to get comprehensive metrics if available
                try:
                    # Basic metrics
                    away_xg, home_xg = generator._calculate_xg_from_plays(game_data)
                    away_hdc, home_hdc = generator._calculate_hdc_from_plays(game_data)
                    away_gs, home_gs = generator._calculate_game_scores(game_data)
                    # Attempt to extract starting goalies from boxscore
                    try:
                        box = game_data.get('boxscore', {})

                        def extract_from_box(team_key):
                            team = box.get(team_key, {})
                            # 1) explicit goalie starters list if present
                            starters = team.get('goalies') or team.get('starters')
                            if starters and isinstance(starters, list):
                                for g in starters:
                                    nm = (g.get('name') or g.get('firstLastName') or g.get('playerName')) if isinstance(g, dict) else None
                                    if nm:
                                        return nm
                            # 2) fall back to players with G position
                            players = team.get('players') or []
                            if isinstance(players, dict):
                                players_iter = players.values()
                            else:
                                players_iter = players
                            goalie_candidates = []
                            for p in players_iter:
                                try:
                                    pos = p.get('positionCode') or p.get('position', {}).get('code')
                                    toi = p.get('toi') or p.get('timeOnIce') or 0
                                    starter = p.get('starter') or p.get('starting') or False
                                    name = p.get('name') or p.get('firstLastName') or p.get('playerName')
                                    if (pos == 'G' or pos == 'GOALIE') and name:
                                        # prefer flagged starter; otherwise highest TOI
                                        toi_int = 0
                                        try:
                                            s = str(toi)
                                            toi_int = int(s.replace(':','')[:4] or 0)
                                        except Exception:
                                            pass
                                        goalie_candidates.append((bool(starter), toi_int, name))
                                except Exception:
                                    continue
                            if not goalie_candidates:
                                return None
                            goalie_candidates.sort(key=lambda t: (t[0], t[1]), reverse=True)
                            return goalie_candidates[0][2]

                        metrics_used["away_goalie"] = extract_from_box('awayTeam')
                        metrics_used["home_goalie"] = extract_from_box('homeTeam')
                    except Exception:
                        pass
                    
                    # Advanced metrics from period stats
                    away_period_stats = generator._calculate_real_period_stats(game_data, game_data['boxscore']['awayTeam']['id'], 'away')
                    home_period_stats = generator._calculate_real_period_stats(game_data, game_data['boxscore']['homeTeam']['id'], 'home')
                    
                    metrics_used.update({
                        "away_xg": away_xg, "home_xg": home_xg,
                        "away_hdc": away_hdc, "home_hdc": home_hdc,
                        "away_gs": away_gs, "home_gs": home_gs,
                        "away_corsi_pct": np.mean(away_period_stats.get('corsi_pct', [50.0])),
                        "home_corsi_pct": np.mean(home_period_stats.get('corsi_pct', [50.0])),
                        "away_power_play_pct": np.mean(away_period_stats.get('pp_goals', [0])) / max(1, np.mean(away_period_stats.get('pp_attempts', [1]))) * 100,
                        "home_power_play_pct": np.mean(home_period_stats.get('pp_goals', [0])) / max(1, np.mean(home_period_stats.get('pp_attempts', [1]))) * 100,
                        "away_faceoff_pct": np.mean(away_period_stats.get('fo_pct', [50.0])),
                        "home_faceoff_pct": np.mean(home_period_stats.get('fo_pct', [50.0])),
                        "away_hits": np.mean(away_period_stats.get('hits', [0])),
                        "home_hits": np.mean(home_period_stats.get('hits', [0])),
                        "away_blocked_shots": np.mean(away_period_stats.get('bs', [0])),
                        "home_blocked_shots": np.mean(home_period_stats.get('bs', [0])),
                        "away_giveaways": np.mean(away_period_stats.get('gv', [0])),
                        "home_giveaways": np.mean(home_period_stats.get('gv', [0])),
                        "away_takeaways": np.mean(away_period_stats.get('tk', [0])),
                        "home_takeaways": np.mean(home_period_stats.get('tk', [0])),
                        "away_penalty_minutes": np.mean(away_period_stats.get('pim', [0])),
                        "home_penalty_minutes": np.mean(home_period_stats.get('pim', [0]))
                    })
                except Exception as e:
                    print(f"⚠️  Could not extract detailed metrics: {e}")
                
                # Add prediction to learning model
                # Use the actual game date, not today's date
                game_date = game_data.get('gameDate', datetime.now().strftime('%Y-%m-%d'))
                if isinstance(game_date, str):
                    # Convert from YYYY-MM-DD format
                    game_date = game_date.split('T')[0] if 'T' in game_date else game_date
                else:
                    game_date = datetime.now().strftime('%Y-%m-%d')
                
                # Enrich metrics_used with situational features for analysis
                try:
                    away_rest = self.learning_model._calculate_rest_days_advantage(away_team, 'away', game_date)
                    home_rest = self.learning_model._calculate_rest_days_advantage(home_team, 'home', game_date)
                except Exception:
                    away_rest = 0.0
                    home_rest = 0.0
                try:
                    away_goalie_perf = self.learning_model._goalie_performance_for_game(away_team, 'away', game_date)
                    home_goalie_perf = self.learning_model._goalie_performance_for_game(home_team, 'home', game_date)
                except Exception:
                    away_goalie_perf = 0.0
                    home_goalie_perf = 0.0
                try:
                    away_sos = self.learning_model._calculate_sos(away_team, 'away')
                    home_sos = self.learning_model._calculate_sos(home_team, 'home')
                except Exception:
                    away_sos = 0.0
                    home_sos = 0.0
                try:
                    away_venue_win_pct = self.learning_model._calculate_venue_win_percentage(away_team, 'away')
                    home_venue_win_pct = self.learning_model._calculate_venue_win_percentage(home_team, 'home')
                except Exception:
                    away_venue_win_pct = 0.5
                    home_venue_win_pct = 0.5
                metrics_used.update({
                    "away_rest": away_rest,
                    "home_rest": home_rest,
                    "away_goalie_perf": away_goalie_perf,
                    "home_goalie_perf": home_goalie_perf,
                    "away_sos": away_sos,
                    "home_sos": home_sos,
                    "away_venue_win_pct": away_venue_win_pct,
                    "home_venue_win_pct": home_venue_win_pct,
                })

                self.learning_model.add_prediction(
                    game_id=game_id,
                    date=game_date,
                    away_team=away_team,
                    home_team=home_team,
                    predicted_away_prob=win_prob['away_probability'],
                    predicted_home_prob=win_prob['home_probability'],
                    metrics_used=metrics_used,
                    actual_winner=actual_winner
                )
                # Online update correlation model
                try:
                    label = 'away' if actual_winner in (away_team, 'away') else 'home'
                    self.corr_model.online_update(metrics_used, label)
                except Exception:
                    pass
                
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
        
        # Get games from today
        games = self.get_todays_games()
        print(f"\n🔍 Found {len(games)} games from today")
        
        newly_completed = []
        
        # Get today's date to filter out old games
        central_tz = pytz.timezone('US/Central')
        central_now = datetime.now(central_tz)
        today = central_now.strftime('%Y-%m-%d')
        
        # Initialize games_by_date dict if not set
        if not hasattr(self, 'games_by_date'):
            self.games_by_date = {}
        
        # Check for completed games
        for game in games:
            game_id = str(game.get('id'))
            game_state = game.get('gameState', 'UNKNOWN')
            away_team = game.get('awayTeam', {}).get('abbrev', 'UNK')
            home_team = game.get('homeTeam', {}).get('abbrev', 'UNK')
            
            # Get game date from schedule (we stored this when fetching games)
            game_date = self.games_by_date.get(game_id, '')
            
            print(f"   {away_team} @ {home_team}: {game_state}" + (f" (Date: {game_date})" if game_date else ""))
            
            # Only process games that:
            # 1. Are completed (FINAL or OFF)
            # 2. Haven't been processed before
            # 3. Are from today
            # If game is already processed, skip it
            is_today = game_date == today
            is_already_processed = game_id in self.processed_games
            
            if is_already_processed:
                print(f"      ⏭️  Already processed, skipping")
            elif game_state in ['FINAL', 'OFF']:
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
            
            # Periodic re-fitting of correlation weights (every ~25 games)
            if model_perf['total_games'] % 25 == 0:
                print("🔄 Re-fitting correlation model weights...")
                try:
                    self.corr_model.refit_weights_from_history()
                except Exception as e:
                    print(f"⚠️  Error re-fitting correlation weights: {e}")
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

