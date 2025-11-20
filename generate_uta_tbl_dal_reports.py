#!/usr/bin/env python3
"""Generate UTA, TBL, and DAL team reports and save as images to desktop"""

from team_report_generator import TeamReportGenerator
import os
import subprocess
from pathlib import Path

# Get desktop path
desktop = Path.home() / "Desktop"

# Teams to generate
teams = ['UTA', 'TBL', 'DAL']

gen = TeamReportGenerator()

# Pre-calculate clutch rankings ONCE for all teams (this will cache for 24 hours)
print("Pre-calculating league-wide clutch rankings (this may take a minute)...")
print("(This only needs to happen once - will be cached for 24 hours)")
try:
    gen.get_league_clutch_rankings()
    print("✓ Clutch rankings calculated and cached")
except Exception as e:
    print(f"Warning: Could not pre-calculate rankings: {e}")
    print("(Reports will still generate, but may be slower)")

print()

for team in teams:
    print(f"\n{'='*60}")
    print(f"Generating report for {team}...")
    print('='*60)
    try:
        # Generate PDF report
        pdf_path = gen.generate_team_report(team)
        
        if pdf_path and os.path.exists(pdf_path):
            # Convert PDF to image using wand/ImageMagick
            image_path = desktop / f"{team}_report.png"
            
            try:
                from wand.image import Image as WandImage
                with WandImage(filename=pdf_path, resolution=300) as img:
                    # Get first page only
                    img_seq = img.sequence[0]
                    with WandImage(img_seq) as first_page:
                        first_page.format = 'png'
                        first_page.save(filename=str(image_path))
                
                print(f"✓ Saved {team} report image to Desktop: {image_path.name}")
            except ImportError:
                # Fallback to sips (macOS built-in tool)
                try:
                    result = subprocess.run([
                        'sips', '-s', 'format', 'png', 
                        '-s', 'formatOptions', 'high',
                        '--out', str(image_path),
                        pdf_path
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0 and os.path.exists(image_path):
                        print(f"✓ Saved {team} report image to Desktop: {image_path.name}")
                    else:
                        print(f"✗ Could not convert {team} PDF to image using sips")
                        print(f"  PDF saved at: {pdf_path}")
                except Exception as e:
                    print(f"✗ Could not convert {team} PDF to image: {e}")
                    print(f"  PDF saved at: {pdf_path}")
        else:
            print(f"✗ Could not generate PDF for {team}")
    except Exception as e:
        print(f"✗ Error generating report for {team}: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*60}")
print("✓ Completed! Check your Desktop for the report images.")
print('='*60)

