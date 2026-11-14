#!/usr/bin/env python3
"""Sample-size stability for rate metrics (no invented counts).

Problem: a D with 5 controlled entries → 100% controlled-entry looks elite;
noise, not skill. Fix without fabricating events:

  1. Hard denom floors — null / exclude from leaderboards below n_min.
  2. Empirical-Bayes shrinkage — pull observed rate toward league prior
     with strength k (equivalent sample size). Published as *_regressed.
  3. Wilson interval half-width — expose uncertainty; flag low_confidence
     when half-width > threshold.
  4. Volume companion — always publish the attempt count next to the %.

All inputs are real observed successes/attempts.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Optional, Tuple


def wilson_interval(
    successes: float, n: float, z: float = 1.96
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Return (lo, hi, half_width) on [0,1]. None if n<=0."""
    if n is None or n <= 0:
        return None, None, None
    p = max(0.0, min(1.0, float(successes) / float(n)))
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    margin = (z / denom) * math.sqrt((p * (1.0 - p) / n) + z2 / (4.0 * n * n))
    lo = max(0.0, center - margin)
    hi = min(1.0, center + margin)
    return lo, hi, (hi - lo) / 2.0


def shrink_rate(
    successes: float,
    n: float,
    *,
    prior: float,
    prior_strength: float,
) -> Optional[float]:
    """Empirical Bayes: (x + k*π) / (n + k). Returns rate on [0,1]."""
    if n is None or n < 0 or prior_strength < 0:
        return None
    if n == 0 and prior_strength == 0:
        return None
    return (float(successes) + prior_strength * prior) / (float(n) + prior_strength)


def stabilize_pct(
    successes: float,
    attempts: float,
    *,
    prior: float,
    prior_strength: float = 20.0,
    min_attempts: int = 15,
    max_half_width: float = 0.18,
) -> Dict[str, Any]:
    """Build a real-data rate block with raw + regressed + confidence."""
    n = float(attempts or 0)
    x = float(successes or 0)
    raw = (100.0 * x / n) if n > 0 else None
    reg = shrink_rate(x, n, prior=prior, prior_strength=prior_strength)
    lo, hi, hw = wilson_interval(x, n)
    low_n = n < float(min_attempts)
    low_conf = (hw is None) or (hw > max_half_width) or low_n
    return {
        "successes": int(x) if x == int(x) else round(x, 2),
        "attempts": int(n) if n == int(n) else round(n, 2),
        "raw_pct": round(raw, 1) if raw is not None else None,
        "regressed_pct": round(100.0 * reg, 1) if reg is not None else None,
        "prior_pct": round(100.0 * prior, 1),
        "prior_strength": prior_strength,
        "wilson_lo_pct": round(100.0 * lo, 1) if lo is not None else None,
        "wilson_hi_pct": round(100.0 * hi, 1) if hi is not None else None,
        "wilson_halfwidth_pct": round(100.0 * hw, 1) if hw is not None else None,
        "min_attempts": min_attempts,
        "low_sample": low_n,
        "low_confidence": low_conf,
        # Leaderboard value: null if below floor (don't rank noise)
        "rank_pct": (
            round(100.0 * reg, 1)
            if (reg is not None and not low_n)
            else None
        ),
    }


def league_prior_from_totals(
    rows: Iterable[Tuple[float, float]],
) -> float:
    """π = Σx / Σn across rows with n>0."""
    sx = sn = 0.0
    for x, n in rows:
        if n and n > 0:
            sx += float(x)
            sn += float(n)
    if sn <= 0:
        return 0.5
    return sx / sn


# Default floors for skater % leaderboards (attempts).
SKATER_PCT_FLOORS: Dict[str, int] = {
    "controlled_entry_pct": 25,
    "failed_entry_pct": 25,
    "dump_in_recovery_pct": 12,
    "slot_drive_to_shot_pct": 10,
    "dz_retrieval_to_controlled_exit_pct": 8,
    "ev5v5_controlled_entry_pct": 25,
}

# Shrinkage strength k (pseudo-attempts toward league mean).
SKATER_PRIOR_STRENGTH: Dict[str, float] = {
    "controlled_entry_pct": 25.0,
    "failed_entry_pct": 25.0,
    "dump_in_recovery_pct": 15.0,
    "slot_drive_to_shot_pct": 12.0,
    "dz_retrieval_to_controlled_exit_pct": 10.0,
    "ev5v5_controlled_entry_pct": 25.0,
}


def attach_skater_stability(
    skater: Dict[str, Any],
    *,
    priors: Dict[str, float],
) -> Dict[str, Any]:
    """Add rates_stable block onto a skater row using observed totals."""
    rates = dict(skater.get("rates") or {})
    totals = skater  # totals live at top level in combined rows
    specs = [
        ("controlled_entry_pct", "controlled_entries", "entries"),
        ("failed_entry_pct", "failed_entries", "entries"),
        ("dump_in_recovery_pct", "dump_ins_recovered", "dump_ins"),
        ("slot_drive_to_shot_pct", "slot_drives_to_shot", "slot_drives"),
        (
            "dz_retrieval_to_controlled_exit_pct",
            "dz_recovery_to_controlled_exit",
            "dz_recoveries",
        ),
    ]
    stable: Dict[str, Any] = {}
    for rate_key, num_key, den_key in specs:
        x = totals.get(num_key)
        n = totals.get(den_key)
        if x is None or n is None:
            continue
        prior = priors.get(rate_key, 0.5)
        block = stabilize_pct(
            float(x),
            float(n),
            prior=prior,
            prior_strength=SKATER_PRIOR_STRENGTH.get(rate_key, 20.0),
            min_attempts=SKATER_PCT_FLOORS.get(rate_key, 15),
        )
        stable[rate_key] = block
        # Surface regressed for consumers that want a single number
        rates[f"{rate_key}_regressed"] = block["regressed_pct"]
        rates[f"{rate_key}_n"] = block["attempts"]
        rates[f"{rate_key}_low_sample"] = block["low_sample"]
        # Ranking-safe: overwrite display rank helper (keep raw as-is)
        rates[f"{rate_key}_rank"] = block["rank_pct"]
    skater = {**skater, "rates": rates, "rates_stable": stable}
    return skater


def compute_priors_from_skaters(skaters: List[Dict[str, Any]]) -> Dict[str, float]:
    pairs = {
        "controlled_entry_pct": ("controlled_entries", "entries"),
        "failed_entry_pct": ("failed_entries", "entries"),
        "dump_in_recovery_pct": ("dump_ins_recovered", "dump_ins"),
        "slot_drive_to_shot_pct": ("slot_drives_to_shot", "slot_drives"),
        "dz_retrieval_to_controlled_exit_pct": (
            "dz_recovery_to_controlled_exit",
            "dz_recoveries",
        ),
    }
    out: Dict[str, float] = {}
    for rate_key, (xk, nk) in pairs.items():
        out[rate_key] = league_prior_from_totals(
            (float(s.get(xk) or 0), float(s.get(nk) or 0)) for s in skaters
        )
    return out
