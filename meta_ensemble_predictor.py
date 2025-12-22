#!/usr/bin/env python3
"""
Meta Ensemble Predictor
Combines all prediction methods for maximum accuracy
"""
from typing import Dict, Optional
from ensemble_predictor import EnsemblePredictor
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

class MetaEnsemblePredictor:
    """Combines multiple ensemble strategies for maximum accuracy"""
    
    def __init__(self):
        self.specialized_ensemble = EnsemblePredictor()
        self.base_model = ImprovedSelfLearningModelV2()
    
    def predict(self, away_team: str, home_team: str, 
                game_id: str = None, game_date: str = None,
                away_lineup: Dict = None, home_lineup: Dict = None,
                away_goalie: str = None, home_goalie: str = None,
                away_injuries: list = None, home_injuries: list = None) -> Dict:
        """Meta-ensemble prediction combining all methods
        
        Args:
            away_team: Away team abbreviation
            home_team: Home team abbreviation
            game_id: NHL game ID
            game_date: Game date
            away_lineup: Away team lineup (if available)
            home_lineup: Home team lineup (if available)
            away_goalie: Confirmed away goalie
            home_goalie: Confirmed home goalie
            away_injuries: List of injured away players
            home_injuries: List of injured home players
        
        Returns:
            Meta-ensemble prediction with confidence score
        """
        predictions = []
        weights = []
        
        # 1. Specialized ensemble (40% weight)
        try:
            spec_pred = self.specialized_ensemble.predict(away_team, home_team, game_id, game_date)
            predictions.append(spec_pred)
            weights.append(0.40)
        except Exception as e:
            print(f"Specialized ensemble failed: {e}")
        
        # 2. Player-level model (20% weight) - if lineups available
        if away_lineup and home_lineup:
            try:
                player_pred = self.base_model.predict_game_with_lineup(
                    away_team, home_team, away_lineup, home_lineup, game_id, game_date
                )
                predictions.append(player_pred)
                weights.append(0.20)
            except Exception as e:
                print(f"Player-level model failed: {e}")
        
        # 3. Base model with all features (30% weight)
        try:
            base_pred = self.base_model.predict_game(away_team, home_team, game_id=game_id, game_date=game_date)
            predictions.append(base_pred)
            weights.append(0.30)
        except Exception as e:
            print(f"Base model failed: {e}")
        
        # 4. Historical H2H (10% weight)
        # Simplified - would need full implementation
        # predictions.append(h2h_pred)
        # weights.append(0.10)
        
        if not predictions:
            raise Exception("All prediction methods failed")
        
        # Weighted ensemble
        total_weight = sum(weights)
        ensemble_away = sum(p['away_prob'] * w for p, w in zip(predictions, weights)) / total_weight
        ensemble_home = sum(p['home_prob'] * w for p, w in zip(predictions, weights)) / total_weight
        
        # Apply injury adjustments
        injury_adjustment = self._calculate_injury_impact(away_injuries, home_injuries)
        ensemble_away += injury_adjustment
        ensemble_home -= injury_adjustment
        
        # Normalize
        total = ensemble_away + ensemble_home
        if total > 0:
            ensemble_away = (ensemble_away / total) * 100
            ensemble_home = (ensemble_home / total) * 100
        
        # Calculate confidence
        confidence = max(ensemble_away, ensemble_home) / 100
        
        # Boost confidence if multiple models agree
        agreement_score = self._calculate_agreement(predictions, away_team, home_team)
        if agreement_score > 0.8:
            confidence = min(1.0, confidence * 1.1)
        
        return {
            'away_team': away_team,
            'home_team': home_team,
            'away_prob': ensemble_away,
            'home_prob': ensemble_home,
            'predicted_winner': away_team if ensemble_away > ensemble_home else home_team,
            'prediction_confidence': confidence,
            'component_predictions': predictions,
            'weights_used': weights,
            'injury_adjustment': injury_adjustment,
            'agreement_score': agreement_score,
            'ensemble_method': 'meta_ensemble'
        }
    
    def _calculate_injury_impact(self, away_injuries: list, home_injuries: list) -> float:
        """Calculate net injury impact (positive favors away team)"""
        if not away_injuries and not home_injuries:
            return 0.0
        
        away_impact = self._team_injury_impact(away_injuries or [])
        home_impact = self._team_injury_impact(home_injuries or [])
        
        # Net impact (positive = away team advantage)
        return home_impact - away_impact
    
    def _team_injury_impact(self, injuries: list) -> float:
        """Calculate injury impact for one team"""
        impact = 0.0
        
        for injury in injuries:
            player_name = injury.get('name', '')
            position = injury.get('position', '')
            
            # Simplified - would need player stats lookup
            # For now, use position-based estimates
            if position == 'G':
                impact += 0.10  # Backup goalie major impact
            elif 'C' in position or 'W' in position:
                impact += 0.03  # Forward impact
            elif 'D' in position:
                impact += 0.02  # Defenseman impact
        
        return min(0.15, impact)  # Cap at 15% impact
    
    def _calculate_agreement(self, predictions: list, away_team: str = None, home_team: str = None) -> float:
        """Calculate how much models agree (0-1)"""
        if len(predictions) < 2:
            return 1.0
        
        # Check if all models predict same winner
        winners = []
        for p in predictions:
            if p['away_prob'] > p['home_prob']:
                winners.append(away_team or p.get('away_team', 'away'))
            else:
                winners.append(home_team or p.get('home_team', 'home'))
        
        most_common = max(set(winners), key=winners.count)
        agreement = winners.count(most_common) / len(winners)
        
        return agreement
    
    def should_predict(self, prediction: Dict, confidence_threshold: float = 0.50) -> bool:
        """Determine if prediction is confident enough to use
        
        Args:
            prediction: Prediction dict from predict()
            confidence_threshold: Minimum confidence to predict (default 50%)
        
        Returns:
            True if prediction is confident enough
        """
        return prediction['prediction_confidence'] >= confidence_threshold

if __name__ == "__main__":
    from rotowire_scraper import RotoWireScraper
    
    meta = MetaEnsemblePredictor()
    scraper = RotoWireScraper()
    
    print("🎯 Meta-Ensemble Predictor Test")
    print("=" * 60)
    
    # Get today's games
    data = scraper.scrape_daily_data()
    
    if data['games']:
        game = data['games'][0]
        
        print(f"\n🏒 {game['away_team']} @ {game['home_team']}")
        print(f"Goalies: {game.get('away_goalie', 'TBD')} vs {game.get('home_goalie', 'TBD')}")
        
        # Make prediction
        pred = meta.predict(
            game['away_team'],
            game['home_team'],
            away_lineup=game.get('away_lineup'),
            home_lineup=game.get('home_lineup'),
            away_goalie=game.get('away_goalie'),
            home_goalie=game.get('home_goalie')
        )
        
        print(f"\n📊 Meta-Ensemble Prediction:")
        print(f"  {pred['predicted_winner']} wins")
        print(f"  Probabilities: {game['away_team']} {pred['away_prob']:.1f}% / {game['home_team']} {pred['home_prob']:.1f}%")
        print(f"  Confidence: {pred['prediction_confidence']:.1%}")
        print(f"  Agreement Score: {pred['agreement_score']:.1%}")
        print(f"  Injury Adjustment: {pred['injury_adjustment']:+.2f}")
        
        # Check if we should predict
        should_bet = meta.should_predict(pred, confidence_threshold=0.60)
        print(f"\n  Should Predict (60% threshold): {'✅ YES' if should_bet else '❌ NO (low confidence)'}")
        
        print(f"\n  Component Models Used: {len(pred['component_predictions'])}")
        for i, comp in enumerate(pred['component_predictions'], 1):
            method = comp.get('ensemble_method', comp.get('prediction_type', 'unknown'))
            print(f"    {i}. {method}: {comp['away_prob']:.1f}% / {comp['home_prob']:.1f}%")
