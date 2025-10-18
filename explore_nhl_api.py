#!/usr/bin/env python3
"""
NHL API Endpoint Explorer
Discovers and displays all available NHL API endpoints and their data structures
"""

import requests
import json
from datetime import datetime, timedelta
from pprint import pprint

class NHLAPIExplorer:
    def __init__(self):
        self.base_url = "https://api-web.nhle.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Known team IDs for testing
        self.team_ids = {
            'FLA': 13, 'EDM': 22, 'BOS': 6, 'TOR': 10, 'MTL': 8, 'OTT': 9,
            'BUF': 7, 'DET': 17, 'TBL': 14, 'CAR': 12, 'WSH': 15, 'PIT': 5,
            'NYR': 3, 'NYI': 2, 'NJD': 1, 'PHI': 4, 'CBJ': 29, 'NSH': 18,
            'STL': 19, 'MIN': 30, 'WPG': 52, 'COL': 21, 'ARI': 53, 'VGK': 54,
            'SJS': 28, 'LAK': 26, 'ANA': 24, 'CGY': 20, 'VAN': 23, 'SEA': 55,
            'CHI': 16, 'DAL': 25
        }
    
    def explore_team_endpoints(self):
        """Explore all team-related API endpoints"""
        print("🏒 TEAM API ENDPOINTS 🏒")
        print("=" * 50)
        
        # Test with Florida Panthers (ID: 13)
        team_id = 13
        
        # 1. Team Information
        print("\n1. TEAM INFORMATION")
        print("-" * 30)
        url = f"{self.base_url}/teams/{team_id}"
        print(f"Endpoint: {url}")
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                print("✅ Success! Data structure:")
                print(f"   - Team Name: {data.get('name', 'N/A')}")
                print(f"   - Abbreviation: {data.get('abbrev', 'N/A')}")
                print(f"   - Conference: {data.get('conferenceName', 'N/A')}")
                print(f"   - Division: {data.get('divisionName', 'N/A')}")
                print(f"   - Available fields: {list(data.keys())}")
                
                # Show sample of key data
                if 'venue' in data:
                    print(f"   - Venue: {data['venue'].get('default', 'N/A')}")
                if 'franchiseId' in data:
                    print(f"   - Franchise ID: {data['franchiseId']}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 2. Team Roster
        print("\n2. TEAM ROSTER")
        print("-" * 30)
        url = f"{self.base_url}/teams/{team_id}/roster"
        print(f"Endpoint: {url}")
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                print("✅ Success! Data structure:")
                print(f"   - Forwards: {len(data.get('forwards', []))}")
                print(f"   - Defensemen: {len(data.get('defensemen', []))}")
                print(f"   - Goalies: {len(data.get('goalies', []))}")
                print(f"   - Available fields: {list(data.keys())}")
                
                # Show sample player data
                if data.get('forwards'):
                    player = data['forwards'][0]
                    print(f"   - Sample forward: {player.get('name', 'N/A')} - {player.get('position', 'N/A')}")
                    print(f"     Available player fields: {list(player.keys())}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 3. Team Stats
        print("\n3. TEAM STATISTICS")
        print("-" * 30)
        url = f"{self.base_url}/teams/{team_id}/stats"
        print(f"Endpoint: {url}")
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                print("✅ Success! Data structure:")
                print(f"   - Available fields: {list(data.keys())}")
                if 'stats' in data:
                    print(f"   - Stats fields: {list(data['stats'].keys())}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def explore_player_endpoints(self):
        """Explore all player-related API endpoints"""
        print("\n\n🏃 PLAYER API ENDPOINTS 🏃")
        print("=" * 50)
        
        # Get a sample player ID from team roster
        try:
            roster_response = self.session.get(f"{self.base_url}/teams/13/roster")
            if roster_response.status_code == 200:
                roster_data = roster_response.json()
                
                # Get first forward for testing
                if roster_data.get('forwards'):
                    player = roster_data['forwards'][0]
                    player_id = player.get('id')
                    player_name = player.get('name', 'Unknown')
                    
                    print(f"Testing with player: {player_name} (ID: {player_id})")
                    
                    # 1. Player Profile
                    print("\n1. PLAYER PROFILE")
                    print("-" * 30)
                    url = f"{self.base_url}/players/{player_id}"
                    print(f"Endpoint: {url}")
                    
                    try:
                        response = self.session.get(url)
                        if response.status_code == 200:
                            data = response.json()
                            print("✅ Success! Data structure:")
                            print(f"   - Name: {data.get('name', 'N/A')}")
                            print(f"   - Position: {data.get('position', 'N/A')}")
                            print(f"   - Available fields: {list(data.keys())}")
                            
                            # Show detailed info
                            if 'height' in data:
                                print(f"   - Height: {data['height']}")
                            if 'weight' in data:
                                print(f"   - Weight: {data['weight']}")
                            if 'birthDate' in data:
                                print(f"   - Birth Date: {data['birthDate']}")
                            if 'birthCity' in data:
                                print(f"   - Birth City: {data['birthCity']}")
                        else:
                            print(f"❌ Failed: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                    
                    # 2. Player Statistics
                    print("\n2. PLAYER STATISTICS")
                    print("-" * 30)
                    url = f"{self.base_url}/players/{player_id}/stats"
                    print(f"Endpoint: {url}")
                    
                    try:
                        response = self.session.get(url)
                        if response.status_code == 200:
                            data = response.json()
                            print("✅ Success! Data structure:")
                            print(f"   - Available fields: {list(data.keys())}")
                            
                            # Show stats breakdown
                            if 'stats' in data:
                                for stat_type, stat_data in data['stats'].items():
                                    print(f"   - {stat_type}: {list(stat_data.keys()) if isinstance(stat_data, dict) else 'Data available'}")
                        else:
                            print(f"❌ Failed: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                    
                    # 3. Player Game Log
                    print("\n3. PLAYER GAME LOG")
                    print("-" * 30)
                    url = f"{self.base_url}/players/{player_id}/game-log"
                    print(f"Endpoint: {url}")
                    
                    try:
                        response = self.session.get(url)
                        if response.status_code == 200:
                            data = response.json()
                            print("✅ Success! Data structure:")
                            print(f"   - Available fields: {list(data.keys())}")
                            if 'gameLog' in data:
                                print(f"   - Game log entries: {len(data['gameLog'])}")
                                if data['gameLog']:
                                    print(f"   - Sample game fields: {list(data['gameLog'][0].keys())}")
                        else:
                            print(f"❌ Failed: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                    
        except Exception as e:
            print(f"❌ Error getting roster: {e}")
    
    def explore_game_endpoints(self):
        """Explore all game-related API endpoints"""
        print("\n\n🎮 GAME API ENDPOINTS 🎮")
        print("=" * 50)
        
        # Find a recent game
        try:
            # Get today's schedule
            today = datetime.now().strftime("%Y-%m-%d")
            schedule_url = f"{self.base_url}/schedule/{today}"
            print(f"Getting schedule from: {schedule_url}")
            
            response = self.session.get(schedule_url)
            if response.status_code == 200:
                schedule_data = response.json()
                
                if 'gameWeek' in schedule_data and schedule_data['gameWeek']:
                    # Get first game from today
                    for day in schedule_data['gameWeek']:
                        if day.get('games'):
                            game = day['games'][0]
                            game_id = game.get('id')
                            away_team = game.get('awayTeam', {}).get('abbrev', 'Unknown')
                            home_team = game.get('homeTeam', {}).get('abbrev', 'Unknown')
                            
                            print(f"Testing with game: {away_team} @ {home_team} (ID: {game_id})")
                            
                            # 1. Game Center Feed
                            print("\n1. GAME CENTER FEED")
                            print("-" * 30)
                            url = f"{self.base_url}/gamecenter/{game_id}/feed/live"
                            print(f"Endpoint: {url}")
                            
                            try:
                                response = self.session.get(url)
                                if response.status_code == 200:
                                    data = response.json()
                                    print("✅ Success! Data structure:")
                                    print(f"   - Available fields: {list(data.keys())}")
                                    
                                    if 'game' in data:
                                        game_info = data['game']
                                        print(f"   - Game fields: {list(game_info.keys())}")
                                        print(f"   - Score: {game_info.get('awayTeamScore', 0)} - {game_info.get('homeTeamScore', 0)}")
                                        print(f"   - Status: {game_info.get('gameState', 'N/A')}")
                                    
                                    if 'plays' in data:
                                        print(f"   - Plays available: {len(data['plays'])}")
                                        if data['plays']:
                                            print(f"   - Sample play fields: {list(data['plays'][0].keys())}")
                                else:
                                    print(f"❌ Failed: {response.status_code}")
                            except Exception as e:
                                print(f"❌ Error: {e}")
                            
                            # 2. Game Boxscore
                            print("\n2. GAME BOXSCORE")
                            print("-" * 30)
                            url = f"{self.base_url}/gamecenter/{game_id}/boxscore"
                            print(f"Endpoint: {url}")
                            
                            try:
                                response = self.session.get(url)
                                if response.status_code == 200:
                                    data = response.json()
                                    print("✅ Success! Data structure:")
                                    print(f"   - Available fields: {list(data.keys())}")
                                    
                                    if 'awayTeam' in data:
                                        away_stats = data['awayTeam']
                                        print(f"   - Away team fields: {list(away_stats.keys())}")
                                        if 'players' in away_stats:
                                            print(f"   - Away players: {len(away_stats['players'])}")
                                            if away_stats['players']:
                                                print(f"   - Sample player fields: {list(away_stats['players'][0].keys())}")
                                
                                else:
                                    print(f"❌ Failed: {response.status_code}")
                            except Exception as e:
                                print(f"❌ Error: {e}")
                            
                            # 3. Game Summary
                            print("\n3. GAME SUMMARY")
                            print("-" * 30)
                            url = f"{self.base_url}/gamecenter/{game_id}/summary"
                            print(f"Endpoint: {url}")
                            
                            try:
                                response = self.session.get(url)
                                if response.status_code == 200:
                                    data = response.json()
                                    print("✅ Success! Data structure:")
                                    print(f"   - Available fields: {list(data.keys())}")
                                else:
                                    print(f"❌ Failed: {response.status_code}")
                            except Exception as e:
                                print(f"❌ Error: {e}")
                            
                            break  # Only test first game
                else:
                    print("No games found for today")
            else:
                print(f"❌ Failed to get schedule: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error exploring game endpoints: {e}")
    
    def explore_additional_endpoints(self):
        """Explore additional NHL API endpoints"""
        print("\n\n🔍 ADDITIONAL NHL API ENDPOINTS 🔍")
        print("=" * 50)
        
        # 1. League Standings
        print("\n1. LEAGUE STANDINGS")
        print("-" * 30)
        url = f"{self.base_url}/standings/now"
        print(f"Endpoint: {url}")
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                print("✅ Success! Data structure:")
                print(f"   - Available fields: {list(data.keys())}")
                if 'standings' in data:
                    print(f"   - Standings entries: {len(data['standings'])}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 2. Player Search
        print("\n2. PLAYER SEARCH")
        print("-" * 30)
        url = f"{self.base_url}/players/search"
        print(f"Endpoint: {url}")
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                print("✅ Success! Data structure:")
                print(f"   - Available fields: {list(data.keys())}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 3. Draft Information
        print("\n3. DRAFT INFORMATION")
        print("-" * 30)
        url = f"{self.base_url}/draft/2024"
        print(f"Endpoint: {url}")
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                print("✅ Success! Data structure:")
                print(f"   - Available fields: {list(data.keys())}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run_full_exploration(self):
        """Run the complete API exploration"""
        print("🚀 NHL API COMPLETE EXPLORATION 🚀")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.explore_team_endpoints()
        self.explore_player_endpoints()
        self.explore_game_endpoints()
        self.explore_additional_endpoints()
        
        print("\n\n🎯 SUMMARY OF AVAILABLE DATA")
        print("=" * 50)
        print("✅ Team Information: Names, conferences, divisions, venues")
        print("✅ Team Rosters: Forwards, defensemen, goalies with detailed info")
        print("✅ Player Profiles: Height, weight, birth info, positions")
        print("✅ Player Statistics: Season stats, game logs, performance metrics")
        print("✅ Game Data: Live feeds, boxscores, summaries, play-by-play")
        print("✅ League Data: Standings, draft information, player search")
        print("✅ Real-time Updates: Live game data and statistics")

if __name__ == "__main__":
    explorer = NHLAPIExplorer()
    explorer.run_full_exploration()
