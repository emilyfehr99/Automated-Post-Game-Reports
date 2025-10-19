#!/usr/bin/env python3
"""
Improved Self-Learning Win Probability Model
Implements Phase 1 improvements for better prediction accuracy
"""

import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedSelfLearningModel:
    def __init__(self, predictions_file: str = "win_probability_predictions.json"):
        """Initialize the improved self-learning model"""
        self.predictions_file = Path(predictions_file)
        self.model_data = self.load_model_data()
        
        # Improved learning parameters
        self.learning_rate = 0.05  # Increased from 0.01
        self.momentum = 0.9  # New: momentum for weight updates
        self.min_games_for_update = 5
        
        # Team performance tracking
        self.team_stats_file = Path("team_performance_stats.json")
        self.team_stats = self.load_team_stats()
        
    def load_model_data(self) -> Dict:
        """Load existing model data and predictions"""
        if self.predictions_file.exists():
            try:
                with open(self.predictions_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading model data: {e}")
        
        # Initialize with default model
        return {
            "predictions": [],
            "model_weights": {
                "xg_weight": 0.35,           # Reduced from 0.4 to make room for Edge data
                "hdc_weight": 0.25,          # Reduced from 0.3
                "shot_attempts_weight": 0.15, # Reduced from 0.2
                "game_score_weight": 0.1,    # Kept same
                "edge_speed_weight": 0.05,   # NEW: Edge speed advantage
                "edge_distance_weight": 0.03, # NEW: Edge distance capability
                "edge_burst_weight": 0.02,   # NEW: Edge burst potential
                "other_metrics_weight": 0.0
            },
            "weight_momentum": {  # New: momentum tracking
                "xg_weight": 0.0,
                "hdc_weight": 0.0,
                "shot_attempts_weight": 0.0,
                "game_score_weight": 0.0,
                "edge_speed_weight": 0.0,    # NEW: Edge momentum tracking
                "edge_distance_weight": 0.0, # NEW: Edge momentum tracking
                "edge_burst_weight": 0.0,   # NEW: Edge momentum tracking
                "other_metrics_weight": 0.0
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
        
        # Initialize empty team stats
        return {}
    
    def save_model_data(self):
        """Save updated model data"""
        try:
            self.model_data["last_updated"] = datetime.now().isoformat()
            with open(self.predictions_file, 'w') as f:
                json.dump(self.model_data, f, indent=2)
            logger.info("Model data saved successfully")
        except Exception as e:
            logger.error(f"Error saving model data: {e}")
    
    def save_team_stats(self):
        """Save team performance statistics"""
        try:
            with open(self.team_stats_file, 'w') as f:
                json.dump(self.team_stats, f, indent=2)
            logger.info("Team stats saved successfully")
        except Exception as e:
            logger.error(f"Error saving team stats: {e}")
    
    def update_team_stats(self, game_data: Dict):
        """Update team performance statistics from game data"""
        try:
            # Extract team info
            away_team = game_data.get('away_team', '')
            home_team = game_data.get('home_team', '')
            away_score = game_data.get('away_score', 0)
            home_score = game_data.get('home_score', 0)
            
            # Get metrics from game data
            metrics = game_data.get('metrics_used', {})
            away_xg = metrics.get('away_xg', 0)
            home_xg = metrics.get('home_xg', 0)
            away_hdc = metrics.get('away_hdc', 0)
            home_hdc = metrics.get('home_hdc', 0)
            away_shots = metrics.get('away_shots', 0)
            home_shots = metrics.get('home_shots', 0)
            
            # Update away team stats
            if away_team not in self.team_stats:
                self.team_stats[away_team] = {
                    'home': {'games': [], 'xg': [], 'hdc': [], 'shots': [], 'goals': []},
                    'away': {'games': [], 'xg': [], 'hdc': [], 'shots': [], 'goals': []}
                }
            
            # Add away team game (they were away)
            self.team_stats[away_team]['away']['games'].append(game_data.get('date', ''))
            self.team_stats[away_team]['away']['xg'].append(away_xg)
            self.team_stats[away_team]['away']['hdc'].append(away_hdc)
            self.team_stats[away_team]['away']['shots'].append(away_shots)
            self.team_stats[away_team]['away']['goals'].append(away_score)
            
            # Update home team stats
            if home_team not in self.team_stats:
                self.team_stats[home_team] = {
                    'home': {'games': [], 'xg': [], 'hdc': [], 'shots': [], 'goals': []},
                    'away': {'games': [], 'xg': [], 'hdc': [], 'shots': [], 'goals': []}
                }
            
            # Add home team game (they were home)
            self.team_stats[home_team]['home']['games'].append(game_data.get('date', ''))
            self.team_stats[home_team]['home']['xg'].append(home_xg)
            self.team_stats[home_team]['home']['hdc'].append(home_hdc)
            self.team_stats[home_team]['home']['shots'].append(home_shots)
            self.team_stats[home_team]['home']['goals'].append(home_score)
            
            # Keep only last 20 games for each team/situation
            for team in [away_team, home_team]:
                for situation in ['home', 'away']:
                    for stat in ['games', 'xg', 'hdc', 'shots', 'goals']:
                        if len(self.team_stats[team][situation][stat]) > 20:
                            self.team_stats[team][situation][stat] = self.team_stats[team][situation][stat][-20:]
            
            self.save_team_stats()
            
        except Exception as e:
            logger.error(f"Error updating team stats: {e}")
    
    def get_team_performance(self, team: str, is_home: bool) -> Dict:
        """Get team performance metrics with recent form weighting"""
        situation = 'home' if is_home else 'away'
        
        if team not in self.team_stats or situation not in self.team_stats[team]:
            # Return default values if no data
            return {
                'xg': 2.5,
                'hdc': 1.3,
                'shots': 25,
                'goals': 2.8,
                'xg_avg': 2.5,
                'hdc_avg': 1.3,
                'shots_avg': 25,
                'goals_avg': 2.8,
                'games_played': 0
            }
        
        team_data = self.team_stats[team][situation]
        games_played = len(team_data['games'])
        
        if games_played == 0:
            return {
                'xg': 2.5,
                'hdc': 1.3,
                'shots': 25,
                'goals': 2.8,
                'xg_avg': 2.5,
                'hdc_avg': 1.3,
                'shots_avg': 25,
                'goals_avg': 2.8,
                'games_played': 0
            }
        
        # Apply recent form weighting (exponential decay)
        weights = []
        for i in range(games_played):
            # More recent games get higher weight
            weight = np.exp(-0.1 * (games_played - 1 - i))  # Decay factor
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Calculate weighted averages
        xg_avg = sum(xg * w for xg, w in zip(team_data['xg'], weights))
        hdc_avg = sum(hdc * w for hdc, w in zip(team_data['hdc'], weights))
        shots_avg = sum(shots * w for shots, w in zip(team_data['shots'], weights))
        goals_avg = sum(goals * w for goals, w in zip(team_data['goals'], weights))
        
        return {
            'xg': xg_avg,
            'hdc': hdc_avg,
            'shots': shots_avg,
            'goals': goals_avg,
            'xg_avg': xg_avg,
            'hdc_avg': hdc_avg,
            'shots_avg': shots_avg,
            'goals_avg': goals_avg,
            'games_played': games_played
        }
    
    def get_edge_advantages(self, away_team: str, home_team: str) -> Dict:
        """Get Edge data advantages for both teams"""
        try:
            # Try to load Edge data
            edge_data_file = Path("nhl_edge_data.json")
            if not edge_data_file.exists():
                logger.warning("Edge data file not found, using default values")
                return {
                    'away_speed': 0.0,
                    'away_distance': 0.0,
                    'away_burst': 0.0,
                    'home_speed': 0.0,
                    'home_distance': 0.0,
                    'home_burst': 0.0
                }
            
            with open(edge_data_file, 'r') as f:
                edge_data = json.load(f)
            
            team_stats = edge_data.get('team_stats', {})
            
            # Get team Edge statistics
            away_stats = team_stats.get(away_team, {})
            home_stats = team_stats.get(home_team, {})
            
            # Calculate relative advantages (0-1 scale)
            away_speed = away_stats.get('speed_score', 0.5)
            away_distance = away_stats.get('distance_score', 0.5)
            away_burst = away_stats.get('burst_score', 0.5)
            
            home_speed = home_stats.get('speed_score', 0.5)
            home_distance = home_stats.get('distance_score', 0.5)
            home_burst = home_stats.get('burst_score', 0.5)
            
            # Convert to relative advantages (positive = team advantage)
            return {
                'away_speed': (away_speed - home_speed) * 0.1,  # Scale to 10% max impact
                'away_distance': (away_distance - home_distance) * 0.1,
                'away_burst': (away_burst - home_burst) * 0.1,
                'home_speed': (home_speed - away_speed) * 0.1,
                'home_distance': (home_distance - away_distance) * 0.1,
                'home_burst': (home_burst - away_burst) * 0.1
            }
            
        except Exception as e:
            logger.error(f"Error getting Edge advantages: {e}")
            return {
                'away_speed': 0.0,
                'away_distance': 0.0,
                'away_burst': 0.0,
                'home_speed': 0.0,
                'home_distance': 0.0,
                'home_burst': 0.0
            }
    
    def predict_game(self, away_team: str, home_team: str, current_away_score: int = None, current_home_score: int = None, period: int = 1, game_id: str = None) -> Dict:
        """Predict a game using improved team-specific data including Edge metrics"""
        # Get team performance data
        away_perf = self.get_team_performance(away_team, is_home=False)
        home_perf = self.get_team_performance(home_team, is_home=True)
        
        # If we have a game_id, try to get live stats to override historical data
        if game_id:
            try:
                from live_stats_extractor import LiveStatsExtractor
                extractor = LiveStatsExtractor()
                live_stats = extractor.get_live_stats(game_id)
                
                if live_stats and live_stats['away_team'] == away_team and live_stats['home_team'] == home_team:
                    # Override with live data
                    away_perf['hdc'] = live_stats['away_hdc']
                    away_perf['shots'] = live_stats['away_shots']
                    home_perf['hdc'] = live_stats['home_hdc']
                    home_perf['shots'] = live_stats['home_shots']
                    print(f"Using live stats: {away_team} HDC={live_stats['away_hdc']} Shots={live_stats['away_shots']}, {home_team} HDC={live_stats['home_hdc']} Shots={live_stats['home_shots']}")
            except Exception as e:
                print(f"Could not get live stats: {e}")
        
        # Get Edge data advantages
        edge_advantages = self.get_edge_advantages(away_team, home_team)
        
        # Get current model weights
        weights = self.get_current_weights()
        
        # Calculate weighted scores (traditional metrics)
        away_score = (
            away_perf['xg_avg'] * weights['xg_weight'] +
            away_perf['hdc_avg'] * weights['hdc_weight'] +
            away_perf['shots_avg'] * weights['shot_attempts_weight'] +
            away_perf['goals_avg'] * weights['game_score_weight']
        )
        
        home_score = (
            home_perf['xg_avg'] * weights['xg_weight'] +
            home_perf['hdc_avg'] * weights['hdc_weight'] +
            home_perf['shots_avg'] * weights['shot_attempts_weight'] +
            home_perf['goals_avg'] * weights['game_score_weight']
        )
        
        # Add Edge data advantages (small but meaningful impact)
        away_edge_advantage = (
            edge_advantages['away_speed'] * weights['edge_speed_weight'] +
            edge_advantages['away_distance'] * weights['edge_distance_weight'] +
            edge_advantages['away_burst'] * weights['edge_burst_weight']
        )
        
        home_edge_advantage = (
            edge_advantages['home_speed'] * weights['edge_speed_weight'] +
            edge_advantages['home_distance'] * weights['edge_distance_weight'] +
            edge_advantages['home_burst'] * weights['edge_burst_weight']
        )
        
        # Apply Edge advantages (as multipliers, max 5% impact)
        away_score *= (1.0 + away_edge_advantage)
        home_score *= (1.0 + home_edge_advantage)
        
        # Add home ice advantage based on actual learned data
        home_advantage = weights.get('home_advantage_weight', 0.023)  # 2.3% from our actual data
        home_score *= (1.0 + home_advantage)
        
        # Calculate base probabilities
        total_score = away_score + home_score
        if total_score > 0:
            away_prob = (away_score / total_score) * 100
            home_prob = (home_score / total_score) * 100
        else:
            away_prob = 50.0
            home_prob = 50.0
        
        # Adjust for current live score if provided
        if current_away_score is not None and current_home_score is not None:
            score_diff = current_away_score - current_home_score
            
            # Time remaining in game (rough estimate)
            if period == 1:
                time_left = 40  # 2 periods left
            elif period == 2:
                time_left = 20  # 1 period left
            elif period == 3:
                time_left = 5   # Less than 1 period
            else:
                time_left = 1   # Overtime
                
            # Adjust probabilities based on score and time
            if score_diff > 0:  # Away team leading
                # Leading team gets boost, but less as time runs out
                boost = (score_diff * 25) * (time_left / 40)  # Max 25% per goal
                away_prob += boost
                home_prob -= boost
            elif score_diff < 0:  # Home team leading
                boost = (abs(score_diff) * 25) * (time_left / 40)
                home_prob += boost
                away_prob -= boost
            
            # Ensure probabilities stay within reasonable bounds
            away_prob = max(5, min(95, away_prob))
            home_prob = max(5, min(95, home_prob))
            
            # Normalize to 100%
            total = away_prob + home_prob
            away_prob = (away_prob / total) * 100
            home_prob = (home_prob / total) * 100
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'away_score': away_score,
            'home_score': home_score,
            'away_perf': away_perf,
            'home_perf': home_perf
        }
    
    def add_prediction(self, game_id: str, date: str, away_team: str, home_team: str,
                      predicted_away_prob: float, predicted_home_prob: float,
                      metrics_used: Dict, actual_winner: Optional[str] = None):
        """Add a new prediction to the model data"""
        
        prediction = {
            "game_id": game_id,
            "date": date,
            "away_team": away_team,
            "home_team": home_team,
            "predicted_away_win_prob": predicted_away_prob,
            "predicted_home_win_prob": predicted_home_prob,
            "metrics_used": metrics_used,
            "actual_winner": actual_winner,
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
            
            # Update team stats
            self.update_team_stats(prediction)
        
        self.model_data["predictions"].append(prediction)
        logger.info(f"Added prediction for {away_team} @ {home_team}: {predicted_away_prob:.1f}% vs {predicted_home_prob:.1f}%")
    
    def update_model_performance(self, prediction: Dict):
        """Update model performance metrics"""
        # Initialize model_performance if it doesn't exist
        if "model_performance" not in self.model_data:
            self.model_data["model_performance"] = {
                "total_games": 0,
                "correct_predictions": 0,
                "accuracy": 0.0,
                "recent_accuracy": 0.0
            }
        
        perf = self.model_data["model_performance"]
        perf["total_games"] += 1
        
        if prediction["prediction_accuracy"] is not None:
            if prediction["prediction_accuracy"] > 0.5:  # Correct prediction
                perf["correct_predictions"] += 1
            
            perf["accuracy"] = perf["correct_predictions"] / perf["total_games"]
            
            # Calculate recent accuracy (last 20 games)
            recent_predictions = [p for p in self.model_data["predictions"][-20:] 
                                if p.get("prediction_accuracy") is not None]
            if recent_predictions:
                recent_correct = sum(1 for p in recent_predictions if p["prediction_accuracy"] > 0.5)
                perf["recent_accuracy"] = recent_correct / len(recent_predictions)
    
    def update_model_weights(self):
        """Update model weights with improved learning and momentum"""
        logger.info("Running improved daily model update...")
        
        # Get recent predictions for learning
        recent_predictions = [p for p in self.model_data["predictions"][-20:] 
                            if p.get("prediction_accuracy") is not None and p.get("actual_winner")]
        
        if len(recent_predictions) < self.min_games_for_update:
            logger.info(f"Not enough games for update ({len(recent_predictions)} < {self.min_games_for_update})")
            return
        
        # Calculate weight adjustments based on prediction errors
        weight_adjustments = {
            "xg_weight": 0.0,
            "hdc_weight": 0.0,
            "shot_attempts_weight": 0.0,
            "game_score_weight": 0.0,
            "other_metrics_weight": 0.0
        }
        
        for prediction in recent_predictions:
            # Calculate prediction error
            predicted_winner = 'away' if prediction['predicted_away_win_prob'] > prediction['predicted_home_win_prob'] else 'home'
            actual_winner = prediction['actual_winner']
            
            if predicted_winner != actual_winner:
                # Prediction was wrong - adjust weights
                metrics = prediction.get('metrics_used', {})
                
                # Simple heuristic: if away team won but had lower xG, reduce xG weight
                if actual_winner == 'away' and metrics.get('away_xg', 0) < metrics.get('home_xg', 0):
                    weight_adjustments['xg_weight'] -= self.learning_rate * 0.1
                elif actual_winner == 'home' and metrics.get('home_xg', 0) < metrics.get('away_xg', 0):
                    weight_adjustments['xg_weight'] -= self.learning_rate * 0.1
                else:
                    weight_adjustments['xg_weight'] += self.learning_rate * 0.05
                
                # Similar logic for other metrics
                if actual_winner == 'away' and metrics.get('away_hdc', 0) < metrics.get('home_hdc', 0):
                    weight_adjustments['hdc_weight'] -= self.learning_rate * 0.1
                elif actual_winner == 'home' and metrics.get('home_hdc', 0) < metrics.get('away_hdc', 0):
                    weight_adjustments['hdc_weight'] -= self.learning_rate * 0.1
                else:
                    weight_adjustments['hdc_weight'] += self.learning_rate * 0.05
        
        # Apply momentum and update weights
        current_weights = self.model_data["model_weights"]
        momentum = self.model_data.get("weight_momentum", {})
        
        for weight_name in current_weights:
            # Calculate momentum
            momentum[weight_name] = (self.momentum * momentum.get(weight_name, 0) + 
                                   weight_adjustments[weight_name])
            
            # Update weight with momentum
            current_weights[weight_name] += momentum[weight_name]
            
            # Ensure weights stay positive and sum to 1
            current_weights[weight_name] = max(0.01, current_weights[weight_name])
        
        # Normalize weights to sum to 1
        total_weight = sum(current_weights.values())
        for weight_name in current_weights:
            current_weights[weight_name] /= total_weight
        
        self.model_data["weight_momentum"] = momentum
        
        logger.info(f"Updated model weights: {current_weights}")
        logger.info(f"Weight changes: {weight_adjustments}")
    
    def get_current_weights(self) -> Dict:
        """Get current model weights with Edge data defaults"""
        weights = self.model_data["model_weights"].copy()
        
        # Ensure Edge weights exist (for backward compatibility)
        if 'edge_speed_weight' not in weights:
            weights['edge_speed_weight'] = 0.05
        if 'edge_distance_weight' not in weights:
            weights['edge_distance_weight'] = 0.03
        if 'edge_burst_weight' not in weights:
            weights['edge_burst_weight'] = 0.02
        
        return weights
    
    def get_model_performance(self) -> Dict:
        """Get current model performance metrics"""
        return self.model_data.get("model_performance", {
            "total_games": 0,
            "correct_predictions": 0,
            "accuracy": 0.0,
            "recent_accuracy": 0.0
        })
    
    def run_daily_update(self):
        """Run daily model update with improvements"""
        self.update_model_weights()
        self.save_model_data()
        
        performance = self.get_model_performance()
        logger.info(f"Model performance: {performance['accuracy']:.3f} accuracy ({performance['correct_predictions']}/{performance['total_games']} games)")

if __name__ == "__main__":
    # Test the improved model
    model = ImprovedSelfLearningModel()
    
    print("🧪 Testing Improved Model")
    print("=" * 30)
    
    # Test prediction
    prediction = model.predict_game("TOR", "MTL")
    print(f"TOR @ MTL Prediction:")
    print(f"  Away (TOR): {prediction['away_prob']:.1f}%")
    print(f"  Home (MTL): {prediction['home_prob']:.1f}%")
    print(f"  Confidence: {max(prediction['away_prob'], prediction['home_prob']) - 50:.1f}%")
    
    # Show team performance data
    print(f"\nTeam Performance Data:")
    print(f"  TOR (Away): {prediction['away_perf']}")
    print(f"  MTL (Home): {prediction['home_perf']}")
