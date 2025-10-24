"""
Improved Advanced Metrics Model with historical data and better features
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator

logger = logging.getLogger(__name__)

class ImprovedAdvancedModel:
    """Advanced NHL prediction model with historical data and improved features"""
    
    def __init__(self, predictions_file: str = "improved_advanced_predictions.json"):
        self.predictions_file = Path(predictions_file)
        self.model_data = self.load_model_data()
        self.api_client = NHLAPIClient()
        self.report_generator = PostGameReportGenerator()
        
        # Initialize data structures
        if "team_advanced_stats" not in self.model_data:
            self.model_data["team_advanced_stats"] = {}
        if "head_to_head_records" not in self.model_data:
            self.model_data["head_to_head_records"] = {}
        if "goalie_performance" not in self.model_data:
            self.model_data["goalie_performance"] = {}
        if "home_ice_advantage" not in self.model_data:
            self.model_data["home_ice_advantage"] = {}
        if "rest_days_advantage" not in self.model_data:
            self.model_data["rest_days_advantage"] = {}
        
        self.team_advanced_stats = self.model_data["team_advanced_stats"]
        self.head_to_head_records = self.model_data["head_to_head_records"]
        self.goalie_performance = self.model_data["goalie_performance"]
        self.home_ice_advantage = self.model_data["home_ice_advantage"]
        self.rest_days_advantage = self.model_data["rest_days_advantage"]
        
        # Model performance tracking
        if "model_performance" not in self.model_data:
            self.model_data["model_performance"] = {
                "total_games": 0, "correct_predictions": 0, "accuracy": 0.0,
                "high_confidence_accuracy": 0.0, "high_confidence_games": 0
            }
        
        # Improved metric weights based on analysis
        self.metric_weights = {
            "pressure_score": 0.25,      # Most predictive
            "possession_score": 0.20,    # Second most predictive
            "momentum_score": 0.15,      # Important for recent form
            "territorial_score": 0.15,   # Zone control matters
            "xg_avg": 0.15,             # Expected goals
            "hdc_avg": 0.10             # High danger chances
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            "high": 0.65,    # Only predict when >65% confident
            "medium": 0.55,  # Medium confidence
            "low": 0.45      # Low confidence
        }
        
        self.model_data["last_updated"] = datetime.now().isoformat()
    
    def load_model_data(self) -> Dict:
        """Load model data from file"""
        if self.predictions_file.exists():
            with open(self.predictions_file, 'r') as f:
                return json.load(f)
        return {"predictions": []}
    
    def save_model_data(self):
        """Save model data to file"""
        self.model_data["team_advanced_stats"] = self.team_advanced_stats
        self.model_data["head_to_head_records"] = self.head_to_head_records
        self.model_data["goalie_performance"] = self.goalie_performance
        self.model_data["home_ice_advantage"] = self.home_ice_advantage
        self.model_data["rest_days_advantage"] = self.rest_days_advantage
        
        with open(self.predictions_file, 'w') as f:
            json.dump(self.model_data, f, indent=2)
    
    def _get_default_advanced_performance(self) -> Dict:
        """Get default performance values for teams with no data"""
        return {
            'pressure_score': 50.0,
            'possession_score': 100.0,
            'momentum_score': 1.0,
            'territorial_score': 50.0,
            'xg_avg': 2.5,
            'hdc_avg': 5.0,
            'games_played': 0,
            'confidence': 0.1,
            'home_ice_advantage': 0.0,
            'goalie_save_pct': 0.900,
            'goalie_gaa': 3.0
        }
    
    def get_team_advanced_performance(self, team_abbrev: str, venue: str) -> Dict:
        """Get comprehensive team performance including all advanced metrics"""
        team_key = team_abbrev.upper()
        
        # Get basic advanced stats
        if team_key not in self.team_advanced_stats or venue not in self.team_advanced_stats[team_key]:
            base_perf = self._get_default_advanced_performance()
        else:
            venue_data = self.team_advanced_stats[team_key][venue]
            
            if not venue_data.get('games'):
                base_perf = self._get_default_advanced_performance()
            else:
                # Calculate averages
                base_perf = {
                    'pressure_score': np.mean(venue_data.get('pressure_score', [50.0])),
                    'possession_score': np.mean(venue_data.get('possession_score', [100.0])),
                    'momentum_score': np.mean(venue_data.get('momentum_score', [1.0])),
                    'territorial_score': np.mean(venue_data.get('territorial_score', [50.0])),
                    'xg_avg': np.mean(venue_data.get('xg', [2.5])),
                    'hdc_avg': np.mean(venue_data.get('hdc', [5.0])),
                    'games_played': len(venue_data['games']),
                    'confidence': min(1.0, len(venue_data['games']) / 15.0)  # More games = higher confidence
                }
        
        # Add home ice advantage
        base_perf['home_ice_advantage'] = self._get_home_ice_advantage(team_key, venue)
        
        # Add goalie performance
        goalie_stats = self._get_goalie_performance(team_key)
        base_perf.update(goalie_stats)
        
        return base_perf
    
    def _get_home_ice_advantage(self, team_abbrev: str, venue: str) -> float:
        """Calculate home ice advantage for a team"""
        if venue != "home":
            return 0.0
        
        team_key = team_abbrev.upper()
        
        if team_key not in self.home_ice_advantage:
            return 0.05  # Default 5% home ice advantage
        
        home_advantage = self.home_ice_advantage[team_key]
        return home_advantage
    
    def _get_goalie_performance(self, team_abbrev: str) -> Dict:
        """Get goalie performance metrics"""
        team_key = team_abbrev.upper()
        
        if team_key not in self.goalie_performance:
            return {
                'goalie_save_pct': 0.900,
                'goalie_gaa': 3.0,
                'goalie_confidence': 0.1
            }
        
        goalie_stats = self.goalie_performance[team_key]
        return {
            'goalie_save_pct': goalie_stats.get('save_pct', 0.900),
            'goalie_gaa': goalie_stats.get('gaa', 3.0),
            'goalie_confidence': min(1.0, goalie_stats.get('games_played', 0) / 10.0)
        }
    
    def _get_head_to_head_advantage(self, team1: str, team2: str) -> float:
        """Get head-to-head advantage between two teams"""
        team1_key = team1.upper()
        team2_key = team2.upper()
        
        # Create a consistent key for the matchup
        matchup_key = f"{min(team1_key, team2_key)}_vs_{max(team1_key, team2_key)}"
        
        if matchup_key not in self.head_to_head_records:
            return 0.0  # No head-to-head data
        
        h2h_record = self.head_to_head_records[matchup_key]
        
        # Calculate win percentage for team1
        total_games = h2h_record.get('total_games', 0)
        if total_games == 0:
            return 0.0
        
        team1_wins = h2h_record.get(f'{team1_key}_wins', 0)
        win_pct = team1_wins / total_games
        
        # Convert to advantage (-0.5 to 0.5)
        advantage = (win_pct - 0.5) * 2.0
        return advantage
    
    def _get_rest_days_advantage(self, team_abbrev: str, game_date: str) -> float:
        """Calculate rest days advantage"""
        team_key = team_abbrev.upper()
        
        if team_key not in self.rest_days_advantage:
            return 0.0
        
        rest_data = self.rest_days_advantage[team_key]
        
        # Get last game date
        last_game_date = rest_data.get('last_game_date')
        if not last_game_date:
            return 0.0
        
        # Calculate days between games
        try:
            last_date = datetime.strptime(last_game_date, '%Y-%m-%d')
            current_date = datetime.strptime(game_date, '%Y-%m-%d')
            days_rest = (current_date - last_date).days
            
            # Rest advantage: 1 day = -0.02, 2 days = 0.0, 3+ days = +0.01
            if days_rest == 1:
                return -0.02  # Back-to-back disadvantage
            elif days_rest == 2:
                return 0.0    # Normal rest
            elif days_rest >= 3:
                return 0.01   # Well-rested advantage
            else:
                return 0.0
        except:
            return 0.0
    
    def _calculate_composite_scores(self, game_data: Dict, team_id: int, team_abbrev: str, team_side: str) -> Dict:
        """Calculate comprehensive composite scores for a team"""
        try:
            # Get period stats
            period_stats = self.report_generator._calculate_real_period_stats(game_data, team_id, team_side)
            
            # Get zone metrics
            zone_metrics = self.report_generator._calculate_zone_metrics(game_data, team_id, team_side)
            
            # Get pass metrics
            pass_metrics = self.report_generator._calculate_pass_metrics(game_data, team_id, team_side)
            
            # Calculate pressure score
            oz_shots = np.sum(zone_metrics.get('oz_originating_shots', [0]))
            fc_sog = np.sum(zone_metrics.get('fc_cycle_sog', [0]))
            rush_sog = np.sum(zone_metrics.get('rush_sog', [0]))
            total_sog = np.sum(period_stats.get('shots', [1]))
            
            pressure_score = ((oz_shots + fc_sog + rush_sog) / max(1, total_sog)) * 100 if total_sog > 0 else 0.0
            
            # Calculate possession score
            total_passes = np.sum(pass_metrics[0]) if pass_metrics else 0
            successful_passes = np.sum(pass_metrics[1]) if pass_metrics else 0
            possession_score = (successful_passes / max(1, total_passes)) * 100 if total_passes > 0 else 0.0
            
            # Calculate momentum score
            goals_by_period = self.report_generator._calculate_goals_by_period(game_data, team_abbrev)
            momentum_score = 1.0
            if len(goals_by_period) >= 3:
                total_goals = np.sum(goals_by_period)
                if total_goals > 0:
                    momentum_score = (goals_by_period[2] - goals_by_period[0]) / total_goals
            
            # Calculate territorial score
            territorial_score = (oz_shots / max(1, total_sog)) * 100 if total_sog > 0 else 0.0
            
            # Get xG and HDC
            away_xg, home_xg = self.report_generator._calculate_xg_from_plays(game_data)
            away_hdc, home_hdc = self.report_generator._calculate_hdc_from_plays(game_data)
            
            if team_side == 'away':
                xg_val = away_xg
                hdc_val = away_hdc
            else:
                xg_val = home_xg
                hdc_val = home_hdc
            
            return {
                'pressure_score': pressure_score,
                'possession_score': possession_score,
                'momentum_score': momentum_score,
                'territorial_score': territorial_score,
                'xg': xg_val,
                'hdc': hdc_val
            }
        except Exception as e:
            logger.error(f"Error calculating composite scores for {team_abbrev}: {e}")
            return {
                'pressure_score': 50.0,
                'possession_score': 100.0,
                'momentum_score': 1.0,
                'territorial_score': 50.0,
                'xg': 2.5,
                'hdc': 5.0
            }
    
    def predict_game(self, away_team_abbrev: str, home_team_abbrev: str, game_date: str = None) -> Dict:
        """Make a comprehensive prediction with all advanced features"""
        # Get team performances
        away_perf = self.get_team_advanced_performance(away_team_abbrev, "away")
        home_perf = self.get_team_advanced_performance(home_team_abbrev, "home")
        
        # Calculate base scores using weighted metrics
        away_score = 0.0
        home_score = 0.0
        
        for metric, weight in self.metric_weights.items():
            away_score += away_perf[metric] * weight
            home_score += home_perf[metric] * weight
        
        # Apply home ice advantage
        home_ice_boost = home_perf['home_ice_advantage']
        home_score += home_ice_boost * 100  # Convert to score units
        
        # Apply head-to-head advantage
        h2h_advantage = self._get_head_to_head_advantage(away_team_abbrev, home_team_abbrev)
        away_score += h2h_advantage * 50  # Convert to score units
        home_score -= h2h_advantage * 50
        
        # Apply rest days advantage if game date provided
        if game_date:
            away_rest_advantage = self._get_rest_days_advantage(away_team_abbrev, game_date)
            home_rest_advantage = self._get_rest_days_advantage(home_team_abbrev, game_date)
            
            away_score += away_rest_advantage * 100
            home_score += home_rest_advantage * 100
        
        # Calculate probabilities
        total_score = away_score + home_score
        
        if total_score > 0:
            away_prob = (away_score / total_score) * 100
            home_prob = (home_score / total_score) * 100
        else:
            away_prob = 50.0
            home_prob = 50.0
        
        # Calculate confidence based on data quality and score separation
        avg_confidence = (away_perf['confidence'] + home_perf['confidence']) / 2.0
        score_separation = abs(away_score - home_score) / max(away_score, home_score, 1.0)
        
        # Higher confidence when we have more data and clearer separation
        prediction_confidence = (avg_confidence * 0.7) + (score_separation * 0.3)
        prediction_confidence = min(1.0, prediction_confidence)  # Cap at 100%
        
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
            'head_to_head_advantage': h2h_advantage
        }
    
    def update_team_advanced_stats(self, game_id: str, date: str, away_team_abbrev: str, home_team_abbrev: str,
                                   away_team_id: int, home_team_id: int,
                                   away_metrics: Dict, home_metrics: Dict):
        """Update team statistics with new game data"""
        
        def _update_venue_data(team_abbrev: str, venue: str, metrics: Dict):
            if team_abbrev not in self.team_advanced_stats:
                self.team_advanced_stats[team_abbrev] = {"home": {}, "away": {}}
            if venue not in self.team_advanced_stats[team_abbrev]:
                self.team_advanced_stats[team_abbrev][venue] = {}
            
            venue_data = self.team_advanced_stats[team_abbrev][venue]
            
            for key, value in metrics.items():
                if key not in venue_data:
                    venue_data[key] = []
                venue_data[key].append(value)
            
            if 'games' not in venue_data:
                venue_data['games'] = []
            venue_data['games'].append(date)
            
            # Keep only last 25 games to prevent memory bloat
            for key in venue_data.keys():
                if len(venue_data[key]) > 25:
                    venue_data[key] = venue_data[key][-25:]
        
        _update_venue_data(away_team_abbrev, "away", away_metrics)
        _update_venue_data(home_team_abbrev, "home", home_metrics)
        
        # Update head-to-head records
        self._update_head_to_head_record(away_team_abbrev, home_team_abbrev, 
                                        away_metrics.get('goals', 0), home_metrics.get('goals', 0))
        
        # Update home ice advantage
        self._update_home_ice_advantage(home_team_abbrev, away_metrics.get('goals', 0), home_metrics.get('goals', 0))
        
        # Update rest days tracking
        self._update_rest_days_tracking(away_team_abbrev, home_team_abbrev, date)
    
    def _update_head_to_head_record(self, team1: str, team2: str, team1_goals: int, team2_goals: int):
        """Update head-to-head record between two teams"""
        team1_key = team1.upper()
        team2_key = team2.upper()
        
        matchup_key = f"{min(team1_key, team2_key)}_vs_{max(team1_key, team2_key)}"
        
        if matchup_key not in self.head_to_head_records:
            self.head_to_head_records[matchup_key] = {
                'total_games': 0,
                f'{team1_key}_wins': 0,
                f'{team2_key}_wins': 0
            }
        
        record = self.head_to_head_records[matchup_key]
        record['total_games'] += 1
        
        if team1_goals > team2_goals:
            record[f'{team1_key}_wins'] += 1
        elif team2_goals > team1_goals:
            record[f'{team2_key}_wins'] += 1
    
    def _update_home_ice_advantage(self, home_team: str, away_goals: int, home_goals: int):
        """Update home ice advantage calculation"""
        team_key = home_team.upper()
        
        if team_key not in self.home_ice_advantage:
            self.home_ice_advantage[team_key] = {
                'home_games': 0,
                'home_wins': 0,
                'advantage': 0.05
            }
        
        home_stats = self.home_ice_advantage[team_key]
        home_stats['home_games'] += 1
        
        if home_goals > away_goals:
            home_stats['home_wins'] += 1
        
        # Calculate advantage as win percentage above 50%
        if home_stats['home_games'] > 0:
            win_pct = home_stats['home_wins'] / home_stats['home_games']
            home_stats['advantage'] = max(0.0, win_pct - 0.5)
    
    def _update_rest_days_tracking(self, away_team: str, home_team: str, game_date: str):
        """Update rest days tracking for teams"""
        for team in [away_team, home_team]:
            team_key = team.upper()
            
            if team_key not in self.rest_days_advantage:
                self.rest_days_advantage[team_key] = {
                    'last_game_date': None,
                    'games_played': 0
                }
            
            self.rest_days_advantage[team_key]['last_game_date'] = game_date
            self.rest_days_advantage[team_key]['games_played'] += 1
    
    def add_prediction(self, game_id: str, date: str, away_team: str, home_team: str,
                       predicted_away_prob: float, predicted_home_prob: float,
                       actual_winner: Optional[str] = None,
                       away_goals: Optional[int] = None, home_goals: Optional[int] = None):
        """Add a prediction record and update model performance"""
        
        prediction_record = {
            "game_id": game_id,
            "date": date,
            "away_team": away_team,
            "home_team": home_team,
            "predicted_away_win_prob": predicted_away_prob,
            "predicted_home_win_prob": predicted_home_prob,
            "actual_away_score": away_goals,
            "actual_home_score": home_goals,
            "actual_winner": actual_winner,
            "predicted_winner": away_team if predicted_away_prob > predicted_home_prob else home_team,
            "is_correct": (away_team if predicted_away_prob > predicted_home_prob else home_team) == actual_winner
        }
        
        self.model_data["predictions"].append(prediction_record)
        self.update_model_performance(prediction_record)
        
        logger.info(f"Added prediction for {away_team} @ {home_team}: {predicted_away_prob:.1f}% vs {predicted_home_prob:.1f}%")
    
    def update_model_performance(self, prediction_record: Dict):
        """Update model performance metrics"""
        perf = self.model_data["model_performance"]
        perf["total_games"] += 1
        
        if prediction_record["is_correct"]:
            perf["correct_predictions"] += 1
        
        perf["accuracy"] = (perf["correct_predictions"] / perf["total_games"]) * 100
        
        # Track high confidence accuracy
        confidence = prediction_record.get("confidence", 0)
        if confidence >= self.confidence_thresholds["high"] * 100:
            perf["high_confidence_games"] += 1
            if prediction_record["is_correct"]:
                perf["high_confidence_accuracy"] = (perf.get("high_confidence_correct", 0) + 1) / perf["high_confidence_games"] * 100
