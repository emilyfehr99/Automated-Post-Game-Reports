#!/usr/bin/env python3
import json
import random
import numpy as np
from pathlib import Path
from score_prediction_model import ScorePredictionModel

class PlayoffSeriesPredictor:
    """Best-of-7 series simulation based on 'DNA of Playoff Success' Audit weights."""
    
    def __init__(self):
        self.model = ScorePredictionModel()
        self.metrics_path = Path('data/team_advanced_metrics.json')
        self.edge_path = Path('data/team_edge_profiles.json')
        self.advanced_metrics = {}
        self.edge_profiles = {}
        self.starters = {}
        self._load_metrics()
        self._load_starters()
        self._load_edge_data()
        
        # FINAL 5-YEAR CHAMPIONSHIP WEIGHTS (Tactical Audit v2.1 2020-2025)
        # These weights prioritize offensive zone persistence and transition efficiency.
        self.PLAYOFF_WEIGHTS = {
            'rebound_gen_rate': 0.33,       
            'avg_en_to_s': 0.22,           
            'quick_strike_rate': 0.21,      
            'hd_pizzas_per_game': -0.14,    
            'rapid_reb_rate': 0.08,         
            'avg_ex_to_en': -0.07,          
            'pizzas_per_game': -0.10,     
            # Edge Tracking Weights (Phase 18 Integration)
            'edge_top_speed': 0.15,         
            'edge_burst_frequency': 0.12,   
            # Possession Starters (Phase 19 Integration)
            'ozone_faceoff_pct': 0.05,      # Clean wins drive immediate persistence
        }

    def _load_metrics(self):
        if self.metrics_path.exists():
            with open(self.metrics_path) as f:
                data = json.load(f)
                self.advanced_metrics = data.get('teams', {})
    
    def _load_starters(self):
        """Identify the #1 goalie for each team based on games played in high-fidelity metrics."""
        if not self.metrics_path.exists():
            return
            
        with open(self.metrics_path) as f:
            data = json.load(f)
        
        goalie_data = data.get('goalies', {})
        team_starters = {} # team -> (name, games)
        
        for gid, gs in goalie_data.items():
            team = gs.get('team')
            name = gs.get('name')
            games = gs.get('games', 0)
            
            if not team or not name: continue
            
            if team not in team_starters or games > team_starters[team][1]:
                team_starters[team] = (name, games)
                
        self.starters = {t: n for t, (n, g) in team_starters.items()}
        print(f"🥅 Identified #1 starters for {len(self.starters)} teams for playoff simulation")

    def _load_edge_data(self):
        if self.edge_path.exists():
            with open(self.edge_path) as f:
                self.edge_profiles = json.load(f)
            print(f"⛸️  Loaded high-fidelity Edge tracking profiles for {len(self.edge_profiles)} teams")

    def get_team_playoff_modifier(self, team_abbr):
        """Calculate the 'Playoff Integrity' modifier for a team."""
        stats = self.advanced_metrics.get(team_abbr, {})
        edge = self.edge_profiles.get(team_abbr, {})
        
        if not stats: return 1.0
            
        modifier = 0
        # Tactical PBP Metrics
        for metric, weight in self.PLAYOFF_WEIGHTS.items():
            if metric.startswith('edge'): continue # Handle edge separately
            val = stats.get(metric, 0)
            modifier += (val * weight)
            
        # Edge Tracking Metrics
        # Baseline Speed: 21.5 mph, Burst: 0.5/mile
        speed_delta = (edge.get('avg_top_speed', 21.5) - 21.5) * self.PLAYOFF_WEIGHTS['edge_top_speed']
        burst_delta = (edge.get('avg_burst_frequency', 0.5) - 0.5) * self.PLAYOFF_WEIGHTS['edge_burst_frequency']
        
        modifier += speed_delta + burst_delta
            
        # Normalization
        return modifier * 0.1

    def calculate_game_win_prob(self, away_team, home_team):
        """Calculate the single-game win probability with playoff tuning."""
        # Identify starters
        away_goalie = self.starters.get(away_team)
        home_goalie = self.starters.get(home_team)
        
        # Get base probability from Poisson Model (including high-fidelity GSAX)
        res = self.model.predict_score(
            away_team, home_team, 
            away_goalie=away_goalie, 
            home_goalie=home_goalie
        )
        away_prob = res['away_win_prob']
        
        # Apply Playoff Modifiers
        away_mod = self.get_team_playoff_modifier(away_team)
        home_mod = self.get_team_playoff_modifier(home_team)
        
        # Balance out the shift (if Away has better DNA, they get a boost, and vice-versa)
        net_shift = away_mod - home_mod
        
        final_away_prob = np.clip(away_prob + net_shift, 0.01, 0.99)
        return final_away_prob

    def simulate_series(self, away, home, away_wins=0, home_wins=0, simulations=10000):
        """
        Simulate a Best-of-7 Series (2-2-1-1-1 Home-Ice Format).
        Supports mid-series simulations if away_wins/home_wins are provided.
        """
        away_series_wins = 0
        total_games_completed = 0
        
        # Pre-calculate win probs for both venues
        p_away_at_home = self.calculate_game_win_prob(away, home)
        p_home_at_away = self.calculate_game_win_prob(home, away)
        p_away_at_away = 1 - p_home_at_away
        
        # Format: H-H-A-A-H-A-H
        full_venues = ['home', 'home', 'away', 'away', 'home', 'away', 'home']
        
        # Calculate how many games were already played
        games_played = away_wins + home_wins
        remaining_venues = full_venues[games_played:]
        
        if games_played >= 7 or away_wins >= 4 or home_wins >= 4:
            return {
                'away': away, 'home': home,
                'away_series_win_prob': 1.0 if away_wins >= 4 else 0.0,
                'home_series_win_prob': 1.0 if home_wins >= 4 else 0.0,
                'status': 'FINISHED',
                'winner': away if away_wins >= 4 else home
            }

        for _ in range(simulations):
            a_w = away_wins
            h_w = home_wins
            sim_games = 0
            
            for venue in remaining_venues:
                sim_games += 1
                prob = p_away_at_home if venue == 'home' else p_away_at_away
                
                if random.random() < prob:
                    a_w += 1
                else:
                    h_w += 1
                    
                if a_w == 4 or h_w == 4:
                    break
            
            if a_w == 4:
                away_series_wins += 1
            total_games_completed += sim_games
            
        away_series_prob = away_series_wins / simulations
        
        return {
            'away': away,
            'home': home,
            'away_series_win_prob': away_series_prob,
            'home_series_win_prob': 1 - away_series_prob,
            'avg_remaining_games': round(total_games_completed / simulations, 1),
            'current_state': f"{away} {away_wins} - {home_wins} {home}",
            'winner_projection': away if away_series_prob > 0.5 else home
        }

    def predict_cup_winner(self):
        """Analyze all current teams and rank them by 'Championship DNA' alignment."""
        if not self.advanced_metrics:
            return None
            
        contender_scores = []
        for team_abbr in self.advanced_metrics:
            dna_score = self.get_team_playoff_modifier(team_abbr)
            # Use points percentage from standings to identify 'Playoff-Bound' teams
            # Actually, just rank everyone for now.
            contender_scores.append({
                'team': team_abbr,
                'dna_alignment': dna_score,
                'signature': self.advanced_metrics[team_abbr]
            })
            
        # Rank by DNA Alignment (Playoff Modifier)
        # Higher score = Better alignment with the 5-year Champion Profile
        contender_scores.sort(key=lambda x: x['dna_alignment'], reverse=True)
        return contender_scores

if __name__ == "__main__":
    predictor = PlayoffSeriesPredictor()
    
    print("\n🏆 THE 2026 STANLEY CUP CHAMPIONSHIP DNA AUDIT")
    print("="*60)
    print("Ranking teams by alignment with the 5-Year 'Cup Winner' DNA Profile")
    print("(Rebounds: 0.33, HD Giveaways: -0.14, Rush Caps: -0.09)")
    print("-" * 60)
    
    rankings = predictor.predict_cup_winner()
    if rankings:
        for i, r in enumerate(rankings[:10], 1):
            star = "⭐ " if i == 1 else "   "
            print(f"{star}{i:<2}. {r['team']:<5} | DNA Alignment: {r['dna_alignment']:>8.4f}")
    
    print("\n📈 TEST: Florida vs Edmonton (2024 Finals Benchmark)")
    result = predictor.simulate_series('EDM', 'FLA')
    print(f"Result: {result['winner_projection']} wins series (Win Prob: {max(result['away_series_win_prob'], result['home_series_win_prob']):.1%})")
