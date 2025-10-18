#!/usr/bin/env python3
"""
Test script to verify All Three Zones API setup
"""

import os
import sys
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_configuration():
    """Test if configuration is properly set up"""
    logger.info("Testing configuration...")
    
    # Check if credentials are set
    username = os.getenv('A3Z_USERNAME')
    password = os.getenv('A3Z_PASSWORD')
    
    if not username or not password:
        logger.error("❌ A3Z_USERNAME and A3Z_PASSWORD must be set in environment variables")
        return False
    
    logger.info("✅ Credentials are configured")
    
    # Check if required files exist
    required_files = [
        'main.py',
        'a3z_scraper.py',
        'config.py',
        'run.py',
        'requirements.txt'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            logger.error(f"❌ Required file {file} not found")
            return False
    
    logger.info("✅ All required files exist")
    return True

def test_dependencies():
    """Test if all dependencies can be imported"""
    logger.info("Testing dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import requests
        import selenium
        from bs4 import BeautifulSoup
        from pydantic import BaseModel
        from dotenv import load_dotenv
        
        logger.info("✅ All dependencies can be imported")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("Run: pip install -r requirements.txt")
        return False

def test_api_server():
    """Test if the API server can start"""
    logger.info("Testing API server...")
    
    try:
        # Import the app
        from main import app
        
        logger.info("✅ FastAPI app can be imported")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to import API app: {e}")
        return False

def test_scraper():
    """Test if the scraper can be initialized"""
    logger.info("Testing scraper initialization...")
    
    try:
        from a3z_scraper import AllThreeZonesScraper
        
        # Try to create scraper instance
        scraper = AllThreeZonesScraper()
        logger.info("✅ Scraper can be initialized")
        
        # Clean up
        scraper.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize scraper: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting All Three Zones API setup tests...")
    
    tests = [
        ("Configuration", test_configuration),
        ("Dependencies", test_dependencies),
        ("API Server", test_api_server),
        ("Scraper", test_scraper),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} test passed")
            else:
                logger.error(f"❌ {test_name} test failed")
        except Exception as e:
            logger.error(f"❌ {test_name} test failed with exception: {e}")
    
    logger.info(f"\n--- Test Results ---")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed! The API is ready to use.")
        logger.info("\nTo start the API server, run:")
        logger.info("python run.py")
        logger.info("\nOr:")
        logger.info("uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        logger.error("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 