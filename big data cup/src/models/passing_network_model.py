"""Dynamic Passing Network Centrality - Graph Analysis."""
import numpy as np
import pandas as pd
import networkx as nx
from collections import defaultdict
from typing import Dict, List, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.data_loader import DataLoader

class PassingNetworkAnalyzer:
    """Analyze passing networks using graph centrality metrics."""
    
    def __init__(self, data_dir: str):
        """Initialize analyzer."""
        self.data_loader = DataLoader(data_dir)
        self.results = {}
        
    def build_passing_network(self, events_df: pd.DataFrame, 
                             time_window: float = 300.0) -> nx.DiGraph:
        """Build weighted directed graph of passes."""
        G = nx.DiGraph()
        
        # Filter for Play events (passes)
        plays = events_df[events_df['Event'] == 'Play'].copy()
        
        # Extract passes (events with Player_Id_2)
        passes = plays[
            plays['Player_Id_2'].notna() & 
            (plays['Player_Id_2'] != '')
        ].copy()
        
        for _, pass_event in passes.iterrows():
            # Handle both numeric and string player IDs (e.g., 'Go' for goalies)
            try:
                from_player = str(int(float(pass_event['Player_Id']))) if pd.notna(pass_event['Player_Id']) else None
            except:
                from_player = str(pass_event['Player_Id']) if pd.notna(pass_event['Player_Id']) else None
            
            try:
                to_player = str(int(float(pass_event['Player_Id_2']))) if pd.notna(pass_event['Player_Id_2']) else None
            except:
                to_player = str(pass_event['Player_Id_2']) if pd.notna(pass_event['Player_Id_2']) else None
            
            if not from_player or not to_player:
                continue
            
            # Add edge (or increment weight if exists)
            if G.has_edge(from_player, to_player):
                G[from_player][to_player]['weight'] += 1
            else:
                G.add_edge(from_player, to_player, weight=1)
            
            # Store player metadata
            if from_player not in G.nodes():
                G.nodes[from_player]['team'] = str(pass_event.get('Team', 'Unknown'))
            if to_player not in G.nodes():
                G.nodes[to_player]['team'] = str(pass_event.get('Team', 'Unknown'))
        
        return G
    
    def calculate_centrality_metrics(self, G: nx.DiGraph) -> pd.DataFrame:
        """Calculate various centrality metrics for each player."""
        if len(G.nodes()) == 0:
            return pd.DataFrame()
        
        metrics = []
        
        # Betweenness Centrality
        betweenness = nx.betweenness_centrality(G, weight='weight')
        
        # PageRank
        try:
            pagerank = nx.pagerank(G, weight='weight')
        except:
            pagerank = {node: 0 for node in G.nodes()}
        
        # Eigenvector Centrality
        try:
            eigenvector = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
        except:
            eigenvector = {node: 0 for node in G.nodes()}
        
        # Degree centrality
        in_degree_centrality = nx.in_degree_centrality(G)
        out_degree_centrality = nx.out_degree_centrality(G)
        
        # Closeness centrality
        try:
            closeness = nx.closeness_centrality(G, distance='weight')
        except:
            closeness = {node: 0 for node in G.nodes()}
        
        # Calculate actual stats
        in_degrees = dict(G.in_degree(weight='weight'))
        out_degrees = dict(G.out_degree(weight='weight'))
        
        for node in G.nodes():
            metrics.append({
                'player_id': node,
                'team': G.nodes[node].get('team', 'Unknown'),
                'betweenness_centrality': betweenness.get(node, 0),
                'pagerank': pagerank.get(node, 0),
                'eigenvector_centrality': eigenvector.get(node, 0),
                'in_degree_centrality': in_degree_centrality.get(node, 0),
                'out_degree_centrality': out_degree_centrality.get(node, 0),
                'closeness_centrality': closeness.get(node, 0),
                'in_degree': in_degrees.get(node, 0),
                'out_degree': out_degrees.get(node, 0),
                'total_passes_received': in_degrees.get(node, 0),
                'total_passes_made': out_degrees.get(node, 0)
            })
        
        return pd.DataFrame(metrics)
    
    def identify_hidden_playmakers(self, centrality_df: pd.DataFrame, 
                                   events_df: pd.DataFrame) -> pd.DataFrame:
        """Identify players with high centrality but low traditional stats."""
        # Get traditional stats
        assists = events_df[
            (events_df['Event'] == 'Goal') & 
            (events_df['Player_Id_2'].notna())
        ].groupby('Player_Id_2').size().to_dict()
        
        goals = events_df[
            (events_df['Event'] == 'Goal') & 
            (events_df['Player_Id'].notna())
        ].groupby('Player_Id').size().to_dict()
        
        # Merge with centrality - handle string and numeric IDs
        centrality_df = centrality_df.copy()
        
        def safe_get_stat(player_id, stat_dict):
            """Safely get stat, trying both string and numeric keys."""
            if pd.isna(player_id):
                return 0
            player_str = str(player_id)
            # Try exact match first
            if player_str in stat_dict:
                return stat_dict[player_str]
            # Try converting keys to strings
            str_dict = {str(k): v for k, v in stat_dict.items()}
            return str_dict.get(player_str, 0)
        
        centrality_df['assists'] = centrality_df['player_id'].apply(
            lambda x: safe_get_stat(x, assists)
        )
        centrality_df['goals'] = centrality_df['player_id'].apply(
            lambda x: safe_get_stat(x, goals)
        )
        
        centrality_df['total_points'] = centrality_df['assists'] + centrality_df['goals']
        
        # Calculate "hidden value" score (high centrality, low points)
        centrality_df['centrality_score'] = (
            centrality_df['betweenness_centrality'] * 0.4 +
            centrality_df['pagerank'] * 0.3 +
            centrality_df['eigenvector_centrality'] * 0.3
        )
        
        # Hidden playmaker: high centrality but low traditional stats
        centrality_df['hidden_value'] = centrality_df['centrality_score'] / (centrality_df['total_points'] + 1)
        
        return centrality_df.sort_values('hidden_value', ascending=False)
    
    def analyze_network_evolution(self, events_df: pd.DataFrame, 
                                 num_windows: int = 4) -> pd.DataFrame:
        """Analyze how network centrality evolves over time."""
        if events_df.empty:
            return pd.DataFrame()
        
        max_time = events_df['Clock_Seconds'].max()
        min_time = events_df['Clock_Seconds'].min()
        window_size = (max_time - min_time) / num_windows
        
        evolution = []
        
        for i in range(num_windows):
            window_start = min_time + i * window_size
            window_end = window_start + window_size
            
            window_events = events_df[
                (events_df['Clock_Seconds'] >= window_start) &
                (events_df['Clock_Seconds'] < window_end)
            ]
            
            if window_events.empty:
                continue
            
            G = self.build_passing_network(window_events)
            centrality = self.calculate_centrality_metrics(G)
            
            if not centrality.empty:
                centrality['window'] = i
                centrality['time_start'] = window_start
                centrality['time_end'] = window_end
                evolution.append(centrality)
        
        if evolution:
            return pd.concat(evolution, ignore_index=True)
        return pd.DataFrame()
    
    def run_full_analysis(self) -> Dict:
        """Run complete passing network analysis."""
        games = self.data_loader.get_all_games()
        
        all_centrality = []
        all_hidden_playmakers = []
        all_evolution = []
        
        for game in games:
            print(f"Analyzing passing networks for {game['game_id']}...")
            
            events_df = self.data_loader.load_events(
                game['events'],
                full_path=game.get('events_full_path')
            )
            if events_df.empty:
                continue
            
            # Build network
            G = self.build_passing_network(events_df)
            
            if len(G.nodes()) == 0:
                continue
            
            # Calculate centrality
            centrality = self.calculate_centrality_metrics(G)
            centrality['game_id'] = game['game_id']
            all_centrality.append(centrality)
            
            # Identify hidden playmakers
            hidden = self.identify_hidden_playmakers(centrality, events_df)
            hidden['game_id'] = game['game_id']
            all_hidden_playmakers.append(hidden)
            
            # Network evolution
            evolution = self.analyze_network_evolution(events_df, num_windows=4)
            if not evolution.empty:
                evolution['game_id'] = game['game_id']
                all_evolution.append(evolution)
        
        if not all_centrality:
            return {'insights': {}}
        
        # Combine results
        combined_centrality = pd.concat(all_centrality, ignore_index=True)
        combined_hidden = pd.concat(all_hidden_playmakers, ignore_index=True) if all_hidden_playmakers else pd.DataFrame()
        combined_evolution = pd.concat(all_evolution, ignore_index=True) if all_evolution else pd.DataFrame()
        
        # Aggregate by player
        player_aggregate = combined_centrality.groupby('player_id').agg({
            'betweenness_centrality': 'mean',
            'pagerank': 'mean',
            'eigenvector_centrality': 'mean',
            'total_passes_received': 'sum',
            'total_passes_made': 'sum',
            'team': 'first'
        }).reset_index()
        
        # Top hidden playmakers across all games
        if not combined_hidden.empty:
            top_hidden = combined_hidden.nlargest(10, 'hidden_value')[
                ['player_id', 'team', 'centrality_score', 'total_points', 'hidden_value']
            ]
        else:
            top_hidden = pd.DataFrame()
        
        # Generate insights
        insights = {
            'avg_betweenness': combined_centrality['betweenness_centrality'].mean(),
            'avg_pagerank': combined_centrality['pagerank'].mean(),
            'max_betweenness_player': player_aggregate.loc[player_aggregate['betweenness_centrality'].idxmax(), 'player_id'] if not player_aggregate.empty else '',
            'max_pagerank_player': player_aggregate.loc[player_aggregate['pagerank'].idxmax(), 'player_id'] if not player_aggregate.empty else '',
            'total_players_in_network': len(player_aggregate),
            'top_hidden_playmakers': top_hidden.to_dict('records') if not top_hidden.empty else []
        }
        
        self.results = {
            'centrality': combined_centrality,
            'player_aggregate': player_aggregate,
            'hidden_playmakers': combined_hidden,
            'top_hidden': top_hidden,
            'network_evolution': combined_evolution,
            'insights': insights
        }
        
        return self.results
    
    def visualize_networks(self, output_dir: str):
        """Create visualizations."""
        if 'player_aggregate' not in self.results:
            return
        
        import matplotlib.pyplot as plt
        from pathlib import Path
        import networkx as nx
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 1. Centrality vs Traditional Stats
        if not self.results['hidden_playmakers'].empty:
            hidden_df = self.results['hidden_playmakers']
            
            plt.figure(figsize=(12, 8))
            scatter = plt.scatter(hidden_df['total_points'], hidden_df['centrality_score'], 
                                 s=100, alpha=0.6, c=hidden_df['pagerank'], 
                                 cmap='viridis', edgecolors='black')
            
            # Annotate top hidden playmakers
            top_hidden = hidden_df.nlargest(5, 'hidden_value')
            for _, row in top_hidden.iterrows():
                plt.annotate(f"P{row['player_id']}", 
                            (row['total_points'], row['centrality_score']),
                            fontsize=8, alpha=0.8)
            
            plt.colorbar(scatter, label='PageRank')
            plt.xlabel('Traditional Points (Goals + Assists)')
            plt.ylabel('Centrality Score')
            plt.title('Hidden Playmakers: High Centrality, Low Traditional Stats')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(output_path / 'passing_network_hidden_playmakers.png', dpi=300)
            plt.close()
        
        # 2. Top Centrality Players
        player_df = self.results['player_aggregate'].nlargest(15, 'betweenness_centrality')
        
        plt.figure(figsize=(12, 8))
        plt.barh(range(len(player_df)), player_df['betweenness_centrality'], 
                alpha=0.7, edgecolor='black')
        plt.yticks(range(len(player_df)), [f"P{pid}" for pid in player_df['player_id']])
        plt.xlabel('Betweenness Centrality')
        plt.ylabel('Player')
        plt.title('Top 15 Players by Betweenness Centrality (Network Importance)')
        plt.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        plt.savefig(output_path / 'passing_network_top_centrality.png', dpi=300)
        plt.close()
        
        # 3. Centrality Distribution
        plt.figure(figsize=(10, 6))
        plt.hist(self.results['centrality']['betweenness_centrality'], 
                bins=30, alpha=0.7, edgecolor='black')
        plt.xlabel('Betweenness Centrality')
        plt.ylabel('Frequency')
        plt.title('Distribution of Player Centrality')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / 'passing_network_centrality_distribution.png', dpi=300)
        plt.close()

