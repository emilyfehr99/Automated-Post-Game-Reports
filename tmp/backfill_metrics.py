import json
import traceback
from nhl_api_client import NHLAPIClient
from prediction_interface import PredictionInterface
from pdf_report_generator import PostGameReportGenerator
from advanced_metrics_analyzer import AdvancedMetricsAnalyzer

def backfill():
    with open('data/win_probability_predictions_v2.json', 'r') as f:
        data = json.load(f)
    
    preds = data['predictions']
    api = NHLAPIClient()
    generator = PostGameReportGenerator()
    
    updates = 0
    
    for p in preds:
        metrics = p.get('metrics_used', {})
        if metrics.get('home_xg', 0) == 0 and p.get('actual_winner'):
            game_id = p.get('game_id')
            print(f"Backfilling {game_id} for {p.get('away_team')} @ {p.get('home_team')}")
            
            try:
                game_data = api.get_comprehensive_game_data(str(game_id))
                if not game_data or 'boxscore' not in game_data:
                    continue
                
                away_team_id = game_data['boxscore']['awayTeam']['id']
                home_team_id = game_data['boxscore']['homeTeam']['id']
                
                # Copy from prediction_interface
                if 'play_by_play' in game_data:
                    away_xg, home_xg = generator._calculate_xg_from_plays(game_data)
                    away_hdc, home_hdc = generator._calculate_hdc_from_plays(game_data)
                    metrics['away_xg'] = away_xg
                    metrics['home_xg'] = home_xg
                    metrics['away_hdc'] = away_hdc
                    metrics['home_hdc'] = home_hdc
                
                away_zone_metrics = generator._calculate_zone_metrics(game_data, away_team_id, 'away')
                home_zone_metrics = generator._calculate_zone_metrics(game_data, home_team_id, 'home')
                
                metrics['away_nzt'] = sum(away_zone_metrics.get('nz_turnovers', [0, 0, 0]))
                metrics['away_nztsa'] = sum(away_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0]))
                metrics['away_ozs'] = sum(away_zone_metrics.get('oz_originating_shots', [0, 0, 0]))
                metrics['away_rush'] = sum(away_zone_metrics.get('rush_sog', [0, 0, 0]))
                
                metrics['home_nzt'] = sum(home_zone_metrics.get('nz_turnovers', [0, 0, 0]))
                metrics['home_nztsa'] = sum(home_zone_metrics.get('nz_turnovers_to_shots', [0, 0, 0]))
                metrics['home_ozs'] = sum(home_zone_metrics.get('oz_originating_shots', [0, 0, 0]))
                metrics['home_rush'] = sum(home_zone_metrics.get('rush_sog', [0, 0, 0]))
                
                analyzer = AdvancedMetricsAnalyzer(game_data.get('play_by_play', {}))
                
                away_pressure = analyzer.calculate_pressure_metrics(away_team_id)
                home_pressure = analyzer.calculate_pressure_metrics(home_team_id)
                metrics['away_pressure'] = away_pressure.get('sustained_pressure_sequences', 0)
                metrics['home_pressure'] = home_pressure.get('sustained_pressure_sequences', 0)
                
                away_rebounds = analyzer.calculate_rebounds_by_period(away_team_id)
                home_rebounds = analyzer.calculate_rebounds_by_period(home_team_id)
                metrics['away_rebounds'] = sum(away_rebounds.get('rebounds_by_period', {}).values())
                metrics['home_rebounds'] = sum(home_rebounds.get('rebounds_by_period', {}).values())
                
                momentum = analyzer.calculate_momentum_metrics(away_team_id, home_team_id)
                metrics['p1_xg_away'] = momentum['p1_xg']['away']
                metrics['p1_xg_home'] = momentum['p1_xg']['home']
                metrics['p2_xg_away'] = momentum['p2_xg']['away']
                metrics['p2_xg_home'] = momentum['p2_xg']['home']
                
                away_trans = analyzer.calculate_transition_metrics(away_team_id)
                home_trans = analyzer.calculate_transition_metrics(home_team_id)
                metrics['away_nzt_possession'] = away_trans.get('nzt_possession_pct', 50.0)
                metrics['home_nzt_possession'] = home_trans.get('nzt_possession_pct', 50.0)
                metrics['away_ca_shots'] = away_trans.get('counter_attack_shots', 0)
                metrics['home_ca_shots'] = home_trans.get('counter_attack_shots', 0)
                
                away_movement = analyzer.calculate_pre_shot_movement_metrics(away_team_id)
                home_movement = analyzer.calculate_pre_shot_movement_metrics(home_team_id)
                metrics['away_lateral'] = away_movement['lateral_movement'].get('avg_delta_y', 0.0)
                metrics['home_lateral'] = home_movement['lateral_movement'].get('avg_delta_y', 0.0)
                metrics['away_royal_road'] = away_movement['royal_road_proxy'].get('attempts', 0)
                metrics['home_royal_road'] = home_movement['royal_road_proxy'].get('attempts', 0)
                
                away_period_stats = generator._calculate_real_period_stats(game_data, away_team_id, 'away')
                home_period_stats = generator._calculate_real_period_stats(game_data, home_team_id, 'home')
                
                metrics['away_corsi_pct'] = sum(away_period_stats.get('corsi_pct', [50.0]*3)) / 3.0
                metrics['home_corsi_pct'] = sum(home_period_stats.get('corsi_pct', [50.0]*3)) / 3.0
                
                pp_goals_away = sum(away_period_stats.get('pp_goals', [0]*3))
                pp_attempts_away = sum(away_period_stats.get('pp_attempts', [0]*3))
                metrics['away_power_play_pct'] = (pp_goals_away / pp_attempts_away * 100) if pp_attempts_away > 0 else 0.0
                
                pp_goals_home = sum(home_period_stats.get('pp_goals', [0]*3))
                pp_attempts_home = sum(home_period_stats.get('pp_attempts', [0]*3))
                metrics['home_power_play_pct'] = (pp_goals_home / pp_attempts_home * 100) if pp_attempts_home > 0 else 0.0
                
                p['metrics_used'] = metrics
                updates += 1
            except Exception as e:
                print(f"Error on {game_id}: {e}")
                
    if updates > 0:
        with open('data/win_probability_predictions_v2.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Updated {updates} games")
    else:
        print("No games to update")

if __name__ == '__main__':
    backfill()
