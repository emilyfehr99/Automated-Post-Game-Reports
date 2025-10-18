"""
Self-Learning Model Integration
Integrates the self-learning model with the existing GitHub Actions workflow
Runs alongside the current post-game reports without affecting them
"""

import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from nhl_api_client import NHLAPIClient
from self_learning_model import SelfLearningWinProbabilityModel


def run_self_learning_update():
    """
    Run the self-learning model update
    This can be called from the GitHub Actions workflow
    """
    print("🧠 SELF-LEARNING MODEL - DAILY UPDATE")
    print("=" * 50)
    
    try:
        # Initialize the model
        model = SelfLearningWinProbabilityModel()
        
        # Process completed games from yesterday
        model.process_completed_games()
        
        # Retrain model if we have enough data
        model.retrain_model()
        
        # Show current stats
        stats = model.get_model_stats()
        print(f"\n📊 Model Statistics:")
        print(f"   - Total predictions: {stats['total_predictions']}")
        print(f"   - Completed predictions: {stats['completed_predictions']}")
        print(f"   - Average accuracy: {stats['average_accuracy']:.3f}")
        
        print("✅ Self-learning model update completed!")
        
    except Exception as e:
        print(f"❌ Error in self-learning model update: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_self_learning_update()
