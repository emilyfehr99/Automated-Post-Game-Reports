import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from daily_prediction_notifier import DailyPredictionNotifier
import json

notifier = DailyPredictionNotifier()

# Mock the Rotowire scrape and Vegas odds
notifier.rotowire.scrape_daily_data = lambda: {'games': [{'away_team': 'TOR', 'home_team': 'BOS'}]}

# We'll just patch `_market_odds` and bypass `fail_fast_if_stale`
import vegas_odds_scraper
vegas_odds_scraper.scrape_vegas_odds = lambda: {}
import utils.freshness_guard
utils.freshness_guard.fail_fast_if_stale = lambda **kwargs: None

# Mock NHL schedule
from nhl_api_client import NHLAPIClient
NHLAPIClient.get_game_schedule = lambda self: {'games': [{'awayTeam': {'abbrev': 'TOR'}, 'homeTeam': {'abbrev': 'BOS'}, 'id': 123, 'gameType': 3}]}

summary = notifier.get_daily_predictions_summary()
print(summary)
