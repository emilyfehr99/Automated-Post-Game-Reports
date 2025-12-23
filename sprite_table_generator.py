"""
Sprite Goal Analysis - ReportLab Table Generator
Creates comparison tables matching the existing report style
"""

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Image as RLImage,  Spacer
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
import os
import requests
from io import BytesIO
from PIL import Image as PILImage, ImageDraw, ImageFont

def register_russo_font():
    """Register RussoOne font for use in tables"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_paths = [
            os.path.join(script_dir, 'assets', 'RussoOne-Regular.ttf'),
            os.path.join(script_dir, 'RussoOne-Regular.ttf'),
            "/Users/emilyfehr8/Library/Fonts/RussoOne-Regular.ttf"
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('RussoOne-Regular', font_path))
                registerFontFamily(
                    'RussoOne',
                    normal='RussoOne-Regular',
                    bold='RussoOne-Regular',
                    italic='RussoOne-Regular',
                    boldItalic='RussoOne-Regular'
                )
                return True
    except:
        pass
    return False

def get_team_color(team_abbrev):
    """Get team's primary color"""
    team_colors = {
        'ANA': '#F47A38', 'BOS': '#FFB81C', 'BUF': '#002654', 'CGY': '#C8102E',
        'CAR': '#CC0000', 'CHI': '#CF0A2C', 'COL': '#6F263D', 'CBJ': '#002654',
        'DAL': '#006847', 'DET': '#CE1126', 'EDM': '#FF4C00', 'FLA': '#041E42',
        'LAK': '#111111', 'MIN': '#154734', 'MTL': '#AF1E2D', 'NSH': '#FFB81C',
        'NJD': '#CE1126', 'NYI': '#00539B', 'NYR': '#0038A8', 'OTT': '#C52032',
        'PHI': '#F74902', 'PIT': '#000000', 'SJS': '#006D75', 'SEA': '#001628',
        'STL': '#002F87', 'TBL': '#002868', 'TOR': '#00205B', 'VAN': '#00205B',
        'VGK': '#B4975A', 'WSH': '#041E42', 'WPG': '#041E42', 'ARI': '#8C2633'
    }
    return team_colors.get(team_abbrev, '#1a4d6b')  # Default dark blue

def get_team_logo(team_abbrev, size=40):
    """Download and resize team logo"""
    logo_map = {
        'TBL': 'tb', 'NSH': 'nsh', 'EDM': 'edm', 'FLA': 'fla',
        'COL': 'col', 'DAL': 'dal', 'BOS': 'bos', 'TOR': 'tor',
        'MTL': 'mtl', 'OTT': 'ott', 'BUF': 'buf', 'DET': 'det',
        'CAR': 'car', 'WSH': 'wsh', 'PIT': 'pit', 'NYR': 'nyr',
        'NYI': 'nyi', 'NJD': 'nj', 'PHI': 'phi', 'CBJ': 'cbj',
        'STL': 'stl', 'MIN': 'min', 'WPG': 'wpg', 'ARI': 'ari',
        'VGK': 'vgk', 'SJS': 'sj', 'LAK': 'la', 'ANA': 'ana',
        'CGY': 'cgy', 'VAN': 'van', 'SEA': 'sea', 'CHI': 'chi'
    }
    
    logo_abbrev = logo_map.get(team_abbrev, team_abbrev.lower())
    logo_url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{logo_abbrev}.png"
    
    try:
        response = requests.get(logo_url, timeout=5)
        if response.status_code == 200:
            img = PILImage.open(BytesIO(response.content))
            img = img.resize((100, 100), PILImage.Resampling.LANCZOS)
            
            # Save to temp file
            temp_path = f"/tmp/team_logo_{team_abbrev}.png"
            img.save(temp_path)
            return RLImage(temp_path, width=size, height=size)
    except:
        pass
    
    return None

def create_sprite_analysis_tables(sprite_data):
    """
    Create 4 comparison tables for sprite analysis
    matching the existing report style
    """
    # Register RussoOne font
    font_registered = register_russo_font()
    font_name = 'RussoOne-Regular' if font_registered else 'Helvetica-Bold'
    
    if not sprite_data or 'stats' not in sprite_data:
        return []
    
    away_id = sprite_data['away_team_id']
    home_id = sprite_data['home_team_id']
    
    away_stats = sprite_data['stats'].get(away_id, {})
    home_stats = sprite_data['stats'].get(home_id, {})
    
    away_abbrev = away_stats.get('abbrev', 'AWAY')
    home_abbrev = home_stats.get('abbrev', 'HOME')
    
    # Get team colors
    header_color = get_team_color(home_abbrev)
    home_color = get_team_color(home_abbrev)
    away_color = get_team_color(away_abbrev)
    
    # Get team logos
    away_logo = get_team_logo(away_abbrev, size=12)
    home_logo = get_team_logo(home_abbrev, size=12)
    
    flowables = []
    
    # Define table style
    table_style = TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_color)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Ensure header title is vertically centered
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        # Explicitly center data
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('VALIGN', (1, 0), (1, -1), 'MIDDLE'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('VALIGN', (3, 0), (3, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 6),  # Reduced from 7 for better fit
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 7),  # Reduced from 8 for better fit
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('INNERGRID', (0, 1), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
        ('TOPPADDING', (0, 0), (-1, 0), 0),
        ('LEADING', (0, 0), (-1, 0), 7),  # Slightly more than font size 6
        ('LEFTPADDING', (0, 0), (-1, 0), 0),
        ('RIGHTPADDING', (0, 0), (-1, 0), 0),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 0),
        ('TOPPADDING', (0, 1), (-1, -1), 0),
        ('SPAN', (0, 0), (-1, 0)),
    ])
    
    # Define text colors
    green_color = colors.HexColor('#008000')  # Dark Green
    red_color = colors.HexColor('#FF0000')    # Bright Red
    black_color = colors.black
    
    def get_metric_color(val1, val2, lower_is_better=False):
        """Return (color1, color2) tuple based on comparison"""
        if val1 == val2: return black_color, black_color
        try:
            v1_float = float(val1)
            v2_float = float(val2)
        except: return black_color, black_color
        
        if lower_is_better:
            return (green_color, red_color) if v1_float < v2_float else (red_color, green_color)
        else:
            return (green_color, red_color) if v1_float > v2_float else (red_color, green_color)

    # Calculate colors
    nf_away = away_stats.get('net_front_traffic_pct', 0)
    nf_home = home_stats.get('net_front_traffic_pct', 0)
    c_nf_away, c_nf_home = get_metric_color(nf_away, nf_home, lower_is_better=False)
    
    sd_away = away_stats.get('avg_shot_dist', 0)
    sd_home = home_stats.get('avg_shot_dist', 0)
    c_sd_away, c_sd_home = get_metric_color(sd_away, sd_home, lower_is_better=True)
    
    pass_away = away_stats.get('avg_passes', 0)
    pass_home = home_stats.get('avg_passes', 0)
    c_pass_away, c_pass_home = get_metric_color(pass_away, pass_home, lower_is_better=False)
    
    # Zone Entry - Split Bar (Carry vs Pass Share)
    ze_away_counts = away_stats.get('entry_counts', {'carry':0, 'pass':0, 'dump':0})
    ze_home_counts = home_stats.get('entry_counts', {'carry':0, 'pass':0, 'dump':0})
    
    # Calculate Total Game Counts for Share Calculation
    total_carries = ze_away_counts.get('carry', 0) + ze_home_counts.get('carry', 0)
    total_passes = ze_away_counts.get('pass', 0) + ze_home_counts.get('pass', 0)
    
    # Calculate Shares (avoid div by zero)
    # Away Share
    away_carry_share = (ze_away_counts.get('carry', 0) / total_carries * 100) if total_carries > 0 else 0
    away_pass_share = (ze_away_counts.get('pass', 0) / total_passes * 100) if total_passes > 0 else 0
    
    # Home Share
    home_carry_share = (ze_home_counts.get('carry', 0) / total_carries * 100) if total_carries > 0 else 0
    home_pass_share = (ze_home_counts.get('pass', 0) / total_passes * 100) if total_passes > 0 else 0
    
    col_width = 0.40*inch  # Reduced to fit within page margins
    
    def create_split_bar(top_pct, bottom_pct, fill_color_hex, width=400, height=160):
        """
        Create a split cell with two horizontal bars using team color
        Top Half: Carry Share
        Bottom Half: Pass Share
        Fills entire cell height (height=40 -> 0.20 inch)
        Adds text labels "CARRY" and "PASS"
        """
        img = PILImage.new('RGB', (width, height), color='#FFFFFF') # White background
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, or use default
        try:
            # Use specific path if possible or default
            # Scale font up for high-res image (was 9 -> now ~36)
            font = ImageFont.truetype("/Users/emilyfehr8/.gemini/antigravity/scratch/Automated-Post-Game-Reports/assets/RussoOne-Regular.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        half_height = height // 2
        
        # 1. Top Bar (Carry)
        # Background: Very light grey
        top_bg = PILImage.new('RGB', (width, half_height), color='#F0F0F0') 
        img.paste(top_bg, (0, 0))
        
        # Top Fill (Team Color)
        top_fill_w = int((top_pct / 100.0) * width)
        if top_fill_w > 0:
            top_fill = PILImage.new('RGB', (top_fill_w, half_height), color=fill_color_hex) 
            img.paste(top_fill, (0, 0))
            
        # Label "CARRY" with percentage - ensure proper formatting
        if top_pct is None or top_pct == 0:
            text = "CARRY 0%"
        else:
            text = f"CARRY {int(top_pct)}%"
        
        # Calculate text position to center
        try:
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            text_w = right - left
            text_h = bottom - top
        except:
            text_w, text_h = draw.textsize(text, font=font)
            
        text_x = (width - text_w) / 2
        text_y = (half_height - text_h) / 2
        
        # Draw outline/shadow for readability
        outline_color = '#000000'
        # Thicker outline for bigger text
        for offset in range(-2, 3):
             for offset_y in range(-2, 3):
                 if offset == 0 and offset_y == 0: continue
                 draw.text((text_x + offset, text_y + offset_y), text, font=font, fill=outline_color)
                 
        draw.text((text_x, text_y), text, font=font, fill='#FFFFFF')

        # 2. Bottom Bar (Pass)
        # Background
        bot_bg = PILImage.new('RGB', (width, half_height), color='#F0F0F0') 
        img.paste(bot_bg, (0, half_height))
        
        # Bottom Fill (Team Color)
        bot_fill_w = int((bottom_pct / 100.0) * width)
        if bot_fill_w > 0:
            bot_fill = PILImage.new('RGB', (bot_fill_w, half_height), color=fill_color_hex)
            img.paste(bot_fill, (0, half_height))
            
        # Label "PASS" with percentage - ensure proper formatting
        if bottom_pct is None or bottom_pct == 0:
            text = "PASS 0%"
        else:
            text = f"PASS {int(bottom_pct)}%"
        try:
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            text_w = right - left
            text_h = bottom - top
        except:
            text_w, text_h = draw.textsize(text, font=font)
            
        text_x = (width - text_w) / 2
        # Center in bottom half: start y = half_height + (half_height - text_h)/2
        text_y = half_height + (half_height - text_h) / 2
        
        for offset in range(-2, 3):
             for offset_y in range(-2, 3):
                 if offset == 0 and offset_y == 0: continue
                 draw.text((text_x + offset, text_y + offset_y), text, font=font, fill=outline_color)
                 
        draw.text((text_x, text_y), text, font=font, fill='#FFFFFF')

        # Add thin separator
        separator = PILImage.new('RGB', (width, 2), color='#FFFFFF') # Thicker separator for hi-res
        img.paste(separator, (0, half_height))

        # Save
        temp_path = f"/tmp/split_bar_{fill_color_hex}_{top_pct}_{bottom_pct}.png"
        img.save(temp_path)
        return RLImage(temp_path, width=0.35*inch, height=0.20*inch)
    
    # Generate split-bar images with Team Colors
    ze_away_bar = create_split_bar(away_carry_share, away_pass_share, away_color)
    ze_home_bar = create_split_bar(home_carry_share, home_pass_share, home_color)
    
    # Table 1: Net-Front Traffic %
    net_front_table = Table([
        ['NET-FRONT TRAFFIC %'],  # Updated label
        [away_logo if away_logo else away_abbrev, 
         f"{nf_away}%",  # Display as percentage
         home_logo if home_logo else home_abbrev,
         f"{nf_home}%"]  # Display as percentage
    ], colWidths=[col_width]*4, rowHeights=[0.15*inch, 0.22*inch])  # Increased header height for centering
    net_front_table.setStyle(table_style)
    net_front_table.setStyle(TableStyle([
        ('TEXTCOLOR', (1, 1), (1, 1), c_nf_away),
        ('TEXTCOLOR', (3, 1), (3, 1), c_nf_home),
    ]))
    
    # Table 2: Shot Distance  
    shot_dist_table = Table([
        ['AVG GOAL DISTANCE'],
        [away_logo if away_logo else away_abbrev,
         f"{int(sd_away)} ft",
         home_logo if home_logo else home_abbrev,
         f"{int(sd_home)} ft"]
    ], colWidths=[col_width]*4, rowHeights=[0.15*inch, 0.22*inch])  # Increased header height for centering
    shot_dist_table.setStyle(table_style)
    shot_dist_table.setStyle(TableStyle([
        ('TEXTCOLOR', (1, 1), (1, 1), c_sd_away),
        ('TEXTCOLOR', (3, 1), (3, 1), c_sd_home),
    ]))
    
    # Table 3: Zone Entry (Split Visual)
    entry_table = Table([
        ['ENTRY TYPE SHARE'],
        [away_logo if away_logo else away_abbrev,
         ze_away_bar,
         home_logo if home_logo else home_abbrev,
         ze_home_bar]
    ], colWidths=[col_width]*4, rowHeights=[0.15*inch, 0.22*inch])  # Increased header height for centering
    entry_table.setStyle(table_style)
    
    # Table 4: Passes
    pass_table = Table([
        ['PASSES PER GOAL'],
        [away_logo if away_logo else away_abbrev,
         f"{pass_away}",
         home_logo if home_logo else home_abbrev,
         f"{pass_home}"]
    ], colWidths=[col_width]*4, rowHeights=[0.15*inch, 0.22*inch])  # Increased header height for centering
    pass_table.setStyle(table_style)
    pass_table.setStyle(TableStyle([
        ('TEXTCOLOR', (1, 1), (1, 1), c_pass_away),
        ('TEXTCOLOR', (3, 1), (3, 1), c_pass_home),
    ]))
    
    # Add tables with spacing between them
    from reportlab.platypus import Spacer
    
    # Create a container table with spacers between each table
    spacer_width = 0.2*inch  # Space between tables
    horizontal_row = Table(
        [[net_front_table, Spacer(spacer_width, 1), shot_dist_table, Spacer(spacer_width, 1), entry_table, Spacer(spacer_width, 1), pass_table]], 
        colWidths=[col_width*4, spacer_width, col_width*4, spacer_width, col_width*4, spacer_width, col_width*4]
    )
    horizontal_row.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    flowables.append(horizontal_row)
    
    # Add explanatory note
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    
    note_style = ParagraphStyle(
        'NoteStyle',
        fontName='RussoOne-Regular',
        fontSize=6,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=0,
        spaceBefore=4
    )
    
    note_text = "* Four tables above analyze goals for (GF) only"
    flowables.append(Spacer(1, 4))
    flowables.append(Paragraph(note_text, note_style))
    
    return flowables

if __name__ == "__main__":
    from sprite_goal_analyzer import SpriteGoalAnalyzer
    from reportlab.platypus import SimpleDocTemplate
    
    analyzer = SpriteGoalAnalyzer()
    data = analyzer.analyze_game_goals_by_team('2025020536')
    
    if data:
        output_path = "/Users/emilyfehr8/Desktop/sprite_tables_test.pdf"
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        tables = create_sprite_analysis_tables(data)
        story.extend(tables)
        doc.build(story)
        print(f"✅ Test PDF saved: {output_path}")
    else:
        print("❌ No data available")
