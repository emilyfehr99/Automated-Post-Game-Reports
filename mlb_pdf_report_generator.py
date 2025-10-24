#!/usr/bin/env python3
"""
MLB Scouting Report PDF Generator
Creates professional PDF scouting reports for MLB players
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
import json
from datetime import datetime

class MLBScoutingReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
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
    
    def generate_report(self, scouting_data, output_filename):
        """Generate the complete scouting report PDF"""
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Title page
        story.extend(self._create_title_page(scouting_data))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(scouting_data))
        story.append(PageBreak())
        
        # Hitting analysis
        story.extend(self._create_hitting_analysis(scouting_data))
        story.append(PageBreak())
        
        # Pitching analysis
        story.extend(self._create_pitching_analysis(scouting_data))
        story.append(PageBreak())
        
        # Game plan
        story.extend(self._create_game_plan(scouting_data))
        story.append(PageBreak())
        
        # Statistical analysis
        story.extend(self._create_statistical_analysis(scouting_data))
        
        # Build PDF
        doc.build(story)
        print(f"✅ MLB Scouting Report generated: {output_filename}")
    
    def _create_title_page(self, data):
        """Create the title page"""
        story = []
        
        # Main title
        story.append(Paragraph("MLB SCOUTING REPORT", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Player name
        story.append(Paragraph(f"<b>{data.get('player', 'Player Name')}</b>", 
                              self.styles['Title']))
        story.append(Spacer(1, 10))
        
        # Team and position
        story.append(Paragraph(f"<b>Team:</b> {data.get('team', 'N/A')}", 
                              self.styles['Normal']))
        story.append(Paragraph(f"<b>Position:</b> {data.get('position', 'N/A')}", 
                              self.styles['Normal']))
        story.append(Paragraph(f"<b>Season:</b> {data.get('season', 'N/A')}", 
                              self.styles['Normal']))
        story.append(Paragraph(f"<b>Report Date:</b> {data.get('report_date', 'N/A')}", 
                              self.styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # Report description
        story.append(Paragraph(
            "This comprehensive scouting report provides detailed analysis of the player's "
            "hitting and pitching tendencies, statistical performance, and strategic recommendations "
            "for game planning against this opponent.",
            self.styles['Normal']
        ))
        
        return story
    
    def _create_executive_summary(self, data):
        """Create executive summary section"""
        story = []
        
        story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        # Key insights
        insights = data.get('insights', {})
        
        story.append(Paragraph("<b>Key Hitting Insights:</b>", self.styles['Subsection']))
        for insight in insights.get('hitting_insights', []):
            story.append(Paragraph(f"• {insight}", self.styles['Normal']))
        
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("<b>Key Pitching Insights:</b>", self.styles['Subsection']))
        for insight in insights.get('pitching_insights', []):
            story.append(Paragraph(f"• {insight}", self.styles['Normal']))
        
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("<b>Defensive Considerations:</b>", self.styles['Subsection']))
        for insight in insights.get('defensive_insights', []):
            story.append(Paragraph(f"• {insight}", self.styles['Normal']))
        
        return story
    
    def _create_hitting_analysis(self, data):
        """Create hitting analysis section"""
        story = []
        
        story.append(Paragraph("HITTING ANALYSIS", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        hitting_analysis = data.get('hitting_analysis', {})
        
        # Pitch type preferences
        if 'favorite_pitch_types' in hitting_analysis:
            story.append(Paragraph("<b>Pitch Type Preferences:</b>", self.styles['Subsection']))
            pitch_data = hitting_analysis['favorite_pitch_types']
            table_data = [['Pitch Type', 'Frequency']]
            for pitch, freq in pitch_data.items():
                table_data.append([pitch, str(freq)])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 12))
        
        # Zone analysis
        if 'hot_zones' in hitting_analysis:
            story.append(Paragraph("<b>Hot Zones:</b>", self.styles['Subsection']))
            zone_data = hitting_analysis['hot_zones']
            for zone, freq in zone_data.items():
                story.append(Paragraph(f"• Zone {zone}: {freq}%", self.styles['Normal']))
        
        return story
    
    def _create_pitching_analysis(self, data):
        """Create pitching analysis section"""
        story = []
        
        story.append(Paragraph("PITCHING ANALYSIS", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        pitching_analysis = data.get('pitching_analysis', {})
        
        # Pitch arsenal
        if 'pitch_arsenal' in pitching_analysis:
            story.append(Paragraph("<b>Pitch Arsenal:</b>", self.styles['Subsection']))
            arsenal_data = pitching_analysis['pitch_arsenal']
            table_data = [['Pitch Type', 'Usage %']]
            for pitch, usage in arsenal_data.items():
                table_data.append([pitch, f"{usage:.1f}%"])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 12))
        
        # Velocity analysis
        if 'avg_velocity' in pitching_analysis:
            story.append(Paragraph("<b>Velocity Analysis:</b>", self.styles['Subsection']))
            story.append(Paragraph(f"• Average Velocity: {pitching_analysis['avg_velocity']:.1f} mph", 
                                  self.styles['Normal']))
            if 'max_velocity' in pitching_analysis:
                story.append(Paragraph(f"• Max Velocity: {pitching_analysis['max_velocity']:.1f} mph", 
                                      self.styles['Normal']))
        
        return story
    
    def _create_game_plan(self, data):
        """Create game plan section"""
        story = []
        
        story.append(Paragraph("GAME PLAN RECOMMENDATIONS", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        game_plan = data.get('insights', {}).get('game_plan', [])
        
        story.append(Paragraph("<b>Strategic Recommendations:</b>", self.styles['Subsection']))
        for i, recommendation in enumerate(game_plan, 1):
            story.append(Paragraph(f"{i}. {recommendation}", self.styles['Normal']))
        
        return story
    
    def _create_statistical_analysis(self, data):
        """Create statistical analysis section"""
        story = []
        
        story.append(Paragraph("STATISTICAL ANALYSIS", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        # Advanced metrics
        advanced_metrics = data.get('raw_data', {}).get('advanced_metrics', {})
        if advanced_metrics:
            story.append(Paragraph("<b>Advanced Metrics:</b>", self.styles['Subsection']))
            
            metrics_data = []
            for metric, value in advanced_metrics.items():
                if isinstance(value, (int, float)):
                    metrics_data.append([metric.replace('_', ' ').title(), f"{value:.3f}"])
            
            if metrics_data:
                table = Table(metrics_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)
        
        return story
