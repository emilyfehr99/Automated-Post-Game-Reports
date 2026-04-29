import sys
sys.path.append('.')
from daily_prediction_notifier import DailyPredictionNotifier
from rotowire_scraper import RotoWireScraper
import json

notifier = DailyPredictionNotifier()
scraper = RotoWireScraper()
today = "2026-04-29"
games = notifier.schedule.games_by_date.get(today, [])
if not games:
    games = scraper.get_todays_games()

for game in games:
    print(f"--- {game['away_team']} @ {game['home_team']} ---")
    score_pred = notifier.score_model.predict_score(game['away_team'], game['home_team'], is_playoff=True)
    print(f"Score model: away={score_pred['away_score']}, home={score_pred['home_score']}")
    
    pred = notifier.meta_ensemble.predict(away_team=game['away_team'], home_team=game['home_team'], game_date=today, is_playoff=True)
    print(f"Meta model goals: away={pred.get('predicted_away_goals')}, home={pred.get('predicted_home_goals')}")
