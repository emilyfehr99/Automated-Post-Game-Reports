#!/usr/bin/env python3
"""
Create All Team Logos - Generate PNG logos for all NHL teams
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
from io import BytesIO

class AllTeamLogoCreator:
    def __init__(self, output_dir="team_logos_png"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # All NHL team colors and info
        self.team_info = {
            'EDM': {'primary': '#FF4C00', 'secondary': '#041E42', 'text': 'white', 'symbol': '🛢️'},
            'VGK': {'primary': '#B4975A', 'secondary': '#333333', 'text': 'white', 'symbol': '⚔️'},
            'FLA': {'primary': '#C8102E', 'secondary': '#041E42', 'text': 'white', 'symbol': '🐱'},
            'BOS': {'primary': '#FFB81C', 'secondary': '#000000', 'text': 'black', 'symbol': '🐻'},
            'TOR': {'primary': '#003E7E', 'secondary': '#FFFFFF', 'text': 'white', 'symbol': '🍁'},
            'MTL': {'primary': '#AF1E2D', 'secondary': '#192168', 'text': 'white', 'symbol': '🇨🇦'},
            'OTT': {'primary': '#C52032', 'secondary': '#000000', 'text': 'white', 'symbol': '🏛️'},
            'BUF': {'primary': '#002654', 'secondary': '#FCB514', 'text': 'white', 'symbol': '🐃'},
            'DET': {'primary': '#CE1126', 'secondary': '#FFFFFF', 'text': 'white', 'symbol': '🔴'},
            'TBL': {'primary': '#002868', 'secondary': '#FFFFFF', 'text': 'white', 'symbol': '⚡'},
            'CAR': {'primary': '#CC0000', 'secondary': '#000000', 'text': 'white', 'symbol': '🌪️'},
            'WSH': {'primary': '#C8102E', 'secondary': '#041E42', 'text': 'white', 'symbol': '🦅'},
            'PIT': {'primary': '#000000', 'secondary': '#FCB514', 'text': 'white', 'symbol': '🐧'},
            'NYR': {'primary': '#0038A8', 'secondary': '#CE1126', 'text': 'white', 'symbol': '🗽'},
            'NYI': {'primary': '#00539B', 'secondary': '#F57D31', 'text': 'white', 'symbol': '🏝️'},
            'NJD': {'primary': '#CE1126', 'secondary': '#000000', 'text': 'white', 'symbol': '😈'},
            'PHI': {'primary': '#F74902', 'secondary': '#000000', 'text': 'white', 'symbol': '🦅'},
            'CBJ': {'primary': '#002654', 'secondary': '#CE1126', 'text': 'white', 'symbol': '🔵'},
            'NSH': {'primary': '#FFB81C', 'secondary': '#002F87', 'text': 'black', 'symbol': '🎸'},
            'STL': {'primary': '#002F87', 'secondary': '#FCB514', 'text': 'white', 'symbol': '🎵'},
            'MIN': {'primary': '#154734', 'secondary': '#DDD0C0', 'text': 'white', 'symbol': '🌲'},
            'WPG': {'primary': '#041E42', 'secondary': '#004C97', 'text': 'white', 'symbol': '✈️'},
            'COL': {'primary': '#6F263D', 'secondary': '#236192', 'text': 'white', 'symbol': '🏔️'},
            'ARI': {'primary': '#8C2633', 'secondary': '#E2D6B5', 'text': 'white', 'symbol': '🌵'},
            'SJS': {'primary': '#006D75', 'secondary': '#000000', 'text': 'white', 'symbol': '🦈'},
            'LAK': {'primary': '#111111', 'secondary': '#A2AAAD', 'text': 'white', 'symbol': '👑'},
            'ANA': {'primary': '#F47A20', 'secondary': '#B9975B', 'text': 'white', 'symbol': '🦆'},
            'CGY': {'primary': '#C8102E', 'secondary': '#F1BE48', 'text': 'white', 'symbol': '🔥'},
            'VAN': {'primary': '#001F5C', 'secondary': '#00843D', 'text': 'white', 'symbol': '🌊'},
            'SEA': {'primary': '#001628', 'secondary': '#99D9EA', 'text': 'white', 'symbol': '🐙'},
            'CHI': {'primary': '#C8102E', 'secondary': '#000000', 'text': 'white', 'symbol': '🦅'},
            'DAL': {'primary': '#006847', 'secondary': '#111111', 'text': 'white', 'symbol': '⭐'}
        }
    
    def create_team_logo(self, team_abbrev, size=(200, 200)):
        """Create a professional team logo"""
        if team_abbrev not in self.team_info:
            print(f"❌ No team info found for {team_abbrev}")
            return None
        
        team_data = self.team_info[team_abbrev]
        primary_color = team_data['primary']
        secondary_color = team_data['secondary']
        text_color = team_data['text']
        symbol = team_data['symbol']
        
        # Create figure
        fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Create circular logo with team colors
        circle = patches.Circle((5, 5), 4.5, facecolor=primary_color, 
                              edgecolor=secondary_color, linewidth=3)
        ax.add_patch(circle)
        
        # Add inner circle for depth
        inner_circle = patches.Circle((5, 5), 3.5, facecolor=secondary_color, 
                                    edgecolor=primary_color, linewidth=1)
        ax.add_patch(inner_circle)
        
        # Add team abbreviation
        ax.text(5, 5.5, team_abbrev, color=text_color, fontsize=24, 
               ha='center', va='center', fontweight='bold', zorder=3)
        
        # Add symbol if available
        if symbol:
            ax.text(5, 4, symbol, color=text_color, fontsize=16, 
                   ha='center', va='center', zorder=4)
        
        # Add team name below
        team_names = {
            'EDM': 'OILERS', 'VGK': 'GOLDEN KNIGHTS', 'FLA': 'PANTHERS', 'BOS': 'BRUINS',
            'TOR': 'MAPLE LEAFS', 'MTL': 'CANADIENS', 'OTT': 'SENATORS', 'BUF': 'SABRES',
            'DET': 'RED WINGS', 'TBL': 'LIGHTNING', 'CAR': 'HURRICANES', 'WSH': 'CAPITALS',
            'PIT': 'PENGUINS', 'NYR': 'RANGERS', 'NYI': 'ISLANDERS', 'NJD': 'DEVILS',
            'PHI': 'FLYERS', 'CBJ': 'BLUE JACKETS', 'NSH': 'PREDATORS', 'STL': 'BLUES',
            'MIN': 'WILD', 'WPG': 'JETS', 'COL': 'AVALANCHE', 'ARI': 'COYOTES',
            'SJS': 'SHARKS', 'LAK': 'KINGS', 'ANA': 'DUCKS', 'CGY': 'FLAMES',
            'VAN': 'CANUCKS', 'SEA': 'KRAKEN', 'CHI': 'BLACKHAWKS', 'DAL': 'STARS'
        }
        
        team_name = team_names.get(team_abbrev, team_abbrev)
        ax.text(5, 2.5, team_name, color=text_color, fontsize=8, 
               ha='center', va='center', fontweight='bold', zorder=3)
        
        # Save to file
        logo_path = os.path.join(self.output_dir, f"{team_abbrev}.png")
        plt.savefig(logo_path, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return logo_path
    
    def create_all_logos(self):
        """Create logos for all NHL teams"""
        print("🏒 Creating PNG logos for all NHL teams...")
        print("=" * 50)
        
        created_count = 0
        for team_abbrev in self.team_info.keys():
            print(f"Creating logo for {team_abbrev}...")
            logo_path = self.create_team_logo(team_abbrev)
            if logo_path:
                print(f"✅ Created {team_abbrev} logo: {logo_path}")
                created_count += 1
            else:
                print(f"❌ Failed to create {team_abbrev} logo")
        
        print(f"\n✅ Created {created_count}/{len(self.team_info)} team logos")
        return created_count

def main():
    """Create all NHL team logos"""
    creator = AllTeamLogoCreator()
    
    # Create all logos
    created = creator.create_all_logos()
    
    if created > 0:
        print(f"\n🎉 Successfully created {created} NHL team logos!")
        print("All PNG logos are now ready for use in ReportLab PDFs.")
    else:
        print("\n❌ No logos were successfully created.")

if __name__ == "__main__":
    main()
