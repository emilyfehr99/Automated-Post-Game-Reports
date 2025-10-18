#!/usr/bin/env python3
"""
Hudl Instat Multi-User Manager
Manages multiple users accessing the same Hudl account to prevent conflicts
"""

import time
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from hudl_instat_analyzer import HudlInstatMiniAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserSession:
    """Represents a user session"""
    user_id: str
    username: str
    session_id: str
    created_at: float
    last_activity: float
    is_active: bool
    api_instance: Optional[HudlInstatMiniAPI] = None

class HudlMultiUserManager:
    """Manages multiple users accessing Hudl Instat"""
    
    def __init__(self, shared_username: str, shared_password: str):
        """Initialize the multi-user manager"""
        self.shared_username = shared_username
        self.shared_password = shared_password
        self.active_sessions: Dict[str, UserSession] = {}
        self.session_timeout = 1800  # 30 minutes
        self.max_concurrent_sessions = 3
        
    def create_user_session(self, user_id: str) -> Optional[UserSession]:
        """Create a new user session"""
        # Check if user already has an active session
        if user_id in self.active_sessions:
            existing_session = self.active_sessions[user_id]
            if existing_session.is_active and (time.time() - existing_session.last_activity) < self.session_timeout:
                logger.info(f"🔄 Reusing existing session for user {user_id}")
                existing_session.last_activity = time.time()
                return existing_session
            else:
                # Clean up expired session
                self.cleanup_session(user_id)
        
        # Check if we're at the session limit
        active_count = sum(1 for session in self.active_sessions.values() if session.is_active)
        if active_count >= self.max_concurrent_sessions:
            logger.warning(f"⚠️  Maximum concurrent sessions ({self.max_concurrent_sessions}) reached")
            return None
        
        # Create new session
        try:
            logger.info(f"🆕 Creating new session for user {user_id}")
            
            # Create API instance with unique user identifier
            api = HudlInstatMiniAPI(
                username=self.shared_username,
                password=self.shared_password,
                user_identifier=user_id
            )
            
            if not api.authenticated:
                logger.error(f"❌ Failed to authenticate for user {user_id}")
                return None
            
            # Create session record
            session = UserSession(
                user_id=user_id,
                username=self.shared_username,
                session_id=f"{user_id}_{int(time.time())}",
                created_at=time.time(),
                last_activity=time.time(),
                is_active=True,
                api_instance=api
            )
            
            self.active_sessions[user_id] = session
            logger.info(f"✅ Session created for user {user_id} (Session: {session.session_id})")
            return session
            
        except Exception as e:
            logger.error(f"❌ Error creating session for user {user_id}: {e}")
            return None
    
    def get_user_session(self, user_id: str) -> Optional[UserSession]:
        """Get an active user session"""
        if user_id not in self.active_sessions:
            return self.create_user_session(user_id)
        
        session = self.active_sessions[user_id]
        
        # Check if session is still active
        if not session.is_active or (time.time() - session.last_activity) > self.session_timeout:
            logger.info(f"🔄 Session expired for user {user_id}, creating new one")
            self.cleanup_session(user_id)
            return self.create_user_session(user_id)
        
        # Update last activity
        session.last_activity = time.time()
        return session
    
    def cleanup_session(self, user_id: str):
        """Clean up a user session"""
        if user_id in self.active_sessions:
            session = self.active_sessions[user_id]
            if session.api_instance:
                session.api_instance.close()
            session.is_active = False
            logger.info(f"🧹 Cleaned up session for user {user_id}")
    
    def cleanup_expired_sessions(self):
        """Clean up all expired sessions"""
        current_time = time.time()
        expired_users = []
        
        for user_id, session in self.active_sessions.items():
            if not session.is_active or (current_time - session.last_activity) > self.session_timeout:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            self.cleanup_session(user_id)
        
        if expired_users:
            logger.info(f"🧹 Cleaned up {len(expired_users)} expired sessions")
    
    def get_team_info(self, user_id: str, team_id: str) -> Dict:
        """Get team info for a specific user"""
        session = self.get_user_session(user_id)
        if not session or not session.api_instance:
            return {"error": "No active session for user"}
        
        return session.api_instance.get_team_info(team_id)
    
    def get_team_players(self, user_id: str, team_id: str) -> List[Dict]:
        """Get team players for a specific user"""
        session = self.get_user_session(user_id)
        if not session or not session.api_instance:
            return [{"error": "No active session for user"}]
        
        return session.api_instance.get_team_players(team_id)
    
    def get_team_games(self, user_id: str, team_id: str) -> List[Dict]:
        """Get team games for a specific user"""
        session = self.get_user_session(user_id)
        if not session or not session.api_instance:
            return [{"error": "No active session for user"}]
        
        return session.api_instance.get_team_games(team_id)
    
    def get_session_status(self) -> Dict:
        """Get status of all sessions"""
        self.cleanup_expired_sessions()
        
        active_sessions = []
        for user_id, session in self.active_sessions.items():
            if session.is_active:
                active_sessions.append({
                    "user_id": user_id,
                    "session_id": session.session_id,
                    "created_at": session.created_at,
                    "last_activity": session.last_activity,
                    "age_minutes": (time.time() - session.created_at) / 60
                })
        
        return {
            "active_sessions": active_sessions,
            "total_active": len(active_sessions),
            "max_concurrent": self.max_concurrent_sessions
        }
    
    def close_all_sessions(self):
        """Close all active sessions"""
        for user_id in list(self.active_sessions.keys()):
            self.cleanup_session(user_id)
        logger.info("🔒 All sessions closed")

def main():
    """Example usage of the multi-user manager"""
    print("👥 Hudl Instat Multi-User Manager Example")
    print("=" * 60)
    
    # Initialize with shared credentials
    try:
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        manager = HudlMultiUserManager(HUDL_USERNAME, HUDL_PASSWORD)
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
        return
    
    # Example: Multiple users accessing the same team
    team_id = "21479"
    users = ["emily", "coach1", "analyst1"]
    
    print(f"\n🏒 Testing multi-user access to team {team_id}")
    
    for user in users:
        print(f"\n👤 User: {user}")
        
        # Get team info
        team_info = manager.get_team_info(user, team_id)
        print(f"  Team Info: {team_info}")
        
        # Get players
        players = manager.get_team_players(user, team_id)
        print(f"  Players found: {len(players)}")
        
        # Small delay to simulate different users
        time.sleep(2)
    
    # Show session status
    print(f"\n📊 Session Status:")
    status = manager.get_session_status()
    print(json.dumps(status, indent=2))
    
    # Clean up
    manager.close_all_sessions()
    print("\n✅ All sessions closed")

if __name__ == "__main__":
    main()
