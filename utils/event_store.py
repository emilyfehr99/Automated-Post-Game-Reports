from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


PREDICTION_EVENTS_PATH = Path("data/prediction_events.jsonl")
OUTCOME_EVENTS_PATH = Path("data/outcome_events.jsonl")


def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def append_prediction_event(event: Dict[str, Any], *, path: Path = PREDICTION_EVENTS_PATH) -> None:
    """
    Append-only prediction event. One JSON object per line.

    Required fields (best-effort): game_id, date, away_team, home_team.
    """
    _ensure_parent(path)
    payload = dict(event)
    payload.setdefault("event_type", "prediction")
    payload.setdefault("recorded_at_utc", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    with open(path, "a") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def append_outcome_event(
    *,
    game_id: str,
    date: Optional[str],
    away_team: Optional[str],
    home_team: Optional[str],
    actual_away_score: Optional[int],
    actual_home_score: Optional[int],
    actual_winner: Optional[str],
    lead_after_p1: Optional[int] = None,
    path: Path = OUTCOME_EVENTS_PATH,
) -> None:
    _ensure_parent(path)
    payload: Dict[str, Any] = {
        "event_type": "outcome",
        "recorded_at_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "game_id": game_id,
        "date": date,
        "away_team": away_team,
        "home_team": home_team,
        "actual_away_score": actual_away_score,
        "actual_home_score": actual_home_score,
        "actual_winner": actual_winner,
    }
    if lead_after_p1 is not None:
        payload["lead_after_p1"] = int(lead_after_p1)
    with open(path, "a") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def load_latest_by_game_id(path: Path) -> Dict[str, Dict[str, Any]]:
    """
    Load JSONL and return latest record per game_id.
    """
    latest: Dict[str, Dict[str, Any]] = {}
    if not path.exists():
        return latest
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            gid = obj.get("game_id")
            if gid is None:
                continue
            latest[str(gid)] = obj
    return latest

