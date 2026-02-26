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
                break
        
        # Load comprehensive goalie stats
        for p in [Path('data/goalie_stats.json'), Path('goalie_stats.json')]:
            if p.exists():
                with open(p) as f:
                    g_data = json.load(f)
                self.goalie_stats = g_data.get('goalies', {})
                # Create a name -> ID layout for easy lookup
                self.goalie_names = {v['name']: k for k, v in self.goalie_stats.items()}
                break
        
        # NOTE: Finishing profiles (team_scoring_profiles.json) removed —
        # 29/32 teams were above 1.2x (noise), and xG luck regression
        # already captures over/underperformance vs expected goals.
        
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
        
        # Apply multiplicative modifiers
        away_expected *= away_def_factor
        home_expected *= home_def_factor
        
        # Apply additive adjustments
        away_expected += away_luck_adj
        away_expected += away_div_adj
        away_expected += away_h2h_adj
        away_expected += away_b2b_adj
        away_expected += away_goalie_adj
        
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
            away_b2b, home_b2b,
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
        if gs and gs.get('games', 0) >= 5:
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
            
            # Base GSAX adjustment (0.8 scale) + Venue adjustment
            # Note: gsax_pg is GA saved relative to expected, so positive = good
            # Return value is added to expected goals, so negative = fewer goals allowed
            total_adj = (-gsax_pg * 0.8) - venue_adj
            return total_adj
            
        return 0.0
    
    def _generate_factors(self, away, home, away_exp, home_exp,
                          away_luck, home_luck, away_goalie, home_goalie,
                          away_hdc, home_hdc, away_def, home_def,
                          away_b2b, home_b2b,
                          away_h2h_adj, home_h2h_adj) -> Dict:
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
            
            warnings = []
            
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
