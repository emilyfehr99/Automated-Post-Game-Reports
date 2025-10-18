from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
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

class PostGameReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the single-page analytics report"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.darkred,
            alignment=TA_LEFT,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceAfter=3,
            fontName='Helvetica'
        )
        
        # Stat text style
        self.stat_style = ParagraphStyle(
            'CustomStat',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.darkgreen,
            alignment=TA_LEFT,
            spaceAfter=3,
            fontName='Helvetica-Bold'
        )
        
        # Small text style for compact layout
        self.small_style = ParagraphStyle(
            'CustomSmall',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceAfter=2,
            fontName='Helvetica'
        )
    
    def create_header_section(self, game_data):
        """Create compact header with game info and final score"""
        story = []
        
        game_info = game_data['game_center']['game']
        away_team = game_data['game_center']['awayTeam']
        home_team = game_data['game_center']['homeTeam']
        
        # Game header with score
        story.append(Paragraph(f"NHL POST-GAME ANALYTICS REPORT", self.title_style))
        story.append(Paragraph(f"{away_team['abbrev']} vs {home_team['abbrev']} • {game_info['gameDate']}", self.subtitle_style))
        
        # Final score display
        away_score = game_info['awayTeamScore']
        home_score = game_info['homeTeamScore']
        winner = away_team['abbrev'] if away_score > home_score else home_team['abbrev']
        
        score_text = f"<b>FINAL: {away_team['abbrev']} {away_score} - {home_team['abbrev']} {home_score}</b>"
        story.append(Paragraph(score_text, self.stat_style))
        story.append(Paragraph(f"Winner: {winner}", self.normal_style))
        
        return story
    
    def create_analytics_summary(self, game_data):
        """Create key analytics summary section"""
        story = []
        
        story.append(Paragraph("KEY ANALYTICS INSIGHTS", self.section_style))
        
        # Get team stats from boxscore
        boxscore = game_data['boxscore']
        away_stats = boxscore['awayTeam']
        home_stats = boxscore['homeTeam']
        
        # Calculate advanced metrics
        away_shots = away_stats.get('sog', 0)
        home_shots = home_stats.get('sog', 0)
        away_goals = away_stats['score']
        home_goals = home_stats['score']
        
        # Shooting percentage
        away_shooting_pct = (away_goals / away_shots * 100) if away_shots > 0 else 0
        home_shooting_pct = (home_goals / home_shots * 100) if home_shots > 0 else 0
        
        # Create analytics table
        analytics_data = [
            ['Metric', away_stats['abbrev'], home_stats['abbrev'], 'Advantage'],
            ['Shooting %', f"{away_shooting_pct:.1f}%", f"{home_shooting_pct:.1f}%", 
             away_stats['abbrev'] if away_shooting_pct > home_shooting_pct else home_stats['abbrev']],
            ['Power Play', away_stats.get('powerPlayConversion', 'N/A'), home_stats.get('powerPlayConversion', 'N/A'), 'N/A'],
            ['Faceoff %', f"{(away_stats.get('faceoffWins', 0) / (away_stats.get('faceoffWins', 0) + home_stats.get('faceoffWins', 0)) * 100):.1f}%" if (away_stats.get('faceoffWins', 0) + home_stats.get('faceoffWins', 0)) > 0 else "N/A",
             f"{(home_stats.get('faceoffWins', 0) / (away_stats.get('faceoffWins', 0) + home_stats.get('faceoffWins', 0)) * 100):.1f}%" if (away_stats.get('faceoffWins', 0) + home_stats.get('faceoffWins', 0)) > 0 else "N/A", 'N/A'],
            ['Hits', away_stats.get('hits', 0), home_stats.get('hits', 0),
             away_stats['abbrev'] if away_stats.get('hits', 0) > home_stats.get('hits', 0) else home_stats['abbrev']],
            ['Blocked Shots', away_stats.get('blockedShots', 0), home_stats.get('blockedShots', 0),
             away_stats['abbrev'] if away_stats.get('blockedShots', 0) > home_stats.get('blockedShots', 0) else home_stats['abbrev']]
        ]
        
        analytics_table = Table(analytics_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.1*inch])
        analytics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(analytics_table)
        story.append(Spacer(1, 8))
        
        return story
    
    def create_period_analysis(self, game_data):
        """Create period-by-period analysis with momentum indicators"""
        story = []
        
        story.append(Paragraph("PERIOD ANALYSIS & MOMENTUM", self.section_style))
        
        game_info = game_data['game_center']['game']
        away_periods = game_info.get('awayTeamScoreByPeriod', [0, 0, 0])
        home_periods = game_info.get('homeTeamScoreByPeriod', [0, 0, 0])
        
        # Ensure we have at least 3 periods
        while len(away_periods) < 3:
            away_periods.append(0)
        while len(home_periods) < 3:
            home_periods.append(0)
        
        # Create period analysis table
        period_data = [['Period', 'Away', 'Home', 'Momentum', 'Key Insight']]
        
        periods = ['1st', '2nd', '3rd']
        if len(away_periods) > 3:
            periods.append('OT')
        
        for i, period in enumerate(periods):
            away_score = away_periods[i] if i < len(away_periods) else 0
            home_score = home_periods[i] if i < len(home_periods) else 0
            
            # Determine momentum
            if away_score > home_score:
                momentum = "Away"
                insight = f"{game_data['game_center']['awayTeam']['abbrev']} controlled play"
            elif home_score > away_score:
                momentum = "Home"
                insight = f"{game_data['game_center']['homeTeam']['abbrev']} dominated period"
            else:
                momentum = "Even"
                insight = "Balanced period"
            
            period_data.append([period, away_score, home_score, momentum, insight])
        
        period_table = Table(period_data, colWidths=[0.8*inch, 0.8*inch, 0.8*inch, 1*inch, 2.6*inch])
        period_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),  # Left align insights
        ]))
        
        story.append(period_table)
        story.append(Spacer(1, 8))
        
        return story
    
    def create_player_analytics(self, game_data):
        """Create player performance analytics section"""
        story = []
        
        story.append(Paragraph("PLAYER PERFORMANCE ANALYTICS", self.section_style))
        
        # Get player stats from boxscore
        boxscore = game_data['boxscore']
        away_players = boxscore.get('awayTeam', {}).get('players', [])
        home_players = boxscore.get('homeTeam', {}).get('players', [])
        
        all_players = away_players + home_players
        
        # Find top performers with advanced metrics
        performers = []
        
        for player in all_players:
            stats = player.get('stats', {})
            goals = stats.get('goals', 0)
            assists = stats.get('assists', 0)
            points = goals + assists
            
            if points > 0:
                team = player.get('team', {}).get('abbrev', 'Unknown')
                performers.append({
                    'name': player.get('name', 'Unknown'),
                    'team': team,
                    'goals': goals,
                    'assists': assists,
                    'points': points,
                    'efficiency': f"{(points / 1):.1f}" if points > 0 else "0.0"  # Points per game
                })
        
        # Sort by points
        performers.sort(key=lambda x: x['points'], reverse=True)
        
        if performers:
            # Create top performers table
            performer_data = [['Player', 'Team', 'G', 'A', 'Pts', 'Efficiency']]
            for player in performers[:6]:  # Top 6 performers
                performer_data.append([
                    player['name'][:15],  # Truncate long names
                    player['team'],
                    player['goals'],
                    player['assists'],
                    player['points'],
                    player['efficiency']
                ])
            
            performer_table = Table(performer_data, colWidths=[2*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.8*inch])
            performer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
            ]))
            story.append(performer_table)
        else:
            story.append(Paragraph("No player performance data available", self.normal_style))
        
        story.append(Spacer(1, 8))
        return story
    
    def create_goalie_analytics(self, game_data):
        """Create goalie performance analytics"""
        story = []
        
        story.append(Paragraph("GOALIE PERFORMANCE ANALYTICS", self.section_style))
        
        # Get goalie stats from boxscore
        boxscore = game_data['boxscore']
        away_goalies = []
        home_goalies = []
        
        # Find goalies in player lists
        for player in boxscore.get('awayTeam', {}).get('players', []):
            if player.get('position', '').upper() == 'G':
                away_goalies.append(player)
        
        for player in boxscore.get('homeTeam', {}).get('players', []):
            if player.get('position', '').upper() == 'G':
                home_goalies.append(player)
        
        # Create goalie analytics table
        goalie_data = [['Team', 'Goalie', 'SV%', 'GAA', 'Quality Start']]
        
        for goalie in away_goalies:
            stats = goalie.get('stats', {})
            shots_against = stats.get('shotsAgainst', 0)
            saves = stats.get('saves', 0)
            goals_against = stats.get('goalsAgainst', 0)
            save_pct = f"{(saves/shots_against*100):.1f}%" if shots_against > 0 else "N/A"
            gaa = f"{(goals_against/1):.2f}" if goals_against > 0 else "0.00"  # Goals against average per game
            
            # Quality start indicator (save % > 91.7% or goals against < 2)
            quality_start = "Yes" if (saves/shots_against*100 > 91.7 or goals_against < 2) else "No"
            
            goalie_data.append([
                boxscore['awayTeam']['abbrev'],
                goalie.get('name', 'Unknown')[:12],  # Truncate long names
                save_pct,
                gaa,
                quality_start
            ])
        
        for goalie in home_goalies:
            stats = goalie.get('stats', {})
            shots_against = stats.get('shotsAgainst', 0)
            saves = stats.get('saves', 0)
            goals_against = stats.get('goalsAgainst', 0)
            save_pct = f"{(saves/shots_against*100):.1f}%" if shots_against > 0 else "N/A"
            gaa = f"{(goals_against/1):.2f}" if goals_against > 0 else "0.00"
            
            quality_start = "Yes" if (saves/shots_against*100 > 91.7 or goals_against < 2) else "No"
            
            goalie_data.append([
                boxscore['homeTeam']['abbrev'],
                goalie.get('name', 'Unknown')[:12],
                save_pct,
                gaa,
                quality_start
            ])
        
        if len(goalie_data) > 1:
            goalie_table = Table(goalie_data, colWidths=[1*inch, 1.5*inch, 0.8*inch, 0.8*inch, 1.2*inch])
            goalie_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
            ]))
            story.append(goalie_table)
        else:
            story.append(Paragraph("No goalie performance data available", self.normal_style))
        
        story.append(Spacer(1, 8))
        return story
    
    def create_game_insights(self, game_data):
        """Create game insights and analysis section"""
        story = []
        
        story.append(Paragraph("GAME INSIGHTS & ANALYSIS", self.section_style))
        
        # Analyze the game flow
        game_info = game_data['game_center']['game']
        away_team = game_data['game_center']['awayTeam']
        home_team = game_data['game_center']['homeTeam']
        
        away_score = game_info['awayTeamScore']
        home_score = game_info['homeTeamScore']
        
        # Game flow analysis
        if away_score > home_score:
            winner = away_team['abbrev']
            loser = home_team['abbrev']
            margin = away_score - home_score
        else:
            winner = home_team['abbrev']
            loser = away_team['abbrev']
            margin = home_score - away_score
        
        # Create insights table
        insights_data = [
            ['Aspect', 'Analysis', 'Impact'],
            ['Game Control', f"{winner} dominated possession and scoring", 'High'],
            ['Key Factor', f"{'Goalie performance' if margin <= 2 else 'Offensive efficiency'}", 'Medium'],
            ['Momentum Shift', f"{'Early lead' if margin > 2 else 'Late game heroics'}", 'Medium'],
            ['Special Teams', f"{'Power play success' if margin > 1 else 'Penalty kill dominance'}", 'Medium']
        ]
        
        insights_table = Table(insights_data, colWidths=[1.5*inch, 3*inch, 1*inch])
        insights_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Left align analysis
        ]))
        
        story.append(insights_table)
        story.append(Spacer(1, 8))
        
        return story
    
    def create_compact_visualizations(self, game_data):
        """Create compact charts for single-page layout"""
        story = []
        
        story.append(Paragraph("PERFORMANCE VISUALIZATIONS", self.section_style))
        
        try:
            # Create a compact combined chart
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
            
            # Chart 1: Shots comparison
            boxscore = game_data['boxscore']
            away_team = boxscore['awayTeam']['abbrev']
            home_team = boxscore['homeTeam']['abbrev']
            away_shots = boxscore['awayTeam'].get('sog', 0)
            home_shots = boxscore['homeTeam'].get('sog', 0)
            
            teams = [away_team, home_team]
            shots = [away_shots, home_shots]
            colors_chart = ['#C8102E', '#FF6B35']
            
            bars1 = ax1.bar(teams, shots, color=colors_chart, alpha=0.8)
            ax1.set_title('Shots on Goal', fontsize=10, fontweight='bold')
            ax1.set_ylabel('Shots', fontsize=8)
            
            # Add value labels
            for bar, shot in zip(bars1, shots):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{shot}', ha='center', va='bottom', fontweight='bold', fontsize=8)
            
            # Chart 2: Scoring by period
            game_info = game_data['game_center']['game']
            away_periods = game_info.get('awayTeamScoreByPeriod', [0, 0, 0])
            home_periods = game_info.get('homeTeamScoreByPeriod', [0, 0, 0])
            
            periods = ['1st', '2nd', '3rd']
            x = np.arange(len(periods))
            width = 0.35
            
            bars2 = ax2.bar(x - width/2, away_periods[:3], width, 
                           label=away_team, color='#C8102E', alpha=0.8)
            bars3 = ax2.bar(x + width/2, home_periods[:3], width, 
                           label=home_team, color='#FF6B35', alpha=0.8)
            
            ax2.set_title('Scoring by Period', fontsize=10, fontweight='bold')
            ax2.set_ylabel('Goals', fontsize=8)
            ax2.set_xticks(x)
            ax2.set_xticklabels(periods, fontsize=8)
            ax2.legend(fontsize=7)
            
            plt.tight_layout()
            
            # Save to BytesIO and convert to ReportLab Image
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=200, bbox_inches='tight')
            img_buffer.seek(0)
            
            # Create ReportLab Image
            img = Image(img_buffer)
            img.drawHeight = 3*inch
            img.drawWidth = 7*inch
            
            story.append(img)
            plt.close()
            
        except Exception as e:
            story.append(Paragraph(f"Chart generation error: {str(e)}", self.small_style))
        
        return story
    
    def generate_analytics_report(self, game_data, output_filename):
        """Generate the single-page analytics-focused report"""
        doc = SimpleDocTemplate(output_filename, pagesize=letter, rightMargin=36, leftMargin=36, 
                              topMargin=36, bottomMargin=36)
        
        story = []
        
        # Add all sections for single-page layout
        story.extend(self.create_header_section(game_data))
        story.extend(self.create_analytics_summary(game_data))
        
        # Create two-column layout for middle sections
        story.extend(self.create_period_analysis(game_data))
        story.extend(self.create_player_analytics(game_data))
        
        story.extend(self.create_goalie_analytics(game_data))
        story.extend(self.create_game_insights(game_data))
        story.extend(self.create_compact_visualizations(game_data))
        
        # Build the PDF
        doc.build(story)
        print(f"Analytics report generated successfully: {output_filename}")
    
    def generate_report(self, game_data, output_filename):
        """Legacy method - now calls the analytics report"""
        self.generate_analytics_report(game_data, output_filename)
