"""
Advanced NHL Prediction Model using sophisticated metrics instead of simple weights
"""

import json
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pdf_report_generator import PostGameReportGenerator
from nhl_api_client import NHLAPIClient

class AdvancedMetricsModel:
    """
    NHL prediction model using advanced metrics like sustained pressure,
    possession control, and momentum instead of simple weighted averages
    """
    
    def __init__(self, predictions_file: str = "advanced_predictions.json"):
        self.predictions_file = Path(predictions_file)
        self.api = NHLAPIClient()
        self.generator = PostGameReportGenerator()
        
        # Load existing data
        self.model_data = self.load_model_data()
        self.team_stats = self.model_data.get("team_stats", {})
        
        # Advanced metrics storage
        self.advanced_metrics = self.model_data.get("advanced_metrics", {})
        
    def load_model_data(self) -> Dict:
        """Load model data from file"""
        if self.predictions_file.exists():
            with open(self.predictions_file, 'r') as f:
                return json.load(f)
        return {
            "predictions": [],
            "team_stats": {},
            "advanced_metrics": {},
            "model_performance": {
                "total_games": 0,
                "correct_predictions": 0,
                "accuracy": 0.0
            }
        }
    
    def save_model_data(self):
        """Save model data to file"""
        self.model_data["team_stats"] = self.team_stats
        self.model_data["advanced_metrics"] = self.advanced_metrics
        self.model_data["last_updated"] = datetime.now().isoformat()
        
        with open(self.predictions_file, 'w') as f:
            json.dump(self.model_data, f, indent=2)
    
    def calculate_pressure_score(self, zone_metrics: Dict) -> float:
        """
        Calculate sustained pressure score from zone metrics
        Higher score = more sustained offensive pressure
        """
        if not zone_metrics:
            return 0.0
        
        # Get zone metrics
        oz_shots = sum(zone_metrics.get('oz_originating_shots', [0]))
        fc_sog = sum(zone_metrics.get('fc_cycle_sog', [0]))
        rush_sog = sum(zone_metrics.get('rush_sog', [0]))
        nz_turnovers = sum(zone_metrics.get('nz_turnovers', [0]))
        
        # Calculate pressure score
        total_pressure_shots = oz_shots + fc_sog + rush_sog
        pressure_score = total_pressure_shots + (nz_turnovers * 0.5)  # Turnovers create pressure
        
        return pressure_score
    
    def calculate_possession_score(self, pass_metrics: Tuple) -> float:
        """
        Calculate possession control score from pass metrics
        Higher score = better puck control and movement
        """
        if not pass_metrics or len(pass_metrics) < 2:
            return 0.0
        
        total_passes = sum(pass_metrics[0]) if pass_metrics[0] else 0
        successful_passes = sum(pass_metrics[1]) if pass_metrics[1] else 0
        interceptions = sum(pass_metrics[2]) if len(pass_metrics) > 2 and pass_metrics[2] else 0
        
        if total_passes == 0:
            return 0.0
        
        # Possession score = pass success rate + defensive interceptions
        pass_success_rate = successful_passes / total_passes
        possession_score = (pass_success_rate * 100) + (interceptions * 2)  # Interceptions are valuable
        
        return possession_score
    
    def calculate_momentum_score(self, period_metrics: Tuple) -> float:
        """
        Calculate momentum score from period-by-period performance
        Higher score = better late-game performance and consistency
        """
        if not period_metrics or len(period_metrics) < 2:
            return 0.0
        
        period_xg = period_metrics[0] if period_metrics[0] else [0, 0, 0]
        period_performance = period_metrics[1] if period_metrics[1] else [0, 0, 0]
        
        if len(period_xg) < 3 or len(period_performance) < 3:
            return 0.0
        
        # Calculate momentum indicators
        early_game = period_xg[0] + period_xg[1]  # First two periods
        late_game = period_xg[2]  # Third period
        
        if early_game > 0:
            momentum_ratio = late_game / early_game
        else:
            momentum_ratio = 1.0 if late_game > 0 else 0.0
        
        # Consistency score (lower variance = more consistent)
        xg_variance = np.var(period_xg) if len(period_xg) > 1 else 0
        consistency_score = max(0, 10 - xg_variance)  # Lower variance = higher score
        
        momentum_score = (momentum_ratio * 20) + consistency_score
        
        return momentum_score
    
    def calculate_territorial_control(self, zone_metrics: Dict) -> float:
        """
        Calculate territorial control score
        Higher score = more time spent in offensive zone
        """
        if not zone_metrics:
            return 0.0
        
        oz_shots = sum(zone_metrics.get('oz_originating_shots', [0]))
        dz_shots = sum(zone_metrics.get('dz_originating_shots', [0]))
        nz_shots = sum(zone_metrics.get('nz_originating_shots', [0]))
        
        total_shots = oz_shots + dz_shots + nz_shots
        if total_shots == 0:
            return 0.0
        
        # Territorial control = offensive zone dominance
        territorial_score = (oz_shots / total_shots) * 100
        
        return territorial_score
    
    def get_team_advanced_performance(self, team: str, venue: str) -> Dict:
        """Get comprehensive advanced performance metrics for a team"""
        team_key = team.upper()
        
        if team_key not in self.advanced_metrics:
            return self._get_default_advanced_performance()
        
        team_data = self.advanced_metrics[team_key]
        if venue not in team_data:
            return self._get_default_advanced_performance()
        
        venue_data = team_data[venue]
        
        # Calculate averages for all advanced metrics
        performance = {}
        
        # Pressure scores
        pressure_scores = venue_data.get('pressure_scores', [])
        performance['pressure_avg'] = np.mean(pressure_scores) if pressure_scores else 0.0
        
        # Possession scores
        possession_scores = venue_data.get('possession_scores', [])
        performance['possession_avg'] = np.mean(possession_scores) if possession_scores else 0.0
        
        # Momentum scores
        momentum_scores = venue_data.get('momentum_scores', [])
        performance['momentum_avg'] = np.mean(momentum_scores) if momentum_scores else 0.0
        
        # Territorial control
        territorial_scores = venue_data.get('territorial_scores', [])
        performance['territorial_avg'] = np.mean(territorial_scores) if territorial_scores else 0.0
        
        # Traditional metrics (still important)
        xg_scores = venue_data.get('xg_scores', [])
        performance['xg_avg'] = np.mean(xg_scores) if xg_scores else 0.0
        
        hdc_scores = venue_data.get('hdc_scores', [])
        performance['hdc_avg'] = np.mean(hdc_scores) if hdc_scores else 0.0
        
        # Games played
        performance['games_played'] = len(pressure_scores)
        
        return performance
    
    def _get_default_advanced_performance(self) -> Dict:
        """Get default performance for teams with no data"""
        return {
            'pressure_avg': 0.0,
            'possession_avg': 0.0,
            'momentum_avg': 0.0,
            'territorial_avg': 0.0,
            'xg_avg': 0.0,
            'hdc_avg': 0.0,
            'games_played': 0
        }
    
    def predict_game_advanced(self, away_team: str, home_team: str) -> Dict:
        """
        Make prediction using advanced metrics instead of simple weights
        """
        # Get advanced performance data
        away_perf = self.get_team_advanced_performance(away_team, "away")
        home_perf = self.get_team_advanced_performance(home_team, "home")
        
        # Calculate composite scores
        away_score = self._calculate_composite_score(away_perf)
        home_score = self._calculate_composite_score(home_perf)
        
        # Handle edge cases
        if away_score == 0 and home_score == 0:
            away_prob = 50.0
            home_prob = 50.0
            confidence = 10.0
        else:
            # Calculate probabilities
            total_score = away_score + home_score
            away_prob = (away_score / total_score) * 100
            home_prob = (home_score / total_score) * 100
            
            # Calculate confidence based on data quality and score difference
            data_quality = min(away_perf['games_played'], home_perf['games_played']) / 10.0
            score_difference = abs(away_score - home_score) / max(away_score, home_score, 1)
            confidence = min(95.0, (data_quality * 30) + (score_difference * 40))
        
        # Determine predicted winner
        predicted_winner = "away" if away_prob > home_prob else "home"
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'predicted_winner': predicted_winner,
            'prediction_confidence': confidence,
            'away_score': away_score,
            'home_score': home_score,
            'away_performance': away_perf,
            'home_performance': home_perf
        }
    
    def _calculate_composite_score(self, performance: Dict) -> float:
        """
        Calculate composite score from all advanced metrics
        This replaces the weighted approach with a more sophisticated calculation
        """
        # Base scores from advanced metrics
        pressure_score = performance.get('pressure_avg', 0.0)
        possession_score = performance.get('possession_avg', 0.0)
        momentum_score = performance.get('momentum_avg', 0.0)
        territorial_score = performance.get('territorial_avg', 0.0)
        
        # Traditional metrics (still important)
        xg_score = performance.get('xg_avg', 0.0)
        hdc_score = performance.get('hdc_avg', 0.0)
        
        # Calculate composite score
        # Advanced metrics get higher weight as they're more predictive
        composite_score = (
            pressure_score * 0.25 +      # Sustained pressure is very important
            possession_score * 0.20 +    # Puck control matters
            momentum_score * 0.15 +      # Late-game performance
            territorial_score * 0.15 +   # Zone control
            xg_score * 0.15 +            # Shot quality
            hdc_score * 0.10             # Dangerous chances
        )
        
        return composite_score
    
    def add_game_data(self, game_id: str, date: str, away_team: str, home_team: str, 
                     game_data: Dict, actual_winner: Optional[str] = None):
        """
        Add game data and extract advanced metrics
        """
        try:
            # Extract advanced metrics using the report generator
            away_team_id = game_data['boxscore']['awayTeam']['id']
            home_team_id = game_data['boxscore']['homeTeam']['id']
            
            # Get zone metrics
            away_zone_metrics = self.generator._calculate_zone_metrics(game_data, away_team_id, 'away')
            home_zone_metrics = self.generator._calculate_zone_metrics(game_data, home_team_id, 'home')
            
            # Get pass metrics
            away_pass_metrics = self.generator._calculate_pass_metrics(game_data, away_team_id, 'away')
            home_pass_metrics = self.generator._calculate_pass_metrics(game_data, home_team_id, 'home')
            
            # Get period metrics
            away_period_metrics = self.generator._calculate_period_metrics(game_data, away_team_id, 'away')
            home_period_metrics = self.generator._calculate_period_metrics(game_data, home_team_id, 'home')
            
            # Get traditional metrics
            away_xg, home_xg = self.generator._calculate_xg_from_plays(game_data)
            away_hdc, home_hdc = self.generator._calculate_hdc_from_plays(game_data)
            
            # Calculate advanced scores
            away_pressure = self.calculate_pressure_score(away_zone_metrics)
            home_pressure = self.calculate_pressure_score(home_zone_metrics)
            
            away_possession = self.calculate_possession_score(away_pass_metrics)
            home_possession = self.calculate_possession_score(home_pass_metrics)
            
            away_momentum = self.calculate_momentum_score(away_period_metrics)
            home_momentum = self.calculate_momentum_score(home_period_metrics)
            
            away_territorial = self.calculate_territorial_control(away_zone_metrics)
            home_territorial = self.calculate_territorial_control(home_zone_metrics)
            
            # Store advanced metrics
            self._store_advanced_metrics(away_team, "away", {
                'pressure_scores': [away_pressure],
                'possession_scores': [away_possession],
                'momentum_scores': [away_momentum],
                'territorial_scores': [away_territorial],
                'xg_scores': [away_xg],
                'hdc_scores': [away_hdc]
            })
            
            self._store_advanced_metrics(home_team, "home", {
                'pressure_scores': [home_pressure],
                'possession_scores': [home_possession],
                'momentum_scores': [home_momentum],
                'territorial_scores': [home_territorial],
                'xg_scores': [home_xg],
                'hdc_scores': [home_hdc]
            })
            
            # Make prediction
            prediction = self.predict_game_advanced(away_team, home_team)
            
            # Store prediction
            prediction_record = {
                'game_id': game_id,
                'date': date,
                'away_team': away_team,
                'home_team': home_team,
                'predicted_away_prob': prediction['away_prob'],
                'predicted_home_prob': prediction['home_prob'],
                'predicted_winner': prediction['predicted_winner'],
                'prediction_confidence': prediction['prediction_confidence'],
                'away_score': prediction['away_score'],
                'home_score': prediction['home_score'],
                'actual_winner': actual_winner,
                'advanced_metrics': {
                    'away_pressure': away_pressure,
                    'home_pressure': home_pressure,
                    'away_possession': away_possession,
                    'home_possession': home_possession,
                    'away_momentum': away_momentum,
                    'home_momentum': home_momentum,
                    'away_territorial': away_territorial,
                    'home_territorial': home_territorial
                }
            }
            
            self.model_data['predictions'].append(prediction_record)
            
            # Update performance metrics
            if actual_winner:
                self._update_performance_metrics(prediction_record)
            
            self.save_model_data()
            
            return prediction
            
        except Exception as e:
            print(f"Error adding game data: {e}")
            return None
    
    def _store_advanced_metrics(self, team: str, venue: str, metrics: Dict):
        """Store advanced metrics for a team"""
        team_key = team.upper()
        
        if team_key not in self.advanced_metrics:
            self.advanced_metrics[team_key] = {"home": {}, "away": {}}
        
        if venue not in self.advanced_metrics[team_key]:
            self.advanced_metrics[team_key][venue] = {}
        
        venue_data = self.advanced_metrics[team_key][venue]
        
        # Append new metrics to existing lists
        for metric_name, values in metrics.items():
            if metric_name not in venue_data:
                venue_data[metric_name] = []
            
            if isinstance(values, list):
                venue_data[metric_name].extend(values)
            else:
                venue_data[metric_name].append(values)
            
            # Keep only last 20 games to prevent memory bloat
            if len(venue_data[metric_name]) > 20:
                venue_data[metric_name] = venue_data[metric_name][-20:]
    
    def _update_performance_metrics(self, prediction_record: Dict):
        """Update model performance metrics"""
        perf = self.model_data['model_performance']
        perf['total_games'] += 1
        
        predicted_winner = prediction_record['predicted_winner']
        actual_winner = prediction_record['actual_winner']
        
        if predicted_winner == actual_winner:
            perf['correct_predictions'] += 1
        
        perf['accuracy'] = (perf['correct_predictions'] / perf['total_games']) * 100
    
    def get_model_performance(self) -> Dict:
        """Get current model performance"""
        return self.model_data['model_performance']
