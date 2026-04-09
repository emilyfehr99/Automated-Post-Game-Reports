import json
import os
import sys
from nhl_api_client import NHLAPIClient
from pdf_report_generator import PostGameReportGenerator
from advanced_metrics_analyzer import AdvancedMetricsAnalyzer

def high_fidelity_backfill(num_games=100):
    with open('data/win_probability_predictions_v2.json', 'r') as f:
        data = json.load(f)
    
    preds = data['predictions']
    api = NHLAPIClient()
    generator = PostGameReportGenerator()
    
    updates = 0
    # Last num_games that have been played
    to_process = [p for p in preds if p.get('actual_winner')][-num_games:]
    
    print(f"🔄 High-Fidelity Backfilling {len(to_process)} games...")
    
    for p in to_process:
        game_id = str(p.get('game_id'))
        print(f"  🥅 Processing {game_id} ({p.get('away_team')} @ {p.get('home_team')})...")
        
        try:
            game_data = api.get_comprehensive_game_data(game_id)
            if not game_data or 'boxscore' not in game_data:
                print(f"    ⚠️ No data for {game_id}")
                continue
            
            away_team_id = game_data['boxscore']['awayTeam']['id']
            home_team_id = game_data['boxscore']['homeTeam']['id']
            
            metrics = p.get('metrics_used', {})
            
            # 1. xG and HDC from Play-by-Play
            if 'play_by_play' in game_data:
                away_xg, home_xg = generator._calculate_xg_from_plays(game_data)
                away_hdc, home_hdc = generator._calculate_hdc_from_plays(game_data)
                metrics['away_xg'] = away_xg
                metrics['home_xg'] = home_xg
                metrics['away_hdc'] = away_hdc
                metrics['home_hdc'] = home_hdc
                
                # Period-wise Momentum
                analyzer = AdvancedMetricsAnalyzer(game_data['play_by_play'])
                momentum = analyzer.calculate_momentum_metrics(away_team_id, home_team_id)
                metrics['p1_xg_away'] = momentum['p1_xg']['away']
                metrics['p1_xg_home'] = momentum['p1_xg']['home']
                metrics['p2_xg_away'] = momentum['p2_xg']['away']
                metrics['p2_xg_home'] = momentum['p2_xg']['home']
                metrics['p3_xg_away'] = momentum['p3_xg']['away']
                metrics['p3_xg_home'] = momentum['p3_xg']['home']
                metrics['lead_after_p1'] = momentum['lead_after_p1']
                metrics['lead_after_p2'] = momentum['lead_after_p2']
                
                # GSAX calculation
                away_score = game_data['boxscore']['awayTeam'].get('score', 0)
                home_score = game_data['boxscore']['homeTeam'].get('score', 0)
                metrics['home_gsax'] = round(away_xg - away_score, 2)
                metrics['away_gsax'] = round(home_xg - home_score, 2)
                
                # Tactical
                metrics['home_pressure'] = analyzer.calculate_pressure_metrics(home_team_id).get('sustained_pressure_sequences', 0)
                metrics['away_pressure'] = analyzer.calculate_pressure_metrics(away_team_id).get('sustained_pressure_sequences', 0)
                
            # 2. Zone Metrics
            away_zone = generator._calculate_zone_metrics(game_data, away_team_id, 'away')
            home_zone = generator._calculate_zone_metrics(game_data, home_team_id, 'home')
            
            metrics['away_nzt'] = sum(away_zone.get('nz_turnovers', [0]))
            metrics['home_nzt'] = sum(home_zone.get('nz_turnovers', [0]))
            metrics['away_ozs'] = sum(away_zone.get('oz_originating_shots', [0]))
            metrics['home_ozs'] = sum(home_zone.get('oz_originating_shots', [0]))
            metrics['away_rush'] = sum(away_zone.get('rush_sog', [0]))
            metrics['home_rush'] = sum(home_zone.get('rush_sog', [0]))
            
            # Period Stats for Corsi/PDO
            away_period_stats = generator._calculate_real_period_stats(game_data, away_team_id, 'away')
            home_period_stats = generator._calculate_real_period_stats(game_data, home_team_id, 'home')
            
            if away_period_stats:
                metrics['away_corsi_pct'] = sum(away_period_stats.get('corsi_pct', [50]*3)) / 3.0
                metrics['away_pdo'] = sum(away_period_stats.get('pdo', [100]*3)) / 3.0
            if home_period_stats:
                metrics['home_corsi_pct'] = sum(home_period_stats.get('corsi_pct', [50]*3)) / 3.0
                metrics['home_pdo'] = sum(home_period_stats.get('pdo', [100]*3)) / 3.0

            # Store goalies
            p['home_goalie'] = str(game_data['boxscore']['homeTeam'].get('goalieId', 'Unknown'))
            p['away_goalie'] = str(game_data['boxscore']['awayTeam'].get('goalieId', 'Unknown'))

            p['metrics_used'] = metrics
            p['hq_backfill'] = True
            updates += 1
            
        except Exception as e:
            print(f"    ❌ Error on {game_id}: {e}")
            
    if updates > 0:
        with open('data/win_probability_predictions_v2.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(f"✅ Successfully high-fidelity updated {updates} games")
    else:
        print("No games updated")

if __name__ == '__main__':
    # Increase recursion limit for complex analyzers if needed
    sys.setrecursionlimit(2000)
    high_fidelity_backfill(100)
