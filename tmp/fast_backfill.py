import json

def fast_backfill():
    # Load team stats
    with open('data/season_2025_2026_team_stats.json', 'r') as f:
        team_stats = json.load(f)['teams']
        
    # Load predictions
    with open('data/win_probability_predictions_v2.json', 'r') as f:
        data = json.load(f)
        
    preds = data['predictions']
    updates = 0
    
    for p in preds:
        if p.get('actual_winner'):
            home = p.get('home_team')
            away = p.get('away_team')
            game_id = str(p.get('game_id'))
            
            # Find game index in home_stats
            home_data = team_stats.get(home, {}).get('home', {})
            away_data = team_stats.get(away, {}).get('away', {})
            
            home_games = [str(g) for g in home_data.get('games', [])]
            away_games = [str(g) for g in away_data.get('games', [])]
            
            if game_id in home_games and game_id in away_games:
                h_idx = home_games.index(game_id)
                a_idx = away_games.index(game_id)
                
                metrics = p.get('metrics_used', {})
                # Fill home metrics
                m_home_xg = float(home_data.get('xg', [])[h_idx])
                m_home_opp_xg = float(home_data.get('opp_xg', [])[h_idx])
                m_home_ga = float(home_data.get('opp_goals', [])[h_idx])
                
                metrics['home_xg'] = m_home_xg
                metrics['home_gsax'] = round(m_home_opp_xg - m_home_ga, 2)
                metrics['home_corsi_pct'] = float(home_data.get('corsi_pct', [])[h_idx])
                metrics['home_pdo'] = float(home_data.get('pdo', [])[h_idx])
                metrics['home_power_play_pct'] = float(home_data.get('power_play_pct', [])[h_idx])
                metrics['home_penalty_kill_pct'] = float(home_data.get('penalty_kill_pct', [])[h_idx])
                metrics['home_nzt'] = float(home_data.get('nzt', [])[h_idx])
                metrics['home_ozs'] = float(home_data.get('ozs', [])[h_idx])
                metrics['home_rush'] = float(home_data.get('rush', [])[h_idx])
                metrics['home_hdc'] = float(home_data.get('hdc', [])[h_idx])
                metrics['home_nztsa'] = float(home_data.get('nztsa', [])[h_idx])
                metrics['home_rebounds'] = float(home_data.get('rebounds', [])[h_idx] if len(home_data.get('rebounds', [])) > h_idx else 0)
                
                # Fill away metrics
                m_away_xg = float(away_data.get('xg', [])[a_idx])
                m_away_opp_xg = float(away_data.get('opp_xg', [])[a_idx])
                m_away_ga = float(away_data.get('opp_goals', [])[a_idx])
                
                metrics['away_xg'] = m_away_xg
                metrics['away_gsax'] = round(m_away_opp_xg - m_away_ga, 2)
                metrics['away_corsi_pct'] = float(away_data.get('corsi_pct', [])[a_idx])
                metrics['away_pdo'] = float(away_data.get('pdo', [])[a_idx])
                metrics['away_power_play_pct'] = float(away_data.get('power_play_pct', [])[a_idx])
                metrics['away_penalty_kill_pct'] = float(away_data.get('penalty_kill_pct', [])[a_idx])
                metrics['away_nzt'] = float(away_data.get('nzt', [])[a_idx])
                metrics['away_ozs'] = float(away_data.get('ozs', [])[a_idx])
                metrics['away_rush'] = float(away_data.get('rush', [])[a_idx])
                metrics['away_hdc'] = float(away_data.get('hdc', [])[a_idx])
                metrics['away_nztsa'] = float(away_data.get('nztsa', [])[a_idx])
                metrics['away_rebounds'] = float(away_data.get('rebounds', [])[a_idx] if len(away_data.get('rebounds', [])) > a_idx else 0)
                
                p['metrics_used'] = metrics
                updates += 1

    if updates > 0:
        with open('data/win_probability_predictions_v2.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Fast updated {updates} games")
    else:
        print("No games to update")

if __name__ == '__main__':
    fast_backfill()
