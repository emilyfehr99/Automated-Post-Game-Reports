"""
Self-Learning Win Probability Model
A separate system that learns from its own predictions and game outcomes
Does NOT affect the current post-game reports
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass, asdict
from nhl_api_client import NHLAPIClient
from advanced_metrics_analyzer import AdvancedMetricsAnalyzer


@dataclass
class PredictionRecord:
    """Record of a win probability prediction"""
    game_id: str
    date: str
    away_team: str
    home_team: str
    predicted_away_win_prob: float
    predicted_home_win_prob: float
    actual_winner: Optional[str] = None  # "away", "home", or None if not yet determined
    metrics_used: Optional[Dict] = None
    prediction_accuracy: Optional[float] = None  # Calculated after game ends
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class SelfLearningWinProbabilityModel:
    """Self-improving win probability model that learns from its predictions"""
    
    def __init__(self, data_file: str = "win_probability_predictions.json"):
        self.data_file = Path(data_file)
        self.client = NHLAPIClient()
        self.predictions: List[PredictionRecord] = []
        self.model_weights = {
            'xg_weight': 0.4,
            'hdc_weight': 0.3,
            'shot_attempts_weight': 0.2,
            'faceoff_weight': 0.05,
            'other_metrics_weight': 0.05
        }
        self.load_predictions()
    
    def load_predictions(self):
        """Load existing predictions from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.predictions = [PredictionRecord(**pred) for pred in data.get('predictions', [])]
                print(f"📊 Loaded {len(self.predictions)} existing predictions")
            except Exception as e:
                print(f"⚠️  Could not load predictions: {e}")
                self.predictions = []
        else:
            self.predictions = []
    
    def save_predictions(self):
        """Save predictions to file"""
        try:
            data = {
                'predictions': [asdict(pred) for pred in self.predictions],
                'model_weights': self.model_weights,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Saved {len(self.predictions)} predictions")
        except Exception as e:
            print(f"⚠️  Could not save predictions: {e}")
    
    def make_prediction(self, game_data: Dict) -> Tuple[float, float, Dict]:
        """
        Make a win probability prediction using current model weights
        Returns: (away_win_prob, home_win_prob, metrics_used)
        """
        try:
            # Get game info
            away_team_id = game_data['boxscore']['awayTeam']['id']
            home_team_id = game_data['boxscore']['homeTeam']['id']
            away_team_abbrev = game_data['boxscore']['awayTeam']['abbrev']
            home_team_abbrev = game_data['boxscore']['homeTeam']['abbrev']
            
            # Analyze metrics
            analyzer = AdvancedMetricsAnalyzer(game_data['play_by_play'])
            
            # Get team metrics
            away_metrics = {
                'shot_quality': analyzer.calculate_shot_quality_metrics(away_team_id),
                'pressure': analyzer.calculate_pressure_metrics(away_team_id)
            }
            
            home_metrics = {
                'shot_quality': analyzer.calculate_shot_quality_metrics(home_team_id),
                'pressure': analyzer.calculate_pressure_metrics(home_team_id)
            }
            
            # Extract key metrics
            away_xg = away_metrics['shot_quality'].get('expected_goals', 0)
            home_xg = home_metrics['shot_quality'].get('expected_goals', 0)
            
            away_hdc = away_metrics['shot_quality'].get('high_danger_chances', 0)
            home_hdc = home_metrics['shot_quality'].get('high_danger_chances', 0)
            
            away_shots = away_metrics['shot_quality'].get('shot_attempts', 0)
            home_shots = home_metrics['shot_quality'].get('shot_attempts', 0)
            
            # Get faceoff data from boxscore
            away_fo_pct = game_data['boxscore']['awayTeam'].get('faceoffWinPercentage', 50)
            home_fo_pct = game_data['boxscore']['homeTeam'].get('faceoffWinPercentage', 50)
            
            # Calculate weighted score using current model weights
            away_score = (
                away_xg * self.model_weights['xg_weight'] +
                away_hdc * self.model_weights['hdc_weight'] +
                away_shots * self.model_weights['shot_attempts_weight'] +
                away_fo_pct * self.model_weights['faceoff_weight']
            )
            
            home_score = (
                home_xg * self.model_weights['xg_weight'] +
                home_hdc * self.model_weights['hdc_weight'] +
                home_shots * self.model_weights['shot_attempts_weight'] +
                home_fo_pct * self.model_weights['faceoff_weight']
            )
            
            # Convert to probabilities
            total_score = away_score + home_score
            if total_score > 0:
                away_win_prob = (away_score / total_score) * 100
                home_win_prob = (home_score / total_score) * 100
            else:
                away_win_prob = 50.0
                home_win_prob = 50.0
            
            # Store metrics used
            metrics_used = {
                'away_xg': away_xg,
                'home_xg': home_xg,
                'away_hdc': away_hdc,
                'home_hdc': home_hdc,
                'away_shots': away_shots,
                'home_shots': home_shots,
                'away_fo_pct': away_fo_pct,
                'home_fo_pct': home_fo_pct,
                'model_weights': self.model_weights.copy()
            }
            
            return away_win_prob, home_win_prob, metrics_used
            
        except Exception as e:
            print(f"❌ Error making prediction: {e}")
            return 50.0, 50.0, {}
    
    def record_prediction(self, game_data: Dict, game_id: str) -> PredictionRecord:
        """Record a prediction for a game"""
        try:
            # Get game info
            away_team = game_data['boxscore']['awayTeam']['abbrev']
            home_team = game_data['boxscore']['homeTeam']['abbrev']
            game_date = game_data['boxscore']['gameDate'][:10]  # YYYY-MM-DD
            
            # Make prediction
            away_win_prob, home_win_prob, metrics_used = self.make_prediction(game_data)
            
            # Create prediction record
            prediction = PredictionRecord(
                game_id=game_id,
                date=game_date,
                away_team=away_team,
                home_team=home_team,
                predicted_away_win_prob=away_win_prob,
                predicted_home_win_prob=home_win_prob,
                metrics_used=metrics_used
            )
            
            # Add to predictions
            self.predictions.append(prediction)
            
            print(f"📊 Recorded prediction: {away_team} {away_win_prob:.1f}% vs {home_team} {home_win_prob:.1f}%")
            
            return prediction
            
        except Exception as e:
            print(f"❌ Error recording prediction: {e}")
            return None
    
    def update_outcome(self, game_id: str, actual_winner: str):
        """Update a prediction with the actual game outcome"""
        try:
            # Find the prediction
            prediction = None
            for pred in self.predictions:
                if pred.game_id == game_id:
                    prediction = pred
                    break
            
            if not prediction:
                print(f"⚠️  No prediction found for game {game_id}")
                return
            
            # Update with actual winner
            prediction.actual_winner = actual_winner
            
            # Calculate prediction accuracy
            if actual_winner == "away":
                predicted_winner_prob = prediction.predicted_away_win_prob
            elif actual_winner == "home":
                predicted_winner_prob = prediction.predicted_home_win_prob
            else:
                predicted_winner_prob = 50.0  # Tie or unknown
            
            # Accuracy is how confident we were in the correct outcome
            prediction.prediction_accuracy = predicted_winner_prob / 100.0
            
            print(f"✅ Updated outcome for {prediction.away_team} @ {prediction.home_team}: {actual_winner} won (accuracy: {prediction.prediction_accuracy:.3f})")
            
        except Exception as e:
            print(f"❌ Error updating outcome: {e}")
    
    def retrain_model(self):
        """Retrain the model based on prediction accuracy"""
        try:
            # Get predictions with outcomes
            completed_predictions = [p for p in self.predictions if p.actual_winner is not None]
            
            if len(completed_predictions) < 10:
                print(f"📊 Need at least 10 completed predictions to retrain (have {len(completed_predictions)})")
                return
            
            print(f"🧠 Retraining model with {len(completed_predictions)} completed predictions...")
            
            # Simple weight adjustment based on accuracy
            # This is a basic approach - could be enhanced with more sophisticated ML
            
            # Calculate current model performance
            avg_accuracy = np.mean([p.prediction_accuracy for p in completed_predictions])
            print(f"📈 Current model accuracy: {avg_accuracy:.3f}")
            
            # Analyze which metrics were most predictive
            # This is a simplified approach - in practice, you'd use more sophisticated analysis
            
            # For now, just log the performance
            print(f"🎯 Model performance summary:")
            print(f"   - Total predictions: {len(self.predictions)}")
            print(f"   - Completed games: {len(completed_predictions)}")
            print(f"   - Average accuracy: {avg_accuracy:.3f}")
            print(f"   - Current weights: {self.model_weights}")
            
            # TODO: Implement actual weight adjustment based on metric performance
            # This would involve analyzing which metrics were most predictive
            # and adjusting the weights accordingly
            
        except Exception as e:
            print(f"❌ Error retraining model: {e}")
    
    def get_model_stats(self) -> Dict:
        """Get current model statistics"""
        completed_predictions = [p for p in self.predictions if p.actual_winner is not None]
        
        if not completed_predictions:
            return {
                'total_predictions': len(self.predictions),
                'completed_predictions': 0,
                'average_accuracy': 0.0,
                'model_weights': self.model_weights
            }
        
        avg_accuracy = np.mean([p.prediction_accuracy for p in completed_predictions])
        
        return {
            'total_predictions': len(self.predictions),
            'completed_predictions': len(completed_predictions),
            'average_accuracy': avg_accuracy,
            'model_weights': self.model_weights,
            'last_updated': datetime.now().isoformat()
        }
    
    def process_completed_games(self):
        """Process recently completed games to update outcomes"""
        try:
            # Get yesterday's games (games that might have finished)
            central_tz = timezone(timedelta(hours=-6))
            central_now = datetime.now(central_tz)
            yesterday = central_now - timedelta(days=1)
            yesterday_str = yesterday.strftime('%Y-%m-%d')
            
            print(f"🔍 Checking outcomes for games from {yesterday_str}...")
            
            # Get yesterday's games
            schedule = self.client.get_game_schedule(yesterday_str)
            if not schedule or 'gameWeek' not in schedule:
                print("No games found for yesterday")
                return
            
            games = []
            for day in schedule['gameWeek']:
                if day.get('date') == yesterday_str and 'games' in day:
                    games.extend(day['games'])
            
            # Check each game
            for game in games:
                game_id = str(game.get('id'))
                game_state = game.get('gameState', 'UNKNOWN')
                
                # Find prediction for this game
                prediction = None
                for pred in self.predictions:
                    if pred.game_id == game_id and pred.actual_winner is None:
                        prediction = pred
                        break
                
                if not prediction:
                    continue
                
                # Determine actual winner
                if game_state == 'OFF':  # Game finished
                    away_goals = game.get('awayTeam', {}).get('score', 0)
                    home_goals = game.get('homeTeam', {}).get('score', 0)
                    
                    if away_goals > home_goals:
                        actual_winner = "away"
                    elif home_goals > away_goals:
                        actual_winner = "home"
                    else:
                        actual_winner = "tie"
                    
                    # Update prediction with outcome
                    self.update_outcome(game_id, actual_winner)
            
            # Save updated predictions
            self.save_predictions()
            
        except Exception as e:
            print(f"❌ Error processing completed games: {e}")
    
    def run_daily_update(self):
        """Run daily update to process new games and retrain model"""
        print("🧠 SELF-LEARNING WIN PROBABILITY MODEL - DAILY UPDATE")
        print("=" * 60)
        
        # Process completed games from yesterday
        self.process_completed_games()
        
        # Retrain model if we have enough data
        self.retrain_model()
        
        # Show current stats
        stats = self.get_model_stats()
        print(f"\n📊 Model Statistics:")
        print(f"   - Total predictions: {stats['total_predictions']}")
        print(f"   - Completed predictions: {stats['completed_predictions']}")
        print(f"   - Average accuracy: {stats['average_accuracy']:.3f}")
        
        print("\n✅ Daily update completed!")


if __name__ == "__main__":
    # Run daily update
    model = SelfLearningWinProbabilityModel()
    model.run_daily_update()
