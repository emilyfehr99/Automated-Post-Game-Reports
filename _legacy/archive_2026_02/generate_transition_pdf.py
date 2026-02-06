#!/usr/bin/env python3
"""
Generate detailed Zone Transition Efficiency report for NHL games in PDF format
Focuses on:
1. Entries leading to Shots (ENtoSOG)
2. Exits leading to Entries (EXtoEN)
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from zone_efficiency_analyzer import ZoneTransitionEfficiencyAnalyzer
from nhl_api_client import NHLAPIClient

def generate_transition_pdf(game_id, output_path=None):
    """Generate comprehensive zone transition PDF report"""
    
    if not output_path:
        output_path = f"zone_transitions_{game_id}.pdf"
    
    analyzer = ZoneTransitionEfficiencyAnalyzer()
    api_client = NHLAPIClient()
    
    # Get game data
    game_data = api_client.get_comprehensive_game_data(game_id)
    if not game_data:
        print(f"❌ Could not fetch game data for {game_id}")
        return None
        
    # Get team mapping
    boxscore = game_data.get('boxscore', {})
    teams = {
        boxscore.get('awayTeam', {}).get('id'): boxscore.get('awayTeam', {}).get('abbrev', 'AWAY'),
        boxscore.get('homeTeam', {}).get('id'): boxscore.get('homeTeam', {}).get('abbrev', 'HOME')
    }
    
    # Analyze transitions
    result = analyzer.analyze_game(game_id)
    if not result:
        print(f"❌ No transition data found for game {game_id}")
        return None
    
    # Setup document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        alignment=1
    )
    
    team_header_style = ParagraphStyle(
        'TeamHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#1A4D6B')
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=5
    )
    
    # Add Title
    story.append(Paragraph("ZONE TRANSITION EFFICIENCY REPORT", title_style))
    story.append(Paragraph(f"Game ID: {game_id} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # 1. Summary Table
    summary_data = [['Team', 'Total Entries', 'EN → SOG', 'Eff %', 'Total Exits', 'EX → EN', 'Eff %']]
    for team_id, abbrev in teams.items():
        stats = result['stats'].get(team_id, {})
        en_total = stats.get('total_entries', 0)
        en_sog = len(stats.get('entries_to_shots', []))
        en_eff = (en_sog / en_total * 100) if en_total > 0 else 0
        
        ex_total = stats.get('total_exits', 0)
        ex_en = len(stats.get('exits_to_entries', []))
        ex_eff = (ex_en / ex_total * 100) if ex_total > 0 else 0
        
        summary_data.append([
            abbrev,
            str(en_total),
            str(en_sog),
            f"{en_eff:.1f}%",
            str(ex_total),
            str(ex_en),
            f"{ex_eff:.1f}%"
        ])
    
    t = Table(summary_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A4D6B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # 2. Detailed Lists
    for team_id, abbrev in teams.items():
        story.append(Paragraph(f"TEAM: {abbrev}", team_header_style))
        stats = result['stats'].get(team_id, {})
        
        # Entries leading to Shots
        story.append(Paragraph("ENTRIES LEADING TO SOG", section_style))
        entries = stats.get('entries_to_shots', [])
        if not entries:
            story.append(Paragraph("None identified in play-by-play.", styles['Italic']))
        else:
            data = [['Period', 'Entry Time', 'Shot Time', 'Shot Type', 'Elapsed']]
            for e in entries:
                data.append([
                    str(e['period']),
                    e['entry_time'],
                    e['shot_time'],
                    e['shot_type'].replace('-', ' ').title(),
                    f"{e['time_diff']}s"
                ])
            
            et = Table(data, hAlign='LEFT')
            et.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(et)
        
        story.append(Spacer(1, 10))
        
        # Exits leading to Entries
        story.append(Paragraph("EXITS LEADING TO ENTRIES", section_style))
        exits = stats.get('exits_to_entries', [])
        if not exits:
            story.append(Paragraph("None identified in play-by-play.", styles['Italic']))
        else:
            data = [['Period', 'Exit Time', 'Entry Time', 'Transition Type', 'Elapsed']]
            for e in exits:
                data.append([
                    str(e['period']),
                    e['exit_time'],
                    e['entry_time'],
                    e['type'].title(),
                    f"{e['time_diff']}s"
                ])
            
            xt = Table(data, hAlign='LEFT')
            xt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(xt)
            
        story.append(PageBreak())
    
    doc.build(story)
    print(f"✅ Transition PDF generated: {output_path}")
    return output_path

if __name__ == "__main__":
    import sys
    game_id = sys.argv[1] if len(sys.argv) > 1 else '2025020573'
    generate_transition_pdf(game_id)
