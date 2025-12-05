#!/usr/bin/env python3
"""
Test Report with Debug - Generate report with debug output to verify logo usage
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import requests
import os

class DebugReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.logos_dir = "team_logos_png"
        
        self.title_style = ParagraphStyle(
            'Title', parent=self.styles['Heading1'],
            fontSize=24, textColor=colors.darkblue,
            alignment=TA_CENTER, spaceAfter=20
        )
    
    def get_team_logo(self, team_abbrev, size=(1*inch, 1*inch)):
        """Get team PNG logo with debug output"""
        logo_path = os.path.join(self.logos_dir, f"{team_abbrev}.png")
        print(f"🔍 Looking for logo: {logo_path}")
        
        if os.path.exists(logo_path):
            print(f"✅ Found logo file: {logo_path}")
            try:
                img = Image(logo_path)
                img.drawHeight = size[1]
                img.drawWidth = size[0]
                print(f"✅ Created ReportLab Image: {img.drawWidth}x{img.drawHeight}")
                return img
            except Exception as e:
                print(f"❌ Failed to create ReportLab Image: {e}")
                return None
        else:
            print(f"❌ Logo file not found: {logo_path}")
            return None
    
    def create_logo_placeholder(self, team_abbrev):
        """Create text placeholder with debug output"""
        print(f"📝 Creating text placeholder for {team_abbrev}")
        return Paragraph(f"<b>{team_abbrev}</b>", self.styles['Normal'])
    
    def generate_debug_report(self, game_id):
        """Generate report with debug output"""
        print("🏒 GENERATING DEBUG REPORT WITH LOGO VERIFICATION")
        print("=" * 60)
        
        # Get game data
        play_by_play_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
        
        try:
            response = requests.get(play_by_play_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ Game data fetched successfully")
            else:
                print(f"❌ API returned {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None
        
        # Get team info
        away_team = data.get('awayTeam', {})
        home_team = data.get('homeTeam', {})
        away_abbrev = away_team.get('abbrev', 'Unknown')
        home_abbrev = home_team.get('abbrev', 'Unknown')
        
        print(f"\n🏒 TEAMS IN GAME:")
        print(f"Away: {away_abbrev}")
        print(f"Home: {home_abbrev}")
        
        # Create PDF
        output_filename = f"debug_report_{game_id}.pdf"
        doc = SimpleDocTemplate(output_filename, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("🏒 DEBUG REPORT - LOGO VERIFICATION 🏒", self.title_style))
        story.append(Spacer(1, 20))
        
        # Team logos section
        print(f"\n🖼️ LOADING TEAM LOGOS:")
        print("=" * 30)
        
        away_logo = self.get_team_logo(away_abbrev)
        home_logo = self.get_team_logo(home_abbrev)
        
        # Create logo table
        logo_data = [['Away Team', 'Home Team']]
        logo_row = []
        
        if away_logo:
            print(f"✅ Using PNG logo for {away_abbrev}")
            logo_row.append(away_logo)
        else:
            print(f"⚠️ Using text placeholder for {away_abbrev}")
            logo_row.append(self.create_logo_placeholder(away_abbrev))
        
        if home_logo:
            print(f"✅ Using PNG logo for {home_abbrev}")
            logo_row.append(home_logo)
        else:
            print(f"⚠️ Using text placeholder for {home_abbrev}")
            logo_row.append(self.create_logo_placeholder(home_abbrev))
        
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
        
        # Summary
        story.append(Paragraph(f"Game: {away_abbrev} vs {home_abbrev}", self.styles['Heading2']))
        story.append(Paragraph(f"Game ID: {game_id}", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        print(f"\n✅ Debug report generated: {output_filename}")
        return output_filename

def main():
    """Generate debug report"""
    generator = DebugReportGenerator()
    game_id = "2024030242"
    
    result = generator.generate_debug_report(game_id)
    
    if result:
        print(f"\n🎉 SUCCESS! Debug report created: {result}")
        print("Check the PDF to verify if logos are displaying correctly.")
    else:
        print("\n❌ Failed to generate debug report")

if __name__ == "__main__":
    main()
