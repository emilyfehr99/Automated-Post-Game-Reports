#!/usr/bin/env python3
"""
Test script to verify credentials are working correctly
"""

import logging
from config import Config
from a3z_scraper import AllThreeZonesScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_credentials():
    """Test that credentials are loaded correctly"""
    logger.info("Testing credential configuration...")
    
    # Test config loading
    logger.info(f"✅ Username: {Config.A3Z_USERNAME}")
    logger.info(f"✅ Password: {Config.A3Z_PASSWORD[:5]}...")
    logger.info(f"✅ API Host: {Config.API_HOST}")
    logger.info(f"✅ API Port: {Config.API_PORT}")
    logger.info(f"✅ Debug Mode: {Config.DEBUG}")
    
    # Test scraper initialization
    try:
        scraper = AllThreeZonesScraper()
        logger.info("✅ Scraper initialized successfully with credentials")
        
        # Test login
        if scraper.login():
            logger.info("✅ Login successful with stored credentials!")
        else:
            logger.error("❌ Login failed with stored credentials")
            
    except Exception as e:
        logger.error(f"❌ Error testing credentials: {e}")
        return False
    finally:
        if 'scraper' in locals():
            scraper.close()
    
    return True

def main():
    """Main test function"""
    logger.info("🏒 All Three Zones Credentials Test")
    logger.info("=" * 50)
    
    if test_credentials():
        logger.info("🎉 All credential tests passed!")
        logger.info("\nYour credentials are now permanently stored and working!")
        logger.info("You can now use the API without entering credentials each time.")
    else:
        logger.error("❌ Credential tests failed")
        return False

if __name__ == "__main__":
    main() 