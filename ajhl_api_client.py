#!/usr/bin/env python3
"""
AJHL API Client
Python client library for the AJHL Data Collection API
"""

import json
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AJHLTeam:
    """AJHL Team data structure"""
    team_id: str
    team_name: str
    city: str
    division: str
    hudl_team_id: Optional[str] = None
    last_updated: Optional[datetime] = None
    data_available: bool = False

@dataclass
class AJHLGame:
    """AJHL Game data structure"""
    game_id: str
    team_id: str
    opponent: str
    game_date: datetime
    home_away: str
    result: Optional[str] = None
    data_files: List[str] = None
    last_updated: datetime = None

@dataclass
class AJHLPlayer:
    """AJHL Player data structure"""
    player_id: str
    team_id: str
    name: str
    position: str
    stats: Dict[str, Any] = None
    last_updated: datetime = None

class AJHLAPIClient:
    """Client for AJHL Data Collection API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        """Initialize the API client"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}" if api_key else None
            }
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise
    
    # Team endpoints
    async def get_teams(self) -> List[AJHLTeam]:
        """Get all teams"""
        response = await self._make_request("GET", "/teams")
        return [AJHLTeam(**team) for team in response]
    
    async def get_team(self, team_id: str) -> AJHLTeam:
        """Get specific team"""
        response = await self._make_request("GET", f"/teams/{team_id}")
        return AJHLTeam(**response)
    
    # Game endpoints
    async def get_games(
        self, 
        team_id: Optional[str] = None, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[AJHLGame]:
        """Get games with optional filtering"""
        params = {"limit": limit, "offset": offset}
        if team_id:
            params["team_id"] = team_id
        
        response = await self._make_request("GET", "/games", params=params)
        return [AJHLGame(**game) for game in response]
    
    async def get_game(self, game_id: str) -> AJHLGame:
        """Get specific game"""
        response = await self._make_request("GET", f"/games/{game_id}")
        return AJHLGame(**response)
    
    # Player endpoints
    async def get_players(
        self, 
        team_id: Optional[str] = None, 
        position: Optional[str] = None,
        limit: int = 100, 
        offset: int = 0
    ) -> List[AJHLPlayer]:
        """Get players with optional filtering"""
        params = {"limit": limit, "offset": offset}
        if team_id:
            params["team_id"] = team_id
        if position:
            params["position"] = position
        
        response = await self._make_request("GET", "/players", params=params)
        return [AJHLPlayer(**player) for player in response]
    
    # Data collection endpoints
    async def collect_data(
        self, 
        team_ids: List[str], 
        collection_type: str = "full",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger data collection for specified teams"""
        data = {
            "team_ids": team_ids,
            "collection_type": collection_type,
            "force_refresh": force_refresh
        }
        return await self._make_request("POST", "/collect", json=data)
    
    async def get_collection_status(self) -> Dict[str, Any]:
        """Get current collection status"""
        return await self._make_request("GET", "/collect/status")
    
    async def stop_collection(self) -> Dict[str, Any]:
        """Stop current data collection"""
        return await self._make_request("POST", "/collect/stop")
    
    # System endpoints
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system health status"""
        return await self._make_request("GET", "/status")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check"""
        return await self._make_request("GET", "/health")
    
    # Notification endpoints
    async def get_notification_config(self) -> Dict[str, Any]:
        """Get notification configuration"""
        return await self._make_request("GET", "/notifications/config")
    
    async def update_notification_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update notification configuration"""
        return await self._make_request("POST", "/notifications/config", json=config)
    
    async def test_notifications(self) -> Dict[str, Any]:
        """Test notification system"""
        return await self._make_request("POST", "/notifications/test")
    
    # Utility methods
    async def get_team_by_name(self, team_name: str) -> Optional[AJHLTeam]:
        """Get team by name"""
        teams = await self.get_teams()
        for team in teams:
            if team.team_name.lower() == team_name.lower():
                return team
        return None
    
    async def get_recent_games(self, team_id: str, days: int = 30) -> List[AJHLGame]:
        """Get recent games for a team"""
        games = await self.get_games(team_id=team_id)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_games = []
        for game in games:
            if game.game_date >= cutoff_date:
                recent_games.append(game)
        
        return sorted(recent_games, key=lambda x: x.game_date, reverse=True)
    
    async def get_team_players(self, team_id: str) -> List[AJHLPlayer]:
        """Get all players for a team"""
        return await self.get_players(team_id=team_id)
    
    async def get_players_by_position(self, team_id: str, position: str) -> List[AJHLPlayer]:
        """Get players by position for a team"""
        return await self.get_players(team_id=team_id, position=position)

class AJHLDataManager:
    """High-level data management class"""
    
    def __init__(self, api_client: AJHLAPIClient):
        """Initialize with API client"""
        self.client = api_client
    
    async def get_lloydminster_data(self) -> Dict[str, Any]:
        """Get comprehensive data for Lloydminster Bobcats"""
        team = await self.client.get_team_by_name("Lloydminster Bobcats")
        if not team:
            raise ValueError("Lloydminster Bobcats not found")
        
        # Get team data
        games = await self.client.get_recent_games(team.team_id, days=90)
        players = await self.client.get_team_players(team.team_id)
        
        return {
            "team": team,
            "recent_games": games,
            "players": players,
            "data_summary": {
                "total_games": len(games),
                "total_players": len(players),
                "last_updated": team.last_updated
            }
        }
    
    async def get_opponent_data(self, opponent_name: str) -> Dict[str, Any]:
        """Get data for a specific opponent"""
        team = await self.client.get_team_by_name(opponent_name)
        if not team:
            raise ValueError(f"Team '{opponent_name}' not found")
        
        games = await self.client.get_recent_games(team.team_id, days=30)
        players = await self.client.get_team_players(team.team_id)
        
        return {
            "team": team,
            "recent_games": games,
            "players": players
        }
    
    async def collect_all_team_data(self) -> Dict[str, Any]:
        """Collect data for all teams"""
        teams = await self.client.get_teams()
        team_ids = [team.team_id for team in teams]
        
        result = await self.client.collect_data(team_ids, collection_type="full")
        return result
    
    async def collect_lloydminster_data(self) -> Dict[str, Any]:
        """Collect data specifically for Lloydminster Bobcats"""
        team = await self.client.get_team_by_name("Lloydminster Bobcats")
        if not team:
            raise ValueError("Lloydminster Bobcats not found")
        
        result = await self.client.collect_data([team.team_id], collection_type="full")
        return result

# Example usage and testing
async def main():
    """Example usage of the API client"""
    async with AJHLAPIClient(api_key="your-api-key-here") as client:
        # Test basic connectivity
        print("🔍 Testing API connectivity...")
        health = await client.health_check()
        print(f"Health check: {health}")
        
        # Get system status
        status = await client.get_system_status()
        print(f"System status: {status}")
        
        # Get all teams
        print("\n🏒 Getting all teams...")
        teams = await client.get_teams()
        for team in teams:
            print(f"  {team.team_name} ({team.city}) - {team.division}")
        
        # Get Lloydminster Bobcats data
        print("\n📊 Getting Lloydminster Bobcats data...")
        try:
            manager = AJHLDataManager(client)
            lloydminster_data = await manager.get_lloydminster_data()
            print(f"  Team: {lloydminster_data['team'].team_name}")
            print(f"  Recent games: {len(lloydminster_data['recent_games'])}")
            print(f"  Players: {len(lloydminster_data['players'])}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Test data collection
        print("\n📥 Testing data collection...")
        try:
            result = await client.collect_data(["21479"], collection_type="full")
            print(f"  Collection result: {result}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
