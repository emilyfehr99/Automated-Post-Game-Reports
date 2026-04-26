from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


PREDICTION_EVENTS_PATH = Path("data/prediction_events.jsonl")
OUTCOME_EVENTS_PATH = Path("data/outcome_events.jsonl")
POSTGAME_METRICS_EVENTS_PATH = Path("data/postgame_metrics_events.jsonl")


def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)

def _json_safe(obj: Any) -> Any:
    """
    Best-effort conversion to JSON-serializable types.
    This keeps event ingestion resilient when upstream code returns sets,
    numpy scalars, Paths, etc.
    """
    # Fast paths
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # Common non-JSON containers
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, set):
        # Order doesn't matter for sets; stabilize for diffs/debugging.
        try:
            return sorted([_json_safe(v) for v in obj], key=lambda x: str(x))
        except Exception:
            return [_json_safe(v) for v in obj]

    # Path-like
    if isinstance(obj, Path):
        return str(obj)

    # datetime-like
    if hasattr(obj, "isoformat") and callable(getattr(obj, "isoformat")):
        try:
            return obj.isoformat()
        except Exception:
            pass

    # numpy scalars / arrays (avoid importing numpy)
    if hasattr(obj, "item") and callable(getattr(obj, "item")):
        try:
            return _json_safe(obj.item())
        except Exception:
            pass
    if hasattr(obj, "tolist") and callable(getattr(obj, "tolist")):
        try:
            return _json_safe(obj.tolist())
        except Exception:
            pass

    # Fallback: string representation
    return str(obj)


def append_prediction_event(event: Dict[str, Any], *, path: Path = PREDICTION_EVENTS_PATH) -> None:
    """
    Append-only prediction event. One JSON object per line.

    Required fields (best-effort): game_id, date, away_team, home_team.
    """
    _ensure_parent(path)
    payload = _json_safe(dict(event))
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
    **kwargs,
) -> None:
    _ensure_parent(path)
    payload: Dict[str, Any] = _json_safe({
        "event_type": "outcome",
        "recorded_at_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "game_id": game_id,
        "date": date,
        "away_team": away_team,
        "home_team": home_team,
        "actual_away_score": actual_away_score,
        "actual_home_score": actual_home_score,
        "actual_winner": actual_winner,
    })
    if lead_after_p1 is not None:
        payload["lead_after_p1"] = int(lead_after_p1)
    
    # Store any extra metrics (e.g. xG, shots) directly in the outcome event
    for k, v in kwargs.items():
        if v is not None:
            payload[k] = _json_safe(v)
            
    with open(path, "a") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def append_postgame_metrics_event(event: Dict[str, Any], *, path: Path = POSTGAME_METRICS_EVENTS_PATH) -> None:
    """
    Append-only postgame metrics event. One JSON object per line.

    Required fields (best-effort): game_id, date, away_team, home_team, postgame_metrics.
    """
    _ensure_parent(path)
    payload = _json_safe(dict(event))
    payload.setdefault("event_type", "postgame_metrics")
    payload.setdefault("recorded_at_utc", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
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

