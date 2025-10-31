#!/usr/bin/env python3
import json
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

def fmt(p):
    return None if p is None else (f"{p:.3f}")

def run(n=60):
    model = ImprovedSelfLearningModelV2()
    model.deterministic = True

    # Baseline: before features (disable per-goalie GSAX and rest-bucket adj)
    model.feature_flags['use_per_goalie_gsax'] = False
    model.feature_flags['use_rest_bucket_adj'] = False
    before = model.backtest_recent_recompute(n)

    # After: enable features
    model.feature_flags['use_per_goalie_gsax'] = True
    model.feature_flags['use_rest_bucket_adj'] = True
    after = model.backtest_recent_recompute(n)

    result = {
        'samples': before.get('samples'),
        'before': {
            'accuracy': before.get('accuracy'),
            'brier': before.get('brier'),
            'log_loss': before.get('log_loss'),
        },
        'after': {
            'accuracy': after.get('accuracy'),
            'brier': after.get('brier'),
            'log_loss': after.get('log_loss'),
        }
    }

    print("Comparative Backtest (last {} completed games)".format(result['samples']))
    print("Before  - acc:", fmt(result['before']['accuracy']), "brier:", fmt(result['before']['brier']), "logloss:", fmt(result['before']['log_loss']))
    print("After   - acc:", fmt(result['after']['accuracy']),  "brier:", fmt(result['after']['brier']),  "logloss:", fmt(result['after']['log_loss']))

if __name__ == "__main__":
    run(60)
