import requests
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NHLAPIClient:
    """Client for the NHL API (api-web.nhle.com)"""
    
    BASE_URL = "https://api-web.nhle.com/v1"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def get_game_boxscore(self, game_id):
        """Get boxscore for a specific game"""
        try:
            url = f"{self.BASE_URL}/gamecenter/{game_id}/boxscore"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching boxscore for game {game_id}: {e}")
            return None

    def get_play_by_play(self, game_id):
        """Get play-by-play for a specific game"""
        try:
            url = f"{self.BASE_URL}/gamecenter/{game_id}/play-by-play"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching play-by-play for game {game_id}: {e}")
            return None

    def get_comprehensive_game_data(self, game_id):
        """Get both boxscore and play-by-play data"""
        try:
            boxscore = self.get_game_boxscore(game_id)
            play_by_play = self.get_play_by_play(game_id)
            
            if not boxscore:
                return None
                
            # Merge data
            data = {
                'boxscore': boxscore,
                'play_by_play': play_by_play,
                'game_center': {  # For backward compatibility if needed
                    'boxscore': boxscore,
                    'play_by_play': play_by_play
                }
            }
            return data
        except Exception as e:
            logger.error(f"Error fetching comprehensive data for game {game_id}: {e}")
            return None

    def get_game_schedule(self, date):
        """Get schedule for a specific date (YYYY-MM-DD)"""
        try:
            url = f"{self.BASE_URL}/schedule/{date}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching schedule for {date}: {e}")
            return None

    def get_standings(self, date=None):
        """Get standings for a specific date"""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            url = f"{self.BASE_URL}/standings/{date}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching standings: {e}")
            return None
