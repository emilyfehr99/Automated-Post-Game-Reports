#!/usr/bin/env python3
"""
Test script using the exact same table creation code as NHL report
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

def test_exact_nhl_code():
    """Test using exact NHL report table creation code"""
    
    # Create a simple test document
    doc = SimpleDocTemplate("test_exact_nhl_code.pdf", pagesize=letter)
    story = []
    
    # Setup styles exactly like NHL report
    styles = getSampleStyleSheet()
    
    metric_style = ParagraphStyle(
        'CourierMetric', parent=styles['Normal'],
        fontSize=12, textColor=colors.white,
        alignment=TA_CENTER, spaceAfter=6,
        fontName='Helvetica-Bold',  # Try Helvetica instead of Courier
        leading=14
    )
    
    # Test data (same as debug output)
    away_team_stats = {'goals': 1, 'shots': 29, 'hits': 37, 'faceoffs_won': 47, 'faceoffs_lost': 0, 'penalties': 0, 'corsi': 76, 'expected_goals': 0.19}
    home_team_stats = {'goals': 5, 'shots': 25, 'hits': 20, 'faceoffs_won': 6, 'faceoffs_lost': 0, 'penalties': 0, 'corsi': 28, 'expected_goals': 0.07}
    away_team = {'abbrev': 'EDM'}
    home_team = {'abbrev': 'FLA'}
    
    # Calculate faceoff percentages (exact same code as NHL report)
    away_faceoff_pct = (away_team_stats['faceoffs_won'] / (away_team_stats['faceoffs_won'] + away_team_stats['faceoffs_lost']) * 100) if (away_team_stats['faceoffs_won'] + away_team_stats['faceoffs_lost']) > 0 else 0
    home_faceoff_pct = (home_team_stats['faceoffs_won'] / (home_team_stats['faceoffs_won'] + home_team_stats['faceoffs_lost']) * 100) if (home_team_stats['faceoffs_won'] + home_team_stats['faceoffs_lost']) > 0 else 0
    
    print(f"🔍 DEBUG - Creating comprehensive metrics table with:")
    print(f"  Away team: {away_team.get('abbrev', 'Away')} - Goals: {away_team_stats.get('goals', 'MISSING')}, Shots: {away_team_stats.get('shots', 'MISSING')}")
    print(f"  Home team: {home_team.get('abbrev', 'Home')} - Goals: {home_team_stats.get('goals', 'MISSING')}, Shots: {home_team_stats.get('shots', 'MISSING')}")
    
    # EXACT same code as NHL report
    basic_stats_data = [
        ['Metric', f"{away_team.get('abbrev', 'Away')}", f"{home_team.get('abbrev', 'Home')}"],
        ['Goals', 
         Paragraph(f"<b>{away_team_stats['goals']}</b>", metric_style),
         Paragraph(f"<b>{home_team_stats['goals']}</b>", metric_style)],
        ['Shots', 
         Paragraph(f"<b>{away_team_stats['shots']}</b>", metric_style),
         Paragraph(f"<b>{home_team_stats['shots']}</b>", metric_style)],
        ['Hits', 
         Paragraph(f"<b>{away_team_stats['hits']}</b>", metric_style),
         Paragraph(f"<b>{home_team_stats['hits']}</b>", metric_style)],
        ['Faceoffs Won', 
         Paragraph(f"<b>{away_team_stats['faceoffs_won']}</b>", metric_style),
         Paragraph(f"<b>{home_team_stats['faceoffs_won']}</b>", metric_style)],
        ['Faceoff %', 
         Paragraph(f"<b>{away_faceoff_pct:.1f}%</b>", metric_style),
         Paragraph(f"<b>{home_faceoff_pct:.1f}%</b>", metric_style)],
        ['Penalties', 
         Paragraph(f"<b>{away_team_stats['penalties']}</b>", metric_style),
         Paragraph(f"<b>{home_team_stats['penalties']}</b>", metric_style)],
        ['Corsi', 
         Paragraph(f"<b>{away_team_stats['corsi']}</b>", metric_style),
         Paragraph(f"<b>{home_team_stats['corsi']}</b>", metric_style)],
        ['Expected Goals', 
         Paragraph(f"<b>{away_team_stats.get('expected_goals', away_team_stats.get('xg', 0)):.2f}</b>", metric_style),
         Paragraph(f"<b>{home_team_stats.get('expected_goals', home_team_stats.get('xg', 0)):.2f}</b>", metric_style)]
    ]
    
    # EXACT same table creation as NHL report
    basic_table = Table(basic_stats_data, colWidths=[2*inch, 2*inch, 2*inch])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a2a2a')),  # Dark header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#1a1a1a')),  # Dark metric column
        ('BACKGROUND', (1, 1), (1, -1), colors.HexColor('#FF4C00')),  # EDM colors
        ('BACKGROUND', (2, 1), (2, -1), colors.HexColor('#C8102E')),  # FLA colors
        ('TEXTCOLOR', (1, 1), (1, -1), colors.white),
        ('TEXTCOLOR', (2, 1), (2, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(Paragraph("EXACT NHL CODE TEST", styles['Heading1']))
    story.append(Spacer(1, 20))
    story.append(basic_table)
    
    # Build document with dark background
    def add_dark_background(canvas, doc):
        canvas.setFillColor(colors.HexColor('#1a1a1a'))
        canvas.rect(0, 0, letter[0], letter[1], fill=1)
    
    doc.build(story, onFirstPage=add_dark_background, onLaterPages=add_dark_background)
    print("✅ Exact NHL code test created: test_exact_nhl_code.pdf")
    print("Check if the numbers are visible in this table")

if __name__ == "__main__":
    test_exact_nhl_code()
