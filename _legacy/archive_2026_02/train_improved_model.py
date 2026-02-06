"""
Train the improved advanced model with historical data
"""

import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import logging
from nhl_api_client import NHLAPIClient
from improved_advanced_model import ImprovedAdvancedModel
from pdf_report_generator import PostGameReportGenerator

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class ImprovedModelTrainer:
    """Train the improved advanced model with comprehensive historical data"""
    
    def __init__(self):
        self.api_client = NHLAPIClient()
        self.model = ImprovedAdvancedModel()
        self.report_generator = PostGameReportGenerator()
        
        # Team name mappings for historical seasons
        self.team_mappings = {
            "2024-2025": {
                "UTA": "UTA",  # Utah Hockey Club -> Utah Mammoth
            }
        }
    
    def load_historical_data(self, filename: str = "historical_seasons.json") -> Dict:
        """Load historical season data"""
        data_file = Path(filename)
        
        if not data_file.exists():
            print(f"❌ Historical data file {filename} not found")
            print("   Run collect_historical_seasons.py first to collect data")
            return {}
        
        with open(data_file, 'r') as f:
            return json.load(f)
    
    def process_historical_games(self, season_data: Dict) -> int:
        """Process all historical games to train the model"""
        print("🏒 PROCESSING HISTORICAL GAMES FOR MODEL TRAINING")
        print("=" * 60)
        
        total_games = sum(len(games) for games in season_data.values())
        print(f"📊 Total games to process: {total_games}")
        
        processed_count = 0
        failed_count = 0
        
        # Process games chronologically across all seasons
        all_games = []
        for season, games in season_data.items():
            for game in games:
                game['season'] = season
                all_games.append(game)
        
        # Sort by date
        all_games.sort(key=lambda x: x.get('gameDate', '1900-01-01'))
        
        print(f"\\n🎯 Processing {len(all_games)} games chronologically...")
        
        for i, game in enumerate(all_games):
            try:
                game_id = game.get('gameId')
                season = game.get('season', 'Unknown')
                
                if not game_id:
                    print(f"   ⚠️  Skipping game {i+1}: No game ID")
                    failed_count += 1
                    continue
                
                away_team_abbrev = game['awayTeam']['abbrev']
                home_team_abbrev = game['homeTeam']['abbrev']
                away_score = game['awayTeam']['score']
                home_score = game['homeTeam']['score']
                game_date = game.get('gameDate', '1900-01-01')
                
                # Apply team name mapping if needed
                if season in self.team_mappings:
                    mappings = self.team_mappings[season]
                    if away_team_abbrev in mappings:
                        away_team_abbrev = mappings[away_team_abbrev]
                    if home_team_abbrev in mappings:
                        home_team_abbrev = mappings[home_team_abbrev]
                
                # Progress indicator
                if (i + 1) % 50 == 0:
                    print(f"   📈 Processed {i+1}/{len(all_games)} games...")
                
                # Get comprehensive game data
                game_data = self.api_client.get_comprehensive_game_data(game_id)
                
                if game_data:
                    # Calculate advanced metrics
                    away_team_id = game_data['boxscore']['awayTeam']['id']
                    home_team_id = game_data['boxscore']['homeTeam']['id']
                    
                    away_advanced_metrics = self.model._calculate_composite_scores(
                        game_data, away_team_id, away_team_abbrev, 'away'
                    )
                    home_advanced_metrics = self.model._calculate_composite_scores(
                        game_data, home_team_id, home_team_abbrev, 'home'
                    )
                    
                    # Add goal information
                    away_advanced_metrics['goals'] = away_score
                    home_advanced_metrics['goals'] = home_score
                    
                    # Update model's internal statistics
                    self.model.update_team_advanced_stats(
                        game_id, game_date, away_team_abbrev, home_team_abbrev,
                        away_team_id, home_team_id,
                        away_advanced_metrics, home_advanced_metrics
                    )
                    
                    # Make prediction using historical data
                    prediction_result = self.model.predict_game(away_team_abbrev, home_team_abbrev, game_date)
                    
                    predicted_away_win_prob = prediction_result['away_prob']
                    predicted_home_win_prob = prediction_result['home_prob']
                    predicted_winner = prediction_result['predicted_winner']
                    confidence = prediction_result['confidence']
                    quality = prediction_result['quality']
                    
                    # Determine actual winner
                    if away_score > home_score:
                        actual_winner = away_team_abbrev
                    elif home_score > away_score:
                        actual_winner = home_team_abbrev
                    else:
                        actual_winner = "TIE"
                    
                    is_correct = (predicted_winner == actual_winner)
                    
                    # Add prediction to model
                    self.model.add_prediction(
                        game_id=game_id,
                        date=game_date,
                        away_team=away_team_abbrev,
                        home_team=home_team_abbrev,
                        predicted_away_prob=predicted_away_win_prob,
                        predicted_home_prob=predicted_home_win_prob,
                        actual_winner=actual_winner,
                        away_goals=away_score,
                        home_goals=home_score
                    )
                    
                    processed_count += 1
                    
                    # Show some examples
                    if processed_count <= 10 or (processed_count % 100 == 0):
                        print(f"   ✅ {processed_count}. {away_team_abbrev} @ {home_team_abbrev} ({season})")
                        print(f"      Predicted: {predicted_winner} ({predicted_away_win_prob:.1f}% vs {predicted_home_win_prob:.1f}%)")
                        print(f"      Actual: {actual_winner} ({away_score}-{home_score})")
                        print(f"      Confidence: {confidence:.1f}% ({quality}) - {'✅' if is_correct else '❌'}")
                
                else:
                    print(f"   ❌ Could not fetch game data for {game_id}")
                    failed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing game {i+1}: {e}")
                failed_count += 1
        
        print(f"\\n📊 PROCESSING SUMMARY:")
        print(f"   ✅ Successfully processed: {processed_count} games")
        print(f"   ❌ Failed to process: {failed_count} games")
        print(f"   📈 Total games: {len(all_games)}")
        
        return processed_count
    
    def analyze_model_performance(self):
        """Analyze the trained model's performance"""
        print("\\n🎯 MODEL PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        performance = self.model.model_data["model_performance"]
        predictions = self.model.model_data["predictions"]
        
        print(f"\\n📊 Overall Performance:")
        print(f"   Total games: {performance['total_games']}")
        print(f"   Correct predictions: {performance['correct_predictions']}")
        print(f"   Accuracy: {performance['accuracy']:.1f}%")
        
        # Analyze by confidence level
        high_conf_games = [p for p in predictions if p.get('confidence', 0) >= 65]
        medium_conf_games = [p for p in predictions if 55 <= p.get('confidence', 0) < 65]
        low_conf_games = [p for p in predictions if p.get('confidence', 0) < 55]
        
        print(f"\\n🎯 Performance by Confidence Level:")
        print(f"   High confidence (≥65%): {len(high_conf_games)} games")
        if high_conf_games:
            high_conf_correct = sum(1 for p in high_conf_games if p.get('is_correct', False))
            print(f"   High confidence accuracy: {high_conf_correct}/{len(high_conf_games)} = {(high_conf_correct/len(high_conf_games)*100):.1f}%")
        
        print(f"   Medium confidence (55-64%): {len(medium_conf_games)} games")
        if medium_conf_games:
            medium_conf_correct = sum(1 for p in medium_conf_games if p.get('is_correct', False))
            print(f"   Medium confidence accuracy: {medium_conf_correct}/{len(medium_conf_games)} = {(medium_conf_correct/len(medium_conf_games)*100):.1f}%")
        
        print(f"   Low confidence (<55%): {len(low_conf_games)} games")
        if low_conf_games:
            low_conf_correct = sum(1 for p in low_conf_games if p.get('is_correct', False))
            print(f"   Low confidence accuracy: {low_conf_correct}/{len(low_conf_games)} = {(low_conf_correct/len(low_conf_games)*100):.1f}%")
        
        # Analyze by season
        print(f"\\n📅 Performance by Season:")
        season_stats = {}
        for pred in predictions:
            season = pred.get('season', 'Unknown')
            if season not in season_stats:
                season_stats[season] = {'total': 0, 'correct': 0}
            season_stats[season]['total'] += 1
            if pred.get('is_correct', False):
                season_stats[season]['correct'] += 1
        
        for season, stats in season_stats.items():
            accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"   {season}: {stats['correct']}/{stats['total']} = {accuracy:.1f}%")
        
        # Show team performance insights
        print(f"\\n🏒 Team Performance Insights:")
        team_stats = {}
        for pred in predictions:
            away_team = pred.get('away_team', 'Unknown')
            home_team = pred.get('home_team', 'Unknown')
            
            for team in [away_team, home_team]:
                if team not in team_stats:
                    team_stats[team] = {'total': 0, 'correct': 0}
                team_stats[team]['total'] += 1
                if pred.get('is_correct', False):
                    team_stats[team]['correct'] += 1
        
        # Show top and bottom performing teams
        team_accuracies = [(team, stats['correct']/stats['total']*100) for team, stats in team_stats.items() if stats['total'] >= 10]
        team_accuracies.sort(key=lambda x: x[1], reverse=True)
        
        print(f"   Top 5 teams (accuracy):")
        for team, accuracy in team_accuracies[:5]:
            print(f"     {team}: {accuracy:.1f}%")
        
        print(f"   Bottom 5 teams (accuracy):")
        for team, accuracy in team_accuracies[-5:]:
            print(f"     {team}: {accuracy:.1f}%")
    
    def save_trained_model(self):
        """Save the trained model"""
        self.model.save_model_data()
        print(f"\\n💾 Trained model saved to {self.model.predictions_file}")
    
    def train_model(self, historical_data_file: str = "historical_seasons.json"):
        """Main training function"""
        print("🚀 TRAINING IMPROVED ADVANCED MODEL")
        print("=" * 60)
        
        # Load historical data
        season_data = self.load_historical_data(historical_data_file)
        
        if not season_data:
            print("❌ No historical data available. Cannot train model.")
            return
        
        # Clear existing model data
        self.model.model_data['predictions'] = []
        self.model.model_data['team_advanced_stats'] = {}
        self.model.model_data['head_to_head_records'] = {}
        self.model.model_data['goalie_performance'] = {}
        self.model.model_data['home_ice_advantage'] = {}
        self.model.model_data['rest_days_advantage'] = {}
        self.model.model_data['model_performance'] = {
            "total_games": 0, "correct_predictions": 0, "accuracy": 0.0,
            "high_confidence_accuracy": 0.0, "high_confidence_games": 0
        }
        
        # Process all historical games
        processed_games = self.process_historical_games(season_data)
        
        if processed_games > 0:
            # Analyze performance
            self.analyze_model_performance()
            
            # Save trained model
            self.save_trained_model()
            
            print(f"\\n🎉 MODEL TRAINING COMPLETE!")
            print(f"   Processed {processed_games} games")
            print(f"   Model ready for predictions with improved accuracy")
        else:
            print("❌ No games were successfully processed. Training failed.")

def main():
    """Main function"""
    trainer = ImprovedModelTrainer()
    trainer.train_model()

if __name__ == "__main__":
    main()
