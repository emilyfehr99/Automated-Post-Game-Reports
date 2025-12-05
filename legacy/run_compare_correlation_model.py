#!/usr/bin/env python3
"""
Compare accuracy of current ensemble model vs a correlation-weighted model
on the same set of completed games in win_probability_predictions_v2.json.
"""
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

PRED_FILE = Path('win_probability_predictions_v2.json')

# Correlation results captured from latest analysis (component -> correlation)
CORR_WEIGHTS = {
    'gs_diff': 0.4614,
    'power_play_diff': 0.3213,
    'blocked_shots_diff': -0.2931,
    'corsi_diff': -0.2659,
    'hits_diff': -0.1374,
    'rest_diff': 0.1023,
    'hdc_diff': 0.0759,
    'shots_diff': -0.0744,
    'giveaways_diff': -0.0427,
    'sos_diff': -0.0390,
    'takeaways_diff': 0.0334,
    'xg_diff': -0.0274,
    'pim_diff': 0.0160,
    'faceoff_diff': -0.0118,
}


def sigmoid(x: float) -> float:
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def build_feature_row(metrics: Dict) -> Dict[str, float]:
    # Build away-home diffs from stored metrics
    return {
        'gs_diff': float(metrics.get('away_gs', 0.0)) - float(metrics.get('home_gs', 0.0)),
        'power_play_diff': float(metrics.get('away_power_play_pct', 0.0)) - float(metrics.get('home_power_play_pct', 0.0)),
        'blocked_shots_diff': float(metrics.get('away_blocked_shots', 0.0)) - float(metrics.get('home_blocked_shots', 0.0)),
        'corsi_diff': float(metrics.get('away_corsi_pct', 50.0)) - float(metrics.get('home_corsi_pct', 50.0)),
        'hits_diff': float(metrics.get('away_hits', 0.0)) - float(metrics.get('home_hits', 0.0)),
        'rest_diff': float(metrics.get('away_rest', 0.0)) - float(metrics.get('home_rest', 0.0)),
        'hdc_diff': float(metrics.get('away_hdc', 0.0)) - float(metrics.get('home_hdc', 0.0)),
        'shots_diff': float(metrics.get('away_shots', 0.0)) - float(metrics.get('home_shots', 0.0)),
        'giveaways_diff': float(metrics.get('away_giveaways', 0.0)) - float(metrics.get('home_giveaways', 0.0)),
        'sos_diff': float(metrics.get('away_sos', 0.0)) - float(metrics.get('home_sos', 0.0)),
        'takeaways_diff': float(metrics.get('away_takeaways', 0.0)) - float(metrics.get('home_takeaways', 0.0)),
        'xg_diff': float(metrics.get('away_xg', 0.0)) - float(metrics.get('home_xg', 0.0)),
        'pim_diff': float(metrics.get('away_penalty_minutes', 0.0)) - float(metrics.get('home_penalty_minutes', 0.0)),
        'faceoff_diff': float(metrics.get('away_faceoff_pct', 50.0)) - float(metrics.get('home_faceoff_pct', 50.0)),
    }


def correlation_score(feat: Dict[str, float]) -> float:
    # Normalize feature scales crudely: z-score by robust scale per component across dataset later
    # For quick approach, just weighted sum using correlation weights (signed) and small scaling
    s = 0.0
    for k, w in CORR_WEIGHTS.items():
        v = feat.get(k, 0.0)
        # scale to reduce extreme influence; many metrics are in small ranges already
        s += w * (v / (10.0 if k in ('power_play_diff','corsi_diff','faceoff_diff') else 1.0))
    return s


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

    # Evaluate both models on the same sample
    total = 0
    ens_correct = 0
    corr_correct = 0
    for p in preds:
        away = p.get('away_team')
        home = p.get('home_team')
        actual = p.get('actual_winner')
        date = p.get('date')
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

        # Ensemble prediction
        ens = model.ensemble_predict(away, home, game_date=date)
        ens_pred = 'away' if ens.get('away_prob', 0.5) > ens.get('home_prob', 0.5) else 'home'

        # Correlation model prediction
        feats = build_feature_row(p.get('metrics_used') or {})
        s = correlation_score(feats)
        pr_away = sigmoid(s)
        corr_pred = 'away' if pr_away >= 0.5 else 'home'

        total += 1
        ens_correct += 1 if ens_pred == label else 0
        corr_correct += 1 if corr_pred == label else 0

    if total == 0:
        print('No comparable games')
        return

    print(f"Samples: {total}")
    print(f"Ensemble accuracy: {ens_correct/total:.3f} ({ens_correct}/{total})")
    print(f"Correlation-model accuracy: {corr_correct/total:.3f} ({corr_correct}/{total})")


if __name__ == '__main__':
    main()


