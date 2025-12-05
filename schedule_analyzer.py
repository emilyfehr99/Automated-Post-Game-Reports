import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ScheduleAnalyzer:
    def __init__(self, schedule_file="season_2025_2026_schedule.json"):
        self.schedule_file = schedule_file
        self.games_by_date = {} # Date string -> list of game dicts
        self.games_by_team = {} # Team Abbrev -> list of game dicts (sorted by date)
        self.load_schedule()

    def load_schedule(self):
        """Loads and indexes the schedule for fast lookup."""
        try:
            with open(self.schedule_file, 'r') as f:
                games = json.load(f)
                
            # Sort games by date/time just in case
            # We use startTimeUTC for sorting
            games.sort(key=lambda x: x.get('startTimeUTC', ''))

            for game in games:
                game_date = game.get('gameDate')
                if not game_date:
                    continue
                
                # Index by Date
                if game_date not in self.games_by_date:
                    self.games_by_date[game_date] = []
                self.games_by_date[game_date].append(game)

                # Index by Team
                # Note: This includes ALL games (past and future)
                away_team = game.get('awayTeam', {}).get('abbrev')
                home_team = game.get('homeTeam', {}).get('abbrev')
                
                if away_team:
                    if away_team not in self.games_by_team: self.games_by_team[away_team] = []
                    self.games_by_team[away_team].append(game)
                
                if home_team:
                    if home_team not in self.games_by_team: self.games_by_team[home_team] = []
                    self.games_by_team[home_team].append(game)
            
            logger.info(f"ScheduleAnalyzer loaded {len(games)} games.")

        except Exception as e:
            logger.error(f"Failed to load schedule file {self.schedule_file}: {e}")

    def played_yesterday(self, team_abbr, current_date_str):
        """
        Returns True if the team played a game on the day before current_date_str.
        current_date_str format: 'YYYY-MM-DD'
        """
        try:
            curr = datetime.strptime(current_date_str, "%Y-%m-%d")
            yesterday = (curr - timedelta(days=1)).strftime("%Y-%m-%d")
            
            if yesterday in self.games_by_date:
                for game in self.games_by_date[yesterday]:
                    a_team = game.get('awayTeam', {}).get('abbrev')
                    h_team = game.get('homeTeam', {}).get('abbrev')
                    if team_abbr == a_team or team_abbr == h_team:
                        logger.info(f"Fatigue Detected: {team_abbr} played yesterday ({yesterday})")
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking fatigue for {team_abbr}: {e}")
            return False

    def get_recent_games(self, team_abbr, before_date_str, n=10):
        """
        Returns the last n COMPLETED games for a team BEFORE the given date.
        Useful for calculating Recency Bias (Last 10).
        """
        recent = []
        try:
            if team_abbr not in self.games_by_team:
                return []
            
            # We iterate backwards through the team's schedule
            all_games = self.games_by_team[team_abbr]
            # Assumes games are sorted chronologically from load_schedule
            
            # Filter for games strictly before the target date and are FINAL
            # Efficient implementation: iterate backwards
            
            current_date_dt = datetime.strptime(before_date_str, "%Y-%m-%d")
            
            count = 0
            for i in range(len(all_games) - 1, -1, -1):
                game = all_games[i]
                g_date_str = game.get('gameDate')
                g_state = game.get('gameState')
                
                if not g_date_str: continue
                
                g_dt = datetime.strptime(g_date_str, "%Y-%m-%d")
                
                if g_dt < current_date_dt and g_state in ['FINAL', 'OFF']:
                    recent.append(game)
                    count += 1
                    if count >= n:
                        break
            
            return recent # Oldest to newest output? No, currently newest to oldest.
                          # Let's reverse it to be chronological if needed, but for averages it doesn't matter.
        except Exception as e:
            logger.error(f"Error getting recent games for {team_abbr}: {e}")
            return []
