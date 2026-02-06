#!/usr/bin/env python3
"""
Interactive Rink Overlay Adjuster
Allows manual resizing and positioning of goal route overlay on custom rink image
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import numpy as np
import json
from pathlib import Path
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractiveRinkAdjuster:
    """Interactive tool to resize and position goal route overlay"""
    
    def __init__(self, custom_rink_path: str, trajectories: list):
        """
        Initialize with custom rink and trajectory data
        
        Args:
            custom_rink_path: Path to custom rink image
            trajectories: List of goal trajectory dicts
        """
        self.custom_rink = Image.open(custom_rink_path)
        self.img_width, self.img_height = self.custom_rink.size
        self.trajectories = trajectories
        
        # Overlay bounds (start with full image)
        self.overlay_x = 0
        self.overlay_y = 0
        self.overlay_width = self.img_width
        self.overlay_height = self.img_height
        
        # Interaction state
        self.dragging = False
        self.drag_corner = None
        self.drag_start = None
        self.corner_size = 20
        
        # NHL rink dimensions
        self.RINK_LENGTH = 200  # feet
        self.RINK_WIDTH = 85  # feet
        
    def rink_to_overlay_coords(self, rink_x: float, rink_y: float) -> tuple:
        """
        Convert NHL rink coordinates to overlay pixel coordinates
        
        Args:
            rink_x: X in feet from center ice (-100 to 100)
            rink_y: Y in feet from center ice (-42.5 to 42.5)
            
        Returns:
            (pixel_x, pixel_y) in overlay space
        """
        # Scale to overlay dimensions
        scale_x = self.overlay_width / self.RINK_LENGTH
        scale_y = self.overlay_height / self.RINK_WIDTH
        
        # Convert from rink coords to overlay coords
        overlay_x = (rink_x + self.RINK_LENGTH/2) * scale_x + self.overlay_x
        overlay_y = (rink_y + self.RINK_WIDTH/2) * scale_y + self.overlay_y
        
        return (overlay_x, overlay_y)
    
    def draw_routes(self, ax):
        """Draw goal routes on the axes"""
        for traj in self.trajectories:
            path = traj.get('path', [])
            if len(path) < 2:
                continue
            
            xs, ys = [], []
            for rink_x, rink_y in path:
                px, py = self.rink_to_overlay_coords(rink_x, rink_y)
                xs.append(px)
                ys.append(py)
            
            ax.plot(xs, ys, 'r-', alpha=0.3, linewidth=1.5)
    
    def draw_heatmap(self, ax):
        """Draw heatmap overlay"""
        all_x, all_y = [], []
        
        for traj in self.trajectories:
            path = traj.get('path', [])
            for rink_x, rink_y in path:
                px, py = self.rink_to_overlay_coords(rink_x, rink_y)
                all_x.append(px)
                all_y.append(py)
        
        if all_x:
            from scipy.ndimage import gaussian_filter
            heatmap, xedges, yedges = np.histogram2d(
                all_x, all_y,
                bins=[60, 30],
                range=[[0, self.img_width], [0, self.img_height]]
            )
            heatmap = gaussian_filter(heatmap, sigma=2)
            
            extent = [0, self.img_width, self.img_height, 0]
            ax.imshow(heatmap.T, extent=extent, origin='upper',
                     cmap='YlOrRd', alpha=0.5, interpolation='bilinear')
    
    def adjust_interactive(self):
        """
        Interactive adjustment interface
        
        Controls:
        - Drag corners to resize
        - Drag center to move
        - Press 's' to save
        - Press 'r' to reset
        """
        self.fig, self.ax = plt.subplots(figsize=(16, 8))
        self.ax.imshow(self.custom_rink)
        
        # Initialize corners list
        self.corners = []
        
        # Draw initial overlay
        self.redraw()
        
        # Draw control box
        self.control_box = Rectangle(
            (self.overlay_x, self.overlay_y),
            self.overlay_width, self.overlay_height,
            fill=False, edgecolor='cyan', linewidth=3, linestyle='--'
        )
        self.ax.add_patch(self.control_box)
        
        # Draw corner handles
        self.corner_size = 20
        self.corners = self.draw_corners()
        
        # Instructions
        title = ("INTERACTIVE OVERLAY ADJUSTER\n"
                "Drag CORNERS to resize | Drag CENTER to move | "
                "Press 'S' to SAVE | Press 'R' to RESET")
        self.ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        self.ax.axis('off')
        
        # Connect events
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        plt.show()
    
    def draw_corners(self):
        """Draw corner handles"""
        corners = []
        positions = [
            (self.overlay_x, self.overlay_y),  # Top-left
            (self.overlay_x + self.overlay_width, self.overlay_y),  # Top-right
            (self.overlay_x, self.overlay_y + self.overlay_height),  # Bottom-left
            (self.overlay_x + self.overlay_width, self.overlay_y + self.overlay_height)  # Bottom-right
        ]
        
        for x, y in positions:
            corner = Rectangle(
                (x - self.corner_size/2, y - self.corner_size/2),
                self.corner_size, self.corner_size,
                fill=True, facecolor='cyan', edgecolor='blue', linewidth=2
            )
            self.ax.add_patch(corner)
            corners.append(corner)
        
        return corners
    
    def get_corner_at(self, x, y):
        """Check if click is on a corner handle"""
        positions = [
            (self.overlay_x, self.overlay_y, 'tl'),
            (self.overlay_x + self.overlay_width, self.overlay_y, 'tr'),
            (self.overlay_x, self.overlay_y + self.overlay_height, 'bl'),
            (self.overlay_x + self.overlay_width, self.overlay_y + self.overlay_height, 'br')
        ]
        
        for cx, cy, corner_id in positions:
            if abs(x - cx) < self.corner_size and abs(y - cy) < self.corner_size:
                return corner_id
        
        return None
    
    def is_inside_box(self, x, y):
        """Check if point is inside overlay box"""
        return (self.overlay_x < x < self.overlay_x + self.overlay_width and
                self.overlay_y < y < self.overlay_y + self.overlay_height)
    
    def on_press(self, event):
        """Handle mouse press"""
        if event.xdata is None or event.ydata is None:
            return
        
        x, y = event.xdata, event.ydata
        
        # Check if clicking corner
        corner = self.get_corner_at(x, y)
        if corner:
            self.dragging = True
            self.drag_corner = corner
            self.drag_start = (x, y)
            return
        
        # Check if clicking inside box (for moving)
        if self.is_inside_box(x, y):
            self.dragging = True
            self.drag_corner = 'center'
            self.drag_start = (x, y)
    
    def on_release(self, event):
        """Handle mouse release"""
        self.dragging = False
        self.drag_corner = None
        self.drag_start = None
    
    def on_motion(self, event):
        """Handle mouse motion"""
        if not self.dragging or event.xdata is None or event.ydata is None:
            return
        
        x, y = event.xdata, event.ydata
        dx = x - self.drag_start[0]
        dy = y - self.drag_start[1]
        
        if self.drag_corner == 'center':
            # Move entire overlay
            self.overlay_x += dx
            self.overlay_y += dy
        elif self.drag_corner == 'tl':
            # Resize from top-left
            self.overlay_x += dx
            self.overlay_y += dy
            self.overlay_width -= dx
            self.overlay_height -= dy
        elif self.drag_corner == 'tr':
            # Resize from top-right
            self.overlay_y += dy
            self.overlay_width += dx
            self.overlay_height -= dy
        elif self.drag_corner == 'bl':
            # Resize from bottom-left
            self.overlay_x += dx
            self.overlay_width -= dx
            self.overlay_height += dy
        elif self.drag_corner == 'br':
            # Resize from bottom-right
            self.overlay_width += dx
            self.overlay_height += dy
        
        # Ensure minimum size
        self.overlay_width = max(100, self.overlay_width)
        self.overlay_height = max(50, self.overlay_height)
        
        self.drag_start = (x, y)
        self.redraw()
    
    def on_key(self, event):
        """Handle keyboard input"""
        if event.key == 's':
            self.save_overlay()
        elif event.key == 'r':
            self.reset_overlay()
    
    def redraw(self):
        """Redraw the overlay"""
        self.ax.clear()
        self.ax.imshow(self.custom_rink)
        
        # Redraw routes and heatmap
        self.draw_routes(self.ax)
        self.draw_heatmap(self.ax)
        
        # Redraw control box
        self.control_box = Rectangle(
            (self.overlay_x, self.overlay_y),
            self.overlay_width, self.overlay_height,
            fill=False, edgecolor='cyan', linewidth=3, linestyle='--'
        )
        self.ax.add_patch(self.control_box)
        
        # Redraw corners (create new ones since we cleared)
        self.corners = self.draw_corners()
        
        title = ("INTERACTIVE OVERLAY ADJUSTER\n"
                "Drag CORNERS to resize | Drag CENTER to move | "
                "Press 'S' to SAVE | Press 'R' to RESET")
        self.ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        self.ax.axis('off')
        
        self.fig.canvas.draw()
    
    def reset_overlay(self):
        """Reset to full image size"""
        self.overlay_x = 0
        self.overlay_y = 0
        self.overlay_width = self.img_width
        self.overlay_height = self.img_height
        self.redraw()
        logger.info("Reset overlay to full size")
    
    def save_overlay(self):
        """Save the current overlay"""
        output_path = "data/adjusted_rink_overlay.png"
        
        # Create final figure without controls
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.imshow(self.custom_rink)
        
        self.draw_routes(ax)
        self.draw_heatmap(ax)
        
        ax.set_title(f"Goal Routes Overlay - {len(self.trajectories)} Goals",
                    fontsize=16, fontweight='bold')
        ax.axis('off')
        plt.tight_layout()
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        logger.info(f"✅ Saved adjusted overlay to {output_path}")
        print(f"\n✅ Overlay saved to: {output_path}")
        
        # Also save calibration settings
        settings = {
            'overlay_x': self.overlay_x,
            'overlay_y': self.overlay_y,
            'overlay_width': self.overlay_width,
            'overlay_height': self.overlay_height
        }
        with open('data/overlay_settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
        
        print(f"📐 Calibration saved to: data/overlay_settings.json")


def main():
    """Main execution"""
    # Paths
    custom_rink = "nhl-analytics/public/rink.jpeg"
    trajectory_file = "data/goal_trajectories_all_teams.json"
    
    # Validate
    if not Path(custom_rink).exists():
        print(f"❌ Error: Rink image not found at {custom_rink}")
        return
    
    if not Path(trajectory_file).exists():
        print(f"❌ Error: Trajectory data not found at {trajectory_file}")
        return
    
    # Load trajectories
    with open(trajectory_file, 'r') as f:
        trajectories = json.load(f)
    
    print(f"\n📊 Loaded {len(trajectories)} goal trajectories")
    print("\n🎮 Starting interactive adjuster...")
    print("=" * 60)
    print("CONTROLS:")
    print("  • Drag CORNERS to resize overlay")
    print("  • Drag CENTER to move overlay")
    print("  • Press 'S' to SAVE final result")
    print("  • Press 'R' to RESET to full size")
    print("=" * 60 + "\n")
    
    # Create adjuster
    adjuster = InteractiveRinkAdjuster(custom_rink, trajectories)
    adjuster.adjust_interactive()


if __name__ == "__main__":
    main()
