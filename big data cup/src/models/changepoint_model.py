"""Bayesian Change Point Detection - Strategy Shift Analysis."""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.data_loader import DataLoader

class ChangePointAnalyzer:
    """Detect strategy changes using change point detection."""
    
    def __init__(self, data_dir: str):
        """Initialize analyzer."""
        self.data_loader = DataLoader(data_dir)
        self.results = {}
        
    def compute_rolling_metrics(self, events_df: pd.DataFrame, team: str,
                               window_size: float = 120.0) -> pd.DataFrame:
        """Compute rolling window metrics for change point detection."""
        team_data = events_df[events_df['Team'] == team].copy()
        
        if team_data.empty:
            return pd.DataFrame()
        
        # Sort by time
        team_data = team_data.sort_values('Clock_Seconds')
        
        min_time = team_data['Clock_Seconds'].min()
        max_time = team_data['Clock_Seconds'].max()
        
        # Create time windows
        windows = []
        current_time = min_time
        
        while current_time < max_time:
            window_end = current_time + window_size
            
            window_data = team_data[
                (team_data['Clock_Seconds'] >= current_time) &
                (team_data['Clock_Seconds'] < window_end)
            ]
            
            if not window_data.empty:
                # Calculate metrics
                shot_rate = len(window_data[window_data['Event'] == 'Shot']) / window_size * 60  # per minute
                entry_rate = len(window_data[window_data['Event'] == 'Zone Entry']) / window_size * 60
                
                # Entry type distribution
                entries = window_data[window_data['Event'] == 'Zone Entry']
                if not entries.empty:
                    carry_pct = len(entries[entries['Detail_1'].str.contains('Carried', na=False)]) / len(entries)
                    dump_pct = len(entries[entries['Detail_1'].str.contains('Dumped', na=False)]) / len(entries)
                else:
                    carry_pct = 0
                    dump_pct = 0
                
                # Goal rate
                goal_rate = len(window_data[window_data['Event'] == 'Goal']) / window_size * 60
                
                windows.append({
                    'team': team,
                    'window_start': current_time,
                    'window_end': window_end,
                    'window_center': (current_time + window_end) / 2,
                    'shot_rate': shot_rate,
                    'entry_rate': entry_rate,
                    'carry_entry_pct': carry_pct,
                    'dump_entry_pct': dump_pct,
                    'goal_rate': goal_rate,
                    'total_events': len(window_data)
                })
            
            current_time = window_end
        
        return pd.DataFrame(windows)
    
    def detect_change_points_simple(self, metrics_df: pd.DataFrame, 
                                   metric_col: str, threshold: float = 2.0) -> List[float]:
        """Simple change point detection using z-score."""
        if metrics_df.empty or metric_col not in metrics_df.columns:
            return []
        
        values = metrics_df[metric_col].values
        if len(values) < 3:
            return []
        
        # Calculate rolling mean and std
        window_size = min(5, len(values) // 2)
        if window_size < 2:
            return []
        
        change_points = []
        
        for i in range(window_size, len(values) - window_size):
            before_mean = np.mean(values[i-window_size:i])
            before_std = np.std(values[i-window_size:i])
            
            after_mean = np.mean(values[i:i+window_size])
            
            if before_std > 0:
                z_score = abs(after_mean - before_mean) / before_std
                
                if z_score > threshold:
                    change_points.append(metrics_df.iloc[i]['window_center'])
        
        return change_points
    
    def detect_multiple_change_points(self, metrics_df: pd.DataFrame) -> Dict[str, List[float]]:
        """Detect change points for multiple metrics."""
        if metrics_df.empty:
            return {}
        
        change_points = {}
        
        # Detect for each metric
        metrics_to_check = ['shot_rate', 'entry_rate', 'carry_entry_pct', 'goal_rate']
        
        for metric in metrics_to_check:
            if metric in metrics_df.columns:
                cps = self.detect_change_points_simple(metrics_df, metric, threshold=1.5)
                change_points[metric] = cps
        
        return change_points
    
    def classify_strategy_shifts(self, events_df: pd.DataFrame, 
                                change_points: List[float], 
                                before_window: float = 60.0,
                                after_window: float = 60.0) -> pd.DataFrame:
        """Classify what type of strategy shift occurred."""
        shifts = []
        
        for cp in change_points:
            # Get events before and after change point
            before_events = events_df[
                (events_df['Clock_Seconds'] >= cp - before_window) &
                (events_df['Clock_Seconds'] < cp)
            ]
            
            after_events = events_df[
                (events_df['Clock_Seconds'] >= cp) &
                (events_df['Clock_Seconds'] < cp + after_window)
            ]
            
            if before_events.empty or after_events.empty:
                continue
            
            # Compare metrics
            before_shot_rate = len(before_events[before_events['Event'] == 'Shot']) / before_window * 60
            after_shot_rate = len(after_events[after_events['Event'] == 'Shot']) / after_window * 60
            
            before_entries = before_events[before_events['Event'] == 'Zone Entry']
            after_entries = after_events[after_events['Event'] == 'Zone Entry']
            
            before_carry_pct = len(before_entries[before_entries['Detail_1'].str.contains('Carried', na=False)]) / len(before_entries) if not before_entries.empty else 0
            after_carry_pct = len(after_entries[after_entries['Detail_1'].str.contains('Carried', na=False)]) / len(after_entries) if not after_entries.empty else 0
            
            # Classify shift type
            shift_type = "Unknown"
            if abs(after_shot_rate - before_shot_rate) > abs(after_carry_pct - before_carry_pct):
                if after_shot_rate > before_shot_rate:
                    shift_type = "More Aggressive (Increased Shot Rate)"
                else:
                    shift_type = "More Conservative (Decreased Shot Rate)"
            else:
                if after_carry_pct > before_carry_pct:
                    shift_type = "More Controlled (Increased Carry Entries)"
                else:
                    shift_type = "More Direct (Increased Dump Entries)"
            
            shifts.append({
                'change_point_time': cp,
                'shift_type': shift_type,
                'before_shot_rate': before_shot_rate,
                'after_shot_rate': after_shot_rate,
                'shot_rate_change': after_shot_rate - before_shot_rate,
                'before_carry_pct': before_carry_pct,
                'after_carry_pct': after_carry_pct,
                'carry_pct_change': after_carry_pct - before_carry_pct
            })
        
        return pd.DataFrame(shifts)
    
    def run_full_analysis(self) -> Dict:
        """Run complete change point analysis."""
        games = self.data_loader.get_all_games()
        
        all_change_points = []
        all_shifts = []
        all_metrics = []
        
        for game in games:
            print(f"Analyzing change points for {game['game_id']}...")
            
            events_df = self.data_loader.load_events(
                game['events'],
                full_path=game.get('events_full_path')
            )
            if events_df.empty:
                continue
            
            # Analyze each team
            for team in events_df['Team'].unique():
                # Compute rolling metrics
                metrics_df = self.compute_rolling_metrics(events_df, team, window_size=90.0)
                
                if metrics_df.empty:
                    continue
                
                metrics_df['game_id'] = game['game_id']
                all_metrics.append(metrics_df)
                
                # Detect change points
                change_points_dict = self.detect_multiple_change_points(metrics_df)
                
                # Combine all change points
                all_cps = []
                for metric, cps in change_points_dict.items():
                    for cp in cps:
                        all_cps.append({
                            'game_id': game['game_id'],
                            'team': team,
                            'change_point_time': cp,
                            'metric': metric
                        })
                
                all_change_points.extend(all_cps)
                
                # Classify shifts
                if all_cps:
                    unique_cps = sorted(set([cp['change_point_time'] for cp in all_cps]))
                    shifts = self.classify_strategy_shifts(events_df, unique_cps)
                    
                    if not shifts.empty:
                        shifts['game_id'] = game['game_id']
                        shifts['team'] = team
                        all_shifts.append(shifts)
        
        if not all_change_points:
            return {'insights': {}}
        
        # Combine results
        combined_cps = pd.DataFrame(all_change_points)
        combined_shifts = pd.concat(all_shifts, ignore_index=True) if all_shifts else pd.DataFrame()
        combined_metrics = pd.concat(all_metrics, ignore_index=True) if all_metrics else pd.DataFrame()
        
        # Aggregate insights
        if not combined_shifts.empty:
            shift_types = combined_shifts['shift_type'].value_counts().to_dict()
            avg_shot_rate_change = combined_shifts['shot_rate_change'].mean()
            avg_carry_change = combined_shifts['carry_pct_change'].mean()
        else:
            shift_types = {}
            avg_shot_rate_change = 0
            avg_carry_change = 0
        
        insights = {
            'total_change_points': len(combined_cps),
            'avg_cps_per_team': len(combined_cps) / len(combined_cps['team'].unique()) if not combined_cps.empty else 0,
            'shift_type_distribution': shift_types,
            'avg_shot_rate_change': avg_shot_rate_change,
            'avg_carry_entry_change': avg_carry_change,
            'most_common_shift': max(shift_types.items(), key=lambda x: x[1])[0] if shift_types else "None"
        }
        
        self.results = {
            'change_points': combined_cps,
            'strategy_shifts': combined_shifts,
            'rolling_metrics': combined_metrics,
            'insights': insights
        }
        
        return self.results
    
    def visualize_changepoints(self, output_dir: str):
        """Create visualizations."""
        if 'rolling_metrics' not in self.results or self.results['rolling_metrics'].empty:
            return
        
        import matplotlib.pyplot as plt
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        metrics_df = self.results['rolling_metrics']
        
        # 1. Shot rate over time with change points
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        for idx, team in enumerate(metrics_df['team'].unique()[:4]):  # First 4 teams
            ax = axes[idx // 2, idx % 2]
            team_data = metrics_df[metrics_df['team'] == team]
            
            if team_data.empty:
                continue
            
            # Plot shot rate
            time_minutes = team_data['window_center'] / 60
            ax.plot(time_minutes, team_data['shot_rate'], label='Shot Rate', alpha=0.7)
            
            # Mark change points
            if 'change_points' in self.results:
                team_cps = self.results['change_points'][
                    (self.results['change_points']['team'] == team) &
                    (self.results['change_points']['metric'] == 'shot_rate')
                ]['change_point_time'].values
                
                for cp in team_cps:
                    ax.axvline(x=cp/60, color='r', linestyle='--', alpha=0.5, linewidth=2)
            
            ax.set_xlabel('Game Time (minutes)')
            ax.set_ylabel('Shot Rate (per minute)')
            ax.set_title(f'{team} - Shot Rate & Change Points')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / 'changepoint_shot_rate_changes.png', dpi=300)
        plt.close()
        
        # 2. Strategy shift distribution
        if 'strategy_shifts' in self.results and not self.results['strategy_shifts'].empty:
            shifts_df = self.results['strategy_shifts']
            
            plt.figure(figsize=(12, 6))
            shift_counts = shifts_df['shift_type'].value_counts()
            plt.barh(range(len(shift_counts)), shift_counts.values, alpha=0.7, edgecolor='black')
            plt.yticks(range(len(shift_counts)), shift_counts.index)
            plt.xlabel('Frequency')
            plt.ylabel('Strategy Shift Type')
            plt.title('Distribution of Strategy Shift Types')
            plt.grid(True, alpha=0.3, axis='x')
            plt.tight_layout()
            plt.savefig(output_path / 'changepoint_shift_distribution.png', dpi=300)
            plt.close()
        
        # 3. Entry type changes
        plt.figure(figsize=(14, 8))
        for team in metrics_df['team'].unique()[:2]:  # First 2 teams
            team_data = metrics_df[metrics_df['team'] == team].sort_values('window_center')
            time_minutes = team_data['window_center'] / 60
            
            plt.plot(time_minutes, team_data['carry_entry_pct'] * 100, 
                    label=f'{team} - Carry %', alpha=0.7, linewidth=2)
        
        plt.xlabel('Game Time (minutes)')
        plt.ylabel('Carry Entry Percentage')
        plt.title('Entry Strategy Evolution Over Time')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / 'changepoint_entry_strategy.png', dpi=300)
        plt.close()

