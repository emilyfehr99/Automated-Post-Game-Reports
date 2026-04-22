import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, TimeSeriesSplit, GridSearchCV
from sklearn.metrics import accuracy_score, log_loss, classification_report
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit, cross_val_predict, KFold
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.linear_model import RidgeClassifier, LogisticRegression
import xgboost as xgb
import lightgbm as lgb
import pickle
import math
import shutil
from datetime import datetime, timedelta
try:
    from standings_tracker import StandingsTracker
except Exception:
    from models.standings_tracker import StandingsTracker
from typing import Dict, Optional
try:
    from feature_contract import assert_no_forbidden_features
except Exception:
    from models.feature_contract import assert_no_forbidden_features

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

def normalize_side(val, home_team, away_team):
    """Normalize a value (team name, 'home', 'away') to 'home' or 'away'"""
    if not val:
        return None
    val = str(val).lower()
    if val == 'home':
        return 'home'
    if val == 'away':
        return 'away'
    if val == str(home_team).lower():
        return 'home'
    if val == str(away_team).lower():
        return 'away'
    return None

def load_profiles():
    try:
        with open('team_scoring_profiles.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def load_edge_data():
    """Aggregate player-level NHL Edge metrics into team-level features"""
    file_path = Path('data/nhl_edge_data.json')
    if not file_path.exists():
        return {}
    
    try:
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
            except:
                continue
        
        # Aggregate: Top 3 average for explosiveness
        final_team_edge = {}
        for team, metrics in team_metrics.items():
            top_speeds = sorted(metrics['top_speeds'], reverse=True)[:3]
            top_bursts = sorted(metrics['bursts'], reverse=True)[:3]
            
            final_team_edge[team] = {
                'edge_top_speed': np.mean(top_speeds) if top_speeds else 21.0,
                'edge_burst_avg': np.mean(top_bursts) if top_bursts else 0.5
            }
        return final_team_edge
    except:
        return {}

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
        # Determine actual result (1 = home win, 0 = away win)
        if home_score > away_score:
            actual_home = 1.0
        else:
            actual_home = 0.0
            
        expected_home = self.get_win_prob(home_team, away_team)
        
        # Margin of Victory Multiplier: ln(abs(diff) + 1)
        # Prevents blowouts from inflating rating too wildly
        goal_diff = abs(home_score - away_score)
        multiplier = math.log(goal_diff + 1) if goal_diff > 0 else 1.0
        
        # Calculate Delta
        delta = self.k * multiplier * (actual_home - expected_home)
        
        # Update ratings
        self.ratings[home_team] = self.get_rating(home_team) + delta
        self.ratings[away_team] = self.get_rating(away_team) - delta

class GoalieHistory:
    def __init__(self):
        self.stats = {} # {goalie_name: {'gsax': [], 'hdsv': []}}
        
    def update(self, name, gsax, hdsv=None):
        if not name: return
        if name not in self.stats:
            self.stats[name] = {'gsax': [], 'hdsv': []}
        self.stats[name]['gsax'].append(gsax)
        if hdsv is not None:
            self.stats[name]['hdsv'].append(hdsv)
        
    def get_rolling_gsax(self, name, window=5):
        if not name or name not in self.stats or not self.stats[name]['gsax']:
            return 0.0
        vals = self.stats[name]['gsax'][-window:]
        return np.mean(vals)
        
    def get_rolling_hdsv(self, name, window=5):
        if not name or name not in self.stats or not self.stats[name]['hdsv']:
            return 0.8 # Default NHL avg HDSv%
        vals = self.stats[name]['hdsv'][-window:]
        return np.mean(vals)

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

    def get_travel_distance(self, team, current_city):
        """Distance traveled since last game"""
        if team not in self.history or not self.history[team]['last_city']:
            return 0.0
        return calculate_distance(self.history[team]['last_city'], current_city)
            
    def update_goalie(self, name, gsax):
        self.goalies.update(name, gsax)
        
    def get_goalie_gsax(self, name, window=5):
        return self.goalies.get_rolling_gsax(name, window)

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
        return len(successes) / len(relevant_games)
        
    def get_rolling_stats(self, team, window=5, venue=None, alpha=None):
        """Calculate averages with optional venue filter and exponential decay (alpha)"""
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
                    # Exponential Weighted Mean (most recent has higher weight)
                    weights = [alpha * (1 - alpha) ** i for i in range(len(vals))]
                    weights = weights[::-1]  # Latest value gets alpha
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

def load_data():
    file_path = Path('data/win_probability_predictions_v2.json')
    if not file_path.exists():
        file_path = Path('win_probability_predictions_v2.json')
        
    if not file_path.exists():
        print("⚠️ Predictions file not found!")
        return []

    print(f"Loading predictions from {file_path}...")
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    return data.get('predictions', [])

def calculate_target_encoding(df, col, target='target', min_samples_leaf=5, smoothing=10):
    """Smoothed Target Encoding for teams"""
    prior = df[target].mean()
    counts = df.groupby(col)[target].count()
    means = df.groupby(col)[target].mean()
    smooth = (counts * means + smoothing * prior) / (counts + smoothing)
    return smooth.to_dict(), prior

def extract_features_chronologically(predictions):
    # Sort by date
    print("Sorting games chronologically...")
    sorted_preds = sorted(predictions, key=lambda x: x.get('date', ''))
    
    # Filter for games with actual outcomes
    played_games = [p for p in sorted_preds if p.get('actual_winner')]
    print(f"📊 Total played games in history: {len(played_games)}")
    
    # Train on all completed games for maximum stability.
    # (We rely on time-split evaluation + recency weighting to keep the model
    # responsive to recent form without overfitting small windows.)
    train_subset = played_games
    print(f"🎯 Training on all completed games: {len(train_subset)} samples")
    
    tracker = TeamHistory()
    standings = StandingsTracker()
    profiles = load_profiles() # Load finishing profiles
    edge_data = load_edge_data() # Load NHL Edge speed profiles
    training_data = []
    
    for p in train_subset:
        game_id = p.get('game_id')
        date_str = p.get('date')
        if not date_str:
            continue
            
        try:
            game_date = datetime.strptime(date_str, "%Y-%m-%d")
        except:
            continue
            
        home = p.get('home_team')
        away = p.get('away_team')
        metrics = p.get('metrics_used', {})
        
        winner_side = normalize_side(p.get('actual_winner'), home, away)
        h_score_final = float(metrics.get('home_goals', 0) or p.get('actual_home_score', 0) or 0)
        a_score_final = float(metrics.get('away_goals', 0) or p.get('actual_away_score', 0) or 0)
        
        # 1. CALCULATE FEATURES (Before updating history)
        home_elo = tracker.get_elo(home)
        away_elo = tracker.get_elo(away)
        
        home_rest = tracker.get_days_rest(home, game_date)
        away_rest = tracker.get_days_rest(away, game_date)
        
        h_l5 = tracker.get_rolling_stats(home, 5, alpha=0.3)
        a_l5 = tracker.get_rolling_stats(away, 5, alpha=0.3)
        h_l10 = tracker.get_rolling_stats(home, 10, alpha=0.3)
        a_l10 = tracker.get_rolling_stats(away, 10, alpha=0.3)
        
        # Venue Specific Rolling (L5)
        h_home_l5 = tracker.get_rolling_stats(home, 5, venue='home', alpha=0.3)
        a_away_l5 = tracker.get_rolling_stats(away, 5, venue='away', alpha=0.3)
        
        # Goalie Features
        h_goalie = metrics.get('home_goalie') or p.get('home_goalie')
        a_goalie = metrics.get('away_goalie') or p.get('away_goalie')
        h_gsax_roll = tracker.goalies.get_rolling_gsax(h_goalie)
        a_gsax_roll = tracker.goalies.get_rolling_gsax(a_goalie)
        h_hdsv_roll = tracker.goalies.get_rolling_hdsv(h_goalie)
        a_hdsv_roll = tracker.goalies.get_rolling_hdsv(a_goalie)
        
        # Fatigue / Travel (Phase 4)
        h_travel = tracker.get_travel_distance(home, home) # Home is always 0 travel in simple home game
        a_travel = tracker.get_travel_distance(away, home) # Away team travels to home city
        
        # Finish Factors
        h_finish = profiles.get(home, 1.0)
        a_finish = profiles.get(away, 1.0)
        
        if winner_side:
            row = {
                'game_id': game_id,
                'date': game_date,
                'target': 1 if winner_side == 'home' else 0,
                'p1_target': 1 if metrics.get('lead_after_p1') == 1 else 0, # Home leads after P1
                'margin': h_score_final - a_score_final,
                # Scoreline targets (USED ONLY FOR SCORELINE/TOTALS MODELING; never as features)
                'home_goals_final': h_score_final,
                'away_goals_final': a_score_final,
                'total_goals_final': h_score_final + a_score_final,
                'home_team': home,
                'away_team': away,
                
                # elo_diff
                'elo_diff': (home_elo + tracker.elo.ha) - away_elo,
                
                # Contextual Features
                'rest_diff': home_rest - away_rest,
                'home_b2b': 1 if home_rest == 1 else 0,
                'away_b2b': 1 if away_rest == 1 else 0,
                
                # Goalie Difference
                'gsax_diff': h_gsax_roll - a_gsax_roll,
                'finish_diff': h_finish - a_finish,
                
                # NHL Edge Micro-Movement (Phase 6)
                'edge_speed_diff': edge_data.get(home, {}).get('edge_top_speed', 21.0) - edge_data.get(away, {}).get('edge_top_speed', 21.0),
                'edge_burst_diff': edge_data.get(home, {}).get('edge_burst_avg', 0.5) - edge_data.get(away, {}).get('edge_burst_avg', 0.5),
                
                # Rolling General (EWMA)
                'l5_goal_diff': h_l5.get('goal_diff', 0) - a_l5.get('goal_diff', 0),
                'l5_xg_diff': h_l5.get('xg_diff', 0) - a_l5.get('xg_diff', 0),
                'l5_corsi_diff': h_l5.get('corsi_pct', 50) - a_l5.get('corsi_pct', 50),
                'l5_pdo_diff': h_l5.get('pdo', 100) - a_l5.get('pdo', 100),
                
                # Special Teams
                'l5_pp_diff': h_l5.get('pp_pct', 20) - a_l5.get('pp_pct', 20),
                'l5_pk_diff': h_l5.get('pk_pct', 80) - a_l5.get('pk_pct', 80),
                'l5_st_net': (h_l5.get('pp_pct', 20) + h_l5.get('pk_pct', 80)) - (a_l5.get('pp_pct', 20) + a_l5.get('pk_pct', 80)),
                
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
                
                # Phase 15: Momentum & Game Flow
                'p1_xg_diff': h_l5.get('p1_xg', 0.8) - a_l5.get('p1_xg', 0.8),
                'p2_xg_diff': h_l5.get('p2_xg', 0.8) - a_l5.get('p2_xg', 0.8),
                'p3_xg_diff': h_l5.get('p3_xg', 0.8) - a_l5.get('p3_xg', 0.8),
                'p1_p2_dominance': (h_l10.get('p1_xg', 0.8) + h_l10.get('p2_xg', 0.8)) - (a_l10.get('p1_xg', 0.8) + a_l10.get('p2_xg', 0.8)),
                'h_preservation_rate': tracker.get_rolling_rate(home, 'led_after_p2', 'won_game', window=20),
                'a_preservation_rate': tracker.get_rolling_rate(away, 'led_after_p2', 'won_game', window=20),
                'h_comeback_rate': tracker.get_rolling_rate(home, 'trailed_after_p2', 'won_game', window=20),
                'a_comeback_rate': tracker.get_rolling_rate(away, 'trailed_after_p2', 'won_game', window=20),
                
                # Phase 18: Advanced Transition Analytics
                'l5_nzt_possession_diff': h_l5.get('nzt_possession', 50) - a_l5.get('nzt_possession', 50),
                'l5_ca_shots_diff': h_l5.get('ca_shots', 0) - a_l5.get('ca_shots', 0),
                'l5_rush_sv_pct_diff': h_l5.get('rush_sv_pct', 90) - a_l5.get('rush_sv_pct', 90),
                
                # Venue Specific
                'home_venue_goal_diff': h_home_l5.get('goal_diff', 0),
                'away_venue_goal_diff': a_away_l5.get('goal_diff', 0),
                
                # Strength of Schedule (SoS)
                'home_sos': tracker.get_sos(home, 5),
                'away_sos': tracker.get_sos(away, 5),
                
                # Stability
                'l5_std_diff': tracker.get_rolling_std(home, 5) - tracker.get_rolling_std(away, 5),
                
                'l10_goal_diff': h_l10.get('goal_diff', 0) - a_l10.get('goal_diff', 0),
                'l10_xg_diff': h_l10.get('xg_diff', 0) - a_l10.get('xg_diff', 0),
                
                # Interaction Features (Phase 8 Advanced DS)
                'elo_rest_inter': ((home_elo + tracker.elo.ha) - away_elo) * (home_rest - away_rest),
                'speed_finish_inter': (edge_data.get(home, {}).get('edge_top_speed', 21.0) - edge_data.get(away, {}).get('edge_top_speed', 21.0)) * (h_finish - a_finish),
                
                # Phase 14: Season-Phase Context
                'season_month': game_date.month,
                'is_late_season': 1 if game_date.month in [3, 4] else 0,
                'h_desperation': standings.calculate_desperation_index(home, game_date.strftime('%Y-%m-%d')),
                'a_desperation': standings.calculate_desperation_index(away, game_date.strftime('%Y-%m-%d')),
                
                # Raw Components for Phase 11 Symbolic Features
                'home_xg': h_l5.get('xg_avg', 2.5),
                'away_xg': a_l5.get('xg_avg', 2.5),
                'home_elo': home_elo + tracker.elo.ha,
                'away_elo': away_elo
            }
            training_data.append(row)
            
        # 2. UPDATE HISTORY
        h_score = float(metrics.get('home_goals', 0) or p.get('actual_home_score', 0) or 0)
        a_score = float(metrics.get('away_goals', 0) or p.get('actual_away_score', 0) or 0)
        
        # Save current Elos for next SoS calc
        curr_h_elo = tracker.get_elo(home)
        curr_a_elo = tracker.get_elo(away)
        
        tracker.elo.update(home, away, h_score, a_score)
        
        h_xg = float(metrics.get('home_xg', h_score) or h_score)
        a_xg = float(metrics.get('away_xg', a_score) or a_score)
        
        # Goalie Update (GSAx = xG - Goals, HDSV from metrics)
        h_gsax = h_xg - h_score
        a_gsax = a_xg - a_score
        h_hdsv = float(metrics.get('home_hdsv_pct', 0.8) or 0.8)
        a_hdsv = float(metrics.get('away_hdsv_pct', 0.8) or 0.8)
        
        tracker.goalies.update(h_goalie, h_gsax, h_hdsv)
        tracker.goalies.update(a_goalie, a_gsax, a_hdsv)
        
        h_shots = float(metrics.get('home_shots', 30) or 30)
        a_shots = float(metrics.get('away_shots', 30) or 30)
        
        h_pdo = ((h_score / h_shots if h_shots > 0 else 0.1) + ((a_shots - a_score) / a_shots if a_shots > 0 else 0.9)) * 100
        a_pdo = ((a_score / a_shots if a_shots > 0 else 0.1) + ((h_shots - h_score) / h_shots if h_shots > 0 else 0.9)) * 100
        h_corsi = float(metrics.get('home_corsi_pct', 50) or 50)
        a_corsi = float(metrics.get('away_corsi_pct', 50) or 50)
        
        h_pp = float(metrics.get('home_power_play_pct', 0) or 0)
        a_pp = float(metrics.get('away_power_play_pct', 0) or 0)
        
        # Calculate PK as (100 - Opponent PP%)
        h_pk = 100 - a_pp
        a_pk = 100 - h_pp
        
        h_stats = {
            'goal_diff': h_score - a_score, 
            'xg_diff': h_xg - a_xg, 
            'corsi_pct': h_corsi, 
            'pdo': h_pdo, 
            'pp_pct': h_pp,
            'pressure': float(metrics.get('home_pressure', 2) or 2),
            'rebounds': float(metrics.get('home_rebounds', 1) or 1),
            'lateral': float(metrics.get('home_lateral', 5.0) or 5.0),
            # Phase 15
            'p1_xg': float(metrics.get('p1_xg_home', 0.8) or 0.8),
            'p2_xg': float(metrics.get('p2_xg_home', 0.8) or 0.8),
            'p3_xg': float(metrics.get('p3_xg_home', 0.8) or 0.8),
            'led_after_p1': 1 if metrics.get('lead_after_p1') == 1 else 0,
            'led_after_p2': 1 if metrics.get('lead_after_p2') == 1 else 0,
            'trailed_after_p2': 1 if metrics.get('lead_after_p2') == -1 else 0,
            'won_game': 1 if h_score > a_score else 0,
            # Phase 18
            'nzt_possession': float(metrics.get('home_nzt_possession', 50.0) or 50.0),
            'ca_shots': float(metrics.get('home_ca_shots', 0) or 0),
            'rush_sv_pct': float(metrics.get('home_rush_sv_pct', 90.0) or 90.0)
        }
        a_stats = {
            'goal_diff': a_score - h_score, 
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
            'won_game': 1 if a_score > h_score else 0,
            # Phase 18
            'nzt_possession': float(metrics.get('away_nzt_possession', 50.0) or 50.0),
            'ca_shots': float(metrics.get('away_ca_shots', 0) or 0),
            'rush_sv_pct': float(metrics.get('away_rush_sv_pct', 90.0) or 90.0)
        }
        
        tracker.update(home, game_date, h_stats, venue='home', opponent_elo=curr_a_elo, city=home)
        tracker.update(away, game_date, a_stats, venue='away', opponent_elo=curr_h_elo, city=home)
        
    train_df = pd.DataFrame(training_data)
    
    # NEW: Add Team Mean Win Rate (Target Encoding) for Train/Test split
    # We do this later in the main loop to avoid leakage, but here's the mapping
    return train_df


def split_train_cal_test(df: pd.DataFrame, train_frac: float = 0.80, cal_frac: float = 0.10):
    """Chronological train->calibrate->test split using fixed fractions."""
    df = df.sort_values("date").reset_index(drop=True)
    n = len(df)
    train_end = int(n * float(train_frac))
    cal_end = int(n * float(train_frac + cal_frac))
    train_df = df.iloc[:train_end].copy()
    cal_df = df.iloc[train_end:cal_end].copy()
    test_df = df.iloc[cal_end:].copy()
    return train_df, cal_df, test_df


def _build_matrices_and_sidecars(
    train_df: pd.DataFrame,
    cal_df: pd.DataFrame,
    test_df: pd.DataFrame,
    *,
    stability_recent_n: int = 200,
):
    """Prepare X/y matrices consistently (leakage-safe target encoding, same transforms)."""
    base_features = [
        c
        for c in train_df.columns
        if c
        not in [
            "game_id",
            "date",
            "target",
            "margin",
            "p1_target",
            # Scoreline targets (must never become features)
            "home_goals_final",
            "away_goals_final",
            "total_goals_final",
        ]
    ]
    # Hard fail on any forbidden postgame/label columns ever reaching the feature matrix.
    assert_no_forbidden_features(base_features)

    X_train = train_df[base_features].copy()
    y_train = train_df["target"].astype(int)
    y_margin_train = train_df["margin"] if "margin" in train_df.columns else None

    X_cal = cal_df[base_features].copy()
    y_cal = cal_df["target"].astype(int)

    X_test = test_df[base_features].copy()
    y_test = test_df["target"].astype(int)
    y_margin_test = test_df["margin"] if "margin" in test_df.columns else None

    # Target encodings learned on train only (saved for predictor)
    home_map, home_prior = calculate_target_encoding(train_df, "home_team")
    away_map, away_prior = calculate_target_encoding(train_df, "away_team", target="target")

    for X, dframe in [(X_train, train_df), (X_cal, cal_df), (X_test, test_df)]:
        X["home_win_rate"] = dframe["home_team"].map(home_map).fillna(home_prior)
        X["away_win_rate"] = dframe["away_team"].map(away_map).fillna(away_prior)
        X.drop(columns=["home_team", "away_team"], inplace=True)

        # Interactions
        if "away_sos" in dframe.columns:
            X["home_win_rate_away_sos"] = X["home_win_rate"] * dframe["away_sos"]
        if "away_b2b" in dframe.columns and "finish_diff" in dframe.columns:
            X["away_b2b_home_strength"] = dframe["away_b2b"] * dframe["finish_diff"]

        # Symbolic features (if present)
        if all(k in dframe.columns for k in ["home_xg", "away_xg", "home_elo", "away_elo"]):
            X["pressure_index"] = (dframe["home_xg"] / (dframe["away_xg"] + 0.1)) * (
                dframe["home_elo"] / (dframe["away_elo"] + 0.1)
            )
        if all(k in dframe.columns for k in ["home_xg", "away_xg", "home_sos", "away_sos"]):
            X["xg_efficiency"] = (dframe["home_xg"] * (dframe["home_sos"] / 1500.0)) - (
                dframe["away_xg"] * (dframe["away_sos"] / 1500.0)
            )
        if all(k in dframe.columns for k in ["elo_diff", "l10_xg_diff"]):
            X["power_momentum"] = dframe["elo_diff"] * dframe["l10_xg_diff"]

        prune = [
            "home_win_rate",  # intentionally not used directly
            "home_venue_goal_diff",
            "away_venue_goal_diff",
            "l5_pizza_diff",
            "l5_nzt_diff",
            "l5_rush_diff",
            "l5_pk_diff",
            "l5_pp_diff",
            "l5_ozs_diff",
            "l5_hdc_diff",
        ]
        for col in prune:
            if col in X.columns:
                X.drop(columns=[col], inplace=True)

    # Stability pruning (shared across all splits)
    try:
        X_train, X_cal, X_test, dropped = prune_unstable_features(
            X_train, X_cal, X_test, recent_n=int(stability_recent_n)
        )
        if dropped:
            print(f"🧹 Stability prune: dropped {len(dropped)} unstable features")
            # Print names to make diagnosing upstream feature drift easy in CI logs.
            print("   dropped:", ", ".join(dropped[:50]) + (" ..." if len(dropped) > 50 else ""))
    except Exception as e:
        print(f"⚠️ Stability pruning skipped: {e}")

    # Feature health: missingness in the most recent window
    try:
        import pandas as _pd
        X_all = _pd.concat([X_train, X_cal, X_test], axis=0, ignore_index=True)
        recent = X_all.tail(int(stability_recent_n))
        miss = recent.isna().mean().sort_values(ascending=False)
        top = miss[miss > 0.0].head(20)
        if len(top) > 0:
            print(f"🩺 Feature health (missing rate) on last {len(recent)} rows:")
            for name, frac in top.items():
                print(f"  - {name}: {frac:.1%}")
        else:
            print(f"🩺 Feature health: no missing values in last {len(recent)} rows")
    except Exception as e:
        print(f"⚠️ Feature health report failed: {e}")

    # Recency weights on train (newest games heavier)
    n_train = len(train_df)
    if n_train > 1:
        ages = (n_train - 1) - np.arange(n_train, dtype=float)
        sample_weights = 0.5 ** (ages / 60.0)
    else:
        sample_weights = np.ones(n_train, dtype=float)

    if "season_month" in train_df.columns:
        late_mask = train_df["season_month"].isin([3, 4]).values
        sample_weights[late_mask] *= 1.25

    encoding_stats = {
        "home_map": home_map,
        "home_prior": float(home_prior),
        "away_map": away_map,
        "away_prior": float(away_prior),
    }

    feature_names = list(X_train.columns)
    return {
        "X_train": X_train,
        "y_train": y_train,
        "y_margin_train": y_margin_train,
        "X_cal": X_cal,
        "y_cal": y_cal,
        "X_test": X_test,
        "y_test": y_test,
        "y_margin_test": y_margin_test,
        "sample_weights": sample_weights,
        "feature_names": feature_names,
        "encoding_stats": encoding_stats,
    }


def train_calibrate_evaluate_variant(
    *,
    name: str,
    train_df: pd.DataFrame,
    cal_df: pd.DataFrame,
    test_df: pd.DataFrame,
    do_grid_search: bool,
    fixed_params: Optional[Dict] = None,
):
    """Train -> calibrate -> evaluate, writing variant-prefixed artifacts."""
    mats = _build_matrices_and_sidecars(train_df, cal_df, test_df)
    X_train = mats["X_train"]
    y_train = mats["y_train"]
    X_cal = mats["X_cal"]
    y_cal = mats["y_cal"]
    X_test = mats["X_test"]
    y_test = mats["y_test"]
    w = mats["sample_weights"]

    print(f"\n🧠 Training XGB variant={name} (grid_search={do_grid_search})")
    print(f"  train={len(X_train)} cal={len(X_cal)} test={len(X_test)} feats={X_train.shape[1]}")

    best_params = None
    if do_grid_search:
        tscv = TimeSeriesSplit(n_splits=5)
        param_grid = {
            "max_depth": [3, 4, 5],
            "learning_rate": [0.01, 0.03, 0.05],
            "n_estimators": [100, 150, 200],
            "subsample": [0.8, 0.9],
            "colsample_bytree": [0.8, 0.9],
            "gamma": [0, 0.1, 0.2],
        }
        base = xgb.XGBClassifier(
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
        )
        grid = GridSearchCV(
            estimator=base,
            param_grid=param_grid,
            cv=tscv,
            scoring="neg_log_loss",
            n_jobs=-1,
        )
        grid.fit(X_train, y_train, sample_weight=w)
        best_model = grid.best_estimator_
        best_params = dict(grid.best_params_ or {})
        print(f"✅ {name} best params: {best_params}")
    else:
        params = fixed_params or {}
        if not params:
            params = {
                "max_depth": 4,
                "learning_rate": 0.03,
                "n_estimators": 150,
                "subsample": 0.85,
                "colsample_bytree": 0.85,
                "gamma": 0.0,
            }
        best_params = dict(params)
        best_model = xgb.XGBClassifier(
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            **best_params,
        )
        best_model.fit(X_train, y_train, sample_weight=w)

    # Calibrate on true future fold
    best_model.fit(X_train, y_train, sample_weight=w)
    cal = CalibratedClassifierCV(estimator=best_model, method="isotonic", cv="prefit")
    cal.fit(X_cal, y_cal)

    # Evaluate on test window (identical across variants)
    y_prob = np.clip(cal.predict_proba(X_test)[:, 1], 1e-6, 1 - 1e-6)
    y_pred = (y_prob >= 0.5).astype(int)
    acc = float(accuracy_score(y_test, y_pred))
    loss = float(log_loss(y_test, y_prob))
    print(f"📊 {name} test acc={acc:.3f} logloss={loss:.4f}")

    # Save sidecars for predictor
    with open(f"team_encodings_{name}.json", "w") as f:
        json.dump(mats["encoding_stats"], f)
    with open(f"xgb_features_{name}.pkl", "wb") as f:
        pickle.dump(mats["feature_names"], f)
    with open(f"xgb_calibrated_model_{name}.pkl", "wb") as f:
        pickle.dump(cal, f)

    # Booster JSON for any legacy code paths
    try:
        best_model.save_model(f"xgb_nhl_model_{name}.json")
    except Exception as e:
        print(f"⚠️ Could not save booster JSON for {name}: {e}")

    # Shared recent evaluator (apples-to-apples vs Elo)
    recent_eval = None
    try:
        recent_eval = rolling_recent_eval(
            pd.concat([train_df, cal_df, test_df], ignore_index=True),
            recent_n=200,
            n_splits=4,
        )
    except Exception as e:
        print(f"⚠️ Recent-window evaluation failed for {name}: {e}")

    return {
        "name": name,
        "best_params": best_params,
        "test_acc": acc,
        "test_logloss": loss,
        "recent_eval": recent_eval,
        "artifacts": {
            "calibrated_model": f"xgb_calibrated_model_{name}.pkl",
            "features": f"xgb_features_{name}.pkl",
            "encodings": f"team_encodings_{name}.json",
            "booster_json": f"xgb_nhl_model_{name}.json",
        },
    }

def train_optimized_model():
    print("🚀 STARTING ADVANCED DATA SCIENCE OPTIMIZATION (PHASE 7)")
    print("=" * 60)
    
    raw_preds = load_data()
    df = extract_features_chronologically(raw_preds)
    
    if len(df) < 100:
        print("⚠️ Not enough samples for training.")
        return
        
    print(f"✅ Extracted {len(df)} training samples")
    df = df.sort_values('date')

    # --- Feature leakage audit (hard fail) ---
    _audit_no_postgame_feature_leakage(df)

    # --- Build identical forward windows for all variants ---
    # We always evaluate on the same future calibration + test windows.
    train_df_full, cal_df, test_df = split_train_cal_test(df, train_frac=0.80, cal_frac=0.10)
    # Recent-300 challenger: train only on the most recent N games *from the train block*
    recent_n = 300
    train_df_recent = train_df_full.tail(recent_n).copy() if len(train_df_full) > recent_n else train_df_full.copy()
    print(f"🏷️ Variants: full_train={len(train_df_full)} recent_train={len(train_df_recent)} cal={len(cal_df)} test={len(test_df)}")

    # Train FULL variant (includes hyperparam search)
    full_res = train_calibrate_evaluate_variant(
        name="full",
        train_df=train_df_full,
        cal_df=cal_df,
        test_df=test_df,
        do_grid_search=True,
    )

    # Train RECENT variant (reuse full params for speed/stability)
    recent_res = train_calibrate_evaluate_variant(
        name="recent",
        train_df=train_df_recent,
        cal_df=cal_df,
        test_df=test_df,
        do_grid_search=False,
        fixed_params=full_res.get("best_params"),
    )

    # Pick champion by forward test log loss (lower is better)
    champ = "full"
    try:
        if float(recent_res["test_logloss"]) < float(full_res["test_logloss"]) - 1e-6:
            champ = "recent"
    except Exception:
        champ = "full"

    print(f"🏆 XGB champion={champ} (full_ll={full_res.get('test_logloss'):.4f}, recent_ll={recent_res.get('test_logloss'):.4f})")

    # Write legacy artifact filenames to keep the rest of the pipeline stable.
    try:
        chosen = full_res if champ == "full" else recent_res
        art = chosen.get("artifacts", {}) if isinstance(chosen, dict) else {}
        # Calibrated model + features are pickles; booster + encodings are JSON.
        if art.get("calibrated_model") and Path(str(art["calibrated_model"])).exists():
            shutil.copyfile(str(art["calibrated_model"]), "xgb_calibrated_model.pkl")
        if art.get("features") and Path(str(art["features"])).exists():
            shutil.copyfile(str(art["features"]), "xgb_features.pkl")
        if art.get("encodings") and Path(str(art["encodings"])).exists():
            shutil.copyfile(str(art["encodings"]), "team_encodings.json")
        if art.get("booster_json") and Path(str(art["booster_json"])).exists():
            shutil.copyfile(str(art["booster_json"]), "xgb_nhl_model.json")
        print("✅ Wrote legacy champion artifacts (xgb_* + team_encodings.json)")
    except Exception as e:
        print(f"⚠️ Could not write legacy champion artifacts: {e}")

    # Persist performance snapshot (including champion)
    perf_out = {
        "updated_at_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "xgb_champion": champ,
        "variants": {
            "full": {
                "train_n": int(len(train_df_full)),
                "test_acc": float(full_res.get("test_acc")),
                "test_logloss": float(full_res.get("test_logloss")),
                "recent_eval": full_res.get("recent_eval"),
            },
            "recent": {
                "train_n": int(len(train_df_recent)),
                "test_acc": float(recent_res.get("test_acc")),
                "test_logloss": float(recent_res.get("test_logloss")),
                "recent_eval": recent_res.get("recent_eval"),
            },
        },
        # Keep top-level fields for backward compatibility with guardrails
        "xgb_recent_logloss": float((recent_res.get("recent_eval") or {}).get("xgb_recent_logloss") or (full_res.get("recent_eval") or {}).get("xgb_recent_logloss") or float("nan")),
        "elo_recent_logloss": float((recent_res.get("recent_eval") or {}).get("elo_recent_logloss") or (full_res.get("recent_eval") or {}).get("elo_recent_logloss") or float("nan")),
    }
    with open("model_performance.json", "w") as f:
        json.dump(perf_out, f, indent=2)
    print("✅ Saved model_performance.json (with xgb_champion)")

    # NOTE: The rest of the previous monolithic training flow remains below for now,
    # but is bypassed because we return early after producing artifacts.
    return
    
    # Time-based split with a dedicated calibration fold:
    # train -> calibrate (future) -> final test (further future)
    n = len(df)
    train_end = int(n * 0.80)
    cal_end = int(n * 0.90)
    train_df = df.iloc[:train_end]
    cal_df = df.iloc[train_end:cal_end]
    test_df = df.iloc[cal_end:]
    
    features = [c for c in df.columns if c not in ['game_id', 'date', 'target', 'margin', 'p1_target']]
    X_train = train_df[features].copy()
    y_train = train_df['target']
    y_margin_train = train_df['margin']
    X_cal = cal_df[features].copy()
    y_cal = cal_df['target']
    X_test = test_df[features].copy()
    y_test = test_df['target']
    y_margin_test = test_df['margin']
    
    # 1. Target Encoding (Advanced DS Concept)
    # Learn team win rates from training data to identify "Home Strong" or "Away resilient" teams
    home_map, home_prior = calculate_target_encoding(train_df, 'home_team')
    away_map, away_prior = calculate_target_encoding(train_df, 'away_team', target='target') # target=1 is home win, so we need to flip for away?
    # Actually, let's just use "win rate of this team being in this slot"
    
    X_train['home_win_rate'] = train_df['home_team'].map(home_map).fillna(home_prior)
    X_train['away_win_rate'] = train_df['away_team'].map(away_map).fillna(away_prior)
    X_cal['home_win_rate'] = cal_df['home_team'].map(home_map).fillna(home_prior)
    X_cal['away_win_rate'] = cal_df['away_team'].map(away_map).fillna(away_prior)
    X_test['home_win_rate'] = test_df['home_team'].map(home_map).fillna(home_prior)
    X_test['away_win_rate'] = test_df['away_team'].map(away_map).fillna(away_prior)
    
    # Save the maps for predictor
    encoding_stats = {
        'home_map': home_map, 'home_prior': home_prior,
        'away_map': away_map, 'away_prior': away_prior
    }
    with open("team_encodings.json", "w") as f:
        json.dump(encoding_stats, f)
        
    # Drop team names from feature sets
    X_train = X_train.drop(columns=['home_team', 'away_team'])
    X_cal = X_cal.drop(columns=['home_team', 'away_team'])
    X_test = X_test.drop(columns=['home_team', 'away_team'])
    
    # NEW: Final feature sync for interaction terms
    X_train['home_win_rate_away_sos'] = X_train['home_win_rate'] * train_df['away_sos']
    X_cal['home_win_rate_away_sos'] = X_cal['home_win_rate'] * cal_df['away_sos']
    X_test['home_win_rate_away_sos'] = X_test['home_win_rate'] * test_df['away_sos']
    X_train['away_b2b_home_strength'] = train_df['away_b2b'] * train_df['finish_diff']
    X_cal['away_b2b_home_strength'] = cal_df['away_b2b'] * cal_df['finish_diff']
    X_test['away_b2b_home_strength'] = test_df['away_b2b'] * test_df['finish_diff']
    
    # Phase 11: Symbolic Feature Discovery
    # 1. Pressure Index: Compounding offensive threat with team quality
    X_train['pressure_index'] = (train_df['home_xg'] / (train_df['away_xg'] + 0.1)) * (train_df['home_elo'] / (train_df['away_elo'] + 0.1))
    X_cal['pressure_index'] = (cal_df['home_xg'] / (cal_df['away_xg'] + 0.1)) * (cal_df['home_elo'] / (cal_df['away_elo'] + 0.1))
    X_test['pressure_index'] = (test_df['home_xg'] / (test_df['away_xg'] + 0.1)) * (test_df['home_elo'] / (test_df['away_elo'] + 0.1))
    
    # 2. xG Efficiency: xG relative to opponent strength
    X_train['xg_efficiency'] = (train_df['home_xg'] * (train_df['home_sos'] / 1500)) - (train_df['away_xg'] * (train_df['away_sos'] / 1500))
    X_cal['xg_efficiency'] = (cal_df['home_xg'] * (cal_df['home_sos'] / 1500)) - (cal_df['away_xg'] * (cal_df['away_sos'] / 1500))
    X_test['xg_efficiency'] = (test_df['home_xg'] * (test_df['home_sos'] / 1500)) - (test_df['away_xg'] * (test_df['away_sos'] / 1500))
    
    # 3. Power Momentum: Synergy of talent and recent offensive form
    X_train['power_momentum'] = train_df['elo_diff'] * train_df['l10_xg_diff']
    X_cal['power_momentum'] = cal_df['elo_diff'] * cal_df['l10_xg_diff']
    X_test['power_momentum'] = test_df['elo_diff'] * test_df['l10_xg_diff']
    
    # Final drop of low-impact or redundant columns (Phase 9 Elite Pruning)
    final_prune = [
        'home_win_rate', 'home_b2b', 'rest_diff', 'gsax_diff', 'away_b2b',
        'home_venue_goal_diff', 'away_venue_goal_diff', 'l5_pizza_diff',
        'l5_nzt_diff', 'l5_rush_diff', 'l5_pk_diff', 'l5_pp_diff', 
        'l5_ozs_diff', 'l5_hdc_diff'
    ]
    for p in final_prune:
        if p in X_train.columns: X_train.drop(columns=[p], inplace=True)
        if p in X_cal.columns: X_cal.drop(columns=[p], inplace=True)
        if p in X_test.columns: X_test.drop(columns=[p], inplace=True)

    # --- Stability pruning (reduce overfit + broken upstream signals) ---
    # Drop features that are missing/constant/mostly-zero in the most recent window.
    try:
        X_train, X_cal, X_test, dropped = prune_unstable_features(
            X_train, X_cal, X_test, recent_n=200
        )
        if dropped:
            print(f"🧹 Stability prune: dropped {len(dropped)} unstable features")
    except Exception as e:
        print(f"⚠️ Stability pruning skipped: {e}")

    features = [f for f in X_train.columns]
    
    # Phase 14: Adaptive Sample Weighting (Recency, time-aware)
    # Exponential recency weights: newest game weight=1.0, half-life ~60 games.
    # This keeps the model current while still learning from the full season.
    n_train = len(train_df)
    if n_train > 1:
        half_life_games = 60.0
        ages = np.arange(n_train - 1, -1, -1, dtype=float)  # 0=oldest? we want newest=0
        # Make newest index have age=0
        ages = (n_train - 1) - np.arange(n_train, dtype=float)
        sample_weights = 0.5 ** (ages / half_life_games)
    else:
        sample_weights = np.ones(len(y_train))
    
    # Extra emphasis on March/April games for "Playoff Push" intensity
    # (Checking season_month in the corresponding indices of y_train)
    late_season_mask = (train_df['season_month'].isin([3, 4])).values
    sample_weights[late_season_mask] *= 1.25 # 25% extra weight for playoff push context
    
    print(f"Training on {len(X_train)} games, Calibrating on {len(X_cal)} games, Testing on {len(X_test)} games")
    
    # 2. Hyperparameter Tuning using TimeSeriesSplit
    tscv = TimeSeriesSplit(n_splits=5)
    
    param_grid = {
        'max_depth': [3, 4],
        'learning_rate': [0.01, 0.05],
        'n_estimators': [50, 100],
        'subsample': [0.8, 0.9],
    }
    
    base_xgb = xgb.XGBClassifier(
        objective='binary:logistic',
        eval_metric='logloss',
        random_state=42
    )
    
    print("\n🔍 Tuning XGBoost components for ensemble (optimize log loss)...")
    grid_search = GridSearchCV(
        estimator=base_xgb,
        param_grid=param_grid,
        cv=tscv,
        scoring='neg_log_loss',
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train, sample_weight=sample_weights)
    best_xgb = grid_search.best_estimator_
    
    # 3. Build Optimized Model (Phase 9 Refined)
    print("\n🏗️ Training highly-tuned XGBoost with Power Index Interaction...")
    
    param_grid = {
        'max_depth': [3, 4, 5],
        'learning_rate': [0.01, 0.03, 0.05],
        'n_estimators': [100, 150, 200],
        'subsample': [0.8, 0.9],
        'colsample_bytree': [0.8, 0.9],
        'gamma': [0, 0.1, 0.2]
    }
    
    grid_search = GridSearchCV(
        estimator=xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', random_state=42),
        param_grid=param_grid,
        cv=tscv,
        scoring='neg_log_loss',
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train, sample_weight=sample_weights)
    best_model = grid_search.best_estimator_
    print(f"✅ Best Params: {grid_search.best_params_}")
    
    # 3b. Probability Calibration (true future holdout)
    # Fit base model on train, then calibrate on the *next* (future) fold only.
    print("\n⚖️ Calibrating probabilities (Isotonic, future holdout)...")
    best_model.fit(X_train, y_train, sample_weight=sample_weights)
    calibrated_model = CalibratedClassifierCV(
        estimator=best_model,
        method='isotonic',
        cv='prefit'
    )
    calibrated_model.fit(X_cal, y_cal)
    
    # Evaluate on Holdout
    y_pred = calibrated_model.predict(X_test)
    y_prob = calibrated_model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    loss = log_loss(y_test, y_prob)
    
    # Confidence bucket reporting on final test window
    try:
        bucket = confidence_bucket_report(
            y_true=(y_test.values if hasattr(y_test, "values") else y_test),
            p_home=y_prob,
        )
        print("\n🎚️ Confidence buckets (final test)")
        for b in bucket["buckets"]:
            print(
                f"  conf≥{b['min_conf']:.2f}: n={b['n']:>3} acc={b['acc']:.3f} "
                f"logloss={b['logloss']:.4f}"
            )
    except Exception as e:
        print(f"⚠️ Confidence-bucket report failed: {e}")

    print("\n" + "="*30)
    print(f"FINAL PHASE 9 RESULTS:")
    print(f"Accuracy: {acc:.1%}")
    print(f"Log Loss: {loss:.4f}")
    print("="*30)
    
    # Feature Importance
    imp = pd.Series(best_model.feature_importances_, index=features).sort_values(ascending=False)
    print("\nTop Phase 9 Predictors:")
    print(imp.head(12))

    # --- Correct evaluation: rolling forward splits ---
    # Report how the calibrated model performs when repeatedly training on the past
    # and predicting the future (matches production usage).
    try:
        print("\n📈 Rolling forward evaluation (time-split)")
        print("-" * 60)
        roll = rolling_time_split_eval(
            df=df,
            base_model=best_model,
            calibrated=True,
            n_splits=6,
        )
        print(
            f"XGB(cal) mean acc={roll['mean_acc']:.3f}  "
            f"mean logloss={roll['mean_logloss']:.4f}  "
            f"mean brier={roll['mean_brier']:.4f}  "
            f"splits={roll['n_splits_used']}"
        )
        print(
            f"Elo baseline mean acc={roll['elo_mean_acc']:.3f}  "
            f"mean logloss={roll['elo_mean_logloss']:.4f}"
        )
    except Exception as e:
        print(f"⚠️ Rolling evaluation failed: {e}")

    # --- Feature leakage audit ---
    # Ensure we did not accidentally include post-game fields as features.
    try:
        _audit_no_postgame_feature_leakage(df)
        print("✅ Feature leakage audit passed")
    except Exception as e:
        print(f"❌ Feature leakage audit failed: {e}")
        # Hard fail so we don't save a model that looks great due to leakage.
        raise

    # --- Recent-window evaluation (apples-to-apples vs Elo) ---
    recent_eval = None
    try:
        recent_eval = rolling_recent_eval(df, recent_n=200, n_splits=4)
        print(
            f"Recent(200) XGB(cal) logloss={recent_eval['xgb_recent_logloss']:.4f} "
            f"acc={recent_eval['xgb_recent_acc']:.3f} | "
            f"Elo logloss={recent_eval['elo_recent_logloss']:.4f} "
            f"acc={recent_eval['elo_recent_acc']:.3f}"
        )
    except Exception as e:
        print(f"⚠️ Recent-window evaluation failed: {e}")

    # Persist a lightweight performance snapshot so production can downweight
    # components if they underperform their baselines recently.
    try:
        perf_out = {
            "updated_at_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "xgb_cal_mean_acc": float(roll.get("mean_acc")) if "roll" in locals() else None,
            "xgb_cal_mean_logloss": float(roll.get("mean_logloss")) if "roll" in locals() else None,
            "elo_mean_acc": float(roll.get("elo_mean_acc")) if "roll" in locals() else None,
            "elo_mean_logloss": float(roll.get("elo_mean_logloss")) if "roll" in locals() else None,
        }
        # (Scoreline metrics appended later once total-goals model is trained.)
        if isinstance(recent_eval, dict):
            perf_out.update(recent_eval)
        with open("model_performance.json", "w") as f:
            json.dump(perf_out, f, indent=2)
        print("✅ Saved model_performance.json")
    except Exception as e:
        print(f"⚠️ Could not save model_performance.json: {e}")
    
    # 3c. Meta-Labeling (Phase 10: Model for the Model)
    print("\n🏗️ Training Phase 10 Meta-Confidence Model...")
    # Get out-of-sample predictions to create meta-targets
    # Use standard KFold for meta-labels to avoid TimeSeriesSplit partition issues
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    y_pred_cv = cross_val_predict(best_model, X_train, y_train, cv=kf, method='predict')
    y_meta = (y_pred_cv == y_train).astype(int)
    
    # Train a "Confidence Model" to predict if the primary model is right
    confidence_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    confidence_model.fit(X_train, y_meta)
    
    meta_acc = accuracy_score([1]*len(y_test), (calibrated_model.predict(X_test) == y_test).astype(int))
    print(f"✅ Meta-Model trained. Baseline Accuracy predicted: {meta_acc:.1%}")
    
    # 3d. Goal Margin Regression (Phase 12)
    print("\n🏗️ Training Phase 12 Goal Margin Regressor...")
    margin_model = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
        random_state=42
    )
    margin_model.fit(X_train, y_margin_train, sample_weight=sample_weights)
    margin_preds = margin_model.predict(X_test)
    margin_mae = np.mean(np.abs(margin_preds - y_margin_test))
    print(f"✅ Margin Regressor trained. MAE: {margin_mae:.2f} goals")

    # 3d.1 Total Goals Model (Scoreline backbone)
    # Predict total goals (home+away) from the SAME feature pipeline as the win model.
    total_goals_model = None
    total_goals_mae = None
    try:
        if "total_goals_final" in train_df.columns and "total_goals_final" in test_df.columns:
            y_total_train = train_df["total_goals_final"].astype(float).values
            y_total_test = test_df["total_goals_final"].astype(float).values

            total_goals_model = xgb.XGBRegressor(
                objective="count:poisson",
                n_estimators=250,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.9,
                colsample_bytree=0.9,
                reg_lambda=1.0,
                random_state=42,
            )
            total_goals_model.fit(X_train, y_total_train, sample_weight=sample_weights)
            total_preds = total_goals_model.predict(X_test)
            total_goals_mae = float(np.mean(np.abs(total_preds - y_total_test)))
            print(f"✅ Total Goals model trained. MAE: {total_goals_mae:.2f} goals")
        else:
            print("⚠️ Total Goals model skipped (missing total_goals_final column)")
    except Exception as e:
        print(f"⚠️ Total Goals model training failed: {e}")

    # Append scoreline metrics to model_performance.json (created earlier).
    try:
        if total_goals_mae is not None:
            p = Path("model_performance.json")
            if p.exists():
                with open(p, "r") as f:
                    perf = json.load(f)
            else:
                perf = {}
            perf["total_goals_mae"] = float(total_goals_mae)
            with open(p, "w") as f:
                json.dump(perf, f, indent=2)
            print("✅ Updated model_performance.json with total_goals_mae")
    except Exception as e:
        print(f"⚠️ Could not update model_performance.json with scoreline metrics: {e}")
    
    # 3e. Period 1 Meta-Model (Phase 17)
    print("\n🏗️ Training Phase 17 Period 1 Meta-Model...")
    y_p1_train = train_df['p1_target'].values
    y_p1_test = test_df['p1_target'].values
    
    # Only train if we have both classes (Home lead vs No lead)
    if len(np.unique(y_p1_train)) > 1:
        p1_model = xgb.XGBClassifier(
            objective='binary:logistic',
            eval_metric='logloss',
            n_estimators=100,
            max_depth=4,
            learning_rate=0.03,
            random_state=42
        )
        p1_model.fit(X_train, y_p1_train, sample_weight=sample_weights)
        p1_acc = accuracy_score(y_p1_test, p1_model.predict(X_test))
        print(f"✅ Period 1 Model trained. Accuracy: {p1_acc:.1%}")
    else:
        print("⚠️ Not enough P1 data (single class detected), skipping P1 model training.")
        p1_model = None
    
    # 4. SAVE MODELS (probability-first)
    # Since CalibratedClassifierCV is a wrapper, we save it as a pickle
    # Gate 1: minimum accuracy sanity check (kept)
    # Gate 2: must beat Elo logloss on the same final test window OR improve vs prior saved model.
    # Gate 3: must not underperform Elo on recent-window logloss (last ~200 games).
    elo_test_logloss = None
    try:
        elo_test_logloss = elo_logloss_on_test(train_df, test_df)
        print(f"📉 Elo baseline logloss on final test: {elo_test_logloss:.4f}")
    except Exception as e:
        print(f"⚠️ Could not compute Elo test logloss: {e}")

    prior_xgb_ll = None
    try:
        p = Path("model_performance.json")
        if p.exists():
            with open(p, "r") as f:
                prior = json.load(f)
            prior_xgb_ll = prior.get("xgb_recent_logloss") or prior.get("xgb_cal_mean_logloss")
    except Exception:
        prior_xgb_ll = None

    beats_elo = (elo_test_logloss is not None) and (loss < float(elo_test_logloss) - 1e-6)
    improves_prior = (prior_xgb_ll is not None) and (loss < float(prior_xgb_ll) - 1e-6)

    recent_ok = True
    try:
        if isinstance(recent_eval, dict):
            x_recent = float(recent_eval.get("xgb_recent_logloss"))
            e_recent = float(recent_eval.get("elo_recent_logloss"))
            if np.isfinite(x_recent) and np.isfinite(e_recent):
                recent_ok = x_recent <= (e_recent + 1e-6)
    except Exception:
        recent_ok = True

    should_save = (acc >= 0.50) and (beats_elo or improves_prior) and recent_ok

    if should_save:
        # Save calibrated model (pickle contains the entire stack + calibrator)
        with open("xgb_calibrated_model.pkl", "wb") as f:
            pickle.dump(calibrated_model, f)
        
        # Save the meta-confidence model
        with open('meta_confidence_model.pkl', 'wb') as f:
            pickle.dump(confidence_model, f)
            
        # Save the margin regression model
        with open('margin_regression_model.pkl', 'wb') as f:
            pickle.dump(margin_model, f)

        # Save the total goals model (if trained)
        if total_goals_model is not None:
            with open("total_goals_model.pkl", "wb") as f:
                pickle.dump(total_goals_model, f)
            
        # Save the Period 1 meta-model
        with open('p1_outcome_model.pkl', 'wb') as f:
            pickle.dump(p1_model, f)

        # Also save booster as JSON (uncalibrated) for legacy code
        best_xgb.save_model("xgb_nhl_model.json")
        
        print("\n💾 Saved stacked model to xgb_calibrated_model.pkl")
        print("💾 Saved XGB component to xgb_nhl_model.json")
        
        with open("xgb_features.pkl", "wb") as f:
            pickle.dump(features, f)
    else:
         print("\n⚠️ Did not save model (failed probability-first gates).")
         print(f"  - acc={acc:.3f} loss={loss:.4f} beats_elo={beats_elo} improves_prior={improves_prior} recent_ok={recent_ok}")

def rolling_time_split_eval(
    df: pd.DataFrame,
    base_model,
    calibrated: bool = True,
    n_splits: int = 6,
) -> Dict[str, float]:
    """Forward-chaining evaluation on the full season dataset.

    Trains on earlier games and evaluates on later games for each split.
    Also reports an Elo-only baseline built from results up to that point.
    """
    from sklearn.metrics import brier_score_loss

    df = df.sort_values("date").reset_index(drop=True)
    features_all = [c for c in df.columns if c not in ["game_id", "date", "target", "margin", "p1_target"]]

    # Build encodings using only training folds inside each split to avoid leakage.
    tscv = TimeSeriesSplit(n_splits=max(2, int(n_splits)))

    accs = []
    lls = []
    briers = []
    elo_accs = []
    elo_lls = []

    # Elo tracker for baseline (updated only with training fold results)
    elo = EloTracker()

    splits_used = 0
    for train_idx, test_idx in tscv.split(df):
        train_df = df.iloc[train_idx].copy()
        test_df = df.iloc[test_idx].copy()
        if len(test_df) < 30 or len(train_df) < 200:
            continue

        # Target encodings learned on train only
        home_map, home_prior = calculate_target_encoding(train_df, "home_team")
        away_map, away_prior = calculate_target_encoding(train_df, "away_team", target="target")

        def build_X(dframe: pd.DataFrame) -> pd.DataFrame:
            X = dframe[features_all].copy()
            X["home_win_rate"] = dframe["home_team"].map(home_map).fillna(home_prior)
            X["away_win_rate"] = dframe["away_team"].map(away_map).fillna(away_prior)
            X = X.drop(columns=["home_team", "away_team"])
            # Minimal interactions used in training
            if "away_sos" in dframe.columns:
                X["home_win_rate_away_sos"] = X["home_win_rate"] * dframe["away_sos"]
            if "away_b2b" in dframe.columns and "finish_diff" in dframe.columns:
                X["away_b2b_home_strength"] = dframe["away_b2b"] * dframe["finish_diff"]
            # Symbolic features if available
            if all(k in dframe.columns for k in ["home_xg", "away_xg", "home_elo", "away_elo", "home_sos", "away_sos", "elo_diff", "l10_xg_diff"]):
                X["pressure_index"] = (dframe["home_xg"] / (dframe["away_xg"] + 0.1)) * (dframe["home_elo"] / (dframe["away_elo"] + 0.1))
                X["xg_efficiency"] = (dframe["home_xg"] * (dframe["home_sos"] / 1500.0)) - (dframe["away_xg"] * (dframe["away_sos"] / 1500.0))
                X["power_momentum"] = dframe["elo_diff"] * dframe["l10_xg_diff"]
            # Keep prune list consistent
            prune = [
                "home_venue_goal_diff", "away_venue_goal_diff", "l5_pizza_diff",
                "l5_nzt_diff", "l5_rush_diff", "l5_pk_diff", "l5_pp_diff",
                "l5_ozs_diff", "l5_hdc_diff",
            ]
            for col in prune:
                if col in X.columns:
                    X.drop(columns=[col], inplace=True)
            return X

        X_train = build_X(train_df)
        y_train = train_df["target"].astype(int).values
        X_test = build_X(test_df)
        y_test = test_df["target"].astype(int).values

        # Recency weights inside train fold
        n_train = len(train_df)
        ages = (n_train - 1) - np.arange(n_train, dtype=float)
        w = 0.5 ** (ages / 60.0)
        late_mask = train_df["season_month"].isin([3, 4]).values if "season_month" in train_df.columns else np.zeros(n_train, dtype=bool)
        w[late_mask] *= 1.25

        # Fit model (clone-ish by re-instantiating when possible)
        model = xgb.XGBClassifier(
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            **{k: getattr(base_model, k) for k in ["max_depth", "learning_rate", "n_estimators", "subsample", "colsample_bytree", "gamma"] if hasattr(base_model, k)},
        )
        model.fit(X_train, y_train, sample_weight=w)

        if calibrated:
            # Calibrate on the last 20% of the training fold (future within fold),
            # then evaluate on the test fold.
            fold_n = len(X_train)
            fold_cal_start = int(fold_n * 0.80)
            X_tr = X_train.iloc[:fold_cal_start]
            y_tr = y_train[:fold_cal_start]
            X_ca = X_train.iloc[fold_cal_start:]
            y_ca = y_train[fold_cal_start:]
            w_tr = w[:fold_cal_start]

            model.fit(X_tr, y_tr, sample_weight=w_tr)
            cal = CalibratedClassifierCV(estimator=model, method="isotonic", cv="prefit")
            cal.fit(X_ca, y_ca)
            p = cal.predict_proba(X_test)[:, 1]
        else:
            p = model.predict_proba(X_test)[:, 1]

        preds = (p >= 0.5).astype(int)
        accs.append(float(accuracy_score(y_test, preds)))
        lls.append(float(log_loss(y_test, np.clip(p, 1e-6, 1 - 1e-6))))
        briers.append(float(brier_score_loss(y_test, p)))

        # Elo baseline: update Elo with training fold results, then predict test fold.
        elo = EloTracker()
        for _, row in train_df.iterrows():
            # target==1 => home win
            home = row["home_team"]
            away = row["away_team"]
            # Update with a synthetic 1-goal margin just to record outcome
            if int(row["target"]) == 1:
                elo.update(home, away, 2, 1)
            else:
                elo.update(home, away, 1, 2)

        elo_p = []
        for _, row in test_df.iterrows():
            home = row["home_team"]
            away = row["away_team"]
            elo_home = float(elo.get_win_prob(home, away))
            elo_p.append(elo_home)
        elo_p = np.array(elo_p, dtype=float)
        elo_preds = (elo_p >= 0.5).astype(int)
        elo_accs.append(float(np.mean(elo_preds == y_test)))
        elo_lls.append(float(log_loss(y_test, np.clip(elo_p, 1e-6, 1 - 1e-6))))

        splits_used += 1

    return {
        "mean_acc": float(np.mean(accs)) if accs else float("nan"),
        "mean_logloss": float(np.mean(lls)) if lls else float("nan"),
        "mean_brier": float(np.mean(briers)) if briers else float("nan"),
        "n_splits_used": int(splits_used),
        "elo_mean_acc": float(np.mean(elo_accs)) if elo_accs else float("nan"),
        "elo_mean_logloss": float(np.mean(elo_lls)) if elo_lls else float("nan"),
    }


def rolling_recent_eval(df: pd.DataFrame, recent_n: int = 200, n_splits: int = 4) -> Dict[str, float]:
    """Evaluate XGB vs Elo on the same forward windows for the most recent games."""
    df = df.sort_values("date").reset_index(drop=True)
    if len(df) < (recent_n + 200):
        # Need enough history to make training folds meaningful
        recent_n = min(recent_n, max(0, len(df) - 200))
    recent_df = df.iloc[-recent_n:].copy()
    if len(recent_df) < 60:
        raise ValueError("Not enough rows for recent evaluation")

    tscv = TimeSeriesSplit(n_splits=max(2, int(n_splits)))

    xgb_probs = []
    xgb_y = []
    elo_probs = []
    elo_y = []

    # Use a moderate, non-extreme XGB config to avoid producing saturated
    # probabilities that can dominate log loss. The goal is apples-to-apples
    # comparison on identical windows, not micro-optimizing this evaluator.

    def build_X_with_train_encodings(tr_df: pd.DataFrame, dframe: pd.DataFrame) -> pd.DataFrame:
        """Build feature matrix using the same transforms as training (leakage-safe)."""
        base_feats = [c for c in tr_df.columns if c not in ["game_id", "date", "target", "margin", "p1_target"]]
        home_map, home_prior = calculate_target_encoding(tr_df, "home_team")
        away_map, away_prior = calculate_target_encoding(tr_df, "away_team", target="target")
        X = dframe[base_feats].copy()
        X["home_win_rate"] = dframe["home_team"].map(home_map).fillna(home_prior)
        X["away_win_rate"] = dframe["away_team"].map(away_map).fillna(away_prior)
        X.drop(columns=["home_team", "away_team"], inplace=True)

        if "away_sos" in dframe.columns:
            X["home_win_rate_away_sos"] = X["home_win_rate"] * dframe["away_sos"]
        if "away_b2b" in dframe.columns and "finish_diff" in dframe.columns:
            X["away_b2b_home_strength"] = dframe["away_b2b"] * dframe["finish_diff"]

        if all(k in dframe.columns for k in ["home_xg", "away_xg", "home_elo", "away_elo"]):
            X["pressure_index"] = (dframe["home_xg"] / (dframe["away_xg"] + 0.1)) * (dframe["home_elo"] / (dframe["away_elo"] + 0.1))
        if all(k in dframe.columns for k in ["home_xg", "away_xg", "home_sos", "away_sos"]):
            X["xg_efficiency"] = (dframe["home_xg"] * (dframe["home_sos"] / 1500.0)) - (dframe["away_xg"] * (dframe["away_sos"] / 1500.0))
        if all(k in dframe.columns for k in ["elo_diff", "l10_xg_diff"]):
            X["power_momentum"] = dframe["elo_diff"] * dframe["l10_xg_diff"]

        prune = [
            "home_win_rate",
            "home_venue_goal_diff", "away_venue_goal_diff", "l5_pizza_diff",
            "l5_nzt_diff", "l5_rush_diff", "l5_pk_diff", "l5_pp_diff",
            "l5_ozs_diff", "l5_hdc_diff",
        ]
        for col in prune:
            if col in X.columns:
                X.drop(columns=[col], inplace=True)
        return X

    for tr_idx, te_idx in tscv.split(recent_df):
        tr = recent_df.iloc[tr_idx].copy()
        te = recent_df.iloc[te_idx].copy()
        if len(te) < 10 or len(tr) < 80:
            continue

        X_tr_full = build_X_with_train_encodings(tr, tr)
        y_tr_full = tr["target"].astype(int).values
        X_te = build_X_with_train_encodings(tr, te)
        y_te = te["target"].astype(int).values

        # Recency weights within the train split
        ntr = len(tr)
        ages = (ntr - 1) - np.arange(ntr, dtype=float)
        w = 0.5 ** (ages / 60.0)

        # Inner-split future calibration
        cal_start = int(ntr * 0.80)
        X_tr = X_tr_full.iloc[:cal_start]
        y_tr = y_tr_full[:cal_start]
        X_ca = X_tr_full.iloc[cal_start:]
        y_ca = y_tr_full[cal_start:]
        w_tr = w[:cal_start]

        model = xgb.XGBClassifier(
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            max_depth=3,
            learning_rate=0.03,
            n_estimators=80,
            subsample=0.85,
            colsample_bytree=0.85,
            gamma=0.0,
            reg_lambda=1.0,
        )
        model.fit(X_tr, y_tr, sample_weight=w_tr)
        # Calibrate only if we have a non-degenerate calibration slice.
        # Isotonic on small/imbalanced slices can produce saturated 0/1 probs,
        # which makes log loss meaningless for comparison.
        if len(np.unique(y_ca)) < 2 or len(y_ca) < 30:
            p = model.predict_proba(X_te)[:, 1]
        else:
            cal = CalibratedClassifierCV(estimator=model, method="sigmoid", cv="prefit")
            cal.fit(X_ca, y_ca)
            p = cal.predict_proba(X_te)[:, 1]

        xgb_probs.extend(p.tolist())
        xgb_y.extend(y_te.tolist())

        # Elo baseline on the same windows: train Elo on tr outcomes, predict te.
        elo = EloTracker()
        for _, row in tr.iterrows():
            home = row["home_team"]
            away = row["away_team"]
            if int(row["target"]) == 1:
                elo.update(home, away, 2, 1)
            else:
                elo.update(home, away, 1, 2)

        elo_p = []
        for _, row in te.iterrows():
            elo_p.append(float(elo.get_win_prob(row["home_team"], row["away_team"])))
        elo_probs.extend(elo_p)
        elo_y.extend(y_te.tolist())

    if not xgb_probs or not elo_probs:
        raise ValueError("Recent evaluation produced no predictions")

    xgb_probs = np.clip(np.array(xgb_probs, dtype=float), 1e-6, 1 - 1e-6)
    elo_probs = np.clip(np.array(elo_probs, dtype=float), 1e-6, 1 - 1e-6)
    y = np.array(xgb_y, dtype=int)
    y2 = np.array(elo_y, dtype=int)
    # Sanity: align lengths
    m = min(len(y), len(y2), len(xgb_probs), len(elo_probs))
    y = y[:m]
    y2 = y2[:m]
    xgb_probs = xgb_probs[:m]
    elo_probs = elo_probs[:m]

    out = {
        "recent_n": int(recent_n),
        "xgb_recent_logloss": float(log_loss(y, xgb_probs)),
        "xgb_recent_acc": float(np.mean((xgb_probs >= 0.5) == (y >= 0.5))),
        "elo_recent_logloss": float(log_loss(y2, elo_probs)),
        "elo_recent_acc": float(np.mean((elo_probs >= 0.5) == (y2 >= 0.5))),
    }
    # Diagnostic percentiles to sanity-check calibration/overconfidence
    out["xgb_recent_p05"] = float(np.quantile(xgb_probs, 0.05))
    out["xgb_recent_p50"] = float(np.quantile(xgb_probs, 0.50))
    out["xgb_recent_p95"] = float(np.quantile(xgb_probs, 0.95))
    return out


def elo_logloss_on_test(train_df: pd.DataFrame, test_df: pd.DataFrame) -> float:
    """Compute Elo log loss on `test_df`, with Elo fit on `train_df` only."""
    elo = EloTracker()
    train_df = train_df.sort_values("date")
    test_df = test_df.sort_values("date")
    for _, row in train_df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        if int(row["target"]) == 1:
            elo.update(home, away, 2, 1)
        else:
            elo.update(home, away, 1, 2)
    probs = []
    y = []
    for _, row in test_df.iterrows():
        probs.append(float(elo.get_win_prob(row["home_team"], row["away_team"])))
        y.append(int(row["target"]))
    probs = np.clip(np.array(probs, dtype=float), 1e-6, 1 - 1e-6)
    return float(log_loss(np.array(y, dtype=int), probs))


def _audit_no_postgame_feature_leakage(df: pd.DataFrame) -> None:
    """Fail fast if any obviously post-game fields appear in features."""
    forbidden = {
        "actual_home_score",
        "actual_away_score",
        "home_goals",
        "away_goals",
        "home_score",
        "away_score",
        "final_score",
        "actual_winner",
        "home_shots_final",
        "away_shots_final",
    }
    cols = set(df.columns)
    leaked = sorted([c for c in forbidden if c in cols])
    if leaked:
        raise ValueError(f"Post-game columns present in training dataframe: {leaked}")

    # Ensure we never accidentally keep team identifiers as numeric leak channels.
    if "home_team" not in cols or "away_team" not in cols:
        raise ValueError("Expected team id columns missing (audit cannot validate encoding path)")


def prune_unstable_features(
    X_train: pd.DataFrame,
    X_cal: pd.DataFrame,
    X_test: pd.DataFrame,
    recent_n: int = 200,
    max_missing: float = 0.15,
    max_zero_frac: float = 0.90,
    min_std: float = 1e-8,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list]:
    """Drop features that look broken/unstable in the most recent window."""
    if not isinstance(X_train, pd.DataFrame):
        raise TypeError("X_train must be a DataFrame")
    if X_train.empty:
        return X_train, X_cal, X_test, []

    recent = X_train.tail(int(recent_n)) if len(X_train) > recent_n else X_train
    dropped = []

    for col in list(X_train.columns):
        s = recent[col]
        # Missingness
        miss = float(s.isna().mean())
        if miss > float(max_missing):
            dropped.append(col)
            continue
        # Zero fraction (for numeric)
        try:
            zero_frac = float((s.fillna(0) == 0).mean())
        except Exception:
            zero_frac = 0.0
        if zero_frac > float(max_zero_frac):
            dropped.append(col)
            continue
        # Near-constant
        try:
            sd = float(np.nanstd(s.astype(float).values))
        except Exception:
            sd = float("inf")
        if sd < float(min_std):
            dropped.append(col)

    if dropped:
        X_train = X_train.drop(columns=dropped, errors="ignore")
        X_cal = X_cal.drop(columns=dropped, errors="ignore")
        X_test = X_test.drop(columns=dropped, errors="ignore")

    return X_train, X_cal, X_test, dropped


def confidence_bucket_report(y_true, p_home, min_conf_levels=None) -> Dict[str, object]:
    """Report accuracy/logloss by confidence bucket using P(max side)."""
    y = np.array(y_true, dtype=int)
    p = np.clip(np.array(p_home, dtype=float), 1e-6, 1 - 1e-6)
    if y.size != p.size:
        raise ValueError("y_true and p_home must have same length")

    conf = np.maximum(p, 1.0 - p)
    if min_conf_levels is None:
        min_conf_levels = [0.50, 0.55, 0.60, 0.65, 0.70]

    buckets = []
    for thr in min_conf_levels:
        mask = conf >= float(thr)
        n = int(mask.sum())
        if n == 0:
            buckets.append({"min_conf": float(thr), "n": 0, "acc": None, "logloss": None})
            continue
        p_sub = p[mask]
        y_sub = y[mask]
        preds = (p_sub >= 0.5).astype(int)
        buckets.append(
            {
                "min_conf": float(thr),
                "n": n,
                "acc": float(np.mean(preds == y_sub)),
                "logloss": float(log_loss(y_sub, p_sub)),
            }
        )

    return {"buckets": buckets}


if __name__ == "__main__":
    train_optimized_model()
