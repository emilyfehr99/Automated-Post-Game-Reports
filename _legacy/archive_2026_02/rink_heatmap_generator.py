#!/usr/bin/env python3
"""
Rink Heatmap Generator
Renders goal trajectories and heatmaps on NHL rink diagrams
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import seaborn as sns
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from scipy.stats import gaussian_kde
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RinkHeatmapGenerator:
    """Generates visual heatmaps and route overlays on NHL rink diagrams"""
    
    # NHL rink dimensions (in feet)
    RINK_LENGTH = 200
    RINK_WIDTH = 85
    
    # Zone lines
    BLUE_LINE_OFFENSIVE = 75
    BLUE_LINE_DEFENSIVE = -75
    CENTER_LINE = 0
    
    # Goal dimensions
    GOAL_LINE = 89
    GOAL_WIDTH = 6
    
    # Faceoff circle radius
    FACEOFF_RADIUS = 15
    
    def __init__(self, figsize=(12, 6)):
        self.figsize = figsize
        
    def draw_nhl_rink(self, ax: plt.Axes, half_rink: bool = False):
        """
        Draw official NHL rink dimensions and markings
        
        Args:
            ax: Matplotlib axes to draw on
            half_rink: If True, only draw offensive zone (common for goal analysis)
        """
        # Set limits
        if half_rink:
            ax.set_xlim(25, 100)
            ax.set_ylim(-42.5, 42.5)
        else:
            ax.set_xlim(-100, 100)
            ax.set_ylim(-42.5, 42.5)
        
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Rink boards (rounded rectangle)
        if half_rink:
            # Just show offensive zone
            rink = patches.Rectangle((25, -42.5), 75, 85, 
                                     linewidth=2, edgecolor='black', facecolor='white')
        else:
            rink = patches.FancyBboxPatch((-100, -42.5), 200, 85, 
                                         boxstyle="round,pad=0,rounding_size=28",
                                         linewidth=2, edgecolor='black', facecolor='white')
        ax.add_patch(rink)
        
        # Center red line
        if not half_rink:
            ax.plot([0, 0], [-42.5, 42.5], 'r-', linewidth=2, label='Center Line')
        
        # Blue lines
        if not half_rink:
            ax.plot([self.BLUE_LINE_DEFENSIVE, self.BLUE_LINE_DEFENSIVE], 
                   [-42.5, 42.5], 'b-', linewidth=2, label='Blue Line')
        
        ax.plot([self.BLUE_LINE_OFFENSIVE, self.BLUE_LINE_OFFENSIVE], 
               [-42.5, 42.5], 'b-', linewidth=2)
        
        # Goal line and crease
        ax.plot([self.GOAL_LINE, self.GOAL_LINE], [-42.5, 42.5], 'r-', linewidth=1)
        
        # Goal crease (simplified as semicircle)
        crease = patches.Arc((self.GOAL_LINE, 0), 8, 8, angle=0, theta1=90, theta2=270,
                            linewidth=2, edgecolor='red', facecolor='lightblue', alpha=0.3)
        ax.add_patch(crease)
        
        # Goal net
        goal = patches.Rectangle((self.GOAL_LINE, -self.GOAL_WIDTH/2), 1, self.GOAL_WIDTH,
                                 linewidth=2, edgecolor='red', facecolor='red', alpha=0.5)
        ax.add_patch(goal)
        
        # Faceoff circles (offensive zone)
        for y_pos in [-22, 22]:
            circle = patches.Circle((69, y_pos), self.FACEOFF_RADIUS, 
                                   linewidth=1.5, edgecolor='red', facecolor='none')
            ax.add_patch(circle)
            
            # Faceoff dot
            dot = patches.Circle((69, y_pos), 1, color='red')
            ax.add_patch(dot)
        
        # Center faceoff circle
        if not half_rink:
            center_circle = patches.Circle((0, 0), self.FACEOFF_RADIUS,
                                          linewidth=1.5, edgecolor='blue', facecolor='none')
            ax.add_patch(center_circle)
            
            center_dot = patches.Circle((0, 0), 1, color='blue')
            ax.add_patch(center_dot)
    
    def plot_trajectory_heatmap(self, trajectories: List[Dict], ax: plt.Axes = None, 
                               title: str = "Goal Scoring Heatmap"):
        """
        Create density heatmap of puck positions from trajectories
        
        Args:
            trajectories: List of trajectory dictionaries
            ax: Matplotlib axes (creates new if None)
            title: Plot title
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        
        # Draw rink
        self.draw_nhl_rink(ax, half_rink=True)
        
        # Extract all puck positions
        all_x = []
        all_y = []
        
        for traj in trajectories:
            path = traj.get('path', [])
            for x, y in path:
                all_x.append(x)
                all_y.append(y)
        
        if not all_x:
            logger.warning("No trajectory data to plot")
            return ax
        
        # Create 2D histogram for heatmap
        x_bins = np.linspace(25, 100, 50)
        y_bins = np.linspace(-42.5, 42.5, 40)
        
        heatmap, xedges, yedges = np.histogram2d(all_x, all_y, bins=[x_bins, y_bins])
        
        # Plot heatmap
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        im = ax.imshow(heatmap.T, extent=extent, origin='lower', 
                      cmap='YlOrRd', alpha=0.6, aspect='auto')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        return ax
    
    def plot_common_routes(self, clustered_routes: Dict, top_n: int = 10, 
                          ax: plt.Axes = None, title: str = "Common Goal Routes"):
        """
        Overlay most frequent goal routes as lines
        
        Args:
            clustered_routes: Dictionary of clustered trajectories
            top_n: Number of top routes to display
            ax: Matplotlib axes (creates new if None)
            title: Plot title
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        
        # Draw rink
        self.draw_nhl_rink(ax, half_rink=True)
        
        # Color palette for different clusters
        colors = sns.color_palette("husl", min(len(clustered_routes), top_n))
        
        cluster_count = 0
        for cluster_id, routes in list(clustered_routes.items())[:top_n]:
            if cluster_count >= top_n:
                break
            
            # Calculate average path for this cluster
            all_paths = [r['path'] for r in routes]
            
            # Plot each route in the cluster with transparency
            for path in all_paths:
                x_coords = [p[0] for p in path]
                y_coords = [p[1] for p in path]
                
                ax.plot(x_coords, y_coords, color=colors[cluster_count], 
                       alpha=0.3, linewidth=1)
            
            # Plot cluster average as thick line
            max_len = max(len(p) for p in all_paths)
            avg_x = []
            avg_y = []
            
            for i in range(max_len):
                x_vals = [p[i][0] for p in all_paths if i < len(p)]
                y_vals = [p[i][1] for p in all_paths if i < len(p)]
                if x_vals:
                    avg_x.append(np.mean(x_vals))
                    avg_y.append(np.mean(y_vals))
            
            ax.plot(avg_x, avg_y, color=colors[cluster_count], 
                   linewidth=3, label=f"Route {cluster_count + 1} ({len(routes)} goals)")
            
            cluster_count += 1
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=8)
        
        return ax
    
    def plot_hybrid_visualization(self, trajectories: List[Dict], 
                                  clustered_routes: Dict, 
                                  team: str = "Team",
                                  output_path: Optional[str] = None):
        """
        Create hybrid visualization with heatmap + route overlays
        
        Args:
            trajectories: List of all trajectories
            clustered_routes: Clustered route patterns
            team: Team name for title
            output_path: Path to save figure (optional)
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Left: Heatmap
        self.plot_trajectory_heatmap(trajectories, ax=ax1, 
                                     title=f"{team} Goal Scoring Heatmap")
        
        # Right: Common routes
        self.plot_common_routes(clustered_routes, top_n=5, ax=ax2,
                               title=f"{team} Top 5 Goal Routes")
        
        plt.tight_layout()
        
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved visualization to {output_path}")
        
        return fig
    
    def generate_goal_route_report(self, trajectories: List[Dict],
                                   clustered_routes: Dict,
                                   team: str = "Team",
                                   output_dir: str = "reports"):
        """
        Generate comprehensive goal route analysis report
        
        Args:
            trajectories: List of all trajectories
            clustered_routes: Clustered route patterns
            team: Team abbreviation
            output_dir: Directory to save reports
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate hybrid visualization
        viz_path = output_path / f"goal_routes_{team}.png"
        self.plot_hybrid_visualization(trajectories, clustered_routes, team, str(viz_path))
        
        # Generate statistics
        stats = self._calculate_route_statistics(trajectories, clustered_routes)
        
        # Save stats to JSON
        stats_path = output_path / f"goal_route_stats_{team}.json"
        import json
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Generated goal route report for {team}")
        
        return viz_path, stats_path
    
    def _calculate_route_statistics(self, trajectories: List[Dict], 
                                    clustered_routes: Dict) -> Dict:
        """Calculate summary statistics for routes"""
        total_goals = len(trajectories)
        
        if total_goals == 0:
            return {}
        
        # Average release distance
        avg_distance = np.mean([t['release_distance'] for t in trajectories])
        
        # Most common route
        most_common_cluster = max(clustered_routes.items(), key=lambda x: len(x[1]))
        most_common_pct = (len(most_common_cluster[1]) / total_goals) * 100
        
        # Lateral vs straight shots
        high_curvature = sum(1 for t in trajectories if t['curvature'] > 1.2)
        
        return {
            'total_goals': total_goals,
            'avg_release_distance': round(avg_distance, 1),
            'num_route_patterns': len(clustered_routes),
            'most_common_route_pct': round(most_common_pct, 1),
            'high_curvature_shots': high_curvature,
            'high_curvature_pct': round((high_curvature / total_goals) * 100, 1)
        }


if __name__ == "__main__":
    # Example usage
    from goal_route_analyzer import GoalRouteAnalyzer
    
    # Load trajectories
    analyzer = GoalRouteAnalyzer()
    trajectories = analyzer.load_trajectories("data/goal_trajectories_COL.json")
    
    # Cluster routes
    clusters = analyzer.cluster_routes(trajectories)
    
    # Generate visualization
    generator = RinkHeatmapGenerator()
    generator.generate_goal_route_report(trajectories, clusters, team="COL")
