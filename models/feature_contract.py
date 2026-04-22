from __future__ import annotations

from typing import Iterable, List


# Columns that must never be used as pregame ML features.
# These are either postgame outcomes/labels or derived from them.
FORBIDDEN_FEATURE_NAMES = {
    "target",
    "p1_target",
    "margin",
    "home_goals_final",
    "away_goals_final",
    "total_goals_final",
}


def validate_feature_names(feature_names: Iterable[str]) -> List[str]:
    """
    Return list of forbidden feature names present (empty if OK).

    We keep this strict and explicit to avoid silent leakage re-entering the pipeline.
    """
    bad = []
    for n in feature_names:
        if n in FORBIDDEN_FEATURE_NAMES:
            bad.append(n)
    return sorted(set(bad))


def assert_no_forbidden_features(feature_names: Iterable[str]) -> None:
    bad = validate_feature_names(feature_names)
    if bad:
        raise ValueError(f"Forbidden features present in ML matrix: {bad}")

