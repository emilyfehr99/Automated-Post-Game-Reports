#!/usr/bin/env python3
"""
Show the actual NHL team logos
Downloads and displays the real SVG logos
"""

import requests
import json
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import xml.etree.ElementTree as ET
import re
import numpy as np

def get_team_logos():
    """Get the actual team logo URLs"""
    print("🏒 FETCHING REAL NHL TEAM LOGOS 🏒")
    print("=" * 50)
    
    # Get play-by-play data to get team info
    game_id = "2024030242"
    play_by_play_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    try:
        response = session.get(play_by_play_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            away_team = data.get('awayTeam', {})
            home_team = data.get('homeTeam', {})
            
            print(f"Away Team: {away_team.get('commonName', {}).get('default', 'Unknown')} ({away_team.get('abbrev', 'Unknown')})")
            print(f"Home Team: {home_team.get('commonName', {}).get('default', 'Unknown')} ({home_team.get('abbrev', 'Unknown')})")
            print()
            
            return away_team, home_team
        else:
            print(f"❌ API returned {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def download_and_show_logo(team_info, team_name):
    """Download and display a team logo"""
    logo_url = team_info.get('logo', '')
    if not logo_url:
        print(f"❌ No logo URL for {team_name}")
        return
    
    print(f"📥 Downloading logo for {team_name}...")
    print(f"   URL: {logo_url}")
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    try:
        response = session.get(logo_url, timeout=10)
        if response.status_code == 200:
            svg_content = response.content.decode('utf-8')
            print(f"   ✅ Downloaded {len(svg_content)} characters of SVG")
            
            # Parse SVG to extract information
            try:
                root = ET.fromstring(svg_content)
                print(f"   📐 SVG dimensions: {root.get('width', 'unknown')}x{root.get('height', 'unknown')}")
                print(f"   📐 ViewBox: {root.get('viewBox', 'unknown')}")
                
                # Count paths
                paths = root.findall('.//{http://www.w3.org/2000/svg}path')
                print(f"   🎨 Found {len(paths)} path elements")
                
                # Show colors used
                colors = set()
                for path in paths:
                    fill = path.get('fill', 'none')
                    if fill != 'none':
                        colors.add(fill)
                
                print(f"   🎨 Colors used: {', '.join(sorted(colors))}")
                
                # Create a visualization
                create_logo_visualization(svg_content, team_name, colors)
                
            except ET.ParseError as e:
                print(f"   ❌ SVG parsing error: {e}")
                
        else:
            print(f"   ❌ Failed to download: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error downloading logo: {e}")

def create_logo_visualization(svg_content, team_name, colors):
    """Create a visualization of the logo"""
    try:
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Left plot: Color palette
        ax1.set_title(f'{team_name} Logo Colors', fontsize=14, fontweight='bold')
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis('off')
        
        color_list = list(colors)
        for i, color in enumerate(color_list):
            y_pos = 0.8 - (i * 0.15)
            rect = patches.Rectangle((0.1, y_pos), 0.3, 0.1, 
                                   facecolor=color, edgecolor='black', linewidth=1)
            ax1.add_patch(rect)
            ax1.text(0.5, y_pos + 0.05, color, fontsize=10, va='center')
        
        # Right plot: SVG content preview
        ax2.set_title(f'{team_name} SVG Preview', fontsize=14, fontweight='bold')
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        
        # Show SVG content as text
        svg_preview = svg_content[:500] + "..." if len(svg_content) > 500 else svg_content
        ax2.text(0.05, 0.95, f"SVG Content Preview:\n\n{svg_preview}", 
                fontsize=8, va='top', ha='left', 
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(f'{team_name}_logo_analysis.png', dpi=150, bbox_inches='tight')
        plt.show()
        
        print(f"   📊 Logo analysis saved as {team_name}_logo_analysis.png")
        
    except Exception as e:
        print(f"   ❌ Error creating visualization: {e}")

def main():
    """Main function to show the logos"""
    print("🏒 NHL TEAM LOGO VIEWER 🏒")
    print("=" * 30)
    
    # Get team information
    away_team, home_team = get_team_logos()
    
    if away_team and home_team:
        print("\n" + "="*50)
        print("📥 DOWNLOADING AND ANALYZING LOGOS")
        print("="*50)
        
        # Download and show away team logo
        away_name = away_team.get('abbrev', 'Away')
        download_and_show_logo(away_team, away_name)
        
        print()
        
        # Download and show home team logo  
        home_name = home_team.get('abbrev', 'Home')
        download_and_show_logo(home_team, home_name)
        
        print("\n" + "="*50)
        print("✅ LOGO ANALYSIS COMPLETE!")
        print("="*50)
        print("The logos have been downloaded and analyzed.")
        print("Check the generated PNG files to see the logo colors and SVG content.")
        
    else:
        print("❌ Could not fetch team information")

if __name__ == "__main__":
    main()
