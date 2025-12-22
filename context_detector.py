#!/usr/bin/env python3
"""
Context Detector
Determines which specialized model(s) to use for a given game
"""
from typing import List, Tuple
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from standings_tracker import StandingsTracker

class ContextDetector:
    def __init__(self):
        self.model = ImprovedSelfLearningModelV2()
        self.standings = StandingsTracker()
    
    def predict_total_goals(self, away_team: str, home_team: str) -> float:
        """Estimate expected total goals for the game"""
        # Get team performance
        away_perf = self.model.get_team_performance(away_team, venue="away")
        home_perf = self.model.get_team_performance(home_team, venue="home")
        
        # Simple total estimation
        away_expected = away_perf.get('goals_avg', 2.5)
        home_expected = home_perf.get('goals_avg', 2.5)
        
        return away_expected + home_expected
    
    def is_playoff_race(self, team: str, game_date: str = None) -> bool:
        """Check if team is in playoff race"""
        desperation = self.standings.calculate_desperation_index(team, game_date)
        return abs(desperation) > 0.05  # Significant desperation
    
    def detect_game_context(self, away_team: str, home_team: str, game_date: str = None) -> List[Tuple[str, float]]:
        """Determine which specialized model(s) to use
        
        Returns:
            List of (context_type, confidence) tuples
        """
        contexts = []
        
        # Calculate expected total
        expected_total = self.predict_total_goals(away_team, home_team)
        
        # High-scoring vs defensive matchup
        if expected_total > 6.0:
            contexts.append(('high_scoring', 0.7))
        elif expected_total < 5.5:
            contexts.append(('defensive', 0.7))
        else:
            contexts.append(('standard', 0.5))
        
        # Check playoff race
        away_in_race = self.is_playoff_race(away_team, game_date)
        home_in_race = self.is_playoff_race(home_team, game_date)
        
        if away_in_race or home_in_race:
            # Confidence higher if both teams in race
            confidence = 0.8 if (away_in_race and home_in_race) else 0.6
            contexts.append(('playoff_race', confidence))
        
        # Check rivalry
        rivalry_intensity = self.standings.get_rivalry_intensity(away_team, home_team)
        if rivalry_intensity > 0.05:
            # Confidence based on rivalry intensity
            confidence = min(0.9, rivalry_intensity * 10)  # Scale 0.05-0.08 to 0.5-0.8
            contexts.append(('rivalry', confidence))
        
        return contexts

if __name__ == "__main__":
    detector = ContextDetector()
    
    print("🔍 Context Detection Test")
    print("=" * 60)
    
    # Test various matchups
    test_games = [
        ('COL', 'DAL'),  # High-scoring teams
        ('BOS', 'MTL'),  # Rivalry
        ('NJD', 'NYI'),  # Defensive
        ('EDM', 'CGY'),  # Rivalry + potential high-scoring
    ]
    
    for away, home in test_games:
        print(f"\n{away} @ {home}:")
        
        expected_total = detector.predict_total_goals(away, home)
        print(f"  Expected Total: {expected_total:.1f} goals")
        
        contexts = detector.detect_game_context(away, home)
        print(f"  Contexts:")
        for context_type, confidence in contexts:
            print(f"    - {context_type}: {confidence:.1%} confidence")
