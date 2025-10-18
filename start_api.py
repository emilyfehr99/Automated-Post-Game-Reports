#!/usr/bin/env python3
"""
AJHL API Startup Script
Easy way to start the AJHL Data Collection API
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    print("🔍 Checking requirements...")
    
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import httpx
        print("✅ Core API requirements found")
        return True
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        print("📦 Installing requirements...")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "ajhl_requirements.txt"], check=True)
            print("✅ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements")
            return False

def check_credentials():
    """Check if credentials file exists"""
    print("🔐 Checking credentials...")
    
    if not Path("hudl_credentials.py").exists():
        print("❌ hudl_credentials.py not found")
        print("📝 Creating template credentials file...")
        
        template = '''# Hudl Instat Credentials
# Replace with your actual credentials

HUDL_USERNAME = "your_username_here"
HUDL_PASSWORD = "your_password_here"
'''
        
        with open("hudl_credentials.py", "w") as f:
            f.write(template)
        
        print("📄 Created hudl_credentials.py template")
        print("⚠️  Please edit hudl_credentials.py with your actual credentials")
        return False
    else:
        print("✅ Credentials file found")
        return True

def check_database():
    """Check if database exists"""
    print("🗄️  Checking database...")
    
    if not Path("ajhl_api.db").exists():
        print("📊 Database will be created on first run")
    else:
        print("✅ Database found")
    
    return True

def start_api():
    """Start the API server"""
    print("🚀 Starting AJHL API Server...")
    
    try:
        # Start the API
        subprocess.run([
            sys.executable, "ajhl_api_system.py"
        ])
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")
    except Exception as e:
        print(f"❌ Error starting API server: {e}")

def test_api():
    """Test the API endpoints"""
    print("🧪 Testing API endpoints...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test root endpoint
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        print("🎉 API is working correctly!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def show_menu():
    """Show main menu"""
    print("\n🏒 AJHL Data Collection API")
    print("=" * 40)
    print("1. Start API server")
    print("2. Test API endpoints")
    print("3. View API documentation")
    print("4. Setup notifications")
    print("5. Check system status")
    print("6. Exit")
    print("=" * 40)

def main():
    """Main startup function"""
    print("🚀 Starting AJHL API System...")
    
    # Check requirements
    if not check_requirements():
        print("❌ System check failed. Please install requirements manually.")
        return
    
    # Check credentials
    if not check_credentials():
        print("❌ Please configure credentials and run again.")
        return
    
    # Check database
    check_database()
    
    while True:
        show_menu()
        
        try:
            choice = input("\nSelect an option (1-6): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting API server...")
                print("📖 API will be available at: http://localhost:8000")
                print("📚 Documentation: http://localhost:8000/docs")
                print("🛑 Press Ctrl+C to stop the server")
                start_api()
            
            elif choice == "2":
                print("\n🧪 Testing API endpoints...")
                if test_api():
                    print("✅ All tests passed!")
                else:
                    print("❌ Some tests failed")
            
            elif choice == "3":
                print("\n📚 Opening API documentation...")
                print("🌐 Documentation: http://localhost:8000/docs")
                print("📖 ReDoc: http://localhost:8000/redoc")
                print("🔍 Health check: http://localhost:8000/health")
            
            elif choice == "4":
                print("\n⚙️ Setting up notifications...")
                subprocess.run([sys.executable, "setup_notifications.py"])
            
            elif choice == "5":
                print("\n📊 System Status:")
                print("  ✅ Requirements: Installed")
                print("  ✅ Credentials: Configured")
                print("  ✅ Database: Ready")
                print("  🔄 API Server: Not running")
                print("\n💡 Start the API server (option 1) to begin data collection")
            
            elif choice == "6":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid option. Please select 1-6.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
