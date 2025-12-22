"""
Sprite Visualization Generator - Creates circular charts for goal analysis metrics
Generates matplotlib pie charts matching report aesthetics
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle
import numpy as np
from typing import Dict
import os

class SpriteVizGenerator:
    """Generates circular visualizations for sprite goal analysis"""
    
    def __init__(self):
        # Dark theme colors matching report aesthetic
        self.bg_color = '#1a1a1a'
        self.text_color = '#ffffff'
        self.accent_color = '#00bcd4'
        
        # Color schemes for each metric
        self.net_front_colors = ['#4caf50', '#9e9e9e']  # Green/Gray
        self.goal_type_colors = ['#ff5722', '#ff9800', '#ffc107']  # Red/Orange/Yellow
        self.entry_colors = ['#2196f3', '#03a9f4', '#00bcd4']  # Blues
        self.passing_colors = ['#9c27b0', '#e91e63', '#f44336']  # Purple/Pink/Red
    
    def create_simple_pie(self, ax, data, colors, title):
        """Create a simple, clean pie chart"""
        # Filter out zero values
        labels = [k for k, v in data.items() if v > 0]
        sizes = [v for v in data.values() if v > 0]
        colors_filtered = [colors[i] for i, v in enumerate(data.values()) if v > 0]
        
        if not sizes:
            # No data - show empty circle
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center',
                   fontsize=14, color=self.text_color, transform=ax.transAxes)
            ax.set_facecolor(self.bg_color)
            return
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(sizes, labels=None, colors=colors_filtered,
                                            autopct='%1.0f%%', startangle=90,
                                            textprops={'color': self.text_color, 'fontsize': 11, 'weight': 'bold'})
        
        # Add title
        ax.set_title(title, color=self.text_color, fontsize=13, weight='bold', pad=15)
        
        # Create legend
        legend_labels = [f"{label}: {size}" for label, size in zip(labels, sizes)]
        ax.legend(wedges, legend_labels, loc='upper left', bbox_to_anchor=(-0.3, 1),
                 fontsize=9, frameon=False, labelcolor=self.text_color)
    
    def create_percentage_circle(self, ax, percentage, title):
        """Create a simple percentage display with circle"""
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Draw circle
        circle = Circle((0.5, 0.5), 0.35, fill=True, color=self.net_front_colors[0], alpha=0.8)
        ax.add_patch(circle)
        
        # Add percentage text
        ax.text(0.5, 0.5, f"{percentage:.0f}%", ha='center', va='center',
               fontsize=28, color=self.text_color, weight='bold')
        
        # Add title
        ax.text(0.5, 0.15, title, ha='center', va='center',
               fontsize=13, color=self.text_color, weight='bold')
        
        ax.set_facecolor(self.bg_color)
    
    def create_sprite_metrics_row(self, metrics: Dict, output_path: str = None) -> str:
        """
        Create horizontal row of 4 circular metrics
        
        Args:
            metrics: Dict from SpriteGoalAnalyzer.analyze_game_goals()
            output_path: Where to save image (default: /tmp/sprite_metrics_{timestamp}.png)
        
        Returns:
            Path to generated image
        """
        if not metrics:
            return None
        
        # Create figure with 4 subplots
        fig, axes = plt.subplots(1, 4, figsize=(16, 4.5), facecolor=self.bg_color)
        fig.subplots_adjust(wspace=0.6, left=0.05, right=0.95)
        
        # 1. Net-Front Presence (percentage circle)
        self.create_percentage_circle(axes[0], metrics['net_front_pct'], 
                                      '🏒 NET-FRONT\nPRESENCE')
        
        # 2. Goal Types (pie chart)
        self.create_simple_pie(axes[1], metrics['goal_types'], 
                              self.goal_type_colors, '📊 GOAL\nTYPES')
        
        # 3. Zone Entries (pie chart)
        self.create_simple_pie(axes[2], metrics['zone_entries'],
                              self.entry_colors, '🚪 ZONE\nENTRIES')
        
        # 4. Passing Complexity (pie chart)
        self.create_simple_pie(axes[3], metrics['passing'],
                              self.passing_colors, '🎯 PASSING\nCOMPLEXITY')
        
        # Set background for all subplots
        for ax in axes:
            ax.set_facecolor(self.bg_color)
        
        # Save figure
        if not output_path:
            import time
            output_path = f"/tmp/sprite_metrics_{int(time.time())}.png"
        
        plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                   facecolor=self.bg_color, edgecolor='none')
        plt.close()
        
        return output_path


if __name__ == "__main__":
    #  Test with sample data
    from sprite_goal_analyzer import SpriteGoalAnalyzer
    
    analyzer = SpriteGoalAnalyzer()
    metrics = analyzer.analyze_game_goals('2025020536')
    
    if metrics:
        print("Generating visualization...")
        viz_gen = SpriteVizGenerator()
        output_file = viz_gen.create_sprite_metrics_row(
            metrics, 
            "/Users/emilyfehr8/Desktop/sprite_metrics_test.png"
        )
        print(f"✅ Visualization saved: {output_file}")
        print(f"\nMetrics:")
        print(f"  Net-Front: {metrics['net_front_pct']}%")
        print(f"  Goal Types: {metrics['goal_types']}")
        print(f"  Entries: {metrics['zone_entries']}")  
        print(f"  Passing: {metrics['passing']}")
    else:
        print("❌ No metrics available")
