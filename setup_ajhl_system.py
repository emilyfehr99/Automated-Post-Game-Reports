#!/usr/bin/env python3
"""
AJHL System Setup Script
Complete setup and configuration for AJHL daily data collection system
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🏒 {title}")
    print(f"{'='*60}")

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_requirements():
    """Install required packages"""
    print_header("Installing Requirements")
    
    if not run_command("pip install -r ajhl_requirements.txt", "Installing Python packages"):
        print("⚠️  Some packages may have failed to install. Check the output above.")
        return False
    
    return True

def setup_directories():
    """Create necessary directories"""
    print_header("Setting Up Directories")
    
    directories = [
        "ajhl_data",
        "ajhl_data/daily_downloads",
        "ajhl_data/processed_data",
        "ajhl_data/reports",
        "ajhl_data/logs",
        "ajhl_data/backups",
        "ajhl_data/monitoring",
        "ajhl_data/monitoring/dashboards"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def setup_credentials():
    """Setup Hudl credentials"""
    print_header("Setting Up Credentials")
    
    credentials_file = "hudl_credentials.py"
    
    if os.path.exists(credentials_file):
        print(f"✅ {credentials_file} already exists")
        return True
    
    print("📝 Creating hudl_credentials.py template...")
    
    credentials_template = '''"""
Hudl Instat Credentials
Add your authorized Hudl credentials here
"""

# Hudl Instat Login Credentials (Shared Account)
HUDL_USERNAME = "your_username_here"  # Replace with your actual username
HUDL_PASSWORD = "your_password_here"  # Replace with your actual password

# Multi-User Configuration
MAX_CONCURRENT_SESSIONS = 3  # Maximum number of users that can be logged in simultaneously
SESSION_TIMEOUT_MINUTES = 30  # How long a session stays active (in minutes)

# User Identifiers (for tracking who is using the API)
# Add your team members here
TEAM_MEMBERS = {
    "emily": "Emily Fehr",
    "coach1": "Head Coach",
    "analyst1": "Data Analyst",
    "assistant1": "Assistant Coach"
}

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8001
DEBUG = True
'''
    
    try:
        with open(credentials_file, 'w') as f:
            f.write(credentials_template)
        print(f"✅ Created {credentials_file}")
        print("⚠️  IMPORTANT: Update hudl_credentials.py with your actual Hudl credentials!")
        return True
    except Exception as e:
        print(f"❌ Failed to create {credentials_file}: {e}")
        return False

def create_startup_scripts():
    """Create startup scripts for different operating systems"""
    print_header("Creating Startup Scripts")
    
    # Unix/Linux/Mac startup script
    unix_script = '''#!/bin/bash
# AJHL Daily Scraper Startup Script

echo "🏒 Starting AJHL Daily Scraper..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if credentials are configured
if ! grep -q "your_username_here" hudl_credentials.py; then
    echo "✅ Credentials appear to be configured"
else
    echo "⚠️  Please update hudl_credentials.py with your actual credentials"
    echo "   Edit the file and replace 'your_username_here' and 'your_password_here'"
    exit 1
fi

# Start the scheduler
echo "🚀 Starting daily scheduler..."
python3 ajhl_daily_scheduler.py

echo "✅ AJHL Daily Scraper started"
'''
    
    # Windows startup script
    windows_script = '''@echo off
REM AJHL Daily Scraper Startup Script

echo 🏒 Starting AJHL Daily Scraper...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if credentials are configured
findstr /C:"your_username_here" hudl_credentials.py >nul
if errorlevel 1 (
    echo ✅ Credentials appear to be configured
) else (
    echo ⚠️  Please update hudl_credentials.py with your actual credentials
    echo    Edit the file and replace 'your_username_here' and 'your_password_here'
    pause
    exit /b 1
)

REM Start the scheduler
echo 🚀 Starting daily scheduler...
python ajhl_daily_scheduler.py

echo ✅ AJHL Daily Scraper started
pause
'''
    
    try:
        # Create Unix script
        with open("start_ajhl_scraper.sh", 'w') as f:
            f.write(unix_script)
        os.chmod("start_ajhl_scraper.sh", 0o755)
        print("✅ Created start_ajhl_scraper.sh")
        
        # Create Windows script
        with open("start_ajhl_scraper.bat", 'w') as f:
            f.write(windows_script)
        print("✅ Created start_ajhl_scraper.bat")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create startup scripts: {e}")
        return False

def create_test_script():
    """Create a test script to verify the setup"""
    print_header("Creating Test Script")
    
    test_script = '''#!/usr/bin/env python3
"""
AJHL System Test Script
Test the AJHL data collection system
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import selenium
        print("✅ Selenium imported successfully")
    except ImportError as e:
        print(f"❌ Selenium import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import schedule
        print("✅ Schedule imported successfully")
    except ImportError as e:
        print(f"❌ Schedule import failed: {e}")
        return False
    
    try:
        import plotly
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    return True

def test_credentials():
    """Test if credentials are configured"""
    print("🔐 Testing credentials...")
    
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        
        if HUDL_USERNAME == "your_username_here" or HUDL_PASSWORD == "your_password_here":
            print("⚠️  Credentials not configured - please update hudl_credentials.py")
            return False
        
        print("✅ Credentials appear to be configured")
        return True
    except ImportError as e:
        print(f"❌ Could not import credentials: {e}")
        return False

def test_directories():
    """Test if directories exist"""
    print("📁 Testing directories...")
    
    required_dirs = [
        "ajhl_data",
        "ajhl_data/daily_downloads",
        "ajhl_data/reports",
        "ajhl_data/logs"
    ]
    
    for directory in required_dirs:
        if not Path(directory).exists():
            print(f"❌ Directory missing: {directory}")
            return False
        print(f"✅ Directory exists: {directory}")
    
    return True

def test_ajhl_modules():
    """Test if AJHL modules can be imported"""
    print("🏒 Testing AJHL modules...")
    
    try:
        from ajhl_team_config import AJHL_TEAMS, get_active_teams
        print("✅ AJHL team config imported successfully")
        print(f"   Found {len(get_active_teams())} active teams")
    except ImportError as e:
        print(f"❌ AJHL team config import failed: {e}")
        return False
    
    try:
        from ajhl_team_manager import AJHLTeamManager
        print("✅ AJHL team manager imported successfully")
    except ImportError as e:
        print(f"❌ AJHL team manager import failed: {e}")
        return False
    
    try:
        from ajhl_daily_scheduler import AJHLDailyScheduler
        print("✅ AJHL daily scheduler imported successfully")
    except ImportError as e:
        print(f"❌ AJHL daily scheduler import failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🏒 AJHL System Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Credentials Test", test_credentials),
        ("Directories Test", test_directories),
        ("AJHL Modules Test", test_ajhl_modules)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n🧪 Running {test_name}...")
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The AJHL system is ready to use.")
        print("\\n🚀 To start the system:")
        print("   - Update hudl_credentials.py with your actual credentials")
        print("   - Run: python ajhl_daily_scheduler.py")
        print("   - Or use: ./start_ajhl_scraper.sh (Unix/Mac) or start_ajhl_scraper.bat (Windows)")
    else:
        print("⚠️  Some tests failed. Please check the errors above and run setup again.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''
    
    try:
        with open("test_ajhl_system.py", 'w') as f:
            f.write(test_script)
        os.chmod("test_ajhl_system.py", 0o755)
        print("✅ Created test_ajhl_system.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create test script: {e}")
        return False

def create_readme():
    """Create a comprehensive README file"""
    print_header("Creating Documentation")
    
    readme_content = '''# AJHL Daily Data Collection System

A comprehensive automated system for daily collection of CSV data from Hudl Instat for all Alberta Junior Hockey League (AJHL) teams.

## 🏒 Features

- **Daily Automated Collection**: Automatically downloads CSV data for all AJHL teams
- **Multi-Team Support**: Handles all 18 AJHL teams across North and South divisions
- **Comprehensive Data Profiles**: Multiple data collection profiles (comprehensive, daily analytics, goalie-focused)
- **Scheduling System**: Built-in daily scheduling with configurable run times
- **Monitoring Dashboard**: Real-time monitoring and reporting system
- **Error Recovery**: Automatic retry mechanisms and error handling
- **Data Organization**: Structured storage with team-specific directories

## 📁 System Components

### Core Files
- `ajhl_team_config.py` - Team configuration and data profiles
- `ajhl_team_manager.py` - Main team management and data collection
- `ajhl_daily_scheduler.py` - Daily scheduling and automation
- `ajhl_monitoring_dashboard.py` - Monitoring and reporting dashboard

### Supporting Files
- `hudl_credentials.py` - Hudl Instat credentials (create this)
- `ajhl_requirements.txt` - Python package requirements
- `setup_ajhl_system.py` - System setup script
- `test_ajhl_system.py` - System test script

## 🚀 Quick Start

### 1. Setup
```bash
# Run the setup script
python setup_ajhl_system.py

# Install requirements
pip install -r ajhl_requirements.txt
```

### 2. Configure Credentials
Edit `hudl_credentials.py` and add your Hudl Instat credentials:
```python
HUDL_USERNAME = "your_actual_username"
HUDL_PASSWORD = "your_actual_password"
```

### 3. Test the System
```bash
python test_ajhl_system.py
```

### 4. Start Daily Collection
```bash
# Start the scheduler
python ajhl_daily_scheduler.py

# Or use the startup script
./start_ajhl_scraper.sh  # Unix/Mac
start_ajhl_scraper.bat   # Windows
```

## 📊 AJHL Teams Supported

### North Division
- Sherwood Park Crusaders
- Spruce Grove Saints
- St. Albert Steel
- Strathcona Chiefs
- Whitecourt Wolverines
- Bonnyville Pontiacs
- Drayton Valley Thunder
- Fort McMurray Oil Barons
- Grande Prairie Storm
- Lloydminster Bobcats

### South Division
- Brooks Bandits
- Calgary Canucks
- Camrose Kodiaks
- Drumheller Dragons
- Okotoks Oilers
- Olds Grizzlys
- Blackfalds Bulldogs
- Canmore Eagles

## 🔧 Configuration

### Data Collection Profiles
- **comprehensive**: All available data including shifts, stats, shots, passes, puck battles
- **daily_analytics**: Essential daily metrics for analysis
- **goalie_focused**: Goalie-specific statistics and metrics

### Scheduling Options
- Daily run time: 6:00 AM (configurable)
- Team processing delay: 60 seconds between teams
- Max concurrent teams: 3
- Retry attempts: 3 with 30-minute delays

## 📈 Monitoring and Reports

### Dashboard Features
- Real-time success rate tracking
- Team data volume monitoring
- Processing time analysis
- Division comparison charts
- Team status overview

### Generated Reports
- Daily summary reports (JSON)
- HTML monitoring dashboard
- Text summary reports
- Scheduler statistics

## 🗂️ Data Storage Structure

```
ajhl_data/
├── daily_downloads/          # Daily CSV downloads by team
│   ├── brooks_bandits/
│   ├── calgary_canucks/
│   └── ...
├── processed_data/           # Processed and cleaned data
├── reports/                  # Daily and summary reports
├── logs/                     # System logs and statistics
├── backups/                  # Data backups
└── monitoring/               # Dashboard and monitoring files
    └── dashboards/
```

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify Hudl credentials in `hudl_credentials.py`
   - Check if account has access to AJHL teams
   - Ensure no session conflicts

2. **Missing Team Data**
   - Some teams may not have Hudl team IDs discovered yet
   - Run team ID discovery process
   - Check team configuration

3. **Scheduler Not Running**
   - Check system logs in `ajhl_data/logs/`
   - Verify Python environment
   - Check file permissions

4. **Data Download Failures**
   - Check internet connection
   - Verify Hudl platform accessibility
   - Review error logs for specific issues

### Log Files
- `ajhl_daily_scraper.log` - Main application logs
- `ajhl_scheduler.log` - Scheduler-specific logs
- `scheduler_stats.json` - Scheduler statistics

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review log files for error details
3. Run the test script to verify system status
4. Check Hudl Instat platform accessibility

## ⚠️ Important Notes

- This system requires valid Hudl Instat credentials
- Respect Hudl's terms of service and rate limits
- Use responsibly and don't overload their servers
- Regular monitoring recommended to ensure data quality
- Backup important data regularly

## 🔄 Maintenance

### Daily
- Monitor dashboard for success rates
- Check log files for errors
- Verify data downloads

### Weekly
- Review team data coverage
- Clean up old data files
- Update team configurations if needed

### Monthly
- Analyze data quality trends
- Update Hudl team IDs as needed
- Review and optimize data profiles

## 📄 License

This project is for educational and research purposes. Please respect Hudl's terms of service and any applicable laws.
'''
    
    try:
        with open("AJHL_README.md", 'w') as f:
            f.write(readme_content)
        print("✅ Created AJHL_README.md")
        return True
    except Exception as e:
        print(f"❌ Failed to create README: {e}")
        return False

def main():
    """Main setup function"""
    print_header("AJHL Daily Scraper Setup")
    print("Setting up the complete AJHL data collection system...")
    
    # Check Python version
    if not check_python_version():
        print("❌ Setup failed: Python version incompatible")
        return False
    
    # Run setup steps
    setup_steps = [
        ("Installing Requirements", install_requirements),
        ("Setting Up Directories", setup_directories),
        ("Setting Up Credentials", setup_credentials),
        ("Creating Startup Scripts", create_startup_scripts),
        ("Creating Test Script", create_test_script),
        ("Creating Documentation", create_readme)
    ]
    
    success_count = 0
    total_steps = len(setup_steps)
    
    for step_name, step_func in setup_steps:
        if step_func():
            success_count += 1
        else:
            print(f"⚠️  {step_name} had issues, but continuing...")
    
    print_header("Setup Complete")
    print(f"✅ Completed {success_count}/{total_steps} setup steps")
    
    if success_count == total_steps:
        print("🎉 AJHL system setup completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Update hudl_credentials.py with your actual Hudl credentials")
        print("2. Run: python test_ajhl_system.py")
        print("3. Start the system: python ajhl_daily_scheduler.py")
        print("\n📚 See AJHL_README.md for detailed documentation")
    else:
        print("⚠️  Setup completed with some issues. Please review the output above.")
        print("You may need to manually fix some components.")
    
    return success_count == total_steps

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
