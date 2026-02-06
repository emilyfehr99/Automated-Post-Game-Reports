"""
Model Monitoring Demo
Shows how the self-learning model continuously improves predictions
"""

from self_learning_model import SelfLearningModel
import json

def main():
    print("🧠 SELF-LEARNING MODEL MONITORING DEMO")
    print("=" * 50)
    
    # Initialize the model
    model = SelfLearningModel()
    
    # Show current model state
    print("\n📊 CURRENT MODEL STATE:")
    weights = model.get_current_weights()
    perf = model.get_model_performance()
    
    print(f"Model Weights:")
    for metric, weight in weights.items():
        print(f"  {metric}: {weight:.3f}")
    
    print(f"\nModel Performance:")
    print(f"  Total Games: {perf['total_games']}")
    print(f"  Accuracy: {perf['accuracy']:.3f}")
    print(f"  Recent Accuracy: {perf['recent_accuracy']:.3f}")
    
    # Show recent predictions
    recent = model.get_recent_predictions(days=7)
    print(f"\n📈 RECENT PREDICTIONS (Last 7 days): {len(recent)} games")
    
    if recent:
        for pred in recent[-5:]:  # Show last 5
            winner = pred.get('actual_winner', 'TBD')
            away_prob = pred['predicted_away_win_prob']
            home_prob = pred['predicted_home_win_prob']
            accuracy = pred.get('prediction_accuracy', 'N/A')
            
            print(f"  {pred['away_team']} @ {pred['home_team']}: {away_prob:.1f}% vs {home_prob:.1f}% | Winner: {winner} | Accuracy: {accuracy}")
    
    # Show model analysis
    analysis = model.analyze_model_performance()
    print(f"\n🔍 MODEL ANALYSIS:")
    print(f"  Total Predictions: {analysis['total_predictions']}")
    print(f"  Overall Accuracy: {analysis['overall_accuracy']:.3f}")
    
    if analysis.get('team_accuracy'):
        print(f"\n📊 TEAM ACCURACY (Top 5):")
        sorted_teams = sorted(analysis['team_accuracy'].items(), key=lambda x: x[1], reverse=True)
        for team, acc in sorted_teams[:5]:
            print(f"  {team}: {acc:.3f}")
    
    if analysis.get('confidence_accuracy'):
        print(f"\n🎯 CONFIDENCE ACCURACY:")
        for bucket, acc in analysis['confidence_accuracy'].items():
            print(f"  {bucket}: {acc:.3f}")
    
    # Show how the model will update
    print(f"\n🔄 MODEL UPDATE PROCESS:")
    print("  1. ✅ GitHub Actions runs every 10 minutes")
    print("  2. 🏒 Processes completed games")
    print("  3. 🧠 Learns from actual outcomes")
    print("  4. 📊 Updates model weights based on accuracy")
    print("  5. 💾 Saves improved model for next predictions")
    
    print(f"\n📈 EXPECTED IMPROVEMENTS:")
    print("  • Model weights will adjust based on which metrics are most predictive")
    print("  • Game Score (GS) weight will likely increase (as you noted)")
    print("  • Faceoff % weight will likely decrease")
    print("  • Overall prediction accuracy should improve over time")
    
    print(f"\n🎯 NEXT STEPS:")
    print("  • Model will automatically update with each new game")
    print("  • Weights will evolve based on actual performance")
    print("  • Predictions will become more accurate over time")
    print("  • You can monitor progress in the GitHub Actions logs")

if __name__ == "__main__":
    main()
