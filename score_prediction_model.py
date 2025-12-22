#!/usr/bin/env python3
"""
Advanced Score Prediction Model
Predicts realistic game scores based on team metrics, xG, goalie performance, and context
"""
import numpy as np
from typing import Dict, Tuple
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

class ScorePredictionModel:
    """Advanced model for predicting realistic game scores"""
    
    def __init__(self):
        self.base_model = ImprovedSelfLearningModelV2()
        
        # League averages (2024-25 season)
        self.league_avg_goals = 3.0
        self.league_avg_xg = 2.5
        
    def predict_score(self, away_team: str, home_team: str, 
                     away_goalie: str = None, home_goalie: str = None,
                     game_date: str = None) -> Dict:
        """Predict realistic game score
        
        Returns:
            Dict with away_score, home_score, total_goals, and confidence
        """
        # Get team performance data
        away_perf = self.base_model.get_team_performance(away_team, venue="away")
        home_perf = self.base_model.get_team_performance(home_team, venue="home")
        
        # 1. Calculate Expected Goals (xG) baseline
        away_xg = self._calculate_expected_goals(away_team, home_team, "away", away_perf, home_perf)
        home_xg = self._calculate_expected_goals(home_team, away_team, "home", home_perf, away_perf)
        
        # 2. Apply goalie adjustments
        away_xg_adjusted = self._apply_goalie_adjustment(away_xg, home_goalie, home_team)
        home_xg_adjusted = self._apply_goalie_adjustment(home_xg, away_goalie, away_team)
        
        # 3. Apply pace/tempo adjustments
        away_xg_final, home_xg_final = self._apply_pace_adjustment(
            away_xg_adjusted, home_xg_adjusted, away_perf, home_perf
        )
        
        # 4. Apply situational context (rivalry, playoff race)
        away_xg_final, home_xg_final = self._apply_situational_adjustment(
            away_xg_final, home_xg_final, away_team, home_team
        )
        
        # 5. Convert xG to actual goals with variance
        away_goals = self._xg_to_goals(away_xg_final)
        home_goals = self._xg_to_goals(home_xg_final)
        
        # 6. Ensure realistic score differential
        away_goals, home_goals = self._normalize_score_differential(away_goals, home_goals)
        
        return {
            'away_score': int(round(away_goals)),
            'home_score': int(round(home_goals)),
            'away_xg': round(away_xg_final, 2),
            'home_xg': round(home_xg_final, 2),
            'total_goals': int(round(away_goals + home_goals)),
            'confidence': self._calculate_confidence(away_xg_final, home_xg_final)
        }
    
    def _calculate_expected_goals(self, team: str, opponent: str, venue: str,
                                 team_perf: Dict, opp_perf: Dict) -> float:
        """Calculate expected goals for a team"""
        # Base xG from team's offensive strength
        team_xg_avg = team_perf.get('xg_avg', self.league_avg_xg)
        
        # Opponent's defensive strength (xG against)
        opp_xg_against = opp_perf.get('xg_against_avg', self.league_avg_xg)
        
        # Goals scoring rate
        team_goals_avg = team_perf.get('goals_avg', self.league_avg_goals)
        
        # Shooting percentage (goals / xG ratio)
        if team_xg_avg > 0:
            shooting_efficiency = team_goals_avg / team_xg_avg
        else:
            shooting_efficiency = 1.0
        
        # Combine factors with more conservative weighting
        base_xg = (team_xg_avg * 0.4 + opp_xg_against * 0.4 + team_goals_avg * 0.2)
        
        # Apply shooting efficiency (capped to avoid extremes)
        shooting_efficiency = max(0.8, min(1.2, shooting_efficiency))
        expected_goals = base_xg * shooting_efficiency
        
        # Home ice advantage (3% boost for home team)
        if venue == "home":
            expected_goals *= 1.03
        
        return max(2.0, min(4.0, expected_goals))  # Clamp to realistic range
    
    def _apply_goalie_adjustment(self, xg: float, goalie_name: str, team: str) -> float:
        """Adjust xG based on goalie performance"""
        if not goalie_name or goalie_name == "TBD":
            return xg
        
        try:
            from goalie_performance_tracker import GoaliePerformanceTracker
            tracker = GoaliePerformanceTracker()
            
            # Get goalie's recent form
            recent_starts = tracker.get_goalie_recent_starts(goalie_name, team, n=5)
            
            if recent_starts:
                # Calculate average GSAx (Goals Saved Above Expected)
                avg_gsax = np.mean([s.get('gsax', 0) for s in recent_starts])
                
                # Elite goalies (GSAx > 0.5): reduce xG against by 15%
                # Average goalies (GSAx ~0): no change
                # Poor goalies (GSAx < -0.5): increase xG against by 15%
                
                if avg_gsax > 0.5:
                    adjustment = 0.85  # Elite goalie
                elif avg_gsax > 0.2:
                    adjustment = 0.92  # Above average
                elif avg_gsax < -0.5:
                    adjustment = 1.15  # Poor goalie
                elif avg_gsax < -0.2:
                    adjustment = 1.08  # Below average
                else:
                    adjustment = 1.0  # Average
                
                return xg * adjustment
        except:
            pass
        
        return xg
    
    def _apply_pace_adjustment(self, away_xg: float, home_xg: float,
                               away_perf: Dict, home_perf: Dict) -> Tuple[float, float]:
        """Adjust for game pace/tempo"""
        # High-tempo teams generate more shots and chances
        away_shots = away_perf.get('shots_avg', 30)
        home_shots = home_perf.get('shots_avg', 30)
        
        # League average is ~30 shots per game
        avg_shots = (away_shots + home_shots) / 2
        
        if avg_shots > 33:
            # High-tempo game: boost both teams' xG by 10%
            pace_factor = 1.10
        elif avg_shots > 31:
            # Above average pace: boost by 5%
            pace_factor = 1.05
        elif avg_shots < 27:
            # Low-tempo game: reduce by 10%
            pace_factor = 0.90
        elif avg_shots < 29:
            # Below average pace: reduce by 5%
            pace_factor = 0.95
        else:
            pace_factor = 1.0
        
        return away_xg * pace_factor, home_xg * pace_factor
    
    def _apply_situational_adjustment(self, away_xg: float, home_xg: float,
                                     away_team: str, home_team: str) -> Tuple[float, float]:
        """Apply situational context adjustments"""
        try:
            from standings_tracker import StandingsTracker
            tracker = StandingsTracker()
            
            # Rivalry games tend to be higher scoring
            rivalry_intensity = tracker.get_rivalry_intensity(away_team, home_team)
            if rivalry_intensity > 0.05:
                # Rivalry boost: 5-10% more goals
                rivalry_factor = 1.05 + (rivalry_intensity * 0.5)
                away_xg *= rivalry_factor
                home_xg *= rivalry_factor
        except:
            pass
        
        return away_xg, home_xg
    
    def _xg_to_goals(self, xg: float) -> float:
        """Convert xG to actual goals with realistic variance"""
        # Add some randomness (±10% variance, reduced from 15%)
        variance = np.random.normal(0, 0.10)
        goals = xg * (1 + variance)
        
        # Ensure minimum of 0.5 goals
        return max(0.5, goals)
    
    def _normalize_score_differential(self, away_goals: float, home_goals: float) -> Tuple[float, float]:
        """Ensure realistic score differentials"""
        diff = abs(away_goals - home_goals)
        
        # NHL games rarely have >5 goal differentials
        if diff > 5:
            # Scale down the differential
            if away_goals > home_goals:
                away_goals = home_goals + 4.5
            else:
                home_goals = away_goals + 4.5
        
        # Ensure total goals is realistic (2-8 range)
        total = away_goals + home_goals
        if total < 2:
            # Scale up
            scale = 2.5 / total
            away_goals *= scale
            home_goals *= scale
        elif total > 8:
            # Scale down
            scale = 7.5 / total
            away_goals *= scale
            home_goals *= scale
        
        return away_goals, home_goals
    
    def _calculate_confidence(self, away_xg: float, home_xg: float) -> float:
        """Calculate confidence in score prediction"""
        # Higher xG differential = more confident
        diff = abs(away_xg - home_xg)
        
        if diff > 1.0:
            return 0.85  # High confidence
        elif diff > 0.5:
            return 0.75  # Medium-high confidence
        elif diff > 0.3:
            return 0.65  # Medium confidence
        else:
            return 0.55  # Lower confidence (close game)

if __name__ == "__main__":
    model = ScorePredictionModel()
    
    print("🎯 Advanced Score Prediction Model Test")
    print("=" * 60)
    
    # Test various matchups
    test_games = [
        ('COL', 'DAL', 'High-scoring teams'),
        ('BOS', 'MTL', 'Rivalry game'),
        ('NJD', 'NYI', 'Defensive matchup'),
    ]
    
    for away, home, description in test_games:
        pred = model.predict_score(away, home)
        
        print(f"\n{away} @ {home} ({description}):")
        print(f"  Score: {away} {pred['away_score']} - {home} {pred['home_score']}")
        print(f"  Total: {pred['total_goals']} goals")
        print(f"  xG: {away} {pred['away_xg']} - {home} {pred['home_xg']}")
        print(f"  Confidence: {pred['confidence']:.1%}")
