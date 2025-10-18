#!/usr/bin/env python3
"""
Start Daily Network Data Capture
Run this script to start the daily 3 AM capture system
"""

import sys
import os
import json
import logging
from daily_3am_capture import DailyNetworkCapture, setup_daily_schedule

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function"""
    logger.info("🎯 Starting Daily 4 AM Eastern Network Data Capture System")
    logger.info("=" * 50)
    
    # Create capture instance (uses database for credentials)
    capture = DailyNetworkCapture()
    
    # Run a test capture first
    logger.info("🧪 Running test capture...")
    success = capture.run_daily_capture()
    
    if success:
        logger.info("✅ Test capture successful!")
        logger.info("🚀 Starting daily 4 AM Eastern schedule...")
        
        # Start the daily schedule
        setup_daily_schedule()
    else:
        logger.error("❌ Test capture failed - please check credentials in database")

if __name__ == "__main__":
    main()
