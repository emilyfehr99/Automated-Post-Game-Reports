from __future__ import annotations

import math
from typing import Iterable, Optional

import numpy as np


def estimate_nb_size_from_mean_var(mean: float, var: float, *, min_size: float = 0.5, max_size: float = 200.0) -> Optional[float]:
    """
    Negative Binomial (NB2) parameterization:
      Var(Y) = mean + mean^2 / size

    Solve for size: size = mean^2 / (var - mean)
    """
    if mean is None or var is None:
        return None
    if mean <= 0:
        return None
    if var <= mean + 1e-12:
        return None
    size = (mean * mean) / max(1e-12, (var - mean))
    return float(max(min_size, min(max_size, size)))


def nb_logpmf(y: np.ndarray, mean: np.ndarray, size: float) -> np.ndarray:
    """
    Log PMF for NB with mean/size (NB2).
    """
    y = np.asarray(y, dtype=float)
    mu = np.clip(np.asarray(mean, dtype=float), 1e-6, 1e9)
    r = float(max(1e-6, size))
    # p = r/(r+mu)
    p = r / (r + mu)
    # log comb(y+r-1, y) + r log p + y log(1-p)
    lg = np.vectorize(math.lgamma)
    return (lg(y + r) - lg(r) - lg(y + 1.0)) + (r * np.log(p)) + (y * np.log1p(-p))


def nb_nll(y: Iterable[float], mean: Iterable[float], size: float) -> float:
    ll = nb_logpmf(np.asarray(list(y), dtype=float), np.asarray(list(mean), dtype=float), float(size))
    return float(-np.mean(ll))

