#!/bin/bash

# Audio Converter 24/7 Startup Script
# This script ensures the audio converter runs continuously

# Set the working directory
cd /Users/emilyfehr8/CascadeProjects

# Set environment variables
export PYTHONPATH="/Users/emilyfehr8/CascadeProjects:$PYTHONPATH"
export FLASK_ENV=production
export PATH="/opt/homebrew/bin:$PATH"

# Function to start the service
start_service() {
    echo "$(date): Starting Audio Converter Service on port 5002..."
    
    # Kill any existing processes on port 5002
    lsof -ti:5002 | xargs kill -9 2>/dev/null || true
    
    # Start the service with the correct Python path
    /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 simple_audio_converter_web.py &
    
    # Get the process ID
    SERVICE_PID=$!
    echo "$(date): Service started with PID: $SERVICE_PID"
    
    # Wait for the process to finish
    wait $SERVICE_PID
    echo "$(date): Service stopped with exit code: $?"
}

# Function to check if service is running
check_service() {
    if lsof -i:5002 >/dev/null 2>&1; then
        return 0  # Service is running
    else
        return 1  # Service is not running
    fi
}

# Main loop - restart service if it stops
echo "$(date): Audio Converter 24/7 Service Manager Starting..."

while true; do
    if ! check_service; then
        echo "$(date): Service not running, starting..."
        start_service
    else
        echo "$(date): Service is running, checking again in 30 seconds..."
        sleep 30
    fi
done
