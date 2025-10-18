#!/usr/bin/env python3
"""
Quick launcher for the Audio to Text Converter Web Interface
"""

import subprocess
import sys
import os
import webbrowser
import time
import threading

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['flask', 'whisper', 'torch', 'moviepy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstalling missing packages...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_web.txt'])
            print("✓ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("✗ Failed to install dependencies. Please run manually:")
            print("  pip install -r requirements_web.txt")
            return False
    
    return True

def open_browser():
    """Open browser after a short delay."""
    time.sleep(3)
    webbrowser.open('http://localhost:5000')

def main():
    """Main function to launch the web app."""
    print("=" * 60)
    print("🎤 Audio to Text Converter - Web Interface")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('audio_converter_web.py'):
        print("Error: audio_converter_web.py not found!")
        print("Please run this script from the directory containing the web app files.")
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    print("\nStarting web server...")
    print("The web interface will open in your browser automatically.")
    print("If it doesn't open, go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server.")
    print("-" * 60)
    
    # Open browser in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Start the Flask app
        subprocess.run([sys.executable, 'audio_converter_web.py'])
    except KeyboardInterrupt:
        print("\n\nShutting down web server...")
        print("Thank you for using Audio to Text Converter!")

if __name__ == "__main__":
    main()
