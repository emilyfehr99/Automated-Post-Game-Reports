
import json
import logging
from pathlib import Path
from nhl_api_client import NHLAPIClient

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def backfill():
    predictions_file = Path('data/win_probability_predictions_v2.json')
    if not predictions_file.exists():
        logger.error("File not found")
        return

    with open(predictions_file, 'r') as f:
        data = json.load(f)

    client = NHLAPIClient()
    updated = 0
    
    # Only backfill games that have an actual_winner but NO lead_after_p1
    # AND prioritize regular season games (substring '02' in game_id)
    to_check = [p for p in data['predictions'] if p.get('actual_winner') and 'lead_after_p1' not in p.get('metrics_used', {})]
    to_check = [p for p in to_check if '02' in str(p['game_id'])[4:6]][:50]
    
    logger.info(f"Checking {len(to_check)} recent games for P1 outcomes...")

    for pred in to_check:
        game_id = pred['game_id']
        try:
            url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/landing"
            resp = client.session.get(url, timeout=10)
            if resp.status_code == 200:
                landing_data = resp.json()
                p1_away = 0
                p1_home = 0
                away_abbr = pred.get('away_team')
                home_abbr = pred.get('home_team')
                
                scoring = landing_data.get('summary', {}).get('scoring', [])
                for period_data in scoring:
                    if period_data.get('periodDescriptor', {}).get('number') == 1:
                        for goal in period_data.get('goals', []):
                            goal_team = goal.get('teamAbbrev', {}).get('default')
                            if not goal_team and 'teamAbbrev' in goal:
                                 goal_team = goal['teamAbbrev']
                                 
                            if goal_team == away_abbr:
                                p1_away += 1
                            elif goal_team == home_abbr:
                                p1_home += 1
                
                lead = 0
                if p1_home > p1_away: lead = 1
                elif p1_away > p1_home: lead = -1
                
                if 'metrics_used' not in pred:
                    pred['metrics_used'] = {}
                pred['metrics_used']['lead_after_p1'] = lead
                updated += 1
                logger.info(f"Updated {game_id}: P1 Lead {lead}")
        except Exception as e:
            logger.error(f"Error for {game_id}: {e}")

    if updated > 0:
        with open(predictions_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully backfilled {updated} games.")

if __name__ == "__main__":
    backfill()
