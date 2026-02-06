#!/usr/bin/env python3
"""
Compare pure correlation model vs 70/30 correlation+ensemble blend
on the same set of completed games.
"""
import json
from pathlib import Path

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
from correlation_model import CorrelationModel

PRED_FILE = Path('win_probability_predictions_v2.json')


def main():
    if not PRED_FILE.exists():
        print('No predictions file')
        return
    
    with open(PRED_FILE, 'r') as f:
        data = json.load(f)
    
    preds = [p for p in data.get('predictions', []) if p.get('actual_winner')]
    if not preds:
        print('No completed predictions')
        return
    
    model = ImprovedSelfLearningModelV2()
    model.deterministic = True
    corr_model = CorrelationModel()
    
    pure_corr_correct = 0
    blend_correct = 0
    total = 0
    
    for p in preds:
        away = p.get('away_team')
        home = p.get('home_team')
        actual = p.get('actual_winner')
        date = p.get('date')
        metrics = p.get('metrics_used', {})
        
        if not away or not home or not actual:
            continue
        
        # Normalize actual label
        label = None
        if actual in ('away', away):
            label = 'away'
        elif actual in ('home', home):
            label = 'home'
        else:
            continue
        
        # Pure correlation model
        corr_pred = corr_model.predict_from_metrics(metrics)
        corr_away_prob = corr_pred.get('away_prob', 0.5)
        corr_pred_label = 'away' if corr_away_prob >= 0.5 else 'home'
        
        # Ensemble model
        try:
            ens_pred = model.ensemble_predict(away, home, game_date=date)
            ens_away_prob = ens_pred.get('away_prob', 0.5)
            ens_pred_label = 'away' if ens_away_prob >= 0.5 else 'home'
        except Exception:
            ens_away_prob = 0.5
            ens_pred_label = 'home'
        
        # 70/30 blend
        blend_away_prob = 0.7 * corr_away_prob + 0.3 * ens_away_prob
        blend_pred_label = 'away' if blend_away_prob >= 0.5 else 'home'
        
        total += 1
        pure_corr_correct += 1 if corr_pred_label == label else 0
        blend_correct += 1 if blend_pred_label == label else 0
    
    if total == 0:
        print('No comparable games')
        return
    
    print(f"Test set: {total} completed games")
    print(f"\nPure Correlation Model:")
    print(f"  Accuracy: {pure_corr_correct/total:.3f} ({pure_corr_correct}/{total})")
    print(f"\n70/30 Blend (Correlation/Ensemble):")
    print(f"  Accuracy: {blend_correct/total:.3f} ({blend_correct}/{total})")
    
    if blend_correct > pure_corr_correct:
        print(f"\n✅ Blend is better by {blend_correct - pure_corr_correct} games ({100*(blend_correct-pure_corr_correct)/total:.1f}%)")
    elif pure_corr_correct > blend_correct:
        print(f"\n✅ Pure correlation is better by {pure_corr_correct - blend_correct} games ({100*(pure_corr_correct-blend_correct)/total:.1f}%)")
    else:
        print("\n✅ Both models tied")


if __name__ == '__main__':
    main()

