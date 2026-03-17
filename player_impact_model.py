#!/usr/bin/env python3
"""
Player Impact Model
Calculates individual player xG contributions and lineup strength
"""
from typing import Dict, List, Optional
from player_stats_collector import PlayerStatsCollector
import json

class PlayerImpactModel:
    def __init__(self):
        self.stats_collector = PlayerStatsCollector()
        self.league_avg_xg_per_60 = 0.8  # League average xG per 60 minutes
        self.league_avg_toi = 16.0  # League average TOI per game
    
    def calculate_player_xg_rate(self, player_name: str, team_abbr: str) -> float:
        """Calculate a player's expected goals contribution per game"""
        # Get player stats
        roster = self.stats_collector.get_team_roster_stats(team_abbr)
        
        player_stats = None
        for p in roster:
            if player_name.lower() in p.get('name', '').lower():
                player_stats = p
                break
        
        if not player_stats:
            # Return league average if player not found
            return self.league_avg_xg_per_60 * (self.league_avg_toi / 60)
        
        # Calculate xG rate based on:
        # 1. Goals per 60 (actual production)
        # 2. Shooting percentage (talent vs luck)
        # 3. Ice time (opportunity)
        
        goals_per_60 = player_stats.get('goals_per_60', 0)
        shooting_pct = player_stats.get('shooting_pct', 10.0)
        toi = player_stats.get('toi_per_game', self.league_avg_toi)
        
        # Adjust for shooting percentage regression (league avg ~10%)
        # If player is shooting 15%, they're likely getting lucky
        # If player is shooting 5%, they're likely unlucky
        talent_adjustment = 1.0
        if shooting_pct > 12:
            talent_adjustment = 0.9  # Expect regression
        elif shooting_pct < 8:
            talent_adjustment = 1.1  # Expect positive regression
        
        # Calculate expected goals per game
        xg_per_game = (goals_per_60 * talent_adjustment) * (toi / 60)
        
        return xg_per_game
    
    def calculate_lineup_strength(self, lineup: Dict, team_abbr: str) -> Dict:
        """Calculate expected offensive and defensive strength from lineup"""
        
        offensive_strength = 0.0
        defensive_strength = 0.0
        
        # Calculate offensive contribution from forwards
        forwards = lineup.get('forwards', [])
        for forward in forwards[:12]:  # Top 12 forwards
            player_name = forward.get('name', '')
            xg_contribution = self.calculate_player_xg_rate(player_name, team_abbr)
            offensive_strength += xg_contribution
        
        # Power play boost (PP1 gets ~2 min/game, PP2 gets ~0.5 min/game)
        pp1 = lineup.get('power_play_1', [])
        pp2 = lineup.get('power_play_2', [])
        
        pp1_strength = 0.0
        for player in pp1:
            player_name = player.get('name', '')
            xg_rate = self.calculate_player_xg_rate(player_name, team_abbr)
            # PP units are ~2x more effective than even strength
            pp1_strength += xg_rate * 2.0 * (2.0 / 60)  # 2 min of PP time
        
        pp2_strength = 0.0
        for player in pp2:
            player_name = player.get('name', '')
            xg_rate = self.calculate_player_xg_rate(player_name, team_abbr)
            pp2_strength += xg_rate * 2.0 * (0.5 / 60)  # 0.5 min of PP time
        
        offensive_strength += pp1_strength + pp2_strength
        
        # Defensive strength (simplified - based on team average)
        # In a full implementation, this would use individual defensive metrics
        defensive_strength = 2.5  # League average goals against
        
        return {
            'projected_xgf': offensive_strength,
            'projected_xga': defensive_strength,
            'pp1_strength': pp1_strength,
            'pp2_strength': pp2_strength,
            'forward_depth': len(forwards)
        }
    
    def predict_game_score(self, away_lineup: Dict, home_lineup: Dict, 
                          away_team: str, home_team: str,
                          away_goalie: str = None, home_goalie: str = None) -> Dict:
        """Predict game score based on lineups"""
        
        # Calculate lineup strengths
        away_strength = self.calculate_lineup_strength(away_lineup, away_team)
        home_strength = self.calculate_lineup_strength(home_lineup, home_team)
        
        # Apply home ice advantage (5%)
        home_strength['projected_xgf'] *= 1.05
        
        # Adjust for goalie quality (simplified)
        # In full implementation, would use goalie-specific stats
        goalie_adjustment = 0.9  # Good goalie reduces xGA by 10%
        
        away_xgf = away_strength['projected_xgf']
        away_xga = home_strength['projected_xgf'] * goalie_adjustment
        
        home_xgf = home_strength['projected_xgf']
        home_xga = away_strength['projected_xgf'] * goalie_adjustment
        
        # Calculate win probability
        # Simple logistic model: P(away win) = 1 / (1 + e^(-(xgf_diff)))
        import math
        xg_diff = away_xgf - home_xgf
        away_win_prob = 1 / (1 + math.exp(-xg_diff))
        
        return {
            'away_xgf': away_xgf,
            'home_xgf': home_xgf,
            'away_xga': away_xga,
            'home_xga': home_xga,
            'away_win_prob': away_win_prob,
            'home_win_prob': 1 - away_win_prob,
            'away_lineup_strength': away_strength,
            'home_lineup_strength': home_strength
        }

if __name__ == "__main__":
    from rotowire_scraper import RotoWireScraper
    
    print("🎯 Player Impact Model - Live Game Prediction")
    print("=" * 60)
    
    # Get today's games from RotoWire
    scraper = RotoWireScraper()
    data = scraper.scrape_daily_data()
    
    if data['games']:
        game = data['games'][0]  # First game
        
        print(f"\n🏒 {game['away_team']} @ {game['home_team']}")
        print(f"Goalies: {game.get('away_goalie', 'TBD')} vs {game.get('home_goalie', 'TBD')}")
        
        if 'away_lineup' in game and 'home_lineup' in game:
            model = PlayerImpactModel()
            
            prediction = model.predict_game_score(
                game['away_lineup'],
                game['home_lineup'],
                game['away_team'],
                game['home_team'],
                game.get('away_goalie'),
                game.get('home_goalie')
            )
            
            print(f"\n📊 Player-Level Prediction:")
            print(f"  {game['away_team']} xGF: {prediction['away_xgf']:.2f}")
            print(f"  {game['home_team']} xGF: {prediction['home_xgf']:.2f}")
            print(f"\n  Win Probability:")
            print(f"    {game['away_team']}: {prediction['away_win_prob']:.1%}")
            print(f"    {game['home_team']}: {prediction['home_win_prob']:.1%}")
            
            # Compare with betting odds
            if 'odds' in game and game['odds']:
                print(f"\n  Market Odds: {game['odds'].get('favorite_team', 'N/A')} {game['odds'].get('moneyline', 'N/A')}")
        else:
            print("\n⚠️  Lineups not available yet")
    else:
        print("\n⚠️  No games found")
