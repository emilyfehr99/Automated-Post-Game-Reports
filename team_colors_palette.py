#!/usr/bin/env python3
"""Generate a comprehensive PDF of all team color palettes"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_team_colors_palette():
    """Create a PDF showing all team primary and accent colors with visual swatches"""
    
    # Register Russo One font if available
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_dir, 'RussoOne-Regular.ttf')
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('RussoOne-Regular', font_path))
    else:
        font_path = "/Users/emilyfehr8/Library/Fonts/RussoOne-Regular.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('RussoOne-Regular', font_path))
    
    output_file = os.path.join(script_dir, 'team_colors_palette.pdf')
    doc = SimpleDocTemplate(output_file, pagesize=letter,
                          rightMargin=36, leftMargin=36,
                          topMargin=36, bottomMargin=36)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    if 'RussoOne-Regular' in pdfmetrics.getRegisteredFontNames():
        title_style = styles['Heading1']
        title_style.fontName = 'RussoOne-Regular'
    else:
        title_style = styles['Heading1']
    
    title = Paragraph("NHL Team Color Palette Reference", title_style)
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    # Team colors - matching what's in team_report_generator.py (updated with all new colors)
    teams = {
        'TBL': ('Tampa Bay Lightning', (0, 40, 104), (255, 184, 28), 'Blue', 'Gold'),
        'NSH': ('Nashville Predators', (255, 184, 28), (4, 30, 66), 'Gold (PANTONE 1235 C)', 'Dark Blue (PANTONE 282 C)'),
        'EDM': ('Edmonton Oilers', (0, 32, 91), (207, 69, 32), 'Royal Blue (PANTONE 281 C)', 'Orange (PANTONE 173 C)'),
        'FLA': ('Florida Panthers', (200, 16, 46), (185, 151, 91), 'Red (PANTONE 186 C)', 'Gold (PANTONE 465 C)'),
        'COL': ('Colorado Avalanche', (111, 38, 61), (35, 97, 146), 'Burgundy (PANTONE 209 C)', 'Steel Blue (PANTONE 647 C)'),
        'DAL': ('Dallas Stars', (0, 132, 61), (1, 1, 1), 'Victory Green (PANTONE 348 C)', 'Black'),
        'BOS': ('Boston Bruins', (255, 184, 28), (0, 0, 0), 'Gold (PANTONE 1235 C)', 'Black'),
        'TOR': ('Toronto Maple Leafs', (0, 32, 91), (128, 128, 128), 'Blue (PANTONE 281 C)', 'Gray'),
        'MTL': ('Montreal Canadiens', (166, 25, 46), (0, 30, 98), 'Red (PANTONE 187 C)', 'Blue (PANTONE 2758 C)'),
        'OTT': ('Ottawa Senators', (200, 16, 46), (185, 151, 91), 'Red (PANTONE 186 C)', 'Gold (PANTONE 465 C)'),
        'BUF': ('Buffalo Sabres', (0, 48, 135), (255, 184, 28), 'Royal Blue (PANTONE 287 C)', 'Gold (PANTONE 1235 C)'),
        'DET': ('Detroit Red Wings', (200, 16, 46), (128, 128, 128), 'Red (PANTONE 186 C)', 'Gray'),
        'CAR': ('Carolina Hurricanes', (200, 16, 46), (0, 0, 0), 'Red (PANTONE 186 C)', 'Black'),
        'WSH': ('Washington Capitals', (200, 16, 46), (4, 30, 66), 'Red (PANTONE 186 C)', 'Navy (PANTONE 282 C)'),
        'PIT': ('Pittsburgh Penguins', (255, 184, 28), (255, 184, 28), 'Gold (PANTONE 1235 C)', 'Gold (PANTONE 1235 C)'),
        'NYR': ('New York Rangers', (0, 50, 160), (200, 16, 46), 'Blue (PANTONE 286 C)', 'Red (PANTONE 186 C)'),
        'NYI': ('New York Islanders', (0, 48, 135), (252, 76, 2), 'Royal Blue (PANTONE 287 C)', 'Orange (PANTONE 1655 C)'),
        'NJD': ('New Jersey Devils', (200, 16, 46), (1, 1, 1), 'Red (PANTONE 186 C)', 'Black'),
        'PHI': ('Philadelphia Flyers', (207, 69, 32), (1, 1, 1), 'Orange (PANTONE 173 C)', 'Black'),
        'CBJ': ('Columbus Blue Jackets', (4, 30, 66), (200, 16, 46), 'Union Blue (PANTONE 282 C)', 'Goal Red (PANTONE 186 C)'),
        'STL': ('St. Louis Blues', (0, 114, 206), (255, 184, 28), 'Blue (PANTONE 285 C)', 'Yellow (PANTONE 1235 C)'),
        'MIN': ('Minnesota Wild', (21, 71, 52), (166, 25, 46), 'Forest Green (PANTONE 3435 C)', 'Iron Range Red (PANTONE 187 C)'),
        'WPG': ('Winnipeg Jets', (4, 30, 66), (166, 25, 46), 'Polar Night Blue (PANTONE 282 C)', 'Red (PANTONE 187 C)'),
        'VGK': ('Vegas Golden Knights', (185, 151, 91), (1, 1, 1), 'Gold (PANTONE 465 C)', 'Black'),
        'SJS': ('San Jose Sharks', (0, 98, 113), (1, 1, 1), 'Deep Pacific Teal (PANTONE 3155 C)', 'Black'),
        'LAK': ('Los Angeles Kings', (1, 1, 1), (162, 170, 173), 'Black', 'Silver (PANTONE 429 C)'),
        'ANA': ('Anaheim Ducks', (207, 69, 32), (185, 151, 91), 'Orange (PANTONE 173 C)', 'Gold (PANTONE 465 C)'),
        'CGY': ('Calgary Flames', (200, 16, 46), (241, 190, 72), 'Red (PANTONE 186 C)', 'Gold (PANTONE 142 C)'),
        'VAN': ('Vancouver Canucks', (0, 132, 61), (0, 32, 91), 'Green (PANTONE 348 C)', 'Blue (PANTONE 281 C)'),
        'SEA': ('Seattle Kraken', (200, 16, 46), (156, 219, 217), 'Red Alert (PANTONE 186 C)', 'Ice Blue (PANTONE 324 C)'),
        'UTA': ('Utah Hockey Club', (1, 1, 1), (105, 179, 231), 'Rock Black', 'Mountain Blue (PANTONE 292 C)'),
        'CHI': ('Chicago Blackhawks', (207, 10, 44), (255, 184, 28), 'Red', 'Gold'),
    }
    
    # Create table data with color swatches
    table_data = []
    header = ['Team', 'Team Name', 'Primary', 'Primary RGB', 'Hex', 'Accent', 'Accent RGB', 'Hex']
    table_data.append(header)
    
    for abbrev in sorted(teams.keys()):
        name, primary_rgb, accent_rgb, primary_name, accent_name = teams[abbrev]
        
        # Convert RGB to hex
        primary_hex = f"#{primary_rgb[0]:02X}{primary_rgb[1]:02X}{primary_rgb[2]:02X}"
        accent_hex = f"#{accent_rgb[0]:02X}{accent_rgb[1]:02X}{accent_rgb[2]:02X}"
        
        table_data.append([
            abbrev,
            name,
            primary_name,
            f"RGB{primary_rgb}",
            primary_hex,
            accent_name,
            f"RGB{accent_rgb}",
            accent_hex
        ])
    
    # Create table
    table = Table(table_data, colWidths=[0.6*inch, 1.8*inch, 1.0*inch, 1.0*inch, 0.7*inch, 1.0*inch, 1.0*inch, 0.7*inch])
    
    # Style the table
    table_style = TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 1), (-1, -1), 4),
        ('RIGHTPADDING', (0, 1), (-1, -1), 4),
    ])
    
    # Add color swatches to primary and accent columns
    for i, abbrev in enumerate(sorted(teams.keys()), start=1):
        _, primary_rgb, accent_rgb, _, _ = teams[abbrev]
        primary_color = colors.Color(primary_rgb[0]/255, primary_rgb[1]/255, primary_rgb[2]/255)
        accent_color = colors.Color(accent_rgb[0]/255, accent_rgb[1]/255, accent_rgb[2]/255)
        
        # Primary color background (column 2 - "Primary" column)
        table_style.add('BACKGROUND', (2, i), (2, i), primary_color)
        table_style.add('TEXTCOLOR', (2, i), (2, i), 
                       colors.white if sum(primary_rgb) < 400 else colors.black)
        
        # Accent color background (column 5 - "Accent" column)
        table_style.add('BACKGROUND', (5, i), (5, i), accent_color)
        table_style.add('TEXTCOLOR', (5, i), (5, i), 
                       colors.white if sum(accent_rgb) < 400 else colors.black)
    
    table.setStyle(table_style)
    story.append(table)
    
    # Build PDF
    doc.build(story)
    print(f"Team colors palette PDF created: {output_file}")
    
    # Open in Preview (macOS)
    import subprocess
    subprocess.run(['open', output_file])
    
    return output_file

if __name__ == '__main__':
    create_team_colors_palette()

