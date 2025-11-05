"""Information Entropy of Play Sequences - Creativity Analysis."""
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.data_loader import DataLoader

class EntropyAnalyzer:
    """Analyze play sequence entropy (creativity/unpredictability)."""
    
    def __init__(self, data_dir: str):
        """Initialize analyzer."""
        self.data_loader = DataLoader(data_dir)
        self.results = {}
        
    def build_event_sequences(self, events_df: pd.DataFrame, window_size: int = 3) -> List[List[str]]:
        """Build sequences of events."""
        sequences = []
        
        # Group by team and period
        for (team, period), group in events_df.groupby(['Team', 'Period']):
            events = group['Event'].values.tolist()
            
            # Create sliding windows
            for i in range(len(events) - window_size + 1):
                sequence = events[i:i+window_size]
                sequences.append(sequence)
        
        return sequences
    
    def calculate_shannon_entropy(self, sequences: List[List[str]]) -> float:
        """Calculate Shannon entropy: H(X) = -Σ p(x)log₂(p(x))."""
        if not sequences:
            return 0.0
        
        # Count sequence frequencies
        sequence_counts = Counter(tuple(seq) for seq in sequences)
        total = len(sequences)
        
        # Calculate probabilities and entropy
        entropy = 0.0
        for count in sequence_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * np.log2(p)
        
        return entropy
    
    def calculate_transition_entropy(self, events_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate entropy of event transitions (Markov chain)."""
        transitions = defaultdict(int)
        event_counts = defaultdict(int)
        
        # Build transition matrix
        for team, group in events_df.groupby('Team'):
            events = group['Event'].values.tolist()
            
            for i in range(len(events) - 1):
                from_event = events[i]
                to_event = events[i + 1]
                transitions[(from_event, to_event)] += 1
                event_counts[from_event] += 1
        
        # Calculate conditional entropy for each starting event
        conditional_entropies = {}
        
        for from_event, total in event_counts.items():
            entropy = 0.0
            
            # Find all transitions from this event
            from_transitions = {k: v for k, v in transitions.items() if k[0] == from_event}
            
            if not from_transitions:
                conditional_entropies[from_event] = 0.0
                continue
            
            for (f, t), count in from_transitions.items():
                p = count / total
                if p > 0:
                    entropy -= p * np.log2(p)
            
            conditional_entropies[from_event] = entropy
        
        # Weighted average (by event frequency)
        total_events = sum(event_counts.values())
        weighted_entropy = sum(
            entropy * (event_counts[event] / total_events)
            for event, entropy in conditional_entropies.items()
        )
        
        return {
            'overall_transition_entropy': weighted_entropy,
            'conditional_entropies': conditional_entropies,
            'transition_matrix': dict(transitions)
        }
    
    def calculate_team_entropy(self, events_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate entropy metrics per team."""
        team_metrics = []
        
        for team, team_data in events_df.groupby('Team'):
            # Sequence entropy
            sequences = self.build_event_sequences(team_data, window_size=3)
            sequence_entropy = self.calculate_shannon_entropy(sequences)
            
            # Transition entropy
            transition_info = self.calculate_transition_entropy(team_data)
            transition_entropy = transition_info['overall_transition_entropy']
            
            # Event diversity (unique events / total events)
            unique_events = team_data['Event'].nunique()
            total_events = len(team_data)
            diversity = unique_events / total_events if total_events > 0 else 0
            
            # Goals scored (creativity should correlate with scoring)
            goals = len(team_data[team_data['Event'] == 'Goal'])
            
            team_metrics.append({
                'team': team,
                'sequence_entropy': sequence_entropy,
                'transition_entropy': transition_entropy,
                'event_diversity': diversity,
                'total_events': total_events,
                'goals': goals,
                'entropy_per_goal': transition_entropy / goals if goals > 0 else 0
            })
        
        return pd.DataFrame(team_metrics)
    
    def link_entropy_to_performance(self, entropy_df: pd.DataFrame, events_df: pd.DataFrame) -> Dict:
        """Analyze relationship between entropy and performance."""
        # Get goals per team
        goals_by_team = events_df[events_df['Event'] == 'Goal'].groupby('Team').size().to_dict()
        
        # Merge
        entropy_df = entropy_df.copy()
        entropy_df['actual_goals'] = entropy_df['team'].map(goals_by_team).fillna(0)
        
        # Correlation analysis
        if len(entropy_df) > 1:
            correlation = entropy_df['transition_entropy'].corr(entropy_df['actual_goals'])
            
            # High entropy vs low entropy teams
            median_entropy = entropy_df['transition_entropy'].median()
            high_entropy_teams = entropy_df[entropy_df['transition_entropy'] > median_entropy]
            low_entropy_teams = entropy_df[entropy_df['transition_entropy'] <= median_entropy]
            
            high_entropy_goals = high_entropy_teams['actual_goals'].mean() if not high_entropy_teams.empty else 0
            low_entropy_goals = low_entropy_teams['actual_goals'].mean() if not low_entropy_teams.empty else 0
            
            goals_ratio = high_entropy_goals / low_entropy_goals if low_entropy_goals > 0 else 0
            
            return {
                'entropy_goals_correlation': correlation,
                'high_entropy_avg_goals': high_entropy_goals,
                'low_entropy_avg_goals': low_entropy_goals,
                'high_vs_low_goals_ratio': goals_ratio,
                'median_entropy_threshold': median_entropy
            }
        
        return {}
    
    def run_full_analysis(self) -> Dict:
        """Run complete entropy analysis."""
        games = self.data_loader.get_all_games()
        
        all_team_entropy = []
        
        for game in games:
            print(f"Analyzing entropy for {game['game_id']}...")
            
            events_df = self.data_loader.load_events(
                game['events'], 
                full_path=game.get('events_full_path')
            )
            if events_df.empty:
                print(f"  ⚠️  No events data for {game['game_id']}")
                continue
            
            # Calculate team entropy
            team_entropy = self.calculate_team_entropy(events_df)
            team_entropy['game_id'] = game['game_id']
            all_team_entropy.append(team_entropy)
        
        if not all_team_entropy:
            return {'insights': {}}
        
        # Combine results
        combined_entropy = pd.concat(all_team_entropy, ignore_index=True)
        
        # Aggregate by team across all games
        team_aggregate = combined_entropy.groupby('team').agg({
            'sequence_entropy': 'mean',
            'transition_entropy': 'mean',
            'event_diversity': 'mean',
            'goals': 'sum',
            'total_events': 'sum'
        }).reset_index()
        
        # Link to performance
        all_events = pd.concat([self.data_loader.load_events(g['events']) for g in games], ignore_index=True)
        performance_link = self.link_entropy_to_performance(team_aggregate, all_events)
        
        # Generate insights
        insights = {
            'avg_sequence_entropy': combined_entropy['sequence_entropy'].mean(),
            'avg_transition_entropy': combined_entropy['transition_entropy'].mean(),
            'max_entropy_team': team_aggregate.loc[team_aggregate['transition_entropy'].idxmax(), 'team'] if not team_aggregate.empty else '',
            'min_entropy_team': team_aggregate.loc[team_aggregate['transition_entropy'].idxmin(), 'team'] if not team_aggregate.empty else '',
            'entropy_range': combined_entropy['transition_entropy'].max() - combined_entropy['transition_entropy'].min(),
            **performance_link
        }
        
        self.results = {
            'team_entropy': combined_entropy,
            'team_aggregate': team_aggregate,
            'insights': insights
        }
        
        return self.results
    
    def visualize_entropy(self, output_dir: str):
        """Create visualizations."""
        if 'team_aggregate' not in self.results:
            return
        
        import matplotlib.pyplot as plt
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        team_df = self.results['team_aggregate']
        
        # 1. Entropy vs Goals
        plt.figure(figsize=(10, 6))
        plt.scatter(team_df['transition_entropy'], team_df['goals'], 
                   s=100, alpha=0.6, edgecolors='black')
        
        for _, row in team_df.iterrows():
            plt.annotate(row['team'], 
                        (row['transition_entropy'], row['goals']),
                        fontsize=8)
        
        plt.xlabel('Transition Entropy (bits)')
        plt.ylabel('Total Goals')
        plt.title('Team Creativity (Entropy) vs Performance (Goals)')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / 'entropy_vs_goals.png', dpi=300)
        plt.close()
        
        # 2. Entropy distribution
        plt.figure(figsize=(10, 6))
        plt.hist(self.results['team_entropy']['transition_entropy'], 
                bins=20, alpha=0.7, edgecolor='black')
        plt.xlabel('Transition Entropy (bits)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Team Creativity (Entropy)')
        plt.axvline(x=self.results['insights'].get('median_entropy_threshold', 0), 
                   color='r', linestyle='--', alpha=0.5, label='Median')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / 'entropy_distribution.png', dpi=300)
        plt.close()
        
        # 3. Team comparison
        plt.figure(figsize=(12, 6))
        team_df_sorted = team_df.sort_values('transition_entropy', ascending=False)
        plt.barh(team_df_sorted['team'], team_df_sorted['transition_entropy'], 
                alpha=0.7, edgecolor='black')
        plt.xlabel('Transition Entropy (bits)')
        plt.ylabel('Team')
        plt.title('Team Creativity Ranking (Higher = More Unpredictable)')
        plt.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        plt.savefig(output_path / 'entropy_team_ranking.png', dpi=300)
        plt.close()

