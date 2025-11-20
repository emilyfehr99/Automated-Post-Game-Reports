#!/usr/bin/env python3
"""
Setup script for Audio to Text Converter
This script helps install dependencies and verify the installation.
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        print(f"  Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_ffmpeg():
    """Install FFmpeg if not available."""
    print("\nChecking for FFmpeg...")
    
    # Check if ffmpeg is already installed
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✓ FFmpeg is already installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Install FFmpeg based on platform
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("Installing FFmpeg via Homebrew...")
        if not run_command("brew install ffmpeg", "FFmpeg installation"):
            print("Please install Homebrew first: https://brew.sh/")
            return False
    elif system == "linux":
        print("Installing FFmpeg via package manager...")
        # Try different package managers
        if not run_command("sudo apt-get update && sudo apt-get install -y ffmpeg", "FFmpeg installation (apt)"):
            if not run_command("sudo yum install -y ffmpeg", "FFmpeg installation (yum)"):
                print("Please install FFmpeg manually for your Linux distribution")
                return False
    elif system == "windows":
        print("Please install FFmpeg manually:")
        print("1. Download from: https://ffmpeg.org/download.html")
        print("2. Add to your PATH environment variable")
        return False
    else:
        print(f"Unsupported platform: {system}")
        return False
    
    return True

def install_python_dependencies():
    """Install Python dependencies."""
    print("\nInstalling Python dependencies...")
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Pip upgrade")
    
    # Install requirements
    requirements_file = "requirements_audio_converter.txt"
    if os.path.exists(requirements_file):
        return run_command(f"{sys.executable} -m pip install -r {requirements_file}", "Python dependencies installation")
    else:
        print(f"✗ Requirements file {requirements_file} not found")
        return False

def test_installation():
    """Test if the installation works."""
    print("\nTesting installation...")
    
    try:
        import whisper
        import torch
        import moviepy.editor
        print("✓ All required modules imported successfully")
        
        # Test Whisper model loading
        print("Testing Whisper model loading...")
        model = whisper.load_model("tiny")  # Use tiny model for quick test
        print("✓ Whisper model loaded successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Test error: {e}")
        return False

def main():
    """Main setup function."""
    print("=" * 60)
    print("Audio to Text Converter Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install FFmpeg
    if not install_ffmpeg():
        print("\n⚠️  FFmpeg installation failed. You may need to install it manually.")
        print("   The converter will still work for audio files, but video processing may fail.")
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("\n✗ Setup failed during dependency installation")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\n✗ Setup failed during testing")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ Setup completed successfully!")
    print("=" * 60)
    print("\nYou can now use the audio to text converter:")
    print("  python audio_to_text_converter.py --help")
    print("\nExample usage:")
    print("  python audio_to_text_converter.py meeting.mp4")
    print("  python audio_to_text_converter.py --batch /path/to/videos/")

if __name__ == "__main__":
    main()
