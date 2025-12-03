#!/usr/bin/env python3
"""
Meta-model demo: train a simple logistic regression on top of existing
predictions to see how much extra accuracy we can squeeze out.

Matches your point #1 (stronger supervised model on top of features),
but keeps it as an offline diagnostic tool so we can compare safely.

Features used (per game):
  - predicted_away_win_prob, predicted_home_win_prob
  - prediction_margin (|away - home|)
  - prediction_confidence (max prob)
  - spread (same as margin)
  - monte_carlo_flip_rate
  - away_prob_score_first, home_prob_score_first (if present)
  - away_first_goal_win_uplift, home_first_goal_win_uplift (if present)

Target:
  - y = 1 if home team wins, 0 otherwise.

We do a time-aware split: train on first 70% of games, test on last 30%.

Usage:
  python meta_model_demo.py
"""

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))


def _load_dataset(path: Path) -> Tuple[List[List[float]], List[int], List[List[float]], List[int]]:
    with path.open("r") as f:
        data = json.load(f)
    preds = data.get("predictions", data)

    rows: List[Dict[str, Any]] = []
    for p in preds:
        if not p.get("actual_winner"):
            continue
        pa = p.get("predicted_away_win_prob")
        ph = p.get("predicted_home_win_prob")
        if pa is None or ph is None:
            continue
        if pa > 1.0 or ph > 1.0:
            pa /= 100.0
            ph /= 100.0
        total = pa + ph
        if total <= 0:
            continue
        pa /= total
        ph /= total

        away = p.get("away_team")
        home = p.get("home_team")
        winner = p.get("actual_winner")
        if winner not in ("away", "home"):
            if winner == away:
                winner = "away"
            elif winner == home:
                winner = "home"
            else:
                continue

        y = 1 if winner == "home" else 0
        flip = float(p.get("monte_carlo_flip_rate", 0.0) or 0.0)
        margin = abs(pa - ph)
        conf = max(pa, ph)
        spread = margin
        mu = p.get("metrics_used") or {}

        # First-goal features (may be missing on older entries)
        away_sf = float(mu.get("away_prob_score_first", 0.5) or 0.5)
        home_sf = float(mu.get("home_prob_score_first", 0.5) or 0.5)
        away_uplift = float(mu.get("away_first_goal_win_uplift", 0.2) or 0.2)
        home_uplift = float(mu.get("home_first_goal_win_uplift", 0.2) or 0.2)

        x = [
            pa,
            ph,
            margin,
            conf,
            spread,
            flip,
            away_sf,
            home_sf,
            away_uplift,
            home_uplift,
        ]
        rows.append({"x": x, "y": y})

    if len(rows) < 50:
        raise SystemExit(f"Not enough completed games with features ({len(rows)})")

    # Time-aware split: first 70% train, last 30% test
    n = len(rows)
    cutoff = int(n * 0.7)
    train = rows[:cutoff]
    test = rows[cutoff:]
    X_train = [r["x"] for r in train]
    y_train = [r["y"] for r in train]
    X_test = [r["x"] for r in test]
    y_test = [r["y"] for r in test]
    return X_train, y_train, X_test, y_test


def _train_logistic(X: List[List[float]], y: List[int], lr: float = 0.05, epochs: int = 800) -> Tuple[List[float], float]:
    n_features = len(X[0])
    w = [0.0] * n_features
    b = 0.0
    n = len(X)
    for epoch in range(epochs):
        grad_w = [0.0] * n_features
        grad_b = 0.0
        for xi, yi in zip(X, y):
            z = sum(wj * xj for wj, xj in zip(w, xi)) + b
            p = _sigmoid(z)
            diff = p - yi  # derivative of log loss
            for j in range(n_features):
                grad_w[j] += diff * xi[j]
            grad_b += diff
        # Average gradients
        for j in range(n_features):
            w[j] -= lr * grad_w[j] / n
        b -= lr * grad_b / n
    return w, b


def _evaluate(X: List[List[float]], y: List[int], w: List[float], b: float) -> Dict[str, float]:
    correct = 0
    brier_sum = 0.0
    ll_sum = 0.0
    for xi, yi in zip(X, y):
        z = sum(wj * xj for wj, xj in zip(w, xi)) + b
        p_home = _sigmoid(z)
        pred = 1 if p_home >= 0.5 else 0
        if pred == yi:
            correct += 1
        brier_sum += (p_home - yi) ** 2
        p_true = min(max(p_home if yi == 1 else 1.0 - p_home, 1e-6), 1.0 - 1e-6)
        ll_sum += -math.log(p_true)
    n = len(y)
    return {
        "n": n,
        "accuracy": correct / n if n else 0.0,
        "brier": brier_sum / n if n else None,
        "log_loss": ll_sum / n if n else None,
    }


def main() -> None:
    path = Path("win_probability_predictions_v2.json")
    if not path.exists():
        print(f"Predictions file not found at {path.resolve()}")
        return

    X_train, y_train, X_test, y_test = _load_dataset(path)
    print(f"Training meta-model on {len(X_train)} games, testing on {len(X_test)} future games.\n")

    # Train simple logistic regression
    w, b = _train_logistic(X_train, y_train)

    # Evaluate
    train_stats = _evaluate(X_train, y_train, w, b)
    test_stats = _evaluate(X_test, y_test, w, b)

    print("=== Meta-model performance (logistic on top of existing features) ===")
    train_brier = f"{train_stats['brier']:.3f}" if train_stats["brier"] is not None else "N/A"
    train_log_loss = f"{train_stats['log_loss']:.3f}" if train_stats["log_loss"] is not None else "N/A"
    test_brier = f"{test_stats['brier']:.3f}" if test_stats["brier"] is not None else "N/A"
    test_log_loss = f"{test_stats['log_loss']:.3f}" if test_stats["log_loss"] is not None else "N/A"
    print(
        f"Train: N={train_stats['n']}, Acc={train_stats['accuracy']:.3f}, "
        f"Brier={train_brier}, LogLoss={train_log_loss}"
    )
    print(
        f"Test : N={test_stats['n']}, Acc={test_stats['accuracy']:.3f}, "
        f"Brier={test_brier}, LogLoss={test_log_loss}"
    )

    print("\nLearned weights (one per feature in order):")
    feature_names = [
        "away_prob",
        "home_prob",
        "margin",
        "confidence",
        "spread",
        "flip_rate",
        "away_prob_score_first",
        "home_prob_score_first",
        "away_first_goal_uplift",
        "home_first_goal_uplift",
    ]
    for name, coef in zip(feature_names, w):
        print(f"  {name:26s}: {coef:+.4f}")
    print(f"  intercept{'':20s}: {b:+.4f}")


if __name__ == "__main__":
    main()


