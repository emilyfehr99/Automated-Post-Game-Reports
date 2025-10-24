#!/usr/bin/env python3
"""
Manual Live Game Predictor - For when you know the game details
"""

from improved_self_learning_model import ImprovedSelfLearningModel

class ManualLivePredictor:
    def __init__(self):
        self.model = ImprovedSelfLearningModel()
    
    def predict_with_score(self, away_team, home_team, away_score=0, home_score=0, period=1, time_remaining="20:00"):
        """Get prediction with current game state"""
        
        print(f"🏒 LIVE GAME PREDICTION")
        print("="*50)
        print(f"Game: {away_team} @ {home_team}")
        print(f"Current Score: {away_team} {away_score} - {home_score} {home_team}")
        print(f"Period: {period}, Time: {time_remaining}")
        print("-"*50)
        
        # Get base prediction
        prediction = self.model.predict_game(away_team, home_team)
        
        # Adjust based on current score
        adjusted_prediction = self.adjust_for_current_score(
            prediction, away_team, home_team, away_score, home_score, period, time_remaining
        )
        
        return adjusted_prediction
    
    def adjust_for_current_score(self, base_prediction, away_team, home_team, away_score, home_score, period, time_remaining):
        """Adjust prediction based on current game state"""
        
        away_prob = base_prediction.get('away_prob', 50)
        home_prob = base_prediction.get('home_prob', 50)
        
        # Calculate score differential
        score_diff = away_score - home_score
        
        # Time remaining in game (rough estimate)
        if period == 1:
            time_left = 40  # 2 periods left
        elif period == 2:
            time_left = 20  # 1 period left
        elif period == 3:
            time_left = 5   # Less than 1 period
        else:
            time_left = 1   # Overtime
            
        # Adjust probabilities based on score and time
        if score_diff > 0:  # Away team leading
            # Leading team gets boost, but less as time runs out
            boost = (score_diff * 5) * (time_left / 40)
            away_prob += boost
            home_prob -= boost
        elif score_diff < 0:  # Home team leading
            boost = (abs(score_diff) * 5) * (time_left / 40)
            home_prob += boost
            away_prob -= boost
        
        # Ensure probabilities stay within reasonable bounds
        away_prob = max(5, min(95, away_prob))
        home_prob = max(5, min(95, home_prob))
        
        # Normalize to 100%
        total = away_prob + home_prob
        away_prob = (away_prob / total) * 100
        home_prob = (home_prob / total) * 100
        
        return {
            'away_team': away_team,
            'home_team': home_team,
            'away_prob': away_prob,
            'home_prob': home_prob,
            'away_score': away_score,
            'home_score': home_score,
            'period': period,
            'time_remaining': time_remaining,
            'base_prediction': base_prediction
        }
    
    def display_prediction(self, result):
        """Display the prediction results"""
        print(f"📊 LIVE WIN PROBABILITY:")
        print(f"   {result['away_team']}: {result['away_prob']:.1f}%")
        print(f"   {result['home_team']}: {result['home_prob']:.1f}%")
        
        # Determine favorite
        if result['away_prob'] > result['home_prob']:
            favorite = result['away_team']
            favorite_prob = result['away_prob']
        else:
            favorite = result['home_team']
            favorite_prob = result['home_prob']
            
        print(f"\n🎯 CURRENT FAVORITE: {favorite} ({favorite_prob:.1f}%)")
        
        # Show base prediction for comparison
        base = result['base_prediction']
        print(f"\n📈 BASE PREDICTION (pre-game):")
        print(f"   {result['away_team']}: {base.get('away_prob', 50):.1f}%")
        print(f"   {result['home_team']}: {base.get('home_prob', 50):.1f}%")
        
        # Show adjustments
        away_change = result['away_prob'] - base.get('away_prob', 50)
        home_change = result['home_prob'] - base.get('home_prob', 50)
        
        if abs(away_change) > 1:
            print(f"\n🔄 ADJUSTMENTS DUE TO CURRENT SCORE:")
            print(f"   {result['away_team']}: {away_change:+.1f}%")
            print(f"   {result['home_team']}: {home_change:+.1f}%")
        
        print("="*50)

def main():
    """Interactive manual predictor"""
    predictor = ManualLivePredictor()
    
    print("🏒 Manual Live Game Predictor")
    print("="*40)
    print("Enter game details to get live win probability")
    print()
    
    try:
        # Get team names
        away_team = input("Away team (e.g., WSH): ").strip().upper()
        home_team = input("Home team (e.g., VAN): ").strip().upper()
        
        # Get current score
        away_score = int(input(f"{away_team} current score: ") or "0")
        home_score = int(input(f"{home_team} current score: ") or "0")
        
        # Get period
        period = int(input("Current period (1, 2, 3, OT): ") or "1")
        
        # Get time remaining
        time_remaining = input("Time remaining in period (e.g., 15:30): ").strip() or "20:00"
        
        print()
        
        # Get prediction
        result = predictor.predict_with_score(away_team, home_team, away_score, home_score, period, time_remaining)
        predictor.display_prediction(result)
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
