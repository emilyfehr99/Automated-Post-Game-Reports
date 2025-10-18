#!/usr/bin/env python3
"""
Startup script for All Three Zones API
"""

import uvicorn
import logging
import sys
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the API server"""
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")
        
        # Log startup information
        logger.info(f"Starting All Three Zones API on {Config.API_HOST}:{Config.API_PORT}")
        logger.info(f"Debug mode: {Config.DEBUG}")
        logger.info(f"Environment: {'Development' if Config.is_development() else 'Production'}")
        
        # Start the server
        uvicorn.run(
            "main:app",
            host=Config.API_HOST,
            port=Config.API_PORT,
            reload=Config.DEBUG,
            log_level=Config.LOG_LEVEL.lower(),
            access_log=True
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 