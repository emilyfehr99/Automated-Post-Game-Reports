#!/usr/bin/env python3
"""
Goalie Performance Tracker
Tracks detailed goalie metrics including recent form, matchup history, rest days, and workload
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from nhl_api_client import NHLAPIClient

class GoaliePerformanceTracker:
    def __init__(self):
        self.api = NHLAPIClient()
        self.goalie_cache = {}
    
    def get_goalie_recent_starts(self, goalie_name: str, team_abbr: str, n: int = 5) -> List[Dict]:
        """Get goalie's last N starts with detailed stats"""
        try:
            # Load predictions to find goalie's recent games
            with open('data/win_probability_predictions_v2.json', 'r') as f:
                data = json.load(f)
                predictions = data.get('predictions', [])
            
            # Find games where this goalie started
            goalie_games = []
            for pred in reversed(predictions):  # Most recent first
                if not pred.get('actual_winner'):
                    continue
                
                away_goalie = pred.get('metrics_used', {}).get('away_goalie')
                home_goalie = pred.get('metrics_used', {}).get('home_goalie')
                
                is_away = away_goalie and goalie_name.lower() in str(away_goalie).lower()
                is_home = home_goalie and goalie_name.lower() in str(home_goalie).lower()
                
                if is_away or is_home:
                    venue = 'away' if is_away else 'home'
                    opponent = pred['home_team'] if is_away else pred['away_team']
                    
                    # Determine if won
                    actual_winner = pred.get('actual_winner', '').upper()
                    team = pred['away_team'] if is_away else pred['home_team']
                    won = actual_winner == team.upper()
                    
                    # Get goals against
                    metrics = pred.get('metrics_used', {})
                    if is_away:
                        goals_against = metrics.get('home_goals', 0)
                        shots_against = metrics.get('home_shots', 0)
                    else:
                        goals_against = metrics.get('away_goals', 0)
                        shots_against = metrics.get('away_shots', 0)
                    
                    saves = shots_against - goals_against
                    sv_pct = (saves / shots_against) if shots_against > 0 else 0
                    
                    goalie_games.append({
                        'date': pred['date'],
                        'opponent': opponent,
                        'venue': venue,
                        'won': won,
                        'goals_against': goals_against,
                        'shots_against': shots_against,
                        'saves': saves,
                        'sv_pct': sv_pct,
                        'gsax': metrics.get(f'{venue}_gsax', 0)
                    })
                    
                    if len(goalie_games) >= n:
                        break
            
            return goalie_games
            
        except Exception as e:
            print(f"Error getting recent starts for {goalie_name}: {e}")
            return []
    
    def calculate_recent_form(self, goalie_name: str, team_abbr: str, n: int = 5) -> Dict:
        """Calculate goalie's recent form score"""
        recent_starts = self.get_goalie_recent_starts(goalie_name, team_abbr, n)
        
        if not recent_starts:
            return {
                'form_score': 0.0,
                'games_played': 0,
                'avg_sv_pct': 0.0,
                'avg_gsax': 0.0,
                'record': '0-0'
            }
        
        # Weight recent games more heavily
        weights = [0.3, 0.25, 0.20, 0.15, 0.10][:len(recent_starts)]
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]  # Normalize
        
        form_score = 0.0
        wins = 0
        losses = 0
        
        for i, game in enumerate(recent_starts):
            gsax = game.get('gsax', 0)
            form_score += gsax * weights[i]
            
            if game['won']:
                wins += 1
            else:
                losses += 1
        
        avg_sv_pct = sum(g['sv_pct'] for g in recent_starts) / len(recent_starts)
        avg_gsax = sum(g.get('gsax', 0) for g in recent_starts) / len(recent_starts)
        
        return {
            'form_score': form_score,
            'games_played': len(recent_starts),
            'avg_sv_pct': avg_sv_pct,
            'avg_gsax': avg_gsax,
            'record': f'{wins}-{losses}',
            'recent_starts': recent_starts
        }
    
    def get_rest_days(self, goalie_name: str, team_abbr: str, game_date: str = None) -> int:
        """Calculate days since goalie's last start"""
        if game_date is None:
            game_date = datetime.now().strftime('%Y-%m-%d')
        
        recent_starts = self.get_goalie_recent_starts(goalie_name, team_abbr, n=2)
        
        if not recent_starts:
            return 7  # Unknown, assume well-rested
        
        last_start_date = datetime.strptime(recent_starts[0]['date'], '%Y-%m-%d')
        current_date = datetime.strptime(game_date, '%Y-%m-%d')
        
        days_rest = (current_date - last_start_date).days
        return days_rest
    
    def calculate_fatigue_factor(self, goalie_name: str, team_abbr: str, game_date: str = None) -> Dict:
        """Calculate fatigue/rest impact on performance"""
        rest_days = self.get_rest_days(goalie_name, team_abbr, game_date)
        
        # Get workload (games in last 7 days)
        recent_starts = self.get_goalie_recent_starts(goalie_name, team_abbr, n=10)
        
        if game_date is None:
            game_date = datetime.now().strftime('%Y-%m-%d')
        
        current_date = datetime.strptime(game_date, '%Y-%m-%d')
        games_last_7 = sum(
            1 for g in recent_starts
            if (current_date - datetime.strptime(g['date'], '%Y-%m-%d')).days <= 7
        )
        
        # Calculate penalties
        if rest_days == 0:
            rest_penalty = -0.15  # Back-to-back
            rest_status = 'back_to_back'
        elif rest_days == 1:
            rest_penalty = -0.05  # 1 day rest
            rest_status = 'short_rest'
        elif rest_days in [2, 3]:
            rest_penalty = 0.0    # Optimal
            rest_status = 'optimal'
        elif rest_days >= 4:
            rest_penalty = -0.03  # Rust
            rest_status = 'rusty'
        else:
            rest_penalty = 0.0
            rest_status = 'normal'
        
        # Workload penalty
        if games_last_7 >= 4:
            workload_penalty = -0.10
            workload_status = 'heavy'
        elif games_last_7 == 3:
            workload_penalty = -0.05
            workload_status = 'moderate'
        else:
            workload_penalty = 0.0
            workload_status = 'normal'
        
        total_fatigue = rest_penalty + workload_penalty
        
        return {
            'rest_days': rest_days,
            'rest_status': rest_status,
            'rest_penalty': rest_penalty,
            'games_last_7': games_last_7,
            'workload_status': workload_status,
            'workload_penalty': workload_penalty,
            'total_fatigue_factor': total_fatigue
        }
    
    def get_matchup_history(self, goalie_name: str, team_abbr: str, opponent: str) -> Dict:
        """Get goalie's historical performance vs opponent"""
        try:
            with open('data/win_probability_predictions_v2.json', 'r') as f:
                data = json.load(f)
                predictions = data.get('predictions', [])
            
            # Find all games vs this opponent
            matchup_games = []
            for pred in predictions:
                if not pred.get('actual_winner'):
                    continue
                
                away_goalie = pred.get('metrics_used', {}).get('away_goalie')
                home_goalie = pred.get('metrics_used', {}).get('home_goalie')
                
                is_away = (away_goalie and goalie_name.lower() in str(away_goalie).lower() 
                          and pred['home_team'] == opponent)
                is_home = (home_goalie and goalie_name.lower() in str(home_goalie).lower() 
                          and pred['away_team'] == opponent)
                
                if is_away or is_home:
                    venue = 'away' if is_away else 'home'
                    metrics = pred.get('metrics_used', {})
                    
                    if is_away:
                        goals_against = metrics.get('home_goals', 0)
                        shots_against = metrics.get('home_shots', 0)
                    else:
                        goals_against = metrics.get('away_goals', 0)
                        shots_against = metrics.get('away_shots', 0)
                    
                    saves = shots_against - goals_against
                    sv_pct = (saves / shots_against) if shots_against > 0 else 0
                    
                    matchup_games.append({
                        'date': pred['date'],
                        'goals_against': goals_against,
                        'shots_against': shots_against,
                        'sv_pct': sv_pct,
                        'gsax': metrics.get(f'{venue}_gsax', 0)
                    })
            
            if not matchup_games:
                return {
                    'games_played': 0,
                    'avg_sv_pct': 0.0,
                    'avg_gsax': 0.0,
                    'modifier': 0.0
                }
            
            # Calculate career stats vs this team
            avg_sv_pct = sum(g['sv_pct'] for g in matchup_games) / len(matchup_games)
            avg_gsax = sum(g.get('gsax', 0) for g in matchup_games) / len(matchup_games)
            
            # Last 3 meetings
            recent_3 = matchup_games[:3]
            recent_gsax = sum(g.get('gsax', 0) for g in recent_3) / len(recent_3) if recent_3 else 0
            
            # Modifier: positive if performs well vs this team
            modifier = (avg_gsax * 0.6) + (recent_gsax * 0.4)
            
            return {
                'games_played': len(matchup_games),
                'avg_sv_pct': avg_sv_pct,
                'avg_gsax': avg_gsax,
                'recent_gsax': recent_gsax,
                'modifier': modifier,
                'last_3_games': recent_3
            }
            
        except Exception as e:
            print(f"Error getting matchup history: {e}")
            return {'games_played': 0, 'modifier': 0.0}
    
    def get_comprehensive_goalie_analysis(self, goalie_name: str, team_abbr: str, 
                                         opponent: str, game_date: str = None) -> Dict:
        """Get complete goalie analysis for prediction"""
        form = self.calculate_recent_form(goalie_name, team_abbr)
        fatigue = self.calculate_fatigue_factor(goalie_name, team_abbr, game_date)
        matchup = self.get_matchup_history(goalie_name, team_abbr, opponent)
        
        # Calculate overall goalie impact
        # Ensemble: 40% form + 30% matchup + 30% fatigue
        goalie_impact = (
            form['form_score'] * 0.40 +
            matchup['modifier'] * 0.30 +
            fatigue['total_fatigue_factor'] * 0.30
        )
        
        return {
            'goalie_name': goalie_name,
            'team': team_abbr,
            'opponent': opponent,
            'recent_form': form,
            'fatigue_analysis': fatigue,
            'matchup_history': matchup,
            'overall_impact': goalie_impact,
            'confidence': min(form['games_played'] / 5.0, 1.0)  # More games = more confidence
        }

if __name__ == "__main__":
    from rotowire_scraper import RotoWireScraper
    
    print("🥅 Goalie Performance Tracker - Live Analysis")
    print("=" * 60)
    
    # Get today's games
    scraper = RotoWireScraper()
    data = scraper.scrape_daily_data()
    
    if data['games']:
        game = data['games'][0]
        
        print(f"\n🏒 {game['away_team']} @ {game['home_team']}")
        
        away_goalie = game.get('away_goalie', 'TBD')
        home_goalie = game.get('home_goalie', 'TBD')
        
        print(f"Goalies: {away_goalie} vs {home_goalie}\n")
        
        tracker = GoaliePerformanceTracker()
        
        # Analyze both goalies
        for goalie, team, opponent in [
            (away_goalie, game['away_team'], game['home_team']),
            (home_goalie, game['home_team'], game['away_team'])
        ]:
            if goalie != 'TBD':
                analysis = tracker.get_comprehensive_goalie_analysis(goalie, team, opponent)
                
                print(f"📊 {goalie} ({team})")
                print(f"   Recent Form: {analysis['recent_form']['record']} (Last 5)")
                print(f"   Form Score: {analysis['recent_form']['form_score']:+.2f}")
                print(f"   Rest: {analysis['fatigue_analysis']['rest_days']} days ({analysis['fatigue_analysis']['rest_status']})")
                print(f"   Workload: {analysis['fatigue_analysis']['games_last_7']} games in last 7 days")
                print(f"   vs {opponent}: {analysis['matchup_history']['games_played']} career games, {analysis['matchup_history']['avg_gsax']:+.2f} avg GSAX")
                print(f"   Overall Impact: {analysis['overall_impact']:+.2f}")
                print()
