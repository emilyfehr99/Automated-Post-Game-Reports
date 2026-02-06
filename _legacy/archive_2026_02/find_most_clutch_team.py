#!/usr/bin/env python3
"""Script to find the most clutch team based on clutch metrics"""

from team_report_generator import TeamReportGenerator
from nhl_api_client import NHLAPIClient
import json

def analyze_clutch_teams():
    """Analyze all teams and find the most clutch based on various metrics"""
    
    gen = TeamReportGenerator()
    api = NHLAPIClient()
    
    # Get all teams from standings API
    import requests
    url = 'https://api-web.nhle.com/v1/standings/now'
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code != 200:
        print("Could not get standings data")
        return
    
    standings_data = response.json()
    teams_data = []
    team_abbrevs = []
    
    # Extract all team abbreviations from standings
    for team in standings_data.get('standings', []):
        abbrev = team.get('teamAbbrev', {}).get('default', '')
        if abbrev:
            team_abbrevs.append(abbrev)
    
    print(f"Analyzing {len(team_abbrevs)} teams for clutch performance...\n")
    
    # Analyze each team
    for abbrev in team_abbrevs:
        print(f"Processing {abbrev}...", end=" ")
        try:
            # Get team's games
            games = gen.get_team_games(abbrev)
            if not games:
                print("No games found")
                continue
            
            # Aggregate stats
            stats = gen.aggregate_team_stats(abbrev, games)
            
            clutch = stats['clutch']
            wins_above_expected = stats.get('wins_above_expected', 0)
            total_games = len(games)
            
            # Calculate clutch metrics
            one_goal_games = clutch.get('one_goal_games', 0)
            one_goal_wins = clutch.get('one_goal_wins', 0)
            one_goal_win_pct = (one_goal_wins / one_goal_games * 100) if one_goal_games > 0 else 0.0
            
            comeback_wins = clutch.get('comeback_wins', 0)
            comeback_rate = (comeback_wins / total_games * 100) if total_games > 0 else 0.0
            
            third_period_goals = clutch.get('third_period_goals', 0)
            third_period_goals_per_game = third_period_goals / total_games if total_games > 0 else 0.0
            
            # Scoring first record
            scored_first_wins = clutch.get('scored_first_wins', 0)
            scored_first_losses = clutch.get('scored_first_losses', 0)
            scored_first_total = scored_first_wins + scored_first_losses
            scored_first_win_pct = (scored_first_wins / scored_first_total * 100) if scored_first_total > 0 else 0.0
            
            # Opponent scored first (comeback scenarios)
            opp_scored_first_wins = clutch.get('opponent_scored_first_wins', 0)
            opp_scored_first_total = opp_scored_first_wins + clutch.get('opponent_scored_first_losses', 0)
            opp_scored_first_win_pct = (opp_scored_first_wins / opp_scored_first_total * 100) if opp_scored_first_total > 0 else 0.0
            
            # Composite clutch score (weighted combination)
            # Weights: Wins above expected (30%), One-goal win% (25%), Comeback rate (20%), 
            # Opponent scored first win% (15%), Third period goals (10%)
            clutch_score = (
                (wins_above_expected / total_games * 100 * 0.3) if total_games > 0 else 0 +
                (one_goal_win_pct * 0.25) +
                (comeback_rate * 0.20) +
                (opp_scored_first_win_pct * 0.15) +
                (third_period_goals_per_game * 10 * 0.10)  # Scale third period goals
            )
            
            teams_data.append({
                'abbrev': abbrev,
                'total_games': total_games,
                'wins': stats.get('wins', 0),
                'wins_above_expected': wins_above_expected,
                'one_goal_games': one_goal_games,
                'one_goal_wins': one_goal_wins,
                'one_goal_win_pct': one_goal_win_pct,
                'comeback_wins': comeback_wins,
                'comeback_rate': comeback_rate,
                'third_period_goals': third_period_goals,
                'third_period_goals_per_game': third_period_goals_per_game,
                'scored_first_win_pct': scored_first_win_pct,
                'opp_scored_first_win_pct': opp_scored_first_win_pct,
                'clutch_score': clutch_score
            })
            print(f"✓ ({total_games} games)")
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    if not teams_data:
        print("\nNo team data collected. Cannot determine most clutch team.")
        return
    
    # Sort by clutch score
    teams_data.sort(key=lambda x: x['clutch_score'], reverse=True)
    
    # Display results
    print("\n" + "="*100)
    print("MOST CLUTCH TEAMS RANKING")
    print("="*100)
    print(f"{'Rank':<6} {'Team':<6} {'Clutch':<8} {'WinsAX':<8} {'1-Goal%':<9} {'Comeback%':<11} {'3P Goals/G':<12} {'Record':<10}")
    print("-"*100)
    
    for i, team in enumerate(teams_data[:15], 1):  # Top 15
        print(f"{i:<6} {team['abbrev']:<6} {team['clutch_score']:>7.2f}  {team['wins_above_expected']:>7.1f}  "
              f"{team['one_goal_win_pct']:>7.1f}%  {team['comeback_rate']:>9.1f}%  "
              f"{team['third_period_goals_per_game']:>10.2f}  {team['wins']}-{team['total_games']-team['wins']}")
    
    # Most clutch team details
    most_clutch = teams_data[0]
    print("\n" + "="*100)
    print(f"🏆 MOST CLUTCH TEAM: {most_clutch['abbrev']}")
    print("="*100)
    print(f"Clutch Score: {most_clutch['clutch_score']:.2f}")
    print(f"Record: {most_clutch['wins']}-{most_clutch['total_games']-most_clutch['wins']} ({most_clutch['total_games']} games)")
    print(f"Wins Above Expected: {most_clutch['wins_above_expected']:.1f}")
    print(f"One-Goal Games: {most_clutch['one_goal_wins']}/{most_clutch['one_goal_games']} ({most_clutch['one_goal_win_pct']:.1f}%)")
    print(f"Comeback Wins: {most_clutch['comeback_wins']} ({most_clutch['comeback_rate']:.1f}% of games)")
    print(f"Third Period Goals: {most_clutch['third_period_goals']} ({most_clutch['third_period_goals_per_game']:.2f} per game)")
    print(f"When Opponent Scores First: {most_clutch['opp_scored_first_win_pct']:.1f}% win rate")
    
    return teams_data

if __name__ == '__main__':
    analyze_clutch_teams()

