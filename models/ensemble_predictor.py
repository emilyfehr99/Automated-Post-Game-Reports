#!/usr/bin/env python3
"""
Ensemble Predictor
Combines specialized models based on game context for maximum accuracy
"""
from typing import Dict
try:
    from context_detector import ContextDetector
except Exception:
    from utils.context_detector import ContextDetector
try:
    from specialized_models import (
        HighScoringGameModel,
        DefensiveMatchupModel,
        PlayoffRaceModel,
        RivalryGameModel,
        PlayoffSeriesModel,
    )
except Exception:
    from models.specialized_models import (
        HighScoringGameModel,
        DefensiveMatchupModel,
        PlayoffRaceModel,
        RivalryGameModel,
        PlayoffSeriesModel,
    )
try:
    from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
except Exception:
    from models.improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

class EnsemblePredictor:
    def __init__(self, base_model=None):
        self.detector = ContextDetector(model=base_model)
        
        # Initialize specialized models lazily to avoid 6x redundant data/font/schedule loading
        self._model_classes = {
            'standard': ImprovedSelfLearningModelV2,
            'high_scoring': HighScoringGameModel,
            'defensive': DefensiveMatchupModel,
            'playoff_race': PlayoffRaceModel,
            'rivalry': RivalryGameModel,
            'playoff_series': PlayoffSeriesModel
        }
        self.models = {}
        if base_model is not None:
            self.models['standard'] = base_model

    def _get_model(self, context_type: str):
        if context_type not in self.models:
            cls = self._model_classes.get(context_type, self._model_classes['standard'])
            self.models[context_type] = cls()
        return self.models[context_type]
    
    def predict(self, away_team: str, home_team: str, game_id: str = None, game_date: str = None, is_playoff: bool = False, series_status: str = None) -> Dict:
        """Make ensemble prediction using specialized models
        
        Returns:
            Dict with prediction and component details
        """
        # Detect game contexts
        contexts = self.detector.detect_game_context(away_team, home_team, game_date, is_playoff=is_playoff)
        
        # Get predictions from each relevant model
        predictions = []
        weights = []
        
        for context_type, confidence in contexts:
            model = self._get_model(context_type)
            
            # Pass playoff flags if the model supports them
            try:
                pred = model.predict_game(away_team, home_team, game_id=game_id, game_date=game_date, is_playoff=is_playoff, series_status=series_status)
            except TypeError:
                pred = model.predict_game(away_team, home_team, game_id=game_id, game_date=game_date)
            
            predictions.append({
                'context': context_type,
                'confidence': confidence,
                'away_prob': pred['away_prob'],
                'home_prob': pred['home_prob']
            })
            weights.append(confidence)
        
        # Weighted ensemble
        total_weight = sum(weights)
        if total_weight == 0:
            # Fallback to standard model
            return self._get_model('standard').predict_game(away_team, home_team, game_id=game_id, game_date=game_date)
        
        ensemble_away = sum(p['away_prob'] * w for p, w in zip(predictions, weights)) / total_weight
        ensemble_home = sum(p['home_prob'] * w for p, w in zip(predictions, weights)) / total_weight
        
        # Normalize
        total = ensemble_away + ensemble_home
        if total > 0:
            ensemble_away = (ensemble_away / total) * 100
            ensemble_home = (ensemble_home / total) * 100
        
        return {
            'away_team': away_team,
            'home_team': home_team,
            'away_prob': ensemble_away,
            'home_prob': ensemble_home,
            'predicted_winner': away_team if ensemble_away > ensemble_home else home_team,
            'prediction_confidence': max(ensemble_away, ensemble_home) / 100,
            'contexts_used': contexts,
            'component_predictions': predictions,
            'ensemble_method': 'specialized_models'
        }

if __name__ == "__main__":
    ensemble = EnsemblePredictor()
    
    print("🎯 Ensemble Predictor Test")
    print("=" * 60)
    
    # Test various game types
    test_games = [
        ('COL', 'DAL', 'High-scoring matchup'),
        ('BOS', 'MTL', 'Original Six rivalry'),
        ('NJD', 'NYI', 'Standard game'),
    ]
    
    for away, home, description in test_games:
        print(f"\n{away} @ {home} ({description}):")
        
        pred = ensemble.predict(away, home)
        
        print(f"  Prediction: {pred['predicted_winner']} wins")
        print(f"  Probabilities: {away} {pred['away_prob']:.1f}% / {home} {pred['home_prob']:.1f}%")
        print(f"  Confidence: {pred['prediction_confidence']:.1%}")
        print(f"  Contexts used:")
        for context, confidence in pred['contexts_used']:
            print(f"    - {context}: {confidence:.0%}")
        print(f"  Component predictions:")
        for comp in pred['component_predictions']:
            print(f"    - {comp['context']}: {comp['away_prob']:.1f}% / {comp['home_prob']:.1f}% (weight: {comp['confidence']:.0%})")
