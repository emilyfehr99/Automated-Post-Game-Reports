import json
import sys
sys.path.append('.')
from daily_prediction_notifier import DailyPredictionNotifier

notifier = DailyPredictionNotifier()
predictions = notifier.get_daily_predictions_summary()
print(predictions)
