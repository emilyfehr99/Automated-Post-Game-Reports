"""Fourier Analysis of Game Rhythm - Frequency Domain Analysis."""
import numpy as np
import pandas as pd
from scipy import signal
from scipy.fft import fft, fftfreq
from typing import Dict, List, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.data_loader import DataLoader

class FourierAnalyzer:
    """Analyze game rhythm using Fourier transform."""
    
    def __init__(self, data_dir: str):
        """Initialize analyzer."""
        self.data_loader = DataLoader(data_dir)
        self.results = {}
        
    def create_event_timeseries(self, events_df: pd.DataFrame, team: str = None,
                               event_type: str = None, window_seconds: float = 60.0) -> np.ndarray:
        """Create time series of event frequency."""
        # Filter by team and event type if specified
        filtered = events_df.copy()
        if team:
            filtered = filtered[filtered['Team'] == team]
        if event_type:
            filtered = filtered[filtered['Event'] == event_type]
        
        if filtered.empty:
            return np.array([])
        
        # Get time range
        max_time = filtered['Clock_Seconds'].max()
        min_time = filtered['Clock_Seconds'].min()
        
        # Create time bins
        num_bins = int((max_time - min_time) / window_seconds) + 1
        time_bins = np.linspace(min_time, max_time, num_bins)
        
        # Count events in each bin
        event_counts = np.zeros(len(time_bins) - 1)
        
        for i in range(len(time_bins) - 1):
            mask = (
                (filtered['Clock_Seconds'] >= time_bins[i]) &
                (filtered['Clock_Seconds'] < time_bins[i + 1])
            )
            event_counts[i] = mask.sum()
        
        return event_counts
    
    def compute_fft_analysis(self, time_series: np.ndarray, 
                            sampling_rate: float = 1.0) -> Dict:
        """Compute FFT and extract dominant frequencies."""
        if len(time_series) < 4:
            return {}
        
        # Remove DC component (mean)
        time_series = time_series - np.mean(time_series)
        
        # Compute FFT
        fft_values = fft(time_series)
        frequencies = fftfreq(len(time_series), 1.0 / sampling_rate)
        
        # Get power spectrum
        power = np.abs(fft_values) ** 2
        
        # Only positive frequencies
        positive_freq_idx = frequencies >= 0
        positive_frequencies = frequencies[positive_freq_idx]
        positive_power = power[positive_freq_idx]
        
        # Find dominant frequency (highest power, excluding DC)
        if len(positive_power) > 1:
            # Skip DC (index 0)
            dominant_idx = np.argmax(positive_power[1:]) + 1
            dominant_freq = positive_frequencies[dominant_idx]
            dominant_power = positive_power[dominant_idx]
        else:
            dominant_freq = 0
            dominant_power = 0
        
        # Calculate period (1/frequency)
        period = 1.0 / dominant_freq if dominant_freq > 0 else np.inf
        
        # Energy in different frequency bands
        low_freq_energy = np.sum(positive_power[(positive_frequencies > 0) & (positive_frequencies < 0.01)])
        mid_freq_energy = np.sum(positive_power[(positive_frequencies >= 0.01) & (positive_frequencies < 0.05)])
        high_freq_energy = np.sum(positive_power[positive_frequencies >= 0.05])
        
        total_energy = low_freq_energy + mid_freq_energy + high_freq_energy
        
        return {
            'dominant_frequency': dominant_freq,
            'dominant_power': dominant_power,
            'dominant_period': period,
            'frequencies': positive_frequencies,
            'power_spectrum': positive_power,
            'low_freq_energy_pct': low_freq_energy / total_energy if total_energy > 0 else 0,
            'mid_freq_energy_pct': mid_freq_energy / total_energy if total_energy > 0 else 0,
            'high_freq_energy_pct': high_freq_energy / total_energy if total_energy > 0 else 0
        }
    
    def analyze_team_rhythm(self, events_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze rhythm for each team."""
        team_rhythms = []
        
        for team, team_data in events_df.groupby('Team'):
            # All events rhythm
            all_events_ts = self.create_event_timeseries(team_data, team=team, window_seconds=45.0)
            if len(all_events_ts) < 4:
                continue
            
            all_fft = self.compute_fft_analysis(all_events_ts, sampling_rate=1.0/45.0)
            
            # Shot rhythm
            shot_ts = self.create_event_timeseries(team_data, team=team, event_type='Shot', window_seconds=45.0)
            shot_fft = {}
            if len(shot_ts) >= 4:
                shot_fft = self.compute_fft_analysis(shot_ts, sampling_rate=1.0/45.0)
            
            # Goals
            goals = len(team_data[team_data['Event'] == 'Goal'])
            
            team_rhythms.append({
                'team': team,
                'dominant_frequency': all_fft.get('dominant_frequency', 0),
                'dominant_period': all_fft.get('dominant_period', 0),
                'rhythm_power': all_fft.get('dominant_power', 0),
                'shot_dominant_frequency': shot_fft.get('dominant_frequency', 0),
                'shot_dominant_period': shot_fft.get('dominant_period', 0),
                'low_freq_pct': all_fft.get('low_freq_energy_pct', 0),
                'mid_freq_pct': all_fft.get('mid_freq_energy_pct', 0),
                'high_freq_pct': all_fft.get('high_freq_energy_pct', 0),
                'goals': goals,
                'avg_event_rate': len(team_data) / (team_data['Clock_Seconds'].max() - team_data['Clock_Seconds'].min()) if team_data['Clock_Seconds'].max() > team_data['Clock_Seconds'].min() else 0
            })
        
        return pd.DataFrame(team_rhythms)
    
    def detect_rhythm_disruption(self, events_df: pd.DataFrame, 
                                window_size: int = 20) -> pd.DataFrame:
        """Detect when team rhythm is disrupted."""
        disruptions = []
        
        for team, team_data in events_df.groupby('Team'):
            # Create time series
            time_series = self.create_event_timeseries(team_data, team=team, window_seconds=30.0)
            
            if len(time_series) < window_size * 2:
                continue
            
            # Rolling FFT analysis
            for i in range(window_size, len(time_series) - window_size):
                window = time_series[i-window_size:i]
                next_window = time_series[i:i+window_size]
                
                window_fft = self.compute_fft_analysis(window, sampling_rate=1.0/30.0)
                next_fft = self.compute_fft_analysis(next_window, sampling_rate=1.0/30.0)
                
                # Calculate frequency shift
                freq_shift = abs(window_fft.get('dominant_frequency', 0) - 
                               next_fft.get('dominant_frequency', 0))
                
                power_drop = (window_fft.get('dominant_power', 0) - 
                            next_fft.get('dominant_power', 0)) / window_fft.get('dominant_power', 1)
                
                # Disruption if significant frequency shift or power drop
                if freq_shift > 0.01 or power_drop > 0.3:
                    disruptions.append({
                        'team': team,
                        'window_index': i,
                        'freq_shift': freq_shift,
                        'power_drop': power_drop,
                        'time_minutes': i * 30.0 / 60.0
                    })
        
        return pd.DataFrame(disruptions)
    
    def run_full_analysis(self) -> Dict:
        """Run complete Fourier analysis."""
        games = self.data_loader.get_all_games()
        
        all_team_rhythms = []
        all_disruptions = []
        
        for game in games:
            print(f"Analyzing rhythm for {game['game_id']}...")
            
            events_df = self.data_loader.load_events(
                game['events'],
                full_path=game.get('events_full_path')
            )
            if events_df.empty:
                continue
            
            # Team rhythm analysis
            team_rhythm = self.analyze_team_rhythm(events_df)
            team_rhythm['game_id'] = game['game_id']
            all_team_rhythms.append(team_rhythm)
            
            # Rhythm disruption detection
            disruptions = self.detect_rhythm_disruption(events_df)
            disruptions['game_id'] = game['game_id']
            all_disruptions.append(disruptions)
        
        if not all_team_rhythms:
            return {'insights': {}}
        
        # Combine results
        combined_rhythms = pd.concat(all_team_rhythms, ignore_index=True)
        combined_disruptions = pd.concat(all_disruptions, ignore_index=True) if all_disruptions else pd.DataFrame()
        
        # Aggregate by team
        team_aggregate = combined_rhythms.groupby('team').agg({
            'dominant_frequency': 'mean',
            'dominant_period': 'mean',
            'rhythm_power': 'mean',
            'goals': 'sum',
            'avg_event_rate': 'mean'
        }).reset_index()
        
        # Link rhythm to performance
        if len(team_aggregate) > 1:
            correlation = team_aggregate['dominant_frequency'].corr(team_aggregate['goals'])
            
            # High frequency vs low frequency teams
            median_freq = team_aggregate['dominant_frequency'].median()
            high_freq_teams = team_aggregate[team_aggregate['dominant_frequency'] > median_freq]
            low_freq_teams = team_aggregate[team_aggregate['dominant_frequency'] <= median_freq]
            
            high_freq_goals = high_freq_teams['goals'].mean() if not high_freq_teams.empty else 0
            low_freq_goals = low_freq_teams['goals'].mean() if not low_freq_teams.empty else 0
            
            goals_ratio = high_freq_goals / low_freq_goals if low_freq_goals > 0 else 0
            
            insights = {
                'avg_dominant_frequency': combined_rhythms['dominant_frequency'].mean(),
                'frequency_goals_correlation': correlation,
                'high_freq_avg_goals': high_freq_goals,
                'low_freq_avg_goals': low_freq_goals,
                'high_vs_low_goals_ratio': goals_ratio,
                'median_frequency_threshold': median_freq,
                'avg_dominant_period': combined_rhythms['dominant_period'].mean(),
                'total_rhythm_disruptions': len(combined_disruptions)
            }
        else:
            insights = {
                'avg_dominant_frequency': combined_rhythms['dominant_frequency'].mean(),
                'avg_dominant_period': combined_rhythms['dominant_period'].mean()
            }
        
        self.results = {
            'team_rhythms': combined_rhythms,
            'team_aggregate': team_aggregate,
            'disruptions': combined_disruptions,
            'insights': insights
        }
        
        return self.results
    
    def visualize_rhythm(self, output_dir: str):
        """Create visualizations."""
        if 'team_aggregate' not in self.results:
            return
        
        import matplotlib.pyplot as plt
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        team_df = self.results['team_aggregate']
        
        # 1. Frequency vs Goals
        plt.figure(figsize=(10, 6))
        plt.scatter(team_df['dominant_frequency'], team_df['goals'], 
                   s=100, alpha=0.6, edgecolors='black')
        
        for _, row in team_df.iterrows():
            plt.annotate(row['team'], 
                        (row['dominant_frequency'], row['goals']),
                        fontsize=8)
        
        plt.xlabel('Dominant Frequency (Hz)')
        plt.ylabel('Total Goals')
        plt.title('Team Rhythm (Frequency) vs Performance (Goals)')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / 'fourier_frequency_vs_goals.png', dpi=300)
        plt.close()
        
        # 2. Period distribution
        plt.figure(figsize=(10, 6))
        plt.hist(self.results['team_rhythms']['dominant_period'], 
                bins=20, alpha=0.7, edgecolor='black')
        plt.xlabel('Dominant Period (seconds)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Team Game Rhythm Periods')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / 'fourier_period_distribution.png', dpi=300)
        plt.close()
        
        # 3. Rhythm power comparison
        plt.figure(figsize=(12, 6))
        team_df_sorted = team_df.sort_values('rhythm_power', ascending=False)
        plt.barh(team_df_sorted['team'], team_df_sorted['rhythm_power'], 
                alpha=0.7, edgecolor='black')
        plt.xlabel('Rhythm Power')
        plt.ylabel('Team')
        plt.title('Team Rhythm Strength (Higher = More Consistent Rhythm)')
        plt.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        plt.savefig(output_path / 'fourier_rhythm_power.png', dpi=300)
        plt.close()

