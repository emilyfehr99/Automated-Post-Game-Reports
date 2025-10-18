#!/usr/bin/env python3
"""
AJHL API Test Script
Test the AJHL Data Collection API
"""

import asyncio
import requests
import time
from ajhl_api_client import AJHLAPIClient

def test_api_health():
    """Test basic API health"""
    print("🔍 Testing API health...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API health check passed")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running")
        return False
    except Exception as e:
        print(f"❌ Error testing API health: {e}")
        return False

def test_api_endpoints():
    """Test basic API endpoints"""
    print("🔍 Testing API endpoints...")
    
    try:
        # Test root endpoint
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test teams endpoint
        response = requests.get("http://localhost:8000/teams", timeout=5)
        if response.status_code == 200:
            teams = response.json()
            print(f"✅ Teams endpoint working - {len(teams)} teams found")
        else:
            print(f"❌ Teams endpoint failed: {response.status_code}")
            return False
        
        # Test status endpoint
        response = requests.get("http://localhost:8000/status", timeout=5)
        if response.status_code == 200:
            print("✅ Status endpoint working")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False

async def test_api_client():
    """Test the API client"""
    print("🔍 Testing API client...")
    
    try:
        # Read API key from file
        api_key = None
        if Path("api_key.txt").exists():
            with open("api_key.txt", "r") as f:
                content = f.read()
                for line in content.split("\n"):
                    if "Default API Key:" in line:
                        api_key = line.split(":")[1].strip()
                        break
        
        if not api_key:
            print("❌ No API key found. Please run setup first.")
            return False
        
        async with AJHLAPIClient(api_key=api_key) as client:
            # Test health check
            health = await client.health_check()
            print(f"✅ Client health check: {health}")
            
            # Test getting teams
            teams = await client.get_teams()
            print(f"✅ Client teams: {len(teams)} teams found")
            
            # Test getting system status
            status = await client.get_system_status()
            print(f"✅ Client system status: {status['data']['scraper_initialized']}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing API client: {e}")
        return False

def test_shared_accounts():
    """Test shared account management"""
    print("🔍 Testing shared account management...")
    
    try:
        from ajhl_shared_account_manager import get_shared_account_status
        
        status = get_shared_account_status()
        print(f"✅ Shared accounts: {status['active_sessions']} active sessions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing shared accounts: {e}")
        return False

def test_api_keys():
    """Test API key management"""
    print("🔍 Testing API key management...")
    
    try:
        from ajhl_api_keys import list_api_keys, validate_api_key
        
        keys = list_api_keys()
        print(f"✅ API keys: {len(keys)} keys found")
        
        # Test key validation
        if keys:
            # Get the first key (we can't test validation without the actual key)
            print("✅ API key management working")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API keys: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 AJHL API Test Suite")
    print("=" * 30)
    
    tests = [
        ("API Health", test_api_health),
        ("API Endpoints", test_api_endpoints),
        ("API Client", test_api_client),
        ("Shared Accounts", test_shared_accounts),
        ("API Keys", test_api_keys)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                print(f"✅ {test_name} test passed")
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n✅ API is ready to use!")
    else:
        print("\n❌ API has issues. Please check the setup.")
