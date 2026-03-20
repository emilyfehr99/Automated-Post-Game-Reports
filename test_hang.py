import logging
from daily_prediction_notifier import DailyPredictionNotifier
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger('test')

def run_test():
    notifier = DailyPredictionNotifier()
    logger.info("Starting FIRST call to get_daily_predictions_summary")
    summary1 = notifier.get_daily_predictions_summary()
    logger.info("Finished FIRST call")
    
    logger.info("Starting SECOND call to get_daily_predictions_summary (as in save_to_file)")
    summary2 = notifier.get_daily_predictions_summary()
    logger.info("Finished SECOND call")

if __name__ == "__main__":
    run_test()
