import sys
sys.path.append('.')
import xgboost as xgb
import shap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from models.train_xgboost_model import load_data, extract_features_chronologically, _build_matrices_and_sidecars

def run_shap_audit():
    print("🏒 Starting Quarterly SHAP Audit...")
    
    # 1. Load Data
    print("Loading data...")
    predictions = load_data()
    df = extract_features_chronologically(predictions)
    
    # Sort chronologically to get the latest games for the test set
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # Use the last 20% as a test set for the audit
    test_idx = int(len(df) * 0.8)
    test_df = df.iloc[test_idx:].copy()
    
    # Process features (drop metadata)
    drop_cols = ['game_id', 'date', 'home_team', 'away_team', 'target', 'total_goals', 'home_goals', 'away_goals', 'score_winner_is_home']
    
    X_test = test_df.drop(columns=[c for c in drop_cols if c in test_df.columns])
    
    # Clean up column names for XGBoost
    import re
    X_test = X_test.rename(columns=lambda x: re.sub('[^A-Za-z0-9_]+', '', x))
    X_test = X_test.fillna(0) # Basic imputation
    
    # Ensure all columns are numeric
    for col in X_test.columns:
        if not pd.api.types.is_numeric_dtype(X_test[col]):
            try:
                X_test[col] = X_test[col].astype(float)
            except:
                X_test = X_test.drop(columns=[col])

    # 2. Load the main model
    model_path = "models/xgb_nhl_model.json"
    if not os.path.exists(model_path):
        model_path = "xgb_nhl_model.json" # might be in root
    
    if not os.path.exists(model_path):
        print(f"❌ Could not find model at {model_path}. Exiting.")
        return
        
    print(f"Loading model from {model_path}...")
    model = xgb.Booster()
    model.load_model(model_path)
    
    # 3. Align columns to match model
    model_features = model.feature_names
    missing_cols = set(model_features) - set(X_test.columns)
    for col in missing_cols:
        X_test[col] = 0.0
    X_test = X_test[model_features] # reorder and select
    
    # 4. Run SHAP Explainability
    print(f"Running SHAP TreeExplainer on {len(X_test)} samples (with {len(model_features)} features)...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    
    # Calculate mean absolute SHAP values for global feature importance
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    
    importance_df = pd.DataFrame({
        'Feature': X_test.columns,
        'Mean |SHAP|': mean_abs_shap
    }).sort_values('Mean |SHAP|', ascending=False).reset_index(drop=True)
    
    print("\n🏆 Top 20 Most Important Features (SHAP):")
    print(importance_df.head(20).to_string(index=False))
    
    # Focus analysis on overused elements requested by user
    print("\n🔍 Overused Elements Audit:")
    overused = ['h_xg_10d', 'h_xg_20d', 'a_xg_10d', 'a_xg_20d', 'h_corsi_pct', 'a_corsi_pct']
    for feat in overused:
        if feat in importance_df['Feature'].values:
            val = importance_df[importance_df['Feature'] == feat]['Mean |SHAP|'].values[0]
            rank = importance_df.index[importance_df['Feature'] == feat].tolist()[0] + 1
            print(f"  • {feat}: Rank {rank}, Impact {val:.4f}")
        else:
            print(f"  • {feat}: Not found in model features")
            
    edge_feats = ['h_bursts_20mph', 'a_bursts_20mph', 'h_oz_time_pct', 'a_oz_time_pct']
    print("\n🔍 Edge Tracking Features Audit:")
    for feat in edge_feats:
        if feat in importance_df['Feature'].values:
            val = importance_df[importance_df['Feature'] == feat]['Mean |SHAP|'].values[0]
            rank = importance_df.index[importance_df['Feature'] == feat].tolist()[0] + 1
            print(f"  • {feat}: Rank {rank}, Impact {val:.4f}")
        else:
            print(f"  • {feat}: Not found in model features")

    # Generate Calibration Data for Plot
    print("\n📊 Generating Decile Calibration Data...")
    y_true = test_df['target'].values
    dtest = xgb.DMatrix(X_test)
    y_pred = model.predict(dtest)
    
    # Apply Isotonic from the file?
    # Actually, we can just bin P(win) and see the calibration before/after isotonic.
    df_cal = pd.DataFrame({'pred': y_pred, 'actual': y_true})
    df_cal['decile'] = pd.qcut(df_cal['pred'], 10, duplicates='drop')
    cal_summary = df_cal.groupby('decile', observed=False).agg(
        mean_pred=('pred', 'mean'),
        observed_win_rate=('actual', 'mean'),
        count=('actual', 'count')
    ).reset_index()
    
    print("\n📈 Calibration Plot Data (Bin P(win) vs Observed):")
    print(cal_summary.to_string(index=False))
    
    # Save text report
    with open("artifacts/shap_audit_report.txt", "w") as f:
        f.write("SHAP AUDIT REPORT\n")
        f.write("=================\n")
        f.write(importance_df.head(50).to_string(index=False))
        f.write("\n\nCALIBRATION:\n")
        f.write(cal_summary.to_string(index=False))
        
    print("\n✅ Audit complete. Saved to artifacts/shap_audit_report.txt.")

if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)
    run_shap_audit()
