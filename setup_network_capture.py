#!/usr/bin/env python3
"""
Setup Network Data Capture System
Easy setup for automated network data capture
"""

import os
import json
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_config_file():
    """Create configuration file for network capture"""
    try:
        logger.info("🔧 Creating configuration file...")
        
        config = {
            "hudl_credentials": {
                "username": "your_username_here",
                "password": "your_password_here"
            },
            "capture_settings": {
                "team_id": "21479",
                "output_directory": "daily_network_data",
                "capture_time": "03:00",
                "headless_mode": True
            },
            "schedule_settings": {
                "enabled": True,
                "timezone": "America/New_York",
                "retry_attempts": 3,
                "retry_delay_minutes": 5
            }
        }
        
        with open("network_capture_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        logger.info("✅ Configuration file created: network_capture_config.json")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating config file: {e}")
        return False

def create_requirements_file():
    """Create requirements.txt file"""
    try:
        logger.info("📦 Creating requirements.txt...")
        
        requirements = [
            "selenium>=4.0.0",
            "webdriver-manager>=3.8.0",
            "schedule>=1.2.0",
            "requests>=2.28.0",
            "beautifulsoup4>=4.11.0"
        ]
        
        with open("requirements.txt", "w") as f:
            for req in requirements:
                f.write(f"{req}\n")
        
        logger.info("✅ Requirements file created: requirements.txt")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating requirements file: {e}")
        return False

def create_startup_script():
    """Create startup script for daily capture"""
    try:
        logger.info("🚀 Creating startup script...")
        
        startup_script = """#!/usr/bin/env python3
\"\"\"
Start Daily Network Data Capture
Run this script to start the daily 3 AM capture system
\"\"\"

import sys
import os
import json
import logging
from daily_3am_capture import DailyNetworkCapture, setup_daily_schedule

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    \"\"\"Load configuration from file\"\"\"
    try:
        with open("network_capture_config.json", "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        logger.error("❌ Configuration file not found. Please run setup_network_capture.py first.")
        return None

def main():
    \"\"\"Main function\"\"\"
    logger.info("🎯 Starting Daily Network Data Capture System")
    logger.info("=" * 50)
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    # Get credentials
    username = config["hudl_credentials"]["username"]
    password = config["hudl_credentials"]["password"]
    
    if username == "your_username_here" or password == "your_password_here":
        logger.error("❌ Please update your credentials in network_capture_config.json")
        return
    
    # Create capture instance
    capture = DailyNetworkCapture(username, password)
    
    # Run a test capture first
    logger.info("🧪 Running test capture...")
    success = capture.run_daily_capture()
    
    if success:
        logger.info("✅ Test capture successful!")
        logger.info("🚀 Starting daily 3 AM schedule...")
        
        # Start the daily schedule
        setup_daily_schedule()
    else:
        logger.error("❌ Test capture failed - please check credentials")

if __name__ == "__main__":
    main()
"""
        
        with open("start_daily_capture.py", "w") as f:
            f.write(startup_script)
        
        # Make it executable
        os.chmod("start_daily_capture.py", 0o755)
        
        logger.info("✅ Startup script created: start_daily_capture.py")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating startup script: {e}")
        return False

def create_readme():
    """Create README file with instructions"""
    try:
        logger.info("📖 Creating README file...")
        
        readme_content = """# Daily Network Data Capture System

This system automatically captures network data from Hudl Instat every day at 3 AM, exactly like the manual process you described.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure credentials:**
   - Edit `network_capture_config.json`
   - Replace `your_username_here` and `your_password_here` with your actual Hudl credentials

3. **Test the system:**
   ```bash
   python test_network_capture.py
   ```

4. **Start daily capture:**
   ```bash
   python start_daily_capture.py
   ```

## How It Works

1. **Daily at 3 AM:** The system automatically runs
2. **Login:** Uses your credentials to login to Hudl Instat
3. **Navigate:** Goes to the team data page
4. **Capture:** Captures all network requests and responses (exactly like you did manually)
5. **Save:** Saves the data to files in the `daily_network_data` folder

## Output Files

- `network_data_YYYYMMDD_HHMMSS.json` - Complete captured data
- `response_YYYYMMDD_HHMMSS_N.txt` - Individual API responses (like your manual process)

## Configuration

Edit `network_capture_config.json` to customize:
- Team ID (default: 21479 for Lloydminster Bobcats)
- Output directory
- Capture time (default: 3 AM)
- Headless mode (default: true)

## Troubleshooting

- **Login fails:** Check your credentials in the config file
- **No data captured:** Check if the team page loads correctly
- **Schedule not running:** Make sure the script is running continuously

## Manual Process

This system automates exactly what you did manually:
1. Open browser dev tools
2. Go to Network tab
3. Select XHR/Fetch
4. Navigate to data tabs
5. Copy preview section data
6. Save as text files

Now it's all automated! 🎉
"""
        
        with open("README_network_capture.md", "w") as f:
            f.write(readme_content)
        
        logger.info("✅ README file created: README_network_capture.md")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating README file: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🎯 Setting up Daily Network Data Capture System")
    logger.info("=" * 50)
    
    # Create all necessary files
    success = True
    
    if not create_config_file():
        success = False
    
    if not create_requirements_file():
        success = False
    
    if not create_startup_script():
        success = False
    
    if not create_readme():
        success = False
    
    if success:
        logger.info("✅ Setup completed successfully!")
        logger.info("📋 Next steps:")
        logger.info("  1. Edit network_capture_config.json with your credentials")
        logger.info("  2. Run: pip install -r requirements.txt")
        logger.info("  3. Test: python test_network_capture.py")
        logger.info("  4. Start: python start_daily_capture.py")
    else:
        logger.error("❌ Setup failed - please check the errors above")

if __name__ == "__main__":
    main()
