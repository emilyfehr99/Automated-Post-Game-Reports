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
        feat = {
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
        # Add goalie and recent form if available
        if 'away_goalie_perf' in metrics and 'home_goalie_perf' in metrics:
            feat['goalie_perf_diff'] = float(metrics.get('away_goalie_perf', 0.0)) - float(metrics.get('home_goalie_perf', 0.0))
        if 'recent_form_diff' in metrics:
            feat['recent_form_diff'] = float(metrics.get('recent_form_diff', 0.0))
        # Add venue win percentage difference (replaces generic home ice advantage)
        if 'away_venue_win_pct' in metrics and 'home_venue_win_pct' in metrics:
            feat['venue_win_pct_diff'] = float(metrics.get('away_venue_win_pct', 0.5)) - float(metrics.get('home_venue_win_pct', 0.5))
        return feat

    def _score(self, feats: Dict[str, float]) -> float:
        s = self.bias
        for k, w in self.weights.items():
            v = feats.get(k, 0.0)
            # Simple scale for percentage-like features to similar magnitude
            if k in ('power_play_diff','corsi_diff','faceoff_diff'):
                v = v / 10.0
            # Reduce GS weight (was over-weighted in misses)
            if k == 'gs_diff':
                v = v * 0.5  # Reduce GS influence by 50%
            s += w * v
        # Use venue-specific win percentage difference instead of generic home ice advantage
        # This accounts for teams that are actually bad at home or good on the road
        venue_win_pct_diff = feats.get('venue_win_pct_diff', 0.0)
        if venue_win_pct_diff != 0.0:
            # Weight venue win% difference: positive = away team better at away than home team at home
            # Scale by 0.5 to account for typical NHL home advantage range
            s += 0.5 * venue_win_pct_diff
        else:
            # Fallback to neutral if no venue data available
            pass
        # Add recent form if available
        recent_form_diff = feats.get('recent_form_diff', 0.0)
        if recent_form_diff != 0.0:
            s += 0.2 * recent_form_diff  # Weight recent form
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
    
    def refit_weights_from_history(self, predictions_file: str = 'win_probability_predictions_v2.json') -> None:
        """Periodically re-fit weights using logistic regression on all completed games.
        This should be called weekly/monthly to ensure weights stay current.
        """
        import json
        from pathlib import Path
        
        pred_file = Path(predictions_file)
        if not pred_file.exists():
            return
        
        with open(pred_file, 'r') as f:
            data = json.load(f)
        
        completed = [p for p in data.get('predictions', []) if p.get('actual_winner')]
        if len(completed) < 20:  # Need minimum samples
            return
        
        # Build feature matrix and labels
        X = []
        y = []
        for pred in completed:
            metrics = pred.get('metrics_used', {})
            if not metrics:
                continue
            feats = self._feature_row_from_metrics(metrics)
            X.append([feats.get(k, 0.0) for k in self.feature_keys])
            # Normalize label
            actual = pred.get('actual_winner')
            away = (pred.get('away_team') or '').upper()
            home = (pred.get('home_team') or '').upper()
            if actual in ('away', away):
                y.append(1.0)
            elif actual in ('home', home):
                y.append(0.0)
            else:
                continue
        
        if len(X) < 20:
            return
        
        # Simple batch gradient descent (logistic regression)
        # Initialize from current weights
        weights_vec = np.array([self.weights.get(k, 0.0) for k in self.feature_keys])
        bias_val = self.bias
        X_arr = np.array(X)
        y_arr = np.array(y)
        
        # Scale percentage features
        for i, k in enumerate(self.feature_keys):
            if k in ('power_play_diff','corsi_diff','faceoff_diff'):
                X_arr[:, i] = X_arr[:, i] / 10.0
            if k == 'gs_diff':
                X_arr[:, i] = X_arr[:, i] * 0.5  # Apply GS reduction
        
        # Gradient descent
        lr = 0.01
        epochs = 100
        for epoch in range(epochs):
            scores = X_arr @ weights_vec + bias_val
            probs = 1.0 / (1.0 + np.exp(-np.clip(scores, -500, 500)))
            err = probs - y_arr
            grad_weights = X_arr.T @ err / len(X_arr)
            grad_bias = np.mean(err)
            weights_vec -= lr * grad_weights
            bias_val -= lr * grad_bias
        
        # Update weights
        for i, k in enumerate(self.feature_keys):
            self.weights[k] = float(weights_vec[i])
        self.bias = float(bias_val)
        self._save()
        print(f"✅ Re-fitted correlation weights from {len(X)} completed games")


