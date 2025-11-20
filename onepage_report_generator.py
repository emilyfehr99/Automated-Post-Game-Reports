from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus.flowables import Flowable
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from advanced_metrics_analyzer import AdvancedMetricsAnalyzer
import os
from create_header_image import create_dynamic_header

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
            from reportlab.lib.utils import ImageReader
            img = ImageReader(self.image_path)
            # Draw image at absolute top-left corner (0, 0)
            self.canv.drawImage(img, 0, 0, width=self.width, height=self.height)

class OnePageReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.register_fonts()
        self.setup_custom_styles()
    
    def register_fonts(self):
        """Register custom fonts with ReportLab"""
        try:
            # Register Russo One font
            pdfmetrics.registerFont(TTFont('RussoOne-Regular', '/Users/emilyfehr8/Library/Fonts/RussoOne-Regular.ttf'))
        except:
            try:
                # Fallback to system font
                pdfmetrics.registerFont(TTFont('RussoOne-Regular', '/System/Library/Fonts/Arial Bold.ttf'))
            except:
                # Use default font if all else fails
                pass
    
    def create_header_image(self, game_data, game_id=None):
        """Create the modern header image for the report using the user's header with team names"""
        try:
            # Use the user's header image from project directory
            header_path = "/Users/emilyfehr8/CascadeProjects/nhl_postgame_reports/Header.jpg"
            
            if os.path.exists(header_path):
                # Create a custom header with team names overlaid
                from PIL import Image as PILImage, ImageDraw, ImageFont
                
                # Load the header image
                header_img = PILImage.open(header_path)
                
                # Create a drawing context
                draw = ImageDraw.Draw(header_img)
                
                # Get team names with error handling
                try:
                    # Handle both old and new data structures
                    if 'boxscore' in game_data['game_center']:
                        away_team = game_data['game_center']['boxscore']['awayTeam']['abbrev']
                    else:
                        away_team = game_data['game_center']['awayTeam']['abbrev']
                    # Handle both old and new data structures
                    if 'boxscore' in game_data['game_center']:
                        home_team = game_data['game_center']['boxscore']['homeTeam']['abbrev']
                    else:
                        home_team = game_data['game_center']['homeTeam']['abbrev']
                except (KeyError, TypeError):
                    # Fallback to default team names if data is missing
                    away_team = "FLA"
                    home_team = "EDM"
                
                # Try to load Russo One font first (better text rendering), fallback to others
                try:
                    font = ImageFont.truetype("/Users/emilyfehr8/Library/Fonts/RussoOne-Regular.ttf", 112)
                except:
                    try:
                        font = ImageFont.truetype("/Users/emilyfehr8/Library/Fonts/DAGGERSQUARE.otf", 112)
                    except:
                        try:
                            font = ImageFont.truetype("/System/Library/Fonts/Arial Bold.ttf", 112)
                        except:
                            font = ImageFont.load_default()
                
                # Calculate text positions
                img_width, img_height = header_img.size
                text_color = (255, 255, 255)  # White text
                
                # Position team names on left and right sides
                away_text = f"{away_team}"
                home_text = f"{home_team}"
                
                # Get text bounding boxes
                away_bbox = draw.textbbox((0, 0), away_text, font=font)
                home_bbox = draw.textbbox((0, 0), home_text, font=font)
                
                away_width = away_bbox[2] - away_bbox[0]
                home_width = home_bbox[2] - home_bbox[0]
                text_height = away_bbox[3] - away_bbox[1]
                
                # Position away team on left, home team on right
                away_x = 50  # Left margin
                home_x = img_width - home_width - 50  # Right margin
                text_y = (img_height - text_height) // 2  # Vertically centered
                
                # Draw team names
                draw.text((away_x, text_y), away_text, fill=text_color, font=font)
                draw.text((home_x, text_y), home_text, fill=text_color, font=font)
                
                # Save the modified header
                temp_header_path = f"/tmp/header_{game_id or 'temp'}.jpg"
                header_img.save(temp_header_path, "JPEG", quality=95)
                
                return HeaderFlowable(temp_header_path, 612, 100)  # Full width, 100pt height
            else:
                print(f"Header image not found at {header_path}")
                return None
        except Exception as e:
            print(f"Error creating header image: {e}")
            return None
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='RussoOne-Regular'
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='RussoOne-Regular'
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.darkred,
            alignment=TA_CENTER,
            spaceAfter=10,
            fontName='RussoOne-Regular'
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='RussoOne-Regular'
        )
        
        # Stat text style
        self.stat_style = ParagraphStyle(
            'CustomStat',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=4,
            fontName='RussoOne-Regular'
        )
        
        # Small stat style
        self.small_stat_style = ParagraphStyle(
            'CustomSmallStat',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=3,
            fontName='RussoOne-Regular'
        )
    
    def get_team_logo_path(self, team_abbrev):
        """Get the path to the team logo"""
        logo_path = f"/Users/emilyfehr8/CascadeProjects/nhl_postgame_reports/corrected_nhl_logos/{team_abbrev}.png"
        if os.path.exists(logo_path):
            return logo_path
        return None
    
    def create_team_logo(self, team_abbrev, size=30):
        """Create a team logo image"""
        logo_path = self.get_team_logo_path(team_abbrev)
        if logo_path:
            return Image(logo_path, width=size, height=size)
        return None
    
    def get_game_score(self, player_data):
        """Calculate Game Score for a player"""
        try:
            # Basic Game Score calculation (goals, assists, shots, etc.)
            goals = player_data.get('goals', 0)
            assists = player_data.get('assists', 0)
            shots = player_data.get('shots', 0)
            hits = player_data.get('hits', 0)
            blocks = player_data.get('blockedShots', 0)
            pim = player_data.get('pim', 0)
            plus_minus = player_data.get('plusMinus', 0)
            
            # Simple Game Score formula
            gs = (goals * 0.75) + (assists * 0.7) + (shots * 0.05) + (hits * 0.05) + (blocks * 0.05) - (pim * 0.15) + (plus_minus * 0.1)
            return round(gs, 1)
        except:
            return 0.0
    
    def create_one_page_report(self, game_data, output_filename, game_id=None):
        """Generate a comprehensive one-page report"""
        # Set margins to allow header to extend to edges
        doc = SimpleDocTemplate(output_filename, pagesize=letter, rightMargin=36, leftMargin=36, 
                              topMargin=0, bottomMargin=18)
        
        story = []
        
        # Add header image
        header_image = self.create_header_image(game_data, game_id)
        if header_image:
            story.append(Spacer(1, -20))
            story.append(header_image)
            story.append(Spacer(1, 10))
        
        # Get team data - handle both old and new data structures
        try:
            if 'boxscore' in game_data['game_center']:
                # New structure: game_center contains boxscore
                away_team = game_data['game_center']['boxscore']['awayTeam']
                home_team = game_data['game_center']['boxscore']['homeTeam']
            else:
                # Old structure: direct access
                away_team = game_data['game_center']['awayTeam']
                home_team = game_data['game_center']['homeTeam']
            
            away_abbrev = away_team['abbrev']
            home_abbrev = home_team['abbrev']
            away_score = away_team['score']
            home_score = home_team['score']
        except:
            away_abbrev = "AWY"
            home_abbrev = "HME"
            away_score = 0
            home_score = 0
        
        # Game score
        story.append(Paragraph(f"{away_abbrev} {away_score} - {home_score} {home_abbrev}", self.title_style))
        story.append(Spacer(1, 10))
        
        # Create main content sections
        
        # Column 1: Team Stats
        team_stats = self.create_team_stats_section(game_data)
        
        # Column 2: Advanced Metrics
        advanced_metrics = self.create_advanced_metrics_section(game_data)
        
        # Column 3: Player Performance
        player_performance = self.create_player_performance_section(game_data)
        
        # Add each section directly instead of using a main table
        story.append(team_stats)
        story.append(Spacer(1, 10))
        story.append(advanced_metrics)
        story.append(Spacer(1, 10))
        story.append(player_performance)
        
        # Build PDF
        doc.build(story)
    
    def create_team_stats_section(self, game_data):
        """Create team statistics section"""
        try:
            # Handle both old and new data structures
            if 'boxscore' in game_data['game_center']:
                away_team = game_data['game_center']['boxscore']['awayTeam']
                home_team = game_data['game_center']['boxscore']['homeTeam']
            else:
                away_team = game_data['game_center']['awayTeam']
                home_team = game_data['game_center']['homeTeam']
            
            away_abbrev = away_team['abbrev']
            home_abbrev = home_team['abbrev']
        except:
            away_abbrev = "AWY"
            home_abbrev = "HME"
        
        # Get team stats
        try:
            # Handle both old and new data structures
            if 'boxscore' in game_data['game_center']:
                away_stats = game_data['game_center']['boxscore']['awayTeam']['stats']
                home_stats = game_data['game_center']['boxscore']['homeTeam']['stats']
            else:
                away_stats = game_data['game_center']['awayTeam']['stats']
                home_stats = game_data['game_center']['homeTeam']['stats']
        except:
            away_stats = {}
            home_stats = {}
        
        # Create team stats table
        team_data = [
            [Paragraph("TEAM STATS", self.section_style)],
            [Paragraph(f"{away_abbrev}", self.stat_style), Paragraph(f"{home_abbrev}", self.stat_style)],
            [Paragraph("Goals", self.small_stat_style), Paragraph(str(away_stats.get('goals', 0)), self.small_stat_style), Paragraph(str(home_stats.get('goals', 0)), self.small_stat_style)],
            [Paragraph("Shots", self.small_stat_style), Paragraph(str(away_stats.get('shots', 0)), self.small_stat_style), Paragraph(str(home_stats.get('shots', 0)), self.small_stat_style)],
            [Paragraph("Hits", self.small_stat_style), Paragraph(str(away_stats.get('hits', 0)), self.small_stat_style), Paragraph(str(home_stats.get('hits', 0)), self.small_stat_style)],
            [Paragraph("Blocks", self.small_stat_style), Paragraph(str(away_stats.get('blockedShots', 0)), self.small_stat_style), Paragraph(str(home_stats.get('blockedShots', 0)), self.small_stat_style)],
            [Paragraph("PIM", self.small_stat_style), Paragraph(str(away_stats.get('pim', 0)), self.small_stat_style), Paragraph(str(home_stats.get('pim', 0)), self.small_stat_style)],
            [Paragraph("PP%", self.small_stat_style), Paragraph(str(away_stats.get('powerPlayPercentage', 0)), self.small_stat_style), Paragraph(str(home_stats.get('powerPlayPercentage', 0)), self.small_stat_style)],
        ]
        
        team_table = Table(team_data, colWidths=[0.8*inch, 0.5*inch, 0.5*inch])
        team_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (0, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
            ('SPAN', (0, 0), (2, 0)),
        ]))
        
        return team_table
    
    def create_advanced_metrics_section(self, game_data):
        """Create advanced metrics section"""
        # Get advanced metrics from analyzer
        try:
            from advanced_metrics_analyzer import AdvancedMetricsAnalyzer
            analyzer = AdvancedMetricsAnalyzer(game_data.get('play_by_play', {}))
            # Handle both old and new data structures
            if 'boxscore' in game_data['game_center']:
                away_team_id = game_data['game_center']['boxscore']['awayTeam']['id']
                home_team_id = game_data['game_center']['boxscore']['homeTeam']['id']
            else:
                away_team_id = game_data['game_center']['awayTeam']['id']
                home_team_id = game_data['game_center']['homeTeam']['id']
            metrics = analyzer.generate_comprehensive_report(away_team_id, home_team_id)
        except:
            metrics = {}
        
        # Create advanced metrics table
        adv_data = [
            [Paragraph("ADVANCED METRICS", self.section_style)],
            [Paragraph("Metric", self.small_stat_style), Paragraph("Away", self.small_stat_style), Paragraph("Home", self.small_stat_style)],
            [Paragraph("Corsi%", self.small_stat_style), Paragraph(str(metrics.get('away_corsi_pct', 0)), self.small_stat_style), Paragraph(str(metrics.get('home_corsi_pct', 0)), self.small_stat_style)],
            [Paragraph("Fenwick%", self.small_stat_style), Paragraph(str(metrics.get('away_fenwick_pct', 0)), self.small_stat_style), Paragraph(str(metrics.get('home_fenwick_pct', 0)), self.small_stat_style)],
            [Paragraph("xGF%", self.small_stat_style), Paragraph(str(metrics.get('away_xgf_pct', 0)), self.small_stat_style), Paragraph(str(metrics.get('home_xgf_pct', 0)), self.small_stat_style)],
            [Paragraph("HDCF%", self.small_stat_style), Paragraph(str(metrics.get('away_hdcf_pct', 0)), self.small_stat_style), Paragraph(str(metrics.get('home_hdcf_pct', 0)), self.small_stat_style)],
            [Paragraph("PDO", self.small_stat_style), Paragraph(str(metrics.get('away_pdo', 0)), self.small_stat_style), Paragraph(str(metrics.get('home_pdo', 0)), self.small_stat_style)],
        ]
        
        adv_table = Table(adv_data, colWidths=[0.8*inch, 0.5*inch, 0.5*inch])
        adv_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (0, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
            ('SPAN', (0, 0), (2, 0)),
        ]))
        
        return adv_table
    
    def create_player_performance_section(self, game_data):
        """Create player performance section with detailed metrics"""
        try:
            # Handle both old and new data structures
            if 'boxscore' in game_data['game_center']:
                away_team = game_data['game_center']['boxscore']['awayTeam']['abbrev']
                home_team = game_data['game_center']['boxscore']['homeTeam']['abbrev']
            else:
                away_team = game_data['game_center']['awayTeam']['abbrev']
                home_team = game_data['game_center']['homeTeam']['abbrev']
        except:
            away_team = "AWY"
            home_team = "HME"
        
        # Get player data
        try:
            # Handle both old and new data structures
            if 'boxscore' in game_data['game_center']:
                away_players = game_data['game_center']['boxscore']['awayTeam']['players']
                home_players = game_data['game_center']['boxscore']['homeTeam']['players']
            else:
                away_players = game_data['game_center']['awayTeam']['players']
                home_players = game_data['game_center']['homeTeam']['players']
        except:
            away_players = []
            home_players = []
        
        # Create player performance table
        player_data = [
            [Paragraph("PLAYER PERFORMANCE", self.section_style)],
            [Paragraph("Player", self.small_stat_style), Paragraph("G", self.small_stat_style), Paragraph("A", self.small_stat_style), Paragraph("P", self.small_stat_style), Paragraph("GS", self.small_stat_style)],
        ]
        
        # Add top 3 players from each team
        for team_players, team_name in [(away_players, away_team), (home_players, home_team)]:
            if team_players:
                # Sort by Game Score and take top 3
                sorted_players = sorted(team_players, key=lambda p: self.get_game_score(p), reverse=True)[:3]
                
                for player in sorted_players:
                    name = player.get('name', 'Unknown')[:12]  # Truncate long names
                    goals = player.get('goals', 0)
                    assists = player.get('assists', 0)
                    points = goals + assists
                    gs = self.get_game_score(player)
                    
                    player_data.append([
                        Paragraph(name, self.small_stat_style),
                        Paragraph(str(goals), self.small_stat_style),
                        Paragraph(str(assists), self.small_stat_style),
                        Paragraph(str(points), self.small_stat_style),
                        Paragraph(str(gs), self.small_stat_style)
                    ])
        
        player_table = Table(player_data, colWidths=[0.6*inch, 0.3*inch, 0.3*inch, 0.3*inch, 0.3*inch])
        player_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (0, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
            ('SPAN', (0, 0), (4, 0)),
        ]))
        
        return player_table
