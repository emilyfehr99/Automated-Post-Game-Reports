#!/usr/bin/env python3
"""Generate a PDF reference of all team colors for review"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_team_colors_reference():
    """Create a PDF showing all team primary and accent colors"""
    
    # Register Russo One font if available
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_dir, 'RussoOne-Regular.ttf')
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('RussoOne-Regular', font_path))
    else:
        font_path = "/Users/emilyfehr8/Library/Fonts/RussoOne-Regular.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('RussoOne-Regular', font_path))
    
    output_file = os.path.join(script_dir, 'team_colors_reference.pdf')
    doc = SimpleDocTemplate(output_file, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    if 'RussoOne-Regular' in pdfmetrics.getRegisteredFontNames():
        title_style = styles['Heading1']
        title_style.fontName = 'RussoOne-Regular'
    else:
        title_style = styles['Heading1']
    
    title = Paragraph("NHL Team Colors Reference", title_style)
    story.append(title)
    story.append(Spacer(1, 0.3*inch))
    
    # Team colors dictionary
    team_colors = {
        'TBL': ('Tampa Bay Lightning', (0, 40, 104), (255, 184, 28), 'Blue', 'Gold'),
        'NSH': ('Nashville Predators', (255, 184, 28), (4, 30, 66), 'Gold', 'Navy'),
        'EDM': ('Edmonton Oilers', (4, 30, 66), (255, 140, 0), 'Blue', 'Orange'),
        'FLA': ('Florida Panthers', (200, 16, 46), (185, 151, 91), 'Red', 'Gold'),
        'COL': ('Colorado Avalanche', (111, 38, 61), (139, 197, 63), 'Burgundy', 'Blue'),
        'DAL': ('Dallas Stars', (0, 99, 65), (143, 135, 130), 'Green', 'Silver'),
        'BOS': ('Boston Bruins', (252, 181, 20), (139, 0, 0), 'Gold', 'Brown/Maroon'),
        'TOR': ('Toronto Maple Leafs', (0, 32, 91), (255, 255, 255), 'Blue', 'White'),
        'MTL': ('Montreal Canadiens', (175, 30, 45), (25, 33, 104), 'Red', 'Blue'),
        'OTT': ('Ottawa Senators', (200, 16, 46), (194, 145, 44), 'Red', 'Gold'),
        'BUF': ('Buffalo Sabres', (0, 38, 84), (255, 184, 28), 'Blue', 'Gold'),
        'DET': ('Detroit Red Wings', (206, 17, 38), (255, 255, 255), 'Red', 'White'),
        'CAR': ('Carolina Hurricanes', (226, 24, 54), (0, 0, 0), 'Red', 'Black'),
        'WSH': ('Washington Capitals', (4, 30, 66), (255, 184, 28), 'Blue', 'Gold'),
        'PIT': ('Pittsburgh Penguins', (255, 184, 28), (207, 196, 147), 'Gold', 'Gold'),
        'NYR': ('New York Rangers', (0, 56, 168), (255, 255, 255), 'Blue', 'White'),
        'NYI': ('New York Islanders', (0, 83, 155), (255, 184, 28), 'Blue', 'Orange'),
        'NJD': ('New Jersey Devils', (206, 17, 38), (255, 255, 255), 'Red', 'White'),
        'PHI': ('Philadelphia Flyers', (247, 30, 36), (0, 0, 0), 'Orange', 'Black'),
        'CBJ': ('Columbus Blue Jackets', (0, 38, 84), (200, 16, 46), 'Blue', 'Red'),
        'STL': ('St. Louis Blues', (0, 47, 108), (252, 181, 20), 'Blue', 'Yellow'),
        'MIN': ('Minnesota Wild', (0, 99, 65), (200, 16, 46), 'Green', 'Red'),
        'WPG': ('Winnipeg Jets', (4, 30, 66), (215, 33, 41), 'Navy Blue', 'Red'),
        'ARI': ('Arizona Coyotes', (140, 38, 51), (226, 214, 181), 'Red', 'Sand'),
        'VGK': ('Vegas Golden Knights', (185, 151, 91), (185, 151, 91), 'Gold', 'Gold'),
        'SJS': ('San Jose Sharks', (0, 109, 117), (234, 114, 0), 'Teal', 'Orange'),
        'LAK': ('Los Angeles Kings', (162, 170, 173), (162, 170, 173), 'Silver', 'Silver'),
        'ANA': ('Anaheim Ducks', (185, 151, 91), (200, 16, 46), 'Gold', 'Red'),
        'CGY': ('Calgary Flames', (200, 16, 46), (255, 184, 28), 'Red', 'Yellow'),
        'VAN': ('Vancouver Canucks', (0, 132, 61), (0, 32, 91), 'Green', 'Blue'),
        'SEA': ('Seattle Kraken', (200, 16, 46), (156, 219, 217), 'Red Alert', 'Ice Blue'),
        'UTA': ('Utah Hockey Club', (1, 1, 1), (105, 179, 231), 'Rock Black', 'Mountain Blue'),
        'CHI': ('Chicago Blackhawks', (207, 10, 44), (255, 184, 28), 'Red', 'Gold'),
    }
    
    # Create table data
    table_data = [['Team', 'Team Name', 'Primary Color', 'Primary RGB', 'Accent Color', 'Accent RGB']]
    
    for abbrev in sorted(team_colors.keys()):
        name, primary_rgb, accent_rgb, primary_name, accent_name = team_colors[abbrev]
        table_data.append([
            abbrev,
            name,
            primary_name,
            f"RGB{primary_rgb}",
            accent_name,
            f"RGB{accent_rgb}"
        ])
    
    # Create table
    table = Table(table_data, colWidths=[0.8*inch, 2.2*inch, 1.3*inch, 1.2*inch, 1.3*inch, 1.2*inch])
    
    # Style the table
    table_style = TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows - alternate colors for primary and accent
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])
    
    # Add color swatches to primary and accent columns
    for i, abbrev in enumerate(sorted(team_colors.keys()), start=1):
        _, primary_rgb, accent_rgb, _, _ = team_colors[abbrev]
        primary_color = colors.Color(primary_rgb[0]/255, primary_rgb[1]/255, primary_rgb[2]/255)
        accent_color = colors.Color(accent_rgb[0]/255, accent_rgb[1]/255, accent_rgb[2]/255)
        
        # Primary color background
        table_style.add('BACKGROUND', (2, i), (2, i), primary_color)
        table_style.add('TEXTCOLOR', (2, i), (2, i), 
                       colors.white if sum(primary_rgb) < 400 else colors.black)
        
        # Accent color background
        table_style.add('BACKGROUND', (4, i), (4, i), accent_color)
        table_style.add('TEXTCOLOR', (4, i), (4, i), 
                       colors.white if sum(accent_rgb) < 400 else colors.black)
    
    table.setStyle(table_style)
    story.append(table)
    
    # Build PDF
    doc.build(story)
    print(f"Team colors reference PDF created: {output_file}")
    
    # Open in Preview (macOS)
    import subprocess
    subprocess.run(['open', output_file])
    
    return output_file

if __name__ == '__main__':
    create_team_colors_reference()

