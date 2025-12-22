#!/usr/bin/env python3
"""
Standings Tracker
Tracks NHL standings and calculates playoff race desperation index
"""
from typing import Dict, Optional
from datetime import datetime
from nhl_api_client import NHLAPIClient

class StandingsTracker:
    def __init__(self):
        self.api = NHLAPIClient()
        self.standings_cache = {}
    
    def get_current_standings(self, date: str = None) -> Dict:
        """Get current NHL standings"""
        # Check cache
        cache_key = date or datetime.now().strftime('%Y-%m-%d')
        if cache_key in self.standings_cache:
            return self.standings_cache[cache_key]
        
        try:
            # NHL API standings endpoint
            url = f"https://api-web.nhle.com/v1/standings/{date or 'now'}"
            response = self.api.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse standings by team
            standings = {}
            for standing in data.get('standings', []):
                team_abbr = standing.get('teamAbbrev', {}).get('default', '')
                if team_abbr:
                    standings[team_abbr] = {
                        'points': standing.get('points', 0),
                        'games_played': standing.get('gamesPlayed', 0),
                        'wins': standing.get('wins', 0),
                        'losses': standing.get('losses', 0),
                        'ot_losses': standing.get('otLosses', 0),
                        'conference_rank': standing.get('conferenceSequence', 99),
                        'division_rank': standing.get('divisionSequence', 99),
                        'wildcard_rank': standing.get('wildcardSequence', 0)
                    }
            
            # Cache the result
            self.standings_cache[cache_key] = standings
            return standings
            
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return {}
    
    def get_playoff_threshold(self, standings: Dict, conference: str) -> int:
        """Get the points threshold for playoff spot (WC2)"""
        # Find the 8th place team in conference (last playoff spot)
        conference_teams = []
        
        for team, data in standings.items():
            # Determine conference (simplified - would need team-to-conference mapping)
            conference_teams.append((team, data['points']))
        
        # Sort by points
        conference_teams.sort(key=lambda x: x[1], reverse=True)
        
        # 8th place is the cutoff (16 teams make playoffs, 8 per conference)
        if len(conference_teams) >= 8:
            return conference_teams[7][1]  # 8th place points
        
        return 90  # Default threshold
    
    def calculate_desperation_index(self, team: str, date: str = None) -> float:
        """Calculate team's playoff desperation index
        
        Returns:
            float: -0.10 to +0.10 adjustment factor
                   Positive = desperate (fighting for playoffs)
                   Negative = eliminated/tanking
                   Zero = locked in or mid-season
        """
        standings = self.get_current_standings(date)
        
        if team not in standings:
            return 0.0
        
        team_data = standings[team]
        points = team_data['points']
        games_played = team_data['games_played']
        games_remaining = 82 - games_played
        
        # Get playoff threshold (simplified - using 90 points as rough cutoff)
        playoff_threshold = 90
        
        # Calculate points from playoff spot
        points_back = playoff_threshold - points
        
        # Max points possible
        max_points = points + (games_remaining * 2)
        
        # Desperation logic
        if games_remaining < 10:
            # Late season
            if points_back <= -10:
                # Locked in, coasting
                return -0.02
            elif -5 <= points_back <= 5:
                # Bubble team, high desperation
                return 0.10
            elif points_back > 10 and max_points < playoff_threshold:
                # Mathematically eliminated, tanking
                return -0.08
        elif games_remaining < 20:
            # Playoff push
            if -3 <= points_back <= 8:
                # In the hunt
                return 0.06
        
        # Mid-season or safe position
        return 0.0
    
    def get_rivalry_intensity(self, away_team: str, home_team: str) -> float:
        """Calculate rivalry intensity bonus
        
        Returns:
            float: 0.0 to 0.08 intensity bonus
        """
        # Original Six rivalries
        original_six_rivalries = {
            ('BOS', 'MTL'), ('MTL', 'BOS'),
            ('TOR', 'MTL'), ('MTL', 'TOR'),
            ('NYR', 'NYI'), ('NYI', 'NYR'),
            ('BOS', 'TOR'), ('TOR', 'BOS'),
            ('CHI', 'DET'), ('DET', 'CHI'),
        }
        
        # Provincial rivalries
        provincial_rivalries = {
            ('EDM', 'CGY'), ('CGY', 'EDM'),
            ('VAN', 'CGY'), ('CGY', 'VAN'),
            ('TOR', 'OTT'), ('OTT', 'TOR'),
            ('MTL', 'OTT'), ('OTT', 'MTL'),
        }
        
        # State rivalries
        state_rivalries = {
            ('NYR', 'NYI'), ('NYI', 'NYR'),
            ('NYR', 'NJD'), ('NJD', 'NYR'),
            ('LAK', 'ANA'), ('ANA', 'LAK'),
            ('FLA', 'TBL'), ('TBL', 'FLA'),
        }
        
        matchup = (away_team, home_team)
        
        if matchup in original_six_rivalries:
            return 0.08
        elif matchup in provincial_rivalries:
            return 0.07
        elif matchup in state_rivalries:
            return 0.05
        
        # Division games (simplified - would need division mapping)
        # For now, return small bonus for any matchup
        return 0.02

if __name__ == "__main__":
    tracker = StandingsTracker()
    
    print("🏆 NHL Standings & Playoff Race Tracker")
    print("=" * 60)
    
    # Get current standings
    standings = tracker.get_current_standings()
    
    if standings:
        print(f"\n📊 Current Standings (Top 10 by points):")
        sorted_teams = sorted(standings.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        
        for i, (team, data) in enumerate(sorted_teams, 1):
            desperation = tracker.calculate_desperation_index(team)
            print(f"{i:2}. {team:3} - {data['points']:3} pts ({data['wins']}-{data['losses']}-{data['ot_losses']}) "
                  f"[Desperation: {desperation:+.2f}]")
        
        # Test rivalry detection
        print(f"\n🔥 Rivalry Intensity Examples:")
        rivalries = [
            ('BOS', 'MTL'),
            ('EDM', 'CGY'),
            ('NYR', 'NYI'),
            ('STL', 'TBL')
        ]
        
        for away, home in rivalries:
            intensity = tracker.get_rivalry_intensity(away, home)
            print(f"   {away} @ {home}: {intensity:+.2f}")
    else:
        print("❌ Could not fetch standings")
