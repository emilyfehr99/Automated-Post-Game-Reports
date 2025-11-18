"""
Collect NHL data for the last two seasons using API data only
Run through post game report generator (don't post) to collect metrics
Then place data into the model for training
"""

import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
import numpy as np

class ModelDataCollector:
    """Collect NHL data for model training using API data only"""
    
    def __init__(self):
        self.api = NHLAPIClient()
        self.report_generator = PostGameReportGenerator()
        self.model = ImprovedSelfLearningModelV2()
        
        # Season date ranges (approximate)
        self.season_ranges = {
            "2024-2025": {
                "start": datetime(2024, 10, 8),
                "end": datetime(2025, 4, 18)
            },
            "2023-2024": {
                "start": datetime(2023, 10, 10),
                "end": datetime(2024, 4, 18)
            }
        }
    
    def get_season_games(self, season: str) -> List[Dict]:
        """Get all games for a season from the API"""
        if season not in self.season_ranges:
            print(f"❌ Unknown season: {season}")
            return []
        
        season_range = self.season_ranges[season]
        start_date = season_range["start"]
        end_date = season_range["end"]
        
        print(f"📅 Collecting {season} season games from {start_date.date()} to {end_date.date()}")
        
        all_games = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            try:
                # Get schedule for this date
                schedule = self.api.get_game_schedule(date_str)
                
                if schedule and 'gameWeek' in schedule:
                    for week in schedule['gameWeek']:
                        for game in week['games']:
                            if game['gameState'] == 'OFF':  # Only completed games
                                game['season'] = season
                                all_games.append(game)
                
                # Progress indicator
                if current_date.day == 1:  # First of each month
                    print(f"   📊 Found {len(all_games)} games through {date_str}")
                
            except Exception as e:
                print(f"   ⚠️  Error collecting data for {date_str}: {e}")
            
            current_date += timedelta(days=1)
        
        print(f"✅ Found {len(all_games)} games for {season} season")
        return all_games
    
    def process_game_for_model(self, game: Dict) -> Optional[Dict]:
        """Process a single game and extract metrics for the model"""
        game_id = game.get('gameId')
        
        if not game_id:
            return None
        
        try:
            # Get comprehensive game data
            game_data = self.api.get_comprehensive_game_data(game_id)
            
            if not game_data:
                return None
            
            # Extract team information
            away_team_abbrev = game['awayTeam']['abbrev']
            home_team_abbrev = game['homeTeam']['abbrev']
            away_score = game['awayTeam']['score']
            home_score = game['homeTeam']['score']
            game_date = game.get('gameDate', '1900-01-01')
            
            # Extract metrics using PostGameReportGenerator
            away_xg, home_xg = self.report_generator._calculate_xg_from_plays(game_data)
            away_hdc, home_hdc = self.report_generator._calculate_hdc_from_plays(game_data)
            away_gs, home_gs = self.report_generator._calculate_game_scores(game_data)
            
            # Get period stats
            away_team_id = game_data['boxscore']['awayTeam']['id']
            home_team_id = game_data['boxscore']['homeTeam']['id']
            
            away_period_stats = self.report_generator._calculate_real_period_stats(game_data, away_team_id, 'away')
            home_period_stats = self.report_generator._calculate_real_period_stats(game_data, home_team_id, 'home')
            
            # Compile metrics
            metrics_used = {
                "away_xg": away_xg, "home_xg": home_xg,
                "away_hdc": away_hdc, "home_hdc": home_hdc,
                "away_shots": game_data['boxscore']['awayTeam'].get('sog', 0),
                "home_shots": game_data['boxscore']['homeTeam'].get('sog', 0),
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
            }
            
            # Determine winner
            if away_score > home_score:
                actual_winner = away_team_abbrev
            elif home_score > away_score:
                actual_winner = home_team_abbrev
            else:
                actual_winner = "TIE"
            
            return {
                'game_id': game_id,
                'date': game_date,
                'away_team': away_team_abbrev,
                'home_team': home_team_abbrev,
                'away_score': away_score,
                'home_score': home_score,
                'actual_winner': actual_winner,
                'metrics_used': metrics_used,
                'season': game.get('season', 'Unknown')
            }
            
        except Exception as e:
            print(f"   ❌ Error processing game {game_id}: {e}")
            return None
    
    def collect_season_data(self, season: str) -> List[Dict]:
        """Collect and process all games for a season"""
        print(f"\\n🏒 COLLECTING {season} SEASON DATA")
        print("=" * 50)
        
        # Get all games for the season
        season_games = self.get_season_games(season)
        
        if not season_games:
            print(f"❌ No games found for {season} season")
            return []
        
        # Process games and extract metrics
        processed_games = []
        failed_count = 0
        
        print(f"\\n🔍 Processing {len(season_games)} games...")
        
        for i, game in enumerate(season_games):
            if (i + 1) % 50 == 0:
                print(f"   📈 Processed {i+1}/{len(season_games)} games...")
            
            processed_game = self.process_game_for_model(game)
            
            if processed_game:
                processed_games.append(processed_game)
            else:
                failed_count += 1
        
        print(f"\\n📊 {season} SEASON SUMMARY:")
        print(f"   ✅ Successfully processed: {len(processed_games)} games")
        print(f"   ❌ Failed to process: {failed_count} games")
        print(f"   📈 Total games: {len(season_games)}")
        
        return processed_games
    
    def train_model_with_data(self, all_games: List[Dict]):
        """Train the model with collected data"""
        print(f"\\n🚀 TRAINING MODEL WITH {len(all_games)} GAMES")
        print("=" * 50)
        
        # Clear existing model data
        self.model.model_data['predictions'] = []
        self.model.model_data['model_performance'] = {
            "total_games": 0, "correct_predictions": 0, "accuracy": 0.0, "recent_accuracy": 0.0
        }
        
        # Sort games by date
        all_games.sort(key=lambda x: x['date'])
        
        correct_predictions = 0
        
        for i, game_data in enumerate(all_games):
            game_id = game_data['game_id']
            date = game_data['date']
            away_team = game_data['away_team']
            home_team = game_data['home_team']
            actual_winner = game_data['actual_winner']
            away_score = game_data['away_score']
            home_score = game_data['home_score']
            metrics_used = game_data['metrics_used']
            
            # Make prediction using historical data
            prediction_result = self.model.ensemble_predict(away_team, home_team)
            
            predicted_away_win_prob = prediction_result['away_prob']
            predicted_home_win_prob = prediction_result['home_prob']
            predicted_winner = prediction_result['predicted_winner']
            
            is_correct = (predicted_winner == actual_winner)
            
            if is_correct:
                correct_predictions += 1
            
            # Add prediction to model
            self.model.add_prediction(
                game_id=game_id,
                date=date,
                away_team=away_team,
                home_team=home_team,
                predicted_away_win_prob=predicted_away_win_prob,
                predicted_home_win_prob=predicted_home_win_prob,
                metrics_used=metrics_used,
                actual_winner=actual_winner,
                away_goals=away_score,
                home_goals=home_score
            )
            
            if (i + 1) % 100 == 0:
                print(f"   📈 Trained on {i+1}/{len(all_games)} games...")
        
        # Save model
        self.model.save_model_data()
        
        # Calculate final accuracy
        final_accuracy = (correct_predictions / len(all_games)) * 100 if all_games else 0.0
        
        print(f"\\n🎯 MODEL TRAINING COMPLETE!")
        print(f"   Total games trained: {len(all_games)}")
        print(f"   Correct predictions: {correct_predictions}")
        print(f"   Final accuracy: {final_accuracy:.1f}%")
        
        return final_accuracy
    
    def collect_and_train(self, seasons: List[str] = None):
        """Main function to collect data and train model"""
        if seasons is None:
            seasons = ["2024-2025", "2023-2024"]
        
        print("🏒 NHL MODEL DATA COLLECTION & TRAINING")
        print("=" * 60)
        
        all_processed_games = []
        
        # Collect data for each season
        for season in seasons:
            season_games = self.collect_season_data(season)
            all_processed_games.extend(season_games)
        
        if not all_processed_games:
            print("❌ No games were successfully processed. Cannot train model.")
            return
        
        # Train model with all collected data
        final_accuracy = self.train_model_with_data(all_processed_games)
        
        print(f"\\n🎉 DATA COLLECTION & TRAINING COMPLETE!")
        print(f"   Processed {len(all_processed_games)} games across {len(seasons)} seasons")
        print(f"   Model accuracy: {final_accuracy:.1f}%")
        print(f"   Model ready for predictions!")

def main():
    """Main function"""
    collector = ModelDataCollector()
    collector.collect_and_train()

if __name__ == "__main__":
    main()
