#!/usr/bin/env python3
"""Generate 5 team reports and save as images to desktop"""

from team_report_generator import TeamReportGenerator
import os
import subprocess
from pathlib import Path

# Get desktop path
desktop = Path.home() / "Desktop"

# List of 5 teams to generate
teams = ['NJD', 'COL', 'NYR', 'BOS', 'VGK']

gen = TeamReportGenerator()

for team in teams:
    print(f"\nGenerating report for {team}...")
    try:
        # Generate PDF report
        pdf_path = gen.generate_team_report(team)
        
        if pdf_path and os.path.exists(pdf_path):
            # Convert PDF to image using sips (macOS built-in tool)
            # First page only, high resolution
            image_path = desktop / f"{team}_report.png"
            
            # Use sips to convert PDF to PNG (extracts first page)
            result = subprocess.run([
                'sips', '-s', 'format', 'png', 
                '-s', 'formatOptions', 'high',
                '--out', str(image_path),
                pdf_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and image_path.exists():
                print(f"✓ Saved {team} report image to Desktop: {image_path.name}")
            else:
                # Alternative: try using pdftoppm if available
                try:
                    result = subprocess.run([
                        'pdftoppm', '-png', '-r', '300', '-f', '1', '-l', '1',
                        pdf_path, str(desktop / team)
                    ], capture_output=True, text=True)
                    if result.returncode == 0:
                        # Rename the output file
                        output_file = desktop / f"{team}-1.png"
                        if output_file.exists():
                            output_file.rename(image_path)
                            print(f"✓ Saved {team} report image to Desktop: {image_path.name}")
                        else:
                            print(f"✗ Could not convert {team} PDF to image")
                    else:
                        print(f"✗ Could not convert {team} PDF to image")
                except FileNotFoundError:
                    print(f"✗ Could not convert {team} PDF - need sips or pdftoppm")
        else:
            print(f"✗ Could not generate PDF for {team}")
    except Exception as e:
        print(f"✗ Error generating report for {team}: {e}")

print(f"\n✓ Completed! Check your Desktop for the report images.")

