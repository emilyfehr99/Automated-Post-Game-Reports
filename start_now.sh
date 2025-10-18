#!/bin/bash

# Quick Start Script for Audio Converter
# This starts the service immediately for testing

echo "🎵 Starting Audio Converter Service..."

# Kill any existing processes
lsof -ti:5002 | xargs kill -9 2>/dev/null || true

# Start the service
cd /Users/emilyfehr8/CascadeProjects
python3 simple_audio_converter_web.py &

echo "✅ Service started!"
echo "🌐 Open: http://localhost:5002"
echo "🛑 Press Ctrl+C to stop"

# Wait for user to stop
wait
