import json
from pathlib import Path


def test_smoke_meta_predictor_builds_prediction_dict():
    # Import should succeed in CI (PYTHONPATH set in workflows)
    from models.meta_ensemble_predictor import MetaEnsemblePredictor

    p = MetaEnsemblePredictor()
    out = p.predict("BOS", "TOR")

    assert isinstance(out, dict)
    for k in ["away_team", "home_team", "away_prob", "home_prob", "predicted_margin"]:
        assert k in out

    # If XGB features are present, we require a matching feature snapshot.
    from pathlib import Path
    if Path("xgb_features.pkl").exists():
        import os
        if os.environ.get("CI"):
            assert Path("model_feature_snapshot.json").exists()

    # Scoreline fields are optional but, if present, must be sane
    if out.get("predicted_home_goals") is not None:
        assert 0 <= int(out["predicted_home_goals"]) <= 15
    if out.get("predicted_away_goals") is not None:
        assert 0 <= int(out["predicted_away_goals"]) <= 15


def test_smoke_history_schema_has_predictions_array():
    hist = Path("data/win_probability_predictions_v2.json")
    if not hist.exists():
        hist = Path("win_probability_predictions_v2.json")
    assert hist.exists()
    d = json.loads(hist.read_text())
    assert isinstance(d.get("predictions", []), list)

