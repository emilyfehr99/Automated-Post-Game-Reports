#!/usr/bin/env python3
"""
AJHL Shared Account Manager
Handles shared Hudl Instat accounts with session management
"""

import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
from ajhl_robust_scraper import AJHLRobustScraper, ScrapingMethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AccountSession:
    """Account session information"""
    username: str
    password: str
    session_id: str
    last_used: datetime
    is_active: bool = True
    scraper: Optional[AJHLRobustScraper] = None

class AJHLSharedAccountManager:
    """Manages shared Hudl Instat accounts with session pooling"""
    
    def __init__(self, max_sessions: int = 3):
        """Initialize the shared account manager"""
        self.max_sessions = max_sessions
        self.sessions: Dict[str, AccountSession] = {}
        self.session_lock = threading.Lock()
        self.cleanup_interval = 300  # 5 minutes
        self.session_timeout = 1800  # 30 minutes
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_sessions, daemon=True)
        self.cleanup_thread.start()
    
    def add_account(self, username: str, password: str) -> str:
        """Add a new account to the pool"""
        session_id = f"{username}_{int(time.time())}"
        
        with self.session_lock:
            if len(self.sessions) >= self.max_sessions:
                # Remove oldest session
                oldest_session = min(self.sessions.values(), key=lambda s: s.last_used)
                self._close_session(oldest_session.session_id)
            
            session = AccountSession(
                username=username,
                password=password,
                session_id=session_id,
                last_used=datetime.now()
            )
            
            self.sessions[session_id] = session
            logger.info(f"✅ Added account session: {session_id}")
        
        return session_id
    
    def get_available_session(self) -> Optional[AccountSession]:
        """Get an available session for data collection"""
        with self.session_lock:
            # Find an active session
            for session in self.sessions.values():
                if session.is_active and session.scraper:
                    session.last_used = datetime.now()
                    return session
            
            # If no active session, create one
            if self.sessions:
                session = list(self.sessions.values())[0]
                if not session.scraper:
                    try:
                        session.scraper = AJHLRobustScraper(headless=True)
                        if session.scraper.authenticate(session.username, session.password):
                            session.last_used = datetime.now()
                            logger.info(f"✅ Created scraper for session: {session.session_id}")
                            return session
                        else:
                            session.scraper.close()
                            session.scraper = None
                    except Exception as e:
                        logger.error(f"❌ Failed to create scraper for session {session.session_id}: {e}")
                        session.scraper = None
            
            return None
    
    def release_session(self, session_id: str):
        """Release a session back to the pool"""
        with self.session_lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.last_used = datetime.now()
                logger.info(f"🔄 Released session: {session_id}")
    
    def _close_session(self, session_id: str):
        """Close a specific session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if session.scraper:
                session.scraper.close()
            session.is_active = False
            del self.sessions[session_id]
            logger.info(f"🔒 Closed session: {session_id}")
    
    def _cleanup_sessions(self):
        """Cleanup old sessions"""
        while True:
            try:
                time.sleep(self.cleanup_interval)
                
                with self.session_lock:
                    current_time = datetime.now()
                    sessions_to_close = []
                    
                    for session_id, session in self.sessions.items():
                        if (current_time - session.last_used).seconds > self.session_timeout:
                            sessions_to_close.append(session_id)
                    
                    for session_id in sessions_to_close:
                        self._close_session(session_id)
                        logger.info(f"🧹 Cleaned up expired session: {session_id}")
                
            except Exception as e:
                logger.error(f"❌ Error in cleanup thread: {e}")
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get status of all sessions"""
        with self.session_lock:
            return {
                "total_sessions": len(self.sessions),
                "active_sessions": len([s for s in self.sessions.values() if s.is_active]),
                "sessions_with_scrapers": len([s for s in self.sessions.values() if s.scraper]),
                "sessions": [
                    {
                        "session_id": session_id,
                        "username": session.username,
                        "last_used": session.last_used.isoformat(),
                        "is_active": session.is_active,
                        "has_scraper": session.scraper is not None
                    }
                    for session_id, session in self.sessions.items()
                ]
            }
    
    def close_all_sessions(self):
        """Close all sessions"""
        with self.session_lock:
            for session_id in list(self.sessions.keys()):
                self._close_session(session_id)
            logger.info("🔒 All sessions closed")

# Global account manager instance
account_manager = AJHLSharedAccountManager()

def get_shared_scraper() -> Optional[AJHLRobustScraper]:
    """Get a scraper from the shared account pool"""
    session = account_manager.get_available_session()
    if session and session.scraper:
        return session.scraper
    return None

def release_shared_scraper(session_id: str):
    """Release a scraper back to the pool"""
    account_manager.release_session(session_id)

def add_shared_account(username: str, password: str) -> str:
    """Add a new account to the shared pool"""
    return account_manager.add_account(username, password)

def get_shared_account_status() -> Dict[str, Any]:
    """Get status of shared accounts"""
    return account_manager.get_session_status()

def close_all_shared_accounts():
    """Close all shared accounts"""
    account_manager.close_all_sessions()

if __name__ == "__main__":
    # Test the shared account manager
    print("🧪 Testing Shared Account Manager...")
    
    # Add test accounts
    session1 = add_shared_account("test_user1", "test_pass1")
    session2 = add_shared_account("test_user2", "test_pass2")
    
    print(f"Session 1: {session1}")
    print(f"Session 2: {session2}")
    
    # Get status
    status = get_shared_account_status()
    print(f"Status: {json.dumps(status, indent=2)}")
    
    # Cleanup
    close_all_shared_accounts()
    print("✅ Test completed")
