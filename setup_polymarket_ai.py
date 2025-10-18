#!/usr/bin/env python3
"""
Polymarket AI Predictor - Setup Script
Automated setup and installation script
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Check if requirements file exists
    requirements_file = "requirements_polymarket.txt"
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file {requirements_file} not found")
        return False
    
    # Install dependencies
    return run_command(f"pip install -r {requirements_file}", "Installing Python packages")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "data",
        "models", 
        "logs",
        "exports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def test_installation():
    """Test if the installation works"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        import requests
        import pandas as pd
        import numpy as np
        import sklearn
        import yfinance
        import textblob
        print("✅ All required packages imported successfully")
        
        # Test main module
        from polymarket_ai_predictor import PolymarketAIPredictor
        predictor = PolymarketAIPredictor()
        print("✅ PolymarketAIPredictor initialized successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def create_sample_config():
    """Create a sample configuration file"""
    print("\n⚙️ Creating sample configuration...")
    
    config = {
        "user_settings": {
            "portfolio_value_cad": 1000,
            "max_position_size": 0.1,
            "min_confidence": 0.3,
            "risk_tolerance": "moderate"
        },
        "api_settings": {
            "rate_limit_delay": 1.0,
            "max_retries": 3,
            "timeout": 30
        },
        "notifications": {
            "email_alerts": False,
            "desktop_notifications": True,
            "log_level": "INFO"
        }
    }
    
    try:
        with open("user_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("✅ Sample configuration created: user_config.json")
        return True
    except Exception as e:
        print(f"❌ Error creating config: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Polymarket AI Predictor Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Incompatible Python version")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        return False
    
    # Create directories
    if not create_directories():
        print("\n❌ Setup failed: Could not create directories")
        return False
    
    # Create sample config
    if not create_sample_config():
        print("\n⚠️ Warning: Could not create sample configuration")
    
    # Test installation
    if not test_installation():
        print("\n❌ Setup failed: Installation test failed")
        return False
    
    # Success message
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the command line version:")
    print("   python polymarket_ai_predictor.py")
    print("\n2. Or launch the web interface:")
    print("   streamlit run polymarket_web_interface.py")
    print("\n3. Read the README for detailed instructions:")
    print("   README_Polymarket_AI.md")
    print("\n⚠️ Remember: Check local regulations before trading!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
