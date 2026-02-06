#!/usr/bin/env python3
"""
Test meta-ensemble with different confidence thresholds
"""
import json
from meta_ensemble_predictor import MetaEnsemblePredictor

def test_threshold(threshold, games):
    """Test accuracy at given confidence threshold"""
    meta = MetaEnsemblePredictor()
    
    all_correct = 0
    all_total = 0
    hc_correct = 0
    hc_total = 0
    
    for game in games:
        try:
            pred = meta.predict(
                game['away_team'],
                game['home_team'],
                game_date=game.get('date')
            )
            
            predicted_winner = 'away' if pred['away_prob'] > pred['home_prob'] else 'home'
            actual_winner = game['actual_winner'].lower()
            is_correct = (predicted_winner == actual_winner)
            
            all_total += 1
            if is_correct:
                all_correct += 1
            
            # Check if meets threshold
            if meta.should_predict(pred, confidence_threshold=threshold):
                hc_total += 1
                if is_correct:
                    hc_correct += 1
                    
        except:
            continue
    
    all_acc = (all_correct / all_total * 100) if all_total > 0 else 0
    hc_acc = (hc_correct / hc_total * 100) if hc_total > 0 else 0
    coverage = (hc_total / all_total * 100) if all_total > 0 else 0
    
    return {
        'threshold': threshold,
        'all_accuracy': all_acc,
        'hc_accuracy': hc_acc,
        'coverage': coverage,
        'hc_correct': hc_correct,
        'hc_total': hc_total
    }

if __name__ == "__main__":
    # Load test games
    with open('data/win_probability_predictions_v2.json', 'r') as f:
        data = json.load(f)
        predictions = data.get('predictions', [])
    
    completed = [p for p in predictions if p.get('actual_winner')]
    test_games = completed[-100:]
    
    print("🎯 Meta-Ensemble Threshold Optimization")
    print("=" * 70)
    print(f"Testing on {len(test_games)} games\n")
    
    # Test different thresholds
    thresholds = [0.45, 0.50, 0.55, 0.60, 0.65, 0.70]
    results = []
    
    for threshold in thresholds:
        print(f"Testing threshold: {threshold:.0%}...", end=" ")
        result = test_threshold(threshold, test_games)
        results.append(result)
        print(f"✓ {result['hc_accuracy']:.1f}% accuracy, {result['coverage']:.1f}% coverage")
    
    print("\n" + "=" * 70)
    print("📊 RESULTS SUMMARY")
    print("=" * 70)
    print(f"{'Threshold':<12} {'Accuracy':<12} {'Coverage':<12} {'Games':<12}")
    print("-" * 70)
    
    for r in results:
        threshold_str = f"{r['threshold']:.0%}"
        accuracy_str = f"{r['hc_accuracy']:.1f}%"
        coverage_str = f"{r['coverage']:.1f}%"
        games_str = f"{r['hc_correct']}/{r['hc_total']}"
        print(f"{threshold_str:<12} {accuracy_str:<12} {coverage_str:<12} {games_str}")

    
    # Find optimal threshold (best accuracy * coverage)
    best = max(results, key=lambda x: x['hc_accuracy'] * x['coverage'])
    
    print("\n" + "=" * 70)
    print("🏆 OPTIMAL THRESHOLD")
    print("=" * 70)
    print(f"Threshold: {best['threshold']:.0%}")
    print(f"Accuracy: {best['hc_accuracy']:.1f}%")
    print(f"Coverage: {best['coverage']:.1f}%")
    print(f"Games Predicted: {best['hc_total']}/{len(test_games)}")
    print(f"Score (Accuracy × Coverage): {best['hc_accuracy'] * best['coverage'] / 100:.1f}")
