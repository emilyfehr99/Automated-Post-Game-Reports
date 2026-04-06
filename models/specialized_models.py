#!/usr/bin/env python3
"""
Specialized Models
Contains context-specific prediction models optimized for different game types
"""
from typing import Dict
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

class HighScoringGameModel(ImprovedSelfLearningModelV2):
    """Optimized for high-scoring games (O/U > 6)"""
    
    def __init__(self):
        super().__init__()
        # Override weights for high-scoring context
        self.specialized_weights = {
            'xg_weight': 0.15,           # ↑ Offense matters more
            'shots_weight': 0.10,        # ↑ Volume shooting
            'power_play_weight': 0.12,   # ↑ PP opportunities
            'corsi_weight': 0.08,        # ↑ Possession
            'goalie_performance_weight': 0.05,  # ↓ Goalies less impactful
            'blocked_shots_weight': 0.02,# ↓ Defense less important
            'hdc_weight': 0.06,
            'faceoff_weight': 0.04,
            'hits_weight': 0.02,
            'takeaways_weight': 0.03,
            'penalty_minutes_weight': 0.02,
            'recent_form_weight': 0.08,
            'head_to_head_weight': 0.05,
            'rest_days_weight': 0.03,
            'sos_weight': 0.04,
            'rebounds_weight': 0.05,
            'rush_shots_weight': 0.04,
            'traffic_weight': 0.02,
            'zone_entry_weight': 0.00
        }
    
    def get_current_weights(self) -> Dict:
        """Return specialized weights for high-scoring games"""
        return self.specialized_weights

class DefensiveMatchupModel(ImprovedSelfLearningModelV2):
    """Optimized for defensive matchups (O/U < 5.5)"""
    
    def __init__(self):
        super().__init__()
        # Override weights for defensive context
        self.specialized_weights = {
            'goalie_performance_weight': 0.25,  # ↑ Goalie dominates
            'blocked_shots_weight': 0.12,# ↑ Defense critical
            'hdc_weight': 0.10,          # ↑ Quality over quantity
            'xg_weight': 0.08,           # ↓ Less scoring overall
            'shots_weight': 0.03,        # ↓ Volume less important
            'power_play_weight': 0.05,   # ↓ Fewer PP opportunities
            'corsi_weight': 0.04,
            'faceoff_weight': 0.06,
            'hits_weight': 0.04,
            'takeaways_weight': 0.05,
            'penalty_minutes_weight': 0.03,
            'recent_form_weight': 0.06,
            'head_to_head_weight': 0.04,
            'rest_days_weight': 0.02,
            'sos_weight': 0.02,
            'rebounds_weight': 0.01,
            'rush_shots_weight': 0.00,
            'traffic_weight': 0.00,
            'zone_entry_weight': 0.00
        }
    
    def get_current_weights(self) -> Dict:
        """Return specialized weights for defensive games"""
        return self.specialized_weights

class PlayoffRaceModel(ImprovedSelfLearningModelV2):
    """Optimized for playoff race games (late season, teams fighting for spots)"""
    
    def __init__(self):
        super().__init__()
        # Override weights for playoff race context
        self.specialized_weights = {
            'recent_form_weight': 0.15,  # ↑ Recent performance critical
            'rest_days_weight': 0.02,    # ↓ Teams play through fatigue
            'goalie_performance_weight': 0.12,
            'xg_weight': 0.10,
            'hdc_weight': 0.08,
            'corsi_weight': 0.06,
            'power_play_weight': 0.08,
            'shots_weight': 0.05,
            'blocked_shots_weight': 0.06,
            'faceoff_weight': 0.05,
            'hits_weight': 0.03,
            'takeaways_weight': 0.04,
            'penalty_minutes_weight': 0.02,
            'head_to_head_weight': 0.06,
            'sos_weight': 0.03,
            'rebounds_weight': 0.03,
            'rush_shots_weight': 0.02,
            'traffic_weight': 0.00,
            'zone_entry_weight': 0.00
        }
        
        # Amplify desperation impact
        self.desperation_multiplier = 2.0
    
    def get_current_weights(self) -> Dict:
        """Return specialized weights for playoff race games"""
        return self.specialized_weights

class RivalryGameModel(ImprovedSelfLearningModelV2):
    """Optimized for rivalry games (high intensity, emotional)"""
    
    def __init__(self):
        super().__init__()
        # Override weights for rivalry context
        self.specialized_weights = {
            'recent_form_weight': 0.10,
            'head_to_head_weight': 0.12,  # ↑ Recent meetings matter
            'hits_weight': 0.08,          # ↑ Physical play
            'penalty_minutes_weight': 0.05, # ↑ Chippy games
            'goalie_performance_weight': 0.10,
            'xg_weight': 0.09,
            'hdc_weight': 0.07,
            'corsi_weight': 0.05,
            'power_play_weight': 0.07,
            'shots_weight': 0.06,
            'blocked_shots_weight': 0.05,
            'faceoff_weight': 0.04,
            'takeaways_weight': 0.04,
            'rest_days_weight': 0.03,
            'sos_weight': 0.02,
            'rebounds_weight': 0.02,
            'rush_shots_weight': 0.01,
            'traffic_weight': 0.00,
            'zone_entry_weight': 0.00
        }
        
        # Amplify rivalry and home advantage
        self.rivalry_multiplier = 1.5
        self.home_advantage_multiplier = 1.2
    
    def get_current_weights(self) -> Dict:
        """Return specialized weights for rivalry games"""
        return self.specialized_weights

if __name__ == "__main__":
    print("🎯 Specialized Models Test")
    print("=" * 60)
    
    # Test each specialized model
    models = {
        'High-Scoring': HighScoringGameModel(),
        'Defensive': DefensiveMatchupModel(),
        'Playoff Race': PlayoffRaceModel(),
        'Rivalry': RivalryGameModel()
    }
    
    for name, model in models.items():
        weights = model.get_current_weights()
        print(f"\n{name} Model:")
        print(f"  Top 3 weights:")
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:3]
        for weight_name, value in sorted_weights:
            print(f"    {weight_name}: {value:.3f}")
