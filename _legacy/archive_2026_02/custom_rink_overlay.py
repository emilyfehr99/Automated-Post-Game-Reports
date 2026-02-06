#!/usr/bin/env python3
"""
Custom Rink Overlay Tool
Interactive calibration to overlay goal routes on custom rink images
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomRinkOverlay:
    """Overlay goal trajectories on custom rink images with manual calibration"""
    
    # NHL rink faceoff circle positions (in feet from center ice)
    # Offensive zone faceoff circles
    FACEOFF_LEFT_X = 69  # feet from center
    FACEOFF_LEFT_Y = -22  # feet from center
    FACEOFF_RIGHT_X = 69
    FACEOFF_RIGHT_Y = 22
    
    def __init__(self, rink_image_path: str):
        """
        Initialize with custom rink image
        
        Args:
            rink_image_path: Path to the rink background image
        """
        self.rink_image_path = rink_image_path
        self.rink_image = mpimg.imread(rink_image_path)
        self.calibration_points = []
        self.transform_matrix = None
        
    def calibrate_interactive(self):
        """
        Interactive calibration: click two faceoff circles
        
        User clicks:
        1. Left faceoff circle (69, -22)
        2. Right faceoff circle (69, 22)
        """
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.imshow(self.rink_image)
        ax.set_title("Click the TWO offensive zone faceoff circles\n1. Left circle, 2. Right circle", 
                    fontsize=14, fontweight='bold')
        ax.axis('off')
        
        def onclick(event):
            if event.xdata is not None and event.ydata is not None:
                self.calibration_points.append((event.xdata, event.ydata))
                
                # Draw marker
                ax.plot(event.xdata, event.ydata, 'ro', markersize=10)
                plt.draw()
                
                if len(self.calibration_points) == 1:
                    ax.set_title("Good! Now click the RIGHT faceoff circle", 
                               fontsize=14, fontweight='bold')
                elif len(self.calibration_points) == 2:
                    ax.set_title("Calibration complete! Close this window.", 
                               fontsize=14, fontweight='bold', color='green')
                    plt.disconnect(cid)
        
        cid = plt.connect('button_press_event', onclick)
        plt.show()
        
        if len(self.calibration_points) != 2:
            raise ValueError("Calibration incomplete. Need 2 points.")
        
        # Calculate transformation
        self._calculate_transform()
        
        logger.info(f"Calibration complete with points: {self.calibration_points}")
    
    def _calculate_transform(self):
        """
        Calculate transformation from rink feet to image pixels
        
        We have:
        - Image point 1 (px, py) -> Rink point (69, -22)
        - Image point 2 (px, py) -> Rink point (69, 22)
        """
        img_left = np.array(self.calibration_points[0])  # (px, py)
        img_right = np.array(self.calibration_points[1])  # (px, py)
        
        rink_left = np.array([self.FACEOFF_LEFT_X, self.FACEOFF_LEFT_Y])
        rink_right = np.array([self.FACEOFF_RIGHT_X, self.FACEOFF_RIGHT_Y])
        
        # Calculate scale (pixels per foot)
        img_distance = np.linalg.norm(img_right - img_left)
        rink_distance = np.linalg.norm(rink_right - rink_left)  # Should be 44 feet
        
        self.pixels_per_foot = img_distance / rink_distance
        
        # Calculate rotation angle
        img_vector = img_right - img_left
        rink_vector = rink_right - rink_left
        
        img_angle = np.arctan2(img_vector[1], img_vector[0])
        rink_angle = np.arctan2(rink_vector[1], rink_vector[0])
        
        self.rotation_angle = img_angle - rink_angle
        
        # Calculate origin offset (where rink (0,0) maps to in image)
        # Use left faceoff circle as reference
        self.origin_offset = img_left - self._rotate_point(rink_left * self.pixels_per_foot, 
                                                           self.rotation_angle)
        
        logger.info(f"Transform: {self.pixels_per_foot:.2f} px/ft, rotation: {np.degrees(self.rotation_angle):.2f}°")
    
    def _rotate_point(self, point: np.ndarray, angle: float) -> np.ndarray:
        """Rotate a point by given angle"""
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        return rotation_matrix @ point
    
    def rink_to_image_coords(self, rink_x: float, rink_y: float) -> Tuple[float, float]:
        """
        Convert rink coordinates (feet) to image pixel coordinates
        
        Args:
            rink_x: X coordinate in rink feet
            rink_y: Y coordinate in rink feet
            
        Returns:
            (img_x, img_y) in pixels
        """
        if self.transform_matrix is None and self.pixels_per_foot is None:
            raise ValueError("Must calibrate first!")
        
        # Scale to pixels
        point = np.array([rink_x, rink_y]) * self.pixels_per_foot
        
        # Rotate
        point = self._rotate_point(point, self.rotation_angle)
        
        # Translate
        point = point + self.origin_offset
        
        return (point[0], point[1])
    
    def plot_trajectories_on_rink(self, trajectories: List[Dict], 
                                  output_path: str = "data/custom_rink_overlay.png",
                                  show_heatmap: bool = True,
                                  show_routes: bool = True,
                                  top_n_routes: int = 10):
        """
        Plot goal trajectories on the custom rink image
        
        Args:
            trajectories: List of trajectory dictionaries
            output_path: Where to save the output
            show_heatmap: Whether to show density heatmap
            show_routes: Whether to show individual route lines
            top_n_routes: Number of routes to display
        """
        fig, ax = plt.subplots(figsize=(16, 8))
        
        # Display rink image
        ax.imshow(self.rink_image)
        
        # Convert all trajectory points to image coordinates
        all_img_points = []
        for traj in trajectories:
            path = traj.get('path', [])
            img_path = []
            for rink_x, rink_y in path:
                img_x, img_y = self.rink_to_image_coords(rink_x, rink_y)
                img_path.append((img_x, img_y))
                all_img_points.append((img_x, img_y))
            
            # Plot route line
            if show_routes and len(img_path) > 1:
                xs = [p[0] for p in img_path]
                ys = [p[1] for p in img_path]
                ax.plot(xs, ys, 'r-', alpha=0.3, linewidth=1)
        
        # Plot heatmap
        if show_heatmap and all_img_points:
            xs = [p[0] for p in all_img_points]
            ys = [p[1] for p in all_img_points]
            
            # Create 2D histogram
            h, xedges, yedges = np.histogram2d(xs, ys, bins=50)
            
            # Plot as contour overlay
            extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]
            ax.imshow(h.T, extent=extent, origin='upper', cmap='YlOrRd', alpha=0.5)
        
        ax.set_title(f"Goal Routes Overlay - {len(trajectories)} Goals", 
                    fontsize=16, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        
        # Save
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved overlay to {output_path}")
        
        plt.show()
        
        return output_path


def main():
    """Main execution"""
    import sys
    
    # Paths
    rink_image = "nhl-analytics/public/rink.jpeg"
    trajectory_file = "data/goal_trajectories_all_teams.json"
    output_file = "data/custom_rink_overlay.png"
    
    # Check if files exist
    if not Path(rink_image).exists():
        print(f"Error: Rink image not found at {rink_image}")
        return
    
    if not Path(trajectory_file).exists():
        print(f"Error: Trajectory file not found at {trajectory_file}")
        print("Run aggregate_goal_routes.py first to generate trajectories")
        return
    
    # Load trajectories
    with open(trajectory_file, 'r') as f:
        trajectories = json.load(f)
    
    print(f"Loaded {len(trajectories)} goal trajectories")
    
    # Create overlay tool
    overlay = CustomRinkOverlay(rink_image)
    
    # Interactive calibration
    print("\n" + "="*60)
    print("CALIBRATION INSTRUCTIONS:")
    print("="*60)
    print("1. A window will open with your rink image")
    print("2. Click the LEFT offensive zone faceoff circle")
    print("3. Click the RIGHT offensive zone faceoff circle")
    print("4. Close the window when done")
    print("="*60 + "\n")
    
    overlay.calibrate_interactive()
    
    # Plot trajectories
    print("\nGenerating overlay...")
    output_path = overlay.plot_trajectories_on_rink(
        trajectories,
        output_path=output_file,
        show_heatmap=True,
        show_routes=True
    )
    
    print(f"\n✓ Overlay saved to: {output_path}")


if __name__ == "__main__":
    main()
