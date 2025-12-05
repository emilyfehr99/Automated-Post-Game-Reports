"""
Simple Game State Analyzer - Focuses on comeback probabilities based on score differentials
"""

class SimpleGameStateAnalyzer:
    def __init__(self):
        # Based on NHL historical data and common hockey knowledge
        self.comeback_rates = {
            # 1 goal deficit
            1: {
                'p1': 0.35,  # 35% chance to come back from 1 goal down in period 1
                'p2': 0.30,  # 30% chance to come back from 1 goal down in period 2  
                'p3': 0.25,  # 25% chance to come back from 1 goal down in period 3
            },
            # 2 goal deficit
            2: {
                'p1': 0.20,  # 20% chance to come back from 2 goals down in period 1
                'p2': 0.15,  # 15% chance to come back from 2 goals down in period 2
                'p3': 0.10,  # 10% chance to come back from 2 goals down in period 3
            },
            # 3 goal deficit
            3: {
                'p1': 0.10,  # 10% chance to come back from 3 goals down in period 1
                'p2': 0.08,  # 8% chance to come back from 3 goals down in period 2
                'p3': 0.05,  # 5% chance to come back from 3 goals down in period 3
            },
            # 4+ goal deficit
            4: {
                'p1': 0.05,  # 5% chance to come back from 4+ goals down in period 1
                'p2': 0.03,  # 3% chance to come back from 4+ goals down in period 2
                'p3': 0.01,  # 1% chance to come back from 4+ goals down in period 3
            }
        }
    
    def get_comeback_probability(self, score_diff, period, time_remaining_minutes):
        """Get comeback probability for current game state"""
        
        # Cap score differential at 4+ for lookup
        lookup_diff = min(score_diff, 4)
        
        # Determine period key
        if period <= 1:
            period_key = 'p1'
        elif period <= 2:
            period_key = 'p2'
        else:
            period_key = 'p3'
        
        # Get base comeback rate
        base_rate = self.comeback_rates[lookup_diff][period_key]
        
        # Adjust for time remaining (less time = lower comeback chance)
        if period_key == 'p3':
            # In period 3, adjust based on time remaining
            if time_remaining_minutes > 15:
                time_factor = 1.0
            elif time_remaining_minutes > 10:
                time_factor = 0.8
            elif time_remaining_minutes > 5:
                time_factor = 0.6
            else:
                time_factor = 0.3
            
            base_rate *= time_factor
        
        return base_rate
    
    def analyze_current_game_state(self, away_score, home_score, period, time_remaining_minutes):
        """Analyze current game state for comeback probability"""
        
        # Determine trailing team and score differential
        if away_score > home_score:
            score_diff = away_score - home_score
            trailing_team = "home"
            leading_team = "away"
        elif home_score > away_score:
            score_diff = home_score - away_score
            trailing_team = "away"
            leading_team = "home"
        else:
            return None  # Tied game
        
        # Only analyze significant deficits
        if score_diff < 2:
            return None
        
        # Get comeback probability
        comeback_prob = self.get_comeback_probability(
            score_diff, period, time_remaining_minutes
        )
        
        return {
            'away_score': away_score,
            'home_score': home_score,
            'score_diff': score_diff,
            'period': period,
            'time_remaining_minutes': time_remaining_minutes,
            'trailing_team': trailing_team,
            'leading_team': leading_team,
            'comeback_probability': comeback_prob
        }

if __name__ == "__main__":
    analyzer = SimpleGameStateAnalyzer()
    
    # Test scenarios
    print("Testing comeback probabilities:")
    
    # VAN leading 4-1 in period 2 with 10 minutes left
    state = analyzer.analyze_current_game_state(4, 1, 2, 10)
    if state:
        print(f"VAN 4-1 WSH (P2, 10min): WSH comeback prob = {state['comeback_probability']:.1%}")
    
    # VAN leading 3-0 in period 1 with 15 minutes left  
    state = analyzer.analyze_current_game_state(3, 0, 1, 15)
    if state:
        print(f"VAN 3-0 WSH (P1, 15min): WSH comeback prob = {state['comeback_probability']:.1%}")
    
    # VAN leading 2-1 in period 3 with 5 minutes left
    state = analyzer.analyze_current_game_state(2, 1, 3, 5)
    if state:
        print(f"VAN 2-1 WSH (P3, 5min): WSH comeback prob = {state['comeback_probability']:.1%}")
