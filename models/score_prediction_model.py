#!/usr/bin/env python3
"""
Score Prediction Model v3 — Optimized
Data-driven score predictions with correlation-validated features and
optimizations based on backtest analysis:

Key features:
  - Game Score (GS) r=0.642 with goals
  - Recency-weighted averages (last 10 games get 2x weight)
  - Sanitized PP%/PK% (raw data had values 0-400% / -300%)
  - Back-to-back/rest day adjustment
  - Goalie GSAX integration (from goalie performance data)
  - Opponent defensive quality
  - xG luck regression
  - Home ice advantage (+0.21 GF/game)
  - Division strength context
  - Poisson-sampled scores for realistic variance
"""

import json
import hashlib
import time
import numpy as np
from typing import Dict, Optional, Tuple, List
from pathlib import Path


# NHL structure
DIVISIONS = {
    'Atlantic': ['BOS', 'BUF', 'DET', 'FLA', 'MTL', 'OTT', 'TBL', 'TOR'],
    'Metropolitan': ['CAR', 'CBJ', 'NJD', 'NYI', 'NYR', 'PHI', 'PIT', 'WSH'],
    'Central': ['CHI', 'COL', 'DAL', 'MIN', 'NSH', 'STL', 'UTA', 'WPG'],
    'Pacific': ['ANA', 'CGY', 'EDM', 'LAK', 'SEA', 'SJS', 'VAN', 'VGK'],
}
TEAM_TO_DIV = {t: d for d, teams in DIVISIONS.items() for t in teams}

# Phase 4: Time Zone Mapping (UTC Offsets)
TEAM_TIMEZONES = {
    'ANA': -8, 'LAK': -8, 'SJS': -8, 'VAN': -8, 'SEA': -8, 'VGK': -8,
    'UTA': -7, 'CGY': -7, 'EDM': -7, 'COL': -7,
    'CHI': -6, 'DAL': -6, 'MIN': -6, 'NSH': -6, 'STL': -6, 'WPG': -6,
    'BOS': -5, 'BUF': -5, 'MTL': -5, 'OTT': -5, 'TOR': -5, 'CAR': -5, 'NJD': -5, 
    'NYI': -5, 'NYR': -5, 'PHI': -5, 'PIT': -5, 'WSH': -5, 'FLA': -5, 'TBL': -5, 
    'DET': -5, 'CBJ': -5
}


class ScorePredictionModel:
    """Optimized score prediction using correlation-validated features."""
    
    # League-wide constants from 2025-26 analysis
    LEAGUE_AVG_GF = 3.03
    HOME_ICE_BOOST = 0.11
    XG_LUCK_REGRESSION = 0.35
    B2B_PENALTY = 0.42  # Teams score ~0.42 fewer goals on back-to-backs (late season adjusted)
    
    # Feature weights (from correlation analysis)
    W_GS = 0.30
    W_XG = 0.25
    W_PP = 0.15        # Reduced from 0.20 — PP% data is noisy
    W_HDC = 0.15
    W_CONTEXT = 0.15
    
    def __init__(self):
        """Load all data sources."""
        self.team_stats = {}
        self.team_averages = {}
        self.prediction_history = []
        self.goalie_stats = {}
        self.h2h_cache = {}
        
        # Load team stats
        for p in [Path('data/season_2025_2026_team_stats.json'),
                  Path('season_2025_2026_team_stats.json')]:
            if p.exists():
                with open(p) as f:
                    self.team_stats = json.load(f)
                break
        
        # Load prediction history (has actual scores, B2B, opponents)
        for p in [Path('data/win_probability_predictions_v2.json'),
                  Path('win_probability_predictions_v2.json')]:
            if p.exists():
                with open(p) as f:
                    pred_data = json.load(f)
                self.prediction_history = pred_data.get('predictions', [])
                break
        
        # Load comprehensive goalie stats from high-fidelity metrics source
        # This now contains xG-based GSAX from the ImprovedXGModel
        for p in [Path('data/team_advanced_metrics.json'), Path('team_advanced_metrics.json')]:
            if p.exists():
                with open(p) as f:
                    metrics_data = json.load(f)
                self.goalie_stats = metrics_data.get('goalies', {})
                # Create a name -> ID layout for easy lookup
                self.goalie_names = {v['name']: k for k, v in self.goalie_stats.items()}
                print(f"🧤 Loaded {len(self.goalie_stats)} high-fidelity goalies (xG-based GSAX)")
                break
        
        # Fallback to legacy goalie_stats if above failed
        if not self.goalie_stats:
            for p in [Path('data/goalie_stats.json'), Path('goalie_stats.json')]:
                if p.exists():
                    with open(p) as f:
                        g_data = json.load(f)
                    self.goalie_stats = g_data.get('goalies', {})
                    self.goalie_names = {v['name']: k for k, v in self.goalie_stats.items()}
                    break
        
        # NOTE: Finishing profiles (team_scoring_profiles.json) removed —
        # 29/32 teams were above 1.2x (noise), and xG luck regression
        # already captures over/underperformance vs expected goals.
        
        if self.team_stats:
            self._precompute_averages()
            self._build_h2h_records()
            n_h2h = sum(len(v) for v in self.h2h_cache.values())
            
            # Dynamic league average: compute from actual team data instead of hardcoded
            self._learn_league_avg()
            
            # Scoring bias correction: learn from prediction errors
            self._learn_scoring_bias()
            
            print(f"✅ Score model v3: {len(self.team_averages)} teams, "
                  f"{len(self.prediction_history)} predictions, "
                  f"{n_h2h} H2H records")
            print(f"   📊 Dynamic league avg: {self.LEAGUE_AVG_GF:.2f} GF/game, "
                  f"scoring bias correction: {self._scoring_bias:.3f}")

            # Learn a win-prob calibration curve from historical outcomes.
            # This adjusts the winner decision boundary away from a pure
            # Poisson assumption (helps reach higher winner accuracy).
            self._win_calibration = self._build_win_calibration()

            # OT-scale / blend tuning (time-split validation).
            # We blend calibrated P(win) with a Poisson+OT tie allocation
            # model. This lets OT-like variance influence winner decisions.
            # Also estimate a dispersion parameter for Negative Binomial
            # (more realistic scoring variance than Poisson).
            self._dispersion_k = self._estimate_dispersion_k()

            self._ot_scale = 0.75
            self._ot_blend = 0.85
            self._ot_tie_gamma = 1.0
            self._max_goals = 10
            self._tune_ot_scale_and_blend()
            self._tune_max_goals()
        else:
            print("⚠️  No team stats found, using league averages")
            self._win_calibration = None
            self._ot_scale = 0.75
            self._ot_blend = 0.85
            self._dispersion_k = 20.0
            self._ot_tie_gamma = 1.0
            self._max_goals = 10
            self._scoring_bias = 0.0

    def _learn_league_avg(self):
        """Dynamically compute league average GF/game from actual team data.
        
        Instead of relying on a hardcoded 3.03, this uses the actual season
        data to stay accurate as the season progresses and scoring trends shift.
        """
        all_goals = []
        for team, avgs in self.team_averages.items():
            combined = avgs.get('combined', {})
            goals_flat = combined.get('goals_flat')
            if goals_flat is not None and not np.isnan(goals_flat):
                all_goals.append(goals_flat)
        
        if len(all_goals) >= 10:
            self.LEAGUE_AVG_GF = float(np.mean(all_goals))
        # else keep the default 3.03
    
    def _learn_scoring_bias(self):
        """Learn a scoring bias correction from prediction history.
        
        Compares predicted total goals (away_xg + home_xg from past predictions
        that have actual scores) against actual total goals. If the model has been
        systematically over- or under-predicting totals, applies a correction
        factor to future predictions.
        
        Uses recency weighting so recent errors matter more than old ones.
        """
        self._scoring_bias = 0.0
        
        # Only use predictions that have actual outcomes
        completed = [p for p in self.prediction_history 
                     if p.get('actual_away_score') is not None 
                     and p.get('actual_home_score') is not None]
        
        if len(completed) < 30:
            return  # Not enough data to learn from
        
        # Use last 200 games for the bias calculation (recency)
        recent = completed[-200:]
        
        errors = []  # positive = model predicted too high
        weights = []
        n = len(recent)
        for i, pred in enumerate(recent):
            actual_total = pred['actual_away_score'] + pred['actual_home_score']
            
            # Get predicted total from metrics if available
            metrics = pred.get('metrics_used', {})
            pred_away_xg = metrics.get('away_xg', 0)
            pred_home_xg = metrics.get('home_xg', 0)
            pred_total = pred_away_xg + pred_home_xg
            
            if pred_total > 0:  # Only if we have valid predicted xG
                error = pred_total - actual_total
                errors.append(error)
                # Exponential recency weight: newest gets weight 1.0
                w = 0.5 ** ((n - 1 - i) / 50)  # half-life of 50 games
                weights.append(w)
        
        if len(errors) >= 20:
            total_w = sum(weights)
            if total_w > 0:
                weighted_bias = sum(e * w for e, w in zip(errors, weights)) / total_w
                # Cap the bias correction at +/- 0.5 goals per team
                self._scoring_bias = max(-0.5, min(0.5, weighted_bias / 2.0))
        
        # ─── Per-team scoring environment ───
        # Some teams consistently play in high-scoring games (bad defense, fast pace)
        # while others grind out low-scoring games. Learn this from actual outcomes.
        from collections import defaultdict
        team_totals = defaultdict(list)
        league_avg_total = float(np.mean([
            p['actual_away_score'] + p['actual_home_score'] for p in completed
        ])) if completed else 6.0
        
        for pred in completed:
            total = pred['actual_away_score'] + pred['actual_home_score']
            away = pred.get('away_team', '')
            home = pred.get('home_team', '')
            if away:
                team_totals[away].append(total)
            if home:
                team_totals[home].append(total)
        
        self._team_scoring_env = {}
        for team, totals in team_totals.items():
            if len(totals) >= 10:  # Need sufficient sample
                team_avg = float(np.mean(totals))
                # Per-team adjustment: how much above/below league avg this team's games run
                # Split in half since both teams contribute to the total
                env_adj = (team_avg - league_avg_total) / 2.0
                # Cap at +/- 0.4 per team
                self._team_scoring_env[team] = max(-0.4, min(0.4, env_adj))
        
        # ─── Per-team venue splits (home vs away) ───
        # Learn how each team performs at home vs on the road from actual outcomes.
        # Replaces the flat HOME_ICE_BOOST with per-team adjustments.
        from collections import defaultdict as dd2
        team_home_gf = dd2(list)
        team_away_gf = dd2(list)
        team_home_wins = dd2(int)
        team_home_games = dd2(int)
        
        for pred in completed:
            away = pred.get('away_team', '')
            home = pred.get('home_team', '')
            a_s, h_s = pred['actual_away_score'], pred['actual_home_score']
            
            if home:
                team_home_gf[home].append(h_s)
                team_home_games[home] += 1
                if h_s > a_s:
                    team_home_wins[home] += 1
            if away:
                team_away_gf[away].append(a_s)
        
        self._team_venue_splits = {}
        league_home_gf = float(np.mean([g['actual_home_score'] for g in completed])) if completed else 3.1
        league_away_gf = float(np.mean([g['actual_away_score'] for g in completed])) if completed else 3.0
        
        all_teams_venue = set(list(team_home_gf.keys()) + list(team_away_gf.keys()))
        for team in all_teams_venue:
            h_gf = team_home_gf.get(team, [])
            a_gf = team_away_gf.get(team, [])
            if len(h_gf) >= 8 and len(a_gf) >= 8:
                home_avg = float(np.mean(h_gf))
                away_avg = float(np.mean(a_gf))
                # How much better/worse this team scores at home vs away
                # relative to the league-wide home/away split
                home_boost = (home_avg - league_home_gf)  # vs league home avg
                away_boost = (away_avg - league_away_gf)  # vs league away avg
                home_wp = team_home_wins.get(team, 0) / max(1, team_home_games.get(team, 1))
                
                self._team_venue_splits[team] = {
                    'home_gf_adj': max(-0.5, min(0.5, home_boost)),
                    'away_gf_adj': max(-0.5, min(0.5, away_boost)),
                    'home_win_pct': home_wp,
                }
    
    def _get_team_env_adjustment(self, team: str) -> float:
        """Get a team's scoring environment adjustment from learned data.
        
        Positive = this team's games tend to be higher-scoring than average.
        Negative = this team's games tend to be lower-scoring.
        """
        return getattr(self, '_team_scoring_env', {}).get(team.upper(), 0.0)
    
    def _get_venue_adjustment(self, team: str, venue: str) -> float:
        """Get a team's venue-specific scoring adjustment.
        
        Returns how many more/fewer goals this team scores at the given venue
        compared to the league average for that venue.
        """
        splits = getattr(self, '_team_venue_splits', {}).get(team.upper())
        if not splits:
            return 0.0
        if venue == 'home':
            return splits.get('home_gf_adj', 0.0)
        else:
            return splits.get('away_gf_adj', 0.0)

    def _poisson_win_probs(self, away_lam: float, home_lam: float, max_goals: int = 15) -> Tuple[float, float, float]:
        """Return (p_away_reg_win, p_home_reg_win, p_tie_reg) from two Poissons."""
        import math

        away_lam = max(0.01, float(away_lam))
        home_lam = max(0.01, float(home_lam))

        pmf_away = [
            math.exp(-away_lam) * (away_lam ** k) / math.factorial(k)
            for k in range(max_goals + 1)
        ]
        pmf_home = [
            math.exp(-home_lam) * (home_lam ** k) / math.factorial(k)
            for k in range(max_goals + 1)
        ]

        p_away_win = 0.0
        p_home_win = 0.0
        p_tie = 0.0

        for a in range(max_goals + 1):
            pa = pmf_away[a]
            if pa == 0.0:
                continue
            for h in range(max_goals + 1):
                ph = pmf_home[h]
                if a > h:
                    p_away_win += pa * ph
                elif h > a:
                    p_home_win += pa * ph
                else:
                    p_tie += pa * ph

        return p_away_win, p_home_win, p_tie

    def _poisson_away_win_with_ot(self, away_lam: float, home_lam: float, ot_scale: float) -> float:
        """Poisson win prob with OT-like tie reallocation using OT_SCALE."""
        import math

        p_away_win, _p_home_win, p_tie = self._poisson_win_probs(away_lam, home_lam, max_goals=12)
        # Bias OT toward the higher-lambda side; OT_SCALE controls randomness.
        # ot_scale -> small => near-deterministic OT; large => near coin-flip.
        denom = max(1e-6, float(ot_scale))
        diff = float(away_lam) - float(home_lam)
        away_ot_share = 0.5 + 0.5 * math.tanh(diff / denom)
        away_ot_share = max(0.01, min(0.99, away_ot_share))
        return float(p_away_win + p_tie * away_ot_share)

    def _estimate_dispersion_k(self, max_bins: int = 6, min_bin_n: int = 40) -> float:
        """
        Estimate an overdispersion parameter k for Negative Binomial.
        Uses moment matching inside quantile bins of expected goals mu:
          Var[goals | mu] = mu + mu^2 / k  =>  k = mu^2 / (Var - mu)
        """
        try:
            mus: List[float] = []
            ys: List[int] = []
            total_mus: List[float] = []

            # Replicate each game's total context for away/home samples.
            for p in self.prediction_history:
                away = p.get("away_team")
                home = p.get("home_team")
                a = p.get("actual_away_score")
                h = p.get("actual_home_score")
                if not (away and home and a is not None and h is not None):
                    continue
                if a == h:
                    continue

                sp = self.predict_score(away, home, use_calibration=False)
                mu_a = float(sp["away_expected"])
                mu_h = float(sp["home_expected"])
                total_mu = mu_a + mu_h

                for mu_i, y_i in [(mu_a, int(a)), (mu_h, int(h))]:
                    mus.append(float(mu_i))
                    ys.append(int(y_i))
                    total_mus.append(float(total_mu))

            if len(mus) < 250:
                self._dispersion_k_by_total_edges = None
                self._dispersion_k_by_total_values = None
                return 20.0

            mus_arr = np.array(mus, dtype=float)
            ys_arr = np.array(ys, dtype=float)
            total_mus_arr = np.array(total_mus, dtype=float)

            # --- Global k ---
            qs = np.linspace(0.0, 1.0, max_bins + 1)
            edges_mu = np.quantile(mus_arr, qs)
            edges_mu = np.unique(edges_mu)
            if edges_mu.size < 3:
                global_k = 20.0
            else:
                ks: List[float] = []
                weights: List[int] = []
                for i in range(edges_mu.size - 1):
                    lo = edges_mu[i]
                    hi = edges_mu[i + 1]
                    if i == edges_mu.size - 2:
                        mask = (mus_arr >= lo) & (mus_arr <= hi)
                    else:
                        mask = (mus_arr >= lo) & (mus_arr < hi)
                    n = int(mask.sum())
                    if n < min_bin_n:
                        continue
                    # Use observed goal mean for moment matching (empirically stable).
                    m = float(ys_arr[mask].mean())
                    v = float(ys_arr[mask].var(ddof=0))
                    if v <= m + 1e-6:
                        k_i = 1e6
                    else:
                        k_i = (m * m) / max(1e-6, (v - m))
                    if np.isfinite(k_i) and k_i > 0:
                        ks.append(float(k_i))
                        weights.append(n)

                if not ks:
                    global_k = 20.0
                else:
                    global_k = float(np.average(np.array(ks), weights=np.array(weights)))
                    global_k = float(max(0.5, min(50.0, global_k)))

            # --- Context-varying k by total expected goals only ---
            edges_total = None
            values_total = None
            try:
                edges_total = np.unique(np.quantile(total_mus_arr, np.linspace(0.0, 1.0, max_bins + 1)))
                if edges_total.size >= 3:
                    values_total = np.full(edges_total.size - 1, np.nan, dtype=float)
                    max_k = 300.0
                    for i in range(edges_total.size - 1):
                        lo_t = float(edges_total[i])
                        hi_t = float(edges_total[i + 1])
                        if i == edges_total.size - 2:
                            mask = (total_mus_arr >= lo_t) & (total_mus_arr <= hi_t)
                        else:
                            mask = (total_mus_arr >= lo_t) & (total_mus_arr < hi_t)
                        n = int(mask.sum())
                        if n < min_bin_n:
                            continue
                        m = float(ys_arr[mask].mean())
                        v = float(ys_arr[mask].var(ddof=0))
                        if v <= m + 1e-6:
                            kval = float(global_k)
                        else:
                            kval = (m * m) / max(1e-6, (v - m))
                        if not np.isfinite(kval) or kval <= 0:
                            kval = float(global_k)
                        # Keep k in a realistic range; very large k collapses NB->Poisson.
                        kval = float(max(0.5, min(50.0, kval)))
                        values_total[i] = kval
            except Exception:
                edges_total = None
                values_total = None

            self._dispersion_k_by_total_edges = edges_total
            self._dispersion_k_by_total_values = values_total
            return float(global_k)
        except Exception:
            self._dispersion_k_by_total_edges = None
            self._dispersion_k_by_total_values = None
            return 20.0

    def _get_dispersion_k(
        self,
        away_team: str,
        home_team: str,
        away_mu: float,
        home_mu: float,
    ) -> float:
        """Return dispersion k selected by total xG bucket."""
        try:
            total_edges = getattr(self, "_dispersion_k_by_total_edges", None)
            values = getattr(self, "_dispersion_k_by_total_values", None)
            if total_edges is None or values is None:
                return float(getattr(self, "_dispersion_k", 20.0))

            total_mu = float(away_mu) + float(home_mu)
            if not np.isfinite(total_mu):
                return float(getattr(self, "_dispersion_k", 20.0))
            idx = int(np.searchsorted(total_edges, total_mu, side="right") - 1)
            idx = max(0, min(idx, int(len(values) - 1)))
            kval = float(values[idx])
            if np.isfinite(kval) and kval > 0.0:
                return kval
            return float(getattr(self, "_dispersion_k", 20.0))
        except Exception:
            return float(getattr(self, "_dispersion_k", 20.0))

    def _neg_bin_pmf(self, n: int, mu: float, k: float) -> float:
        """
        Negative binomial pmf for counts with mean mu and dispersion k.
        Parameterization: r=k, p=r/(r+mu)
          pmf(n) = C(n+r-1,n) * p^r * (1-p)^n
        """
        import math
        mu = max(1e-9, float(mu))
        k = max(1e-9, float(k))
        p = k / (k + mu)
        # log pmf using lgamma for stability
        logc = math.lgamma(n + k) - math.lgamma(k) - math.lgamma(n + 1)
        logpmf = logc + (k * math.log(p)) + (n * math.log(1.0 - p))
        return float(math.exp(logpmf))

    def _neg_bin_win_probs(self, away_mu: float, home_mu: float, k: float, max_goals: int = 12) -> Tuple[float, float, float]:
        """Return (p_away_reg_win, p_home_reg_win, p_tie_reg) from NB goals."""
        import math

        away_mu = float(away_mu)
        home_mu = float(home_mu)
        k = float(k)

        pmf_away = [self._neg_bin_pmf(g, away_mu, k) for g in range(max_goals + 1)]
        pmf_home = [self._neg_bin_pmf(g, home_mu, k) for g in range(max_goals + 1)]

        p_away_win = 0.0
        p_home_win = 0.0
        p_tie = 0.0

        for a in range(max_goals + 1):
            pa = pmf_away[a]
            if pa == 0.0:
                continue
            for h in range(max_goals + 1):
                ph = pmf_home[h]
                if a > h:
                    p_away_win += pa * ph
                elif h > a:
                    p_home_win += pa * ph
                else:
                    p_tie += pa * ph

        return float(p_away_win), float(p_home_win), float(p_tie)

    def _neg_bin_away_win_with_ot(
        self,
        away_mu: float,
        home_mu: float,
        ot_scale: float,
        k: float,
        tie_gamma: float = 1.0,
    ) -> float:
        """
        Regulation win probs from NB, and OT allocation:
        - OT additional scoring uses NB with mean scaled by ot_scale.
        - Sudden-death approximation: after a regulation tie, we allocate the
          remaining tie mass to the side with higher OT mean, with special
          casing for zero-goal outcomes.
        """
        import math

        # Regulation win/tie
        p_away_win_reg, _p_home_win_reg, p_tie_reg = self._neg_bin_win_probs(
            away_mu, home_mu, k, max_goals=12
        )

        # OT additional expected goals (scaled)
        away_ot_mu = max(0.01, float(away_mu) * float(ot_scale))
        home_ot_mu = max(0.01, float(home_mu) * float(ot_scale))

        # P(OT goals == 0) under NB: (k/(k+mu))^k
        def nb_p0(mu_ot: float) -> float:
            kk = max(1e-9, float(k))
            return float((kk / (kk + mu_ot)) ** kk)

        away0 = nb_p0(away_ot_mu)
        home0 = nb_p0(home_ot_mu)

        away_scored = max(0.0, 1.0 - away0)
        home_scored = max(0.0, 1.0 - home0)

        total_ot_mu = away_ot_mu + home_ot_mu
        away_share = float(away_ot_mu / total_ot_mu) if total_ot_mu > 0 else 0.5
        away_share = max(0.01, min(0.99, away_share))
        # Bias how strongly we allocate OT tie mass by expected OT scoring.
        # tie_gamma=1.0 keeps the original proportional allocation.
        # tie_gamma<1.0 moves toward a more neutral 50/50 split.
        # tie_gamma>1.0 concentrates tie mass more heavily to the higher-OT side.
        tie_gamma = float(tie_gamma)
        if tie_gamma != 1.0:
            away_share = 0.5 + (away_share - 0.5) * tie_gamma
            away_share = max(0.01, min(0.99, float(away_share)))

        # If exactly one side scores in OT, that side wins.
        # If both score or both score 0, we approximate by sharing by away_share.
        p_away_win_ot_cond = (home0 * away_scored) + away_share * (
            (away0 * home0) + (away_scored * home_scored)
        )
        p_away_win_ot_cond = max(0.0, min(1.0, p_away_win_ot_cond))

        return float(p_away_win_reg + p_tie_reg * p_away_win_ot_cond)

    def _tune_ot_scale_and_blend(self) -> None:
        """Tune OT_SCALE and blend weight via time-split validation."""
        if not self.prediction_history or not self._win_calibration:
            return

        # Build completed list with timestamps.
        completed = []
        for p in self.prediction_history:
            away = p.get("away_team")
            home = p.get("home_team")
            a = p.get("actual_away_score")
            h = p.get("actual_home_score")
            if not (away and home):
                continue
            if a is None or h is None:
                continue
            try:
                a_i = int(a)
                h_i = int(h)
            except (TypeError, ValueError):
                continue
            if a_i == h_i:
                continue  # rare in stored data

            away_b2b = bool(p.get("away_back_to_back", False))
            home_b2b = bool(p.get("home_back_to_back", False))

            ts = p.get("timestamp")
            ts_val = None
            if isinstance(ts, (int, float)):
                ts_val = float(ts)
            elif isinstance(ts, str):
                try:
                    ts_val = float(ts)
                except ValueError:
                    ts_val = None
            completed.append((ts_val, away, home, a_i, h_i, away_b2b, home_b2b))

        if len(completed) < 200:
            return

        has_ts = any(ts_val is not None for ts_val, *_ in completed)
        if has_ts:
            completed.sort(key=lambda x: x[0] if x[0] is not None else float("inf"))

        # Use multiple rolling time splits to reduce overfitting.
        # Only safe when we have timestamps; otherwise fall back to a single split.
        if not has_ts:
            train_frac = 0.7
            train_n = max(50, int(len(completed) * train_frac))
            val = completed[train_n:]
            if len(val) < 80:
                return
            val_splits = [val]
        else:
            total_n = len(completed)
            candidate_train_fracs = [0.55, 0.6, 0.65, 0.7, 0.75]
            val_splits = []
            for tf in candidate_train_fracs:
                train_n = max(50, int(total_n * tf))
                val = completed[train_n:]
                # Require enough validation rows for a stable estimate.
                if len(val) >= 80 and train_n >= 200:
                    val_splits.append(val)
            # If we ended up with too few splits, fall back to one.
            if not val_splits:
                train_frac = 0.7
                train_n = max(50, int(len(completed) * train_frac))
                val = completed[train_n:]
                if len(val) < 80:
                    return
                val_splits = [val]

        # Precompute expected-goal features on each validation split.
        val_split_features = []
        for val in val_splits:
            away_expected_list = []
            home_expected_list = []
            p_cal_list = []
            y_list = []
            away_team_list = []
            home_team_list = []
            for _ts, away, home, a_i, h_i, away_b2b, home_b2b in val:
                sp = self.predict_score(
                    away,
                    home,
                    use_calibration=False,
                    away_b2b=away_b2b,
                    home_b2b=home_b2b,
                )
                away_expected = float(sp["away_expected"])
                home_expected = float(sp["home_expected"])
                diff = away_expected - home_expected
                total = away_expected + home_expected
                p_cal = self._calibrated_away_win_prob(diff, total)
                y = 1.0 if a_i > h_i else 0.0
                away_expected_list.append(away_expected)
                home_expected_list.append(home_expected)
                p_cal_list.append(float(p_cal))
                y_list.append(float(y))
                away_team_list.append(str(away))
                home_team_list.append(str(home))

            val_split_features.append(
                {
                    "away_expected": np.array(away_expected_list, dtype=float),
                    "home_expected": np.array(home_expected_list, dtype=float),
                    "p_cal": np.array(p_cal_list, dtype=float),
                    "y": np.array(y_list, dtype=float),
                    "away_team": away_team_list,
                    "home_team": home_team_list,
                }
            )

        # Keep tie allocation proportional (tie_gamma=1.0) for stability.
        ot_scales = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
        blends = [0.6, 0.7, 0.8, 0.85, 0.9, 1.0]  # blend toward calibration
        tie_gammas = [1.0]

        best_mean_acc = -1.0
        best_median_acc = -1.0
        best_mean_brier = float("inf")
        best_mean_logloss = float("inf")
        best_ot = self._ot_scale
        best_blend = self._ot_blend
        best_tie_gamma = float(getattr(self, "_ot_tie_gamma", 1.0))
        th = float(getattr(self, "_win_calibration", {}).get("threshold", 0.5))

        for tie_gamma in tie_gammas:
            for ot in ot_scales:
                # Precompute p_nb for each validation split (depends on ot + tie_gamma).
                p_nb_splits = []
                for feats in val_split_features:
                    away_mu = feats["away_expected"]
                    home_mu = feats["home_expected"]
                    away_teams = feats["away_team"]
                    home_teams = feats["home_team"]
                    p_nb = np.array(
                        [
                            self._neg_bin_away_win_with_ot(
                                float(away_mu[i]),
                                float(home_mu[i]),
                                ot,
                                self._get_dispersion_k(
                                    away_teams[i],
                                    home_teams[i],
                                    float(away_mu[i]),
                                    float(home_mu[i]),
                                ),
                                tie_gamma=float(tie_gamma),
                            )
                            for i in range(len(away_mu))
                        ],
                        dtype=float,
                    )
                    p_nb_splits.append(p_nb)

                for blend in blends:
                    accs = []
                    briers = []
                    loglosses = []
                    for s_idx, feats in enumerate(val_split_features):
                        p_final = float(blend) * feats["p_cal"] + (1.0 - float(blend)) * p_nb_splits[s_idx]
                        p_final = np.clip(p_final, 0.0, 1.0)
                        y_true = feats["y"]

                        preds = p_final >= th
                        accs.append(float(np.mean(preds == (y_true >= 0.5))))

                        briers.append(float(np.mean((p_final - y_true) ** 2)))
                        eps = 1e-6
                        p_safe = np.clip(p_final, eps, 1.0 - eps)
                        ll = -float(np.mean(y_true * np.log(p_safe) + (1.0 - y_true) * np.log(1.0 - p_safe)))
                        loglosses.append(ll)

                    mean_acc = float(np.mean(accs)) if accs else -1.0
                    median_acc = float(np.median(accs)) if accs else -1.0
                    mean_brier = float(np.mean(briers)) if briers else float("inf")
                    mean_logloss = float(np.mean(loglosses)) if loglosses else float("inf")

                    improved = False
                    eps = 1e-9
                    # Primary objective: maximize winner accuracy on the
                    # validation splits (matches backtest metric).
                    if mean_acc > best_mean_acc + eps:
                        improved = True
                    elif abs(mean_acc - best_mean_acc) <= eps:
                        if median_acc > best_median_acc + eps:
                            improved = True
                        elif abs(median_acc - best_median_acc) <= eps:
                            if mean_logloss < best_mean_logloss - eps:
                                improved = True
                            elif abs(mean_logloss - best_mean_logloss) <= eps:
                                if mean_brier < best_mean_brier - eps:
                                    improved = True

                    if improved:
                        best_mean_acc = mean_acc
                        best_median_acc = median_acc
                        best_mean_brier = mean_brier
                        best_mean_logloss = mean_logloss
                        best_ot = ot
                        best_blend = blend
                        best_tie_gamma = float(tie_gamma)

        self._ot_scale = float(best_ot)
        self._ot_blend = float(best_blend)
        self._ot_tie_gamma = float(best_tie_gamma)
        print(
            f"✅ Tuned OT/Blend (multi-split): OT_SCALE={self._ot_scale} "
            f"OT_BLEND={self._ot_blend} OT_TIE_GAMMA={self._ot_tie_gamma} (mean acc={best_mean_acc:.3f}, "
            f"median acc={best_median_acc:.3f}, mean brier={best_mean_brier:.4f}, mean logloss={best_mean_logloss:.4f})"
        )

    def _tune_max_goals(self) -> None:
        """Tune deterministic scoreline cap for winner accuracy."""
        if not self.prediction_history:
            return

        # We only compare winner side; ties are ignored for stability,
        # consistent with the rest of the winner-centric tuning code.
        completed = []
        for p in self.prediction_history:
            away = p.get("away_team")
            home = p.get("home_team")
            a = p.get("actual_away_score")
            h = p.get("actual_home_score")
            if not (away and home and a is not None and h is not None):
                continue
            try:
                a_i = int(a)
                h_i = int(h)
            except (TypeError, ValueError):
                continue
            if a_i == h_i:
                continue

            away_b2b = bool(p.get("away_back_to_back", False))
            home_b2b = bool(p.get("home_back_to_back", False))

            ts = p.get("timestamp")
            ts_val = None
            if isinstance(ts, (int, float)):
                ts_val = float(ts)
            elif isinstance(ts, str):
                try:
                    ts_val = float(ts)
                except ValueError:
                    ts_val = None

            completed.append((ts_val, away, home, a_i, h_i, away_b2b, home_b2b))

        if len(completed) < 200:
            return

        has_ts = any(ts_val is not None for ts_val, *_ in completed)
        if has_ts:
            completed.sort(key=lambda x: x[0] if x[0] is not None else float("inf"))

        candidate_train_fracs = [0.55, 0.6, 0.65, 0.7, 0.75]
        val_splits = []
        if has_ts:
            total_n = len(completed)
            for tf in candidate_train_fracs:
                train_n = max(50, int(total_n * tf))
                val = completed[train_n:]
                if len(val) >= 80 and train_n >= 200:
                    val_splits.append(val)
            if not val_splits:
                train_n = max(50, int(total_n * 0.7))
                val_splits = [completed[train_n:]] if len(completed[train_n:]) >= 80 else [completed[train_n:total_n]]
        else:
            train_n = max(50, int(len(completed) * 0.7))
            val_splits = [completed[train_n:]]

        max_goals_candidates = [9, 10, 11, 12]
        best_mg = int(getattr(self, "_max_goals", 10))
        best_mean_acc = -1.0
        best_mean_med_acc = -1.0

        # Validate each cap using recomputed predictions.
        current_mg = int(getattr(self, "_max_goals", 10))
        try:
            for mg in max_goals_candidates:
                self._max_goals = int(mg)
                split_accs = []
                for val in val_splits:
                    correct = 0
                    n = 0
                    for _ts, away, home, a_i, h_i, away_b2b, home_b2b in val:
                        pred = self.predict_score(
                            away,
                            home,
                            use_calibration=True,
                            away_b2b=away_b2b,
                            home_b2b=home_b2b,
                        )
                        pred_away_score = int(pred.get("away_score", 0))
                        pred_home_score = int(pred.get("home_score", 0))
                        pred_winner_is_away = pred_away_score > pred_home_score
                        actual_winner_is_away = a_i > h_i
                        if pred_winner_is_away == actual_winner_is_away:
                            correct += 1
                        n += 1

                    split_accs.append(correct / n if n else 0.0)

                mean_acc = float(np.mean(split_accs)) if split_accs else -1.0
                median_acc = float(np.median(split_accs)) if split_accs else -1.0

                if mean_acc > best_mean_acc + 1e-9 or (abs(mean_acc - best_mean_acc) <= 1e-9 and median_acc > best_mean_med_acc):
                    best_mean_acc = mean_acc
                    best_mean_med_acc = median_acc
                    best_mg = mg

            self._max_goals = best_mg
            print(f"✅ Tuned max_goals: max_goals={self._max_goals} (mean acc={best_mean_acc:.3f})")
        finally:
            self._max_goals = best_mg

    def _build_win_calibration(
        self,
        num_total_bins: int = 7,
        num_diff_bins: int = 18,
        alpha: float = 1.0,
        train_frac: float = 0.7,
        min_samples: int = 250,
    ):
        """
        Build a 2D empirical calibration:
          feature_1 = diff  = away_expected - home_expected
          feature_2 = total = away_expected + home_expected
          target     = P(away_wins | diff, total)

        Implementation:
          - Split training data into quantile bins over `total`
          - For each total-bin, build quantile bins over `diff`
          - Use Laplace smoothing in each (total-bin, diff-bin)
          - Keep a global 1D fallback calibration for sparsity.
        """
        if not self.prediction_history:
            return None

        completed = []
        for p in self.prediction_history:
            away = p.get("away_team")
            home = p.get("home_team")
            a = p.get("actual_away_score")
            h = p.get("actual_home_score")
            if not away or not home:
                continue
            if a is None or h is None:
                continue
            try:
                a_i = int(a)
                h_i = int(h)
            except (TypeError, ValueError):
                continue
            if a_i == h_i:
                continue  # ignore rare ties

            away_b2b = bool(p.get("away_back_to_back", False))
            home_b2b = bool(p.get("home_back_to_back", False))

            ts = p.get("timestamp")
            ts_val = None
            if isinstance(ts, (int, float)):
                ts_val = float(ts)
            elif isinstance(ts, str):
                # Try numeric timestamp first
                try:
                    ts_val = float(ts)
                except ValueError:
                    ts_val = None

            completed.append((ts_val, away, home, a_i, h_i, away_b2b, home_b2b))

        if len(completed) < min_samples:
            return None

        # Time-based split (if timestamps exist).
        has_ts = any(ts_val is not None for ts_val, *_ in completed)
        if has_ts:
            completed.sort(key=lambda x: x[0] if x[0] is not None else float("inf"))
        train_n = max(50, int(len(completed) * train_frac))
        train = completed[:train_n]
        val = completed[train_n:]

        def build_features(rows):
            d = []
            t = []
            y = []
            for _ts, away, home, a_i, h_i, away_b2b, home_b2b in rows:
                # Expected-goals from the model itself (no calibration for feature building).
                sp = self.predict_score(
                    away,
                    home,
                    use_calibration=False,
                    away_b2b=away_b2b,
                    home_b2b=home_b2b,
                )
                diff = float(sp["away_expected"]) - float(sp["home_expected"])
                total = float(sp["away_expected"]) + float(sp["home_expected"])
                d.append(diff)
                t.append(total)
                y.append(1.0 if a_i > h_i else 0.0)
            return np.array(d, dtype=float), np.array(t, dtype=float), np.array(y, dtype=float)

        diffs_train, totals_train, labels_train = build_features(train)
        diffs_val, totals_val, labels_val = build_features(val) if val else (np.array([]), np.array([]), np.array([]))

        if diffs_train.size < min_samples or diffs_val.size < 80:
            # Not enough validation signal; fall back to the provided defaults.
            pass

        if diffs_train.size < 50:
            return None

        def build_1d_calibration(x: np.ndarray, y: np.ndarray, bins: int, a: float):
            qs = np.linspace(0.0, 1.0, bins + 1)
            edges = np.quantile(x, qs)
            edges = np.unique(edges)
            if edges.size < 3:
                dmin = float(np.min(x))
                dmax = float(np.max(x))
                if dmax - dmin < 1e-6:
                    return None
                edges = np.linspace(dmin, dmax, bins + 1)

            rates = []
            counts = []
            global_rate = (float(y.sum()) + a) / (float(y.size) + 2.0 * a)

            for i in range(edges.size - 1):
                lo = edges[i]
                hi = edges[i + 1]
                if i == edges.size - 2:
                    mask = (x >= lo) & (x <= hi)
                else:
                    mask = (x >= lo) & (x < hi)
                c = int(mask.sum())
                if c == 0:
                    rates.append(global_rate)
                    counts.append(0)
                    continue
                w = float(y[mask].sum())
                rate = (w + a) / (c + 2.0 * a)
                rates.append(float(rate))
                counts.append(c)

            return {
                "edges": edges.astype(float).tolist(),
                "rates": rates,
                "counts": counts,
                "alpha": a,
            }

        def build_2d_calibration(dt, tt, y, n_total_bins: int, n_diff_bins: int, a: float):
            global_cal = build_1d_calibration(dt, y, n_diff_bins, a)
            if not global_cal:
                return None

            total_qs = np.linspace(0.0, 1.0, n_total_bins + 1)
            total_edges = np.quantile(tt, total_qs)
            total_edges = np.unique(total_edges)
            if total_edges.size < 3:
                return global_cal

            total_bins = []
            for i in range(total_edges.size - 1):
                lo_t = total_edges[i]
                hi_t = total_edges[i + 1]
                if i == total_edges.size - 2:
                    t_mask = (tt >= lo_t) & (tt <= hi_t)
                else:
                    t_mask = (tt >= lo_t) & (tt < hi_t)

                c_total = int(t_mask.sum())
                if c_total < 50:
                    total_bins.append({"diff_cal": global_cal, "counts": c_total})
                    continue

                diff_slice = dt[t_mask]
                label_slice = y[t_mask]
                diff_cal = build_1d_calibration(diff_slice, label_slice, n_diff_bins, a)
                if not diff_cal:
                    diff_cal = global_cal

                total_bins.append({"diff_cal": diff_cal, "counts": c_total})

            return {
                "total_edges": total_edges.astype(float).tolist(),
                "total_bins": total_bins,
                "alpha": a,
                "fallback": global_cal,
            }

        def prob_from_cal(cal, diff: float, total: float) -> float:
            # 1D fallback calibration
            if "edges" in cal and "rates" in cal:
                edges = np.array(cal["edges"], dtype=float)
                rates = np.array(cal["rates"], dtype=float)
                if edges.size < 3:
                    return 0.5
                idx = int(np.searchsorted(edges, diff, side="right") - 1)
                idx = max(0, min(idx, rates.size - 1))
                return float(max(0.01, min(0.99, rates[idx])))

            total_edges = np.array(cal.get("total_edges", []), dtype=float)
            total_bins = cal.get("total_bins", [])
            fallback = cal.get("fallback")
            if total_edges.size < 3 or not total_bins or fallback is None:
                return 0.5

            t_idx = int(np.searchsorted(total_edges, total, side="right") - 1)
            t_idx = max(0, min(t_idx, len(total_bins) - 1))
            diff_cal = total_bins[t_idx].get("diff_cal") or fallback
            if not diff_cal or "edges" not in diff_cal:
                return 0.5

            edges = np.array(diff_cal.get("edges", []), dtype=float)
            rates = np.array(diff_cal.get("rates", []), dtype=float)
            if edges.size < 3:
                return 0.5
            d_idx = int(np.searchsorted(edges, diff, side="right") - 1)
            d_idx = max(0, min(d_idx, rates.size - 1))
            return float(max(0.01, min(0.99, rates[d_idx])))

        # Build the 2D calibration directly (fixed bin counts). This is the
        # most stable/accurate configuration observed in backtests.
        best_cal = build_2d_calibration(
            diffs_train,
            totals_train,
            labels_train,
            num_total_bins,
            num_diff_bins,
            alpha,
        )
        if not best_cal:
            return None

        best_cal["threshold"] = 0.5
        return best_cal

    def _calibrated_away_win_prob(self, diff: float, total: float) -> float:
        """Map (diff, total) -> calibrated P(away wins)."""
        cal = getattr(self, "_win_calibration", None)
        if not cal:
            return 0.5
        # Backward compatibility if calibration is 1D-only
        if "edges" in cal and "rates" in cal:
            edges = np.array(cal["edges"], dtype=float)
            rates = np.array(cal["rates"], dtype=float)
            if edges.size < 3:
                return 0.5
            idx = int(np.searchsorted(edges, diff, side="right") - 1)
            idx = max(0, min(idx, rates.size - 1))
            return float(max(0.01, min(0.99, rates[idx])))

        total_edges = np.array(cal.get("total_edges", []), dtype=float)
        total_bins = cal.get("total_bins", [])
        fallback = cal.get("fallback")

        if total_edges.size < 3 or not total_bins or fallback is None:
            # Use fallback 1D calibration (diff only)
            if "edges" in fallback and "rates" in fallback:
                edges = np.array(fallback["edges"], dtype=float)
                rates = np.array(fallback["rates"], dtype=float)
                if edges.size < 3:
                    return 0.5
                d_idx = int(np.searchsorted(edges, diff, side="right") - 1)
                d_idx = max(0, min(d_idx, rates.size - 1))
                return float(max(0.01, min(0.99, rates[d_idx])))
            return 0.5

        # Pick total bin
        t_idx = int(np.searchsorted(total_edges, total, side="right") - 1)
        t_idx = max(0, min(t_idx, len(total_bins) - 1))
        diff_cal = total_bins[t_idx].get("diff_cal") or fallback
        if not diff_cal:
            return 0.5

        edges = np.array(diff_cal.get("edges", []), dtype=float)
        rates = np.array(diff_cal.get("rates", []), dtype=float)
        if edges.size < 3:
            return 0.5

        d_idx = int(np.searchsorted(edges, diff, side="right") - 1)
        d_idx = max(0, min(d_idx, rates.size - 1))
        return float(max(0.01, min(0.99, rates[d_idx])))
    
    def _recency_weight(self, values: list, half_life: int = 10) -> float:
        """Weighted average with exponential recency decay.
        
        Most recent game gets weight 1.0, game 10 games ago gets 0.5,
        game 20 games ago gets 0.25, etc.
        """
        if not values:
            return 0.0
        n = len(values)
        weights = []
        for i in range(n):
            # Index 0 = oldest, index n-1 = most recent
            recency = n - 1 - i  # 0 for newest
            w = 0.5 ** (recency / half_life)
            weights.append(w)
        
        # Reverse so newest has highest weight
        weights = weights[::-1]
        
        total_w = sum(weights)
        if total_w == 0:
            return np.mean(values)
        return sum(v * w for v, w in zip(values, weights)) / total_w
    
    def _sanitize_pp_pk(self, values: list) -> list:
        """Fix corrupt PP%/PK% values.
        
        Raw data has PP% values like 150%, 400% (likely PP goals * 100 / PP opportunities
        with small denominators) and PK% values like -300%. Clamp to 0-100%.
        """
        sanitized = []
        for v in values:
            try:
                val = float(v)
                val = max(0.0, min(100.0, val))  # Clamp to 0-100
                sanitized.append(val)
            except (ValueError, TypeError):
                pass
        return sanitized
    
    def _precompute_averages(self):
        """Pre-compute per-team averages with recency weighting."""
        for team, venues in self.team_stats.get('teams', {}).items():
            avgs = {'home': {}, 'away': {}, 'combined': {}}
            
            for venue in ['home', 'away']:
                vdata = venues.get(venue, {})
                metrics = {}
                
                for key in ['goals', 'opp_goals', 'xg', 'opp_xg', 'gs', 'shots',
                           'hdc', 'hdca', 'hits', 'blocked_shots', 'takeaways',
                           'giveaways', 'faceoff_pct', 'corsi_pct', 'rebounds',
                           'rush_shots', 'cycle_shots', 'fc', 'rush', 'ozs', 'dzs']:
                    vals = vdata.get(key, [])
                    numeric = []
                    for v in vals:
                        try:
                            numeric.append(float(v))
                        except (ValueError, TypeError):
                            pass
                    # Use recency-weighted average
                    metrics[key] = self._recency_weight(numeric) if numeric else None
                    # Also store flat average for comparison
                    metrics[f'{key}_flat'] = np.mean(numeric) if numeric else None
                    
                    # Store short-term form (Last 5, Last 10)
                    if numeric:
                        l5 = numeric[-5:] if len(numeric) >= 5 else numeric
                        l10 = numeric[-10:] if len(numeric) >= 10 else numeric
                        metrics[f'{key}_l5'] = np.mean(l5)
                        metrics[f'{key}_l10'] = np.mean(l10)
                    else:
                        metrics[f'{key}_l5'] = None
                        metrics[f'{key}_l10'] = None
                
                # Sanitize PP% and PK%
                pp_raw = vdata.get('power_play_pct', [])
                pk_raw = vdata.get('penalty_kill_pct', [])
                pp_clean = self._sanitize_pp_pk(pp_raw)
                pk_clean = self._sanitize_pp_pk(pk_raw)
                metrics['power_play_pct'] = self._recency_weight(pp_clean) if pp_clean else 20.0
                metrics['penalty_kill_pct'] = self._recency_weight(pk_clean) if pk_clean else 80.0
                
                metrics['n_games'] = len(vdata.get('goals', []))
                
                # xG luck (using flat average for stability)
                flat_goals = metrics.get('goals_flat') or self.LEAGUE_AVG_GF
                flat_xg = metrics.get('xg_flat') or self.LEAGUE_AVG_GF
                metrics['xg_luck'] = flat_goals - flat_xg
                
                avgs[venue] = metrics
            
            # Combined (weighted by games played)
            h_n = avgs['home'].get('n_games', 0)
            a_n = avgs['away'].get('n_games', 0)
            total_n = h_n + a_n
            if total_n > 0:
                combined = {}
                for key in avgs['home']:
                    if key == 'n_games':
                        combined[key] = total_n
                        continue
                    h_val = avgs['home'].get(key)
                    a_val = avgs['away'].get(key)
                    if h_val is not None and a_val is not None:
                        combined[key] = (h_val * h_n + a_val * a_n) / total_n
                    elif h_val is not None:
                        combined[key] = h_val
                    elif a_val is not None:
                        combined[key] = a_val
                    else:
                        combined[key] = None
                avgs['combined'] = combined
            
            self.team_averages[team] = avgs
    
    def _build_h2h_records(self):
        """Build head-to-head records from prediction history."""
        self.h2h_cache = {}
        for pred in self.prediction_history:
            if not pred.get('actual_winner'):
                continue
            away = pred.get('away_team', '')
            home = pred.get('home_team', '')
            if not away or not home:
                continue
            
            away_score = pred.get('actual_away_score')
            home_score = pred.get('actual_home_score')
            if away_score is None or home_score is None:
                continue
            
            # Store from both perspectives
            key_away = f"{away}_vs_{home}"
            key_home = f"{home}_vs_{away}"
            
            if key_away not in self.h2h_cache:
                self.h2h_cache[key_away] = []
            if key_home not in self.h2h_cache:
                self.h2h_cache[key_home] = []
            
            self.h2h_cache[key_away].append({
                'gf': away_score, 'ga': home_score,
                'won': away_score > home_score,
            })
            self.h2h_cache[key_home].append({
                'gf': home_score, 'ga': away_score,
                'won': home_score > away_score,
            })
    
    def _get_h2h_adjustment(self, team: str, opponent: str) -> float:
        """Get H2H scoring adjustment for team vs specific opponent.
        
        Returns goals above/below team's average when facing this opponent.
        """
        key = f"{team}_vs_{opponent}"
        records = self.h2h_cache.get(key, [])
        if len(records) < 2:
            return 0.0
        
        h2h_gf = np.mean([r['gf'] for r in records])
        team_avg_gf = self._get_team_metric(team, 'goals_flat', 'combined')
        
        # How many more/fewer goals does this team score vs this opponent?
        diff = h2h_gf - team_avg_gf
        
        # Dampen based on sample size (need at least 3-4 games for signal)
        confidence = min(1.0, len(records) / 4.0) * 0.5  # Max 50% weight
        return diff * confidence
    
    def _get_team_metric(self, team: str, metric: str, venue: str = 'combined') -> float:
        """Get a team's average for a metric, with league-average fallback."""
        defaults = {
            'goals': self.LEAGUE_AVG_GF, 'opp_goals': self.LEAGUE_AVG_GF,
            'goals_flat': self.LEAGUE_AVG_GF, 'opp_goals_flat': self.LEAGUE_AVG_GF,
            'xg': 3.0, 'opp_xg': 3.0,
            'gs': 5.7, 'hdc': 7.0, 'hdca': 7.0, 'shots': 28.0,
            'power_play_pct': 20.0, 'penalty_kill_pct': 80.0,
            'faceoff_pct': 50.0, 'corsi_pct': 50.0,
            'xg_luck': 0.0, 'rush_shots': 4.0, 'rebounds': 3.0,
        }
        team_data = self.team_averages.get(team.upper(), {}).get(venue, {})
        val = team_data.get(metric)
        if val is not None and not np.isnan(val):
            return val
        return defaults.get(metric, 0.0)
    
    def predict_score(self, away_team: str, home_team: str,
                     away_goalie: str = None, home_goalie: str = None,
                     game_date: str = None,
                     away_b2b: bool = False, home_b2b: bool = False,
                     away_3_in_4: bool = False, home_3_in_4: bool = False,
                     vegas_odds: Dict = None,
                     use_calibration: bool = True,
                     is_playoff: bool = False,
                     series_status: str = None) -> Dict:
        """
        Predict realistic game score.
        
        Returns:
            Dict with away_score, home_score, total_goals, confidence, factors
        """
        away = away_team.upper()
        home = home_team.upper()
        
        # ─── 1. Game Score baseline (r=0.642 with goals) ───
        # Recency-weighted GS average
        away_gs = self._get_team_metric(away, 'gs', 'away')
        home_gs = self._get_team_metric(home, 'gs', 'home')
        gs_to_goals = lambda gs: max(1.0, 0.5 * gs)
        away_gs_goals = gs_to_goals(away_gs)
        home_gs_goals = gs_to_goals(home_gs)
        
        # ─── 2. xG baseline (recency-weighted) ───
        away_xg = self._get_team_metric(away, 'xg', 'away')
        home_xg = self._get_team_metric(home, 'xg', 'home')
        
        # ─── 3. Opponent defensive quality ───
        away_opp_ga = self._get_team_metric(home, 'opp_goals', 'home')
        home_opp_ga = self._get_team_metric(away, 'opp_goals', 'away')
        away_def_raw = away_opp_ga / self.LEAGUE_AVG_GF
        home_def_raw = home_opp_ga / self.LEAGUE_AVG_GF
        away_def_factor = 1.0 + (away_def_raw - 1.0) * 0.5
        home_def_factor = 1.0 + (home_def_raw - 1.0) * 0.5
        
        # ─── 4. Special teams (sanitized PP%) ───
        away_pp = self._get_team_metric(away, 'power_play_pct', 'away')
        home_pp = self._get_team_metric(home, 'power_play_pct', 'home')
        away_pk = self._get_team_metric(away, 'penalty_kill_pct', 'away')
        home_pk = self._get_team_metric(home, 'penalty_kill_pct', 'home')
        # PP vs opponent PK matchup
        away_pp_effectiveness = (away_pp / 100.0) * (1.0 - home_pk / 100.0)
        home_pp_effectiveness = (home_pp / 100.0) * (1.0 - away_pk / 100.0)
        away_pp_factor = 1.0 + (away_pp_effectiveness - 0.04) * 3.0  # 4% is ~league avg
        home_pp_factor = 1.0 + (home_pp_effectiveness - 0.04) * 3.0
        
        # ─── 5. High Danger Chances ───
        away_hdc = self._get_team_metric(away, 'hdc', 'away')
        home_hdc = self._get_team_metric(home, 'hdc', 'home')
        away_hdc_factor = away_hdc / 7.0
        home_hdc_factor = home_hdc / 7.0
        
        # ─── 6. xG luck regression ───
        away_luck = self._get_team_metric(away, 'xg_luck', 'away')
        home_luck = self._get_team_metric(home, 'xg_luck', 'home')
        away_luck_adj = -away_luck * self.XG_LUCK_REGRESSION
        home_luck_adj = -home_luck * self.XG_LUCK_REGRESSION
        
        # ─── 7. Home/Away venue adjustment (Self-Learning) ───
        # Instead of a flat HOME_ICE_BOOST for all teams, use per-team venue
        # splits learned from actual outcomes. BOS (23-7 at home) gets a big
        # boost, VAN (8-25 at home) gets penalized.
        away_venue_adj = self._get_venue_adjustment(away, 'away')
        home_venue_adj = self._get_venue_adjustment(home, 'home')
        # Fallback: if no learned data, use the flat league-wide home boost
        if away_venue_adj == 0.0 and home_venue_adj == 0.0:
            home_boost = self.HOME_ICE_BOOST
        else:
            home_boost = 0.0  # Per-team adjustments replace the flat boost
        
        # ─── 8. Division strength ───
        div_strength = {'Central': 0.10, 'Atlantic': 0.00, 'Metropolitan': 0.00, 'Pacific': -0.10}
        away_div_adj = div_strength.get(TEAM_TO_DIV.get(away, ''), 0.0)
        home_div_adj = div_strength.get(TEAM_TO_DIV.get(home, ''), 0.0)
        
        # ─── 9. (Finishing profiles removed — noise, captured by xG luck) ───
        
        # ─── 10. Head-to-head adjustment (NEW) ───
        away_h2h_adj = self._get_h2h_adjustment(away, home)
        home_h2h_adj = self._get_h2h_adjustment(home, away)
        
        # ─── 11. Back-to-back penalty (NEW) ───
        away_b2b_adj = -self.B2B_PENALTY if away_b2b else 0.0
        home_b2b_adj = -self.B2B_PENALTY if home_b2b else 0.0
        
        # ─── 12. Goalie adjustment (NEW) ───
        # An opposing goalie's quality affects the shooting team's score.
        # Home goalie (at home) affects Away team; Away goalie (away) affects Home team.
        away_goalie_adj = self._get_goalie_adjustment(home_goalie, home, 'home')
        home_goalie_adj = self._get_goalie_adjustment(away_goalie, away, 'away')
        
        # ─── 13. Short-Term Form (Momentum) ───
        # Compare last 5 and last 10 xG against season-long xG to detect "hot" or "cold" streaks.
        away_xg_l5 = self._get_team_metric(away, 'xg_l5', 'away')
        away_xg_l10 = self._get_team_metric(away, 'xg_l10', 'away')
        away_xg_flat = self._get_team_metric(away, 'xg_flat', 'away')
        
        home_xg_l5 = self._get_team_metric(home, 'xg_l5', 'home')
        home_xg_l10 = self._get_team_metric(home, 'xg_l10', 'home')
        home_xg_flat = self._get_team_metric(home, 'xg_flat', 'home')
        
        away_momentum_adj = 0.0
        if away_xg_l5 and away_xg_l10 and away_xg_flat:
            # L5 forms the sharpest momentum, L10 smooths it out.
            momentum = ((away_xg_l5 - away_xg_flat) * 0.6) + ((away_xg_l10 - away_xg_flat) * 0.4)
            away_momentum_adj = max(-0.4, min(0.4, momentum * 0.5))  # Cap the impact
            
        home_momentum_adj = 0.0
        if home_xg_l5 and home_xg_l10 and home_xg_flat:
            momentum = ((home_xg_l5 - home_xg_flat) * 0.6) + ((home_xg_l10 - home_xg_flat) * 0.4)
            home_momentum_adj = max(-0.4, min(0.4, momentum * 0.5))
        
        # ─── COMBINE: Weighted expected goals ───
        away_raw = (
            self.W_GS * away_gs_goals +
            self.W_XG * away_xg +
            self.W_PP * (self.LEAGUE_AVG_GF * away_pp_factor) +
            self.W_HDC * (self.LEAGUE_AVG_GF * away_hdc_factor) +
            self.W_CONTEXT * self.LEAGUE_AVG_GF
        )
        home_raw = (
            self.W_GS * home_gs_goals +
            self.W_XG * home_xg +
            self.W_PP * (self.LEAGUE_AVG_GF * home_pp_factor) +
            self.W_HDC * (self.LEAGUE_AVG_GF * home_hdc_factor) +
            self.W_CONTEXT * self.LEAGUE_AVG_GF
        )
        
        # ─── Calibrate to league average (3.03 GF/game) ───
        # Raw weighted sum runs ~3.5-3.8, so scale down to league reality
        raw_avg = (away_raw + home_raw) / 2.0
        if raw_avg > 0:
            calibration = self.LEAGUE_AVG_GF / raw_avg
        else:
            calibration = 1.0
        away_expected = away_raw * calibration
        home_expected = home_raw * calibration
        
        # Apply Playoff Scoring Environment Adjustment (~6% reduction in playoffs)
        if is_playoff:
            away_expected *= 0.94
            home_expected *= 0.94
        
        # Apply multiplicative modifiers
        away_expected *= away_def_factor
        home_expected *= home_def_factor
        
        # Apply additive adjustments
        away_expected += away_luck_adj
        away_expected += away_div_adj
        away_expected += away_venue_adj
        away_expected += away_h2h_adj
        away_expected += away_b2b_adj
        away_expected += away_goalie_adj
        away_expected += away_momentum_adj
        
        home_expected += home_luck_adj
        home_expected += home_div_adj
        home_expected += home_venue_adj
        home_expected += home_boost
        home_expected += home_h2h_adj
        home_expected += home_b2b_adj
        home_expected += home_goalie_adj
        home_expected += home_momentum_adj
        
        # ─── 14. Phase 3: 3-in-4 Fatigue (Context Only) ───
        # Note: Triangulation Audit (N=923) showed that a hard goal penalty
        # for 3-in-4 reduces winner accuracy by ~5%. We now handle this
        # via the High-Risk alerting in DailyPredictionNotifier rather than
        # a hard goal offset.
        pass
        
        # ─── 15. Phase 4: Time Zone Jet Lag (Context Only) ───
        # Note: Triangulation Audit (N=923) showed that a hard goal penalty
        # for Jet Lag reduces winner accuracy by ~4%. We keep TEAM_TIMEZONES
        # for ML context, but remove the hard goal offset.
        pass
        
        # ─── 16. Scoring Bias Correction (Self-Learning) ───
        # If the model has been systematically over-predicting totals,
        # _scoring_bias will be positive and we subtract it from both sides.
        # This closes the feedback loop so the model corrects itself over time.
        if hasattr(self, '_scoring_bias') and self._scoring_bias != 0:
            away_expected -= self._scoring_bias
            home_expected -= self._scoring_bias
        
        # ─── 17. Per-Team Scoring Environment (Self-Learning) ───
        # Learned from actual game outcomes: some teams consistently play in
        # high-scoring games (e.g. PIT avg 7.0 total) while others grind out
        # low-scoring affairs (e.g. NYR avg 5.76). Apply each team's tendency.
        away_env = self._get_team_env_adjustment(away)
        home_env = self._get_team_env_adjustment(home)
        away_expected += away_env
        home_expected += home_env
        
        # ─── Clamp to realistic range ───
        # NHL teams very rarely exceed 4.5 xG in a game. Keeping the cap
        # tight prevents the deterministic rounding from producing
        # unrealistic 5-4, 6-5 scorelines.
        away_expected = max(1.5, min(4.5, away_expected))
        home_expected = max(1.5, min(4.5, home_expected))
        
        # ─── Winner selection ───
        # If calibration is available, use it to learn the empirical win
        # probability vs (away_expected - home_expected). Otherwise fall back
        # to the Poisson-based win probability heuristic.
        max_goals = int(getattr(self, "_max_goals", 10))

        winner_side = None
        away_win_prob_final = None
        home_win_prob_final = None
        if use_calibration and getattr(self, "_win_calibration", None):
            diff = float(away_expected - home_expected)
            total = float(away_expected + home_expected)
            p_cal = self._calibrated_away_win_prob(diff, total)
            # Blend calibration with an OT-aware Negative Binomial model.
            # This captures systematic OT variance and overdispersion not
            # fully represented by pure expected-goals calibration.
            p_nb_ot = self._neg_bin_away_win_with_ot(
                away_expected,
                home_expected,
                float(getattr(self, "_ot_scale", 0.75)),
                float(self._get_dispersion_k(away, home, away_expected, home_expected)),
                tie_gamma=float(getattr(self, "_ot_tie_gamma", 1.0)),
            )
            blend = float(getattr(self, "_ot_blend", 0.85))
            away_win_prob = blend * p_cal + (1.0 - blend) * p_nb_ot
            th = float(getattr(self, "_win_calibration", {}).get("threshold", 0.5))
            winner_side = "away" if away_win_prob >= th else "home"
            away_win_prob_final = float(max(0.0, min(1.0, away_win_prob)))
            home_win_prob_final = float(1.0 - away_win_prob_final)
        else:
            # Poisson-based win probability (with proportional tie allocation)
            import math

            max_prob_goals = 15
            away_lam = float(away_expected)
            home_lam = float(home_expected)

            pmf_away = [
                math.exp(-away_lam) * (away_lam ** k) / math.factorial(k)
                for k in range(max_prob_goals + 1)
            ]
            pmf_home = [
                math.exp(-home_lam) * (home_lam ** k) / math.factorial(k)
                for k in range(max_prob_goals + 1)
            ]

            p_away_win = 0.0
            p_home_win = 0.0
            p_tie = 0.0

            for a in range(max_prob_goals + 1):
                pa = pmf_away[a]
                if pa == 0.0:
                    continue
                for h in range(max_prob_goals + 1):
                    ph = pmf_home[h]
                    if a > h:
                        p_away_win += pa * ph
                    elif h > a:
                        p_home_win += pa * ph
                    else:
                        p_tie += pa * ph

            tie_total = p_tie
            total_lam = away_lam + home_lam
            if total_lam > 0:
                away_ot_share = away_lam / total_lam
                home_ot_share = home_lam / total_lam
            else:
                away_ot_share = 0.5
                home_ot_share = 0.5

            away_win_total = p_away_win + tie_total * away_ot_share
            home_win_total = p_home_win + tie_total * home_ot_share
            winner_side = "away" if away_win_total > home_win_total else "home"
            away_win_prob_final = float(max(0.0, min(1.0, away_win_total)))
            home_win_prob_final = float(max(0.0, min(1.0, home_win_total)))


        # ─── Deterministic scoreline (MAP under NB) ───
        # Winner accuracy should be driven by `away_win_prob` / `winner_side`,
        # not by a random score draw. We therefore emit a *deterministic* most-
        # likely scoreline under an overdispersed (Negative Binomial) goal model.
        away_score, home_score = self._map_scoreline_nb(
            away=away,
            home=home,
            away_mu=float(away_expected),
            home_mu=float(home_expected),
            winner_side=str(winner_side) if winner_side else None,
        )
        
        # ─── Generate analysis factors ───
        factors = self._generate_factors(
            away, home, away_expected, home_expected,
            away_luck, home_luck, away_goalie, home_goalie,
            away_hdc, home_hdc, away_def_factor, home_def_factor,
            away_b2b, home_b2b,
            away_h2h_adj, home_h2h_adj,
            away_momentum_adj, home_momentum_adj
        )
        
        # ─── Confidence ───
        confidence = self._calculate_confidence(away, home, away_expected, home_expected)
        
        return {
            'away_score': away_score,
            'home_score': home_score,
            'away_xg': round(away_expected, 2),
            'home_xg': round(home_expected, 2),
            'away_expected': away_expected,
            'home_expected': home_expected,
            'away_win_prob': away_win_prob_final if away_win_prob_final is not None else 0.5,
            'home_win_prob': home_win_prob_final if home_win_prob_final is not None else 0.5,
            'total_goals': away_score + home_score,
            'confidence': confidence,
            'factors': factors,
        }
    
    def _get_goalie_data(self, goalie_name: str) -> Optional[Dict]:
        """Find goalie data by name."""
        if not goalie_name or goalie_name == 'TBD' or not self.goalie_stats:
            return None
        
        # Exact match
        if goalie_name in self.goalie_names:
            return self.goalie_stats[self.goalie_names[goalie_name]]
        
        # Partial match
        for name, gid in self.goalie_names.items():
            if goalie_name.lower() in name.lower() or name.lower() in goalie_name.lower():
                return self.goalie_stats[gid]
        return None

    def _get_goalie_adjustment(self, goalie_name: str, team: str, venue: str) -> float:
        """Get scoring adjustment based on opposing goalie quality.
        
        A strong opposing goalie reduces expected goals; a weak one increases them.
        Uses GSAX/game from comprehensive goalie_stats.
        """
        gs = self._get_goalie_data(goalie_name)
        
        if gs and gs.get('games', 0) >= 1:
            # 1. Backup Goalie Penalty (Phase 3 Improvement)
            # If a goalie has played very few games relative to the season, they are likely a backup/AHL call-up
            backup_penalty = 0.0
            team_games = self._get_team_metric(team, 'n_games', 'combined')
            
            # If we're deep enough into the season (e.g., > 20 games) and the goalie has played < 25% of games
            if team_games > 20 and gs.get('games', 0) < (team_games * 0.25):
                # Apply a severe +0.35 to +0.50 expected goals penalty to the team starting them
                backup_penalty = 0.40
                if gs.get('games', 0) < 5:
                    backup_penalty = 0.50 # AHL call-up or extreme backup
            
            # 2. Base GSAX Adjustment
            if gs.get('games', 0) >= 5:
                # Positive GSAX means goalie is saving more than expected -> reduces opponent goals
                gsax_pg = gs.get('gsax_per_game', 0.0)
                
                # Venue Adjustment (Home/Away Splits)
                venue_adj = 0.0
                home_sv = gs.get('home_sv_pct', 0)
                away_sv = gs.get('away_sv_pct', 0)
                if home_sv > 0 and away_sv > 0:
                    diff = home_sv - away_sv
                    if abs(diff) > 0.015: # Significant split (> 1.5% SV%)
                        # Scale: 0.010 SV% diff ~ 0.25 goals per game adjustment
                        if venue == 'home':
                            venue_adj = diff * 25.0 # Positive diff = bonus at home
                        else:
                            venue_adj = -diff * 25.0 # Positive diff = penalty away
                        
                        # Cap venue adjustment at +/- 0.4 goals
                        venue_adj = max(-0.4, min(0.4, venue_adj))
                
                # Rebound Adjustment (High rebound rate = more goals allowed)
                reb_adj = 0.0
                reb_rate = gs.get('rebound_rate', 0.075) # League avg ~7.5%
                if reb_rate > 0.08:
                    # Every 1% above 8% adds 0.05 goals
                    reb_adj = (reb_rate - 0.08) * 5.0
                    reb_adj = min(0.3, reb_adj) # Max 0.3 goal penalty
                
                # Angle Adjustment (Acute angle vulnerability)
                angle_adj = 0.0
                acute_sv = gs.get('acute_angle_sv_pct', 0)
                center_sv = gs.get('center_angle_sv_pct', 0)
                if acute_sv > 0 and center_sv > 0:
                    # If much worse on sides than center
                    if center_sv - acute_sv > 0.015:
                        angle_adj = (center_sv - acute_sv) * 10.0
                        angle_adj = min(0.2, angle_adj)
                
                # Base GSAX adjustment (0.8 scale) + Modifiers + Backup Penalty
                # Note: total_adj is added to expected goals, so positive = more goals for the shooting team
                total_adj = (-gsax_pg * 0.8) - venue_adj + reb_adj + angle_adj + backup_penalty
                return total_adj
            else:
                return backup_penalty
        
        # If we have no data on the goalie (e.g. unconfirmed lineup), assume league-average.
        # Previously this was +0.50 which inflated both sides by a full goal when
        # lineups weren't available, causing systemic 5-4 / 4-3 predictions.
        return 0.0
    
    def _generate_factors(self, away, home, away_exp, home_exp,
                          away_luck, home_luck, away_goalie, home_goalie,
                          away_hdc, home_hdc, away_def, home_def,
                          away_b2b, home_b2b,
                          away_h2h_adj, home_h2h_adj,
                          away_momentum, home_momentum) -> Dict:
        """Generate human-readable analysis factors."""
        factors = {
            'pace': 'Neutral',
            'goalie_away': 'Neutral',
            'goalie_home': 'Neutral',
            'situation': 'Neutral',
        }
        
        total_exp = away_exp + home_exp
        if total_exp > 7.5:
            factors['pace'] = "🔥 High Tempo (Offense Boost)"
        elif total_exp < 5.5:
            factors['pace'] = "🧊 Grinding/Defensive Pace"
        
        # Goalie context
        is_away_home = False # used to pass to venue check
        for g_name, label in [(away_goalie, 'goalie_away'), (home_goalie, 'goalie_home')]:
            gs = self._get_goalie_data(g_name)
            if not gs or gs.get('games', 0) < 5:
                continue
            
            # Determine if this goalie is home or away right now
            is_home_for_this_game = (label == 'goalie_home')
            opp_team = away if is_home_for_this_game else home
            
            gsax = gs.get('gsax_total', 0)
            rebound_rate = gs.get('rebound_rate', 0)
            glv = gs.get('glove_sv_pct', 0)
            blk = gs.get('blocker_sv_pct', 0)
            goalie_games = gs.get('games', 0)
            
            warnings = []
            
            # Backup Goalie Penalty
            team_games = self._get_team_metric(opp_team, 'n_games', 'combined')
            if team_games > 20 and goalie_games < (team_games * 0.25):
                warnings.append("🚨 SEVERE: Backup Penalty")
            
            # Overall quality
            if gsax > 8.0:
                factors[label] = f"🧱 Elite Goalie ({g_name}, +{gsax:.1f} GSAX)"
            elif gsax < -8.0:
                factors[label] = f"⚠️ Struggling Goalie ({g_name}, {gsax:.1f} GSAX)"
                
            # Rebounds
            if rebound_rate > 0.09:
                warnings.append("Juicy Rebounds")
                
            # Off-wing weakness (significant differential)
            if glv > 0 and blk > 0:
                if glv - blk > 0.04:
                    warnings.append(f"Blocker Vuln ({(glv-blk)*100:.1f}%)")
                elif blk - glv > 0.04:
                    warnings.append(f"Glove Vuln ({(blk-glv)*100:.1f}%)")
                    
            # Shot types and angles
            if gs.get('slap_shots', 0) > 20 and gs.get('slap_sv_pct', 1.0) < 0.85:
                warnings.append("Struggles vs Slapshots")
            if gs.get('acute_angle_shots', 0) > 20 and gs.get('acute_angle_sv_pct', 1.0) < 0.88:
                warnings.append("Struggles on Sharp Angles")
                
            # Venue splits
            home_sv = gs.get('home_sv_pct', 0)
            away_sv = gs.get('away_sv_pct', 0)
            if home_sv > 0 and away_sv > 0:
                if is_home_for_this_game and (home_sv - away_sv > 0.025):
                    warnings.append(f"Much Better at Home ({home_sv:.3f} vs {away_sv:.3f})")
                elif not is_home_for_this_game and (home_sv - away_sv > 0.025):
                    warnings.append(f"Struggles on Road ({away_sv:.3f} vs {home_sv:.3f})")
                    
            # Head-to-Head
            opp_stats = gs.get('opponent_stats', {}).get(opp_team)
            if opp_stats and opp_stats['shots'] >= 25:
                # Calculate h2h save %
                h2h_sv = (opp_stats['shots'] - opp_stats['goals']) / opp_stats['shots']
                if h2h_sv < 0.875:
                    warnings.append(f"Owned by {opp_team} ({h2h_sv:.3f} SV%)")
                elif h2h_sv > 0.935:
                    warnings.append(f"Dominates {opp_team} ({h2h_sv:.3f} SV%)")
            
            if warnings and factors[label] == 'Neutral':
                factors[label] = f"🥅 {g_name} ({', '.join(warnings)})"
            elif warnings:
                factors[label] += f" | {', '.join(warnings)}"
        
        # Situational
        situations = []
        if away_b2b:
            situations.append(f"😴 {away} on back-to-back")
        if home_b2b:
            situations.append(f"😴 {home} on back-to-back")
        if abs(away_h2h_adj) > 0.2:
            emoji = "💪" if away_h2h_adj > 0 else "😰"
            situations.append(f"{emoji} {away} H2H edge ({away_h2h_adj:+.1f})")
        if abs(home_h2h_adj) > 0.2:
            emoji = "💪" if home_h2h_adj > 0 else "😰"
            situations.append(f"{emoji} {home} H2H edge ({home_h2h_adj:+.1f})")
        if abs(away_luck) > 0.4:
            if away_luck < -0.4:
                situations.append(f"📈 {away} due for regression (luck: {away_luck:+.2f})")
            else:
                situations.append(f"📉 {away} overperforming (luck: {away_luck:+.2f})")
        if abs(home_luck) > 0.4:
            if home_luck < -0.4:
                situations.append(f"📈 {home} due for regression (luck: {home_luck:+.2f})")
            else:
                situations.append(f"📉 {home} overperforming (luck: {home_luck:+.2f})")
                
        # Momentum updates
        if away_momentum > 0.15:
            situations.append(f"🔥 {away} is Hot (+{away_momentum:.2f} xG L10)")
        elif away_momentum < -0.15:
            situations.append(f"🧊 {away} is Cold ({away_momentum:.2f} xG L10)")
            
        if home_momentum > 0.15:
            situations.append(f"🔥 {home} is Hot (+{home_momentum:.2f} xG L10)")
        elif home_momentum < -0.15:
            situations.append(f"🧊 {home} is Cold ({home_momentum:.2f} xG L10)")
        
        if situations:
            factors['situation'] = ' | '.join(situations[:2])
        
        return factors
    
    def _map_scoreline_nb(
        self,
        away: str,
        home: str,
        away_mu: float,
        home_mu: float,
        winner_side: Optional[str],
        max_goals: int = 11,
    ) -> Tuple[int, int]:
        """Return the most-likely (MAP) scoreline under independent NB goals.

        This is deterministic and avoids injecting random noise into the product.
        If the MAP outcome is tied, we convert it to an OT/SO final by awarding
        +1 goal to `winner_side` (or the higher-mean side if not provided).
        """
        away_u = str(away).upper()
        home_u = str(home).upper()
        away_mu = float(max(0.01, away_mu))
        home_mu = float(max(0.01, home_mu))

        desired = (winner_side or "").lower()
        if desired not in {"away", "home", ""}:
            desired = ""

        k = float(self._get_dispersion_k(away_u, home_u, away_mu, home_mu))
        k = float(max(0.25, k))

        # Compute NB pmfs for 0..max_goals and pick joint argmax.
        pmf_a = [self._neg_bin_pmf(g, away_mu, k) for g in range(int(max_goals) + 1)]
        pmf_h = [self._neg_bin_pmf(g, home_mu, k) for g in range(int(max_goals) + 1)]

        best_a = 0
        best_h = 0
        best_p = -1.0
        for a in range(int(max_goals) + 1):
            pa = pmf_a[a]
            if pa <= 0.0:
                continue
            for h in range(int(max_goals) + 1):
                ph = pmf_h[h]
                p = pa * ph
                if p > best_p:
                    best_p = p
                    best_a = a
                    best_h = h

        a = int(best_a)
        h = int(best_h)

        # Convert regulation tie to OT/SO result (winner gets +1).
        if a == h:
            if desired == "away":
                a = min(int(max_goals), a + 1)
            elif desired == "home":
                h = min(int(max_goals), h + 1)
            else:
                if away_mu >= home_mu:
                    a = min(int(max_goals), a + 1)
                else:
                    h = min(int(max_goals), h + 1)

        # If a specific winner is requested but MAP disagrees, nudge minimally.
        if desired == "away" and a < h:
            a = min(int(max_goals), h + 1)
        elif desired == "home" and h < a:
            h = min(int(max_goals), a + 1)

        return int(a), int(h)
    
    def _calculate_confidence(self, away: str, home: str,
                              away_exp: float, home_exp: float) -> float:
        """Calculate prediction confidence (0-1)."""
        away_games = self.team_averages.get(away, {}).get('combined', {}).get('n_games', 0)
        home_games = self.team_averages.get(home, {}).get('combined', {}).get('n_games', 0)
        data_conf = min(1.0, (away_games + home_games) / 60.0)
        
        diff = abs(away_exp - home_exp)
        diff_conf = min(1.0, diff / 2.0)
        
        confidence = 0.6 * data_conf + 0.4 * diff_conf
        return round(max(0.1, min(0.9, confidence)), 2)
    
    def backtest(self, verbose: bool = False) -> Dict:
        """Backtest against actual game results from prediction history."""
        results = {
            'total': 0, 'correct_winner': 0,
            'score_errors': [], 'goal_diff_errors': [],
        }
        
        for pred in self.prediction_history:
            if not pred.get('actual_winner'):
                continue
            
            away = pred.get('away_team', '')
            home = pred.get('home_team', '')
            actual_away = pred.get('actual_away_score')
            actual_home = pred.get('actual_home_score')
            
            if not all([away, home, actual_away is not None, actual_home is not None]):
                continue
            
            away_b2b = pred.get('away_back_to_back', False)
            home_b2b = pred.get('home_back_to_back', False)
            
            # Extract goalie names if available
            metrics = pred.get('metrics_used', {})
            away_goalie = metrics.get('away_goalie', 'TBD')
            home_goalie = metrics.get('home_goalie', 'TBD')
            
            # Predict (using deterministic Poisson for reproducibility)
            prediction = self.predict_score(
                away, home,
                away_goalie=away_goalie, home_goalie=home_goalie,
                away_b2b=away_b2b, home_b2b=home_b2b
            )
            
            pred_away = prediction['away_score']
            pred_home = prediction['home_score']
            
            # Winner accuracy
            actual_winner_is_away = actual_away > actual_home
            pred_winner_is_away = pred_away > pred_home
            
            correct = actual_winner_is_away == pred_winner_is_away
            results['correct_winner'] += int(correct)
            results['total'] += 1
            
            # Score accuracy
            score_error = abs(pred_away - actual_away) + abs(pred_home - actual_home)
            results['score_errors'].append(score_error)
            
            goal_diff_error = abs((pred_away - pred_home) - (actual_away - actual_home))
            results['goal_diff_errors'].append(goal_diff_error)
            
            if verbose and not correct:
                print(f"  ❌ {away}@{home}: pred {pred_away}-{pred_home}, actual {actual_away}-{actual_home}")
        
        if results['total'] > 0:
            results['winner_accuracy'] = results['correct_winner'] / results['total']
            results['avg_score_error'] = np.mean(results['score_errors'])
            results['median_score_error'] = np.median(results['score_errors'])
            results['avg_diff_error'] = np.mean(results['goal_diff_errors'])
        
        return results


if __name__ == "__main__":
    model = ScorePredictionModel()
    
    # Run backtest
    print("\n📊 BACKTEST RESULTS")
    print("=" * 60)
    bt = model.backtest()
    print(f"  Games tested:       {bt['total']}")
    print(f"  Winner accuracy:    {bt.get('winner_accuracy', 0):.1%}")
    print(f"  Avg score error:    {bt.get('avg_score_error', 0):.2f} goals")
    print(f"  Median score error: {bt.get('median_score_error', 0):.2f} goals")
    print(f"  Avg diff error:     {bt.get('avg_diff_error', 0):.2f}")
    
    # Sample predictions
    print("\n🏒 TODAY'S PREDICTIONS")
    print("=" * 60)
    
    games = [
        ('CBJ', 'BOS'), ('TBL', 'CAR'), ('TOR', 'FLA'), ('NYI', 'MTL'),
        ('NJD', 'PIT'), ('DET', 'OTT'), ('CHI', 'NSH'), ('PHI', 'NYR'),
        ('SEA', 'STL'), ('MIN', 'COL'), ('CGY', 'SJS'), ('EDM', 'LAK'),
    ]
    
    for away, home in games:
        pred = model.predict_score(away, home)
        print(f"\n  {away} @ {home}: {away} {pred['away_score']} - {home} {pred['home_score']}")
        print(f"    xG: {pred['away_xg']:.2f} - {pred['home_xg']:.2f} | Conf: {pred['confidence']:.0%}")
        for k, v in pred['factors'].items():
            if v != 'Neutral':
                print(f"    {v}")
