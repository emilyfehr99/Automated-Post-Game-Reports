"""
Enhanced version of the current advanced model with better features
Focuses on improving the existing 100 games rather than historical data
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging
from improved_advanced_model import ImprovedAdvancedModel

logger = logging.getLogger(__name__)

class EnhancedCurrentModel(ImprovedAdvancedModel):
    """Enhanced version of the current model with better features and confidence thresholds"""
    
    def __init__(self, predictions_file: str = "enhanced_current_predictions.json"):
        super().__init__(predictions_file)
        
        # Enhanced metric weights based on analysis
        self.metric_weights = {
            "pressure_score": 0.30,      # Most predictive - increased weight
            "possession_score": 0.25,    # Second most predictive
            "momentum_score": 0.20,      # Important for recent form
            "territorial_score": 0.15,   # Zone control matters
            "xg_avg": 0.10              # Expected goals - reduced weight
        }
        
        # Enhanced confidence thresholds
        self.confidence_thresholds = {
            "high": 0.70,    # Only predict when >70% confident
            "medium": 0.60,  # Medium confidence
            "low": 0.50      # Low confidence
        }
        
        # Home ice advantage factors by team (estimated)
        self.home_ice_advantages = {
            "BOS": 0.08, "TOR": 0.08, "MTL": 0.07, "OTT": 0.06,
            "NYR": 0.08, "NYI": 0.07, "NJD": 0.06, "PHI": 0.07,
            "PIT": 0.07, "WSH": 0.08, "CAR": 0.07, "CBJ": 0.06,
            "TBL": 0.08, "FLA": 0.07, "DET": 0.07, "BUF": 0.06,
            "CHI": 0.07, "STL": 0.07, "NSH": 0.07, "MIN": 0.07,
            "WPG": 0.08, "COL": 0.08, "DAL": 0.07, "ARI": 0.06,
            "VGK": 0.08, "LAK": 0.07, "SJS": 0.06, "ANA": 0.06,
            "EDM": 0.08, "CGY": 0.07, "VAN": 0.07, "SEA": 0.07,
            "UTA": 0.07  # Utah Hockey Club
        }
        
        # Default home ice advantage
        self.default_home_advantage = 0.06
    
    def _get_home_ice_advantage(self, team_abbrev: str, venue: str) -> float:
        """Get enhanced home ice advantage for a team"""
        if venue != "home":
            return 0.0
        
        team_key = team_abbrev.upper()
        return self.home_ice_advantages.get(team_key, self.default_home_advantage)
    
    def _calculate_enhanced_confidence(self, away_perf: Dict, home_perf: Dict, 
                                     away_score: float, home_score: float) -> float:
        """Calculate enhanced confidence based on multiple factors"""
        
        # Base confidence from data quality
        avg_data_confidence = (away_perf['confidence'] + home_perf['confidence']) / 2.0
        
        # Score separation factor
        total_score = away_score + home_score
        if total_score > 0:
            score_separation = abs(away_score - home_score) / total_score
        else:
            score_separation = 0.0
        
        # Games played factor (more games = higher confidence)
        avg_games_played = (away_perf['games_played'] + home_perf['games_played']) / 2.0
        games_confidence = min(1.0, avg_games_played / 10.0)  # Max confidence at 10+ games
        
        # Metric consistency factor (how consistent are the metrics)
        away_consistency = self._calculate_metric_consistency(away_perf)
        home_consistency = self._calculate_metric_consistency(home_perf)
        avg_consistency = (away_consistency + home_consistency) / 2.0
        
        # Combine all factors
        enhanced_confidence = (
            avg_data_confidence * 0.3 +
            score_separation * 0.3 +
            games_confidence * 0.2 +
            avg_consistency * 0.2
        )
        
        return min(1.0, enhanced_confidence)
    
    def _calculate_metric_consistency(self, team_perf: Dict) -> float:
        """Calculate how consistent a team's metrics are"""
        # This is a simplified version - in practice, you'd look at variance
        # For now, we'll use games played as a proxy for consistency
        games_played = team_perf.get('games_played', 0)
        return min(1.0, games_played / 8.0)  # Max consistency at 8+ games
    
    def predict_game(self, away_team_abbrev: str, home_team_abbrev: str, game_date: str = None) -> Dict:
        """Make an enhanced prediction with better features"""
        
        # Get team performances
        away_perf = self.get_team_advanced_performance(away_team_abbrev, "away")
        home_perf = self.get_team_advanced_performance(home_team_abbrev, "home")
        
        # Calculate base scores using enhanced weights
        away_score = 0.0
        home_score = 0.0
        
        for metric, weight in self.metric_weights.items():
            away_score += away_perf[metric] * weight
            home_score += home_perf[metric] * weight
        
        # Apply enhanced home ice advantage
        home_ice_boost = self._get_home_ice_advantage(home_team_abbrev, "home")
        home_score += home_ice_boost * 100  # Convert to score units
        
        # Apply head-to-head advantage if available
        h2h_advantage = self._get_head_to_head_advantage(away_team_abbrev, home_team_abbrev)
        away_score += h2h_advantage * 30  # Reduced impact
        home_score -= h2h_advantage * 30
        
        # Calculate probabilities
        total_score = away_score + home_score
        
        if total_score > 0:
            away_prob = (away_score / total_score) * 100
            home_prob = (home_score / total_score) * 100
        else:
            away_prob = 50.0
            home_prob = 50.0
        
        # Calculate enhanced confidence
        prediction_confidence = self._calculate_enhanced_confidence(
            away_perf, home_perf, away_score, home_score
        )
        
        # Determine prediction quality
        if prediction_confidence >= self.confidence_thresholds["high"]:
            quality = "high"
        elif prediction_confidence >= self.confidence_thresholds["medium"]:
            quality = "medium"
        else:
            quality = "low"
        
        predicted_winner = away_team_abbrev if away_prob > home_prob else home_team_abbrev
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'predicted_winner': predicted_winner,
            'confidence': prediction_confidence * 100,
            'quality': quality,
            'away_composite_score': away_score,
            'home_composite_score': home_score,
            'away_performance': away_perf,
            'home_performance': home_perf,
            'home_ice_advantage': home_ice_boost,
            'head_to_head_advantage': h2h_advantage,
            'should_predict': prediction_confidence >= self.confidence_thresholds["medium"]
        }
    
    def get_high_confidence_predictions(self, predictions: List[Dict]) -> List[Dict]:
        """Filter predictions to only include high confidence ones"""
        high_conf_predictions = []
        
        for pred in predictions:
            confidence = pred.get('confidence', 0)
            if confidence >= self.confidence_thresholds["high"] * 100:
                high_conf_predictions.append(pred)
        
        return high_conf_predictions
    
    def analyze_prediction_quality(self, predictions: List[Dict]) -> Dict:
        """Analyze the quality of predictions by confidence level"""
        analysis = {
            "total_predictions": len(predictions),
            "high_confidence": {"count": 0, "correct": 0, "accuracy": 0.0},
            "medium_confidence": {"count": 0, "correct": 0, "accuracy": 0.0},
            "low_confidence": {"count": 0, "correct": 0, "accuracy": 0.0}
        }
        
        for pred in predictions:
            confidence = pred.get('confidence', 0)
            is_correct = pred.get('is_correct', False)
            
            if confidence >= self.confidence_thresholds["high"] * 100:
                analysis["high_confidence"]["count"] += 1
                if is_correct:
                    analysis["high_confidence"]["correct"] += 1
            elif confidence >= self.confidence_thresholds["medium"] * 100:
                analysis["medium_confidence"]["count"] += 1
                if is_correct:
                    analysis["medium_confidence"]["correct"] += 1
            else:
                analysis["low_confidence"]["count"] += 1
                if is_correct:
                    analysis["low_confidence"]["correct"] += 1
        
        # Calculate accuracies
        for level in ["high_confidence", "medium_confidence", "low_confidence"]:
            count = analysis[level]["count"]
            correct = analysis[level]["correct"]
            if count > 0:
                analysis[level]["accuracy"] = (correct / count) * 100
        
        return analysis

def main():
    """Test the enhanced model"""
    print("🚀 TESTING ENHANCED CURRENT MODEL")
    print("=" * 60)
    
    # Load existing predictions
    with open('advanced_predictions.json', 'r') as f:
        existing_data = json.load(f)
    
    existing_predictions = existing_data.get('predictions', [])
    
    print(f"📊 Loaded {len(existing_predictions)} existing predictions")
    
    # Create enhanced model
    enhanced_model = EnhancedCurrentModel()
    
    # Re-predict all games with enhanced model
    enhanced_predictions = []
    
    for i, pred in enumerate(existing_predictions):
        away_team = pred.get('away_team', 'Unknown')
        home_team = pred.get('home_team', 'Unknown')
        date = pred.get('date', '1900-01-01')
        actual_winner = pred.get('actual_winner', 'Unknown')
        
        # Make enhanced prediction
        enhanced_pred = enhanced_model.predict_game(away_team, home_team, date)
        
        # Add actual results
        enhanced_pred['actual_winner'] = actual_winner
        enhanced_pred['is_correct'] = enhanced_pred['predicted_winner'] == actual_winner
        
        enhanced_predictions.append(enhanced_pred)
        
        if i < 5:  # Show first 5 examples
            print(f"\\n{i+1}. {away_team} @ {home_team}")
            print(f"   Enhanced: {enhanced_pred['predicted_winner']} ({enhanced_pred['away_prob']:.1f}% vs {enhanced_pred['home_prob']:.1f}%)")
            print(f"   Confidence: {enhanced_pred['confidence']:.1f}% ({enhanced_pred['quality']})")
            print(f"   Actual: {actual_winner} - {'✅' if enhanced_pred['is_correct'] else '❌'}")
    
    # Analyze prediction quality
    analysis = enhanced_model.analyze_prediction_quality(enhanced_predictions)
    
    print(f"\\n📊 ENHANCED MODEL ANALYSIS:")
    print(f"   Total predictions: {analysis['total_predictions']}")
    print(f"   High confidence: {analysis['high_confidence']['count']} games, {analysis['high_confidence']['accuracy']:.1f}% accuracy")
    print(f"   Medium confidence: {analysis['medium_confidence']['count']} games, {analysis['medium_confidence']['accuracy']:.1f}% accuracy")
    print(f"   Low confidence: {analysis['low_confidence']['count']} games, {analysis['low_confidence']['accuracy']:.1f}% accuracy")
    
    # Get high confidence predictions only
    high_conf_predictions = enhanced_model.get_high_confidence_predictions(enhanced_predictions)
    
    if high_conf_predictions:
        high_conf_correct = sum(1 for p in high_conf_predictions if p.get('is_correct', False))
        high_conf_accuracy = (high_conf_correct / len(high_conf_predictions)) * 100
        
        print(f"\\n🎯 HIGH CONFIDENCE PREDICTIONS ONLY:")
        print(f"   Count: {len(high_conf_predictions)} games")
        print(f"   Accuracy: {high_conf_accuracy:.1f}%")
        print(f"   This is the model's 'best bets' - only predict when very confident")
    
    # Save enhanced predictions
    enhanced_data = {
        "predictions": enhanced_predictions,
        "model_performance": analysis,
        "last_updated": datetime.now().isoformat()
    }
    
    with open('enhanced_current_predictions.json', 'w') as f:
        json.dump(enhanced_data, f, indent=2)
    
    print(f"\\n💾 Enhanced predictions saved to enhanced_current_predictions.json")
    print(f"\\n🎉 ENHANCED MODEL COMPLETE!")
    print(f"   Focus on high-confidence predictions for best accuracy")

if __name__ == "__main__":
    main()
