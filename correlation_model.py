#!/usr/bin/env python3
from __future__ import annotations
"""
Correlation-weighted model with online updates.
Trains weights from historical completed predictions and predicts pre-game using
team averages and situational features (rest, goalie_perf, SOS).
"""
import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

CORR_MODEL_FILE = Path('correlation_model_weights.json')


def sigmoid(x: float) -> float:
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


class CorrelationModel:
    def __init__(self, model_path: Path = CORR_MODEL_FILE):
        self.model_path = model_path
        self.weights: Dict[str, float] = {}
        self.bias: float = 0.0
        self.feature_keys: List[str] = [
            'gs_diff','power_play_diff','blocked_shots_diff','corsi_diff','hits_diff',
            'rest_diff','hdc_diff','shots_diff','giveaways_diff','sos_diff',
            'takeaways_diff','xg_diff','pim_diff','faceoff_diff'
        ]
        self._load()

    def _load(self) -> None:
        if self.model_path.exists():
            try:
                obj = json.load(open(self.model_path, 'r'))
                self.weights = obj.get('weights', {})
                self.bias = float(obj.get('bias', 0.0))
                return
            except Exception:
                pass
        # Defaults from last correlation ranking as priors
        self.weights = {
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
        self.bias = 0.0

    def _save(self) -> None:
        try:
            json.dump({'weights': self.weights, 'bias': self.bias}, open(self.model_path, 'w'), indent=2)
        except Exception:
            pass

    def _feature_row_from_metrics(self, metrics: Dict) -> Dict[str, float]:
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

    def _score(self, feats: Dict[str, float]) -> float:
        s = self.bias
        for k, w in self.weights.items():
            v = feats.get(k, 0.0)
            # Simple scale for percentage-like features to similar magnitude
            if k in ('power_play_diff','corsi_diff','faceoff_diff'):
                v = v / 10.0
            s += w * v
        return s

    def predict_from_metrics(self, metrics: Dict) -> Dict[str, float]:
        feats = self._feature_row_from_metrics(metrics)
        s = self._score(feats)
        p_away = sigmoid(s)
        p_home = 1.0 - p_away
        return {'away_prob': p_away, 'home_prob': p_home}

    def online_update(self, metrics: Dict, actual_label: str, lr: float = 0.01) -> None:
        """One-step logistic regression update from a single game.
        actual_label: 'away' or 'home'.
        """
        y = 1.0 if actual_label == 'away' else 0.0
        feats = self._feature_row_from_metrics(metrics)
        s = self._score(feats)
        p = sigmoid(s)
        # Gradient descent update
        err = (p - y)
        for k in self.feature_keys:
            g = feats.get(k, 0.0)
            if k in ('power_play_diff','corsi_diff','faceoff_diff'):
                g = g / 10.0
            self.weights[k] = self.weights.get(k, 0.0) - lr * err * g
        self.bias = self.bias - lr * err
        self._save()


