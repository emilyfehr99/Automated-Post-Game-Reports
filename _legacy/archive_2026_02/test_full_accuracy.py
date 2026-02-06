#!/usr/bin/env python3
"""
Comprehensive Accuracy Test
Tests the complete model stack with all Phase 1-5A features enabled
"""
import json
from meta_ensemble_predictor import MetaEnsemblePredictor
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

def load_historical_games(n=100):
    """Load last N completed games"""
    with open('data/win_probability_predictions_v2.json', 'r') as f:
        data = json.load(f)
        predictions = data.get('predictions', [])
        
    # Filter completed games
    completed = [p for p in predictions if p.get('actual_winner')]
    return completed[-n:]

def test_meta_ensemble_accuracy(games):
    """Test meta-ensemble on historical games"""
    meta = MetaEnsemblePredictor()
    
    correct = 0
    total = 0
    high_confidence_correct = 0
    high_confidence_total = 0
    
    print("Testing meta-ensemble on historical games...")
    print("=" * 60)
    
    for i, game in enumerate(games, 1):
        away = game['away_team']
        home = game['home_team']
        actual_winner_raw = game['actual_winner'].lower()  # 'home' or 'away'
        
        try:
            # Make prediction
            pred = meta.predict(away, home, game_date=game.get('date'))
            
            # Determine predicted winner as 'home' or 'away'
            predicted_winner = 'away' if pred['away_prob'] > pred['home_prob'] else 'home'
            
            # Check if correct
            is_correct = (predicted_winner == actual_winner_raw)
            
            total += 1
            if is_correct:
                correct += 1
            
            # Track high-confidence predictions
            if meta.should_predict(pred, confidence_threshold=0.60):
                high_confidence_total += 1
                if is_correct:
                    high_confidence_correct += 1
            
            if i % 10 == 0:
                print(f"Processed {i}/{len(games)} games...")
                
        except Exception as e:
            print(f"Error on game {i}: {e}")
            continue
    
    overall_accuracy = (correct / total * 100) if total > 0 else 0
    hc_accuracy = (high_confidence_correct / high_confidence_total * 100) if high_confidence_total > 0 else 0
    
    print(f"\n📊 Results:")
    print(f"  Overall Accuracy: {overall_accuracy:.1f}% ({correct}/{total})")
    print(f"  High-Confidence (>60%) Accuracy: {hc_accuracy:.1f}% ({high_confidence_correct}/{high_confidence_total})")
    print(f"  High-Confidence Coverage: {high_confidence_total/total*100:.1f}% of games")
    
    return {
        'overall_accuracy': overall_accuracy,
        'high_confidence_accuracy': hc_accuracy,
        'coverage': high_confidence_total / total if total > 0 else 0
    }

def test_base_model_accuracy(games):
    """Test baseline model for comparison"""
    model = ImprovedSelfLearningModelV2()
    
    correct = 0
    total = 0
    
    print("\nTesting baseline model for comparison...")
    print("=" * 60)
    
    for i, game in enumerate(games, 1):
        away = game['away_team']
        home = game['home_team']
        actual_winner_raw = game['actual_winner'].lower()  # 'home' or 'away'
        
        try:
            pred = model.predict_game(away, home, game_date=game.get('date'))
            predicted_winner = 'away' if pred['away_prob'] > pred['home_prob'] else 'home'
            
            if predicted_winner == actual_winner_raw:
                correct += 1
            total += 1
            
        except Exception as e:
            continue
    
    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"  Baseline Accuracy: {accuracy:.1f}% ({correct}/{total})")
    
    return accuracy

if __name__ == "__main__":
    print("🎯 Comprehensive Accuracy Test")
    print("=" * 60)
    print("\nLoading historical games...")
    
    games = load_historical_games(n=100)
    print(f"Loaded {len(games)} completed games\n")
    
    # Test baseline
    baseline = test_base_model_accuracy(games)
    
    # Test meta-ensemble
    meta_results = test_meta_ensemble_accuracy(games)
    
    print(f"\n" + "=" * 60)
    print("📈 IMPROVEMENT SUMMARY")
    print("=" * 60)
    print(f"Baseline Model: {baseline:.1f}%")
    print(f"Meta-Ensemble (All Games): {meta_results['overall_accuracy']:.1f}%")
    print(f"Meta-Ensemble (High-Confidence): {meta_results['high_confidence_accuracy']:.1f}%")
    print(f"\nImprovement: {meta_results['overall_accuracy'] - baseline:+.1f}%")
    print(f"High-Confidence Improvement: {meta_results['high_confidence_accuracy'] - baseline:+.1f}%")
