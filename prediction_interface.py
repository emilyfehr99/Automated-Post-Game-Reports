"""
Pre-Game Prediction Interface
Uses the self-learning model for predictions before games are played
This is separate from the post-game win probability analysis
"""

import json
from nhl_api_client import NHLAPIClient
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from datetime import datetime, timedelta
import pytz

class PredictionInterface:
    def __init__(self):
        """Initialize the prediction interface"""
        self.api = NHLAPIClient()
        self.learning_model = ImprovedSelfLearningModelV2()
        
    def get_todays_predictions(self):
        """Get predictions for today's games using the self-learning model"""
        print('🏒 NHL GAME PREDICTIONS (Self-Learning Model) 🏒')
        print('=' * 60)
        central_tz = pytz.timezone('US/Central')
        now_ct = datetime.now(central_tz)
        print(f'📅 Date (CT): {now_ct.strftime("%Y-%m-%d")}')
        
        # Get current model weights
        weights = self.learning_model.get_current_weights()
        print(f'🎯 Model Weights: xG={weights["xg_weight"]}, HDC={weights["hdc_weight"]}, Shots={weights["shot_attempts_weight"]}, GS={weights["game_score_weight"]}')
        print()
        
        # Define today's window in Central Time and convert to UTC bounds
        start_of_day_ct = now_ct.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day_ct = start_of_day_ct + timedelta(days=1)
        start_utc = start_of_day_ct.astimezone(pytz.utc)
        end_utc = end_of_day_ct.astimezone(pytz.utc)

        # Fetch schedule for the week (API returns a gameWeek)
        schedule_data = self.api.get_game_schedule(now_ct.strftime('%Y-%m-%d'))
        
        # Get ONLY today's games using the day bucket matching Central date
        games = []
        today_ct_str = now_ct.strftime('%Y-%m-%d')
        for day_data in schedule_data.get('gameWeek', []):
            if not isinstance(day_data, dict):
                continue
            if day_data.get('date') == today_ct_str and 'games' in day_data:
                games.extend(day_data['games'])
        
        # Helper to parse ISO8601 UTC timestamps
        def parse_utc(ts: str):
            try:
                # Ensure timezone-aware
                return datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(pytz.utc)
            except Exception:
                return None

        # Filter for games starting within today's Central day, using UTC bounds (extra safety)
        today_games = []
        for game in games:
            ts = game.get('startTimeUTC')
            dt_utc = parse_utc(ts) if isinstance(ts, str) else None
            if not dt_utc:
                continue
            if start_utc <= dt_utc < end_utc and game.get('gameState') in ['PRE', 'FUT']:
                today_games.append(game)
        
        print(f'🔍 Found {len(today_games)} games today')
        print()
        
        # Generate predictions using the self-learning model
        predictions = []
        for i, game in enumerate(today_games):
            away_team = game.get('awayTeam', {}).get('abbrev', 'UNK')
            home_team = game.get('homeTeam', {}).get('abbrev', 'UNK')
            game_time = game.get('startTimeUTC', 'UNK')
            # Convert to Central for display if possible
            try:
                dt_utc = parse_utc(game_time)
                game_time_ct = dt_utc.astimezone(central_tz).strftime('%Y-%m-%d %I:%M %p CT') if dt_utc else game_time
            except Exception:
                game_time_ct = game_time
            
            print(f'{i+1}. {away_team} @ {home_team}')
            print(f'   🕐 Time: {game_time_ct}')
            
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
                'predicted_away_win_prob': prediction["away_prob"] / 100,  # Convert to decimal
                'predicted_home_win_prob': prediction["home_prob"] / 100,  # Convert to decimal
                'favorite': favorite,
                'spread': spread
            })

        # Run daily learning update (only learn from completed games, not future predictions)
        try:
            self.learning_model.run_daily_update()
        except Exception as e:
            print(f"⚠️  Error updating learning model: {e}")

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
