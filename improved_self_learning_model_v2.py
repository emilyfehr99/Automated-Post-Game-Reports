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
        # Load team stats from main file first, then fallback to separate file
        if "team_stats" in self.model_data:
            self.team_stats = self.model_data["team_stats"]
        else:
            self.team_stats = self.load_team_stats()
        
    def load_model_data(self) -> Dict:
        """Load existing model data and predictions"""
        if self.predictions_file.exists():
            try:
                with open(self.predictions_file, 'r') as f:
                    data = json.load(f)
                    # Load team stats from main file if available
                    if "team_stats" in data:
                        self.team_stats = data["team_stats"]
                    return data
            except Exception as e:
                logger.error(f"Error loading model data: {e}")
        
        # Initialize with improved balanced model
        return {
            "predictions": [],
            "model_weights": {
                "xg_weight": 0.40,           # Expected goals - STRONGEST predictor
                "hdc_weight": 0.20,          # High danger chances - good predictor
                "corsi_weight": 0.10,        # Corsi % - possession metric
                "power_play_weight": 0.08,   # Power play performance
                "faceoff_weight": 0.06,      # Faceoff percentage
                "shots_weight": 0.05,        # Shots on goal
                "hits_weight": 0.03,         # Physical play
                "blocked_shots_weight": 0.03, # Defensive play
                "takeaways_weight": 0.02,    # Defensive plays (positive)
                "penalty_minutes_weight": 0.01, # Discipline
                "recent_form_weight": 0.02,  # Recent form (reduced - limited data)
                "head_to_head_weight": 0.00, # Head-to-head record (disabled - no real data)
                "rest_days_weight": 0.00,    # Rest days advantage (disabled - no real data)
                "goalie_performance_weight": 0.00,  # Goalie performance (disabled - no real data)
                "game_score_weight": 0.15    # Game score (composite metric)
            },
            "weight_momentum": {
                "xg_weight": 0.0,
                "hdc_weight": 0.0,
                "corsi_weight": 0.0,
                "power_play_weight": 0.0,
                "faceoff_weight": 0.0,
                "shots_weight": 0.0,
                "hits_weight": 0.0,
                "blocked_shots_weight": 0.0,
                "takeaways_weight": 0.0,
                "penalty_minutes_weight": 0.0,
                "recent_form_weight": 0.0,
                "head_to_head_weight": 0.0,
                "rest_days_weight": 0.0,
                "goalie_performance_weight": 0.0,
                "game_score_weight": 0.0
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
            # Include team stats in the main model data
            self.model_data["team_stats"] = self.team_stats
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
        gs_data = venue_data.get('gs', [])
        
        # Filter out zeros and calculate proper averages
        valid_goals = [g for g in goals if g > 0] if goals else [0]
        valid_xg = [x for x in xg_data if x > 0] if xg_data else [0]
        valid_hdc = [h for h in hdc_data if h > 0] if hdc_data else [0]
        valid_shots = [s for s in shots_data if s > 0] if shots_data else [0]
        valid_gs = [g for g in gs_data if g > 0] if gs_data else [0]
        
        # Get additional metrics from venue data
        corsi_data = venue_data.get('corsi_pct', [])
        power_play_data = venue_data.get('power_play_pct', [])
        faceoff_data = venue_data.get('faceoff_pct', [])
        hits_data = venue_data.get('hits', [])
        blocked_shots_data = venue_data.get('blocked_shots', [])
        giveaways_data = venue_data.get('giveaways', [])
        takeaways_data = venue_data.get('takeaways', [])
        penalty_minutes_data = venue_data.get('penalty_minutes', [])
        
        # Calculate averages for all metrics
        valid_corsi = [c for c in corsi_data if c > 0] if corsi_data else [50.0]
        valid_power_play = [p for p in power_play_data if p > 0] if power_play_data else [0.0]
        valid_faceoff = [f for f in faceoff_data if f > 0] if faceoff_data else [50.0]
        valid_hits = [h for h in hits_data if h > 0] if hits_data else [0]
        valid_blocked_shots = [b for b in blocked_shots_data if b > 0] if blocked_shots_data else [0]
        valid_giveaways = [g for g in giveaways_data if g > 0] if giveaways_data else [0]
        valid_takeaways = [t for t in takeaways_data if t > 0] if takeaways_data else [0]
        valid_penalty_minutes = [p for p in penalty_minutes_data if p > 0] if penalty_minutes_data else [0]
        
        return {
            'xg': np.mean(valid_xg) if valid_xg else 0.0,
            'hdc': np.mean(valid_hdc) if valid_hdc else 0.0,
            'shots': np.mean(valid_shots) if valid_shots else 0.0,
            'goals': np.mean(valid_goals) if valid_goals else 0.0,
            'gs': np.mean(valid_gs) if valid_gs else 0.0,
            'xg_avg': np.mean(valid_xg) if valid_xg else 0.0,
            'hdc_avg': np.mean(valid_hdc) if valid_hdc else 0.0,
            'shots_avg': np.mean(valid_shots) if valid_shots else 0.0,
            'goals_avg': np.mean(valid_goals) if valid_goals else 0.0,
            'gs_avg': np.mean(valid_gs) if valid_gs else 0.0,
            'corsi_avg': np.mean(valid_corsi) if valid_corsi else 50.0,
            'power_play_avg': np.mean(valid_power_play) if valid_power_play else 0.0,
            'faceoff_avg': np.mean(valid_faceoff) if valid_faceoff else 50.0,
            'hits_avg': np.mean(valid_hits) if valid_hits else 0.0,
            'blocked_shots_avg': np.mean(valid_blocked_shots) if valid_blocked_shots else 0.0,
            'giveaways_avg': np.mean(valid_giveaways) if valid_giveaways else 0.0,
            'takeaways_avg': np.mean(valid_takeaways) if valid_takeaways else 0.0,
            'penalty_minutes_avg': np.mean(valid_penalty_minutes) if valid_penalty_minutes else 0.0,
            'games_played': len(games),
            'recent_form': self._calculate_recent_form(team_key, venue),
            'head_to_head': self._calculate_head_to_head(team_key, venue),
            'rest_days_advantage': self._calculate_rest_days_advantage(team_key, venue),
            'goalie_performance': self._calculate_goalie_performance(team_key, venue),
            'confidence': self._calculate_confidence(len(games))
        }
    
    def _get_default_performance(self) -> Dict:
        """Get default performance for teams with no data"""
        return {
            'xg': 2.0, 'hdc': 2.0, 'shots': 30.0, 'goals': 2.0, 'gs': 3.0,
            'xg_avg': 2.0, 'hdc_avg': 2.0, 'shots_avg': 30.0, 'goals_avg': 2.0, 'gs_avg': 3.0,
            'corsi_avg': 50.0, 'power_play_avg': 0.0, 'faceoff_avg': 50.0,
            'hits_avg': 0.0, 'blocked_shots_avg': 0.0, 'giveaways_avg': 0.0,
            'takeaways_avg': 0.0, 'penalty_minutes_avg': 0.0,
            'games_played': 0, 'recent_form': 0.5, 'head_to_head': 0.5,
            'rest_days_advantage': 0.0, 'goalie_performance': 0.5, 'confidence': 0.1
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
    
    def _calculate_head_to_head(self, team: str, venue: str) -> float:
        """Calculate head-to-head performance against common opponents"""
        # For now, return neutral value - would need opponent-specific data
        # This could be enhanced with actual head-to-head records
        return 0.5
    
    def _calculate_rest_days_advantage(self, team: str, venue: str) -> float:
        """Calculate rest days advantage (back-to-back games)"""
        # For now, return neutral value - would need schedule data
        # This could be enhanced with actual rest day calculations
        return 0.0
    
    def _calculate_goalie_performance(self, team: str, venue: str) -> float:
        """Calculate goalie performance metrics"""
        # For now, return neutral value - would need goalie-specific data
        # This could be enhanced with actual goalie save percentages, GAA, etc.
        return 0.5
    
    def _simple_prediction(self, away_team: str, home_team: str, away_perf: Dict, home_perf: Dict) -> Dict:
        """Simple prediction when we don't have enough data"""
        # Use basic win/loss records if available, otherwise neutral prediction
        away_wins = away_perf.get('games_played', 0)
        home_wins = home_perf.get('games_played', 0)
        
        if away_wins == 0 and home_wins == 0:
            # No data for either team - neutral prediction with home advantage
            away_prob = 47.5
            home_prob = 52.5
            confidence = 10.0
        else:
            # Use simple win rate if available
            total_games = away_wins + home_wins
            if total_games > 0:
                away_prob = (away_wins / total_games) * 100
                home_prob = (home_wins / total_games) * 100
                # Add home advantage
                home_prob += 5.0
                away_prob -= 5.0
                confidence = min(30.0, total_games * 10.0)
            else:
                away_prob = 47.5
                home_prob = 52.5
                confidence = 10.0
        
        # Normalize to 100%
        total = away_prob + home_prob
        away_prob = (away_prob / total) * 100
        home_prob = (home_prob / total) * 100
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'away_score': away_prob,
            'home_score': home_prob,
            'away_perf': away_perf,
            'home_perf': home_perf,
            'prediction_confidence': confidence,
            'uncertainty': 0.0
        }
    
    def predict_game(self, away_team: str, home_team: str, current_away_score: int = None, 
                    current_home_score: int = None, period: int = 1, game_id: str = None) -> Dict:
        """Predict a game with improved features and confidence"""
        
        # Get team performance data
        away_perf = self.get_team_performance(away_team, is_home=False)
        home_perf = self.get_team_performance(home_team, is_home=True)
        
        # If we don't have enough data for either team, use simple prediction
        if away_perf['games_played'] < 2 or home_perf['games_played'] < 2:
            return self._simple_prediction(away_team, home_team, away_perf, home_perf)
        
        # Get current model weights
        weights = self.get_current_weights()
        
        # Calculate weighted scores with comprehensive metrics and advanced features
        away_score = (
            away_perf['xg_avg'] * weights['xg_weight'] +
            away_perf['hdc_avg'] * weights['hdc_weight'] +
            away_perf['corsi_avg'] * weights['corsi_weight'] +
            away_perf['power_play_avg'] * weights['power_play_weight'] +
            away_perf['faceoff_avg'] * weights['faceoff_weight'] +
            away_perf['shots_avg'] * weights['shots_weight'] +
            away_perf['hits_avg'] * weights['hits_weight'] +
            away_perf['blocked_shots_avg'] * weights['blocked_shots_weight'] +
            (away_perf['takeaways_avg'] - away_perf['giveaways_avg']) * weights['takeaways_weight'] +
            away_perf['penalty_minutes_avg'] * weights['penalty_minutes_weight'] +
            away_perf['recent_form'] * weights['recent_form_weight'] +
            away_perf['head_to_head'] * weights['head_to_head_weight'] +
            away_perf['rest_days_advantage'] * weights['rest_days_weight'] +
            away_perf['goalie_performance'] * weights['goalie_performance_weight']
        )
        
        home_score = (
            home_perf['xg_avg'] * weights['xg_weight'] +
            home_perf['hdc_avg'] * weights['hdc_weight'] +
            home_perf['corsi_avg'] * weights['corsi_weight'] +
            home_perf['power_play_avg'] * weights['power_play_weight'] +
            home_perf['faceoff_avg'] * weights['faceoff_weight'] +
            home_perf['shots_avg'] * weights['shots_weight'] +
            home_perf['hits_avg'] * weights['hits_weight'] +
            home_perf['blocked_shots_avg'] * weights['blocked_shots_weight'] +
            (home_perf['takeaways_avg'] - home_perf['giveaways_avg']) * weights['takeaways_weight'] +
            home_perf['penalty_minutes_avg'] * weights['penalty_minutes_weight'] +
            home_perf['recent_form'] * weights['recent_form_weight'] +
            home_perf['head_to_head'] * weights['head_to_head_weight'] +
            home_perf['rest_days_advantage'] * weights['rest_days_weight'] +
            home_perf['goalie_performance'] * weights['goalie_performance_weight']
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
    
    def ensemble_predict(self, away_team: str, home_team: str, current_away_score: int = None, 
                        current_home_score: int = None, period: int = 1, game_id: str = None) -> Dict:
        """Use ensemble of multiple prediction methods for improved accuracy"""
        
        # Method 1: Traditional metrics (our comprehensive model)
        traditional = self.predict_game(away_team, home_team, current_away_score, current_home_score, period, game_id)
        
        # Method 2: Recent form weighted prediction
        form_based = self._form_based_predict(away_team, home_team)
        
        # Method 3: Momentum/streak based prediction
        momentum_based = self._momentum_based_predict(away_team, home_team)
        
        # Combine methods with weights (favor proven traditional model)
        weights = [0.70, 0.20, 0.10]  # Traditional, form, momentum
        
        away_prob = (
            traditional['away_prob'] * weights[0] +
            form_based['away_prob'] * weights[1] +
            momentum_based['away_prob'] * weights[2]
        )
        
        home_prob = (
            traditional['home_prob'] * weights[0] +
            form_based['home_prob'] * weights[1] +
            momentum_based['home_prob'] * weights[2]
        )
        
        # Normalize to 100%
        total = away_prob + home_prob
        away_prob = (away_prob / total) * 100
        home_prob = (home_prob / total) * 100
        
        # Calculate ensemble confidence
        ensemble_confidence = (
            traditional['prediction_confidence'] * weights[0] +
            form_based['prediction_confidence'] * weights[1] +
            momentum_based['prediction_confidence'] * weights[2]
        )
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'prediction_confidence': ensemble_confidence,
            'ensemble_methods': {
                'traditional': traditional,
                'form_based': form_based,
                'momentum_based': momentum_based
            },
            'ensemble_weights': weights
        }
    
    def _form_based_predict(self, away_team: str, home_team: str) -> Dict:
        """Predict based primarily on recent form (last 5 games)"""
        away_perf = self.get_team_performance(away_team, is_home=False)
        home_perf = self.get_team_performance(home_team, is_home=True)
        
        # Use recent form but weight it by confidence and games played
        away_form_score = away_perf['recent_form'] * away_perf['confidence'] * 100
        home_form_score = home_perf['recent_form'] * home_perf['confidence'] * 100
        
        # Add home advantage
        home_form_score *= 1.05
        
        # If we don't have enough data, fall back to traditional metrics
        if away_perf['games_played'] < 3 or home_perf['games_played'] < 3:
            # Use traditional prediction as fallback
            traditional = self.predict_game(away_team, home_team)
            return {
                'away_prob': traditional['away_prob'],
                'home_prob': traditional['home_prob'],
                'prediction_confidence': traditional['prediction_confidence'] * 0.7  # Lower confidence for fallback
            }
        
        # Calculate probabilities
        total_score = away_form_score + home_form_score
        if total_score > 0:
            away_prob = (away_form_score / total_score) * 100
            home_prob = (home_form_score / total_score) * 100
        else:
            away_prob = 50.0
            home_prob = 50.0
        
        # Lower confidence for form-based predictions
        confidence = min(away_perf['confidence'], home_perf['confidence']) * 0.8 * 100
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'prediction_confidence': confidence
        }
    
    def _momentum_based_predict(self, away_team: str, home_team: str) -> Dict:
        """Predict based on momentum and streaks"""
        away_perf = self.get_team_performance(away_team, is_home=False)
        home_perf = self.get_team_performance(home_team, is_home=True)
        
        # If we don't have enough data, fall back to traditional metrics
        if away_perf['games_played'] < 3 or home_perf['games_played'] < 3:
            traditional = self.predict_game(away_team, home_team)
            return {
                'away_prob': traditional['away_prob'],
                'home_prob': traditional['home_prob'],
                'prediction_confidence': traditional['prediction_confidence'] * 0.6  # Lower confidence for fallback
            }
        
        # Calculate momentum from recent form and confidence
        away_momentum = away_perf['recent_form'] * away_perf['confidence'] * 100
        home_momentum = home_perf['recent_form'] * home_perf['confidence'] * 100
        
        # Add home advantage
        home_momentum *= 1.05
        
        # Calculate probabilities
        total_momentum = away_momentum + home_momentum
        if total_momentum > 0:
            away_prob = (away_momentum / total_momentum) * 100
            home_prob = (home_momentum / total_momentum) * 100
        else:
            away_prob = 50.0
            home_prob = 50.0
        
        # Lower confidence for momentum-based predictions
        confidence = min(away_perf['confidence'], home_perf['confidence']) * 0.6 * 100
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'prediction_confidence': confidence
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
            "predicted_away_win_prob": predicted_away_prob / 100.0,  # Convert percentage to decimal
            "predicted_home_win_prob": predicted_home_prob / 100.0,  # Convert percentage to decimal
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
        
        # Initialize team stats if needed with comprehensive metrics
        def create_venue_data():
            return {
                "games": [], "xg": [], "hdc": [], "shots": [], "goals": [], "gs": [],
                "corsi_pct": [], "power_play_pct": [], "faceoff_pct": [],
                "hits": [], "blocked_shots": [], "giveaways": [], "takeaways": [], "penalty_minutes": []
            }
        
        if away_team not in self.team_stats:
            self.team_stats[away_team] = {"home": create_venue_data(), "away": create_venue_data()}
        
        if home_team not in self.team_stats:
            self.team_stats[home_team] = {"home": create_venue_data(), "away": create_venue_data()}
        
        # Get metrics from the prediction
        metrics = prediction.get("metrics_used", {})
        
        # Update away team stats with comprehensive metrics
        away_data = self.team_stats[away_team]["away"]
        away_data["games"].append(date)
        away_data["goals"].append(away_score)
        away_data["xg"].append(metrics.get("away_xg", 0.0))
        away_data["hdc"].append(metrics.get("away_hdc", 0))
        away_data["shots"].append(metrics.get("away_shots", 0))
        away_data["gs"].append(metrics.get("away_gs", 0.0))
        away_data["corsi_pct"].append(metrics.get("away_corsi_pct", 50.0))
        away_data["power_play_pct"].append(metrics.get("away_power_play_pct", 0.0))
        away_data["faceoff_pct"].append(metrics.get("away_faceoff_pct", 50.0))
        away_data["hits"].append(metrics.get("away_hits", 0))
        away_data["blocked_shots"].append(metrics.get("away_blocked_shots", 0))
        away_data["giveaways"].append(metrics.get("away_giveaways", 0))
        away_data["takeaways"].append(metrics.get("away_takeaways", 0))
        away_data["penalty_minutes"].append(metrics.get("away_penalty_minutes", 0))
        
        # Update home team stats with comprehensive metrics
        home_data = self.team_stats[home_team]["home"]
        home_data["games"].append(date)
        home_data["goals"].append(home_score)
        home_data["xg"].append(metrics.get("home_xg", 0.0))
        home_data["hdc"].append(metrics.get("home_hdc", 0))
        home_data["shots"].append(metrics.get("home_shots", 0))
        home_data["gs"].append(metrics.get("home_gs", 0.0))
        home_data["corsi_pct"].append(metrics.get("home_corsi_pct", 50.0))
        home_data["power_play_pct"].append(metrics.get("home_power_play_pct", 0.0))
        home_data["faceoff_pct"].append(metrics.get("home_faceoff_pct", 50.0))
        home_data["hits"].append(metrics.get("home_hits", 0))
        home_data["blocked_shots"].append(metrics.get("home_blocked_shots", 0))
        home_data["giveaways"].append(metrics.get("home_giveaways", 0))
        home_data["takeaways"].append(metrics.get("home_takeaways", 0))
        home_data["penalty_minutes"].append(metrics.get("home_penalty_minutes", 0))
        
        # Keep only last 20 games to prevent memory bloat
        all_metric_keys = ["games", "xg", "hdc", "shots", "goals", "gs", "corsi_pct", "power_play_pct", 
                          "faceoff_pct", "hits", "blocked_shots", "giveaways", "takeaways", "penalty_minutes"]
        for team in [away_team, home_team]:
            for venue in ["home", "away"]:
                for key in all_metric_keys:
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
    
    def analyze_model_performance(self) -> Dict:
        """Analyze model performance by team and other metrics"""
        predictions = self.model_data.get("predictions", [])
        
        # Calculate team accuracy
        team_accuracy = {}
        team_games = {}
        
        for pred in predictions:
            if pred.get("actual_winner"):
                away_team = pred.get("away_team")
                home_team = pred.get("home_team")
                predicted_winner = pred.get("predicted_winner")
                actual_winner = pred.get("actual_winner")
                
                # Count games for each team
                if away_team:
                    team_games[away_team] = team_games.get(away_team, 0) + 1
                if home_team:
                    team_games[home_team] = team_games.get(home_team, 0) + 1
                
                # Count correct predictions for each team
                if predicted_winner == actual_winner:
                    if actual_winner == away_team and away_team:
                        team_accuracy[away_team] = team_accuracy.get(away_team, 0) + 1
                    elif actual_winner == home_team and home_team:
                        team_accuracy[home_team] = team_accuracy.get(home_team, 0) + 1
        
        # Convert to percentages
        for team in team_accuracy:
            if team_games.get(team, 0) > 0:
                team_accuracy[team] = team_accuracy[team] / team_games[team]
        
        return {
            "team_accuracy": team_accuracy,
            "team_games": team_games,
            "total_predictions": len(predictions)
        }
    
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
