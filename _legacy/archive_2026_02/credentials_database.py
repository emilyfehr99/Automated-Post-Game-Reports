#!/usr/bin/env python3
"""
Credentials Database for Network Capture System
Stores user credentials securely in SQLite database
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CredentialsDatabase:
    """Database for storing user credentials"""
    
    def __init__(self, db_path: str = "network_capture_credentials.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with credentials table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create credentials table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    team_id TEXT DEFAULT '21479',
                    capture_time TEXT DEFAULT '04:00',
                    timezone TEXT DEFAULT 'America/New_York',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Credentials database initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing database: {e}")
    
    def store_credentials(self, username: str, password: str, team_id: str = "21479", 
                         capture_time: str = "04:00", timezone: str = "America/New_York") -> bool:
        """Store user credentials in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing credentials
            cursor.execute('DELETE FROM credentials')
            
            # Insert new credentials
            cursor.execute('''
                INSERT INTO credentials (username, password, team_id, capture_time, timezone, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password, team_id, capture_time, timezone, datetime.now()))
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Credentials stored successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing credentials: {e}")
            return False
    
    def get_credentials(self) -> Optional[Dict[str, Any]]:
        """Get active credentials from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT username, password, team_id, capture_time, timezone
                FROM credentials 
                WHERE is_active = 1 
                ORDER BY updated_at DESC 
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'username': result[0],
                    'password': result[1],
                    'team_id': result[2],
                    'capture_time': result[3],
                    'timezone': result[4]
                }
            else:
                logger.warning("⚠️ No credentials found in database")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting credentials: {e}")
            return None
    
    def update_capture_time(self, capture_time: str) -> bool:
        """Update capture time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE credentials 
                SET capture_time = ?, updated_at = ?
                WHERE is_active = 1
            ''', (capture_time, datetime.now()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Capture time updated to {capture_time}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating capture time: {e}")
            return False

def main():
    """Main function to set up credentials"""
    logger.info("🔐 Setting up credentials database...")
    
    # Create database instance
    db = CredentialsDatabase()
    
    # Store your credentials
    success = db.store_credentials(
        username="chaserochon777@gmail.com",
        password="357Chaser!468",
        team_id="21479",
        capture_time="04:00",  # 4 AM Eastern
        timezone="America/New_York"
    )
    
    if success:
        logger.info("✅ Credentials stored successfully!")
        logger.info("📊 Credentials details:")
        logger.info("  • Username: chaserochon777@gmail.com")
        logger.info("  • Team ID: 21479 (Lloydminster Bobcats)")
        logger.info("  • Capture Time: 04:00 (4 AM Eastern)")
        logger.info("  • Timezone: America/New_York")
        
        # Verify credentials
        creds = db.get_credentials()
        if creds:
            logger.info("✅ Credentials verified in database")
        else:
            logger.error("❌ Failed to verify credentials")
    else:
        logger.error("❌ Failed to store credentials")

if __name__ == "__main__":
    main()
