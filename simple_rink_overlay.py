#!/usr/bin/env python3
"""
Simple Rink Overlay - Resize API rink to match custom image
Uses NHL standard dimensions: 200ft x 85ft
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import numpy as np
import json
from pathlib import Path
from typing import List, Dict
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleRinkOverlay:
    """Overlay goal routes on custom rink by matching dimensions"""
    
    # NHL Official Rink Dimensions (in feet)
    RINK_LENGTH = 200
    RINK_WIDTH = 85
    
    def __init__(self, custom_rink_path: str):
        """Load custom rink image"""
        self.custom_rink = Image.open(custom_rink_path)
        self.img_width, self.img_height = self.custom_rink.size
        
        # Calculate pixels per foot based on image dimensions
        # Assume image shows full rink (200ft x 85ft)
        self.pixels_per_foot_x = self.img_width / self.RINK_LENGTH
        self.pixels_per_foot_y = self.img_height / self.RINK_WIDTH
        
        logger.info(f"Image size: {self.img_width}x{self.img_height} pixels")
        logger.info(f"Scale: {self.pixels_per_foot_x:.2f} px/ft (X), {self.pixels_per_foot_y:.2f} px/ft (Y)")
    
    def rink_to_image_coords(self, rink_x: float, rink_y: float) -> tuple:
        """
        Convert NHL rink coordinates to image pixel coordinates
        
        Rink coords: (-100, -42.5) to (100, 42.5) feet (center ice at 0,0)
        Image coords: (0, 0) to (width, height) pixels (top-left origin)
        
        Args:
            rink_x: X in feet from center ice (-100 to 100)
            rink_y: Y in feet from center ice (-42.5 to 42.5)
            
        Returns:
            (pixel_x, pixel_y)
        """
        # Translate rink center (0,0) to image center
        # Rink X: -100 -> 0px, 0 -> center, 100 -> width
        pixel_x = (rink_x + self.RINK_LENGTH/2) * self.pixels_per_foot_x
        
        # Rink Y: -42.5 -> 0px, 0 -> center, 42.5 -> height
        # Note: Image Y is inverted (0 at top)
        pixel_y = (rink_y + self.RINK_WIDTH/2) * self.pixels_per_foot_y
        
        return (pixel_x, pixel_y)
    
    def plot_overlay(self, trajectories: List[Dict], 
                    output_path: str = "data/simple_rink_overlay.png",
                    show_routes: bool = True,
                    show_heatmap: bool = True,
                    route_alpha: float = 0.4,
                    route_color: str = 'red'):
        """
        Create overlay of goal routes on custom rink image
        
        Args:
            trajectories: List of trajectory dicts with 'path' key
            output_path: Where to save result
            show_routes: Show individual trajectory lines
            show_heatmap: Show density heatmap
            route_alpha: Transparency of route lines (0-1)
            route_color: Color of route lines
        """
        fig, ax = plt.subplots(figsize=(16, 8))
        
        # Display custom rink as background
        ax.imshow(self.custom_rink)
        
        # Convert and plot trajectories
        all_points_x = []
        all_points_y = []
        
        for traj in trajectories:
            path = traj.get('path', [])
            if len(path) < 2:
                continue
            
            # Convert path to image coordinates
            img_path_x = []
            img_path_y = []
            
            for rink_x, rink_y in path:
                px, py = self.rink_to_image_coords(rink_x, rink_y)
                img_path_x.append(px)
                img_path_y.append(py)
                all_points_x.append(px)
                all_points_y.append(py)
            
            # Plot route line
            if show_routes:
                ax.plot(img_path_x, img_path_y, color=route_color, 
                       alpha=route_alpha, linewidth=1.5)
        
        # Plot heatmap overlay
        if show_heatmap and all_points_x:
            # Create 2D histogram
            heatmap, xedges, yedges = np.histogram2d(
                all_points_x, all_points_y, 
                bins=[60, 30],
                range=[[0, self.img_width], [0, self.img_height]]
            )
            
            # Smooth the heatmap
            from scipy.ndimage import gaussian_filter
            heatmap = gaussian_filter(heatmap, sigma=2)
            
            # Plot as semi-transparent overlay
            extent = [0, self.img_width, self.img_height, 0]
            ax.imshow(heatmap.T, extent=extent, origin='upper', 
                     cmap='YlOrRd', alpha=0.5, interpolation='bilinear')
        
        # Add title and stats
        ax.set_title(f"Goal Routes Overlay - {len(trajectories)} Goals Analyzed", 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Add stats text
        if trajectories:
            avg_distance = np.mean([t['release_distance'] for t in trajectories])
            stats_text = f"Avg Shot Distance: {avg_distance:.1f}ft"
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                   fontsize=12, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.axis('off')
        plt.tight_layout()
        
        # Save
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        logger.info(f"Saved overlay to {output_path}")
        
        plt.close()
        
        return output_path


def main():
    """Main execution"""
    # Paths
    custom_rink = "nhl-analytics/public/rink.jpeg"
    trajectory_file = "data/goal_trajectories_all_teams.json"
    output_file = "data/simple_rink_overlay.png"
    
    # Validate files
    if not Path(custom_rink).exists():
        print(f"❌ Error: Custom rink image not found at {custom_rink}")
        return
    
    if not Path(trajectory_file).exists():
        print(f"❌ Error: Trajectory data not found at {trajectory_file}")
        print("Run: python3 aggregate_goal_routes.py first")
        return
    
    # Load trajectories
    with open(trajectory_file, 'r') as f:
        trajectories = json.load(f)
    
    print(f"\n📊 Loaded {len(trajectories)} goal trajectories")
    
    # Create overlay
    print(f"🏒 Creating overlay on custom rink...")
    overlay = SimpleRinkOverlay(custom_rink)
    
    output_path = overlay.plot_overlay(
        trajectories,
        output_path=output_file,
        show_routes=True,
        show_heatmap=True,
        route_alpha=0.3,
        route_color='red'
    )
    
    print(f"\n✅ Overlay complete!")
    print(f"📁 Saved to: {output_path}")
    print(f"\nOpening result...")
    
    # Open result
    import subprocess
    subprocess.run(['open', output_path])


if __name__ == "__main__":
    main()
