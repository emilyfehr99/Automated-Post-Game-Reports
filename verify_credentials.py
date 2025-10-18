#!/usr/bin/env python3
"""
Verify Credentials Database
Check that your credentials are stored correctly
"""

import logging
from credentials_database import CredentialsDatabase

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Verify credentials in database"""
    logger.info("🔍 Verifying credentials in database...")
    
    # Create database instance
    db = CredentialsDatabase()
    
    # Get credentials
    creds = db.get_credentials()
    
    if creds:
        logger.info("✅ Credentials found in database:")
        logger.info(f"  • Username: {creds['username']}")
        logger.info(f"  • Password: {'*' * len(creds['password'])}")
        logger.info(f"  • Team ID: {creds['team_id']}")
        logger.info(f"  • Capture Time: {creds['capture_time']}")
        logger.info(f"  • Timezone: {creds['timezone']}")
        logger.info("✅ Database is working correctly!")
    else:
        logger.error("❌ No credentials found in database")
        logger.error("Please run: python credentials_database.py")

if __name__ == "__main__":
    main()
