import os
import requests
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from requests.adapters import HTTPAdapter
try:
    from urllib3.util.retry import Retry
except Exception:  # pragma: no cover
    Retry = None
import pandas as pd

class NHLAPIClient:
    def __init__(self, timeout: int = 8, pool_size: int = 24):
        self.base_url = "https://api-web.nhle.com/v1"
        self.timeout = timeout
        self.verbose = os.environ.get("NHL_API_DEBUG", "").lower() in ("1", "true", "yes")
        self.cache_dir = Path(os.environ.get("NHL_GAME_CACHE_DIR", ".cache/nhl_games"))
        self._mem_cache: Dict[str, dict] = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        # Reuse TCP connections across the many parallel game fetches in CI.
        retry = None
        if Retry is not None:
            retry = Retry(
                total=2,
                connect=2,
                read=2,
                backoff_factor=0.2,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=frozenset(["GET"]),
            )
        adapter = HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size, max_retries=retry or 0)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def _safe_get(self, url: str, timeout: int = None):
        """Helper to perform session.get with timeout and error handling"""
        t = timeout or self.timeout
        try:
            resp = self.session.get(url, timeout=t)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    def _cache_path(self, game_id) -> Path:
        return self.cache_dir / f"{game_id}.json"

    def _read_cache(self, game_id) -> Optional[dict]:
        key = str(game_id)
        if key in self._mem_cache:
            return self._mem_cache[key]
        path = self._cache_path(key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            self._mem_cache[key] = data
            return data
        except Exception:
            return None

    def _write_cache(self, game_id, payload: dict) -> None:
        key = str(game_id)
        self._mem_cache[key] = payload
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            path = self._cache_path(key)
            path.write_text(json.dumps(payload, separators=(",", ":")))
        except Exception:
            pass

    def prefetch_games(self, game_ids: Iterable, max_workers: int = 16) -> Dict[str, dict]:
        """Warm disk/memory cache for many games in parallel."""
        ids = [str(g) for g in game_ids if g]
        missing = [gid for gid in ids if self._read_cache(gid) is None]
        if missing:
            workers = min(max_workers, max(1, len(missing)))
            with ThreadPoolExecutor(max_workers=workers) as ex:
                list(ex.map(lambda gid: self.get_comprehensive_game_data(gid, use_cache=True), missing))
        return {gid: self._read_cache(gid) for gid in ids if self._read_cache(gid) is not None}

    def get_team_info(self, team_id):
        """Get team information by team ID"""
        url = f"{self.base_url}/teams/{team_id}"
        return self._safe_get(url)
    
    def get_team_roster(self, team_abbr):
        """Get team roster by team abbreviation"""
        url = f"{self.base_url}/roster/{team_abbr}/current"
        return self._safe_get(url)
    
    def get_team_roster_by_abbrev(self, team_abbr, season=None):
        """Get team roster by team abbreviation (optional season)"""
        if season:
            url = f"{self.base_url}/roster/{team_abbr}/{season}"
            res = self._safe_get(url)
            if res is not None:
                return res
        return self.get_team_roster(team_abbr)
    
    def get_game_schedule(self, date=None):
        """Get game schedule for a specific date"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        url = f"{self.base_url}/schedule/{date}"
        return self._safe_get(url)
    
    def get_game_center(self, game_id):
        """Get detailed game information by combining boxscore and play-by-play"""
        # Get boxscore data
        boxscore_url = f"{self.base_url}/gamecenter/{game_id}/boxscore"
        boxscore_data = self._safe_get(boxscore_url)
        
        # Get play-by-play data
        pbp_url = f"{self.base_url}/gamecenter/{game_id}/play-by-play"
        pbp_data = self._safe_get(pbp_url)
        
        if boxscore_data is not None and pbp_data is not None:
            # Combine the data
            combined_data = {
                'boxscore': boxscore_data,
                'play_by_play': pbp_data
            }
            return combined_data
        return None

    def get_player_landing(self, player_id):
        """Resolve a player ID to NHL landing profile (handles callups / new IDs)."""
        if not player_id:
            return None
        url = f"{self.base_url}/player/{player_id}/landing"
        return self._safe_get(url)

    def get_game_boxscore(self, game_id):
        """Get game boxscore"""
        cached = self._read_cache(game_id)
        if cached and cached.get("boxscore") is not None:
            return cached["boxscore"]
        url = f"{self.base_url}/gamecenter/{game_id}/boxscore"
        return self._safe_get(url)
    
    def get_player_stats(self, player_id):
        """Get player statistics"""
        url = f"{self.base_url}/players/{player_id}/stats"
        return self._safe_get(url)
    
    def find_recent_game(self, team1_abbrev, team2_abbrev, days_back=30):
        """Find the most recent game between two teams"""
        # Get team IDs from abbreviations
        team_ids = {
            'FLA': 13, 'EDM': 22, 'BOS': 6, 'TOR': 10, 'MTL': 8, 'OTT': 9,
            'BUF': 7, 'DET': 17, 'TBL': 14, 'CAR': 12, 'WSH': 15, 'PIT': 5,
            'NYR': 3, 'NYI': 2, 'NJD': 1, 'PHI': 4, 'CBJ': 29, 'NSH': 18,
            'STL': 19, 'MIN': 30, 'WPG': 52, 'COL': 21, 'UTA': 59, 'VGK': 54,
            'SJS': 28, 'LAK': 26, 'ANA': 24, 'CGY': 20, 'VAN': 23, 'SEA': 55,
            'CHI': 16, 'DAL': 25
        }
        
        team1_id = team_ids.get(team1_abbrev.upper())
        team2_id = team_ids.get(team2_abbrev.upper())
        
        if not team1_id or not team2_id:
            raise ValueError(f"Team abbreviation not found: {team1_abbrev} or {team2_id}")
        
        # Search through recent dates for the game
        for i in range(days_back):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            schedule = self.get_game_schedule(date_str)
            if schedule and 'gameWeek' in schedule:
                for day in schedule['gameWeek']:
                    for game in day.get('games', []):
                        if (game.get('awayTeam', {}).get('id') == team1_id and 
                            game.get('homeTeam', {}).get('id') == team2_id) or \
                           (game.get('awayTeam', {}).get('id') == team2_id and 
                            game.get('homeTeam', {}).get('id') == team1_id):
                            return game['id']
        
        return None
    
    def get_stanley_cup_finals_game(self):
        """Get the most recent Stanley Cup Finals game between FLA and EDM"""
        # For Stanley Cup Finals, we'll look for recent games between these teams
        # Since this is a specific request, we'll search for recent matchups
        return self.find_recent_game('FLA', 'EDM', days_back=60)
    
    def get_play_by_play(self, game_id):
        """Get play-by-play data for a game"""
        cached = self._read_cache(game_id)
        if cached and cached.get("play_by_play") is not None:
            return cached["play_by_play"]
        url = f"{self.base_url}/gamecenter/{game_id}/play-by-play"
        return self._safe_get(url)

    def get_game_right_rail(self, game_id):
        """Get right-rail team game stats (official PP, FO%, etc.)."""
        cached = self._read_cache(game_id)
        if cached and cached.get("right_rail") is not None:
            return cached["right_rail"]
        url = f"{self.base_url}/gamecenter/{game_id}/right-rail"
        return self._safe_get(url)

    def get_game_landing(self, game_id):
        """Get game landing summary"""
        cached = self._read_cache(game_id)
        if cached and cached.get("landing") is not None:
            return cached["landing"]
        url = f"{self.base_url}/gamecenter/{game_id}/landing"
        return self._safe_get(url)

    def get_comprehensive_game_data(
        self,
        game_id,
        *,
        include_right_rail: bool = True,
        use_cache: bool = True,
    ):
        """Fetch boxscore/PBP/landing in parallel (no duplicate endpoints).

        Previously this issued 5 sequential calls and re-fetched boxscore/PBP
        via get_game_center. Cache finalized games on disk for reuse across
        outcomes / team-stats / goalie builders in the same CI run.
        """
        game_id = str(game_id)
        if use_cache:
            cached = self._read_cache(game_id)
            if cached is not None:
                return cached

        urls = {
            "boxscore": f"{self.base_url}/gamecenter/{game_id}/boxscore",
            "play_by_play": f"{self.base_url}/gamecenter/{game_id}/play-by-play",
            "landing": f"{self.base_url}/gamecenter/{game_id}/landing",
        }
        if include_right_rail:
            urls["right_rail"] = f"{self.base_url}/gamecenter/{game_id}/right-rail"

        results: Dict[str, Optional[dict]] = {}
        with ThreadPoolExecutor(max_workers=len(urls)) as ex:
            futs = {ex.submit(self._safe_get, url): key for key, url in urls.items()}
            for fut in as_completed(futs):
                results[futs[fut]] = fut.result()

        boxscore = results.get("boxscore")
        play_by_play = results.get("play_by_play")
        landing = results.get("landing")
        right_rail = results.get("right_rail") if include_right_rail else None

        self._log(
            f"game {game_id}: box={boxscore is not None} pbp={play_by_play is not None} "
            f"landing={landing is not None} rail={right_rail is not None}"
        )

        if boxscore is None:
            self._log(f"Warning: Missing boxscore for {game_id}")
            return None

        # Derive a minimal game_center from boxscore — avoids a 4th/5th HTTP hop.
        game_center = {
            "id": game_id,
            "gameState": boxscore.get("gameState"),
            "game": {
                "gameDate": boxscore.get("gameDate") or datetime.now().strftime("%Y-%m-%d"),
                "awayTeamScore": (boxscore.get("awayTeam") or {}).get("score"),
                "homeTeamScore": (boxscore.get("homeTeam") or {}).get("score"),
                "awayTeamScoreByPeriod": [0, 0, 0, 0],
                "homeTeamScoreByPeriod": [0, 0, 0, 0],
            },
            "awayTeam": {
                "abbrev": (boxscore.get("awayTeam") or {}).get("abbrev"),
                "name": (boxscore.get("awayTeam") or {}).get("name", "Away Team"),
            },
            "homeTeam": {
                "abbrev": (boxscore.get("homeTeam") or {}).get("abbrev"),
                "name": (boxscore.get("homeTeam") or {}).get("name", "Home Team"),
            },
            "venue": {"default": "Unknown Arena"},
        }

        payload = {
            "game_center": game_center,
            "boxscore": boxscore,
            "play_by_play": play_by_play,
            "landing": landing,
            "right_rail": right_rail,
        }

        state = str(boxscore.get("gameState") or game_center.get("gameState") or "").upper()
        if use_cache and state in {"OFF", "FINAL", "OFFICIAL"}:
            self._write_cache(game_id, payload)
        else:
            self._mem_cache[game_id] = payload
        return payload

    def get_team_recent_games(self, team_abbr, limit=5):
        """Get recent game IDs for a team"""
        # Get team ID
        team_ids = {
            'FLA': 13, 'EDM': 22, 'BOS': 6, 'TOR': 10, 'MTL': 8, 'OTT': 9,
            'BUF': 7, 'DET': 17, 'TBL': 14, 'CAR': 12, 'WSH': 15, 'PIT': 5,
            'NYR': 3, 'NYI': 2, 'NJD': 1, 'PHI': 4, 'CBJ': 29, 'NSH': 18,
            'STL': 19, 'MIN': 30, 'WPG': 52, 'COL': 21, 'VGK': 54,
            'SJS': 28, 'LAK': 26, 'ANA': 24, 'CGY': 20, 'VAN': 23, 'SEA': 55,
            'CHI': 16, 'DAL': 25, 'UTA': 59
        }
        team_id = team_ids.get(team_abbr.upper())
        if not team_id:
            return []

        # We need to find recent games. The schedule endpoint is by date.
        # A better way is to use the team schedule endpoint if available, 
        # or search backwards.
        # For now, we'll search backwards from today.
        
        game_ids = []
        days_back = 0
        max_days = 60 # Look back 2 months max
        
        while len(game_ids) < limit and days_back < max_days:
            date = datetime.now() - timedelta(days=days_back)
            date_str = date.strftime("%Y-%m-%d")
            
            try:
                schedule = self.get_game_schedule(date_str)
                if schedule and 'gameWeek' in schedule:
                    for day in schedule['gameWeek']:
                        for game in day.get('games', []):
                            if game.get('gameState') in ['FINAL', 'OFF']:
                                if (game.get('awayTeam', {}).get('id') == team_id or 
                                    game.get('homeTeam', {}).get('id') == team_id):
                                    game_ids.append(game['id'])
            except Exception as e:
                print(f"Error fetching schedule for {date_str}: {e}")
                
            days_back += 1
            
        return game_ids[:limit]

    def get_betting_odds(self, game_id):
        """Extract betting odds for a game from the schedule endpoint"""
        # We need to find the game in the schedule
        # Try today and yesterday
        for days_ago in range(7):  # Look back up to a week
            date = datetime.now() - timedelta(days=days_ago)
            date_str = date.strftime("%Y-%m-%d")
            
            try:
                schedule = self.get_game_schedule(date_str)
                if schedule and 'gameWeek' in schedule:
                    for day in schedule['gameWeek']:
                        for game in day.get('games', []):
                            if game.get('id') == int(game_id):
                                return {
                                    'away_odds': game.get('awayTeam', {}).get('odds', []),
                                    'home_odds': game.get('homeTeam', {}).get('odds', [])
                                }
            except Exception as e:
                print(f"Error fetching odds for {date_str}: {e}")
                continue
        
        return None
    
    def parse_american_odds_to_probability(self, american_odds_str):
        """Convert American odds (e.g., '+205', '-250') to implied probability"""
        try:
            odds = float(american_odds_str)
            if odds > 0:
                # Underdog: probability = 100 / (odds + 100)
                return 100 / (odds + 100)
            else:
                # Favorite: probability = |odds| / (|odds| + 100)
                return abs(odds) / (abs(odds) + 100)
        except (ValueError, TypeError):
            return None
    
    def get_consensus_betting_probability(self, game_id):
        """Get consensus betting probability from multiple sportsbooks"""
        odds_data = self.get_betting_odds(game_id)
        if not odds_data:
            return None
        
        away_probs = []
        home_probs = []
        
        # Parse away team odds
        for odds_entry in odds_data.get('away_odds', []):
            odds_str = odds_entry.get('value', '')
            prob = self.parse_american_odds_to_probability(odds_str)
            if prob:
                away_probs.append(prob)
        
        # Parse home team odds
        for odds_entry in odds_data.get('home_odds', []):
            odds_str = odds_entry.get('value', '')
            prob = self.parse_american_odds_to_probability(odds_str)
            if prob:
                home_probs.append(prob)
        
        if not away_probs or not home_probs:
            return None
        
        # Calculate consensus (average across providers)
        avg_away_prob = sum(away_probs) / len(away_probs)
        avg_home_prob = sum(home_probs) / len(home_probs)
        
        # Normalize to sum to 1.0
        total = avg_away_prob + avg_home_prob
        if total > 0:
            return {
                'away_prob': avg_away_prob / total,
                'home_prob': avg_home_prob / total,
                'num_books': len(away_probs)
            }
        
        return None

    def get_standings(self):
        """Get current league standings"""
        url = f"{self.base_url}/standings/now"
        return self._safe_get(url)
