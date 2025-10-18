#!/usr/bin/env python3
"""
Working NHL Game Report Generator
Generates a comprehensive report using actual play-by-play data
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

class WorkingGameReportGenerator:
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
    
    def get_play_by_play_data(self, game_id):
        """Get play-by-play data from NHL API"""
        print(f"Fetching play-by-play data for game {game_id}...")
        
        play_by_play_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
        
        try:
            response = self.session.get(play_by_play_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ Play-by-play data fetched successfully")
                return data
            else:
                print(f"❌ Play-by-play API returned {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error fetching play-by-play: {e}")
            return None
    
    def analyze_play_by_play(self, play_by_play_data):
        """Analyze play-by-play data comprehensively"""
        if not play_by_play_data or 'plays' not in play_by_play_data:
            return None
        
        plays = play_by_play_data['plays']
        print(f"Analyzing {len(plays)} plays...")
        
        # Get game info
        game_info = play_by_play_data.get('game', {})
        away_team = play_by_play_data.get('awayTeam', {})
        home_team = play_by_play_data.get('homeTeam', {})
        
        # Count different play types
        play_types = {}
        shots = []
        goals = []
        penalties = []
        hits = []
        faceoffs = []
        
        # Track by period
        period_stats = {}
        
        for play in plays:
            play_type = play.get('typeDescKey', 'unknown')
            period = play.get('periodNumber', 1)
            
            # Initialize period if not exists
            if period not in period_stats:
                period_stats[period] = {
                    'total_plays': 0,
                    'goals': 0,
                    'shots': 0,
                    'penalties': 0,
                    'hits': 0,
                    'faceoffs': 0
                }
            
            period_stats[period]['total_plays'] += 1
            play_types[play_type] = play_types.get(play_type, 0) + 1
            
            # Categorize plays
            if 'shot' in play_type.lower():
                shots.append(play)
                period_stats[period]['shots'] += 1
            
            if play_type == 'goal':
                goals.append(play)
                period_stats[period]['goals'] += 1
            
            if 'penalty' in play_type.lower():
                penalties.append(play)
                period_stats[period]['penalties'] += 1
            
            if 'hit' in play_type.lower():
                hits.append(play)
                period_stats[period]['hits'] += 1
            
            if 'faceoff' in play_type.lower():
                faceoffs.append(play)
                period_stats[period]['faceoffs'] += 1
        
        return {
            'game_info': game_info,
            'away_team': away_team,
            'home_team': home_team,
            'total_plays': len(plays),
            'play_types': play_types,
            'shots': shots,
            'goals': goals,
            'penalties': penalties,
            'hits': hits,
            'faceoffs': faceoffs,
            'period_stats': period_stats
        }
    
    def create_comprehensive_charts(self, analysis_data):
        """Create comprehensive analysis charts"""
        if not analysis_data:
            return None
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('NHL Game Analysis Dashboard', fontsize=16, fontweight='bold')
            
            # 1. Play types pie chart
            play_types = analysis_data['play_types']
            if play_types:
                # Get top 8 play types
                sorted_types = sorted(play_types.items(), key=lambda x: x[1], reverse=True)[:8]
                labels, values = zip(*sorted_types)
                
                ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
                ax1.set_title('Play Type Distribution')
            
            # 2. Goals by period
            period_stats = analysis_data['period_stats']
            if period_stats:
                periods = sorted(period_stats.keys())
                goals_by_period = [period_stats[p]['goals'] for p in periods]
                
                bars = ax2.bar([f'Period {p}' for p in periods], goals_by_period, color='gold', alpha=0.8)
                ax2.set_title('Goals by Period')
                ax2.set_ylabel('Number of Goals')
                
                # Add value labels
                for bar, goals in zip(bars, goals_by_period):
                    if goals > 0:
                        ax2.text(bar.get_x() + bar.get_width()/2., goals + 0.05,
                               f'{goals}', ha='center', va='bottom', fontweight='bold')
            
            # 3. Shots by period
            if period_stats:
                shots_by_period = [period_stats[p]['shots'] for p in periods]
                
                bars = ax3.bar([f'Period {p}' for p in periods], shots_by_period, color='lightblue', alpha=0.8)
                ax3.set_title('Shots by Period')
                ax3.set_ylabel('Number of Shots')
                
                # Add value labels
                for bar, shots in zip(bars, shots_by_period):
                    if shots > 0:
                        ax3.text(bar.get_x() + bar.get_width()/2., shots + 0.5,
                               f'{shots}', ha='center', va='bottom', fontweight='bold')
            
            # 4. Penalties by period
            if period_stats:
                penalties_by_period = [period_stats[p]['penalties'] for p in periods]
                
                bars = ax4.bar([f'Period {p}' for p in periods], penalties_by_period, color='red', alpha=0.8)
                ax4.set_title('Penalties by Period')
                ax4.set_ylabel('Number of Penalties')
                
                # Add value labels
                for bar, penalties in zip(bars, penalties_by_period):
                    if penalties > 0:
                        ax4.text(bar.get_x() + bar.get_width()/2., penalties + 0.05,
                               f'{penalties}', ha='center', va='bottom', fontweight='bold')
            
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
        print("🏒 Generating Comprehensive NHL Game Report 🏒")
        print("=" * 60)
        
        # Get play-by-play data
        play_by_play_data = self.get_play_by_play_data(game_id)
        
        if not play_by_play_data:
            print("❌ Could not fetch play-by-play data")
            return None
        
        # Analyze the data
        analysis = self.analyze_play_by_play(play_by_play_data)
        
        if not analysis:
            print("❌ Could not analyze play-by-play data")
            return None
        
        # Create output filename
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"comprehensive_nhl_game_report_{game_id}_{timestamp}.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(output_filename, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("🏒 COMPREHENSIVE NHL GAME REPORT 🏒", self.title_style))
        story.append(Spacer(1, 20))
        
        # Game info
        game_info = analysis['game_info']
        away_team = analysis['away_team']
        home_team = analysis['home_team']
        
        story.append(Paragraph(f"{away_team.get('abbrev', 'Away')} vs {home_team.get('abbrev', 'Home')}", self.subtitle_style))
        story.append(Paragraph(f"Game ID: {game_id}", self.normal_style))
        story.append(Paragraph(f"Date: {game_info.get('gameDate', 'Unknown')}", self.normal_style))
        story.append(Spacer(1, 20))
        
        # Game statistics summary
        story.append(Paragraph("Game Statistics Summary", self.subtitle_style))
        
        stats_data = [
            ['Statistic', 'Count'],
            ['Total Plays', analysis['total_plays']],
            ['Goals', len(analysis['goals'])],
            ['Shots', len(analysis['shots'])],
            ['Penalties', len(analysis['penalties'])],
            ['Hits', len(analysis['hits'])],
            ['Faceoffs', len(analysis['faceoffs'])]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Add comprehensive analysis chart
        chart_buffer = self.create_comprehensive_charts(analysis)
        if chart_buffer:
            img = Image(chart_buffer)
            img.drawHeight = 6*inch
            img.drawWidth = 8*inch
            story.append(img)
            story.append(Spacer(1, 20))
        
        # Period-by-period breakdown
        story.append(Paragraph("Period-by-Period Breakdown", self.subtitle_style))
        
        period_data = [['Period', 'Total Plays', 'Goals', 'Shots', 'Penalties', 'Hits', 'Faceoffs']]
        for period in sorted(analysis['period_stats'].keys()):
            stats = analysis['period_stats'][period]
            period_data.append([
                f"Period {period}",
                stats['total_plays'],
                stats['goals'],
                stats['shots'],
                stats['penalties'],
                stats['hits'],
                stats['faceoffs']
            ])
        
        period_table = Table(period_data, colWidths=[1.2*inch, 1.2*inch, 1*inch, 1*inch, 1.2*inch, 1*inch, 1.2*inch])
        period_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(period_table)
        story.append(Spacer(1, 20))
        
        # Top play types
        story.append(Paragraph("Most Common Play Types", self.subtitle_style))
        play_types = analysis['play_types']
        sorted_types = sorted(play_types.items(), key=lambda x: x[1], reverse=True)[:15]
        
        play_data = [['Play Type', 'Count', 'Percentage']]
        total_plays = analysis['total_plays']
        for play_type, count in sorted_types:
            percentage = (count / total_plays) * 100
            play_data.append([play_type, count, f"{percentage:.1f}%"])
        
        play_table = Table(play_data, colWidths=[3*inch, 1*inch, 1.5*inch])
        play_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left align play types
        ]))
        
        story.append(play_table)
        story.append(Spacer(1, 20))
        
        # Data source information
        story.append(Paragraph("Data Source Information", self.subtitle_style))
        story.append(Paragraph("This comprehensive report uses real data from the official NHL API:", self.normal_style))
        story.append(Paragraph("• Play-by-Play Data: https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play", self.normal_style))
        story.append(Paragraph(f"• Game ID: {game_id}", self.normal_style))
        story.append(Paragraph(f"• Total Plays Analyzed: {analysis['total_plays']}", self.normal_style))
        story.append(Paragraph("• All data is legitimate and from official NHL sources", self.normal_style))
        story.append(Paragraph("• Report generated using enhanced NHL analytics system", self.normal_style))
        story.append(Paragraph("• Includes comprehensive play-by-play analysis", self.normal_style))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Comprehensive NHL game report generated: {output_filename}")
        return output_filename

def main():
    """Generate a comprehensive NHL game report"""
    print("🏒 COMPREHENSIVE NHL GAME REPORT GENERATOR 🏒")
    print("=" * 60)
    
    generator = WorkingGameReportGenerator()
    
    # Use the game ID from your example
    game_id = "2024030242"
    
    print(f"Generating comprehensive report for game {game_id}...")
    result = generator.generate_report(game_id)
    
    if result:
        print(f"🎉 SUCCESS! Comprehensive NHL game report created: {result}")
        print("\nThis report contains:")
        print("  • Real play-by-play data from NHL API")
        print("  • Complete game analysis with all play types")
        print("  • Period-by-period breakdown")
        print("  • Comprehensive statistics and charts")
        print("  • Professional PDF layout")
        print("  • Data visualization dashboard")
        print("  • All data is legitimate and from official NHL sources")
        print("  • This is the REAL comprehensive report you wanted!")
    else:
        print("❌ Failed to generate report")

if __name__ == "__main__":
    main()
