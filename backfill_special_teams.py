#!/usr/bin/env python3
"""Backfill special teams data (power play & penalty kill) for historical games."""

import json
from pathlib import Path
from typing import Tuple

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2


def _compute_penalty_kill(default_source: float) -> float:
    """Clamp derived penalty kill percentage to [0, 100]."""
    return float(max(0.0, min(100.0, default_source)))


def backfill_special_teams(window: int = 5000) -> Tuple[int, int]:
    """Backfill penalty kill values in stored predictions and rebuild team stats."""

    model = ImprovedSelfLearningModelV2()
    predictions = model.model_data.get("predictions", [])

    updated_predictions = 0
    for pred in predictions:
        if not pred.get("actual_winner"):
            continue
        metrics = pred.get("metrics_used") or {}
        if not metrics:
            continue

        changed = False

        # Derive away penalty kill from opponent power play when missing
        away_pk = metrics.get("away_penalty_kill_pct")
        if away_pk is None or away_pk == 0:
            home_pp = float(metrics.get("home_power_play_pct", 0.0))
            derived_away_pk = _compute_penalty_kill(100.0 - home_pp)
            if derived_away_pk or away_pk is None:
                metrics["away_penalty_kill_pct"] = derived_away_pk
                changed = True

        # Derive home penalty kill from opponent power play when missing
        home_pk = metrics.get("home_penalty_kill_pct")
        if home_pk is None or home_pk == 0:
            away_pp = float(metrics.get("away_power_play_pct", 0.0))
            derived_home_pk = _compute_penalty_kill(100.0 - away_pp)
            if derived_home_pk or home_pk is None:
                metrics["home_penalty_kill_pct"] = derived_home_pk
                changed = True

        if changed:
            pred["metrics_used"] = metrics
            updated_predictions += 1

    if updated_predictions:
        print(f"✅ Backfilled penalty kill data for {updated_predictions} predictions")
        model.model_data["predictions"] = predictions
        model.save_model_data()
    else:
        print("ℹ️  No predictions required penalty kill backfill")

    # Rebuild team stats using updated predictions
    model.team_stats = {}
    teams_updated = model.backfill_from_predictions(max_games=window)
    print(f"🏒 Updated team stats for {teams_updated} games")

    # Persist team stats separately for quick loading
    model.save_team_stats()

    return updated_predictions, teams_updated


def main():
    updated_predictions, teams_updated = backfill_special_teams()
    summary = {
        "predictions_updated": updated_predictions,
        "team_games_processed": teams_updated,
        "team_stats_file": str(Path("season_2025_2026_team_stats.json").resolve())
    }
    print("\nSummary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
