#!/usr/bin/env python3
import json
import random
from typing import Any, Dict, List, Optional

import numpy as np
from pathlib import Path
from score_prediction_model import ScorePredictionModel

# NHL playoff round index (simulate_2026_playoffs_master) -> round-depth model target
_ROUND_MODEL_TARGET = {
    1: "won_round_1",
    2: "won_round_2",
    3: "won_conference",
    4: "won_cup",
}

class PlayoffSeriesPredictor:
    """Best-of-7 series simulation based on 'DNA of Playoff Success' Audit weights."""
    
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent  # automated-post-game-reports/
        self._playoff_series_historical_5yr = self._load_playoff_series_historical_5yr(base_dir)
        self.model = ScorePredictionModel()
        self.metrics_path = base_dir / 'data' / 'team_advanced_metrics.json'
        self.edge_path = base_dir / 'data' / 'team_edge_profiles.json'
        self.historical_weights_path = base_dir / 'data' / 'ultimate_tactical_weights.json'
        self.cup_prior_path = base_dir / 'data' / 'cup_prior_current.json'
        self.round_models_path = base_dir / 'data' / 'reg_season_playoff_round_models_5yr.json'
        self.round_features_path = base_dir / 'data' / 'reg_season_team_features_current.json'
        self.advanced_metrics = {}
        self.edge_profiles = {}
        self.starters = {}
        self.cup_priors = {}
        self.round_models: Dict[str, Dict[str, Any]] = {}
        self.round_team_features: Dict[str, Dict[str, float]] = {}
        self.metric_norms = {}
        
        # City Coordinates (Lat, Lon) for fatigue/travel calculation
        self.TEAM_COORDS = {
            'ANA': (33.8078, -117.8765), 'BOS': (42.3662, -71.0621), 'BUF': (42.8750, -78.8764),
            'CGY': (51.0375, -114.0519), 'CAR': (35.8033, -78.7219), 'CHI': (41.8817, -87.6742),
            'COL': (39.7486, -105.0075), 'CBJ': (39.9692, -83.0061), 'DAL': (32.7905, -96.8103),
            'DET': (42.3411, -83.0553), 'EDM': (53.5469, -113.4901), 'FLA': (26.1583, -80.3256),
            'LAK': (34.0430, -118.2673), 'MIN': (44.9447, -93.1011), 'MTL': (45.4961, -73.5694),
            'NSH': (36.1592, -86.7785), 'NJD': (40.7335, -74.1711), 'NYI': (40.7135, -73.7158),
            'NYR': (40.7505, -73.9934), 'OTT': (45.2969, -75.9268), 'PHI': (39.9012, -75.1720),
            'PIT': (40.4395, -79.9893), 'SJS': (37.3329, -121.9017), 'SEA': (47.6221, -122.3540),
            'STL': (38.6268, -90.2026), 'TBL': (27.9427, -82.4492), 'TOR': (43.6435, -79.3791),
            'UTA': (40.7683, -111.9011), 'VAN': (49.2778, -123.1088), 'VGK': (36.1028, -115.1783),
            'WSH': (38.8982, -77.0209), 'WPG': (49.8926, -97.1437)
        }
        
        self._load_metrics()
        self._load_starters()
        self._load_edge_data()
        self._load_cup_priors()
        self._load_round_models()
        self._load_round_team_features()
        
        # FINAL 5-YEAR CHAMPIONSHIP WEIGHTS (Tactical Audit v2.2 2020-2026)
        # These weights prioritize offensive zone persistence and transition efficiency.
        self.PLAYOFF_WEIGHTS = {
            'rebound_gen_rate': 0.35,       # ↑ Increased for 2026 meta
            'avg_en_to_s': 0.25,           # ↑ Increased: entry quality is king
            'quick_strike_rate': 0.20,      
            'hd_pizzas_per_game': -0.15,    
            'rapid_reb_rate': 0.10,         
            'avg_ex_to_en': -0.05,          
            'pizzas_per_game': -0.12,     
            # Edge Tracking Weights (Phase 18 Integration)
            'edge_top_speed': 0.15,         
            'edge_burst_frequency': 0.12,   
            # Possession Starters (Phase 19 Integration)
            'ozone_faceoff_pct': 0.08,      # Clean wins drive immediate persistence
            'lateral_movement_forcing': 0.18, # NEW: High signal in 2026
        }
        self._load_historical_weights()
        self._compute_metric_norms()

    def _load_playoff_series_historical_5yr(self, base_dir: Path) -> Dict[str, Any]:
        """5 seasons of NHL playoff empiricals; built by scripts/build_playoff_series_historical_5yr.py."""
        p = base_dir / "data" / "playoff_series_historical_5yr.json"
        if not p.exists():
            return {}
        try:
            with open(p) as f:
                out = json.load(f)
            return out if isinstance(out, dict) else {}
        except Exception:
            return {}

    def _historical_poisson_mean_combined_goals(self) -> float:
        """Per-game combined goals: 5yr NHL playoff mean, clipped (not matchup-specific)."""
        h = self._playoff_series_historical_5yr
        pg = h.get("per_game_combined_goals") or {}
        ps = h.get("poisson_series_game") or {}
        m = float(pg.get("mean") or 5.5)
        lo = float(ps.get("poisson_mean_floor") or 1.75)
        hi = float(ps.get("poisson_mean_ceiling") or 8.25)
        return float(max(lo, min(m, hi)))

    def _historical_series_length_refs(self) -> tuple[float, float, float]:
        """Mean games per series, P(7), mean total goals per series from 5yr JSON (reference)."""
        h = self._playoff_series_historical_5yr
        sl = h.get("series_length_games") or {}
        st = h.get("series_total_goals") or {}
        mg = float(sl.get("mean") or 0.0)
        p7 = float(sl.get("prob_series_goes_seven") or 0.0)
        tgt = float(st.get("mean") or 0.0)
        return mg, p7, tgt

    def _load_historical_weights(self):
        """
        If available, prefer learned weights derived from historical playoff outcomes.
        File format expected:
          { "weights": { "avg_en_to_s": 0.21, ... }, "updated_at": "YYYY-MM-DD" }
        """
        if not self.historical_weights_path.exists():
            return
        try:
            with open(self.historical_weights_path) as f:
                w = json.load(f)
            learned = w.get("weights", {})
            if not isinstance(learned, dict) or not learned:
                return

            # Only update keys we already understand (avoid silently adding unknown features)
            for k, v in learned.items():
                if k in self.PLAYOFF_WEIGHTS and isinstance(v, (int, float)):
                    self.PLAYOFF_WEIGHTS[k] = float(v)
            print(f"🏆 Loaded learned historical playoff weights ({w.get('updated_at', 'unknown date')})")
        except Exception:
            return

    def _compute_metric_norms(self):
        """
        Compute league-wide mean/std for each weighted metric so we apply weights on a
        comparable scale (z-scores) instead of raw, differently-scaled values.
        """
        if not isinstance(self.advanced_metrics, dict) or not self.advanced_metrics:
            return

        norms = {}
        for metric in self.PLAYOFF_WEIGHTS.keys():
            if metric.startswith("edge"):
                continue
            vals = []
            for team, stats in self.advanced_metrics.items():
                if not isinstance(stats, dict):
                    continue
                v = stats.get(metric, None)
                if isinstance(v, (int, float)):
                    vals.append(float(v))
            if len(vals) >= 8:
                mean = float(np.mean(vals))
                std = float(np.std(vals))
                if std <= 1e-9:
                    std = 1.0
                norms[metric] = {"mean": mean, "std": std}

        # Edge metrics norms (optional)
        if isinstance(self.edge_profiles, dict) and self.edge_profiles:
            speed_vals = []
            burst_vals = []
            for team, edge in self.edge_profiles.items():
                if not isinstance(edge, dict):
                    continue
                s = edge.get("avg_top_speed")
                b = edge.get("avg_burst_frequency")
                if isinstance(s, (int, float)):
                    speed_vals.append(float(s))
                if isinstance(b, (int, float)):
                    burst_vals.append(float(b))
            if len(speed_vals) >= 8:
                norms["edge_avg_top_speed"] = {"mean": float(np.mean(speed_vals)), "std": float(np.std(speed_vals)) or 1.0}
            if len(burst_vals) >= 8:
                norms["edge_avg_burst_frequency"] = {"mean": float(np.mean(burst_vals)), "std": float(np.std(burst_vals)) or 1.0}

        self.metric_norms = norms

    def _load_metrics(self):
        if self.metrics_path.exists():
            with open(self.metrics_path) as f:
                data = json.load(f)
                self.advanced_metrics = data.get('teams', {})
    
    def _load_starters(self):
        """Identify the #1 goalie for each team based on games played in high-fidelity metrics."""
        if not self.metrics_path.exists():
            return
            
        with open(self.metrics_path) as f:
            data = json.load(f)
        
        goalie_data = data.get('goalies', {})
        team_starters = {} # team -> (name, games)
        
        for gid, gs in goalie_data.items():
            team = gs.get('team')
            name = gs.get('name')
            games = gs.get('games', 0)
            
            if not team or not name: continue
            
            if team not in team_starters or games > team_starters[team][1]:
                team_starters[team] = (name, games)
                
        self.starters = {t: n for t, (n, g) in team_starters.items()}
        print(f"🥅 Identified #1 starters for {len(self.starters)} teams for playoff simulation")

    def _load_edge_data(self):
        """Unify Edge tracking data from team_advanced_metrics.json."""
        for abbr, stats in self.advanced_metrics.items():
            # Extract high-fidelity tracking data from advanced metrics pool
            profile = {
                'avg_max_speed': stats.get('max_skating_speed', 21.0),
                'avg_burst_frequency': stats.get('skating_bursts_per_game', 0.5),
                'avg_shot_speed': stats.get('avg_shot_speed', 75.0),
                'puck_possession_dist': stats.get('puck_possession_dist', 1.0)
            }
            self.edge_profiles[abbr] = profile
        
        print(f"⛸️  Synchronized high-fidelity Edge tracking for {len(self.edge_profiles)} teams")

    def _load_cup_priors(self):
        """Load regular-season-derived Cup priors (optional)."""
        if not self.cup_prior_path.exists():
            return
        try:
            with open(self.cup_prior_path) as f:
                data = json.load(f)
            teams = data.get("teams", {})
            if isinstance(teams, dict):
                self.cup_priors = teams
                print(f"📌 Loaded Cup priors for {len(self.cup_priors)} teams (regular-season model)")
        except Exception:
            return

    def _load_round_models(self):
        """Load regular-season → playoff-depth logistic models (optional)."""
        if not self.round_models_path.exists():
            return
        try:
            with open(self.round_models_path) as f:
                data = json.load(f)
        except Exception:
            return
        targets = data.get("targets", {})
        if not isinstance(targets, dict):
            return
        for key, block in targets.items():
            if not isinstance(block, dict) or block.get("skipped"):
                continue
            pos = block.get("positives")
            neg = block.get("negatives")
            try:
                pos_i = int(pos)
                neg_i = int(neg)
            except (TypeError, ValueError):
                continue
            if pos_i + neg_i <= 0:
                continue
            logistic = block.get("logistic") or {}
            scaler = block.get("scaler") or {}
            coef = logistic.get("coef")
            mean = scaler.get("mean")
            scale = scaler.get("scale")
            if not isinstance(coef, dict) or not isinstance(mean, dict) or not isinstance(scale, dict):
                continue
            try:
                intercept = float(logistic.get("intercept", 0.0))
            except (TypeError, ValueError):
                continue
            self.round_models[key] = {
                "intercept": intercept,
                "coef": {str(k): float(v) for k, v in coef.items() if isinstance(v, (int, float))},
                "mean": {str(k): float(v) for k, v in mean.items() if isinstance(v, (int, float))},
                "scale": {str(k): float(v) for k, v in scale.items() if isinstance(v, (int, float))},
                "baseline": float(pos_i) / float(pos_i + neg_i),
            }
        if self.round_models:
            print(f"📊 Loaded {len(self.round_models)} regular-season → playoff round models")

    def _load_round_team_features(self):
        """Per-team feature vector for the current season (from Cup training export)."""
        if not self.round_features_path.exists():
            return
        try:
            with open(self.round_features_path) as f:
                data = json.load(f)
            teams = data.get("teams", {})
            if not isinstance(teams, dict):
                return
            for ab, feats in teams.items():
                if not isinstance(feats, dict):
                    continue
                k = str(ab).strip().upper()
                self.round_team_features[k] = {
                    str(fn): float(fv) for fn, fv in feats.items() if isinstance(fv, (int, float))
                }
            if self.round_team_features:
                print(f"📐 Loaded current-season feature rows for {len(self.round_team_features)} teams (round priors)")
        except Exception:
            return

    @staticmethod
    def _logit_delta_vs_baseline(p_model: float, baseline: float, strength: float = 0.03) -> float:
        p = max(1e-6, min(1.0 - 1e-6, float(p_model)))
        b = max(1e-6, min(1.0 - 1e-6, float(baseline)))
        return float(np.log(p / (1.0 - p)) - np.log(b / (1.0 - b))) * strength

    def _round_model_linear_logit(self, team_abbr: str, target: str) -> Optional[float]:
        m = self.round_models.get(target)
        if not m:
            return None
        feats = self.round_team_features.get(str(team_abbr).strip().upper())
        if not feats:
            return None
        total = float(m["intercept"])
        for fname, c in m["coef"].items():
            if abs(c) < 1e-15:
                continue
            raw = feats.get(fname)
            if raw is None:
                raw = 0.0
            mean = float(m["mean"].get(fname, 0.0))
            sc = float(m["scale"].get(fname, 1.0))
            if sc <= 1e-12:
                sc = 1.0
            z = (float(raw) - mean) / sc
            total += float(c) * z
        return total

    def get_team_playoff_modifier(self, team_abbr, playoff_round: Optional[int] = None):
        """
        Playoff Integrity modifier: tactical DNA (+ optional Cup / round-depth priors).

        ``playoff_round`` 1–4 selects which regular-season→playoff-depth model to blend
        (R1 … Cup). ``None`` skips round-depth priors (DNA + Cup only).
        """
        stats = self.advanced_metrics.get(team_abbr, {})
        edge = self.edge_profiles.get(team_abbr, {})

        modifier = 0.0
        if stats:
            # Tactical PBP Metrics
            for metric, weight in self.PLAYOFF_WEIGHTS.items():
                if metric.startswith('edge'): continue # Handle edge separately
                val = stats.get(metric, 0)
                if not isinstance(val, (int, float)):
                    continue
                val = float(val)
                # z-score normalize if we have league norms
                if metric in self.metric_norms:
                    mean = self.metric_norms[metric]["mean"]
                    std = self.metric_norms[metric]["std"]
                    val = (val - mean) / std
                modifier += (val * weight)

            # Edge Tracking Metrics
            speed = edge.get('avg_top_speed', None)
            burst = edge.get('avg_burst_frequency', None)
            if isinstance(speed, (int, float)):
                speed = float(speed)
                if "edge_avg_top_speed" in self.metric_norms:
                    n = self.metric_norms["edge_avg_top_speed"]
                    speed = (speed - n["mean"]) / n["std"]
                else:
                    speed = (speed - 21.5)
            else:
                speed = 0.0

            if isinstance(burst, (int, float)):
                burst = float(burst)
                if "edge_avg_burst_frequency" in self.metric_norms:
                    n = self.metric_norms["edge_avg_burst_frequency"]
                    burst = (burst - n["mean"]) / n["std"]
                else:
                    burst = (burst - 0.5)
            else:
                burst = 0.0

            speed_delta = speed * self.PLAYOFF_WEIGHTS['edge_top_speed']
            burst_delta = burst * self.PLAYOFF_WEIGHTS['edge_burst_frequency']

            modifier += speed_delta + burst_delta

        # Regular-season Cup prior (learned from last-5-years): keep this small.
        prior = None
        try:
            prior = float(self.cup_priors.get(team_abbr, {}).get("cup_prior_norm"))
        except Exception:
            prior = None
        if prior is not None and prior > 0:
            baseline = 1.0 / 32.0
            modifier += self._logit_delta_vs_baseline(prior, baseline, strength=0.03)

        # Regular-season → depth model for this playoff round (optional)
        if playoff_round is not None:
            target = _ROUND_MODEL_TARGET.get(int(playoff_round))
            if target and target in self.round_models:
                lin = self._round_model_linear_logit(team_abbr, target)
                if lin is not None:
                    p_depth = float(1.0 / (1.0 + np.exp(-lin)))
                    b_depth = float(self.round_models[target]["baseline"])
                    modifier += self._logit_delta_vs_baseline(p_depth, b_depth, strength=0.025)

        return modifier * 0.1

    def calculate_game_win_prob(self, away_team, home_team, away_wins: int = 0, home_wins: int = 0, playoff_round: Optional[int] = None):
        """Calculate the single-game win probability with playoff tuning."""
        # Identify starters
        away_goalie = self.starters.get(away_team)
        home_goalie = self.starters.get(home_team)
        
        # Phase 42: Unified Optimal Sovereignty
        # Pass is_playoff and series_status to ensure we use the same 
        # perfection-tier logic as the daily reports.
        series_status = None
        if away_wins > 0 or home_wins > 0:
            if away_wins > home_wins:
                series_status = f"{away_team} leads {away_wins}-{home_wins}"
            elif home_wins > away_wins:
                series_status = f"{home_team} leads {home_wins}-{away_wins}"
            else:
                series_status = f"Series tied {away_wins}-{home_wins}"

        # Use 1-indexed game numbers for seeding variety across series
        game_num = away_wins + home_wins + 1
        fake_game_id = 2025030000 + game_num # Deterministic seed for series
        
        res = self.model.predict_score(
            away_team, home_team, 
            away_goalie=away_goalie, 
            home_goalie=home_goalie,
            is_playoff=True,
            series_status=series_status,
            game_id=fake_game_id
        )
        away_prob = res['away_win_prob']
        
        # Apply Playoff Modifiers
        away_mod = self.get_team_playoff_modifier(away_team, playoff_round=playoff_round)
        home_mod = self.get_team_playoff_modifier(home_team, playoff_round=playoff_round)
        
        # 1. Goalie Hot Hand Modifier
        away_hot_hand = self._calculate_goalie_hot_hand(away_team)
        home_hot_hand = self._calculate_goalie_hot_hand(home_team)
        
        # 2. Goalie Cumulative Load (Fatigue from playing deep into series)
        games_in_series = away_wins + home_wins
        away_g_fatigue = self._calculate_goalie_fatigue(away_team, games_in_series)
        home_g_fatigue = self._calculate_goalie_fatigue(home_team, games_in_series)
        
        # 3. Series Fatigue (Travel) Modifier
        away_fatigue = self._calculate_series_fatigue(away_team, home_team, games_in_series, is_away=True)
        home_fatigue = self._calculate_series_fatigue(away_team, home_team, games_in_series, is_away=False)
        
        # 4. Elimination Game Modifier
        # (Handled by ScorePredictionModel Phase 41 +12% xG boost)
        away_elim_mod, home_elim_mod = 0.0, 0.0
        
        # 5. Phase 18 Lateral movement advantage
        lateral_adv = self._calculate_lateral_advantage(away_team, home_team)
        
        # 6. Home Ice Matchup Advantage (Last Change)
        # Home coach can match shutdown lines vs star lines. 
        # Only applies to home team, varies by defensive quality.
        home_matchup_adv = self._calculate_matchup_advantage(home_team, away_team)
        
        # 7. Special Teams Net Edge (PP + PK)
        st_edge = self._calculate_special_teams_edge(away_team, home_team)
        
        # 8. Shot Block Resilience
        away_blocks = self._calculate_shot_block_resilience(away_team)
        home_blocks = self._calculate_shot_block_resilience(home_team)
        
        # 9. Championship Pedigree
        away_pedigree = self._calculate_pedigree_modifier(away_team)
        home_pedigree = self._calculate_pedigree_modifier(home_team)
        
        # 10. Tactical Solving (Seriality)
        # If a team has won consecutive games, they may have 'solved' the opponent
        tactical_shift = self._calculate_tactical_solving(away_wins, home_wins)
        
        # 11. Playoff OT Conditioning
        away_cond = self._calculate_conditioning_boost(away_team)
        home_cond = self._calculate_conditioning_boost(home_team)
        
        # 12. NHL Edge: Transition & Skating Speed Edge (With Playoff Intensity)
        # Apply Playoff Intensity Multiplier and Series Fatigue Decay
        total_games_played = away_wins + home_wins
        fatigue_decay = max(0.95, 1.0 - (total_games_played * 0.008)) # -0.8% speed per game in series
        is_playoff = True # In this context, it's always a playoff game
        intensity_boost = 1.05 if is_playoff else 1.0 # +5% effort in playoffs
        
        away_speed = self._calculate_skating_edge(away_team, decay=fatigue_decay, intensity=intensity_boost)
        home_speed = self._calculate_skating_edge(home_team, decay=fatigue_decay, intensity=intensity_boost)
        
        # 13. NHL Edge: Puck Control Dominance
        away_puck = self._calculate_possession_edge(away_team, intensity=intensity_boost)
        home_puck = self._calculate_possession_edge(home_team, intensity=intensity_boost)
        
        # Combine all modifiers (net_shift)
        # Tactical DNA + Hot Hand + Fatigue + Elimination + Goalie Fatigue + Lateral + Matchup + ST + Blocks + Pedigree + Solving + OT + Speed + Puck
        net_shift = (away_mod - home_mod) + (away_hot_hand - home_hot_hand) + \
                    (home_fatigue - away_fatigue) + (away_elim_mod - home_elim_mod) + \
                    (home_g_fatigue - away_g_fatigue) + \
                    lateral_adv + home_matchup_adv + st_edge + \
                    (away_blocks - home_blocks) + (away_pedigree - home_pedigree) + \
                    tactical_shift + (away_cond - home_cond) + \
                    (away_speed - home_speed) + (away_puck - home_puck)
        
        final_away_prob = np.clip(away_prob + net_shift, 0.01, 0.99)
        return final_away_prob

    def _calculate_tactical_solving(self, away_wins: int, home_wins: int) -> float:
        """Slight boost for teams on a win streak in the series (System Solving)."""
        # We don't have game-by-game order in this simple (wins, wins) state, 
        # but we can assume a team with a 2-game lead (e.g. 2-0, 3-1) has tactical momentum.
        diff = away_wins - home_wins
        if diff >= 2: return 0.01 # Away solved home
        if diff <= -2: return -0.01 # Home solved away
        return 0.0

    def _calculate_conditioning_boost(self, team_abbr: str) -> float:
        """Aerobic conditioning boost (based on Edge Burst Frequency) for long Playoff OTs."""
        edge = self.edge_profiles.get(team_abbr, {})
        burst = edge.get('avg_burst_frequency', 0.5)
        # Top-tier conditioning (burst > 0.6) grants a small edge in the 5v5 playoff OT meta.
        if burst > 0.6: return 0.005
        return 0.0

    def _calculate_skating_edge(self, team_abbr: str, decay: float = 1.0, intensity: float = 1.0) -> float:
        """NHL Edge: Skating speed and transition efficiency with Playoff scaling."""
        edge = self.edge_profiles.get(team_abbr, {})
        speed = edge.get('avg_max_speed', 21.0) * decay
        bursts = edge.get('avg_burst_frequency', 0.5) * intensity
        # Reward teams with both high peak speed and high frequency
        if speed > 22.0 and bursts > 0.55: return 0.01
        if speed > 21.5: return 0.005
        return 0.0

    def _calculate_possession_edge(self, team_abbr: str, intensity: float = 1.0) -> float:
        """NHL Edge: Puck possession distance dominance with Playoff intensity."""
        edge = self.edge_profiles.get(team_abbr, {})
        dist = edge.get('puck_possession_dist', 1.0) * intensity
        # Scale: average distance is around 1.0-1.2 miles per game for a team
        if dist > 1.25: return 0.01 # Elite puck control
        if dist > 1.15: return 0.005
        return 0.0

    def _calculate_matchup_advantage(self, home_team: str, away_team: str) -> float:
        """Home team gets last change, allowing tactical line matching."""
        h_stats = self.advanced_metrics.get(home_team, {})
        # If home team has elite defensive suppressors (low shots against)
        # and away team is top-heavy, the home edge increases.
        h_suppression = h_stats.get('avg_ex_to_en', 0) # Entry suppression
        if h_suppression < -0.05: # Elite entry defense
            return 0.015 # Extra 1.5% for tactical matching
        return 0.005 # Baseline last-change edge

    def _calculate_special_teams_edge(self, away_team: str, home_team: str) -> float:
        """Net Special Teams (PP% + PK%) advantage."""
        # Pull from learned model averages
        a_avgs = self.model.team_averages.get(away_team, {}).get('combined', {})
        h_avgs = self.model.team_averages.get(home_team, {}).get('combined', {})
        
        a_net = a_avgs.get('power_play_pct', 20.0) + a_avgs.get('penalty_kill_pct', 80.0)
        h_net = h_avgs.get('power_play_pct', 20.0) + h_avgs.get('penalty_kill_pct', 80.0)
        
        # Reward teams with 'Net ST' over 105 (Playoff benchmark)
        shift = (a_net - h_net) * 0.001
        return np.clip(shift, -0.02, 0.02)

    def _calculate_shot_block_resilience(self, team_abbr: str) -> float:
        """Playoff teams that sacrifice bodies get a defensive resilience boost."""
        stats = self.advanced_metrics.get(team_abbr, {})
        # Use total_blocks / games if available
        blocks = stats.get('total_blocks', 0)
        games = stats.get('games', 1)
        bpg = blocks / games
        if bpg > 18.0: return 0.015 # Elite shot blocking
        if bpg > 15.0: return 0.005 # Above average
        return 0.0

    def _calculate_pedigree_modifier(self, team_abbr: str) -> float:
        """Experience boost for teams with recent Cup success (Pedigree)."""
        PEDIGREE = {
            'TBL': 0.01, # Multi-cup core
            'COL': 0.01, # 2022 Champ
            'VGK': 0.01, # 2023 Champ
            'FLA': 0.005, # Recent Finalist
        }
        return PEDIGREE.get(team_abbr, 0.0)

    def _calculate_goalie_fatigue(self, team_abbr: str, games_in_series: int) -> float:
        """Penalty for goalie playing heavy minutes deep in a series."""
        if games_in_series < 4: return 0.0
        # 1% penalty per game after Game 4
        return (games_in_series - 3) * 0.01

    def _calculate_goalie_hot_hand(self, team_abbr: str) -> float:
        """Calculate if a goalie is on a 'Hot Hand' streak (> .915 SV% last 3 games)."""
        # This would ideally pull from a per-game goalie SV% store
        # For now, we'll use a signal from advanced_metrics if 'recent_gsax' is present
        stats = self.advanced_metrics.get(team_abbr, {})
        recent_gsax = stats.get('recent_gsax_per_game', 0) # GSAx over last 3 games
        if recent_gsax > 1.5: return 0.04 # Major hot hand
        if recent_gsax > 0.5: return 0.02 # Moderate hot hand
        if recent_gsax < -1.0: return -0.03 # Cold hand
        return 0.0

    def _calculate_series_fatigue(self, away_team: str, home_team: str, games_played: int, is_away: bool) -> float:
        """Calculate travel fatigue based on distance between cities."""
        if away_team not in self.TEAM_COORDS or home_team not in self.TEAM_COORDS:
            return 0.0
            
        c1 = self.TEAM_COORDS[away_team]
        c2 = self.TEAM_COORDS[home_team]
        
        # Simple Euclidean distance as proxy for travel hours
        dist = np.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)
        
        # Cross-continent travel (dist > 25) incurs fatigue if many games played
        # Penalty is higher for the away team in Game 5 and Game 7
        fatigue = 0.0
        if dist > 25:
            if games_played >= 4: # Deep in series
                fatigue = 0.02
                if is_away: fatigue *= 1.5 # Extra penalty for visiting team
        
        return fatigue

    def _calculate_elimination_modifier(self, away_wins: int, home_wins: int) -> tuple[float, float]:
        """Apply 'Urgency' modifier for teams facing elimination."""
        away_mod = 0.0
        home_mod = 0.0
        
        # Facing elimination (Down 3-x)
        if away_wins == 3 and home_wins < 3:
            # Home team is desperate
            home_mod += 0.025 # Boosted for high-leverage
            if home_wins == 0: # Down 3-0 is harder (psychological)
                home_mod -= 0.01
            # Away team might be tight/pressured to close out
            away_mod -= 0.015
        elif home_wins == 3 and away_wins < 3:
            # Away team is desperate
            away_mod += 0.025
            if away_wins == 0:
                away_mod -= 0.01
            # Home team might be tight
            home_mod -= 0.015
            
        return away_mod, home_mod

    def _calculate_lateral_advantage(self, away_team: str, home_team: str) -> float:
        """Calculate advantage based on lateral movement forcing (Phase 18)."""
        a_stats = self.advanced_metrics.get(away_team, {})
        h_stats = self.advanced_metrics.get(home_team, {})
        
        a_lateral = a_stats.get('lateral_movement_forcing', 0)
        h_lateral = h_stats.get('lateral_movement_forcing', 0)
        
        # High lateral movement forcing = moving the goalie, creating better chances
        return (a_lateral - h_lateral) * 0.01

    @staticmethod
    def _projected_series_length_games_int(
        avg_games: float,
        away_wins: int,
        home_wins: int,
        max_additional_games: int,
    ) -> int:
        """Whole number of games in the series from this state; best-of-7 is 4–7 from 0–0."""
        g = int(round(avg_games))
        lo = max(1, 4 - max(away_wins, home_wins))
        hi = max_additional_games
        return max(lo, min(hi, g))

    def _simulate_series_numpy_batch(
        self,
        away: str,
        home: str,
        away_wins: int,
        home_wins: int,
        simulations: int,
        remaining_venues: list,
        playoff_round: Optional[int] = None,
    ) -> tuple[int, float, float, float]:
        """
        Dynamic probability simulation.
        Probabilities are recalculated in each step based on the current series score.
        """
        rng = np.random.default_rng()
        n = int(simulations)
        a_w = np.full(n, away_wins, dtype=np.int32)
        h_w = np.full(n, home_wins, dtype=np.int32)
        mu_combined = self._historical_poisson_mean_combined_goals()
        total_games = np.zeros(n, dtype=np.float64)
        total_goals = np.zeros(n, dtype=np.float64)

        # Map current game index to its place in full_venues (H-H-A-A-H-A-H)
        full_venues = ['home', 'home', 'away', 'away', 'home', 'away', 'home']
        
        for g_idx in range(away_wins + home_wins, 7):
            mask = (a_w < 4) & (h_w < 4)
            if not np.any(mask):
                break
            
            venue = full_venues[g_idx]
            
            # Recalculate probabilities for unique (a_w, h_w) states in the current batch
            # For simplicity in batching, we group by unique scorelines
            unique_scores = set(zip(a_w[mask], h_w[mask]))
            p_map = {}
            for aw, hw in unique_scores:
                # Probability depends on who is home/away in THIS game
                if venue == 'home':
                    p_map[(aw, hw)] = self.calculate_game_win_prob(away, home, aw, hw, playoff_round)
                else:
                    # 'away' venue in the series schedule means home_team is visiting away_team's arena
                    # So away_team is 'home' for this calculation
                    p_map[(aw, hw)] = 1.0 - self.calculate_game_win_prob(home, away, hw, aw, playoff_round)
            
            # Apply probabilities to batch
            p_vector = np.array([p_map[(aw, hw)] if (aw < 4 and hw < 4) else 0.5 for aw, hw in zip(a_w, h_w)])
            
            u = rng.random(n)
            away_win = u < p_vector
            inc_a = (mask & away_win).astype(np.int32)
            inc_h = (mask & ~away_win).astype(np.int32)
            a_w = a_w + inc_a
            h_w = h_w + inc_h
            total_games += mask.astype(np.float64)
            
            sampled = rng.poisson(mu_combined, size=n).astype(np.float64)
            total_goals += np.where(mask, sampled, 0.0)

        away_series_wins = int(np.sum(a_w == 4))
        total_games_completed = float(np.sum(total_games))
        total_series_goals_sum = float(np.sum(total_goals))
        prob_seven = float(np.mean(total_games + (away_wins + home_wins) == 7.0))
        return away_series_wins, total_games_completed, total_series_goals_sum, prob_seven

    def simulate_series(self, away, home, away_wins=0, home_wins=0, simulations=10000, playoff_round: Optional[int] = None):
        """
        Best-of-7 on the 2-2-1-1-1 schedule.

        - **Who wins each game**: Bernoulli draws using ``calculate_game_win_prob`` (same calibration +
          playoff DNA as the rest of the stack).
        - **Goals in each game**: Poisson with mean from **5-year NHL playoff** per-game combined
          goals (``data/playoff_series_historical_5yr.json``). Single-game win rates still use
          ``cup_prior_current.json`` + ``reg_season_playoff_round_models_5yr.json`` (RS-trained on 5 seasons).

        Series length and total goals are **Monte Carlo** expectations over those draws.
        ``historical_*`` fields summarize the same JSON (reference marginals).
        """
        away_series_wins = 0
        total_games_completed = 0
        total_series_goals_sum = 0.0

        # Pre-calculate win probs for both venues
        p_away_at_home = self.calculate_game_win_prob(away, home, playoff_round=playoff_round)
        p_home_at_away = self.calculate_game_win_prob(home, away, playoff_round=playoff_round)
        p_away_at_away = 1 - p_home_at_away
        
        # Format: H-H-A-A-H-A-H
        full_venues = ['home', 'home', 'away', 'away', 'home', 'away', 'home']
        
        # Calculate how many games were already played
        games_played = away_wins + home_wins
        remaining_venues = full_venues[games_played:]
        
        if games_played >= 7 or away_wins >= 4 or home_wins >= 4:
            return {
                'away': away, 'home': home,
                'away_series_win_prob': 1.0 if away_wins >= 4 else 0.0,
                'home_series_win_prob': 1.0 if home_wins >= 4 else 0.0,
                'status': 'FINISHED',
                'winner': away if away_wins >= 4 else home,
                'avg_remaining_games': 0.0,
                'projected_avg_games_in_series': 0.0,
                'projected_mean_games_in_series': 0.0,
                'projected_rounded_games_in_series': 0,
                'prob_series_goes_seven': None,
                'historical_mean_games_per_series_5yr': None,
                'historical_prob_series_goes_seven_5yr': None,
                'historical_mean_total_goals_per_series_5yr': None,
                'projected_total_goals_series': None,
                'projected_goals_per_game': None,
            }

        prob_seven = 0.0
        # Vectorized path: dominates export runtime when simulations is large (hundreds of series × N).
        if simulations >= 64:
            away_series_wins, total_games_completed, total_series_goals_sum, prob_seven = (
                self._simulate_series_numpy_batch(
                    away,
                    home,
                    away_wins,
                    home_wins,
                    simulations,
                    remaining_venues,
                    playoff_round=playoff_round
                )
            )
        else:
            rng_small = np.random.default_rng()
            for _ in range(simulations):
                a_w = away_wins
                h_w = home_wins
                sim_games = 0
                goals_this_series = 0.0

                for venue in remaining_venues:
                    sim_games += 1
                    lt = self._historical_poisson_mean_combined_goals()
                    goals_this_series += float(rng_small.poisson(max(lt, 1e-6)))
                    
                    # DYNAMIC recalculation
                    if venue == 'home':
                        prob = self.calculate_game_win_prob(away, home, a_w, h_w, playoff_round)
                    else:
                        prob = 1.0 - self.calculate_game_win_prob(home, away, h_w, a_w, playoff_round)

                    if random.random() < prob:
                        # ─── 20. Phase 43: Spatial Special Teams (Pass Efficiency) ───
                        if playoff_round is not None:
                            # Elite PP passing (>80%) creates higher-quality looks
                            # PIT (Penguins) typically have elite PP movement
                            away_pp_eff = self._get_team_metric(away, 'pp_pass_efficiency', 'away')
                            home_pp_eff = self._get_team_metric(home, 'pp_pass_efficiency', 'home')
                            
                            # Use 80% threshold from process_special_teams.py
                            if away_pp_eff > 80.0:
                                pass # Logic extension
                            if home_pp_eff > 80.0:
                                pass # Logic extension
                        a_w += 1
                    else:
                        h_w += 1

                    if a_w == 4 or h_w == 4:
                        break

                games_per_sim.append(sim_games)
                if a_w == 4:
                    away_series_wins += 1
                total_games_completed += sim_games
                total_series_goals_sum += goals_this_series
            if games_per_sim:
                prob_seven = float(sum(1 for g in games_per_sim if g == 7)) / float(len(games_per_sim))

        away_series_prob = away_series_wins / simulations
        avg_games = total_games_completed / simulations
        avg_total_goals = total_series_goals_sum / simulations
        games_int = self._projected_series_length_games_int(
            avg_games, away_wins, home_wins, len(remaining_venues)
        )
        mean_games_rounded = round(float(avg_games), 2)
        gpg = (avg_total_goals / avg_games) if avg_games > 1e-9 else 0.0
        h_mg, h_p7, h_tg = self._historical_series_length_refs()

        return {
            'away': away,
            'home': home,
            'away_series_win_prob': away_series_prob,
            'home_series_win_prob': 1 - away_series_prob,
            'avg_remaining_games': mean_games_rounded,
            'projected_avg_games_in_series': mean_games_rounded,
            'projected_mean_games_in_series': mean_games_rounded,
            'projected_rounded_games_in_series': int(games_int),
            'prob_series_goes_seven': round(prob_seven, 4),
            'historical_mean_games_per_series_5yr': round(h_mg, 4) if h_mg > 0 else None,
            'historical_prob_series_goes_seven_5yr': round(h_p7, 6) if h_mg > 0 else None,
            'historical_mean_total_goals_per_series_5yr': round(h_tg, 4) if h_tg > 0 else None,
            'projected_total_goals_series': round(avg_total_goals, 1),
            'projected_goals_per_game': round(gpg, 2),
            'current_state': f"{away} {away_wins} - {home_wins} {home}",
            'winner_projection': away if away_series_prob > 0.5 else home
        }

    def predict_cup_winner(self, filter_teams: Optional[List[str]] = None):
        """Analyze current teams and rank them by 'Championship DNA' alignment."""
        if not self.advanced_metrics:
            return None
            
        contender_scores = []
        for team_abbr in self.advanced_metrics:
            if filter_teams and team_abbr not in filter_teams:
                continue
                
            dna_score = self.get_team_playoff_modifier(team_abbr)
            # Use points percentage from standings to identify 'Playoff-Bound' teams
            # Actually, just rank everyone for now.
            contender_scores.append({
                'team': team_abbr,
                'dna_alignment': dna_score,
                'signature': self.advanced_metrics[team_abbr]
            })
            
        # Rank by DNA Alignment (Playoff Modifier)
        # Higher score = Better alignment with the 5-year Champion Profile
        contender_scores.sort(key=lambda x: x['dna_alignment'], reverse=True)
        return contender_scores

if __name__ == "__main__":
    predictor = PlayoffSeriesPredictor()
    
    print("\n🏆 THE 2026 STANLEY CUP CHAMPIONSHIP DNA AUDIT")
    print("="*60)
    print("Ranking teams by alignment with the 5-Year 'Cup Winner' DNA Profile")
    print("(Rebounds: 0.33, HD Giveaways: -0.14, Rush Caps: -0.09)")
    print("-" * 60)
    
    rankings = predictor.predict_cup_winner()
    if rankings:
        for i, r in enumerate(rankings[:10], 1):
            star = "⭐ " if i == 1 else "   "
            print(f"{star}{i:<2}. {r['team']:<5} | DNA Alignment: {r['dna_alignment']:>8.4f}")
    
    print("\n📈 TEST: Florida vs Edmonton (2024 Finals Benchmark)")
    result = predictor.simulate_series('EDM', 'FLA')
    print(f"Result: {result['winner_projection']} wins series (Win Prob: {max(result['away_series_win_prob'], result['home_series_win_prob']):.1%})")
