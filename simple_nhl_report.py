#!/usr/bin/env python3
"""
Simple NHL Report Generator - Working Version
Generates a real NHL report using actual API data
"""

import requests
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

class SimpleNHLReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_styles()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    def setup_styles(self):
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=15
        )
        
        self.normal_style = ParagraphStyle(
            'Normal',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=6
        )
    
    def get_game_data(self, game_id):
        """Get real game data from NHL API"""
        print(f"Fetching data for game {game_id}...")
        
        # Try to get game data
        url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/feed/live"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API returned {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching game data: {e}")
            return None
    
    def get_team_roster(self, team_code):
        """Get team roster data"""
        url = f"https://api-web.nhle.com/v1/roster/{team_code}/20242025"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def create_score_chart(self, game_data):
        """Create a simple score chart"""
        if not game_data:
            return None
        
        try:
            game_info = game_data['game']
            away_team = game_data['awayTeam']['abbrev']
            home_team = game_data['homeTeam']['abbrev']
            
            # Get period scores
            away_periods = game_info.get('awayTeamScoreByPeriod', [0, 0, 0])
            home_periods = game_info.get('homeTeamScoreByPeriod', [0, 0, 0])
            
            # Create chart
            fig, ax = plt.subplots(figsize=(10, 6))
            periods = ['1st', '2nd', '3rd']
            x = np.arange(len(periods))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, away_periods[:3], width, label=away_team, color='#FF4C00', alpha=0.8)
            bars2 = ax.bar(x + width/2, home_periods[:3], width, label=home_team, color='#C8102E', alpha=0.8)
            
            ax.set_title(f'{away_team} vs {home_team} - Goals by Period', fontsize=16, fontweight='bold')
            ax.set_ylabel('Goals')
            ax.set_xlabel('Period')
            ax.set_xticks(x)
            ax.set_xticklabels(periods)
            ax.legend()
            
            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                               f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            # Save to BytesIO
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        except Exception as e:
            print(f"Chart creation error: {e}")
            return None
    
    def generate_report(self, game_id, output_filename=None):
        """Generate a real NHL report"""
        print("🏒 Generating Real NHL Report 🏒")
        print("=" * 40)
        
        # Get game data
        game_data = self.get_game_data(game_id)
        
        if not game_data:
            print("❌ Could not fetch game data")
            return None
        
        # Create output filename
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            away_team = game_data['awayTeam']['abbrev']
            home_team = game_data['homeTeam']['abbrev']
            output_filename = f"real_nhl_report_{away_team}_vs_{home_team}_{timestamp}.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(output_filename, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("🏒 REAL NHL GAME REPORT 🏒", self.title_style))
        story.append(Spacer(1, 20))
        
        # Game info
        game_info = game_data['game']
        away_team = game_data['awayTeam']
        home_team = game_data['homeTeam']
        
        story.append(Paragraph(f"{away_team['abbrev']} vs {home_team['abbrev']}", self.subtitle_style))
        story.append(Paragraph(f"Final Score: {away_team['abbrev']} {game_info['awayTeamScore']} - {home_team['abbrev']} {game_info['homeTeamScore']}", self.normal_style))
        story.append(Paragraph(f"Date: {game_info['gameDate']}", self.normal_style))
        story.append(Spacer(1, 20))
        
        # Score table
        score_data = [
            ['', '1st', '2nd', '3rd', 'Total'],
            [away_team['abbrev'], 
             game_info['awayTeamScoreByPeriod'][0] if len(game_info['awayTeamScoreByPeriod']) > 0 else 0,
             game_info['awayTeamScoreByPeriod'][1] if len(game_info['awayTeamScoreByPeriod']) > 1 else 0,
             game_info['awayTeamScoreByPeriod'][2] if len(game_info['awayTeamScoreByPeriod']) > 2 else 0,
             game_info['awayTeamScore']],
            [home_team['abbrev'],
             game_info['homeTeamScoreByPeriod'][0] if len(game_info['homeTeamScoreByPeriod']) > 0 else 0,
             game_info['homeTeamScoreByPeriod'][1] if len(game_info['homeTeamScoreByPeriod']) > 1 else 0,
             game_info['homeTeamScoreByPeriod'][2] if len(game_info['homeTeamScoreByPeriod']) > 2 else 0,
             game_info['homeTeamScore']]
        ]
        
        score_table = Table(score_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(score_table)
        story.append(Spacer(1, 20))
        
        # Add chart
        chart_buffer = self.create_score_chart(game_data)
        if chart_buffer:
            img = Image(chart_buffer)
            img.drawHeight = 4*inch
            img.drawWidth = 6*inch
            story.append(img)
            story.append(Spacer(1, 20))
        
        # Game summary
        story.append(Paragraph("Game Summary", self.subtitle_style))
        
        winner = away_team['abbrev'] if game_info['awayTeamScore'] > game_info['homeTeamScore'] else home_team['abbrev']
        loser = home_team['abbrev'] if game_info['awayTeamScore'] > game_info['homeTeamScore'] else away_team['abbrev']
        
        story.append(Paragraph(f"The {winner} defeated the {loser} by a score of {max(game_info['awayTeamScore'], game_info['homeTeamScore'])}-{min(game_info['awayTeamScore'], game_info['homeTeamScore'])}.", self.normal_style))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Real NHL report generated: {output_filename}")
        return output_filename

def main():
    """Generate a real NHL report"""
    print("🏒 REAL NHL REPORT GENERATOR 🏒")
    print("=" * 40)
    
    generator = SimpleNHLReportGenerator()
    
    # Use a known game ID that should have data
    game_id = "2024030416"  # This is a real game ID
    
    print(f"Generating report for game {game_id}...")
    result = generator.generate_report(game_id)
    
    if result:
        print(f"🎉 SUCCESS! Real NHL report created: {result}")
        print("This report contains:")
        print("  • Real game data from NHL API")
        print("  • Actual team scores and periods")
        print("  • Professional PDF layout")
        print("  • Data visualization charts")
    else:
        print("❌ Failed to generate report")

if __name__ == "__main__":
    main()
