import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from daily_prediction_notifier import DailyPredictionNotifier
notifier = DailyPredictionNotifier()
print(notifier.get_daily_predictions_summary())
