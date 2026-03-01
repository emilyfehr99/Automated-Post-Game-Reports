#!/usr/bin/env python3
"""
Meta Ensemble Predictor
Combines all prediction methods for maximum accuracy
"""
from typing import Dict, Optional
import json
import numpy as np
import xgboost as xgb
import pandas as pd
import pickle
import math
from pathlib import Path
from datetime import datetime
from ensemble_predictor import EnsemblePredictor
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

class EloTracker:
    def __init__(self, k_factor=20, home_advantage=35):
        self.ratings = {}  # {team: rating}
        self.k = k_factor
        self.ha = home_advantage
        self.base_rating = 1500

    def get_rating(self, team):
        return self.ratings.get(team, self.base_rating)

    def get_win_prob(self, home_team, away_team):
        home_rating = self.get_rating(home_team) + self.ha
        away_rating = self.get_rating(away_team)
        return 1 / (1 + 10 ** ((away_rating - home_rating) / 400))

    def update(self, home_team, away_team, home_score, away_score):
        if home_score > away_score:
            actual_home = 1.0
        else:
            actual_home = 0.0
            
        expected_home = self.get_win_prob(home_team, away_team)
        
        goal_diff = abs(home_score - away_score)
        multiplier = math.log(goal_diff + 1) if goal_diff > 0 else 1.0
        
        delta = self.k * multiplier * (actual_home - expected_home)
        
        self.ratings[home_team] = self.get_rating(home_team) + delta
        self.ratings[away_team] = self.get_rating(away_team) - delta

class TeamHistory:
    def __init__(self):
        self.history = {}  # {team_abbr: {'dates': [], 'stats': []}}
        self.elo = EloTracker()
        
    def update(self, team, date, game_stats):
        """Update team history with a new game"""
        if team not in self.history:
            self.history[team] = {'dates': [], 'stats': []}
            
        self.history[team]['dates'].append(date)
        self.history[team]['stats'].append(game_stats)
        
    def update_elo(self, home, away, h_score, a_score):
        self.elo.update(home, away, h_score, a_score)
        
    def get_elo(self, team):
        return self.elo.get_rating(team)

    def get_days_rest(self, team, current_date):
        """Get days since last game"""
        if team not in self.history or not self.history[team]['dates']:
            return 3  # Default to reasonable rest
            
        last_date = self.history[team]['dates'][-1]
        delta = (current_date - last_date).days
        return max(1, delta)
        
    def get_rolling_stats(self, team, window=5):
        """Calculate rolling averages for specified window"""
        if team not in self.history or len(self.history[team]['stats']) < 1:
            return {}
            
        stats_list = self.history[team]['stats'][-window:]
        aggregated = {}
        if not stats_list:
            return {}
            
        keys = stats_list[0].keys()
        for k in keys:
            vals = [g[k] for g in stats_list if g.get(k) is not None]
            if vals:
                aggregated[k] = np.mean(vals)
            else:
                aggregated[k] = 0.0
        return aggregated

class MetaEnsemblePredictor:
    """Combines multiple ensemble strategies for maximum accuracy"""
    
    def __init__(self):
        self.specialized_ensemble = EnsemblePredictor()
        self.base_model = ImprovedSelfLearningModelV2()
        
        # Load XGBoost Components
        self.xgb_model = None
        self.history_tracker = TeamHistory()
        self.feature_names = []
        self.team_profiles = {}
        
        try:
            self._load_xgboost_components()
        except Exception as e:
            print(f"⚠️ Failed to load XGBoost components: {e}")

    def _load_xgboost_components(self):
        """Load model, features list, and build history state"""
        # 1. Load Model
        model_path = Path("xgb_nhl_model.json")
        if model_path.exists():
            self.xgb_model = xgb.XGBClassifier()
            self.xgb_model.load_model(str(model_path))
            print(f"✅ Loaded XGBoost model from {model_path}")
            
        # 2. Load Feature Names
        feat_path = Path("xgb_features.pkl")
        if feat_path.exists():
            with open(feat_path, "rb") as f:
                self.feature_names = pickle.load(f)
            print(f"✅ Loaded {len(self.feature_names)} feature definitions")
        else:
            print("⚠️ feature definitions not found, XGBoost disabled")
            self.xgb_model = None
            return

        # 3. Load Finishing Profiles
        try:
            with open('team_scoring_profiles.json', 'r') as f:
                self.team_profiles = json.load(f)
            print(f"✅ Loaded {len(self.team_profiles)} team finishing profiles")
        except:
            print("⚠️ Could not load team finishing profiles")

        # 4. Build Team History State
        data_path = Path('data/win_probability_predictions_v2.json')
        if not data_path.exists():
            data_path = Path('win_probability_predictions_v2.json')
            
        if data_path.exists():
            print("⏳ Rebuilding team history state...")
            with open(data_path, 'r') as f:
                data = json.load(f)
            
            raw_preds = data.get('predictions', [])
            # Sort chronologically to replay history correctly
            sorted_preds = sorted(raw_preds, key=lambda x: x.get('date', '1900-01-01'))
            
            count = 0
            for p in sorted_preds:
                date_str = p.get('date')
                if not date_str:
                    continue
                try:
                    game_date = datetime.strptime(date_str, "%Y-%m-%d")
                except:
                    continue
                    
                metrics = p.get('metrics_used', {})
                home = p.get('home_team')
                away = p.get('away_team')
                
                # Extract stats (logic matches train_xgboost_model.py)
                h_goals = float(metrics.get('home_goals', 0) or p.get('actual_home_score', 0) or 0)
                a_goals = float(metrics.get('away_goals', 0) or p.get('actual_away_score', 0) or 0)
                h_xg = float(metrics.get('home_xg', 0) or 0)
                a_xg = float(metrics.get('away_xg', 0) or 0)
                h_corsi = float(metrics.get('home_corsi_pct', 50) or 50)
                a_corsi = float(metrics.get('away_corsi_pct', 50) or 50)
                h_pp = float(metrics.get('home_power_play_pct', 0) or 0)
                a_pp = float(metrics.get('away_power_play_pct', 0) or 0)

                h_stats = {'goal_diff': h_goals - a_goals, 'xg_diff': h_xg - a_xg, 'corsi_pct': h_corsi, 'pdo': 100.0, 'pp_pct': h_pp}
                a_stats = {'goal_diff': a_goals - h_goals, 'xg_diff': a_xg - h_xg, 'corsi_pct': a_corsi, 'pdo': 100.0, 'pp_pct': a_pp}
                
                self.history_tracker.update_elo(home, away, h_goals, a_goals)
                self.history_tracker.update(home, game_date, h_stats)
                self.history_tracker.update(away, game_date, a_stats)
                count += 1
            print(f"✅ Replayed {count} games to build current state")

    def _predict_xgboost(self, away_team, home_team, game_date_str=None) -> Optional[Dict]:
        """Make prediction using XGBoost model with dynamic features"""
        if not self.xgb_model or not self.feature_names:
            return None
            
        # Determine Game Date (default to today if None)
        if game_date_str:
            try:
                game_date = datetime.strptime(game_date_str, "%Y-%m-%d")
            except:
                game_date = datetime.now()
        else:
            game_date = datetime.now()
            
        tracker = self.history_tracker
        
        # Calculate Features
        home_elo = tracker.get_elo(home_team)
        away_elo = tracker.get_elo(away_team)
        
        home_rest = tracker.get_days_rest(home_team, game_date)
        away_rest = tracker.get_days_rest(away_team, game_date)
        
        h_l5 = tracker.get_rolling_stats(home_team, 5)
        a_l5 = tracker.get_rolling_stats(away_team, 5)
        h_l10 = tracker.get_rolling_stats(home_team, 10)
        a_l10 = tracker.get_rolling_stats(away_team, 10)
        
        # Finish Factors
        h_finish = self.team_profiles.get(home_team, 1.0)
        a_finish = self.team_profiles.get(away_team, 1.0)
        
        # Build Feature Vector
        feature_data = {
            'elo_diff': (home_elo + tracker.elo.ha) - away_elo,
            
            # Finish Factor
            'finish_diff': h_finish - a_finish,
            'home_finish': h_finish,
            'away_finish': a_finish,
            
            'rest_diff': home_rest - away_rest,
            'home_fatigue': 1 if home_rest <= 1 else 0,
            'away_fatigue': 1 if away_rest <= 1 else 0,
            
            'l5_goal_diff': h_l5.get('goal_diff', 0) - a_l5.get('goal_diff', 0),
            'l5_xg_diff': h_l5.get('xg_diff', 0) - a_l5.get('xg_diff', 0),
            'l5_corsi_diff': h_l5.get('corsi_pct', 50) - a_l5.get('corsi_pct', 50),
            'l5_pdo_diff': h_l5.get('pdo', 100) - a_l5.get('pdo', 100),
            'l5_pp_diff': h_l5.get('pp_pct', 20) - a_l5.get('pp_pct', 20),
            
            'l10_goal_diff': h_l10.get('goal_diff', 0) - a_l10.get('goal_diff', 0),
            'l10_xg_diff': h_l10.get('xg_diff', 0) - a_l10.get('xg_diff', 0),
        }
        
        # Ensure ordered columns match training
        try:
            vector = []
            for name in self.feature_names:
                vector.append(feature_data.get(name, 0.0))
                
            # Predict
            df = pd.DataFrame([vector], columns=self.feature_names)
            probs = self.xgb_model.predict_proba(df)[0]
            
            away_prob = probs[0] * 100
            home_prob = probs[1] * 100
            
            return {
                'away_team': away_team,
                'home_team': home_team,
                'away_prob': away_prob,
                'home_prob': home_prob,
                'prediction_type': 'xgboost_ml'
            }
        except Exception as e:
            print(f"XGBoost prediction error: {e}")
            return None
    
    def predict(self, away_team: str, home_team: str, 
                game_id: str = None, game_date: str = None,
                away_lineup: Dict = None, home_lineup: Dict = None,
                away_goalie: str = None, home_goalie: str = None,
                away_injuries: list = None, home_injuries: list = None,
                vegas_odds: Dict = None) -> Dict:
        """Meta-ensemble prediction combining all methods"""
        predictions = []
        weights = []
        
        # 1. XGBoost ML Model (50% Weight - Highest Accuracy Component)
        xgb_pred = self._predict_xgboost(away_team, home_team, game_date)
        if xgb_pred:
            predictions.append(xgb_pred)
            weights.append(0.50)
        
        # 2. Specialized ensemble (25% weight)
        try:
            spec_pred = self.specialized_ensemble.predict(away_team, home_team, game_id, game_date)
            predictions.append(spec_pred)
            weights.append(0.25)
        except Exception as e:
            print(f"Specialized ensemble failed: {e}")
        
        # 3. Player-level model (15% weight)
        if away_lineup and home_lineup:
            try:
                player_pred = self.base_model.predict_game_with_lineup(
                    away_team, home_team, away_lineup, home_lineup, game_id, game_date, vegas_odds=vegas_odds
                )
                predictions.append(player_pred)
                weights.append(0.15)
            except Exception as e:
                print(f"Player-level model failed: {e}")
        
        # 4. Base model (10% weight - reduced due to lower accuracy)
        try:
            base_pred = self.base_model.predict_game(away_team, home_team, game_id=game_id, game_date=game_date, vegas_odds=vegas_odds)
            predictions.append(base_pred)
            weights.append(0.10)
        except Exception as e:
            print(f"Base model failed: {e}")
            
        if not predictions:
            raise Exception("All prediction methods failed")
        
        # Weighted ensemble calculation
        total_weight = sum(weights)
        if total_weight == 0:
             total_weight = 1.0
             
        ensemble_away = sum(p['away_prob'] * w for p, w in zip(predictions, weights)) / total_weight
        ensemble_home = sum(p['home_prob'] * w for p, w in zip(predictions, weights)) / total_weight
        
        # Apply injury adjustments
        injury_adjustment = self._calculate_injury_impact(away_injuries, home_injuries)
        ensemble_away += injury_adjustment * 0.5
        ensemble_home -= injury_adjustment * 0.5
        
        # Normalize
        total = ensemble_away + ensemble_home
        if total > 0:
            ensemble_away = (ensemble_away / total) * 100
            ensemble_home = (ensemble_home / total) * 100
        
        confidence = max(ensemble_away, ensemble_home) / 100
        
        agreement_score = self._calculate_agreement(predictions, away_team, home_team)
        if agreement_score > 0.8:
            confidence = min(1.0, confidence * 1.05)
        
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
            'ensemble_method': 'meta_ensemble_v2_xgboost'
        }
    
    def _calculate_injury_impact(self, away_injuries: list, home_injuries: list) -> float:
        if not away_injuries and not home_injuries:
            return 0.0
        away_impact = self._team_injury_impact(away_injuries or [])
        home_impact = self._team_injury_impact(home_injuries or [])
        return home_impact - away_impact
    
    def _team_injury_impact(self, injuries: list) -> float:
        impact = 0.0
        for injury in injuries:
            position = injury.get('position', '')
            if position == 'G':
                impact += 0.10
            elif 'C' in position or 'W' in position:
                impact += 0.03
            elif 'D' in position:
                impact += 0.02
        return min(0.15, impact)
    
    def _calculate_agreement(self, predictions: list, away_team: str = None, home_team: str = None) -> float:
        if len(predictions) < 2:
            return 1.0
        winners = []
        for p in predictions:
            if p['away_prob'] > p['home_prob']:
                winners.append(away_team or p.get('away_team', 'away'))
            else:
                winners.append(home_team or p.get('home_team', 'home'))
        most_common = max(set(winners), key=winners.count)
        return winners.count(most_common) / len(winners)
    
    def should_predict(self, prediction: Dict, confidence_threshold: float = 0.50) -> bool:
        return prediction['prediction_confidence'] >= confidence_threshold

if __name__ == "__main__":
    from rotowire_scraper import RotoWireScraper
    meta = MetaEnsemblePredictor()
    scraper = RotoWireScraper()
    print("🎯 Meta-Ensemble Predictor Test (with XGBoost)")
    print("=" * 60)
    data = scraper.scrape_daily_data()
    if data['games']:
        game = data['games'][0]
        print(f"\n🏒 {game['away_team']} @ {game['home_team']}")
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
