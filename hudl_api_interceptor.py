#!/usr/bin/env python3
"""
Hudl Instat API Interceptor
Intercepts and replicates the API calls made by the Hudl Instat interface
to get access to all 135+ metrics directly from the API.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HudlAPIInterceptor:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://hockey.instatscout.com"
        self.api_url = f"{self.base_url}/api"
        
        # Headers to mimic the browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Origin': 'https://hockey.instatscout.com',
            'Referer': 'https://hockey.instatscout.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    def get_team_overview_stats(self, team_id: int = 21479, season_id: int = 34) -> Optional[Dict[str, Any]]:
        """
        Get team overview statistics using the exact API call from the console logs
        """
        try:
            logger.info(f"🔍 Making API call for team {team_id}, season {season_id}")
            
            payload = {
                "params": {
                    "_p_team_id": team_id,
                    "_p_season_id": season_id,
                    "_p_tournament_id": None
                },
                "proc": "scout_uni_overview_team_stat"
            }
            
            response = self.session.post(f"{self.api_url}/scout_uni_overview_team_stat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Successfully retrieved team overview stats")
                logger.info(f"📊 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return data
            else:
                logger.error(f"❌ API call failed with status {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error making API call: {e}")
            return None
    
    def get_lexical_params(self, phrases: list = [1021, 15994, 15995, 17890, 16630]) -> Optional[Dict[str, Any]]:
        """
        Get lexical parameters (metric definitions and translations)
        """
        try:
            logger.info(f"🔍 Getting lexical parameters for phrases: {phrases}")
            
            payload = {
                "params": {
                    "lang": "en",
                    "phrases": phrases
                },
                "proc": "scout_param_lexical"
            }
            
            response = self.session.post(f"{self.api_url}/scout_param_lexical", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Successfully retrieved lexical parameters")
                logger.info(f"📊 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return data
            else:
                logger.error(f"❌ Lexical API call failed with status {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting lexical parameters: {e}")
            return None
    
    def get_team_players_stats(self, team_id: int = 21479, season_id: int = 34) -> Optional[Dict[str, Any]]:
        """
        Get detailed team players statistics - this might contain all 135+ metrics
        """
        try:
            logger.info(f"🔍 Getting detailed team players stats for team {team_id}")
            
            # Try different possible API endpoints for player stats
            possible_endpoints = [
                "scout_uni_team_players_stat",
                "scout_uni_team_skaters_stat", 
                "scout_uni_team_players_detailed",
                "scout_uni_team_players_comprehensive",
                "scout_uni_team_players_all_metrics"
            ]
            
            for endpoint in possible_endpoints:
                try:
                    payload = {
                        "params": {
                            "_p_team_id": team_id,
                            "_p_season_id": season_id,
                            "_p_tournament_id": None
                        },
                        "proc": endpoint
                    }
                    
                    response = self.session.post(f"{self.api_url}/{endpoint}", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"✅ Successfully retrieved data from {endpoint}")
                        logger.info(f"📊 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        return data
                    else:
                        logger.debug(f"❌ {endpoint} failed with status {response.status_code}")
                        
                except Exception as e:
                    logger.debug(f"❌ Error with {endpoint}: {e}")
                    continue
            
            logger.warning("⚠️ No working player stats endpoint found")
            return None
                
        except Exception as e:
            logger.error(f"❌ Error getting team players stats: {e}")
            return None
    
    def discover_all_metrics(self, team_id: int = 21479) -> Dict[str, Any]:
        """
        Discover all available metrics by making multiple API calls
        """
        logger.info(f"🔍 Discovering all metrics for team {team_id}")
        
        results = {}
        
        # 1. Get team overview stats
        overview = self.get_team_overview_stats(team_id)
        if overview:
            results['overview'] = overview
        
        # 2. Get lexical parameters
        lexical = self.get_lexical_params()
        if lexical:
            results['lexical'] = lexical
        
        # 3. Get detailed player stats
        players = self.get_team_players_stats(team_id)
        if players:
            results['players'] = players
        
        # 4. Try to get all available procedures
        try:
            logger.info("🔍 Attempting to discover all available procedures...")
            # This is a guess - we might need to find the actual discovery endpoint
            response = self.session.get(f"{self.api_url}/procedures")
            if response.status_code == 200:
                results['procedures'] = response.json()
        except Exception as e:
            logger.debug(f"Could not discover procedures: {e}")
        
        return results

def main():
    """Main function to test the API interceptor"""
    logger.info("🚀 Starting Hudl API Interceptor...")
    
    interceptor = HudlAPIInterceptor()
    
    # Discover all metrics
    results = interceptor.discover_all_metrics()
    
    # Save results to file
    with open('hudl_api_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("✅ Results saved to hudl_api_results.json")
    
    # Print summary
    for key, value in results.items():
        if isinstance(value, dict):
            logger.info(f"📊 {key}: {len(value)} keys")
        else:
            logger.info(f"📊 {key}: {type(value)}")

if __name__ == "__main__":
    main()
