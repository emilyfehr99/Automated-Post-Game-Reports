#!/usr/bin/env python3
"""
Advanced NHL Prediction Model
Implements multiple techniques to achieve 60%+ accuracy
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

class AdvancedPredictionModel:
    def __init__(self):
        """Initialize the advanced prediction model"""
        self.model_file = Path("improved_self_learning_model.json")
        self.model_data = self.load_model_data()
        
        # Advanced parameters
        self.confidence_threshold = 0.55  # Only predict when 55%+ confident
        self.recent_games_weight = 2.0    # Last 5 games weighted 2x
        self.ensemble_methods = 3         # Number of prediction methods
        
    def load_model_data(self) -> Dict:
        """Load existing model data"""
        if self.model_file.exists():
            with open(self.model_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_team_recent_form(self, team: str, is_home: bool = True) -> Dict:
        """Get team's recent form (last 5 games) with weighted importance"""
        predictions = self.model_data.get('predictions', [])
        team_games = []
        
        # Get recent games for this team
        for pred in predictions[-50:]:  # Check last 50 predictions
            if pred.get('actual_winner'):
                if (pred.get('away_team') == team and not is_home) or \
                   (pred.get('home_team') == team and is_home):
                    team_games.append(pred)
        
        if len(team_games) < 3:
            return {'form_score': 0.5, 'win_streak': 0, 'recent_wins': 0}
        
        # Calculate recent form (last 5 games, weighted)
        recent_games = team_games[-5:]
        wins = 0
        total_weight = 0
        
        for i, game in enumerate(recent_games):
            weight = self.recent_games_weight if i >= len(recent_games) - 2 else 1.0
            total_weight += weight
            
            if is_home:
                if game.get('actual_winner') == 'home':
                    wins += weight
            else:
                if game.get('actual_winner') == 'away':
                    wins += weight
        
        form_score = wins / total_weight if total_weight > 0 else 0.5
        recent_wins = sum(1 for g in recent_games[-3:] if 
                         (g.get('actual_winner') == 'home' and is_home) or
                         (g.get('actual_winner') == 'away' and not is_home))
        
        return {
            'form_score': form_score,
            'win_streak': recent_wins,
            'recent_wins': recent_wins,
            'games_analyzed': len(recent_games)
        }
    
    def get_goalie_advantage(self, away_team: str, home_team: str) -> Dict:
        """Estimate goalie advantage based on recent performance"""
        # This would integrate with goalie stats API in production
        # For now, use team performance as proxy
        away_form = self.get_team_recent_form(away_team, False)
        home_form = self.get_team_recent_form(home_team, True)
        
        # Estimate goalie performance from team form
        away_goalie = away_form['form_score'] * 0.8  # Goalies affect ~80% of team performance
        home_goalie = home_form['form_score'] * 0.8
        
        return {
            'away_goalie_advantage': away_goalie - 0.5,
            'home_goalie_advantage': home_goalie - 0.5,
            'goalie_differential': home_goalie - away_goalie
        }
    
    def get_special_teams_advantage(self, away_team: str, home_team: str) -> Dict:
        """Estimate special teams advantage"""
        # This would integrate with power play/penalty kill stats
        # For now, use recent form as proxy
        away_form = self.get_team_recent_form(away_team, False)
        home_form = self.get_team_recent_form(home_team, True)
        
        # Estimate special teams from recent performance
        away_special = away_form['form_score'] * 0.3  # Special teams ~30% impact
        home_special = home_form['form_score'] * 0.3
        
        return {
            'away_special_advantage': away_special - 0.5,
            'home_special_advantage': home_special - 0.5,
            'special_differential': home_special - away_special
        }
    
    def get_momentum_advantage(self, away_team: str, home_team: str) -> Dict:
        """Calculate momentum/streak advantage"""
        away_form = self.get_team_recent_form(away_team, False)
        home_form = self.get_team_recent_form(home_team, True)
        
        # Momentum based on recent wins
        away_momentum = min(away_form['win_streak'] * 0.1, 0.3)  # Max 30% boost
        home_momentum = min(home_form['win_streak'] * 0.1, 0.3)
        
        return {
            'away_momentum': away_momentum,
            'home_momentum': home_momentum,
            'momentum_differential': home_momentum - away_momentum
        }
    
    def ensemble_predict(self, away_team: str, home_team: str) -> Dict:
        """Use ensemble of multiple prediction methods"""
        # Method 1: Traditional metrics (existing model)
        traditional = self.traditional_predict(away_team, home_team)
        
        # Method 2: Recent form weighted
        form_based = self.form_based_predict(away_team, home_team)
        
        # Method 3: Momentum/streak based
        momentum_based = self.momentum_based_predict(away_team, home_team)
        
        # Combine methods with weights
        weights = [0.4, 0.35, 0.25]  # Traditional, form, momentum
        
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
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'confidence': max(away_prob, home_prob) / 100,
            'method': 'ensemble',
            'traditional': traditional,
            'form_based': form_based,
            'momentum_based': momentum_based
        }
    
    def traditional_predict(self, away_team: str, home_team: str) -> Dict:
        """Traditional prediction using existing model logic"""
        # Use existing model weights and logic
        weights = self.model_data.get('model_weights', {})
        
        # Simplified traditional prediction
        away_score = 0.5  # Base score
        home_score = 0.5
        
        # Apply home advantage
        home_advantage = weights.get('home_advantage_weight', 0.023)
        home_score *= (1.0 + home_advantage)
        
        # Calculate probabilities
        total = away_score + home_score
        away_prob = (away_score / total) * 100
        home_prob = (home_score / total) * 100
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'method': 'traditional'
        }
    
    def form_based_predict(self, away_team: str, home_team: str) -> Dict:
        """Prediction based on recent form"""
        away_form = self.get_team_recent_form(away_team, False)
        home_form = self.get_team_recent_form(home_team, True)
        
        # Use form scores directly
        away_score = away_form['form_score']
        home_score = home_form['form_score']
        
        # Apply home advantage
        home_advantage = 0.035  # 3.5%
        home_score *= (1.0 + home_advantage)
        
        # Calculate probabilities
        total = away_score + home_score
        away_prob = (away_score / total) * 100
        home_prob = (home_score / total) * 100
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'method': 'form_based',
            'away_form': away_form,
            'home_form': home_form
        }
    
    def momentum_based_predict(self, away_team: str, home_team: str) -> Dict:
        """Prediction based on momentum and streaks"""
        momentum = self.get_momentum_advantage(away_team, home_team)
        
        # Base scores with momentum
        away_score = 0.5 + momentum['away_momentum']
        home_score = 0.5 + momentum['home_momentum']
        
        # Apply home advantage
        home_advantage = 0.035
        home_score *= (1.0 + home_advantage)
        
        # Calculate probabilities
        total = away_score + home_score
        away_prob = (away_score / total) * 100
        home_prob = (home_score / total) * 100
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'method': 'momentum_based',
            'momentum': momentum
        }
    
    def predict_game(self, away_team: str, home_team: str) -> Dict:
        """Main prediction method with confidence threshold"""
        # Get ensemble prediction
        prediction = self.ensemble_predict(away_team, home_team)
        
        # Check confidence threshold
        confidence = prediction['confidence']
        
        if confidence < self.confidence_threshold:
            # Low confidence - return conservative prediction
            return {
                'away_prob': 50.0,
                'home_prob': 50.0,
                'confidence': 0.5,
                'method': 'conservative',
                'reason': f'Low confidence ({confidence:.1%} < {self.confidence_threshold:.1%})'
            }
        
        # High confidence prediction
        return {
            'away_prob': prediction['away_prob'],
            'home_prob': prediction['home_prob'],
            'confidence': confidence,
            'method': 'ensemble',
            'details': prediction
        }

def main():
    """Test the advanced prediction model"""
    model = AdvancedPredictionModel()
    
    # Test predictions
    test_games = [
        ('VAN', 'WSH'),
        ('EDM', 'DET'),
        ('ANA', 'CHI'),
        ('BOS', 'UTA')
    ]
    
    print("🏒 ADVANCED NHL PREDICTIONS 🏒")
    print("=" * 50)
    
    for away, home in test_games:
        prediction = model.predict_game(away, home)
        
        print(f"\n{away} @ {home}")
        print(f"  Away: {prediction['away_prob']:.1f}%")
        print(f"  Home: {prediction['home_prob']:.1f}%")
        print(f"  Confidence: {prediction['confidence']:.1%}")
        print(f"  Method: {prediction['method']}")
        
        if prediction['confidence'] >= 0.55:
            winner = away if prediction['away_prob'] > prediction['home_prob'] else home
            confidence_boost = max(prediction['away_prob'], prediction['home_prob']) - 50
            print(f"  🏆 Winner: {winner} (+{confidence_boost:.1f}%)")

if __name__ == "__main__":
    main()
