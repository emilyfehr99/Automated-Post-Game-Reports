#!/usr/bin/env python3
"""
Score Prediction Model v2
Data-driven score predictions based on correlation analysis findings:
  - Game Score (GS) r=0.642 with goals (top composite predictor)
  - PP% r=0.466 with goals (special teams matter most)
  - xG averages as baseline floor (r=0.122 per-game but stable in aggregate)
  - xG luck regression (teams far from xG regress toward it)
  - Home ice advantage (+0.21 GF/game empirically)
  - Division strength context (Central division dominates 54% WR)
"""

import json
import numpy as np
from typing import Dict, Optional
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
    """Data-driven score prediction using correlation-validated features."""
    
    # League-wide constants from 2025-26 analysis
    LEAGUE_AVG_GF = 3.03          # League average goals per game
    HOME_ICE_BOOST = 0.21         # Empirical home GF advantage
    XG_LUCK_REGRESSION = 0.35     # How much xG luck regresses per prediction (35%)
    
    # Feature weights (derived from correlation magnitudes, normalized)
    # GS: 0.642, PP%: 0.466, PK%: 0.421, xG: 0.122, HDC: ~0.1
    W_GS = 0.30
    W_PP = 0.20
    W_XG = 0.20
    W_HDC = 0.15
    W_CONTEXT = 0.15  # home ice + division + luck regression
    
    def __init__(self):
        """Load team stats data."""
        self.team_stats = {}
        self.team_averages = {}  # Pre-computed per-team averages
        
        # Try loading team stats
        stats_paths = [
            Path('data/season_2025_2026_team_stats.json'),
            Path('season_2025_2026_team_stats.json'),
        ]
        for p in stats_paths:
            if p.exists():
                with open(p) as f:
                    self.team_stats = json.load(f)
                break
        
        if self.team_stats:
            self._precompute_averages()
            print(f"✅ Score model loaded stats for {len(self.team_averages)} teams")
        else:
            print("⚠️  No team stats found, using league averages")
        
        # Load finishing profiles if available
        self.team_profiles = {}
        try:
            with open('team_scoring_profiles.json', 'r') as f:
                self.team_profiles = json.load(f)
        except:
            pass
    
    def _precompute_averages(self):
        """Pre-compute per-team averages from game-level data."""
        for team, venues in self.team_stats.get('teams', {}).items():
            avgs = {'home': {}, 'away': {}, 'combined': {}}
            
            for venue in ['home', 'away']:
                vdata = venues.get(venue, {})
                metrics = {}
                for key in ['goals', 'opp_goals', 'xg', 'opp_xg', 'gs', 'shots',
                           'hdc', 'hdca', 'hits', 'blocked_shots', 'takeaways',
                           'giveaways', 'faceoff_pct', 'power_play_pct',
                           'penalty_kill_pct', 'corsi_pct', 'rebounds',
                           'rush_shots', 'cycle_shots', 'fc', 'rush', 'ozs', 'dzs']:
                    vals = vdata.get(key, [])
                    numeric = []
                    for v in vals:
                        try:
                            numeric.append(float(v))
                        except (ValueError, TypeError):
                            pass
                    metrics[key] = np.mean(numeric) if numeric else None
                
                metrics['n_games'] = len(vdata.get('goals', []))
                metrics['xg_luck'] = (
                    (metrics.get('goals') or self.LEAGUE_AVG_GF) - 
                    (metrics.get('xg') or self.LEAGUE_AVG_GF)
                )
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
    
    def _get_team_metric(self, team: str, metric: str, venue: str = 'combined') -> float:
        """Get a team's average for a metric, with league-average fallback."""
        defaults = {
            'goals': self.LEAGUE_AVG_GF,
            'opp_goals': self.LEAGUE_AVG_GF,
            'xg': 3.0,
            'opp_xg': 3.0,
            'gs': 5.7,
            'hdc': 7.0,
            'hdca': 7.0,
            'shots': 28.0,
            'power_play_pct': 50.0,  # Raw PP% from data (not standard PP%)
            'penalty_kill_pct': 50.0,
            'faceoff_pct': 50.0,
            'corsi_pct': 50.0,
            'xg_luck': 0.0,
            'rush_shots': 4.0,
            'cycle_shots': 10.0,
            'rebounds': 3.0,
        }
        
        team_data = self.team_averages.get(team.upper(), {}).get(venue, {})
        val = team_data.get(metric)
        if val is not None and not np.isnan(val):
            return val
        return defaults.get(metric, 0.0)
    
    def predict_score(self, away_team: str, home_team: str,
                     away_goalie: str = None, home_goalie: str = None,
                     game_date: str = None) -> Dict:
        """
        Predict realistic game score.
        
        Returns:
            Dict with away_score, home_score, total_goals, confidence, factors
        """
        away = away_team.upper()
        home = home_team.upper()
        
        # ─── 1. Game Score baseline (r=0.642 with goals) ───
        away_gs = self._get_team_metric(away, 'gs', 'away')
        home_gs = self._get_team_metric(home, 'gs', 'home')
        
        # GS roughly maps: GS 5.0 ≈ 2.5 goals, GS 7.0 ≈ 3.5 goals
        gs_to_goals = lambda gs: max(1.0, 0.5 * gs)
        away_gs_goals = gs_to_goals(away_gs)
        home_gs_goals = gs_to_goals(home_gs)
        
        # ─── 2. xG baseline (stable aggregate predictor) ───
        away_xg = self._get_team_metric(away, 'xg', 'away')
        home_xg = self._get_team_metric(home, 'xg', 'home')
        
        # ─── 3. Opponent defensive quality adjustment ───
        # If opponent allows fewer goals, reduce expected scoring
        away_opp_ga = self._get_team_metric(home, 'opp_goals', 'home')  # Home team's GA
        home_opp_ga = self._get_team_metric(away, 'opp_goals', 'away')  # Away team's GA
        
        # Dampen defense factor to 50% of deviation (prevent extreme multipliers)
        away_def_raw = away_opp_ga / self.LEAGUE_AVG_GF
        home_def_raw = home_opp_ga / self.LEAGUE_AVG_GF
        away_def_factor = 1.0 + (away_def_raw - 1.0) * 0.5  # e.g. 1.54 → 1.27
        home_def_factor = 1.0 + (home_def_raw - 1.0) * 0.5
        
        # ─── 4. Special teams (PP%: r=0.466 with goals) ───
        away_pp = self._get_team_metric(away, 'power_play_pct', 'away')
        home_pp = self._get_team_metric(home, 'power_play_pct', 'home')
        # Normalize PP% around league average (raw data is weird, may be >100)
        away_pp_factor = 1.0 + (away_pp - 50.0) * 0.005  # Small boost per PP% point
        home_pp_factor = 1.0 + (home_pp - 50.0) * 0.005
        
        # ─── 5. High Danger Chances ───
        away_hdc = self._get_team_metric(away, 'hdc', 'away')
        home_hdc = self._get_team_metric(home, 'hdc', 'home')
        away_hdc_factor = away_hdc / 7.0  # League average ~7
        home_hdc_factor = home_hdc / 7.0
        
        # ─── 6. xG luck regression ───
        away_luck = self._get_team_metric(away, 'xg_luck', 'away')
        home_luck = self._get_team_metric(home, 'xg_luck', 'home')
        # Regress toward xG: if team scores +0.5 above xG, expect them to come back
        away_luck_adj = -away_luck * self.XG_LUCK_REGRESSION
        home_luck_adj = -home_luck * self.XG_LUCK_REGRESSION
        
        # ─── 7. Home ice advantage ───
        home_boost = self.HOME_ICE_BOOST
        
        # ─── 8. Division strength ───
        div_strength = {
            'Central': 0.10,      # 54% win rate, outperforms
            'Atlantic': 0.00,     # 50.4%, baseline
            'Metropolitan': 0.00, # 50.4%, baseline
            'Pacific': -0.10,     # 45.2%, underperforms
        }
        away_div_adj = div_strength.get(TEAM_TO_DIV.get(away, ''), 0.0)
        home_div_adj = div_strength.get(TEAM_TO_DIV.get(home, ''), 0.0)
        
        # ─── 9. Finishing ability ───
        away_finish = self.team_profiles.get(away, 1.0)
        home_finish = self.team_profiles.get(home, 1.0)
        # Conservative: use 40% of observed finishing lift (prevent stacking with def factor)
        away_finish_adj = 1.0 + (away_finish - 1.0) * 0.4
        home_finish_adj = 1.0 + (home_finish - 1.0) * 0.4
        
        # ─── COMBINE: Weighted expected goals ───
        away_expected = (
            self.W_GS * away_gs_goals +
            self.W_XG * away_xg +
            self.W_PP * (self.LEAGUE_AVG_GF * away_pp_factor) +
            self.W_HDC * (self.LEAGUE_AVG_GF * away_hdc_factor) +
            self.W_CONTEXT * self.LEAGUE_AVG_GF
        )
        # Apply modifiers
        away_expected *= away_def_factor  # Opponent defense
        away_expected *= away_finish_adj  # Finishing ability
        away_expected += away_luck_adj    # Luck regression
        away_expected += away_div_adj     # Division strength
        
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
        home_expected += home_boost  # Home ice
        
        # ─── Clamp expected goals to realistic range ───
        away_expected = max(1.5, min(4.5, away_expected))
        home_expected = max(1.5, min(4.5, home_expected))
        
        # ─── Poisson-sampled scores for realistic variance ───
        # NHL goals follow a Poisson distribution. Simple rounding compresses
        # everything to 3-4 (99.6% 1-goal games). Poisson sampling produces
        # realistic spreads matching the actual NHL distribution:
        #   1-goal: ~44%, 2-goal: ~14%, 3-goal: ~26%, 4-goal: ~9%
        away_score, home_score = self._poisson_score(away_expected, home_expected)
        
        # ─── Generate analysis factors ───
        factors = self._generate_factors(
            away, home, away_expected, home_expected,
            away_luck, home_luck, away_goalie, home_goalie,
            away_hdc, home_hdc, away_def_factor, home_def_factor,
            away_finish, home_finish
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
    
    def _generate_factors(self, away: str, home: str,
                          away_exp: float, home_exp: float,
                          away_luck: float, home_luck: float,
                          away_goalie: str, home_goalie: str,
                          away_hdc: float, home_hdc: float,
                          away_def: float, home_def: float,
                          away_finish: float, home_finish: float) -> Dict:
        """Generate human-readable analysis factors."""
        factors = {
            'pace': 'Neutral',
            'goalie_away': 'Neutral',
            'goalie_home': 'Neutral',
            'situation': 'Neutral',
            'finishing': 'Neutral',
        }
        
        # Pace: high total expected goals
        total_exp = away_exp + home_exp
        if total_exp > 6.5:
            factors['pace'] = "🔥 High Tempo (Offense Boost)"
        elif total_exp < 5.0:
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
        if home_finish > 1.2:
            factors['finishing'] = f"🎯 {home} Elite Finishing (x{home_finish:.2f})"
        elif away_finish > 1.2:
            factors['finishing'] = f"🎯 {away} Elite Finishing (x{away_finish:.2f})"
        elif home_finish < 0.85:
            factors['finishing'] = f"🧱 {home} Low Finishing (x{home_finish:.2f})"
        elif away_finish < 0.85:
            factors['finishing'] = f"🧱 {away} Low Finishing (x{away_finish:.2f})"
        
        # xG luck regression situation
        if abs(away_luck) > 0.4 or abs(home_luck) > 0.4:
            if away_luck < -0.4:
                factors['situation'] = f"📈 {away} due for positive regression (xG luck: {away_luck:+.2f})"
            elif home_luck < -0.4:
                factors['situation'] = f"📈 {home} due for positive regression (xG luck: {home_luck:+.2f})"
            elif away_luck > 0.4:
                factors['situation'] = f"📉 {away} overperforming xG ({away_luck:+.2f}), may cool"
            elif home_luck > 0.4:
                factors['situation'] = f"📉 {home} overperforming xG ({home_luck:+.2f}), may cool"
        
        return factors
    
    def _poisson_score(self, away_lambda: float, home_lambda: float) -> tuple:
        """
        Sample scores from Poisson distribution for realistic variance.
        
        Uses deterministic seeding for reproducibility. Takes a single
        Poisson draw rather than mode-of-N (which over-concentrates on
        1-goal games), producing variance that matches real NHL data:
          Real: 44% 1-goal, 14% 2-goal, 26% 3-goal
        """
        import hashlib, time
        # Seed on date + expected values for daily reproducibility
        date_str = time.strftime('%Y-%m-%d')
        seed_str = f"{date_str}_{away_lambda:.4f}_{home_lambda:.4f}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        rng = np.random.RandomState(seed)
        
        # Single Poisson draw — preserves natural variance
        away_score = max(0, int(rng.poisson(away_lambda)))
        home_score = max(0, int(rng.poisson(home_lambda)))
        
        # Ensure at least 1 goal each (shutouts are rare in predictions)
        away_score = max(1, away_score)
        home_score = max(1, home_score)
        
        # Resolve ties: OT/SO gives winner +1
        if away_score == home_score:
            if away_lambda > home_lambda:
                away_score += 1
            elif home_lambda > away_lambda:
                home_score += 1
            else:
                # True toss-up: give home ice advantage
                home_score += 1
        
        return away_score, home_score
    
    def _calculate_confidence(self, away: str, home: str,
                              away_exp: float, home_exp: float) -> float:
        """Calculate prediction confidence (0-1)."""
        # Base confidence from data availability
        away_games = self.team_averages.get(away, {}).get('combined', {}).get('n_games', 0)
        home_games = self.team_averages.get(home, {}).get('combined', {}).get('n_games', 0)
        
        data_conf = min(1.0, (away_games + home_games) / 60.0)  # Max at ~30 games each
        
        # Score differential confidence
        diff = abs(away_exp - home_exp)
        diff_conf = min(1.0, diff / 2.0)  # Higher diff = more confident
        
        # Combined
        confidence = 0.6 * data_conf + 0.4 * diff_conf
        return round(max(0.1, min(0.9, confidence)), 2)


if __name__ == "__main__":
    model = ScorePredictionModel()
    
    print("\n🎯 Score Prediction Model v2 — Test")
    print("=" * 60)
    
    test_games = [
        ('COL', 'DAL', 'Top Central matchup'),
        ('BUF', 'NJD', 'Struggling offenses'),
        ('WSH', 'CAR', 'Metro rivalry'),
        ('TOR', 'FLA', 'Atlantic battle'),
        ('CHI', 'COL', 'Weak vs strong'),
        ('VAN', 'SEA', 'Pacific basement'),
        ('CBJ', 'BOS', "Today's game"),
        ('MIN', 'COL', "Today's game"),
        ('EDM', 'LAK', "Today's game"),
    ]
    
    for away, home, desc in test_games:
        pred = model.predict_score(away, home)
        print(f"\n  {desc}: {away} @ {home}")
        print(f"    Score: {away} {pred['away_score']} - {home} {pred['home_score']}")
        print(f"    xG:    {away} {pred['away_xg']:.2f} - {home} {pred['home_xg']:.2f}")
        print(f"    Confidence: {pred['confidence']:.0%}")
        for k, v in pred['factors'].items():
            if v != 'Neutral':
                print(f"    {v}")
