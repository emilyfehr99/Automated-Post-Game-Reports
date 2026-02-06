#!/usr/bin/env python3
"""
Quick update script to only regenerate lat, long_movement, and gs metrics
for existing games without recalculating everything else
"""

import json
import os
from pathlib import Path
from nhl_api_client import NHLAPIClient
from advanced_metrics_analyzer import AdvancedMetricsAnalyzer

def update_movement_and_gs():
    """Update only lat, long_movement, and gs for all existing games"""
    
    data_file = Path('data/season_2025_2026_team_stats.json')
    
    # Load existing data
    print(f"Loading existing data from {data_file}...")
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    teams_data = data.get('teams', {})
    api = NHLAPIClient()
    
    total_teams = len(teams_data)
    
    for idx, (team_abbrev, team_info) in enumerate(teams_data.items(), 1):
        print(f"\n[{idx}/{total_teams}] Processing {team_abbrev}...")
        
        # Process home games
        home_games = team_info.get('home', {}).get('games', [])
        print(f"  Updating {len(home_games)} home games...")
        
        for i, game_id in enumerate(home_games):
            if (i + 1) % 5 == 0:
                print(f"    Home game {i+1}/{len(home_games)}...")
            
            try:
                game_data = api.get_comprehensive_game_data(str(game_id))
                if not game_data or 'boxscore' not in game_data:
                    continue
                
                # Get team IDs
                away_team_id = game_data['boxscore']['awayTeam']['id']
                home_team_id = game_data['boxscore']['homeTeam']['id']
                
                # Run advanced metrics analyzer
                analyzer = AdvancedMetricsAnalyzer(game_data.get('play_by_play', {}))
                metrics_report = analyzer.generate_comprehensive_report(away_team_id, home_team_id)
                
                # Get home team pre-shot movement
                pre_shot_data = metrics_report.get('home_team', {}).get('pre_shot_movement', {})
                lat = pre_shot_data.get('lateral_movement', {}).get('avg_delta_y', 0.0)
                long_movement = pre_shot_data.get('longitudinal_movement', {}).get('avg_delta_x', 0.0)
                
                # Get GS from game score calculation
                from team_report_generator import TeamReportGenerator
                gen = TeamReportGenerator()
                period_gs_xg = gen._calculate_period_metrics(game_data, home_team_id, 'home')
                
                if period_gs_xg:
                    gs_periods, _ = period_gs_xg
                    total_gs = sum(gs_periods)
                else:
                    total_gs = 0.0
                
                # Update the values
                teams_data[team_abbrev]['home']['lat'][i] = round(lat, 2)
                teams_data[team_abbrev]['home']['long_movement'][i] = round(long_movement, 2)
                teams_data[team_abbrev]['home']['gs'][i] = round(total_gs, 2)
                
            except Exception as e:
                print(f"      Error processing home game {game_id}: {e}")
                continue
        
        # Process away games
        away_games = team_info.get('away', {}).get('games', [])
        print(f"  Updating {len(away_games)} away games...")
        
        for i, game_id in enumerate(away_games):
            if (i + 1) % 5 == 0:
                print(f"    Away game {i+1}/{len(away_games)}...")
            
            try:
                game_data = api.get_comprehensive_game_data(str(game_id))
                if not game_data or 'boxscore' not in game_data:
                    continue
                
                # Get team IDs
                away_team_id = game_data['boxscore']['awayTeam']['id']
                home_team_id = game_data['boxscore']['homeTeam']['id']
                
                # Run advanced metrics analyzer
                analyzer = AdvancedMetricsAnalyzer(game_data.get('play_by_play', {}))
                metrics_report = analyzer.generate_comprehensive_report(away_team_id, home_team_id)
                
                # Get away team pre-shot movement
                pre_shot_data = metrics_report.get('away_team', {}).get('pre_shot_movement', {})
                lat = pre_shot_data.get('lateral_movement', {}).get('avg_delta_y', 0.0)
                long_movement = pre_shot_data.get('longitudinal_movement', {}).get('avg_delta_x', 0.0)
                
                # Get GS from game score calculation
                from team_report_generator import TeamReportGenerator
                gen = TeamReportGenerator()
                period_gs_xg = gen._calculate_period_metrics(game_data, away_team_id, 'away')
                
                if period_gs_xg:
                    gs_periods, _ = period_gs_xg
                    total_gs = sum(gs_periods)
                else:
                    total_gs = 0.0
                
                # Update the values
                teams_data[team_abbrev]['away']['lat'][i] = round(lat, 2)
                teams_data[team_abbrev]['away']['long_movement'][i] = round(long_movement, 2)
                teams_data[team_abbrev]['away']['gs'][i] = round(total_gs, 2)
                
            except Exception as e:
                print(f"      Error processing away game {game_id}: {e}")
                continue
        
        # Save progress after each team
        output = {"teams": teams_data}
        with open(data_file, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"  ✓ Saved progress for {team_abbrev}")
    
    print(f"\n{'='*60}")
    print(f"✓ Update complete! {data_file}")
    print(f"{'='*60}")

if __name__ == "__main__":
    update_movement_and_gs()
