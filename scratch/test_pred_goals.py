import json
import sys
sys.path.append('.')
from daily_prediction_notifier import DailyPredictionNotifier

notifier = DailyPredictionNotifier()
pred = notifier.meta_ensemble.predict(
    away_team="UTA",
    home_team="VGK",
    game_date="2026-04-29",
    is_playoff=True
)
print("Meta ensemble goals:")
print(pred.get("predicted_home_goals"), pred.get("predicted_away_goals"))
