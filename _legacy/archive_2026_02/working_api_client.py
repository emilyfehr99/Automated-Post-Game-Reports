#!/usr/bin/env python3
"""
Working API Client for Hudl Instat
Based on the actual network request data provided by user
"""

import time
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class WorkingAPIConfig:
    """Configuration based on the actual network request data"""
    base_url: str = "https://www.hudl.com/app/metropole/shim/api-hockey.instatscout.com"
    api_endpoint: str = "/data"
    session: Optional[requests.Session] = None
    
    def __post_init__(self):
        if self.session is None:
            self.session = requests.Session()
            # Set headers based on the actual network request data
            self.session.headers.update({
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-CA,en-US;q=0.9,en;q=0.8',
                'Content-Type': 'application/json',
                'Origin': 'https://app.hudl.com',
                'Referer': 'https://app.hudl.com/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15',
                'Priority': 'u=3, i'
            })

class WorkingAPIClient:
    """API client based on the actual working network request data"""
    
    def __init__(self, config: WorkingAPIConfig = None):
        self.config = config or WorkingAPIConfig()
        self.session = self.config.session
        
    def set_authentication(self, 
                          authorization_token: str,
                          x_auth_token: str,
                          cookies: Dict[str, str]):
        """Set authentication using the actual tokens from the network request"""
        try:
            # Set Authorization header
            self.session.headers['Authorization'] = f"Bearer {authorization_token}"
            
            # Set x-auth-token header
            self.session.headers['x-auth-token'] = x_auth_token
            
            # Set cookies
            for name, value in cookies.items():
                self.session.cookies.set(name, value)
            
            logger.info("✅ Authentication headers and cookies set successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting authentication: {e}")
            return False
    
    def _make_request(self, proc: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Hudl Instat API using the exact structure"""
        url = f"{self.config.base_url}{self.config.api_endpoint}"
        
        # Based on the actual network request structure
        payload = {
            "body": {
                "params": params,
                "proc": proc
            }
        }
        
        logger.info(f"🔗 Making API request to {proc}")
        logger.info(f"📊 Params: {params}")
        logger.info(f"🌐 URL: {url}")
        
        try:
            response = self.session.post(url, json=payload)
            
            logger.info(f"📊 Response status: {response.status_code}")
            logger.info(f"📊 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ API request successful for {proc}")
                return data
            else:
                logger.error(f"❌ API request failed for {proc}: {response.status_code}")
                logger.error(f"❌ Response: {response.text[:500]}...")
                return {}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API request failed for {proc}: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error for {proc}: {e}")
            return {}
    
    def get_team_statistics(self, team_id: str, season_id: str = "34", tournament_id: str = None) -> Dict[str, Any]:
        """Get team statistics using scout_uni_overview_team_stat"""
        params = {
            "_p_team_id": team_id,
            "_p_season_id": season_id
        }
        
        if tournament_id:
            params["_p_tournament_id"] = tournament_id
            
        return self._make_request("scout_uni_overview_team_stat", params)
    
    def get_team_players(self, team_id: str, season_id: str = "34", tournament_id: str = None) -> Dict[str, Any]:
        """Get team players using scout_uni_overview_team_players"""
        params = {
            "_p_team_id": team_id,
            "_p_season_id": season_id
        }
        
        if tournament_id:
            params["_p_tournament_id"] = tournament_id
            
        return self._make_request("scout_uni_overview_team_players", params)
    
    def get_lexical_parameters(self, phrase_ids: List[int], lang: str = "en") -> Dict[str, Any]:
        """Get lexical parameters using scout_param_lexical"""
        params = {
            "lang": lang,
            "phrases": phrase_ids
        }
        
        return self._make_request("scout_param_lexical", params)
    
    def get_comprehensive_team_data(self, team_id: str, season_id: str = "34", tournament_id: str = None) -> Dict[str, Any]:
        """Get comprehensive team data"""
        logger.info(f"🚀 Getting comprehensive data for team {team_id}")
        
        # Get team statistics
        team_stats = self.get_team_statistics(team_id, season_id, tournament_id)
        
        # Get team players
        team_players = self.get_team_players(team_id, season_id, tournament_id)
        
        # Extract phrase IDs for lexical parameters
        phrase_ids = []
        if team_stats and 'data' in team_stats:
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
        
        for item in data:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, (int, str)) and str(value).isdigit():
                        phrase_ids.append(int(value))
                    elif isinstance(value, dict):
                        phrase_ids.extend(self._extract_phrase_ids([value]))
        
        return list(set(phrase_ids))

def main():
    """Test the working API client with real authentication data"""
    client = WorkingAPIClient()
    
    # Authentication data from the actual network request
    authorization_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjZaYjBkN0VpWG9TQ0FhUTdYaW90SCJ9.eyJodHRwczovL2lkZW50aXR5Lmh1ZGwuY29tL2Nvbm5lY3Rpb25fbmFtZSI6InByb2QtaHVkbC11c2Vycy10ZXJyYWZvcm0iLCJodHRwczovL2lkZW50aXR5Lmh1ZGwuY29tL3VzZXJfaWQiOiIxOTEwMzIzMCIsImh0dHBzOi8vaWRlbnRpdHkuaHVkbC5jb20vdG9rIjoiaWQiLCJodHRwczovL2lkZW50aXR5Lmh1ZGwuY29tL2lzX3N5c2FkbWluIjpmYWxzZSwiaHR0cHM6Ly9pZGVudGl0eS5odWRsLmNvbS9pbnRlcm5hbF9pZF9odWRsIjoiMTkxMDMyMzAiLCJodHRwczovL2lkZW50aXR5Lmh1ZGwuY29tL2ludGVybmFsX2lkX2luc3RhdCI6NDU1MjE0LCJodHRwczovL2lkZW50aXR5Lmh1ZGwuY29tL2luc3RhdF90b2tlbiI6ImV5SmhiR2NpT2lKSVV6STFOaUlzSW5SNWNDSTZJa3BYVkNKOS5leUpsYldGcGJDSTZJbU5vWVhObGNtOWphRzl1TnpjM1FHZHRZV2xzTG1OdmJTSXNJblJ2YTJWdUlqb2lVR0owTm5abFpqaFRaR3haTjNReVJGaFBSRGREVUVWS1FuaG9TVWRvYlVVaUxDSmxlSEFpT2pFM05qQTJORFk0TVRnc0ltbGhkQ0k2TVRjMU9EQTFORGd4T0gwLjRWblNibXpXSWtaal90Qy14al8wd3k5ZDA1akQ4NWstc2tmQmw1ci1mOTAiLCJuaWNrbmFtZSI6ImNoYXNlcm9jaG9uNzc3IiwibmFtZSI6ImNoYXNlcm9jaG9uNzc3QGdtYWlsLmNvbSIsInBpY3R1cmUiOiJodHRwczovL3MuZ3JhdmF0YXIuY29tL2F2YXRhci8xMTAwOTlhMjQ0NGI5MDJjNzU3OGRhNjBmYWY5N2YxMj9zPTQ4MCZyPXBnJmQ9aHR0cHMlM0ElMkYlMkZjZG4uYXV0aDAuY29tJTJGYXZhdGFycyUyRmNoLnBuZyIsInVwZGF0ZWRfYXQiOiIyMDI1LTA5LTE2VDIwOjMzOjM3LjY4MFoiLCJlbWFpbCI6ImNoYXNlcm9jaG9uNzc3QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczovL2lkZW50aXR5Lmh1ZGwuY29tLyIsImF1ZCI6Ik1jNlVXcXV5eVk0S3F4M2xPVEV5Q0JEaHZlRjkyQ3FaIiwic3ViIjoiYXV0aDB8aHVkbHwxOTEwMzIzMCIsImlhdCI6MTc1ODA1NDgyMCwiZXhwIjoxNzU5MjY0NDIwLCJzaWQiOiJPLWdOSzdwUDVCbXF6bi01Mll0dU5hcklENXIxd19LZyIsIm5vbmNlIjoiUTFKaFRYWkJVMU5IVmpCcU9HTkNNbWN5TW1aV01qaHJNM0V6WjFkWlJERkhVRmhtYW5saFkyMUpSUT09In0.Z3ZbtJB8I8kzldhH3pWalJH8cWeSUf5eokPuI-HUV_WZV_Yv1WhixeY3v8OoNCurQkhPTMl7Og5gqc2xvXgM0M_cw6Q5wmyNUwliljizklmDoXhg77XkOlGeTHldMUnbEKi9g0wqGsM2DpMUWGvugUAkfGYLa6Gh1xYmcJMyjp1eB8ZZvBJaqwP9o_R5z6s43YULLJvGmsywVTNAvm-78gD_OBINSkZwHmS4hxmknxozQLagsr5OV7XPTAPKtd0rsOCe50MD4ekaKPFy166pVsEGZ2NIs8ePo4nOOjJfLxpDNz6_MhLmwGKZBtHWW18F6S755IHcvos8_wPyQALM8A"
    
    x_auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImNoYXNlcm9jaG9uNzc3QGdtYWlsLmNvbSIsInRva2VuIjoiUGJ0NnZlZjhTZGxZN3QyRFhPRDdDUEVKQnhoSUdobUUiLCJleHAiOjE3NjA2NDY4MTgsImlhdCI6MTc1ODA1NDgxOH0.4VnSbmzWIkZj_tC-xj_0wy9d05jD85k-skfBl5r-f90"
    
    # Cookies from the actual network request
    cookies = {
        'sp': '093e65ec-5dc6-4fd6-9cc6-a97517162848',
        'employee': 'false',
        'token': 'Pbt6vef8SdlY7t2DXOD7CPEJBxhIGhmE',
        'CloudFront-Key-Pair-Id': 'K32VAT8DA954VA',
        'CloudFront-Policy': 'eyJTdGF0ZW1lbnQiOiBbeyJSZXNvdXJjZSI6IioiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3NTkyNjQ0MjB9fX1dfQ__',
        'CloudFront-Signature': 'LPs87gGS~dldQSyShlMGRAQmy2dwaT~PxLNPP9bc9a3SWcpm21qW6Q4s7XgHJXkZlg1wvCFRe-qmD23uMdvgU9wyUoM-YUjyo31eiy-sY-x7apOdNOoF2KZ9aJLlnGv~6idb-TRJ27iOFGu8j3vKggzoPuTKERDcy-eGuDS5ucLyXSqTndzStcrsCA7D14qJaJfLqzH2oPMsp7xfGKYoYCeHpgpFGj4BSWdVCaHvHiT4IMarGas82rdl5X0EP-Q09QndriRBC0Zde8ySaNxBedG29NhtZUMJV8IXmLUw5vlByFkeRn3Atpr8akpdDBBPE8G-WgRjUAKEu0UvWe5jEg__',
        'locale-des': '',
        'locale-rec': 'en-CA',
        'locale-tl': '',
        'locale-tog': '',
        'ident': 'a=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjZaYjBkN0VpWG9TQ0FhUTdYaW90SCJ9.eyJodHRwczovL2lkZW50aXR5Lmh1ZGwuY29tL2Nvbm5lY3Rpb25fbmFtZSI6InByb2QtaHVkbC11c2Vycy10ZXJyYWZvcm0iLCJodHRwczovL2lkZW50aXR5Lmh1ZGwuY29tL3VzZXJfaWQiOiIxOTEwMzIzMCIsImh0dHBzOi8vaWRlbnRpdHkuaHVkbC5jb20vdG9rIjoiaWQiLCJodHRwczovL2lkZW50aXR5Lmh1ZGwuY29tL2lzX3N5c2FkbWluIjpmYWxzZSwiaHR0cHM6Ly9pZGVudGl0eS5odWRsLmNvbS9pbnRlcm5hbF9pZF9odWRsIjoiMTkxMDMyMzAiLCJodHRwczovL2lkZW50aXR5Lmh1ZGwuY29tL2ludGVybmFsX2lkX2luc3RhdCI6NDU1MjE0LCJodHRwczovL2lkZW50aXR5Lmh1ZGwuY29tL2luc3RhdF90b2tlbiI6ImV5SmhiR2NpT2lKSVV6STFOaUlzSW5SNWNDSTZJa3BYVkNKOS5leUpsYldGcGJDSTZJbU5vWVhObGNtOWphRzl1TnpjM1FHZHRZV2xzTG1OdmJTSXNJblJ2YTJWdUlqb2lVR0owTm5abFpqaFRaR3haTjNReVJGaFBSRGREVUVWS1FuaG9TVWRvYlVVaUxDSmxlSEFpT2pFM05qQTJORFk0TVRnc0ltbGhkQ0k2TVRjMU9EQTFORGd4T0gwLjRWblNibXpXSWtaal90Qy14al8wd3k5ZDA1akQ4NWstc2tmQmw1ci1mOTAiLCJuaWNrbmFtZSI6ImNoYXNlcm9jaG9uNzc3IiwibmFtZSI6ImNoYXNlcm9jaG9uNzc3QGdtYWlsLmNvbSIsInBpY3R1cmUiOiJodHRwczovL3MuZ3JhdmF0YXIuY29tL2F2YXRhci8xMTAwOTlhMjQ0NGI5MDJjNzU3OGRhNjBmYWY5N2YxMj9zPTQ4MCZyPXBnJmQ9aHR0cHMlM0ElMkYlMkZjZG4uYXV0aDAuY29tJTJGYXZhdGFycyUyRmNoLnBuZyIsInVwZGF0ZWRfYXQiOiIyMDI1LTA5LTE2VDIwOjMzOjM3LjY4MFoiLCJlbWFpbCI6ImNoYXNlcm9jaG9uNzc3QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczovL2lkZW50aXR5Lmh1ZGwuY29tLyIsImF1ZCI6Ik1jNlVXcXV5eVk0S3F4M2xPVEV5Q0JEaHZlRjkyQ3FaIiwic3ViIjoiYXV0aDB8aHVkbHwxOTEwMzIzMCIsImlhdCI6MTc1ODA1NDgyMCwiZXhwIjoxNzU5MjY0NDIwLCJzaWQiOiJPLWdOSzdwUDVCbXF6bi01Mll0dU5hcklENXIxd19LZyIsIm5vbmNlIjoiUTFKaFRYWkJVMU5IVmpCcU9HTkNNbWN5TW1aV01qaHJNM0V6WjFkWlJERkhVRmhtYW5saFkyMUpSUT09In0.Z3ZbtJB8I8kzldhH3pWalJH8cWeSUf5eokPuI-HUV_WZV_Yv1WhixeY3v8OoNCurQkhPTMl7Og5gqc2xvXgM0M_cw6Q5wmyNUwliljizklmDoXhg77XkOlGeTHldMUnbEKi9g0wqGsM2DpMUWGvugUAkfGYLa6Gh1xYmcJMyjp1eB8ZZvBJaqwP9o_R5z6s43YULLJvGmsywVTNAvm-78gD_OBINSkZwHmS4hxmknxozQLagsr5OV7XPTAPKtd0rsOCe50MD4ekaKPFy166pVsEGZ2NIs8ePo4nOOjJfLxpDNz6_MhLmwGKZBtHWW18F6S755IHcvos8_wPyQALM8A&u=19103230&n=chaserochon777',
        'p': 'sport=footballrecruiting&team=&username=',
        '_hjSessionUser_1417044': 'eyJpZCI6Ijk1YTk5N2E5LTAzOTYtNWJkYi04YTYyLTJkOGFmZGVkZTMyNCIsImNyZWF0ZWQiOjE3NTczNjEwMDI1NDYsImV4aXN0aW5nIjp0cnVlfQ==',
        'tzoffset': '-5',
        '_ym_d': '1757361003',
        '_ym_uid': '1757361003638517047'
    }
    
    # Set authentication
    if not client.set_authentication(authorization_token, x_auth_token, cookies):
        logger.error("❌ Authentication setup failed")
        return
    
    # Test with Lloydminster Bobcats (team_id: 21479)
    team_id = "21479"
    season_id = "34"
    
    logger.info(f"🧪 Testing working API client with team {team_id}")
    
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
    with open("working_api_results.json", "w") as f:
        json.dump(comprehensive_data, f, indent=2)
    
    logger.info("✅ Working API test results saved to working_api_results.json")

if __name__ == "__main__":
    main()
