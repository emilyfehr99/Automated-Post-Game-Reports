#!/usr/bin/env python3
"""Quick check for most clutch team"""

from team_report_generator import TeamReportGenerator
import requests

def find_top_clutch_team():
    gen = TeamReportGenerator()
    
    # Get all teams from standings API
    url = 'https://api-web.nhle.com/v1/standings/now'
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code != 200:
        print("Could not get standings data")
        return
    
    standings_data = response.json()
    team_abbrevs = []
    
    # Extract all team abbreviations from standings
    for team in standings_data.get('standings', []):
        abbrev = team.get('teamAbbrev', {}).get('default', '')
        if abbrev:
            team_abbrevs.append(abbrev)
    
    print(f"Analyzing {len(team_abbrevs)} teams for clutch performance...\n")
    
    teams_data = []
    
    # Analyze each team
    for abbrev in team_abbrevs:
        try:
            # Get team's games
            games = gen.get_team_games(abbrev)
            if not games:
                continue
            
            # Aggregate stats
            aggregated_stats = gen.aggregate_team_stats(abbrev, games)
            total_games = aggregated_stats['games_played']
            if total_games == 0:
                continue
            
            # Calculate clutch metrics
            wins_above_expected = aggregated_stats['wins_above_expected']
            one_goal_games = aggregated_stats['clutch']['one_goal_games']
            one_goal_wins = aggregated_stats['clutch']['one_goal_wins']
            one_goal_win_pct = (one_goal_wins / one_goal_games * 100) if one_goal_games > 0 else 0.0
            comeback_wins = aggregated_stats['clutch']['comeback_wins']
            comeback_rate = (comeback_wins / aggregated_stats['wins'] * 100) if aggregated_stats['wins'] > 0 else 0.0
            third_period_goals_per_game = aggregated_stats['clutch']['third_period_goals'] / total_games
            
            # Simple clutch score (can be refined)
            clutch_score = (wins_above_expected * 2) + (one_goal_win_pct * 0.1) + (comeback_rate * 0.15) + (third_period_goals_per_game * 5)
            
            teams_data.append({
                'abbrev': abbrev,
                'clutch_score': clutch_score,
                'wins_above_expected': wins_above_expected,
                'one_goal_win_pct': one_goal_win_pct,
                'comeback_rate': comeback_rate,
                'third_period_goals_per_game': third_period_goals_per_game
            })
            print(f"{abbrev}: {clutch_score:.2f}", end="  ")
        except Exception as e:
            continue
    
    if not teams_data:
        print("\nNo team data collected.")
        return
    
    # Sort by clutch score
    teams_data.sort(key=lambda x: x['clutch_score'], reverse=True)
    
    print("\n" + "="*80)
    print("TOP 5 MOST CLUTCH TEAMS:")
    print("="*80)
    
    for i, team in enumerate(teams_data[:5], 1):
        print(f"{i}. {team['abbrev']}: Clutch Score = {team['clutch_score']:.2f}")
        print(f"   Wins Above Expected: {team['wins_above_expected']:.1f}")
        print(f"   1-Goal Win %: {team['one_goal_win_pct']:.1f}%")
        print(f"   Comeback Rate: {team['comeback_rate']:.1f}%")
        print(f"   3P Goals/Game: {team['third_period_goals_per_game']:.2f}")
        print()

if __name__ == "__main__":
    find_top_clutch_team()

