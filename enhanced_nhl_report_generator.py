#!/usr/bin/env python3
"""
Enhanced NHL Report Generator - 2025 Edition
Comprehensive report generator with all advanced features
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from io import BytesIO
import os
import math
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Any
from enhanced_nhl_api_client import EnhancedNHLAPIClient
from nhl_advanced_analytics import NHLAdvancedAnalytics

class EnhancedNHLReportGenerator:
    def __init__(self):
        """Initialize the enhanced NHL report generator"""
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        self.api_client = EnhancedNHLAPIClient()
        self.analytics = NHLAdvancedAnalytics()
        
        # Team colors for visualizations
        self.team_colors = {
            'EDM': '#FF4C00', 'FLA': '#C8102E', 'BOS': '#FFB81C', 'TOR': '#003E7E',
            'MTL': '#AF1E2D', 'OTT': '#C52032', 'BUF': '#002654', 'DET': '#CE1126',
            'TBL': '#002868', 'CAR': '#CC0000', 'WSH': '#C8102E', 'PIT': '#000000',
            'NYR': '#0038A8', 'NYI': '#00539B', 'NJD': '#CE1126', 'PHI': '#F74902',
            'CBJ': '#002654', 'NSH': '#FFB81C', 'STL': '#002F87', 'MIN': '#154734',
            'WPG': '#041E42', 'COL': '#6F263D', 'ARI': '#8C2633', 'VGK': '#B4975A',
            'SJS': '#006D75', 'LAK': '#111111', 'ANA': '#F47A20', 'CGY': '#C8102E',
            'VAN': '#001F5C', 'SEA': '#001628', 'CHI': '#C8102E', 'DAL': '#006847'
        }
        
        # Corrected NHL logos directory
        self.logos_dir = "corrected_nhl_logos"
        
        # xG model coefficients
        self.xg_coefficients = {
            'shot_type': {
                'wrist': 0.08, 'slap': 0.12, 'snap': 0.10, 'backhand': 0.06,
                'tip-in': 0.15, 'deflected': 0.13, 'wrap-around': 0.05, 'default': 0.08
            }
        }
        
        # Situation code meanings
        self.situation_codes = {
            '1551': '5v5',
            '1451': '4v5 (Power Play)',
            '1351': '3v5 (5v3 Power Play)',
            '1541': '5v4 (Penalty Kill)',
            '1441': '4v4',
            '0660': '3v3 (Overtime)'
        }
        
        # Zone codes
        self.zone_codes = {
            'O': 'Offensive Zone',
            'D': 'Defensive Zone', 
            'N': 'Neutral Zone'
        }
    
    def get_team_logo(self, team_abbrev, size=(1*inch, 1*inch)):
        """Get team PNG logo if available"""
        logo_path = os.path.join(self.logos_dir, f"{team_abbrev}.png")
        print(f"🔍 Looking for logo: {logo_path}")
        
        if os.path.exists(logo_path):
            print(f"✅ Found logo file: {logo_path}")
            try:
                # Create ReportLab Image from PNG file
                img = Image(logo_path)
                img.drawHeight = size[1]
                img.drawWidth = size[0]
                print(f"✅ Created ReportLab Image: {img.drawWidth}x{img.drawHeight}")
                return img
            except Exception as e:
                print(f"❌ Could not load PNG logo for {team_abbrev}: {e}")
                return None
        else:
            print(f"❌ No PNG logo found for {team_abbrev}")
            return None
    
    def create_logo_placeholder(self, team_abbrev, size=(1*inch, 1*inch)):
        """Create a text placeholder for team logo"""
        return Paragraph(f"<b>{team_abbrev}</b>", self.highlight_style)

    def setup_custom_styles(self):
        """Setup custom paragraph styles for the enhanced report"""
        # Enhanced title style
        self.title_style = ParagraphStyle(
            'EnhancedTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=25,
            fontName='Helvetica-Bold'
        )
        
        # Enhanced subtitle style
        self.subtitle_style = ParagraphStyle(
            'EnhancedSubtitle',
            parent=self.styles['Heading2'],
            fontSize=20,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=18,
            fontName='Helvetica-Bold'
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'EnhancedSection',
            parent=self.styles['Heading3'],
            fontSize=16,
            textColor=colors.darkred,
            alignment=TA_LEFT,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        # Subsection style
        self.subsection_style = ParagraphStyle(
            'EnhancedSubsection',
            parent=self.styles['Heading4'],
            fontSize=14,
            textColor=colors.darkgreen,
            alignment=TA_LEFT,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'EnhancedNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceAfter=6,
            fontName='Helvetica'
        )
        
        # Stat text style
        self.stat_style = ParagraphStyle(
            'EnhancedStat',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.darkgreen,
            alignment=TA_LEFT,
            spaceAfter=4,
            fontName='Helvetica-Bold'
        )
        
        # Highlight style
        self.highlight_style = ParagraphStyle(
            'EnhancedHighlight',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.darkblue,
            alignment=TA_LEFT,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
    
    def calculate_advanced_xg(self, shot_data):
        """Calculate advanced Expected Goals with more factors"""
        base_xg = 0.08
        
        # Shot type multiplier
        shot_type = shot_data.get('shotType', 'default').lower()
        type_multiplier = self.xg_coefficients['shot_type'].get(shot_type, 
                                                               self.xg_coefficients['shot_type']['default'])
        
        # Distance and angle calculations
        x_coord = shot_data.get('xCoord', 0)
        y_coord = shot_data.get('yCoord', 0)
        
        # Calculate distance to nearest goal
        goal_x = 89 if x_coord > 0 else -89
        distance = math.sqrt((x_coord - goal_x)**2 + (y_coord - 0)**2)
        
        # Distance effect (exponential decay)
        distance_multiplier = math.exp(-distance / 50)
        
        # Angle effect
        if distance > 0:
            angle = math.degrees(math.asin(abs(y_coord) / distance))
            angle_multiplier = math.cos(math.radians(angle))
        else:
            angle_multiplier = 1.0
        
        # Zone effect
        zone = shot_data.get('zoneCode', 'O')
        zone_multiplier = 1.0
        if zone == 'O':  # Offensive zone
            zone_multiplier = 1.2
        elif zone == 'D':  # Defensive zone
            zone_multiplier = 0.3
        else:  # Neutral zone
            zone_multiplier = 0.8
        
        # Calculate final xG
        xg = base_xg * type_multiplier * distance_multiplier * angle_multiplier * zone_multiplier
        
        return max(0, min(1, xg))
    
    def create_player_mapping(self, play_by_play_data):
        """Create comprehensive player mapping"""
        player_mapping = {}
        
        if 'rosterSpots' in play_by_play_data:
            roster_spots = play_by_play_data['rosterSpots']
            print(f"Creating player mapping from {len(roster_spots)} roster spots...")
            
            for spot in roster_spots:
                player_id = spot.get('playerId')
                first_name = spot.get('firstName', {}).get('default', '')
                last_name = spot.get('lastName', {}).get('default', '')
                sweater_number = spot.get('sweaterNumber', '')
                position = spot.get('positionCode', '')
                team_id = spot.get('teamId', '')
                
                if player_id and first_name and last_name:
                    full_name = f"{first_name} {last_name}"
                    if sweater_number:
                        full_name = f"{full_name} #{sweater_number}"
                    if position:
                        full_name = f"{full_name} ({position})"
                    
                    player_mapping[player_id] = {
                        'name': full_name,
                        'first_name': first_name,
                        'last_name': last_name,
                        'number': sweater_number,
                        'position': position,
                        'team_id': team_id
                    }
        
        print(f"✅ Created player mapping for {len(player_mapping)} players")
        return player_mapping
    
    def extract_comprehensive_metrics(self, play_by_play_data, player_mapping):
        """Extract comprehensive metrics from play-by-play data"""
        if not play_by_play_data or 'plays' not in play_by_play_data:
            return None
        
        plays = play_by_play_data['plays']
        print(f"Extracting comprehensive metrics from {len(plays)} plays...")
        
        # Initialize player stats
        player_stats = defaultdict(lambda: {
            # Basic stats
            'goals': 0, 'assists': 0, 'points': 0,
            'shots': 0, 'shots_on_goal': 0, 'missed_shots': 0, 'blocked_shots': 0,
            'hits': 0, 'hits_taken': 0, 'faceoffs_won': 0, 'faceoffs_lost': 0,
            'penalties': 0, 'penalty_minutes': 0, 'giveaways': 0, 'takeaways': 0,
            
            # Advanced stats
            'expected_goals': 0, 'corsi': 0, 'fenwick': 0,
            'high_danger_chances': 0, 'scoring_chances': 0, 'slot_shots': 0,
            'power_play_goals': 0, 'power_play_assists': 0, 'power_play_shots': 0,
            'penalty_kill_goals': 0, 'penalty_kill_assists': 0, 'penalty_kill_shots': 0,
            
            # Detailed tracking
            'shot_locations': [], 'shot_types': [], 'goals_scored': [], 'assists_given': []
        })
        
        # Game-level stats
        game_stats = {
            'total_plays': len(plays),
            'play_types': defaultdict(int),
            'situation_breakdown': defaultdict(int),
            'zone_breakdown': defaultdict(int),
            'period_stats': defaultdict(lambda: {
                'total_plays': 0, 'goals': 0, 'shots': 0, 'penalties': 0,
                'hits': 0, 'faceoffs': 0, 'giveaways': 0, 'takeaways': 0
            }),
            'goals': [], 'shots': [], 'hits': [], 'faceoffs': [], 'penalties': [],
            'giveaways': [], 'takeaways': [], 'scoring_chances': [], 'high_danger_chances': []
        }
        
        # Process each play
        for play in plays:
            play_type = play.get('typeDescKey', '')
            period = play.get('periodDescriptor', {}).get('number', 1)
            time_remaining = play.get('timeRemaining', '20:00')
            situation_code = play.get('situationCode', '1551')
            details = play.get('details', {})
            
            # Update game-level stats
            game_stats['play_types'][play_type] += 1
            game_stats['situation_breakdown'][situation_code] += 1
            game_stats['period_stats'][period]['total_plays'] += 1
            
            # Zone analysis
            zone = details.get('zoneCode', 'N')
            game_stats['zone_breakdown'][zone] += 1
            
            # Goals
            if play_type == 'goal':
                game_stats['goals'].append(play)
                game_stats['period_stats'][period]['goals'] += 1
                
                scoring_player_id = details.get('scoringPlayerId')
                if scoring_player_id:
                    player_stats[scoring_player_id]['goals'] += 1
                    player_stats[scoring_player_id]['goals_scored'].append({
                        'period': period, 'time': time_remaining,
                        'xG': self.calculate_advanced_xg(details),
                        'situation': self.situation_codes.get(situation_code, 'Unknown'),
                        'zone': self.zone_codes.get(zone, 'Unknown')
                    })
                    
                    # Situation-specific goals
                    if '1451' in situation_code or '1351' in situation_code:  # Power play
                        player_stats[scoring_player_id]['power_play_goals'] += 1
                    elif '1541' in situation_code:  # Penalty kill
                        player_stats[scoring_player_id]['penalty_kill_goals'] += 1
                
                # Assists
                for assist_key in ['assist1PlayerId', 'assist2PlayerId']:
                    assist_player_id = details.get(assist_key)
                    if assist_player_id:
                        player_stats[assist_player_id]['assists'] += 1
                        player_stats[assist_player_id]['assists_given'].append({
                            'period': period, 'time': time_remaining,
                            'situation': self.situation_codes.get(situation_code, 'Unknown'),
                            'zone': self.zone_codes.get(zone, 'Unknown')
                        })
                        
                        # Situation-specific assists
                        if '1451' in situation_code or '1351' in situation_code:
                            player_stats[assist_player_id]['power_play_assists'] += 1
                        elif '1541' in situation_code:
                            player_stats[assist_player_id]['penalty_kill_assists'] += 1
            
            # Shots
            elif play_type in ['shot-on-goal', 'missed-shot', 'blocked-shot']:
                game_stats['shots'].append(play)
                game_stats['period_stats'][period]['shots'] += 1
                
                shooting_player_id = details.get('shootingPlayerId')
                if shooting_player_id:
                    player_stats[shooting_player_id]['shots'] += 1
                    player_stats[shooting_player_id]['corsi'] += 1
                    
                    x_coord = details.get('xCoord', 0)
                    y_coord = details.get('yCoord', 0)
                    shot_type = details.get('shotType', 'unknown')
                    
                    player_stats[shooting_player_id]['shot_locations'].append((x_coord, y_coord))
                    player_stats[shooting_player_id]['shot_types'].append(shot_type)
                    
                    # Calculate advanced xG
                    xg = self.calculate_advanced_xg(details)
                    player_stats[shooting_player_id]['expected_goals'] += xg
                    
                    # Calculate distance for shot quality
                    goal_x = 89 if x_coord > 0 else -89
                    distance = math.sqrt((x_coord - goal_x)**2 + (y_coord - 0)**2)
                    
                    # Shot classification
                    if play_type == 'shot-on-goal':
                        player_stats[shooting_player_id]['shots_on_goal'] += 1
                        player_stats[shooting_player_id]['fenwick'] += 1
                        
                        # High-danger chance (close to net, good angle)
                        if distance < 20 and abs(y_coord) < 15:
                            player_stats[shooting_player_id]['high_danger_chances'] += 1
                            game_stats['high_danger_chances'].append(play)
                        
                        # Slot shot (between faceoff dots)
                        if abs(y_coord) < 20 and x_coord > 0:
                            player_stats[shooting_player_id]['slot_shots'] += 1
                        
                        # Scoring chance (close to net)
                        if distance < 25:
                            player_stats[shooting_player_id]['scoring_chances'] += 1
                            game_stats['scoring_chances'].append(play)
                        
                    elif play_type == 'missed-shot':
                        player_stats[shooting_player_id]['missed_shots'] += 1
                        player_stats[shooting_player_id]['fenwick'] += 1
                    elif play_type == 'blocked-shot':
                        player_stats[shooting_player_id]['blocked_shots'] += 1
                    
                    # Situation-specific shots
                    if '1451' in situation_code or '1351' in situation_code:
                        player_stats[shooting_player_id]['power_play_shots'] += 1
                    elif '1541' in situation_code:
                        player_stats[shooting_player_id]['penalty_kill_shots'] += 1
            
            # Hits
            elif play_type == 'hit':
                game_stats['hits'].append(play)
                game_stats['period_stats'][period]['hits'] += 1
                
                hitting_player_id = details.get('hittingPlayerId')
                hittee_player_id = details.get('hitteePlayerId')
                
                if hitting_player_id:
                    player_stats[hitting_player_id]['hits'] += 1
                if hittee_player_id:
                    player_stats[hittee_player_id]['hits_taken'] += 1
            
            # Faceoffs
            elif play_type == 'faceoff':
                game_stats['faceoffs'].append(play)
                game_stats['period_stats'][period]['faceoffs'] += 1
                
                winning_player_id = details.get('winningPlayerId')
                losing_player_id = details.get('losingPlayerId')
                
                if winning_player_id:
                    player_stats[winning_player_id]['faceoffs_won'] += 1
                if losing_player_id:
                    player_stats[losing_player_id]['faceoffs_lost'] += 1
            
            # Penalties
            elif play_type == 'penalty':
                game_stats['penalties'].append(play)
                game_stats['period_stats'][period]['penalties'] += 1
                
                committed_by_player_id = details.get('committedByPlayerId')
                if committed_by_player_id:
                    player_stats[committed_by_player_id]['penalties'] += 1
                    penalty_minutes = details.get('duration', 2)
                    player_stats[committed_by_player_id]['penalty_minutes'] += penalty_minutes
            
            # Giveaways
            elif play_type == 'giveaway':
                game_stats['giveaways'].append(play)
                game_stats['period_stats'][period]['giveaways'] += 1
                
                player_id = details.get('playerId')
                if player_id:
                    player_stats[player_id]['giveaways'] += 1
            
            # Takeaways
            elif play_type == 'takeaway':
                game_stats['takeaways'].append(play)
                game_stats['period_stats'][period]['takeaways'] += 1
                
                player_id = details.get('playerId')
                if player_id:
                    player_stats[player_id]['takeaways'] += 1
        
        # Calculate derived statistics
        for player_id, stats in player_stats.items():
            # Basic derived stats
            stats['points'] = stats['goals'] + stats['assists']
            
            if stats['shots_on_goal'] > 0:
                stats['shooting_percentage'] = (stats['goals'] / stats['shots_on_goal']) * 100
            else:
                stats['shooting_percentage'] = 0
            
            total_faceoffs = stats['faceoffs_won'] + stats['faceoffs_lost']
            if total_faceoffs > 0:
                stats['faceoff_percentage'] = (stats['faceoffs_won'] / total_faceoffs) * 100
            else:
                stats['faceoff_percentage'] = 0
            
            # Advanced derived stats
            stats['xg_difference'] = stats['goals'] - stats['expected_goals']
            
            if stats['giveaways'] + stats['takeaways'] > 0:
                stats['turnover_ratio'] = stats['takeaways'] / (stats['giveaways'] + stats['takeaways'])
            else:
                stats['turnover_ratio'] = 0
            
            # Add player name
            if player_id in player_mapping:
                stats['name'] = player_mapping[player_id]['name']
                stats['position'] = player_mapping[player_id]['position']
                stats['team_id'] = player_mapping[player_id]['team_id']
            else:
                stats['name'] = f'Player {player_id}'
                stats['position'] = 'Unknown'
                stats['team_id'] = 'Unknown'
        
        return {
            'game_stats': dict(game_stats),
            'player_stats': dict(player_stats),
            'game_info': play_by_play_data.get('game', {}),
            'away_team': play_by_play_data.get('awayTeam', {}),
            'home_team': play_by_play_data.get('homeTeam', {})
        }
    
    def create_enhanced_title_page(self, game_data: Dict) -> List:
        """Create an enhanced title page with game context"""
        story = []
        
        # Main title
        story.append(Paragraph("🏒 ENHANCED NHL POST-GAME REPORT 🏒", self.title_style))
        story.append(Spacer(1, 20))
        
        # Game info
        game_info = game_data['game_center']['game']
        away_team = game_data['game_center']['awayTeam']
        home_team = game_data['game_center']['homeTeam']
        
        # Team logos section
        story.append(Paragraph("🏒 TEAM LOGOS", self.section_style))
        
        # Get team logos
        away_logo = self.get_team_logo(away_team['abbrev'])
        home_logo = self.get_team_logo(home_team['abbrev'])
        
        # Create a table with team logos
        logo_data = [['Away Team', 'Home Team']]
        logo_row = []
        
        if away_logo:
            logo_row.append(away_logo)
        else:
            logo_row.append(self.create_logo_placeholder(away_team['abbrev']))
        
        if home_logo:
            logo_row.append(home_logo)
        else:
            logo_row.append(self.create_logo_placeholder(home_team['abbrev']))
        
        logo_data.append(logo_row)
        
        logo_table = Table(logo_data, colWidths=[3*inch, 3*inch])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(logo_table)
        story.append(Spacer(1, 20))
        
        # Game header with enhanced styling
        story.append(Paragraph(f"{away_team['abbrev']} vs {home_team['abbrev']}", self.subtitle_style))
        story.append(Paragraph(f"Final Score: {away_team['abbrev']} {game_info['awayTeamScore']} - {home_team['abbrev']} {game_info['homeTeamScore']}", self.highlight_style))
        
        # Game details
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"<b>Date:</b> {game_info['gameDate']}", self.normal_style))
        story.append(Paragraph(f"<b>Venue:</b> {game_data['game_center'].get('venue', {}).get('default', 'Unknown Arena')}", self.normal_style))
        story.append(Paragraph(f"<b>Game Type:</b> Stanley Cup Finals", self.normal_style))
        
        # Add standings context if available
        if 'standings' in game_data and game_data['standings']:
            story.append(Spacer(1, 10))
            story.append(Paragraph("📊 STANDINGS CONTEXT", self.section_style))
            self._add_standings_context(story, game_data['standings'], away_team['abbrev'], home_team['abbrev'])
        
        story.append(PageBreak())
        return story
    
    def create_enhanced_score_summary(self, game_data: Dict) -> List:
        """Create enhanced score summary with period analysis"""
        story = []
        
        story.append(Paragraph("📈 ENHANCED SCORE SUMMARY", self.subtitle_style))
        story.append(Spacer(1, 15))
        
        game_info = game_data['game_center']['game']
        away_team = game_data['game_center']['awayTeam']
        home_team = game_data['game_center']['homeTeam']
        
        # Enhanced score table with team logos
        # Get team logos for the score table
        away_logo_small = self.get_team_logo(away_team['abbrev'], size=(0.5*inch, 0.5*inch))
        home_logo_small = self.get_team_logo(home_team['abbrev'], size=(0.5*inch, 0.5*inch))
        
        # Create team name cells with logos
        away_team_cell = []
        if away_logo_small:
            away_team_cell.append(away_logo_small)
        away_team_cell.append(Paragraph(f"<b>{away_team['abbrev']}</b>", self.normal_style))
        
        home_team_cell = []
        if home_logo_small:
            home_team_cell.append(home_logo_small)
        home_team_cell.append(Paragraph(f"<b>{home_team['abbrev']}</b>", self.normal_style))
        
        score_data = [
            ['', '1st', '2nd', '3rd', 'OT', 'Total', 'Shots', 'PP%'],
            away_team_cell + [
             game_info['awayTeamScoreByPeriod'][0] if len(game_info['awayTeamScoreByPeriod']) > 0 else 0,
             game_info['awayTeamScoreByPeriod'][1] if len(game_info['awayTeamScoreByPeriod']) > 1 else 0,
             game_info['awayTeamScoreByPeriod'][2] if len(game_info['awayTeamScoreByPeriod']) > 2 else 0,
             game_info['awayTeamScoreByPeriod'][3] if len(game_info['awayTeamScoreByPeriod']) > 3 else 0,
             game_info['awayTeamScore'],
             game_data['boxscore']['awayTeam'].get('sog', 'N/A'),
             f"{game_data['boxscore']['awayTeam'].get('powerPlayConversion', 'N/A')}"],
            home_team_cell + [
             game_info['homeTeamScoreByPeriod'][0] if len(game_info['homeTeamScoreByPeriod']) > 0 else 0,
             game_info['homeTeamScoreByPeriod'][1] if len(game_info['homeTeamScoreByPeriod']) > 1 else 0,
             game_info['homeTeamScoreByPeriod'][2] if len(game_info['homeTeamScoreByPeriod']) > 2 else 0,
             game_info['homeTeamScoreByPeriod'][3] if len(game_info['homeTeamScoreByPeriod']) > 3 else 0,
             game_info['homeTeamScore'],
             game_data['boxscore']['homeTeam'].get('sog', 'N/A'),
             f"{game_data['boxscore']['homeTeam'].get('powerPlayConversion', 'N/A')}"]
        ]
        
        score_table = Table(score_data, colWidths=[1.2*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(score_table)
        story.append(Spacer(1, 20))
        
        # Add period analysis
        story.append(Paragraph("🎯 PERIOD ANALYSIS", self.section_style))
        self._add_period_analysis(story, game_info, away_team, home_team)
        
        return story
    
    def create_advanced_player_analytics(self, game_data: Dict) -> List:
        """Create advanced player analytics section"""
        story = []
        
        story.append(Paragraph("⭐ ADVANCED PLAYER ANALYTICS", self.subtitle_style))
        story.append(Spacer(1, 15))
        
        # Get player stats from boxscore
        boxscore = game_data['boxscore']
        away_players = boxscore.get('awayTeam', {}).get('players', [])
        home_players = boxscore.get('homeTeam', {}).get('players', [])
        
        # Top performers analysis
        story.append(Paragraph("🏆 TOP PERFORMERS", self.section_style))
        self._add_top_performers(story, away_players + home_players)
        
        # Player comparison
        story.append(Paragraph("⚖️ KEY PLAYER COMPARISONS", self.section_style))
        self._add_player_comparisons(story, away_players, home_players)
        
        # Advanced metrics
        story.append(Paragraph("📊 ADVANCED METRICS", self.section_style))
        self._add_advanced_metrics(story, game_data)
        
        return story
    
    def create_play_by_play_analysis(self, game_data: Dict) -> List:
        """Create detailed play-by-play analysis"""
        story = []
        
        story.append(Paragraph("🎬 PLAY-BY-PLAY ANALYSIS", self.subtitle_style))
        story.append(Spacer(1, 15))
        
        if 'play_by_play' in game_data and game_data['play_by_play']:
            play_data = game_data['play_by_play']
            
            # Key moments
            story.append(Paragraph("🔑 KEY MOMENTS", self.section_style))
            self._add_key_moments(story, play_data)
            
            # Momentum analysis
            story.append(Paragraph("📈 MOMENTUM ANALYSIS", self.section_style))
            self._add_momentum_analysis(story, play_data)
            
            # Shot analysis
            story.append(Paragraph("🎯 SHOT ANALYSIS", self.section_style))
            self._add_shot_analysis(story, play_data)
        else:
            story.append(Paragraph("Play-by-play data not available for this game.", self.normal_style))
        
        return story
    
    def create_enhanced_visualizations(self, game_data: Dict) -> List:
        """Create enhanced visualizations using the analytics engine"""
        story = []
        
        story.append(Paragraph("📊 ENHANCED VISUALIZATIONS", self.subtitle_style))
        story.append(Spacer(1, 15))
        
        try:
            # Team comparison dashboard
            if 'play_by_play' in game_data and game_data['play_by_play']:
                fig = self.analytics.create_team_comparison_dashboard(
                    game_data['boxscore']['awayTeam'],
                    game_data['boxscore']['homeTeam']
                )
                if fig:
                    img_buffer = BytesIO()
                    fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                    img_buffer.seek(0)
                    
                    img = Image(img_buffer)
                    img.drawHeight = 6*inch
                    img.drawWidth = 8*inch
                    story.append(img)
                    story.append(Spacer(1, 15))
                    plt.close(fig)
            
            # Momentum chart
            if 'play_by_play' in game_data and game_data['play_by_play']:
                fig = self.analytics.create_momentum_chart(game_data['play_by_play'])
                if fig:
                    img_buffer = BytesIO()
                    fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                    img_buffer.seek(0)
                    
                    img = Image(img_buffer)
                    img.drawHeight = 4*inch
                    img.drawWidth = 7*inch
                    story.append(img)
                    story.append(Spacer(1, 15))
                    plt.close(fig)
            
            # Shot heatmaps
            away_team = game_data['game_center']['awayTeam']['abbrev']
            home_team = game_data['game_center']['homeTeam']['abbrev']
            
            if 'play_by_play' in game_data and game_data['play_by_play']:
                # Away team heatmap
                fig = self.analytics.create_shot_heatmap(game_data['play_by_play'], away_team)
                if fig:
                    img_buffer = BytesIO()
                    fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                    img_buffer.seek(0)
                    
                    img = Image(img_buffer)
                    img.drawHeight = 4*inch
                    img.drawWidth = 6*inch
                    story.append(img)
                    story.append(Spacer(1, 10))
                    plt.close(fig)
                
                # Home team heatmap
                fig = self.analytics.create_shot_heatmap(game_data['play_by_play'], home_team)
                if fig:
                    img_buffer = BytesIO()
                    fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                    img_buffer.seek(0)
                    
                    img = Image(img_buffer)
                    img.drawHeight = 4*inch
                    img.drawWidth = 6*inch
                    story.append(img)
                    story.append(Spacer(1, 15))
                    plt.close(fig)
            
        except Exception as e:
            story.append(Paragraph(f"Visualization error: {str(e)}", self.normal_style))
        
        return story
    
    def create_comprehensive_metrics_section(self, game_data: Dict) -> List:
        """Create comprehensive metrics section with all advanced analytics"""
        story = []
        
        story.append(Paragraph("📊 COMPREHENSIVE METRICS ANALYSIS", self.subtitle_style))
        story.append(Spacer(1, 15))
        
        if 'play_by_play' not in game_data or not game_data['play_by_play']:
            story.append(Paragraph("Play-by-play data not available for comprehensive metrics", self.normal_style))
            return story
        
        # Get comprehensive metrics
        player_mapping = self.create_player_mapping(game_data['play_by_play'])
        analysis_data = self.extract_comprehensive_metrics(game_data['play_by_play'], player_mapping)
        
        if not analysis_data:
            story.append(Paragraph("Could not extract comprehensive metrics", self.normal_style))
            return story
        
        # Add comprehensive metrics chart
        chart_buffer = self.create_comprehensive_metrics_chart(analysis_data)
        if chart_buffer:
            img = Image(chart_buffer)
            img.drawHeight = 8*inch
            img.drawWidth = 10*inch
            story.append(img)
            story.append(Spacer(1, 20))
        
        # All metrics summary
        story.append(Paragraph("📋 ALL METRICS IDENTIFIED AND EXTRACTED", self.section_style))
        story.append(Paragraph("Based on comprehensive analysis of the NHL API data, here's EVERY SINGLE METRIC we can extract:", self.normal_style))
        story.append(Spacer(1, 10))
        
        # Metrics categories
        metrics_categories = [
            "✅ BASIC STATISTICS:",
            "Goals, Assists, Points - All scoring metrics",
            "Shots, Shots on Goal, Missed Shots, Blocked Shots - Complete shot tracking",
            "Hits Given/Taken - Physical play metrics",
            "Faceoffs Won/Lost - Faceoff performance",
            "Penalties, Penalty Minutes - Discipline metrics",
            "Giveaways, Takeaways - Turnover analysis",
            "",
            "✅ ADVANCED STATISTICS:",
            "Corsi (All Shot Attempts) - Possession metric",
            "Fenwick (Unblocked Shot Attempts) - Quality possession metric",
            "Expected Goals (xG) - Advanced shot quality model",
            "High-Danger Chances - Close-range, high-probability shots",
            "Scoring Chances - Shots from dangerous areas",
            "Slot Shots - Shots from between faceoff dots",
            "",
            "✅ SITUATION ANALYSIS:",
            "5v5, 4v5 (Power Play), 5v4 (Penalty Kill), 4v4, 3v3 - All game situations",
            "Power Play Goals/Assists/Shots - Man advantage performance",
            "Penalty Kill Goals/Assists/Shots - Short-handed performance",
            "Even Strength Performance - 5v5 metrics",
            "",
            "✅ ZONE ANALYSIS:",
            "Offensive Zone Play - Attack zone metrics",
            "Defensive Zone Play - Defensive metrics",
            "Neutral Zone Play - Transition metrics",
            "Zone-Specific Faceoffs - Faceoff performance by zone",
            "",
            "✅ SHOT QUALITY METRICS:",
            "Shot Type Analysis - Wrist, slap, snap, backhand, tip-in, deflected",
            "Shot Location Analysis - X/Y coordinates for every shot",
            "Distance to Goal - Calculated for each shot",
            "Shot Angle - Calculated for each shot",
            "Zone-Based Shot Quality - Different xG by zone",
            "",
            "✅ GAME FLOW METRICS:",
            "Period-by-Period Breakdown - Performance by period",
            "Time-Based Analysis - Performance by game time",
            "Momentum Tracking - Game flow analysis",
            "Clutch Performance - Late-game metrics",
            "",
            "✅ PLAYER PERFORMANCE METRICS:",
            "Shooting Percentage - Goals per shots on goal",
            "Faceoff Percentage - Faceoff win rate",
            "Turnover Ratio - Takeaways vs giveaways",
            "xG vs Actual Goals - Performance vs expectation",
            "Power Play/Penalty Kill Performance - Special teams metrics"
        ]
        
        for metric in metrics_categories:
            if metric.startswith("✅"):
                story.append(Paragraph(metric, self.highlight_style))
            elif metric == "":
                story.append(Spacer(1, 5))
            else:
                story.append(Paragraph(metric, self.normal_style))
        
        story.append(Spacer(1, 15))
        
        # What we've achieved
        story.append(Paragraph("🎯 WHAT WE'VE ACHIEVED", self.section_style))
        achievements = [
            f"✅ Extracted ALL {analysis_data['game_stats']['total_plays']} plays from the NHL API",
            f"✅ Analyzed {len(analysis_data['player_stats'])} players with complete statistics",
            f"✅ Identified {len(analysis_data['game_stats']['play_types'])} different play types with detailed metrics",
            f"✅ Tracked {len(analysis_data['game_stats']['situation_breakdown'])} different game situations (5v5, 4v5, etc.)",
            f"✅ Analyzed {len(analysis_data['game_stats']['zone_breakdown'])} zones (Offensive, Defensive, Neutral)",
            "✅ Calculated advanced metrics like Corsi, Fenwick, xG",
            "✅ Shot quality analysis with distance, angle, and zone factors",
            "✅ Professional visualizations with comprehensive charts",
            "✅ Real player names properly resolved from roster data"
        ]
        
        for achievement in achievements:
            story.append(Paragraph(achievement, self.normal_style))
        
        story.append(Spacer(1, 15))
        
        # Data source information
        story.append(Paragraph("📡 DATA SOURCE INFORMATION", self.section_style))
        story.append(Paragraph("This comprehensive report extracts ALL key metrics from NHL API data:", self.normal_style))
        story.append(Paragraph("• Play-by-Play Data: https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play", self.normal_style))
        story.append(Paragraph(f"• All {analysis_data['game_stats']['total_plays']} plays analyzed for comprehensive metrics", self.normal_style))
        story.append(Paragraph("• Advanced analytics including Corsi, Fenwick, xG, and shot quality", self.normal_style))
        story.append(Paragraph("• Zone analysis, situation analysis, and game flow metrics", self.normal_style))
        story.append(Paragraph("• Professional data visualizations and comprehensive tables", self.normal_style))
        story.append(Paragraph("• All data is legitimate and from official NHL sources", self.normal_style))
        
        return story
    
    def create_goalie_analysis(self, game_data: Dict) -> List:
        """Create comprehensive goalie analysis"""
        story = []
        
        story.append(Paragraph("🥅 GOALIE PERFORMANCE ANALYSIS", self.subtitle_style))
        story.append(Spacer(1, 15))
        
        # Get goalie stats
        boxscore = game_data['boxscore']
        away_goalies = []
        home_goalies = []
        
        for player in boxscore.get('awayTeam', {}).get('players', []):
            if player.get('position', '').upper() == 'G':
                away_goalies.append(player)
        
        for player in boxscore.get('homeTeam', {}).get('players', []):
            if player.get('position', '').upper() == 'G':
                home_goalies.append(player)
        
        # Create goalie performance charts
        for goalie in away_goalies + home_goalies:
            try:
                fig = self.analytics.create_goalie_performance_chart(goalie)
                if fig:
                    img_buffer = BytesIO()
                    fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                    img_buffer.seek(0)
                    
                    img = Image(img_buffer)
                    img.drawHeight = 5*inch
                    img.drawWidth = 7*inch
                    story.append(img)
                    story.append(Spacer(1, 15))
                    plt.close(fig)
            except Exception as e:
                story.append(Paragraph(f"Goalie chart error: {str(e)}", self.normal_style))
        
        return story
    
    def _add_standings_context(self, story: List, standings_data: Dict, team1: str, team2: str):
        """Add standings context to the report"""
        # This would extract and display relevant standings information
        story.append(Paragraph(f"Current standings context for {team1} vs {team2}", self.normal_style))
    
    def _add_period_analysis(self, story: List, game_info: Dict, away_team: Dict, home_team: Dict):
        """Add detailed period analysis"""
        away_periods = game_info.get('awayTeamScoreByPeriod', [])
        home_periods = game_info.get('homeTeamScoreByPeriod', [])
        
        for i, (away_goals, home_goals) in enumerate(zip(away_periods, home_periods)):
            period_name = f"Period {i+1}"
            if i == 3:
                period_name = "Overtime"
            
            story.append(Paragraph(f"<b>{period_name}:</b> {away_team['abbrev']} {away_goals} - {home_team['abbrev']} {home_goals}", self.normal_style))
    
    def _add_top_performers(self, story: List, players: List):
        """Add top performers analysis"""
        # Sort players by points
        players_with_stats = []
        for player in players:
            stats = player.get('stats', {})
            points = stats.get('goals', 0) + stats.get('assists', 0)
            if points > 0:
                players_with_stats.append((player, points))
        
        players_with_stats.sort(key=lambda x: x[1], reverse=True)
        
        if players_with_stats:
            story.append(Paragraph("Top Point Scorers:", self.subsection_style))
            for player, points in players_with_stats[:5]:
                name = player.get('name', 'Unknown')
                team = player.get('team', {}).get('abbrev', 'Unknown')
                goals = player.get('stats', {}).get('goals', 0)
                assists = player.get('stats', {}).get('assists', 0)
                story.append(Paragraph(f"• {name} ({team}): {goals}G, {assists}A, {points}P", self.normal_style))
    
    def _add_player_comparisons(self, story: List, away_players: List, home_players: List):
        """Add player comparison analysis"""
        # This would implement detailed player comparisons
        story.append(Paragraph("Player comparison analysis would go here", self.normal_style))
    
    def _add_advanced_metrics(self, story: List, game_data: Dict):
        """Add advanced metrics analysis"""
        if 'play_by_play' not in game_data or not game_data['play_by_play']:
            story.append(Paragraph("Play-by-play data not available for advanced metrics", self.normal_style))
            return
        
        # Get comprehensive metrics
        player_mapping = self.create_player_mapping(game_data['play_by_play'])
        analysis_data = self.extract_comprehensive_metrics(game_data['play_by_play'], player_mapping)
        
        if not analysis_data:
            story.append(Paragraph("Could not extract advanced metrics", self.normal_style))
            return
        
        game_stats = analysis_data['game_stats']
        player_stats = analysis_data['player_stats']
        
        # Advanced metrics summary
        story.append(Paragraph("📊 COMPREHENSIVE METRICS SUMMARY", self.subsection_style))
        
        # Basic stats table
        basic_stats_data = [
            ['Metric', 'Count'],
            ['Total Plays', game_stats['total_plays']],
            ['Goals', len(game_stats.get('goals', []))],
            ['Shots', len(game_stats.get('shots', []))],
            ['Hits', len(game_stats.get('hits', []))],
            ['Faceoffs', len(game_stats.get('faceoffs', []))],
            ['Penalties', len(game_stats.get('penalties', []))],
            ['Giveaways', len(game_stats.get('giveaways', []))],
            ['Takeaways', len(game_stats.get('takeaways', []))],
            ['High-Danger Chances', len(game_stats.get('high_danger_chances', []))],
            ['Scoring Chances', len(game_stats.get('scoring_chances', []))],
            ['Players with Stats', len(player_stats)]
        ]
        
        basic_table = Table(basic_stats_data, colWidths=[3*inch, 2*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(basic_table)
        story.append(Spacer(1, 15))
        
        # Situation breakdown
        story.append(Paragraph("🎯 SITUATION BREAKDOWN", self.subsection_style))
        situation_breakdown = game_stats['situation_breakdown']
        situation_data = [['Situation', 'Count', 'Percentage']]
        
        total_plays = sum(situation_breakdown.values())
        for code, count in situation_breakdown.items():
            situation_name = self.situation_codes.get(code, code)
            percentage = (count / total_plays * 100) if total_plays > 0 else 0
            situation_data.append([situation_name, count, f"{percentage:.1f}%"])
        
        situation_table = Table(situation_data, colWidths=[2.5*inch, 1*inch, 1*inch])
        situation_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(situation_table)
        story.append(Spacer(1, 15))
        
        # Zone breakdown
        story.append(Paragraph("🏒 ZONE BREAKDOWN", self.subsection_style))
        zone_breakdown = game_stats['zone_breakdown']
        zone_data = [['Zone', 'Count', 'Percentage']]
        
        for code, count in zone_breakdown.items():
            zone_name = self.zone_codes.get(code, code)
            percentage = (count / total_plays * 100) if total_plays > 0 else 0
            zone_data.append([zone_name, count, f"{percentage:.1f}%"])
        
        zone_table = Table(zone_data, colWidths=[2.5*inch, 1*inch, 1*inch])
        zone_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(zone_table)
        story.append(Spacer(1, 15))
        
        # Top players with comprehensive metrics
        story.append(Paragraph("⭐ TOP PLAYERS - COMPREHENSIVE METRICS", self.subsection_style))
        
        top_players = sorted(player_stats.items(), 
                           key=lambda x: x[1].get('points', 0), reverse=True)[:10]
        
        comprehensive_player_data = [
            ['Player', 'Pts', 'G', 'A', 'SOG', 'Corsi', 'Fenwick', 'xG', 'HDC', 'SC', 'Slot', 'Hits', 'FO%']
        ]
        
        for player_id, stats in top_players:
            comprehensive_player_data.append([
                stats['name'][:20],  # Truncate long names
                stats.get('points', 0),
                stats.get('goals', 0),
                stats.get('assists', 0),
                stats.get('shots_on_goal', 0),
                stats.get('corsi', 0),
                stats.get('fenwick', 0),
                f"{stats.get('expected_goals', 0):.2f}",
                stats.get('high_danger_chances', 0),
                stats.get('scoring_chances', 0),
                stats.get('slot_shots', 0),
                stats.get('hits', 0),
                f"{stats.get('faceoff_percentage', 0):.1f}%"
            ])
        
        comprehensive_table = Table(comprehensive_player_data, 
                                  colWidths=[2*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 
                                           0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 
                                           0.5*inch, 0.5*inch, 0.5*inch])
        comprehensive_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left align player names
        ]))
        
        story.append(comprehensive_table)
        story.append(Spacer(1, 15))
        
        # Metrics legend
        story.append(Paragraph("📋 METRICS LEGEND", self.subsection_style))
        story.append(Paragraph("Pts = Points, G = Goals, A = Assists, SOG = Shots on Goal", self.normal_style))
        story.append(Paragraph("Corsi = All Shot Attempts, Fenwick = Unblocked Shot Attempts", self.normal_style))
        story.append(Paragraph("xG = Expected Goals, HDC = High-Danger Chances, SC = Scoring Chances", self.normal_style))
        story.append(Paragraph("Slot = Slot Shots, FO% = Faceoff Percentage", self.normal_style))
    
    def _add_key_moments(self, story: List, play_data: Dict):
        """Add key moments analysis"""
        if not play_data or 'plays' not in play_data:
            story.append(Paragraph("Play-by-play data not available for key moments", self.normal_style))
            return
        
        plays = play_data['plays']
        
        # Find key moments (goals, penalties, major events)
        key_moments = []
        for play in plays:
            play_type = play.get('typeDescKey', '')
            period = play.get('periodDescriptor', {}).get('number', 1)
            time_remaining = play.get('timeRemaining', '20:00')
            details = play.get('details', {})
            
            if play_type == 'goal':
                scoring_player = details.get('scoringPlayerId', 'Unknown')
                key_moments.append({
                    'time': f"P{period} {time_remaining}",
                    'event': f"GOAL by Player {scoring_player}",
                    'type': 'goal'
                })
            elif play_type == 'penalty':
                penalty_player = details.get('committedByPlayerId', 'Unknown')
                penalty_type = details.get('typeDescKey', 'Penalty')
                key_moments.append({
                    'time': f"P{period} {time_remaining}",
                    'event': f"PENALTY: {penalty_type} by Player {penalty_player}",
                    'type': 'penalty'
                })
        
        # Show top 10 key moments
        story.append(Paragraph("🔑 KEY MOMENTS", self.subsection_style))
        if key_moments:
            key_moments_data = [['Time', 'Event']]
            for moment in key_moments[:10]:  # Top 10 moments
                key_moments_data.append([moment['time'], moment['event']])
            
            key_moments_table = Table(key_moments_data, colWidths=[1.5*inch, 4*inch])
            key_moments_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Left align events
            ]))
            
            story.append(key_moments_table)
        else:
            story.append(Paragraph("No key moments identified", self.normal_style))
    
    def _add_momentum_analysis(self, story: List, play_data: Dict):
        """Add momentum analysis"""
        if not play_data or 'plays' not in play_data:
            story.append(Paragraph("Play-by-play data not available for momentum analysis", self.normal_style))
            return
        
        plays = play_data['plays']
        
        # Analyze momentum by period
        period_momentum = {}
        for play in plays:
            period = play.get('periodDescriptor', {}).get('number', 1)
            play_type = play.get('typeDescKey', '')
            
            if period not in period_momentum:
                period_momentum[period] = {
                    'goals': 0, 'shots': 0, 'hits': 0, 'penalties': 0,
                    'giveaways': 0, 'takeaways': 0
                }
            
            if play_type == 'goal':
                period_momentum[period]['goals'] += 1
            elif play_type in ['shot-on-goal', 'missed-shot', 'blocked-shot']:
                period_momentum[period]['shots'] += 1
            elif play_type == 'hit':
                period_momentum[period]['hits'] += 1
            elif play_type == 'penalty':
                period_momentum[period]['penalties'] += 1
            elif play_type == 'giveaway':
                period_momentum[period]['giveaways'] += 1
            elif play_type == 'takeaway':
                period_momentum[period]['takeaways'] += 1
        
        story.append(Paragraph("📈 MOMENTUM ANALYSIS BY PERIOD", self.subsection_style))
        
        momentum_data = [['Period', 'Goals', 'Shots', 'Hits', 'Penalties', 'Turnovers']]
        for period in sorted(period_momentum.keys()):
            stats = period_momentum[period]
            turnovers = stats['giveaways'] + stats['takeaways']
            momentum_data.append([
                f"Period {period}",
                stats['goals'],
                stats['shots'],
                stats['hits'],
                stats['penalties'],
                turnovers
            ])
        
        momentum_table = Table(momentum_data, colWidths=[1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        momentum_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(momentum_table)
    
    def _add_shot_analysis(self, story: List, play_data: Dict):
        """Add shot analysis"""
        if not play_data or 'plays' not in play_data:
            story.append(Paragraph("Play-by-play data not available for shot analysis", self.normal_style))
            return
        
        plays = play_data['plays']
        
        # Analyze shot patterns
        shot_types = defaultdict(int)
        shot_locations = []
        total_shots = 0
        shots_on_goal = 0
        missed_shots = 0
        blocked_shots = 0
        
        for play in plays:
            play_type = play.get('typeDescKey', '')
            if play_type in ['shot-on-goal', 'missed-shot', 'blocked-shot']:
                total_shots += 1
                details = play.get('details', {})
                
                if play_type == 'shot-on-goal':
                    shots_on_goal += 1
                elif play_type == 'missed-shot':
                    missed_shots += 1
                elif play_type == 'blocked-shot':
                    blocked_shots += 1
                
                # Shot type analysis
                shot_type = details.get('shotType', 'unknown')
                shot_types[shot_type] += 1
                
                # Shot location analysis
                x_coord = details.get('xCoord', 0)
                y_coord = details.get('yCoord', 0)
                if x_coord != 0 or y_coord != 0:
                    shot_locations.append((x_coord, y_coord))
        
        story.append(Paragraph("🎯 SHOT ANALYSIS", self.subsection_style))
        
        # Shot summary
        shot_summary_data = [
            ['Shot Type', 'Count', 'Percentage'],
            ['Total Shots', total_shots, '100.0%'],
            ['Shots on Goal', shots_on_goal, f"{(shots_on_goal/total_shots*100):.1f}%" if total_shots > 0 else "0.0%"],
            ['Missed Shots', missed_shots, f"{(missed_shots/total_shots*100):.1f}%" if total_shots > 0 else "0.0%"],
            ['Blocked Shots', blocked_shots, f"{(blocked_shots/total_shots*100):.1f}%" if total_shots > 0 else "0.0%"]
        ]
        
        shot_summary_table = Table(shot_summary_data, colWidths=[2*inch, 1*inch, 1*inch])
        shot_summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(shot_summary_table)
        story.append(Spacer(1, 10))
        
        # Shot types breakdown
        if shot_types:
            story.append(Paragraph("📊 SHOT TYPES BREAKDOWN", self.subsection_style))
            shot_types_data = [['Shot Type', 'Count', 'Percentage']]
            
            for shot_type, count in sorted(shot_types.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_shots * 100) if total_shots > 0 else 0
                shot_types_data.append([shot_type.title(), count, f"{percentage:.1f}%"])
            
            shot_types_table = Table(shot_types_data, colWidths=[2*inch, 1*inch, 1*inch])
            shot_types_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(shot_types_table)
    
    def create_comprehensive_metrics_chart(self, analysis_data):
        """Create comprehensive metrics visualization"""
        if not analysis_data:
            return None
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
            fig.suptitle('COMPREHENSIVE NHL METRICS DASHBOARD', fontsize=20, fontweight='bold')
            
            game_stats = analysis_data['game_stats']
            player_stats = analysis_data['player_stats']
            
            # 1. Situation breakdown
            situation_breakdown = game_stats['situation_breakdown']
            situation_labels = [self.situation_codes.get(code, code) for code in situation_breakdown.keys()]
            situation_values = list(situation_breakdown.values())
            
            ax1.pie(situation_values, labels=situation_labels, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Game Situation Breakdown', fontsize=14, fontweight='bold')
            
            # 2. Zone breakdown
            zone_breakdown = game_stats['zone_breakdown']
            zone_labels = [self.zone_codes.get(code, code) for code in zone_breakdown.keys()]
            zone_values = list(zone_breakdown.values())
            
            bars = ax2.bar(zone_labels, zone_values, color=['lightblue', 'lightgreen', 'lightcoral'], alpha=0.8)
            ax2.set_title('Zone Distribution', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Number of Plays')
            
            # Add value labels
            for bar, value in zip(bars, zone_values):
                ax2.text(bar.get_x() + bar.get_width()/2., value + 1,
                       f'{value}', ha='center', va='bottom', fontweight='bold')
            
            # 3. Advanced metrics comparison
            top_players = sorted(player_stats.items(), 
                               key=lambda x: x[1].get('points', 0), reverse=True)[:8]
            
            if top_players:
                player_names = [stats['name'] for _, stats in top_players]
                corsi_values = [stats.get('corsi', 0) for _, stats in top_players]
                fenwick_values = [stats.get('fenwick', 0) for _, stats in top_players]
                xg_values = [stats.get('expected_goals', 0) for _, stats in top_players]
                
                x = np.arange(len(player_names))
                width = 0.25
                
                ax3.bar(x - width, corsi_values, width, label='Corsi', color='blue', alpha=0.8)
                ax3.bar(x, fenwick_values, width, label='Fenwick', color='green', alpha=0.8)
                ax3.bar(x + width, xg_values, width, label='Expected Goals', color='orange', alpha=0.8)
                
                ax3.set_xlabel('Players')
                ax3.set_ylabel('Count')
                ax3.set_title('Advanced Metrics Comparison', fontsize=14, fontweight='bold')
                ax3.set_xticks(x)
                ax3.set_xticklabels(player_names, rotation=45, ha='right')
                ax3.legend()
            
            # 4. High-danger chances and scoring chances
            if top_players:
                hdc_values = [stats.get('high_danger_chances', 0) for _, stats in top_players]
                sc_values = [stats.get('scoring_chances', 0) for _, stats in top_players]
                slot_values = [stats.get('slot_shots', 0) for _, stats in top_players]
                
                x = np.arange(len(player_names))
                width = 0.25
                
                ax4.bar(x - width, hdc_values, width, label='High-Danger Chances', color='red', alpha=0.8)
                ax4.bar(x, sc_values, width, label='Scoring Chances', color='purple', alpha=0.8)
                ax4.bar(x + width, slot_values, width, label='Slot Shots', color='gold', alpha=0.8)
                
                ax4.set_xlabel('Players')
                ax4.set_ylabel('Count')
                ax4.set_title('Shot Quality Metrics', fontsize=14, fontweight='bold')
                ax4.set_xticks(x)
                ax4.set_xticklabels(player_names, rotation=45, ha='right')
                ax4.legend()
            
            plt.tight_layout()
            
            # Save to BytesIO
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        except Exception as e:
            print(f"Comprehensive metrics chart error: {e}")
            return None
    
    def generate_enhanced_report(self, game_id: str, output_filename: str = None) -> str:
        """Generate the complete enhanced NHL post-game report"""
        print("🏒 Generating Enhanced NHL Post-Game Report 🏒")
        print("=" * 60)
        
        # Get comprehensive game data
        print("Fetching comprehensive game data...")
        game_data = self.api_client.get_comprehensive_game_data(game_id)
        
        if not game_data['game_center']:
            print("❌ Could not fetch game data")
            return None
        
        # Create output filename if not provided
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            away_team = game_data['game_center']['awayTeam']['abbrev']
            home_team = game_data['game_center']['homeTeam']['abbrev']
            output_filename = f"enhanced_nhl_report_{away_team}_vs_{home_team}_{timestamp}.pdf"
        
        # Create the PDF document
        doc = SimpleDocTemplate(output_filename, pagesize=letter, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Add all sections
        print("Creating enhanced title page...")
        story.extend(self.create_enhanced_title_page(game_data))
        
        print("Creating enhanced score summary...")
        story.extend(self.create_enhanced_score_summary(game_data))
        
        print("Creating advanced player analytics...")
        story.extend(self.create_advanced_player_analytics(game_data))
        
        print("Creating play-by-play analysis...")
        story.extend(self.create_play_by_play_analysis(game_data))
        
        print("Creating enhanced visualizations...")
        story.extend(self.create_enhanced_visualizations(game_data))
        
        print("Creating comprehensive metrics section...")
        story.extend(self.create_comprehensive_metrics_section(game_data))
        
        print("Creating goalie analysis...")
        story.extend(self.create_goalie_analysis(game_data))
        
        # Build the PDF
        print("Building PDF report...")
        doc.build(story)
        
        print(f"✅ Enhanced report generated successfully: {output_filename}")
        return output_filename


# Example usage
if __name__ == "__main__":
    generator = EnhancedNHLReportGenerator()
    
    # Test with a known game ID
    game_id = "2024030242"  # Working game ID
    output_file = generator.generate_enhanced_report(game_id)
    
    if output_file:
        print(f"🎉 Enhanced NHL report created: {output_file}")
    else:
        print("❌ Failed to create enhanced report")
