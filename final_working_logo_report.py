#!/usr/bin/env python3
"""
Final working NHL report with team logos
"""

import requests
import json
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_team_logo(team_abbrev):
    """Create a team logo"""
    fig, ax = plt.subplots(figsize=(4, 4), facecolor='white')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    if team_abbrev == 'EDM':
        # Edmonton Oilers
        bg_circle = patches.Circle((50, 50), 40, facecolor='#FF4C00', edgecolor='#041E42', linewidth=4)
        ax.add_patch(bg_circle)
        inner_circle = patches.Circle((50, 50), 25, facecolor='#041E42', edgecolor='white', linewidth=3)
        ax.add_patch(inner_circle)
        oil_drop = patches.Circle((35, 35), 8, facecolor='white', edgecolor='#041E42', linewidth=2)
        ax.add_patch(oil_drop)
        ax.text(50, 50, 'EDM', fontsize=28, fontweight='bold', ha='center', va='center', color='white')
    elif team_abbrev == 'VGK':
        # Vegas Golden Knights
        shield_points = [(50, 80), (70, 75), (80, 60), (75, 40), (60, 20), (40, 20), (25, 40), (20, 60), (30, 75)]
        shield = patches.Polygon(shield_points, facecolor='#B9975B', edgecolor='#000000', linewidth=4)
        ax.add_patch(shield)
        inner_points = [(p[0]*0.7 + 15, p[1]*0.7 + 15) for p in shield_points]
        inner_shield = patches.Polygon(inner_points, facecolor='#333F48', edgecolor='white', linewidth=2)
        ax.add_patch(inner_shield)
        ax.text(50, 50, 'VGK', fontsize=24, fontweight='bold', ha='center', va='center', color='white')
    else:
        # Generic
        bg_circle = patches.Circle((50, 50), 40, facecolor='#666666', edgecolor='#000000', linewidth=3)
        ax.add_patch(bg_circle)
        ax.text(50, 50, team_abbrev, fontsize=24, fontweight='bold', ha='center', va='center', color='white')
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')
    img_buffer.seek(0)
    plt.close()
    return img_buffer

def get_game_data(game_id):
    """Get game data"""
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    try:
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def main():
    """Create final working report"""
    print("🏒 FINAL WORKING LOGO REPORT 🏒")
    
    # Get game data
    game_id = "2024030242"
    game_data = get_game_data(game_id)
    
    if not game_data:
        print("❌ Could not fetch game data")
        return
    
    away_team = game_data.get('awayTeam', {})
    home_team = game_data.get('homeTeam', {})
    
    away_abbrev = away_team.get('abbrev', 'Away')
    home_abbrev = home_team.get('abbrev', 'Home')
    
    print(f"Creating report for {away_abbrev} vs {home_abbrev}")
    
    # Create logos
    print("Creating team logos...")
    away_logo = create_team_logo(away_abbrev)
    home_logo = create_team_logo(home_abbrev)
    print("✅ Logos created")
    
    # Create PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"final_working_logo_report_{game_id}_{timestamp}.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    
    # Title
    title_style = ParagraphStyle('Title', parent=getSampleStyleSheet()['Heading1'],
                                fontSize=24, textColor=colors.darkblue,
                                alignment=TA_CENTER, spaceAfter=20)
    
    story.append(Paragraph("🏒 NHL GAME REPORT WITH TEAM LOGOS 🏒", title_style))
    story.append(Spacer(1, 20))
    
    # Header with logos
    try:
        away_img = Image(away_logo)
        away_img.drawHeight = 3*inch
        away_img.drawWidth = 3*inch
        
        home_img = Image(home_logo)
        home_img.drawHeight = 3*inch
        home_img.drawWidth = 3*inch
        
        header_data = [
            [away_img, f"🏒 {away_abbrev} vs {home_abbrev} 🏒", home_img],
            [f"{away_team.get('commonName', {}).get('default', 'Away Team')}", "NHL Game Report", f"{home_team.get('commonName', {}).get('default', 'Home Team')}"]
        ]
        
        header_table = Table(header_data, colWidths=[3*inch, 2*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 24),
            ('FONTSIZE', (0, 1), (-1, 1), 16),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkblue),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        print("✅ Logo header created")
        
    except Exception as e:
        print(f"❌ Error creating logo header: {e}")
        story.append(Paragraph(f"🏒 {away_abbrev} vs {home_abbrev} 🏒", title_style))
    
    # Game info
    story.append(Paragraph("GAME INFORMATION", getSampleStyleSheet()['Heading2']))
    story.append(Paragraph(f"Game ID: {game_id}", getSampleStyleSheet()['Normal']))
    story.append(Paragraph(f"Date: {game_data.get('game', {}).get('gameDate', 'Unknown')}", getSampleStyleSheet()['Normal']))
    story.append(Paragraph(f"Final Score: {away_abbrev} {away_team.get('score', 0)} - {home_team.get('score', 0)} {home_abbrev}", getSampleStyleSheet()['Normal']))
    story.append(Spacer(1, 20))
    
    # Logo info
    story.append(Paragraph("TEAM LOGOS", getSampleStyleSheet()['Heading2']))
    story.append(Paragraph("This report features team logos created with team colors:", getSampleStyleSheet()['Normal']))
    story.append(Paragraph(f"• {away_abbrev}: Team-specific design with official colors", getSampleStyleSheet()['Normal']))
    story.append(Paragraph(f"• {home_abbrev}: Team-specific design with official colors", getSampleStyleSheet()['Normal']))
    story.append(Paragraph("• Logos are created using matplotlib and should be visible!", getSampleStyleSheet()['Normal']))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Final report created: {filename}")
    print("\nThis report should show the team logos!")

if __name__ == "__main__":
    main()
