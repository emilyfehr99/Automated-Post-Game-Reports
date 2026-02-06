#!/usr/bin/env python3
"""
SVG to PNG Converter - Convert SVG team logos to PNG for ReportLab
"""

import os
import subprocess
import sys
from PIL import Image
from io import BytesIO
import requests

class SVGToPNGConverter:
    def __init__(self, input_dir="simple_logos", output_dir="team_logos_png"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def convert_svg_to_png_pillow(self, svg_path, png_path, size=(100, 100)):
        """Convert SVG to PNG using PIL (limited SVG support)"""
        try:
            # PIL has limited SVG support, but let's try
            with open(svg_path, 'rb') as f:
                img = Image.open(f)
                img = img.convert('RGBA')
                img = img.resize(size, Image.Resampling.LANCZOS)
                img.save(png_path, 'PNG')
            return True
        except Exception as e:
            print(f"PIL conversion failed for {svg_path}: {e}")
            return False
    
    def convert_svg_to_png_cairosvg(self, svg_path, png_path, size=(100, 100)):
        """Convert SVG to PNG using cairosvg"""
        try:
            import cairosvg
            cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size[0], output_height=size[1])
            return True
        except ImportError:
            print("cairosvg not available")
            return False
        except Exception as e:
            print(f"cairosvg conversion failed for {svg_path}: {e}")
            return False
    
    def convert_svg_to_png_wand(self, svg_path, png_path, size=(100, 100)):
        """Convert SVG to PNG using Wand (ImageMagick)"""
        try:
            from wand.image import Image as WandImage
            with WandImage() as img:
                img.read(filename=svg_path)
                img.resize(size[0], size[1])
                img.format = 'png'
                img.save(filename=png_path)
            return True
        except ImportError:
            print("Wand (ImageMagick) not available")
            return False
        except Exception as e:
            print(f"Wand conversion failed for {svg_path}: {e}")
            return False
    
    def convert_svg_to_png_rsvg(self, svg_path, png_path, size=(100, 100)):
        """Convert SVG to PNG using rsvg-convert command line tool"""
        try:
            cmd = [
                'rsvg-convert',
                '--width', str(size[0]),
                '--height', str(size[1]),
                '--format', 'png',
                '--output', png_path,
                svg_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return True
            else:
                print(f"rsvg-convert failed: {result.stderr}")
                return False
        except FileNotFoundError:
            print("rsvg-convert command not found")
            return False
        except Exception as e:
            print(f"rsvg-convert conversion failed for {svg_path}: {e}")
            return False
    
    def create_simple_png_logo(self, team_abbrev, png_path, size=(100, 100)):
        """Create a simple PNG logo as fallback"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            
            fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100))
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Team colors
            team_colors = {
                'EDM': '#FF4C00', 'VGK': '#B4975A', 'FLA': '#C8102E', 'BOS': '#FFB81C',
                'TOR': '#003E7E', 'MTL': '#AF1E2D', 'OTT': '#C52032', 'BUF': '#002654',
                'DET': '#CE1126', 'TBL': '#002868', 'CAR': '#CC0000', 'WSH': '#C8102E',
                'PIT': '#000000', 'NYR': '#0038A8', 'NYI': '#00539B', 'NJD': '#CE1126',
                'PHI': '#F74902', 'CBJ': '#002654', 'NSH': '#FFB81C', 'STL': '#002F87',
                'MIN': '#154734', 'WPG': '#041E42', 'COL': '#6F263D', 'ARI': '#8C2633',
                'SJS': '#006D75', 'LAK': '#111111', 'ANA': '#F47A20', 'CGY': '#C8102E',
                'VAN': '#001F5C', 'SEA': '#001628', 'CHI': '#C8102E', 'DAL': '#006847'
            }
            
            color = team_colors.get(team_abbrev, '#666666')
            
            # Create circular logo
            circle = patches.Circle((5, 5), 4, facecolor=color, edgecolor='white', linewidth=2)
            ax.add_patch(circle)
            
            # Add team abbreviation
            ax.text(5, 5, team_abbrev, fontsize=20, fontweight='bold', 
                   ha='center', va='center', color='white')
            
            # Save to file
            plt.savefig(png_path, format='png', dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            return True
        except Exception as e:
            print(f"Failed to create simple PNG logo for {team_abbrev}: {e}")
            return False
    
    def convert_all_svgs(self):
        """Convert all SVG files to PNG"""
        print("🔄 Converting SVG team logos to PNG...")
        print("=" * 50)
        
        converted_count = 0
        svg_files = [f for f in os.listdir(self.input_dir) if f.endswith('.svg')]
        
        for svg_file in svg_files:
            team_abbrev = svg_file.replace('.svg', '')
            svg_path = os.path.join(self.input_dir, svg_file)
            png_path = os.path.join(self.output_dir, f"{team_abbrev}.png")
            
            print(f"Converting {team_abbrev}...")
            
            # Try different conversion methods
            success = False
            
            # Method 1: cairosvg
            if not success:
                success = self.convert_svg_to_png_cairosvg(svg_path, png_path)
                if success:
                    print(f"✅ Converted {team_abbrev} using cairosvg")
            
            # Method 2: rsvg-convert
            if not success:
                success = self.convert_svg_to_png_rsvg(svg_path, png_path)
                if success:
                    print(f"✅ Converted {team_abbrev} using rsvg-convert")
            
            # Method 3: Wand (ImageMagick)
            if not success:
                success = self.convert_svg_to_png_wand(svg_path, png_path)
                if success:
                    print(f"✅ Converted {team_abbrev} using Wand")
            
            # Method 4: PIL (limited support)
            if not success:
                success = self.convert_svg_to_png_pillow(svg_path, png_path)
                if success:
                    print(f"✅ Converted {team_abbrev} using PIL")
            
            # Method 5: Create simple PNG as fallback
            if not success:
                success = self.create_simple_png_logo(team_abbrev, png_path)
                if success:
                    print(f"✅ Created simple PNG logo for {team_abbrev}")
            
            if success:
                converted_count += 1
            else:
                print(f"❌ Failed to convert {team_abbrev}")
        
        print(f"\n✅ Converted {converted_count}/{len(svg_files)} team logos to PNG")
        return converted_count

def main():
    """Convert SVG team logos to PNG"""
    converter = SVGToPNGConverter()
    
    # Convert all SVGs
    converted = converter.convert_all_svgs()
    
    if converted > 0:
        print(f"\n🎉 Successfully converted {converted} team logos to PNG format!")
        print("PNG logos are now ready for use in ReportLab PDFs.")
    else:
        print("\n❌ No logos were successfully converted.")

if __name__ == "__main__":
    main()
