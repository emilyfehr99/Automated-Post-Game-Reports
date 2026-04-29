#!/usr/bin/env python3
"""
Meta Ensemble Predictor
Combines all prediction methods for maximum accuracy
"""
from typing import Dict, Optional
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
    def __init__(self, k_factor=20, home_advantage=35):
        self.ratings = {}  # {team: rating}
        self.k = k_factor
        self.ha = home_advantage
        self.base_rating = 1500

    def get_rating(self, team):
        return self.ratings.get(team, self.base_rating)

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
        self.team_profiles = {}
        self.travel_archetypes = {}
        self.edge_profiles = {}
        self.team_encodings = {}
        self.rotowire = RotoWireScraper()
        self.standings = StandingsTracker()
        self._component_weights = None
        self._load_component_weights()
        
        try:
            self._load_xgboost_components()
        except Exception as e:
            print(f"⚠️ Failed to load XGBoost components: {e}")

    def _load_component_weights(self) -> None:
        """Load dynamic component weights from recent backtests if available."""
        # Defaults (roughly match existing behavior)
        self._component_weights = {
            "xgb": 0.50,
            "elo": 0.10,
            "specialized": 0.25,
            "player": 0.15,
            "base": 0.10,
            "vegas": 0.15,
        }
        self._model_mode = "ensemble"
        self._shrink_alpha = 1.0
        try:
            p = Path("model_performance.json")
            if not p.exists():
                print("ℹ️  No model_performance.json found; using default ensemble weights")
                return
            with open(p, "r") as f:
                perf = json.load(f)
            # Prefer recent-window metrics when present; fall back to mean-over-splits.
            x_ll = perf.get("xgb_recent_logloss") or perf.get("xgb_cal_mean_logloss")
            e_ll = perf.get("elo_recent_logloss") or perf.get("elo_mean_logloss")
            if x_ll is None or e_ll is None:
                print("ℹ️  model_performance.json missing logloss fields; using default ensemble weights")
                return

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

    def _load_xgboost_components(self):
        """Load model, features list, and build history state"""
        # Prefer the current champion (full vs recent) when available.
        try:
            p = Path("model_performance.json")
            if p.exists():
                with open(p, "r") as f:
                    perf = json.load(f)
                champ = perf.get("champion")
        except Exception:
            champ = None

        suffix = f"_{champ}" if champ else ""

        # 1. Load Calibrated Model (Preferred)
        # This is algo-agnostic because it's a pickled CalibratedClassifierCV
        cal_model_path = Path(f"xgb_calibrated_model{suffix}.pkl")
        legacy_cal_model_path = Path("xgb_calibrated_model.pkl")
        
        loaded_cal = False
        if cal_model_path.exists():
            try:
                with open(cal_model_path, "rb") as f:
                    self.calibrated_model = pickle.load(f)
                print(f"✅ Loaded Calibrated champion model from {cal_model_path}")
                loaded_cal = True
            except Exception as e:
                print(f"⚠️ Failed to load calibrated model: {e}")
        
        if not loaded_cal and legacy_cal_model_path.exists():
            try:
                with open(legacy_cal_model_path, "rb") as f:
                    self.calibrated_model = pickle.load(f)
                print(f"✅ Loaded Calibrated model from {legacy_cal_model_path}")
                loaded_cal = True
            except Exception as e:
                print(f"⚠️ Failed to load calibrated model: {e}")

        # 1b. Load Standard Model (Fallback/Legacy)
        # Note: Legacy fallback is still hardcoded for XGB for now, 
        # but production mostly relies on calibrated_model above.
        model_path = Path(f"xgb_nhl_model{suffix}.json")
        legacy_model_path = Path("xgb_nhl_model.json")
        if not loaded_cal:
            if model_path.exists():
                self.xgb_model = xgb.XGBClassifier()
                self.xgb_model.load_model(str(model_path))
                print(f"✅ Loaded XGBoost fallback from {model_path}")
            elif legacy_model_path.exists():
                self.xgb_model = xgb.XGBClassifier()
                self.xgb_model.load_model(str(legacy_model_path))
                print(f"✅ Loaded XGBoost fallback from {legacy_model_path}")
            
        # 2. Load Feature Names
        feat_path = Path(f"xgb_features{suffix}.pkl")
        legacy_feat_path = Path("xgb_features.pkl")
        if feat_path.exists():
            with open(feat_path, "rb") as f:
                self.feature_names = pickle.load(f)
            print(f"✅ Loaded {len(self.feature_names)} feature definitions")
        elif legacy_feat_path.exists():
            with open(legacy_feat_path, "rb") as f:
                self.feature_names = pickle.load(f)
            print(f"✅ Loaded {len(self.feature_names)} feature definitions")
        else:
            print("⚠️ feature definitions not found, XGBoost disabled")
            self.xgb_model = None
            return

        # Feature snapshot (strict anti-leakage / drift validation)
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
            self._scoreline_calibration = None

        # Probability calibration (post-hoc isotonic points)
        try:
            p = Path("xgb_prob_calibration.json")
            if p.exists():
                with open(p, "r") as f:
                    self._prob_calibration = json.load(f)
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
                        'edge_burst_avg': np.mean(top_bursts) if top_bursts else 0.5
                    }
                print(f"✅ Loaded {len(self.edge_profiles)} team Edge profiles")
        except Exception as e:
            print(f"⚠️ Could not load NHL Edge profiles: {e}")

        # 6. Load Team win rate encodings (Phase 8.1)
        try:
            enc_path = Path(f"team_encodings{suffix}.json")
            legacy_enc_path = Path("team_encodings.json")
            if enc_path.exists():
                with open(enc_path, "r") as f:
                    self.team_encodings = json.load(f)
                print(f"✅ Loaded Phase 8.1 Team Encodings")
            elif legacy_enc_path.exists():
                with open(legacy_enc_path, "r") as f:
                    self.team_encodings = json.load(f)
                print(f"✅ Loaded Phase 8.1 Team Encodings")
        except Exception as e:
            print(f"⚠️ Could not load team encodings: {e}")

        # 4. Build Team History State
        data_path = Path('data/win_probability_predictions_v2.json')
        if not data_path.exists():
            data_path = Path('win_probability_predictions_v2.json')
            
        if data_path.exists():
            print("⏳ Rebuilding team history state...")
            with open(data_path, 'r') as f:
                data = json.load(f)
            
            raw_preds = data.get('predictions', [])
            # Sort chronologically to replay history correctly
            sorted_preds = sorted(raw_preds, key=lambda x: x.get('date', '1900-01-01'))
            
            count = 0
            for p in sorted_preds:
                date_str = p.get('date')
                if not date_str:
                    continue
                try:
                    game_date = datetime.strptime(date_str, "%Y-%m-%d")
                except:
                    continue
                    
                metrics = p.get('metrics_used', {})
                home = p.get('home_team')
                away = p.get('away_team')
                
                # Extract stats (logic matches train_xgboost_model.py)
                h_goals = float(metrics.get('home_goals', 0) or p.get('actual_home_score', 0) or 0)
                a_goals = float(metrics.get('away_goals', 0) or p.get('actual_away_score', 0) or 0)
                h_xg = float(metrics.get('home_xg', h_goals) or h_goals)
                a_xg = float(metrics.get('away_xg', a_goals) or a_goals)
                
                # Goalie Update
                h_goalie = metrics.get('home_goalie') or p.get('home_goalie')
                a_goalie = metrics.get('away_goalie') or p.get('away_goalie')
                h_hdsv = float(metrics.get('home_hdsv_pct', 0.8) or metrics.get('home_hd_sv_pct', 0.8) or 0.8)
                a_hdsv = float(metrics.get('away_hdsv_pct', 0.8) or metrics.get('away_hd_sv_pct', 0.8) or 0.8)
                h_shots = float(metrics.get('home_shots', 30) or 30)
                a_shots = float(metrics.get('away_shots', 30) or 30)
                
                if h_goalie: self.history_tracker.update_goalie(h_goalie, h_xg - h_goals, h_hdsv, h_shots)
                if a_goalie: self.history_tracker.update_goalie(a_goalie, a_xg - a_goals, a_hdsv, a_shots)
                
                # Real PDO
                h_pdo = ((h_goals / h_shots if h_shots > 0 else 0.1) + ((a_shots - a_goals) / a_shots if a_shots > 0 else 0.9)) * 100
                a_pdo = ((a_goals / a_shots if a_shots > 0 else 0.1) + ((h_shots - h_goals) / h_shots if h_shots > 0 else 0.9)) * 100

                h_corsi = float(metrics.get('home_corsi_pct', 50) or 50)
                a_corsi = float(metrics.get('away_corsi_pct', 50) or 50)
                h_pp = float(metrics.get('home_power_play_pct', 0) or 0)
                a_pp = float(metrics.get('away_power_play_pct', 0) or 0)
                
                # PK Symmetery
                h_pk = 100 - a_pp
                a_pk = 100 - h_pp
                
                h_stats = {
                    'goal_diff': h_goals - a_goals, 
                    'xg_diff': h_xg - a_xg, 
                    'corsi_pct': h_corsi, 
                    'pdo': h_pdo, 
                    'pp_pct': h_pp,
                    'pk_pct': h_pk,
                    'lateral': float(metrics.get('home_lateral', 5.0) or 5.0),
                    # Phase 15
                    'p1_xg': float(metrics.get('p1_xg_home', 0.8) or 0.8),
                    'p2_xg': float(metrics.get('p2_xg_home', 0.8) or 0.8),
                    'p3_xg': float(metrics.get('p3_xg_home', 0.8) or 0.8),
                    'led_after_p1': 1 if metrics.get('lead_after_p1') == 1 else 0,
                    'led_after_p2': 1 if metrics.get('lead_after_p2') == 1 else 0,
                    'trailed_after_p2': 1 if metrics.get('lead_after_p2') == -1 else 0,
                    'won_game': 1 if h_goals > a_goals else 0
                }
                a_stats = {
                    'goal_diff': a_goals - h_goals, 
                    'xg_diff': a_xg - h_xg, 
                    'corsi_pct': a_corsi, 
                    'pdo': a_pdo, 
                    'pp_pct': a_pp,
                    'pk_pct': a_pk,
                    'rush': float(metrics.get('away_rush', 2) or 2),
                    'nzt': float(metrics.get('away_nzt', 5) or 5),
                    'ozs': float(metrics.get('away_ozs', 10) or 10),
                    'hdc': float(metrics.get('away_hdc', 5) or 5),
                    'pizzas': float(metrics.get('away_hd_giveaways', 2) or 2),
                    # Phase 13
                    'royal_road': float(metrics.get('away_royal_road', 1) or 1),
                    'pressure': float(metrics.get('away_pressure', 2) or 2),
                    'rebounds': float(metrics.get('away_rebounds', 1) or 1),
                    'lateral': float(metrics.get('away_lateral', 5.0) or 5.0),
                    # Phase 15
                    'p1_xg': float(metrics.get('p1_xg_away', 0.8) or 0.8),
                    'p2_xg': float(metrics.get('p2_xg_away', 0.8) or 0.8),
                    'p3_xg': float(metrics.get('p3_xg_away', 0.8) or 0.8),
                    'led_after_p1': 1 if metrics.get('lead_after_p1') == -1 else 0,
                    'led_after_p2': 1 if metrics.get('lead_after_p2') == -1 else 0,
                    'trailed_after_p2': 1 if metrics.get('lead_after_p1') == 1 else 0,
                    'won_game': 1 if a_goals > h_goals else 0
                }
                
                curr_h_elo = self.history_tracker.get_elo(home)
                curr_a_elo = self.history_tracker.get_elo(away)
                
                self.history_tracker.elo.update(home, away, h_goals, a_goals)
                self.history_tracker.update(home, game_date, h_stats, venue='home', opponent_elo=curr_a_elo, city=home)
                self.history_tracker.update(away, game_date, a_stats, venue='away', opponent_elo=curr_h_elo, city=home)
                count += 1
            print(f"✅ Replayed {count} games to build current state")

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
        
        # Build Feature Vector (Optimized for 59.0% Accuracy Set)
        feature_data = {
            'elo_diff': (home_elo + tracker.elo.ha) - away_elo,
            
            # Contextual Features
            'rest_diff': home_rest - away_rest,
            'home_b2b': 1 if home_rest == 1 else 0,
            'away_b2b': 1 if away_rest == 1 else 0,
            
            # Goalie Difference
            'gsax_diff': h_gsax_roll - a_gsax_roll,
            'finish_diff': h_finish - a_finish,
            
            # NHL Edge Micro-Movement (Phase 6)
            'edge_speed_diff': self.edge_profiles.get(home_team, {}).get('edge_top_speed', 21.0) - self.edge_profiles.get(away_team, {}).get('edge_top_speed', 21.0),
            'edge_burst_diff': self.edge_profiles.get(home_team, {}).get('edge_burst_avg', 0.5) - self.edge_profiles.get(away_team, {}).get('edge_burst_avg', 0.5),
            
            # Rolling General (EWMA)
            'l5_goal_diff': h_l5.get('goal_diff', 0) - a_l5.get('goal_diff', 0),
            'l5_xg_diff': h_l5.get('xg_diff', 0) - a_l5.get('xg_diff', 0),
            'l5_corsi_diff': h_l5.get('corsi_pct', 50) - a_l5.get('corsi_pct', 50),
            'l5_pdo_diff': h_l5.get('pdo', 100) - a_l5.get('pdo', 100),
            
            # Special Teams (Matchup-Adjusted Phase 3)
            'l5_pp_diff': h_l5.get('pp_pct', 20) - a_l5.get('pp_pct', 20),
            'l5_pk_diff': h_l5.get('pk_pct', 80) - a_l5.get('pk_pct', 80),
            'l5_st_net': (h_l5.get('pp_pct', 20) + h_l5.get('pk_pct', 80)) - (a_l5.get('pp_pct', 20) + a_l5.get('pk_pct', 80)),
            'h_pp_edge': h_l5.get('pp_pct', 20) - a_l5.get('pk_pct', 80), # Home PP vs Away PK
            'a_pp_edge': a_l5.get('pp_pct', 20) - h_l5.get('pk_pct', 80), # Away PP vs Home PK
            'h_discipline_target': a_l5.get('pim', 8.0), # How many PIMs does opponent take?
            'a_discipline_target': h_l5.get('pim', 8.0),
            
            # Phase 3 Fatigue Density
            'h_3_in_4': 1 if tracker.get_game_count_in_window(home_team, datetime.now(), 4) >= 3 else 0,
            'a_3_in_4': 1 if tracker.get_game_count_in_window(away_team, datetime.now(), 4) >= 3 else 0,
            
            # Technical Metrics
            'l5_rush_diff': h_l5.get('rush', 2) - a_l5.get('rush', 2),
            'l5_nzt_diff': h_l5.get('nzt', 5) - a_l5.get('nzt', 5),
            'l5_ozs_diff': h_l5.get('ozs', 10) - a_l5.get('ozs', 10),
            'l5_hdc_diff': h_l5.get('hdc', 5) - a_l5.get('hdc', 5),
            'l5_pizza_diff': h_l5.get('pizzas', 2) - a_l5.get('pizzas', 2),
            
            # Phase 13: Tactical Signals
            'l5_royal_road_diff': h_l5.get('royal_road', 1) - a_l5.get('royal_road', 1),
            'l5_pressure_diff': h_l5.get('pressure', 2) - a_l5.get('pressure', 2),
            'l5_rebound_diff': h_l5.get('rebounds', 1) - a_l5.get('rebounds', 1),
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
            'l5_nzt_possession_diff': h_l5.get('nzt_possession', 50) - a_l5.get('nzt_possession', 50),
            'l5_ca_shots_diff': h_l5.get('ca_shots', 0) - a_l5.get('ca_shots', 0),
            'l5_rush_sv_pct_diff': h_l5.get('rush_sv_pct', 90) - a_l5.get('rush_sv_pct', 90),
            
            # Venue Indicators
            'home_venue_goal_diff': h_home_l5.get('goal_diff', 0),
            # Phase 14: Season-Phase Context
            'season_month': datetime.now().month,
            'is_late_season': 1 if datetime.now().month in [3, 4] else 0,
            'h_desperation': self.standings.calculate_desperation_index(home_team),
            'a_desperation': self.standings.calculate_desperation_index(away_team),
            
            # Phase 4: Travel Jet Lag (TZ Delta)
            'tz_delta': TEAM_TIMEZONES.get(away_team, -5) - TEAM_TIMEZONES.get(home_team, -5),
            
            # Venue Specific
            
            # Strength of Schedule (SoS)
            'home_sos': tracker.get_sos(home_team, 5),
            'away_sos': tracker.get_sos(away_team, 5),
            
            # Stability
            'l5_std_diff': tracker.get_rolling_std(home_team, 5) - tracker.get_rolling_std(away_team, 5),
            
            'l10_goal_diff': h_l10.get('goal_diff', 0) - a_l10.get('goal_diff', 0),
            'l10_xg_diff': h_l10.get('xg_diff', 0) - a_l10.get('xg_diff', 0),
            
            # Interaction Features (Phase 8 Advanced DS)
            'elo_rest_inter': ((home_elo + self.history_tracker.elo.ha) - away_elo) * (home_rest - away_rest),
            'speed_finish_inter': (self.edge_profiles.get(home_team, {}).get('edge_top_speed', 21.0) - self.edge_profiles.get(away_team, {}).get('edge_top_speed', 21.0)) * (h_finish - a_finish),
            
            # Phase 14: Season-Phase Context
            'season_month': datetime.now().month,
            'is_late_season': 1 if datetime.now().month in [3, 4] else 0,
            'h_desperation': self.standings.calculate_desperation_index(home_team),
            'a_desperation': self.standings.calculate_desperation_index(away_team),
            
            # Raw Components for Phase 11/12 Symbolic Features
            # Phase 48: Apply momentum_scalar to reduce xG-heavy bias during playoffs
            'l5_xg_diff': (h_l5.get('xg_diff', 0) - a_l5.get('xg_diff', 0)) * momentum_scalar,
            'l10_xg_diff': (h_l10.get('xg_diff', 0) - a_l10.get('xg_diff', 0)) * momentum_scalar,
            'home_xg': h_l5.get('xg_avg', 2.5) * momentum_scalar,
            'away_xg': a_l5.get('xg_avg', 2.5) * momentum_scalar,
            'home_elo': home_elo + tracker.elo.ha,
            'away_elo': away_elo,
            'home_win_rate': self.team_encodings.get('home_map', {}).get(home_team, self.team_encodings.get('home_prior', 0.5)),
            'away_win_rate': self.team_encodings.get('away_map', {}).get(away_team, self.team_encodings.get('away_prior', 0.5)),

            # Phase 9: Automated Interaction Discovery
            'home_win_rate_away_sos': self.team_encodings.get('home_map', {}).get(home_team, 0.5) * self.history_tracker.get_sos(away_team, 5),
            'away_b2b_home_strength': (1 if away_rest == 1 else 0) * h_finish,
            'l10_xg_st_inter': (h_l10.get('xg_diff', 0) - a_l10.get('xg_diff', 0)) * ((h_l5.get('pp_pct', 20) + h_l5.get('pk_pct', 80)) - (a_l5.get('pp_pct', 20) + a_l5.get('pk_pct', 80))),
            
            # Phase 11: Symbolic Feature Discovery
            'pressure_index': (h_l5.get('xg_avg', 2.5) / (a_l5.get('xg_avg', 2.5) + 0.1)) * ((home_elo + self.history_tracker.elo.ha) / (away_elo + 0.1)),
            'xg_efficiency': (h_l5.get('xg_avg', 2.5) * (self.history_tracker.get_sos(home_team, 5) / 1500)) - (a_l5.get('xg_avg', 2.5) * (self.history_tracker.get_sos(away_team, 5) / 1500)),
            'power_momentum': ((home_elo + self.history_tracker.elo.ha) - away_elo) * (h_l10.get('xg_diff', 0) - a_l10.get('xg_diff', 0))
        }
        
        # --- Helper for dynamic feature alignment ---
        def _get_aligned_df(model):
            if model is None: return None
            
            # Get feature names from model if possible
            feats_to_use = self.feature_names
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

        # Ensure ordered columns match training for MAIN model
        try:
            # Strict anti-leakage / drift guard: feature list must match training snapshot exactly.
            if isinstance(self._feature_snapshot, dict) and self._feature_snapshot.get("sha256"):
                joined = "\n".join([str(x) for x in self.feature_names]).encode("utf-8")
                cur = hashlib.sha256(joined).hexdigest()
                exp = str(self._feature_snapshot.get("sha256"))
                if cur != exp:
                    raise RuntimeError(
                        f"Feature snapshot mismatch (runtime={cur} expected={exp}). "
                        "Refusing XGB prediction due to potential leakage/drift."
                    )
                
            # 4. Make Prediction
            df_main = _get_aligned_df(self.calibrated_model or self.xgb_model)
            
            # Prefer calibrated model for better probability accuracy
            if self.calibrated_model is not None:
                prob = self.calibrated_model.predict_proba(df_main)[0][1] # Probability of home win
            elif self.xgb_model is not None:
                prob = self.xgb_model.predict_proba(df_main)[0][1] # Probability of home win
            else:
                return None

            # Apply post-hoc calibration mapping if available.
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
            
            away_prob = (1 - prob) * 100
            home_prob = prob * 100
            
            # 5. Goal Margin Prediction (Phase 12)
            # Use dynamic alignment to handle potentially different features in margin model
            predicted_margin = 0.0
            if self.margin_model is not None:
                try:
                    df_margin = _get_aligned_df(self.margin_model)
                    predicted_margin = float(self.margin_model.predict(df_margin)[0])
                except Exception as e:
                    print(f"Margin prediction error: {e}")

            # 5b. Scoreline: prefer direct home/away goals models when available.
            predicted_total = None
            predicted_home_goals = None
            predicted_away_goals = None
            try:
                if self.home_goals_model is not None and self.away_goals_model is not None:
                    df_h = _get_aligned_df(self.home_goals_model)
                    df_a = _get_aligned_df(self.away_goals_model)
                    
                    h = float(self.home_goals_model.predict(df_h)[0])
                    a = float(self.away_goals_model.predict(df_a)[0])
                    # Clamp predicted means
                    h = float(max(0.05, min(12.0, h)))
                    a = float(max(0.05, min(12.0, a)))

                    # If we have NB dispersion calibration, use NB mode (more realistic variance than rounding means).
                    nb_size = None
                    try:
                        if isinstance(self._scoreline_calibration, dict):
                            nb_size = self._scoreline_calibration.get("total_goals_nb_size")
                        nb_size = float(nb_size) if nb_size is not None else None
                    except Exception:
                        nb_size = None

                    def _nb_mode(mu: float, size: Optional[float]) -> int:
                        if size is None or size <= 1.0:
                            return int(round(mu))
                        r = float(size)
                        p = r / (r + float(mu))
                        # mode = floor((r-1)*(1-p)/p) for r>1
                        m = int(math.floor(((r - 1.0) * (1.0 - p)) / max(1e-9, p)))
                        return int(m)

                    predicted_home_goals = int(max(0, min(12, _nb_mode(h, nb_size))))
                    predicted_away_goals = int(max(0, min(12, _nb_mode(a, nb_size))))
                    predicted_total = float(predicted_home_goals + predicted_away_goals)
            except Exception as e:
                print(f"Home/away goals prediction error: {e}")
                predicted_home_goals = None
                predicted_away_goals = None
                predicted_total = None

            # Fallback: total-goals model + margin split
            if predicted_total is None:
                try:
                    if self.total_goals_model is not None:
                        df_tg = _get_aligned_df(self.total_goals_model)
                        predicted_total = float(self.total_goals_model.predict(df_tg)[0])
                except Exception as e:
                    print(f"Total goals prediction error: {e}")
                    predicted_total = None

                if predicted_total is not None:
                    predicted_total = float(max(2.0, min(12.0, predicted_total)))
                    h = (predicted_total + float(predicted_margin)) / 2.0
                    a = (predicted_total - float(predicted_margin)) / 2.0
                    h = float(max(0.0, h))
                    a = float(max(0.0, a))
                    predicted_home_goals = int(round(h))
                    predicted_away_goals = int(round(a))

            # Ensure no ties in displayed final: break ties toward predicted winner.
            if predicted_home_goals is not None and predicted_away_goals is not None:
                if predicted_home_goals == predicted_away_goals:
                    if home_prob >= away_prob:
                        predicted_home_goals += 1
                    else:
                        predicted_away_goals += 1
                predicted_total = float(predicted_home_goals + predicted_away_goals)

            # Attach dispersion hint for downstream consumers (optional).
            nb_size = None
            try:
                if isinstance(self._scoreline_calibration, dict):
                    nb_size = self._scoreline_calibration.get("total_goals_nb_size")
            except Exception:
                nb_size = None

            # Totals distribution (NB) -> implied O/U probabilities for decision support
            total_over_5_5 = None
            total_over_6_5 = None
            try:
                if predicted_total is not None and nb_size is not None:
                    mu_total = float(max(0.1, min(20.0, float(predicted_total))))
                    sz = float(nb_size)
                    from scipy.stats import nbinom
                    # P(X > k) = 1 - P(X <= k)
                    # p = r / (r + mu)
                    p_nb = sz / (sz + mu_total)
                    total_over_5_5 = float(1.0 - nbinom.cdf(5, sz, p_nb))
                    total_over_6_5 = float(1.0 - nbinom.cdf(6, sz, p_nb))
            except Exception:
                pass
            
            # 6. Meta-Confidence Estimation
            confidence_tier = "Standard"
            if self.confidence_model is not None:
                try:
                    df_conf = _get_aligned_df(self.confidence_model)
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
                    df_p1 = _get_aligned_df(self.p1_model)
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

            # Phase 48: Playoff Weight Decay
            # Reduce momentum bias (xg_10d/20d) by 20% if in playoff mode
            momentum_scalar = 0.8 if is_playoff else 1.0

            return {
                'away_team': away_team,
                'home_team': home_team,
                'away_prob': away_prob,
                'home_prob': home_prob,
                'predicted_margin': predicted_margin,
                'predicted_total_goals': predicted_total,
                'predicted_home_goals': predicted_home_goals,
                'predicted_away_goals': predicted_away_goals,
                'scoreline_nb_size': nb_size,
                'total_over_5_5': total_over_5_5,
                'total_under_5_5': (None if total_over_5_5 is None else float(1.0 - total_over_5_5)),
                'total_over_6_5': total_over_6_5,
                'total_under_6_5': (None if total_over_6_5 is None else float(1.0 - total_over_6_5)),
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
                'home_travel_miles': home_travel,
                'prediction_type': 'xgboost_ml'
            }
        except Exception as e:
            print(f"XGBoost prediction error: {e}")
            return None
    
    def get_injury_impact(self, team: str) -> float:
        """Calculate injury impact multiplier (0.90 - 1.0) using RotoWire data"""
        try:
            # Scrape latest data
            data = self.rotowire.scrape_daily_data()
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
        except Exception as e:
            print(f"Error calculating injury impact for {team}: {e}")
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
        
        # Weighted ensemble calculation
        total_weight = sum(weights)
        ensemble_away = sum(p['away_prob'] * w for p, w in zip(predictions, weights)) / total_weight
        ensemble_home = sum(p['home_prob'] * w for p, w in zip(predictions, weights)) / total_weight

        # --- Final shrink toward Elo champion (stability + accuracy) ---
        # If recent evaluation shows Elo outperforming XGB, we shrink the final
        # probabilities toward Elo to reduce overconfident misses.
        try:
            alpha = float(getattr(self, "_shrink_alpha", 1.0))
            if alpha < 0.999:
                elo_home = float(self.history_tracker.elo.get_win_prob(home_team, away_team)) * 100.0
                elo_away = 100.0 - elo_home
                ensemble_home = alpha * ensemble_home + (1.0 - alpha) * elo_home
                ensemble_away = alpha * ensemble_away + (1.0 - alpha) * elo_away
        except Exception:
            pass
        
        # Apply Contextual Factors (Phase 4 Blending)
        # 1. Injury Impact
        h_health = self.get_injury_impact(home_team) if not home_injuries else (1.0 - self._team_injury_impact(home_injuries))
        a_health = self.get_injury_impact(away_team) if not away_injuries else (1.0 - self._team_injury_impact(away_injuries))
        
        # 2. Travel Impact
        h_travel = self.history_tracker.get_travel_distance(home_team, home_team)
        a_travel = self.history_tracker.get_travel_distance(away_team, home_team)
        
        # Phase 5: Road Warrior Mitigation
        h_is_rw = self.travel_archetypes.get(home_team, {}).get('is_road_warrior', False)
        a_is_rw = self.travel_archetypes.get(away_team, {}).get('is_road_warrior', False)
        
        # Every 1000 miles reduction takes ~0.5% (was 1%) from prob
        h_fatigue = max(0.95, 1.0 - (h_travel / 20000.0))
        a_fatigue = max(0.95, 1.0 - (a_travel / 20000.0))
        
        # If a team is a Road Warrior, they suffer 50% less fatigue penalty
        if h_is_rw and h_fatigue < 1.0:
            h_fatigue = 1.0 - ((1.0 - h_fatigue) * 0.5)
        if a_is_rw and a_fatigue < 1.0:
            a_fatigue = 1.0 - ((1.0 - a_fatigue) * 0.5)
        
        # Combined Impact Ratio
        impact_ratio = (h_health * h_fatigue) / (a_health * a_fatigue)
        ensemble_home *= impact_ratio
        
        # 3. HDSv% Signal (Phase 4)
        h_hdsv = self.history_tracker.goalies.get_rolling_hdsv(home_goalie)
        a_hdsv = self.history_tracker.goalies.get_rolling_hdsv(away_goalie)
        hdsv_bonus = (h_hdsv - a_hdsv) * 10.0 # 1 point diff = 1% prob shift
        ensemble_home += hdsv_bonus
        ensemble_away -= hdsv_bonus
        
        # 4. Market Edge Calculation (+EV Tracking - Phase 16)
        edge_away = 0.0
        edge_home = 0.0
        if vegas_odds:
            try:
                v_away = vegas_odds.get('away_ml')
                v_home = vegas_odds.get('home_ml')
                if v_away and v_home:
                    # Convert to implied probability
                    implied_away = 100 / (v_away + 100) if v_away > 0 else abs(v_away) / (abs(v_away) + 100)
                    implied_home = 100 / (v_home + 100) if v_home > 0 else abs(v_home) / (abs(v_home) + 100)
                    
                    # Calculate Edge: (Model Prob - Implied Prob) / Implied Prob * 100
                    edge_away = (ensemble_away / 100.0 - implied_away) / implied_away * 100 if implied_away > 0 else 0
                    edge_home = (ensemble_home / 100.0 - implied_home) / implied_home * 100 if implied_home > 0 else 0
            except: pass

        # 5. Final Aggregation
        confidence = max(ensemble_away, ensemble_home) / 100
        agreement_score = self._calculate_agreement(predictions, away_team, home_team)
        
        # Phase 10/12: Signal Alignment
        confidence_tier = xgb_pred.get('confidence_tier', 'Standard') if xgb_pred else "Standard"
        
        # If margin and win prob both agree on a blowout, bump confidence
        if xgb_margin > 1.5 and ensemble_home > 55:
            confidence_tier = "🔥 High Confidence"
        elif xgb_margin < -1.5 and ensemble_away > 55:
            confidence_tier = "🔥 High Confidence"
        
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

        return {
            'away_team': away_team,
            'home_team': home_team,
            'away_prob': ensemble_away,
            'home_prob': ensemble_home,
            'predicted_winner': away_team if ensemble_away > ensemble_home else home_team,
            'prediction_confidence': max(ensemble_away, ensemble_home) / 100.0,
            'confidence_tier': xgb_pred.get('confidence_tier', 'Standard') if xgb_pred else 'Standard',
            'predicted_margin': xgb_margin,
            'edge_away': edge_away,
            'edge_home': edge_home,
            'is_plus_ev_away': edge_away > 5.0,
            'is_plus_ev_home': edge_home > 5.0,
            'suggested_units': suggested_units,
            'p1_home_prob': xgb_p1_prob,
            'contexts_used': xgb_pred.get('contexts_used', []) if xgb_pred else []
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
