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
        self.history[team]['last_city'] = city or team # Default to home city if not provided
        
        if opponent_elo is not None:
            self.history[team]['opponents_elo'].append(opponent_elo)

    def get_travel_distance(self, team, current_city):
        """Distance traveled since last game"""
        if team not in self.history or not self.history[team]['last_city']:
            return 0.0
        return calculate_distance(self.history[team]['last_city'], current_city)
        
        if venue == 'home':
            self.history[team]['home_stats'].append(game_stats)
        elif venue == 'away':
            self.history[team]['away_stats'].append(game_stats)
            
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
    sorted_preds = sorted(predictions, key=lambda x: x['date'])
    
    tracker = TeamHistory()
    profiles = load_profiles() # Load finishing profiles
    edge_data = load_edge_data() # Load NHL Edge speed profiles
    training_data = []
    
    print("Generating rolling features + Elo + Finish Factors...")
    
    for p in sorted_preds:
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
                'margin': h_score_final - a_score_final,
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
            'pk_pct': h_pk,
            'rush': float(p.get('home_rush', 2) or 2),
            'nzt': float(p.get('home_nzt', 5) or 5),
            'ozs': float(p.get('home_ozs', 10) or 10),
            'hdc': float(metrics.get('home_hdc', 5) or 5),
            'pizzas': float(p.get('home_hd_giveaways', 2) or 2)
        }
        a_stats = {
            'goal_diff': a_score - h_score, 
            'xg_diff': a_xg - h_xg, 
            'corsi_pct': a_corsi, 
            'pdo': a_pdo, 
            'pp_pct': a_pp,
            'pk_pct': a_pk,
            'rush': float(p.get('away_rush', 2) or 2),
            'nzt': float(p.get('away_nzt', 5) or 5),
            'ozs': float(p.get('away_ozs', 10) or 10),
            'hdc': float(metrics.get('away_hdc', 5) or 5),
            'pizzas': float(p.get('away_hd_giveaways', 2) or 2)
        }
        
        tracker.update(home, game_date, h_stats, venue='home', opponent_elo=curr_a_elo, city=home)
        tracker.update(away, game_date, a_stats, venue='away', opponent_elo=curr_h_elo, city=home)
        
    train_df = pd.DataFrame(training_data)
    
    # NEW: Add Team Mean Win Rate (Target Encoding) for Train/Test split
    # We do this later in the main loop to avoid leakage, but here's the mapping
    return train_df

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
    
    # Use 90/10 split for small dataset
    split_idx = int(len(df) * 0.90)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    features = [c for c in df.columns if c not in ['game_id', 'date', 'target', 'margin']]
    X_train = train_df[features].copy()
    y_train = train_df['target']
    y_margin_train = train_df['margin']
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
    X_test = X_test.drop(columns=['home_team', 'away_team'])
    
    # NEW: Final feature sync for interaction terms
    X_train['home_win_rate_away_sos'] = X_train['home_win_rate'] * train_df['away_sos']
    X_test['home_win_rate_away_sos'] = X_test['home_win_rate'] * test_df['away_sos']
    X_train['away_b2b_home_strength'] = train_df['away_b2b'] * train_df['finish_diff']
    X_test['away_b2b_home_strength'] = test_df['away_b2b'] * test_df['finish_diff']
    
    # Phase 11: Symbolic Feature Discovery
    # 1. Pressure Index: Compounding offensive threat with team quality
    X_train['pressure_index'] = (train_df['home_xg'] / (train_df['away_xg'] + 0.1)) * (train_df['home_elo'] / (train_df['away_elo'] + 0.1))
    X_test['pressure_index'] = (test_df['home_xg'] / (test_df['away_xg'] + 0.1)) * (test_df['home_elo'] / (test_df['away_elo'] + 0.1))
    
    # 2. xG Efficiency: xG relative to opponent strength
    X_train['xg_efficiency'] = (train_df['home_xg'] * (train_df['home_sos'] / 1500)) - (train_df['away_xg'] * (train_df['away_sos'] / 1500))
    X_test['xg_efficiency'] = (test_df['home_xg'] * (test_df['home_sos'] / 1500)) - (test_df['away_xg'] * (test_df['away_sos'] / 1500))
    
    # 3. Power Momentum: Synergy of talent and recent offensive form
    X_train['power_momentum'] = train_df['elo_diff'] * train_df['l10_xg_diff']
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
        if p in X_test.columns: X_test.drop(columns=[p], inplace=True)

    features = [f for f in X_train.columns]
    
    # Sample Weighting: Recent games have more weight (form factor)
    # Give recent 20% of training data 2x weight of older data
    sample_weights = np.ones(len(y_train))
    recent_split = int(len(y_train) * 0.8)
    sample_weights[recent_split:] = 1.5 # 50% more weight to recent form
    
    print(f"Training on {len(X_train)} games, Testing on {len(X_test)} games")
    
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
    
    print("\n🔍 Tuning XGBoost components for ensemble...")
    grid_search = GridSearchCV(
        estimator=base_xgb,
        param_grid=param_grid,
        cv=tscv,
        scoring='accuracy',
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
        scoring='accuracy',
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train, sample_weight=sample_weights)
    best_model = grid_search.best_estimator_
    print(f"✅ Best Params: {grid_search.best_params_}")
    
    # 3b. Probability Calibration
    print("\n⚖️ Calibrating probabilities (Isotonic Phase 9 Refined)...")
    calibrated_model = CalibratedClassifierCV(
        estimator=best_model,
        method='isotonic',
        cv=tscv
    )
    calibrated_model.fit(X_train, y_train, sample_weight=sample_weights)
    
    # Evaluate on Holdout
    y_pred = calibrated_model.predict(X_test)
    y_prob = calibrated_model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    loss = log_loss(y_test, y_prob)
    
    print("\n" + "="*30)
    print(f"FINAL PHASE 9 RESULTS:")
    print(f"Accuracy: {acc:.1%}")
    print(f"Log Loss: {loss:.4f}")
    print("="*30)
    
    # Feature Importance
    imp = pd.Series(best_model.feature_importances_, index=features).sort_values(ascending=False)
    print("\nTop Phase 9 Predictors:")
    print(imp.head(12))
    
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
    
    # 4. SAVE MODELS
    # Since CalibratedClassifierCV is a wrapper, we save it as a pickle
    if acc >= 0.50:
        # Save calibrated model (pickle contains the entire stack + calibrator)
        with open("xgb_calibrated_model.pkl", "wb") as f:
            pickle.dump(calibrated_model, f)
        
        # Save the meta-confidence model
        with open('meta_confidence_model.pkl', 'wb') as f:
            pickle.dump(confidence_model, f)
            
        # Save the margin regression model
        with open('margin_regression_model.pkl', 'wb') as f:
            pickle.dump(margin_model, f)

        # Also save booster as JSON (uncalibrated) for legacy code
        best_xgb.save_model("xgb_nhl_model.json")
        
        print("\n💾 Saved stacked model to xgb_calibrated_model.pkl")
        print("💾 Saved XGB component to xgb_nhl_model.json")
        
        with open("xgb_features.pkl", "wb") as f:
            pickle.dump(features, f)
    else:
         print("\n⚠️ Holdout accuracy too low, did not save model.")

if __name__ == "__main__":
    train_optimized_model()
