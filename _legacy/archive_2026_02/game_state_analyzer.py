"""
Game State Analyzer - Analyzes historical comeback patterns and game states
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import requests

class GameStateAnalyzer:
    def __init__(self):
        self.game_state_data = {}
        self.comeback_rates = {}
        self.load_game_state_data()
    
    def load_game_state_data(self):
        """Load historical game state data"""
        data_file = "game_state_data.json"
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                self.game_state_data = json.load(f)
                print(f"Loaded {len(self.game_state_data)} game states")
        else:
            print("No game state data found, will build from scratch")
            self.game_state_data = {}
    
    def save_game_state_data(self):
        """Save game state data to file"""
        with open("game_state_data.json", 'w') as f:
            json.dump(self.game_state_data, f, indent=2)
        print(f"Saved {len(self.game_state_data)} game states")
    
    def analyze_historical_games(self, days_back=30):
        """Analyze historical games to build comeback rate database"""
        print(f"Analyzing last {days_back} days of games for comeback patterns...")
        
        # Get recent games
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        games_analyzed = 0
        comeback_rates = defaultdict(lambda: {'total': 0, 'comebacks': 0})
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            print(f"Analyzing games for {date_str}...")
            
            try:
                # Get games for this date
                url = f"https://api-web.nhle.com/v1/score/{date_str}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    games = data.get('games', [])
                    
                    for game in games:
                        if self.analyze_single_game(game, comeback_rates):
                            games_analyzed += 1
                            
            except Exception as e:
                print(f"Error analyzing {date_str}: {e}")
            
            current_date += timedelta(days=1)
        
        # Calculate comeback rates
        for state, data in comeback_rates.items():
            if data['total'] > 0:
                comeback_rate = data['comebacks'] / data['total']
                self.comeback_rates[state] = comeback_rate
                print(f"State {state}: {data['comebacks']}/{data['total']} = {comeback_rate:.1%}")
        
        # Save the comeback rates to game state data
        self.game_state_data = self.comeback_rates
        
        print(f"Analyzed {games_analyzed} games")
        self.save_game_state_data()
        return self.comeback_rates
    
    def analyze_single_game(self, game, comeback_rates):
        """Analyze a single game for comeback patterns"""
        try:
            game_id = game.get('id')
            if not game_id:
                return False
            
            # Get play-by-play data
            pbp_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
            response = requests.get(pbp_url, timeout=10)
            if response.status_code != 200:
                return False
            
            pbp_data = response.json()
            plays = pbp_data.get('plays', [])
            
            if not plays:
                return False
            
            # Track score progression
            away_score = 0
            home_score = 0
            period = 1
            
            for play in plays:
                if play.get('typeDescKey') == 'goal':
                    # Goal scored
                    if play.get('teamId') == game.get('awayTeam', {}).get('id'):
                        away_score += 1
                    else:
                        home_score += 1
                    
                    # Check for comeback opportunities
                    self.check_comeback_state(
                        away_score, home_score, period, 
                        game, comeback_rates, plays, play
                    )
                
                elif play.get('typeDescKey') == 'period-start':
                    period = play.get('period', period)
            
            return True
            
        except Exception as e:
            print(f"Error analyzing game {game.get('id', 'unknown')}: {e}")
            return False
    
    def check_comeback_state(self, away_score, home_score, period, game, comeback_rates, plays, current_play):
        """Check if current state represents a comeback opportunity"""
        try:
            # Determine if this is a comeback situation
            score_diff = abs(away_score - home_score)
            time_remaining = self.get_time_remaining(period, current_play)
            
            # Only consider significant deficits (2+ goals) with time remaining
            if score_diff < 2 or time_remaining < 300:  # Less than 5 minutes
                return
            
            # Create state key
            if away_score > home_score:
                # Away team leading
                state = f"home_down_{score_diff}_p{period}_t{time_remaining//60}"
                trailing_team = game.get('homeTeam', {}).get('abbrev', 'HOME')
            else:
                # Home team leading  
                state = f"away_down_{score_diff}_p{period}_t{time_remaining//60}"
                trailing_team = game.get('awayTeam', {}).get('abbrev', 'AWAY')
            
            # Check if trailing team came back
            final_away, final_home = self.get_final_score(plays)
            came_back = False
            
            if away_score > home_score and final_home > final_away:
                came_back = True
            elif home_score > away_score and final_away > final_home:
                came_back = True
            
            # Record this state
            comeback_rates[state]['total'] += 1
            if came_back:
                comeback_rates[state]['comebacks'] += 1
                
        except Exception as e:
            print(f"Error checking comeback state: {e}")
    
    def get_time_remaining(self, period, play):
        """Get time remaining in seconds"""
        try:
            time_str = play.get('timeInPeriod', '20:00')
            if ':' in time_str:
                minutes, seconds = map(int, time_str.split(':'))
                time_remaining = minutes * 60 + seconds
            else:
                time_remaining = 1200  # 20 minutes default
            
            # Adjust for period
            if period > 3:
                time_remaining += (period - 3) * 1200  # Overtime periods
            
            return time_remaining
        except:
            return 1200  # Default 20 minutes
    
    def get_final_score(self, plays):
        """Get final score from plays"""
        away_score = 0
        home_score = 0
        
        # Get team IDs from the game data
        away_team_id = None
        home_team_id = None
        
        for play in plays:
            if 'awayTeam' in play and 'homeTeam' in play:
                away_team_id = play['awayTeam']['id']
                home_team_id = play['homeTeam']['id']
                break
        
        if not away_team_id or not home_team_id:
            return 0, 0
        
        for play in plays:
            if play.get('typeDescKey') == 'goal':
                if play.get('teamId') == away_team_id:
                    away_score += 1
                elif play.get('teamId') == home_team_id:
                    home_score += 1
        
        return away_score, home_score
    
    def get_comeback_probability(self, score_diff, period, time_remaining, trailing_team_type):
        """Get comeback probability for current game state"""
        # Create state key
        time_bucket = time_remaining // 60  # Round to nearest minute
        state = f"{trailing_team_type}_down_{score_diff}_p{period}_t{time_bucket}"
        
        # Get exact match or closest match
        if state in self.comeback_rates:
            return self.comeback_rates[state]
        
        # Try to find similar states
        for key, rate in self.comeback_rates.items():
            if (f"down_{score_diff}" in key and 
                f"p{period}" in key and 
                trailing_team_type in key):
                return rate
        
        # Default comeback rates based on score differential
        default_rates = {
            1: 0.35,  # 35% chance to come back from 1 goal down
            2: 0.15,  # 15% chance to come back from 2 goals down  
            3: 0.05,  # 5% chance to come back from 3 goals down
            4: 0.01,  # 1% chance to come back from 4 goals down
        }
        
        return default_rates.get(score_diff, 0.01)
    
    def analyze_current_game_state(self, game_id):
        """Analyze current game state for comeback probability"""
        try:
            # Get current game data
            url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return None
            
            data = response.json()
            plays = data.get('plays', [])
            
            if not plays:
                return None
            
            # Get current score and period
            current_play = plays[-1] if plays else {}
            away_score = current_play.get('awayScore', 0)
            home_score = current_play.get('homeScore', 0)
            period = current_play.get('period', 1)
            time_remaining = self.get_time_remaining(period, current_play)
            
            # Determine trailing team
            if away_score > home_score:
                score_diff = away_score - home_score
                trailing_team = "home"
                leading_team = "away"
            elif home_score > away_score:
                score_diff = home_score - away_score
                trailing_team = "away" 
                leading_team = "home"
            else:
                return None  # Tied game
            
            # Get comeback probability
            comeback_prob = self.get_comeback_probability(
                score_diff, period, time_remaining, trailing_team
            )
            
            return {
                'away_score': away_score,
                'home_score': home_score,
                'score_diff': score_diff,
                'period': period,
                'time_remaining': time_remaining,
                'trailing_team': trailing_team,
                'leading_team': leading_team,
                'comeback_probability': comeback_prob
            }
            
        except Exception as e:
            print(f"Error analyzing current game state: {e}")
            return None

if __name__ == "__main__":
    analyzer = GameStateAnalyzer()
    
    # Build historical database
    print("Building comeback rate database...")
    comeback_rates = analyzer.analyze_historical_games(days_back=30)
    
    # Test on current game
    print("\nTesting on current VAN/WSH game...")
    game_state = analyzer.analyze_current_game_state(2025020089)
    if game_state:
        print(f"Current state: {game_state}")
        print(f"Comeback probability: {game_state['comeback_probability']:.1%}")
