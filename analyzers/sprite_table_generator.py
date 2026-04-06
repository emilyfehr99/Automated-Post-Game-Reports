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
    """Get team's primary color matching pdf_report_generator.py"""
    team_colors = {
        'TBL': colors.Color(0/255, 40/255, 104/255),  # Tampa Bay Lightning Blue
        'NSH': colors.Color(255/255, 184/255, 28/255),  # Nashville Predators Gold
        'EDM': colors.Color(4/255, 30/255, 66/255),  # Edmonton Oilers Blue
        'FLA': colors.Color(200/255, 16/255, 46/255),  # Florida Panthers Red
        'COL': colors.Color(111/255, 38/255, 61/255),  # Colorado Avalanche Burgundy
        'DAL': colors.Color(0/255, 99/255, 65/255),  # Dallas Stars Green
        'BOS': colors.Color(252/255, 181/255, 20/255),  # Boston Bruins Gold
        'TOR': colors.Color(0/255, 32/255, 91/255),  # Toronto Maple Leafs Blue
        'MTL': colors.Color(175/255, 30/255, 45/255),  # Montreal Canadiens Red
        'OTT': colors.Color(200/255, 16/255, 46/255),  # Ottawa Senators Red
        'BUF': colors.Color(0/255, 38/255, 84/255),  # Buffalo Sabres Blue
        'DET': colors.Color(206/255, 17/255, 38/255),  # Detroit Red Wings Red
        'CAR': colors.Color(226/255, 24/255, 54/255),  # Carolina Hurricanes Red
        'WSH': colors.Color(4/255, 30/255, 66/255),  # Washington Capitals Blue
        'PIT': colors.Color(255/255, 184/255, 28/255),  # Pittsburgh Penguins Gold
        'NYR': colors.Color(0/255, 56/255, 168/255),  # New York Rangers Blue
        'NYI': colors.Color(0/255, 83/255, 155/255),  # New York Islanders Blue
        'NJD': colors.Color(206/255, 17/255, 38/255),  # New Jersey Devils Red
        'PHI': colors.Color(247/255, 30/255, 36/255),  # Philadelphia Flyers Orange
        'CBJ': colors.Color(0/255, 38/255, 84/255),  # Columbus Blue Jackets Blue
        'STL': colors.Color(0/255, 47/255, 108/255),  # St. Louis Blues Blue
        'MIN': colors.Color(0/255, 99/255, 65/255),  # Minnesota Wild Green
        'WPG': colors.Color(4/255, 30/255, 66/255),  # Winnipeg Jets Blue
        'ARI': colors.Color(140/255, 38/255, 51/255),  # Arizona Coyotes Red
        'VGK': colors.Color(185/255, 151/255, 91/255),  # Vegas Golden Knights Gold
        'SJS': colors.Color(0/255, 109/255, 117/255),  # San Jose Sharks Teal
        'LAK': colors.Color(162/255, 170/255, 173/255),  # Los Angeles Kings Silver
        'ANA': colors.Color(185/255, 151/255, 91/255),  # Anaheim Ducks Gold
        'CGY': colors.Color(200/255, 16/255, 46/255),  # Calgary Flames Red
        'VAN': colors.Color(0/255, 32/255, 91/255),  # Vancouver Canucks Blue
        'SEA': colors.Color(0/255, 22/255, 40/255),  # Seattle Kraken Navy
        'UTA': colors.Color(105/255, 179/255, 231/255),  # Utah Hockey Club
        'CHI': colors.Color(207/255, 10/255, 44/255)  # Chicago Blackhawks Red
    }
    return team_colors.get(team_abbrev, colors.Color(26/255, 77/255, 107/255))  # Default dark blue

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
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
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
    
    # Calculate each team's total entries (carry + pass, excluding dump)
    away_total_entries = ze_away_counts.get('carry', 0) + ze_away_counts.get('pass', 0)
    home_total_entries = ze_home_counts.get('carry', 0) + ze_home_counts.get('pass', 0)
    
    # Calculate Shares as percentage of each team's entries
    # Away Team: What % of their entries were carries vs passes
    away_carry_share = (ze_away_counts.get('carry', 0) / away_total_entries * 100) if away_total_entries > 0 else 50
    away_pass_share = (ze_away_counts.get('pass', 0) / away_total_entries * 100) if away_total_entries > 0 else 50
    
    # Home Team: What % of their entries were carries vs passes  
    home_carry_share = (ze_home_counts.get('carry', 0) / home_total_entries * 100) if home_total_entries > 0 else 50
    home_pass_share = (ze_home_counts.get('pass', 0) / home_total_entries * 100) if home_total_entries > 0 else 50
    
    col_width = 0.40*inch  # Reduced to fit within page margins
    
    
    def create_split_bar(carry_pct, pass_pct, fill_color_obj, width=400, height=160):
        """
        Create a vertical split bar with Carry on left and Pass on right
        Each side fills from bottom up to its percentage
        Labels at bottom: "Carry" and "Pass"
        """
        # Convert Color object to Hex string if needed
        if hasattr(fill_color_obj, 'red'):
            r = int(fill_color_obj.red * 255)
            g = int(fill_color_obj.green * 255)
            b = int(fill_color_obj.blue * 255)
            fill_color_hex = f'#{r:02X}{g:02X}{b:02X}'
        else:
            fill_color_hex = fill_color_obj
            
        img = PILImage.new('RGB', (width, height), color='#FFFFFF')  # White background
        draw = ImageDraw.Draw(img)
        
        # Try to load a font using relative path for CI compatibility
        try:
            base_dir = os.path.dirname(__file__)
            font_path = os.path.join(base_dir, "assets", "RussoOne-Regular.ttf")
            font = ImageFont.truetype(font_path, 28)
            label_font = ImageFont.truetype(font_path, 24)
        except:
            font = ImageFont.load_default()
            label_font = font
        
        half_width = width // 2
        label_height = 35  # Reserve space at bottom for labels
        bar_height = height - label_height
        
        # LEFT SIDE: Carry
        # Background: Light grey
        draw.rectangle([(0, 0), (half_width - 2, bar_height)], fill='#F0F0F0')
        
        # Fill from bottom up based on percentage
        carry_fill_height = int((carry_pct / 100.0) * bar_height)
        if carry_fill_height > 0:
            fill_y_start = bar_height - carry_fill_height
            draw.rectangle([(0, fill_y_start), (half_width - 2, bar_height)], fill=fill_color_hex)
        
        # Percentage text in center of bar
        carry_text = f"{int(carry_pct)}%"
        try:
            bbox = draw.textbbox((0, 0), carry_text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except:
            text_w, text_h = draw.textsize(carry_text, font=font)
        
        text_x = (half_width - 2 - text_w) // 2
        text_y = (bar_height - text_h) // 2
        
        # Draw with outline for readability
        for offset_x in range(-1, 2):
            for offset_y in range(-1, 2):
                if offset_x == 0 and offset_y == 0: continue
                draw.text((text_x + offset_x, text_y + offset_y), carry_text, font=font, fill='#000000')
        draw.text((text_x, text_y), carry_text, font=font, fill='#FFFFFF')
        
        # RIGHT SIDE: Pass
        # Background: Light grey
        draw.rectangle([(half_width + 2, 0), (width, bar_height)], fill='#F0F0F0')
        
        # Fill from bottom up based on percentage
        pass_fill_height = int((pass_pct / 100.0) * bar_height)
        if pass_fill_height > 0:
            fill_y_start = bar_height - pass_fill_height
            draw.rectangle([(half_width + 2, fill_y_start), (width, bar_height)], fill=fill_color_hex)
        
        # Percentage text in center of bar
        pass_text = f"{int(pass_pct)}%"
        try:
            bbox = draw.textbbox((0, 0), pass_text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except:
            text_w, text_h = draw.textsize(pass_text, font=font)
        
        text_x = half_width + 2 + (half_width - 2 - text_w) // 2
        text_y = (bar_height - text_h) // 2
        
        # Draw with outline
        for offset_x in range(-1, 2):
            for offset_y in range(-1, 2):
                if offset_x == 0 and offset_y == 0: continue
                draw.text((text_x + offset_x, text_y + offset_y), pass_text, font=font, fill='#000000')
        draw.text((text_x, text_y), pass_text, font=font, fill='#FFFFFF')
        
        # LABELS AT BOTTOM
        # "Carry" label on left
        carry_label = "Carry"
        try:
            bbox = draw.textbbox((0, 0), carry_label, font=label_font)
            label_w = bbox[2] - bbox[0]
            label_h = bbox[3] - bbox[1]
        except:
            label_w, label_h = draw.textsize(carry_label, font=label_font)
        
        label_x = (half_width - 2 - label_w) // 2
        label_y = bar_height + (label_height - label_h) // 2
        draw.text((label_x, label_y), carry_label, font=label_font, fill='#000000')
        
        # "Pass" label on right
        pass_label = "Pass"
        try:
            bbox = draw.textbbox((0, 0), pass_label, font=label_font)
            label_w = bbox[2] - bbox[0]
            label_h = bbox[3] - bbox[1]
        except:
            label_w, label_h = draw.textsize(pass_label, font=label_font)
        
        label_x = half_width + 2 + (half_width - 2 - label_w) // 2
        label_y = bar_height + (label_height - label_h) // 2
        draw.text((label_x, label_y), pass_label, font=label_font, fill='#000000')

        
        # Save to temp file and return as ReportLab Image
        temp_path = f"/tmp/split_bar_{fill_color_hex}_{int(carry_pct)}_{int(pass_pct)}.png"
        img.save(temp_path)
        # Increased size significantly for readability
        return RLImage(temp_path, width=0.75*inch, height=0.35*inch)

    
    # Generate split-bar images with Team Colors
    ze_away_bar = create_split_bar(away_carry_share, away_pass_share, away_color)
    ze_home_bar = create_split_bar(home_carry_share, home_pass_share, home_color)
    
    # Table 1: Net-Front Traffic %
    net_front_table = Table([
        ['NET-FRONT TRAFFIC % ON GF'],  # Updated label
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
    # Using specific column widths for the bars (0.75" bar vs 0.4" logo/text)
    entry_table = Table([
        ['ENTRY TYPE SHARE ON GF'],
        [away_logo if away_logo else away_abbrev,
         ze_away_bar,
         home_logo if home_logo else home_abbrev,
         ze_home_bar]
    ], colWidths=[0.3*inch, 0.75*inch, 0.3*inch, 0.75*inch], rowHeights=[0.15*inch, 0.38*inch])
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
    spacer_width = 0.15*inch  # Space between tables
    horizontal_row = Table(
        [[net_front_table, Spacer(spacer_width, 1), shot_dist_table, Spacer(spacer_width, 1), entry_table, Spacer(spacer_width, 1), pass_table]], 
        colWidths=[col_width*4, spacer_width, col_width*4, spacer_width, 2.1*inch, spacer_width, col_width*4]
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
    
    # Note removed per user request
    # note_text = "* Four tables above analyze goals for (GF) only"
    # flowables.append(Spacer(1, 4))
    # flowables.append(Paragraph(note_text, note_style))
    
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
