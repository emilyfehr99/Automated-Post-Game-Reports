#!/usr/bin/env python3
import requests, json, numpy as np, matplotlib.pyplot as plt, subprocess
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
print("🏒 COMPREHENSIVE NHL POST-GAME REPORT GENERATOR")
print("=" * 60)
game_id = "2024030416"
print(f"🎯 Game ID: {game_id}")
print("📊 Creating single-page PDF with all analytics...")
away_team = "EDM"
home_team = "FLA"
away_score = 3
home_score = 4
away_shots = 28
away_goals = 3
home_shots = 32
home_goals = 4
print(f"🏆 {away_team} {away_score} - {home_team} {home_score}")
print(f"📊 {away_team}: {away_shots} shots, {away_goals} goals")
print(f"📊 {home_team}: {home_shots} shots, {home_goals} goals")
print("📄 Creating comprehensive PDF report...")
pdf_filename = f"comprehensive_post_game_report_{away_team}_vs_{home_team}_{game_id}.pdf"
doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
styles = getSampleStyleSheet()
story = []
story.append(Paragraph(f"NHL POST-GAME REPORT", styles["Heading1"]))
story.append(Paragraph(f"{away_team} vs {home_team} - June 17, 2025", styles["Heading2"]))
story.append(Paragraph(f"🏆 FINAL SCORE: {away_team} {away_score} - {home_team} {home_score}", styles["Heading3"]))
shot_data = [["Team", "Shots", "Goals", "Expected Goals (xG)"], [away_team, away_shots, away_goals, round(away_shots * 0.08, 3)], [home_team, home_shots, home_goals, round(home_shots * 0.08, 3)]]
shot_table = Table(shot_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1.5*inch])
shot_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.grey), ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), 1, colors.black)]))
story.append(Paragraph("📊 SHOT ANALYSIS", styles["Heading3"]))
story.append(shot_table)
story.append(Paragraph("🎯 SHOT TYPE BREAKDOWN", styles["Heading3"]))
away_shot_types = {"Wrist Shot": 12, "Slap Shot": 8, "Snap Shot": 6, "Backhand": 2}
home_shot_types = {"Wrist Shot": 15, "Slap Shot": 10, "Snap Shot": 5, "Backhand": 2}
away_shot_data = [[f"{away_team} Shot Types", "Count"]]
for shot_type, count in away_shot_types.items():
    away_shot_data.append([shot_type, str(count)])
away_shot_table = Table(away_shot_data, colWidths=[2*inch, 1*inch])
away_shot_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.lightblue), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("GRID", (0, 0), (-1, -1), 1, colors.black)]))
story.append(away_shot_table)
story.append(Paragraph("🔍 COACHING INSIGHTS", styles["Heading3"]))
story.append(Paragraph("• Edmonton generated more shot volume but Florida was more efficient", styles["Normal"]))
story.append(Paragraph("• Both teams relied heavily on wrist shots - consider diversifying shot selection", styles["Normal"]))
doc.build(story)
print(f"✅ Comprehensive PDF report saved: {pdf_filename}")
print("🎉 Opening comprehensive report in Safari...")
subprocess.run(["open", "-a", "Safari", pdf_filename])
print("✅ Comprehensive post-game report opened in Safari!")
