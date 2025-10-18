import os
from typing import Optional
from dotenv import load_dotenv

# Import credentials from credentials.py as fallback
try:
    from credentials import (
        A3Z_USERNAME as CRED_USERNAME,
        A3Z_PASSWORD as CRED_PASSWORD,
        API_HOST as CRED_API_HOST,
        API_PORT as CRED_API_PORT,
        DEBUG as CRED_DEBUG,
        SCRAPER_TIMEOUT as CRED_SCRAPER_TIMEOUT,
        SCRAPER_RETRY_ATTEMPTS as CRED_SCRAPER_RETRY_ATTEMPTS,
        LOG_LEVEL as CRED_LOG_LEVEL
    )
except ImportError:
    # Fallback values if credentials.py doesn't exist
    CRED_USERNAME = None
    CRED_PASSWORD = None
    CRED_API_HOST = "0.0.0.0"
    CRED_API_PORT = 8000
    CRED_DEBUG = False
    CRED_SCRAPER_TIMEOUT = 30
    CRED_SCRAPER_RETRY_ATTEMPTS = 3
    CRED_LOG_LEVEL = "INFO"

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the All Three Zones API"""
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", CRED_API_HOST)
    API_PORT: int = int(os.getenv("API_PORT", CRED_API_PORT))
    DEBUG: bool = os.getenv("DEBUG", str(CRED_DEBUG)).lower() == "true"
    
    # All Three Zones Credentials
    A3Z_USERNAME: Optional[str] = os.getenv("A3Z_USERNAME", CRED_USERNAME)
    A3Z_PASSWORD: Optional[str] = os.getenv("A3Z_PASSWORD", CRED_PASSWORD)
    
    # Scraping Configuration
    SCRAPER_TIMEOUT: int = int(os.getenv("SCRAPER_TIMEOUT", CRED_SCRAPER_TIMEOUT))
    SCRAPER_RETRY_ATTEMPTS: int = int(os.getenv("SCRAPER_RETRY_ATTEMPTS", CRED_SCRAPER_RETRY_ATTEMPTS))
    
    # CORS Configuration
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", CRED_LOG_LEVEL)
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.A3Z_USERNAME or not cls.A3Z_PASSWORD:
            raise ValueError(
                "A3Z_USERNAME and A3Z_PASSWORD must be set in environment variables or credentials.py. "
                "Please check your .env file, environment variables, or credentials.py file."
            )
        return True
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL if needed for future use"""
        return os.getenv("DATABASE_URL", "")
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode"""
        return cls.DEBUG
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return not cls.DEBUG 