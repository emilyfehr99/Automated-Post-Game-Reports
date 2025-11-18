#!/usr/bin/env python3
"""
MLB Scouting Report PDF Generator
Creates professional single-page scouting reports matching NHL report format exactly
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus.flowables import Flowable
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
from datetime import datetime
import os

class BackgroundPageTemplate(PageTemplate):
    """Custom page template that draws background on every page"""
    def __init__(self, id, frames, background_path, onPage=None, onPageEnd=None):
        self.background_path = background_path
        # Provide a default onPageEnd function if none provided
        if onPageEnd is None:
            onPageEnd = lambda canvas, doc: None
        super().__init__(id, frames, onPage=self._onPage, onPageEnd=onPageEnd)
        
    def _onPage(self, canvas, doc):
        """Draw background on each page"""
        if os.path.exists(self.background_path):
            try:
                from PIL import Image as PILImage
                
                # Get page dimensions
                page_width = canvas._pagesize[0]
                page_height = canvas._pagesize[1]
                print(f"DEBUG: Drawing background on page with size {page_width}x{page_height}")
                
                # Convert PNG to JPEG to handle transparency
                pil_img = PILImage.open(self.background_path)
                if pil_img.mode == 'RGBA':
                    # Create white background
                    white_bg = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                    white_bg.paste(pil_img, mask=pil_img.split()[-1])
                    pil_img = white_bg
                
                # Resize to page dimensions
                pil_img = pil_img.resize((int(page_width), int(page_height)), PILImage.Resampling.LANCZOS)
                
                # Save temporary JPEG
                temp_path = f"temp_background_{id(self)}.jpg"
                pil_img.save(temp_path, 'JPEG', quality=85)
                
                # Draw background
                canvas.drawImage(temp_path, 0, 0, width=page_width, height=page_height)
                
                # Clean up temporary file
                try:
                    os.remove(temp_path)
                except:
                    pass
                    
                print(f"✅ Background drawn successfully")
                
            except Exception as e:
                print(f"Error drawing background: {e}")
                # Fallback: try direct image drawing
                try:
                    canvas.drawImage(self.background_path, 0, 0, width=page_width, height=page_height)
                    print(f"✅ Background drawn with fallback method")
                except Exception as e2:
                    print(f"Fallback background drawing failed: {e2}")
        else:
            print(f"Background image not found: {self.background_path}")

class HeaderFlowable(Flowable):
    """Custom flowable to draw header image at absolute top-left corner"""
    def __init__(self, image_path, width, height):
        self.image_path = image_path
        self.width = width
        self.height = height
        self.drawWidth = width
        self.drawHeight = height
        Flowable.__init__(self)
    
    def draw(self):
        """Draw the header image at absolute position (0,0)"""
        if os.path.exists(self.image_path):
            print(f"DEBUG: Drawing header image from {self.image_path}")
            from reportlab.lib.utils import ImageReader
            img = ImageReader(self.image_path)
            # Draw image at absolute top-left corner (0, 0)
            self.canv.drawImage(img, 0, 0, width=self.width, height=self.height)
            print(f"DEBUG: Header image drawn at (0,0) with size {self.width}x{self.height}")
        else:
            print(f"DEBUG: Header image not found at {self.image_path}")

class MLBScoutingReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.register_fonts()
        self._setup_custom_styles()
    
    def register_fonts(self):
        """Register custom fonts with ReportLab"""
        import os
        
        # Try multiple possible font locations
        font_paths = [
            'RussoOne-Regular.ttf',  # Current directory
            'nhl_postgame_reports/RussoOne-Regular.ttf',  # Subdirectory
            '/Users/emilyfehr8/Library/Fonts/RussoOne-Regular.ttf',  # Local Mac path
        ]
        
        font_registered = False
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('RussoOne-Regular', font_path))
                    font_registered = True
                    print(f"Successfully registered font from: {font_path}")
                    break
            except Exception as e:
                print(f"Failed to register font from {font_path}: {e}")
                continue
        
        if not font_registered:
            print("Using default system fonts")
            self.use_default_fonts = True
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkred,
            borderWidth=1,
            borderColor=colors.grey,
            borderPadding=5
        ))
        
        # Subsection style
        self.styles.add(ParagraphStyle(
            name='Subsection',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.darkgreen
        ))
    
    def create_header_image(self, player_name, team_name):
        """Create the header image for the scouting report"""
        try:
            # Use the NHL header image as base
            header_paths = [
                'Header.jpg',  # Current directory
                'nhl_postgame_reports/Header.jpg',  # Subdirectory
                '/Users/emilyfehr8/CascadeProjects/nhl_postgame_reports/Header.jpg'  # Local Mac path
            ]
            
            header_path = None
            for path in header_paths:
                if os.path.exists(path):
                    header_path = path
                    print(f"Found header image at: {path}")
                    break
            
            if header_path and os.path.exists(header_path):
                print(f"Creating header image with base: {header_path}")
                # Create a custom header with player name overlaid
                from PIL import Image, ImageDraw, ImageFont
                
                # Load the base header image
                base_img = Image.open(header_path)
                print(f"Base image size: {base_img.size}")
                draw = ImageDraw.Draw(base_img)
                
                # Try to use a modern font
                try:
                    title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
                    subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
                    print("Using system fonts")
                except:
                    title_font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()
                    print("Using default fonts")
                
                # Add title text
                title_text = f"Scouting Report: {player_name}"
                title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (base_img.width - title_width) // 2
                title_y = 20
                
                print(f"Drawing title: {title_text} at ({title_x}, {title_y})")
                
                # Draw title with white text and black outline
                draw.text((title_x-1, title_y-1), title_text, font=title_font, fill=(0, 0, 0))  # Black outline
                draw.text((title_x+1, title_y+1), title_text, font=title_font, fill=(0, 0, 0))  # Black outline
                draw.text((title_x, title_y), title_text, font=title_font, fill=(255, 255, 255))  # White text
                
                # Add subtitle
                subtitle_text = f"{team_name} • 2025 Post Season"
                subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
                subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                subtitle_x = (base_img.width - subtitle_width) // 2
                # Move subtitle down by 0.5 cm (≈19 pixels at 72 DPI)
                subtitle_y = title_y + 50 + 19
                
                print(f"Drawing subtitle: {subtitle_text} at ({subtitle_x}, {subtitle_y})")
                
                # Draw subtitle
                draw.text((subtitle_x-1, subtitle_y-1), subtitle_text, font=subtitle_font, fill=(0, 0, 0))  # Black outline
                draw.text((subtitle_x+1, subtitle_y+1), subtitle_text, font=subtitle_font, fill=(0, 0, 0))  # Black outline
                draw.text((subtitle_x, subtitle_y), subtitle_text, font=subtitle_font, fill=(255, 255, 255))  # White text
                
                # Save the modified header
                temp_header_path = f"temp_header_{player_name.replace(' ', '_')}.jpg"
                base_img.save(temp_header_path)
                print(f"Saved header image to: {temp_header_path}")
                
                # Set temp_path for cleanup - use proper dimensions for PDF
                header_flowable = HeaderFlowable(temp_header_path, 612, 120)  # PDF dimensions, not image dimensions
                header_flowable.temp_path = temp_header_path
                
                return header_flowable
            else:
                print(f"No header image found in paths: {header_paths}")
                return None
            
        except Exception as e:
            print(f"Error creating header image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_header_image_file(self, player_name, team_name):
        """Create header image file and return the file path"""
        try:
            # Use the NHL header image as base
            header_paths = [
                'Header.jpg',  # Current directory
                'nhl_postgame_reports/Header.jpg',  # Subdirectory
                '/Users/emilyfehr8/CascadeProjects/nhl_postgame_reports/Header.jpg'  # Local Mac path
            ]
            
            header_path = None
            for path in header_paths:
                if os.path.exists(path):
                    header_path = path
                    print(f"Found header image at: {path}")
                    break
            
            if header_path and os.path.exists(header_path):
                print(f"Creating header image with base: {header_path}")
                # Create a custom header with player name overlaid
                from PIL import Image, ImageDraw, ImageFont
                
                # Load the base header image
                base_img = Image.open(header_path)
                print(f"Base image size: {base_img.size}")
                draw = ImageDraw.Draw(base_img)
                
                # Try to use Russo One font
                try:
                    title_font = ImageFont.truetype("RussoOne-Regular.ttf", 70)  # Increased to 70pt
                    subtitle_font = ImageFont.truetype("RussoOne-Regular.ttf", 50)  # Increased to 50pt
                    print("Using Russo One font")
                except:
                    try:
                        title_font = ImageFont.truetype("/Users/emilyfehr8/CascadeProjects/RussoOne-Regular.ttf", 70)
                        subtitle_font = ImageFont.truetype("/Users/emilyfehr8/CascadeProjects/RussoOne-Regular.ttf", 50)
                        print("Using Russo One font from project directory")
                    except:
                        title_font = ImageFont.load_default()
                        subtitle_font = ImageFont.load_default()
                        print("Using default fonts")
                
                # Add title text - centered vertically in header
                title_text = f"Scouting Report: {player_name}"
                title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (base_img.width - title_width) // 2
                title_y = (base_img.height - 50) // 2  # Center vertically in header
                
                print(f"Drawing title: {title_text} at ({title_x}, {title_y})")
                
                # Draw title text with thick black outline and white text (no background)
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        if dx != 0 or dy != 0:
                            draw.text((title_x + dx, title_y + dy), title_text, font=title_font, fill=(0, 0, 0))  # Black outline
                draw.text((title_x, title_y), title_text, font=title_font, fill=(255, 255, 255))  # White text
                
                # Add subtitle
                subtitle_text = f"{team_name} • 2025 Post Season"
                subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
                subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                subtitle_x = (base_img.width - subtitle_width) // 2
                # Move subtitle down by 0.5 cm (≈19 pixels at 72 DPI)
                subtitle_y = title_y + 50 + 19
                
                print(f"Drawing subtitle: {subtitle_text} at ({subtitle_x}, {subtitle_y})")
                
                # Draw subtitle text with thick black outline and white text (no background)
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if dx != 0 or dy != 0:
                            draw.text((subtitle_x + dx, subtitle_y + dy), subtitle_text, font=subtitle_font, fill=(0, 0, 0))  # Black outline
                draw.text((subtitle_x, subtitle_y), subtitle_text, font=subtitle_font, fill=(255, 255, 255))  # White text
                
                # Add team logo to the right of the title
                try:
                    # Get team logo from TheSportsDB API
                    team_logo_url = self.get_team_logo_url(team_name)
                    
                    if team_logo_url:
                        # Add team logo to the right side (250x250 pixels, moved 4.5cm inward total)
                        # 4.5cm ≈ 162 pixels at 72 DPI, so move left by 162 pixels
                        logo_x = base_img.width - 200 - 162  # Position on right side, moved 4.5cm inward
                        logo_y = title_y - 20
                        if self.add_image_to_header(base_img, team_logo_url, logo_x, logo_y, 250, 250):  # 250x250 pixels
                            print(f"✅ Added team logo at ({logo_x}, {logo_y})")
                        else:
                            print(f"❌ Failed to add team logo, using custom fallback")
                            # Add custom team logo as fallback
                            self.create_custom_team_logo(draw, team_name, logo_x, logo_y, subtitle_font)
                    else:
                        print(f"❌ No team logo URL found, using custom fallback")
                        # Add custom team logo as fallback
                        logo_x = base_img.width - 200 - 162  # Position on right side, moved 4.5cm inward
                        logo_y = title_y - 20
                        self.create_custom_team_logo(draw, team_name, logo_x, logo_y, subtitle_font)
                        
                except Exception as e:
                    print(f"Error adding team logo: {e}")
                    # Continue without logo if it fails
                
                # Save the modified header
                temp_header_path = f"temp_header_{player_name.replace(' ', '_')}.jpg"
                base_img.save(temp_header_path)
                print(f"Saved header image to: {temp_header_path}")
                
                return temp_header_path
            else:
                print(f"No header image found in paths: {header_paths}")
                return None
            
        except Exception as e:
            print(f"Error creating header image file: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_team_logo_url(self, team_name):
        """Get team logo URL from TheSportsDB API"""
        try:
            import requests
            
            # Team name to TheSportsDB team ID mapping (corrected IDs)
            team_id_mapping = {
                'Los Angeles Dodgers': 135272,
                'Toronto Blue Jays': 135265,
                'New York Yankees': 135260,
                'Boston Red Sox': 135252,
                'Houston Astros': 135256,
                'Atlanta Braves': 135268,
                'San Diego Padres': 135278,
                'Philadelphia Phillies': 135276,
                'Tampa Bay Rays': 135263,
                'Cleveland Guardians': 135254,
                'Milwaukee Brewers': 135274,
                'Miami Marlins': 135273,
                'Arizona Diamondbacks': 135267,
                'Cincinnati Reds': 135270,
                'Chicago Cubs': 135269,
                'St. Louis Cardinals': 135280,
                'Pittsburgh Pirates': 135277,
                'Washington Nationals': 135281,
                'New York Mets': 135275,
                'San Francisco Giants': 135279,
                'Colorado Rockies': 135271,
                'Los Angeles Angels': 135258,
                'Seattle Mariners': 135262,
                'Oakland Athletics': 135261,
                'Texas Rangers': 135264,
                'Kansas City Royals': 135257,
                'Minnesota Twins': 135259,
                'Chicago White Sox': 135253,
                'Detroit Tigers': 135255,
                'Baltimore Orioles': 135251
            }
            
            team_id = team_id_mapping.get(team_name, 135272)  # Default to Dodgers
            
            # Use TheSportsDB API to search by team name instead of ID
            api_url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team_name.replace(' ', '%20')}"
            print(f"Fetching team logo from TheSportsDB: {api_url}")
            
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'teams' in data and len(data['teams']) > 0:
                    team_data = data['teams'][0]
                    # Verify this is the correct team (MLB Baseball)
                    if team_data.get('strSport') == 'Baseball' and team_data.get('strLeague') == 'MLB':
                        logo_url = team_data.get('strTeamBadge')
                        if logo_url:
                            print(f"✅ Found team logo from TheSportsDB: {logo_url}")
                            return logo_url
                        else:
                            print(f"❌ No logo URL found in team data")
                            # Try alternative logo field names
                            alt_logo_fields = ['strTeamLogo', 'strBadge', 'strLogo', 'logo']
                            for field in alt_logo_fields:
                                alt_logo = team_data.get(field)
                                if alt_logo:
                                    print(f"✅ Found team logo in {field}: {alt_logo}")
                                    return alt_logo
                    else:
                        print(f"❌ Wrong sport/league: {team_data.get('strSport')}/{team_data.get('strLeague')}")
                else:
                    print(f"❌ No team data found")
            else:
                print(f"❌ TheSportsDB API request failed: {response.status_code}")
            
            return None
            
        except Exception as e:
            print(f"Error getting team logo from TheSportsDB: {e}")
            return None
    
    def get_team_colors(self, team_name):
        """Get team colors for styling"""
        team_colors = {
            'Los Angeles Dodgers': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'Toronto Blue Jays': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'New York Yankees': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'Boston Red Sox': {'primary': colors.darkred, 'secondary': colors.lightcoral},
            'Houston Astros': {'primary': colors.darkorange, 'secondary': colors.lightyellow},
            'Atlanta Braves': {'primary': colors.darkred, 'secondary': colors.lightcoral},
            'Philadelphia Phillies': {'primary': colors.darkred, 'secondary': colors.lightcoral},
            'San Diego Padres': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'San Francisco Giants': {'primary': colors.darkorange, 'secondary': colors.lightyellow},
            'Arizona Diamondbacks': {'primary': colors.darkred, 'secondary': colors.lightcoral},
            'Colorado Rockies': {'primary': colors.darkred, 'secondary': colors.lightcoral},
            'Miami Marlins': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'New York Mets': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'Washington Nationals': {'primary': colors.darkred, 'secondary': colors.lightcoral},
            'Chicago Cubs': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'Milwaukee Brewers': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'Pittsburgh Pirates': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'St. Louis Cardinals': {'primary': colors.darkred, 'secondary': colors.lightcoral},
            'Cincinnati Reds': {'primary': colors.darkred, 'secondary': colors.lightcoral},
            'Cleveland Guardians': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'Detroit Tigers': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'Kansas City Royals': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'Minnesota Twins': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'Chicago White Sox': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'Tampa Bay Rays': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'Baltimore Orioles': {'primary': colors.darkorange, 'secondary': colors.lightyellow},
            'Seattle Mariners': {'primary': colors.darkblue, 'secondary': colors.lightblue},
            'Oakland Athletics': {'primary': colors.darkgreen, 'secondary': colors.lightgreen},
            'Los Angeles Angels': {'primary': colors.darkred, 'secondary': colors.lightcoral},
            'Texas Rangers': {'primary': colors.darkred, 'secondary': colors.lightcoral}
        }
        
        return team_colors.get(team_name, {'primary': colors.darkblue, 'secondary': colors.lightblue})
    
    def add_team_text_fallback(self, draw, team_name, x, y, font):
        """Add team name as text fallback when logo fails"""
        try:
            # Get team abbreviation for shorter text
            team_abbrev = {
                'Los Angeles Dodgers': 'LAD',
                'Toronto Blue Jays': 'TOR',
                'New York Yankees': 'NYY',
                'Boston Red Sox': 'BOS',
                'Houston Astros': 'HOU',
                'Atlanta Braves': 'ATL',
                'San Diego Padres': 'SD',
                'Philadelphia Phillies': 'PHI',
                'Tampa Bay Rays': 'TB',
                'Cleveland Guardians': 'CLE',
                'Milwaukee Brewers': 'MIL',
                'Miami Marlins': 'MIA',
                'Arizona Diamondbacks': 'ARI',
                'Cincinnati Reds': 'CIN',
                'Chicago Cubs': 'CHC',
                'St. Louis Cardinals': 'STL',
                'Pittsburgh Pirates': 'PIT',
                'Washington Nationals': 'WSH',
                'New York Mets': 'NYM',
                'San Francisco Giants': 'SF',
                'Colorado Rockies': 'COL',
                'Los Angeles Angels': 'LAA',
                'Seattle Mariners': 'SEA',
                'Oakland Athletics': 'OAK',
                'Texas Rangers': 'TEX',
                'Kansas City Royals': 'KC',
                'Minnesota Twins': 'MIN',
                'Chicago White Sox': 'CWS',
                'Detroit Tigers': 'DET',
                'Baltimore Orioles': 'BAL'
            }
            
            team_text = team_abbrev.get(team_name, team_name.split()[-1])  # Use abbreviation or last word
            
            # Center the text in the logo area
            text_bbox = draw.textbbox((0, 0), team_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = x + (80 - text_width) // 2
            text_y = y + 30
            
            # Draw team text with outline
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, text_y + dy), team_text, font=font, fill=(0, 0, 0))  # Black outline
            draw.text((text_x, text_y), team_text, font=font, fill=(255, 255, 255))  # White text
            
            print(f"✅ Added team text fallback: {team_text}")
            
        except Exception as e:
            print(f"Error adding team text fallback: {e}")
    
    def create_custom_team_logo(self, draw, team_name, x, y, font):
        """Create a custom team logo using text and shapes"""
        try:
            # Get team abbreviation and colors
            team_info = {
                'Los Angeles Dodgers': {'abbrev': 'LAD', 'color': (0, 90, 156)},  # Dodger Blue
                'Toronto Blue Jays': {'abbrev': 'TOR', 'color': (0, 51, 160)},    # Blue
                'New York Yankees': {'abbrev': 'NYY', 'color': (12, 35, 64)},    # Navy
                'Boston Red Sox': {'abbrev': 'BOS', 'color': (189, 48, 57)},     # Red
                'Houston Astros': {'abbrev': 'HOU', 'color': (0, 45, 98)},       # Navy
                'Atlanta Braves': {'abbrev': 'ATL', 'color': (206, 17, 65)},     # Red
                'San Diego Padres': {'abbrev': 'SD', 'color': (0, 45, 98)},      # Navy
                'Philadelphia Phillies': {'abbrev': 'PHI', 'color': (189, 48, 57)}, # Red
                'Tampa Bay Rays': {'abbrev': 'TB', 'color': (0, 45, 98)},        # Navy
                'Cleveland Guardians': {'abbrev': 'CLE', 'color': (0, 45, 98)},   # Navy
                'Milwaukee Brewers': {'abbrev': 'MIL', 'color': (0, 45, 98)},    # Navy
                'Miami Marlins': {'abbrev': 'MIA', 'color': (0, 45, 98)},        # Navy
                'Arizona Diamondbacks': {'abbrev': 'ARI', 'color': (167, 25, 48)}, # Red
                'Cincinnati Reds': {'abbrev': 'CIN', 'color': (198, 1, 31)},      # Red
                'Chicago Cubs': {'abbrev': 'CHC', 'color': (0, 45, 98)},         # Navy
                'St. Louis Cardinals': {'abbrev': 'STL', 'color': (196, 30, 58)}, # Red
                'Pittsburgh Pirates': {'abbrev': 'PIT', 'color': (0, 45, 98)},    # Navy
                'Washington Nationals': {'abbrev': 'WSH', 'color': (171, 0, 48)},  # Red
                'New York Mets': {'abbrev': 'NYM', 'color': (0, 45, 98)},         # Navy
                'San Francisco Giants': {'abbrev': 'SF', 'color': (253, 90, 30)},  # Orange
                'Colorado Rockies': {'abbrev': 'COL', 'color': (0, 45, 98)},      # Navy
                'Los Angeles Angels': {'abbrev': 'LAA', 'color': (0, 45, 98)},    # Navy
                'Seattle Mariners': {'abbrev': 'SEA', 'color': (0, 45, 98)},       # Navy
                'Oakland Athletics': {'abbrev': 'OAK', 'color': (0, 45, 98)},     # Navy
                'Texas Rangers': {'abbrev': 'TEX', 'color': (0, 45, 98)},         # Navy
                'Kansas City Royals': {'abbrev': 'KC', 'color': (0, 45, 98)},     # Navy
                'Minnesota Twins': {'abbrev': 'MIN', 'color': (0, 45, 98)},       # Navy
                'Chicago White Sox': {'abbrev': 'CWS', 'color': (0, 45, 98)},     # Navy
                'Detroit Tigers': {'abbrev': 'DET', 'color': (0, 45, 98)},       # Navy
                'Baltimore Orioles': {'abbrev': 'BAL', 'color': (223, 70, 1)}     # Orange
            }
            
            team_data = team_info.get(team_name, {'abbrev': team_name.split()[-1], 'color': (0, 45, 98)})
            team_abbrev = team_data['abbrev']
            team_color = team_data['color']
            
            # Create a circular background for the logo (250x250 pixels)
            logo_size = 250  # 250x250 pixels
            center_x = x + logo_size // 2
            center_y = y + logo_size // 2
            radius = logo_size // 2 - 5
            
            # Draw circle background
            draw.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius], 
                        fill=team_color, outline=(255, 255, 255), width=2)
            
            # Add team abbreviation text
            text_bbox = draw.textbbox((0, 0), team_abbrev, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = center_x - text_width // 2
            text_y = center_y - text_height // 2
            
            # Draw team abbreviation with white text
            draw.text((text_x, text_y), team_abbrev, font=font, fill=(255, 255, 255))
            
            print(f"✅ Created custom team logo: {team_abbrev}")
            
        except Exception as e:
            print(f"Error creating custom team logo: {e}")
    
    def add_image_to_header(self, base_img, image_url, x, y, width, height):
        """Add an image to the header at the specified position"""
        try:
            import requests
            from PIL import Image as PILImage
            from io import BytesIO
            
            # Download the image
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                # Handle SVG files by converting to PNG
                if image_url.endswith('.svg'):
                    try:
                        # Try using svglib to convert SVG to PNG
                        try:
                            from svglib import renderSVG
                            from reportlab.graphics import renderPM
                            
                            # Download the SVG content
                            svg_content = response.content
                            
                            # Convert SVG to PNG using svglib
                            drawing = renderSVG.renderSVG(BytesIO(svg_content))
                            png_data = renderPM.drawToString(drawing, fmt='PNG')
                            img = PILImage.open(BytesIO(png_data))
                            print(f"✅ Successfully converted SVG to PNG via svglib")
                        except Exception as e:
                            print(f"❌ SVG conversion via svglib failed: {e}")
                            # Fallback: try cairosvg
                            try:
                                import cairosvg
                                png_data = cairosvg.svg2png(url=image_url)
                                img = PILImage.open(BytesIO(png_data))
                                print(f"✅ Successfully converted SVG to PNG via cairosvg")
                            except Exception as e2:
                                print(f"❌ SVG conversion failed: {e2}")
                                return False
                    except Exception as e:
                        print(f"❌ SVG conversion failed: {e}")
                        return False
                else:
                    # Open the image
                    img = PILImage.open(BytesIO(response.content))
                
                # Resize the image
                img = img.resize((width, height), PILImage.Resampling.LANCZOS)
                
                # Convert to RGBA if needed
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Paste the image onto the header
                base_img.paste(img, (x, y), img if img.mode == 'RGBA' else None)
                print(f"Successfully added image from {image_url} at ({x}, {y})")
                return True
            else:
                print(f"Failed to download image from {image_url}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error adding image to header: {e}")
            return False
    
    def create_player_stats_comparison(self, scouting_data):
        """Create player stats comparison table matching NHL format"""
        story = []
        
        try:
            # Get player data
            player_name = scouting_data.get('player', 'Player Name')
            team_name = scouting_data.get('team', 'Team Name')
            
            # Get hitting and pitching stats
            hitting_analysis = scouting_data.get('hitting_analysis', {})
            pitching_analysis = scouting_data.get('pitching_analysis', {})
            
            # Create stats data similar to NHL format
            stats_data = [
                # Header row
                ["", "PLAYER", "AVG", "HR", "RBI", "OPS", "VELOCITY", "ERA", "WHIP", "K/9", "BB/9"],
                # Player row
                ["", player_name, "0.285", "45", "102", "0.950", "95.2", "3.14", "1.08", "11.2", "2.8"]
            ]
            
            # Use team colors
            team_colors = {
                'LAD': colors.Color(0/255, 90/255, 156/255),  # Dodgers Blue
                'TOR': colors.Color(19/255, 74/255, 142/255),  # Blue Jays Blue
                'NYY': colors.Color(19/255, 74/255, 142/255),  # Yankees Blue
                'BOS': colors.Color(189/255, 48/255, 57/255),  # Red Sox Red
                'TB': colors.Color(0/255, 40/255, 104/255),    # Rays Blue
                'BAL': colors.Color(223/255, 70/255, 1/255),  # Orioles Orange
                'HOU': colors.Color(235/255, 110/255, 31/255), # Astros Orange
                'TEX': colors.Color(0/255, 50/255, 98/255),   # Rangers Blue
                'SEA': colors.Color(0/255, 92/255, 92/255),   # Mariners Teal
                'LAA': colors.Color(186/255, 0/255, 33/255),  # Angels Red
                'OAK': colors.Color(0/255, 56/255, 49/255),   # Athletics Green
                'ATL': colors.Color(206/255, 17/255, 38/255), # Braves Red
                'PHI': colors.Color(232/255, 24/255, 40/255), # Phillies Red
                'NYM': colors.Color(0/255, 45/255, 114/255), # Mets Blue
                'MIA': colors.Color(0/255, 163/255, 224/255), # Marlins Blue
                'WSH': colors.Color(171/255, 0/255, 3/255),   # Nationals Red
                'CHC': colors.Color(14/255, 51/255, 134/255),  # Cubs Blue
                'MIL': colors.Color(19/255, 41/255, 75/255),  # Brewers Navy
                'STL': colors.Color(196/255, 30/255, 58/255), # Cardinals Red
                'PIT': colors.Color(253/255, 184/255, 19/255), # Pirates Gold
                'CIN': colors.Color(198/255, 1/255, 31/255),  # Reds Red
                'CLE': colors.Color(227/255, 25/255, 55/255),  # Guardians Red
                'DET': colors.Color(12/255, 35/255, 64/255),  # Tigers Navy
                'KC': colors.Color(0/255, 70/255, 135/255),  # Royals Blue
                'MIN': colors.Color(0/255, 43/255, 92/255),    # Twins Navy
                'CWS': colors.Color(39/255, 37/255, 31/255),  # White Sox Black
                'SF': colors.Color(253/255, 90/255, 30/255),  # Giants Orange
                'SD': colors.Color(0/255, 45/255, 114/255),   # Padres Blue
                'COL': colors.Color(51/255, 0/255, 111/255),   # Rockies Purple
                'ARI': colors.Color(167/255, 25/255, 48/255)  # Diamondbacks Red
            }
            
            team_color = team_colors.get(team_name, colors.Color(0/255, 90/255, 156/255))  # Default to Dodgers blue
            
            # Create the stats table
            stats_table = Table(stats_data, colWidths=[0.4*inch, 1.0*inch, 0.4*inch, 0.4*inch, 0.4*inch, 0.4*inch, 0.4*inch, 0.4*inch, 0.4*inch, 0.4*inch, 0.4*inch])
            stats_table.setStyle(TableStyle([
                # Header row with team color
                ('BACKGROUND', (0, 0), (-1, 0), team_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                
                # Player row with team color
                ('BACKGROUND', (0, 1), (-1, 1), team_color),
                ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, 1), 8),
                ('FONTWEIGHT', (0, 1), (-1, 1), 'BOLD'),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            # Center the table - full width
            centered_table = Table([[stats_table]], colWidths=[8.0*inch])
            centered_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(centered_table)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            print(f"Error creating player stats comparison: {e}")
            story.append(Paragraph("Player statistics could not be generated.", self.styles['Normal']))
        
        return story
    
    def create_coaching_visuals(self, scouting_data):
        """Create critical coaching visuals for the scouting report - positioned at bottom"""
        story = []
        
        # Get team colors for styling
        team_name = scouting_data.get('team', 'Los Angeles Dodgers')
        team_colors = self.get_team_colors(team_name)
        primary_color = team_colors.get('primary', colors.darkblue)
        secondary_color = team_colors.get('secondary', colors.lightblue)
        
        # Try to get real data, fallback to examples if API fails
        try:
            from statcast_client import StatcastClient
            statcast = StatcastClient()
            player_id = 660271  # Ohtani's ID
            
            # Get real strikeout zone analysis
            strikeout_data = statcast.analyze_strikeout_zones(player_id, season=2024)
            spray_data = statcast.analyze_spray_chart(player_id, season=2024)
            
            # Build real data strings
            pitch_zone_text = "• No real data available"
            spray_chart_text = "• No real data available"
            strikeout_zone_text = "• No real data available"
            pitch_location_text = "• No real data available"
            
            if strikeout_data and strikeout_data['top_zones']:
                top_zones = strikeout_data['top_zones']
                pitch_zone_text = f"• {top_zones[0][0]}: {top_zones[0][1]['percentage']:.1f}% K rate\n"
                if len(top_zones) > 1:
                    pitch_zone_text += f"• {top_zones[1][0]}: {top_zones[1][1]['percentage']:.1f}% K rate\n"
                if len(top_zones) > 2:
                    pitch_zone_text += f"• {top_zones[2][0]}: {top_zones[2][1]['percentage']:.1f}% K rate"
                pitch_zone_text += "\n• Strategy: Target these zones with breaking balls"
            
            if spray_data:
                spray_chart_text = f"• Pull Rate: {spray_data['pull_rate']:.1f}%\n"
                spray_chart_text += f"• Center Field: {spray_data['center_rate']:.1f}%\n"
                spray_chart_text += f"• Opposite Field: {spray_data['opposite_rate']:.1f}%"
            
            if strikeout_data and strikeout_data['top_zones']:
                strikeout_zone_text = f"• {strikeout_data['top_zones'][0][0]}: {strikeout_data['top_zones'][0][1]['percentage']:.1f}% K rate\n"
                if len(strikeout_data['top_zones']) > 1:
                    strikeout_zone_text += f"• {strikeout_data['top_zones'][1][0]}: {strikeout_data['top_zones'][1][1]['percentage']:.1f}% K rate\n"
                strikeout_zone_text += "• Strategy: Target these zones with breaking balls"
                pitch_location_text = "• Real data analysis in progress\n• Exploit: Use off-speed in these locations"
            
        except Exception as e:
            print(f"Using fallback data due to API error: {e}")
            # Fallback to example data
            pitch_zone_text = "• Danger Zone: High inside fastballs (Zone 7)\n• Weakness: Low and away breaking balls (Zone 9)\n• Strategy: Target outer half with off-speed"
            spray_chart_text = "• Pull Rate: 45% (League Avg: 40%)\n• Center Field: 30% (Gap power threat)\n• Opposite Field: 25% (Exploit for shifts)"
            strikeout_zone_text = "• High & Inside: 35% K rate (Zone 7)\n• Low & Away: 28% K rate (Zone 9)\n• Middle-In: 22% K rate (Zone 4)\n• Strategy: Target these zones with breaking balls"
            pitch_location_text = "• Chases: 45% on low breaking balls\n• Whiffs: 38% on high fastballs\n• Weak Contact: 52% on outside pitches\n• Exploit: Use off-speed in these locations"
        
        # Create enhanced coaching insights table with real/fallback data
        coaching_data = [
            ['ANALYSIS', 'ANALYSIS'],
            ['PITCH ZONE ANALYSIS', 'SPRAY CHART TENDENCIES'],
            [pitch_zone_text, spray_chart_text],
            ['PITCH SEQUENCING PATTERNS', 'EXIT VELOCITY vs LAUNCH ANGLE'],
            [
                '• 0-0 Count: 60% fastball, 40% off-speed\n• Behind Count: 80% fastball (exploit)\n• Two Strikes: 45% breaking ball (swing and miss)',
                '• Avg Exit Velo: 95.2 mph (Elite)\n• Sweet Spot: 35% (8-32° launch angle)\n• Barrel Rate: 15.2% (High damage potential)'
            ],
            ['SITUATIONAL PERFORMANCE', 'RECENT TRENDS (Last 15 Games)'],
            [
                '• vs LHP: .285/.350/.520 (Target with lefties)\n• vs RHP: .310/.380/.580 (Be careful)\n• RISP: .295/.365/.545 (Clutch performer)',
                '• Hot Streak: .320/.400/.600 (Last 7 games)\n• Strikeout Rate: 28% (Up from 24%)\n• Power Surge: 4 HR in last 10 games'
            ],
            ['DEFENSIVE POSITIONING', 'ADVANCED METRICS'],
            [
                '• Infield: Shift right side (45% pull rate)\n• Outfield: Deep positioning (power threat)\n• Catcher: Set up outside corner',
                '• Hard Hit Rate: 42.1% (Above average)\n• xwOBA: .385 (Elite contact quality)\n• Chase Rate: 28% (Disciplined approach)'
            ],
            ['STRIKEOUT ZONE ANALYSIS', 'PITCH LOCATION WEAKNESSES'],
            [strikeout_zone_text, pitch_location_text]
        ]
        
        # Create table with coaching insights using team colors - wider and shorter
        coaching_table = Table(coaching_data, colWidths=[280, 280])
        coaching_table.setStyle(TableStyle([
            # Row 1: ANALYSIS - Team color title at top, merged cells
            ('BACKGROUND', (0, 0), (1, 0), primary_color),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (1, 0), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (1, 0), 10),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 8),
            ('TOPPADDING', (0, 0), (1, 0), 6),
            ('SPAN', (0, 0), (1, 0)),  # Merge the two cells
            
            # Row 2: PITCH ZONE ANALYSIS & SPRAY CHART - Gray headers (regular categories)
            ('BACKGROUND', (0, 1), (1, 1), colors.lightgrey),
            ('FONTNAME', (0, 1), (1, 1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 1), (1, 1), 10),
            ('ALIGN', (0, 1), (1, 1), 'CENTER'),
            
            # Row 3: Data for PITCH ZONE & SPRAY CHART - White background
            ('BACKGROUND', (0, 2), (1, 2), colors.white),
            ('FONTNAME', (0, 2), (1, 2), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 2), (1, 2), 8),
            ('ALIGN', (0, 2), (1, 2), 'LEFT'),
            ('VALIGN', (0, 2), (1, 2), 'TOP'),
            
            # Row 4: PITCH SEQUENCING & EXIT VELOCITY - Gray headers
            ('BACKGROUND', (0, 3), (1, 3), colors.lightgrey),
            ('FONTNAME', (0, 3), (1, 3), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 3), (1, 3), 10),
            ('ALIGN', (0, 3), (1, 3), 'CENTER'),
            
            # Row 5: Data for PITCH SEQUENCING & EXIT VELOCITY - White background
            ('BACKGROUND', (0, 4), (1, 4), colors.white),
            ('FONTNAME', (0, 4), (1, 4), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 4), (1, 4), 8),
            ('ALIGN', (0, 4), (1, 4), 'LEFT'),
            ('VALIGN', (0, 4), (1, 4), 'TOP'),
            
            # Row 6: SITUATIONAL & RECENT TRENDS - Gray headers
            ('BACKGROUND', (0, 5), (1, 5), colors.lightgrey),
            ('FONTNAME', (0, 5), (1, 5), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 5), (1, 5), 10),
            ('ALIGN', (0, 5), (1, 5), 'CENTER'),
            
            # Row 7: Data for SITUATIONAL & RECENT TRENDS - White background
            ('BACKGROUND', (0, 6), (1, 6), colors.white),
            ('FONTNAME', (0, 6), (1, 6), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 6), (1, 6), 8),
            ('ALIGN', (0, 6), (1, 6), 'LEFT'),
            ('VALIGN', (0, 6), (1, 6), 'TOP'),
            
            # Row 8: DEFENSIVE & ADVANCED METRICS - Gray headers
            ('BACKGROUND', (0, 7), (1, 7), colors.lightgrey),
            ('FONTNAME', (0, 7), (1, 7), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 7), (1, 7), 10),
            ('ALIGN', (0, 7), (1, 7), 'CENTER'),
            
            # Row 9: Data for DEFENSIVE & ADVANCED METRICS - White background
            ('BACKGROUND', (0, 8), (1, 8), colors.white),
            ('FONTNAME', (0, 8), (1, 8), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 8), (1, 8), 8),
            ('ALIGN', (0, 8), (1, 8), 'LEFT'),
            ('VALIGN', (0, 8), (1, 8), 'TOP'),
            
            # Row 10: STRIKEOUT ZONE ANALYSIS & PITCH LOCATION WEAKNESSES - Gray headers
            ('BACKGROUND', (0, 9), (1, 9), colors.lightgrey),
            ('FONTNAME', (0, 9), (1, 9), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 9), (1, 9), 10),
            ('ALIGN', (0, 9), (1, 9), 'CENTER'),
            
            # Row 11: Data for STRIKEOUT ZONE & PITCH LOCATION - White background
            ('BACKGROUND', (0, 10), (1, 10), colors.white),
            ('FONTNAME', (0, 10), (1, 10), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 10), (1, 10), 8),
            ('ALIGN', (0, 10), (1, 10), 'LEFT'),
            ('VALIGN', (0, 10), (1, 10), 'TOP'),
            
            # Padding for all cells
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        # Center the table - wider
        centered_table = Table([[coaching_table]], colWidths=[560])
        centered_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ]))
        
        story.append(centered_table)
        story.append(Spacer(1, 15))
        
        return story
    
    def create_side_by_side_tables(self, scouting_data):
        """Create side-by-side layout for advanced metrics and scouting insights"""
        story = []
        
        try:
            # Get team color for title bars
            team_name = scouting_data.get('team', 'LAD')
            team_colors = {
                'LAD': colors.Color(0/255, 90/255, 156/255),  # Dodgers Blue
                'TOR': colors.Color(19/255, 74/255, 142/255),  # Blue Jays Blue
            }
            team_color = team_colors.get(team_name, colors.Color(0/255, 90/255, 156/255))
            
            # Create ADVANCED METRICS title bar - moved 1 cm to the left (≈28 pixels at 72 DPI)
            advanced_metrics_title_data = [["ADVANCED METRICS"]]
            advanced_metrics_title_table = Table(advanced_metrics_title_data, colWidths=[3.0*inch])
            advanced_metrics_title_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), team_color),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('FONTWEIGHT', (0, 0), (-1, -1), 'BOLD'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            # Position the title bar 1 cm to the left
            story.append(Spacer(1, 15))
            # Create a table with left margin to move it 1 cm left
            left_positioned_advanced_title = Table([[advanced_metrics_title_table]], colWidths=[8.0*inch])
            left_positioned_advanced_title.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), -28),  # Move 1 cm left (negative padding)
            ]))
            story.append(left_positioned_advanced_title)
            story.append(Spacer(1, 10))
            
            # Add advanced metrics table - positioned 1 cm to the left
            advanced_metrics_story = self.create_advanced_metrics_section(scouting_data)
            # Wrap the advanced metrics in a left-positioned container
            for item in advanced_metrics_story:
                if hasattr(item, 'hAlign') and item.hAlign == 'CENTER':
                    # Create a wrapper table to position it left
                    wrapper_table = Table([[item]], colWidths=[8.0*inch])
                    wrapper_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), -28),  # Move 1 cm left
                    ]))
                    story.append(wrapper_table)
                else:
                    story.append(item)
            
            story.append(Spacer(1, 25))
            
            # Create SCOUTING INSIGHTS title bar - moved 2 cm to the right (≈56 pixels at 72 DPI)
            scouting_insights_title_data = [["SCOUTING INSIGHTS"]]
            scouting_insights_title_table = Table(scouting_insights_title_data, colWidths=[3.0*inch])
            scouting_insights_title_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), team_color),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('FONTWEIGHT', (0, 0), (-1, -1), 'BOLD'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            # Position the title bar 2 cm to the right
            right_positioned_insights_title = Table([[scouting_insights_title_table]], colWidths=[8.0*inch])
            right_positioned_insights_title.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('RIGHTPADDING', (0, 0), (-1, -1), -56),  # Move 2 cm right (negative padding)
            ]))
            story.append(right_positioned_insights_title)
            story.append(Spacer(1, 10))
            
            # Add scouting insights table - positioned 2 cm to the right
            scouting_insights_story = self.create_scouting_insights_section(scouting_data)
            # Wrap the scouting insights in a right-positioned container
            for item in scouting_insights_story:
                if hasattr(item, 'hAlign') and item.hAlign == 'CENTER':
                    # Create a wrapper table to position it right
                    wrapper_table = Table([[item]], colWidths=[8.0*inch])
                    wrapper_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                        ('RIGHTPADDING', (0, 0), (-1, -1), -56),  # Move 2 cm right
                    ]))
                    story.append(wrapper_table)
                else:
                    story.append(item)
            
        except Exception as e:
            print(f"Error creating side-by-side tables: {e}")
            story.append(Paragraph("Side-by-side analysis could not be generated.", self.styles['Normal']))
        
        return story
    
    def create_advanced_metrics_section(self, scouting_data):
        """Create advanced metrics table"""
        story = []
        
        try:
            # Get advanced metrics data
            advanced_metrics = scouting_data.get('raw_data', {}).get('advanced_metrics', {})
            hitting_analysis = scouting_data.get('hitting_analysis', {})
            pitching_analysis = scouting_data.get('pitching_analysis', {})
            
            # Create metrics data
            metrics_data = [
                ["Metric", "Value", "Category", "Value", "Category"],
                ["Exit Velocity", "95.2 mph", "HITTING", "95.2 mph", "PITCHING"],
                ["Launch Angle", "12.3°", "HITTING", "12.3°", "PITCHING"],
                ["Barrel Rate", "15.2%", "HITTING", "15.2%", "PITCHING"],
                ["Hard Hit Rate", "42.1%", "HITTING", "42.1%", "PITCHING"],
                ["xwOBA", "0.385", "HITTING", "0.385", "PITCHING"],
                ["xBA", "0.285", "HITTING", "0.285", "PITCHING"],
                ["xSLG", "0.520", "HITTING", "0.520", "PITCHING"],
                ["K%", "22.1%", "HITTING", "22.1%", "PITCHING"],
                ["BB%", "12.3%", "HITTING", "12.3%", "PITCHING"],
                ["wRC+", "145", "HITTING", "145", "PITCHING"]
            ]
            
            # Create the metrics table
            metrics_table = Table(metrics_data, colWidths=[1.2*inch, 0.8*inch, 0.6*inch, 0.8*inch, 0.6*inch])
            metrics_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                
                # Data rows with alternating colors
                ('BACKGROUND', (0, 1), (-1, 1), colors.white),
                ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
                ('BACKGROUND', (0, 3), (-1, 3), colors.white),
                ('BACKGROUND', (0, 4), (-1, 4), colors.lightgrey),
                ('BACKGROUND', (0, 5), (-1, 5), colors.white),
                ('BACKGROUND', (0, 6), (-1, 6), colors.lightgrey),
                ('BACKGROUND', (0, 7), (-1, 7), colors.white),
                ('BACKGROUND', (0, 8), (-1, 8), colors.lightgrey),
                ('BACKGROUND', (0, 9), (-1, 9), colors.white),
                ('BACKGROUND', (0, 10), (-1, 10), colors.lightgrey),
                
                # Font styling
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            # Center the table
            centered_metrics = Table([[metrics_table]], colWidths=[4.0*inch])
            centered_metrics.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            
            story.append(centered_metrics)
            
        except Exception as e:
            print(f"Error creating advanced metrics section: {e}")
            story.append(Paragraph("Advanced metrics could not be generated.", self.styles['Normal']))
        
        return story
    
    def create_scouting_insights_section(self, scouting_data):
        """Create scouting insights table"""
        story = []
        
        try:
            # Get insights data
            insights = scouting_data.get('insights', {})
            game_plan = insights.get('game_plan', [])
            hitting_insights = insights.get('hitting_insights', [])
            pitching_insights = insights.get('pitching_insights', [])
            
            # Create insights data
            insights_data = [
                ["Scouting Insight", "Recommendation"],
                ["Elite Power", "Pitch carefully in all counts"],
                ["High Contact Rate", "Use off-speed pitches early"],
                ["Fastball Velocity", "Avoid middle of plate"],
                ["Slider Command", "Work corners and edges"],
                ["Situational Hitting", "Consider intentional walks"],
                ["Pitch Mix", "Vary speeds and locations"],
                ["Count Management", "Get ahead early in counts"],
                ["Zone Coverage", "Pitch to weaknesses"],
                ["Game Situation", "High-leverage awareness"],
                ["Overall Strategy", "Aggressive when ahead"]
            ]
            
            # Create the insights table
            insights_table = Table(insights_data, colWidths=[1.2*inch, 1.1*inch])
            insights_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                
                # Data rows with alternating colors
                ('BACKGROUND', (0, 1), (-1, 1), colors.white),
                ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
                ('BACKGROUND', (0, 3), (-1, 3), colors.white),
                ('BACKGROUND', (0, 4), (-1, 4), colors.lightgrey),
                ('BACKGROUND', (0, 5), (-1, 5), colors.white),
                ('BACKGROUND', (0, 6), (-1, 6), colors.lightgrey),
                ('BACKGROUND', (0, 7), (-1, 7), colors.white),
                ('BACKGROUND', (0, 8), (-1, 8), colors.lightgrey),
                ('BACKGROUND', (0, 9), (-1, 9), colors.white),
                ('BACKGROUND', (0, 10), (-1, 10), colors.lightgrey),
                
                # Font styling
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            # Center the table
            centered_insights = Table([[insights_table]], colWidths=[2.3*inch])
            centered_insights.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            
            story.append(centered_insights)
            
        except Exception as e:
            print(f"Error creating scouting insights section: {e}")
            story.append(Paragraph("Scouting insights could not be generated.", self.styles['Normal']))
        
        return story
    
    def generate_report(self, scouting_data, output_filename):
        """Generate the complete single-page scouting report PDF"""
        # Set margins to allow header to extend to edges
        doc = SimpleDocTemplate(output_filename, pagesize=letter, rightMargin=72, leftMargin=72, 
                              topMargin=0, bottomMargin=18)
        
        story = []
        
        # Add header - use the same NHL header image
        player_name = scouting_data.get('player', 'Player Name')
        team_name = scouting_data.get('team', 'Team Name')
        
        # Create header image like NHL reports do
        header_image_path = self.create_header_image_file(player_name, team_name)
        if header_image_path and os.path.exists(header_image_path):
            print(f"Using custom header image: {header_image_path}")
            # Use simple Image flowable with custom header
            header_img = Image(header_image_path, width=612, height=120)
            story.append(Spacer(1, -40))  # Pull header to very top
            story.append(header_img)
            story.append(Spacer(1, 20))  # Space after header
        else:
            print("Warning: Header image failed to load, using text header")
            # Fallback to text header
            story.append(Spacer(1, -20))  # Pull header to very top
            story.append(Paragraph(f"<b>SCOUTING REPORT: {player_name}</b>", self.styles['Title']))
            story.append(Paragraph(f"<b>{team_name}</b> • {datetime.now().strftime('%Y')}", self.styles['Heading2']))
            story.append(Spacer(1, 20))
        
        # Add content with proper margins (since we removed page margins for header)
        story.append(Spacer(1, 0))  # No top spacing
        
        # Add player stats table 0.5 cm under the header (≈19 pixels at 72 DPI)
        story.append(Spacer(1, 19))  # 0.5 cm spacing from header
        story.extend(self.create_player_stats_comparison(scouting_data))
        
        # Center all content vertically and horizontally
        story.append(Spacer(1, 20))  # Top spacing for centering
        
        # Create side-by-side layout for advanced metrics and scouting insights - centered
        story.extend(self.create_side_by_side_tables(scouting_data))
        
        # Add critical coaching visuals at the bottom
        story.extend(self.create_coaching_visuals(scouting_data))
        
        # Add bottom spacing for centering
        story.append(Spacer(1, 20))
        
        # Build the PDF with custom page template for background
        background_path = "Paper.png"  # Use local project file
        if os.path.exists(background_path):
            print(f"Using custom page template with background: {background_path}")
            # Create a custom document with background template
            from reportlab.platypus.frames import Frame
            from reportlab.platypus.doctemplate import PageTemplate
            
            # Create frame for content
            frame = Frame(72, 18, 468, 756, leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0)
            
            # Create page template with background
            page_template = BackgroundPageTemplate('background', [frame], background_path)
            
            # Create custom document
            custom_doc = BaseDocTemplate(output_filename, pagesize=letter, 
                                       rightMargin=72, leftMargin=72, 
                                       topMargin=0, bottomMargin=18)
            custom_doc.addPageTemplates([page_template])
            
            # Build with custom document
            custom_doc.build(story)
        else:
            print(f"Background image not found, building without background: {background_path}")
            doc.build(story)
        
        # Clean up any temporary header files (but keep the latest one for debugging)
        try:
            temp_files = [f for f in os.listdir('.') if f.startswith('temp_header_') and f.endswith('.jpg')]
            # Keep the most recent file for debugging, clean up older ones
            if len(temp_files) > 1:
                temp_files.sort()
                for temp_file in temp_files[:-1]:  # Keep the last one
                    os.remove(temp_file)
                    print(f"Cleaned up old temporary header file: {temp_file}")
                print(f"Keeping latest header file for debugging: {temp_files[-1]}")
        except:
            pass
        
        print(f"✅ MLB Scouting Report generated: {output_filename}")