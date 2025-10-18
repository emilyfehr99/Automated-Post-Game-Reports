"""
Self-Learning Win Probability Model
Continuously learns and updates model weights based on actual game outcomes
"""

import json
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SelfLearningModel:
    def __init__(self, predictions_file: str = "win_probability_predictions.json"):
        """Initialize the self-learning model"""
        self.predictions_file = Path(predictions_file)
        self.model_data = self.load_model_data()
        self.learning_rate = 0.01  # How much to adjust weights based on errors
        self.min_games_for_update = 5  # Minimum games needed before updating weights
        
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
                "xg_weight": 0.4,
                "hdc_weight": 0.3,
                "shot_attempts_weight": 0.2,
                "game_score_weight": 0.1,
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
    
    def save_model_data(self):
        """Save updated model data"""
        try:
            self.model_data["last_updated"] = datetime.now().isoformat()
            with open(self.predictions_file, 'w') as f:
                json.dump(self.model_data, f, indent=2)
            logger.info("Model data saved successfully")
        except Exception as e:
            logger.error(f"Error saving model data: {e}")
    
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
        
        self.model_data["predictions"].append(prediction)
        logger.info(f"Added prediction for {away_team} @ {home_team}: {predicted_away_prob:.1f}% vs {predicted_home_prob:.1f}%")
    
    def update_model_performance(self, prediction: Dict):
        """Update model performance metrics"""
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
        """Update model weights based on prediction accuracy"""
        if len(self.model_data["predictions"]) < self.min_games_for_update:
            logger.info(f"Not enough games ({len(self.model_data['predictions'])}) to update weights. Need {self.min_games_for_update}")
            return
        
        # Get recent predictions with actual outcomes
        recent_predictions = [p for p in self.model_data["predictions"][-50:] 
                            if p.get("actual_winner") and p.get("prediction_accuracy") is not None]
        
        if len(recent_predictions) < 10:
            logger.info(f"Not enough recent predictions with outcomes ({len(recent_predictions)}) to update weights")
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
            metrics = prediction["metrics_used"]
            accuracy = prediction["prediction_accuracy"]
            
            # Calculate error (how far off we were from perfect prediction)
            error = abs(accuracy - 0.5)  # 0.5 means we were completely wrong
            
            # Adjust weights based on which metrics were most predictive
            for metric in weight_adjustments:
                if metric in metrics:
                    # If this metric was high and we were right, increase its weight
                    # If this metric was high and we were wrong, decrease its weight
                    metric_value = metrics.get(metric.replace("_weight", ""), 0)
                    if metric_value > 0:
                        if accuracy > 0.5:  # We were right
                            weight_adjustments[metric] += error * self.learning_rate * metric_value
                        else:  # We were wrong
                            weight_adjustments[metric] -= error * self.learning_rate * metric_value
        
        # Apply weight adjustments
        old_weights = self.model_data["model_weights"].copy()
        for metric, adjustment in weight_adjustments.items():
            new_weight = old_weights[metric] + adjustment
            # Keep weights between 0 and 1
            new_weight = max(0.0, min(1.0, new_weight))
            self.model_data["model_weights"][metric] = new_weight
        
        # Normalize weights to sum to 1.0
        total_weight = sum(self.model_data["model_weights"].values())
        if total_weight > 0:
            for metric in self.model_data["model_weights"]:
                self.model_data["model_weights"][metric] /= total_weight
        
        logger.info(f"Updated model weights: {self.model_data['model_weights']}")
        logger.info(f"Weight changes: {weight_adjustments}")
    
    def get_current_weights(self) -> Dict[str, float]:
        """Get current model weights"""
        return self.model_data["model_weights"].copy()
    
    def get_model_performance(self) -> Dict:
        """Get current model performance metrics"""
        if "model_performance" not in self.model_data:
            self.model_data["model_performance"] = {
                "total_games": 0,
                "correct_predictions": 0,
                "accuracy": 0.0,
                "recent_accuracy": 0.0
            }
        return self.model_data["model_performance"].copy()
    
    def get_recent_predictions(self, days: int = 7) -> List[Dict]:
        """Get recent predictions from the last N days"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        recent = []
        
        for prediction in self.model_data["predictions"]:
            try:
                pred_time = datetime.fromisoformat(prediction["timestamp"]).timestamp()
                if pred_time > cutoff_date:
                    recent.append(prediction)
            except:
                continue
        
        return recent
    
    def analyze_model_performance(self) -> Dict:
        """Analyze model performance and provide insights"""
        predictions = self.model_data["predictions"]
        if not predictions:
            return {"error": "No predictions available"}
        
        # Calculate accuracy by team
        team_accuracy = {}
        for prediction in predictions:
            if prediction.get("actual_winner") and prediction.get("prediction_accuracy"):
                for team in [prediction["away_team"], prediction["home_team"]]:
                    if team not in team_accuracy:
                        team_accuracy[team] = {"correct": 0, "total": 0}
                    team_accuracy[team]["total"] += 1
                    if prediction["prediction_accuracy"] > 0.5:
                        team_accuracy[team]["correct"] += 1
        
        # Calculate accuracy by prediction confidence
        confidence_accuracy = {}
        for prediction in predictions:
            if prediction.get("actual_winner") and prediction.get("prediction_accuracy"):
                confidence = max(prediction["predicted_away_win_prob"], 
                               prediction["predicted_home_win_prob"]) / 100.0
                conf_bucket = f"{int(confidence * 10) * 10}-{int(confidence * 10) * 10 + 10}%"
                
                if conf_bucket not in confidence_accuracy:
                    confidence_accuracy[conf_bucket] = {"correct": 0, "total": 0}
                
                confidence_accuracy[conf_bucket]["total"] += 1
                if prediction["prediction_accuracy"] > 0.5:
                    confidence_accuracy[conf_bucket]["correct"] += 1
        
        return {
            "total_predictions": len(predictions),
            "overall_accuracy": self.model_data["model_performance"]["accuracy"],
            "recent_accuracy": self.model_data["model_performance"]["recent_accuracy"],
            "team_accuracy": {team: data["correct"] / data["total"] if data["total"] > 0 else 0 
                            for team, data in team_accuracy.items()},
            "confidence_accuracy": {bucket: data["correct"] / data["total"] if data["total"] > 0 else 0 
                                  for bucket, data in confidence_accuracy.items()}
        }
    
    def run_daily_update(self):
        """Run daily model update - should be called by GitHub Actions"""
        logger.info("Running daily model update...")
        
        # Update model weights based on recent performance
        self.update_model_weights()
        
        # Save updated model
        self.save_model_data()
        
        # Log performance
        perf = self.get_model_performance()
        logger.info(f"Model performance: {perf['accuracy']:.3f} accuracy ({perf['correct_predictions']}/{perf['total_games']} games)")
        
        return perf


def main():
    """Test the self-learning model"""
    model = SelfLearningModel()
    
    # Test adding a prediction
    model.add_prediction(
        game_id="2025020079",
        date="2025-10-18",
        away_team="SEA",
        home_team="TOR",
        predicted_away_prob=46.4,
        predicted_home_prob=53.6,
        metrics_used={
            "away_xg": 2.8,
            "home_xg": 3.2,
            "away_hdc": 1.5,
            "home_hdc": 2.0,
            "away_shots": 28,
            "home_shots": 32,
            "away_gs": 12.8,
            "home_gs": 15.2
        }
    )
    
    # Get current performance
    perf = model.get_model_performance()
    print(f"Model Performance: {perf}")
    
    # Analyze performance
    analysis = model.analyze_model_performance()
    print(f"Model Analysis: {analysis}")


if __name__ == "__main__":
    main()
