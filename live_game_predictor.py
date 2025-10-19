#!/usr/bin/env python3
"""
Live Game Predictor - Get real-time win probability for any NHL game
"""

import os
import sys
from datetime import datetime
import pytz
from nhl_api_client import NHLAPIClient
from improved_self_learning_model import ImprovedSelfLearningModel

class LiveGamePredictor:
    def __init__(self):
        self.api = NHLAPIClient()
        self.model = ImprovedSelfLearningModel()
        
    def get_live_games(self, date=None):
        """Get all games happening on a specific date"""
        if date is None:
            central_tz = pytz.timezone('US/Central')
            date = datetime.now(central_tz).strftime('%Y-%m-%d')
        
        # Get games for the specified date
        games = self.api.get_game_schedule(date)
        
        # Handle different return types
        if isinstance(games, list):
            return games
        elif isinstance(games, dict) and 'dates' in games:
            # NHL API returns data in dates array
            all_games = []
            for date_data in games.get('dates', []):
                all_games.extend(date_data.get('games', []))
            return all_games
        else:
            return []
    
    def find_game(self, team1, team2, date=None):
        """Find a specific game between two teams"""
        games = self.get_live_games(date)
        
        print(f"📅 Found {len(games)} games on {date or 'today'}")
        
        for game in games:
            if not isinstance(game, dict):
                continue
                
            away_team = game.get('teams', {}).get('away', {}).get('team', {}).get('abbreviation', '')
            home_team = game.get('teams', {}).get('home', {}).get('team', {}).get('abbreviation', '')
            
            print(f"   {away_team} @ {home_team}")
            
            # Check if this is the game we're looking for
            if ((away_team == team1.upper() and home_team == team2.upper()) or 
                (away_team == team2.upper() and home_team == team1.upper())):
                return game
                
        return None
    
    def get_live_prediction(self, team1, team2, date=None):
        """Get live win probability for a specific game"""
        print(f"🔍 Looking for {team1.upper()} vs {team2.upper()}...")
        
        # Find the game
        game = self.find_game(team1, team2, date)
        if not game:
            print(f"❌ No game found between {team1.upper()} and {team2.upper()}")
            return None
        
        game_id = game.get('gamePk')
        away_team = game.get('teams', {}).get('away', {}).get('team', {}).get('abbreviation', '')
        home_team = game.get('teams', {}).get('home', {}).get('team', {}).get('abbreviation', '')
        game_state = game.get('status', {}).get('detailedState', '')
        
        print(f"✅ Found game: {away_team} @ {home_team} (Game ID: {game_id})")
        print(f"📊 Game State: {game_state}")
        
        # Get current game data
        game_data = self.api.get_comprehensive_game_data(str(game_id))
        if not game_data:
            print(f"❌ Could not get live game data for {game_id}")
            return None
        
        # Get live prediction
        prediction = self.model.predict_game(away_team, home_team)
        
        # Get current score if game is in progress
        current_score = self.get_current_score(game_data)
        
        return {
            'game_id': game_id,
            'away_team': away_team,
            'home_team': home_team,
            'game_state': game_state,
            'current_score': current_score,
            'prediction': prediction
        }
    
    def get_prediction_by_game_id(self, game_id):
        """Get prediction for a specific game ID"""
        print(f"🔍 Getting prediction for Game ID: {game_id}")
        
        # Get game data
        game_data = self.api.get_comprehensive_game_data(str(game_id))
        if not game_data:
            print(f"❌ Could not get game data for {game_id}")
            return None
        
        # Extract team info from game data
        try:
            # Try boxscore first (where the data actually is)
            boxscore = game_data.get('boxscore', {})
            away_team = boxscore.get('awayTeam', {}).get('abbrev', '')
            home_team = boxscore.get('homeTeam', {}).get('abbrev', '')
            
            # Fallback to gameData if boxscore doesn't have it
            if not away_team or not home_team:
                away_team = game_data.get('gameData', {}).get('teams', {}).get('away', {}).get('abbreviation', '')
                home_team = game_data.get('gameData', {}).get('teams', {}).get('home', {}).get('abbreviation', '')
            
            if not away_team or not home_team:
                print("❌ Could not extract team information from game data")
                return None
                
            print(f"✅ Found teams: {away_team} @ {home_team}")
            
            # Get prediction with current live score and live stats
            current_score = self.get_current_score(game_data)
            away_score, home_score = map(int, current_score.split('-'))
            prediction = self.model.predict_game(away_team, home_team, away_score, home_score, 2, game_id)  # Pass game_id for live stats
            
            return {
                'game_id': game_id,
                'away_team': away_team,
                'home_team': home_team,
                'game_state': 'Unknown',
                'current_score': current_score,
                'prediction': prediction
            }
            
        except Exception as e:
            print(f"❌ Error processing game data: {e}")
            return None
    
    def get_current_score(self, game_data):
        """Get current score from game data"""
        try:
            # Try the alternative API endpoint for live scores
            import requests
            game_id = game_data.get('game_center', {}).get('id') or game_data.get('boxscore', {}).get('id')
            if game_id:
                response = requests.get(f'https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play')
                if response.status_code == 200:
                    alt_data = response.json()
                    away_score = alt_data.get('awayTeam', {}).get('score', 0)
                    home_score = alt_data.get('homeTeam', {}).get('score', 0)
                    return f"{away_score}-{home_score}"
            
            # Fallback to original method
            boxscore = game_data.get('boxscore', {})
            away_score = boxscore.get('teams', {}).get('away', {}).get('teamStats', {}).get('teamSkaterStats', {}).get('goals', 0)
            home_score = boxscore.get('teams', {}).get('home', {}).get('teamStats', {}).get('teamSkaterStats', {}).get('goals', 0)
            return f"{away_score}-{home_score}"
        except:
            return "0-0"
    
    def display_prediction(self, result):
        """Display the prediction results"""
        if not result:
            return
            
        print("\n" + "="*60)
        print(f"🏒 LIVE GAME PREDICTION")
        print("="*60)
        print(f"Game: {result['away_team']} @ {result['home_team']}")
        print(f"Status: {result['game_state']}")
        print(f"Current Score: {result['current_score']}")
        print(f"Game ID: {result['game_id']}")
        print("-"*60)
        
        pred = result['prediction']
        away_prob = pred.get('away_prob', 50)
        home_prob = pred.get('home_prob', 50)
        confidence = pred.get('confidence', 50)
        
        print(f"📊 WIN PROBABILITY:")
        print(f"   {result['away_team']}: {away_prob:.1f}%")
        print(f"   {result['home_team']}: {home_prob:.1f}%")
        print(f"   Confidence: {confidence:.1f}%")
        
        # Determine favorite
        if away_prob > home_prob:
            favorite = result['away_team']
            favorite_prob = away_prob
        else:
            favorite = result['home_team']
            favorite_prob = home_prob
            
        print(f"\n🎯 FAVORITE: {favorite} ({favorite_prob:.1f}%)")
        
        # Add some context
        if confidence >= 60:
            print("✅ High confidence prediction")
        elif confidence >= 50:
            print("⚠️  Moderate confidence prediction")
        else:
            print("❓ Low confidence prediction")
            
        print("="*60)
    
    def demo_prediction(self, team1, team2):
        """Demonstrate prediction without requiring a real game"""
        print(f"🎮 DEMO MODE: Predicting {team1.upper()} vs {team2.upper()}")
        print("(This is a demonstration using the model without live game data)")
        
        # Get prediction
        prediction = self.model.predict_game(team1.upper(), team2.upper())
        
        result = {
            'game_id': 'DEMO',
            'away_team': team1.upper(),
            'home_team': team2.upper(),
            'game_state': 'Demo Mode',
            'current_score': '0-0',
            'prediction': prediction
        }
        
        self.display_prediction(result)

def main():
    """Main function for live predictions"""
    predictor = LiveGamePredictor()
    
    if len(sys.argv) >= 3:
        # Command line usage: python live_game_predictor.py WSH VAN
        team1 = sys.argv[1]
        team2 = sys.argv[2]
        
        # Try to find a real game first
        result = predictor.get_live_prediction(team1, team2)
        
        if result:
            predictor.display_prediction(result)
        else:
            # If no real game found, run demo mode
            print("\n🔄 No live game found, running demo mode...")
            predictor.demo_prediction(team1, team2)
        
    elif len(sys.argv) == 2:
        # Game ID mode: python live_game_predictor.py 2025020083
        game_id = sys.argv[1]
        result = predictor.get_prediction_by_game_id(game_id)
        predictor.display_prediction(result)
        
    else:
        # Interactive mode
        print("🏒 NHL Live Game Predictor")
        print("="*40)
        print("Usage:")
        print("  python live_game_predictor.py WSH VAN    # Predict specific teams")
        print("  python live_game_predictor.py 2025020083 # Predict by game ID")
        print("  python live_game_predictor.py            # Interactive mode")
        print("="*40)
        
        while True:
            try:
                print("\nEnter two team abbreviations (e.g., WSH VAN) or 'quit' to exit:")
                user_input = input("> ").strip().upper()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                teams = user_input.split()
                if len(teams) != 2:
                    print("❌ Please enter exactly two team abbreviations")
                    continue
                    
                team1, team2 = teams
                
                # Try to find a real game first
                result = predictor.get_live_prediction(team1, team2)
                
                if result:
                    predictor.display_prediction(result)
                else:
                    # If no real game found, run demo mode
                    print("\n🔄 No live game found, running demo mode...")
                    predictor.demo_prediction(team1, team2)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()