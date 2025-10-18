#!/bin/bash

# Audio Converter 24/7 Service Installation Script
# This script installs the audio converter as a system service

echo "🎵 Installing Audio Converter 24/7 Service..."

# Check if running as root (needed for system service installation)
if [[ $EUID -eq 0 ]]; then
   echo "❌ Please don't run this script as root. Run it as your regular user."
   exit 1
fi

# Create the LaunchAgents directory if it doesn't exist
mkdir -p ~/Library/LaunchAgents

# Copy the plist file to LaunchAgents
echo "📋 Installing service configuration..."
cp com.audioconverter.service.plist ~/Library/LaunchAgents/

# Load the service
echo "🚀 Loading the service..."
launchctl load ~/Library/LaunchAgents/com.audioconverter.service.plist

# Start the service
echo "▶️  Starting the service..."
launchctl start com.audioconverter.service

echo ""
echo "✅ Audio Converter 24/7 Service installed successfully!"
echo ""
echo "🌐 Your audio converter is now running at: http://localhost:5002"
echo "📊 Service status: launchctl list | grep audioconverter"
echo "📝 Logs: tail -f /Users/emilyfehr8/CascadeProjects/audio_converter.log"
echo "🛑 To stop: launchctl unload ~/Library/LaunchAgents/com.audioconverter.service.plist"
echo ""
echo "The service will automatically start when you restart your computer!"
