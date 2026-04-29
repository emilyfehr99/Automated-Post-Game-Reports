import json
import sys
sys.path.append('.')
from daily_prediction_notifier import DailyPredictionNotifier

notifier = DailyPredictionNotifier()
pred = notifier.meta_ensemble.predict(
    away_team="UTA",
    home_team="VGK",
    game_date="2026-04-29",
    is_playoff=True,
    series_status="VGK leads 3-1"
)
print("PREDICTED HOME GOALS:", pred.get("predicted_home_goals"))
print("PREDICTED AWAY GOALS:", pred.get("predicted_away_goals"))
