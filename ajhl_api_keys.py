#!/usr/bin/env python3
"""
AJHL API Key Management
Simple API key system for the AJHL Data Collection API
"""

import json
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class APIKey:
    """API Key data structure"""
    key_id: str
    key_hash: str
    name: str
    description: str
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True
    permissions: List[str] = None
    expires_at: Optional[datetime] = None

class AJHLAPIKeyManager:
    """Manages API keys for the AJHL API"""
    
    def __init__(self, keys_file: str = "ajhl_api_keys.json"):
        """Initialize the API key manager"""
        self.keys_file = Path(keys_file)
        self.keys: Dict[str, APIKey] = {}
        self.load_keys()
    
    def load_keys(self):
        """Load API keys from file"""
        if self.keys_file.exists():
            try:
                with open(self.keys_file, 'r') as f:
                    data = json.load(f)
                    for key_id, key_data in data.items():
                        key_data['created_at'] = datetime.fromisoformat(key_data['created_at'])
                        if key_data.get('last_used'):
                            key_data['last_used'] = datetime.fromisoformat(key_data['last_used'])
                        if key_data.get('expires_at'):
                            key_data['expires_at'] = datetime.fromisoformat(key_data['expires_at'])
                        self.keys[key_id] = APIKey(**key_data)
                logger.info(f"✅ Loaded {len(self.keys)} API keys")
            except Exception as e:
                logger.error(f"❌ Error loading API keys: {e}")
                self.keys = {}
        else:
            # Create default API key
            self.create_default_key()
    
    def save_keys(self):
        """Save API keys to file"""
        try:
            data = {}
            for key_id, key in self.keys.items():
                key_data = asdict(key)
                key_data['created_at'] = key.created_at.isoformat()
                if key.last_used:
                    key_data['last_used'] = key.last_used.isoformat()
                if key.expires_at:
                    key_data['expires_at'] = key.expires_at.isoformat()
                data[key_id] = key_data
            
            with open(self.keys_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"✅ Saved {len(self.keys)} API keys")
        except Exception as e:
            logger.error(f"❌ Error saving API keys: {e}")
    
    def create_default_key(self):
        """Create a default API key for initial setup"""
        default_key = self.generate_key(
            name="Default Key",
            description="Default API key for initial setup",
            permissions=["read", "write", "admin"]
        )
        logger.info("✅ Created default API key")
        return default_key
    
    def generate_key(
        self, 
        name: str, 
        description: str = "", 
        permissions: List[str] = None,
        expires_days: Optional[int] = None
    ) -> str:
        """Generate a new API key"""
        if permissions is None:
            permissions = ["read"]
        
        # Generate unique key ID
        key_id = secrets.token_urlsafe(16)
        
        # Generate API key
        api_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Set expiration
        expires_at = None
        if expires_days:
            expires_at = datetime.now() + timedelta(days=expires_days)
        
        # Create API key object
        api_key_obj = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            description=description,
            created_at=datetime.now(),
            is_active=True,
            permissions=permissions,
            expires_at=expires_at
        )
        
        # Store the key
        self.keys[key_id] = api_key_obj
        self.save_keys()
        
        logger.info(f"✅ Generated API key: {name}")
        return api_key
    
    def validate_key(self, api_key: str) -> Optional[APIKey]:
        """Validate an API key"""
        if not api_key:
            return None
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        for key in self.keys.values():
            if key.key_hash == key_hash and key.is_active:
                # Check expiration
                if key.expires_at and datetime.now() > key.expires_at:
                    key.is_active = False
                    self.save_keys()
                    continue
                
                # Update last used
                key.last_used = datetime.now()
                self.save_keys()
                
                return key
        
        return None
    
    def revoke_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        if key_id in self.keys:
            self.keys[key_id].is_active = False
            self.save_keys()
            logger.info(f"✅ Revoked API key: {key_id}")
            return True
        return False
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """List all API keys (without the actual keys)"""
        keys_list = []
        for key in self.keys.values():
            keys_list.append({
                "key_id": key.key_id,
                "name": key.name,
                "description": key.description,
                "created_at": key.created_at.isoformat(),
                "last_used": key.last_used.isoformat() if key.last_used else None,
                "is_active": key.is_active,
                "permissions": key.permissions,
                "expires_at": key.expires_at.isoformat() if key.expires_at else None
            })
        return keys_list
    
    def get_key_by_id(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID"""
        return self.keys.get(key_id)
    
    def update_key(self, key_id: str, **kwargs) -> bool:
        """Update API key properties"""
        if key_id in self.keys:
            key = self.keys[key_id]
            for attr, value in kwargs.items():
                if hasattr(key, attr):
                    setattr(key, attr, value)
            self.save_keys()
            return True
        return False

# Global API key manager
api_key_manager = AJHLAPIKeyManager()

def generate_api_key(name: str, description: str = "", permissions: List[str] = None) -> str:
    """Generate a new API key"""
    return api_key_manager.generate_key(name, description, permissions)

def validate_api_key(api_key: str) -> Optional[APIKey]:
    """Validate an API key"""
    return api_key_manager.validate_key(api_key)

def revoke_api_key(key_id: str) -> bool:
    """Revoke an API key"""
    return api_key_manager.revoke_key(key_id)

def list_api_keys() -> List[Dict[str, Any]]:
    """List all API keys"""
    return api_key_manager.list_keys()

def get_default_api_key() -> str:
    """Get the default API key for initial setup"""
    keys = api_key_manager.list_keys()
    if keys:
        # Return the first active key
        for key in keys:
            if key['is_active']:
                # We need to get the actual key, not just the hash
                # This is a bit tricky since we only store hashes
                # For now, we'll generate a new default key
                return api_key_manager.generate_key(
                    name="Default Key",
                    description="Default API key for initial setup",
                    permissions=["read", "write", "admin"]
                )
    
    # Create a new default key
    return api_key_manager.create_default_key()

if __name__ == "__main__":
    # Test the API key manager
    print("🧪 Testing API Key Manager...")
    
    # Generate a test key
    test_key = generate_api_key(
        name="Test Key",
        description="Test API key",
        permissions=["read", "write"]
    )
    
    print(f"Generated key: {test_key}")
    
    # Validate the key
    validated_key = validate_api_key(test_key)
    if validated_key:
        print(f"✅ Key validated: {validated_key.name}")
    else:
        print("❌ Key validation failed")
    
    # List keys
    keys = list_api_keys()
    print(f"Total keys: {len(keys)}")
    
    print("✅ Test completed")
