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


class ScorePredictionModel:
    """Optimized score prediction using correlation-validated features."""
    
    # League-wide constants from 2025-26 analysis
    LEAGUE_AVG_GF = 3.03
    HOME_ICE_BOOST = 0.21
    XG_LUCK_REGRESSION = 0.35
    B2B_PENALTY = 0.30  # Teams score ~0.3 fewer goals on back-to-backs
    
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
                self.goalie_stats = pred_data.get('goalie_stats', {})
                break
        
        # Load finishing profiles
        self.team_profiles = {}
        try:
            with open('team_scoring_profiles.json', 'r') as f:
                self.team_profiles = json.load(f)
        except:
            pass
        
        if self.team_stats:
            self._precompute_averages()
            self._build_h2h_records()
            n_h2h = sum(len(v) for v in self.h2h_cache.values())
            print(f"✅ Score model v3: {len(self.team_averages)} teams, "
                  f"{len(self.prediction_history)} predictions, "
                  f"{n_h2h} H2H records")
        else:
            print("⚠️  No team stats found, using league averages")
    
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
                     away_b2b: bool = False, home_b2b: bool = False) -> Dict:
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
        
        # ─── 7. Home ice advantage ───
        home_boost = self.HOME_ICE_BOOST
        
        # ─── 8. Division strength ───
        div_strength = {'Central': 0.10, 'Atlantic': 0.00, 'Metropolitan': 0.00, 'Pacific': -0.10}
        away_div_adj = div_strength.get(TEAM_TO_DIV.get(away, ''), 0.0)
        home_div_adj = div_strength.get(TEAM_TO_DIV.get(home, ''), 0.0)
        
        # ─── 9. Finishing ability ───
        away_finish = self.team_profiles.get(away, 1.0)
        home_finish = self.team_profiles.get(home, 1.0)
        away_finish_adj = 1.0 + (away_finish - 1.0) * 0.4
        home_finish_adj = 1.0 + (home_finish - 1.0) * 0.4
        
        # ─── 10. Head-to-head adjustment (NEW) ───
        away_h2h_adj = self._get_h2h_adjustment(away, home)
        home_h2h_adj = self._get_h2h_adjustment(home, away)
        
        # ─── 11. Back-to-back penalty (NEW) ───
        away_b2b_adj = -self.B2B_PENALTY if away_b2b else 0.0
        home_b2b_adj = -self.B2B_PENALTY if home_b2b else 0.0
        
        # ─── 12. Goalie adjustment (NEW) ───
        away_goalie_adj = self._get_goalie_adjustment(away_goalie, away, 'away')
        home_goalie_adj = self._get_goalie_adjustment(home_goalie, home, 'home')
        
        # ─── COMBINE: Weighted expected goals ───
        away_expected = (
            self.W_GS * away_gs_goals +
            self.W_XG * away_xg +
            self.W_PP * (self.LEAGUE_AVG_GF * away_pp_factor) +
            self.W_HDC * (self.LEAGUE_AVG_GF * away_hdc_factor) +
            self.W_CONTEXT * self.LEAGUE_AVG_GF
        )
        away_expected *= away_def_factor
        away_expected *= away_finish_adj
        away_expected += away_luck_adj
        away_expected += away_div_adj
        away_expected += away_h2h_adj
        away_expected += away_b2b_adj
        away_expected += away_goalie_adj  # Goalie of opponent affects scoring
        
        home_expected = (
            self.W_GS * home_gs_goals +
            self.W_XG * home_xg +
            self.W_PP * (self.LEAGUE_AVG_GF * home_pp_factor) +
            self.W_HDC * (self.LEAGUE_AVG_GF * home_hdc_factor) +
            self.W_CONTEXT * self.LEAGUE_AVG_GF
        )
        home_expected *= home_def_factor
        home_expected *= home_finish_adj
        home_expected += home_luck_adj
        home_expected += home_div_adj
        home_expected += home_boost
        home_expected += home_h2h_adj
        home_expected += home_b2b_adj
        home_expected += home_goalie_adj
        
        # ─── Clamp to realistic range ───
        away_expected = max(1.5, min(4.5, away_expected))
        home_expected = max(1.5, min(4.5, home_expected))
        
        # ─── Poisson-sampled scores for realistic variance ───
        away_score, home_score = self._poisson_score(away_expected, home_expected)
        
        # ─── Generate analysis factors ───
        factors = self._generate_factors(
            away, home, away_expected, home_expected,
            away_luck, home_luck, away_goalie, home_goalie,
            away_hdc, home_hdc, away_def_factor, home_def_factor,
            away_finish, home_finish, away_b2b, home_b2b,
            away_h2h_adj, home_h2h_adj
        )
        
        # ─── Confidence ───
        confidence = self._calculate_confidence(away, home, away_expected, home_expected)
        
        return {
            'away_score': away_score,
            'home_score': home_score,
            'away_xg': round(away_expected, 2),
            'home_xg': round(home_expected, 2),
            'total_goals': away_score + home_score,
            'confidence': confidence,
            'factors': factors,
        }
    
    def _get_goalie_adjustment(self, goalie_name: str, team: str, venue: str) -> float:
        """Get scoring adjustment based on opposing goalie quality.
        
        A strong opposing goalie reduces expected goals; a weak one increases them.
        Uses GSAX from goalie_stats if available, otherwise returns 0.
        """
        if not goalie_name or goalie_name == 'TBD':
            return 0.0
        
        # Check goalie_stats from prediction data
        if self.goalie_stats:
            gs = self.goalie_stats.get(goalie_name, {})
            if gs and gs.get('games', 0) >= 5:
                games = gs['games']
                xga = float(gs.get('xga_sum', 0)) / games
                ga = float(gs.get('ga_sum', 0)) / games
                gsax = xga - ga  # Positive = saves more than expected
                # Good goalie (high GSAX) reduces opponent scoring
                # Scale: GSAX of 0.5 ≈ -0.15 goals adjustment
                return -gsax * 0.3
        
        return 0.0
    
    def _generate_factors(self, away, home, away_exp, home_exp,
                          away_luck, home_luck, away_goalie, home_goalie,
                          away_hdc, home_hdc, away_def, home_def,
                          away_finish, home_finish,
                          away_b2b, home_b2b,
                          away_h2h_adj, home_h2h_adj) -> Dict:
        """Generate human-readable analysis factors."""
        factors = {
            'pace': 'Neutral',
            'goalie_away': 'Neutral',
            'goalie_home': 'Neutral',
            'situation': 'Neutral',
            'finishing': 'Neutral',
        }
        
        total_exp = away_exp + home_exp
        if total_exp > 7.5:
            factors['pace'] = "🔥 High Tempo (Offense Boost)"
        elif total_exp < 5.5:
            factors['pace'] = "🧊 Grinding/Defensive Pace"
        
        # Goalie context
        if away_goalie and away_goalie != 'TBD':
            if home_def < 0.90:
                factors['goalie_away'] = f"🛡️ Strong Goalie ({away_goalie})"
            elif home_def > 1.10:
                factors['goalie_away'] = f"⚠️ Shaky Goaltending ({away_goalie})"
        if home_goalie and home_goalie != 'TBD':
            if away_def < 0.90:
                factors['goalie_home'] = f"🛡️ Strong Goalie ({home_goalie})"
            elif away_def > 1.10:
                factors['goalie_home'] = f"⚠️ Shaky Goaltending ({home_goalie})"
        
        # Finishing
        if home_finish > 1.5:
            factors['finishing'] = f"🎯 {home} Elite Finishing (x{home_finish:.2f})"
        elif away_finish > 1.5:
            factors['finishing'] = f"🎯 {away} Elite Finishing (x{away_finish:.2f})"
        elif home_finish < 1.05:
            factors['finishing'] = f"🧱 {home} Low Finishing (x{home_finish:.2f})"
        elif away_finish < 1.05:
            factors['finishing'] = f"🧱 {away} Low Finishing (x{away_finish:.2f})"
        
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
        
        if situations:
            factors['situation'] = ' | '.join(situations[:2])
        
        return factors
    
    def _poisson_score(self, away_lambda: float, home_lambda: float) -> Tuple[int, int]:
        """Poisson-sampled scores for realistic variance."""
        date_str = time.strftime('%Y-%m-%d')
        seed_str = f"{date_str}_{away_lambda:.4f}_{home_lambda:.4f}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        rng = np.random.RandomState(seed)
        
        away_score = max(1, min(7, int(rng.poisson(away_lambda))))
        home_score = max(1, min(7, int(rng.poisson(home_lambda))))
        
        if away_score == home_score:
            if away_lambda > home_lambda:
                away_score += 1
            elif home_lambda > away_lambda:
                home_score += 1
            else:
                home_score += 1
        
        return away_score, home_score
    
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
            
            # Predict (using deterministic Poisson for reproducibility)
            prediction = self.predict_score(
                away, home,
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
