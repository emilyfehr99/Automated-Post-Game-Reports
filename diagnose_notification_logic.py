
import os
import sys
import logging
from prediction_interface import PredictionInterface

# Configure logging to show everything
logging.basicConfig(level=logging.INFO)

def diagnose():
    print("🔍 DIAGNOSING NOTIFICATION LOGIC...")
    
    # Initialize Predictor
    try:
        pi = PredictionInterface()
        print("✅ PredictionInterface initialized")
    except Exception as e:
        print(f"❌ Failed to init PredictionInterface: {e}")
        return

    # Call the suspect method
    print("\n👉 Calling get_daily_predictions() [Used by Notifier]...")
    try:
        # We need to ensure we have a valid environment (Team Stats, Schedule)
        # We verified 'data/season_2025_2026_schedule.json' exists locally.
        
        predictions = pi.get_daily_predictions()
        
        print(f"\n📊 Generated {len(predictions)} predictions:")
        
        for i, p in enumerate(predictions):
            print(f"\n--- Game {i+1}: {p['away_team']} @ {p['home_team']} ---")
            print(f"   Score: {p['away_team']} {p['away_score']} - {p['home_score']} {p['home_team']}")
            print(f"   Confidence: {p['confidence']:.1f}%")
            print(f"   Volatility: {p['volatility']}")
            print(f"   Reasoning: {p.get('reasoning')}")
            
            # Check for 4-3 pattern
            if (p['away_score'] == 4 and p['home_score'] == 3) or \
               (p['away_score'] == 3 and p['home_score'] == 4):
                 print("   ⚠️  Result is 4-3")
            else:
                 print("   ✅  Result is VARIED")
                 
    except Exception as e:
        print(f"❌ Error during get_daily_predictions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose()
