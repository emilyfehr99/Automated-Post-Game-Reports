#!/usr/bin/env python3
"""
Hudl Instat API Client
Reverse engineered from inspect element network requests
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class HudlAPIConfig:
    """Configuration for Hudl API client"""
    base_url: str = "https://api-hockey.instatscout.com"
    api_endpoint: str = "/data"
    session: Optional[requests.Session] = None
    
    def __post_init__(self):
        if self.session is None:
            self.session = requests.Session()
            # Set common headers based on what we see in the network requests
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://instat.hudl.com/',
                'Origin': 'https://instat.hudl.com'
            })

class HudlInstatAPIClient:
    """Direct API client for Hudl Instat based on reverse engineered network requests"""
    
    def __init__(self, config: HudlAPIConfig = None):
        self.config = config or HudlAPIConfig()
        self.session = self.config.session
        
    def _make_request(self, proc: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Hudl Instat API"""
        url = f"{self.config.base_url}{self.config.api_endpoint}"
        
        payload = {
            "body": {
                "params": params,
                "proc": proc
            }
        }
        
        logger.info(f"🔗 Making API request to {proc}")
        logger.info(f"📊 Params: {params}")
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ API request successful for {proc}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API request failed for {proc}: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error for {proc}: {e}")
            return {}
    
    def get_team_statistics(self, team_id: str, season_id: str = "34", tournament_id: str = None) -> Dict[str, Any]:
        """
        Get team statistics using scout_uni_overview_team_stat
        Based on: scout_uni_overview_team_stat with _p_team_id, _p_season_id, _p_tournament_id
        """
        params = {
            "_p_team_id": team_id,
            "_p_season_id": season_id
        }
        
        if tournament_id:
            params["_p_tournament_id"] = tournament_id
            
        return self._make_request("scout_uni_overview_team_stat", params)
    
    def get_team_players(self, team_id: str, season_id: str = "34", tournament_id: str = None) -> Dict[str, Any]:
        """
        Get team players using scout_uni_overview_team_players
        Based on: scout_uni_overview_team_players with _p_team_id, _p_season_id, _p_tournament_id
        """
        params = {
            "_p_team_id": team_id,
            "_p_season_id": season_id
        }
        
        if tournament_id:
            params["_p_tournament_id"] = tournament_id
            
        return self._make_request("scout_uni_overview_team_players", params)
    
    def get_lexical_parameters(self, phrase_ids: List[int], lang: str = "en") -> Dict[str, Any]:
        """
        Get lexical parameters using scout_param_lexical
        Based on: scout_param_lexical with phrases array and lang
        """
        params = {
            "lang": lang,
            "phrases": phrase_ids
        }
        
        return self._make_request("scout_param_lexical", params)
    
    def get_player_statistics(self, player_id: str, season_id: str = "34", tournament_id: str = None) -> Dict[str, Any]:
        """
        Get individual player statistics using scout_uni_overview_player_stat
        """
        params = {
            "_p_player_id": player_id,
            "_p_season_id": season_id
        }
        
        if tournament_id:
            params["_p_tournament_id"] = tournament_id
            
        return self._make_request("scout_uni_overview_player_stat", params)
    
    def get_team_matches(self, team_id: str, season_id: str = "34", tournament_id: str = None) -> Dict[str, Any]:
        """
        Get team matches using scout_uni_overview_team_matches
        """
        params = {
            "_p_team_id": team_id,
            "_p_season_id": season_id
        }
        
        if tournament_id:
            params["_p_tournament_id"] = tournament_id
            
        return self._make_request("scout_uni_overview_team_matches", params)
    
    def get_comprehensive_team_data(self, team_id: str, season_id: str = "34", tournament_id: str = None) -> Dict[str, Any]:
        """
        Get comprehensive team data including statistics, players, and lexical parameters
        This replicates what the HTML scraping was doing
        """
        logger.info(f"🚀 Getting comprehensive data for team {team_id}")
        
        # Get team statistics
        team_stats = self.get_team_statistics(team_id, season_id, tournament_id)
        
        # Get team players
        team_players = self.get_team_players(team_id, season_id, tournament_id)
        
        # Extract phrase IDs from the data for lexical parameters
        phrase_ids = []
        if team_stats and 'data' in team_stats:
            # Extract phrase IDs from the statistics data
            # This is based on the pattern we saw in the console logs
            phrase_ids = self._extract_phrase_ids(team_stats['data'])
        
        # Get lexical parameters
        lexical_params = {}
        if phrase_ids:
            lexical_params = self.get_lexical_parameters(phrase_ids)
        
        return {
            'team_statistics': team_stats,
            'team_players': team_players,
            'lexical_parameters': lexical_params,
            'team_id': team_id,
            'season_id': season_id,
            'tournament_id': tournament_id
        }
    
    def _extract_phrase_ids(self, data: List[Dict]) -> List[int]:
        """Extract phrase IDs from the data structure"""
        phrase_ids = []
        
        # This is a simplified extraction - in reality, we'd need to analyze
        # the data structure more carefully to find all phrase IDs
        for item in data:
            if isinstance(item, dict):
                # Look for common phrase ID patterns
                for key, value in item.items():
                    if isinstance(value, (int, str)) and str(value).isdigit():
                        phrase_ids.append(int(value))
                    elif isinstance(value, dict):
                        phrase_ids.extend(self._extract_phrase_ids([value]))
        
        # Remove duplicates and return
        return list(set(phrase_ids))
    
    def set_authentication(self, session_cookies: Dict[str, str] = None, auth_token: str = None):
        """Set authentication for the API client"""
        if session_cookies:
            self.session.cookies.update(session_cookies)
            logger.info("✅ Session cookies set")
        
        if auth_token:
            self.session.headers['Authorization'] = f'Bearer {auth_token}'
            logger.info("✅ Auth token set")

def main():
    """Test the API client"""
    client = HudlInstatAPIClient()
    
    # Test with Lloydminster Bobcats (team_id: 21479)
    team_id = "21479"
    season_id = "34"
    
    logger.info(f"🧪 Testing API client with team {team_id}")
    
    # Test team statistics
    team_stats = client.get_team_statistics(team_id, season_id)
    logger.info(f"📊 Team stats response: {len(str(team_stats))} characters")
    
    # Test team players
    team_players = client.get_team_players(team_id, season_id)
    logger.info(f"👥 Team players response: {len(str(team_players))} characters")
    
    # Test comprehensive data
    comprehensive_data = client.get_comprehensive_team_data(team_id, season_id)
    logger.info(f"🎯 Comprehensive data: {len(str(comprehensive_data))} characters")
    
    # Save results for analysis
    with open("hudl_api_test_results.json", "w") as f:
        json.dump(comprehensive_data, f, indent=2)
    
    logger.info("✅ API test results saved to hudl_api_test_results.json")

if __name__ == "__main__":
    main()
