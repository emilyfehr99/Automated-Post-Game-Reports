import json
import sys
sys.path.append('.')
from daily_prediction_notifier import DailyPredictionNotifier

notifier = DailyPredictionNotifier()
base_pred = notifier.predictor.learning_model.predict_game("UTA", "VGK")
print(json.dumps(base_pred, indent=2))
