#!/usr/bin/env python3
"""
Improved Self-Learning Win Probability Model V2
Implements comprehensive improvements for better prediction accuracy
"""

import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from correlation_model import CorrelationModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_WEIGHT_PRIORS = {
    "xg_weight": 0.40,
    "hdc_weight": 0.20,
    "corsi_weight": 0.10,
    "power_play_weight": 0.08,
    "faceoff_weight": 0.06,
    "shots_weight": 0.05,
    "hits_weight": 0.03,
    "blocked_shots_weight": 0.03,
    "takeaways_weight": 0.02,
    "penalty_minutes_weight": 0.01,
    "recent_form_weight": 0.02,
    "head_to_head_weight": 0.00,
    "rest_days_weight": 0.00,
    "goalie_performance_weight": 0.00,
    "game_score_weight": 0.15,
    "sos_weight": 0.00,
}

class ImprovedSelfLearningModelV2:
    def __init__(self, predictions_file: str = "win_probability_predictions_v2.json"):
        """Initialize the improved self-learning model V2"""
        self.predictions_file = Path(predictions_file)
        self.model_data = self.load_model_data()
        # Feature flags for experiments/backtests
        self.feature_flags = {
            'use_per_goalie_gsax': False,
            'use_rest_bucket_adj': False,
        }
        # Deterministic mode (disables random noise during evaluation)
        self.deterministic = False
        # Build goalie start history (team -> [(date, goalie_name)])
        # Load persisted goalie history if present, else build from predictions
        
        # Improved learning parameters
        self.learning_rate = 0.03  # Slightly higher to adapt a bit faster
        self.momentum = 0.8  # Momentum for weight updates
        self.min_games_for_update = 3
        self.weight_clip_range = (0.03, 0.65)  # Allow more expressiveness per metric
        self.games_data = [] # List of tuples: (home_exp, away_exp, home_goals, away_goals)
        
        # Determine paths relative to script location
        self.script_dir = Path(__file__).parent.absolute()
        self.predictions_file = self.script_dir / "data" / "win_probability_predictions_v2.json"
        
        # Load existing model data
        self.model_data = self.load_model_data()
        
        # Build goalie start history (team -> [(date, goalie_name)])
        # Load persisted goalie history if present, else build from predictions
        self.goalie_history = self.model_data.get('goalie_history') or self._build_goalie_history()
        
        # Team performance tracking - use new season stats format
        self.team_stats_file = Path("data/season_2025_2026_team_stats.json")
        self.historical_stats_file = Path("historical_seasons_team_stats.json")
        
        # Load current season stats
        self.team_stats = self.load_team_stats()
        
        # Load historical stats if available
        self.historical_stats = self.load_historical_stats()
        
        # Correlation model for diagnostics and weight signals
        try:
            self.correlation_model = CorrelationModel()
        except Exception as exc:
            logger.warning(f"Failed to initialize correlation model: {exc}")
            self.correlation_model = None

        self.upset_model = self.model_data.get("upset_model")
        self.backtest_reports = self.model_data.get("backtest_reports", [])

    def predict_upset_probability(self, features: List[float]) -> float:
        """Predict upset probability using stored logistic regression coefficients."""
        model_params = self.model_data.get("upset_model")
        if not model_params:
            # fallback heuristic
            coeffs = [0.5, -0.4, 0.2, 0.8]
            intercept = -1.0
        else:
            coeffs = model_params.get("coef", [0.5, -0.4, 0.2, 0.8])
            intercept = model_params.get("intercept", -1.0)
        coeffs = list(coeffs) + [0.0] * (len(features) - len(coeffs))
        z = intercept
        for w, x in zip(coeffs, features):
            z += float(w) * float(x)
        try:
            return 1.0 / (1.0 + np.exp(-z))
        except OverflowError:
            return 0.0 if z < 0 else 1.0
        
    @staticmethod
    def _normalize_outcome_side(value: Optional[str], away_team: Optional[str], home_team: Optional[str]) -> Optional[str]:
        """Normalize a winner string to 'away' or 'home'."""
        if not value:
            return None
        if not isinstance(value, str):
            return None
        normalized = value.strip().lower()
        if normalized in ("away", "home"):
            return normalized
        if away_team and normalized == away_team.lower():
            return "away"
        if home_team and normalized == home_team.lower():
            return "home"
        return None
    
    @staticmethod
    def _side_to_team(side: Optional[str], away_team: Optional[str], home_team: Optional[str]) -> Optional[str]:
        """Return the team abbreviation for a normalized side value."""
        if side == "away":
            return away_team
        if side == "home":
            return home_team
        return None

    @staticmethod
    def _is_number(value) -> bool:
        if isinstance(value, (int, float)):
            return True
        try:
            float(value)
            return True
        except (TypeError, ValueError):
            return False

    @staticmethod
    def _determine_context_bucket(away_rest: float, home_rest: float) -> str:
        """Determine schedule context bucket based on rest advantage."""
        if away_rest <= -0.5 and home_rest >= 0.5:
            return "away_b2b_vs_rest"
        if home_rest <= -0.5 and away_rest >= 0.5:
            return "home_b2b_vs_rest"
        if away_rest <= -0.5 and home_rest <= -0.5:
            return "both_b2b"
        if away_rest >= 0.5 and home_rest >= 0.5:
            return "both_rest_adv"
        if away_rest <= -0.5:
            return "away_b2b"
        if home_rest <= -0.5:
            return "home_b2b"
        if away_rest >= 0.5:
            return "away_rest_adv"
        if home_rest >= 0.5:
            return "home_rest_adv"
        return "neutral"

    def determine_context_bucket(self, away_rest: float, home_rest: float) -> str:
        return self._determine_context_bucket(away_rest, home_rest)

    @staticmethod
    def _compute_calibration_points(records: List[Tuple[float, float]], num_bins: int = 12) -> Tuple[List[Tuple[float, float]], int]:
        if not records:
            return [], 0
        records = sorted(records, key=lambda x: x[0])
        bins = [0.0 for _ in range(num_bins)]
        counts = [0 for _ in range(num_bins)]
        bin_bounds = np.linspace(0.0, 1.0, num_bins + 1)
        for prob, outcome in records:
            idx = min(num_bins - 1, max(0, int(np.searchsorted(bin_bounds, prob, side="right") - 1)))
            bins[idx] += outcome
            counts[idx] += 1
        calibrated = []
        running_prev = 0.0
        for i in range(num_bins):
            if counts[i] > 0:
                acc = bins[i] / counts[i]
            else:
                acc = running_prev
            acc = max(running_prev, acc)
            running_prev = acc
            midpoint = (bin_bounds[i] + bin_bounds[i + 1]) / 2.0
            calibrated.append((float(midpoint), float(acc)))
        return calibrated, len(records)

    @staticmethod
    def _apply_calibration_points(prob: float, points: List[Tuple[float, float]]) -> float:
        """Apply calibration with bounds to prevent extreme predictions"""
        if not points:
            return prob
        points = sorted(points, key=lambda x: x[0])
        if prob <= points[0][0]:
            calibrated = points[0][1]
        elif prob >= points[-1][0]:
            calibrated = points[-1][1]
        else:
            for i in range(1, len(points)):
                x0, y0 = points[i - 1]
                x1, y1 = points[i]
                if x0 <= prob <= x1:
                    if x1 == x0:
                        calibrated = y1
                    else:
                        t = (prob - x0) / (x1 - x0)
                        calibrated = y0 + t * (y1 - y0)
                    break
            else:
                calibrated = prob
        # Apply bounds: keep between 5% and 95% to prevent extreme predictions
        return max(0.05, min(0.95, calibrated))

    def _determine_upset(self, predicted_side: Optional[str], actual_side: Optional[str],
                          prediction_confidence: Optional[float], prediction_margin: Optional[float],
                          confidence_threshold: float = 0.6, margin_threshold: float = 0.1) -> bool:
        if not predicted_side or not actual_side:
            return False
        if predicted_side == actual_side:
            return False
        conf = prediction_confidence or 0.0
        margin = prediction_margin or 0.0
        return conf >= confidence_threshold or margin >= margin_threshold

    def predict_score_distribution(self, home_xg: float, away_xg: float) -> Tuple[int, int]:
        """Predict the likeliest exact score using Poisson distribution."""
        import math
        
        # Limit lambdas to reasonable hockey range to prevent performance issues
        lam_h = max(0.5, min(10.0, home_xg))
        lam_a = max(0.5, min(10.0, away_xg))
        
        def poisson_pmf(k, lam):
            return (lam**k * math.exp(-lam)) / math.factorial(k)
            
        max_prob = -1.0
        best_score = (3, 2) # Fallback
        
        # Check scores from 0-0 to 9-9
        for h in range(10):
            prob_h = poisson_pmf(h, lam_h)
            for a in range(10):
                prob_a = poisson_pmf(a, lam_a)
                joint_prob = prob_h * prob_a
                
                if joint_prob > max_prob:
                    max_prob = joint_prob
                    best_score = (h, a)
                    
        return best_score

    def _estimate_monte_carlo_signal(self, prediction: Dict, iterations: int = 40) -> float:
        """Estimate volatility by perturbing metrics and observing prediction flips."""
        if not self.correlation_model:
            return 0.0
        metrics = prediction.get("metrics_used") or {}
        if not metrics:
            return 0.0
        predicted_side = prediction.get("predicted_winner")
        if predicted_side not in ("away", "home"):
            away_prob = prediction.get("raw_away_prob", prediction.get("predicted_away_win_prob", 0.5))
            home_prob = prediction.get("raw_home_prob", prediction.get("predicted_home_win_prob", 0.5))
            predicted_side = "away" if away_prob >= home_prob else "home"
        if predicted_side not in ("away", "home"):
            return 0.0
        flips = 0
        samples = 0
        for _ in range(iterations):
            perturbed = {}
            for key, value in metrics.items():
                if self._is_number(value):
                    val = float(value)
                    scale = max(0.02, abs(val) * 0.1)
                    perturbed[key] = val + float(np.random.normal(0.0, scale))
                else:
                    perturbed[key] = value
            try:
                corr_probs = self.correlation_model.predict_from_metrics(perturbed)
            except Exception:
                continue
            sample_side = "away" if corr_probs.get("away_prob", 0.5) >= corr_probs.get("home_prob", 0.5) else "home"
            samples += 1
            if sample_side != predicted_side:
                flips += 1
        if samples == 0:
            return 0.0
        return flips / samples

    def update_calibration_model(self, min_games: int = 60, num_bins: int = 12) -> int:
        """Recompute calibration curve using completed games, segmented by context."""
        completed = [p for p in self.model_data.get("predictions", []) if p.get("actual_winner")]
        overall_records: List[Tuple[float, float]] = []
        bucket_records: Dict[str, List[Tuple[float, float]]] = {}
        for pred in completed:
            away_prob = pred.get("raw_away_prob")
            if away_prob is None:
                away_prob = pred.get("predicted_away_win_prob")
            if away_prob is None:
                continue
            actual_side = self._normalize_outcome_side(
                pred.get("actual_winner"),
                pred.get("away_team"),
                pred.get("home_team"),
            )
            if actual_side not in ("away", "home"):
                continue
            try:
                prob_val = max(0.0, min(1.0, float(away_prob)))
            except (TypeError, ValueError):
                continue
            outcome = 1.0 if actual_side == "away" else 0.0
            overall_records.append((prob_val, outcome))
            context_bucket = pred.get("context_bucket") or "neutral"
            bucket_records.setdefault(context_bucket, []).append((prob_val, outcome))
        if len(overall_records) < min_games:
            return 0

        overall_points, total_samples = self._compute_calibration_points(overall_records, num_bins)
        bucket_points = {}
        bucket_sizes = {}
        min_bucket_samples = max(30, min_games // 2)
        for bucket, records in bucket_records.items():
            if len(records) < min_bucket_samples:
                continue
            points, size = self._compute_calibration_points(records, num_bins)
            if size >= min_bucket_samples:
                bucket_points[bucket] = points
                bucket_sizes[bucket] = size

        self.model_data["calibration_points"] = overall_points
        self.model_data["calibration_by_bucket"] = bucket_points
        self.model_data["calibration_metadata"] = {
            "updated_at": datetime.now().isoformat(),
            "sample_size": total_samples,
            "num_bins": num_bins,
            "bucket_samples": bucket_sizes,
        }
        return total_samples

    def apply_calibration(self, away_probability: Optional[float], context_bucket: Optional[str] = None) -> float:
        if away_probability is None:
            return 0.5
        try:
            prob = float(away_probability)
        except (TypeError, ValueError):
            prob = 0.5
        prob = max(0.0, min(1.0, prob))
        bucket_map = self.model_data.get("calibration_by_bucket") or {}
        if context_bucket:
            bucket_points = bucket_map.get(context_bucket)
            if bucket_points and len(bucket_points) >= 2:
                return self._apply_calibration_points(prob, bucket_points)
        points = self.model_data.get("calibration_points") or []
        if len(points) < 2:
            return prob
        return self._apply_calibration_points(prob, points)
        
    def load_model_data(self) -> Dict:
        """Load existing model data and predictions"""
        if self.predictions_file.exists():
            try:
                with open(self.predictions_file, 'r') as f:
                    data = json.load(f)
                    # Load team stats from main file if available
                    if "team_stats" in data:
                        self.team_stats = data["team_stats"]
                    data.setdefault("calibration_points", [])
                    data.setdefault("calibration_metadata", {})
                    data.setdefault("calibration_by_bucket", {})
                    data.setdefault("backtest_reports", [])
                    return data
            except Exception as e:
                logger.error(f"Error loading model data: {e}")
        
        # Initialize with improved balanced model
        return {
            "predictions": [],
            "model_weights": DEFAULT_WEIGHT_PRIORS.copy(),
            "weight_momentum": {
                "xg_weight": 0.0,
                "hdc_weight": 0.0,
                "corsi_weight": 0.0,
                "power_play_weight": 0.0,
                "faceoff_weight": 0.0,
                "shots_weight": 0.0,
                "hits_weight": 0.0,
                "blocked_shots_weight": 0.0,
                "takeaways_weight": 0.0,
                "penalty_minutes_weight": 0.0,
                "recent_form_weight": 0.0,
                "head_to_head_weight": 0.0,
                "rest_days_weight": 0.0,
                "goalie_performance_weight": 0.0,
                "game_score_weight": 0.0,
                "sos_weight": 0.0
            },
            "last_updated": datetime.now().isoformat(),
            "model_performance": {
                "total_games": 0,
                "correct_predictions": 0,
                "accuracy": 0.0,
                "recent_accuracy": 0.0
            },
            "calibration_points": [],
            "calibration_metadata": {},
            "calibration_by_bucket": {},
            "backtest_reports": [],
            "goalie_stats": {}
        }
    
    def load_team_stats(self) -> Dict:
        """Load current season team performance statistics"""
        # All 32 NHL teams (ARI moved to UTA in 2024)
        all_nhl_teams = [
            'ANA', 'BOS', 'BUF', 'CGY', 'CAR', 'CHI', 'COL',
            'CBJ', 'DAL', 'DET', 'EDM', 'FLA', 'LAK', 'MIN', 'MTL',
            'NSH', 'NJD', 'NYI', 'NYR', 'OTT', 'PHI', 'PIT', 'SJS',
            'SEA', 'STL', 'TBL', 'TOR', 'UTA', 'VAN', 'VGK', 'WSH', 'WPG'
        ]
        
        def create_venue_data():
            return {
                "games": [], "xg": [], "hdc": [], "shots": [], "goals": [], "gs": [],
                "opp_xg": [], "opp_goals": [],
                "last_goalie": None,
                "opponents": [],
                "corsi_pct": [], "power_play_pct": [], "penalty_kill_pct": [], "faceoff_pct": [],
                "hits": [], "blocked_shots": [], "giveaways": [], "takeaways": [], "penalty_minutes": [],
                # Advanced movement and zone metrics
                "lateral": [], "longitudinal": [],
                "nzt": [], "nztsa": [], "ozs": [], "nzs": [], "dzs": [],
                "fc": [], "rush": [],
                # Clutch indicators
                "clutch_score": [],
                # Goals and shots (for/against) - explicit tracking
                "goals_for": [], "goals_against": [],
                "shots_for": [], "shots_against": [],
                "xG_for": [], "xG_against": [],
                "hdc_for": [], "hdc_against": [],
                # Opponent metrics (for compatibility)
                "opp_xg": [], "opp_goals": []
            }
        
        stats = {}
        # Initialize all 32 teams with empty data
        for team in all_nhl_teams:
            stats[team] = {"home": create_venue_data(), "away": create_venue_data()}
        
        if self.team_stats_file.exists():
            try:
                with open(self.team_stats_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if 'teams' in data:
                            file_stats = data.get('teams', {})
                            # Merge file data into initialized stats
                            for team, venues in file_stats.items():
                                if team in stats:
                                    # Ensure all new fields exist (migrate old data structure)
                                    for venue in ['home', 'away']:
                                        if venue in venues:
                                            # Add all missing fields from create_venue_data
                                            new_fields = {
                                                'lateral': [], 'longitudinal': [],
                                                'nzt': [], 'nztsa': [], 'ozs': [], 'nzs': [], 'dzs': [],
                                                'fc': [], 'rush': [],
                                                'clutch_score': [],
                                                'goals_for': [], 'goals_against': [],
                                                'shots_for': [], 'shots_against': [],
                                                'xG_for': [], 'xG_against': [],
                                                'hdc_for': [], 'hdc_against': [],
                                                'pp_goals': [], 'pp_attempts': [],
                                                'pp_pct': [],  # Team report naming
                                                'faceoff_wins': [], 'faceoff_total': [],
                                                'fo_pct': [],  # Team report naming
                                                'blocks': [], 'pim': [],  # Team report naming
                                                'third_period_goals': [],
                                                'one_goal_game': [],
                                                'scored_first': [],
                                                'opponent_scored_first': [],
                                                'period_shots': [], 'period_corsi_pct': [],
                                                'period_pp_goals': [], 'period_pp_attempts': [],
                                                'period_pim': [], 'period_hits': [],
                                                'period_fo_pct': [], 'period_blocks': [],
                                                'period_giveaways': [], 'period_takeaways': [],
                                                'period_gs': [], 'period_xg': [],
                                                'period_nzt': [], 'period_nztsa': [],
                                                'period_ozs': [], 'period_nzs': [],
                                                'period_dzs': [], 'period_fc': [],
                                                'period_rush': []
                                            }
                                            for key, default_value in new_fields.items():
                                                if key not in venues[venue]:
                                                    venues[venue][key] = default_value
                                            # Migrate existing data to new structure
                                            if 'goals' in venues[venue] and not venues[venue].get('goals_for'):
                                                # Populate goals_for/goals_against from goals/opp_goals
                                                goals = venues[venue].get('goals', [])
                                                opp_goals = venues[venue].get('opp_goals', [])
                                                venues[venue]['goals_for'] = goals.copy()
                                                venues[venue]['goals_against'] = opp_goals.copy()
                                            if 'shots' in venues[venue] and not venues[venue].get('shots_for'):
                                                # Need to calculate shots_against from opponent data
                                                shots = venues[venue].get('shots', [])
                                                venues[venue]['shots_for'] = shots.copy()
                                                # shots_against will be populated when rebuilding
                                            if 'xg' in venues[venue] and not venues[venue].get('xG_for'):
                                                xg = venues[venue].get('xg', [])
                                                opp_xg = venues[venue].get('opp_xg', [])
                                                venues[venue]['xG_for'] = xg.copy()
                                                venues[venue]['xG_against'] = opp_xg.copy()
                                            if 'hdc' in venues[venue] and not venues[venue].get('hdc_for'):
                                                hdc = venues[venue].get('hdc', [])
                                                venues[venue]['hdc_for'] = hdc.copy()
                                                # hdc_against will be populated when rebuilding
                                    stats[team] = venues
                            logger.info(f"Loaded team stats for {len([t for t in stats if stats[t]['home']['games'] or stats[t]['away']['games']])} teams with data")
                        else:
                            # Direct team dict
                            for team, venues in data.items():
                                if team in stats:
                                    stats[team] = venues
                            logger.info(f"Loaded team stats with {len([t for t in stats if stats[t]['home']['games'] or stats[t]['away']['games']])} teams with data")
            except Exception as e:
                logger.error(f"Error loading team stats: {e}")
        else:
            logger.warning(f"Team stats file not found: {self.team_stats_file}, initialized all 32 teams")
        
        return stats
    
    def load_historical_stats(self) -> Dict:
        """Load historical seasons team performance statistics"""
        if self.historical_stats_file.exists():
            try:
                with open(self.historical_stats_file, 'r') as f:
                    data = json.load(f)
                    return data.get('seasons', {})
            except Exception as e:
                logger.error(f"Error loading historical stats: {e}")
        return {}
    
    def save_model_data(self):
        """Save model data to file"""
        try:
            # Include team stats in the main model data
            self.model_data["team_stats"] = self.team_stats
            if "goalie_stats" not in self.model_data:
                self.model_data["goalie_stats"] = {}
            if "team_last_game" not in self.model_data:
                self.model_data["team_last_game"] = {}
            # Persist goalie history
            self.model_data["goalie_history"] = self.goalie_history
            with open(self.predictions_file, 'w') as f:
                json.dump(self.model_data, f, indent=2, default=str)
            logger.info("Model data saved successfully")
        except Exception as e:
            logger.error(f"Error saving model data: {e}")
    
    def save_team_stats(self):
        """Save team statistics to file"""
        try:
            payload = {'teams': self.team_stats}
            with open(self.team_stats_file, 'w') as f:
                json.dump(payload, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving team stats: {e}")
    
    def get_current_weights(self) -> Dict:
        """Get current model weights with clipping"""
        weights = dict(self.model_data.get("model_weights", {}))
        # If features are disabled, force their weights to 0.0 before clipping
        if not self.feature_flags.get('use_rest_bucket_adj', True):
            weights['rest_days_weight'] = 0.0
        if not self.feature_flags.get('use_per_goalie_gsax', True):
            weights['goalie_performance_weight'] = 0.0
        # sos flag piggybacks on rest flag for now; keep enabled by default when non-zero
        
        # Apply weight clipping to prevent extreme values
        clipped_weights = {}
        for key, value in weights.items():
            clipped_weights[key] = np.clip(value, self.weight_clip_range[0], self.weight_clip_range[1])
        
        # Normalize weights to sum to 1.0
        total = sum(clipped_weights.values())
        if total > 0:
            for key in clipped_weights:
                clipped_weights[key] /= total
        
        return clipped_weights
    
    def _build_goalie_history(self) -> Dict[str, List[Tuple[str, str]]]:
        """Build per-team goalie start history from stored predictions/metrics_used."""
        hist: Dict[str, List[Tuple[str, str]]] = {}
        try:
            preds = self.model_data.get('predictions', [])
            for p in preds:
                date = p.get('date')
                if not date:
                    continue
                m = p.get('metrics_used') or {}
                away = (p.get('away_team') or '').upper()
                home = (p.get('home_team') or '').upper()
                ag = m.get('away_goalie')
                hg = m.get('home_goalie')
                if away and ag:
                    hist.setdefault(away, []).append((date, ag))
                if home and hg:
                    hist.setdefault(home, []).append((date, hg))
            for team in hist:
                hist[team].sort(key=lambda t: t[0])
        except Exception:
            pass
        return hist

    def _opponent_strength_index(self, opponent_key: str) -> float:
        """Estimate opponent strength ~ higher is tougher. Uses xg_avg + gs_avg if available."""
        try:
            opp_key = opponent_key.upper()
            src = None
            # Prefer historical seasons data if present
            for _, season in self.historical_stats.items():
                if 'teams' in season and opp_key in season['teams']:
                    src = season['teams'][opp_key]
                    break
            if not src and opp_key in self.team_stats:
                src = self.team_stats[opp_key]
            if isinstance(src, dict):
                xg = float(src.get('xg_avg', 2.0))
                gs = float(src.get('gs_avg', 3.0))
                return xg + gs  # typical ~5
        except Exception:
            pass
        return 5.0

    def _predict_starting_goalie(self, team_key: str, game_date: Optional[str], opponent_key: Optional[str] = None) -> Optional[str]:
        """Predict starter using simple rotation and B2B heuristic."""
        try:
            if not game_date:
                return None
            history = self.goalie_history.get(team_key, [])
            if not history:
                return None
            # Last starter
            last_date, last_goalie = history[-1]
            # Is B2B? based on last game date
            tld = (self.model_data.get('team_last_game') or {}).get(team_key)
            if tld:
                try:
                    d_prev = datetime.strptime(tld, '%Y-%m-%d')
                    d_cur = datetime.strptime(game_date, '%Y-%m-%d')
                    days = (d_cur - d_prev).days
                except Exception:
                    days = 2
            else:
                days = 2
            # Build recent window counts (last 6 starts)
            recent = [g for _, g in history[-6:]]
            counts = {}
            for g in recent:
                counts[g] = counts.get(g, 0) + 1
            # Candidate set: top 2 goalies by starts overall
            overall_counts = {}
            for _, g in history:
                overall_counts[g] = overall_counts.get(g, 0) + 1
            top2 = sorted(overall_counts.items(), key=lambda kv: kv[1], reverse=True)[:2]
            candidates = [g for g, _ in top2] if top2 else list(overall_counts.keys())

            if days <= 1:
                # Prefer goalie different from last if in candidates
                alt = [g for g in candidates if g != last_goalie]
                if alt:
                    # Among alternates, choose one with fewer recent starts
                    alt.sort(key=lambda g: counts.get(g, 0))
                    return alt[0]
                return last_goalie
            # Not B2B: choose goalie with fewer recent starts to balance workload
            if candidates:
                candidates.sort(key=lambda g: counts.get(g, 0))
                # Tie-break by better GSAX if available (games >= 3)
                gstats = self.model_data.get('goalie_stats', {})
                if len(candidates) >= 2 and counts.get(candidates[0], 0) == counts.get(candidates[1], 0):
                    # If opponent is strong, prefer better GSAX; if weak, prefer fewer recent starts
                    strong_opp = False
                    if opponent_key:
                        opp_idx = self._opponent_strength_index(opponent_key)
                        strong_opp = opp_idx >= 5.3  # threshold for top-half opponent
                    def gsax(g):
                        s = gstats.get(g)
                        if not s or s.get('games', 0) < 3:
                            return -1e9
                        games = s['games']
                        xga = float(s.get('xga_sum', 0.0)) / games
                        ga = float(s.get('ga_sum', 0.0)) / games
                        return xga - ga
                    if strong_opp:
                        c_sorted = sorted(candidates[:2], key=lambda g: gsax(g), reverse=True)
                        return c_sorted[0]
                    # else keep balanced starter (already sorted by fewer recent starts)
                return candidates[0]
            gstats = self.model_data.get('goalie_stats', {})
            candidates = {}
            for _, g in history:
                if g in gstats:
                    cand = gstats[g]
                    if cand.get('games', 0) >= 3:
                        xga = float(cand.get('xga_sum', 0.0)) / cand['games']
                        ga = float(cand.get('ga_sum', 0.0)) / cand['games']
                        candidates[g] = xga - ga
            if candidates:
                return max(candidates.items(), key=lambda kv: kv[1])[0]
            return last_goalie
        except Exception:
            return None
    
    def get_team_performance(self, team: str, venue: str) -> Dict:
        """Get comprehensive team performance data from new team stats format"""
        team_key = team.upper()
        
        # Prefer current season stats if available
        if team_key in self.team_stats:
            venue_data = self.team_stats[team_key].get(venue, {})
            # Compute situational factors
            rest_adv = self._calculate_rest_days_advantage(team_key, venue)
            goalie_perf = self._calculate_goalie_performance(team_key, venue)
 
            # Calculate averages from arrays if they exist
            def safe_mean(arr, default=0.0):
                if arr and len(arr) > 0:
                    return float(np.mean([float(x) for x in arr if x is not None]))
                return default
            
            goals_against_avg = safe_mean(venue_data.get('opp_goals', []), default=2.5)
            xg_avg = safe_mean(venue_data.get('xg', []), default=2.0)
            
            # Opponent xG is stored in 'xg_against' in our file, or 'opp_xg' sometimes.
            # Based on inspection, keys are 'xG_for' and 'xG_against' in the aggregated arrays at the bottom,
            # but inside 'home' block it's 'xg' and 'opp_xg' usually? 
            # File snippet showed 'xg' and 'opp_goals'. It didn't explicitly show 'opp_xg' in the lines 1-100 block 
            # but usually it's symmetric. However, at line 289 we saw 'xG_against'.
            # Let's try to grab 'xG_against' from the venue data if it exists, otherwise fallback to index matching?
            # Actually, let's just use 'xg' from the Perspective of 'opp_goals' or look for 'opp_xg'.
            # If not found, use 2.0.
            xg_against_avg = safe_mean(venue_data.get('xG_against', []), default=2.0)
            if xg_against_avg == 2.0 and 'opp_xg' in venue_data:
                 xg_against_avg = safe_mean(venue_data.get('opp_xg', []), default=2.0)
            
            hdc_avg = safe_mean(venue_data.get('hdc', []), default=0.0)
            shots_avg = safe_mean(venue_data.get('shots', []), default=30.0)
            goals_avg = safe_mean(venue_data.get('goals', []), 2.0)
            goals_against_avg = safe_mean(venue_data.get('goals_against', []), 3.0)
            gs_avg = safe_mean(venue_data.get('gs', []), 0.0)
            
            # Advanced Metrics
            corsi_avg = safe_mean(venue_data.get('corsi_pct', []), 50.0)
            fenwick_avg = safe_mean(venue_data.get('fenwick_pct', []), 50.0)
            power_play_avg = safe_mean(venue_data.get('power_play_pct', []), 20.0)
            penalty_kill_avg = safe_mean(venue_data.get('penalty_kill_pct', []), 80.0)
            faceoff_avg = safe_mean(venue_data.get('faceoff_pct', []), 50.0)
            hits_avg = safe_mean(venue_data.get('hits', []), 20.0)
            takeaways_avg = safe_mean(venue_data.get('takeaways', []), 5.0)
            blocked_shots_avg = safe_mean(venue_data.get('blocked_shots', []), 15.0)
            pdo_avg = safe_mean(venue_data.get('pdo', []), 100.0)
            ozs_avg = safe_mean(venue_data.get('ozs', []), 15.0) # Offensive Zone Starts
            
            giveaways_avg = safe_mean(venue_data.get('giveaways', []), 0.0)
            penalty_minutes_avg = safe_mean(venue_data.get('penalty_minutes', []), 0.0)
            
            games_played = len(venue_data.get('games', []))

            if games_played:
                return {
                    'xg': xg_avg,
                    'hdc': hdc_avg,
                    'shots': shots_avg,
                    'goals': goals_avg,
                    'gs': gs_avg,
                    'xg_avg': xg_avg,
                    'hdc_avg': hdc_avg,
                    'shots_avg': shots_avg,
                    'goals_avg': goals_avg,
                    'goals_against_avg': goals_against_avg,
                    'xg_avg': xg_avg,
                    'xg_against_avg': xg_against_avg,
                    'gs_avg': gs_avg,
                    'corsi_avg': corsi_avg,
                    'power_play_avg': power_play_avg,
                    'penalty_kill_avg': penalty_kill_avg,
                    'faceoff_avg': faceoff_avg,
                    'hits_avg': hits_avg,
                    'blocked_shots_avg': blocked_shots_avg,
                    'takeaways_avg': takeaways_avg,
                    'pdo_avg': pdo_avg,
                    'ozs_avg': ozs_avg,
                    'recent_form': self._calculate_recent_form(team_key, venue, window=10),  # Venue-aware, last 10 games
                    'head_to_head': 0.5,  # Default
                    'rest_days_advantage': rest_adv,
                    'goalie_performance': goalie_perf,
                    'confidence': self._calculate_confidence(games_played)
                }

        # Fallback to historical data if current season not available
        for season_name, season_data in self.historical_stats.items():
            if 'teams' in season_data and team_key in season_data['teams']:
                team_data = season_data['teams'][team_key]
                rest_adv = self._calculate_rest_days_advantage(team_key, venue="home")
                goalie_perf = self._calculate_goalie_performance(team_key, venue="home")

                return {
                    'xg': team_data.get('xg_avg', 0.0),
                    'hdc': team_data.get('hdc_avg', 0.0),
                    'shots': 30.0,
                    'goals': 2.0,
                    'gs': team_data.get('gs_avg', 0.0),
                    'xg_avg': team_data.get('xg_avg', 0.0),
                    'hdc_avg': team_data.get('hdc_avg', 0.0),
                    'shots_avg': 30.0,
                    'goals_avg': 2.0,
                    'goals_against_avg': 2.0,
                    'xg_avg': team_data.get('xg_avg', 0.0),
                    'xg_against_avg': 2.0,
                    'gs_avg': team_data.get('gs_avg', 0.0),
                    'corsi_avg': 50.0,
                    'power_play_avg': 0.0,
                    'penalty_kill_avg': 80.0,
                    'faceoff_avg': 50.0,
                    'hits_avg': 0.0,
                    'blocked_shots_avg': 0.0,
                    'giveaways_avg': 0.0,
                    'takeaways_avg': 0.0,
                    'penalty_minutes_avg': 0.0,
                    'games_played': team_data.get('games_played', 0),
                    'recent_form': self._calculate_recent_form(team_key, venue, window=10),
                    'head_to_head': 0.5,
                    'rest_days_advantage': rest_adv,
                    'goalie_performance': goalie_perf,
                    'confidence': self._calculate_confidence(team_data.get('games_played', 0))
                }
        
        # Try to get team data from NHL API standings as fallback
        try:
            import requests
            url = 'https://api-web.nhle.com/v1/standings/now'
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                standings = response.json()
                if standings and 'standings' in standings:
                    for team_data in standings['standings']:
                        team_abbrev_obj = team_data.get('teamAbbrev', {})
                        if isinstance(team_abbrev_obj, dict):
                            abbrev = team_abbrev_obj.get('default', '')
                        else:
                            abbrev = str(team_abbrev_obj) if team_abbrev_obj else ''
                        
                        if abbrev.upper() == team_key:
                            # Use standings data to estimate performance
                            wins = team_data.get('wins', 0)
                            losses = team_data.get('losses', 0)
                            ot_losses = team_data.get('otLosses', 0)
                            games_played = wins + losses + ot_losses
                            points = wins * 2 + ot_losses
                            
                            if games_played > 0:
                                win_pct = wins / games_played
                                points_per_game = points / games_played
                                
                                # Estimate metrics from win percentage and points
                                # Better teams have higher xG, more shots, better corsi
                                xg_estimate = 2.0 + (win_pct - 0.5) * 1.5  # Range: 1.25 to 3.5
                                shots_estimate = 28.0 + (win_pct - 0.5) * 8.0  # Range: 24 to 32
                                corsi_estimate = 45.0 + win_pct * 10.0  # Range: 45 to 55
                                
                                logger.info(f"Using API standings fallback for {team_key}: {wins}-{losses}-{ot_losses}, win_pct={win_pct:.3f}")
                                
                                return {
                                    'xg': xg_estimate, 'hdc': 2.0, 'shots': shots_estimate, 'goals': 2.5, 'gs': 3.0,
                                    'xg_avg': xg_estimate, 'xg_against_avg': 2.5, 'hdc_avg': 2.0, 'shots_avg': shots_estimate, 'goals_avg': 2.5, 'goals_against_avg': 2.5, 'gs_avg': 3.0,
                                    'corsi_avg': corsi_estimate, 'power_play_avg': 20.0, 'penalty_kill_avg': 80.0, 'faceoff_avg': 50.0,
                                    'hits_avg': 20.0, 'blocked_shots_avg': 15.0, 'giveaways_avg': 8.0,
                                    'takeaways_avg': 6.0, 'penalty_minutes_avg': 8.0,
                                    'games_played': games_played, 'recent_form': win_pct, 'head_to_head': 0.5,
                                    'rest_days_advantage': 0.0, 'goalie_performance': 0.5, 'confidence': min(0.5, games_played / 20.0)
                                }
        except Exception as e:
            logger.warning(f"Could not get standings fallback for {team_key}: {e}")
        
        # Return defaults if no data found
        return self._get_default_performance()
    
    def _get_default_performance(self) -> Dict:
        """Get default performance for teams with no data"""
        return {
            'xg': 2.0, 'hdc': 2.0, 'shots': 30.0, 'goals': 2.0, 'gs': 3.0,
            'xg_avg': 2.0, 'hdc_avg': 2.0, 'shots_avg': 30.0, 'goals_avg': 2.0, 'goals_against_avg': 2.0, 'gs_avg': 3.0,
            'corsi_avg': 50.0, 'power_play_avg': 0.0, 'penalty_kill_avg': 80.0, 'faceoff_avg': 50.0,
            'hits_avg': 0.0, 'blocked_shots_avg': 0.0, 'giveaways_avg': 0.0,
            'takeaways_avg': 0.0, 'penalty_minutes_avg': 0.0,
            'games_played': 0, 'recent_form': 0.5, 'head_to_head': 0.5,
            'rest_days_advantage': 0.0, 'goalie_performance': 0.5, 'confidence': 0.1
        }
    
    def _calculate_sos(self, team: str, venue: str, window: int = 5) -> float:
        """Compute a simple strength-of-schedule index from recent opponents.

        Uses average opponent xg_avg + gs_avg over last N opponents as a proxy.
        Returns a normalized factor around 0.5 (0.4..0.6), small impact only.
        """
        try:
            team_key = team.upper()
            if team_key not in self.team_stats or venue not in self.team_stats[team_key]:
                return 0.5
            opps = self.team_stats[team_key][venue].get('opponents', [])
            if not opps:
                return 0.5
            opps_recent = opps[-window:]
            vals = []
            for opp in opps_recent:
                opp_key = opp.upper()
                src = None
                # Prefer historical seasons data if present
                for _, season in self.historical_stats.items():
                    if 'teams' in season and opp_key in season['teams']:
                        src = season['teams'][opp_key]
                        break
                if not src and opp_key in self.team_stats:
                    src = self.team_stats[opp_key]
                if src:
                    # Handle both new and historical shapes
                    xg = src.get('xg_avg', 2.0) if isinstance(src, dict) else 2.0
                    gs = src.get('gs_avg', 3.0) if isinstance(src, dict) else 3.0
                    vals.append(xg + gs)
            if not vals:
                return 0.5
            avg = sum(vals) / len(vals)
            # Normalize: assume typical xg+gs around 5; map +/-1 to +/-0.05 around 0.5
            norm = 0.5 + max(-0.05, min(0.05, (avg - 5.0) * 0.05))
            return float(max(0.4, min(0.6, norm)))
        except Exception:
            return 0.5
        
    def _calculate_recent_form(self, team: str, venue: str, window: int = 10) -> float:
        """Calculate venue-aware recent form from completed predictions (last 7-10 games).
        
        Uses actual game results from stored predictions, filtered by venue.
        Returns win rate in last N games at that venue (home/away).
        """
        team_key = team.upper()
        predictions = self.model_data.get('predictions', [])
        
        # Filter for games involving this team at this venue with actual results
        relevant_games = []
        for pred in predictions:
            if not pred.get('actual_winner'):
                continue
            away_team = (pred.get('away_team') or '').upper()
            home_team = (pred.get('home_team') or '').upper()
            date = pred.get('date', '')
            actual_winner = pred.get('actual_winner')
            
            # Check if team played at this venue
            if venue == 'away' and team_key == away_team:
                relevant_games.append((date, 'away', actual_winner, away_team, home_team))
            elif venue == 'home' and team_key == home_team:
                relevant_games.append((date, 'home', actual_winner, away_team, home_team))
        
        # Sort by date and take last window games
        relevant_games.sort(key=lambda x: x[0])
        recent_games = relevant_games[-window:] if len(relevant_games) > window else relevant_games
        
        if not recent_games:
            return 0.5  # Default neutral
        
        # Calculate win rate
        wins = 0
        for date, v, winner, away, home in recent_games:
            # Normalize winner
            if winner in ('away', away):
                won = (v == 'away' and team_key == away)
            elif winner in ('home', home):
                won = (v == 'home' and team_key == home)
            else:
                won = False
            if won:
                wins += 1
        
        return wins / len(recent_games) if recent_games else 0.5
    
    def _calculate_venue_win_percentage(self, team: str, venue: str) -> float:
        """Calculate full-season win percentage at a specific venue (home/away).
        
        Returns win rate (0.0-1.0) for this team at this venue across all completed games.
        Returns 0.5 if no data available (neutral).
        """
        team_key = team.upper()
        predictions = self.model_data.get('predictions', [])
        
        # Filter for all games involving this team at this venue with actual results
        relevant_games = []
        for pred in predictions:
            if not pred.get('actual_winner'):
                continue
            away_team = (pred.get('away_team') or '').upper()
            home_team = (pred.get('home_team') or '').upper()
            actual_winner = pred.get('actual_winner')
            
            # Check if team played at this venue
            if venue == 'away' and team_key == away_team:
                relevant_games.append((actual_winner, away_team, home_team))
            elif venue == 'home' and team_key == home_team:
                relevant_games.append((actual_winner, away_team, home_team))
        
        if not relevant_games:
            return 0.5  # Default neutral if no data
        
        # Calculate win rate
        wins = 0
        for winner, away, home in relevant_games:
            if venue == 'away':
                won = (winner in ('away', away, team_key))
            else:  # venue == 'home'
                won = (winner in ('home', home, team_key))
            if won:
                wins += 1
        
        return float(wins / len(relevant_games))
    
    def _calculate_confidence(self, games_played: int) -> float:
        """Calculate confidence based on sample size"""
        if games_played == 0:
            return 0.1
        elif games_played < 3:
            return 0.3
        elif games_played < 10:
            return 0.5 + (games_played - 3) * 0.05
        else:
            return 0.85
    
    def _calculate_head_to_head(self, team: str, venue: str) -> float:
        """Calculate head-to-head performance against common opponents"""
        # For now, return neutral value - would need opponent-specific data
        # This could be enhanced with actual head-to-head records
        return 0.5
    
    def _calculate_rest_days_advantage(self, team: str, venue: str, game_date: Optional[str] = None) -> float:
        """Estimate rest advantage using last game before the provided game_date.

        Finds the most recent played date < game_date from combined home+away games.
        If game_date is None, falls back to last known game vs now (less accurate).
        """
        try:
            team_key = team.upper()
            # Build combined sorted list of game dates
            if team_key not in self.team_stats:
                return 0.0
            combined = []
            for v in ('home', 'away'):
                v_games = self.team_stats[team_key].get(v, {}).get('games', [])
                for dt in v_games:
                    try:
                        combined.append(datetime.strptime(dt, '%Y-%m-%d'))
                    except Exception:
                        continue
            if not combined:
                return 0.0
            combined.sort()
            if game_date:
                try:
                    target = datetime.strptime(game_date, '%Y-%m-%d')
                except Exception:
                    target = None
            else:
                target = None
            # Find last game strictly before target; else fallback to latest
            last_date = None
            if target:
                for d in reversed(combined):
                    if d < target:
                        last_date = d
                        break
            if last_date is None:
                last_date = combined[-1]
            base_days_ref = target if target else datetime.now()
            days_rest = (base_days_ref - last_date).days
            
            # Detect B2B: need to check if previous game was 1 day before last_date
            is_b2b = (days_rest == 1)
            b2b_game = 1  # Default to first game of B2B
            if is_b2b and len(combined) >= 2:
                # Find second-to-last game date
                last_two = sorted([d for d in combined if d < target])[-2:] if target else []
                if len(last_two) >= 2:
                    days_between_last_two = (last_two[1] - last_two[0]).days
                    if days_between_last_two == 1:
                        b2b_game = 2  # This is the second game of B2B
            
            # Travel penalty: if switching venues (away->home or home->away) in B2B
            travel_penalty = 0.0
            if is_b2b:
                # Get venue of last game - check team_stats
                last_venue = None
                for v in ('home', 'away'):
                    v_games = self.team_stats[team_key].get(v, {}).get('games', [])
                    if last_date.strftime('%Y-%m-%d') in v_games:
                        last_venue = v
                        break
                if last_venue and last_venue != venue:
                    travel_penalty = -0.015  # Penalty for venue switch in B2B
            
            # Base heuristic with B2B detail
            if is_b2b:
                if b2b_game == 2:
                    base = -0.04  # Second game of B2B is worse
                else:
                    base = -0.025  # First game of B2B
            elif days_rest == 2:
                base = 0.0
            elif days_rest >= 3:
                base = 0.02
            else:
                base = 0.0
            
            # Historical rest-bucket adjustment (cap +/- 0.02)
            bucket_adj = self._rest_bucket_adjustment(team_key, venue, days_rest)
            total = base + bucket_adj + travel_penalty
            return float(max(-0.06, min(0.06, total)))
        except Exception:
            return 0.0

    def _rest_bucket_adjustment(self, team_key: str, venue: str, current_days_rest: int) -> float:
        """Compute adjustment from historical performance for the rest bucket.

        Uses all recorded games this season (home+away combined) to derive rest buckets.
        Buckets: 1 (B2B), 2, 3+ days. Adjustment = bucket win rate - overall win rate, scaled.
        """
        if not self.feature_flags.get('use_rest_bucket_adj', True):
            return 0.0
        try:
            team_data = self.team_stats.get(team_key, {})
            if not team_data:
                return 0.0
            # Build unified game list [(date, won: int)] from home and away
            unified = []
            for v in ('home', 'away'):
                vdata = team_data.get(v, {})
                v_games = vdata.get('games', [])
                v_goals = vdata.get('goals', [])
                v_opp = vdata.get('opp_goals', [])
                for dt, gf, ga in zip(v_games, v_goals, v_opp):
                    try:
                        d = datetime.strptime(dt, '%Y-%m-%d')
                    except Exception:
                        continue
                    unified.append((d, 1 if float(gf) > float(ga) else 0))
            if len(unified) < 6:
                return 0.0
            unified.sort(key=lambda t: t[0])
            # Compute rest days and wins aligned to the later game
            rest_wins = []
            for i in range(1, len(unified)):
                d_prev, _ = unified[i-1]
                d_cur, win_flag = unified[i]
                days = (d_cur - d_prev).days
                rest_wins.append((days, win_flag))
            def bucket(d):
                if d <= 1:
                    return 'B2B'
                if d == 2:
                    return 'D2'
                return 'D3+'
            wins = [(bucket(d), w) for d, w in rest_wins]
            if not wins:
                return 0.0
            overall = sum(w for _, w in wins) / len(wins)
            by_bucket = {}
            counts = {}
            for b, w in wins:
                by_bucket[b] = by_bucket.get(b, 0) + w
                counts[b] = counts.get(b, 0) + 1
            for b in list(by_bucket.keys()):
                by_bucket[b] /= counts[b]
            cur_bucket = bucket(current_days_rest)
            if cur_bucket not in by_bucket or counts.get(cur_bucket, 0) < 2:
                return 0.0
            diff = by_bucket[cur_bucket] - overall
            # Scale to small advantage, cap +/-0.02
            return float(max(-0.02, min(0.02, diff * 0.05)))
        except Exception:
            return 0.0
    
    def _calculate_goalie_performance(self, team: str, venue: str) -> float:
        """Proxy starting goalie GSAX.

        Prefer per-goalie GSAX when we have a last_goalie for this venue and
        accumulated goalie_stats for that goalie; otherwise fallback to team proxy.
        """
        try:
            team_key = team.upper()
            if team_key not in self.team_stats or venue not in self.team_stats[team_key]:
                return 0.5
            # Try per-goalie first if enabled
            if self.feature_flags.get('use_per_goalie_gsax', True):
                last_goalie = self.team_stats[team_key][venue].get('last_goalie')
                gstats = self.model_data.get('goalie_stats', {})
                if last_goalie and last_goalie in gstats:
                    gs = gstats[last_goalie]
                    games = max(1, gs.get('games', 0))
                    # Require minimum sample to reduce noise
                    if games < 3:
                        raise ValueError('insufficient goalie sample, fallback to team proxy')
                    xga = float(gs.get('xga_sum', 0.0)) / games
                    ga = float(gs.get('ga_sum', 0.0)) / games
                    gsax_avg = xga - ga
                    # Shrink toward neutral based on sample size beyond 3 (up to 13)
                    shrink = min(1.0, max(0.0, (games - 3) / 10.0))
                    adj = (0.40 / 6.0) * shrink
                    perf = 0.55 + max(-3.0, min(3.0, gsax_avg)) * adj
                    return float(max(0.35, min(0.75, perf)))
            # Team proxy fallback
            opp_xg = self.team_stats[team_key][venue].get('opp_xg', [])
            opp_g = self.team_stats[team_key][venue].get('opp_goals', [])
            n = min(len(opp_xg), len(opp_g))
            if n == 0:
                return 0.5
            window = min(5, n)
            recent = []
            for i in range(1, window+1):
                try:
                    xg_val = float(opp_xg[-i]) if opp_xg[-i] is not None else 0.0
                    ga_val = float(opp_g[-i]) if opp_g[-i] is not None else 0.0
                    if xg_val > 0 or ga_val > 0:  # Only include valid data
                        recent.append((xg_val, ga_val))
                except (ValueError, TypeError, IndexError):
                    continue
            
            if len(recent) == 0:
                return 0.5  # No valid data, return neutral
            
            gsax_vals = [xg - ga for xg, ga in recent]
            gsax_avg = sum(gsax_vals) / len(gsax_vals)
            perf = 0.55 + max(-3.0, min(3.0, gsax_avg)) * (0.40 / 6.0)
            return float(max(0.35, min(0.75, perf)))
        except Exception:
            return 0.5

    def _goalie_performance_for_game(self, team: str, venue: str, game_date: Optional[str], 
                                      confirmed_goalie: Optional[str] = None) -> float:
        """Get goalie performance using confirmed or predicted starter when enabled and available.
        
        Args:
            team: Team abbreviation
            venue: 'home' or 'away'
            game_date: Game date string
            confirmed_goalie: Confirmed goalie name (from lineup service), if available
        """
        try:
            if self.feature_flags.get('use_per_goalie_gsax', True) and game_date:
                team_key = team.upper()
                # Use confirmed goalie if available, otherwise predict
                starter = confirmed_goalie or self._predict_starting_goalie(team_key, game_date)
                if starter:
                    # Try to find goalie in goalie_stats by name (exact or fuzzy match)
                    goalie_stats = self.model_data.get('goalie_stats', {})
                    gs = None
                    # Try exact match first
                    if starter in goalie_stats:
                        gs = goalie_stats[starter]
                    else:
                        # Fuzzy match: check if any goalie name contains starter name or vice versa
                        for goalie_name, stats in goalie_stats.items():
                            if starter.lower() in goalie_name.lower() or goalie_name.lower() in starter.lower():
                                gs = stats
                                break
                    
                    if gs and gs.get('games', 0) >= 3:  # Lowered threshold since we have confirmed starter
                        games = gs['games']
                        xga = float(gs.get('xga_sum', 0.0)) / games
                        ga = float(gs.get('ga_sum', 0.0)) / games
                        gsax_avg = xga - ga
                        shrink = min(1.0, max(0.0, (games - 3) / 10.0))  # Adjusted for lower threshold
                        adj = (0.40 / 6.0) * shrink
                        perf = 0.55 + max(-3.0, min(3.0, gsax_avg)) * adj
                        return float(max(0.35, min(0.75, perf)))
        except Exception:
            pass
        return self._calculate_goalie_performance(team, venue)

    def _calculate_goalie_matchup_quality(self, away_team: str, home_team: str, game_date: Optional[str],
                                          away_goalie_confirmed: Optional[str] = None,
                                          home_goalie_confirmed: Optional[str] = None) -> float:
        """Calculate goalie matchup quality advantage for away team.
        
        Returns a value between -1.0 and 1.0 where:
        - Positive = away goalie is better than home goalie
        - Negative = home goalie is better than away goalie
        - Magnitude indicates the strength of the advantage
        """
        try:
            away_goalie_perf = self._goalie_performance_for_game(
                away_team, 'away', game_date, confirmed_goalie=away_goalie_confirmed
            )
            home_goalie_perf = self._goalie_performance_for_game(
                home_team, 'home', game_date, confirmed_goalie=home_goalie_confirmed
            )
            # Goalie performance is normalized 0.35-0.75, so difference ranges from -0.4 to +0.4
            # Scale to -1.0 to +1.0 for better interpretability
            matchup_diff = (away_goalie_perf - home_goalie_perf) / 0.4
            return float(max(-1.0, min(1.0, matchup_diff)))
        except Exception:
            return 0.0
    
    def _calculate_special_teams_matchup(self, away_team: str, home_team: str) -> float:
        """Calculate special teams matchup advantage for away team.
        
        Combines:
        - Away PP% vs Home PK%
        - Home PP% vs Away PK%
        
        Returns a value between -1.0 and 1.0 where:
        - Positive = away team has special teams advantage
        - Negative = home team has special teams advantage
        """
        try:
            away_perf = self.get_team_performance(away_team, 'away')
            home_perf = self.get_team_performance(home_team, 'home')
            
            # Get power play percentages
            away_pp_pct = away_perf.get('power_play_avg', 0.0) / 100.0  # Convert to 0-1
            home_pp_pct = home_perf.get('power_play_avg', 0.0) / 100.0
            
            # Get penalty kill percentages (100 - PK% = goals allowed rate)
            away_pk_pct = away_perf.get('penalty_kill_avg', 80.0) / 100.0  # Default 80% PK
            home_pk_pct = home_perf.get('penalty_kill_avg', 80.0) / 100.0
            
            # Calculate expected goals on power play
            # Away PP effectiveness = away_pp_pct * (1 - home_pk_pct)
            away_pp_effectiveness = away_pp_pct * (1.0 - home_pk_pct)
            home_pp_effectiveness = home_pp_pct * (1.0 - away_pk_pct)
            
            # Special teams advantage = difference in effectiveness
            # Normalize to -1.0 to +1.0 range
            st_diff = (away_pp_effectiveness - home_pp_effectiveness) * 2.0
            return float(max(-1.0, min(1.0, st_diff)))
        except Exception:
            return 0.0

    def debug_situational_components(self, away_team: str, home_team: str, game_date: Optional[str]) -> Dict:
        """Expose rest and goalie components for debugging comparisons."""
        try:
            away_rest = self._calculate_rest_days_advantage(away_team, 'away', game_date)
            home_rest = self._calculate_rest_days_advantage(home_team, 'home', game_date)
            away_goalie = self._goalie_performance_for_game(away_team, 'away', game_date)
            home_goalie = self._goalie_performance_for_game(home_team, 'home', game_date)
            goalie_matchup = self._calculate_goalie_matchup_quality(away_team, home_team, game_date)
            special_teams_matchup = self._calculate_special_teams_matchup(away_team, home_team)
            return {
                'away_rest': away_rest,
                'home_rest': home_rest,
                'away_goalie_perf': away_goalie,
                'home_goalie_perf': home_goalie,
                'goalie_matchup_quality': goalie_matchup,
                'special_teams_matchup': special_teams_matchup,
            }
        except Exception:
            return {
                'away_rest': None,
                'home_rest': None,
                'away_goalie_perf': None,
                'home_goalie_perf': None,
                'goalie_matchup_quality': None,
                'special_teams_matchup': None,
            }

    def backtest_recent(self, n: int = 60) -> Dict:
        """Backtest accuracy on last n completed games with actual results."""
        import math
        preds = [p for p in self.model_data.get('predictions', []) if p.get('actual_winner')]
        if not preds:
            return {"samples": 0, "accuracy": 0.0, "brier": None, "log_loss": None}
        sample = preds[-n:]
        correct = 0
        brier_sum = 0.0
        log_loss_sum = 0.0
        ll_count = 0
        for p in sample:
            away_team = p.get('away_team')
            home_team = p.get('home_team')
            pa = p.get('predicted_away_win_prob')
            ph = p.get('predicted_home_win_prob')
            if pa is None or ph is None:
                pa = (p.get('predicted_away_win_prob', 50.0) / 100.0)
                ph = (p.get('predicted_home_win_prob', 50.0) / 100.0)
            total = (pa or 0.5) + (ph or 0.5)
            if total > 0:
                pa /= total
                ph /= total
            winner = p.get('actual_winner')
            # Normalize winner to 'away'/'home' if team abbrev stored
            if winner and winner not in ('away','home'):
                if winner == away_team:
                    winner = 'away'
                elif winner == home_team:
                    winner = 'home'
            predicted = 'away' if pa > ph else 'home'
            if winner in ('away','home') and predicted == winner:
                correct += 1
            y = 1.0 if winner == 'away' else 0.0 if winner == 'home' else None
            if y is not None:
                brier_sum += (pa - y) ** 2
                p_true = pa if y == 1.0 else ph
                p_true = min(max(p_true, 1e-6), 1 - 1e-6)
                log_loss_sum += -math.log(p_true)
                ll_count += 1
        size = len(sample)
        return {
            'samples': size,
            'accuracy': correct / size if size else 0.0,
            'brier': brier_sum / size if size else None,
            'log_loss': log_loss_sum / ll_count if ll_count else None,
        }

    def backtest_recent_recompute(self, n: int = 60) -> Dict:
        """Backtest by recomputing probabilities for last n completed games using current model settings."""
        import math
        preds = [p for p in self.model_data.get('predictions', []) if p.get('actual_winner')]
        if not preds:
            return {"samples": 0, "accuracy": 0.0, "brier": None, "log_loss": None}
        sample = preds[-n:]
        correct = 0
        brier_sum = 0.0
        log_loss_sum = 0.0
        ll_count = 0
        for p in sample:
            away_team = p.get('away_team')
            home_team = p.get('home_team')
            if not away_team or not home_team:
                continue
            # Recompute using ensemble
            res = self.ensemble_predict(away_team, home_team)
            pa = res.get('away_prob', 0.5)
            ph = res.get('home_prob', 0.5)
            total = (pa or 0.5) + (ph or 0.5)
            if total > 0:
                pa /= total
                ph /= total
            winner = p.get('actual_winner')
            if winner and winner not in ('away','home'):
                if winner == away_team:
                    winner = 'away'
                elif winner == home_team:
                    winner = 'home'
            predicted = 'away' if pa > ph else 'home'
            if winner in ('away','home') and predicted == winner:
                correct += 1
            y = 1.0 if winner == 'away' else 0.0 if winner == 'home' else None
            if y is not None:
                brier_sum += (pa - y) ** 2
                p_true = pa if y == 1.0 else ph
                p_true = min(max(p_true, 1e-6), 1 - 1e-6)
                log_loss_sum += -math.log(p_true)
                ll_count += 1
        size = len(sample)
        return {
            'samples': size,
            'accuracy': correct / size if size else 0.0,
            'brier': brier_sum / size if size else None,
            'log_loss': log_loss_sum / ll_count if ll_count else None,
        }
    
    def _simple_prediction(self, away_team: str, home_team: str, away_perf: Dict, home_perf: Dict) -> Dict:
        """Simple prediction when we don't have enough data"""
        # Use basic win/loss records if available, otherwise neutral prediction
        away_wins = away_perf.get('games_played', 0)
        home_wins = home_perf.get('games_played', 0)
        
        if away_wins == 0 and home_wins == 0:
            # No data for either team - neutral prediction with home advantage
            away_prob = 47.5
            home_prob = 52.5
            confidence = 10.0
        else:
            # Use simple win rate if available
            total_games = away_wins + home_wins
            if total_games > 0:
                away_prob = (away_wins / total_games) * 100
                home_prob = (home_wins / total_games) * 100
                # Add home advantage
                home_prob += 5.0
                away_prob -= 5.0
                confidence = min(30.0, total_games * 10.0)
            else:
                away_prob = 47.5
                home_prob = 52.5
                confidence = 10.0
        
        # Normalize to 100%
        total = away_prob + home_prob
        away_prob = (away_prob / total) * 100
        home_prob = (home_prob / total) * 100
        
        confidence_pct = confidence
        confidence = max(0.0, min(1.0, confidence_pct / 100.0))
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'away_score': away_prob,
            'home_score': home_prob,
            'away_perf': away_perf,
            'home_perf': home_perf,
            'prediction_confidence': confidence,
            'uncertainty': 0.0
        }
    
    def predict_game(self, away_team: str, home_team: str, current_away_score: int = None, 
                    current_home_score: int = None, period: int = 1, game_id: str = None, game_date: Optional[str] = None) -> Dict:
        """Predict a game with improved features and confidence"""
        
        # Get team performance data
        away_perf = self.get_team_performance(away_team, venue="away")
        home_perf = self.get_team_performance(home_team, venue="home")
        
        # If we don't have enough data for either team, use simple prediction
        if away_perf['games_played'] < 2 or home_perf['games_played'] < 2:
            return self._simple_prediction(away_team, home_team, away_perf, home_perf)
        
        # Get current model weights
        weights = self.get_current_weights()
        
        # Calculate weighted scores with comprehensive metrics and advanced features
        # Override goalie performance with predicted starter when available
        away_goalie_perf = self._goalie_performance_for_game(away_team, 'away', game_date)
        home_goalie_perf = self._goalie_performance_for_game(home_team, 'home', game_date)
        # Strength of schedule modifiers (around 0.5)
        away_sos = self._calculate_sos(away_team, 'away')
        home_sos = self._calculate_sos(home_team, 'home')
        # Recalculate rest for this game date
        away_rest = self._calculate_rest_days_advantage(away_team, 'away', game_date)
        home_rest = self._calculate_rest_days_advantage(home_team, 'home', game_date)

        away_score = (
            away_perf['xg_avg'] * weights['xg_weight'] +
            away_perf['hdc_avg'] * weights['hdc_weight'] +
            away_perf['corsi_avg'] * weights['corsi_weight'] +
            away_perf['power_play_avg'] * weights['power_play_weight'] +
            away_perf['faceoff_avg'] * weights['faceoff_weight'] +
            away_perf['shots_avg'] * weights['shots_weight'] +
            away_perf['hits_avg'] * weights['hits_weight'] +
            away_perf['blocked_shots_avg'] * weights['blocked_shots_weight'] +
            (away_perf['takeaways_avg'] - away_perf['giveaways_avg']) * weights['takeaways_weight'] +
            away_perf['penalty_minutes_avg'] * weights['penalty_minutes_weight'] +
            away_perf['recent_form'] * weights['recent_form_weight'] +
            away_perf['head_to_head'] * weights['head_to_head_weight'] +
            away_rest * weights['rest_days_weight'] +
            away_goalie_perf * weights['goalie_performance_weight'] +
            away_sos * weights.get('sos_weight', 0.0)
        )
        
        home_score = (
            home_perf['xg_avg'] * weights['xg_weight'] +
            home_perf['hdc_avg'] * weights['hdc_weight'] +
            home_perf['corsi_avg'] * weights['corsi_weight'] +
            home_perf['power_play_avg'] * weights['power_play_weight'] +
            home_perf['faceoff_avg'] * weights['faceoff_weight'] +
            home_perf['shots_avg'] * weights['shots_weight'] +
            home_perf['hits_avg'] * weights['hits_weight'] +
            home_perf['blocked_shots_avg'] * weights['blocked_shots_weight'] +
            (home_perf['takeaways_avg'] - home_perf['giveaways_avg']) * weights['takeaways_weight'] +
            home_perf['penalty_minutes_avg'] * weights['penalty_minutes_weight'] +
            home_perf['recent_form'] * weights['recent_form_weight'] +
            home_perf['head_to_head'] * weights['head_to_head_weight'] +
            home_rest * weights['rest_days_weight'] +
            home_goalie_perf * weights['goalie_performance_weight'] +
            home_sos * weights.get('sos_weight', 0.0)
        )
        
        # Add home ice advantage (small but consistent)
        home_advantage = 0.05
        home_score *= (1.0 + home_advantage)
        
        # Calculate base probabilities
        total_score = away_score + home_score
        if total_score > 0:
            away_prob = (away_score / total_score) * 100
            home_prob = (home_score / total_score) * 100
        else:
            away_prob = 50.0
            home_prob = 50.0
        
        # Add uncertainty based on confidence
        away_confidence = away_perf['confidence']
        home_confidence = home_perf['confidence']
        avg_confidence = (away_confidence + home_confidence) / 2
        
        # Add noise for uncertainty (reduces extreme predictions) unless deterministic
        uncertainty_noise = (1 - avg_confidence) * 10  # Up to 10% noise
        noise = 0.0 if self.deterministic else float(np.random.normal(0, uncertainty_noise))
        away_prob += noise
        home_prob -= noise
        
        # Ensure probabilities stay within reasonable bounds (as percentages)
        away_prob = max(10, min(90, away_prob))
        home_prob = max(10, min(90, home_prob))
        
        # Normalize to 100%
        total = away_prob + home_prob
        away_prob = (away_prob / total) * 100
        home_prob = (home_prob / total) * 100
        
        # Convert to decimal (0-1) for internal consistency with ensemble_predict
        # But store as percentage for display
        away_prob_decimal = away_prob / 100.0
        home_prob_decimal = home_prob / 100.0
        
        # Calculate confidence in prediction (keep as decimal 0-1)
        prediction_confidence = avg_confidence
        
        return {
            'away_prob': away_prob_decimal,  # Return as decimal for blending
            'home_prob': home_prob_decimal,   # Return as decimal for blending
            'away_score': away_score,
            'home_score': home_score,
            'away_perf': away_perf,
            'home_perf': home_perf,
            'prediction_confidence': prediction_confidence,
            'uncertainty': uncertainty_noise
        }
    
    def ensemble_predict(self, away_team: str, home_team: str, current_away_score: int = None, 
                        current_home_score: int = None, period: int = 1, game_id: str = None, game_date: Optional[str] = None) -> Dict:
        """Use ensemble of multiple prediction methods for improved accuracy"""
        
        # Method 1: Traditional metrics (our comprehensive model)
        traditional = self.predict_game(away_team, home_team, current_away_score, current_home_score, period, game_id, game_date)
        
        # Method 2: Recent form weighted prediction
        form_based = self._form_based_predict(away_team, home_team)
        
        # Method 3: Momentum/streak based prediction
        momentum_based = self._momentum_based_predict(away_team, home_team)
        
        # Combine methods with weights (favor proven traditional model)
        # If we have strong first-goal stats, we can modestly nudge toward the
        # team that historically converts first goals into wins more reliably.
        weights = [0.70, 0.20, 0.10]  # Traditional, form, momentum
        
        away_prob = (
            traditional['away_prob'] * weights[0] +
            form_based['away_prob'] * weights[1] +
            momentum_based['away_prob'] * weights[2]
        )
        
        home_prob = (
            traditional['home_prob'] * weights[0] +
            form_based['home_prob'] * weights[1] +
            momentum_based['home_prob'] * weights[2]
        )
        
        # Normalize to 1.0 (decimal probabilities)
        total = away_prob + home_prob
        if total > 0:
            away_prob = away_prob / total
            home_prob = home_prob / total
        else:
            away_prob = 0.5
            home_prob = 0.5
        
        # Calculate ensemble confidence
        ensemble_confidence = (
            traditional['prediction_confidence'] * weights[0] +
            form_based['prediction_confidence'] * weights[1] +
            momentum_based['prediction_confidence'] * weights[2]
        )
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'prediction_confidence': ensemble_confidence,
            'ensemble_methods': {
                'traditional': traditional,
                'form_based': form_based,
                'momentum_based': momentum_based
            },
            'ensemble_weights': weights
        }
    
    def _form_based_predict(self, away_team: str, home_team: str) -> Dict:
        """Predict based primarily on recent form (last 5 games)"""
        away_perf = self.get_team_performance(away_team, venue="away")
        home_perf = self.get_team_performance(home_team, venue="home")
        
        # Use recent form but weight it by confidence and games played
        away_form_score = away_perf['recent_form'] * away_perf['confidence']
        home_form_score = home_perf['recent_form'] * home_perf['confidence']
        
        # Add home advantage
        home_form_score *= 1.05
        
        # If we don't have enough data, fall back to traditional metrics
        if away_perf['games_played'] < 3 or home_perf['games_played'] < 3:
            # Use traditional prediction as fallback
            traditional = self.predict_game(away_team, home_team)
            return {
                'away_prob': traditional['away_prob'],
                'home_prob': traditional['home_prob'],
                'prediction_confidence': traditional['prediction_confidence'] * 0.7  # Lower confidence for fallback
            }
        
        # Calculate probabilities
        total_score = away_form_score + home_form_score
        if total_score > 0:
            away_prob = (away_form_score / total_score) * 100
            home_prob = (home_form_score / total_score) * 100
        else:
            away_prob = 50.0
            home_prob = 50.0
        
        # Lower confidence for form-based predictions
        confidence_pct = min(away_perf['confidence'], home_perf['confidence']) * 0.8 * 100
        confidence = max(0.0, min(1.0, confidence_pct / 100.0))
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'prediction_confidence': confidence
        }
    
    def _momentum_based_predict(self, away_team: str, home_team: str) -> Dict:
        """Predict based on momentum and streaks"""
        away_perf = self.get_team_performance(away_team, venue="away")
        home_perf = self.get_team_performance(home_team, venue="home")
        
        # If we don't have enough data, fall back to traditional metrics
        if away_perf['games_played'] < 3 or home_perf['games_played'] < 3:
            traditional = self.predict_game(away_team, home_team)
            return {
                'away_prob': traditional['away_prob'],
                'home_prob': traditional['home_prob'],
                'prediction_confidence': traditional['prediction_confidence'] * 0.6  # Lower confidence for fallback
            }
        
        # Calculate momentum from recent form and confidence
        away_momentum = away_perf['recent_form'] * away_perf['confidence'] * 100
        home_momentum = home_perf['recent_form'] * home_perf['confidence'] * 100
        
        # Add home advantage
        home_momentum *= 1.05
        
        # Calculate probabilities
        total_momentum = away_momentum + home_momentum
        if total_momentum > 0:
            away_prob = (away_momentum / total_momentum) * 100
            home_prob = (home_momentum / total_momentum) * 100
        else:
            away_prob = 50.0
            home_prob = 50.0
        
        # Lower confidence for momentum-based predictions
        confidence_pct = min(away_perf['confidence'], home_perf['confidence']) * 0.6 * 100
        confidence = max(0.0, min(1.0, confidence_pct / 100.0))
        
        return {
            'away_prob': away_prob,
            'home_prob': home_prob,
            'prediction_confidence': confidence
        }

    # ---------- First-goal derived features ----------

    def get_first_goal_profile(self, team: str, venue: str) -> Dict[str, float]:
        """
        Return first-goal profile for a team at a given venue ('home' or 'away'):
        - scored_first_rate
        - win_rate_scoring_first
        - win_rate_conceding_first
        - first_goal_uplift
        Falls back to neutral priors if we lack data.
        """
        venue_key = "home" if venue == "home" else "away"
        stats = self.model_data.get("first_goal_stats", {})
        team_stats = stats.get(team.upper())
        if not team_stats or venue_key not in team_stats:
            # Neutral priors: 50% chance to score first, modest uplift
            return {
                "scored_first_rate": 0.5,
                "win_rate_scoring_first": 0.6,
                "win_rate_conceding_first": 0.4,
                "first_goal_uplift": 0.2,
            }
        return team_stats[venue_key]

    def get_team_bias(self, team: str, venue: str) -> float:
        """
        Return a small bias correction for a team at a given venue ('home'/'away'),
        based on historical average error. Positive means we historically
        UNDER-estimated that team's win probability at this venue.
        """
        venue_key = "home" if venue == "home" else "away"
        bias_map = self.model_data.get("team_bias") or {}
        team_map = bias_map.get(team.upper())
        if not team_map:
            return 0.0
        return float(team_map.get(venue_key, 0.0) or 0.0)
    
    def add_prediction(self, game_id: str, date: str, away_team: str, home_team: str,
                      predicted_away_prob: float, predicted_home_prob: float,
                      metrics_used: Dict, actual_winner: Optional[str] = None,
                      actual_away_score: int = None, actual_home_score: int = None,
                      prediction_confidence: Optional[float] = None,
                      raw_away_prob: Optional[float] = None, raw_home_prob: Optional[float] = None,
                      calibrated_away_prob: Optional[float] = None, calibrated_home_prob: Optional[float] = None,
                      correlation_away_prob: Optional[float] = None, correlation_home_prob: Optional[float] = None,
                      ensemble_away_prob: Optional[float] = None, ensemble_home_prob: Optional[float] = None):
        """Add a new prediction with actual game outcomes"""
        
        predicted_side = "away" if predicted_away_prob > predicted_home_prob else "home"
        predicted_team = self._side_to_team(predicted_side, away_team, home_team)
        
        if prediction_confidence is None:
            prediction_confidence = max(predicted_away_prob, predicted_home_prob)
        if prediction_confidence is not None:
            if prediction_confidence > 1:
                prediction_confidence = prediction_confidence / 100.0
            prediction_confidence = max(0.0, min(1.0, prediction_confidence))
        
        if raw_away_prob is None:
            raw_away_prob = predicted_away_prob
        if raw_home_prob is None:
            raw_home_prob = predicted_home_prob
        if calibrated_away_prob is None:
            calibrated_away_prob = predicted_away_prob
        if calibrated_home_prob is None:
            calibrated_home_prob = predicted_home_prob
        
        prediction_margin = abs(predicted_away_prob - predicted_home_prob)
        corr_disagreement = None
        if correlation_away_prob is not None and correlation_home_prob is not None:
            corr_disagreement = abs(float(correlation_away_prob) - float(correlation_home_prob if correlation_home_prob is not None else correlation_away_prob))
        if corr_disagreement is None and correlation_away_prob is not None and ensemble_away_prob is not None:
            corr_disagreement = abs(float(correlation_away_prob) - float(ensemble_away_prob))
        if corr_disagreement is None:
            corr_disagreement = 0.0
        
        away_rest_val = float(metrics_used.get("away_rest", 0.0)) if metrics_used else 0.0
        home_rest_val = float(metrics_used.get("home_rest", 0.0)) if metrics_used else 0.0
        context_bucket = self.determine_context_bucket(away_rest_val, home_rest_val)
        away_b2b = away_rest_val <= -0.5
        home_b2b = home_rest_val <= -0.5

        flip_rate = float(metrics_used.get("monte_carlo_flip_rate", 0.0)) if metrics_used else 0.0
        if flip_rate == 0.0:
            try:
                flip_rate = self._estimate_monte_carlo_signal({
                    "metrics_used": metrics_used,
                    "predicted_winner": predicted_side,
                    "raw_away_prob": raw_away_prob,
                    "raw_home_prob": raw_home_prob
                }, iterations=40)
            except Exception:
                flip_rate = 0.0
        
        feature_vec = [prediction_confidence, prediction_margin, corr_disagreement, flip_rate]
        upset_probability = self.predict_upset_probability(feature_vec)
        
        actual_side = self._normalize_outcome_side(actual_winner, away_team, home_team)
        actual_team = self._side_to_team(actual_side, away_team, home_team)
        
        # Additional outcome labels
        goal_diff = None
        if actual_away_score is not None and actual_home_score is not None:
            try:
                goal_diff = int(actual_home_score) - int(actual_away_score)
            except (TypeError, ValueError):
                goal_diff = None
        
        prediction = {
            "game_id": game_id,
            "date": date,
            "away_team": away_team,
            "home_team": home_team,
            "predicted_away_win_prob": predicted_away_prob,  # Already in decimal format
            "predicted_home_win_prob": predicted_home_prob,  # Already in decimal format
            "metrics_used": metrics_used,
            "actual_winner": actual_winner,
            "actual_winner_side": actual_side,
            "actual_winner_team": actual_team or actual_winner,
            "actual_away_score": actual_away_score,
            "actual_home_score": actual_home_score,
            "goal_diff": goal_diff,
            "prediction_accuracy": None,
            "timestamp": datetime.now().isoformat(),
            "predicted_winner": predicted_side,
            "predicted_winner_team": predicted_team,
            "prediction_confidence": prediction_confidence,
            "prediction_margin": prediction_margin,
            "raw_away_prob": raw_away_prob,
            "raw_home_prob": raw_home_prob,
            "calibrated_away_prob": calibrated_away_prob,
            "calibrated_home_prob": calibrated_home_prob,
            "correlation_away_prob": correlation_away_prob,
            "correlation_home_prob": correlation_home_prob,
            "ensemble_away_prob": ensemble_away_prob,
            "ensemble_home_prob": ensemble_home_prob,
            "corr_disagreement": corr_disagreement,
            "monte_carlo_flip_rate": flip_rate,
            "upset_probability": upset_probability,
            "context_bucket": context_bucket,
            "away_back_to_back": away_b2b,
            "home_back_to_back": home_b2b,
            "away_rest_value": away_rest_val,
            "home_rest_value": home_rest_val
        }
        
        # Calculate prediction accuracy if we know the actual winner
        if actual_side:
            if actual_side == "away":
                prediction["prediction_accuracy"] = predicted_away_prob  # Already in decimal format
            elif actual_side == "home":
                prediction["prediction_accuracy"] = predicted_home_prob  # Already in decimal format
            
            # Update model performance
            self.update_model_performance(prediction)
            
            # Update team stats with actual game data
            self.update_team_stats(prediction)
            
            # Correlation diagnostics and upset flag
            correlation_side = None
            if correlation_away_prob is not None and correlation_home_prob is not None:
                correlation_side = "away" if correlation_away_prob >= correlation_home_prob else "home"
                prediction["correlation_predicted_winner"] = correlation_side
                prediction["correlation_correct"] = (correlation_side == actual_side)
            prediction["was_upset"] = self._determine_upset(
                predicted_side, actual_side, prediction_confidence, prediction_margin
            )

            # Log high-confidence mistakes for continual learning diagnostics
            try:
                if prediction_confidence >= 0.6 and predicted_side != actual_side:
                    err_log = self.model_data.setdefault("error_log", [])
                    err_log.append({
                        "game_id": game_id,
                        "date": date,
                        "away_team": away_team,
                        "home_team": home_team,
                        "predicted_away_prob": predicted_away_prob,
                        "predicted_home_prob": predicted_home_prob,
                        "actual_winner": actual_winner,
                        "prediction_confidence": prediction_confidence,
                        "prediction_margin": prediction_margin,
                        "context_bucket": context_bucket,
                        "away_rest": away_rest_val,
                        "home_rest": home_rest_val,
                        "monte_carlo_flip_rate": flip_rate,
                    })
                    # Keep only the most recent 200 errors
                    self.model_data["error_log"] = err_log[-200:]
            except Exception:
                pass
        else:
            prediction["correlation_predicted_winner"] = None
            prediction["correlation_correct"] = None
            prediction["was_upset"] = False
        
        # Ensure probabilities are within bounds before storing
        predicted_away_prob = max(0.05, min(0.95, predicted_away_prob))
        predicted_home_prob = max(0.05, min(0.95, predicted_home_prob))
        # Normalize to sum to 1.0
        total = predicted_away_prob + predicted_home_prob
        predicted_away_prob = predicted_away_prob / total
        predicted_home_prob = predicted_home_prob / total
        
        # Update prediction dict with bounded values
        prediction["predicted_away_win_prob"] = predicted_away_prob
        prediction["predicted_home_win_prob"] = predicted_home_prob
        
        self.model_data["predictions"].append(prediction)
        logger.info(
            f"Added prediction for {away_team} @ {home_team}: "
            f"{predicted_away_prob * 100:.1f}% vs {predicted_home_prob * 100:.1f}%"
        )
        
        # Save the updated model data immediately
        self.save_model_data()
    
    def update_model_performance(self, prediction: Dict):
        """Update model performance metrics"""
        if "model_performance" not in self.model_data:
            self.model_data["model_performance"] = {
                "total_games": 0,
                "correct_predictions": 0,
                "accuracy": 0.0,
                "recent_accuracy": 0.0
            }
        
        perf = self.model_data["model_performance"]
        perf["total_games"] += 1
        
        # Check if prediction was correct
        away_prob = prediction.get("predicted_away_win_prob", 0)
        home_prob = prediction.get("predicted_home_win_prob", 0)
        away_team = prediction.get("away_team")
        home_team = prediction.get("home_team")
        actual_side = self._normalize_outcome_side(prediction.get("actual_winner"), away_team, home_team)
        
        if actual_side == "away" and away_prob >= home_prob:
            perf["correct_predictions"] += 1
        elif actual_side == "home" and home_prob >= away_prob:
            perf["correct_predictions"] += 1
        
        perf["accuracy"] = perf["correct_predictions"] / perf["total_games"]
        
        # Calculate recent accuracy (last 30 games with actual results)
        # Get all games with actual winners, then take the last 30
        all_completed_games = [p for p in self.model_data["predictions"] if p.get("actual_winner")]
        recent_games = all_completed_games[-30:] if len(all_completed_games) >= 30 else all_completed_games
        
        # Only calculate recent accuracy if we have enough completed games
        if len(recent_games) >= 5:
            recent_correct = 0
            for p in recent_games:
                away_p = p.get("predicted_away_win_prob", 0)
                home_p = p.get("predicted_home_win_prob", 0)
                winner_side = self._normalize_outcome_side(
                    p.get("actual_winner"), p.get("away_team"), p.get("home_team")
                )
                
                # Skip 50/50 predictions (placeholder predictions)
                if abs(away_p - home_p) < 0.01:  # Skip if difference is less than 1%
                    continue
                
                if winner_side == "away" and away_p >= home_p:
                    recent_correct += 1
                elif winner_side == "home" and home_p >= away_p:
                    recent_correct += 1
            
            # Only update if we have valid predictions
            valid_recent_games = [p for p in recent_games if abs(p.get("predicted_away_win_prob", 0) - p.get("predicted_home_win_prob", 0)) >= 0.01]
            if len(valid_recent_games) >= 3:
                perf["recent_accuracy"] = recent_correct / len(valid_recent_games)
            else:
                perf["recent_accuracy"] = perf["accuracy"]
        else:
            perf["recent_accuracy"] = perf["accuracy"]
    
    def update_team_stats(self, prediction: Dict):
        """Update team statistics with actual game data"""
        away_team = prediction["away_team"].upper()
        home_team = prediction["home_team"].upper()
        date = prediction["date"]
        
        # Get actual scores
        away_score = prediction.get("actual_away_score", 0)
        home_score = prediction.get("actual_home_score", 0)
        
        # Initialize team stats if needed with comprehensive metrics
        # Match ALL metrics from team_report_generator.py aggregate_team_stats
        def create_venue_data():
            return {
                "games": [],
                # Goals and shots (for/against)
                "goals": [], "goals_for": [], "goals_against": [],
                "shots": [], "shots_for": [], "shots_against": [],
                # Expected goals and high-danger chances (for/against)
                "xg": [], "xG_for": [], "xG_against": [],
                "hdc": [], "hdc_for": [], "hdc_against": [],
                # Game score
                "gs": [],
                # Opponent metrics (for compatibility)
                "opp_xg": [], "opp_goals": [],
                # Goalie
                "last_goalie": None,
                "opponents": [],
                # Advanced stats (match team_report_generator naming exactly)
                "corsi_pct": [], "pp_pct": [], "fo_pct": [],  # Team report uses pp_pct and fo_pct
                "power_play_pct": [], "penalty_kill_pct": [], "faceoff_pct": [],  # Keep for compatibility
                # Power play details (separate from percentage)
                "pp_goals": [], "pp_attempts": [],
                # Faceoff details (separate from percentage)
                "faceoff_wins": [], "faceoff_total": [],
                # Physical play (match team_report_generator naming)
                "hits": [], "blocks": [], "giveaways": [], "takeaways": [], "pim": [],
                "blocked_shots": [], "penalty_minutes": [],  # Keep for compatibility
                # Advanced movement and zone metrics
                "lateral": [], "longitudinal": [],
                "nzt": [], "nztsa": [], "ozs": [], "nzs": [], "dzs": [],
                "fc": [], "rush": [],
                # Clutch indicators (detailed)
                "clutch_score": [],
                "third_period_goals": [],
                "one_goal_game": [],  # Boolean per game
                "scored_first": [],  # Boolean per game
                "opponent_scored_first": [],  # Boolean per game
                # Period-by-period metrics (arrays of [p1, p2, p3] per game)
                "period_shots": [],  # [[p1_shots, p2_shots, p3_shots], ...]
                "period_corsi_pct": [],  # [[p1_corsi, p2_corsi, p3_corsi], ...]
                "period_pp_goals": [],  # [[p1_pp_goals, p2_pp_goals, p3_pp_goals], ...]
                "period_pp_attempts": [],  # [[p1_pp_attempts, p2_pp_attempts, p3_pp_attempts], ...]
                "period_pim": [],  # [[p1_pim, p2_pim, p3_pim], ...]
                "period_hits": [],  # [[p1_hits, p2_hits, p3_hits], ...]
                "period_fo_pct": [],  # [[p1_fo, p2_fo, p3_fo], ...]
                "period_blocks": [],  # [[p1_blocks, p2_blocks, p3_blocks], ...]
                "period_giveaways": [],  # [[p1_gv, p2_gv, p3_gv], ...]
                "period_takeaways": [],  # [[p1_tk, p2_tk, p3_tk], ...]
                "period_gs": [],  # [[p1_gs, p2_gs, p3_gs], ...]
                "period_xg": [],  # [[p1_xg, p2_xg, p3_xg], ...]
                "period_nzt": [],  # [[p1_nzt, p2_nzt, p3_nzt], ...]
                "period_nztsa": [],  # [[p1_nztsa, p2_nztsa, p3_nztsa], ...]
                "period_ozs": [],  # [[p1_ozs, p2_ozs, p3_ozs], ...]
                "period_nzs": [],  # [[p1_nzs, p2_nzs, p3_nzs], ...]
                "period_dzs": [],  # [[p1_dzs, p2_dzs, p3_dzs], ...]
                "period_fc": [],  # [[p1_fc, p2_fc, p3_fc], ...]
                "period_rush": []  # [[p1_rush, p2_rush, p3_rush], ...]
            }
        
        if away_team not in self.team_stats:
            self.team_stats[away_team] = {"home": create_venue_data(), "away": create_venue_data()}
        
        if home_team not in self.team_stats:
            self.team_stats[home_team] = {"home": create_venue_data(), "away": create_venue_data()}
        
        # Get metrics from the prediction
        metrics = prediction.get("metrics_used", {})
        
        # Update away team stats with comprehensive metrics
        away_data = self.team_stats[away_team]["away"]
        away_data["games"].append(date)
        
        # Goals (for/against)
        away_data["goals"].append(away_score)
        away_data["goals_for"].append(away_score)
        away_data["goals_against"].append(home_score)
        
        # Shots (for/against)
        away_shots = metrics.get("away_shots", 0)
        home_shots = metrics.get("home_shots", 0)
        away_data["shots"].append(away_shots)
        away_data["shots_for"].append(away_shots)
        away_data["shots_against"].append(home_shots)
        
        # Expected goals (for/against)
        away_xg = metrics.get("away_xg", 0.0)
        home_xg = metrics.get("home_xg", 0.0)
        away_data["xg"].append(away_xg)
        away_data["xG_for"].append(away_xg)
        away_data["xG_against"].append(home_xg)
        away_data["opp_xg"].append(home_xg)  # For compatibility
        
        # High-danger chances (for/against)
        away_hdc = metrics.get("away_hdc", 0)
        home_hdc = metrics.get("home_hdc", 0)
        away_data["hdc"].append(away_hdc)
        away_data["hdc_for"].append(away_hdc)
        away_data["hdc_against"].append(home_hdc)
        
        # Game score
        away_data["gs"].append(metrics.get("away_gs", 0.0))
        
        # Opponent metrics (for compatibility)
        away_data["opp_goals"].append(home_score)
        away_data["opponents"].append(home_team)
        if metrics.get("away_goalie"):
            away_data["last_goalie"] = metrics.get("away_goalie")
        away_data["corsi_pct"].append(metrics.get("away_corsi_pct", 50.0))
        
        # Power play (store both naming conventions)
        away_pp_pct = metrics.get("away_power_play_pct", 0.0)
        away_data["power_play_pct"].append(away_pp_pct)
        away_data["pp_pct"].append(away_pp_pct)  # Team report naming
        away_data["penalty_kill_pct"].append(metrics.get("away_penalty_kill_pct", 80.0))
        
        # Faceoff (store both naming conventions)
        away_fo_pct = metrics.get("away_faceoff_pct", 50.0)
        away_data["faceoff_pct"].append(away_fo_pct)
        away_data["fo_pct"].append(away_fo_pct)  # Team report naming
        
        # Power play details
        away_data["pp_goals"].append(metrics.get("away_pp_goals", 0))
        away_data["pp_attempts"].append(metrics.get("away_pp_attempts", 0))
        
        # Faceoff details
        away_data["faceoff_wins"].append(metrics.get("away_faceoff_wins", 0))
        away_data["faceoff_total"].append(metrics.get("away_faceoff_total", 0))
        
        # Physical play (store both naming conventions)
        away_hits = metrics.get("away_hits", 0)
        away_blocks = metrics.get("away_blocked_shots", 0)
        away_pim = metrics.get("away_penalty_minutes", 0)
        
        away_data["hits"].append(away_hits)
        away_data["blocked_shots"].append(away_blocks)
        away_data["blocks"].append(away_blocks)  # Team report naming
        away_data["giveaways"].append(metrics.get("away_giveaways", 0))
        away_data["takeaways"].append(metrics.get("away_takeaways", 0))
        away_data["penalty_minutes"].append(away_pim)
        away_data["pim"].append(away_pim)  # Team report naming
        
        # Advanced movement metrics
        away_data["lateral"].append(metrics.get("away_lateral", 0.0))
        away_data["longitudinal"].append(metrics.get("away_longitudinal", 0.0))
        
        # Zone start metrics
        away_data["nzt"].append(metrics.get("away_nzt", 0))
        away_data["nztsa"].append(metrics.get("away_nztsa", 0))
        away_data["ozs"].append(metrics.get("away_ozs", 0))
        away_data["nzs"].append(metrics.get("away_nzs", 0))
        away_data["dzs"].append(metrics.get("away_dzs", 0))
        
        # Shot type metrics
        away_data["fc"].append(metrics.get("away_fc", 0))
        away_data["rush"].append(metrics.get("away_rush", 0))
        
        # Clutch score and detailed clutch metrics
        clutch_score = self._calculate_clutch_score(prediction, "away")
        away_data["clutch_score"].append(clutch_score)
        away_data["third_period_goals"].append(metrics.get("away_third_period_goals", 0))
        away_data["one_goal_game"].append(metrics.get("away_one_goal_game", False))
        away_data["scored_first"].append(metrics.get("away_scored_first", False))
        away_data["opponent_scored_first"].append(metrics.get("away_opponent_scored_first", False))
        
        # Period-by-period metrics
        away_data["period_shots"].append(metrics.get("away_period_shots", [0, 0, 0]))
        away_data["period_corsi_pct"].append(metrics.get("away_period_corsi_pct", [50.0, 50.0, 50.0]))
        away_data["period_pp_goals"].append(metrics.get("away_period_pp_goals", [0, 0, 0]))
        away_data["period_pp_attempts"].append(metrics.get("away_period_pp_attempts", [0, 0, 0]))
        away_data["period_pim"].append(metrics.get("away_period_pim", [0, 0, 0]))
        away_data["period_hits"].append(metrics.get("away_period_hits", [0, 0, 0]))
        away_data["period_fo_pct"].append(metrics.get("away_period_fo_pct", [50.0, 50.0, 50.0]))
        away_data["period_blocks"].append(metrics.get("away_period_blocks", [0, 0, 0]))
        away_data["period_giveaways"].append(metrics.get("away_period_giveaways", [0, 0, 0]))
        away_data["period_takeaways"].append(metrics.get("away_period_takeaways", [0, 0, 0]))
        away_data["period_gs"].append(metrics.get("away_period_gs", [0.0, 0.0, 0.0]))
        away_data["period_xg"].append(metrics.get("away_period_xg", [0.0, 0.0, 0.0]))
        away_data["period_nzt"].append(metrics.get("away_period_nzt", [0, 0, 0]))
        away_data["period_nztsa"].append(metrics.get("away_period_nztsa", [0, 0, 0]))
        away_data["period_ozs"].append(metrics.get("away_period_ozs", [0, 0, 0]))
        away_data["period_nzs"].append(metrics.get("away_period_nzs", [0, 0, 0]))
        away_data["period_dzs"].append(metrics.get("away_period_dzs", [0, 0, 0]))
        away_data["period_fc"].append(metrics.get("away_period_fc", [0, 0, 0]))
        away_data["period_rush"].append(metrics.get("away_period_rush", [0, 0, 0]))
        
        # Update home team stats with comprehensive metrics
        home_data = self.team_stats[home_team]["home"]
        home_data["games"].append(date)
        
        # Goals (for/against)
        home_data["goals"].append(home_score)
        home_data["goals_for"].append(home_score)
        home_data["goals_against"].append(away_score)
        
        # Shots (for/against)
        home_shots = metrics.get("home_shots", 0)
        away_shots = metrics.get("away_shots", 0)
        home_data["shots"].append(home_shots)
        home_data["shots_for"].append(home_shots)
        home_data["shots_against"].append(away_shots)
        
        # Expected goals (for/against)
        home_xg = metrics.get("home_xg", 0.0)
        away_xg = metrics.get("away_xg", 0.0)
        home_data["xg"].append(home_xg)
        home_data["xG_for"].append(home_xg)
        home_data["xG_against"].append(away_xg)
        home_data["opp_xg"].append(float(away_xg) if away_xg is not None else 0.0)  # For compatibility
        
        # High-danger chances (for/against)
        home_hdc = metrics.get("home_hdc", 0)
        away_hdc = metrics.get("away_hdc", 0)
        home_data["hdc"].append(home_hdc)
        home_data["hdc_for"].append(home_hdc)
        home_data["hdc_against"].append(away_hdc)
        
        # Game score
        home_data["gs"].append(metrics.get("home_gs", 0.0))
        
        # Opponent metrics (for compatibility)
        home_data["opp_goals"].append(float(away_score) if away_score is not None else 0.0)
        home_data["opponents"].append(away_team)
        if metrics.get("home_goalie"):
            home_data["last_goalie"] = metrics.get("home_goalie")
        home_data["corsi_pct"].append(metrics.get("home_corsi_pct", 50.0))
        
        # Power play (store both naming conventions)
        home_pp_pct = metrics.get("home_power_play_pct", 0.0)
        home_data["power_play_pct"].append(home_pp_pct)
        home_data["pp_pct"].append(home_pp_pct)  # Team report naming
        home_data["penalty_kill_pct"].append(metrics.get("home_penalty_kill_pct", 80.0))
        
        # Faceoff (store both naming conventions)
        home_fo_pct = metrics.get("home_faceoff_pct", 50.0)
        home_data["faceoff_pct"].append(home_fo_pct)
        home_data["fo_pct"].append(home_fo_pct)  # Team report naming
        
        # Power play details
        home_data["pp_goals"].append(metrics.get("home_pp_goals", 0))
        home_data["pp_attempts"].append(metrics.get("home_pp_attempts", 0))
        
        # Faceoff details
        home_data["faceoff_wins"].append(metrics.get("home_faceoff_wins", 0))
        home_data["faceoff_total"].append(metrics.get("home_faceoff_total", 0))
        
        # Physical play (store both naming conventions)
        home_hits = metrics.get("home_hits", 0)
        home_blocks = metrics.get("home_blocked_shots", 0)
        home_pim = metrics.get("home_penalty_minutes", 0)
        
        home_data["hits"].append(home_hits)
        home_data["blocked_shots"].append(home_blocks)
        home_data["blocks"].append(home_blocks)  # Team report naming
        home_data["giveaways"].append(metrics.get("home_giveaways", 0))
        home_data["takeaways"].append(metrics.get("home_takeaways", 0))
        home_data["penalty_minutes"].append(home_pim)
        home_data["pim"].append(home_pim)  # Team report naming
        
        # Advanced movement metrics
        home_data["lateral"].append(metrics.get("home_lateral", 0.0))
        home_data["longitudinal"].append(metrics.get("home_longitudinal", 0.0))
        
        # Zone start metrics
        home_data["nzt"].append(metrics.get("home_nzt", 0))
        home_data["nztsa"].append(metrics.get("home_nztsa", 0))
        home_data["ozs"].append(metrics.get("home_ozs", 0))
        home_data["nzs"].append(metrics.get("home_nzs", 0))
        home_data["dzs"].append(metrics.get("home_dzs", 0))
        
        # Shot type metrics
        home_data["fc"].append(metrics.get("home_fc", 0))
        home_data["rush"].append(metrics.get("home_rush", 0))
        
        # Clutch score and detailed clutch metrics
        clutch_score = self._calculate_clutch_score(prediction, "home")
        home_data["clutch_score"].append(clutch_score)
        home_data["third_period_goals"].append(metrics.get("home_third_period_goals", 0))
        home_data["one_goal_game"].append(metrics.get("home_one_goal_game", False))
        home_data["scored_first"].append(metrics.get("home_scored_first", False))
        home_data["opponent_scored_first"].append(metrics.get("home_opponent_scored_first", False))
        
        # Period-by-period metrics
        home_data["period_shots"].append(metrics.get("home_period_shots", [0, 0, 0]))
        home_data["period_corsi_pct"].append(metrics.get("home_period_corsi_pct", [50.0, 50.0, 50.0]))
        home_data["period_pp_goals"].append(metrics.get("home_period_pp_goals", [0, 0, 0]))
        home_data["period_pp_attempts"].append(metrics.get("home_period_pp_attempts", [0, 0, 0]))
        home_data["period_pim"].append(metrics.get("home_period_pim", [0, 0, 0]))
        home_data["period_hits"].append(metrics.get("home_period_hits", [0, 0, 0]))
        home_data["period_fo_pct"].append(metrics.get("home_period_fo_pct", [50.0, 50.0, 50.0]))
        home_data["period_blocks"].append(metrics.get("home_period_blocks", [0, 0, 0]))
        home_data["period_giveaways"].append(metrics.get("home_period_giveaways", [0, 0, 0]))
        home_data["period_takeaways"].append(metrics.get("home_period_takeaways", [0, 0, 0]))
        home_data["period_gs"].append(metrics.get("home_period_gs", [0.0, 0.0, 0.0]))
        home_data["period_xg"].append(metrics.get("home_period_xg", [0.0, 0.0, 0.0]))
        home_data["period_nzt"].append(metrics.get("home_period_nzt", [0, 0, 0]))
        home_data["period_nztsa"].append(metrics.get("home_period_nztsa", [0, 0, 0]))
        home_data["period_ozs"].append(metrics.get("home_period_ozs", [0, 0, 0]))
        home_data["period_nzs"].append(metrics.get("home_period_nzs", [0, 0, 0]))
        home_data["period_dzs"].append(metrics.get("home_period_dzs", [0, 0, 0]))
        home_data["period_fc"].append(metrics.get("home_period_fc", [0, 0, 0]))
        home_data["period_rush"].append(metrics.get("home_period_rush", [0, 0, 0]))
        
        # Update per-goalie GSAX aggregates if goalie names provided
        try:
            if "goalie_stats" not in self.model_data:
                self.model_data["goalie_stats"] = {}
            # Away goalie faced home xG and allowed home goals
            away_goalie = metrics.get("away_goalie")
            if away_goalie:
                gs = self.model_data["goalie_stats"].setdefault(away_goalie, {"games": 0, "xga_sum": 0.0, "ga_sum": 0.0})
                gs["games"] += 1
                gs["xga_sum"] += float(metrics.get("home_xg", 0.0))
                gs["ga_sum"] += float(home_score)
            # Home goalie faced away xG and allowed away goals
            home_goalie = metrics.get("home_goalie")
            if home_goalie:
                gs = self.model_data["goalie_stats"].setdefault(home_goalie, {"games": 0, "xga_sum": 0.0, "ga_sum": 0.0})
                gs["games"] += 1
                gs["xga_sum"] += float(metrics.get("away_xg", 0.0))
                gs["ga_sum"] += float(away_score)
        except Exception:
            pass

        # Update team-level last game dates
        try:
            tld = self.model_data.setdefault("team_last_game", {})
            tld[away_team] = date
            tld[home_team] = date
        except Exception:
            pass
    
    def _calculate_clutch_score(self, prediction: Dict, team_side: str) -> float:
        """Calculate clutch score based on game context (comebacks, one-goal games, etc.)
        
        Clutch score factors:
        - Comeback wins (trailing after 2 periods)
        - One-goal game wins
        - Scoring first and winning
        - Opponent scoring first but still winning
        - Third period goals
        
        Returns a score from 0.0 to 1.0 where higher = more clutch performance
        """
        try:
            away_team = prediction.get("away_team", "")
            home_team = prediction.get("home_team", "")
            actual_winner = prediction.get("actual_winner", "")
            away_score = prediction.get("actual_away_score", 0) or 0
            home_score = prediction.get("actual_home_score", 0) or 0
            
            # Determine if this team won
            team_won = False
            if team_side == "away" and actual_winner == "away":
                team_won = True
            elif team_side == "home" and actual_winner == "home":
                team_won = True
            
            if not team_won:
                return 0.0  # No clutch points for losses
            
            score = 0.0
            
            # One-goal game win (+0.3)
            if abs(away_score - home_score) == 1:
                score += 0.3
            
            # Comeback win (would need period scores - simplified for now)
            # If we have period data, check if trailing after 2 periods
            # For now, assume close games are more clutch
            if abs(away_score - home_score) <= 2:
                score += 0.2
            
            # Scoring first and winning (+0.2)
            # Would need first goal data - simplified
            score += 0.1  # Placeholder
            
            # Third period performance (+0.2)
            # Would need period-by-period data
            score += 0.1  # Placeholder
            
            return min(1.0, score)
        except Exception:
            return 0.0
        
        # Keep only last 20 games to prevent memory bloat
        all_metric_keys = [
            "games", 
            "goals", "goals_for", "goals_against",
            "shots", "shots_for", "shots_against",
            "xg", "xG_for", "xG_against", "opp_xg",
            "hdc", "hdc_for", "hdc_against",
            "gs",
            "corsi_pct", "power_play_pct", "pp_pct", "penalty_kill_pct", "faceoff_pct", "fo_pct",
            "pp_goals", "pp_attempts",
            "faceoff_wins", "faceoff_total",
            "hits", "blocks", "blocked_shots", "giveaways", "takeaways", "pim", "penalty_minutes",
            "lateral", "longitudinal",
            "nzt", "nztsa", "ozs", "nzs", "dzs",
            "fc", "rush",
            "clutch_score", "third_period_goals", "one_goal_game",
            "scored_first", "opponent_scored_first",
            "period_shots", "period_corsi_pct", "period_pp_goals", "period_pp_attempts",
            "period_pim", "period_hits", "period_fo_pct", "period_blocks",
            "period_giveaways", "period_takeaways", "period_gs", "period_xg",
            "period_nzt", "period_nztsa", "period_ozs", "period_nzs", "period_dzs",
            "period_fc", "period_rush"
        ]
        for team in [away_team, home_team]:
            for venue in ["home", "away"]:
                for key in all_metric_keys:
                    if len(self.team_stats[team][venue][key]) > 20:
                        self.team_stats[team][venue][key] = self.team_stats[team][venue][key][-20:]
    
    def run_daily_update(self):
        """Run daily model update with improved learning"""
        logger.info("Running improved daily model update...")
        
        # Get recent predictions for learning
        recent_predictions = [p for p in self.model_data["predictions"][-10:] if p.get("actual_winner")]
        
        if len(recent_predictions) < self.min_games_for_update:
            logger.info(f"Not enough recent games for update ({len(recent_predictions)} < {self.min_games_for_update})")
            return
        
        # Calculate weight updates based on recent performance
        weight_updates = self._calculate_weight_updates(recent_predictions)
        
        # Apply updates with momentum
        current_weights = self.model_data["model_weights"]
        momentum = self.model_data.get("weight_momentum", {})
        
        for weight_name, update in weight_updates.items():
            if weight_name in current_weights:
                # Apply momentum
                momentum[weight_name] = self.momentum * momentum.get(weight_name, 0) + update
                
                # Update weight
                current_weights[weight_name] += momentum[weight_name]
                
                # Apply clipping
                current_weights[weight_name] = np.clip(
                    current_weights[weight_name], 
                    self.weight_clip_range[0], 
                    self.weight_clip_range[1]
                )
        
        # Normalize weights
        total = sum(current_weights.values())
        if total > 0:
            for key in current_weights:
                current_weights[key] /= total
                current_weights[key] = float(current_weights[key])
                momentum[key] = float(momentum.get(key, 0.0))
        
        # Update momentum
        self.model_data["weight_momentum"] = momentum
        self.model_data["last_updated"] = datetime.now().isoformat()
        
        logger.info(f"Updated model weights: {current_weights}")
        
        # Save updated model
        self.save_model_data()
        self.save_team_stats()
        
        # Recalculate performance from scratch to ensure accuracy
        self.recalculate_performance_from_scratch()
        
        # Return model performance for the GitHub workflow
        return self.get_model_performance()
    
    def _calculate_weight_updates(self, recent_predictions: List[Dict]) -> Dict:
        """Calculate deterministic weight updates based on recent performance signals."""
        weight_names = list(self.model_data["model_weights"].keys())
        if not recent_predictions:
            return {name: 0.0 for name in weight_names}
        
        perf = self.model_data.get("model_performance", {})
        baseline_accuracy = perf.get("accuracy", 0.0)
        
        correct = 0
        confidence_balance = 0.0
        correlation_correct = 0
        correlation_total = 0
        upset_count = 0
        monte_samples: List[float] = []
        for pred in recent_predictions:
            away_prob = pred.get("predicted_away_win_prob", 0.5)
            home_prob = pred.get("predicted_home_win_prob", 0.5)
            predicted_side = pred.get("predicted_winner")
            if predicted_side not in ("away", "home"):
                predicted_side = "away" if away_prob > home_prob else "home"
            actual_side = self._normalize_outcome_side(
                pred.get("actual_winner"), pred.get("away_team"), pred.get("home_team")
            )
            confidence = pred.get("prediction_confidence")
            if confidence is None:
                confidence = max(away_prob, home_prob)
            if confidence > 1:
                confidence = confidence / 100.0
            confidence = max(0.0, min(1.0, confidence))
            
            if actual_side and predicted_side == actual_side:
                correct += 1
                confidence_balance += confidence
            else:
                confidence_balance -= confidence
            if pred.get("was_upset"):
                upset_count += 1
            corr_away = pred.get("correlation_away_prob")
            corr_home = pred.get("correlation_home_prob")
            if corr_away is not None and corr_home is not None and actual_side:
                correlation_total += 1
                corr_side = "away" if corr_away >= corr_home else "home"
                if corr_side == actual_side:
                    correlation_correct += 1
            if self.correlation_model:
                sensitivity = self._estimate_monte_carlo_signal(pred)
                if sensitivity:
                    monte_samples.append(sensitivity)
        
        total = len(recent_predictions)
        recent_accuracy = correct / total if total else baseline_accuracy
        accuracy_delta = recent_accuracy - baseline_accuracy
        confidence_signal = confidence_balance / total if total else 0.0
        correlation_accuracy = (correlation_correct / correlation_total) if correlation_total else baseline_accuracy
        correlation_delta = correlation_accuracy - baseline_accuracy
        upset_rate = upset_count / total if total else 0.0
        monte_signal = float(np.mean(monte_samples)) if monte_samples else 0.0
        
        current_weights = self.model_data["model_weights"]
        updates = {}
        for weight_name in weight_names:
            prior = DEFAULT_WEIGHT_PRIORS.get(weight_name, 0.05)
            current_value = current_weights.get(weight_name, prior)
            deviation_from_prior = current_value - prior
            
            performance_signal = (accuracy_delta * prior * 0.3) + (confidence_signal * prior * 0.1)
            correlation_signal = correlation_delta * prior * 0.25
            upset_signal = -upset_rate * prior * 0.2
            monte_carlo_signal = -monte_signal * prior * 0.15
            mean_reversion = -deviation_from_prior * 0.2
            
            updates[weight_name] = performance_signal + correlation_signal + upset_signal + monte_carlo_signal + mean_reversion
        
        return updates
    
    def recalculate_performance_from_scratch(self):
        """Recalculate model performance from all predictions (ensures accuracy after bulk updates)"""
        predictions = self.model_data.get("predictions", [])
        # Filter for completed games - check multiple possible formats
        completed = []
        for p in predictions:
            actual_winner = p.get("actual_winner")
            # Accept if actual_winner exists and is not None/empty
            if actual_winner and actual_winner not in ("", None):
                completed.append(p)
        
        total_games = len(completed)
        logger.info(f"Recalculating performance from {total_games} completed games (out of {len(predictions)} total predictions)")
        correct_predictions = 0
        
        for pred in completed:
            away_prob = pred.get("predicted_away_win_prob", 0)
            home_prob = pred.get("predicted_home_win_prob", 0)
            away_team = pred.get("away_team")
            home_team = pred.get("home_team")
            actual_side = self._normalize_outcome_side(pred.get("actual_winner"), away_team, home_team)
            predicted_side = pred.get("predicted_winner")
            if predicted_side not in ("away", "home"):
                predicted_side = "away" if away_prob > home_prob else "home"
            
            if actual_side and predicted_side == actual_side:
                if actual_side == "away" and away_prob >= home_prob:
                    correct_predictions += 1
                elif actual_side == "home" and home_prob >= away_prob:
                    correct_predictions += 1
        
        accuracy = correct_predictions / total_games if total_games > 0 else 0.0
        
        # Calculate recent accuracy (last 30 completed games)
        recent_games = [p for p in completed if abs(p.get("predicted_away_win_prob", 0) - p.get("predicted_home_win_prob", 0)) >= 0.01]
        recent_games = recent_games[-30:] if len(recent_games) > 30 else recent_games
        recent_correct = 0
        for pred in recent_games:
            away_prob = pred.get("predicted_away_win_prob", 0)
            home_prob = pred.get("predicted_home_win_prob", 0)
            away_team = pred.get("away_team")
            home_team = pred.get("home_team")
            actual_side = self._normalize_outcome_side(pred.get("actual_winner"), away_team, home_team)
            
            if actual_side == "away" and away_prob >= home_prob:
                    recent_correct += 1
            elif actual_side == "home" and home_prob >= away_prob:
                    recent_correct += 1
        
        recent_accuracy = recent_correct / len(recent_games) if len(recent_games) >= 3 else accuracy
        
        # Update stored performance
        if "model_performance" not in self.model_data:
            self.model_data["model_performance"] = {}
        self.model_data["model_performance"].update({
            "total_games": total_games,
            "correct_predictions": correct_predictions,
            "accuracy": accuracy,
            "recent_accuracy": recent_accuracy
        })
        updated_samples = self.update_calibration_model()
        if updated_samples:
            logger.info(f"Updated calibration model with {updated_samples} samples")
        self.save_model_data()
    
    def get_model_performance(self) -> Dict:
        """Get current model performance"""
        return self.model_data.get("model_performance", {
            "total_games": 0,
            "correct_predictions": 0,
            "accuracy": 0.0,
            "recent_accuracy": 0.0
        })
    
    def analyze_model_performance(self) -> Dict:
        """Analyze model performance by team and other metrics"""
        predictions = self.model_data.get("predictions", [])
        
        # Calculate team accuracy
        team_accuracy: Dict[str, float] = {}
        team_games: Dict[str, int] = {}
        # First-goal impact stats (home/away split)
        first_goal_stats: Dict[str, Dict[str, Dict[str, float]]] = {}
        # Structure:
        # first_goal_stats[TEAM][VENUE] = {
        #   "games": int,
        #   "scored_first": int,
        #   "wins_scoring_first": int,
        #   "wins_conceding_first": int,
        #   "games_scoring_first": int,
        #   "games_conceding_first": int,
        # }
        
        def _venue_bucket(team: str, side: str) -> str:
            # For now, we treat side as venue: 'home' or 'away'
            return "home" if side == "home" else "away"
        
        for pred in predictions:
            if not pred.get("actual_winner"):
                continue
            
            away_team = pred.get("away_team")
            home_team = pred.get("home_team")
            predicted_side = self._normalize_outcome_side(pred.get("predicted_winner"), away_team, home_team)
            actual_side = self._normalize_outcome_side(pred.get("actual_winner"), away_team, home_team)
            
            # Count games for each team (overall)
            if away_team:
                team_games[away_team] = team_games.get(away_team, 0) + 1
            if home_team:
                team_games[home_team] = team_games.get(home_team, 0) + 1
            
            # Count correct predictions for each team
            predicted_team = self._side_to_team(predicted_side, away_team, home_team)
            actual_team = self._side_to_team(actual_side, away_team, home_team)
            if predicted_team and actual_team and predicted_team == actual_team:
                team_accuracy[actual_team] = team_accuracy.get(actual_team, 0) + 1

            # --- First-goal historical stats (per team, by venue) ---
            metrics = pred.get("metrics_used") or {}
            away_scored_first = bool(metrics.get("away_scored_first"))
            home_scored_first = bool(metrics.get("home_scored_first"))
            
            # Away team perspective
            if away_team:
                venue = _venue_bucket(away_team, "away")
                team_entry = first_goal_stats.setdefault(away_team, {}).setdefault(venue, {
                    "games": 0,
                    "scored_first": 0,
                    "wins_scoring_first": 0,
                    "wins_conceding_first": 0,
                    "games_scoring_first": 0,
                    "games_conceding_first": 0,
                })
                team_entry["games"] += 1
                if away_scored_first:
                    team_entry["scored_first"] += 1
                    team_entry["games_scoring_first"] += 1
                    if actual_side == "away":
                        team_entry["wins_scoring_first"] += 1
                else:
                    team_entry["games_conceding_first"] += 1
                    if actual_side == "away":
                        team_entry["wins_conceding_first"] += 1

            # Home team perspective
            if home_team:
                venue = _venue_bucket(home_team, "home")
                team_entry = first_goal_stats.setdefault(home_team, {}).setdefault(venue, {
                    "games": 0,
                    "scored_first": 0,
                    "wins_scoring_first": 0,
                    "wins_conceding_first": 0,
                    "games_scoring_first": 0,
                    "games_conceding_first": 0,
                })
                team_entry["games"] += 1
                if home_scored_first:
                    team_entry["scored_first"] += 1
                    team_entry["games_scoring_first"] += 1
                    if actual_side == "home":
                        team_entry["wins_scoring_first"] += 1
                else:
                    team_entry["games_conceding_first"] += 1
                    if actual_side == "home":
                        team_entry["wins_conceding_first"] += 1
        
        # Convert to percentages
        for team in team_accuracy:
            if team_games.get(team, 0) > 0:
                team_accuracy[team] = team_accuracy[team] / team_games[team]

        # Team bias estimation: average signed error between predicted home
        # win probability and actual home outcome (per team, per venue).
        team_bias: Dict[str, Dict[str, float]] = {}
        bias_counts: Dict[str, Dict[str, int]] = {}
        for pred in predictions:
            if not pred.get("actual_winner"):
                continue
            away_team = pred.get("away_team")
            home_team = pred.get("home_team")
            pa = pred.get("predicted_away_win_prob")
            ph = pred.get("predicted_home_win_prob")
            if pa is None or ph is None:
                continue
            total = pa + ph
            if total <= 0:
                continue
            pa /= total
            ph /= total
            winner = self._normalize_outcome_side(pred.get("actual_winner"), away_team, home_team)
            if winner not in ("away", "home"):
                continue
            # Home perspective
            if home_team:
                ven = "home"
                tb = team_bias.setdefault(home_team, {}).setdefault(ven, 0.0)
                bc = bias_counts.setdefault(home_team, {}).setdefault(ven, 0)
                # Error: predicted home prob minus actual outcome (1 if home wins else 0)
                y = 1.0 if winner == "home" else 0.0
                team_bias[home_team][ven] = tb + (ph - y)
                bias_counts[home_team][ven] = bc + 1
            # Away perspective
            if away_team:
                ven = "away"
                tb = team_bias.setdefault(away_team, {}).setdefault(ven, 0.0)
                bc = bias_counts.setdefault(away_team, {}).setdefault(ven, 0)
                # For away, predicted away prob vs actual away outcome
                y = 1.0 if winner == "away" else 0.0
                team_bias[away_team][ven] = tb + (pa - y)
                bias_counts[away_team][ven] = bc + 1

        # Turn sums into average errors and lightly regularize (shrink) them
        max_bias = 0.08  # don't let correction exceed 8 percentage points
        for team, venues in team_bias.items():
            for ven, total_err in venues.items():
                cnt = max(1, bias_counts.get(team, {}).get(ven, 1))
                avg_err = total_err / cnt
                # Shrink toward zero so we don't overreact on small samples
                shrink = min(1.0, cnt / 50.0)
                corrected = avg_err * shrink
                # Clamp
                corrected = max(-max_bias, min(max_bias, corrected))
                team_bias[team][ven] = corrected

        # Derive first-goal rates and win rates per team/venue
        derived_first_goal_stats: Dict[str, Dict[str, Dict[str, float]]] = {}
        for team, venues in first_goal_stats.items():
            derived_first_goal_stats[team] = {}
            for venue, agg in venues.items():
                games = max(1, agg["games"])
                gf_games = max(1, agg["games_scoring_first"])  # avoid div by zero
                ga_games = max(1, agg["games_conceding_first"])
                scored_first_rate = agg["scored_first"] / games
                win_rate_scoring_first = agg["wins_scoring_first"] / gf_games
                win_rate_conceding_first = agg["wins_conceding_first"] / ga_games
                uplift = win_rate_scoring_first - win_rate_conceding_first
                derived_first_goal_stats[team][venue] = {
                    "games": games,
                    "scored_first_rate": scored_first_rate,
                    "win_rate_scoring_first": win_rate_scoring_first,
                    "win_rate_conceding_first": win_rate_conceding_first,
                    "first_goal_uplift": uplift,
                }

        # Persist first-goal stats and team bias into model data for reuse
        self.model_data["first_goal_stats"] = derived_first_goal_stats
        self.model_data["team_bias"] = team_bias
        
        return {
            "team_accuracy": team_accuracy,
            "team_games": team_games,
            "first_goal_stats": derived_first_goal_stats,
            "team_bias": team_bias,
            "total_predictions": len(predictions)
        }

    def run_automated_backtest(self, window: int = 60, save_report: bool = True) -> Dict:
        """Run an automated backtest over the most recent window of completed games."""
        completed = [p for p in self.model_data.get("predictions", []) if p.get("actual_winner_side")]
        if not completed:
            return {}
        subset = completed[-window:] if window and window > 0 and len(completed) >= window else completed
        total = len(subset)
        if total == 0:
            return {}

        correct = sum(1 for p in subset if p.get("actual_winner_side") == p.get("predicted_winner"))
        accuracy = correct / total

        brier_sum = 0.0
        log_loss_sum = 0.0
        high_risk_threshold = 0.55
        high_risk_total = 0
        high_risk_hits = 0
        upset_probs = []
        upset_labels = []
        for p in subset:
            away_prob = float(p.get("predicted_away_win_prob", 0.5))
            away_prob = max(0.0, min(1.0, away_prob))
            actual = 1.0 if p.get("actual_winner_side") == "away" else 0.0
            brier_sum += (away_prob - actual) ** 2
            epsilon = 1e-12
            log_loss_sum += -(actual * np.log(max(away_prob, epsilon)) + (1 - actual) * np.log(max(1 - away_prob, epsilon)))
            upset_prob = float(p.get("upset_probability", 0.0))
            upset_probs.append(upset_prob)
            upset_label = 0 if p.get("actual_winner_side") == p.get("predicted_winner") else 1
            upset_labels.append(upset_label)
            if upset_prob >= high_risk_threshold:
                high_risk_total += 1
                if upset_label == 1:
                    high_risk_hits += 1
        brier = brier_sum / total
        log_loss = log_loss_sum / total
        high_risk_precision = (high_risk_hits / high_risk_total) if high_risk_total else None
        high_risk_coverage = high_risk_total / total if total else None

        roc_auc = None
        try:
            from sklearn.metrics import roc_auc_score
            if len(set(upset_labels)) > 1:
                roc_auc = float(roc_auc_score(upset_labels, upset_probs))
        except Exception:
            roc_auc = None

        context_summary: Dict[str, Dict] = {}
        for p in subset:
            bucket = p.get("context_bucket") or "neutral"
            entry = context_summary.setdefault(bucket, {"total": 0, "correct": 0, "avg_upset_prob": []})
            entry["total"] += 1
            if p.get("actual_winner_side") == p.get("predicted_winner"):
                entry["correct"] += 1
            entry["avg_upset_prob"].append(float(p.get("upset_probability", 0.0)))
        for bucket, entry in context_summary.items():
            total_bucket = entry["total"]
            entry["accuracy"] = entry["correct"] / total_bucket if total_bucket else 0.0
            entry["upset_rate"] = 1.0 - entry["accuracy"]
            entry["avg_upset_prob"] = float(np.mean(entry["avg_upset_prob"])) if entry["avg_upset_prob"] else 0.0
            entry.pop("correct", None)

        report = {
            "generated_at": datetime.now().isoformat(),
            "window": window,
            "sample_size": total,
            "accuracy": accuracy,
            "upset_rate": 1.0 - accuracy,
            "brier": brier,
            "log_loss": log_loss,
            "mean_upset_probability": float(np.mean(upset_probs)) if upset_probs else 0.0,
            "high_risk_threshold": high_risk_threshold,
            "high_risk_precision": high_risk_precision,
            "high_risk_coverage": high_risk_coverage,
            "roc_auc": roc_auc,
            "context_summary": context_summary,
        }

        if save_report:
            reports = self.model_data.setdefault("backtest_reports", [])
            reports.append(report)
            self.model_data["backtest_reports"] = reports[-20:]
            self.backtest_reports = self.model_data["backtest_reports"]
            # Also refresh and persist first-goal statistics and team bias when we run a backtest
            try:
                self.analyze_model_performance()
            except Exception as exc:
                logger.warning(f"Could not update first_goal_stats/team_bias during backtest: {exc}")
            self.save_model_data()

        return report
    
    def clean_duplicate_predictions(self):
        """Remove duplicate game entries from model data"""
        predictions = self.model_data.get('predictions', [])
        seen_game_ids = set()
        cleaned_predictions = []
        
        for pred in predictions:
            game_id = pred.get('game_id')
            if game_id and game_id not in seen_game_ids:
                cleaned_predictions.append(pred)
                seen_game_ids.add(game_id)
            elif not game_id:  # Keep predictions without game_id
                cleaned_predictions.append(pred)
        
        removed_count = len(predictions) - len(cleaned_predictions)
        self.model_data['predictions'] = cleaned_predictions
        
        logger.info(f"Removed {removed_count} duplicate predictions")
        return removed_count

    def backfill_from_predictions(self, max_games: int = 2000) -> int:
        """Backfill team_last_game and opp_xg/opp_goals from stored predictions.

        Safe: only appends when lengths match dates, avoids duplicate growth.
        Returns number of teams updated.
        """
        updated = 0
        preds = [p for p in self.model_data.get('predictions', []) if p.get('actual_winner')]
        if not preds:
            return 0
        # Use chronological order
        preds.sort(key=lambda p: p.get('date',''))
        for p in preds[-max_games:]:
            try:
                date = p.get('date')
                away = p.get('away_team','').upper()
                home = p.get('home_team','').upper()
                metrics = p.get('metrics_used', {}) or {}
                away_xg = float(metrics.get('away_xg', 0.0))
                home_xg = float(metrics.get('home_xg', 0.0))
                away_score = int(p.get('actual_away_score') or 0)
                home_score = int(p.get('actual_home_score') or 0)
                # Ensure structures
                if away not in self.team_stats:
                    self.team_stats[away] = {
                        "home": {"games": [], "opponents": [], "xg": [], "hdc": [], "shots": [], "goals": [], "gs": [], "opp_xg": [], "opp_goals": [], "last_goalie": None, "corsi_pct": [], "power_play_pct": [], "penalty_kill_pct": [], "faceoff_pct": [], "hits": [], "blocked_shots": [], "giveaways": [], "takeaways": [], "penalty_minutes": []},
                        "away": {"games": [], "opponents": [], "xg": [], "hdc": [], "shots": [], "goals": [], "gs": [], "opp_xg": [], "opp_goals": [], "last_goalie": None, "corsi_pct": [], "power_play_pct": [], "penalty_kill_pct": [], "faceoff_pct": [], "hits": [], "blocked_shots": [], "giveaways": [], "takeaways": [], "penalty_minutes": []}
                    }
                if home not in self.team_stats:
                    self.team_stats[home] = {
                        "home": {"games": [], "opponents": [], "xg": [], "hdc": [], "shots": [], "goals": [], "gs": [], "opp_xg": [], "opp_goals": [], "last_goalie": None, "corsi_pct": [], "power_play_pct": [], "penalty_kill_pct": [], "faceoff_pct": [], "hits": [], "blocked_shots": [], "giveaways": [], "takeaways": [], "penalty_minutes": []},
                        "away": {"games": [], "opponents": [], "xg": [], "hdc": [], "shots": [], "goals": [], "gs": [], "opp_xg": [], "opp_goals": [], "last_goalie": None, "corsi_pct": [], "power_play_pct": [], "penalty_kill_pct": [], "faceoff_pct": [], "hits": [], "blocked_shots": [], "giveaways": [], "takeaways": [], "penalty_minutes": []}
                    }
                # Append opp metrics to corresponding venues if date not present
                away_data = self.team_stats[away]['away']
                home_data = self.team_stats[home]['home']

                if date and date not in away_data['games']:
                    away_data['games'].append(date)
                    away_data['opponents'].append(home)
                    away_data['goals'].append(away_score)
                    away_data['xg'].append(float(metrics.get('away_xg', 0.0)))
                    away_data['hdc'].append(float(metrics.get('away_hdc', 0.0)))
                    away_data['shots'].append(float(metrics.get('away_shots', 0.0)))
                    away_data['gs'].append(float(metrics.get('away_gs', 0.0)))
                    away_data['opp_xg'].append(home_xg)
                    away_data['opp_goals'].append(home_score)
                    away_data['corsi_pct'].append(float(metrics.get('away_corsi_pct', 50.0)))
                    away_data['power_play_pct'].append(float(metrics.get('away_power_play_pct', 0.0)))
                    away_pk = metrics.get('away_penalty_kill_pct')
                    if away_pk is None:
                        away_pk = 100.0 - float(metrics.get('home_power_play_pct', 0.0))
                    away_data['penalty_kill_pct'].append(float(max(0.0, min(100.0, away_pk))))
                    away_data['faceoff_pct'].append(float(metrics.get('away_faceoff_pct', 50.0)))
                    away_data['hits'].append(float(metrics.get('away_hits', 0.0)))
                    away_data['blocked_shots'].append(float(metrics.get('away_blocked_shots', 0.0)))
                    away_data['giveaways'].append(float(metrics.get('away_giveaways', 0.0)))
                    away_data['takeaways'].append(float(metrics.get('away_takeaways', 0.0)))
                    away_data['penalty_minutes'].append(float(metrics.get('away_penalty_minutes', 0.0)))
                    if metrics.get('away_goalie'):
                        away_data['last_goalie'] = metrics.get('away_goalie')

                if date and date not in home_data['games']:
                    home_data['games'].append(date)
                    home_data['opponents'].append(away)
                    home_data['goals'].append(home_score)
                    home_data['xg'].append(float(metrics.get('home_xg', 0.0)))
                    home_data['hdc'].append(float(metrics.get('home_hdc', 0.0)))
                    home_data['shots'].append(float(metrics.get('home_shots', 0.0)))
                    home_data['gs'].append(float(metrics.get('home_gs', 0.0)))
                    home_data['opp_xg'].append(away_xg)
                    home_data['opp_goals'].append(away_score)
                    home_data['corsi_pct'].append(float(metrics.get('home_corsi_pct', 50.0)))
                    home_data['power_play_pct'].append(float(metrics.get('home_power_play_pct', 0.0)))
                    home_pk = metrics.get('home_penalty_kill_pct')
                    if home_pk is None:
                        home_pk = 100.0 - float(metrics.get('away_power_play_pct', 0.0))
                    home_data['penalty_kill_pct'].append(float(max(0.0, min(100.0, home_pk))))
                    home_data['faceoff_pct'].append(float(metrics.get('home_faceoff_pct', 50.0)))
                    home_data['hits'].append(float(metrics.get('home_hits', 0.0)))
                    home_data['blocked_shots'].append(float(metrics.get('home_blocked_shots', 0.0)))
                    home_data['giveaways'].append(float(metrics.get('home_giveaways', 0.0)))
                    home_data['takeaways'].append(float(metrics.get('home_takeaways', 0.0)))
                    home_data['penalty_minutes'].append(float(metrics.get('home_penalty_minutes', 0.0)))
                    if metrics.get('home_goalie'):
                        home_data['last_goalie'] = metrics.get('home_goalie')
                # Update last game dates
                tld = self.model_data.setdefault('team_last_game', {})
                tld[away] = date
                tld[home] = date
                updated += 1
            except Exception:
                continue
        self.save_model_data()
        self.save_team_stats()
        return updated

if __name__ == "__main__":
    # Test the improved model
    model = ImprovedSelfLearningModelV2()
    
    print("🏒 Improved Self-Learning Model V2")
    print("=" * 40)
    
    # Test prediction
    prediction = model.predict_game("TOR", "MTL")
    print(f"TOR @ MTL Prediction:")
    print(f"  Away (TOR): {prediction['away_prob']:.1f}%")
    print(f"  Home (MTL): {prediction['home_prob']:.1f}%")
    print(f"  Confidence: {prediction['prediction_confidence'] * 100:.1f}%")
    print(f"  Uncertainty: {prediction['uncertainty']:.2f}")
    
    # Show team performance data
    print(f"\nTeam Performance Data:")
    print(f"  TOR (Away): {prediction['away_perf']}")
    print(f"  MTL (Home): {prediction['home_perf']}")
    
    # Show current weights
    weights = model.get_current_weights()
    print(f"\nCurrent Weights:")
    for key, value in weights.items():
        print(f"  {key}: {value:.4f}")
