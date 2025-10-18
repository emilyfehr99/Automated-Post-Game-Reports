from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus.flowables import Flowable
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER, TA_CENTER, TA_RIGHT
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from advanced_metrics_analyzer import AdvancedMetricsAnalyzer
from improved_xg_model import ImprovedXGModel
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from io import BytesIO
import os
import requests
from PIL import Image as PILImage
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

class PostGameReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.register_fonts()
        self.setup_custom_styles()
        self.xg_model = ImprovedXGModel()  # Initialize improved xG model for period-by-period calculations
    
    def register_fonts(self):
        """Register custom fonts with ReportLab"""
        try:
            # Use path relative to script location
            script_dir = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(script_dir, 'RussoOne-Regular.ttf')
            
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('RussoOne-Regular', font_path))
            else:
                # Try user's Library folder as fallback
                pdfmetrics.registerFont(TTFont('RussoOne-Regular', '/Users/emilyfehr8/Library/Fonts/RussoOne-Regular.ttf'))
        except:
            try:
                # Fallback to Helvetica-Bold which is always available
                pdfmetrics.registerFont(TTFont('RussoOne-Regular', 'Helvetica-Bold'))
            except:
                # Use default font if all else fails
                pass
    
    def create_header_image(self, game_data, game_id=None):
        """Create the modern header image for the report using the user's header with team names"""
        try:
            # Use the user's header image from project directory
            # Use path relative to script location
            script_dir = os.path.dirname(os.path.abspath(__file__))
            header_path = os.path.join(script_dir, "Header.jpg")
            
            if os.path.exists(header_path):
                # Create a custom header with team names overlaid
                from PIL import Image as PILImage, ImageDraw, ImageFont
                
                # Load the header image
                header_img = PILImage.open(header_path)
                
                # Create a drawing context
                draw = ImageDraw.Draw(header_img)
                
                # Get team names with error handling
                try:
                    away_team = game_data['game_center']['awayTeam']['abbrev']
                    home_team = game_data['game_center']['homeTeam']['abbrev']
                except (KeyError, TypeError):
                    # Fallback to default team names if data is missing
                    away_team = "FLA"
                    home_team = "EDM"
                
                # Try to load Russo One font first (better text rendering), fallback to others (reduced by 1cm = 28pt from 140pt)
                try:
                    # Try to load Russo One font first (better for text rendering)
                    # Try to load font from script directory first
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    font_path = os.path.join(script_dir, 'RussoOne-Regular.ttf')
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, 110)
                    else:
                        font = ImageFont.truetype("/Users/emilyfehr8/Library/Fonts/RussoOne-Regular.ttf", 110)
                except:
                    try:
                        # Fallback to DaggerSquare font
                        font = ImageFont.truetype("/Users/emilyfehr8/Library/Fonts/DAGGERSQUARE.otf", 110)
                    except:
                        try:
                            # Fallback to Arial Bold
                            font = ImageFont.truetype("/System/Library/Fonts/Arial Bold.ttf", 110)
                        except:
                            try:
                                font = ImageFont.truetype("Arial.ttf", 110)
                            except:
                                font = ImageFont.load_default()
                
                # Determine game type from API data
                game_type = "Regular Season"  # Default
                try:
                    # Get game type from boxscore data
                    if 'boxscore' in game_data and 'gameType' in game_data['boxscore']:
                        api_game_type = game_data['boxscore']['gameType']
                        
                        # NHL Game Type Codes:
                        # 1 = Pre-season, 2 = Regular Season, 3 = Playoffs, 5 = All-Star, etc.
                        if api_game_type == 1:
                            game_type = "Preseason"
                        elif api_game_type == 2:
                            game_type = "Regular Season"
                        elif api_game_type == 3:
                            game_type = "Playoffs"
                        elif api_game_type == 5:
                            game_type = "All-Star Game"
                        else:
                            game_type = f"Game Type {api_game_type}"
                    else:
                        # Fallback: try to determine from game ID if API data not available
                        if game_id:
                            game_number = int(game_id[-2:]) if len(game_id) >= 2 else 0
                            if game_number >= 1 and game_number <= 4:
                                game_type = "Playoffs"
                            elif game_number >= 5 and game_number <= 8:
                                game_type = "Conference Finals"
                            elif game_number >= 9 and game_number <= 12:
                                game_type = "Stanley Cup Finals"
                except (ValueError, TypeError, KeyError):
                    game_type = "Regular Season"
                
                # Calculate team name text position (left-aligned, moved 3cm right)
                # For regular season, omit the 'Regular Season:' prefix
                if game_type == "Regular Season":
                    team_text = f"{away_team} vs {home_team}"
                else:
                    team_text = f"{game_type}: {away_team} vs {home_team}"
                team_bbox = draw.textbbox((0, 0), team_text, font=font)
                team_text_width = team_bbox[2] - team_bbox[0]
                team_text_height = team_bbox[3] - team_bbox[1]
                
                team_x = 20 + 233 + 28 + 56  # Left-aligned with 20px margin + 6.2cm (233px) + 1cm (28px) + 2cm (56px) to the right
                team_y = (header_img.height - team_text_height) // 2 - 20  # Move up slightly to make room for subtitle
                
                # Load team logos
                away_logo = None
                home_logo = None
                nhl_logo = None
                
                try:
                    import requests
                    from io import BytesIO
                    
                    # Get team abbreviations from boxscore data
                    away_team_abbrev = game_data['boxscore']['awayTeam']['abbrev']
                    home_team_abbrev = game_data['boxscore']['homeTeam']['abbrev']
                    
                    # Try to load team logos from ESPN API using team abbreviations
                    # Map team abbreviations to ESPN logo abbreviations
                    logo_abbrev_map = {
                        'TBL': 'tb', 'NSH': 'nsh', 'EDM': 'edm', 'FLA': 'fla',
                        'COL': 'col', 'DAL': 'dal', 'BOS': 'bos', 'TOR': 'tor',
                        'MTL': 'mtl', 'OTT': 'ott', 'BUF': 'buf', 'DET': 'det',
                        'CAR': 'car', 'WSH': 'wsh', 'PIT': 'pit', 'NYR': 'nyr',
                        'NYI': 'nyi', 'NJD': 'nj', 'PHI': 'phi', 'CBJ': 'cbj',
                        'STL': 'stl', 'MIN': 'min', 'WPG': 'wpg', 'ARI': 'ari',
                        'VGK': 'vgk', 'SJS': 'sj', 'LAK': 'la', 'ANA': 'ana',
                        'CGY': 'cgy', 'VAN': 'van', 'SEA': 'sea', 'CHI': 'chi'
                    }
                    
                    away_logo_abbrev = logo_abbrev_map.get(away_team_abbrev, away_team_abbrev.lower())
                    home_logo_abbrev = logo_abbrev_map.get(home_team_abbrev, home_team_abbrev.lower())
                    
                    away_logo_url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{away_logo_abbrev}.png"
                    home_logo_url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{home_logo_abbrev}.png"
                    nhl_logo_url = "https://a.espncdn.com/i/teamlogos/leagues/500/nhl.png"
                    
                    # Download NHL logo
                    nhl_response = requests.get(nhl_logo_url, timeout=5)
                    if nhl_response.status_code == 200:
                        nhl_logo = PILImage.open(BytesIO(nhl_response.content))
                        nhl_logo = nhl_logo.resize((212, 184), PILImage.Resampling.LANCZOS)
                        print(f"Loaded NHL logo")
                    
                    # Download away team logo
                    away_response = requests.get(away_logo_url, timeout=5)
                    if away_response.status_code == 200:
                        away_logo = PILImage.open(BytesIO(away_response.content))
                        away_logo = away_logo.resize((240, 212), PILImage.Resampling.LANCZOS)
                        print(f"Loaded away team logo: {away_team}")
                    
                    # Download home team logo
                    home_response = requests.get(home_logo_url, timeout=5)
                    if home_response.status_code == 200:
                        home_logo = PILImage.open(BytesIO(home_response.content))
                        home_logo = home_logo.resize((240, 212), PILImage.Resampling.LANCZOS)
                        print(f"Loaded home team logo: {home_team}")
                        
                except Exception as e:
                    print(f"Could not load logos: {e}")
                
                # Draw team logos if available (positioned on the right side)
                if away_logo:
                    # Position away logo on the right side
                    away_logo_x = header_img.width - 769  # Right side with margin (moved 9.5cm/269px total inward)
                    away_logo_y = team_y - 81  # Moved down 0.8cm total (25px) from -106 to -81
                    header_img.paste(away_logo, (away_logo_x, away_logo_y), away_logo)
                
                if home_logo:
                    # Position home logo to the right of away logo
                    home_logo_x = header_img.width - 519  # Further right (moved 9.5cm/269px total inward)
                    home_logo_y = team_y - 81  # Moved down 0.8cm total (25px) from -106 to -81
                    header_img.paste(home_logo, (home_logo_x, home_logo_y), home_logo)
                
                # Draw NHL logo under the team logos if available
                if nhl_logo:
                    # Position NHL logo centered under the team logos (moved up by 1cm = 28pt)
                    nhl_logo_x = header_img.width - 601  # Centered between the two team logos (moved 8cm/241px total inward)
                    nhl_logo_y = team_y + 92  # Below the team logos with proper spacing (moved up 28pt)
                    header_img.paste(nhl_logo, (nhl_logo_x, nhl_logo_y), nhl_logo)
                
                # Draw team name white text with black outline for better visibility
                draw.text((team_x-1, team_y-1), team_text, font=font, fill=(0, 0, 0))  # Black outline
                draw.text((team_x+1, team_y-1), team_text, font=font, fill=(0, 0, 0))  # Black outline
                draw.text((team_x-1, team_y+1), team_text, font=font, fill=(0, 0, 0))  # Black outline
                draw.text((team_x+1, team_y+1), team_text, font=font, fill=(0, 0, 0))  # Black outline
                draw.text((team_x, team_y), team_text, font=font, fill=(255, 255, 255))  # White text
                
                # Create subtitle font (45pt) - Russo One first for better text rendering
                try:
                    # Try to load font from script directory first
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    font_path = os.path.join(script_dir, 'RussoOne-Regular.ttf')
                    if os.path.exists(font_path):
                        subtitle_font = ImageFont.truetype(font_path, 43)
                    else:
                        subtitle_font = ImageFont.truetype("/Users/emilyfehr8/Library/Fonts/RussoOne-Regular.ttf", 43)
                except:
                    try:
                        subtitle_font = ImageFont.truetype("/Users/emilyfehr8/Library/Fonts/DAGGERSQUARE.otf", 43)
                    except:
                        try:
                            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial Bold.ttf", 43)
                        except:
                            try:
                                subtitle_font = ImageFont.truetype("Arial.ttf", 43)
                            except:
                                subtitle_font = ImageFont.load_default()
                
                # Get game date and score for subtitle
                try:
                    # Try to get date from play-by-play data first (most reliable)
                    play_by_play = game_data.get('play_by_play', {})
                    if play_by_play and 'gameDate' in play_by_play:
                        game_date = play_by_play['gameDate']
                    else:
                        # Fallback to game_center data
                        game_date = game_data['game_center']['game']['gameDate']
                    
                    # Get scores from boxscore (most reliable)
                    boxscore = game_data['boxscore']
                    away_score = boxscore['awayTeam']['score']
                    home_score = boxscore['homeTeam']['score']
                    away_team_id = boxscore['awayTeam']['id']
                    home_team_id = boxscore['homeTeam']['id']
                    
                    # Determine winning team
                    if away_score > home_score:
                        winner = away_team
                    elif home_score > away_score:
                        winner = home_team
                    else:
                        winner = "TIE"
                    
                    # Determine game ending type (OT/SO only, blank for regulation)
                    game_ending = ""
                    try:
                        # Check for OT/SO from play-by-play data
                        play_by_play_data = game_data.get('play_by_play', {})
                        if play_by_play_data and 'plays' in play_by_play_data:
                            for play in play_by_play_data['plays']:
                                if play.get('typeDescKey') == 'goal':
                                    period_type = play.get('periodDescriptor', {}).get('periodType', 'REG')
                                    if period_type == 'SO':
                                        game_ending = "SO"
                                        break
                                    elif period_type == 'OT':
                                        game_ending = "OT"
                                        # Don't break - keep checking for SO
                    except:
                        game_ending = ""
                        
                except (KeyError, TypeError):
                    # If we can't get real data, use sample data
                    game_date = "2024-06-15"
                    away_score = 3
                    home_score = 2
                    winner = away_team
                    game_ending = ""
                
                # Calculate subtitle text position (left-aligned below team names, moved up 2cm)
                # Only add game ending indicator if it's OT or SO
                if game_ending:
                    subtitle_text = f"Post Game Report: {game_date} | {away_score}-{home_score} {winner} WINS ({game_ending})"
                else:
                    subtitle_text = f"Post Game Report: {game_date} | {away_score}-{home_score} {winner} WINS"
                subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
                subtitle_text_width = subtitle_bbox[2] - subtitle_bbox[0]
                subtitle_text_height = subtitle_bbox[3] - subtitle_bbox[1]
                
                subtitle_x = 20 + 233 + 28 + 56  # Left-aligned with same margin as title (moved 6.2cm + 1cm + 2cm right total)
                subtitle_y = team_y + team_text_height + 29  # Position 1cm (29 points) below team names (moved up 2cm)
                
                # Draw subtitle in #7F7F7F color
                draw.text((subtitle_x, subtitle_y), subtitle_text, font=subtitle_font, fill=(127, 127, 127))  # #7F7F7F
                
                # Draw grey line 1.5 cm below subtitle
                # 0.5 cm thick = ~14 pixels, width matches subtitle text width
                line_y = subtitle_y + subtitle_text_height + 42  # 1.5 cm = ~42 points (moved down 1cm from previous 14)
                line_start_x = subtitle_x  # Start at same x position as subtitle
                line_width = subtitle_text_width  # Match the width of the subtitle text
                line_thickness = 14  # 0.5 cm = ~14 pixels
                
                # Draw the grey line
                draw.rectangle(
                    [(line_start_x, line_y), (line_start_x + line_width, line_y + line_thickness)],
                    fill=(200, 200, 200)  # Light grey color
                )
                
                # Save the modified header
                modified_header_path = "temp_header_with_teams.png"
                header_img.save(modified_header_path)
                
                # Create ReportLab Image object - extend beyond margins to eliminate white edges
                header_image = Image(modified_header_path, width=756, height=180)  # Increased height to cover top white space
                header_image.hAlign = 'CENTER'
                header_image.vAlign = 'TOP'
                
                # Store the temp file path for cleanup
                header_image.temp_path = modified_header_path
                
                return header_image
            else:
                print(f"Warning: Header image not found at {header_path}")
                return None
                
        except Exception as e:
            print(f"Warning: Could not create header image: {e}")
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
            textColor=colors.darkgreen,
            alignment=TA_CENTER,
            spaceAfter=4,
            fontName='RussoOne-Regular'
        )
    
    def create_score_summary(self, game_data):
        """Create the score summary section"""
        story = []
        
        # Get team info
        boxscore = game_data['boxscore']
        away_team = boxscore['awayTeam']
        home_team = boxscore['homeTeam']
        
        story.append(Paragraph(f"FINAL SCORE", self.title_style))
        story.append(Spacer(1, 20))
        
        # Calculate period scores from play-by-play data
        away_period_scores = [0, 0, 0, 0]  # 1st, 2nd, 3rd, OT
        home_period_scores = [0, 0, 0, 0]  # 1st, 2nd, 3rd, OT
        
        play_by_play = game_data.get('play_by_play')
        if play_by_play and 'plays' in play_by_play:
            for play in play_by_play['plays']:
                if play.get('typeDescKey') == 'goal':
                    details = play.get('details', {})
                    period = play.get('periodDescriptor', {}).get('number', 1)
                    event_team = details.get('eventOwnerTeamId')
                    
                    # Adjust period index (period 1 = index 0, etc.)
                    period_index = min(period - 1, 3)  # Cap at OT (index 3)
                    
                    if event_team == away_team['id']:
                        away_period_scores[period_index] += 1
                    elif event_team == home_team['id']:
                        home_period_scores[period_index] += 1
        
        # Calculate totals
        away_total = sum(away_period_scores)
        home_total = sum(home_period_scores)
        
        # Score display
        score_data = [
            ['', '1st', '2nd', '3rd', 'OT', 'Total'],
            [away_team['abbrev'], 
             away_period_scores[0],
             away_period_scores[1], 
             away_period_scores[2],
             away_period_scores[3],
             away_total],
            [home_team['abbrev'],
             home_period_scores[0],
             home_period_scores[1],
             home_period_scores[2], 
             home_period_scores[3],
             home_total]
        ]
        
        score_table = Table(score_data, colWidths=[1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'RussoOne-Regular'),
        ]))
        
        story.append(score_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_player_roster_map(self, play_by_play):
        """Create a mapping of player IDs to player info"""
        roster_map = {}
        if 'rosterSpots' in play_by_play:
            for player in play_by_play['rosterSpots']:
                player_id = player['playerId']
                roster_map[player_id] = {
                    'firstName': player['firstName']['default'],
                    'lastName': player['lastName']['default'],
                    'sweaterNumber': player['sweaterNumber'],
                    'positionCode': player['positionCode'],
                    'teamId': player['teamId']
                }
        return roster_map

    def _calculate_team_stats_from_play_by_play(self, game_data, team_side):
        """Calculate team statistics from play-by-play data"""
        try:
            play_by_play = game_data.get('play_by_play')
            if not play_by_play or 'plays' not in play_by_play:
                return self._calculate_team_stats_from_players(game_data['boxscore'], team_side)
            
            # Get team ID for filtering
            boxscore = game_data['boxscore']
            team_id = boxscore[team_side]['id']
            
            # Create player roster map
            roster_map = self._create_player_roster_map(play_by_play)
            
            # Initialize counters
            stats = {
                'hits': 0,
                'penaltyMinutes': 0,
                'blockedShots': 0,
                'giveaways': 0,
                'takeaways': 0,
                'powerPlayGoals': 0,
                'powerPlayOpportunities': 0,
                'faceoffWins': 0,
                'faceoffTotal': 0,
                'shotsOnGoal': 0,
                'missedShots': 0
            }
            
            # Process each play
            for play in play_by_play['plays']:
                play_details = play.get('details', {})
                event_owner_team_id = play_details.get('eventOwnerTeamId')
                play_type = play.get('typeDescKey', '')
                
                # Only count plays for this team
                if event_owner_team_id == team_id:
                    if play_type == 'hit':
                        stats['hits'] += 1
                    elif play_type == 'shot-on-goal':
                        stats['shotsOnGoal'] += 1
                    elif play_type == 'missed-shot':
                        stats['missedShots'] += 1
                    elif play_type == 'blocked-shot':
                        stats['blockedShots'] += 1
                    elif play_type == 'giveaway':
                        stats['giveaways'] += 1
                    elif play_type == 'takeaway':
                        stats['takeaways'] += 1
                    elif play_type == 'faceoff':
                        stats['faceoffTotal'] += 1
                        # Check if this team won the faceoff
                        winning_player_id = play_details.get('winningPlayerId')
                        if winning_player_id and winning_player_id in roster_map:
                            if roster_map[winning_player_id]['teamId'] == team_id:
                                stats['faceoffWins'] += 1
                    elif play_type == 'penalty':
                        duration = play_details.get('duration', 0)
                        stats['penaltyMinutes'] += duration
                    elif play_type == 'goal':
                        # Check if it's a power play goal
                        situation_code = play.get('situationCode', '')
                        if situation_code.startswith('14'):  # Power play situation
                            stats['powerPlayGoals'] += 1
                
                # Count power play opportunities (penalties against the other team)
                elif event_owner_team_id != team_id and play_type == 'penalty':
                    situation_code = play.get('situationCode', '')
                    if situation_code.startswith('14'):  # Power play situation
                        stats['powerPlayOpportunities'] += 1
            
            return stats
            
        except (KeyError, TypeError) as e:
            print(f"Error calculating stats from play-by-play: {e}")
            # Fallback to player stats
            return self._calculate_team_stats_from_players(game_data['boxscore'], team_side)
    
    def _calculate_player_stats_from_play_by_play(self, game_data, team_side):
        """Calculate individual player statistics from play-by-play data"""
        try:
            play_by_play = game_data.get('play_by_play')
            if not play_by_play or 'plays' not in play_by_play:
                return {}
            
            # Get team ID for filtering
            boxscore = game_data['boxscore']
            team_id = boxscore[team_side]['id']
            
            # Create player roster map
            roster_map = self._create_player_roster_map(play_by_play)
            
            # Initialize player stats
            player_stats = {}
            for player_id, player_info in roster_map.items():
                if player_info['teamId'] == team_id:
                    player_stats[player_id] = {
                        'name': f"{player_info['firstName']} {player_info['lastName']}",
                        'position': player_info['positionCode'],
                        'sweaterNumber': player_info['sweaterNumber'],
                        'goals': 0,
                        'assists': 0,
                        'points': 0,
                        'plusMinus': 0,
                        'pim': 0,
                        'sog': 0,
                        'hits': 0,
                        'blockedShots': 0,
                        'giveaways': 0,
                        'takeaways': 0,
                        'faceoffWins': 0,
                        'faceoffTotal': 0,
                        'primaryAssists': 0,
                        'secondaryAssists': 0,
                        'penaltiesDrawn': 0,
                        'penaltiesTaken': 0,
                        'goalsFor': 0,
                        'goalsAgainst': 0,
                        'gameScore': 0.0
                    }
            
            # Process each play
            for play in play_by_play['plays']:
                play_details = play.get('details', {})
                event_owner_team_id = play_details.get('eventOwnerTeamId')
                play_type = play.get('typeDescKey', '')
                
                # Only process plays for this team
                if event_owner_team_id == team_id:
                    # Get the primary player involved
                    primary_player_id = None
                    if play_type == 'goal':
                        primary_player_id = play_details.get('scoringPlayerId')
                        assist1_player_id = play_details.get('assist1PlayerId')
                        assist2_player_id = play_details.get('assist2PlayerId')
                        
                        # Count goal
                        if primary_player_id and primary_player_id in player_stats:
                            player_stats[primary_player_id]['goals'] += 1
                            player_stats[primary_player_id]['points'] += 1
                        
                        # Count assists (primary and secondary)
                        if assist1_player_id and assist1_player_id in player_stats:
                            player_stats[assist1_player_id]['assists'] += 1
                            player_stats[assist1_player_id]['primaryAssists'] += 1
                            player_stats[assist1_player_id]['points'] += 1
                        if assist2_player_id and assist2_player_id in player_stats:
                            player_stats[assist2_player_id]['assists'] += 1
                            player_stats[assist2_player_id]['secondaryAssists'] += 1
                            player_stats[assist2_player_id]['points'] += 1
                    
                    elif play_type == 'shot-on-goal':
                        primary_player_id = play_details.get('shootingPlayerId')
                        if primary_player_id and primary_player_id in player_stats:
                            player_stats[primary_player_id]['sog'] += 1
                    
                    elif play_type == 'hit':
                        primary_player_id = play_details.get('hittingPlayerId')
                        if primary_player_id and primary_player_id in player_stats:
                            player_stats[primary_player_id]['hits'] += 1
                    
                    elif play_type == 'blocked-shot':
                        primary_player_id = play_details.get('blockingPlayerId')
                        if primary_player_id and primary_player_id in player_stats:
                            player_stats[primary_player_id]['blockedShots'] += 1
                    
                    elif play_type == 'giveaway':
                        primary_player_id = play_details.get('playerId')
                        if primary_player_id and primary_player_id in player_stats:
                            player_stats[primary_player_id]['giveaways'] += 1
                    
                    elif play_type == 'takeaway':
                        primary_player_id = play_details.get('playerId')
                        if primary_player_id and primary_player_id in player_stats:
                            player_stats[primary_player_id]['takeaways'] += 1
                    
                    elif play_type == 'faceoff':
                        winning_player_id = play_details.get('winningPlayerId')
                        losing_player_id = play_details.get('losingPlayerId')
                        
                        if winning_player_id and winning_player_id in player_stats:
                            player_stats[winning_player_id]['faceoffWins'] += 1
                            player_stats[winning_player_id]['faceoffTotal'] += 1
                        if losing_player_id and losing_player_id in player_stats:
                            player_stats[losing_player_id]['faceoffTotal'] += 1
                    
                    elif play_type == 'penalty':
                        primary_player_id = play_details.get('committedByPlayerId')
                        duration = play_details.get('duration', 0)
                        if primary_player_id and primary_player_id in player_stats:
                            player_stats[primary_player_id]['pim'] += duration
                            player_stats[primary_player_id]['penaltiesTaken'] += 1
                        
                        # Check if there's a player who drew the penalty
                        drawn_by_player_id = play_details.get('drawnByPlayerId')
                        if drawn_by_player_id and drawn_by_player_id in player_stats:
                            player_stats[drawn_by_player_id]['penaltiesDrawn'] += 1
            
            # Calculate Game Score for each player
            for player_id, stats in player_stats.items():
                stats['gameScore'] = self._calculate_game_score(stats)
            
            return player_stats
            
        except (KeyError, TypeError) as e:
            print(f"Error calculating player stats from play-by-play: {e}")
            return {}
    
    def _calculate_game_score(self, player_stats):
        """Calculate Game Score using Dom Luszczyszyn formula"""
        try:
            # Game Score = 0.75×G + 0.7×A1 + 0.55×A2 + 0.075×SOG + 0.05×BLK + 0.15×PD - 0.15×PT + 0.01×FOW - 0.01×FOL + 0.15×GF - 0.15×GA
            game_score = (
                0.75 * player_stats.get('goals', 0) +
                0.7 * player_stats.get('primaryAssists', 0) +
                0.55 * player_stats.get('secondaryAssists', 0) +
                0.075 * player_stats.get('sog', 0) +
                0.05 * player_stats.get('blockedShots', 0) +
                0.15 * player_stats.get('penaltiesDrawn', 0) -
                0.15 * player_stats.get('penaltiesTaken', 0) +
                0.01 * player_stats.get('faceoffWins', 0) -
                0.01 * (player_stats.get('faceoffTotal', 0) - player_stats.get('faceoffWins', 0)) +
                0.15 * player_stats.get('goalsFor', 0) -
                0.15 * player_stats.get('goalsAgainst', 0)
            )
            return round(game_score, 2)
        except (KeyError, TypeError) as e:
            print(f"Error calculating game score: {e}")
            return 0.0
    
    def _calculate_team_stats_from_players(self, boxscore, team_side):
        """Calculate team statistics from individual player data (fallback)"""
        try:
            player_stats = boxscore['playerByGameStats'][team_side]
            
            # Initialize counters
            stats = {
                'hits': 0,
                'penaltyMinutes': 0,
                'blockedShots': 0,
                'giveaways': 0,
                'takeaways': 0,
                'powerPlayGoals': 0,
                'powerPlayOpportunities': 0,
                'faceoffWins': 0,
                'faceoffTotal': 0
            }
            
            # Sum up stats from all players (forwards, defense, goalies)
            for position_group in ['forwards', 'defense', 'goalies']:
                if position_group in player_stats:
                    for player in player_stats[position_group]:
                        stats['hits'] += player.get('hits', 0)
                        stats['penaltyMinutes'] += player.get('pim', 0)
                        stats['blockedShots'] += player.get('blockedShots', 0)
                        stats['giveaways'] += player.get('giveaways', 0)
                        stats['takeaways'] += player.get('takeaways', 0)
                        stats['powerPlayGoals'] += player.get('powerPlayGoals', 0)
                        
                        # Faceoff calculations (only for forwards)
                        if position_group == 'forwards':
                            faceoff_pct = player.get('faceoffWinningPctg', 0)
                            if faceoff_pct > 0:  # Only count if player took faceoffs
                                # Estimate total faceoffs from percentage (this is approximate)
                                estimated_faceoffs = 10  # Rough estimate
                                wins = int(faceoff_pct * estimated_faceoffs)
                                stats['faceoffWins'] += wins
                                stats['faceoffTotal'] += estimated_faceoffs
            
            return stats
            
        except (KeyError, TypeError):
            # Return default values if data is missing
            return {
                'hits': 0,
                'penaltyMinutes': 0,
                'blockedShots': 0,
                'giveaways': 0,
                'takeaways': 0,
                'powerPlayGoals': 0,
                'powerPlayOpportunities': 0,
                'faceoffWins': 0,
                'faceoffTotal': 0
            }
    
    def create_team_stats_comparison(self, game_data):
        """Create period-by-period team statistics comparison table"""
        story = []
        
        # Create a horizontal bar behind the title using a table
        # Get home team color for the bar
        boxscore = game_data['boxscore']
        home_team = boxscore['homeTeam']
        
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
            'UTA': colors.Color(105/255, 179/255, 231/255),  # Utah Hockey Club - Mountain Blue
            'CHI': colors.Color(207/255, 10/255, 44/255)  # Chicago Blackhawks Red
        }
        
        home_team_color = team_colors.get(home_team['abbrev'], colors.white)
        
        # Create title bar with home team color background
        title_bar_data = [["Period by Period"]]
        title_bar_table = Table(title_bar_data, colWidths=[7.5*inch])  # Full width
        title_bar_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), home_team_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTWEIGHT', (0, 0), (-1, -1), 'BOLD'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(title_bar_table)
        story.append(Spacer(1, 5))  # Reduced spacing
        
        try:
            boxscore = game_data['boxscore']
            away_team = boxscore['awayTeam']
            home_team = boxscore['homeTeam']
            
            # Calculate Game Score and xG by period for both teams
            away_gs_periods, away_xg_periods = self._calculate_period_metrics(game_data, away_team['id'], 'away')
            home_gs_periods, home_xg_periods = self._calculate_period_metrics(game_data, home_team['id'], 'home')
            
            # Calculate pass metrics for both teams
            away_ew_passes, away_ns_passes, away_behind_net = self._calculate_pass_metrics(game_data, away_team['id'], 'away')
            home_ew_passes, home_ns_passes, home_behind_net = self._calculate_pass_metrics(game_data, home_team['id'], 'home')
            
        # Calculate zone metrics for both teams
            away_zone_metrics = self._calculate_zone_metrics(game_data, away_team['id'], 'away')
            home_zone_metrics = self._calculate_zone_metrics(game_data, home_team['id'], 'home')
            
            # Calculate real period-by-period stats from NHL API data
            away_period_stats = self._calculate_real_period_stats(game_data, away_team['id'], 'away')
            home_period_stats = self._calculate_real_period_stats(game_data, home_team['id'], 'home')
            
            # Calculate real period scores from play-by-play data (including OT/SO)
            away_period_scores, away_ot_goals, away_so_goals = self._calculate_goals_by_period(game_data, away_team['id'])
            home_period_scores, home_ot_goals, home_so_goals = self._calculate_goals_by_period(game_data, home_team['id'])
            
            # Determine if game went to OT or SO
            has_ot = away_ot_goals > 0 or home_ot_goals > 0
            has_so = away_so_goals > 0 or home_so_goals > 0
            
            # Create mini team logos for the table
            away_logo_img = None
            home_logo_img = None
            
            try:
                # Get logo abbreviations from the mapping we created earlier
                logo_abbrev_map = {
                    'TBL': 'tb', 'NSH': 'nsh', 'EDM': 'edm', 'FLA': 'fla',
                    'COL': 'col', 'DAL': 'dal', 'BOS': 'bos', 'TOR': 'tor',
                    'MTL': 'mtl', 'OTT': 'ott', 'BUF': 'buf', 'DET': 'det',
                    'CAR': 'car', 'WSH': 'wsh', 'PIT': 'pit', 'NYR': 'nyr',
                    'NYI': 'nyi', 'NJD': 'nj', 'PHI': 'phi', 'CBJ': 'cbj',
                    'STL': 'stl', 'MIN': 'min', 'WPG': 'wpg', 'ARI': 'ari',
                    'VGK': 'vgk', 'SJS': 'sj', 'LAK': 'la', 'ANA': 'ana',
                    'CGY': 'cgy', 'VAN': 'van', 'SEA': 'sea', 'CHI': 'chi'
                }
                
                away_logo_abbrev = logo_abbrev_map.get(away_team['abbrev'], away_team['abbrev'].lower())
                home_logo_abbrev = logo_abbrev_map.get(home_team['abbrev'], home_team['abbrev'].lower())
                
                # Download and resize logos for table use (mini size)
                away_logo_url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{away_logo_abbrev}.png"
                home_logo_url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{home_logo_abbrev}.png"
                
                away_response = requests.get(away_logo_url, timeout=5)
                if away_response.status_code == 200:
                    away_logo = PILImage.open(BytesIO(away_response.content))
                    away_logo = away_logo.resize((15, 15), PILImage.Resampling.LANCZOS)  # Much smaller size
                    away_logo_img = Image(away_logo_url, width=15, height=15)
                
                home_response = requests.get(home_logo_url, timeout=5)
                if home_response.status_code == 200:
                    home_logo = PILImage.open(BytesIO(home_response.content))
                    home_logo = home_logo.resize((15, 15), PILImage.Resampling.LANCZOS)  # Much smaller size
                    home_logo_img = Image(home_logo_url, width=15, height=15)
                    
            except Exception as e:
                print(f"Could not load mini logos: {e}")
            
            # Create period-by-period data table with all advanced metrics (dynamically handle OT/SO)
            stats_data = [
                # Header row
                ['Period', 'GF', 'S', 'CF%', 'PP', 'PIM', 'Hits', 'FO%', 'BLK', 'GV', 'TK', 'GS', 'xG', 'NZT', 'NZTS', 'OZS', 'NZS', 'DZS', 'FC', 'Rush'],
                # Away team logo row
                [away_team['abbrev'], away_logo_img if away_logo_img else '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            ]
            
            # Add regulation periods for away team
            for i in range(3):
                stats_data.append([str(i+1), str(away_period_scores[i]), str(away_period_stats['shots'][i]), f"{away_period_stats['corsi_pct'][i]:.1f}%", 
                    f"{away_period_stats['pp_goals'][i]}/{away_period_stats['pp_attempts'][i]}", str(away_period_stats['pim'][i]), 
                    str(away_period_stats['hits'][i]), f"{away_period_stats['fo_pct'][i]:.1f}%", str(away_period_stats['bs'][i]), 
                    str(away_period_stats['gv'][i]), str(away_period_stats['tk'][i]), f'{away_gs_periods[i]:.1f}', f'{away_xg_periods[i]:.2f}', 
                    f'{away_zone_metrics["nz_turnovers"][i]}', f'{away_zone_metrics["nz_turnovers_to_shots"][i]}',
                    f'{away_zone_metrics["oz_originating_shots"][i]}', f'{away_zone_metrics["nz_originating_shots"][i]}', f'{away_zone_metrics["dz_originating_shots"][i]}',
                    f'{away_zone_metrics["fc_cycle_sog"][i]}', f'{away_zone_metrics["rush_sog"][i]}'])
            
            # Add OT row if applicable
            if has_ot:
                stats_data.append(['OT', str(away_ot_goals), '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'])
            
            # Add SO row if applicable  
            if has_so:
                stats_data.append(['SO', str(away_so_goals), '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'])
            
            # Add Final row for away team
            away_total_goals = sum(away_period_scores) + away_ot_goals + away_so_goals
            stats_data.append(['Final', str(away_total_goals), str(sum(away_period_stats['shots'])), f"{sum(away_period_stats['corsi_pct'])/3:.1f}%",
                f"{sum(away_period_stats['pp_goals'])}/{sum(away_period_stats['pp_attempts'])}", str(sum(away_period_stats['pim'])), 
                str(sum(away_period_stats['hits'])), f"{sum(away_period_stats['fo_pct'])/3:.1f}%", str(sum(away_period_stats['bs'])), 
                str(sum(away_period_stats['gv'])), str(sum(away_period_stats['tk'])), f'{sum(away_gs_periods):.1f}', f'{sum(away_xg_periods):.2f}',
                f'{sum(away_zone_metrics["nz_turnovers"])}', f'{sum(away_zone_metrics["nz_turnovers_to_shots"])}',
                 f'{sum(away_zone_metrics["oz_originating_shots"])}', f'{sum(away_zone_metrics["nz_originating_shots"])}', f'{sum(away_zone_metrics["dz_originating_shots"])}',
                f'{sum(away_zone_metrics["fc_cycle_sog"])}', f'{sum(away_zone_metrics["rush_sog"])}'])
            
            # Home team logo row
            stats_data.append([home_team['abbrev'], home_logo_img if home_logo_img else '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
            
            # Add regulation periods for home team
            for i in range(3):
                stats_data.append([str(i+1), str(home_period_scores[i]), str(home_period_stats['shots'][i]), f"{home_period_stats['corsi_pct'][i]:.1f}%",
                    f"{home_period_stats['pp_goals'][i]}/{home_period_stats['pp_attempts'][i]}", str(home_period_stats['pim'][i]), 
                    str(home_period_stats['hits'][i]), f"{home_period_stats['fo_pct'][i]:.1f}%", str(home_period_stats['bs'][i]), 
                    str(home_period_stats['gv'][i]), str(home_period_stats['tk'][i]), f'{home_gs_periods[i]:.1f}', f'{home_xg_periods[i]:.2f}',
                    f'{home_zone_metrics["nz_turnovers"][i]}', f'{home_zone_metrics["nz_turnovers_to_shots"][i]}',
                    f'{home_zone_metrics["oz_originating_shots"][i]}', f'{home_zone_metrics["nz_originating_shots"][i]}', f'{home_zone_metrics["dz_originating_shots"][i]}',
                    f'{home_zone_metrics["fc_cycle_sog"][i]}', f'{home_zone_metrics["rush_sog"][i]}'])
            
            # Add OT row if applicable
            if has_ot:
                stats_data.append(['OT', str(home_ot_goals), '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'])
            
            # Add SO row if applicable
            if has_so:
                stats_data.append(['SO', str(home_so_goals), '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'])
            
            # Add Final row for home team
            home_total_goals = sum(home_period_scores) + home_ot_goals + home_so_goals
            stats_data.append(['Final', str(home_total_goals), str(sum(home_period_stats['shots'])), f"{sum(home_period_stats['corsi_pct'])/3:.1f}%",
                f"{sum(home_period_stats['pp_goals'])}/{sum(home_period_stats['pp_attempts'])}", str(sum(home_period_stats['pim'])), 
                str(sum(home_period_stats['hits'])), f"{sum(home_period_stats['fo_pct'])/3:.1f}%", str(sum(home_period_stats['bs'])), 
                str(sum(home_period_stats['gv'])), str(sum(home_period_stats['tk'])), f'{sum(home_gs_periods):.1f}', f'{sum(home_xg_periods):.2f}',
                f'{sum(home_zone_metrics["nz_turnovers"])}', f'{sum(home_zone_metrics["nz_turnovers_to_shots"])}',
                 f'{sum(home_zone_metrics["oz_originating_shots"])}', f'{sum(home_zone_metrics["nz_originating_shots"])}', f'{sum(home_zone_metrics["dz_originating_shots"])}',
                f'{sum(home_zone_metrics["fc_cycle_sog"])}', f'{sum(home_zone_metrics["rush_sog"])}'])
            
            # Get team colors (using the same team_colors dictionary defined earlier)
            away_team_color = team_colors.get(away_team['abbrev'], colors.white)
            home_team_color = team_colors.get(home_team['abbrev'], colors.white)
            
            # Calculate dynamic row positions based on OT/SO
            away_logo_row = 1
            away_data_start = 2
            away_data_end = away_data_start + 3 + (1 if has_ot else 0) + (1 if has_so else 0)  # P1,P2,P3 + OT? + SO?
            away_final_row = away_data_end
            
            home_logo_row = away_final_row + 1
            home_data_start = home_logo_row + 1
            home_data_end = home_data_start + 3 + (1 if has_ot else 0) + (1 if has_so else 0)
            home_final_row = home_data_end
            
            # Reduce font sizes and padding to fit OT/SO rows on one page
            base_font_size = 5.5 if (has_ot or has_so) else 6
            header_font_size = 4.5 if (has_ot or has_so) else 5
            
            stats_table = Table(stats_data, colWidths=[0.4*inch, 0.35*inch, 0.35*inch, 0.4*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.4*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch, 0.35*inch])
            
            # Build dynamic table style
            table_style = [
                # Header row with home team primary color
                ('BACKGROUND', (0, 0), (-1, 0), home_team_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'RussoOne-Regular'),
                ('FONTSIZE', (0, 0), (-1, 0), header_font_size),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
                ('TOPPADDING', (0, 0), (-1, 0), 3),
                
                # Away team logo row
                ('BACKGROUND', (0, away_logo_row), (-1, away_logo_row), away_team_color),
                ('TEXTCOLOR', (0, away_logo_row), (-1, away_logo_row), colors.white),
                ('FONTNAME', (0, away_logo_row), (-1, away_logo_row), 'RussoOne-Regular'),
                ('FONTSIZE', (0, away_logo_row), (-1, away_logo_row), base_font_size),
                ('FONTWEIGHT', (0, away_logo_row), (-1, away_logo_row), 'BOLD'),
                ('ALIGN', (1, away_logo_row), (1, away_logo_row), 'LEFT'),
                ('VALIGN', (1, away_logo_row), (1, away_logo_row), 'MIDDLE'),
                ('LINEBELOW', (0, away_logo_row), (-1, away_logo_row), 0, colors.transparent),
                ('LINEABOVE', (0, away_logo_row), (-1, away_logo_row), 0, colors.transparent),
                ('INNERGRID', (0, away_logo_row), (-1, away_logo_row), 0, colors.transparent),
                
                # Home team logo row
                ('BACKGROUND', (0, home_logo_row), (-1, home_logo_row), home_team_color),
                ('TEXTCOLOR', (0, home_logo_row), (-1, home_logo_row), colors.white),
                ('FONTNAME', (0, home_logo_row), (-1, home_logo_row), 'RussoOne-Regular'),
                ('FONTSIZE', (0, home_logo_row), (-1, home_logo_row), base_font_size),
                ('FONTWEIGHT', (0, home_logo_row), (-1, home_logo_row), 'BOLD'),
                ('ALIGN', (1, home_logo_row), (1, home_logo_row), 'LEFT'),
                ('VALIGN', (1, home_logo_row), (1, home_logo_row), 'MIDDLE'),
                ('LINEBELOW', (0, home_logo_row), (-1, home_logo_row), 0, colors.transparent),
                ('LINEABOVE', (0, home_logo_row), (-1, home_logo_row), 0, colors.transparent),
                ('INNERGRID', (0, home_logo_row), (-1, home_logo_row), 0, colors.transparent),
                
                # Data rows styling
                ('BACKGROUND', (0, away_data_start), (-1, away_final_row-1), colors.white),
                ('BACKGROUND', (0, home_data_start), (-1, home_final_row-1), colors.white),
                ('FONTNAME', (0, away_data_start), (-1, home_final_row), 'RussoOne-Regular'),
                ('FONTSIZE', (0, away_data_start), (-1, home_final_row), base_font_size),
                ('TOPPADDING', (0, away_data_start), (-1, home_final_row), 2),
                ('BOTTOMPADDING', (0, away_data_start), (-1, home_final_row), 2),
                
                # Grid lines
                ('GRID', (0, 0), (-1, 0), 1, colors.black),  # Header row
                ('GRID', (0, away_data_start), (-1, away_final_row), 1, colors.black),  # Away team data
                ('GRID', (0, home_data_start), (-1, home_final_row), 1, colors.black),  # Home team data
                
                # Final row highlighting
                ('BACKGROUND', (0, away_final_row), (-1, away_final_row), colors.lightgrey),
                ('BACKGROUND', (0, home_final_row), (-1, home_final_row), colors.lightgrey),
                ('FONTWEIGHT', (0, away_final_row), (-1, away_final_row), 'BOLD'),
                ('FONTWEIGHT', (0, home_final_row), (-1, home_final_row), 'BOLD'),
            ]
            
            stats_table.setStyle(TableStyle(table_style))
        
            story.append(stats_table)
            story.append(Spacer(1, 10))  # Reduced spacing to move table closer to header
            
        except Exception as e:
            print(f"Error creating team stats comparison: {e}")
            story.append(Paragraph("Team statistics comparison could not be generated.", self.normal_style))
        
        return story
    
    def _calculate_goals_by_period(self, game_data, team_id):
        """Calculate goals scored by a team in each period from play-by-play data (including OT/SO)"""
        try:
            play_by_play = game_data.get('play_by_play')
            if not play_by_play or 'plays' not in play_by_play:
                return [0, 0, 0], 0, 0  # P1, P2, P3, OT, SO
            
            goals_by_period = [0, 0, 0]
            ot_goals = 0
            so_goals = 0
            
            for play in play_by_play['plays']:
                if play.get('typeDescKey') == 'goal':
                    period = play.get('periodDescriptor', {}).get('number', 1)
                    period_type = play.get('periodDescriptor', {}).get('periodType', 'REG')
                    event_team_id = play.get('details', {}).get('eventOwnerTeamId')
                    
                    if event_team_id == team_id:
                        if period <= 3:  # Regulation periods
                            goals_by_period[period - 1] += 1
                        elif period_type == 'OT':  # Overtime
                            ot_goals += 1
                        elif period_type == 'SO':  # Shootout
                            so_goals += 1
            
            return goals_by_period, ot_goals, so_goals
        except Exception as e:
            print(f"Error calculating goals by period: {e}")
            return [0, 0, 0], 0, 0
    
    def _calculate_period_metrics(self, game_data, team_id, team_side):
        """Calculate Game Score and xG by period for a team"""
        try:
            play_by_play = game_data.get('play_by_play')
            if not play_by_play or 'plays' not in play_by_play:
                # Return default values if no play-by-play data
                return [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
            
            # Initialize period arrays (3 periods)
            game_scores = [0.0, 0.0, 0.0]
            xg_values = [0.0, 0.0, 0.0]
            
            # Get team players
            boxscore = game_data['boxscore']
            team_data = boxscore[f'{team_side}Team']
            team_players = team_data.get('players', [])
            
            # Create player ID to name mapping
            player_map = {}
            for player in team_players:
                player_map[player['id']] = player['name']
            
            # Get all plays for previous_events context
            all_plays = play_by_play['plays']
            
            # Process each play
            for play_index, play in enumerate(all_plays):
                details = play.get('details', {})
                event_team = details.get('eventOwnerTeamId')
                period = play.get('periodDescriptor', {}).get('number', 1)
                
                # Only process plays for this team
                if event_team != team_id:
                    continue
                
                # Skip if period is beyond 3 (overtime, etc.)
                if period > 3:
                    continue
                
                period_index = period - 1
                event_type = play.get('typeDescKey', '')
                
                # Get previous events for context (last 10 events)
                previous_events = all_plays[max(0, play_index-10):play_index]
                
                # Calculate Game Score components for this play
                if event_type == 'goal':
                    # Goals: 0.75 points
                    game_scores[period_index] += 0.75
                    
                    # Calculate xG for this goal using ImprovedXGModel
                    xg = self._calculate_shot_xg(details, 'goal', play, previous_events)
                    xg_values[period_index] += xg
                    
                elif event_type == 'shot-on-goal':
                    # Shots on goal: 0.075 points
                    game_scores[period_index] += 0.075
                    
                    # Calculate xG for this shot using ImprovedXGModel
                    xg = self._calculate_shot_xg(details, 'shot-on-goal', play, previous_events)
                    xg_values[period_index] += xg
                    
                elif event_type == 'missed-shot':
                    # Missed shots don't count for Game Score but count for xG
                    xg = self._calculate_shot_xg(details, 'missed-shot', play, previous_events)
                    xg_values[period_index] += xg
                    
                elif event_type == 'blocked-shot':
                    # Blocked shots: 0.05 points
                    game_scores[period_index] += 0.05
                    # Blocked shots also count for xG
                    xg = self._calculate_shot_xg(details, 'blocked-shot', play, previous_events)
                    xg_values[period_index] += xg
                    
                elif event_type == 'penalty':
                    # Penalties taken: -0.15 points
                    game_scores[period_index] -= 0.15
                    
                elif event_type == 'takeaway':
                    # Takeaways: 0.15 points
                    game_scores[period_index] += 0.15
                    
                elif event_type == 'giveaway':
                    # Giveaways: -0.15 points
                    game_scores[period_index] -= 0.15
                    
                elif event_type == 'faceoff':
                    # Faceoffs: +0.01 for wins, -0.01 for losses
                    # This is simplified - in reality we'd need to track wins/losses
                    pass
                    
                elif event_type == 'hit':
                    # Hits: 0.15 points
                    game_scores[period_index] += 0.15
            
            return game_scores, xg_values
            
        except Exception as e:
            print(f"Error calculating period metrics: {e}")
            import traceback
            traceback.print_exc()
            return [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
    
    def _calculate_shot_xg(self, shot_details, event_type, play_data, previous_events):
        """Calculate expected goals for a single shot using our ImprovedXGModel"""
        try:
            x_coord = shot_details.get('xCoord', 0)
            y_coord = shot_details.get('yCoord', 0)
            shot_type = shot_details.get('shotType', 'wrist').lower()
            
            # Get additional context from play_data
            time_in_period = play_data.get('timeInPeriod', '00:00')
            period = play_data.get('periodDescriptor', {}).get('number', 1)
            team_id = shot_details.get('eventOwnerTeamId', 0)
            
            # Parse strength state from situation code
            situation_code = play_data.get('situationCode', '1551')
            strength_state = self._parse_strength_state(situation_code)
            
            # Get score differential (simplified - would need full game state)
            score_differential = 0  # Default to tied
            
            # Build shot_data dictionary for ImprovedXGModel
            shot_data = {
                'x_coord': x_coord,
                'y_coord': y_coord,
                'shot_type': shot_type,
                'event_type': event_type,
                'time_in_period': time_in_period,
                'period': period,
                'strength_state': strength_state,
                'score_differential': score_differential,
                'team_id': team_id
            }
            
            # Use ImprovedXGModel to calculate xG
            xg = self.xg_model.calculate_xg(shot_data, previous_events)
            return xg
            
        except Exception as e:
            print(f"Error calculating shot xG: {e}")
            import traceback
            traceback.print_exc()
            return 0.0
    
    def _parse_strength_state(self, situation_code):
        """Parse situation code to get strength state (e.g., '5v5', '5v4')"""
        try:
            # Situation code format: XXYY where XX = away skaters, YY = home skaters
            if len(situation_code) >= 4:
                away_skaters = int(situation_code[0:2]) % 10  # Get last digit
                home_skaters = int(situation_code[2:4]) % 10  # Get last digit
                return f"{away_skaters}v{home_skaters}"
            return '5v5'
        except:
            return '5v5'
    
    def _calculate_single_shot_xG_advanced(self, x_coord: float, y_coord: float, zone: str, shot_type: str, event_type: str) -> float:
        """Calculate expected goal value for a single shot based on NHL analytics model"""
        import math
        
        # Base expected goal value
        base_xG = 0.0
        
        # Distance calculation (from goal line at x=89)
        distance_from_goal = ((89 - x_coord) ** 2 + (y_coord) ** 2) ** 0.5
        
        # Angle calculation (angle from goal posts)
        # Goal posts are at y = ±3 (assuming 6-foot goal width)
        angle_to_goal = self._calculate_shot_angle_advanced(x_coord, y_coord)
        
        # Zone-based adjustments
        zone_multiplier = self._get_zone_multiplier_advanced(zone, x_coord, y_coord)
        
        # Shot type adjustments
        shot_type_multiplier = self._get_shot_type_multiplier_advanced(shot_type)
        
        # Event type adjustments (shots on goal vs missed/blocked)
        event_multiplier = self._get_event_type_multiplier_advanced(event_type)
        
        # Core distance-based model (NHL standard curve)
        if distance_from_goal <= 10:
            base_xG = 0.25  # Very close to net
        elif distance_from_goal <= 20:
            base_xG = 0.15  # Close range
        elif distance_from_goal <= 35:
            base_xG = 0.08  # Medium range
        elif distance_from_goal <= 50:
            base_xG = 0.04  # Long range
        else:
            base_xG = 0.02  # Very long range
        
        # Apply angle adjustment (shots from wider angles have lower xG)
        if angle_to_goal > 45:
            angle_multiplier = 0.3  # Very wide angle
        elif angle_to_goal > 30:
            angle_multiplier = 0.5  # Wide angle
        elif angle_to_goal > 15:
            angle_multiplier = 0.8  # Moderate angle
        else:
            angle_multiplier = 1.0  # Good angle
        
        # Calculate final expected goal value
        final_xG = base_xG * zone_multiplier * shot_type_multiplier * event_multiplier * angle_multiplier
        
        # Cap at reasonable maximum
        return min(final_xG, 0.95)
    
    def _calculate_shot_angle_advanced(self, x_coord: float, y_coord: float) -> float:
        """Calculate the angle of the shot relative to the goal"""
        import math
        
        # Goal center is at (89, 0), goal posts at (89, ±3)
        distance_to_center = ((89 - x_coord) ** 2 + (y_coord) ** 2) ** 0.5
        
        if distance_to_center == 0:
            return 0
        
        # Calculate angle using law of cosines
        # Distance from shot to left post
        dist_to_left = ((89 - x_coord) ** 2 + (y_coord - 3) ** 2) ** 0.5
        # Distance from shot to right post  
        dist_to_right = ((89 - x_coord) ** 2 + (y_coord + 3) ** 2) ** 0.5
        
        # Goal width
        goal_width = 6
        
        # Use law of cosines to find angle
        if dist_to_left > 0 and dist_to_right > 0:
            cos_angle = (dist_to_left ** 2 + dist_to_right ** 2 - goal_width ** 2) / (2 * dist_to_left * dist_to_right)
            cos_angle = max(-1, min(1, cos_angle))  # Clamp to valid range
            angle = math.acos(cos_angle)
            return math.degrees(angle)
        
        return 45  # Default angle if calculation fails
    
    def _get_zone_multiplier_advanced(self, zone: str, x_coord: float, y_coord: float) -> float:
        """Get zone-based expected goal multiplier"""
        
        # High danger area (slot, crease area)
        if zone == 'O' and x_coord > 75 and abs(y_coord) < 15:
            return 1.5
        
        # Medium danger area (offensive zone, good position)
        elif zone == 'O' and x_coord > 60 and abs(y_coord) < 25:
            return 1.2
        
        # Low danger area (point shots, wide angles)
        elif zone == 'O':
            return 0.8
        
        # Neutral zone shots (rare but possible)
        elif zone == 'N':
            return 0.3
        
        # Defensive zone shots (very rare)
        elif zone == 'D':
            return 0.1
        
        return 1.0  # Default
    
    def _get_shot_type_multiplier_advanced(self, shot_type: str) -> float:
        """Get shot type-based expected goal multiplier"""
        
        shot_type = shot_type.lower()
        
        # High-danger shot types
        if shot_type in ['tip-in', 'deflection', 'backhand']:
            return 1.3
        elif shot_type in ['wrist', 'snap']:
            return 1.0
        elif shot_type in ['slap', 'slapshot']:
            return 0.9
        elif shot_type in ['wrap-around', 'wrap']:
            return 1.1
        elif shot_type in ['one-timer', 'onetime']:
            return 1.2
        
        return 1.0  # Default for unknown types
    
    def _get_event_type_multiplier_advanced(self, event_type: str) -> float:
        """Get event type-based expected goal multiplier"""
        
        if event_type == 'shot-on-goal':
            return 1.0  # Full value for shots on goal
        elif event_type == 'missed-shot':
            return 0.7  # Reduced value for missed shots
        elif event_type == 'blocked-shot':
            return 0.5  # Lower value for blocked shots
        
        return 1.0  # Default
    
    def _get_team_color(self, team_abbrev):
        """Get the primary team color based on team abbreviation"""
        team_colors = {
            # Atlantic Division
            'BOS': '#FFB81C',  # Boston Bruins - Gold
            'BUF': '#002E62',  # Buffalo Sabres - Navy Blue
            'DET': '#CE1126',  # Detroit Red Wings - Red
            'FLA': '#041E42',  # Florida Panthers - Navy Blue
            'MTL': '#AF1E2D',  # Montreal Canadiens - Red
            'OTT': '#E31837',  # Ottawa Senators - Red
            'TBL': '#002868',  # Tampa Bay Lightning - Blue
            'TOR': '#003E7E',  # Toronto Maple Leafs - Blue
            
            # Metropolitan Division
            'CAR': '#CC0000',  # Carolina Hurricanes - Red
            'CBJ': '#002654',  # Columbus Blue Jackets - Blue
            'NJD': '#CE1126',  # New Jersey Devils - Red
            'NYI': '#F57D31',  # New York Islanders - Orange
            'NYR': '#0038A8',  # New York Rangers - Blue
            'PHI': '#F74902',  # Philadelphia Flyers - Orange
            'PIT': '#FFB81C',  # Pittsburgh Penguins - Gold
            'WSH': '#C8102E',  # Washington Capitals - Red
            
            # Central Division
            'ARI': '#8C2633',  # Arizona Coyotes - Red
            'CHI': '#CF0A2C',  # Chicago Blackhawks - Red
            'COL': '#6F263D',  # Colorado Avalanche - Burgundy
            'DAL': '#006847',  # Dallas Stars - Green
            'MIN': '#154734',  # Minnesota Wild - Green
            'NSH': '#FFB81C',  # Nashville Predators - Gold
            'STL': '#002F87',  # St. Louis Blues - Blue
            'WPG': '#041E42',  # Winnipeg Jets - Navy Blue
            
            # Pacific Division
            'ANA': '#B8860B',  # Anaheim Ducks - Gold
            'CGY': '#C8102E',  # Calgary Flames - Red
            'EDM': '#FF4C00',  # Edmonton Oilers - Orange
            'LAK': '#111111',  # Los Angeles Kings - Black
            'SJS': '#006D75',  # San Jose Sharks - Teal
            'SEA': '#001628',  # Seattle Kraken - Navy Blue
            'UTA': '#69B3E7',  # Utah Hockey Club - Mountain Blue
            'VAN': '#001F5C',  # Vancouver Canucks - Blue
            'VGK': '#B4975A'   # Vegas Golden Knights - Gold
        }
        
        return team_colors.get(team_abbrev.upper(), '#666666')  # Default gray if team not found
    
    def _calculate_pass_metrics(self, game_data, team_id, team_side):
        """Calculate pass metrics by period for a team"""
        try:
            play_by_play = game_data.get('play_by_play')
            if not play_by_play or 'plays' not in play_by_play:
                return [0, 0, 0], [0, 0, 0], [0, 0, 0]  # east_west, north_south, behind_net
            
            # Initialize period arrays (3 periods)
            east_west_passes = [0, 0, 0]  # East to West and West to East
            north_south_passes = [0, 0, 0]  # North to South and South to North
            behind_net_passes = [0, 0, 0]  # Passes behind the net
            
            # Process each play
            for play in play_by_play['plays']:
                details = play.get('details', {})
                event_team = details.get('eventOwnerTeamId')
                period = play.get('periodDescriptor', {}).get('number', 1)
                
                # Only process plays for this team
                if event_team != team_id:
                    continue
                
                # Skip if period is beyond 3 (overtime, etc.)
                if period > 3:
                    continue
                
                period_index = period - 1
                event_type = play.get('typeDescKey', '')
                
                # Get coordinates (robust to alternate schema)
                x_coord = details.get('xCoord')
                y_coord = details.get('yCoord')
                if x_coord is None or y_coord is None:
                    coords = details.get('coordinates', {})
                    x_coord = coords.get('x', x_coord if x_coord is not None else 0)
                    y_coord = coords.get('y', y_coord if y_coord is not None else 0)
                
                # Process all events that have coordinates (most puck events)
                if x_coord != 0 or y_coord != 0:  # Only process events with coordinates
                    # Check if this is a behind-net event
                    if self._is_behind_net_pass(x_coord, y_coord):
                        behind_net_passes[period_index] += 1
                    
                    # Check for East-West movement
                    if self._is_east_west_pass(x_coord, y_coord):
                        east_west_passes[period_index] += 1
                    
                    # Check for North-South movement
                    if self._is_north_south_pass(x_coord, y_coord):
                        north_south_passes[period_index] += 1
            
            return east_west_passes, north_south_passes, behind_net_passes
            
        except Exception as e:
            print(f"Error calculating pass metrics: {e}")
            return [0, 0, 0], [0, 0, 0], [0, 0, 0]
    
    def _is_behind_net_pass(self, x_coord, y_coord):
        """Check if pass is behind the net (X > 89 or X < -89)"""
        return abs(x_coord) > 89
    
    def _is_east_west_pass(self, x_coord, y_coord):
        """Check if pass has significant East-West movement"""
        # Very lenient criteria to catch more events
        # Any significant X movement counts as East-West
        return abs(x_coord) > 10
    
    def _is_north_south_pass(self, x_coord, y_coord):
        """Check if pass has significant North-South movement"""
        # Very lenient criteria to catch more events
        # Any significant Y movement counts as North-South
        return abs(y_coord) > 8
    
    def _calculate_zone_metrics(self, game_data, team_id, team_side):
        """Calculate zone-specific metrics by period for a team"""
        try:
            play_by_play = game_data.get('play_by_play')
            if not play_by_play or 'plays' not in play_by_play:
                return {
                    'nz_turnovers': [0, 0, 0],
                    'nz_turnovers_to_shots': [0, 0, 0],
                    'oz_originating_shots': [0, 0, 0],
                    'nz_originating_shots': [0, 0, 0],
                    'dz_originating_shots': [0, 0, 0],
                    'fc_cycle_sog': [0, 0, 0],
                    'rush_sog': [0, 0, 0]
                }
            
            # Initialize period arrays (3 periods)
            metrics = {
                'nz_turnovers': [0, 0, 0],
                'nz_turnovers_to_shots': [0, 0, 0],
                'oz_originating_shots': [0, 0, 0],
                'nz_originating_shots': [0, 0, 0],
                'dz_originating_shots': [0, 0, 0],
                'fc_cycle_sog': [0, 0, 0],
                'rush_sog': [0, 0, 0]
            }
            
            # Track turnovers for shot-against analysis
            team_turnovers = []
            
            # Process each play
            for play in play_by_play['plays']:
                details = play.get('details', {})
                event_team = details.get('eventOwnerTeamId')
                period = play.get('periodDescriptor', {}).get('number', 1)
                
                # Skip if period is beyond 3 (overtime, etc.)
                if period > 3:
                    continue
                
                period_index = period - 1
                event_type = play.get('typeDescKey', '')
                x_coord = details.get('xCoord', 0)
                y_coord = details.get('yCoord', 0)
                
                # Determine zone
                zone = self._determine_zone(x_coord, y_coord)
                
                # Process team events
                if event_team == team_id:
                    # Track turnovers
                    if event_type in ['giveaway', 'turnover']:
                        team_turnovers.append({
                            'period': period_index,
                            'zone': zone,
                            'x': x_coord,
                            'y': y_coord
                        })
                        
                        # Count NZ turnovers
                        if zone == 'neutral':
                            metrics['nz_turnovers'][period_index] += 1
                    
                    # Track shots by originating zone
                    elif event_type in ['shot-on-goal', 'goal']:
                        if zone == 'offensive':
                            metrics['oz_originating_shots'][period_index] += 1
                        elif zone == 'neutral':
                            metrics['nz_originating_shots'][period_index] += 1
                        elif zone == 'defensive':
                            metrics['dz_originating_shots'][period_index] += 1
                        
                        # Determine shot type using proper hockey logic
                        if self._is_rush_shot(play, play_by_play['plays']):
                            metrics['rush_sog'][period_index] += 1
                        else:
                            # All non-rush shots are considered forecheck/cycle shots
                            metrics['fc_cycle_sog'][period_index] += 1
                
                # Process opponent shots after turnovers
                elif event_team != team_id and event_type in ['shot-on-goal', 'goal']:
                    # Check if this shot came after a team turnover
                    for turnover in team_turnovers:
                        if (turnover['period'] == period_index and 
                            self._is_shot_after_turnover(x_coord, y_coord, turnover, 5)):  # 5 second window
                            if turnover['zone'] == 'neutral':
                                metrics['nz_turnovers_to_shots'][period_index] += 1
                            break
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating zone metrics: {e}")
            return {
                'nz_turnovers': [0, 0, 0],
                'nz_turnovers_to_shots': [0, 0, 0],
                'oz_originating_shots': [0, 0, 0],
                'nz_originating_shots': [0, 0, 0],
                'dz_originating_shots': [0, 0, 0],
                'fc_cycle_sog': [0, 0, 0],
                'rush_sog': [0, 0, 0]
            }
    
    def _calculate_real_period_stats(self, game_data, team_id, team_side):
        """Calculate real period-by-period stats from NHL API data"""
        try:
            play_by_play = game_data.get('play_by_play')
            if not play_by_play or 'plays' not in play_by_play:
                return {
                    'shots': [0, 0, 0],
                    'corsi_pct': [50.0, 50.0, 50.0],
                    'pp_goals': [0, 0, 0],
                    'pp_attempts': [0, 0, 0],
                    'pim': [0, 0, 0],
                    'hits': [0, 0, 0],
                    'fo_pct': [50.0, 50.0, 50.0],
                    'bs': [0, 0, 0],
                    'gv': [0, 0, 0],
                    'tk': [0, 0, 0]
                }
            
            # Initialize period arrays (3 periods)
            shots = [0, 0, 0]
            corsi_for = [0, 0, 0]
            corsi_against = [0, 0, 0]
            pp_goals = [0, 0, 0]
            pp_attempts = [0, 0, 0]
            pim = [0, 0, 0]
            hits = [0, 0, 0]
            faceoffs_won = [0, 0, 0]
            faceoffs_total = [0, 0, 0]
            bs = [0, 0, 0]
            gv = [0, 0, 0]
            tk = [0, 0, 0]
            
            # Process each play
            for play in play_by_play['plays']:
                details = play.get('details', {})
                event_team = details.get('eventOwnerTeamId')
                period = play.get('periodDescriptor', {}).get('number', 1)
                
                # Skip if period is beyond 3 (overtime, etc.)
                if period > 3:
                    continue
                
                period_index = period - 1
                event_type = play.get('typeDescKey', '')
                
                # Count shots on goal
                if event_type == 'shot-on-goal' and event_team == team_id:
                    shots[period_index] += 1
                
                # Count Corsi events (shots, missed shots, blocked shots)
                if event_type in ['shot-on-goal', 'missed-shot', 'blocked-shot']:
                    if event_team == team_id:
                        corsi_for[period_index] += 1
                    else:
                        corsi_against[period_index] += 1
                
                # Count power play goals
                if event_type == 'goal' and event_team == team_id:
                    # Check if it was a power play goal (simplified)
                    if self._is_power_play_goal(play_by_play['plays'], play):
                        pp_goals[period_index] += 1
                
                # Count power play attempts (simplified)
                if event_type == 'penalty' and event_team != team_id:
                    pp_attempts[period_index] += 1
                
                # Count penalty minutes
                if event_type == 'penalty' and event_team == team_id:
                    penalty_minutes = details.get('penaltyMinutes', 2)
                    pim[period_index] += penalty_minutes
                
                # Count hits
                if event_type == 'hit' and event_team == team_id:
                    hits[period_index] += 1
                
                # Count faceoffs
                if event_type == 'faceoff':
                    if event_team == team_id:
                        faceoffs_won[period_index] += 1
                    faceoffs_total[period_index] += 1
                
                # Count blocked shots
                if event_type == 'blocked-shot' and event_team == team_id:
                    bs[period_index] += 1
                
                # Count giveaways
                if event_type == 'giveaway' and event_team == team_id:
                    gv[period_index] += 1
                
                # Count takeaways
                if event_type == 'takeaway' and event_team == team_id:
                    tk[period_index] += 1
            
            # Calculate percentages
            corsi_pct = []
            fo_pct = []
            
            for i in range(3):
                total_corsi = corsi_for[i] + corsi_against[i]
                if total_corsi > 0:
                    corsi_pct.append((corsi_for[i] / total_corsi) * 100)
                else:
                    corsi_pct.append(50.0)
                
                if faceoffs_total[i] > 0:
                    fo_pct.append((faceoffs_won[i] / faceoffs_total[i]) * 100)
                else:
                    fo_pct.append(50.0)
            
            return {
                'shots': shots,
                'corsi_pct': corsi_pct,
                'pp_goals': pp_goals,
                'pp_attempts': pp_attempts,
                'pim': pim,
                'hits': hits,
                'fo_pct': fo_pct,
                'bs': bs,
                'gv': gv,
                'tk': tk
            }
            
        except Exception as e:
            print(f"Error calculating real period stats: {e}")
            return {
                'shots': [0, 0, 0],
                'corsi_pct': [50.0, 50.0, 50.0],
                'pp_goals': [0, 0, 0],
                'pp_attempts': [0, 0, 0],
                'pim': [0, 0, 0],
                'hits': [0, 0, 0],
                'fo_pct': [50.0, 50.0, 50.0],
                'bs': [0, 0, 0],
                'gv': [0, 0, 0],
                'tk': [0, 0, 0]
            }
    
    def _is_power_play_goal(self, all_plays, goal_play):
        """Check if a goal was scored on a power play"""
        try:
            goal_index = all_plays.index(goal_play)
            goal_period = goal_play.get('periodDescriptor', {}).get('number', 1)
            
            # Look back through recent plays to find penalty
            for i in range(max(0, goal_index - 20), goal_index):
                play = all_plays[i]
                if (play.get('periodDescriptor', {}).get('number', 1) == goal_period and
                    play.get('typeDescKey') == 'penalty'):
                    return True
            return False
        except:
            return False
    
    def _determine_zone(self, x_coord, y_coord):
        """Determine which zone the coordinates are in"""
        # NHL rink zones (approximate)
        # Offensive zone: X > 25 (blue line to goal line)
        # Neutral zone: -25 <= X <= 25 (between blue lines)
        # Defensive zone: X < -25 (blue line to goal line)
        if x_coord > 25:
            return 'offensive'
        elif x_coord < -25:
            return 'defensive'
        else:
            return 'neutral'
    
    def _is_rush_shot(self, current_play, all_plays):
        """Determine if a shot is from a rush using proper hockey logic"""
        try:
            play_index = all_plays.index(current_play)
            current_team = current_play.get('details', {}).get('eventOwnerTeamId')
            current_period = current_play.get('periodDescriptor', {}).get('number', 1)
            
            # Look back through recent plays to find rush indicators
            rush_indicators = 0
            zone_entry_found = False
            quick_transition = False
            
            # Check last 5 plays for rush indicators
            for i in range(max(0, play_index - 5), play_index):
                prev_play = all_plays[i]
                prev_team = prev_play.get('details', {}).get('eventOwnerTeamId')
                prev_type = prev_play.get('typeDescKey', '')
                prev_period = prev_play.get('periodDescriptor', {}).get('number', 1)
                
                # Only consider plays from the same team and period
                if prev_team != current_team or prev_period != current_period:
                    continue
                
                # Rush indicators:
                # 1. Takeaway (steal) - indicates quick transition
                if prev_type == 'takeaway':
                    rush_indicators += 2
                    quick_transition = True
                
                # 2. Giveaway by opponent - indicates quick transition
                elif prev_type == 'giveaway':
                    rush_indicators += 1
                
                # 3. Shot block by opponent - indicates quick transition
                elif prev_type == 'blocked-shot':
                    rush_indicators += 1
                
                # 4. Faceoff win in neutral/offensive zone
                elif prev_type == 'faceoff':
                    # Check if it's in neutral or offensive zone
                    coords = prev_play.get('details', {}).get('coordinates', {})
                    x_coord = coords.get('x', 0)
                    if x_coord > 25:  # Offensive zone faceoff
                        rush_indicators += 1
                        zone_entry_found = True
                    elif abs(x_coord) <= 25:  # Neutral zone faceoff
                        rush_indicators += 0.5
                
                # 5. Pass in neutral zone - indicates controlled entry
                elif prev_type == 'pass' and abs(x_coord) <= 25:
                    rush_indicators += 0.5
                
                # 6. Shot from previous play - indicates sustained pressure
                elif prev_type in ['shot-on-goal', 'missed-shot', 'blocked-shot']:
                    rush_indicators += 0.3
            
            # Rush shot criteria:
            # - Quick transition (takeaway/giveaway) + zone entry
            # - OR high rush indicator score (3+)
            # - OR faceoff win in offensive zone + quick transition
            if (quick_transition and zone_entry_found) or rush_indicators >= 3 or (zone_entry_found and rush_indicators >= 2):
                return True
            
            return False
            
        except Exception as e:
            print(f"Error in rush shot detection: {e}")
            return False
    
    def _is_forecheck_cycle_shot(self, current_play, all_plays):
        """Determine if a shot is from forecheck/cycle using proper hockey logic"""
        try:
            play_index = all_plays.index(current_play)
            current_team = current_play.get('details', {}).get('eventOwnerTeamId')
            current_period = current_play.get('periodDescriptor', {}).get('number', 1)
            
            # Look back through recent plays to find forecheck/cycle indicators
            forecheck_indicators = 0
            cycle_indicators = 0
            forecheck_found = False
            sustained_pressure = False
            
            # Check last 8 plays for forecheck/cycle indicators
            for i in range(max(0, play_index - 8), play_index):
                prev_play = all_plays[i]
                prev_team = prev_play.get('details', {}).get('eventOwnerTeamId')
                prev_type = prev_play.get('typeDescKey', '')
                prev_period = prev_play.get('periodDescriptor', {}).get('number', 1)
                
                # Only consider plays from the same team and period
                if prev_team != current_team or prev_period != current_period:
                    continue
                
                coords = prev_play.get('details', {}).get('coordinates', {})
                x_coord = coords.get('x', 0)
                
                # Forecheck indicators:
                # 1. Takeaway in offensive zone - indicates successful forecheck
                if prev_type == 'takeaway' and x_coord > 25:
                    forecheck_indicators += 3
                    forecheck_found = True
                
                # 2. Hit in offensive zone - indicates forecheck pressure
                elif prev_type == 'hit' and x_coord > 25:
                    forecheck_indicators += 1
                
                # 3. Giveaway by opponent in their defensive zone - indicates forecheck pressure
                elif prev_type == 'giveaway' and x_coord < -25:
                    forecheck_indicators += 2
                    forecheck_found = True
                
                # Cycle indicators:
                # 4. Pass in offensive zone - indicates cycle
                elif prev_type == 'pass' and x_coord > 25:
                    cycle_indicators += 1
                    sustained_pressure = True
                
                # 5. Shot from previous play in offensive zone - indicates sustained pressure
                elif prev_type in ['shot-on-goal', 'missed-shot', 'blocked-shot'] and x_coord > 25:
                    cycle_indicators += 0.5
                    sustained_pressure = True
                
                # 6. Faceoff win in offensive zone - indicates cycle opportunity
                elif prev_type == 'faceoff' and x_coord > 25:
                    cycle_indicators += 1
                    sustained_pressure = True
                
                # 7. Multiple passes in offensive zone - indicates cycle
                elif prev_type == 'pass' and x_coord > 25:
                    cycle_indicators += 0.3
            
            # Get shot coordinates for debug
            shot_coords = current_play.get('details', {}).get('coordinates', {})
            shot_x = shot_coords.get('x', 0)
            
            # Forecheck/Cycle shot criteria (extremely lenient):
            # - Any forecheck indicators OR any cycle indicators
            # - OR just cycle indicators (0.5+)
            # - OR any forecheck pressure
            # - OR any shot in offensive zone (simplified approach)
            if (forecheck_indicators > 0 or cycle_indicators > 0 or cycle_indicators >= 0.5 or forecheck_indicators > 0 or 
                shot_x > 25):
                return True
            
            # Debug output for first few shots
            if play_index < 5:  # Only debug first 5 shots to avoid spam
                print(f"Debug - Shot {play_index}: x={shot_x}, forecheck={forecheck_indicators}, cycle={cycle_indicators}")
            
            return False
            
        except Exception as e:
            print(f"Error in forecheck/cycle shot detection: {e}")
            return False
    
    def _is_shot_after_turnover(self, shot_x, shot_y, turnover, time_window_seconds=5):
        """Check if shot occurred after a turnover within time window"""
        # Simplified - in reality would need timestamp comparison
        # For now, just check if shot is in same general area
        distance = ((shot_x - turnover['x']) ** 2 + (shot_y - turnover['y']) ** 2) ** 0.5
        return distance < 50  # Within 50 units
    
    def create_player_performance(self, game_data):
        """Create top 5 players by Game Score across both teams"""
        story = []
        
        # Removed title as requested
        
        boxscore = game_data['boxscore']
        
        # Get player stats from play-by-play data for both teams
        away_team = boxscore['awayTeam']
        home_team = boxscore['homeTeam']
        away_player_stats = self._calculate_player_stats_from_play_by_play(game_data, 'awayTeam')
        home_player_stats = self._calculate_player_stats_from_play_by_play(game_data, 'homeTeam')
        
        # Get all players from both teams
        all_players = []
        
        # Add away team players
        if away_player_stats:
            for player in away_player_stats.values():
                all_players.append({
                    'player': f"#{player['sweaterNumber']} {player['name']}",
                    'team': away_team['abbrev'],
                    'position': player['position'],
                    'goals': player['goals'],
                    'assists': player['assists'],
                    'points': player['points'],
                    'plusMinus': player['plusMinus'],
                    'pim': player['pim'],
                    'sog': player['sog'],
                    'hits': player['hits'],
                    'blockedShots': player['blockedShots'],
                    'gameScore': player['gameScore']
                })
        
        # Add home team players
        if home_player_stats:
            for player in home_player_stats.values():
                all_players.append({
                    'player': f"#{player['sweaterNumber']} {player['name']}",
                    'team': home_team['abbrev'],
                    'position': player['position'],
                    'goals': player['goals'],
                    'assists': player['assists'],
                    'points': player['points'],
                    'plusMinus': player['plusMinus'],
                    'pim': player['pim'],
                    'sog': player['sog'],
                    'hits': player['hits'],
                    'blockedShots': player['blockedShots'],
                    'gameScore': player['gameScore']
                })
        
        # Sort by Game Score, then points, then goals (descending)
        all_players.sort(key=lambda x: (x['gameScore'], x['points'], x['goals']), reverse=True)
        
        # Take top 5 players
        top_5_players = all_players[:5]
        
        if top_5_players:
            # Create table data with team indicators
            table_data = []
            headers = ["Player", "Team", "GS"]
            table_data.append(headers)
            
            for player in top_5_players:
                table_data.append([
                    player['player'],
                    player['team'],
                    f"{player['gameScore']:.1f}" if player['gameScore'] > 0 else "N/A"
                ])
            
            # Get home team color for header
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
                'UTA': colors.Color(105/255, 179/255, 231/255),  # Utah Hockey Club - Mountain Blue
                'CHI': colors.Color(207/255, 10/255, 44/255)  # Chicago Blackhawks Red
            }
            
            home_team_color = team_colors.get(home_team['abbrev'], colors.white)
            
            # Create table with column widths matching the reference image
            player_table = Table(table_data, colWidths=[1.5*inch, 0.4*inch, 0.4*inch])
            player_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), home_team_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'RussoOne-Regular'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('FONTNAME', (0, 1), (-1, -1), 'RussoOne-Regular'),
                # Highlight the top player
                ('BACKGROUND', (0, 1), (-1, 1), colors.yellow),
                ('FONTNAME', (0, 1), (-1, 1), 'RussoOne-Regular'),
                ('FONTSIZE', (0, 1), (-1, 1), 8),
            ]))
            
            # Add the table directly (positioning will be handled by side-by-side layout)
            story.append(player_table)
            
            # Add note about Game Score
            story.append(Spacer(1, 10))
            story.append(Paragraph("<i>Top players ranked by Game Score (GS) - a comprehensive metric combining goals, assists, shots, hits, and other key performance indicators.</i>", self.normal_style))
        
        story.append(Spacer(1, 20))
        return story
    
    def create_side_by_side_tables(self, game_data):
        """Create separate layout for advanced metrics and top players tables"""
        story = []
        
        # Check if game went to OT/SO to adjust positioning
        boxscore = game_data['boxscore']
        away_team = boxscore['awayTeam']
        home_team = boxscore['homeTeam']
        
        # Calculate if game has OT/SO
        away_period_scores, away_ot_goals, away_so_goals = self._calculate_goals_by_period(game_data, away_team['id'])
        home_period_scores, home_ot_goals, home_so_goals = self._calculate_goals_by_period(game_data, home_team['id'])
        has_ot_or_so = (away_ot_goals > 0 or home_ot_goals > 0 or away_so_goals > 0 or home_so_goals > 0)
        
        # Get home team color for the title bar
        team_colors = {
            'TBL': colors.Color(0/255, 40/255, 104/255),  # Tampa Bay Lightning Blue
            'NSH': colors.Color(255/255, 184/255, 28/255),  # Nashville Predators Gold
            'EDM': colors.Color(4/255, 30/255, 66/255),  # Edmonton Oilers Blue
            'FLA': colors.Color(200/255, 16/255, 46/255),  # Florida Panthers Red
            'CGY': colors.Color(200/255, 16/255, 46/255),  # Calgary Flames Red
            'VAN': colors.Color(0/255, 32/255, 91/255),  # Vancouver Canucks Blue
            'LAK': colors.Color(17/255, 17/255, 17/255),  # Los Angeles Kings Black
            'ANA': colors.Color(185/255, 151/255, 91/255),  # Anaheim Ducks Gold
            'SJS': colors.Color(0/255, 109/255, 117/255),  # San Jose Sharks Teal
            'VGK': colors.Color(185/255, 151/255, 91/255),  # Vegas Golden Knights Gold
            'COL': colors.Color(111/255, 38/255, 61/255),  # Colorado Avalanche Burgundy
            'ARI': colors.Color(140/255, 38/255, 51/255),  # Arizona Coyotes Red
            'DAL': colors.Color(0/255, 99/255, 65/255),  # Dallas Stars Green
            'MIN': colors.Color(0/255, 99/255, 65/255),  # Minnesota Wild Green
            'WPG': colors.Color(4/255, 30/255, 66/255),  # Winnipeg Jets Navy Blue
            'CHI': colors.Color(207/255, 10/255, 44/255),  # Chicago Blackhawks Red
            'STL': colors.Color(0/255, 47/255, 108/255),  # St. Louis Blues Blue
            'DET': colors.Color(206/255, 17/255, 38/255),  # Detroit Red Wings Red
            'CBJ': colors.Color(0/255, 38/255, 84/255),  # Columbus Blue Jackets Blue
            'PIT': colors.Color(255/255, 184/255, 28/255),  # Pittsburgh Penguins Gold
            'PHI': colors.Color(247/255, 30/255, 57/255),  # Philadelphia Flyers Orange
            'WSH': colors.Color(4/255, 30/255, 66/255),  # Washington Capitals Red
            'CAR': colors.Color(226/255, 24/255, 54/255),  # Carolina Hurricanes Red
            'NYR': colors.Color(0/255, 56/255, 168/255),  # New York Rangers Blue
            'NYI': colors.Color(0/255, 83/255, 155/255),  # New York Islanders Blue
            'NJD': colors.Color(206/255, 17/255, 38/255),  # New Jersey Devils Red
            'BOS': colors.Color(252/255, 181/255, 20/255),  # Boston Bruins Gold
            'BUF': colors.Color(0/255, 38/255, 84/255),  # Buffalo Sabres Blue
            'TOR': colors.Color(0/255, 32/255, 91/255),  # Toronto Maple Leafs Blue
            'OTT': colors.Color(200/255, 16/255, 46/255),  # Ottawa Senators Red
            'MTL': colors.Color(175/255, 30/255, 45/255),  # Montreal Canadiens Red
            'SEA': colors.Color(0/255, 22/255, 40/255),  # Seattle Kraken Navy
            'UTA': colors.Color(105/255, 179/255, 231/255),  # Utah Hockey Club - Mountain Blue
        }
        home_team_color = team_colors.get(home_team['abbrev'], colors.white)
        
        # Create ADVANCED METRICS title bar - narrower width
        advanced_metrics_title_data = [["ADVANCED METRICS"]]
        advanced_metrics_title_table = Table(advanced_metrics_title_data, colWidths=[5.0*inch])
        advanced_metrics_title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), home_team_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTWEIGHT', (0, 0), (-1, -1), 'BOLD'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        # Position the ADVANCED METRICS title bar centered on page
        advanced_metrics_title_wrapper = Table([[advanced_metrics_title_table]], colWidths=[5.0*inch])
        advanced_metrics_title_wrapper.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0.0*inch),  # Move down 0.5 cm more (-0.2 + 0.5*0.3937 = -0.2 + 0.197 = -0.003, rounded to 0.0)
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(advanced_metrics_title_wrapper)
        story.append(Spacer(1, 5))
        
        # Add advanced metrics table with left positioning
        advanced_metrics_story = self.create_advanced_metrics_section(game_data)
        
        # Extract the advanced metrics table and position it to the left
        for item in advanced_metrics_story:
            if hasattr(item, 'hAlign'):  # This is a Table
                # Create a wrapper to move the advanced metrics table 2 cm to the left
                left_table = Table([[item]], colWidths=[4.4*inch])
                left_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), -1.6*inch),  # Move 4 cm total to the left (2.5 + 1.5)
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0.2*inch),  # Move down 1 cm (-0.2 + 1*0.3937 = -0.2 + 0.394 = 0.194, rounded to 0.2)
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                story.append(left_table)
                break
        
        # Create SHOT LOCATIONS title bar - narrow and centered over the shot plot
        shot_locations_title_data = [["SHOT LOCATIONS"]]
        shot_locations_title_table = Table(shot_locations_title_data, colWidths=[2.4*inch])  # Same width as shot plot
        shot_locations_title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), home_team_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTWEIGHT', (0, 0), (-1, -1), 'BOLD'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # Position the SHOT LOCATIONS title bar centered over the shot plot
        shot_locations_wrapper = Table([[shot_locations_title_table]], colWidths=[2.4*inch])
        shot_locations_wrapper.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4.8*inch),  # Move 0.8 cm more to the right (4.5 + 0.8*0.3937 = 4.5 + 0.315 = 4.815, rounded to 4.8)
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), -4.0*inch),  # Move down 1 cm (-4.4 + 1*0.3937 = -4.4 + 0.394 = -4.006, rounded to -4.0)
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(shot_locations_wrapper)
        
        # Create TOP PLAYERS title bar - positioned under the shot location map
        top_players_title_data = [["TOP PLAYERS"]]
        top_players_title_table = Table(top_players_title_data, colWidths=[2.3*inch])  # Same width as Top Players table
        top_players_title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), home_team_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'RussoOne-Regular'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTWEIGHT', (0, 0), (-1, -1), 'BOLD'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # Position the TOP PLAYERS title bar under the shot location map, moved 3 cm to the left
        # Move up an additional 0.2 cm (0.079 inches) for tighter spacing
        top_players_title_wrapper = Table([[top_players_title_table]], colWidths=[2.3*inch])
        top_players_title_wrapper.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2.38*inch),  # Move 0.3 cm more to the left (2.5 - 0.3*0.3937 = 2.5 - 0.118 = 2.382, rounded to 2.38)
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), -2.0*inch),  # Move up 0.3 cm + 0.2 cm = 0.5 cm total (-1.8 - 0.5*0.3937 = -1.8 - 0.197 = -1.997, rounded to -2.0)
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(top_players_title_wrapper)
        
        # Add shot location plot above the Top Players table position
        shot_plot_story = self.create_visualizations(game_data)
        
        # Extract the shot location plot and position it above where Top Players will be
        for item in shot_plot_story:
            if hasattr(item, 'hAlign') and hasattr(item, '_cellvalues'):  # This is a Table (the plot wrapper)
                # Position the shot plot above the Top Players table location
                # Modify the existing table's positioning
                # Update the table's column width to match the new image size
                item._colWidths = [2.4*inch]
                item.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2.44*inch),  # Move 0.1 cm to the right (2.4 + 0.1*0.3937 = 2.4 + 0.039 = 2.439, rounded to 2.44)
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), -3.6*inch),  # Move down 1 cm (-4.0 + 1*0.3937 = -4.0 + 0.394 = -3.606, rounded to -3.6)
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                story.append(item)
                break
        
        # Add top players table at the same level as advanced metrics, positioned to the right
        top_players_story = self.create_player_performance(game_data)
        
        # Extract the top players table and position it to the right of advanced metrics
        for item in top_players_story:
            if hasattr(item, 'hAlign'):  # This is a Table
                # Create a wrapper to position the top players table to the right
                # Position it to the right of the advanced metrics table (which starts at -1.6 inches from left)
                # Advanced metrics table is 4.4 inches wide, so Top Players should start around 2.8 inches from left
                # Move up an additional 0.5 cm (0.197 inches) if game has OT/SO
                top_padding = -1.4*inch - (0.197*inch if has_ot_or_so else 0)
                
                right_table = Table([[item]], colWidths=[2.3*inch])
                right_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2.4*inch),  # Move 1 cm to the left (2.8 - 0.4 = 2.4)
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), top_padding),  # Move up extra 0.5 cm if OT/SO
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                story.append(right_table)
                break
        
        story.append(Spacer(1, 20))
        return story
    
    
    def create_game_analysis(self, game_data):
        """Create game analysis and key moments section"""
        story = []
        
        story.append(Paragraph("GAME ANALYSIS & KEY MOMENTS", self.subtitle_style))
        story.append(Spacer(1, 15))
        
        # Analyze the game flow
        game_info = game_data['game_center']['game']
        away_team = game_data['game_center']['awayTeam']
        home_team = game_data['game_center']['homeTeam']
        
        # Determine winner and margin
        away_score = game_info['awayTeamScore']
        home_score = game_info['homeTeamScore']
        
        if away_score > home_score:
            winner = away_team['abbrev']
            loser = home_team['abbrev']
            margin = away_score - home_score
        else:
            winner = home_team['abbrev']
            loser = away_team['abbrev']
            margin = home_score - away_score
        
        
        story.append(Spacer(1, 20))
        return story
    
    def create_combined_shot_location_plot(self, game_data):
        """Create combined shot and goal location scatter plot for both teams"""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import os
            
            play_by_play = game_data.get('play_by_play')
            if not play_by_play or 'plays' not in play_by_play:
                return None
                
            boxscore = game_data['boxscore']
            away_team = boxscore['awayTeam']
            home_team = boxscore['homeTeam']
            
            # Collect shot and goal data for both teams with side designation
            away_shots = []
            away_goals = []
            home_shots = []
            home_goals = []
            
            for play in play_by_play['plays']:
                details = play.get('details', {})
                event_type = play.get('typeDescKey', '')
                event_team = details.get('eventOwnerTeamId')
                period = play.get('periodDescriptor', {}).get('number', 1)
                
                # Get coordinates
                x_coord = details.get('xCoord', 0)
                y_coord = details.get('yCoord', 0)
                
                if x_coord is not None and y_coord is not None:
                    # Force each team to always appear on their designated side
                    # Away team: Always left side (negative X)
                    # Home team: Always right side (positive X)
                    
                    if event_team == away_team['id'] and event_type in ['shot-on-goal', 'missed-shot', 'blocked-shot']:
                        # Away team shots - force to left side
                        if x_coord > 0:  # If shot is on right side, flip to left
                            flipped_x = -x_coord
                            flipped_y = -y_coord
                        else:  # Already on left side
                            flipped_x = x_coord
                            flipped_y = y_coord
                        away_shots.append((flipped_x, flipped_y))
                        
                    elif event_team == away_team['id'] and event_type == 'goal':
                        # Away team goals - force to left side
                        if x_coord > 0:  # If goal is on right side, flip to left
                            flipped_x = -x_coord
                            flipped_y = -y_coord
                        else:  # Already on left side
                            flipped_x = x_coord
                            flipped_y = y_coord
                        away_goals.append((flipped_x, flipped_y))
                        
                    elif event_team == home_team['id'] and event_type in ['shot-on-goal', 'missed-shot', 'blocked-shot']:
                        # Home team shots - force to right side
                        if x_coord < 0:  # If shot is on left side, flip to right
                            flipped_x = -x_coord
                            flipped_y = -y_coord
                        else:  # Already on right side
                            flipped_x = x_coord
                            flipped_y = y_coord
                        home_shots.append((flipped_x, flipped_y))
                        
                    elif event_team == home_team['id'] and event_type == 'goal':
                        # Home team goals - force to right side
                        if x_coord < 0:  # If goal is on left side, flip to right
                            flipped_x = -x_coord
                            flipped_y = -y_coord
                        else:  # Already on right side
                            flipped_x = x_coord
                            flipped_y = y_coord
                        home_goals.append((flipped_x, flipped_y))
            
            if not (away_shots or away_goals or home_shots or home_goals):
                print("No shots or goals found for either team")
                return None
                
            print(f"Found {len(away_shots)} shots and {len(away_goals)} goals for {away_team['abbrev']}")
            print(f"Found {len(home_shots)} shots and {len(home_goals)} goals for {home_team['abbrev']}")
            
            # Create the plot - original size
            plt.ioff()
            fig, ax = plt.subplots(figsize=(8, 5.5))
            
            # Load and display the rink image
            # Use path relative to script location
            script_dir = os.path.dirname(os.path.abspath(__file__))
            rink_path = os.path.join(script_dir, 'F300E016-E2BD-450A-B624-5BADF3853AC0.jpeg')
            try:
                if os.path.exists(rink_path):
                    from matplotlib.image import imread
                    rink_img = imread(rink_path)
                    # Display the rink image beneath plotted points
                    ax.imshow(rink_img, extent=[-100, 100, -42.5, 42.5], aspect='equal', alpha=0.75, zorder=0)
                    print(f"Loaded rink image from: {rink_path}")
                else:
                    print(f"Rink image not found at: {rink_path}")
                    # Fallback to drawing rink outline
                    ax.plot([-100, 100], [42.5, 42.5], 'k-', linewidth=3)  # Top boards
                    ax.plot([-100, 100], [-42.5, -42.5], 'k-', linewidth=3)  # Bottom boards
                    ax.plot([-100, -100], [-42.5, 42.5], 'k-', linewidth=3)  # Left boards
                    ax.plot([100, 100], [-42.5, 42.5], 'k-', linewidth=3)  # Right boards
                    ax.plot([89, 89], [-42.5, 42.5], 'r-', linewidth=2)  # Right goal line
                    ax.plot([-89, -89], [-42.5, 42.5], 'r-', linewidth=2)  # Left goal line
                    ax.plot([25, 25], [-42.5, 42.5], 'b-', linewidth=2)  # Right blue line
                    ax.plot([-25, -25], [-42.5, 42.5], 'b-', linewidth=2)  # Left blue line
                    ax.plot([0, 0], [-42.5, 42.5], 'k-', linewidth=1)  # Center line
            except Exception as e:
                print(f"Error loading rink image: {e}")
                # Fallback to drawing rink outline
                ax.plot([-100, 100], [42.5, 42.5], 'k-', linewidth=3)  # Top boards
                ax.plot([-100, 100], [-42.5, -42.5], 'k-', linewidth=3)  # Bottom boards
                ax.plot([-100, -100], [-42.5, 42.5], 'k-', linewidth=3)  # Left boards
                ax.plot([100, 100], [-42.5, 42.5], 'k-', linewidth=3)  # Right boards
                ax.plot([89, 89], [-42.5, 42.5], 'r-', linewidth=2)  # Right goal line
                ax.plot([-89, -89], [-42.5, 42.5], 'r-', linewidth=2)  # Left goal line
                ax.plot([25, 25], [-42.5, 42.5], 'b-', linewidth=2)  # Right blue line
                ax.plot([-25, -25], [-42.5, 42.5], 'b-', linewidth=2)  # Left blue line
                ax.plot([0, 0], [-42.5, 42.5], 'k-', linewidth=1)  # Center line
            
            # Get team colors based on actual teams playing
            away_color = self._get_team_color(away_team['abbrev'])
            home_color = self._get_team_color(home_team['abbrev'])
            
            # Plot away team shots and goals in team color
            if away_shots:
                shot_x, shot_y = zip(*away_shots)
                ax.scatter(shot_x, shot_y, c=away_color, alpha=0.95, s=60, 
                          marker='o', edgecolors='black', linewidth=1.5, zorder=50)

            if away_goals:
                goal_x, goal_y = zip(*away_goals)
                ax.scatter(goal_x, goal_y, c=away_color, alpha=1.0, s=90, 
                                          marker='o', edgecolors='black', linewidth=2.0, zorder=51)

            # Plot home team shots and goals in team color
            if home_shots:
                shot_x, shot_y = zip(*home_shots)
                ax.scatter(shot_x, shot_y, c=home_color, alpha=0.95, s=60, 
                          marker='o', edgecolors='white', linewidth=1.5, zorder=50)

            if home_goals:
                goal_x, goal_y = zip(*home_goals)
                ax.scatter(goal_x, goal_y, c=home_color, alpha=1.0, s=90, 
                          marker='o', edgecolors='white', linewidth=2.0, zorder=51)

            # Set plot properties
            ax.set_xlim(-100, 100)
            ax.set_ylim(-42.5, 42.5)
            ax.set_aspect('equal')
            ax.set_facecolor('white')
            # No legend needed - team colors are self-explanatory
            ax.grid(False)  # Turn off grid since we have the rink image
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

                            # Add team labels on the rink
            # Removed team abbreviations from plot as requested
            
            # Add home team logo at center ice (center faceoff circle)
            try:
                import requests
                from io import BytesIO
                from PIL import Image as PILImage
                
                # Get home team logo
                logo_abbrev_map = {
                    'TBL': 'tb', 'NSH': 'nsh', 'EDM': 'edm', 'FLA': 'fla',
                    'COL': 'col', 'DAL': 'dal', 'BOS': 'bos', 'TOR': 'tor',
                    'MTL': 'mtl', 'OTT': 'ott', 'BUF': 'buf', 'DET': 'det',
                    'CAR': 'car', 'WSH': 'wsh', 'PIT': 'pit', 'NYR': 'nyr',
                    'NYI': 'nyi', 'NJD': 'nj', 'PHI': 'phi', 'CBJ': 'cbj',
                    'STL': 'stl', 'MIN': 'min', 'WPG': 'wpg', 'ARI': 'ari',
                    'VGK': 'vgk', 'SJS': 'sj', 'LAK': 'la', 'ANA': 'ana',
                    'CGY': 'cgy', 'VAN': 'van', 'SEA': 'sea', 'CHI': 'chi'
                }
                home_team_abbrev = logo_abbrev_map.get(home_team['abbrev'], home_team['abbrev'].lower())
                home_logo_url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{home_team_abbrev}.png"
                
                # Download home team logo
                home_response = requests.get(home_logo_url, timeout=5)
                if home_response.status_code == 200:
                    home_logo = PILImage.open(BytesIO(home_response.content))
                    # Resize logo to fit center ice circle
                    logo_size = 12  # 12 feet diameter in coordinate units
                    home_logo = home_logo.resize((logo_size, logo_size), PILImage.Resampling.LANCZOS)
                    
                    # Convert to numpy array for matplotlib
                    import numpy as np
                    logo_array = np.array(home_logo)
                    
                    # Place logo at center ice (0, 0)
                    # Note: matplotlib extent is [left, right, bottom, top]
                    ax.imshow(logo_array, extent=[-logo_size/2, logo_size/2, -logo_size/2, logo_size/2], 
                             alpha=0.8, zorder=10)
                    print(f"Added {home_team['abbrev']} logo at center ice")
                else:
                    print(f"Failed to load home team logo: HTTP {home_response.status_code}")
            except Exception as e:
                print(f"Error adding home team logo: {e}")
                # Fallback: add text at center ice
                # Removed center ice team abbreviation as requested
            
            # Save to file with a unique name to avoid conflicts
            import time
            timestamp = int(time.time() * 1000)  # milliseconds
            plot_filename = f'combined_shot_plot_{away_team["abbrev"]}_vs_{home_team["abbrev"]}_{timestamp}.png'
            abs_plot_filename = os.path.abspath(plot_filename)
            print(f"Saving combined plot to: {abs_plot_filename}")
            fig.savefig(abs_plot_filename, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            
            # Verify file was created
            if os.path.exists(abs_plot_filename):
                print(f"Combined plot saved successfully: {abs_plot_filename}")
                print(f"File size: {os.path.getsize(abs_plot_filename)} bytes")
                return abs_plot_filename
            else:
                print(f"Failed to create combined plot: {abs_plot_filename}")
                return None
            
        except Exception as e:
            print(f"Error creating combined shot location plot: {e}")
            return None
    
    def _classify_lateral_movement(self, avg_feet):
        """Classify lateral (E-W) pre-shot movement into descriptive categories"""
        if avg_feet == 0:
            return "Stationary"
        elif avg_feet < 10:
            return "Minor side-to-side"
        elif avg_feet < 20:
            return "Cross-ice movement"
        elif avg_feet < 35:
            return "Wide-lane movement"
        else:
            return "Full-width movement"
    
    def _classify_longitudinal_movement(self, avg_feet):
        """Classify longitudinal (N-S) pre-shot movement into descriptive categories"""
        if avg_feet == 0:
            return "Stationary"
        elif avg_feet < 15:
            return "Close-range setup"
        elif avg_feet < 30:
            return "Mid-range buildup"
        elif avg_feet < 50:
            return "Extended buildup"
        else:
            return "Long-range rush"
    
    def create_advanced_metrics_section(self, game_data):
        """Create advanced metrics section with specific data"""
        story = []
        
        # Removed ADVANCED METRICS title as requested
        
        try:
            # Get team abbreviations and IDs
            boxscore = game_data['boxscore']
            away_team_abbrev = boxscore['awayTeam']['abbrev']
            home_team_abbrev = boxscore['homeTeam']['abbrev']
            away_team_id = boxscore['awayTeam']['id']
            home_team_id = boxscore['homeTeam']['id']
            
            # Define team primary colors for advanced metrics table
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
                'UTA': colors.Color(105/255, 179/255, 231/255),  # Utah Hockey Club - Mountain Blue
                'CHI': colors.Color(207/255, 10/255, 44/255)  # Chicago Blackhawks Red
            }
            
            home_team_color = team_colors.get(home_team_abbrev, colors.white)
            
            # Get advanced metrics using the analyzer
            from advanced_metrics_analyzer import AdvancedMetricsAnalyzer
            analyzer = AdvancedMetricsAnalyzer(game_data.get('play_by_play', {}))
            metrics = analyzer.generate_comprehensive_report(away_team_id, home_team_id)
            
            # Advanced Metrics Table with real data (title removed as requested)
            
            # Extract real metrics
            away_shot_quality = metrics['away_team']['shot_quality']
            home_shot_quality = metrics['home_team']['shot_quality']
            away_pressure = metrics['away_team']['pressure']
            home_pressure = metrics['home_team']['pressure']
            away_defense = metrics['away_team']['defense']
            home_defense = metrics['home_team']['defense']
            away_cross_ice = metrics['away_team']['cross_ice_passes']
            home_cross_ice = metrics['home_team']['cross_ice_passes']
            away_pre_shot = metrics['away_team']['pre_shot_movement']
            home_pre_shot = metrics['home_team']['pre_shot_movement']
            
            # Load team logos for header - use PNG format from ESPN instead of SVG
            away_logo_img = None
            home_logo_img = None
            try:
                logo_abbrev_map = {
                    'TBL': 'tb', 'NSH': 'nsh', 'EDM': 'edm', 'FLA': 'fla',
                    'COL': 'col', 'DAL': 'dal', 'BOS': 'bos', 'TOR': 'tor',
                    'MTL': 'mtl', 'OTT': 'ott', 'BUF': 'buf', 'DET': 'det',
                    'CAR': 'car', 'WSH': 'wsh', 'PIT': 'pit', 'NYR': 'nyr',
                    'NYI': 'nyi', 'NJD': 'nj', 'PHI': 'phi', 'CBJ': 'cbj',
                    'STL': 'stl', 'MIN': 'min', 'WPG': 'wpg', 'ARI': 'ari',
                    'VGK': 'vgk', 'SJS': 'sj', 'LAK': 'la', 'ANA': 'ana',
                    'CGY': 'cgy', 'VAN': 'van', 'SEA': 'sea', 'CHI': 'chi',
                    'UTA': 'utah'
                }
                
                import requests
                import tempfile
                from PIL import Image as PILImage
                
                away_logo_abbrev = logo_abbrev_map.get(away_team_abbrev, away_team_abbrev.lower())
                home_logo_abbrev = logo_abbrev_map.get(home_team_abbrev, home_team_abbrev.lower())
                
                # Try ESPN PNG logos first
                away_logo_url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{away_logo_abbrev}.png"
                home_logo_url = f"https://a.espncdn.com/i/teamlogos/nhl/500/{home_logo_abbrev}.png"
                
                # Download and save away logo
                away_response = requests.get(away_logo_url, timeout=5)
                if away_response.status_code == 200:
                    away_png_path = tempfile.mktemp(suffix='.png')
                    with open(away_png_path, 'wb') as f:
                        f.write(away_response.content)
                    away_logo_img = Image(away_png_path, width=20, height=20)
                    # Keep file for now, will be cleaned up by OS
                
                # Download and save home logo
                home_response = requests.get(home_logo_url, timeout=5)
                if home_response.status_code == 200:
                    home_png_path = tempfile.mktemp(suffix='.png')
                    with open(home_png_path, 'wb') as f:
                        f.write(home_response.content)
                    home_logo_img = Image(home_png_path, width=20, height=20)
                    # Keep file for now, will be cleaned up by OS
                
                print(f"Logos loaded: Away={away_logo_img is not None}, Home={home_logo_img is not None}")
            except Exception as e:
                print(f"Could not load logos for advanced metrics header: {e}")
                import traceback
                traceback.print_exc()
            
            combined_data = [
                ['Category', 'Metric', away_logo_img if away_logo_img else away_team_abbrev, home_logo_img if home_logo_img else home_team_abbrev],
                
                # Shot Quality Analysis
                ['SHOT QUALITY', 'Expected Goals (xG)', f"{away_shot_quality['expected_goals']:.2f}", f"{home_shot_quality['expected_goals']:.2f}"],
                ['', 'High Danger Shots', str(away_shot_quality['high_danger_shots']), str(home_shot_quality['high_danger_shots'])],
                ['', 'Total Shots', str(away_shot_quality['total_shots']), str(home_shot_quality['total_shots'])],
                ['', 'Shots on Goal', str(away_shot_quality['shots_on_goal']), str(home_shot_quality['shots_on_goal'])],
                ['', 'Shooting %', f"{away_shot_quality['shooting_percentage']:.1%}", f"{home_shot_quality['shooting_percentage']:.1%}"],
                
                # Pressure Analysis
                ['PRESSURE', 'Sustained Pressure Sequences', str(away_pressure['sustained_pressure_sequences']), str(home_pressure['sustained_pressure_sequences'])],
                ['', 'Quick Strike Opportunities', str(away_pressure['quick_strike_opportunities']), str(home_pressure['quick_strike_opportunities'])],
                ['', 'Avg Shots per Sequence', 
                 f"{sum(away_pressure['shot_attempts_per_sequence'])/len(away_pressure['shot_attempts_per_sequence']):.1f}" if away_pressure['shot_attempts_per_sequence'] else '0.0', 
                 f"{sum(home_pressure['shot_attempts_per_sequence'])/len(home_pressure['shot_attempts_per_sequence']):.1f}" if home_pressure['shot_attempts_per_sequence'] else '0.0'],
                
                # Defensive Analysis
                ['DEFENSIVE', 'Blocked Shots', str(away_defense['blocked_shots']), str(home_defense['blocked_shots'])],
                ['', 'Takeaways', str(away_defense['takeaways']), str(home_defense['takeaways'])],
                ['', 'Hits', str(away_defense['hits']), str(home_defense['hits'])],
                ['', 'Shot Attempts Against', str(away_defense['shot_attempts_against']), str(home_defense['shot_attempts_against'])],
                ['', 'High Danger Chances Against', str(away_defense['high_danger_chances_against']), str(home_defense['high_danger_chances_against'])],
                
                # Pre-Shot Movement Analysis
                ['PRE-SHOT MOVEMENT', 'Royal Road Proxy', 
                 f"{away_pre_shot['royal_road_proxy']['attempts']} shots", 
                 f"{home_pre_shot['royal_road_proxy']['attempts']} shots"],
                ['', 'OZ Retrieval to Shot', 
                 f"{away_pre_shot['oz_retrieval_to_shot']['attempts']} shots", 
                 f"{home_pre_shot['oz_retrieval_to_shot']['attempts']} shots"],
                ['', 'Lateral Movement (E-W)', 
                 self._classify_lateral_movement(away_pre_shot['lateral_movement']['avg_delta_y']), 
                 self._classify_lateral_movement(home_pre_shot['lateral_movement']['avg_delta_y'])],
                ['', 'Longitudinal Movement (N-S)', 
                 self._classify_longitudinal_movement(away_pre_shot['longitudinal_movement']['avg_delta_x']), 
                 self._classify_longitudinal_movement(home_pre_shot['longitudinal_movement']['avg_delta_x'])]
            ]
            
            combined_table = Table(combined_data, colWidths=[1.0*inch, 1.4*inch, 0.9*inch, 0.9*inch])
            combined_table.setStyle(TableStyle([
                # Header row with home team primary color background
                ('BACKGROUND', (0, 0), (-1, 0), home_team_color),  # Home team primary color
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'RussoOne-Regular'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                
                # SHOT QUALITY category header and all metric rows - medium orange/salmon background with black text (Category column only)
                ('BACKGROUND', (0, 1), (0, 5), colors.Color(255/255, 160/255, 122/255)),  # Medium orange/salmon
                ('TEXTCOLOR', (0, 1), (0, 5), colors.black),
                
                # PRESSURE category header and all metric rows - light blue background with black text (Category column only)
                ('BACKGROUND', (0, 6), (0, 8), colors.Color(135/255, 206/255, 250/255)),  # Light blue
                ('TEXTCOLOR', (0, 6), (0, 8), colors.black),
                
                # DEFENSIVE category header and all metric rows - light gray background with black text (Category column only)
                ('BACKGROUND', (0, 9), (0, 13), colors.Color(211/255, 211/255, 211/255)),  # Light gray
                ('TEXTCOLOR', (0, 9), (0, 13), colors.black),
                
                # PRE-SHOT MOVEMENT category header and all metric rows - light yellow/cream background with black text (Category column only)
                ('BACKGROUND', (0, 14), (0, 17), colors.Color(255/255, 253/255, 208/255)),  # Light yellow/cream
                ('TEXTCOLOR', (0, 14), (0, 17), colors.black),
                
                # Alternating grey background for Metric and team columns (every second row)
                ('BACKGROUND', (1, 2), (-1, 2), colors.lightgrey),  # Row 2 (High Danger Shots)
                ('BACKGROUND', (1, 4), (-1, 4), colors.lightgrey),  # Row 4 (Shots on Goal)
                ('BACKGROUND', (1, 6), (-1, 6), colors.lightgrey),  # Row 6 (Sustained Pressure)
                ('BACKGROUND', (1, 8), (-1, 8), colors.lightgrey),  # Row 8 (Avg Shots per Sequence)
                ('BACKGROUND', (1, 10), (-1, 10), colors.lightgrey),  # Row 10 (Takeaways)
                ('BACKGROUND', (1, 12), (-1, 12), colors.lightgrey),  # Row 12 (Shot Attempts Against)
                ('BACKGROUND', (1, 15), (-1, 15), colors.lightgrey),  # Row 15 (OZ Retrieval to Shot)
                ('BACKGROUND', (1, 17), (-1, 17), colors.lightgrey),  # Row 17 (Longitudinal Movement)
                
                # Font styling
                ('FONTNAME', (0, 1), (0, -1), 'RussoOne-Regular'),
                ('FONTSIZE', (0, 1), (0, -1), 5.5),
                ('FONTWEIGHT', (0, 1), (0, -1), 'BOLD'),
                ('FONTNAME', (1, 1), (-1, -1), 'RussoOne-Regular'),
                ('FONTSIZE', (1, 1), (-1, -1), 5.5),
                ('TOPPADDING', (0, 1), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
                
                # Grid borders
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            # Add the table directly (positioning will be handled by side-by-side layout)
            story.append(combined_table)
            story.append(Spacer(1, 12))
            
        except Exception as e:
            print(f"Error creating advanced metrics: {e}")
            story.append(Paragraph("Advanced metrics could not be calculated for this game.", self.normal_style))
        
        return story
    
    def create_visualizations(self, game_data):
        """Create shot location visualizations"""
        story = []
                        
        story.append(Spacer(1, 10))
        
        try:
            import os
            boxscore = game_data['boxscore']
            away_team = boxscore['awayTeam']
            home_team = boxscore['homeTeam']
                            
            # Create combined shot location scatter plot for both teams
            try:
                # Create combined plot
                combined_plot = self.create_combined_shot_location_plot(game_data)
                
                # Add a small delay to ensure files are written
                import time
                time.sleep(0.5)
                
                if combined_plot and os.path.exists(combined_plot):
                    print(f"Adding combined plot from file: {combined_plot}")
                    try:
                        combined_image = Image(combined_plot, width=2.4*inch, height=1.65*inch)
                        combined_image.hAlign = 'CENTER'
                        
                        # Move the plot up 3 cm
                        plot_wrapper = Table([[combined_image]], colWidths=[2.4*inch])
                        plot_wrapper.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), -1.2*inch),  # Move up 3 cm
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                        ]))
                        story.append(plot_wrapper)
                        print("Successfully added combined plot to PDF")
                                        
                        # Store the file path for cleanup later
                        if not hasattr(self, 'temp_plot_files'):
                            self.temp_plot_files = []
                        self.temp_plot_files.append(combined_plot)
                    except Exception as e:
                        print(f"Error adding combined plot to PDF: {e}")
                        story.append(Paragraph("Combined shot location plot could not be added to PDF.", self.normal_style))
                else:
                    print(f"Combined shot location plot failed")
                    story.append(Paragraph("Shot location analysis could not be generated.", self.normal_style))
                
                story.append(Spacer(1, 20))
            except Exception as e:
                print(f"Error creating combined plot: {e}")
                story.append(Paragraph("Combined shot location plot could not be created.", self.normal_style))
            
        except Exception as e:
            print(f"Error creating shot location plots: {e}")
            story.append(Paragraph("Shot location analysis could not be created for this game.", self.normal_style))
        
        return story
    
    def generate_report(self, game_data, output_filename, game_id=None):
        """Generate the complete post-game report PDF"""
        # Set margins to allow header to extend to edges
        doc = SimpleDocTemplate(output_filename, pagesize=letter, rightMargin=72, leftMargin=72, 
                              topMargin=0, bottomMargin=18)
        
        story = []
        
        # Add modern header image at the absolute top of the page (height 0)
        header_image = self.create_header_image(game_data, game_id)
        if header_image:
            print(f"Header image loaded: {header_image.drawWidth}x{header_image.drawHeight}")
            # Header starts at exact top of page (0 points from top)
            # Covers full 8.5 inches width (612 points)
            # Use negative spacer to pull header to absolute top
            story.append(Spacer(1, -40))  # Increased negative spacer to pull header higher and cover top white space
            story.append(header_image)
            story.append(Spacer(1, 20))  # Minimal space after header
        else:
            print("Warning: Header image failed to load")
        
        
        # Add left margin for content (since header uses negative margin)
        
        
        # Add content with proper margins (since we removed page margins for header)
        story.append(Spacer(1, 0))  # No top spacing
        
        # Add all sections
        story.extend(self.create_team_stats_comparison(game_data))
        
        # Create side-by-side layout for advanced metrics and top players
        story.extend(self.create_side_by_side_tables(game_data))
        
        # Build the PDF
        doc.build(story)
        
        # Clean up temporary header file if it exists
        if header_image and hasattr(header_image, 'temp_path'):
            try:
                os.remove(header_image.temp_path)
                print(f"Cleaned up temporary header file: {header_image.temp_path}")
            except:
                pass
        
        # Clean up temporary plot files if they exist
        if hasattr(self, 'temp_plot_files'):
            for plot_file in self.temp_plot_files:
                try:
                    if os.path.exists(plot_file):
                        os.remove(plot_file)
                        print(f"Cleaned up temporary plot file: {plot_file}")
                except Exception as e:
                    print(f"Warning: Could not clean up plot file {plot_file}: {e}")
            self.temp_plot_files = []
        
        print(f"Post-game report generated successfully: {output_filename}")
        return output_filename
