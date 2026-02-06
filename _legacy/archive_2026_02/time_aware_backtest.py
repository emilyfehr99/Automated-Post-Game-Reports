#!/usr/bin/env python3
"""
Time-aware backtest for the pre-game prediction model.

Goals (matches your point #5 - data hygiene & time-aware validation):
  - Evaluate accuracy, Brier, and log-loss on FUTURE games only
    (no leakage from using later games to judge earlier ones).
  - Report performance per season and across multiple train/test splits.

Usage:
  python time_aware_backtest.py
"""

import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any


def _parse_date(d: str | None) -> datetime | None:
    if not d:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(d, fmt)
        except ValueError:
            continue
    return None


def _load_predictions(path: Path) -> List[Dict[str, Any]]:
    with path.open("r") as f:
        data = json.load(f)
    preds = data.get("predictions", data)
    # Keep only completed games with usable probabilities
    cleaned: List[Dict[str, Any]] = []
    for p in preds:
        if not p.get("actual_winner"):
            continue
        pa = p.get("predicted_away_win_prob")
        ph = p.get("predicted_home_win_prob")
        if pa is None or ph is None:
            continue
        # Normalize to decimals if needed
        if pa > 1.0 or ph > 1.0:
            pa = pa / 100.0
            ph = ph / 100.0
        total = (pa or 0.5) + (ph or 0.5)
        if total <= 0:
            continue
        p["predicted_away_win_prob"] = pa / total
        p["predicted_home_win_prob"] = ph / total
        cleaned.append(p)
    # Sort chronologically
    cleaned.sort(key=lambda p: _parse_date(p.get("date")) or datetime.min)
    return cleaned


def _eval_chunk(chunk: List[Dict[str, Any]]) -> Dict[str, float]:
    if not chunk:
        return {"n": 0, "accuracy": 0.0, "brier": None, "log_loss": None}
    correct = 0
    brier_sum = 0.0
    log_loss_sum = 0.0
    n_ll = 0
    for p in chunk:
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
        log_loss_sum += -(y * math.log(p_true) + (1.0 - y) * math.log(1.0 - p_true))
        n_ll += 1
    n = len(chunk)
    return {
        "n": n,
        "accuracy": correct / n if n else 0.0,
        "brier": brier_sum / n if n else None,
        "log_loss": log_loss_sum / n_ll if n_ll else None,
    }


def time_split_backtests(preds: List[Dict[str, Any]]) -> None:
    print("=== Time-aware train/test splits ===")
    n = len(preds)
    if n < 50:
        print(f"Not enough completed games ({n}) for meaningful time splits.")
        return

    # Evaluate multiple train:test splits (e.g., 60/40, 70/30, 80/20)
    for train_frac in (0.6, 0.7, 0.8):
        cutoff = int(n * train_frac)
        train = preds[:cutoff]
        test = preds[cutoff:]
        stats = _eval_chunk(test)
        brier = f"{stats['brier']:.3f}" if stats["brier"] is not None else "N/A"
        log_loss = f"{stats['log_loss']:.3f}" if stats["log_loss"] is not None else "N/A"
        print(
            f"Train {int(train_frac*100):2d}% / Test {int((1-train_frac)*100):2d}% "
            f"-> Test N={stats['n']}, Acc={stats['accuracy']:.3f}, "
            f"Brier={brier}, LogLoss={log_loss}"
        )
    print()


def season_breakdown(preds: List[Dict[str, Any]]) -> None:
    print("=== Season-by-season performance ===")
    by_season: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for p in preds:
        d = _parse_date(p.get("date"))
        if not d:
            season = "unknown"
        else:
            # NHL season e.g. 2024-2025 based on year and month
            year = d.year
            if d.month >= 9:
                season = f"{year}-{year+1}"
            else:
                season = f"{year-1}-{year}"
        by_season[season].append(p)

    for season, games in sorted(by_season.items()):
        stats = _eval_chunk(games)
        brier = f"{stats['brier']:.3f}" if stats["brier"] is not None else "N/A"
        log_loss = f"{stats['log_loss']:.3f}" if stats["log_loss"] is not None else "N/A"
        print(
            f"{season}: N={stats['n']}, Acc={stats['accuracy']:.3f}, "
            f"Brier={brier}, LogLoss={log_loss}"
        )
    print()


def main() -> None:
    path = Path("win_probability_predictions_v2.json")
    if not path.exists():
        print(f"Predictions file not found at {path.resolve()}")
        return

    preds = _load_predictions(path)
    print(f"Loaded {len(preds)} completed games with valid probabilities.\n")

    time_split_backtests(preds)
    season_breakdown(preds)


if __name__ == "__main__":
    main()


