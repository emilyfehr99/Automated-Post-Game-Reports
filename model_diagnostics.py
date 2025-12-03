#!/usr/bin/env python3
"""
Model diagnostics CLI for the ImprovedSelfLearningModelV2.

Usage:
    python model_diagnostics.py              # default backtest on last 60 games
    python model_diagnostics.py 120          # backtest on last 120 games

Prints:
    - Sample count
    - Accuracy
    - Brier score
    - Log-loss
    - Recent-accuracy window stats
    - Simple Pearson correlations between each scalar metric and home-win outcome
"""

import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Any

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2


def _pearson(pairs: List[Tuple[float, float]]) -> float | None:
    """Compute Pearson correlation for (x, y) pairs."""
    if len(pairs) < 3:
        return None
    xs = [x for x, _ in pairs]
    ys = [y for _, y in pairs]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in pairs)
    denx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    deny = math.sqrt(sum((y - my) ** 2 for y in ys))
    if denx == 0 or deny == 0:
        return None
    return num / (denx * deny)


def _scalarize(value: Any) -> float | None:
    """
    Convert a metric value into a scalar for correlation:
    - numbers -> float
    - lists/tuples -> mean of elements (if numeric)
    - booleans -> 0/1
    - everything else -> None (skip)
    """
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (list, tuple)) and value:
        # Only keep numeric elements
        nums: List[float] = []
        for v in value:
            try:
                nums.append(float(v))
            except (TypeError, ValueError):
                continue
        if not nums:
            return None
        return sum(nums) / len(nums)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def run_backtest(n: int = 60) -> None:
    """Run backtest + simple correlation analysis and print a compact report."""
    model = ImprovedSelfLearningModelV2("win_probability_predictions_v2.json")

    print("=== Backtest (stored probabilities, last n completed games) ===")
    res = model.backtest_recent(n=n)
    print(f"Samples       : {res.get('samples', 0)}")
    print(f"Accuracy      : {res.get('accuracy', 0.0):.3f}")
    print(f"Brier score   : {res.get('brier') if res.get('brier') is not None else 'N/A'}")
    print(f"Log-loss      : {res.get('log_loss') if res.get('log_loss') is not None else 'N/A'}")
    print()

    print("=== Backtest (recomputed with current ensemble, last n completed games) ===")
    res2 = model.backtest_recent_recompute(n=n)
    print(f"Samples       : {res2.get('samples', 0)}")
    print(f"Accuracy      : {res2.get('accuracy', 0.0):.3f}")
    print(f"Brier score   : {res2.get('brier') if res2.get('brier') is not None else 'N/A'}")
    print(f"Log-loss      : {res2.get('log_loss') if res2.get('log_loss') is not None else 'N/A'}")
    print()

    # Load raw predictions JSON to compute simple correlations
    path = Path("win_probability_predictions_v2.json")
    if not path.exists():
        print(f"⚠️  Predictions file not found at {path.resolve()}")
        return

    with path.open("r") as f:
        data = json.load(f)

    preds = data.get("predictions", data)

    metrics_keys: set[str] = set()
    for p in preds:
        mu = p.get("metrics_used") or {}
        metrics_keys.update(mu.keys())

    # Collect (metric_value, home_win) pairs
    metric_pairs: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
    total_completed = 0
    for p in preds:
        winner = p.get("actual_winner")
        away = p.get("away_team")
        home = p.get("home_team")
        if winner and winner not in ("away", "home"):
            if winner == away:
                winner = "away"
            elif winner == home:
                winner = "home"
        if winner not in ("away", "home"):
            continue
        total_completed += 1
        y = 1.0 if winner == "home" else 0.0
        mu = p.get("metrics_used") or {}
        for k in metrics_keys:
            v = _scalarize(mu.get(k))
            if v is None:
                continue
            metric_pairs[k].append((v, y))

    print(f"Completed games with outcome for correlation: {total_completed}")
    print()

    # Compute Pearson correlations
    correlations: List[Tuple[str, float, int]] = []
    for k in sorted(metrics_keys):
        pairs = metric_pairs.get(k, [])
        r = _pearson(pairs)
        if r is None:
            continue
        correlations.append((k, r, len(pairs)))

    # Sort by absolute correlation strength
    correlations.sort(key=lambda x: abs(x[1]), reverse=True)

    print("=== Top 25 metrics by |correlation with home_win| (1=home win, 0=away win) ===")
    for name, r, count in correlations[:25]:
        print(f"{name:28s} r={r: .3f}  samples={count}")


def main() -> None:
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[0 if False else 1])
        except ValueError:
            print(f"Invalid n value: {sys.argv[1]!r}, expected integer")
            sys.exit(1)
    else:
        n = 60

    run_backtest(n=n)


if __name__ == "__main__":
    main()


