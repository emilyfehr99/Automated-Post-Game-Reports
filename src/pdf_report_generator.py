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
        """Setup custom paragraph styles for the report"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.darkred,
            alignment=TA_LEFT,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceAfter=6,
            fontName='Helvetica'
        )
        
        # Stat text style
        self.stat_style = ParagraphStyle(
            'CustomStat',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.darkgreen,
            alignment=TA_LEFT,
            spaceAfter=4,
            fontName='Helvetica-Bold'
        )
    
    def create_score_summary(self, game_data):
        """Create the score summary section"""
        story = []
        
        # Game header
        game_info = game_data['game_center']['game']
        away_team = game_data['game_center']['awayTeam']
        home_team = game_data['game_center']['homeTeam']
        
        story.append(Paragraph(f"FINAL SCORE", self.title_style))
        story.append(Spacer(1, 20))
        
        # Score display
        score_data = [
            ['', '1st', '2nd', '3rd', 'OT', 'Total'],
            [away_team['abbrev'], 
             game_info['awayTeamScoreByPeriod'][0] if len(game_info['awayTeamScoreByPeriod']) > 0 else 0,
             game_info['awayTeamScoreByPeriod'][1] if len(game_info['awayTeamScoreByPeriod']) > 1 else 0,
             game_info['awayTeamScoreByPeriod'][2] if len(game_info['awayTeamScoreByPeriod']) > 2 else 0,
             game_info['awayTeamScoreByPeriod'][3] if len(game_info['awayTeamScoreByPeriod']) > 3 else 0,
             game_info['awayTeamScore']],
            [home_team['abbrev'],
             game_info['homeTeamScoreByPeriod'][0] if len(game_info['homeTeamScoreByPeriod']) > 0 else 0,
             game_info['homeTeamScoreByPeriod'][1] if len(game_info['homeTeamScoreByPeriod']) > 1 else 0,
             game_info['homeTeamScoreByPeriod'][2] if len(game_info['homeTeamScoreByPeriod']) > 2 else 0,
             game_info['homeTeamScoreByPeriod'][3] if len(game_info['homeTeamScoreByPeriod']) > 3 else 0,
             game_info['homeTeamScore']]
        ]
        
        score_table = Table(score_data, colWidths=[1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        story.append(score_table)
        story.append(Spacer(1, 20))
        
        # Game details
        game_date = game_data['game_center']['game']['gameDate']
        venue = game_data['game_center'].get('venue', {}).get('default', 'Unknown Arena')
        
        story.append(Paragraph(f"<b>Date:</b> {game_date}", self.normal_style))
        story.append(Paragraph(f"<b>Venue:</b> {venue}", self.normal_style))
        story.append(Paragraph(f"<b>Game Type:</b> Stanley Cup Finals", self.normal_style))
        
        return story
    
    def create_team_stats_comparison(self, game_data):
        """Create team statistics comparison section"""
        story = []
        
        story.append(Paragraph("TEAM STATISTICS COMPARISON", self.subtitle_style))
        story.append(Spacer(1, 15))
        
        # Get team stats from boxscore
        boxscore = game_data['boxscore']
        away_stats = boxscore['awayTeam']
        home_stats = boxscore['homeTeam']
        
        # Create stats comparison table
        stats_data = [
            ['Statistic', away_stats['abbrev'], home_stats['abbrev']],
            ['Goals', away_stats['score'], home_stats['score']],
            ['Shots', away_stats.get('sog', 'N/A'), home_stats.get('sog', 'N/A')],
            ['Power Play', f"{away_stats.get('powerPlayConversion', 'N/A')}", f"{home_stats.get('powerPlayConversion', 'N/A')}"],
            ['Penalty Minutes', away_stats.get('penaltyMinutes', 'N/A'), home_stats.get('penaltyMinutes', 'N/A')],
            ['Hits', away_stats.get('hits', 'N/A'), home_stats.get('hits', 'N/A')],
            ['Faceoff Wins', away_stats.get('faceoffWins', 'N/A'), home_stats.get('faceoffWins', 'N/A')],
            ['Blocked Shots', away_stats.get('blockedShots', 'N/A'), home_stats.get('blockedShots', 'N/A')],
            ['Giveaways', away_stats.get('giveaways', 'N/A'), home_stats.get('giveaways', 'N/A')],
            ['Takeaways', away_stats.get('takeaways', 'N/A'), home_stats.get('takeaways', 'N/A')]
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def create_scoring_summary(self, game_data):
        """Create scoring summary section"""
        story = []
        
        story.append(Paragraph("SCORING SUMMARY", self.subtitle_style))
        story.append(Spacer(1, 15))
        
        # Get scoring plays
        plays = game_data['game_center'].get('plays', [])
        scoring_plays = [play for play in plays if play.get('typeDescKey') == 'goal']
        
        if scoring_plays:
            # Create scoring summary table
            scoring_data = [['Period', 'Time', 'Team', 'Scorer', 'Assists', 'Score']]
            
            for play in scoring_plays:
                period = play.get('periodNumber', 'N/A')
                time = play.get('timeInPeriod', 'N/A')
                team = play.get('team', {}).get('abbrev', 'N/A')
                scorer = play.get('scorer', {}).get('name', 'N/A')
                
                # Get assists
                assists = []
                for player in play.get('players', []):
                    if player.get('playerType') == 'assist':
                        assists.append(player.get('name', 'N/A'))
                
                assists_str = ', '.join(assists) if assists else 'Unassisted'
                
                # Get score at time of goal
                score = play.get('score', 'N/A')
                
                scoring_data.append([period, time, team, scorer, assists_str, score])
            
            scoring_table = Table(scoring_data, colWidths=[0.8*inch, 1*inch, 1.2*inch, 2*inch, 2.5*inch, 1*inch])
            scoring_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (3, 1), (4, -1), 'LEFT'),  # Left align scorer and assists columns
            ]))
            
            story.append(scoring_table)
        else:
            story.append(Paragraph("No scoring information available", self.normal_style))
        
        story.append(Spacer(1, 20))
        return story
    
    def create_player_performance(self, game_data):
        """Create player performance highlights section"""
        story = []
        
        story.append(Paragraph("PLAYER PERFORMANCE HIGHLIGHTS", self.subtitle_style))
        story.append(Spacer(1, 15))
        
        # Get player stats from boxscore
        boxscore = game_data['boxscore']
        away_players = boxscore.get('awayTeam', {}).get('players', [])
        home_players = boxscore.get('homeTeam', {}).get('players', [])
        
        all_players = away_players + home_players
        
        # Find top performers
        goal_scorers = []
        assist_leaders = []
        
        for player in all_players:
            stats = player.get('stats', {})
            goals = stats.get('goals', 0)
            assists = stats.get('assists', 0)
            
            if goals > 0:
                goal_scorers.append({
                    'name': player.get('name', 'Unknown'),
                    'team': player.get('team', {}).get('abbrev', 'Unknown'),
                    'goals': goals
                })
            
            if assists > 0:
                assist_leaders.append({
                    'name': player.get('name', 'Unknown'),
                    'team': player.get('team', {}).get('abbrev', 'Unknown'),
                    'assists': assists
                })
        
        # Sort by goals and assists
        goal_scorers.sort(key=lambda x: x['goals'], reverse=True)
        assist_leaders.sort(key=lambda x: x['assists'], reverse=True)
        
        # Top goal scorers
        story.append(Paragraph("Top Goal Scorers", self.section_style))
        if goal_scorers:
            goal_data = [['Player', 'Team', 'Goals']]
            for player in goal_scorers[:5]:  # Top 5
                goal_data.append([player['name'], player['team'], player['goals']])
            
            goal_table = Table(goal_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
            goal_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(goal_table)
        else:
            story.append(Paragraph("No goal scoring data available", self.normal_style))
        
        story.append(Spacer(1, 15))
        
        # Top assist leaders
        story.append(Paragraph("Top Assist Leaders", self.section_style))
        if assist_leaders:
            assist_data = [['Player', 'Team', 'Assists']]
            for player in assist_leaders[:5]:  # Top 5
                assist_data.append([player['name'], player['team'], player['assists']])
            
            assist_table = Table(assist_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
            assist_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(assist_table)
        else:
            story.append(Paragraph("No assist data available", self.normal_style))
        
        story.append(Spacer(1, 20))
        return story
    
    def create_goalie_performance(self, game_data):
        """Create goalie performance section"""
        story = []
        
        story.append(Paragraph("GOALIE PERFORMANCE", self.subtitle_style))
        story.append(Spacer(1, 15))
        
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
        
        # Create goalie comparison table
        goalie_data = [['Team', 'Goalie', 'Shots Against', 'Saves', 'Save %', 'Goals Against', 'Time on Ice']]
        
        for goalie in away_goalies:
            stats = goalie.get('stats', {})
            shots_against = stats.get('shotsAgainst', 0)
            saves = stats.get('saves', 0)
            goals_against = stats.get('goalsAgainst', 0)
            save_pct = f"{(saves/shots_against*100):.1f}%" if shots_against > 0 else "N/A"
            time_on_ice = stats.get('timeOnIce', 'N/A')
            
            goalie_data.append([
                boxscore['awayTeam']['abbrev'],
                goalie.get('name', 'Unknown'),
                shots_against,
                saves,
                save_pct,
                goals_against,
                time_on_ice
            ])
        
        for goalie in home_goalies:
            stats = goalie.get('stats', {})
            shots_against = stats.get('shotsAgainst', 0)
            saves = stats.get('saves', 0)
            goals_against = stats.get('goalsAgainst', 0)
            save_pct = f"{(saves/shots_against*100):.1f}%" if shots_against > 0 else "N/A"
            time_on_ice = stats.get('timeOnIce', 'N/A')
            
            goalie_data.append([
                boxscore['homeTeam']['abbrev'],
                goalie.get('name', 'Unknown'),
                shots_against,
                saves,
                save_pct,
                goals_against,
                time_on_ice
            ])
        
        if len(goalie_data) > 1:  # If we have goalie data
            goalie_table = Table(goalie_data, colWidths=[1.2*inch, 2*inch, 1*inch, 0.8*inch, 1*inch, 1*inch, 1.2*inch])
            goalie_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            story.append(goalie_table)
        else:
            story.append(Paragraph("No goalie performance data available", self.normal_style))
        
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
        
        # Game summary
        story.append(Paragraph(f"<b>Game Summary:</b>", self.section_style))
        story.append(Paragraph(f"The {winner} defeated the {loser} by a score of {max(away_score, home_score)}-{min(away_score, home_score)}.", self.normal_style))
        
        if margin == 1:
            story.append(Paragraph("This was a close, competitive game that could have gone either way.", self.normal_style))
        elif margin <= 3:
            story.append(Paragraph("The game was competitive with a moderate margin of victory.", self.normal_style))
        else:
            story.append(Paragraph("This was a decisive victory with a significant margin.", self.normal_style))
        
        story.append(Spacer(1, 10))
        
        # Key moments analysis
        story.append(Paragraph(f"<b>Key Moments:</b>", self.section_style))
        
        # Analyze scoring by period
        away_periods = game_info.get('awayTeamScoreByPeriod', [])
        home_periods = game_info.get('homeTeamScoreByPeriod', [])
        
        if len(away_periods) >= 3:
            story.append(Paragraph(f"• First Period: {away_team['abbrev']} {away_periods[0]} - {home_team['abbrev']} {home_periods[0]}", self.normal_style))
            story.append(Paragraph(f"• Second Period: {away_team['abbrev']} {away_periods[1]} - {home_team['abbrev']} {home_periods[1]}", self.normal_style))
            story.append(Paragraph(f"• Third Period: {away_team['abbrev']} {away_periods[2]} - {home_team['abbrev']} {home_periods[2]}", self.normal_style))
            
            if len(away_periods) > 3:
                story.append(Paragraph(f"• Overtime: {away_team['abbrev']} {away_periods[3]} - {home_team['abbrev']} {home_periods[3]}", self.normal_style))
        
        story.append(Spacer(1, 10))
        
        # Special teams analysis
        story.append(Paragraph(f"<b>Special Teams:</b>", self.section_style))
        
        # Get power play and penalty kill info from boxscore
        boxscore = game_data['boxscore']
        away_pp = boxscore.get('awayTeam', {}).get('powerPlayConversion', 'N/A')
        home_pp = boxscore.get('homeTeam', {}).get('powerPlayConversion', 'N/A')
        
        story.append(Paragraph(f"• {away_team['abbrev']} Power Play: {away_pp}", self.normal_style))
        story.append(Paragraph(f"• {home_team['abbrev']} Power Play: {home_pp}", self.normal_style))
        
        story.append(Spacer(1, 20))
        return story
    
    def create_visualizations(self, game_data):
        """Create charts and visualizations"""
        story = []
        
        story.append(Paragraph("GAME VISUALIZATIONS", self.subtitle_style))
        story.append(Spacer(1, 15))
        
        # Create shot comparison chart
        try:
            boxscore = game_data['boxscore']
            away_team = boxscore['awayTeam']['abbrev']
            home_team = boxscore['homeTeam']['abbrev']
            
            # Get shots on goal
            away_shots = boxscore['awayTeam'].get('sog', 0)
            home_shots = boxscore['homeTeam'].get('sog', 0)
            
            # Create matplotlib chart
            fig, ax = plt.subplots(figsize=(8, 6))
            teams = [away_team, home_team]
            shots = [away_shots, home_shots]
            colors_chart = ['#C8102E', '#FF6B35']  # Red and Orange
            
            bars = ax.bar(teams, shots, color=colors_chart, alpha=0.8)
            ax.set_title('Shots on Goal Comparison', fontsize=16, fontweight='bold')
            ax.set_ylabel('Shots on Goal', fontsize=12)
            ax.set_xlabel('Team', fontsize=12)
            
            # Add value labels on bars
            for bar, shot in zip(bars, shots):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{shot}', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            # Save to BytesIO and convert to ReportLab Image
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            
            # Create ReportLab Image
            img = Image(img_buffer)
            img.drawHeight = 4*inch
            img.drawWidth = 6*inch
            
            story.append(img)
            story.append(Spacer(1, 15))
            
            plt.close()
            
        except Exception as e:
            story.append(Paragraph(f"Chart generation error: {str(e)}", self.normal_style))
        
        # Create scoring by period chart
        try:
            game_info = game_data['game_center']['game']
            away_periods = game_info.get('awayTeamScoreByPeriod', [0, 0, 0])
            home_periods = game_info.get('homeTeamScoreByPeriod', [0, 0, 0])
            
            # Ensure we have at least 3 periods
            while len(away_periods) < 3:
                away_periods.append(0)
            while len(home_periods) < 3:
                home_periods.append(0)
            
            periods = ['1st', '2nd', '3rd']
            if len(away_periods) > 3:
                periods.append('OT')
            
            fig, ax = plt.subplots(figsize=(8, 6))
            x = np.arange(len(periods))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, away_periods[:len(periods)], width, 
                          label=away_team, color='#C8102E', alpha=0.8)
            bars2 = ax.bar(x + width/2, home_periods[:len(periods)], width, 
                          label=home_team, color='#FF6B35', alpha=0.8)
            
            ax.set_title('Scoring by Period', fontsize=16, fontweight='bold')
            ax.set_ylabel('Goals', fontsize=12)
            ax.set_xlabel('Period', fontsize=12)
            ax.set_xticks(x)
            ax.set_xticklabels(periods)
            ax.legend()
            
            # Add value labels on bars
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                               f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            # Save to BytesIO and convert to ReportLab Image
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            
            # Create ReportLab Image
            img = Image(img_buffer)
            img.drawHeight = 4*inch
            img.drawWidth = 6*inch
            
            story.append(img)
            
            plt.close()
            
        except Exception as e:
            story.append(Paragraph(f"Period scoring chart error: {str(e)}", self.normal_style))
        
        story.append(Spacer(1, 20))
        return story
    
    def generate_report(self, game_data, output_filename):
        """Generate the complete post-game report PDF"""
        doc = SimpleDocTemplate(output_filename, pagesize=letter, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Add title page
        story.append(Paragraph("NHL POST-GAME REPORT", self.title_style))
        story.append(Paragraph("Stanley Cup Finals", self.subtitle_style))
        story.append(Spacer(1, 30))
        
        # Add game info
        game_info = game_data['game_center']['game']
        away_team = game_data['game_center']['awayTeam']
        home_team = game_data['game_center']['homeTeam']
        
        story.append(Paragraph(f"{away_team['abbrev']} vs {home_team['abbrev']}", self.subtitle_style))
        story.append(Paragraph(f"Game Date: {game_info['gameDate']}", self.normal_style))
        story.append(Spacer(1, 20))
        
        # Add all sections
        story.extend(self.create_score_summary(game_data))
        story.extend(self.create_team_stats_comparison(game_data))
        story.extend(self.create_scoring_summary(game_data))
        story.extend(self.create_player_performance(game_data))
        story.extend(self.create_goalie_performance(game_data))
        story.extend(self.create_game_analysis(game_data))
        story.extend(self.create_visualizations(game_data))
        
        # Build the PDF
        doc.build(story)
        print(f"Post-game report generated successfully: {output_filename}")
