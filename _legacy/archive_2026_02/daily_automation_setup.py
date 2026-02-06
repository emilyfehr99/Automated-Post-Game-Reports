#!/usr/bin/env python3
"""
Daily NHL Post-Game Report Automation Setup
Creates automated daily reports at 5 AM for previous day's games
"""

import os
import subprocess
from pathlib import Path

def create_daily_script():
    """Create the daily execution script"""
    
    script_content = '''#!/bin/bash
# Daily NHL Post-Game Reports Generator
# Runs at 5 AM every day for previous day's games

# Set up environment
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
export PYTHONPATH="/Users/emilyfehr8/CascadeProjects/nhl_postgame_reports:$PYTHONPATH"

# Log file for debugging
LOG_FILE="/Users/emilyfehr8/Desktop/nhl_reports_daily.log"

# Function to log with timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

log_message "🏒 Starting daily NHL post-game report generation"

# Change to project directory
cd /Users/emilyfehr8/CascadeProjects/nhl_postgame_reports

# Run the batch generator
log_message "📊 Running batch report generator..."
python3 batch_report_generator.py >> "$LOG_FILE" 2>&1

# Check if PDFs were generated
if [ -d "/Users/emilyfehr8/Desktop/Recent Games" ]; then
    PDF_COUNT=$(ls -1 "/Users/emilyfehr8/Desktop/Recent Games"/*.pdf 2>/dev/null | wc -l)
    log_message "📄 Generated $PDF_COUNT PDF reports"
    
    # Convert to PNG images
    log_message "🖼️  Converting PDFs to PNG images..."
    python3 -c "
import os
import shutil
from pathlib import Path
from pdf2image import convert_from_path

desktop = Path.home() / 'Desktop'
source_dir = desktop / 'Recent Games'
dest_dir = desktop / 'Recent Games Images'

# Clear old images
if dest_dir.exists():
    shutil.rmtree(dest_dir)

dest_dir.mkdir(exist_ok=True)

# Convert PDFs
pdf_files = list(source_dir.glob('*.pdf'))
successful = 0

for pdf_file in pdf_files:
    try:
        pages = convert_from_path(pdf_file, dpi=300, fmt='PNG')
        if pages:
            page = pages[0]
            output_path = dest_dir / f'{pdf_file.stem}.png'
            page.save(output_path, 'PNG', optimize=True, quality=95)
            successful += 1
    except:
        pass

print(f'Converted {successful} reports to PNG')

# Add metrics guide
try:
    import sys
    sys.path.append('/Users/emilyfehr8/CascadeProjects/nhl_postgame_reports')
    from metrics_guide_generator import MetricsGuideGenerator
    
    generator = MetricsGuideGenerator()
    guide_pdf = generator.generate_guide('temp_metrics_guide.pdf')
    
    if guide_pdf and os.path.exists(guide_pdf):
        pages = convert_from_path(guide_pdf, dpi=300, fmt='PNG')
        if pages:
            guide_png = dest_dir / 'NHL_PostGame_Reports_Metrics_Guide.png'
            pages[0].save(guide_png, 'PNG', optimize=True, quality=95)
            print('Added metrics guide')
        os.remove(guide_pdf)
except:
    pass

# Delete PDF folder
if source_dir.exists():
    shutil.rmtree(source_dir)
    print('Deleted PDF folder')
" >> "$LOG_FILE" 2>&1
    
    PNG_COUNT=$(ls -1 "/Users/emilyfehr8/Desktop/Recent Games Images"/*.png 2>/dev/null | wc -l)
    log_message "🖼️  Generated $PNG_COUNT PNG images"
    
    log_message "✅ Daily report generation completed successfully"
else
    log_message "❌ No PDF reports were generated"
fi

log_message "🏒 Daily NHL report generation finished"
'''
    
    # Write the script
    script_path = Path.home() / "nhl_daily_reports.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod(script_path, 0o755)
    
    return script_path

def setup_cron_job(script_path):
    """Set up the cron job for 5 AM daily execution"""
    
    # Create cron entry
    cron_entry = f"0 5 * * * {script_path}\n"
    
    print("🕐 Setting up daily cron job for 5 AM...")
    print(f"📝 Cron entry: {cron_entry.strip()}")
    
    try:
        # Get current crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_crontab = result.stdout if result.returncode == 0 else ""
        
        # Check if entry already exists
        if str(script_path) in current_crontab:
            print("⚠️  Cron job already exists, updating...")
            # Remove old entries
            lines = current_crontab.split('\n')
            new_lines = [line for line in lines if str(script_path) not in line and line.strip()]
            current_crontab = '\n'.join(new_lines) + '\n' if new_lines else ""
        
        # Add new entry
        new_crontab = current_crontab + cron_entry
        
        # Write new crontab
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_crontab)
        
        if process.returncode == 0:
            print("✅ Cron job set up successfully!")
            print("🕐 NHL reports will generate daily at 5:00 AM")
            return True
        else:
            print("❌ Failed to set up cron job")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up cron job: {e}")
        return False

def main():
    """Set up daily automation"""
    print("🏒 NHL Post-Game Reports Daily Automation Setup 🏒")
    print("=" * 60)
    
    # Create the daily script
    print("📝 Creating daily execution script...")
    script_path = create_daily_script()
    print(f"✅ Daily script created: {script_path}")
    
    # Set up cron job
    success = setup_cron_job(script_path)
    
    if success:
        print("\n🎉 AUTOMATION SETUP COMPLETE!")
        print("=" * 40)
        print("📅 Schedule: Every day at 5:00 AM")
        print("📊 Action: Generate reports for previous day's games")
        print("📁 Output: PNG images saved to Desktop/Recent Games Images/")
        print("📋 Includes: Game reports + metrics guide")
        print("🔄 Auto-cleanup: PDF files deleted after PNG conversion")
        print("📝 Logs: /Users/emilyfehr8/Desktop/nhl_reports_daily.log")
        print("\n💡 To disable: Run 'crontab -e' and remove the NHL reports line")
        print("💡 To check status: Check the log file on your Desktop")
    else:
        print("\n❌ AUTOMATION SETUP FAILED")
        print("Manual setup required - see script at:", script_path)

if __name__ == "__main__":
    main()
