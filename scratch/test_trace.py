import json
import sys
sys.path.append('.')
from daily_prediction_notifier import DailyPredictionNotifier

notifier = DailyPredictionNotifier()
today = "2026-04-29"
games = notifier.rotowire.scrape_daily_data()

for game in games:
    if game['away_team'] == 'UTA':
        score_pred = notifier.score_model.predict_score(game['away_team'], game['home_team'], is_playoff=True)
        print("ScoreModel output:", score_pred['away_score'], score_pred['home_score'])
