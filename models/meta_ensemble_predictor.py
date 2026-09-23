#!/usr/bin/env python3
"""
Meta Ensemble Predictor
Combines all prediction methods for maximum accuracy
"""
from typing import Dict, List, Optional, Tuple, Any
import json
import numpy as np
import xgboost as xgb
import pandas as pd
import pickle
import math
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

TEAM_COORDINATES = {
    'ANA': (33.80, -117.88), 'BOS': (42.36, -71.06), 'BUF': (42.89, -78.88),
    'CGY': (51.05, -114.07), 'CAR': (35.80, -78.72), 'CHI': (41.88, -87.67),
    'COL': (39.75, -105.01), 'CBJ': (39.97, -83.00), 'DAL': (32.79, -96.81),
    'DET': (42.34, -83.05), 'EDM': (53.55, -113.49), 'FLA': (26.12, -80.14),
    'LAK': (34.04, -118.27), 'MIN': (44.94, -93.10), 'MTL': (45.51, -73.57),
    'NSH': (36.16, -86.78), 'NJD': (40.73, -74.17), 'NYI': (40.71, -73.60),
    'NYR': (40.75, -73.99), 'OTT': (45.42, -75.70), 'PHI': (39.90, -75.17),
    'PIT': (40.44, -79.99), 'SJS': (37.33, -121.90), 'SEA': (47.62, -122.35),
    'STL': (38.63, -90.20), 'TBL': (27.95, -82.45), 'TOR': (43.65, -79.38),
    'UTA': (40.76, -111.89), 'VAN': (49.28, -123.12), 'VGK': (36.17, -115.14),
    'WSH': (38.90, -77.04), 'WPG': (49.90, -97.14)
}

# Phase 4: Time Zone Mapping (UTC Offsets)
TEAM_TIMEZONES = {
    'ANA': -8, 'LAK': -8, 'SJS': -8, 'VAN': -8, 'SEA': -8, 'VGK': -8,
    'UTA': -7, 'CGY': -7, 'EDM': -7, 'COL': -7,
    'CHI': -6, 'DAL': -6, 'MIN': -6, 'NSH': -6, 'STL': -6, 'WPG': -6,
    'BOS': -5, 'BUF': -5, 'MTL': -5, 'OTT': -5, 'TOR': -5, 'CAR': -5, 'NJD': -5, 
    'NYI': -5, 'NYR': -5, 'PHI': -5, 'PIT': -5, 'WSH': -5, 'FLA': -5, 'TBL': -5, 
    'DET': -5, 'CBJ': -5
}

# Environmental Altitude / Elevation Mapping (feet above sea level)
TEAM_ELEVATIONS = {
    'COL': 5280, 'UTA': 4265, 'CGY': 3440, 'EDM': 2200, 'WPG': 784,
    'MIN': 840, 'CHI': 596, 'STL': 466, 'DAL': 430, 'NSH': 597,
    'DET': 600, 'CBJ': 780, 'PIT': 740, 'BUF': 600, 'TOR': 249,
    'OTT': 230, 'MTL': 118, 'BOS': 20, 'NYR': 33, 'NYI': 50,
    'NJD': 20, 'PHI': 39, 'WSH': 25, 'CAR': 315, 'FLA': 10,
    'TBL': 15, 'ANA': 157, 'LAK': 285, 'SJS': 82, 'VGK': 2001,
    'SEA': 175, 'VAN': 0
}

def calculate_distance(city1, city2):
    """Haversine distance between two teams in miles"""
    if city1 == city2 or city1 not in TEAM_COORDINATES or city2 not in TEAM_COORDINATES:
        return 0.0
    lat1, lon1 = TEAM_COORDINATES[city1]
    lat2, lon2 = TEAM_COORDINATES[city2]
    R = 3958.8 # miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c
try:
    from ensemble_predictor import EnsemblePredictor
except Exception:
    from models.ensemble_predictor import EnsemblePredictor
try:
    from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
except Exception:
    from models.improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
try:
    from rotowire_scraper import RotoWireScraper
except Exception:
    from scrapers.rotowire_scraper import RotoWireScraper
try:
    from standings_tracker import StandingsTracker
except Exception:
    from models.standings_tracker import StandingsTracker
try:
    from nb_utils import prob_total_over
except Exception:
    from models.nb_utils import prob_total_over

class EloTracker:
    def __init__(self, k_factor=20, home_advantage=17):
        self.ratings = {}  # {team: rating}
        self.k = k_factor
        # Empirically calibrated: 400 * log10(0.5241 / 0.4759) = 16.76 ~ 17 (true +2.41% edge)
        self.ha = home_advantage
        self.base_rating = 1500

    def get_rating(self, team):
        return self.ratings.get(team, self.base_rating)

    def regress_season(self, regression_factor=0.33):
        """Regress ratings 1/3 toward 1500 mean across off-season transitions"""
        for team in list(self.ratings.keys()):
            self.ratings[team] = self.base_rating + (1.0 - regression_factor) * (self.ratings[team] - self.base_rating)

    def get_win_prob(self, home_team, away_team):
        home_rating = self.get_rating(home_team) + self.ha
        away_rating = self.get_rating(away_team)
        return 1 / (1 + 10 ** ((away_rating - home_rating) / 400))

    def update(self, home_team, away_team, home_score, away_score):
        if home_score > away_score:
            actual_home = 1.0
        else:
            actual_home = 0.0
            
        expected_home = self.get_win_prob(home_team, away_team)
        
        goal_diff = abs(home_score - away_score)
        multiplier = math.log(goal_diff + 1) if goal_diff > 0 else 1.0
        
        delta = self.k * multiplier * (actual_home - expected_home)
        
        self.ratings[home_team] = self.get_rating(home_team) + delta
        self.ratings[away_team] = self.get_rating(away_team) - delta

class GoalieHistory:
    def __init__(self):
        self.stats = {} # {goalie_name: {'gsax': [], 'hdsv': [], 'shots': []}}
        
    def update(self, name, gsax, hdsv=None, shots=None):
        if not name: return
        if name not in self.stats:
            self.stats[name] = {'gsax': [], 'hdsv': [], 'shots': []}
        self.stats[name]['gsax'].append(gsax)
        if hdsv is not None:
            self.stats[name]['hdsv'].append(hdsv)
        if shots is not None:
            self.stats[name]['shots'].append(shots)
        
    def get_rolling_gsax(self, name, window=5):
        if not name or name not in self.stats or not self.stats[name]['gsax']:
            return 0.0
        vals = self.stats[name]['gsax'][-window:]
        return np.mean(vals)
        
    def get_shrunk_gsax(self, name, window=5, prior_weight=8):
        """Bayesian shrinkage toward 0.0 baseline to neutralize extreme single-game goalie volatility"""
        if not name or name not in self.stats or not self.stats[name]['gsax']:
            return 0.0
        vals = self.stats[name]['gsax']
        n = len(vals)
        rolling_val = float(np.mean(vals[-window:]))
        season_val = float(np.mean(vals))
        shrunk_prior = (n * season_val + prior_weight * 0.0) / (n + prior_weight)
        return 0.7 * rolling_val + 0.3 * shrunk_prior

    def get_rolling_hdsv(self, name, window=5):
        if not name or name not in self.stats or not self.stats[name]['hdsv']:
            return 0.8
        vals = self.stats[name]['hdsv'][-window:]
        return np.mean(vals)

    def get_rolling_shots_faced(self, name, window=10):
        if not name or name not in self.stats or not self.stats[name]['shots']:
            return 0.0
        vals = self.stats[name]['shots'][-window:]
        return np.sum(vals)

class TeamHistory:
    def __init__(self):
        self.history = {}  # {team_abbr: {'dates': [], 'stats': [], 'home_stats': [], 'away_stats': [], 'opponents_elo': [], 'last_city': None}}
        self.elo = EloTracker()
        self.goalies = GoalieHistory()
        self.h2h_history = {}  # {(team_a, team_b): [{'date': d, 'total_goals': tot, 'home_goals': h, 'away_goals': a}]}
        
    def update_h2h(self, team_a, team_b, date, goals_a, goals_b):
        """Record head-to-head game outcome chronologically"""
        pair = tuple(sorted([team_a, team_b]))
        if pair not in self.h2h_history:
            self.h2h_history[pair] = []
        self.h2h_history[pair].append({
            'date': date,
            'total_goals': float(goals_a + goals_b),
            'goals_a': float(goals_a),
            'goals_b': float(goals_b)
        })

    def get_h2h_pace(self, team_a, team_b, prior_weight=4.0, league_mean=6.10):
        """Calculate Empirical Bayes shrunk pace for matchup"""
        pair = tuple(sorted([team_a, team_b]))
        history = self.h2h_history.get(pair, [])
        if not history:
            return league_mean
        n = len(history)
        obs_mean = sum(g['total_goals'] for g in history) / float(n)
        return float((n / (n + prior_weight)) * obs_mean + (prior_weight / (n + prior_weight)) * league_mean)
        
    def update(self, team, date, game_stats, venue=None, opponent_elo=None, city=None):
        """Update team history with a new game"""
        if team not in self.history:
            self.history[team] = {'dates': [], 'stats': [], 'home_stats': [], 'away_stats': [], 'opponents_elo': [], 'last_city': None}
            
        self.history[team]['dates'].append(date)
        self.history[team]['stats'].append(game_stats)
        self.history[team]['last_city'] = city or team
        
        if opponent_elo is not None:
             self.history[team]['opponents_elo'].append(opponent_elo)
        
        if venue == 'home':
            self.history[team]['home_stats'].append(game_stats)
        elif venue == 'away':
            self.history[team]['away_stats'].append(game_stats)
            
    def update_goalie(self, name, gsax, hdsv=None, shots=None):
        self.goalies.update(name, gsax, hdsv, shots)
        
    def get_goalie_gsax(self, name, window=5):
        return self.goalies.get_rolling_gsax(name, window)

    def get_goalie_hdsv(self, name, window=5):
        return self.goalies.get_rolling_hdsv(name, window)

    def get_travel_distance(self, team, current_city):
        """Distance traveled since last game"""
        if team not in self.history or not self.history[team]['last_city']:
            return 0.0
        return calculate_distance(self.history[team]['last_city'], current_city)

    def get_elo(self, team):
        return self.elo.get_rating(team)

    def get_days_rest(self, team, current_date):
        """Get days since last game"""
        if team not in self.history or not self.history[team]['dates']:
            return 4  # Default to fresh rest
            
        last_date = self.history[team]['dates'][-1]
        delta = (current_date - last_date).days
        return max(1, delta)

    def get_rolling_rate(self, team, condition_key, target_key, window=20):
        """Calculate the success rate of a target condition (e.g., win_rate when leading_after_p2)"""
        if team not in self.history or not self.history[team]['stats']:
            return 0.5
        
        relevant_games = [g for g in self.history[team]['stats'][-window:] if g.get(condition_key) == 1]
        if not relevant_games:
            return 0.5
            
        successes = [g for g in relevant_games if g.get(target_key) == 1]
        return float(len(successes)) / float(len(relevant_games))

    def get_game_count_in_window(self, team, current_date, window=4):
        """Phase 3: Count games in a rolling window (e.g. 3-in-4)"""
        if team not in self.history or not self.history[team]['dates']:
            return 1
        dates = self.history[team]['dates']
        count = 0
        for d in reversed(dates):
            if (current_date - d).days < window:
                count += 1
            else:
                break
        return int(count + 1) # Current game counts as 1
        
    def get_rolling_stats(self, team, window=5, venue=None, alpha=None):
        """Calculate averages for specified window with optional venue filter and exponential decay (alpha)"""
        if team not in self.history:
            return {}
            
        if venue == 'home':
            stats_list = self.history[team]['home_stats'][-window:]
        elif venue == 'away':
            stats_list = self.history[team]['away_stats'][-window:]
        else:
            stats_list = self.history[team]['stats'][-window:]
            
        aggregated = {}
        if not stats_list:
            return {}
            
        keys = stats_list[0].keys()
        for k in keys:
            vals = [g[k] for g in stats_list if g.get(k) is not None]
            if vals:
                if alpha is not None and len(vals) > 1:
                    # Exponential Weighted Mean
                    weights = [alpha * (1 - alpha) ** i for i in range(len(vals))]
                    weights = weights[::-1]
                    aggregated[k] = np.average(vals, weights=weights)
                else:
                    aggregated[k] = np.mean(vals)
            else:
                aggregated[k] = 0.0
        return aggregated

    def get_rolling_std(self, team, window=5, key='goal_diff'):
        """Calculate rolling standard deviation for a metric"""
        if team not in self.history or len(self.history[team]['stats']) < 2:
            return 1.0
        stats_list = self.history[team]['stats'][-window:]
        vals = [g[key] for g in stats_list if g.get(key) is not None]
        return np.std(vals) if len(vals) > 1 else 1.0

    def get_sos(self, team, window=5):
        """Calculate Strength of Schedule (Avg Opponent Elo)"""
        if team not in self.history or not self.history[team]['opponents_elo']:
            return self.elo.base_rating
        return np.mean(self.history[team]['opponents_elo'][-window:])

class MetaEnsemblePredictor:
    """Combines multiple ensemble strategies for maximum accuracy"""
    
    @staticmethod
    def compute_bivariate_score_distribution(lam_h: float, lam_a: float, home_favored: bool = True, win_prob: float = 0.55):
        """
        Bivariate Poisson joint score matrix generator for hockey with dynamic empty net & multi-goal dispersion.
        Produces MAP optimal score, top 3 exact scores, and exact market totals.
        """
        max_goals = 9
        P = np.zeros((max_goals, max_goals))
        
        # Base Poisson marginals
        p_h = [ (float(lam_h)**i * math.exp(-float(lam_h))) / math.factorial(i) for i in range(max_goals) ]
        p_a = [ (float(lam_a)**j * math.exp(-float(lam_a))) / math.factorial(j) for j in range(max_goals) ]
        
        for i in range(max_goals):
            for j in range(max_goals):
                base_p = p_h[i] * p_a[j]
                adj = 1.0
                
                # 1. Empirically calibrated empty net pull probability (converts 1-goal margin to 2-goal margin)
                if abs(i - j) == 2 and max(i, j) >= 3:
                    adj = 1.35 if win_prob >= 0.56 else 1.10
                # 2. Regulation ties resolved via OT/SO
                elif abs(i - j) == 0:
                    adj = 0.70
                # 3. High-certainty blowout dispersion
                elif abs(i - j) >= 3 and win_prob >= 0.62:
                    adj = 1.30
                elif abs(i - j) == 1 and win_prob < 0.55:
                    adj = 1.15
                    
                P[i, j] = base_p * adj
                
        P /= max(1e-9, P.sum())
        
        # Identify top coherent outcomes
        coherent_outcomes = []
        for i in range(max_goals):
            for j in range(max_goals):
                if home_favored and i > j:
                    coherent_outcomes.append((i, j, float(P[i, j])))
                elif (not home_favored) and j > i:
                    coherent_outcomes.append((i, j, float(P[i, j])))
                    
        coherent_outcomes.sort(key=lambda x: x[2], reverse=True)
        
        best = coherent_outcomes[0] if coherent_outcomes else (3, 2 if home_favored else (2, 3))
        top_3 = coherent_outcomes[:3] if len(coherent_outcomes) >= 3 else coherent_outcomes
        
        # Market probabilities
        p_over_5_5 = float(np.sum([P[i, j] for i in range(max_goals) for j in range(max_goals) if i + j > 5.5]))
        p_over_6_5 = float(np.sum([P[i, j] for i in range(max_goals) for j in range(max_goals) if i + j > 6.5]))
        p_home_cover_minus_1_5 = float(np.sum([P[i, j] for i in range(max_goals) for j in range(max_goals) if i - j >= 2]))
        p_away_cover_minus_1_5 = float(np.sum([P[i, j] for i in range(max_goals) for j in range(max_goals) if j - i >= 2]))
        
        return {
            "best_home_goals": int(best[0]),
            "best_away_goals": int(best[1]),
            "score_prob": float(best[2]),
            "top_3_scores": [(int(o[0]), int(o[1]), float(o[2])) for o in top_3],
            "total_over_5_5": p_over_5_5,
            "total_over_6_5": p_over_6_5,
            "puckline_home_minus_1_5": p_home_cover_minus_1_5,
            "puckline_away_minus_1_5": p_away_cover_minus_1_5,
        }

    def __init__(self):
        self.specialized_ensemble = EnsemblePredictor()
        self.base_model = ImprovedSelfLearningModelV2()
        
        # Load XGBoost Components
        self.xgb_model = None
        self.calibrated_model = None
        self.confidence_model = None # Phase 10: Meta-Confidence Model
        self.total_goals_model = None  # Scoreline backbone (total goals)
        self.home_goals_model = None
        self.away_goals_model = None
        self.history_tracker = TeamHistory()
        self.feature_names = []
        self._feature_snapshot = None
        self._scoreline_calibration = None
        self._prob_calibration = None
        self.margin_model = None
        self.p1_model = None
        self.confidence_model = None
        self.toss_up_model = None
        self.total_goals_model = None
        self.team_profiles = {}
        self.travel_archetypes = {}
        self.edge_profiles = {}
        self.team_encodings = {}
        self.rotowire = RotoWireScraper()
        self.standings = StandingsTracker()
        
        # Dual-Model State
        self.calibrated_model_reg = None
        self.calibrated_model_ply = None
        self.feature_names_reg = []
        self.feature_names_ply = []
        
        # Phase 48: Multi-Model Stacking
        self.xgb_stack_reg = [] # List of (model, feature_names, weight)
        self.xgb_stack_ply = []
        
        self._component_weights = None
        self._load_component_weights()
        
        try:
            self._load_dual_regime_components()
        except Exception as e:
            print(f"⚠️ Failed to load dual regime components: {e}")

    def _load_component_weights(self) -> None:
        """Load dynamic component weights from recent backtests if available."""
        # Defaults (roughly match existing behavior)
        self._component_weights = {
            "xgb": 0.50,
            "elo": 0.05,
            "specialized": 0.20,
            "player": 0.10,
            "base": 0.15,
            "vegas": 0.15,
        }
        self._model_mode = "ensemble"
        self._shrink_alpha = 1.0
        
        # Stacking Parameters
        self._stacking_temp = 0.12 # Sensitivity for softmax (Adaptive default)
        self._core_budget = 0.60 # Combined weight for primary predictors
        
        try:
            p = Path("model_performance.json")
            if not p.exists():
                print("ℹ️  No model_performance.json found; using default ensemble weights")
                return
            with open(p, "r") as f:
                perf = json.load(f)
            
            # Phase 48: Advanced Softmax Stacking
            # We calculate weights for the two primary predictors (XGB and ELO)
            # based on their recent performance logs.
            x_ll = perf.get("xgb_recent_logloss") or perf.get("xgb_cal_mean_logloss")
            e_ll = perf.get("elo_recent_logloss") or perf.get("elo_mean_logloss")
            
            if x_ll is not None and e_ll is not None:
                # Adaptive Temperature: Trust the winner more if the gap is clear.
                # If gap is small (e.g. 0.01), T increases to 0.18 (more blending).
                # If gap is large (e.g. 0.10), T decreases to 0.08 (trust the leader).
                gap = abs(float(x_ll) - float(e_ll))
                self._stacking_temp = float(max(0.08, min(0.25, 0.20 - (gap * 1.2))))
                
                # Weighted blending based on negative logloss
                w_xgb_raw = math.exp(-float(x_ll) / self._stacking_temp)
                w_elo_raw = math.exp(-float(e_ll) / self._stacking_temp)
                total_raw = w_xgb_raw + w_elo_raw
                
                if total_raw > 0:
                    self._component_weights["xgb"] = round(self._core_budget * (w_xgb_raw / total_raw), 3)
                    self._component_weights["elo"] = round(self._core_budget * (w_elo_raw / total_raw), 3)
                    self._model_mode = "stacked_ensemble"
            
            # Gap detection for champion/challenger status
            x_ll_val = float(x_ll) if x_ll else 1.0
            e_ll_val = float(e_ll) if e_ll else 1.0
            gap = x_ll_val - e_ll_val
            
            # Champion/Challenger Audit (Guardrail)
            # If XGB is significantly worse than Elo (> 0.02 logloss gap), 
            # we aggressively dampen it further than softmax suggests.
            if gap > 0.02:
                print(f"⚠️ XGB Underperformance detected (Gap={gap:+.3f}). Activating Elo-Champion mode.")
                self._component_weights["xgb"] *= 0.5
                self._component_weights["elo"] += (self._component_weights["xgb"] * 0.5)
                self._model_mode = "elo_champion"
            elif gap < -0.10:
                # Strong XGB lead
                self._model_mode = "xgb_champion"

            # Shrinkage factor (secondary smoothing)
            if gap > 0:
                self._shrink_alpha = float(max(0.2, min(1.0, 1.0 - (gap * 15.0))))
            else:
                self._shrink_alpha = 1.0

            # If XGB is worse than Elo by a meaningful margin, reduce its influence.
            # This is a guardrail for periods where feature refresh degrades quality.
            margin = 0.01
            gap = float(x_ll) - float(e_ll)
            if gap > margin:
                # Champion/challenger: if Elo is better on recent windows, treat
                # Elo as the champion and aggressively suppress XGB.
                self._model_mode = "elo_champion"
                self._component_weights["xgb"] = 0.0
                self._component_weights["elo"] = 0.35
                # Keep other signals but reduce their influence vs Elo
                self._component_weights["specialized"] = min(self._component_weights["specialized"], 0.15)
                self._component_weights["player"] = min(self._component_weights["player"], 0.10)
                self._component_weights["base"] = min(self._component_weights["base"], 0.05)
                adjusted = True
            else:
                adjusted = False

            # Additional shrinkage toward Elo when XGB underperforms.
            # Alpha=1 => no shrink. Alpha closer to 0 => mostly Elo.
            # If Elo is better by 0.03 logloss, alpha ~ 0.4.
            if gap > 0:
                self._shrink_alpha = float(max(0.2, min(1.0, 1.0 - (gap * 20.0))))
            else:
                self._shrink_alpha = 1.0

            print(
                "📌 Loaded model_performance.json "
                f"(xgb_ll={float(x_ll):.4f}, elo_ll={float(e_ll):.4f}, gap={gap:+.4f}, "
                f"mode={self._model_mode}, shrink_alpha={self._shrink_alpha:.2f}, adjusted={adjusted}) "
                f"weights={self._component_weights}"
            )
        except Exception:
            return

    def _load_dual_regime_components(self):
        """Pre-load both regular season and playoff model stacks"""
        # Phase 48: Multi-Model Stacking
        # Load Stacks
        self.xgb_stack_reg = self._load_regime_files(is_playoff=False)
        self.xgb_stack_ply = self._load_regime_files(is_playoff=True)
        
        # Set default active components (fallback for legacy lookups)
        # We pick the highest-weighted variant from the regular stack as the 'primary'
        if self.xgb_stack_reg:
            champ = self.xgb_stack_reg[0]
            self.calibrated_model = champ['model']
            self.feature_names = champ['feats']
            self.xgb_model = getattr(self.calibrated_model, 'estimator', None)
        elif self.xgb_stack_ply:
            champ = self.xgb_stack_ply[0]
            self.calibrated_model = champ['model']
            self.feature_names = champ['feats']
            self.xgb_model = getattr(self.calibrated_model, 'estimator', None)
        
        # 3. Load Common Components (Shared across regimes)
        self._load_common_calibrations()

    def _load_common_calibrations(self):
        """Load feature snapshots and calibration mappings that apply to both regimes"""
        try:
            snap_path = Path("model_feature_snapshot.json")
            if snap_path.exists():
                with open(snap_path, "r") as f:
                    self._feature_snapshot = json.load(f)
                print("✅ Loaded model_feature_snapshot.json")
        except Exception as e:
            print(f"⚠️ Could not load model_feature_snapshot.json: {e}")
            self._feature_snapshot = None

        # Scoreline distribution calibration (Negative Binomial dispersion)
        try:
            p = Path("scoreline_calibration.json")
            if p.exists():
                with open(p, "r") as f:
                    self._scoreline_calibration = json.load(f)
        except Exception:
            self._prob_calibration = None

        # Phase 10: Meta-Confidence Model
        try:
            with open('meta_confidence_model.pkl', 'rb') as f:
                self.confidence_model = pickle.load(f)
            print("✅ Loaded Phase 10 Meta-Confidence Model")
        except Exception as e:
            print(f"⚠️ Could not load meta-confidence model: {e}")
            self.confidence_model = None

        # Phase 12: Goal Margin Regression Model
        try:
            margin_path = Path("margin_regression_model.pkl")
            if margin_path.exists():
                with open(margin_path, "rb") as f:
                    self.margin_model = pickle.load(f)
                print(f"✅ Loaded Phase 12 Goal Margin Regression model from {margin_path}")
            else:
                print("⚠️ Goal Margin Regression model not found")
        except Exception as e:
            print(f"⚠️ Error loading goal margin model: {e}")
            self.margin_model = None

        # Total Goals Model (scoreline backbone)
        try:
            tg_path = Path("total_goals_model.pkl")
            if tg_path.exists():
                with open(tg_path, "rb") as f:
                    self.total_goals_model = pickle.load(f)
                print(f"✅ Loaded Total Goals model from {tg_path}")
            else:
                self.total_goals_model = None
        except Exception as e:
            print(f"⚠️ Error loading total goals model: {e}")
            self.total_goals_model = None

        # Home/Away Goals Models (preferred scoreline)
        try:
            hp = Path("home_goals_model.pkl")
            ap = Path("away_goals_model.pkl")
            if hp.exists():
                with open(hp, "rb") as f:
                    self.home_goals_model = pickle.load(f)
                print(f"✅ Loaded Home Goals model from {hp}")
            if ap.exists():
                with open(ap, "rb") as f:
                    self.away_goals_model = pickle.load(f)
                print(f"✅ Loaded Away Goals model from {ap}")
        except Exception as e:
            print(f"⚠️ Error loading home/away goals models: {e}")
            self.home_goals_model = None
            self.away_goals_model = None

        # Phase 17: Period 1 Meta-Model
        try:
            p1_model_path = Path("p1_outcome_model.pkl")
            if p1_model_path.exists():
                with open(p1_model_path, "rb") as f:
                    self.p1_model = pickle.load(f)
                print(f"✅ Loaded Phase 17 Period 1 Meta-Model from {p1_model_path}")
            else:
                self.p1_model = None
                print("⚠️ Period 1 Meta-Model not found")
        except Exception as e:
            print(f"⚠️ Error loading P1 model: {e}")
            self.p1_model = None

        # Dedicated Toss-Up Specialist Model
        try:
            toss_path = Path("toss_up_model.pkl")
            if toss_path.exists():
                with open(toss_path, "rb") as f:
                    self.toss_up_model = pickle.load(f)
                print(f"✅ Loaded Toss-Up Specialist Model from {toss_path}")
            else:
                self.toss_up_model = None
        except Exception as e:
            print(f"⚠️ Error loading toss_up_model: {e}")
            self.toss_up_model = None

        # 3. Load Finishing Profiles
        try:
            with open('team_scoring_profiles.json', 'r') as f:
                self.team_profiles = json.load(f)
            print(f"✅ Loaded {len(self.team_profiles)} team finishing profiles")
        except:
            print("⚠️ Could not load team finishing profiles")

        # 4. Load Travel Archetypes (Phase 5)
        try:
            with open('team_travel_archetypes.json', 'r') as f:
                self.travel_archetypes = json.load(f)
            print(f"✅ Loaded {len(self.travel_archetypes)} team travel archetypes")
        except:
            print("⚠️ Could not load travel archetypes")

        # 5. Load NHL Edge Profiles (Phase 6)
        try:
            file_path = Path('data/nhl_edge_data.json')
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                player_data = data.get('player_data', [])
                team_metrics = {}
                for p in player_data:
                    team = p.get('Team')
                    if not team: continue
                    if team not in team_metrics:
                        team_metrics[team] = {'top_speeds': [], 'bursts': []}
                    try:
                        speed = float(p.get('Top Speed', 0) or 0)
                        burst = float(p.get('Bursts>20 per mile', 0) or 0)
                        if speed > 0: team_metrics[team]['top_speeds'].append(speed)
                        if burst > 0: team_metrics[team]['bursts'].append(burst)
                    except: continue
                
                for team, metrics in team_metrics.items():
                    top_speeds = sorted(metrics['top_speeds'], reverse=True)[:3]
                    top_bursts = sorted(metrics['bursts'], reverse=True)[:3]
                    self.edge_profiles[team] = {
                        'edge_top_speed': np.mean(top_speeds) if top_speeds else 21.0,
                        'edge_bursts_per_mile': np.mean(top_bursts) if top_bursts else 1.5
                    }
                print(f"✅ Loaded Edge profiles for {len(self.edge_profiles)} teams")
            else:
                print("⚠️ data/nhl_edge_data.json not found for Edge features")
        except Exception as e:
            print(f"⚠️ Error loading Edge data: {e}")

        # 6. Load Team Encodings (Symbolic)
        try:
            with open('team_encodings.json', 'r') as f:
                self.team_encodings = json.load(f)
        except:
            pass

    def _load_regime_files(self, is_playoff=False) -> List[Dict[str, Any]]:
        """Helper to load model stack for a specific regime"""
        stack = []
        try:
            p = Path("model_performance.json")
            if p.exists():
                with open(p, "r") as f:
                    perf = json.load(f)
                
                variants = perf.get("variants", {})
                
                # Phase 48: Stacking Strategy
                # We load multiple variants and blend them.
                candidates = []
                if is_playoff:
                    candidates = ["playoff", "full", "recent"]
                else:
                    # In regular season, prioritize champion and recent window
                    champ = perf.get("champion", "full")
                    candidates = [champ, "recent", "full"]
                
                # Deduplicate candidates while preserving order
                candidates = list(dict.fromkeys(candidates))
                
                for var_name in candidates:
                    suffix = f"_{var_name}" if var_name != "calibrated" else ""
                    # Handle special naming conventions
                    model_path = Path(f"xgb_calibrated_model{suffix}.pkl")
                    if not model_path.exists() and var_name == "full":
                         model_path = Path("xgb_calibrated_model.pkl")

                    if model_path.exists():
                        # Get logloss for weighting
                        v_perf = variants.get(var_name, {})
                        v_ll = v_perf.get("test_logloss") or v_perf.get("recent_eval", {}).get("xgb_recent_logloss")
                        
                        # Fallback logloss if missing (neutral)
                        if v_ll is None:
                            v_ll = 0.693 
                            
                        try:
                            with open(model_path, "rb") as f:
                                model = pickle.load(f)
                            
                            # Features
                            feats = self.feature_names 
                            feat_path = Path(f"xgb_features{suffix}.pkl")
                            if not feat_path.exists() and suffix == "":
                                feat_path = Path("xgb_features.pkl")
                                
                            if feat_path.exists():
                                with open(feat_path, "rb") as f:
                                    feat_obj = pickle.load(f)
                                    if isinstance(feat_obj, dict): 
                                        feats = feat_obj.get("feature_names", feats)
                                    else: 
                                        feats = feat_obj
                            
                            stack.append({
                                "name": var_name,
                                "model": model,
                                "feats": list(feats) if feats else [],
                                "logloss": float(v_ll)
                            })
                        except Exception:
                            continue
        except Exception:
            pass

        # Final fallback if no stack built
        if not stack:
            suffix = "_playoff" if is_playoff else ""
            p_fallback = Path(f"xgb_calibrated_model{suffix}.pkl")
            if not p_fallback.exists(): p_fallback = Path("xgb_calibrated_model.pkl")
            
            if p_fallback.exists():
                try:
                    with open(p_fallback, "rb") as f:
                        model = pickle.load(f)
                    stack.append({"name": "fallback", "model": model, "feats": self.feature_names, "logloss": 0.693})
                except: pass

        # Calculate internal stack weights using Softmax (T=0.10)
        if stack:
            ll_list = [s["logloss"] for s in stack]
            raw_ws = [math.exp(-ll / 0.10) for ll in ll_list]
            total_w = sum(raw_ws)
            for i, s in enumerate(stack):
                s["stack_weight"] = raw_ws[i] / total_w
            
        return stack

    def _predict_xgboost(self, away_team, home_team, game_date_str=None, away_goalie=None, home_goalie=None, is_playoff=False, series_status=None) -> Optional[Dict]:
        """Make prediction using XGBoost model with dynamic features"""
        if not self.xgb_model or not self.feature_names:
            return None
            
        # Determine Game Date (default to today if None)
        if game_date_str:
            try:
                game_date = datetime.strptime(game_date_str, "%Y-%m-%d")
            except:
                game_date = datetime.now()
        else:
            game_date = datetime.now()
            
        tracker = self.history_tracker
        
        # Calculate Features
        home_elo = tracker.get_elo(home_team)
        away_elo = tracker.get_elo(away_team)
        
        home_rest = tracker.get_days_rest(home_team, game_date)
        away_rest = tracker.get_days_rest(away_team, game_date)
        
        h_l5 = tracker.get_rolling_stats(home_team, 5, alpha=0.3)
        a_l5 = tracker.get_rolling_stats(away_team, 5, alpha=0.3)
        h_l10 = tracker.get_rolling_stats(home_team, 10, alpha=0.3)
        a_l10 = tracker.get_rolling_stats(away_team, 10, alpha=0.3)
        
        # Venue Specific Rolling (L5)
        h_home_l5 = tracker.get_rolling_stats(home_team, 5, venue='home', alpha=0.3)
        a_away_l5 = tracker.get_rolling_stats(away_team, 5, venue='away', alpha=0.3)
        
        # Goalie Features (with B2B fatigue penalty)
        h_gsax_roll = tracker.goalies.get_rolling_gsax(home_goalie)
        a_gsax_roll = tracker.goalies.get_rolling_gsax(away_goalie)
        
        # Phase 2: Apply 15% penalty to goalies on back-to-backs (rest == 1)
        if home_rest == 1: h_gsax_roll *= 0.85
        if away_rest == 1: a_gsax_roll *= 0.85
        
        h_hdsv_roll = tracker.goalies.get_rolling_hdsv(home_goalie)
        a_hdsv_roll = tracker.goalies.get_rolling_hdsv(away_goalie)
        
        # Fatigue / Travel
        h_travel = tracker.get_travel_distance(home_team, home_team)
        a_travel = tracker.get_travel_distance(away_team, home_team) # Away team travels to home city
        
        # Finish Factors
        h_finish = self.team_profiles.get(home_team, 1.0)
        a_finish = self.team_profiles.get(away_team, 1.0)
        
        # Phase 48: Playoff Weight Decay
        # Reduce momentum bias (xg_10d/20d) by 20% if in playoff mode
        momentum_scalar = 0.8 if is_playoff else 1.0
        regime_flag = 1.0 if is_playoff else 0.0
        
        # Build Feature Vector (Optimized for 59.0% Accuracy Set)
        feature_data = {
            'regime_intensity': regime_flag,
            'elo_diff': (home_elo + tracker.elo.ha) - away_elo,
            
            # Contextual Features
            'rest_diff': home_rest - away_rest,
            'home_b2b': 1 if home_rest == 1 else 0,
            'away_b2b': 1 if away_rest == 1 else 0,
            'rest_adv_b2b': (1.0 if (home_rest > 1 and away_rest == 1) else (-1.0 if (home_rest == 1 and away_rest > 1) else 0.0)),
            
            # Goalie Difference
            'gsax_diff': h_gsax_roll - a_gsax_roll,
            'shrunk_gsax_diff': tracker.goalies.get_shrunk_gsax(home_goalie) - tracker.goalies.get_shrunk_gsax(away_goalie),
            'finish_diff': h_finish - a_finish,
            'finish_adj_xg_diff': (h_l5.get('xg_for', 2.5) * (0.8 + 0.2 * h_finish)) - (a_l5.get('xg_for', 2.5) * (0.8 + 0.2 * a_finish)),
            
            # NHL Edge Micro-Movement (Phase 6)
            'edge_speed_diff': self.edge_profiles.get(home_team, {}).get('edge_top_speed', 21.0) - self.edge_profiles.get(away_team, {}).get('edge_top_speed', 21.0),
            'edge_burst_diff': self.edge_profiles.get(home_team, {}).get('edge_burst_avg', 0.5) - self.edge_profiles.get(away_team, {}).get('edge_burst_avg', 0.5),
            
            # Rolling General (EWMA)
            'l5_goal_diff': h_l5.get('goal_diff', 0.0) - a_l5.get('goal_diff', 0.0),
            'l5_xg_diff': (h_l5.get('xg_diff', 0.0) - a_l5.get('xg_diff', 0.0)) * momentum_scalar,
            'l5_goals_for_diff': h_l5.get('goals_for', 3.0) - a_l5.get('goals_for', 3.0),
            'l5_goals_against_diff': a_l5.get('goals_against', 3.0) - h_l5.get('goals_against', 3.0),
            'l5_xg_for_diff': (h_l5.get('xg_for', 2.5) - a_l5.get('xg_for', 2.5)) * momentum_scalar,
            'l5_xg_against_diff': (a_l5.get('xg_against', 2.5) - h_l5.get('xg_against', 2.5)) * momentum_scalar,
            'l5_shots_diff': h_l5.get('shots', 30.0) - a_l5.get('shots', 30.0),
            'l5_corsi_diff': h_l5.get('corsi_pct', 50.0) - a_l5.get('corsi_pct', 50.0),
            'l5_pdo_diff': h_l5.get('pdo', 100.0) - a_l5.get('pdo', 100.0),
            'h_pdo_regress': 100.0 - (h_l5.get('pdo', 100.0) - a_l5.get('pdo', 100.0)),
            'l5_l10_xg_blend': (0.6 * (h_l5.get('xg_diff', 0.0) - a_l5.get('xg_diff', 0.0)) + 0.4 * (h_l10.get('xg_diff', 0.0) - a_l10.get('xg_diff', 0.0))) * momentum_scalar,
            'l5_l10_goal_blend': 0.6 * (h_l5.get('goal_diff', 0.0) - a_l5.get('goal_diff', 0.0)) + 0.4 * (h_l10.get('goal_diff', 0.0) - a_l10.get('goal_diff', 0.0)),
            'venue_momentum_diff': h_home_l5.get('goal_diff', 0.0) - a_away_l5.get('goal_diff', 0.0),
            
            # Special Teams (Matchup-Adjusted Phase 3)
            'l5_pp_diff': h_l5.get('pp_pct', 20.0) - a_l5.get('pp_pct', 20.0),
            'l5_pk_diff': h_l5.get('pk_pct', 80.0) - a_l5.get('pk_pct', 80.0),
            'l5_st_net': (h_l5.get('pp_pct', 20.0) - (100.0 - a_l5.get('pk_pct', 80.0))) - (a_l5.get('pp_pct', 20.0) - (100.0 - h_l5.get('pk_pct', 80.0))),
            'st_leverage_diff': ((h_l5.get('pp_pct', 20.0) * (100.0 - a_l5.get('pk_pct', 80.0))) - (a_l5.get('pp_pct', 20.0) * (100.0 - h_l5.get('pk_pct', 80.0)))) / 1000.0,
            'tight_game_leverage': (((home_elo + tracker.elo.ha) - away_elo) / 100.0) * 0.4 + (home_rest - away_rest) * 0.3 + (h_finish - a_finish) * 0.3,
            'h_pp_edge': h_l5.get('pp_pct', 20.0) - a_l5.get('pk_pct', 80.0), # Home PP vs Away PK
            'a_pp_edge': a_l5.get('pp_pct', 20.0) - h_l5.get('pk_pct', 80.0), # Away PP vs Home PK
            'h_discipline_target': a_l5.get('pim', 8.0), # How many PIMs does opponent take?
            'a_discipline_target': h_l5.get('pim', 8.0),
            
            # Phase 3 Fatigue Density
            'h_3_in_4': 1 if tracker.get_game_count_in_window(home_team, datetime.now(), 4) >= 3 else 0,
            'a_3_in_4': 1 if tracker.get_game_count_in_window(away_team, datetime.now(), 4) >= 3 else 0,
            
            # Technical Metrics (Symmetric)
            'l5_rush_diff': h_l5.get('rush', 2.0) - a_l5.get('rush', 2.0),
            'l5_nzt_diff': h_l5.get('nzt', 5.0) - a_l5.get('nzt', 5.0),
            'l5_ozs_diff': h_l5.get('ozs', 10.0) - a_l5.get('ozs', 10.0),
            'l5_dzs_diff': a_l5.get('dzs', 10.0) - h_l5.get('dzs', 10.0),
            'l5_hdc_diff': h_l5.get('hdc', 5.0) - a_l5.get('hdc', 5.0),
            'l5_pizza_diff': a_l5.get('pizzas', 2.0) - h_l5.get('pizzas', 2.0),
            
            # Phase 13: Tactical Signals
            'l5_royal_road_diff': h_l5.get('royal_road', 1.0) - a_l5.get('royal_road', 1.0),
            'l5_pressure_diff': h_l5.get('pressure', 2.0) - a_l5.get('pressure', 2.0),
            'l5_rebound_diff': h_l5.get('rebounds', 1.0) - a_l5.get('rebounds', 1.0),
            'l5_lateral_diff': h_l5.get('lateral', 5.0) - a_l5.get('lateral', 5.0),
            
            # Phase 15: Momentum Features
            'p1_xg_diff': h_l5.get('p1_xg', 0.8) - a_l5.get('p1_xg', 0.8),
            'p2_xg_diff': h_l5.get('p2_xg', 0.8) - a_l5.get('p2_xg', 0.8),
            'p3_xg_diff': h_l5.get('p3_xg', 0.8) - a_l5.get('p3_xg', 0.8),
            'p1_p2_dominance': (h_l10.get('p1_xg', 0.8) + h_l10.get('p2_xg', 0.8)) - (a_l10.get('p1_xg', 0.8) + a_l10.get('p2_xg', 0.8)),
            'h_preservation_rate': tracker.get_rolling_rate(home_team, 'led_after_p2', 'won_game', window=20),
            'a_preservation_rate': tracker.get_rolling_rate(away_team, 'led_after_p2', 'won_game', window=20),
            'h_comeback_rate': tracker.get_rolling_rate(home_team, 'trailed_after_p2', 'won_game', window=20),
            'a_comeback_rate': tracker.get_rolling_rate(away_team, 'trailed_after_p2', 'won_game', window=20),

            # Phase 18 Features
            'l5_nzt_possession_diff': h_l5.get('nzt_possession', 50.0) - a_l5.get('nzt_possession', 50.0),
            'l5_ca_shots_diff': a_l5.get('ca_shots', 0.0) - h_l5.get('ca_shots', 0.0),
            'l5_rush_sv_pct_diff': h_l5.get('rush_sv_pct', 90.0) - a_l5.get('rush_sv_pct', 90.0),
            
            # Venue Indicators
            'home_venue_goal_diff': h_home_l5.get('goal_diff', 0.0),
            'away_venue_goal_diff': a_away_l5.get('goal_diff', 0.0),
            # Phase 14: Season-Phase Context
            'season_month': datetime.now().month,
            'is_late_season': 1 if datetime.now().month in [3, 4] else 0,
            'h_desperation': self.standings.calculate_desperation_index(home_team),
            'a_desperation': self.standings.calculate_desperation_index(away_team),
            
            # Phase 4: Travel Jet Lag (TZ Delta)
            'tz_delta': TEAM_TIMEZONES.get(away_team, -5) - TEAM_TIMEZONES.get(home_team, -5),
            
            # Strength of Schedule (SoS)
            'home_sos': tracker.get_sos(home_team, 5),
            'away_sos': tracker.get_sos(away_team, 5),
            
            # Stability
            'l5_std_diff': tracker.get_rolling_std(home_team, 5) - tracker.get_rolling_std(away_team, 5),
            
            'l10_goal_diff': h_l10.get('goal_diff', 0.0) - a_l10.get('goal_diff', 0.0),
            'l10_xg_diff': (h_l10.get('xg_diff', 0.0) - a_l10.get('xg_diff', 0.0)) * momentum_scalar,
            
            # Interaction Features (Phase 8 Advanced DS)
            'elo_rest_inter': ((home_elo + self.history_tracker.elo.ha) - away_elo) * (home_rest - away_rest),
            'speed_finish_inter': (self.edge_profiles.get(home_team, {}).get('edge_top_speed', 21.0) - self.edge_profiles.get(away_team, {}).get('edge_top_speed', 21.0)) * (h_finish - a_finish),
            
            # Raw Components for Phase 11/12 Symbolic Features
            'home_xg': h_l5.get('xg_for', 2.5) * momentum_scalar,
            'away_xg': a_l5.get('xg_for', 2.5) * momentum_scalar,
            'home_elo': home_elo + tracker.elo.ha,
            'away_elo': away_elo,
            'home_win_rate': self.team_encodings.get('home_map', {}).get(home_team, self.team_encodings.get('home_prior', 0.5)),
            'away_win_rate': self.team_encodings.get('away_map', {}).get(away_team, self.team_encodings.get('away_prior', 0.5)),

            # Phase 9: Automated Interaction Discovery
            'home_win_rate_away_sos': self.team_encodings.get('home_map', {}).get(home_team, 0.5) * self.history_tracker.get_sos(away_team, 5),
            'away_b2b_home_strength': (1 if away_rest == 1 else 0) * h_finish,
            'l10_xg_st_inter': (h_l10.get('xg_diff', 0.0) - a_l10.get('xg_diff', 0.0)) * ((h_l5.get('pp_pct', 20.0) + h_l5.get('pk_pct', 80.0)) - (a_l5.get('pp_pct', 20.0) + a_l5.get('pk_pct', 80.0))),
            
            # Phase 11: Symbolic Feature Discovery
            'pressure_index': (h_l5.get('xg_for', 2.5) / (a_l5.get('xg_for', 2.5) + 0.1)) * ((home_elo + self.history_tracker.elo.ha) / (away_elo + 0.1)),
            'xg_efficiency': (h_l5.get('xg_for', 2.5) * (self.history_tracker.get_sos(home_team, 5) / 1500)) - (a_l5.get('xg_for', 2.5) * (self.history_tracker.get_sos(away_team, 5) / 1500)),
            'power_momentum': ((home_elo + self.history_tracker.elo.ha) - away_elo) * (h_l10.get('xg_diff', 0.0) - a_l10.get('xg_diff', 0.0)),

            # Phase 20: Environmental & Physical Hypoxia / Circadian / OT Features
            'hypoxia_fatigue': (max(0, TEAM_ELEVATIONS.get(home_team, 500) - TEAM_ELEVATIONS.get(away_team, 500)) / 1000.0) * (1.5 if away_rest <= 1 else 1.0),
            'eastbound_lag': max(0, TEAM_TIMEZONES.get(home_team, -5) - TEAM_TIMEZONES.get(away_team, -5)) * (1.5 if away_rest <= 1 else 1.0),
            'westbound_lag': max(0, TEAM_TIMEZONES.get(away_team, -5) - TEAM_TIMEZONES.get(home_team, -5)) * 0.5,
            'ot_3v3_diff': (self.edge_profiles.get(home_team, {}).get('edge_top_speed', 21.0) * self.edge_profiles.get(home_team, {}).get('edge_burst_avg', 0.5) * h_finish) - (self.edge_profiles.get(away_team, {}).get('edge_top_speed', 21.0) * self.edge_profiles.get(away_team, {}).get('edge_burst_avg', 0.5) * a_finish),
            'penalty_draw_arb': (h_l5.get('rush', 2.0) * (a_l5.get('pim', 8.0) / 8.0)) - (a_l5.get('rush', 2.0) * (h_l5.get('pim', 8.0) / 8.0))
        }
        
        # --- Helper for dynamic feature alignment ---
        def _get_aligned_df(model, regime_feats=None):
            if model is None: return None
            
            # Get feature names from model if possible, fallback to regime feats
            feats_to_use = regime_feats or self.feature_names
            if hasattr(model, 'get_booster'):
                feats_to_use = model.get_booster().feature_names
            elif hasattr(model, 'feature_names_in_'):
                feats_to_use = list(model.feature_names_in_)
            elif hasattr(model, 'feature_names'):
                feats_to_use = model.feature_names
                
            vec = []
            for name in feats_to_use:
                vec.append(feature_data.get(name, 0.0))
            return pd.DataFrame([vec], columns=feats_to_use)

        # 4. Phase 48: Stacked Prediction
        active_stack = self.xgb_stack_ply if is_playoff else self.xgb_stack_reg
        if not active_stack:
            # Minimal fallback to legacy single model if stack failed to load
            if self.calibrated_model:
                active_stack = [{"model": self.calibrated_model, "feats": self.feature_names, "stack_weight": 1.0, "name": "legacy"}]
            else:
                return None
            
        prob_sum = 0.0
        weight_sum = 0.0
        
        for entry in active_stack:
            v_model = entry['model']
            v_feats = entry['feats']
            v_weight = entry.get('stack_weight', 1.0)
            
            try:
                # Feature Snapshot Guard (only for the primary variant in regular season)
                if entry['name'] == "full" and not is_playoff:
                    if isinstance(self._feature_snapshot, dict) and self._feature_snapshot.get("sha256"):
                        joined = "\n".join([str(x) for x in v_feats]).encode("utf-8")
                        cur = hashlib.sha256(joined).hexdigest()
                        exp = str(self._feature_snapshot.get("sha256"))
                        if cur != exp:
                            print(f"⚠️ Feature snapshot mismatch for {entry['name']} (runtime={cur} expected={exp})")
                            continue # Skip this variant if it's drifting

                df_v = _get_aligned_df(v_model, regime_feats=v_feats)
                v_prob = v_model.predict_proba(df_v)[0][1]
                prob_sum += (v_prob * v_weight)
                weight_sum += v_weight
            except Exception as e:
                print(f"⚠️ Variant {entry['name']} prediction failed: {e}")
                
        if weight_sum > 0:
            prob = prob_sum / weight_sum
        else:
            return None
            
        # Use the first variant for downstream sub-models (margin, etc.) as primary alignment
        active_model = active_stack[0]['model']
        active_feats = active_stack[0]['feats']

        try:
            # 5. Apply post-hoc calibration mapping if available.
            try:
                pts = None
                if isinstance(self._prob_calibration, dict):
                    pts = self._prob_calibration.get("points")
                if pts and isinstance(pts, list) and len(pts) >= 2:
                    x = float(prob)
                    pts_sorted = sorted((float(a), float(b)) for a, b in pts)
                    if x <= pts_sorted[0][0]:
                        prob = float(pts_sorted[0][1])
                    elif x >= pts_sorted[-1][0]:
                        prob = float(pts_sorted[-1][1])
                    else:
                        for i in range(1, len(pts_sorted)):
                            x0, y0 = pts_sorted[i - 1]
                            x1, y1 = pts_sorted[i]
                            if x0 <= x <= x1:
                                t = 0.0 if x1 == x0 else (x - x0) / (x1 - x0)
                                prob = float(y0 + t * (y1 - y0))
                                break
                    prob = float(max(1e-6, min(1.0 - 1e-6, prob)))

            except Exception:
                pass
            
            # 4b. Toss-Up Specialist Model Blend (breaks 50/50 deadlocks using depth-1 additive micro signals)
            if self.toss_up_model is not None and abs(prob - 0.50) <= 0.055:
                try:
                    df_toss = _get_aligned_df(self.toss_up_model, regime_feats=active_feats)
                    toss_prob = float(self.toss_up_model.predict_proba(df_toss)[0][1])
                    # Decisively resolve coin-flip matchups with the specialist
                    prob = float(0.40 * prob + 0.60 * toss_prob)
                    prob = float(max(1e-6, min(1.0 - 1e-6, prob)))
                except Exception as e:
                    print(f"⚠️ Toss-up model inference warning: {e}")

            away_prob = (1 - prob) * 100
            home_prob = prob * 100
            
            # 5. Goal Margin Prediction (Phase 12)
            # Use dynamic alignment to handle potentially different features in margin model
            predicted_margin = 0.0
            if self.margin_model is not None:
                try:
                    df_margin = _get_aligned_df(self.margin_model, regime_feats=active_feats)
                    predicted_margin = float(self.margin_model.predict(df_margin)[0])
                except Exception as e:
                    print(f"Margin prediction error: {e}")

            # 5b. Scoreline: Bivariate Poisson Joint Score Engine
            predicted_total = None
            predicted_home_goals = None
            predicted_away_goals = None
            top_3_scores = []
            total_over_5_5 = None
            total_over_6_5 = None
            pl_h_minus_1_5 = None
            pl_a_minus_1_5 = None
            
            try:
                h = 3.1
                a = 2.9
                if self.home_goals_model is not None and self.away_goals_model is not None:
                    df_h = _get_aligned_df(self.home_goals_model, regime_feats=active_feats)
                    df_a = _get_aligned_df(self.away_goals_model, regime_feats=active_feats)
                    h = float(self.home_goals_model.predict(df_h)[0])
                    a = float(self.away_goals_model.predict(df_a)[0])
                elif self.total_goals_model is not None:
                    df_tg = _get_aligned_df(self.total_goals_model, regime_feats=active_feats)
                    tot = float(self.total_goals_model.predict(df_tg)[0])
                    h = (tot + float(predicted_margin)) / 2.0
                    a = (tot - float(predicted_margin)) / 2.0
                
                # Clamp predicted goal intensities
                h = float(max(0.5, min(7.5, h)))
                a = float(max(0.5, min(7.5, a)))
                
                # Generate optimal scoreline and market probabilities
                biv = self.compute_bivariate_score_distribution(h, a, home_favored=(home_prob >= away_prob))
                predicted_home_goals = biv["best_home_goals"]
                predicted_away_goals = biv["best_away_goals"]
                predicted_total = float(predicted_home_goals + predicted_away_goals)
                top_3_scores = biv["top_3_scores"]
                total_over_5_5 = biv["total_over_5_5"]
                total_over_6_5 = biv["total_over_6_5"]
                pl_h_minus_1_5 = biv["puckline_home_minus_1_5"]
                pl_a_minus_1_5 = biv["puckline_away_minus_1_5"]
            except Exception as e:
                print(f"Bivariate score prediction error: {e}")
                predicted_home_goals = 3 if home_prob >= away_prob else 2
                predicted_away_goals = 2 if home_prob >= away_prob else 3
                predicted_total = 5.0
            
            # 6. Meta-Confidence Estimation
            confidence_tier = "Standard"
            if self.confidence_model is not None:
                try:
                    df_conf = _get_aligned_df(self.confidence_model, regime_feats=active_feats)
                    is_correct = self.confidence_model.predict(df_conf)[0]
                    if is_correct == 1 and max(away_prob, home_prob) > 55:
                        confidence_tier = "🔥 High Confidence"
                    elif is_correct == 0 or max(away_prob, home_prob) < 52:
                        confidence_tier = "⚠️ High Risk"
                except Exception as e:
                    print(f"Confidence model error: {e}")
            
            # 7. Period 1 Outcome Model (Phase 17)
            p1_win_prob = 0.5
            if self.p1_model is not None:
                try:
                    df_p1 = _get_aligned_df(self.p1_model, regime_feats=active_feats)
                    p1_win_prob = self.p1_model.predict_proba(df_p1)[0][1]
                except Exception as e:
                    print(f"P1 prediction error: {e}")
            
            # Phase 47/48 Fatigue Metrics for Score Model
            away_games_7d = tracker.get_game_count_in_window(away_team, datetime.now(), 7)
            home_games_7d = tracker.get_game_count_in_window(home_team, datetime.now(), 7)
            away_travel = tracker.get_travel_distance(away_team, home_team)
            home_travel = tracker.get_travel_distance(home_team, home_team) # Home stays home

            # Phase 48: Goalie Shot Pressure Factor (SPF)
            # Incorporate physical exertion of goalie into team TWI
            away_shots_30d = getattr(tracker.goalies, 'get_rolling_shots_faced', lambda x, y: 0)(away_goalie, 30)
            home_shots_30d = getattr(tracker.goalies, 'get_rolling_shots_faced', lambda x, y: 0)(home_goalie, 30)
            avg_league_shots = 30.0 * 10 # ~300 over 10 games played
            
            a_spf = max(1.0, (away_shots_30d / avg_league_shots)) if away_shots_30d > 0 else 1.0
            h_spf = max(1.0, (home_shots_30d / avg_league_shots)) if home_shots_30d > 0 else 1.0

            return {
                'away_team': away_team,
                'home_team': home_team,
                'away_prob': away_prob,
                'home_prob': home_prob,
                'predicted_margin': predicted_margin,
                'predicted_total_goals': predicted_total,
                'predicted_home_goals': predicted_home_goals,
                'predicted_away_goals': predicted_away_goals,
                'top_3_scores': top_3_scores,
                'scoreline_nb_size': self._scoreline_calibration.get("total_goals_nb_size") if isinstance(self._scoreline_calibration, dict) else None,
                'total_over_5_5': total_over_5_5,
                'total_under_5_5': (None if total_over_5_5 is None else float(1.0 - total_over_5_5)),
                'total_over_6_5': total_over_6_5,
                'total_under_6_5': (None if total_over_6_5 is None else float(1.0 - total_over_6_5)),
                'puckline_home_minus_1_5': pl_h_minus_1_5,
                'puckline_away_minus_1_5': pl_a_minus_1_5,
                'confidence_tier': confidence_tier,
                'p1_home_prob': p1_win_prob * 100,
                # Fatigue signals for downstream score model calibration/OT modeling
                'away_back_to_back': 1 if away_rest == 1 else 0,
                'home_back_to_back': 1 if home_rest == 1 else 0,
                'away_rest_value': float(away_rest),
                'home_rest_value': float(home_rest),
                'away_3_in_4': bool(feature_data.get('a_3_in_4')),
                'home_3_in_4': bool(feature_data.get('h_3_in_4')),
                'away_games_7d': away_games_7d,
                'home_games_7d': home_games_7d,
                'away_travel_miles': away_travel,
                'away_goalie_shots_30d': float(away_shots_30d),
                'home_goalie_shots_30d': float(home_shots_30d),
                'feature_data': feature_data,
                'prediction_type': 'xgboost_ml'
            }
        except Exception as e:
            print(f"XGBoost prediction error: {e}")
            return None
    
    def get_injury_impact(self, team: str) -> float:
        """Calculate injury impact multiplier (0.90 - 1.0) using cached RotoWire data"""
        try:
            now = datetime.now()
            # Cache rotowire scrape for 15 minutes to avoid redundant network requests
            if not hasattr(self, '_rotowire_cache') or self._rotowire_cache is None or (now - getattr(self, '_rotowire_cache_time', datetime.min)).total_seconds() > 900:
                self._rotowire_cache = self.rotowire.scrape_daily_data()
                self._rotowire_cache_time = now
            
            data = self._rotowire_cache or {}
            impact = 1.0
            
            # Find the team's injuries in the scraped data
            for game in data.get('games', []):
                team_injuries = []
                if game.get('away_team') == team:
                    team_injuries = game.get('injuries', [])
                elif game.get('home_team') == team:
                    team_injuries = game.get('injuries', [])
                
                if team_injuries:
                    for inj in team_injuries:
                        status = inj.get('status', '').upper()
                        # Only count significant/confirmed outs
                        if any(s in status for s in ['OUT', 'IR', 'INJURED']):
                            # Tier system (Phase 4): star players are ~3%, regulars ~1%
                            impact -= 0.015 
                        elif 'QUESTIONABLE' in status or 'GTD' in status:
                            impact -= 0.005
            
            return max(0.88, impact) # Cap impact at 12% reduction
        except Exception:
            return 1.0
            return 1.0
    
    def predict(self, away_team: str, home_team: str, 
                game_id: str = None, game_date: str = None,
                away_lineup: Dict = None, home_lineup: Dict = None,
                away_goalie: str = None, home_goalie: str = None,
                away_injuries: list = None, home_injuries: list = None,
                vegas_odds: Dict = None, is_playoff: bool = False,
                series_status: str = None) -> Dict:
        """Meta-ensemble prediction combining all methods"""
        predictions = []
        weights = []
        xgb_p1_prob = 50.0
        
        # 1. XGBoost ML Model (50% Weight - Highest Accuracy Component)
        xgb_weight = float(self._component_weights.get("xgb", 0.50))
        spec_weight = float(self._component_weights.get("specialized", 0.25))
        
        # Phase 18: Playoff Boost
        if is_playoff:
            xgb_weight = 0.40
            spec_weight = 0.35
            
            # Phase 19: Elimination Game Boost
            # If it's a potential close-out game, specialized series logic is even more critical
            if series_status and self._is_elimination_game(series_status):
                xgb_weight = 0.35
                spec_weight = 0.45
            
        xgb_pred = self._predict_xgboost(away_team, home_team, game_date, away_goalie, home_goalie, is_playoff=is_playoff, series_status=series_status)
        xgb_margin = 0.0
        if xgb_pred:
            predictions.append(xgb_pred)
            weights.append(xgb_weight)
            xgb_margin = xgb_pred.get('predicted_margin', 0.0)
            xgb_p1_prob = xgb_pred.get('p1_home_prob', 50.0)

        # 1b. Elo baseline (stacking-safe, stable)
        # Adds a strong, low-variance prior that helps when feature quality is degraded
        # (e.g. missing goalie confirmations, partial advanced-metrics refresh).
        try:
            elo_home = float(self.history_tracker.elo.get_win_prob(home_team, away_team))  # P(home)
            elo_home = max(0.01, min(0.99, elo_home))
            predictions.append({
                'away_prob': (1.0 - elo_home) * 100.0,
                'home_prob': elo_home * 100.0,
                'prediction_type': 'elo_baseline'
            })
            weights.append(float(self._component_weights.get("elo", 0.10)))
        except Exception as e:
            print(f"Elo baseline failed: {e}")
        
        # 2. Specialized ensemble (25% weight)
        try:
            spec_pred = self.specialized_ensemble.predict(away_team, home_team, game_id, game_date, is_playoff=is_playoff, series_status=series_status)
            predictions.append(spec_pred)
            weights.append(spec_weight)
        except Exception as e:
            print(f"Specialized ensemble failed: {e}")
        
        # 3. Player-level model (15% weight)
        if away_lineup and home_lineup and hasattr(self.base_model, 'predict_game_with_lineup'):
            try:
                player_pred = self.base_model.predict_game_with_lineup(
                    away_team, home_team, away_lineup, home_lineup, game_id, game_date
                )
                predictions.append(player_pred)
                weights.append(float(self._component_weights.get("player", 0.15)))
            except Exception as e:
                print(f"Player-level model failed: {e}")
        
        # 4. Base model (10% weight - reduced due to lower accuracy)
        try:
            base_pred = self.base_model.predict_game(away_team, home_team, game_id=game_id, game_date=game_date, is_playoff=is_playoff, series_status=series_status)
            predictions.append(base_pred)
            weights.append(float(self._component_weights.get("base", 0.10)))
        except Exception as e:
            print(f"Base model failed: {e}")
            
        # 4. Vegas Odds Blending (Phase 4)
        if vegas_odds:
            try:
                v_away = vegas_odds.get('away_ml', 0)
                v_home = vegas_odds.get('home_ml', 0)
                if abs(v_away) > 0 and abs(v_home) > 0:
                    a_implied = 100 / (v_away + 100) if v_away > 0 else abs(v_away) / (abs(v_away) + 100)
                    h_implied = 100 / (v_home + 100) if v_home > 0 else abs(v_home) / (abs(v_home) + 100)
                    total = a_implied + h_implied
                    predictions.append({
                        'away_prob': (a_implied / total) * 100,
                        'home_prob': (h_implied / total) * 100,
                        'prediction_type': 'vegas_market'
                    })
                    weights.append(float(self._component_weights.get("vegas", 0.15))) # Market significance
            except: pass

        if not predictions:
            raise Exception("All prediction methods failed")
        
        # Weighted ensemble calculation in Logit Space
        logits = []
        eff_weights = []
        for p, w in zip(predictions, weights):
            ph = p.get('home_prob', 50.0)
            pa = p.get('away_prob', 50.0)
            s = float(ph) + float(pa)
            p_norm = (float(ph) / s) if s > 0 else 0.5
            p_norm = max(0.01, min(0.99, p_norm))
            z = math.log(p_norm / (1.0 - p_norm))
            logits.append(z)
            eff_weights.append(max(0.01, float(w)))

        total_weight = sum(eff_weights) if eff_weights else 1.0
        base_logit = sum(z * w for z, w in zip(logits, eff_weights)) / total_weight

        # Apply Contextual Factors in Logit Space
        # 1. Injury Impact (log odds ratio)
        h_health = self.get_injury_impact(home_team) if not home_injuries else (1.0 - self._team_injury_impact(home_injuries))
        a_health = self.get_injury_impact(away_team) if not away_injuries else (1.0 - self._team_injury_impact(away_injuries))
        h_health = max(0.5, float(h_health))
        a_health = max(0.5, float(a_health))
        delta_inj = math.log(h_health / a_health)

        # 2. Travel & Fatigue Impact
        h_travel = self.history_tracker.get_travel_distance(home_team, home_team)
        a_travel = self.history_tracker.get_travel_distance(away_team, home_team)
        h_is_rw = self.travel_archetypes.get(home_team, {}).get('is_road_warrior', False)
        a_is_rw = self.travel_archetypes.get(away_team, {}).get('is_road_warrior', False)
        
        h_fatigue = max(0.95, 1.0 - (h_travel / 20000.0))
        a_fatigue = max(0.95, 1.0 - (a_travel / 20000.0))
        if h_is_rw and h_fatigue < 1.0:
            h_fatigue = 1.0 - ((1.0 - h_fatigue) * 0.5)
        if a_is_rw and a_fatigue < 1.0:
            a_fatigue = 1.0 - ((1.0 - a_fatigue) * 0.5)
        delta_fatigue = math.log(max(0.5, h_fatigue) / max(0.5, a_fatigue))

        # 3. Goalie HDSv% Signal
        h_hdsv = self.history_tracker.goalies.get_rolling_hdsv(home_goalie)
        a_hdsv = self.history_tracker.goalies.get_rolling_hdsv(away_goalie)
        delta_hdsv = float(np.clip((h_hdsv - a_hdsv) * 0.5, -0.3, 0.3))

        # Total combined logit
        total_logit = base_logit + delta_inj + delta_fatigue + delta_hdsv

        # Invert logit to get calibrated probability
        calibrated_home_p = 1.0 / (1.0 + math.exp(-total_logit))

        # Shrinkage toward Elo / baseline for stability
        try:
            alpha = float(getattr(self, "_shrink_alpha", 1.0))
            if alpha < 0.999:
                elo_home_p = float(self.history_tracker.elo.get_win_prob(home_team, away_team))
                calibrated_home_p = alpha * calibrated_home_p + (1.0 - alpha) * elo_home_p
        except Exception:
            pass

        calibrated_home_p = float(max(0.05, min(0.95, calibrated_home_p)))
        calibrated_away_p = 1.0 - calibrated_home_p

        ensemble_home = calibrated_home_p * 100.0
        ensemble_away = calibrated_away_p * 100.0

        # 3b. Toss-Up Micro-Leverage Index (TMLI: Calibrated with Physical & Tactical Signals)
        if abs(ensemble_home - 50.0) <= 5.5:
            fd = xgb_pred.get('feature_data', {}) if xgb_pred else {}
            pp_diff = float(fd.get('l5_pp_diff', 0.0))
            st_lev = float(fd.get('st_leverage_diff', 0.0))
            st_net = float(fd.get('l5_st_net', 0.0))
            h_b2b = (xgb_pred.get('home_back_to_back', 0) == 1) if xgb_pred else False
            a_b2b = (xgb_pred.get('away_back_to_back', 0) == 1) if xgb_pred else False
            b2b_val = 1.0 if (a_b2b and not h_b2b) else (-1.0 if (h_b2b and not a_b2b) else 0.0)
            h_rest = float(xgb_pred.get('home_rest_value', 2.0)) if xgb_pred else 2.0
            a_rest = float(xgb_pred.get('away_rest_value', 2.0)) if xgb_pred else 2.0
            rest_diff = h_rest - a_rest
            gsax_diff = float(fd.get('shrunk_gsax_diff', fd.get('gsax_diff', 0.0)))
            pizza_diff = float(fd.get('l5_pizza_diff', 0.0))
            goals_for_diff = float(fd.get('l5_goals_for_diff', 0.0))
            nzt_diff = float(fd.get('l5_nzt_diff', 0.0))
            finish_xg = float(fd.get('finish_adj_xg_diff', 0.0))
            speed_finish = float(fd.get('speed_finish_inter', 0.0))
            corsi_diff = float(fd.get('l5_corsi_diff', 0.0))
            pdo_diff = float(fd.get('l5_pdo_diff', 0.0))
            
            # Physical & environmental features
            hypoxia_fatigue = float(fd.get('hypoxia_fatigue', 0.0))
            eastbound_lag = float(fd.get('eastbound_lag', 0.0))
            westbound_lag = float(fd.get('westbound_lag', 0.0))
            ot_3v3_diff = float(fd.get('ot_3v3_diff', 0.0))
            penalty_draw_arb = float(fd.get('penalty_draw_arb', 0.0))

            # Multi-dimensional logit micro-leverage tie-breaker (TMLI v2)
            tmli_logit = (
                pp_diff * 0.02498 +
                st_lev * 0.05443 +
                st_net * 0.14842 +
                b2b_val * 0.05965 +
                rest_diff * (-0.08504) +
                gsax_diff * 0.01665 +
                pizza_diff * (-0.00611) +
                goals_for_diff * (-0.02317) +
                nzt_diff * (-0.09034) +
                finish_xg * 0.12120 +
                speed_finish * 0.19680 +
                corsi_diff * 0.01163 +
                (-pdo_diff) * 0.03851 +
                hypoxia_fatigue * (-0.04083) +
                eastbound_lag * 0.07980 +
                (-westbound_lag) * 0.06691 +
                ot_3v3_diff * 0.04013 +
                penalty_draw_arb * 0.02284 +
                0.11682 # Calibrated baseline home bias
            )

            # Apply micro-leverage adjustment directly to logit space
            total_logit += tmli_logit
            calibrated_home_p = 1.0 / (1.0 + math.exp(-total_logit))
            calibrated_home_p = float(max(0.05, min(0.95, calibrated_home_p)))
            calibrated_away_p = 1.0 - calibrated_home_p
            ensemble_home = calibrated_home_p * 100.0
            ensemble_away = calibrated_away_p * 100.0

        # 4. Market Edge Calculation (+EV Tracking - Phase 16)
        edge_away = 0.0
        edge_home = 0.0
        if vegas_odds:
            try:
                v_away = vegas_odds.get('away_ml')
                v_home = vegas_odds.get('home_ml')
                if v_away and v_home:
                    implied_away = 100 / (v_away + 100) if v_away > 0 else abs(v_away) / (abs(v_away) + 100)
                    implied_home = 100 / (v_home + 100) if v_home > 0 else abs(v_home) / (abs(v_home) + 100)
                    edge_away = (ensemble_away / 100.0 - implied_away) / implied_away * 100 if implied_away > 0 else 0
                    edge_home = (ensemble_home / 100.0 - implied_home) / implied_home * 100 if implied_home > 0 else 0
            except Exception:
                pass

        # 5. Final Aggregation
        confidence = max(ensemble_away, ensemble_home) / 100
        agreement_score = self._calculate_agreement(predictions, away_team, home_team)
        
        # Quant 4-Tier Confidence Classification
        fav_prob = max(ensemble_home, ensemble_away)
        if fav_prob >= 64.0 or (fav_prob >= 60.0 and abs(xgb_margin) >= 1.2):
            confidence_tier = "💎 Elite Lock"
        elif fav_prob >= 56.5 or (fav_prob >= 54.0 and abs(xgb_margin) >= 0.8):
            confidence_tier = "🔥 High Confidence"
        elif fav_prob >= 52.5:
            confidence_tier = "⚖️ Moderate Value"
        else:
            confidence_tier = "🎲 Toss-Up"
        
        # Phase 17: Bankroll Management & Kelly Criterion
        suggested_units = 0.0
        edge = edge_home if ensemble_home > ensemble_away else edge_away
        if edge > 0:
            # Kelly Criterion: f = (p*b - q) / b
            # f = fraction of bankroll
            # p = probability of winning (model_prob)
            # b = net odds (decimal odds - 1)
            # q = probability of losing (1 - p)
            try:
                # Convert moneyline to decimal
                ml = vegas_odds.get('home_ml') if ensemble_home > ensemble_away else vegas_odds.get('away_ml')
                if ml:
                    decimal_odds = (ml / 100 + 1) if ml > 0 else (100 / abs(ml) + 1)
                    b = decimal_odds - 1
                    p = max(ensemble_home, ensemble_away) / 100.0
                    q = 1 - p
                    f = (p * b - q) / b
                    # Apply Fractional Kelly (usually 0.25 to stay conservative)
                    suggested_units = max(0, f * 0.25 * 10.0) # Scale to a 10-unit scale
                    suggested_units = round(suggested_units, 1)
            except: pass

        # 5. Systematic Upset & Trap Game Detection
        is_upset_alert = False
        trap_reasons = []
        upset_prob = 0.0
        
        # Check if Favorite is falling into a known statistical trap
        fav_side = "home" if ensemble_home >= ensemble_away else "away"
        fav_prob = max(ensemble_home, ensemble_away)
        
        if fav_prob >= 53.0:
            h_b2b = (xgb_pred.get('home_back_to_back', 0) == 1) if xgb_pred else False
            a_b2b = (xgb_pred.get('away_back_to_back', 0) == 1) if xgb_pred else False
            h_rest = float(xgb_pred.get('home_rest_value', 2.0)) if xgb_pred else 2.0
            a_rest = float(xgb_pred.get('away_rest_value', 2.0)) if xgb_pred else 2.0
            a_travel = float(xgb_pred.get('away_travel_miles', 0.0)) if xgb_pred else 0.0
            
            if fav_side == "home":
                if h_b2b:
                    upset_prob += 0.22
                    trap_reasons.append(f"{home_team} playing on 0 days rest (Back-to-Back)")
                if a_rest >= 3 and h_rest <= 1:
                    upset_prob += 0.16
                    trap_reasons.append(f"{away_team} rest advantage (+{int(a_rest - h_rest)} days)")
            else: # Away favorite
                if a_b2b:
                    upset_prob += 0.25
                    trap_reasons.append(f"Road favorite {away_team} playing on 0 days rest (Back-to-Back)")
                if a_travel >= 1200:
                    upset_prob += 0.12
                    trap_reasons.append(f"Road fatigue ({int(a_travel)} travel miles)")
                if h_rest >= 3 and a_rest <= 1:
                    upset_prob += 0.16
                    trap_reasons.append(f"Home underdog {home_team} rest advantage (+{int(h_rest - a_rest)} days)")
            
            # If high trap probability, trigger Upset Alert
            if upset_prob >= 0.35:
                is_upset_alert = True
                confidence_tier = "🚨 High Risk Upset Alert"
                # If extreme trap spot, adjust probabilities toward underdog
                if upset_prob >= 0.45:
                    if fav_side == "home":
                        calibrated_home_p = float(max(0.40, calibrated_home_p - 0.06))
                        calibrated_away_p = 1.0 - calibrated_home_p
                    else:
                        calibrated_away_p = float(max(0.40, calibrated_away_p - 0.06))
                        calibrated_home_p = 1.0 - calibrated_away_p
                    ensemble_home = calibrated_home_p * 100.0
                    ensemble_away = calibrated_away_p * 100.0

        # 6. Strict Winner-Scoreline Coherence & Dynamic Bivariate Scoreline
        home_fav = (ensemble_home >= ensemble_away)
        win_p = max(ensemble_home, ensemble_away) / 100.0
        
        # Expected pace conditioning via Continuous Tactical Telemetry & Empirical Bayes H2H Shrinkage
        h_speed = self.edge_profiles.get(home_team, {}).get('edge_top_speed', 21.0) if hasattr(self, 'edge_profiles') and self.edge_profiles else 21.0
        a_speed = self.edge_profiles.get(away_team, {}).get('edge_top_speed', 21.0) if hasattr(self, 'edge_profiles') and self.edge_profiles else 21.0
        h_burst = self.edge_profiles.get(home_team, {}).get('edge_burst_avg', 0.5) if hasattr(self, 'edge_profiles') and self.edge_profiles else 0.5
        a_burst = self.edge_profiles.get(away_team, {}).get('edge_burst_avg', 0.5) if hasattr(self, 'edge_profiles') and self.edge_profiles else 0.5
        speed_burst_norm = ((h_speed * h_burst + a_speed * a_burst) / 2.0 - 10.5) / 1.5

        h_finish = self.team_profiles.get(home_team, 1.0) if hasattr(self, 'team_profiles') and self.team_profiles else 1.0
        a_finish = self.team_profiles.get(away_team, 1.0) if hasattr(self, 'team_profiles') and self.team_profiles else 1.0
        finish_norm = (h_finish * a_finish - 1.0) / 0.15

        base_clash_pace = 6.10 + 0.15 * speed_burst_norm + 0.10 * finish_norm
        
        # Empirical Bayes H2H Shrinkage (k=4.0 prior weight against base tactical clash)
        shrunk_pace = self.history_tracker.get_h2h_pace(home_team, away_team, prior_weight=4.0, league_mean=base_clash_pace)
        tot_pred = max(4.5, min(7.8, shrunk_pace))
        
        margin_pred = abs(xgb_margin) if xgb_margin else 2.6 * (win_p - 0.50)
        
        if home_fav:
            lam_h = (tot_pred + margin_pred) / 2.0
            lam_a = (tot_pred - margin_pred) / 2.0
        else:
            lam_a = (tot_pred + margin_pred) / 2.0
            lam_h = (tot_pred - margin_pred) / 2.0
            
        biv = self.compute_bivariate_score_distribution(lam_h, lam_a, home_favored=home_fav, win_prob=win_p)
        pred_h_goals = int(biv["best_home_goals"])
        pred_a_goals = int(biv["best_away_goals"])
        
        # Enforce strict alignment between ensemble winner probability and predicted score
        if home_fav and pred_h_goals <= pred_a_goals:
            pred_h_goals = pred_a_goals + 1
        elif (not home_fav) and pred_a_goals <= pred_h_goals:
            pred_a_goals = pred_h_goals + 1
                
        pred_total_goals = pred_h_goals + pred_a_goals

        return {
            'away_team': away_team,
            'home_team': home_team,
            'away_prob': ensemble_away,
            'home_prob': ensemble_home,
            'predicted_winner': away_team if ensemble_away > ensemble_home else home_team,
            'prediction_confidence': max(ensemble_away, ensemble_home) / 100.0,
            'confidence_tier': confidence_tier,
            'is_upset_alert': is_upset_alert,
            'upset_probability': float(upset_prob),
            'trap_reasons': trap_reasons,
            'predicted_margin': xgb_margin,
            'edge_away': edge_away,
            'edge_home': edge_home,
            'is_plus_ev_away': edge_away > 5.0,
            'is_plus_ev_home': edge_home > 5.0,
            'suggested_units': suggested_units,
            'p1_home_prob': xgb_p1_prob,
            'contexts_used': xgb_pred.get('contexts_used', []) if xgb_pred else [],
            # Fatigue and Goalie metrics for downstream consumers
            'away_back_to_back': xgb_pred.get('away_back_to_back', 0) if xgb_pred else 0,
            'home_back_to_back': xgb_pred.get('home_back_to_back', 0) if xgb_pred else 0,
            'away_rest_value': xgb_pred.get('away_rest_value', 2.0) if xgb_pred else 2.0,
            'home_rest_value': xgb_pred.get('home_rest_value', 2.0) if xgb_pred else 2.0,
            'away_3_in_4': xgb_pred.get('away_3_in_4', False) if xgb_pred else False,
            'home_3_in_4': xgb_pred.get('home_3_in_4', False) if xgb_pred else False,
            'away_games_7d': xgb_pred.get('away_games_7d', 1) if xgb_pred else 1,
            'home_games_7d': xgb_pred.get('home_games_7d', 1) if xgb_pred else 1,
            'away_travel_miles': xgb_pred.get('away_travel_miles', 0.0) if xgb_pred else 0.0,
            'home_travel_miles': xgb_pred.get('home_travel_miles', 0.0) if xgb_pred else 0.0,
            'away_goalie_shots_30d': xgb_pred.get('away_goalie_shots_30d', 0.0) if xgb_pred else 0.0,
            'home_goalie_shots_30d': xgb_pred.get('home_goalie_shots_30d', 0.0) if xgb_pred else 0.0,
            'predicted_home_goals': pred_h_goals,
            'predicted_away_goals': pred_a_goals,
            'predicted_total_goals': pred_total_goals,
            'top_3_scorelines': biv.get('top_3_scores', []),
            'total_over_5_5': biv.get('total_over_5_5'),
            'total_under_5_5': (None if biv.get('total_over_5_5') is None else float(1.0 - biv.get('total_over_5_5'))),
            'total_over_6_5': biv.get('total_over_6_5'),
            'total_under_6_5': (None if biv.get('total_over_6_5') is None else float(1.0 - biv.get('total_over_6_5'))),
            'puckline_home_minus_1_5': biv.get('puckline_home_minus_1_5'),
            'puckline_away_minus_1_5': biv.get('puckline_away_minus_1_5'),
        }
    
    def _calculate_legacy_injury_impact(self, away_injuries: list, home_injuries: list) -> float:
        if not away_injuries and not home_injuries:
            return 0.0
        away_impact = self._team_injury_impact(away_injuries or [])
        home_impact = self._team_injury_impact(home_injuries or [])
        return home_impact - away_impact
    
    def _team_injury_impact(self, injuries: list) -> float:
        impact = 0.0
        for injury in injuries:
            if isinstance(injury, dict):
                position = injury.get('position', '')
                if position == 'G': impact += 0.10
                elif 'C' in position or 'W' in position: impact += 0.03
                elif 'D' in position: impact += 0.02
        return min(0.15, impact)
    
    def _calculate_agreement(self, predictions: list, away_team: str = None, home_team: str = None) -> float:
        if len(predictions) < 2:
            return 1.0
        winners = []
        for p in predictions:
            if p['away_prob'] > p['home_prob']:
                winners.append(away_team or p.get('away_team', 'away'))
            else:
                winners.append(home_team or p.get('home_team', 'home'))
        most_common = max(set(winners), key=winners.count)
        return winners.count(most_common) / len(winners)

    def _is_elimination_game(self, status: str) -> bool:
        """Parse series status to see if any team has 3 wins (e.g. 'FLA leads 3-2')."""
        if not status: return False
        try:
            import re
            nums = re.findall(r'\d', status)
            if any(n == '3' for n in nums):
                return True
        except: pass
        return False
    
    def should_predict(self, prediction: Dict, confidence_threshold: float = 0.50) -> bool:
        return prediction['prediction_confidence'] >= confidence_threshold

if __name__ == "__main__":
    from rotowire_scraper import RotoWireScraper
    meta = MetaEnsemblePredictor()
    scraper = RotoWireScraper()
    print("🎯 Meta-Ensemble Predictor Test (with XGBoost)")
    print("=" * 60)
    data = scraper.scrape_daily_data()
    if data['games']:
        game = data['games'][0]
        print(f"\n🏒 {game['away_team']} @ {game['home_team']}")
        pred = meta.predict(
            game['away_team'],
            game['home_team'],
            away_lineup=game.get('away_lineup'),
            home_lineup=game.get('home_lineup'),
            away_goalie=game.get('away_goalie'),
            home_goalie=game.get('home_goalie')
        )
        print(f"\n📊 Meta-Ensemble Prediction:")
        print(f"  {pred['predicted_winner']} wins")
        print(f"  Probabilities: {game['away_team']} {pred['away_prob']:.1f}% / {game['home_team']} {pred['home_prob']:.1f}%")
        print(f"  Confidence: {pred['prediction_confidence']:.1%}")
