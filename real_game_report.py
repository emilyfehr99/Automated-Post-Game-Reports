#!/usr/bin/env python3
"""
Real NHL Game Report Generator
Generates a comprehensive report using actual play-by-play data from a real game
"""

import requests
import pandas as pd
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

class RealGameReportGenerator:
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
        """Get comprehensive game data including play-by-play"""
        print(f"Fetching comprehensive data for game {game_id}...")
        
        # Get game center data
        game_center_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/feed/live"
        play_by_play_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
        boxscore_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"
        
        data = {}
        
        # Fetch game center
        try:
            response = self.session.get(game_center_url, timeout=10)
            if response.status_code == 200:
                data['game_center'] = response.json()
                print("✅ Game center data fetched")
            else:
                print(f"❌ Game center API returned {response.status_code}")
        except Exception as e:
            print(f"❌ Error fetching game center: {e}")
        
        # Fetch play-by-play
        try:
            response = self.session.get(play_by_play_url, timeout=10)
            if response.status_code == 200:
                data['play_by_play'] = response.json()
                print("✅ Play-by-play data fetched")
            else:
                print(f"❌ Play-by-play API returned {response.status_code}")
        except Exception as e:
            print(f"❌ Error fetching play-by-play: {e}")
        
        # Fetch boxscore
        try:
            response = self.session.get(boxscore_url, timeout=10)
            if response.status_code == 200:
                data['boxscore'] = response.json()
                print("✅ Boxscore data fetched")
            else:
                print(f"❌ Boxscore API returned {response.status_code}")
        except Exception as e:
            print(f"❌ Error fetching boxscore: {e}")
        
        return data
    
    def analyze_play_by_play(self, play_by_play_data):
        """Analyze play-by-play data"""
        if not play_by_play_data or 'plays' not in play_by_play_data:
            return None
        
        plays = play_by_play_data['plays']
        print(f"Analyzing {len(plays)} plays...")
        
        # Count different play types
        play_types = {}
        shots = []
        goals = []
        penalties = []
        
        for play in plays:
            play_type = play.get('typeDescKey', 'unknown')
            play_types[play_type] = play_types.get(play_type, 0) + 1
            
            # Collect shots
            if 'shot' in play_type.lower():
                shots.append(play)
            
            # Collect goals
            if play_type == 'goal':
                goals.append(play)
            
            # Collect penalties
            if 'penalty' in play_type.lower():
                penalties.append(play)
        
        return {
            'total_plays': len(plays),
            'play_types': play_types,
            'shots': shots,
            'goals': goals,
            'penalties': penalties
        }
    
    def create_play_analysis_chart(self, analysis_data):
        """Create chart showing play type distribution"""
        if not analysis_data:
            return None
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Play types pie chart
            play_types = analysis_data['play_types']
            if play_types:
                # Get top 8 play types
                sorted_types = sorted(play_types.items(), key=lambda x: x[1], reverse=True)[:8]
                labels, values = zip(*sorted_types)
                
                ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
                ax1.set_title('Play Type Distribution')
            
            # Goals by period
            goals = analysis_data['goals']
            if goals:
                periods = {}
                for goal in goals:
                    period = goal.get('periodNumber', 1)
                    periods[period] = periods.get(period, 0) + 1
                
                periods_list = sorted(periods.keys())
                goals_list = [periods[p] for p in periods_list]
                
                ax2.bar([f'Period {p}' for p in periods_list], goals_list, color='gold', alpha=0.8)
                ax2.set_title('Goals by Period')
                ax2.set_ylabel('Number of Goals')
            
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
        """Generate a comprehensive NHL game report"""
        print("🏒 Generating Real NHL Game Report 🏒")
        print("=" * 50)
        
        # Get comprehensive game data
        game_data = self.get_game_data(game_id)
        
        if not game_data.get('game_center'):
            print("❌ Could not fetch game data")
            return None
        
        # Analyze play-by-play data
        analysis = None
        if game_data.get('play_by_play'):
            analysis = self.analyze_play_by_play(game_data['play_by_play'])
        
        # Create output filename
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"real_nhl_game_report_{game_id}_{timestamp}.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(output_filename, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("🏒 REAL NHL GAME REPORT 🏒", self.title_style))
        story.append(Spacer(1, 20))
        
        # Game info
        game_center = game_data['game_center']
        game_info = game_center.get('game', {})
        away_team = game_center.get('awayTeam', {})
        home_team = game_center.get('homeTeam', {})
        
        story.append(Paragraph(f"{away_team.get('abbrev', 'Away')} vs {home_team.get('abbrev', 'Home')}", self.subtitle_style))
        story.append(Paragraph(f"Game ID: {game_id}", self.normal_style))
        story.append(Paragraph(f"Date: {game_info.get('gameDate', 'Unknown')}", self.normal_style))
        story.append(Spacer(1, 20))
        
        # Score summary
        if game_info:
            story.append(Paragraph("Game Summary", self.subtitle_style))
            
            away_score = game_info.get('awayTeamScore', 0)
            home_score = game_info.get('homeTeamScore', 0)
            
            story.append(Paragraph(f"Final Score: {away_team.get('abbrev', 'Away')} {away_score} - {home_team.get('abbrev', 'Home')} {home_score}", self.normal_style))
            
            # Period scores
            away_periods = game_info.get('awayTeamScoreByPeriod', [])
            home_periods = game_info.get('homeTeamScoreByPeriod', [])
            
            if away_periods and home_periods:
                score_data = [
                    ['', '1st', '2nd', '3rd', 'Total'],
                    [away_team.get('abbrev', 'Away'), 
                     away_periods[0] if len(away_periods) > 0 else 0,
                     away_periods[1] if len(away_periods) > 1 else 0,
                     away_periods[2] if len(away_periods) > 2 else 0,
                     away_score],
                    [home_team.get('abbrev', 'Home'),
                     home_periods[0] if len(home_periods) > 0 else 0,
                     home_periods[1] if len(home_periods) > 1 else 0,
                     home_periods[2] if len(home_periods) > 2 else 0,
                     home_score]
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
        
        # Play-by-play analysis
        if analysis:
            story.append(Paragraph("Play-by-Play Analysis", self.subtitle_style))
            
            story.append(Paragraph(f"Total Plays: {analysis['total_plays']}", self.normal_style))
            story.append(Paragraph(f"Goals: {len(analysis['goals'])}", self.normal_style))
            story.append(Paragraph(f"Shots: {len(analysis['shots'])}", self.normal_style))
            story.append(Paragraph(f"Penalties: {len(analysis['penalties'])}", self.normal_style))
            story.append(Spacer(1, 10))
            
            # Add analysis chart
            chart_buffer = self.create_play_analysis_chart(analysis)
            if chart_buffer:
                img = Image(chart_buffer)
                img.drawHeight = 4*inch
                img.drawWidth = 7*inch
                story.append(img)
                story.append(Spacer(1, 20))
            
            # Top play types
            story.append(Paragraph("Most Common Play Types", self.subtitle_style))
            play_types = analysis['play_types']
            sorted_types = sorted(play_types.items(), key=lambda x: x[1], reverse=True)[:10]
            
            play_data = [['Play Type', 'Count']]
            for play_type, count in sorted_types:
                play_data.append([play_type, count])
            
            play_table = Table(play_data, colWidths=[4*inch, 1.5*inch])
            play_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left align play types
            ]))
            
            story.append(play_table)
            story.append(Spacer(1, 20))
        
        # Data source information
        story.append(Paragraph("Data Source Information", self.subtitle_style))
        story.append(Paragraph("This report uses real data from the official NHL API:", self.normal_style))
        story.append(Paragraph("• Game Center: https://api-web.nhle.com/v1/gamecenter/{game_id}/feed/live", self.normal_style))
        story.append(Paragraph("• Play-by-Play: https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play", self.normal_style))
        story.append(Paragraph("• Boxscore: https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore", self.normal_style))
        story.append(Paragraph("• All data is legitimate and from official NHL sources", self.normal_style))
        story.append(Paragraph("• Report generated using enhanced NHL analytics system", self.normal_style))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Real NHL game report generated: {output_filename}")
        return output_filename

def main():
    """Generate a real NHL game report"""
    print("🏒 REAL NHL GAME REPORT GENERATOR 🏒")
    print("=" * 50)
    
    generator = RealGameReportGenerator()
    
    # Use the game ID from your example
    game_id = "2024030242"
    
    print(f"Generating comprehensive report for game {game_id}...")
    result = generator.generate_report(game_id)
    
    if result:
        print(f"🎉 SUCCESS! Real NHL game report created: {result}")
        print("\nThis report contains:")
        print("  • Real game data from NHL API")
        print("  • Complete play-by-play analysis")
        print("  • Actual game scores and periods")
        print("  • Play type distribution analysis")
        print("  • Professional PDF layout")
        print("  • Data visualization charts")
        print("  • All data is legitimate and from official NHL sources")
    else:
        print("❌ Failed to generate report")

if __name__ == "__main__":
    main()
