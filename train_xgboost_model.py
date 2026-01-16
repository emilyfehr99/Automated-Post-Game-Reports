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

class TeamHistory:
    def __init__(self):
        self.history = {}  # {team_abbr: {'dates': [], 'stats': []}}
        self.elo = EloTracker()
        
    def update(self, team, date, game_stats):
        """Update team history with a new game"""
        if team not in self.history:
            self.history[team] = {'dates': [], 'stats': []}
            
        self.history[team]['dates'].append(date)
        self.history[team]['stats'].append(game_stats)
        
    def update_elo(self, home, away, h_score, a_score):
        self.elo.update(home, away, h_score, a_score)
        
    def get_elo(self, team):
        return self.elo.get_rating(team)

    def get_days_rest(self, team, current_date):
        """Get days since last game"""
        if team not in self.history or not self.history[team]['dates']:
            return 3  # Default to reasonable rest
            
        last_date = self.history[team]['dates'][-1]
        delta = (current_date - last_date).days
        return max(1, delta)
        
    def get_rolling_stats(self, team, window=5):
        """Calculate rolling averages"""
        if team not in self.history or len(self.history[team]['stats']) < 1:
            return {}
            
        stats_list = self.history[team]['stats'][-window:]
        aggregated = {}
        if not stats_list:
            return {}
            
        keys = stats_list[0].keys()
        for k in keys:
            vals = [g[k] for g in stats_list if g.get(k) is not None]
            if vals:
                aggregated[k] = np.mean(vals)
            else:
                aggregated[k] = 0.0
        return aggregated

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
    training_data = []
    
    print("Generating rolling features + Elo...")
    
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
        
        h_l5 = tracker.get_rolling_stats(home, 5)
        a_l5 = tracker.get_rolling_stats(away, 5)
        h_l10 = tracker.get_rolling_stats(home, 10)
        a_l10 = tracker.get_rolling_stats(away, 10)
        
        if winner_side:
            row = {
                'game_id': game_id,
                'date': game_date,
                'target': 1 if winner_side == 'home' else 0,
                
                # ELO: The big new feature
                'elo_diff': (home_elo + tracker.elo.ha) - away_elo,
                
                # Rest
                'rest_diff': home_rest - away_rest,
                'home_fatigue': 1 if home_rest <= 1 else 0,
                'away_fatigue': 1 if away_rest <= 1 else 0,
                
                # Rolling
                'l5_goal_diff': h_l5.get('goal_diff', 0) - a_l5.get('goal_diff', 0),
                'l5_xg_diff': h_l5.get('xg_diff', 0) - a_l5.get('xg_diff', 0),
                'l5_corsi_diff': h_l5.get('corsi_pct', 50) - a_l5.get('corsi_pct', 50),
                'l5_pdo_diff': h_l5.get('pdo', 100) - a_l5.get('pdo', 100),
                'l5_pp_diff': h_l5.get('pp_pct', 20) - a_l5.get('pp_pct', 20),
                
                'l10_goal_diff': h_l10.get('goal_diff', 0) - a_l10.get('goal_diff', 0),
                'l10_xg_diff': h_l10.get('xg_diff', 0) - a_l10.get('xg_diff', 0),
            }
            training_data.append(row)
            
        # 2. UPDATE HISTORY
        h_score = float(metrics.get('home_goals', 0) or p.get('actual_home_score', 0) or 0)
        a_score = float(metrics.get('away_goals', 0) or p.get('actual_away_score', 0) or 0)
        
        tracker.update_elo(home, away, h_score, a_score)
        
        h_xg = float(metrics.get('home_xg', 0) or 0)
        a_xg = float(metrics.get('away_xg', 0) or 0)
        h_corsi = float(metrics.get('home_corsi_pct', 50) or 50)
        a_corsi = float(metrics.get('away_corsi_pct', 50) or 50)
        
        h_stats = {'goal_diff': h_score - a_score, 'xg_diff': h_xg - a_xg, 'corsi_pct': h_corsi, 'pdo': 100.0, 'pp_pct': float(metrics.get('home_power_play_pct', 0) or 0)}
        a_stats = {'goal_diff': a_score - h_score, 'xg_diff': a_xg - h_xg, 'corsi_pct': a_corsi, 'pdo': 100.0, 'pp_pct': float(metrics.get('away_power_play_pct', 0) or 0)}
        
        tracker.update(home, game_date, h_stats)
        tracker.update(away, game_date, a_stats)
        
    return pd.DataFrame(training_data)

def train_optimized_model():
    print("🚀 STARTING ELO + ADVANCED MODEL TRAINING")
    print("=" * 60)
    
    raw_preds = load_data()
    df = extract_features_chronologically(raw_preds)
    
    if len(df) < 100:
        return
        
    print(f"✅ Extracted {len(df)} training samples with Elo + Rolling Features")
    df = df.sort_values('date')
    
    split_idx = int(len(df) * 0.85)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    features = [c for c in df.columns if c not in ['game_id', 'date', 'target']]
    X_train = train_df[features]
    y_train = train_df['target']
    X_test = test_df[features]
    y_test = test_df['target']
    
    print(f"Training on {len(X_train)} older games, Testing on {len(X_test)} most recent games")
    
    # Simple hyperparameters derived from previous Grid Search to save time
    # {'colsample_bytree': 0.7, 'learning_rate': 0.1, 'max_depth': 4, 'n_estimators': 100, 'subsample': 0.7}
    
    model = xgb.XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=4,
        subsample=0.7,
        colsample_bytree=0.7,
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
    
    if acc > 0.55:
        model.save_model("xgb_nhl_model.json")
        print("\n💾 Saved optimized model to xgb_nhl_model.json")
        with open("xgb_features.pkl", "wb") as f:
            pickle.dump(features, f)

if __name__ == "__main__":
    train_optimized_model()
