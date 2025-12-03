#!/usr/bin/env python3
"""
Context-aware backtest to see how the model performs in different situations.

Matches your point #2 (context-specific submodels), but starts with diagnostics:
  - Accuracy/Brier/log-loss by context_bucket (rest/B2B situation).
  - Accuracy/Brier/log-loss by spread bucket (model confidence).

Usage:
  python context_backtest.py
"""

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any


def _load_predictions(path: Path) -> List[Dict[str, Any]]:
    with path.open("r") as f:
        data = json.load(f)
    preds = data.get("predictions", data)
    cleaned: List[Dict[str, Any]] = []
    for p in preds:
        if not p.get("actual_winner"):
            continue
        pa = p.get("predicted_away_win_prob")
        ph = p.get("predicted_home_win_prob")
        if pa is None or ph is None:
            continue
        if pa > 1.0 or ph > 1.0:
            pa = pa / 100.0
            ph = ph / 100.0
        total = (pa or 0.5) + (ph or 0.5)
        if total <= 0:
            continue
        p["predicted_away_win_prob"] = pa / total
        p["predicted_home_win_prob"] = ph / total
        cleaned.append(p)
    return cleaned


def _bucket_spread(spread: float) -> str:
    # Spread is absolute difference between probs, in [0,1].
    if spread < 0.05:
        return "<5%"
    if spread < 0.10:
        return "5–10%"
    if spread < 0.15:
        return "10–15%"
    if spread < 0.20:
        return "15–20%"
    return ">=20%"


def _eval_group(games: List[Dict[str, Any]]) -> Dict[str, float]:
    if not games:
        return {"n": 0, "accuracy": 0.0, "brier": None, "log_loss": None}
    correct = 0
    brier_sum = 0.0
    ll_sum = 0.0
    n_ll = 0
    for p in games:
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
        pa = float(p.get("predicted_away_win_prob", 0.5))
        ph = float(p.get("predicted_home_win_prob", 0.5))
        total = pa + ph
        if total > 0:
            pa /= total
            ph /= total
        pred_side = "away" if pa > ph else "home"
        if pred_side == winner:
            correct += 1
        y = 1.0 if winner == "away" else 0.0
        brier_sum += (pa - y) ** 2
        p_true = pa if y == 1.0 else ph
        p_true = min(max(p_true, 1e-6), 1.0 - 1e-6)
        ll_sum += -(y * math.log(p_true) + (1.0 - y) * math.log(1.0 - p_true))
        n_ll += 1
    n = len(games)
    return {
        "n": n,
        "accuracy": correct / n if n else 0.0,
        "brier": brier_sum / n if n else None,
        "log_loss": ll_sum / n_ll if n_ll else None,
    }


def main() -> None:
    path = Path("win_probability_predictions_v2.json")
    if not path.exists():
        print(f"Predictions file not found at {path.resolve()}")
        return

    preds = _load_predictions(path)
    print(f"Loaded {len(preds)} completed games with valid probabilities.\n")

    # --- Context bucket performance ---
    by_context: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for p in preds:
        bucket = p.get("context_bucket") or "neutral"
        by_context[bucket].append(p)

    print("=== Performance by context_bucket (rest/B2B) ===")
    for bucket, games in sorted(by_context.items(), key=lambda kv: kv[0]):
        stats = _eval_group(games)
        brier = f"{stats['brier']:.3f}" if stats["brier"] is not None else "N/A"
        log_loss = f"{stats['log_loss']:.3f}" if stats["log_loss"] is not None else "N/A"
        print(
            f"{bucket:15s}: N={stats['n']:3d}, Acc={stats['accuracy']:.3f}, "
            f"Brier={brier}, LogLoss={log_loss}"
        )
    print()

    # --- Performance by spread (model confidence) ---
    by_spread: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for p in preds:
        pa = float(p.get("predicted_away_win_prob", 0.5))
        ph = float(p.get("predicted_home_win_prob", 0.5))
        total = pa + ph
        if total <= 0:
            continue
        pa /= total
        ph /= total
        spread = abs(pa - ph)
        bucket = _bucket_spread(spread)
        by_spread[bucket].append(p)

    print("=== Performance by probability spread (confidence buckets) ===")
    for bucket, games in sorted(by_spread.items(), key=lambda kv: kv[0]):
        stats = _eval_group(games)
        brier = f"{stats['brier']:.3f}" if stats["brier"] is not None else "N/A"
        log_loss = f"{stats['log_loss']:.3f}" if stats["log_loss"] is not None else "N/A"
        print(
            f"Spread {bucket:6s}: N={stats['n']:3d}, Acc={stats['accuracy']:.3f}, "
            f"Brier={brier}, LogLoss={log_loss}"
        )
    print()


if __name__ == "__main__":
    main()


