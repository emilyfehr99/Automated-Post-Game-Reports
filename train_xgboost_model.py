import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, TimeSeriesSplit, GridSearchCV
from sklearn.metrics import accuracy_score, log_loss, classification_report
import xgboost as xgb
import pickle
import math
from datetime import datetime, timedelta

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
        self.stats = {} # {goalie_name: {'gsax': []}}
        
    def update(self, name, gsax):
        if not name: return
        if name not in self.stats:
            self.stats[name] = {'gsax': []}
        self.stats[name]['gsax'].append(gsax)
        
    def get_rolling_gsax(self, name, window=5):
        if not name or name not in self.stats or not self.stats[name]['gsax']:
            return 0.0
        vals = self.stats[name]['gsax'][-window:]
        return np.mean(vals)

class TeamHistory:
    def __init__(self):
        self.history = {}  # {team_abbr: {'dates': [], 'stats': [], 'home_stats': [], 'away_stats': [], 'opponents_elo': []}}
        self.elo = EloTracker()
        self.goalies = GoalieHistory()
        
    def update(self, team, date, game_stats, venue=None, opponent_elo=None):
        """Update team history with a new game"""
        if team not in self.history:
            self.history[team] = {'dates': [], 'stats': [], 'home_stats': [], 'away_stats': [], 'opponents_elo': []}
            
        self.history[team]['dates'].append(date)
        self.history[team]['stats'].append(game_stats)
        
        if opponent_elo is not None:
            self.history[team]['opponents_elo'].append(opponent_elo)
        
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

def extract_features_chronologically(predictions):
    # Sort by date
    print("Sorting games chronologically...")
    sorted_preds = sorted(predictions, key=lambda x: x['date'])
    
    tracker = TeamHistory()
    profiles = load_profiles() # Load finishing profiles
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
        h_gsax_roll = tracker.get_goalie_gsax(h_goalie)
        a_gsax_roll = tracker.get_goalie_gsax(a_goalie)
        
        # Finish Factors
        h_finish = profiles.get(home, 1.0)
        a_finish = profiles.get(away, 1.0)
        
        if winner_side:
            row = {
                'game_id': game_id,
                'date': game_date,
                'target': 1 if winner_side == 'home' else 0,
                
                # ELO
                'elo_diff': (home_elo + tracker.elo.ha) - away_elo,
                
                # Finish Factor
                'finish_diff': h_finish - a_finish,
                
                # Goalie GSAx
                'gsax_diff': h_gsax_roll - a_gsax_roll,
                
                # Rest / B2B
                'rest_diff': home_rest - away_rest,
                'home_b2b': 1 if home_rest == 1 else 0,
                'away_b2b': 1 if away_rest == 1 else 0,
                
                # Rolling General (EWMA)
                'l5_goal_diff': h_l5.get('goal_diff', 0) - a_l5.get('goal_diff', 0),
                'l5_xg_diff': h_l5.get('xg_diff', 0) - a_l5.get('xg_diff', 0),
                'l5_corsi_diff': h_l5.get('corsi_pct', 50) - a_l5.get('corsi_pct', 50),
                'l5_pdo_diff': h_l5.get('pdo', 100) - a_l5.get('pdo', 100),
                
                # Special Teams
                'l5_pp_diff': h_l5.get('pp_pct', 20) - a_l5.get('pp_pct', 20),
                'l5_pk_diff': h_l5.get('pk_pct', 80) - a_l5.get('pk_pct', 80),
                'l5_st_net': (h_l5.get('pp_pct', 20) + h_l5.get('pk_pct', 80)) - (a_l5.get('pp_pct', 20) + a_l5.get('pk_pct', 80)),
                
                # Technical Metrics (Rush, Transitions, HDC)
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
        
        # Goalie Update (GSAx = xG - Goals)
        tracker.update_goalie(h_goalie, h_xg - h_score)
        tracker.update_goalie(a_goalie, a_xg - a_score)
        
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
        
        tracker.update(home, game_date, h_stats, venue='home', opponent_elo=curr_a_elo)
        tracker.update(away, game_date, a_stats, venue='away', opponent_elo=curr_h_elo)
        
    return pd.DataFrame(training_data)

def train_optimized_model():
    print("🚀 STARTING ELO + ADVANCED MODEL TRAINING")
    print("=" * 60)
    
    raw_preds = load_data()
    df = extract_features_chronologically(raw_preds)
    
    if len(df) < 100:
        print("⚠️ Not enough samples for training.")
        return
        
    print(f"✅ Extracted {len(df)} training samples with Elo + Goalie + PDO")
    df = df.sort_values('date')
    
    # Use 90/10 split for small dataset
    split_idx = int(len(df) * 0.90)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    features = [c for c in df.columns if c not in ['game_id', 'date', 'target']]
    X_train = train_df[features]
    y_train = train_df['target']
    X_test = test_df[features]
    y_test = test_df['target']
    
    print(f"Training on {len(X_train)} older games, Testing on {len(X_test)} most recent games")
    
    # Fixed stable parameters for small dataset
    model = xgb.XGBClassifier(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=3,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='binary:logistic',
        eval_metric='logloss',
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print("\n" + "="*30)
    print(f"HOLDOUT RESULTS (Last {len(X_test)} games):")
    print(f"Accuracy: {acc:.1%}")
    print("="*30)
    
    imp = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
    print("\nTop Predictors:")
    print(imp.head(10))
    
    # Save if accuracy is reasonable (> 50% which is baseline)
    if acc >= 0.50:
        model.save_model("xgb_nhl_model.json")
        print("\n💾 Saved optimized model to xgb_nhl_model.json")
        with open("xgb_features.pkl", "wb") as f:
            pickle.dump(features, f)
    else:
         print("\n⚠️ Holdout accuracy too low, did not save model.")

if __name__ == "__main__":
    train_optimized_model()
