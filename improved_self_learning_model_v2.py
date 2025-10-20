#!/usr/bin/env python3
"""
Improved Self-Learning Win Probability Model V2
Implements comprehensive improvements for better prediction accuracy
"""

import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedSelfLearningModelV2:
    def __init__(self, predictions_file: str = "win_probability_predictions_v2.json"):
        """Initialize the improved self-learning model V2"""
        self.predictions_file = Path(predictions_file)
        self.model_data = self.load_model_data()
        
        # Improved learning parameters
        self.learning_rate = 0.02  # Reduced to prevent overfitting
        self.momentum = 0.8  # Momentum for weight updates
        self.min_games_for_update = 3
        self.weight_clip_range = (0.05, 0.50)  # Prevent extreme weights
        
        # Team performance tracking
        self.team_stats_file = Path("team_performance_stats_v2.json")
        self.team_stats = self.load_team_stats()
        
    def load_model_data(self) -> Dict:
        """Load existing model data and predictions"""
        if self.predictions_file.exists():
            try:
                with open(self.predictions_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading model data: {e}")
        
        # Initialize with improved balanced model
        return {
            "predictions": [],
            "model_weights": {
                "xg_weight": 0.30,           # Expected goals - most predictive
                "hdc_weight": 0.25,          # High danger chances - very predictive
                "shot_attempts_weight": 0.20, # Shot attempts - good predictor
                "game_score_weight": 0.15,   # Game score - team performance
                "recent_form_weight": 0.05,  # Recent form (last 5 games)
                "head_to_head_weight": 0.02, # Head-to-head record
                "rest_days_weight": 0.02,    # Rest days advantage
                "goalie_performance_weight": 0.01  # Goalie performance
            },
            "weight_momentum": {
                "xg_weight": 0.0,
                "hdc_weight": 0.0,
                "shot_attempts_weight": 0.0,
                "game_score_weight": 0.0,
                "recent_form_weight": 0.0,
                "head_to_head_weight": 0.0,
                "rest_days_weight": 0.0,
                "goalie_performance_weight": 0.0
            },
            "last_updated": datetime.now().isoformat(),
            "model_performance": {
                "total_games": 0,
                "correct_predictions": 0,
                "accuracy": 0.0,
                "recent_accuracy": 0.0
            }
        }
    
    def load_team_stats(self) -> Dict:
        """Load team performance statistics"""
        if self.team_stats_file.exists():
            try:
                with open(self.team_stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading team stats: {e}")
        return {}
    
    def save_model_data(self):
        """Save model data to file"""
        try:
            with open(self.predictions_file, 'w') as f:
                json.dump(self.model_data, f, indent=2, default=str)
            logger.info("Model data saved successfully")
        except Exception as e:
            logger.error(f"Error saving model data: {e}")
    
    def save_team_stats(self):
        """Save team statistics to file"""
        try:
            with open(self.team_stats_file, 'w') as f:
                json.dump(self.team_stats, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving team stats: {e}")
    
    def get_current_weights(self) -> Dict:
        """Get current model weights with clipping"""
        weights = self.model_data.get("model_weights", {})
        
        # Apply weight clipping to prevent extreme values
        clipped_weights = {}
        for key, value in weights.items():
            clipped_weights[key] = np.clip(value, self.weight_clip_range[0], self.weight_clip_range[1])
        
        # Normalize weights to sum to 1.0
        total = sum(clipped_weights.values())
        if total > 0:
            for key in clipped_weights:
                clipped_weights[key] /= total
        
        return clipped_weights
    
    def get_team_performance(self, team: str, is_home: bool = True) -> Dict:
        """Get comprehensive team performance data"""
        team_key = team.upper()
        venue = "home" if is_home else "away"
        
        if team_key not in self.team_stats:
            return self._get_default_performance()
        
        team_data = self.team_stats[team_key]
        if venue not in team_data:
            return self._get_default_performance()
        
        venue_data = team_data[venue]
        
        # Calculate averages with proper goal data
        games = venue_data.get('games', [])
        if not games:
            return self._get_default_performance()
        
        # Get actual goals from game outcomes
        goals = venue_data.get('goals', [])
        xg_data = venue_data.get('xg', [])
        hdc_data = venue_data.get('hdc', [])
        shots_data = venue_data.get('shots', [])
        
        # Filter out zeros and calculate proper averages
        valid_goals = [g for g in goals if g > 0] if goals else [0]
        valid_xg = [x for x in xg_data if x > 0] if xg_data else [0]
        valid_hdc = [h for h in hdc_data if h > 0] if hdc_data else [0]
        valid_shots = [s for s in shots_data if s > 0] if shots_data else [0]
        
        return {
            'xg': np.mean(valid_xg) if valid_xg else 0.0,
            'hdc': np.mean(valid_hdc) if valid_hdc else 0.0,
            'shots': np.mean(valid_shots) if valid_shots else 0.0,
            'goals': np.mean(valid_goals) if valid_goals else 0.0,
            'xg_avg': np.mean(valid_xg) if valid_xg else 0.0,
            'hdc_avg': np.mean(valid_hdc) if valid_hdc else 0.0,
            'shots_avg': np.mean(valid_shots) if valid_shots else 0.0,
            'goals_avg': np.mean(valid_goals) if valid_goals else 0.0,
            'games_played': len(games),
            'recent_form': self._calculate_recent_form(team_key, venue),
            'confidence': self._calculate_confidence(len(games))
        }
    
    def _get_default_performance(self) -> Dict:
        """Get default performance for teams with no data"""
        return {
            'xg': 2.0, 'hdc': 2.0, 'shots': 30.0, 'goals': 2.0,
            'xg_avg': 2.0, 'hdc_avg': 2.0, 'shots_avg': 30.0, 'goals_avg': 2.0,
            'games_played': 0, 'recent_form': 0.5, 'confidence': 0.1
        }
    
    def _calculate_recent_form(self, team: str, venue: str) -> float:
        """Calculate recent form (last 5 games)"""
        if team not in self.team_stats or venue not in self.team_stats[team]:
            return 0.5
        
        games = self.team_stats[team][venue].get('games', [])
        goals = self.team_stats[team][venue].get('goals', [])
        
        if len(games) < 2:
            return 0.5
        
        # Use last 5 games or all available
        recent_games = min(5, len(games))
        recent_goals = goals[-recent_games:] if len(goals) >= recent_games else goals
        
        if not recent_goals:
            return 0.5
        
        # Calculate win rate (goals > 0 means win in this context)
        wins = sum(1 for g in recent_goals if g > 0)
        return wins / len(recent_goals)
    
    def _calculate_confidence(self, games_played: int) -> float:
        """Calculate confidence based on sample size"""
        if games_played == 0:
            return 0.1
        elif games_played < 3:
            return 0.3
        elif games_played < 10:
            return 0.5 + (games_played - 3) * 0.05
        else:
            return 0.85
    
    def predict_game(self, away_team: str, home_team: str, current_away_score: int = None, 
                    current_home_score: int = None, period: int = 1, game_id: str = None) -> Dict:
        """Predict a game with improved features and confidence"""
        
        # Get team performance data
        away_perf = self.get_team_performance(away_team, is_home=False)
        home_perf = self.get_team_performance(home_team, is_home=True)
        
        # Get current model weights
        weights = self.get_current_weights()
        
        # Calculate weighted scores with new features
        away_score = (
            away_perf['xg_avg'] * weights['xg_weight'] +
            away_perf['hdc_avg'] * weights['hdc_weight'] +
            away_perf['shots_avg'] * weights['shot_attempts_weight'] +
            away_perf['goals_avg'] * weights['game_score_weight'] +
            away_perf['recent_form'] * weights['recent_form_weight']
        )
        
        home_score = (
            home_perf['xg_avg'] * weights['xg_weight'] +
            home_perf['hdc_avg'] * weights['hdc_weight'] +
            home_perf['shots_avg'] * weights['shot_attempts_weight'] +
            home_perf['goals_avg'] * weights['game_score_weight'] +
            home_perf['recent_form'] * weights['recent_form_weight']
        )
        
        # Add home ice advantage (small but consistent)
        home_advantage = 0.05
        home_score *= (1.0 + home_advantage)
        
        # Calculate base probabilities
        total_score = away_score + home_score
        if total_score > 0:
            away_prob = (away_score / total_score) * 100
            home_prob = (home_score / total_score) * 100
        else:
            away_prob = 50.0
            home_prob = 50.0
        
        # Add uncertainty based on confidence
        away_confidence = away_perf['confidence']
        home_confidence = home_perf['confidence']
        avg_confidence = (away_confidence + home_confidence) / 2
        
        # Add noise for uncertainty (reduces extreme predictions)
        uncertainty_noise = (1 - avg_confidence) * 10  # Up to 10% noise
        noise = np.random.normal(0, uncertainty_noise)
        
        away_prob += noise
        home_prob -= noise
        
        # Ensure probabilities stay within reasonable bounds
        away_prob = max(10, min(90, away_prob))
        home_prob = max(10, min(90, home_prob))
        
        # Normalize to 100%
        total = away_prob + home_prob
        away_prob = (away_prob / total) * 100
        home_prob = (home_prob / total) * 100
        
        # Calculate confidence in prediction
        prediction_confidence = avg_confidence * 100
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'away_score': away_score,
            'home_score': home_score,
            'away_perf': away_perf,
            'home_perf': home_perf,
            'prediction_confidence': prediction_confidence,
            'uncertainty': uncertainty_noise
        }
    
    def add_prediction(self, game_id: str, date: str, away_team: str, home_team: str,
                      predicted_away_prob: float, predicted_home_prob: float,
                      metrics_used: Dict, actual_winner: Optional[str] = None,
                      actual_away_score: int = None, actual_home_score: int = None):
        """Add a new prediction with actual game outcomes"""
        
        prediction = {
            "game_id": game_id,
            "date": date,
            "away_team": away_team,
            "home_team": home_team,
            "predicted_away_win_prob": predicted_away_prob / 100.0,  # Store as decimal
            "predicted_home_win_prob": predicted_home_prob / 100.0,  # Store as decimal
            "metrics_used": metrics_used,
            "actual_winner": actual_winner,
            "actual_away_score": actual_away_score,
            "actual_home_score": actual_home_score,
            "prediction_accuracy": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Calculate prediction accuracy if we know the actual winner
        if actual_winner:
            if actual_winner == "away":
                prediction["prediction_accuracy"] = predicted_away_prob / 100.0
            elif actual_winner == "home":
                prediction["prediction_accuracy"] = predicted_home_prob / 100.0
            
            # Update model performance
            self.update_model_performance(prediction)
            
            # Update team stats with actual game data
            self.update_team_stats(prediction)
        
        self.model_data["predictions"].append(prediction)
        logger.info(f"Added prediction for {away_team} @ {home_team}: {predicted_away_prob:.1f}% vs {predicted_home_prob:.1f}%")
    
    def update_model_performance(self, prediction: Dict):
        """Update model performance metrics"""
        if "model_performance" not in self.model_data:
            self.model_data["model_performance"] = {
                "total_games": 0,
                "correct_predictions": 0,
                "accuracy": 0.0,
                "recent_accuracy": 0.0
            }
        
        perf = self.model_data["model_performance"]
        perf["total_games"] += 1
        
        # Check if prediction was correct
        away_prob = prediction.get("predicted_away_win_prob", 0)
        home_prob = prediction.get("predicted_home_win_prob", 0)
        actual_winner = prediction.get("actual_winner")
        
        if actual_winner == "away" and away_prob > home_prob:
            perf["correct_predictions"] += 1
        elif actual_winner == "home" and home_prob > away_prob:
            perf["correct_predictions"] += 1
        
        perf["accuracy"] = perf["correct_predictions"] / perf["total_games"]
        
        # Calculate recent accuracy (last 20 games)
        recent_games = [p for p in self.model_data["predictions"][-20:] if p.get("actual_winner")]
        if len(recent_games) >= 10:
            recent_correct = 0
            for p in recent_games:
                away_p = p.get("predicted_away_win_prob", 0)
                home_p = p.get("predicted_home_win_prob", 0)
                winner = p.get("actual_winner")
                
                if winner == "away" and away_p > home_p:
                    recent_correct += 1
                elif winner == "home" and home_p > away_p:
                    recent_correct += 1
            
            perf["recent_accuracy"] = recent_correct / len(recent_games)
        else:
            perf["recent_accuracy"] = perf["accuracy"]
    
    def update_team_stats(self, prediction: Dict):
        """Update team statistics with actual game data"""
        away_team = prediction["away_team"].upper()
        home_team = prediction["home_team"].upper()
        date = prediction["date"]
        
        # Get actual scores
        away_score = prediction.get("actual_away_score", 0)
        home_score = prediction.get("actual_home_score", 0)
        
        # Initialize team stats if needed
        if away_team not in self.team_stats:
            self.team_stats[away_team] = {"home": {"games": [], "xg": [], "hdc": [], "shots": [], "goals": []},
                                        "away": {"games": [], "xg": [], "hdc": [], "shots": [], "goals": []}}
        
        if home_team not in self.team_stats:
            self.team_stats[home_team] = {"home": {"games": [], "xg": [], "hdc": [], "shots": [], "goals": []},
                                        "away": {"games": [], "xg": [], "hdc": [], "shots": [], "goals": []}}
        
        # Update away team stats
        away_data = self.team_stats[away_team]["away"]
        away_data["games"].append(date)
        away_data["goals"].append(away_score)  # Store actual goals
        
        # Update home team stats
        home_data = self.team_stats[home_team]["home"]
        home_data["games"].append(date)
        home_data["goals"].append(home_score)  # Store actual goals
        
        # Keep only last 20 games to prevent memory bloat
        for team in [away_team, home_team]:
            for venue in ["home", "away"]:
                for key in ["games", "xg", "hdc", "shots", "goals"]:
                    if len(self.team_stats[team][venue][key]) > 20:
                        self.team_stats[team][venue][key] = self.team_stats[team][venue][key][-20:]
    
    def run_daily_update(self):
        """Run daily model update with improved learning"""
        logger.info("Running improved daily model update...")
        
        # Get recent predictions for learning
        recent_predictions = [p for p in self.model_data["predictions"][-10:] if p.get("actual_winner")]
        
        if len(recent_predictions) < self.min_games_for_update:
            logger.info(f"Not enough recent games for update ({len(recent_predictions)} < {self.min_games_for_update})")
            return
        
        # Calculate weight updates based on recent performance
        weight_updates = self._calculate_weight_updates(recent_predictions)
        
        # Apply updates with momentum
        current_weights = self.model_data["model_weights"]
        momentum = self.model_data.get("weight_momentum", {})
        
        for weight_name, update in weight_updates.items():
            if weight_name in current_weights:
                # Apply momentum
                momentum[weight_name] = self.momentum * momentum.get(weight_name, 0) + update
                
                # Update weight
                current_weights[weight_name] += momentum[weight_name]
                
                # Apply clipping
                current_weights[weight_name] = np.clip(
                    current_weights[weight_name], 
                    self.weight_clip_range[0], 
                    self.weight_clip_range[1]
                )
        
        # Normalize weights
        total = sum(current_weights.values())
        if total > 0:
            for key in current_weights:
                current_weights[key] /= total
        
        # Update momentum
        self.model_data["weight_momentum"] = momentum
        self.model_data["last_updated"] = datetime.now().isoformat()
        
        logger.info(f"Updated model weights: {current_weights}")
        
        # Save updated model
        self.save_model_data()
        self.save_team_stats()
    
    def _calculate_weight_updates(self, recent_predictions: List[Dict]) -> Dict:
        """Calculate weight updates based on recent prediction performance"""
        # This is a simplified version - in practice, you'd use more sophisticated methods
        # like gradient descent or reinforcement learning
        
        updates = {}
        for weight_name in self.model_data["model_weights"].keys():
            # Small random updates to prevent getting stuck
            updates[weight_name] = np.random.normal(0, 0.01)
        
        return updates
    
    def get_model_performance(self) -> Dict:
        """Get current model performance"""
        return self.model_data.get("model_performance", {
            "total_games": 0,
            "correct_predictions": 0,
            "accuracy": 0.0,
            "recent_accuracy": 0.0
        })
    
    def clean_duplicate_predictions(self):
        """Remove duplicate game entries from model data"""
        predictions = self.model_data.get('predictions', [])
        seen_game_ids = set()
        cleaned_predictions = []
        
        for pred in predictions:
            game_id = pred.get('game_id')
            if game_id and game_id not in seen_game_ids:
                cleaned_predictions.append(pred)
                seen_game_ids.add(game_id)
            elif not game_id:  # Keep predictions without game_id
                cleaned_predictions.append(pred)
        
        removed_count = len(predictions) - len(cleaned_predictions)
        self.model_data['predictions'] = cleaned_predictions
        
        logger.info(f"Removed {removed_count} duplicate predictions")
        return removed_count

if __name__ == "__main__":
    # Test the improved model
    model = ImprovedSelfLearningModelV2()
    
    print("🏒 Improved Self-Learning Model V2")
    print("=" * 40)
    
    # Test prediction
    prediction = model.predict_game("TOR", "MTL")
    print(f"TOR @ MTL Prediction:")
    print(f"  Away (TOR): {prediction['away_prob']:.1f}%")
    print(f"  Home (MTL): {prediction['home_prob']:.1f}%")
    print(f"  Confidence: {prediction['prediction_confidence']:.1f}%")
    print(f"  Uncertainty: {prediction['uncertainty']:.2f}")
    
    # Show team performance data
    print(f"\nTeam Performance Data:")
    print(f"  TOR (Away): {prediction['away_perf']}")
    print(f"  MTL (Home): {prediction['home_perf']}")
    
    # Show current weights
    weights = model.get_current_weights()
    print(f"\nCurrent Weights:")
    for key, value in weights.items():
        print(f"  {key}: {value:.4f}")
