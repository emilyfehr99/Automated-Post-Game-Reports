import os
import subprocess
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from datetime import datetime

# Configuration
R_SCRIPT_DIR = "/Users/emilyfehr8/Post Game Reports"
OUTPUT_DIR = "/Users/emilyfehr8/CascadeProjects/automated-post-game-reports/outputs"
CSV_PATH = "/Users/emilyfehr8/Desktop/My Analytics Work/Playoff Profiles/Penguins vs Flyers/Penguins Data/New Jersey Devils 2 _ 5 Pittsburgh Penguins 09.04.2026.csv"
TEAM_NAME = "Pittsburgh Penguins"
OPPONENT_NAME = "New Jersey Devils"
SCORE_TEXT = "5-2 Win"
DATA_SOURCE = "Data: Instat"

# Assets
LOGO_BLIZZARD = "/Users/emilyfehr8/Desktop/My Analytics Work/Norman/Designs/NorMan_Blizzard-removebg-preview.png"
LOGO_CUP = "/Users/emilyfehr8/Desktop/My Analytics Work/Norman/Designs/HC%E2%94%AC-CENTENNIAL-CUP-LOGO-1024x747-1-e1746207635410.png"

# Image paths
IMAGES = {
    "team_boxscore": "team_boxscore.png",
    "player_boxscore": "player_boxscore.png",
    "momentum_chart": "momentum_chart.png",
    "dz_efficiency": "dz_efficiency.png",
    "entry_effectiveness": "entry_effectiveness.png",
    "team_shooting_review": "team_shooting_review.png",
    "transition_report": "transition_report.png",
    "shots_for": "shots_for.png",
    "shots_against": "shots_against.png",
}

def run_r_scripts():
    print("--- Running R Scripts ---")
    scripts = [
        "Canada Auto.R",
        "Team Boxscore Auto.R",
        "Team Shooting Boxscore.R",
        "denials, botches, etc.R"
    ]
    
    for script in scripts:
        script_path = os.path.join(R_SCRIPT_DIR, script)
        print(f"Executing {script}...")
        try:
            subprocess.run(["Rscript", script_path, CSV_PATH, TEAM_NAME], check=True)
        except Exception as e:
            print(f"Error running {script}: {e}")

def create_pptx():
    print("--- Assembling Premium PowerPoint ---")
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(18)
    
    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)
    
    # 1. Background (Dark Gray)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(30, 30, 30)
    bg.line.fill.background()

    # 2. Header Background (Gradient/Pattern feel)
    header_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.5))
    header_bg.fill.solid()
    header_bg.fill.fore_color.rgb = RGBColor(15, 15, 15)
    header_bg.line.fill.background()

    # 3. Header Text
    # "Quarterfinals"
    title_box = slide.shapes.add_textbox(Inches(0.3), Inches(0.1), Inches(6), Inches(1))
    p = title_box.text_frame.add_paragraph()
    p.text = "Quarterfinals"
    p.font.name = 'Daggersquare'
    p.font.size = Pt(64)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    # Sub-header
    sub_title_box = slide.shapes.add_textbox(Inches(0.4), Inches(0.9), Inches(8), Inches(0.5))
    p2 = sub_title_box.text_frame.add_paragraph()
    p2.text = f"Postgame Report | {SCORE_TEXT} | {DATA_SOURCE}"
    p2.font.name = 'Daggersquare'
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(150, 150, 150)

    # 4. Logos
    if os.path.exists(LOGO_BLIZZARD):
        slide.shapes.add_picture(LOGO_BLIZZARD, Inches(8.5), Inches(0.1), height=Inches(1.2))
    if os.path.exists(LOGO_CUP):
        slide.shapes.add_picture(LOGO_CUP, Inches(10.5), Inches(0.1), height=Inches(1.2))

    # 5. Section Lines (White/Light Gray)
    def add_line(x1, y1, x2, y2):
        line = slide.shapes.add_connector(MSO_SHAPE.RECTANGLE, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
        line.line.color.rgb = RGBColor(100, 100, 100)
        line.line.width = Pt(1.5)

    add_line(0, 1.5, 13.33, 1.5) # Header separator
    add_line(6.7, 1.5, 6.7, 9.5)  # Main vertical split
    add_line(0, 9.5, 13.33, 9.5) # Shooting review top
    add_line(0, 10.3, 13.33, 10.3) # Shooting review bottom

    # 6. Content Images
    def add_img(name, left, top, width=None, height=None):
        path = os.path.join(OUTPUT_DIR, IMAGES[name])
        if os.path.exists(path):
            slide.shapes.add_picture(path, Inches(left), Inches(top), 
                                     width=Inches(width) if width else None, 
                                     height=Inches(height) if height else None)
    
    add_img("team_boxscore", 0.1, 1.6, width=6.5)
    add_img("momentum_chart", 6.8, 1.6, width=6.4, height=2.6)
    add_img("player_boxscore", 0.1, 2.8, width=6.5, height=6.5)
    add_img("dz_efficiency", 6.8, 4.4, width=6.4)
    add_img("entry_effectiveness", 6.8, 5.2, width=6.4)
    add_img("team_shooting_review", 0.1, 9.6, width=13.1)
    add_img("shots_for", 0.5, 10.5, width=4.5, height=4.5)
    add_img("shots_against", 5.5, 10.5, width=4.5, height=4.5)
    add_img("transition_report", 10.2, 10.5, width=3.0)

    # Save
    report_name = f"Premium_Post_Game_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pptx"
    report_path = os.path.join(OUTPUT_DIR, report_name)
    prs.save(report_path)
    print(f"--- Premium Report Saved: {report_path} ---")

if __name__ == "__main__":
    run_r_scripts()
    create_pptx()
