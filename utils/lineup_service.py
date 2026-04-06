#!/usr/bin/env python3
"""
Lineup Service - Fetches confirmed goalies, lineups, and injury data for games.
Phase 1: Goalie confirmation (biggest impact)
Phase 2: Key player injuries
Phase 3: Full lineup
"""
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from pathlib import Path
import json

from nhl_api_client import NHLAPIClient


class LineupService:
    def __init__(self):
        self.api = NHLAPIClient()
        self.cache_file = Path('lineup_cache.json')
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Load cached lineup data"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_cache(self):
        """Save lineup cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass
    
    def get_confirmed_goalie(self, team: str, game_id: str, game_date: str) -> Optional[str]:
        """Get confirmed starting goalie for a team in a game.
        
        Checks multiple sources:
        1. NHL API boxscore (if game is close/started)
        2. Cache (if recently fetched)
        3. Returns None if unavailable (will use prediction)
        
        Args:
            team: Team abbreviation (e.g., 'BOS')
            game_id: NHL game ID
            game_date: Game date string (YYYY-MM-DD)
            
        Returns:
            Goalie name if confirmed, None otherwise
        """
        cache_key = f"{game_id}_{team}"
        
        # Check cache first (valid for 4 hours)
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            cached_time = datetime.fromisoformat(cached.get('timestamp', '2000-01-01'))
            if datetime.now() - cached_time < timedelta(hours=4):
                return cached.get('goalie')
        
        # Try to get from boxscore (works ~30 min before game and during)
        try:
            boxscore = self.api.get_game_boxscore(game_id)
            if boxscore:
                goalie = self._extract_goalie_from_boxscore(boxscore, team)
                if goalie:
                    # Cache it
                    self.cache[cache_key] = {
                        'goalie': goalie,
                        'timestamp': datetime.now().isoformat()
                    }
                    self._save_cache()
                    return goalie
        except Exception:
            pass
        
        return None
    
    def _extract_goalie_from_boxscore(self, boxscore: Dict, team: str) -> Optional[str]:
        """Extract starting goalie from boxscore data"""
        team_key = 'awayTeam' if boxscore.get('awayTeam', {}).get('abbrev') == team.upper() else 'homeTeam'
        team_data = boxscore.get(team_key, {})
        
        # Try explicit goalie starters list
        starters = team_data.get('goalies') or team_data.get('starters')
        if starters and isinstance(starters, list):
            for g in starters:
                if isinstance(g, dict):
                    name = g.get('name') or g.get('firstLastName') or g.get('playerName')
                    if name:
                        return name
        
        # Try players list with starter flag
        players = team_data.get('players') or []
        if isinstance(players, dict):
            players_iter = players.values()
        elif isinstance(players, list):
            players_iter = players
        else:
            return None
        
        goalie_candidates = []
        for p in players_iter:
            try:
                pos = p.get('positionCode') or (p.get('position', {}) or {}).get('code')
                if pos != 'G':
                    continue
                starter = p.get('starter') or p.get('starting') or False
                name = p.get('name') or p.get('firstLastName') or p.get('playerName')
                if name:
                    goalie_candidates.append((bool(starter), name))
            except Exception:
                continue
        
        if goalie_candidates:
            # Prefer marked starter, otherwise return first goalie
            goalie_candidates.sort(key=lambda x: x[0], reverse=True)
            return goalie_candidates[0][1]
        
        return None
    
    def get_injured_players(self, team: str) -> List[str]:
        """Get list of currently injured players for a team.
        
        Phase 2: This would scrape NHL.com injury reports or use an API.
        For now, returns empty list (placeholder for future implementation).
        
        Args:
            team: Team abbreviation
            
        Returns:
            List of injured player names
        """
        # TODO: Implement injury scraping/API
        # Options:
        # 1. Scrape NHL.com team injury page
        # 2. Use Rotowire/Rotogrinders API (if available)
        # 3. Twitter scraping for beat writer reports
        return []
    
    def calculate_injury_impact(self, team: str, injured_players: List[str]) -> float:
        """Calculate how much injured players affect team strength.
        
        Returns multiplier (0.95-1.0) where:
        - 1.0 = no impact
        - 0.95 = significant impact (star player out)
        
        Phase 2: Would use player WAR/GAR or historical performance.
        """
        if not injured_players:
            return 1.0
        
        # Simple tier system for now
        # TODO: Enhance with actual player value metrics
        star_players = []  # Would come from team roster analysis
        good_players = []
        
        impact = 1.0
        for player in injured_players:
            if player in star_players:
                impact -= 0.03  # -3% per star player
            elif player in good_players:
                impact -= 0.015  # -1.5% per good player
            else:
                impact -= 0.005  # -0.5% per role player
        
        return max(0.85, impact)  # Cap at 15% reduction
    
    def get_confirmed_lineup(self, team: str, game_id: str) -> Optional[Dict]:
        """Get confirmed full lineup (forwards, defense, goalie).
        
        Phase 3: Full lineup with lines and pairings.
        Currently returns None (placeholder).
        
        Returns:
            Dict with 'forwards', 'defense', 'goalie' lists, or None
        """
        # TODO: Implement full lineup extraction
        return None


def test_lineup_service():
    """Test the lineup service with a recent game"""
    service = LineupService()
    
    # Test with a recent game
    api = NHLAPIClient()
    today = datetime.now().strftime('%Y-%m-%d')
    schedule = api.get_game_schedule(today)
    
    if schedule and 'gameWeek' in schedule:
        for day in schedule['gameWeek']:
            if day.get('date') == today and 'games' in day:
                game = day['games'][0] if day['games'] else None
                if game:
                    game_id = str(game.get('id'))
                    away = game.get('awayTeam', {}).get('abbrev')
                    home = game.get('homeTeam', {}).get('abbrev')
                    
                    print(f"Testing lineup service for {away} @ {home}:")
                    away_goalie = service.get_confirmed_goalie(away, game_id, today)
                    home_goalie = service.get_confirmed_goalie(home, game_id, today)
                    print(f"  Away goalie: {away_goalie or 'Not confirmed'}")
                    print(f"  Home goalie: {home_goalie or 'Not confirmed'}")
                    break


if __name__ == '__main__':
    test_lineup_service()

