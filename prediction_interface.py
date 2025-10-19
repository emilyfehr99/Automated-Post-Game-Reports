"""
Pre-Game Prediction Interface
Uses the self-learning model for predictions before games are played
This is separate from the post-game win probability analysis
"""

import json
from nhl_api_client import NHLAPIClient
from improved_self_learning_model import ImprovedSelfLearningModel
from datetime import datetime
import pytz

class PredictionInterface:
    def __init__(self):
        """Initialize the prediction interface"""
        self.api = NHLAPIClient()
        self.learning_model = ImprovedSelfLearningModel()
        
    def get_todays_predictions(self):
        """Get predictions for today's games using the self-learning model"""
        print('🏒 NHL GAME PREDICTIONS (Self-Learning Model) 🏒')
        print('=' * 60)
        print(f'📅 Date: {datetime.now(pytz.timezone("US/Central")).strftime("%Y-%m-%d")}')
        
        # Get current model weights
        weights = self.learning_model.get_current_weights()
        print(f'🎯 Model Weights: xG={weights["xg_weight"]}, HDC={weights["hdc_weight"]}, Shots={weights["shot_attempts_weight"]}, GS={weights["game_score_weight"]}')
        print()
        
        # Get today's games
        central_tz = pytz.timezone('US/Central')
        today = datetime.now(central_tz).strftime('%Y-%m-%d')
        schedule_data = self.api.get_game_schedule(today)
        
        # Get games from gameWeek
        games = []
        for day_data in schedule_data.get('gameWeek', []):
            if isinstance(day_data, dict) and 'games' in day_data:
                games.extend(day_data['games'])
        
        # Filter for today's games only (2025-2026 season games)
        today_games = []
        for game in games:
            game_time = game.get('startTimeUTC', '')
            if today in game_time and game.get('gameState') in ['PRE', 'FUT']:
                today_games.append(game)
        
        print(f'🔍 Found {len(today_games)} games today')
        print()
        
        # Generate predictions using the self-learning model
        predictions = []
        for i, game in enumerate(today_games):
            away_team = game.get('awayTeam', {}).get('abbrev', 'UNK')
            home_team = game.get('homeTeam', {}).get('abbrev', 'UNK')
            game_time = game.get('startTimeUTC', 'UNK')
            
            print(f'{i+1}. {away_team} @ {home_team}')
            print(f'   🕐 Time: {game_time}')
            
            # Get prediction using self-learning model
            prediction = self.predict_game(away_team, home_team)
            
            print(f'   🎯 Prediction: {away_team} {prediction["away_prob"]:.1f}% | {home_team} {prediction["home_prob"]:.1f}%')
            
            # Determine favorite
            if prediction["away_prob"] > prediction["home_prob"]:
                favorite = away_team
                spread = prediction["away_prob"] - prediction["home_prob"]
            else:
                favorite = home_team
                spread = prediction["home_prob"] - prediction["away_prob"]
            
            print(f'   ⭐ Favorite: {favorite} (+{spread:.1f}%)')
            print(f'   📊 Confidence: {max(prediction["away_prob"], prediction["home_prob"]):.1f}%')
            print()
            
            predictions.append({
                'game_id': game.get('id'),
                'away_team': away_team,
                'home_team': home_team,
                'away_prob': prediction["away_prob"],
                'home_prob': prediction["home_prob"],
                'favorite': favorite,
                'spread': spread
            })
        
        return predictions
    
    def predict_game(self, away_team, home_team):
        """Predict a single game using the improved self-learning model with Edge data"""
        # Use the improved model's predict_game method
        result = self.learning_model.predict_game(away_team, home_team)
        
        # Convert to the format expected by the interface
        return {
            'away_prob': result['away_prob'],
            'home_prob': result['home_prob'],
            'away_score': result['away_score'],
            'home_score': result['home_score']
        }
    
    def get_team_performance_data(self):
        """Get current team performance data (this would be updated regularly)"""
        # This is where you'd get the most recent team performance data
        # For now, using static data - in production this would be updated from recent games
        return {
            'TOR': {'xg_avg': 3.2, 'hdc_avg': 2, 'shots_avg': 32, 'gs_avg': 15.2},
            'SEA': {'xg_avg': 2.8, 'hdc_avg': 1.5, 'shots_avg': 28, 'gs_avg': 12.8},
            'NYR': {'xg_avg': 3.1, 'hdc_avg': 2.2, 'shots_avg': 30, 'gs_avg': 14.9},
            'MTL': {'xg_avg': 2.9, 'hdc_avg': 1.8, 'shots_avg': 29, 'gs_avg': 13.7},
            'MIN': {'xg_avg': 2.7, 'hdc_avg': 1.6, 'shots_avg': 27, 'gs_avg': 13.1},
            'PHI': {'xg_avg': 2.6, 'hdc_avg': 1.4, 'shots_avg': 26, 'gs_avg': 12.4},
            'TBL': {'xg_avg': 3.0, 'hdc_avg': 2.0, 'shots_avg': 31, 'gs_avg': 15.8},
            'CBJ': {'xg_avg': 2.4, 'hdc_avg': 1.2, 'shots_avg': 24, 'gs_avg': 11.2},
            'DAL': {'xg_avg': 3.3, 'hdc_avg': 2.3, 'shots_avg': 33, 'gs_avg': 16.1},
            'STL': {'xg_avg': 2.8, 'hdc_avg': 1.7, 'shots_avg': 28, 'gs_avg': 13.4},
            'NSH': {'xg_avg': 2.9, 'hdc_avg': 1.9, 'shots_avg': 29, 'gs_avg': 13.9},
            'WPG': {'xg_avg': 3.1, 'hdc_avg': 2.1, 'shots_avg': 31, 'gs_avg': 15.0},
            'BOS': {'xg_avg': 2.5, 'hdc_avg': 1.3, 'shots_avg': 25, 'gs_avg': 12.1},
            'COL': {'xg_avg': 3.4, 'hdc_avg': 2.4, 'shots_avg': 34, 'gs_avg': 16.5},
            'CAR': {'xg_avg': 3.2, 'hdc_avg': 2.2, 'shots_avg': 32, 'gs_avg': 15.3},
            'LAK': {'xg_avg': 2.7, 'hdc_avg': 1.6, 'shots_avg': 27, 'gs_avg': 13.0},
            'CGY': {'xg_avg': 2.8, 'hdc_avg': 1.7, 'shots_avg': 28, 'gs_avg': 13.5},
            'VGK': {'xg_avg': 3.0, 'hdc_avg': 2.0, 'shots_avg': 30, 'gs_avg': 14.7},
            'PIT': {'xg_avg': 2.9, 'hdc_avg': 1.8, 'shots_avg': 29, 'gs_avg': 13.8},
            'SJS': {'xg_avg': 2.2, 'hdc_avg': 1.0, 'shots_avg': 22, 'gs_avg': 10.5}
        }
    
    def show_model_performance(self):
        """Show current model performance"""
        perf = self.learning_model.get_model_performance()
        print(f"\n📊 MODEL PERFORMANCE:")
        print(f"  Total Games: {perf['total_games']}")
        print(f"  Accuracy: {perf['accuracy']:.3f}")
        print(f"  Recent Accuracy: {perf['recent_accuracy']:.3f}")
        
        # Show model analysis
        analysis = self.learning_model.analyze_model_performance()
        if analysis.get('team_accuracy'):
            print(f"\n📈 TOP TEAM ACCURACY:")
            sorted_teams = sorted(analysis['team_accuracy'].items(), key=lambda x: x[1], reverse=True)
            for team, acc in sorted_teams[:5]:
                print(f"  {team}: {acc:.3f}")


def main():
    """Main function to run predictions"""
    predictor = PredictionInterface()
    
    # Get today's predictions
    predictions = predictor.get_todays_predictions()
    
    # Show model performance
    predictor.show_model_performance()
    
    print(f"\n🎯 SUMMARY:")
    print(f"  Total games predicted: {len(predictions)}")
    print(f"  Model uses self-learning weights")
    print(f"  Separate from post-game win probability analysis")


if __name__ == "__main__":
    main()
