"""Voronoi Spatial Control Index (VSCI) - Territory Control Analysis."""
import numpy as np
import pandas as pd
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.data_loader import DataLoader

class VoronoiAnalyzer:
    """Analyze spatial control using Voronoi diagrams."""
    
    # Standard NHL rink dimensions (feet)
    RINK_LENGTH = 200
    RINK_WIDTH = 85
    
    def __init__(self, data_dir: str):
        """Initialize analyzer."""
        self.data_loader = DataLoader(data_dir)
        self.results = {}
        
    def compute_voronoi_control(self, positions: Dict[str, Tuple[float, float, str]], 
                                rink_bounds: Optional[Tuple[float, float, float, float]] = None) -> Dict[str, float]:
        """Compute Voronoi diagram and team control percentages.
        
        Returns: {'team1': control_percentage, 'team2': control_percentage, 'total_area': area}
        """
        if len(positions) < 3:
            return {'team1': 0.0, 'team2': 0.0, 'total_area': 0.0}
        
        # Extract positions and teams
        points = []
        point_teams = []
        
        for player_id, (x, y, team) in positions.items():
            # Filter out invalid positions
            if not (np.isnan(x) or np.isnan(y)):
                points.append([x, y])
                point_teams.append(team)
        
        if len(points) < 3:
            return {'team1': 0.0, 'team2': 0.0, 'total_area': 0.0}
        
        points = np.array(points)
        
        # Create bounding box for rink
        if rink_bounds is None:
            min_x, max_x = -self.RINK_LENGTH/2, self.RINK_LENGTH/2
            min_y, max_y = -self.RINK_WIDTH/2, self.RINK_WIDTH/2
        else:
            min_x, max_x, min_y, max_y = rink_bounds
        
        # Add boundary points to ensure Voronoi covers entire rink
        boundary_points = [
            [min_x, min_y], [min_x, max_y],
            [max_x, min_y], [max_x, max_y],
            [min_x, 0], [max_x, 0], [0, min_y], [0, max_y]
        ]
        all_points = np.vstack([points, boundary_points])
        
        try:
            vor = Voronoi(all_points)
        except:
            return {'team1': 0.0, 'team2': 0.0, 'total_area': 0.0}
        
        # Calculate area controlled by each team
        team_areas = {}
        unique_teams = list(set(point_teams))
        
        if len(unique_teams) < 2:
            return {'team1': 0.0, 'team2': 0.0, 'total_area': 0.0}
        
        # For each player (first n points are players)
        for i in range(len(points)):
            team = point_teams[i]
            if team not in team_areas:
                team_areas[team] = 0.0
            
            # Get Voronoi region for this point
            region_idx = vor.point_region[i]
            region = vor.regions[region_idx]
            
            if -1 in region or len(region) == 0:
                continue
            
            # Calculate polygon area
            vertices = vor.vertices[region]
            
            # Clip to rink bounds
            clipped_vertices = []
            for vx, vy in vertices:
                vx = np.clip(vx, min_x, max_x)
                vy = np.clip(vy, min_y, max_y)
                clipped_vertices.append([vx, vy])
            
            if len(clipped_vertices) >= 3:
                # Shoelace formula
                area = 0.5 * abs(sum(
                    clipped_vertices[j][0] * clipped_vertices[(j+1)%len(clipped_vertices)][1] -
                    clipped_vertices[(j+1)%len(clipped_vertices)][0] * clipped_vertices[j][1]
                    for j in range(len(clipped_vertices))
                ))
                team_areas[team] += area
        
        total_area = sum(team_areas.values())
        
        if total_area == 0:
            return {'team1': 0.0, 'team2': 0.0, 'total_area': 0.0}
        
        # Normalize to percentages
        result = {}
        for team in unique_teams:
            pct = (team_areas.get(team, 0) / total_area) * 100
            result[f'team_{team}'] = pct
        
        result['total_area'] = total_area
        result['teams'] = unique_teams
        
        return result
    
    def analyze_game(self, game_info: Dict[str, str]) -> pd.DataFrame:
        """Analyze spatial control for entire game."""
        # Load data
        tracking_df = self.data_loader.load_tracking(game_info['tracking'], sample_rate=30)
        
        if tracking_df.empty:
            return pd.DataFrame()
        
        results = []
        
        # Get unique periods and sample times
        periods = tracking_df['Period'].unique()
        
        for period in periods:
            period_data = tracking_df[tracking_df['Period'] == period].copy()
            
            # Sample at ~1 second intervals
            time_points = period_data['Clock_Seconds'].unique()[::30]  # Sample every 30 frames
            
            for clock_sec in time_points:
                positions = self.data_loader.get_player_positions_at_time(
                    tracking_df, period, clock_sec, tolerance=1.0
                )
                
                if len(positions) < 6:  # Need at least 6 players
                    continue
                
                control = self.compute_voronoi_control(positions)
                
                if control['total_area'] > 0:
                    results.append({
                        'game_id': game_info['game_id'],
                        'period': period,
                        'clock_seconds': clock_sec,
                        'team1': control.get('teams', [''])[0] if control.get('teams') else '',
                        'team2': control.get('teams', [''])[1] if len(control.get('teams', [])) > 1 else '',
                        'team1_control': control.get('team_' + control['teams'][0], 0) if control.get('teams') else 0,
                        'team2_control': control.get('team_' + control['teams'][1], 0) if len(control.get('teams', [])) > 1 else 0,
                        'control_differential': (
                            control.get('team_' + control['teams'][0], 0) - 
                            control.get('team_' + control['teams'][1], 0)
                        ) if len(control.get('teams', [])) > 1 else 0
                    })
        
        return pd.DataFrame(results)
    
    def link_control_to_events(self, control_df: pd.DataFrame, events_df: pd.DataFrame) -> pd.DataFrame:
        """Link spatial control to game events (goals, shots)."""
        if control_df.empty or events_df.empty:
            return pd.DataFrame()
        
        # For each goal/shot, find closest control measurement
        events_with_control = []
        
        for _, event in events_df.iterrows():
            if event['Event'] not in ['Goal', 'Shot']:
                continue
            
            period = event['Period']
            clock_sec = event.get('Clock_Seconds', 0)
            
            # Find closest control measurement
            mask = (
                (control_df['period'] == period) &
                (np.abs(control_df['clock_seconds'] - clock_sec) <= 3.0)
            )
            
            matches = control_df[mask]
            if not matches.empty:
                closest = matches.iloc[matches['clock_seconds'].abs().sub(clock_sec).abs().argmin()]
                
                events_with_control.append({
                    'event': event['Event'],
                    'team': event.get('Team', ''),
                    'period': period,
                    'clock': clock_sec,
                    'control_at_event': closest['control_differential'],
                    'team1_control': closest['team1_control'],
                    'team2_control': closest['team2_control']
                })
        
        return pd.DataFrame(events_with_control)
    
    def run_full_analysis(self) -> Dict:
        """Run complete Voronoi analysis."""
        games = self.data_loader.get_all_games()
        
        all_control = []
        all_events_with_control = []
        
        for game in games[:2]:  # Limit to 2 games for speed
            print(f"Analyzing {game['game_id']}...")
            
            # Check if we have tracking data
            if not game.get('tracking'):
                print(f"  ⚠️  No tracking data for {game['game_id']}, skipping...")
                continue
            
            # Analyze spatial control
            try:
                control_df = self.analyze_game(game)
                if not control_df.empty:
                    all_control.append(control_df)
                
                # Link to events
                if game.get('events'):
                    events_df = self.data_loader.load_events(
                        game['events'],
                        full_path=game.get('events_full_path')
                    )
                    if not events_df.empty and not control_df.empty:
                        events_control = self.link_control_to_events(control_df, events_df)
                        if not events_control.empty:
                            all_events_with_control.append(events_control)
            except Exception as e:
                print(f"  ⚠️  Error analyzing {game['game_id']}: {e}")
                continue
        
        if not all_control:
            return {'insights': {}}
        
        # Combine results
        combined_control = pd.concat(all_control, ignore_index=True)
        combined_events = pd.concat(all_events_with_control, ignore_index=True) if all_events_with_control else pd.DataFrame()
        
        # Generate insights
        avg_control_diff = combined_control['control_differential'].mean()
        std_control = combined_control['control_differential'].std()
        
        # Control vs goals
        goal_insight = {}
        if not combined_events.empty:
            goals = combined_events[combined_events['event'] == 'Goal']
            if not goals.empty:
                avg_control_for_goals = goals['control_at_event'].mean()
                goal_insight = {
                    'avg_control_when_scoring': avg_control_for_goals,
                    'control_advantage_for_goals': avg_control_for_goals
                }
        
        insights = {
            'avg_control_differential': avg_control_diff,
            'control_volatility': std_control,
            'max_control_advantage': combined_control['control_differential'].max(),
            'min_control_advantage': combined_control['control_differential'].min(),
            **goal_insight,
            'total_frames_analyzed': len(combined_control)
        }
        
        self.results = {
            'control_data': combined_control,
            'events_with_control': combined_events,
            'insights': insights
        }
        
        return self.results
    
    def visualize_control(self, output_dir: str):
        """Create visualizations."""
        if 'control_data' not in self.results:
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        control_df = self.results['control_data']
        
        # 1. Control differential over time
        plt.figure(figsize=(14, 6))
        for period in control_df['period'].unique():
            period_data = control_df[control_df['period'] == period]
            time_minutes = period_data['clock_seconds'] / 60
            plt.plot(time_minutes, period_data['control_differential'], 
                    alpha=0.6, label=f'Period {period}')
        
        plt.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        plt.xlabel('Game Time (minutes)')
        plt.ylabel('Control Differential (%)')
        plt.title('Voronoi Spatial Control Over Time')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / 'voronoi_control_over_time.png', dpi=300)
        plt.close()
        
        # 2. Distribution of control
        plt.figure(figsize=(10, 6))
        plt.hist(control_df['control_differential'], bins=50, alpha=0.7, edgecolor='black')
        plt.xlabel('Control Differential (%)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Spatial Control Differential')
        plt.axvline(x=0, color='r', linestyle='--', alpha=0.5)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / 'voronoi_control_distribution.png', dpi=300)
        plt.close()
        
        # 3. Control vs Goals
        if 'events_with_control' in self.results and not self.results['events_with_control'].empty:
            events_df = self.results['events_with_control']
            goals = events_df[events_df['event'] == 'Goal']
            
            if not goals.empty:
                plt.figure(figsize=(10, 6))
                plt.scatter(goals['control_at_event'], range(len(goals)), 
                           alpha=0.6, s=100)
                plt.axvline(x=0, color='r', linestyle='--', alpha=0.5)
                plt.xlabel('Control Differential at Goal (%)')
                plt.ylabel('Goal Number')
                plt.title('Spatial Control at Moment of Goal')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(output_path / 'voronoi_control_at_goals.png', dpi=300)
                plt.close()

